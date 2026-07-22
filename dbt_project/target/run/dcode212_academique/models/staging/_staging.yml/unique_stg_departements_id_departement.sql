
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_departement as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_departements"
where id_departement is not null
group by id_departement
having count(*) > 1



  
  
      
    ) dbt_internal_test