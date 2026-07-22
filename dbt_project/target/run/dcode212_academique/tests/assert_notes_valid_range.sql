
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  select id_note, note
from "etudiants_db"."public_staging"."stg_notes"
where note < 0 or note > 20
  
  
      
    ) dbt_internal_test