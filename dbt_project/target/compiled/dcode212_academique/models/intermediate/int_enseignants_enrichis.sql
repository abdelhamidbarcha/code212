with enseignants as (
    select * from "etudiants_db"."public_staging"."stg_enseignants"
),
departements as (
    select * from "etudiants_db"."public_staging"."stg_departements"
)
select
    e.id_enseignant,
    e.nom,
    e.prenom,
    e.nom || ' ' || e.prenom    as nom_complet,
    e.grade,
    e.email,
    e.date_recrutement,
    d.id_departement,
    d.nom_departement
from enseignants e
left join departements d on e.id_departement = d.id_departement