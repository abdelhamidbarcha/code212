with source as (
    select * from "etudiants_db"."public"."cours"
)
select
    id_cours::integer          as id_cours,
    trim(code_cours)           as code_cours,
    trim(intitule)             as intitule,
    credits_ects::smallint     as credits_ects,
    id_formation::integer      as id_formation,
    id_enseignant::integer     as id_enseignant,
    id_annee::integer          as id_annee,
    volume_horaire::smallint   as volume_horaire
from source