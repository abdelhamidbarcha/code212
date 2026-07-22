
  create view "etudiants_db"."public_intermediate"."int_etudiants_enrichis__dbt_tmp"
    
    
  as (
    with etudiants as (
    select * from "etudiants_db"."public_staging"."stg_etudiants"
),
dedupliques as (
    select
        *,
        row_number() over (partition by id_etudiant order by id_etudiant) as rn
    from etudiants
    where id_etudiant is not null
),
enrichis as (
    select
        id_etudiant,
        matricule,
        nom,
        prenom,
        nom || ' ' || prenom                                        as nom_complet,
        date_naissance,
        date_part('year', age(current_date, date_naissance))::int   as age,
        sexe,
        nationalite,
        email,
        date_premiere_inscription,
        statut
    from dedupliques
    where rn = 1
)
select
    *,
    case
        when age < 20 then '18-19'
        when age < 23 then '20-22'
        when age < 26 then '23-25'
        else '26+'
    end as tranche_age
from enrichis
  );