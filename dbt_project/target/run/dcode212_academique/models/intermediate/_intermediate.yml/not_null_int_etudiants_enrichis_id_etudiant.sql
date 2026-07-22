
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_etudiant
from "etudiants_db"."public_intermediate"."int_etudiants_enrichis"
where id_etudiant is null



  
  
      
    ) dbt_internal_test