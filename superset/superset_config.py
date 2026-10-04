import os

SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "change_moi_en_production")

# Base de métadonnées PROPRE à Superset (dashboards, connexions, utilisateurs) —
# distincte de etudiants_db (le Data Warehouse).
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'postgres')}:{os.getenv('DB_PORT', '5432')}/superset_db"
)

APP_NAME = "Pilotage des inscriptions"

# Interface en français
BABEL_DEFAULT_LOCALE = "fr"
LANGUAGES = {
    "fr": {"flag": "fr", "name": "Français"},
    "en": {"flag": "us", "name": "English"},
}

# Nombres au format français : 4 586 et 12,5
D3_FORMAT = {
    "decimal": ",",
    "thousands": " ",
    "grouping": [3],
    "currency": ["", " MAD"],
}

FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
}