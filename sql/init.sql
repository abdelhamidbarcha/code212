-- ============================
-- SCHEMA SOURCE (RAW) — Système d'Information Académique
-- ============================

CREATE TABLE IF NOT EXISTS departements (
    id_departement   SERIAL PRIMARY KEY,
    nom_departement  VARCHAR(150) NOT NULL,
    faculte          VARCHAR(150),
    responsable      VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS formations (
    id_formation     SERIAL PRIMARY KEY,
    nom_formation    VARCHAR(150) NOT NULL,
    id_departement   INTEGER REFERENCES departements(id_departement),
    niveau           VARCHAR(30),
    type_diplome     VARCHAR(50),
    duree_annees     SMALLINT
);

CREATE TABLE IF NOT EXISTS enseignants (
    id_enseignant     SERIAL PRIMARY KEY,
    nom               VARCHAR(100) NOT NULL,
    prenom            VARCHAR(100) NOT NULL,
    grade             VARCHAR(50),
    id_departement    INTEGER REFERENCES departements(id_departement),
    email             VARCHAR(150),
    date_recrutement  DATE
);

CREATE TABLE IF NOT EXISTS etudiants (
    id_etudiant               SERIAL PRIMARY KEY,
    matricule                 VARCHAR(20) UNIQUE,
    nom                       VARCHAR(100) NOT NULL,
    prenom                    VARCHAR(100) NOT NULL,
    date_naissance            DATE,
    sexe                      CHAR(1),
    nationalite               VARCHAR(60),
    email                     VARCHAR(150),
    date_premiere_inscription DATE,
    statut                    VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS annees_academiques (
    id_annee    SERIAL PRIMARY KEY,
    libelle     VARCHAR(20) NOT NULL,
    semestre    VARCHAR(5),
    date_debut  DATE,
    date_fin    DATE
);

CREATE TABLE IF NOT EXISTS cours (
    id_cours        SERIAL PRIMARY KEY,
    code_cours      VARCHAR(20),
    intitule        VARCHAR(150) NOT NULL,
    credits_ects    SMALLINT,
    id_formation    INTEGER REFERENCES formations(id_formation),
    id_enseignant   INTEGER REFERENCES enseignants(id_enseignant),
    id_annee        INTEGER REFERENCES annees_academiques(id_annee),
    volume_horaire  SMALLINT
);

CREATE TABLE IF NOT EXISTS inscriptions (
    id_inscription      SERIAL PRIMARY KEY,
    id_etudiant         INTEGER REFERENCES etudiants(id_etudiant),
    id_formation        INTEGER REFERENCES formations(id_formation),
    id_annee            INTEGER REFERENCES annees_academiques(id_annee),
    date_inscription    DATE,
    statut_inscription  VARCHAR(30),
    mode                VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS notes (
    id_note          SERIAL PRIMARY KEY,
    id_etudiant      INTEGER REFERENCES etudiants(id_etudiant),
    id_cours         INTEGER REFERENCES cours(id_cours),
    id_annee         INTEGER REFERENCES annees_academiques(id_annee),
    type_evaluation  VARCHAR(30),
    note             NUMERIC(4,2) CHECK (note BETWEEN 0 AND 20),
    date_evaluation  DATE
);

-- Index utiles pour les futures jointures et filtres BI
CREATE INDEX IF NOT EXISTS idx_notes_etudiant ON notes(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_notes_cours ON notes(id_cours);
CREATE INDEX IF NOT EXISTS idx_inscriptions_etudiant ON inscriptions(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_cours_formation ON cours(id_formation);