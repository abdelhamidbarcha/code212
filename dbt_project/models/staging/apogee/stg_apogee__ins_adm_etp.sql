{#
    Inscriptions administratives nettoyées.
    Grain : une ligne par (étudiant, année universitaire, composante).
    En cas de doublon, l'inscription valide (ETA_IAE = 'E') est conservée.
#}
with source as (

    select * from {{ source('apogee', 'ins_adm_etp') }}

),

nettoye as (

    select
        {{ nettoyer_code('cod_ind') }}       as cod_ind,
        {{ convertir_entier('cod_anu') }}    as cod_anu,
        {{ nettoyer_code('eta_iae') }}       as eta_iae,
        {{ nettoyer_code('cod_cmp') }}       as cod_cmp,
        _source,
        _loaded_at
    from source

),

dedoublonne as (

    select
        *,
        count(*) over (partition by cod_ind, cod_anu, cod_cmp) as nb_saisies,
        row_number() over (
            partition by cod_ind, cod_anu, cod_cmp
            order by (eta_iae = 'E') desc, _loaded_at desc
        ) as rang
    from nettoye
    where cod_ind is not null
      and cod_anu is not null

)

select
    cod_ind,
    cod_anu,
    eta_iae,
    cod_cmp,
    nb_saisies,
    _source,
    _loaded_at
from dedoublonne
where rang = 1