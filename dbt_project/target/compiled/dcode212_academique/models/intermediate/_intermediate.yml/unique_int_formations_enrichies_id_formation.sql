
    
    

select
    id_formation as unique_field,
    count(*) as n_records

from "etudiants_db"."public_intermediate"."int_formations_enrichies"
where id_formation is not null
group by id_formation
having count(*) > 1


