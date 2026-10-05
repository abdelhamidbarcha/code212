{#
    Donne au rôle de lecture BI (Superset) l'accès en lecture au schéma reporting,
    et UNIQUEMENT à celui-ci (raw, staging et marts restent inaccessibles).
    Exécutée automatiquement à la fin de chaque commande dbt (on-run-end).
    Sans effet si le rôle ou le schéma n'existe pas encore.
#}
{% macro accorder_acces_bi() %}
    {% set role = var('role_bi') %}
    do $$
    begin
        if exists (select 1 from pg_roles where rolname = '{{ role }}')
           and exists (select 1 from information_schema.schemata where schema_name = 'reporting')
        then
            execute 'grant usage on schema reporting to {{ role }}';
            execute 'grant select on all tables in schema reporting to {{ role }}';
        end if;
    end
    $$;
{% endmacro %}