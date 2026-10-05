{#
    Par défaut, dbt préfixe les schémas personnalisés par le schéma cible
    (ex : "public_staging"). Cette macro utilise directement le nom demandé
    (staging, intermediate, marts, referentiel) pour une base plus lisible.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}