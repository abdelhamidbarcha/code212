{#
    Dimension étudiant : profil démographique.

    Protection des données personnelles (loi 09-08) : l'email et le numéro INE
    ne sont PAS exposés dans les marts ; seuls des indicateurs de présence
    (a_email, a_ine) sont conservés pour le suivi de la qualité.
#}
with individus as (

    select * from {{ ref('stg_apogee__individu') }}

),

historique as (

    select
        cod_ind,
        min(cod_anu)               as premiere_annee_observee,
        max(cod_anu)               as derniere_annee_observee,
        count(distinct cod_anu)    as nb_annees_inscrit
    from {{ ref('stg_apogee__ins_adm_etp') }}
    group by cod_ind

)

select
    i.cod_ind,
    i.cod_etu,
    i.lib_prenom_ind || ' ' || i.lib_nom_pat_ind                      as nom_complet,
    case i.cod_sex_etu when 'F' then 'Femme' when 'M' then 'Homme'
                       else 'Non renseigné' end                        as sexe,
    i.date_naissance,
    extract(year from i.date_naissance)::integer                      as annee_naissance,

    coalesce(nat.lib_nationalite, 'Non renseignée')                   as nationalite,
    coalesce(nat.zone_geographique, 'Non renseignée')                 as zone_nationalite,
    i.cod_nat_etu is distinct from '350'                              as est_etranger,

    coalesce(pay.lib_pays, 'Non renseigné')                           as pays_naissance,
    coalesce(dep.lib_province, 'Non renseignée')                      as province_naissance,
    coalesce(dep.lib_region, 'Non renseignée')                        as region_naissance,
    i.lib_vil_nai_etu                                                 as ville_naissance,

    i.adr_mail_etu is not null                                        as a_email,
    i.numero_ine is not null                                          as a_ine,

    h.premiere_annee_observee,
    h.derniere_annee_observee,
    coalesce(h.nb_annees_inscrit, 0)::integer                         as nb_annees_inscrit
from individus as i
left join {{ ref('ref_pays') }} as nat
    on nat.cod_pay = i.cod_nat_etu
left join {{ ref('ref_pays') }} as pay
    on pay.cod_pay = i.cod_pay_nai_etu
left join {{ ref('ref_departement_naissance') }} as dep
    on dep.cod_dep = i.cod_dep_nai_etu
left join historique as h
    on h.cod_ind = i.cod_ind