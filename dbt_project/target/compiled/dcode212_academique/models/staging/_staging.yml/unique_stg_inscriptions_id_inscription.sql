
    
    

select
    id_inscription as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_inscriptions"
where id_inscription is not null
group by id_inscription
having count(*) > 1


