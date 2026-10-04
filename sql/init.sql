-- =====================================================================
--  SCHÉMA RAW — Réplique des tables sources Apogée
-- ---------------------------------------------------------------------
--  Principes :
--   * Couche d'atterrissage "telle quelle" : noms de colonnes identiques
--     au référentiel Apogée (en minuscules).
--   * Colonnes métier en TEXT : aucune donnée réelle n'est rejetée au
--     chargement à cause d'un format inattendu. Le typage, le nettoyage
--     et les contrôles qualité sont réalisés par dbt (couche staging).
--   * Pas de PK/FK : l'unicité et l'intégrité référentielle sont
--     vérifiées par les tests dbt.
--   * Colonnes techniques préfixées par "_" pour la traçabilité.
--  Script idempotent : il peut être rejoué sans erreur.
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS raw;
COMMENT ON SCHEMA raw IS 'Données brutes issues d''Apogée (ou du générateur), chargées sans transformation.';


-- =====================================================================
--  1. INDIVIDU — Référentiel des étudiants
-- =====================================================================
CREATE TABLE IF NOT EXISTS raw.individu (
    cod_ind           TEXT,
    cod_etu           TEXT,
    numero_ine        TEXT,
    cle_ine           TEXT,
    lib_nom_pat_ind   TEXT,
    lib_prenom_ind    TEXT,
    cod_sex_etu       TEXT,
    date_naissance    TEXT,
    lib_vil_nai_etu   TEXT,
    cod_pay_nai_etu   TEXT,
    cod_nat_etu       TEXT,
    cod_dep_nai_etu   TEXT,
    adr_mail_etu      TEXT,
    -- Colonnes techniques
    _source           TEXT        NOT NULL DEFAULT 'inconnue',
    _loaded_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  raw.individu                 IS 'Référentiel des individus (étudiants) — source Apogée INDIVIDU.';
COMMENT ON COLUMN raw.individu.cod_ind         IS 'Code individu : identifiant interne de l''individu dans la base Apogée.';
COMMENT ON COLUMN raw.individu.cod_etu         IS 'Code étudiant : numéro étudiant (identifiant à 8 chiffres).';
COMMENT ON COLUMN raw.individu.numero_ine      IS 'Numéro INE : Numéro d''Inscription National Étudiant.';
COMMENT ON COLUMN raw.individu.cle_ine         IS 'Clé INE : clé de contrôle du numéro INE.';
COMMENT ON COLUMN raw.individu.lib_nom_pat_ind IS 'Nom de naissance : nom de famille.';
COMMENT ON COLUMN raw.individu.lib_prenom_ind  IS 'Prénom(s) de l''étudiant.';
COMMENT ON COLUMN raw.individu.cod_sex_etu     IS 'Sexe : civilité de l''étudiant.';
COMMENT ON COLUMN raw.individu.date_naissance  IS 'Date de naissance complète.';
COMMENT ON COLUMN raw.individu.lib_vil_nai_etu IS 'Ville de naissance : libellé de la ville de naissance.';
COMMENT ON COLUMN raw.individu.cod_pay_nai_etu IS 'Pays de naissance : code du pays de naissance.';
COMMENT ON COLUMN raw.individu.cod_nat_etu     IS 'Nationalité : code de la nationalité.';
COMMENT ON COLUMN raw.individu.cod_dep_nai_etu IS 'Département de naissance : code du département de naissance.';
COMMENT ON COLUMN raw.individu.adr_mail_etu    IS 'Email : adresse électronique de l''étudiant.';
COMMENT ON COLUMN raw.individu._source         IS 'Technique : origine de la ligne (generateur / apogee).';
COMMENT ON COLUMN raw.individu._loaded_at      IS 'Technique : horodatage du chargement.';


-- =====================================================================
--  2. INS_ADM_ETP — Inscriptions administratives
-- =====================================================================
CREATE TABLE IF NOT EXISTS raw.ins_adm_etp (
    cod_ind     TEXT,
    cod_anu     TEXT,
    eta_iae     TEXT,
    cod_cmp     TEXT,
    -- Colonnes techniques
    _source     TEXT        NOT NULL DEFAULT 'inconnue',
    _loaded_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  raw.ins_adm_etp            IS 'Inscriptions administratives annuelles — source Apogée INS_ADM_ETP.';
COMMENT ON COLUMN raw.ins_adm_etp.cod_ind    IS 'Code individu : identifiant de l''individu, utilisé pour joindre la table INDIVIDU.';
COMMENT ON COLUMN raw.ins_adm_etp.cod_anu    IS 'Code année universitaire concernée par l''inscription administrative.';
COMMENT ON COLUMN raw.ins_adm_etp.eta_iae    IS 'État de l''inscription administrative (ex : E = inscription active).';
COMMENT ON COLUMN raw.ins_adm_etp.cod_cmp    IS 'Code composante (UFR, faculté) de rattachement.';
COMMENT ON COLUMN raw.ins_adm_etp._source    IS 'Technique : origine de la ligne (generateur / apogee).';
COMMENT ON COLUMN raw.ins_adm_etp._loaded_at IS 'Technique : horodatage du chargement.';


-- =====================================================================
--  3. IND_CONTRAT_ELP — Inscriptions pédagogiques (contrats ELP)
-- =====================================================================
CREATE TABLE IF NOT EXISTS raw.ind_contrat_elp (
    cod_ind          TEXT,
    cod_elp          TEXT,
    cod_anu          TEXT,
    cod_etp          TEXT,
    cod_vrs_vet      TEXT,
    tem_prc_ice      TEXT,
    dat_cre_elp_con  TEXT,
    dat_mod_ice      TEXT,
    cod_uti          TEXT,
    -- Colonnes techniques
    _source          TEXT        NOT NULL DEFAULT 'inconnue',
    _loaded_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  raw.ind_contrat_elp                 IS 'Inscriptions pédagogiques aux éléments pédagogiques — source Apogée IND_CONTRAT_ELP.';
COMMENT ON COLUMN raw.ind_contrat_elp.cod_ind         IS 'Code individu : identifiant de l''étudiant, utilisé pour joindre la table INDIVIDU.';
COMMENT ON COLUMN raw.ind_contrat_elp.cod_elp         IS 'Code de l''élément pédagogique concerné par l''inscription.';
COMMENT ON COLUMN raw.ind_contrat_elp.cod_anu         IS 'Année universitaire de l''inscription pédagogique.';
COMMENT ON COLUMN raw.ind_contrat_elp.cod_etp         IS 'Code de l''étape (formation) associée.';
COMMENT ON COLUMN raw.ind_contrat_elp.cod_vrs_vet     IS 'Numéro de version de l''étape.';
COMMENT ON COLUMN raw.ind_contrat_elp.tem_prc_ice     IS 'Témoin de prise en compte : indicateur de prise en compte pour calcul.';
COMMENT ON COLUMN raw.ind_contrat_elp.dat_cre_elp_con IS 'Date de création du contrat pédagogique.';
COMMENT ON COLUMN raw.ind_contrat_elp.dat_mod_ice     IS 'Date de dernière modification.';
COMMENT ON COLUMN raw.ind_contrat_elp.cod_uti         IS 'Code de l''utilisateur ayant créé/modifié l''inscription.';
COMMENT ON COLUMN raw.ind_contrat_elp._source         IS 'Technique : origine de la ligne (generateur / apogee).';
COMMENT ON COLUMN raw.ind_contrat_elp._loaded_at      IS 'Technique : horodatage du chargement.';


-- =====================================================================
--  Index sur les clés de jointure (accélèrent les modèles dbt)
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_raw_individu_cod_ind       ON raw.individu (cod_ind);
CREATE INDEX IF NOT EXISTS idx_raw_ins_adm_etp_ind_anu    ON raw.ins_adm_etp (cod_ind, cod_anu);
CREATE INDEX IF NOT EXISTS idx_raw_contrat_elp_ind_anu    ON raw.ind_contrat_elp (cod_ind, cod_anu);
CREATE INDEX IF NOT EXISTS idx_raw_contrat_elp_etp_elp    ON raw.ind_contrat_elp (cod_etp, cod_elp);


-- =====================================================================
--  Journal des chargements (historique conservé, jamais vidé)
-- =====================================================================
CREATE TABLE IF NOT EXISTS raw.journal_chargement (
    id_chargement  BIGSERIAL   PRIMARY KEY,
    charge_le      TIMESTAMPTZ NOT NULL DEFAULT now(),
    table_cible    TEXT        NOT NULL,
    fichier        TEXT,
    nb_lignes      INTEGER     NOT NULL,
    source         TEXT        NOT NULL
);
COMMENT ON TABLE raw.journal_chargement IS 'Historique des chargements : date, table, volume et origine des données.';