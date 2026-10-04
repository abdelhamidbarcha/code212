{#
    Fait : inscriptions pédagogiques (contrats étudiant x module).
    Grain : une ligne par (cod_ind, cod_anu, cle_etape, cod_elp).
#}
with contrats as (

    select * from {{ ref('stg_apogee__ind_contrat_elp') }}

),

inscriptions_administratives as (

    select distinct cod_ind, cod_anu
    from {{ ref('stg_apogee__ins_adm_etp') }}

)

select
    -- Clés
    c.cod_ind,
    c.cod_anu,
    c.cod_etp || '-' || coalesce(c.cod_vrs_vet, '?')            as cle_etape,
    c.cod_elp,

    -- Prise en compte
    coalesce(c.tem_prc_ice = 'O', false)                        as est_pris_en_compte,

    -- Saisie
    c.dat_cre_elp_con                                           as date_creation,
    c.dat_cre_elp_con::date                                     as jour_creation,
    date_trunc('month', c.dat_cre_elp_con)::date                as mois_creation,
    c.dat_mod_ice                                               as date_modification,
    c.dat_mod_ice is not null                                   as est_modifie,
    (c.dat_mod_ice::date - c.dat_cre_elp_con::date)             as delai_modification_jours,
    c.cod_uti,
    case
        when c.cod_uti in ({% for u in var('utilisateurs_batch') %}'{{ u }}'{% if not loop.last %}, {% endif %}{% endfor %})
            then 'Automatique'
        else 'Manuelle'
    end                                                         as type_saisie,

    -- Cohérence
    ia.cod_ind is not null                                      as a_inscription_administrative,
    c.nb_saisies
from contrats as c
left join inscriptions_administratives as ia
    on  ia.cod_ind = c.cod_ind
    and ia.cod_anu = c.cod_anu