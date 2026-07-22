with source as (
    select * from {{ source('raw', 'inscriptions') }}
)
select
    id_inscription::integer        as id_inscription,
    id_etudiant::integer           as id_etudiant,
    id_formation::integer          as id_formation,
    id_annee::integer              as id_annee,
    date_inscription::date         as date_inscription,
    trim(statut_inscription)       as statut_inscription,
    trim(mode)                     as mode
from source
