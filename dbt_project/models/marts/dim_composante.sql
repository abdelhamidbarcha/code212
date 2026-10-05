{#
    Dimension composante (faculté / école).
    Construite à partir des codes réellement présents dans les données ET du
    référentiel : un code absent du référentiel apparaît quand même, avec un
    libellé "(non référencée)", au lieu de disparaître des tableaux de bord.
#}
with codes as (

    select cod_cmp from {{ ref('stg_apogee__ins_adm_etp') }}
    union
    select cod_cmp from {{ ref('ref_etape') }}
    union
    select cod_cmp from {{ ref('ref_composante') }}

)

select
    c.cod_cmp,
    coalesce(r.lib_cmp, 'Composante ' || c.cod_cmp || ' (non référencée)') as lib_composante,
    coalesce(r.type_etablissement, 'Non renseigné')                         as type_etablissement,
    coalesce(r.mode_acces, 'Non renseigné')                                 as mode_acces,
    r.cod_cmp is not null                                                   as est_referencee
from codes as c
left join {{ ref('ref_composante') }} as r
    on r.cod_cmp = c.cod_cmp
where c.cod_cmp is not null