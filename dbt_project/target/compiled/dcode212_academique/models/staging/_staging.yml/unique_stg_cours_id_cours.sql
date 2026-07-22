
    
    

select
    id_cours as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_cours"
where id_cours is not null
group by id_cours
having count(*) > 1


