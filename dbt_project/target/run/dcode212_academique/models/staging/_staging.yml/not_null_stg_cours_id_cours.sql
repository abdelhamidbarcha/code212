
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_cours
from "etudiants_db"."public_staging"."stg_cours"
where id_cours is null



  
  
      
    ) dbt_internal_test