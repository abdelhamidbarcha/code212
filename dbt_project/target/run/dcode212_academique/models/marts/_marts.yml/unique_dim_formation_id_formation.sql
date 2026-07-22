
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_formation as unique_field,
    count(*) as n_records

from "etudiants_db"."public_marts"."dim_formation"
where id_formation is not null
group by id_formation
having count(*) > 1



  
  
      
    ) dbt_internal_test