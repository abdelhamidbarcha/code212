"""
EXTRACT — Génère des données académiques simulées, cohérentes entre elles
(intégrité référentielle respectée), pour les 8 tables du modèle.

En l'absence de données réelles fournies par l'établissement, ce module
simule un système d'information académique réaliste avec Faker.
"""
import random
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("fr_FR")
SEED = 42
Faker.seed(SEED)
random.seed(SEED)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# ---------------------- Volumes (réalistes, université de taille moyenne) ----------------------
N_DEPARTEMENTS = 8
N_FORMATIONS = 24
N_ENSEIGNANTS = 70
N_ETUDIANTS = 1800

NIVEAUX = ["Licence", "Master", "Doctorat"]
GRADES = ["Professeur", "Maître de Conférences", "Maître Assistant", "Vacataire"]
TYPES_EVAL = ["Examen", "Contrôle Continu", "Rattrapage", "Projet"]
STATUTS_ETUDIANT = ["Actif", "Diplômé", "Abandon"]
STATUTS_INSCRIPTION = ["Validée", "En attente", "Annulée"]
MODES = ["Présentiel", "À distance"]

NOMS_DEPARTEMENTS = [
    "Informatique", "Gestion", "Génie Civil", "Économie",
    "Mathématiques", "Physique", "Droit", "Langues Appliquées",
]
FACULTES = ["Sciences et Techniques", "Sciences Économiques et Juridiques", "Lettres et Sciences Humaines"]


# ==================================================================
# 1. DEPARTEMENTS (entité de référence, indépendante)
# ==================================================================
def generate_departements():
    rows = []
    for i in range(1, N_DEPARTEMENTS + 1):
        rows.append({
            "id_departement": i,
            "nom_departement": NOMS_DEPARTEMENTS[i - 1],
            "faculte": random.choice(FACULTES),
            "responsable": fake.name(),
        })
    return pd.DataFrame(rows)


# ==================================================================
# 2. FORMATIONS (dépend de departements)
# ==================================================================
def generate_formations(df_departements):
    rows = []
    suffixes_licence = ["1ère année", "2ème année", "3ème année"]
    for i in range(1, N_FORMATIONS + 1):
        dept = df_departements.sample(1).iloc[0]
        niveau = random.choice(NIVEAUX)
        rows.append({
            "id_formation": i,
            "nom_formation": f"{dept['nom_departement']} - {niveau}",
            "id_departement": dept["id_departement"],
            "niveau": niveau,
            "type_diplome": "Diplôme National" if niveau != "Doctorat" else "Doctorat",
            "duree_annees": {"Licence": 3, "Master": 2, "Doctorat": 3}[niveau],
        })
    return pd.DataFrame(rows)


# ==================================================================
# 3. ENSEIGNANTS (dépend de departements)
# ==================================================================
def generate_enseignants(df_departements):
    rows = []
    for i in range(1, N_ENSEIGNANTS + 1):
        rows.append({
            "id_enseignant": i,
            "nom": fake.last_name(),
            "prenom": fake.first_name(),
            "grade": random.choice(GRADES),
            "id_departement": df_departements.sample(1).iloc[0]["id_departement"],
            "email": fake.company_email(),
            "date_recrutement": fake.date_between(start_date="-20y", end_date="-1y"),
        })
    return pd.DataFrame(rows)


# ==================================================================
# 4. ANNEES_ACADEMIQUES (entité de référence, indépendante)
# ==================================================================
def generate_annees_academiques():
    rows = []
    id_ = 1
    for annee_debut in [2023, 2024, 2025]:
        libelle = f"{annee_debut}-{annee_debut + 1}"
        rows.append({
            "id_annee": id_, "libelle": libelle, "semestre": "S1",
            "date_debut": f"{annee_debut}-09-01", "date_fin": f"{annee_debut}-12-31",
        })
        id_ += 1
        rows.append({
            "id_annee": id_, "libelle": libelle, "semestre": "S2",
            "date_debut": f"{annee_debut + 1}-01-15", "date_fin": f"{annee_debut + 1}-06-30",
        })
        id_ += 1
    return pd.DataFrame(rows)


# ==================================================================
# 5. COURS (dépend de formations, enseignants, annees_academiques)
# ==================================================================
def generate_cours(df_formations, df_enseignants, df_annees):
    rows = []
    id_ = 1
    for _, formation in df_formations.iterrows():
        # même enseignant "pool" du département pour un peu de cohérence
        enseignants_dept = df_enseignants[df_enseignants["id_departement"] == formation["id_departement"]]
        if enseignants_dept.empty:
            enseignants_dept = df_enseignants
        for _, annee in df_annees.iterrows():
            nb_cours = random.randint(1, 3)
            for _ in range(nb_cours):
                rows.append({
                    "id_cours": id_,
                    "code_cours": f"{formation['nom_formation'][:3].upper()}{id_:04d}",
                    "intitule": fake.catch_phrase(),
                    "credits_ects": random.choice([3, 4, 5, 6]),
                    "id_formation": formation["id_formation"],
                    "id_enseignant": enseignants_dept.sample(1).iloc[0]["id_enseignant"],
                    "id_annee": annee["id_annee"],
                    "volume_horaire": random.choice([24, 30, 36, 48]),
                })
                id_ += 1
    return pd.DataFrame(rows)


# ==================================================================
# 6. ETUDIANTS (entité de référence, indépendante)
# ==================================================================
def generate_etudiants():
    rows = []
    for i in range(1, N_ETUDIANTS + 1):
        sexe = random.choice(["M", "F"])
        prenom = fake.first_name_male() if sexe == "M" else fake.first_name_female()
        date_naissance = fake.date_of_birth(minimum_age=17, maximum_age=28)
        rows.append({
            "id_etudiant": i,
            "matricule": f"ETU{2023 + (i % 3)}{i:05d}",
            "nom": fake.last_name(),
            "prenom": prenom,
            "date_naissance": date_naissance,
            "sexe": sexe,
            "nationalite": fake.country() if random.random() < 0.15 else "Marocaine",
            "email": fake.free_email(),
            "date_premiere_inscription": fake.date_between(start_date="-3y", end_date="-1y"),
            "statut": random.choices(STATUTS_ETUDIANT, weights=[0.75, 0.15, 0.10])[0],
        })
    return pd.DataFrame(rows)


# ==================================================================
# 7. INSCRIPTIONS (dépend de etudiants, formations, annees_academiques)
# ==================================================================
def generate_inscriptions(df_etudiants, df_formations, df_annees):
    rows = []
    id_ = 1
    annees_uniques = df_annees["libelle"].unique()
    for _, etudiant in df_etudiants.iterrows():
        formation = df_formations.sample(1).iloc[0]
        nb_annees_inscrit = random.randint(1, min(3, len(annees_uniques)))
        annees_choisies = random.sample(list(annees_uniques), nb_annees_inscrit)
        for lib in annees_choisies:
            # une inscription par semestre de cette année (S1 + S2)
            annees_du_libelle = df_annees[df_annees["libelle"] == lib]
            for _, annee in annees_du_libelle.iterrows():
                rows.append({
                    "id_inscription": id_,
                    "id_etudiant": etudiant["id_etudiant"],
                    "id_formation": formation["id_formation"],
                    "id_annee": annee["id_annee"],
                    "date_inscription": annee["date_debut"],
                    "statut_inscription": random.choices(STATUTS_INSCRIPTION, weights=[0.85, 0.1, 0.05])[0],
                    "mode": random.choices(MODES, weights=[0.8, 0.2])[0],
                })
                id_ += 1
    return pd.DataFrame(rows)


# ==================================================================
# 8. NOTES (dépend de etudiants, cours, annees_academiques, via inscriptions)
# ==================================================================
def generate_notes(df_inscriptions, df_cours):
    rows = []
    id_ = 1
    cours_par_formation_annee = df_cours.groupby(["id_formation", "id_annee"])

    for _, inscription in df_inscriptions.iterrows():
        try:
            cours_dispo = cours_par_formation_annee.get_group(
                (inscription["id_formation"], inscription["id_annee"])
            )
        except KeyError:
            continue

        for _, cours in cours_dispo.iterrows():
            n_evals = random.randint(1, 2)
            for _ in range(n_evals):
                # note réaliste : distribution centrée autour de 11-12/20
                note = round(min(20, max(0, random.gauss(11.5, 4.0))), 2)
                rows.append({
                    "id_note": id_,
                    "id_etudiant": inscription["id_etudiant"],
                    "id_cours": cours["id_cours"],
                    "id_annee": inscription["id_annee"],
                    "type_evaluation": random.choice(TYPES_EVAL),
                    "note": note,
                    "date_evaluation": fake.date_between(start_date="-2y", end_date="today"),
                })
                id_ += 1
    return pd.DataFrame(rows)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("[EXTRACT] Génération des entités de référence...")
    df_departements = generate_departements()
    df_formations = generate_formations(df_departements)
    df_enseignants = generate_enseignants(df_departements)
    df_annees = generate_annees_academiques()
    df_etudiants = generate_etudiants()

    print("[EXTRACT] Génération des entités dépendantes...")
    df_cours = generate_cours(df_formations, df_enseignants, df_annees)
    df_inscriptions = generate_inscriptions(df_etudiants, df_formations, df_annees)
    df_notes = generate_notes(df_inscriptions, df_cours)

    tables = {
        "departements": df_departements,
        "formations": df_formations,
        "enseignants": df_enseignants,
        "annees_academiques": df_annees,
        "cours": df_cours,
        "etudiants": df_etudiants,
        "inscriptions": df_inscriptions,
        "notes": df_notes,
    }

    for name, df in tables.items():
        path = RAW_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"[EXTRACT] {name:<20} -> {len(df):>6} lignes -> {path}")


if __name__ == "__main__":
    main()
