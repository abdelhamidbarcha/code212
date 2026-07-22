
    
    

select
    id_etudiant as unique_field,
    count(*) as n_records

from "etudiants_db"."public_marts"."dim_etudiant"
where id_etudiant is not null
group by id_etudiant
having count(*) > 1


