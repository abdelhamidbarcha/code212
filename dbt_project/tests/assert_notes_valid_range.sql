select id_note, note
from {{ ref('stg_notes') }}
where note < 0 or note > 20
