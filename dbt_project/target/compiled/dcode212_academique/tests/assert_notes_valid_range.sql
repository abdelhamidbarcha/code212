select id_note, note
from "etudiants_db"."public_staging"."stg_notes"
where note < 0 or note > 20