{#
    Suivi des chargements : historique et date de dernière mise à jour des données.
#}
select
    j.id_chargement,
    j.charge_le,
    j.table_cible,
    j.fichier,
    j.nb_lignes,
    j.source,
    row_number() over (partition by j.table_cible order by j.charge_le desc) = 1 as est_dernier_chargement
from {{ source('apogee', 'journal_chargement') }} as j