
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_note as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_notes"
where id_note is not null
group by id_note
having count(*) > 1



  
  
      
    ) dbt_internal_test