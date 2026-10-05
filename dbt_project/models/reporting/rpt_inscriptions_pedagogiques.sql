{#
    Table de reporting : inscriptions pédagogiques (étudiant x module) avec libellés.
    Sert aux analyses par module, au suivi de la saisie et au calendrier des inscriptions.
#}
select
    p.cod_ind,

    -- Temps
    a.cod_anu,
    a.lib_annee_universitaire                                   as annee_universitaire,
    a.date_debut                                                as date_rentree,

    -- Organisation
    e.cod_cmp,
    e.lib_composante                                            as composante,
    e.lib_filiere                                               as filiere,
    e.cycle,
    case
        when e.annee_etude is null then 'Non renseigné'
        when e.annee_etude = 1     then '1ère année'
        else e.annee_etude::text || 'ème année'
    end                                                         as niveau,
    e.lib_etape                                                 as etape,
    m.cod_elp,
    m.lib_element_pedagogique                                   as module,
    coalesce(m.semestre, 'Non renseigné')                       as semestre,

    -- Profil
    d.sexe,

    -- Contrat
    p.est_pris_en_compte,
    case when p.est_pris_en_compte then 'Pris en compte'
         else 'Non pris en compte' end                          as prise_en_compte,

    -- Saisie
    p.date_creation,
    p.jour_creation,
    p.mois_creation,
    -- Mois dans l'ordre de l'année universitaire (septembre = 01) pour trier les graphiques
    lpad(((extract(month from p.date_creation)::int + 3) % 12 + 1)::text, 2, '0')
        || ' - ' ||
    (array['Janvier','Février','Mars','Avril','Mai','Juin','Juillet',
           'Août','Septembre','Octobre','Novembre','Décembre'])[extract(month from p.date_creation)::int]
                                                                as mois_saisie,
    p.est_modifie,
    p.delai_modification_jours,
    p.cod_uti                                                   as agent_saisie,
    p.type_saisie,
    p.a_inscription_administrative
from {{ ref('fct_inscription_pedagogique') }} as p
join {{ ref('dim_annee_universitaire') }} as a
    on a.cod_anu = p.cod_anu
left join {{ ref('dim_etape') }} as e
    on e.cle_etape = p.cle_etape
left join {{ ref('dim_element_pedagogique') }} as m
    on m.cod_elp = p.cod_elp
left join {{ ref('dim_etudiant') }} as d
    on d.cod_ind = p.cod_ind