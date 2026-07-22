select
    id_formation,
    nom_formation,
    niveau,
    type_diplome,
    duree_annees,
    nom_departement,
    faculte
from {{ ref('int_formations_enrichies') }}
