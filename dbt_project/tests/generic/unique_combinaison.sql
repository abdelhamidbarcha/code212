{#
    Test générique : la combinaison de colonnes doit être unique (grain d'une table).
    Usage (au niveau du modèle) :
      data_tests:
        - unique_combinaison:
            colonnes: [cod_ind, cod_anu]
#}
{% test unique_combinaison(model, colonnes) %}
select
    {{ colonnes | join(', ') }},
    count(*) as nb_lignes
from {{ model }}
group by {{ colonnes | join(', ') }}
having count(*) > 1
{% endtest %}