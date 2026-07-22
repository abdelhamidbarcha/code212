with source as (
    select * from {{ source('raw', 'enseignants') }}
)
select
    id_enseignant::integer      as id_enseignant,
    trim(nom)                   as nom,
    trim(prenom)                as prenom,
    trim(grade)                 as grade,
    id_departement::integer     as id_departement,
    lower(trim(email))          as email,
    date_recrutement::date      as date_recrutement
from source
