
    
    

select
    id_annee as unique_field,
    count(*) as n_records

from "etudiants_db"."public_marts"."dim_temps"
where id_annee is not null
group by id_annee
having count(*) > 1


