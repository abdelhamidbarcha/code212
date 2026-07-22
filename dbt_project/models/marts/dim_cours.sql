select
    id_cours,
    code_cours,
    intitule,
    credits_ects,
    volume_horaire,
    nom_enseignant,
    grade_enseignant,
    nom_formation,
    nom_departement
from {{ ref('int_cours_enrichis') }}
