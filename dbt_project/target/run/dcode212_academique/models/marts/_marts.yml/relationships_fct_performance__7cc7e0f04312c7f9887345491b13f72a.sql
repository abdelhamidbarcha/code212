
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select id_etudiant as from_field
    from "etudiants_db"."public_marts"."fct_performance_academique"
    where id_etudiant is not null
),

parent as (
    select id_etudiant as to_field
    from "etudiants_db"."public_marts"."dim_etudiant"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test