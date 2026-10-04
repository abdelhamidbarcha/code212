"""
EXTRACT — Génère des données Apogée simulées pour les 3 tables sources :
INDIVIDU, INS_ADM_ETP et IND_CONTRAT_ELP.

En attendant l'accès aux données réelles, ce module simule le parcours de
cohortes d'étudiants année après année (passage, redoublement, abandon,
poursuite d'études) afin d'obtenir des données cohérentes et réalistes.

Les fichiers produits ont EXACTEMENT la structure d'un export Apogée
(noms de colonnes en majuscules, tous les champs en texte). Le jour où les
données réelles sont disponibles, seul ce module est remplacé.

Des anomalies de saisie réalistes sont volontairement injectées (taux
paramétrable) pour démontrer le travail de nettoyage et de contrôle qualité
réalisé par dbt.

Dépendances : bibliothèque standard Python uniquement.
"""
import csv
import random
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

import referentiel as ref

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# =====================================================================
#  Paramètres de simulation
# =====================================================================
SEED = 42
NOUVEAUX_ENTRANTS_BASE = 1500         # nouveaux étudiants par an (année de référence)
CROISSANCE_ANNUELLE = 0.04            # +4 % de nouveaux entrants par an
ANNEE_DEBUT_SIMULATION = ref.PREMIERE_ANNEE - 6   # mise en régime : cohortes déjà présentes en 2021

TAUX_ETRANGERS = 0.06
TAUX_MAROCAINS_NES_ETRANGER = 0.02
TAUX_FEMMES = 0.52
TAUX_SANS_EMAIL = 0.08

PROBA_ETAT_IAE = {"E": 0.95, "A": 0.035, "R": 0.015}
TAUX_TEMOIN_NON_PRIS = 0.03            # TEM_PRC_ICE = 'N'
TAUX_CONTRAT_MODIFIE = 0.30            # DAT_MOD_ICE renseignée
TAUX_SAISIE_BATCH = 0.45               # contrats créés par traitement automatique
AGENTS_PAR_COMPOSANTE = 3

# Anomalies de saisie volontaires (contrôlées ensuite par dbt)
TAUX_ANOMALIES = 0.01                  # casse/espaces incohérents
TAUX_CONTRAT_SANS_IA = 0.03            # abandon, mais contrat pédagogique saisi l'année suivante
TAUX_DOUBLON_CONTRAT = 0.002           # double saisie d'une même ligne

COLONNES = {
    "individu": ["COD_IND", "COD_ETU", "NUMERO_INE", "CLE_INE", "LIB_NOM_PAT_IND", "LIB_PRENOM_IND",
                 "COD_SEX_ETU", "DATE_NAISSANCE", "LIB_VIL_NAI_ETU", "COD_PAY_NAI_ETU", "COD_NAT_ETU",
                 "COD_DEP_NAI_ETU", "ADR_MAIL_ETU"],
    "ins_adm_etp": ["COD_IND", "COD_ANU", "ETA_IAE", "COD_CMP"],
    "ind_contrat_elp": ["COD_IND", "COD_ELP", "COD_ANU", "COD_ETP", "COD_VRS_VET", "TEM_PRC_ICE",
                        "DAT_CRE_ELP_CON", "DAT_MOD_ICE", "COD_UTI"],
}

# =====================================================================
#  Noms (étudiants marocains et étrangers)
# =====================================================================
PRENOMS_M = ["Mohamed", "Youssef", "Ayoub", "Hamza", "Omar", "Mehdi", "Amine", "Anass", "Ilyas", "Othmane",
             "Zakaria", "Soufiane", "Yassine", "Achraf", "Reda", "Khalid", "Adam", "Ismail", "Abdelilah",
             "Hicham", "Badr", "Nabil", "Walid", "Saad", "Marouane"]
PRENOMS_F = ["Fatima Zahra", "Salma", "Khadija", "Meryem", "Imane", "Hajar", "Aya", "Oumaima", "Sara",
             "Nisrine", "Chaimae", "Hiba", "Zineb", "Asmae", "Ikram", "Douae", "Kawtar", "Yasmine", "Rania",
             "Ghita", "Hanane", "Soukaina", "Safae", "Nada", "Malak"]
NOMS = ["El Amrani", "Benali", "Alaoui", "Bennani", "El Idrissi", "Tazi", "Berrada", "Chraibi", "El Fassi",
        "Ouazzani", "Lahlou", "Benjelloun", "Bouzid", "El Mansouri", "Aït Ali", "Ouahbi", "Aït Lahcen",
        "Boukhari", "El Khatib", "Haddad", "Naciri", "Zahraoui", "Rachidi", "Amzil", "Ouchen", "Id Brahim",
        "Aït Ouakrim", "El Hachimi", "Moussaoui", "Sebbar"]
PRENOMS_ETR_M = ["Moussa", "Ibrahima", "Mamadou", "Cheikh", "Ousmane", "Abdoulaye", "Souleymane", "Karim"]
PRENOMS_ETR_F = ["Aminata", "Fatoumata", "Awa", "Mariam", "Aïssatou", "Kadiatou", "Ramatou", "Nadia"]
NOMS_ETR = ["Diallo", "Traoré", "Ndiaye", "Koné", "Camara", "Sow", "Coulibaly", "Mbaye", "Ould Ahmed",
            "Touré", "Barry", "Cissé"]
DOMAINES_EMAIL = (["gmail.com", "outlook.com", "yahoo.fr", "hotmail.com"], [0.62, 0.18, 0.10, 0.10])
LETTRES_INE = "DEFGHJKMNPRS"

FILIERES = {f.code: f for f in ref.FILIERES}
COMPOSANTES = {c.code: c for c in ref.COMPOSANTES}
ELPS_PAR_ETAPE: dict[str, list[dict]] = {}
for _elp in ref.construire_elements_pedagogiques():
    ELPS_PAR_ETAPE.setdefault(_elp["cod_etp"], []).append(_elp)


# =====================================================================
#  Utilitaires
# =====================================================================
def sans_accents(texte: str) -> str:
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if c.isascii() and (c.isalnum()))


def tirage(rng: random.Random, probas: dict):
    return rng.choices(list(probas.keys()), weights=list(probas.values()))[0]


def date_heure(rng: random.Random, jour: date, h_min: int = 8, h_max: int = 17) -> datetime:
    return datetime(jour.year, jour.month, jour.day, rng.randint(h_min, h_max - 1),
                    rng.randint(0, 59), rng.randint(0, 59))


def fmt(d) -> str:
    if d is None:
        return ""
    return d.strftime("%Y-%m-%d %H:%M:%S") if isinstance(d, datetime) else d.isoformat()


# =====================================================================
#  1. Simulation des parcours
# =====================================================================
def simuler_parcours(rng: random.Random, filiere, annee_entree: int) -> tuple[list[dict], int | None]:
    """Retourne les inscriptions annuelles d'un étudiant et, éventuellement,
    l'année d'un contrat pédagogique saisi par erreur après son départ."""
    inscriptions = []
    annee, niveau, redoublant = annee_entree, 1, False
    redoublements_niveau = 0
    while annee <= ref.DERNIERE_ANNEE:
        etat = tirage(rng, PROBA_ETAT_IAE)
        inscriptions.append({"cod_anu": annee, "filiere": filiere, "annee_etude": niveau,
                             "eta_iae": etat, "redoublant": redoublant})
        if etat == "A":                      # inscription annulée : l'étudiant quitte l'université
            return inscriptions, None
        mode = "Sélectif" if filiere.cycle == "Master" else COMPOSANTES[filiere.cmp].mode_acces
        p_pass, p_red, _ = ref.PARCOURS[mode]
        issue = "abandon" if etat == "R" else rng.choices(
            ["passage", "redoublement", "abandon"], weights=[p_pass, p_red, 1 - p_pass - p_red])[0]

        if issue == "redoublement" and redoublements_niveau >= 1:
            issue = "abandon"                # deuxième échec au même niveau : exclusion
        if issue == "abandon":
            erreur = annee + 1 if rng.random() < TAUX_CONTRAT_SANS_IA else None
            return inscriptions, erreur
        if issue == "redoublement":
            redoublant, redoublements_niveau = True, redoublements_niveau + 1
        elif niveau < filiere.duree:
            niveau, redoublant, redoublements_niveau = niveau + 1, False, 0
        elif filiere.suite and rng.random() < filiere.p_suite:   # poursuite d'études
            filiere = FILIERES[rng.choice(filiere.suite)]
            niveau, redoublant, redoublements_niveau = 1, False, 0
        else:                                # diplômé(e)
            return inscriptions, None
        annee += 1
    return inscriptions, None


# =====================================================================
#  2. Génération d'un individu
# =====================================================================
def generer_individu(rng, cod_ind, annee_entree, filiere, ines_utilises) -> dict:
    sexe = "F" if rng.random() < TAUX_FEMMES else "M"
    etranger = rng.random() < TAUX_ETRANGERS

    if etranger:
        pays = rng.choices(ref.PAYS, weights=[p.poids_etr for p in ref.PAYS])[0]
        prenom = rng.choice(PRENOMS_ETR_F if sexe == "F" else PRENOMS_ETR_M)
        nom = rng.choice(NOMS_ETR)
        cod_pay, cod_nat, ville, cod_dep = pays.code, pays.code, pays.capitale, ref.CODE_DEP_ETRANGER
        numero_ine = cle_ine = ""            # pas de code Massar pour les étudiants étrangers
    else:
        prenom = rng.choice(PRENOMS_F if sexe == "F" else PRENOMS_M)
        nom = rng.choice(NOMS)
        cod_nat = ref.CODE_MAROC
        if rng.random() < TAUX_MAROCAINS_NES_ETRANGER:
            pays = rng.choices(ref.PAYS, weights=[p.poids_nes for p in ref.PAYS])[0]
            cod_pay, ville, cod_dep = pays.code, pays.capitale, ref.CODE_DEP_ETRANGER
        else:
            prov = rng.choices(ref.PROVINCES, weights=[p.poids for p in ref.PROVINCES])[0]
            cod_pay, ville, cod_dep = ref.CODE_MAROC, prov.ville, prov.code
        while True:
            numero_ine = rng.choice(LETTRES_INE) + f"{rng.randint(0, 999_999_999):09d}"
            if numero_ine not in ines_utilises:
                ines_utilises.add(numero_ine)
                break
        cle_ine = chr(ord("A") + sum(int(c) for c in numero_ine[1:]) % 26)   # clé de contrôle simulée

    age = rng.choices([21, 22, 23, 24, 25], [0.35, 0.30, 0.18, 0.12, 0.05])[0] if filiere.cycle == "Master" \
        else rng.choices([17, 18, 19, 20, 21], [0.08, 0.50, 0.25, 0.12, 0.05])[0]
    naissance = date(annee_entree - age, 1, 1) + timedelta(days=rng.randint(0, 364))

    email = ""
    if rng.random() >= TAUX_SANS_EMAIL:
        domaine = rng.choices(*DOMAINES_EMAIL)[0]
        email = f"{sans_accents(prenom).lower()}.{sans_accents(nom).lower()}{rng.randint(1, 99):02d}@{domaine}"

    ligne = {
        "COD_IND": str(cod_ind),
        "COD_ETU": f"{annee_entree % 100:02d}{cod_ind % 1_000_000:06d}",
        "NUMERO_INE": numero_ine,
        "CLE_INE": cle_ine,
        "LIB_NOM_PAT_IND": nom.upper(),
        "LIB_PRENOM_IND": prenom,
        "COD_SEX_ETU": sexe,
        "DATE_NAISSANCE": naissance.isoformat(),
        "LIB_VIL_NAI_ETU": ville,
        "COD_PAY_NAI_ETU": cod_pay,
        "COD_NAT_ETU": cod_nat,
        "COD_DEP_NAI_ETU": cod_dep,
        "ADR_MAIL_ETU": email,
    }
    # --- Anomalies de saisie volontaires ---
    if rng.random() < TAUX_ANOMALIES:
        ligne["LIB_NOM_PAT_IND"] = f"  {nom.lower()} "
    if rng.random() < TAUX_ANOMALIES:
        ligne["COD_SEX_ETU"] = sexe.lower()
    if email and rng.random() < TAUX_ANOMALIES:
        ligne["ADR_MAIL_ETU"] = email.upper()
    return ligne


# =====================================================================
#  3. Génération des contrats pédagogiques d'une inscription
# =====================================================================
def generer_contrats(rng, cod_ind, insc, agents) -> list[dict]:
    filiere, cod_anu = insc["filiere"], insc["cod_anu"]
    cod_etp = ref.code_etape(filiere, insc["annee_etude"])
    modules = ELPS_PAR_ETAPE[cod_etp]
    if insc["redoublant"]:                   # un redoublant ne reprend que les modules non validés
        modules = rng.sample(modules, rng.randint(len(modules) // 2, len(modules)))
    if insc["eta_iae"] == "R":               # résiliation en cours d'année : 1er semestre seulement
        modules = modules[:ref.MODULES_PAR_SEMESTRE]

    # Saisie : traitement automatique (nuit du 30 septembre) ou agent de scolarité (pic en octobre)
    if rng.random() < TAUX_SAISIE_BATCH:
        cod_uti = "APOBATCH"
        creation = datetime(cod_anu, 9, 30, 2, rng.randint(0, 59), rng.randint(0, 59))
    else:
        cod_uti = rng.choice(agents[filiere.cmp])
        jour = date(cod_anu, 9, 15) + timedelta(days=int(rng.triangular(0, 90, 25)))
        creation = date_heure(rng, jour)

    lignes = []
    for m in modules:
        modification = None
        if rng.random() < TAUX_CONTRAT_MODIFIE:
            modification = date_heure(rng, (creation + timedelta(days=rng.randint(1, 120))).date())
        ligne = {
            "COD_IND": str(cod_ind),
            "COD_ELP": m["cod_elp"],
            "COD_ANU": str(cod_anu),
            "COD_ETP": cod_etp,
            "COD_VRS_VET": ref.version_etape(filiere, cod_anu),
            "TEM_PRC_ICE": "N" if rng.random() < TAUX_TEMOIN_NON_PRIS else "O",
            "DAT_CRE_ELP_CON": fmt(creation),
            "DAT_MOD_ICE": fmt(modification),
            "COD_UTI": cod_uti,
        }
        lignes.append(ligne)
        if rng.random() < TAUX_DOUBLON_CONTRAT:
            lignes.append(dict(ligne))       # double saisie
    return lignes


def generer_agents(rng) -> dict[str, list[str]]:
    """Logins des agents de scolarité, ex : KBENALI."""
    agents = {}
    for cmp in ref.COMPOSANTES:
        logins = set()
        while len(logins) < AGENTS_PAR_COMPOSANTE:
            prenom, nom = rng.choice(PRENOMS_M + PRENOMS_F), rng.choice(NOMS)
            logins.add((sans_accents(prenom)[0] + sans_accents(nom)).upper()[:8])
        agents[cmp.code] = sorted(logins)
    return agents


# =====================================================================
#  4. Orchestration
# =====================================================================
def generer() -> dict[str, list[dict]]:
    rng = random.Random(SEED)
    agents = generer_agents(rng)
    filieres_entree = [f for f in ref.FILIERES if f.poids > 0]
    poids_entree = [f.poids for f in filieres_entree]

    individus, ias, contrats = [], [], []
    ines_utilises: set[str] = set()
    prochain_cod_ind = 100_001
    fenetre = range(ref.PREMIERE_ANNEE, ref.DERNIERE_ANNEE + 1)

    for annee_entree in range(ANNEE_DEBUT_SIMULATION, ref.DERNIERE_ANNEE + 1):
        n = round(NOUVEAUX_ENTRANTS_BASE * (1 + CROISSANCE_ANNUELLE) ** (annee_entree - ref.PREMIERE_ANNEE)
                  * rng.uniform(0.97, 1.03))
        for _ in range(n):
            filiere = rng.choices(filieres_entree, weights=poids_entree)[0]
            parcours, annee_erreur = simuler_parcours(rng, filiere, annee_entree)
            parcours = [i for i in parcours if i["cod_anu"] in fenetre]
            if annee_erreur not in fenetre:
                annee_erreur = None
            if not parcours and annee_erreur is None:
                continue                     # étudiant hors de la période observée

            cod_ind = prochain_cod_ind
            prochain_cod_ind += 1
            individus.append(generer_individu(rng, cod_ind, annee_entree, filiere, ines_utilises))

            for insc in parcours:
                ias.append({"COD_IND": str(cod_ind), "COD_ANU": str(insc["cod_anu"]),
                            "ETA_IAE": insc["eta_iae"], "COD_CMP": insc["filiere"].cmp})
                if insc["eta_iae"] != "A":
                    contrats.extend(generer_contrats(rng, cod_ind, insc, agents))

            if annee_erreur is not None and parcours:     # anomalie : contrat sans inscription administrative
                derniere = dict(parcours[-1], cod_anu=annee_erreur, eta_iae="E", redoublant=True)
                contrats.extend(generer_contrats(rng, cod_ind, derniere, agents))

    return {"individu": individus, "ins_adm_etp": ias, "ind_contrat_elp": contrats}


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[EXTRACT] Simulation Apogée {ref.PREMIERE_ANNEE}-{ref.DERNIERE_ANNEE} (seed={SEED})...")
    tables = generer()
    for nom, lignes in tables.items():
        chemin = RAW_DIR / f"{nom}.csv"
        with open(chemin, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLONNES[nom], lineterminator="\n")
            writer.writeheader()
            writer.writerows(lignes)
        print(f"[EXTRACT] {nom:<16} -> {len(lignes):>7} lignes -> {chemin}")

    print("[EXTRACT] Inscriptions administratives par année :")
    for annee in range(ref.PREMIERE_ANNEE, ref.DERNIERE_ANNEE + 1):
        n = sum(1 for r in tables["ins_adm_etp"] if r["COD_ANU"] == str(annee))
        print(f"           {annee}-{annee + 1} : {n:>6}")


if __name__ == "__main__":
    main()