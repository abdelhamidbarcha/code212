{{ config(severity='warn') }}
{#
    Règle métier : un étudiant ne peut avoir de contrat pédagogique (IND_CONTRAT_ELP)
    une année donnée que s'il possède une inscription administrative (INS_ADM_ETP)
    la même année. Chaque ligne retournée est une anomalie à corriger dans Apogée.
#}
select distinct
    c.cod_ind,
    c.cod_anu
from {{ ref('stg_apogee__ind_contrat_elp') }} as c
left join {{ ref('stg_apogee__ins_adm_etp') }} as i
    on  i.cod_ind = c.cod_ind
    and i.cod_anu = c.cod_anu
where i.cod_ind is null