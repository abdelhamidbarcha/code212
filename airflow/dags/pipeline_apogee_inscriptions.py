"""
Pipeline ELT — Pilotage des inscriptions (données Apogée)

    ingestion :  extract  ->  load
    dbt       :  référentiel -> fraîcheur -> staging -> marts -> reporting
    contrôle  :  rapport de qualité des données

Chaque couche dbt est construite puis testée (dbt build) avant de passer à la
suivante : si un test bloquant échoue, les couches suivantes ne sont pas
reconstruites et les tableaux de bord conservent la dernière version valide.
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import timedelta

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule

sys.path.append("/opt/airflow/src")

log = logging.getLogger(__name__)

# Variables d'environnement transmises aux commandes dbt (logs lisibles dans Airflow)
DBT_ENV = {"DBT_USE_COLORS": "false"}
# "cautious" : un test n'est lancé que si TOUS les modèles qu'il utilise sont dans la sélection
DBT_OPTIONS = "--indirect-selection cautious"

default_args = {
    "owner": "equipe-data",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def commande_dbt(task_id: str, commande: str, doc: str) -> BashOperator:
    return BashOperator(
        task_id=task_id,
        bash_command=commande,
        env=DBT_ENV,
        append_env=True,          # conserve DB_*, DBT_PROJECT_DIR, etc.
        doc_md=doc,
    )


@dag(
    dag_id="pipeline_apogee_inscriptions",
    description="ELT Apogée : génération/chargement des données, transformation dbt, contrôle qualité",
    schedule="0 6 * * *",                                        # tous les jours à 6h00
    start_date=pendulum.datetime(2026, 1, 1, tz="Africa/Casablanca"),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=1),
    default_args=default_args,
    tags=["apogee", "elt", "dbt", "inscriptions"],
    doc_md=__doc__,
)
def pipeline_apogee_inscriptions():

    # =================================================================
    #  1. INGESTION
    # =================================================================
    @task_group(group_id="ingestion")
    def ingestion():

        @task(doc_md="Génère les fichiers Apogée simulés (ignoré si ETL_SOURCE=apogee).")
        def extract():
            if os.getenv("ETL_SOURCE", "generateur") == "apogee":
                raise AirflowSkipException(
                    "Mode données réelles (ETL_SOURCE=apogee) : pas de génération, "
                    "les exports Apogée déposés dans data/raw seront chargés."
                )
            from extract import main
            main()

        @task(
            trigger_rule=TriggerRule.NONE_FAILED,   # s'exécute aussi quand extract est ignoré
            doc_md="Valide puis charge les 3 fichiers dans le schéma raw (transaction unique).",
        )
        def load():
            from load import main
            main()

        extract() >> load()

    # =================================================================
    #  2. TRANSFORMATION (dbt)
    # =================================================================
    @task_group(group_id="transformation_dbt")
    def transformation_dbt():
        referentiel = commande_dbt(
            "referentiel",
            f"dbt build --select resource_type:seed {DBT_OPTIONS}",
            "Charge et teste les nomenclatures (seeds).",
        )
        fraicheur = commande_dbt(
            "fraicheur_sources",
            "dbt source freshness",
            "Vérifie que les données sources sont récentes (alerte > 2 jours, erreur > 7 jours).",
        )
        staging = commande_dbt(
            "staging",
            f"dbt build --select source:apogee staging {DBT_OPTIONS}",
            "Nettoyage, typage, dédoublonnage + tests de qualité des sources.",
        )
        marts = commande_dbt(
            "marts",
            f"dbt build --select intermediate marts {DBT_OPTIONS}",
            "Parcours étudiants + modèle en étoile (dimensions et faits).",
        )
        reporting = commande_dbt(
            "reporting",
            f"dbt build --select reporting {DBT_OPTIONS}",
            "Tables prêtes pour Superset + module qualité.",
        )
        tests_transverses = commande_dbt(
            "tests_transverses",
            "dbt test --select test_type:singular",
            "Règles métier et contrôles de non-régression entre couches.",
        )

        referentiel >> fraicheur >> staging >> marts >> reporting >> tests_transverses

    # =================================================================
    #  3. CONTRÔLE QUALITÉ
    # =================================================================
    @task(doc_md="Affiche la synthèse des contrôles qualité dans les logs.")
    def rapport_qualite() -> dict:
        from sqlalchemy import text

        from config import get_engine

        requete = text("""
            select code_controle, libelle_controle, gravite, nb_anomalies,
                   taux_conformite_pct, statut
            from reporting.rpt_qualite_synthese
            order by code_controle
        """)
        with get_engine().connect() as connexion:
            lignes = connexion.execute(requete).mappings().all()

        log.info("=" * 100)
        log.info("RAPPORT DE QUALITÉ DES DONNÉES")
        log.info("=" * 100)
        for l in lignes:
            log.info("%s | %-58s | %-13s | %6d anomalie(s) | %6.2f %% conformes | %s",
                     l["code_controle"], l["libelle_controle"], l["gravite"],
                     l["nb_anomalies"], l["taux_conformite_pct"] or 0, l["statut"])

        critiques = [l for l in lignes if l["gravite"] == "Critique" and l["nb_anomalies"] > 0]
        for l in critiques:
            log.warning("ANOMALIE CRITIQUE : %s (%d)", l["libelle_controle"], l["nb_anomalies"])

        return {
            "controles": len(lignes),
            "controles_conformes": sum(1 for l in lignes if l["nb_anomalies"] == 0),
            "anomalies_totales": sum(l["nb_anomalies"] for l in lignes),
            "controles_critiques_en_echec": len(critiques),
        }

    ingestion() >> transformation_dbt() >> rapport_qualite()


pipeline_apogee_inscriptions()