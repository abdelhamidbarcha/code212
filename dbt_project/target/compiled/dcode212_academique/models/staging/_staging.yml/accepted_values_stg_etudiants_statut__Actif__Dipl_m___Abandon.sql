
    
    

with all_values as (

    select
        statut as value_field,
        count(*) as n_records

    from "etudiants_db"."public_staging"."stg_etudiants"
    group by statut

)

select *
from all_values
where value_field not in (
    'Actif','Diplômé','Abandon'
)


