
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_enseignant
from "etudiants_db"."public_intermediate"."int_enseignants_enrichis"
where id_enseignant is null



  
  
      
    ) dbt_internal_test