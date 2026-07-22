
    
    

select
    id_enseignant as unique_field,
    count(*) as n_records

from "etudiants_db"."public_intermediate"."int_enseignants_enrichis"
where id_enseignant is not null
group by id_enseignant
having count(*) > 1


