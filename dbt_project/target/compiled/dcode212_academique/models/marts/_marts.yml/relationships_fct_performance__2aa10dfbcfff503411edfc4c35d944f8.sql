
    
    

with child as (
    select id_cours as from_field
    from "etudiants_db"."public_marts"."fct_performance_academique"
    where id_cours is not null
),

parent as (
    select id_cours as to_field
    from "etudiants_db"."public_marts"."dim_cours"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


