
    
    

with child as (
    select id_annee as from_field
    from "etudiants_db"."public_marts"."fct_performance_academique"
    where id_annee is not null
),

parent as (
    select id_annee as to_field
    from "etudiants_db"."public_marts"."dim_temps"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


