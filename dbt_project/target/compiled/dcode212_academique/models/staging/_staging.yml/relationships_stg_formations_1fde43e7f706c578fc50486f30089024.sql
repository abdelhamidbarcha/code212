
    
    

with child as (
    select id_departement as from_field
    from "etudiants_db"."public_staging"."stg_formations"
    where id_departement is not null
),

parent as (
    select id_departement as to_field
    from "etudiants_db"."public_staging"."stg_departements"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


