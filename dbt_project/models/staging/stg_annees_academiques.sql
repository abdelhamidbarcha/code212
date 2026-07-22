with source as (
    select * from {{ source('raw', 'annees_academiques') }}
)
select
    id_annee::integer     as id_annee,
    trim(libelle)         as libelle,
    trim(semestre)        as semestre,
    date_debut::date      as date_debut,
    date_fin::date        as date_fin
from source
