
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_etudiant as unique_field,
    count(*) as n_records

from "etudiants_db"."public_intermediate"."int_etudiants_enrichis"
where id_etudiant is not null
group by id_etudiant
having count(*) > 1



  
  
      
    ) dbt_internal_test