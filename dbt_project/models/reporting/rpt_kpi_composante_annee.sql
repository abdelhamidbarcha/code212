{#
    Indicateurs clés par composante et par année universitaire.

    Les taux sont fournis pour l'affichage en tableau. Pour un taux agrégé
    (ex : toute l'université), utiliser dans Superset le rapport des sommes,
    ex : SUM(femmes) / SUM(effectif), et non la moyenne des taux.
#}
with inscriptions as (

    select * from {{ ref('rpt_inscriptions_administratives') }}

),

comptabilisees as (

    select
        cod_anu,
        annee_universitaire,
        cod_cmp,
        composante,
        type_etablissement,
        count(distinct cod_ind)                                                         as effectif,
        count(distinct cod_ind) filter (where type_inscription = 'Nouvel inscrit')      as nouveaux_inscrits,
        count(distinct cod_ind) filter (where type_inscription = 'Réinscrit')           as reinscrits,
        count(distinct cod_ind) filter (where est_redoublant)                           as redoublants,
        count(distinct cod_ind) filter (where est_redoublant is not null)               as base_redoublement,
        count(distinct cod_ind) filter (where sexe = 'Femme')                           as femmes,
        count(distinct cod_ind) filter (where origine = 'Étudiant étranger')            as etrangers,
        count(distinct cod_ind) filter (where est_reinscrit_annee_suivante)             as reinscrits_annee_suivante,
        count(distinct cod_ind) filter (where est_reinscrit_annee_suivante is not null) as base_reinscription
    from inscriptions
    where est_comptabilise
    group by 1, 2, 3, 4, 5

),

non_comptabilisees as (

    select
        cod_anu,
        cod_cmp,
        count(*) filter (where etat_inscription = 'Annulée')  as inscriptions_annulees,
        count(*) filter (where etat_inscription = 'Résiliée') as inscriptions_resiliees
    from inscriptions
    where not est_comptabilise
    group by 1, 2

)

select
    k.*,
    coalesce(n.inscriptions_annulees, 0)                                          as inscriptions_annulees,
    coalesce(n.inscriptions_resiliees, 0)                                         as inscriptions_resiliees,

    lag(k.effectif) over (partition by k.cod_cmp order by k.cod_anu)              as effectif_annee_precedente,
    round(100.0 * (k.effectif - lag(k.effectif) over (partition by k.cod_cmp order by k.cod_anu))
          / nullif(lag(k.effectif) over (partition by k.cod_cmp order by k.cod_anu), 0), 1)
                                                                                  as evolution_effectif_pct,
    round(100.0 * k.femmes / nullif(k.effectif, 0), 1)                            as part_femmes_pct,
    round(100.0 * k.etrangers / nullif(k.effectif, 0), 1)                         as part_etrangers_pct,
    round(100.0 * k.nouveaux_inscrits / nullif(k.effectif, 0), 1)                 as part_nouveaux_pct,
    round(100.0 * k.redoublants / nullif(k.base_redoublement, 0), 1)              as taux_redoublement_pct,
    round(100.0 * k.reinscrits_annee_suivante / nullif(k.base_reinscription, 0), 1) as taux_reinscription_pct
from comptabilisees as k
left join non_comptabilisees as n
    on  n.cod_anu = k.cod_anu
    and n.cod_cmp = k.cod_cmp