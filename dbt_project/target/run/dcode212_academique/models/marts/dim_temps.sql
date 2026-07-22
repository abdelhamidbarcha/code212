
  
    

  create  table "etudiants_db"."public_marts"."dim_temps__dbt_tmp"
  
  
    as
  
  (
    select
    id_annee,
    libelle    as annee_academique,
    semestre,
    date_debut,
    date_fin
from "etudiants_db"."public_staging"."stg_annees_academiques"
  );
  