
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_annee as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_annees_academiques"
where id_annee is not null
group by id_annee
having count(*) > 1



  
  
      
    ) dbt_internal_test