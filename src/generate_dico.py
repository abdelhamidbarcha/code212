"""
Génère le dictionnaire de données (data dictionary) du modèle académique
sous forme de classeur Excel : un onglet Sommaire + un onglet par table.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

NAVY = "1F3864"
LIGHT_BG = "F2F2F2"
WHITE = "FFFFFF"

FONT_NAME = "Calibri"

header_font = Font(name=FONT_NAME, bold=True, color=WHITE, size=11)
header_fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
title_font = Font(name=FONT_NAME, bold=True, color=NAVY, size=14)
normal_font = Font(name=FONT_NAME, size=10.5)
thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

# ---------- Définition des 8 tables (Colonne, Type, Clé, Description) ----------
TABLES = {
    "departements": [
        ("id_departement", "SERIAL", "PK", "Identifiant unique du département"),
        ("nom_departement", "VARCHAR(150)", "", "Nom du département (ex: Informatique)"),
        ("faculte", "VARCHAR(150)", "", "Faculté de rattachement"),
        ("responsable", "VARCHAR(150)", "", "Nom du responsable de département"),
    ],
    "formations": [
        ("id_formation", "SERIAL", "PK", "Identifiant unique de la formation"),
        ("nom_formation", "VARCHAR(150)", "", "Intitulé de la formation"),
        ("id_departement", "INTEGER", "FK", "Référence vers departements"),
        ("niveau", "VARCHAR(30)", "", "Licence / Master / Doctorat"),
        ("type_diplome", "VARCHAR(50)", "", "Diplôme national, ingénierie, etc."),
        ("duree_annees", "SMALLINT", "", "Durée standard de la formation"),
    ],
    "enseignants": [
        ("id_enseignant", "SERIAL", "PK", "Identifiant unique de l'enseignant"),
        ("nom", "VARCHAR(100)", "", "Nom de famille"),
        ("prenom", "VARCHAR(100)", "", "Prénom"),
        ("grade", "VARCHAR(50)", "", "Professeur, Maître de conférences, Vacataire"),
        ("id_departement", "INTEGER", "FK", "Référence vers departements"),
        ("email", "VARCHAR(150)", "", "Contact professionnel"),
        ("date_recrutement", "DATE", "", "Date d'entrée en fonction"),
    ],
    "etudiants": [
        ("id_etudiant", "SERIAL", "PK", "Identifiant unique de l'étudiant"),
        ("matricule", "VARCHAR(20)", "UNIQUE", "Numéro d'immatriculation officiel"),
        ("nom", "VARCHAR(100)", "", "Nom de famille"),
        ("prenom", "VARCHAR(100)", "", "Prénom"),
        ("date_naissance", "DATE", "", "Utilisée pour calculer l'âge / tranche d'âge"),
        ("sexe", "CHAR(1)", "", "M / F"),
        ("nationalite", "VARCHAR(60)", "", "Nationalité déclarée"),
        ("email", "VARCHAR(150)", "", "Contact étudiant"),
        ("date_premiere_inscription", "DATE", "", "Première inscription à l'université"),
        ("statut", "VARCHAR(30)", "", "Actif / Diplômé / Abandon"),
    ],
    "annees_academiques": [
        ("id_annee", "SERIAL", "PK", "Identifiant unique de la période"),
        ("libelle", "VARCHAR(20)", "", "Ex: 2025-2026"),
        ("semestre", "VARCHAR(5)", "", "S1 / S2"),
        ("date_debut", "DATE", "", "Date de début de la période"),
        ("date_fin", "DATE", "", "Date de fin de la période"),
    ],
    "cours": [
        ("id_cours", "SERIAL", "PK", "Identifiant unique du cours"),
        ("code_cours", "VARCHAR(20)", "", "Code interne (ex: INF301)"),
        ("intitule", "VARCHAR(150)", "", "Nom du cours"),
        ("credits_ects", "SMALLINT", "", "Nombre de crédits"),
        ("id_formation", "INTEGER", "FK", "Référence vers formations"),
        ("id_enseignant", "INTEGER", "FK", "Référence vers enseignants"),
        ("id_annee", "INTEGER", "FK", "Référence vers annees_academiques"),
        ("volume_horaire", "SMALLINT", "", "Nombre d'heures total"),
    ],
    "inscriptions": [
        ("id_inscription", "SERIAL", "PK", "Identifiant unique de l'inscription"),
        ("id_etudiant", "INTEGER", "FK", "Référence vers etudiants"),
        ("id_formation", "INTEGER", "FK", "Référence vers formations"),
        ("id_annee", "INTEGER", "FK", "Référence vers annees_academiques"),
        ("date_inscription", "DATE", "", "Date effective d'inscription"),
        ("statut_inscription", "VARCHAR(30)", "", "Validée / En attente / Annulée"),
        ("mode", "VARCHAR(20)", "", "Présentiel / À distance"),
    ],
    "notes": [
        ("id_note", "SERIAL", "PK", "Identifiant unique de la note"),
        ("id_etudiant", "INTEGER", "FK", "Référence vers etudiants"),
        ("id_cours", "INTEGER", "FK", "Référence vers cours"),
        ("id_annee", "INTEGER", "FK", "Référence vers annees_academiques"),
        ("type_evaluation", "VARCHAR(30)", "", "Examen / Contrôle continu / Rattrapage / Projet"),
        ("note", "NUMERIC(4,2)", "", "Note obtenue, entre 0 et 20"),
        ("date_evaluation", "DATE", "", "Date de l'évaluation"),
    ],
}

HEADERS = ["Colonne", "Type", "Clé", "Description"]
COL_WIDTHS = [26, 16, 8, 55]


def style_header_row(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = Alignment(vertical="center", wrap_text=True)


def write_table_sheet(wb, sheet_name, columns):
    ws = wb.create_sheet(sheet_name)
    ws.sheet_view.showGridLines = False

    # Titre
    ws["A1"] = f"Table : {sheet_name}"
    ws["A1"].font = title_font
    ws.merge_cells("A1:D1")

    header_row = 3
    for i, h in enumerate(HEADERS, start=1):
        ws.cell(row=header_row, column=i, value=h)
    style_header_row(ws, header_row, len(HEADERS))

    for r, (col, typ, key, desc) in enumerate(columns, start=header_row + 1):
        values = [col, typ, key, desc]
        for c, val in enumerate(values, start=1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.font = normal_font
            cell.border = border
            cell.alignment = Alignment(vertical="center", wrap_text=(c == 4))
            if key == "PK":
                cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            elif (r - header_row) % 2 == 0:
                cell.fill = PatternFill(start_color=LIGHT_BG, end_color=LIGHT_BG, fill_type="solid")

    for i, w in enumerate(COL_WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = f"A{header_row + 1}"
    return ws


def write_summary_sheet(wb, tables):
    ws = wb.active
    ws.title = "Sommaire"
    ws.sheet_view.showGridLines = False

    ws["A1"] = "Dictionnaire de Données — Système d'Information Académique"
    ws["A1"].font = Font(name=FONT_NAME, bold=True, color=NAVY, size=16)
    ws.merge_cells("A1:C1")

    ws["A3"] = "Table"
    ws["B3"] = "Nombre de colonnes"
    ws["C3"] = "Description"
    style_header_row(ws, 3, 3)

    descriptions = {
        "departements": "Unités administratives et académiques",
        "formations": "Programmes d'études (filières)",
        "enseignants": "Corps professoral",
        "etudiants": "Profils individuels des étudiants",
        "annees_academiques": "Référentiel temporel (année + semestre)",
        "cours": "Unités d'enseignement",
        "inscriptions": "Lien étudiant ↔ formation pour une période",
        "notes": "Résultats d'évaluation des étudiants",
    }

    for r, (name, cols) in enumerate(tables.items(), start=4):
        ws.cell(row=r, column=1, value=name).font = normal_font
        ws.cell(row=r, column=2, value=len(cols)).font = normal_font
        ws.cell(row=r, column=3, value=descriptions.get(name, "")).font = normal_font
        for c in range(1, 4):
            cell = ws.cell(row=r, column=c)
            cell.border = border
            if r % 2 == 0:
                cell.fill = PatternFill(start_color=LIGHT_BG, end_color=LIGHT_BG, fill_type="solid")

    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 50


wb = Workbook()
write_summary_sheet(wb, TABLES)
for table_name, columns in TABLES.items():
    write_table_sheet(wb, table_name, columns)

wb.save("docs/Dictionnaire_Donnees_Academique.xlsx")
print("OK - fichier généré")
