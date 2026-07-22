
  
    

  create  table "etudiants_db"."public_marts"."dim_etudiant__dbt_tmp"
  
  
    as
  
  (
    select
    id_etudiant,
    matricule,
    nom_complet,
    age,
    tranche_age,
    sexe,
    nationalite,
    statut
from "etudiants_db"."public_intermediate"."int_etudiants_enrichis"
  );
  