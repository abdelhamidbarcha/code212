
    
    

select
    matricule as unique_field,
    count(*) as n_records

from "etudiants_db"."public_staging"."stg_etudiants"
where matricule is not null
group by matricule
having count(*) > 1


