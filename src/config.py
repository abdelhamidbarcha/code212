"""
Configuration centralisée de la connexion au Data Warehouse.

Toutes les informations sensibles viennent des variables d'environnement
(fichier .env injecté par docker-compose). Aucun mot de passe dans le code.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

REQUIRED_VARS = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]


def get_db_url() -> str:
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        raise EnvironmentError(
            f"Variables d'environnement manquantes : {', '.join(missing)}. "
            "Vérifie le fichier .env et la section env_file de docker-compose.yml."
        )
    return (
        f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
    )


def get_engine() -> Engine:
    # pool_pre_ping : évite les erreurs de connexion "fermée" entre deux tâches Airflow
    return create_engine(get_db_url(), pool_pre_ping=True)