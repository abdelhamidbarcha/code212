{#
    Dimension élément pédagogique (module).
#}
with codes as (

    select cod_elp from {{ ref('stg_apogee__ind_contrat_elp') }}
    union
    select cod_elp from {{ ref('ref_element_pedagogique') }}

),

etapes as (

    select distinct on (cod_etp)
        cod_etp, lib_filiere, cycle, annee_etude, cod_cmp
    from {{ ref('ref_etape') }}
    order by cod_etp, cod_vrs_vet desc

)

select
    c.cod_elp,
    coalesce(r.lib_elp, 'Module ' || c.cod_elp || ' (non référencé)') as lib_element_pedagogique,
    coalesce(r.nature_elp, 'Non renseignée')                          as nature,
    r.semestre,
    r.cod_etp,
    coalesce(et.lib_filiere, 'Non renseignée')                        as lib_filiere,
    coalesce(et.cycle, 'Non renseigné')                               as cycle,
    et.annee_etude,
    et.cod_cmp,
    coalesce(cmp.lib_composante, 'Non renseignée')                    as lib_composante,
    r.cod_elp is not null                                             as est_reference
from codes as c
left join {{ ref('ref_element_pedagogique') }} as r
    on r.cod_elp = c.cod_elp
left join etapes as et
    on et.cod_etp = r.cod_etp
left join {{ ref('dim_composante') }} as cmp
    on cmp.cod_cmp = et.cod_cmp
where c.cod_elp is not null