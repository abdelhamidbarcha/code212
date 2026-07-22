select
    id_annee,
    libelle    as annee_academique,
    semestre,
    date_debut,
    date_fin
from {{ ref('stg_annees_academiques') }}
