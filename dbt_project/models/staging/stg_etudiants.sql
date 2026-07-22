with source as (
    select * from {{ source('raw', 'etudiants') }}
)
select
    id_etudiant::integer                    as id_etudiant,
    trim(matricule)                         as matricule,
    trim(nom)                               as nom,
    trim(prenom)                            as prenom,
    date_naissance::date                    as date_naissance,
    upper(trim(sexe))                       as sexe,
    trim(nationalite)                       as nationalite,
    lower(trim(email))                      as email,
    date_premiere_inscription::date         as date_premiere_inscription,
    trim(statut)                            as statut
from source
