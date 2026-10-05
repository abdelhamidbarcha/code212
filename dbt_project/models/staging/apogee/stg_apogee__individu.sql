{#
    Individus nettoyés : noms normalisés, codes en majuscules, dates typées,
    emails en minuscules, un seul enregistrement par COD_IND.
#}
with source as (

    select * from {{ source('apogee', 'individu') }}

),

nettoye as (

    select
        {{ nettoyer_code('cod_ind') }}                       as cod_ind,
        {{ nettoyer_code('cod_etu') }}                       as cod_etu,
        {{ nettoyer_code('numero_ine') }}                    as numero_ine,
        {{ nettoyer_code('cle_ine') }}                       as cle_ine,
        upper({{ nettoyer_texte('lib_nom_pat_ind') }})       as lib_nom_pat_ind,
        initcap({{ nettoyer_texte('lib_prenom_ind') }})      as lib_prenom_ind,
        {{ nettoyer_code('cod_sex_etu') }}                   as cod_sex_etu,
        {{ convertir_date('date_naissance') }}               as date_naissance,
        {{ nettoyer_texte('lib_vil_nai_etu') }}              as lib_vil_nai_etu,
        {{ completer_zeros('cod_pay_nai_etu', 3) }}          as cod_pay_nai_etu,
        {{ completer_zeros('cod_nat_etu', 3) }}              as cod_nat_etu,
        {{ completer_zeros('cod_dep_nai_etu', 3) }}          as cod_dep_nai_etu,
        lower({{ nettoyer_texte('adr_mail_etu') }})          as adr_mail_etu,
        _source,
        _loaded_at
    from source

),

dedoublonne as (

    select
        *,
        row_number() over (
            partition by cod_ind
            order by _loaded_at desc, cod_etu
        ) as rang
    from nettoye
    where cod_ind is not null

)

select
    cod_ind,
    cod_etu,
    numero_ine,
    cle_ine,
    lib_nom_pat_ind,
    lib_prenom_ind,
    cod_sex_etu,
    date_naissance,
    lib_vil_nai_etu,
    cod_pay_nai_etu,
    cod_nat_etu,
    cod_dep_nai_etu,
    adr_mail_etu,
    _source,
    _loaded_at
from dedoublonne
where rang = 1