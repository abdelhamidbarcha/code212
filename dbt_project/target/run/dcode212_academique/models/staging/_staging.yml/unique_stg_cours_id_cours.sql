
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_cours as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_cours"
where id_cours is not null
group by id_cours
having count(*) > 1



  
  
      
    ) dbt_internal_test