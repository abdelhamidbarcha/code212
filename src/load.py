"""
LOAD — Charge les 8 tables brutes (CSV générés par extract.py) dans PostgreSQL.

Approche ELT : aucune transformation ici. La donnée est chargée telle quelle ;
le nettoyage et les jointures seront réalisés plus tard par dbt (SQL Pushdown).

L'ordre de chargement respecte les dépendances de clés étrangères :
  1. Tables de référence indépendantes : departements, annees_academiques, etudiants
  2. Tables dépendantes de niveau 1  : formations, enseignants
  3. Tables dépendantes de niveau 2  : cours
  4. Tables de faits (dépendent de tout le reste) : inscriptions, notes
"""
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# Ordre de chargement : respecte strictement les dépendances de clés étrangères
LOAD_ORDER = [
    "departements",
    "annees_academiques",
    "etudiants",
    "formations",
    "enseignants",
    "cours",
    "inscriptions",
    "notes",
]


def get_engine() -> Engine:
    user = "etudiants_user"
    password = "etudiantscode212_passcode"
    host = "postgres"
    port = "5432"
    name = "etudiants_db"
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url)


def truncate_all(engine: Engine) -> None:
    """Vide les tables dans l'ordre inverse (enfants d'abord) pour éviter
    les erreurs de contrainte FK lors d'un rechargement complet (idempotence)."""
    with engine.begin() as conn:
        for table in reversed(LOAD_ORDER):
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
    print("[LOAD] Tables vidées (TRUNCATE CASCADE) avant rechargement.")


def load_table(engine: Engine, table_name: str) -> int:
    csv_path = RAW_DIR / f"{table_name}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {csv_path}. As-tu bien lancé extract.py avant load.py ?"
        )

    df = pd.read_csv(csv_path)
    df.to_sql(
        table_name,
        engine,
        if_exists="append",   # les tables existent déjà (créées par sql/init.sql)
        index=False,
        method="multi",
        chunksize=500,
    )
    return len(df)


def main() -> None:
    engine = get_engine()

    # Vérifie que la connexion fonctionne avant de commencer
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"[LOAD] Impossible de se connecter à PostgreSQL : {e}")
        sys.exit(1)

    truncate_all(engine)

    total = 0
    for table_name in LOAD_ORDER:
        try:
            n = load_table(engine, table_name)
            total += n
            print(f"[LOAD] {table_name:<20} -> {n:>6} lignes chargées")
        except Exception as e:
            print(f"[LOAD] ERREUR sur la table '{table_name}' : {e}")
            sys.exit(1)

    print(f"[LOAD] Terminé — {total} lignes chargées au total dans {len(LOAD_ORDER)} tables.")


if __name__ == "__main__":
    main()
