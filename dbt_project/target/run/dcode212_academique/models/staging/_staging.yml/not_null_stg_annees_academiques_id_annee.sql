
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_annee
from "etudiants_db"."public_staging"."stg_annees_academiques"
where id_annee is null



  
  
      
    ) dbt_internal_test