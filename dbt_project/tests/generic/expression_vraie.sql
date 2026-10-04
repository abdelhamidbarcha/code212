{#
    Test générique : chaque ligne doit vérifier une expression SQL (règle métier).
    Les valeurs NULL ne sont pas considérées comme des erreurs.
    Usage :
      data_tests:
        - expression_vraie:
            expression: "cod_anu between 2000 and 2100"
#}
{% test expression_vraie(model, expression, column_name=none) %}
select *
from {{ model }}
where not ({{ expression }})
{% endtest %}