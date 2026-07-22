
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_note
from "etudiants_db"."public_intermediate"."int_notes_enrichies"
where id_note is null



  
  
      
    ) dbt_internal_test