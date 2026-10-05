{#
    Contrôle qualité des données : une ligne par anomalie détectée.
    Le catalogue des contrôles (libellé, catégorie, gravité) est dans le seed
    ref_controle_qualite. Les données personnelles (email, INE) ne sont jamais
    affichées : seul le code étudiant permet de retrouver le dossier dans Apogée.
#}
with ia as (

    select * from {{ ref('stg_apogee__ins_adm_etp') }}

),

contrats as (

    select * from {{ ref('stg_apogee__ind_contrat_elp') }}

),

individus as (

    select * from {{ ref('stg_apogee__individu') }}

),

brut as (

    select * from {{ source('apogee', 'individu') }}

),

anomalies as (

    -- Q01 : contrat pédagogique sans inscription administrative la même année
    select 'Q01' as code_controle, c.cod_ind, c.cod_anu,
           count(*)::text || ' module(s) inscrit(s) sans inscription administrative' as detail
    from contrats as c
    left join (select distinct cod_ind, cod_anu from ia) as i
        on i.cod_ind = c.cod_ind and i.cod_anu = c.cod_anu
    where i.cod_ind is null
    group by c.cod_ind, c.cod_anu

    union all
    -- Q02 : inscription administrative valide sans aucun module
    select 'Q02', cod_ind, cod_anu, 'Inscription valide sans aucun module'
    from {{ ref('fct_inscription_administrative') }}
    where est_comptabilise and not a_contrat_pedagogique

    union all
    -- Q03 : contrat pédagogique saisi plusieurs fois
    select 'Q03', cod_ind, cod_anu, 'Module ' || cod_elp || ' saisi ' || nb_saisies || ' fois'
    from contrats
    where nb_saisies > 1

    union all
    -- Q04 : inscription administrative saisie plusieurs fois
    select 'Q04', cod_ind, cod_anu, 'Composante ' || cod_cmp || ' saisie ' || nb_saisies || ' fois'
    from ia
    where nb_saisies > 1

    union all
    -- Q05 : email manquant
    select 'Q05', cod_ind, null::integer, 'Aucune adresse email'
    from individus
    where adr_mail_etu is null

    union all
    -- Q06 : email au format invalide
    select 'Q06', cod_ind, null::integer, 'Adresse email au format invalide'
    from individus
    where adr_mail_etu is not null
      and adr_mail_etu !~ '^[^@[:space:]]+@[^@[:space:]]+\.[a-z]{2,}$'

    union all
    -- Q07 : INE absent pour un étudiant de nationalité marocaine
    select 'Q07', cod_ind, null::integer, 'Numéro INE / Massar absent'
    from individus
    where numero_ine is null
      and cod_nat_etu = '350'

    union all
    -- Q08 : date de naissance absente ou improbable
    select 'Q08', cod_ind, null::integer,
           case when date_naissance is null then 'Date absente ou illisible'
                else 'Date improbable : ' || date_naissance::text end
    from individus
    where date_naissance is null
       or date_naissance not between date '1940-01-01' and current_date - interval '15 years'

    union all
    -- Q09 : composante absente du référentiel
    select 'Q09', ia.cod_ind, ia.cod_anu, 'Code composante ' || ia.cod_cmp
    from ia
    join {{ ref('dim_composante') }} as cmp
        on cmp.cod_cmp = ia.cod_cmp
    where not cmp.est_referencee

    union all
    -- Q10 : étape ou module absent du référentiel
    select 'Q10', c.cod_ind, c.cod_anu, 'Étape ' || c.cod_etp || ' / module ' || c.cod_elp
    from contrats as c
    left join {{ ref('dim_etape') }} as e
        on e.cle_etape = c.cod_etp || '-' || coalesce(c.cod_vrs_vet, '?')
    left join {{ ref('dim_element_pedagogique') }} as m
        on m.cod_elp = c.cod_elp
    where not coalesce(e.est_referencee, false)
       or not coalesce(m.est_reference, false)

    union all
    -- Q11 : saisies non standard corrigées automatiquement par le nettoyage
    select 'Q11', upper(trim(cod_ind)), null::integer, 'Sexe saisi « ' || cod_sex_etu || ' »'
    from brut
    where cod_sex_etu is not null
      and cod_sex_etu !~ '^[MF]$'

    union all
    select 'Q11', upper(trim(cod_ind)), null::integer, 'Nom mal formaté (casse ou espaces)'
    from brut
    where lib_nom_pat_ind <> upper(trim(regexp_replace(lib_nom_pat_ind, '\s+', ' ', 'g')))

    union all
    select 'Q11', upper(trim(cod_ind)), null::integer, 'Email mal formaté (majuscules ou espaces)'
    from brut
    where coalesce(adr_mail_etu, '') <> ''
      and adr_mail_etu <> lower(trim(adr_mail_etu))

)

select
    a.code_controle,
    r.libelle_controle,
    r.categorie,
    r.gravite,
    r.table_source,
    a.cod_ind,
    i.cod_etu,
    a.cod_anu,
    y.lib_annee_universitaire                       as annee_universitaire,
    a.detail,
    current_timestamp                               as date_controle
from anomalies as a
join {{ ref('ref_controle_qualite') }} as r
    on r.code_controle = a.code_controle
left join individus as i
    on i.cod_ind = a.cod_ind
left join {{ ref('dim_annee_universitaire') }} as y
    on y.cod_anu = a.cod_anu