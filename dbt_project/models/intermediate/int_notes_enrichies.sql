with notes as (
    select * from {{ ref('stg_notes') }}
),
etudiants as (
    select * from {{ ref('int_etudiants_enrichis') }}
),
cours as (
    select * from {{ ref('int_cours_enrichis') }}
),
enrichies as (
    select
        n.id_note,
        n.type_evaluation,
        n.note,
        n.date_evaluation,
        e.id_etudiant,
        e.nom_complet     as nom_etudiant,
        e.tranche_age,
        e.sexe,
        c.id_cours,
        c.intitule        as intitule_cours,
        c.credits_ects,
        c.nom_formation,
        c.nom_departement,
        c.nom_enseignant,
        c.annee_academique,
        c.semestre
    from notes n
    left join etudiants e on n.id_etudiant = e.id_etudiant
    left join cours c     on n.id_cours    = c.id_cours
)
select
    *,
    case
        when note < 10 then 'Insuffisant'
        when note < 12 then 'Passable'
        when note < 14 then 'Assez Bien'
        when note < 16 then 'Bien'
        else 'Très Bien'
    end                     as mention,
    (note >= 10)            as est_validee
from enrichies
