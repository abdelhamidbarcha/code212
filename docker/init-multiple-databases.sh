#!/bin/bash
# Crée les bases listées dans POSTGRES_MULTIPLE_DATABASES (séparées par des virgules).
# Exécuté automatiquement par l'image postgres au PREMIER démarrage du volume uniquement.
set -euo pipefail

create_database() {
    local database="$1"
    echo "[init] Création de la base '${database}' (si absente)"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<EOSQL
SELECT 'CREATE DATABASE ${database} OWNER ${POSTGRES_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${database}')\gexec
EOSQL
}

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        create_database "$db"
    done
    echo "[init] Bases créées : ${POSTGRES_MULTIPLE_DATABASES}"
fi


# Rôle en lecture seule pour Superset (accès limité au schéma reporting par dbt)
if [ -n "${BI_PASSWORD:-}" ]; then
    echo "[init] Création du rôle de lecture BI 'bi_lecteur'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<EOSQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'bi_lecteur') THEN
        CREATE ROLE bi_lecteur LOGIN PASSWORD '${BI_PASSWORD}';
    END IF;
END
\$\$;
GRANT CONNECT ON DATABASE etudiants_db TO bi_lecteur;
EOSQL
fi