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