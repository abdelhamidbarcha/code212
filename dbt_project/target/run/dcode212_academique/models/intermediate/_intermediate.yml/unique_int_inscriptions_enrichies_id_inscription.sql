
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_inscription as unique_field,
    count(*) as n_records

from "etudiants_db"."public_intermediate"."int_inscriptions_enrichies"
where id_inscription is not null
group by id_inscription
having count(*) > 1



  
  
      
    ) dbt_internal_test