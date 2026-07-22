with source as (
    select * from "etudiants_db"."public"."notes"
)
select
    id_note::integer             as id_note,
    id_etudiant::integer         as id_etudiant,
    id_cours::integer            as id_cours,
    id_annee::integer            as id_annee,
    trim(type_evaluation)        as type_evaluation,
    note::numeric(4,2)           as note,
    date_evaluation::date        as date_evaluation
from source