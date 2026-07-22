
  
    

  create  table "etudiants_db"."public_marts"."fct_performance_academique__dbt_tmp"
  
  
    as
  
  (
    with notes as (
    select * from "etudiants_db"."public_staging"."stg_notes"
),
cours as (
    select id_cours, id_formation, id_annee, credits_ects from "etudiants_db"."public_staging"."stg_cours"
)
select
    n.id_note,
    n.id_etudiant,
    n.id_cours,
    c.id_formation,
    n.id_annee,
    n.type_evaluation,
    n.note,
    c.credits_ects,
    n.date_evaluation,
    case
        when n.note < 10 then 'Insuffisant'
        when n.note < 12 then 'Passable'
        when n.note < 14 then 'Assez Bien'
        when n.note < 16 then 'Bien'
        else 'Très Bien'
    end                     as mention,
    (n.note >= 10)          as est_validee
from notes n
left join cours c on n.id_cours = c.id_cours
  );
  