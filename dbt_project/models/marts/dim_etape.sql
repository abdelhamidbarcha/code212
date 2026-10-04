{#
    Dimension étape (année d'une filière, par version d'étape).
    Clé : cle_etape = cod_etp-cod_vrs_vet (ex : SMI1-2).
#}
with codes as (

    select cod_etp, cod_vrs_vet from {{ ref('stg_apogee__ind_contrat_elp') }}
    union
    select cod_etp, cod_vrs_vet from {{ ref('ref_etape') }}

)

select
    c.cod_etp || '-' || coalesce(c.cod_vrs_vet, '?')                      as cle_etape,
    c.cod_etp,
    c.cod_vrs_vet,
    coalesce(r.lib_etp, 'Étape ' || c.cod_etp || ' (non référencée)')     as lib_etape,
    r.cod_filiere,
    coalesce(r.lib_filiere, 'Non renseignée')                             as lib_filiere,
    coalesce(r.cycle, 'Non renseigné')                                    as cycle,
    r.annee_etude,
    r.duree_cycle,
    coalesce(r.est_annee_terminale = 'O', false)                          as est_annee_terminale,
    r.cod_cmp,
    coalesce(cmp.lib_composante, 'Non renseignée')                        as lib_composante,
    r.cod_etp is not null                                                 as est_referencee
from codes as c
left join {{ ref('ref_etape') }} as r
    on  r.cod_etp = c.cod_etp
    and r.cod_vrs_vet is not distinct from c.cod_vrs_vet
left join {{ ref('dim_composante') }} as cmp
    on cmp.cod_cmp = r.cod_cmp
where c.cod_etp is not null