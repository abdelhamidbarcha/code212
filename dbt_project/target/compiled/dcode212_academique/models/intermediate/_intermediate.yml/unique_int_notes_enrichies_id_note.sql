
    
    

select
    id_note as unique_field,
    count(*) as n_records

from "etudiants_db"."public_intermediate"."int_notes_enrichies"
where id_note is not null
group by id_note
having count(*) > 1


