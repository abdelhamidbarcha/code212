{#
    Contrats pédagogiques nettoyés.
    Grain : une ligne par (étudiant, année, étape, version d'étape, module).
    Les doubles saisies sont éliminées (la plus ancienne est conservée) ;
    nb_saisies garde la trace du nombre de saisies dans la source.
#}
with source as (

    select * from {{ source('apogee', 'ind_contrat_elp') }}

),

nettoye as (

    select
        {{ nettoyer_code('cod_ind') }}                   as cod_ind,
        {{ nettoyer_code('cod_elp') }}                   as cod_elp,
        {{ convertir_entier('cod_anu') }}                as cod_anu,
        {{ nettoyer_code('cod_etp') }}                   as cod_etp,
        {{ nettoyer_code('cod_vrs_vet') }}               as cod_vrs_vet,
        {{ nettoyer_code('tem_prc_ice') }}               as tem_prc_ice,
        {{ convertir_horodatage('dat_cre_elp_con') }}    as dat_cre_elp_con,
        {{ convertir_horodatage('dat_mod_ice') }}        as dat_mod_ice,
        {{ nettoyer_code('cod_uti') }}                   as cod_uti,
        _source,
        _loaded_at
    from source

),

dedoublonne as (

    select
        *,
        count(*) over (
            partition by cod_ind, cod_anu, cod_etp, cod_vrs_vet, cod_elp
        ) as nb_saisies,
        row_number() over (
            partition by cod_ind, cod_anu, cod_etp, cod_vrs_vet, cod_elp
            order by dat_cre_elp_con, dat_mod_ice desc nulls last
        ) as rang
    from nettoye
    where cod_ind is not null
      and cod_anu is not null
      and cod_elp is not null

)

select
    cod_ind,
    cod_elp,
    cod_anu,
    cod_etp,
    cod_vrs_vet,
    tem_prc_ice,
    dat_cre_elp_con,
    dat_mod_ice,
    cod_uti,
    nb_saisies,
    _source,
    _loaded_at
from dedoublonne
where rang = 1