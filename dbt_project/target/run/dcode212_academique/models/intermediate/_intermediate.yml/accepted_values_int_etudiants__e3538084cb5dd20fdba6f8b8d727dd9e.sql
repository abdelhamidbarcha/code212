
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        tranche_age as value_field,
        count(*) as n_records

    from "etudiants_db"."public_intermediate"."int_etudiants_enrichis"
    group by tranche_age

)

select *
from all_values
where value_field not in (
    '18-19','20-22','23-25','26+'
)



  
  
      
    ) dbt_internal_test