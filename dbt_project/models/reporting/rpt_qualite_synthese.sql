{#
    Synthèse de la qualité des données : une ligne par contrôle du catalogue,
    y compris les contrôles sans anomalie (affichés "Conforme").
#}
with volumes as (

    select 'INDIVIDU' as table_source, count(*) as volume
    from {{ ref('stg_apogee__individu') }}
    union all
    select 'INS_ADM_ETP', count(*)
    from {{ ref('stg_apogee__ins_adm_etp') }}
    union all
    select 'IND_CONTRAT_ELP', count(*)
    from {{ ref('stg_apogee__ind_contrat_elp') }}

),

comptes as (

    select
        code_controle,
        count(*)                as nb_anomalies,
        count(distinct cod_ind) as nb_etudiants_concernes
    from {{ ref('rpt_anomalies_qualite') }}
    group by code_controle

)

select
    r.code_controle,
    r.libelle_controle,
    r.categorie,
    r.gravite,
    r.table_source,
    coalesce(c.nb_anomalies, 0)                                                as nb_anomalies,
    coalesce(c.nb_etudiants_concernes, 0)                                      as nb_etudiants_concernes,
    v.volume                                                                   as volume_controle,
    round(100.0 * coalesce(c.nb_anomalies, 0) / nullif(v.volume, 0), 2)        as taux_anomalie_pct,
    round(100 - 100.0 * coalesce(c.nb_anomalies, 0) / nullif(v.volume, 0), 2)  as taux_conformite_pct,
    case
        when coalesce(c.nb_anomalies, 0) = 0 then 'Conforme'
        when r.gravite = 'Critique'          then 'À corriger en priorité'
        when r.gravite = 'Avertissement'     then 'À surveiller'
        else 'Pour information'
    end                                                                        as statut
from {{ ref('ref_controle_qualite') }} as r
left join comptes as c
    on c.code_controle = r.code_controle
left join volumes as v
    on v.table_source = r.table_source