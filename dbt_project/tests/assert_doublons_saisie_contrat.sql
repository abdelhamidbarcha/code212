{{ config(severity='warn') }}
{#
    Contrôle qualité : contrats pédagogiques saisis plusieurs fois à l'identique
    dans la source. Les doublons sont éliminés en staging (une seule ligne conservée),
    ce test les signale pour correction à la source.
#}
select
    cod_ind,
    cod_anu,
    cod_etp,
    cod_vrs_vet,
    cod_elp,
    nb_saisies
from {{ ref('stg_apogee__ind_contrat_elp') }}
where nb_saisies > 1