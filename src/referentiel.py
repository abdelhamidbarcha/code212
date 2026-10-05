"""
RÉFÉRENTIEL — Nomenclatures de l'université simulée (source unique de vérité).

Ce module :
  1. définit les codes utilisés par le générateur de données (extract.py) ;
  2. exporte les tables de libellés (seeds dbt) qui transforment les codes
     Apogée (FS, SMI1, 350...) en libellés lisibles dans les tableaux de bord.

Passage aux données réelles : l'université remplace simplement les fichiers
CSV de dbt_project/seeds/ par ses propres nomenclatures Apogée.

Usage : python3 src/referentiel.py   (régénère les seeds)
Dépendances : bibliothèque standard Python uniquement.
"""
import csv
from collections import namedtuple
from pathlib import Path

SEEDS_DIR = Path(__file__).resolve().parents[1] / "dbt_project" / "seeds"

# ---------------------------------------------------------------------
#  Période couverte (COD_ANU = année de début : 2024 => 2024-2025)
# ---------------------------------------------------------------------
PREMIERE_ANNEE = 2021
DERNIERE_ANNEE = 2025
ANNEE_REFORME_LICENCE = 2023     # nouvelle version d'étape (COD_VRS_VET = 2) pour les licences
MODULES_PAR_SEMESTRE = 3

# ---------------------------------------------------------------------
#  Composantes (établissements)
# ---------------------------------------------------------------------
Composante = namedtuple("Composante", "code libelle type_etab mode_acces")
COMPOSANTES = [
    Composante("FS",    "Faculté des Sciences",                                         "Faculté", "Accès ouvert"),
    Composante("FSJES", "Faculté des Sciences Juridiques, Économiques et Sociales",     "Faculté", "Accès ouvert"),
    Composante("FLSH",  "Faculté des Lettres et des Sciences Humaines",                 "Faculté", "Accès ouvert"),
    Composante("FST",   "Faculté des Sciences et Techniques",                           "Faculté", "Accès régulé"),
    Composante("ENSA",  "École Nationale des Sciences Appliquées",                      "École",   "Sélectif"),
    Composante("ENCG",  "École Nationale de Commerce et de Gestion",                    "École",   "Sélectif"),
]

# Probabilités annuelles de parcours selon le mode d'accès : (passage, redoublement, abandon)
PARCOURS = {
    "Accès ouvert": (0.58, 0.25, 0.17),
    "Accès régulé": (0.80, 0.12, 0.08),
    "Sélectif":     (0.92, 0.05, 0.03),
}

# ---------------------------------------------------------------------
#  Filières : une étape Apogée = une année d'une filière (ex : SMI1, SMI2, SMI3)
#  poids = part des nouveaux entrants ; suite = filières de poursuite d'études
# ---------------------------------------------------------------------
Filiere = namedtuple("Filiere", "code libelle cmp cycle duree domaine poids suite p_suite")
FILIERES = [
    Filiere("SMI", "Sciences Mathématiques et Informatique",  "FS",    "Licence",            3, "info",     6, ("MSD",),        0.25),
    Filiere("SMP", "Sciences de la Matière Physique",         "FS",    "Licence",            3, "sciences", 4, (),              0.0),
    Filiere("SVT", "Sciences de la Vie et de la Terre",       "FS",    "Licence",            3, "vie",      5, (),              0.0),
    Filiere("MSD", "Science des Données",                     "FS",    "Master",             2, "info",     1, (),              0.0),
    Filiere("DRF", "Droit en langue française",               "FSJES", "Licence",            3, "droit",    7, (),              0.0),
    Filiere("SEG", "Sciences Économiques et Gestion",         "FSJES", "Licence",            3, "eco",      8, ("MFI",),        0.20),
    Filiere("MFI", "Finance et Banque",                       "FSJES", "Master",             2, "eco",      1, (),              0.0),
    Filiere("ETA", "Études Anglaises",                        "FLSH",  "Licence",            3, "lettres",  4, (),              0.0),
    Filiere("ETF", "Études Françaises",                       "FLSH",  "Licence",            3, "lettres",  3, (),              0.0),
    Filiere("LGI", "Génie Informatique",                      "FST",   "Licence",            3, "info",     2, (),              0.0),
    Filiere("LGC", "Génie Civil",                             "FST",   "Licence",            3, "gcivil",   2, (),              0.0),
    Filiere("CPI", "Cycle Préparatoire Intégré",              "ENSA",  "Cycle préparatoire", 2, "sciences", 2, ("GIN", "GCV"), 1.0),
    Filiere("GIN", "Génie Informatique",                      "ENSA",  "Cycle ingénieur",    3, "info",     0, (),              0.0),
    Filiere("GCV", "Génie Civil",                             "ENSA",  "Cycle ingénieur",    3, "gcivil",   0, (),              0.0),
    Filiere("PGE", "Programme Grande École",                  "ENCG",  "Grande École",       5, "eco",      3, (),              0.0),
]

# Intitulés de modules par domaine (au-delà de la liste : "(approfondissement)")
DOMAINES = {
    "info":     ["Algorithmique", "Programmation en C", "Analyse mathématique", "Algèbre linéaire",
                 "Architecture des ordinateurs", "Bases de données", "Systèmes d'exploitation",
                 "Réseaux informatiques", "Programmation orientée objet", "Génie logiciel",
                 "Développement web", "Intelligence artificielle"],
    "sciences": ["Mécanique du point", "Thermodynamique", "Électricité", "Optique", "Analyse", "Algèbre",
                 "Électromagnétisme", "Mécanique quantique", "Physique des matériaux",
                 "Probabilités et statistiques", "Méthodes numériques", "Physique nucléaire"],
    "vie":      ["Biologie cellulaire", "Géologie générale", "Chimie générale", "Biologie animale",
                 "Biologie végétale", "Biochimie", "Génétique", "Microbiologie", "Écologie",
                 "Physiologie", "Immunologie", "Biotechnologie"],
    "droit":    ["Introduction au droit", "Droit constitutionnel", "Droit civil", "Droit administratif",
                 "Droit pénal", "Droit commercial", "Droit du travail", "Procédure civile",
                 "Droit international public", "Droit des sociétés", "Droit fiscal", "Contentieux administratif"],
    "eco":      ["Microéconomie", "Macroéconomie", "Comptabilité générale", "Mathématiques financières",
                 "Statistiques descriptives", "Management", "Marketing", "Comptabilité analytique",
                 "Finance d'entreprise", "Économie monétaire", "Contrôle de gestion", "Audit"],
    "lettres":  ["Grammaire", "Phonétique", "Expression écrite", "Littérature", "Linguistique générale",
                 "Traduction", "Civilisation", "Analyse du discours", "Sociolinguistique", "Didactique",
                 "Littérature comparée", "Méthodologie de recherche"],
    "gcivil":   ["Résistance des matériaux", "Topographie", "Mécanique des sols", "Béton armé", "Hydraulique",
                 "Dessin technique", "Construction métallique", "Routes et ouvrages", "Géotechnique",
                 "Gestion de chantier", "Calcul des structures", "Modélisation BIM"],
}

# ---------------------------------------------------------------------
#  Lieux de naissance (codes département/province simulés, "099" = né à l'étranger)
# ---------------------------------------------------------------------
Province = namedtuple("Province", "code province ville region poids")
PROVINCES = [
    Province("001", "Marrakech",            "Marrakech",            "Marrakech-Safi",               30),
    Province("002", "Safi",                 "Safi",                 "Marrakech-Safi",                6),
    Province("003", "El Kelâa des Sraghna", "El Kelâa des Sraghna", "Marrakech-Safi",                6),
    Province("004", "Essaouira",            "Essaouira",            "Marrakech-Safi",                4),
    Province("005", "Al Haouz",             "Tahannaout",           "Marrakech-Safi",                4),
    Province("006", "Chichaoua",            "Chichaoua",            "Marrakech-Safi",                3),
    Province("007", "Youssoufia",           "Youssoufia",           "Marrakech-Safi",                3),
    Province("008", "Rehamna",              "Ben Guerir",           "Marrakech-Safi",                3),
    Province("010", "Béni Mellal",          "Béni Mellal",          "Béni Mellal-Khénifra",          5),
    Province("011", "Ouarzazate",           "Ouarzazate",           "Drâa-Tafilalet",                4),
    Province("012", "Zagora",               "Zagora",               "Drâa-Tafilalet",                2),
    Province("013", "Agadir Ida-Outanane",  "Agadir",               "Souss-Massa",                   4),
    Province("014", "Casablanca",           "Casablanca",           "Casablanca-Settat",             5),
    Province("015", "El Jadida",            "El Jadida",            "Casablanca-Settat",             3),
    Province("016", "Rabat",                "Rabat",                "Rabat-Salé-Kénitra",            2),
    Province("017", "Fès",                  "Fès",                  "Fès-Meknès",                    2),
    Province("018", "Tanger-Assilah",       "Tanger",               "Tanger-Tétouan-Al Hoceïma",     1),
    Province("019", "Laâyoune",             "Laâyoune",             "Laâyoune-Sakia El Hamra",       2),
    Province("020", "Guelmim",              "Guelmim",              "Guelmim-Oued Noun",             2),
]
CODE_DEP_ETRANGER = "099"

# ---------------------------------------------------------------------
#  Pays / nationalités (codes à 3 chiffres de type INSEE, utilisés par Apogée)
#  poids_etr = poids parmi les étudiants étrangers ; poids_nes = Marocains nés hors du Maroc
# ---------------------------------------------------------------------
Pays = namedtuple("Pays", "code pays nationalite zone capitale poids_etr poids_nes")
PAYS = [
    Pays("350", "Maroc",          "Marocaine",       "Maghreb",              "Rabat",        0, 0),
    Pays("352", "Algérie",        "Algérienne",      "Maghreb",              "Alger",        2, 0),
    Pays("351", "Tunisie",        "Tunisienne",      "Maghreb",              "Tunis",        1, 0),
    Pays("336", "Mauritanie",     "Mauritanienne",   "Afrique subsaharienne", "Nouakchott",  6, 0),
    Pays("341", "Sénégal",        "Sénégalaise",     "Afrique subsaharienne", "Dakar",       5, 0),
    Pays("335", "Mali",           "Malienne",        "Afrique subsaharienne", "Bamako",      4, 0),
    Pays("326", "Côte d'Ivoire",  "Ivoirienne",      "Afrique subsaharienne", "Abidjan",     3, 0),
    Pays("330", "Guinée",         "Guinéenne",       "Afrique subsaharienne", "Conakry",     3, 0),
    Pays("337", "Niger",          "Nigérienne",      "Afrique subsaharienne", "Niamey",      2, 0),
    Pays("344", "Tchad",          "Tchadienne",      "Afrique subsaharienne", "N'Djamena",   2, 0),
    Pays("328", "Gabon",          "Gabonaise",       "Afrique subsaharienne", "Libreville",  2, 0),
    Pays("322", "Cameroun",       "Camerounaise",    "Afrique subsaharienne", "Yaoundé",     1, 0),
    Pays("251", "Yémen",          "Yéménite",        "Moyen-Orient",          "Sanaa",       1, 0),
    Pays("261", "Palestine",      "Palestinienne",   "Moyen-Orient",          "Ramallah",    1, 0),
    Pays("100", "France",         "Française",       "Europe",                "Paris",       0, 5),
    Pays("134", "Espagne",        "Espagnole",       "Europe",                "Madrid",      0, 3),
    Pays("131", "Belgique",       "Belge",           "Europe",                "Bruxelles",   0, 1),
    Pays("127", "Italie",         "Italienne",       "Europe",                "Rome",        0, 1),
]
CODE_MAROC = "350"

# États de l'inscription administrative (ETA_IAE)
EtatIAE = namedtuple("EtatIAE", "code libelle compte_dans_effectif")
ETATS_IAE = [
    EtatIAE("E", "En cours (valide)", "O"),
    EtatIAE("A", "Annulée",           "N"),
    EtatIAE("R", "Résiliée",          "N"),
]


# =====================================================================
#  Construction des nomenclatures dérivées
# =====================================================================
def ordinal(n: int) -> str:
    return "1ère" if n == 1 else f"{n}ème"


def code_etape(filiere: Filiere, annee_etude: int) -> str:
    return f"{filiere.code}{annee_etude}"


def version_etape(filiere: Filiere, cod_anu: int) -> str:
    return "2" if filiere.cycle == "Licence" and cod_anu >= ANNEE_REFORME_LICENCE else "1"


def construire_etapes() -> list[dict]:
    lignes = []
    for f in FILIERES:
        versions = ["1", "2"] if f.cycle == "Licence" else ["1"]
        for a in range(1, f.duree + 1):
            for v in versions:
                lignes.append({
                    "cod_etp": code_etape(f, a),
                    "cod_vrs_vet": v,
                    "lib_etp": f"{f.cycle} {f.libelle} - {ordinal(a)} année",
                    "cod_cmp": f.cmp,
                    "cod_filiere": f.code,
                    "lib_filiere": f.libelle,
                    "cycle": f.cycle,
                    "annee_etude": a,
                    "duree_cycle": f.duree,
                    "est_annee_terminale": "O" if a == f.duree else "N",
                })
    return lignes


def construire_elements_pedagogiques() -> list[dict]:
    """Un module = COD_ELP de la forme <étape><semestre sur 2 chiffres><n° module>, ex : SMI1011."""
    lignes = []
    for f in FILIERES:
        titres = DOMAINES[f.domaine]
        for a in range(1, f.duree + 1):
            for s_local in (1, 2):
                semestre = 2 * (a - 1) + s_local
                for k in range(1, MODULES_PAR_SEMESTRE + 1):
                    i = (a - 1) * 2 * MODULES_PAR_SEMESTRE + (s_local - 1) * MODULES_PAR_SEMESTRE + (k - 1)
                    titre = titres[i % len(titres)]
                    if i >= len(titres):
                        titre += " (approfondissement)"
                    lignes.append({
                        "cod_elp": f"{code_etape(f, a)}{semestre:02d}{k}",
                        "lib_elp": titre,
                        "cod_etp": code_etape(f, a),
                        "semestre": f"S{semestre}",
                        "nature_elp": "Module",
                    })
    return lignes


# =====================================================================
#  Export des seeds dbt
# =====================================================================
def _ecrire(nom: str, lignes: list[dict]) -> None:
    SEEDS_DIR.mkdir(parents=True, exist_ok=True)
    chemin = SEEDS_DIR / f"{nom}.csv"
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(lignes[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(lignes)
    print(f"[REFERENTIEL] {nom:<28} -> {len(lignes):>4} lignes -> {chemin}")


def exporter_seeds() -> None:
    _ecrire("ref_composante", [
        {"cod_cmp": c.code, "lib_cmp": c.libelle, "type_etablissement": c.type_etab, "mode_acces": c.mode_acces}
        for c in COMPOSANTES
    ])
    _ecrire("ref_etape", construire_etapes())
    _ecrire("ref_element_pedagogique", construire_elements_pedagogiques())
    _ecrire("ref_pays", [
        {"cod_pay": p.code, "lib_pays": p.pays, "lib_nationalite": p.nationalite, "zone_geographique": p.zone}
        for p in PAYS
    ])
    _ecrire("ref_departement_naissance",
        [{"cod_dep": p.code, "lib_province": p.province, "lib_region": p.region} for p in PROVINCES]
        + [{"cod_dep": CODE_DEP_ETRANGER, "lib_province": "Né(e) à l'étranger", "lib_region": "Étranger"}]
    )
    _ecrire("ref_etat_iae", [
        {"eta_iae": e.code, "lib_etat_iae": e.libelle, "compte_dans_effectif": e.compte_dans_effectif}
        for e in ETATS_IAE
    ])


if __name__ == "__main__":
    exporter_seeds()