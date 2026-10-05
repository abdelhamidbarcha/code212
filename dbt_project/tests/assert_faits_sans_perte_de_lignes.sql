{#
    Contrôle de non-régression : les tables de faits doivent contenir exactement
    le même nombre de lignes que la couche staging (aucune ligne perdue ni
    dupliquée par une jointure).
#}
select 'fct_inscription_administrative' as table_faits, s.nb as staging, f.nb as faits
from (select count(*) as nb from {{ ref('stg_apogee__ins_adm_etp') }}) as s,
     (select count(*) as nb from {{ ref('fct_inscription_administrative') }}) as f
where s.nb <> f.nb

union all

select 'fct_inscription_pedagogique', s.nb, f.nb
from (select count(*) as nb from {{ ref('stg_apogee__ind_contrat_elp') }}) as s,
     (select count(*) as nb from {{ ref('fct_inscription_pedagogique') }}) as f
where s.nb <> f.nb