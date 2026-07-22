
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_enseignant as unique_field,
    count(*) as n_records

from "etudiants_db"."public_intermediate"."int_enseignants_enrichis"
where id_enseignant is not null
group by id_enseignant
having count(*) > 1



  
  
      
    ) dbt_internal_test