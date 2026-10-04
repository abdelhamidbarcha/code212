{#
    Dimension temps : années universitaires présentes dans les données.
    COD_ANU = année de début (2024 => "2024-2025").
#}
with annees as (

    select cod_anu from {{ ref('stg_apogee__ins_adm_etp') }}
    union
    select cod_anu from {{ ref('stg_apogee__ind_contrat_elp') }}

)

select
    cod_anu,
    cod_anu::text || '-' || (cod_anu + 1)::text      as lib_annee_universitaire,
    make_date(cod_anu, 9, 1)                         as date_debut,
    make_date(cod_anu + 1, 7, 31)                    as date_fin,
    cod_anu = max(cod_anu) over ()                   as est_derniere_annee,
    (dense_rank() over (order by cod_anu desc) - 1)::integer as anciennete
from annees