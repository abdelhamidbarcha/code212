{#
    Table de reporting : inscriptions administratives avec tous les libellés.
    Une ligne par (étudiant, année, composante) — prête pour Superset (aucune jointure).
    Effectif = COUNT(DISTINCT cod_ind) avec le filtre est_comptabilise = vrai.
#}
select
    f.cod_ind,

    -- Temps
    a.cod_anu,
    a.lib_annee_universitaire                                   as annee_universitaire,
    a.est_derniere_annee,

    -- Organisation
    c.cod_cmp,
    c.lib_composante                                            as composante,
    c.type_etablissement,
    c.mode_acces,
    coalesce(e.lib_filiere, 'Non renseignée')                   as filiere,
    coalesce(e.cycle, 'Non renseigné')                          as cycle,
    case
        when e.annee_etude is null then 'Non renseigné'
        when e.annee_etude = 1     then '1ère année'
        else e.annee_etude::text || 'ème année'
    end                                                         as niveau,
    coalesce(e.lib_etape, 'Sans inscription pédagogique')       as etape,

    -- Profil
    d.sexe,
    d.nationalite,
    d.zone_nationalite,
    case when d.est_etranger then 'Étudiant étranger'
         else 'Étudiant marocain' end                           as origine,
    d.region_naissance,
    d.province_naissance,
    f.age_inscription,
    f.tranche_age,

    -- Inscription
    f.lib_etat_inscription                                      as etat_inscription,
    f.est_comptabilise,
    coalesce(f.type_inscription, 'Non comptabilisée')           as type_inscription,
    case
        when f.est_redoublant         then 'Redoublant'
        when not f.est_redoublant     then 'Non redoublant'
        else 'Non déterminé'
    end                                                         as redoublement,
    f.est_redoublant,
    f.est_reinscrit_annee_suivante,
    coalesce(f.statut_annee_suivante, 'Non comptabilisée')      as statut_annee_suivante,
    f.nb_modules_inscrits
from {{ ref('fct_inscription_administrative') }} as f
join {{ ref('dim_annee_universitaire') }} as a
    on a.cod_anu = f.cod_anu
join {{ ref('dim_composante') }} as c
    on c.cod_cmp = f.cod_cmp
left join {{ ref('dim_etape') }} as e
    on e.cle_etape = f.cle_etape
left join {{ ref('dim_etudiant') }} as d
    on d.cod_ind = f.cod_ind