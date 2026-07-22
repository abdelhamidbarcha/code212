select
    id_etudiant,
    matricule,
    nom_complet,
    age,
    tranche_age,
    sexe,
    nationalite,
    statut
from {{ ref('int_etudiants_enrichis') }}
