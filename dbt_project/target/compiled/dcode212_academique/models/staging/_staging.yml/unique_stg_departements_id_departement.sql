
    
    

select
    id_departement as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_departements"
where id_departement is not null
group by id_departement
having count(*) > 1


