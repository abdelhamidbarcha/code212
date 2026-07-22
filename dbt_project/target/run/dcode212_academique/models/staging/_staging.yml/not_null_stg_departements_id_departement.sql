
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_departement
from "etudiants_db"."public_staging"."stg_departements"
where id_departement is null



  
  
      
    ) dbt_internal_test