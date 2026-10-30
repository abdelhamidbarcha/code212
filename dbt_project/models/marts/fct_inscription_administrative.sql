{#
    Fait : inscriptions administratives.
    Grain : une ligne par (cod_ind, cod_anu, cod_cmp).

    Mesure principale : effectif = nombre d'étudiants distincts où est_comptabilise = vrai.
#}
with base as (

    select
        ia.*,
        -- Âge à l'inscription, au 1er jour du mois de référence (octobre) de l'année universitaire
        date_part('year', age(
            make_date(ia.cod_anu, {{ var('mois_reference_age') }}, 1),
            ind.date_naissance
        ))::integer as age_inscription
    from {{ ref('stg_apogee__ins_adm_etp') }} as ia
    left join {{ ref('stg_apogee__individu') }} as ind
        on ind.cod_ind = ia.cod_ind

)

select
    -- Clés
    b.cod_ind,
    b.cod_anu,
    b.cod_cmp,
    p.cle_etape,

    -- État
    b.eta_iae,
    coalesce(e.lib_etat_iae, 'État ' || b.eta_iae || ' (non référencé)')   as lib_etat_inscription,
    coalesce(e.compte_dans_effectif = 'O', false)                          as est_comptabilise,

    -- Âge
    b.age_inscription,
    case
        when b.age_inscription is null then 'Non renseigné'
        when b.age_inscription < 18    then '17 ans et moins'
        when b.age_inscription <= 20   then '18-20 ans'
        when b.age_inscription <= 23   then '21-23 ans'
        when b.age_inscription <= 26   then '24-26 ans'
        else '27 ans et plus'
    end                                                                     as tranche_age,

    -- Parcours
    p.type_inscription,
    p.est_redoublant,
    p.est_reinscrit_annee_suivante,
    p.statut_annee_suivante,

    -- Inscription pédagogique associée
    coalesce(p.nb_modules, 0)                                               as nb_modules_inscrits,
    coalesce(p.nb_modules, 0) > 0                                           as a_contrat_pedagogique,

    -- Traçabilité
    b.nb_saisies
from base as b
left join {{ ref('ref_etat_iae') }} as e
    on e.eta_iae = b.eta_iae
left join {{ ref('int_parcours_annuel') }} as p
    on  p.cod_ind = b.cod_ind
    and p.cod_anu = b.cod_anu