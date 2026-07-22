with cours as (
    select * from "etudiants_db"."public_staging"."stg_cours"
),
formations as (
    select * from "etudiants_db"."public_intermediate"."int_formations_enrichies"
),
enseignants as (
    select * from "etudiants_db"."public_intermediate"."int_enseignants_enrichis"
),
annees as (
    select * from "etudiants_db"."public_staging"."stg_annees_academiques"
)
select
    c.id_cours,
    c.code_cours,
    c.intitule,
    c.credits_ects,
    c.volume_horaire,
    f.id_formation,
    f.nom_formation,
    f.nom_departement,
    ens.id_enseignant,
    ens.nom_complet    as nom_enseignant,
    ens.grade          as grade_enseignant,
    a.id_annee,
    a.libelle          as annee_academique,
    a.semestre
from cours c
left join formations f  on c.id_formation  = f.id_formation
left join enseignants ens on c.id_enseignant = ens.id_enseignant
left join annees a      on c.id_annee       = a.id_annee