import os

SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "change_moi_en_production")

# Base de métadonnées PROPRE à Superset (dashboards, connexions, utilisateurs) —
# distincte de etudiants_db (le Data Warehouse) et de postgres (base par défaut).
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'postgres')}:{os.getenv('DB_PORT', '5432')}/superset_db"
)

FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
}