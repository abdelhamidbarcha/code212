
    
    

with all_values as (

    select
        mention as value_field,
        count(*) as n_records

    from "etudiants_db"."public_intermediate"."int_notes_enrichies"
    group by mention

)

select *
from all_values
where value_field not in (
    'Insuffisant','Passable','Assez Bien','Bien','Très Bien'
)


