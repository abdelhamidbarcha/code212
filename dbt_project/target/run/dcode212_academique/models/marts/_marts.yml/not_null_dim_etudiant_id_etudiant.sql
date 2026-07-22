
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_etudiant
from "etudiants_db"."public_marts"."dim_etudiant"
where id_etudiant is null



  
  
      
    ) dbt_internal_test