{#
    Macros de nettoyage utilisées par la couche staging.
    Elles sont "défensives" : une valeur inattendue devient NULL au lieu de
    faire échouer le pipeline ; les tests dbt signalent ensuite le problème.
#}

{# Texte libre : espaces multiples réduits, espaces en bord supprimés, '' -> NULL #}
{% macro nettoyer_texte(colonne) -%}
    nullif(trim(regexp_replace({{ colonne }}, '\s+', ' ', 'g')), '')
{%- endmacro %}

{# Code : texte nettoyé et mis en majuscules #}
{% macro nettoyer_code(colonne) -%}
    upper({{ nettoyer_texte(colonne) }})
{%- endmacro %}

{# Code numérique complété par des zéros à gauche (ex : '1' -> '001') #}
{% macro completer_zeros(colonne, longueur) -%}
    case
        when {{ nettoyer_code(colonne) }} ~ '^\d+$'
             and length({{ nettoyer_code(colonne) }}) < {{ longueur }}
            then lpad({{ nettoyer_code(colonne) }}, {{ longueur }}, '0')
        else {{ nettoyer_code(colonne) }}
    end
{%- endmacro %}

{# Entier : NULL si la valeur n'est pas un nombre entier #}
{% macro convertir_entier(colonne) -%}
    case when trim({{ colonne }}) ~ '^-?\d+$' then trim({{ colonne }})::integer end
{%- endmacro %}

{# Date : accepte AAAA-MM-JJ, JJ/MM/AAAA et JJ/MM/AA (formats d'export Apogée / Oracle) #}
{% macro convertir_date(colonne) -%}
    case
        when trim({{ colonne }}) ~ '^\d{4}-\d{2}-\d{2}'      then to_date(left(trim({{ colonne }}), 10), 'YYYY-MM-DD')
        when trim({{ colonne }}) ~ '^\d{2}/\d{2}/\d{4}'      then to_date(left(trim({{ colonne }}), 10), 'DD/MM/YYYY')
        when trim({{ colonne }}) ~ '^\d{2}/\d{2}/\d{2}(\s|$)' then to_date(left(trim({{ colonne }}), 8), 'DD/MM/YY')
    end
{%- endmacro %}

{# Horodatage : mêmes formats que convertir_date, avec ou sans heure #}
{% macro convertir_horodatage(colonne) -%}
    case
        when trim({{ colonne }}) ~ '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            then to_timestamp(left(trim({{ colonne }}), 19), 'YYYY-MM-DD HH24:MI:SS')::timestamp
        when trim({{ colonne }}) ~ '^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'
            then to_timestamp(left(trim({{ colonne }}), 19), 'DD/MM/YYYY HH24:MI:SS')::timestamp
        else {{ convertir_date(colonne) }}::timestamp
    end
{%- endmacro %}