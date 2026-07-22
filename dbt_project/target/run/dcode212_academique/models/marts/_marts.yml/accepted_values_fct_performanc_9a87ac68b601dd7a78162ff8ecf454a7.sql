
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        mention as value_field,
        count(*) as n_records

    from "etudiants_db"."public_marts"."fct_performance_academique"
    group by mention

)

select *
from all_values
where value_field not in (
    'Insuffisant','Passable','Assez Bien','Bien','Très Bien'
)



  
  
      
    ) dbt_internal_test