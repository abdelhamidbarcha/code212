
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    matricule as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_etudiants"
where matricule is not null
group by matricule
having count(*) > 1



  
  
      
    ) dbt_internal_test