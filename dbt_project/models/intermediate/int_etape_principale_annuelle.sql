{#
    Étape principale de chaque étudiant pour chaque année universitaire.

    INS_ADM_ETP ne contient pas l'étape : elle est déduite des contrats
    pédagogiques (IND_CONTRAT_ELP). Si un étudiant est inscrit dans plusieurs
    étapes la même année, l'étape principale est celle qui compte le plus de
    modules (puis le niveau le plus élevé).
    Grain : une ligne par (cod_ind, cod_anu).
#}
with contrats as (

    select cod_ind, cod_anu, cod_etp, cod_vrs_vet
    from {{ ref('stg_apogee__ind_contrat_elp') }}
    where cod_etp is not null

),

niveaux as (

    select distinct cod_etp, annee_etude
    from {{ ref('ref_etape') }}

),

par_etape as (

    select
        c.cod_ind,
        c.cod_anu,
        c.cod_etp,
        c.cod_vrs_vet,
        max(n.annee_etude) as annee_etude,
        count(*)           as nb_modules
    from contrats as c
    left join niveaux as n
        on n.cod_etp = c.cod_etp
    group by 1, 2, 3, 4

),

classe as (

    select
        *,
        row_number() over (
            partition by cod_ind, cod_anu
            order by nb_modules desc, annee_etude desc nulls last, cod_etp
        )                                                  as rang,
        count(*) over (partition by cod_ind, cod_anu)        as nb_etapes,
        sum(nb_modules) over (partition by cod_ind, cod_anu) as nb_modules_total
    from par_etape

)

select
    cod_ind,
    cod_anu,
    cod_etp,
    cod_vrs_vet,
    cod_etp || '-' || coalesce(cod_vrs_vet, '?') as cle_etape,
    nb_modules_total::integer                    as nb_modules,
    nb_etapes::integer                           as nb_etapes
from classe
where rang = 1