#!/bin/bash
# Crée plusieurs bases de données au démarrage du conteneur Postgres
set -e

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
  echo "Création de plusieurs bases de données : $POSTGRES_MULTIPLE_DATABASES"
  for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
    echo "  -> Création de la base '$db'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
      CREATE DATABASE $db;
      GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
  done
fi
