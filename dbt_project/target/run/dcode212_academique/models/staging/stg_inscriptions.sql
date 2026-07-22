
  create view "etudiants_db"."public_staging"."stg_inscriptions__dbt_tmp"
    
    
  as (
    with source as (
    select * from "etudiants_db"."public"."inscriptions"
)
select
    id_inscription::integer        as id_inscription,
    id_etudiant::integer           as id_etudiant,
    id_formation::integer          as id_formation,
    id_annee::integer              as id_annee,
    date_inscription::date         as date_inscription,
    trim(statut_inscription)       as statut_inscription,
    trim(mode)                     as mode
from source
  );