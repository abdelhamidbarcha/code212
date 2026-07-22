
  
    

  create  table "etudiants_db"."public_marts"."dim_formation__dbt_tmp"
  
  
    as
  
  (
    select
    id_formation,
    nom_formation,
    niveau,
    type_diplome,
    duree_annees,
    nom_departement,
    faculte
from "etudiants_db"."public_intermediate"."int_formations_enrichies"
  );
  