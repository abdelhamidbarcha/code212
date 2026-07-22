
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select note
from "etudiants_db"."public_staging"."stg_notes"
where note is null



  
  
      
    ) dbt_internal_test