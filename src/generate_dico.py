"""
Génère le DICTIONNAIRE DE DONNÉES du Data Warehouse (classeur Excel).

Le dictionnaire est construit automatiquement à partir du catalogue PostgreSQL :
tables, colonnes, types et descriptions (les descriptions dbt sont copiées en
commentaires PostgreSQL grâce à persist_docs). Il est donc toujours à jour.

Onglets :
  1. Sommaire       : une ligne par table (couche, description, volumétrie)
  2. Dictionnaire   : une ligne par colonne (type, description) — filtrable
  3. Indicateurs    : définition des indicateurs des tableaux de bord
  4. Contrôles      : catalogue des contrôles de qualité

Usage : python src/generate_dico.py   (fichier produit : docs/Dictionnaire_de_donnees.xlsx)
"""
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from sqlalchemy import text

from config import get_engine

SORTIE = Path(__file__).resolve().parents[1] / "docs" / "Dictionnaire_de_donnees.xlsx"

COUCHES = {
    "raw":          ("1. Données brutes",   "Exports Apogée chargés tels quels"),
    "referentiel":  ("2. Référentiel",      "Nomenclatures (libellés des codes)"),
    "staging":      ("3. Staging",          "Données nettoyées, typées et dédoublonnées"),
    "intermediate": ("4. Intermédiaire",    "Logique métier (parcours, étape principale)"),
    "marts":        ("5. Marts",            "Modèle en étoile : dimensions et faits"),
    "reporting":    ("6. Reporting",        "Tables exposées à Superset"),
}

INDICATEURS = [
    ("Effectif", "Nombre d'étudiants distincts ayant une inscription administrative valide (ETA_IAE = E).",
     "COUNT(DISTINCT cod_ind) WHERE est_comptabilise"),
    ("Nouveaux inscrits", "Étudiants dont c'est la première inscription observée (non calculable pour la première année de l'historique).",
     "type_inscription = 'Nouvel inscrit'"),
    ("Taux de redoublement", "Part des étudiants inscrits dans la même étape que l'année précédente.",
     "redoublants / étudiants dont l'année précédente est connue"),
    ("Taux de réinscription", "Part des étudiants de l'année N à nouveau inscrits en N+1.",
     "réinscrits en N+1 / étudiants de N (hors dernière année)"),
    ("Taux de sortie en cours de cycle", "Part des étudiants quittant l'université avant la fin de leur cycle (abandon probable).",
     "statut_annee_suivante = 'Sortie en cours de cycle'"),
    ("Part des femmes / des étrangers", "Part des étudiantes / des étudiants de nationalité non marocaine dans l'effectif.",
     "femmes (ou étrangers) / effectif"),
    ("Inscriptions aux modules", "Nombre de contrats pédagogiques (un étudiant inscrit à un module).",
     "COUNT(*) sur rpt_inscriptions_pedagogiques"),
    ("Saisie automatique", "Part des contrats créés par un traitement Apogée en masse (utilisateur batch).",
     "type_saisie = 'Automatique'"),
    ("Taux de prise en compte", "Part des contrats retenus pour le calcul des résultats (TEM_PRC_ICE = O).",
     "est_pris_en_compte"),
    ("Score de qualité", "Moyenne des taux de conformité des contrôles qualité.",
     "AVG(taux_conformite_pct)"),
]

# --------------------------------------------------------------------- styles
BLEU, GRIS, BLANC = "1F3864", "F2F2F2", "FFFFFF"
POLICE = "Calibri"
f_titre = Font(name=POLICE, bold=True, color=BLEU, size=16)
f_sous_titre = Font(name=POLICE, italic=True, color="595959", size=10)
f_entete = Font(name=POLICE, bold=True, color=BLANC, size=11)
f_normal = Font(name=POLICE, size=10)
fond_entete = PatternFill("solid", start_color=BLEU, end_color=BLEU)
fond_gris = PatternFill("solid", start_color=GRIS, end_color=GRIS)
trait = Side(style="thin", color="BFBFBF")
bordure = Border(left=trait, right=trait, top=trait, bottom=trait)


def ecrire_tableau(ws, titre, entetes, lignes, largeurs):
    ws.sheet_view.showGridLines = False
    ws["A1"] = titre
    ws["A1"].font = f_titre
    ws["A2"] = f"Généré automatiquement le {datetime.now():%d/%m/%Y à %H:%M}"
    ws["A2"].font = f_sous_titre

    ligne_entete = 4
    for c, valeur in enumerate(entetes, start=1):
        cellule = ws.cell(row=ligne_entete, column=c, value=valeur)
        cellule.font, cellule.fill, cellule.border = f_entete, fond_entete, bordure
        cellule.alignment = Alignment(vertical="center", wrap_text=True)

    for r, ligne in enumerate(lignes, start=ligne_entete + 1):
        for c, valeur in enumerate(ligne, start=1):
            cellule = ws.cell(row=r, column=c, value=valeur)
            cellule.font, cellule.border = f_normal, bordure
            cellule.alignment = Alignment(vertical="top", wrap_text=True)
            if (r - ligne_entete) % 2 == 0:
                cellule.fill = fond_gris

    for i, largeur in enumerate(largeurs, start=1):
        ws.column_dimensions[get_column_letter(i)].width = largeur
    ws.freeze_panes = ws.cell(row=ligne_entete + 1, column=1)
    if lignes:
        ws.auto_filter.ref = f"A{ligne_entete}:{get_column_letter(len(entetes))}{ligne_entete + len(lignes)}"


def main() -> None:
    schemas = list(COUCHES)
    with get_engine().connect() as cx:
        tables = cx.execute(text("""
            select n.nspname as schema, c.relname as nom,
                   case c.relkind when 'v' then 'Vue' else 'Table' end as type,
                   obj_description(c.oid, 'pg_class') as description
            from pg_class c
            join pg_namespace n on n.oid = c.relnamespace
            where n.nspname = any(:schemas) and c.relkind in ('r', 'v')
            order by n.nspname, c.relname
        """), {"schemas": schemas}).mappings().all()

        colonnes = cx.execute(text("""
            select c.table_schema as schema, c.table_name as nom, c.ordinal_position as position,
                   c.column_name as colonne, c.data_type as type,
                   col_description(format('%I.%I', c.table_schema, c.table_name)::regclass,
                                   c.ordinal_position) as description
            from information_schema.columns c
            where c.table_schema = any(:schemas)
            order by c.table_schema, c.table_name, c.ordinal_position
        """), {"schemas": schemas}).mappings().all()

        volumes = {}
        for t in tables:
            volumes[(t["schema"], t["nom"])] = cx.execute(
                text(f'select count(*) from "{t["schema"]}"."{t["nom"]}"')).scalar()

        controles = cx.execute(text("""
            select code_controle, libelle_controle, categorie, gravite, table_source
            from referentiel.ref_controle_qualite order by code_controle
        """)).all()

    # Une colonne sans description reprend celle d'une colonne de même nom documentée
    # ailleurs (ex : cod_ind décrit dans raw.individu)
    description_par_nom = {}
    for col in colonnes:
        if col["description"] and col["colonne"] not in description_par_nom:
            description_par_nom[col["colonne"]] = col["description"]
    colonnes = [dict(col, description=col["description"] or description_par_nom.get(col["colonne"], ""))
                for col in colonnes]

    nb_colonnes = {}
    for col in colonnes:
        nb_colonnes[(col["schema"], col["nom"])] = nb_colonnes.get((col["schema"], col["nom"]), 0) + 1

    ordre = sorted(tables, key=lambda t: (COUCHES[t["schema"]][0], t["nom"]))
    classeur = Workbook()

    ecrire_tableau(
        classeur.active, "Data Warehouse — Pilotage des inscriptions (Apogée)",
        ["Couche", "Schéma", "Table", "Type", "Description", "Colonnes", "Lignes"],
        [(COUCHES[t["schema"]][0], t["schema"], t["nom"], t["type"], t["description"] or "",
          nb_colonnes.get((t["schema"], t["nom"]), 0), volumes[(t["schema"], t["nom"])]) for t in ordre],
        [20, 14, 36, 8, 70, 10, 10],
    )
    classeur.active.title = "Sommaire"

    ecrire_tableau(
        classeur.create_sheet("Dictionnaire"), "Dictionnaire des colonnes",
        ["Couche", "Table", "N°", "Colonne", "Type", "Description"],
        [(COUCHES[c["schema"]][0], f'{c["schema"]}.{c["nom"]}', c["position"], c["colonne"], c["type"],
          c["description"] or "") for c in sorted(colonnes, key=lambda c: (COUCHES[c["schema"]][0], c["nom"], c["position"]))],
        [20, 44, 5, 30, 26, 80],
    )

    ecrire_tableau(
        classeur.create_sheet("Indicateurs"), "Définition des indicateurs",
        ["Indicateur", "Définition", "Mode de calcul"], INDICATEURS, [32, 80, 55],
    )

    ecrire_tableau(
        classeur.create_sheet("Contrôles qualité"), "Catalogue des contrôles de qualité",
        ["Code", "Contrôle", "Catégorie", "Gravité", "Table source"], [tuple(c) for c in controles],
        [8, 60, 16, 16, 20],
    )

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    classeur.save(SORTIE)
    print(f"[DICO] {len(tables)} tables, {len(colonnes)} colonnes -> {SORTIE}")


if __name__ == "__main__":
    main()