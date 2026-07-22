
    
    

select
    id_note as unique_field,
    count(*) as n_records

from "etudiants_db"."public_marts"."fct_performance_academique"
where id_note is not null
group by id_note
having count(*) > 1


