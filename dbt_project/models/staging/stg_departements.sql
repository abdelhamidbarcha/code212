with source as (
    select * from {{ source('raw', 'departements') }}
)
select
    id_departement::integer                as id_departement,
    trim(nom_departement)                  as nom_departement,
    trim(faculte)                          as faculte,
    trim(responsable)                      as responsable
from source
