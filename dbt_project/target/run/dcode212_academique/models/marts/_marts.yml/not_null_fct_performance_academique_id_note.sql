
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_note
from "etudiants_db"."public_marts"."fct_performance_academique"
where id_note is null



  
  
      
    ) dbt_internal_test