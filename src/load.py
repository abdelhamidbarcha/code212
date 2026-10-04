"""
LOAD — Charge les exports Apogée (CSV) dans le schéma raw de PostgreSQL.

Approche ELT : aucune transformation métier ici. La donnée est chargée telle
quelle ; le nettoyage, le typage et les contrôles qualité sont réalisés par dbt.

Garanties :
  * Le schéma raw est créé / mis à jour automatiquement (sql/init.sql, idempotent).
  * Contrôle de structure : les colonnes de chaque fichier doivent correspondre
    au référentiel Apogée, sinon le chargement est refusé avec un message clair.
    Les fichiers sont tous validés AVANT de toucher la base.
  * Chargement ATOMIQUE : les 3 tables sont vidées et rechargées dans une seule
    transaction. En cas d'erreur, rien n'est modifié : les tableaux de bord ne
    voient jamais de données à moitié chargées.
  * Chargement rapide via COPY (commande native de PostgreSQL).
  * Chaque chargement est historisé dans raw.journal_chargement.

Variables d'environnement (optionnelles) :
  ETL_SOURCE     origine des données : generateur (défaut) / apogee
  CSV_ENCODING   encodage des fichiers (défaut utf-8 ; ex : latin-1 pour un export Oracle)
  CSV_DELIMITER  séparateur de colonnes (défaut "," ; ex : ";")
"""
import csv
import io
import os
import sys
import time
from pathlib import Path

from config import get_engine

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = Path(os.getenv("RAW_DIR", str(ROOT / "data" / "raw")))
INIT_SQL = ROOT / "sql" / "init.sql"

SOURCE = os.getenv("ETL_SOURCE", "generateur")
ENCODING = os.getenv("CSV_ENCODING", "utf-8")
DELIMITER = os.getenv("CSV_DELIMITER", ",")

# Colonnes attendues pour chaque table (référentiel Apogée, en minuscules)
TABLES = {
    "individu": ["cod_ind", "cod_etu", "numero_ine", "cle_ine", "lib_nom_pat_ind", "lib_prenom_ind",
                 "cod_sex_etu", "date_naissance", "lib_vil_nai_etu", "cod_pay_nai_etu", "cod_nat_etu",
                 "cod_dep_nai_etu", "adr_mail_etu"],
    "ins_adm_etp": ["cod_ind", "cod_anu", "eta_iae", "cod_cmp"],
    "ind_contrat_elp": ["cod_ind", "cod_elp", "cod_anu", "cod_etp", "cod_vrs_vet", "tem_prc_ice",
                        "dat_cre_elp_con", "dat_mod_ice", "cod_uti"],
}


class ErreurChargement(Exception):
    """Erreur fonctionnelle (fichier absent, structure incorrecte, volumétrie incohérente)."""


# =====================================================================
#  1. Lecture et validation d'un fichier
# =====================================================================
def preparer_fichier(table: str, colonnes: list[str]) -> tuple[io.StringIO, int]:
    """Valide la structure du CSV et le convertit en flux prêt pour COPY
    (colonnes remises dans l'ordre attendu + colonne technique _source)."""
    chemin = RAW_DIR / f"{table}.csv"
    if not chemin.exists():
        raise ErreurChargement(
            f"Fichier introuvable : {chemin}. Lance extract.py ou dépose l'export Apogée dans {RAW_DIR}."
        )

    flux = io.StringIO()
    writer = csv.writer(flux, lineterminator="\n")
    with open(chemin, newline="", encoding=ENCODING) as fh:
        reader = csv.reader(fh, delimiter=DELIMITER)
        entete = [c.strip().lower() for c in next(reader, [])]

        manquantes = [c for c in colonnes if c not in entete]
        if manquantes:
            raise ErreurChargement(
                f"{chemin.name} : colonnes manquantes {manquantes}. Colonnes trouvées : {entete}"
            )
        en_trop = [c for c in entete if c not in colonnes]
        if en_trop:
            print(f"[LOAD]   {chemin.name} : colonnes non utilisées ignorées {en_trop}")

        positions = [entete.index(c) for c in colonnes]
        nb_lignes = 0
        for num_ligne, ligne in enumerate(reader, start=2):
            if not any(valeur.strip() for valeur in ligne):
                continue                                   # ligne vide
            if len(ligne) != len(entete):
                raise ErreurChargement(
                    f"{chemin.name}, ligne {num_ligne} : {len(ligne)} champs au lieu de {len(entete)}."
                )
            writer.writerow([ligne[p] for p in positions] + [SOURCE])
            nb_lignes += 1

    flux.seek(0)
    return flux, nb_lignes


# =====================================================================
#  2. Chargement en base
# =====================================================================
def charger(fichiers: dict[str, tuple[io.StringIO, int]]) -> None:
    connexion = get_engine().raw_connection()
    try:
        # Création / mise à jour du schéma (idempotent)
        with connexion.cursor() as cur:
            cur.execute(INIT_SQL.read_text(encoding="utf-8"))
        connexion.commit()

        # Rechargement complet dans UNE seule transaction
        with connexion.cursor() as cur:
            cur.execute("TRUNCATE " + ", ".join(f"raw.{t}" for t in TABLES))
            for table, colonnes in TABLES.items():
                flux, attendues = fichiers[table]
                liste_colonnes = ", ".join(colonnes + ["_source"])
                cur.copy_expert(f"COPY raw.{table} ({liste_colonnes}) FROM STDIN WITH (FORMAT csv)", flux)

                cur.execute(f"SELECT count(*) FROM raw.{table}")
                chargees = cur.fetchone()[0]
                if chargees != attendues:
                    raise ErreurChargement(f"raw.{table} : {chargees} lignes en base au lieu de {attendues}.")

                cur.execute(
                    "INSERT INTO raw.journal_chargement (table_cible, fichier, nb_lignes, source) "
                    "VALUES (%s, %s, %s, %s)",
                    (table, f"{table}.csv", chargees, SOURCE),
                )
                print(f"[LOAD] raw.{table:<16} -> {chargees:>7} lignes chargées")
        connexion.commit()

        # Mise à jour des statistiques pour l'optimiseur (accélère dbt)
        with connexion.cursor() as cur:
            for table in TABLES:
                cur.execute(f"ANALYZE raw.{table}")
        connexion.commit()
    except Exception:
        connexion.rollback()
        print("[LOAD] Échec : rollback effectué, aucune donnée n'a été modifiée.")
        raise
    finally:
        connexion.close()


def main() -> None:
    debut = time.time()
    print(f"[LOAD] Source : {SOURCE} | Dossier : {RAW_DIR} | Encodage : {ENCODING} | Séparateur : '{DELIMITER}'")

    # Toutes les validations AVANT de toucher la base
    fichiers = {}
    for table, colonnes in TABLES.items():
        fichiers[table] = preparer_fichier(table, colonnes)
        print(f"[LOAD] {table}.csv validé ({fichiers[table][1]} lignes)")

    charger(fichiers)
    total = sum(n for _, n in fichiers.values())
    print(f"[LOAD] Terminé : {total} lignes chargées dans {len(TABLES)} tables en {time.time() - debut:.1f} s.")


if __name__ == "__main__":
    try:
        main()
    except ErreurChargement as erreur:
        print(f"[LOAD] ERREUR : {erreur}")
        sys.exit(1)