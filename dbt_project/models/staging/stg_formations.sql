with source as (
    select * from {{ source('raw', 'formations') }}
)
select
    id_formation::integer     as id_formation,
    trim(nom_formation)       as nom_formation,
    id_departement::integer   as id_departement,
    trim(niveau)              as niveau,
    trim(type_diplome)        as type_diplome,
    duree_annees::smallint    as duree_annees
from source
