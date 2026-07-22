
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_formation
from "etudiants_db"."public_staging"."stg_formations"
where id_formation is null



  
  
      
    ) dbt_internal_test