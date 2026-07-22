
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_cours
from "etudiants_db"."public_intermediate"."int_cours_enrichis"
where id_cours is null



  
  
      
    ) dbt_internal_test