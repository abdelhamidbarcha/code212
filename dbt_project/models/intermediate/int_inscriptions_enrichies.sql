with inscriptions as (
    select * from {{ ref('stg_inscriptions') }}
),
etudiants as (
    select * from {{ ref('int_etudiants_enrichis') }}
),
formations as (
    select * from {{ ref('int_formations_enrichies') }}
),
annees as (
    select * from {{ ref('stg_annees_academiques') }}
)
select
    i.id_inscription,
    i.date_inscription,
    i.statut_inscription,
    i.mode,
    e.id_etudiant,
    e.nom_complet          as nom_etudiant,
    e.tranche_age,
    e.sexe,
    e.statut               as statut_etudiant,
    f.id_formation,
    f.nom_formation,
    f.nom_departement,
    a.id_annee,
    a.libelle              as annee_academique,
    a.semestre
from inscriptions i
left join etudiants e  on i.id_etudiant  = e.id_etudiant
left join formations f on i.id_formation = f.id_formation
left join annees a     on i.id_annee     = a.id_annee
