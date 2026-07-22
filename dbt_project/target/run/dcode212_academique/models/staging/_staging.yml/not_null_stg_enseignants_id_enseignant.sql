
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_enseignant
from "etudiants_db"."public_staging"."stg_enseignants"
where id_enseignant is null



  
  
      
    ) dbt_internal_test