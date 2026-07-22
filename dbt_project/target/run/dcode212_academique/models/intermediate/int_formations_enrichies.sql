
  create view "etudiants_db"."public_intermediate"."int_formations_enrichies__dbt_tmp"
    
    
  as (
    with formations as (
    select * from "etudiants_db"."public_staging"."stg_formations"
),
departements as (
    select * from "etudiants_db"."public_staging"."stg_departements"
)
select
    f.id_formation,
    f.nom_formation,
    f.niveau,
    f.type_diplome,
    f.duree_annees,
    d.id_departement,
    d.nom_departement,
    d.faculte
from formations f
left join departements d on f.id_departement = d.id_departement
  );