
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_inscription
from "etudiants_db"."public_intermediate"."int_inscriptions_enrichies"
where id_inscription is null



  
  
      
    ) dbt_internal_test