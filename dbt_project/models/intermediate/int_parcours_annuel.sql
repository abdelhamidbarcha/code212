{#
    Parcours annuel de chaque étudiant : situation l'année précédente et
    l'année suivante, pour qualifier chaque inscription.

    - type_inscription : Nouvel inscrit / Réinscrit / Non déterminé
      (première année de l'historique : impossible de savoir si l'étudiant était déjà inscrit)
    - est_redoublant : même étape que l'année précédente
    - statut_annee_suivante : Passage, Redoublement, Poursuite des études, Réorientation,
      Sortie en fin de cycle (diplômé probable), Sortie en cours de cycle (abandon probable)

    Seules les inscriptions comptabilisées dans les effectifs (ETA_IAE valide)
    servent à reconstituer les parcours.
    Grain : une ligne par (cod_ind, cod_anu).
#}
with inscriptions as (

    select
        i.cod_ind,
        i.cod_anu,
        bool_or(coalesce(e.compte_dans_effectif = 'O', false)) as est_comptabilise
    from {{ ref('stg_apogee__ins_adm_etp') }} as i
    left join {{ ref('ref_etat_iae') }} as e
        on e.eta_iae = i.eta_iae
    group by 1, 2

),

etapes as (

    select distinct on (cod_etp)
        cod_etp,
        cod_filiere,
        annee_etude,
        est_annee_terminale = 'O' as est_annee_terminale
    from {{ ref('ref_etape') }}
    order by cod_etp, cod_vrs_vet desc

),

annuel as (

    select
        ins.cod_ind,
        ins.cod_anu,
        ins.est_comptabilise,
        ep.cod_etp,
        ep.cle_etape,
        ep.nb_modules,
        et.cod_filiere,
        et.annee_etude,
        coalesce(et.est_annee_terminale, false) as est_annee_terminale
    from inscriptions as ins
    left join {{ ref('int_etape_principale_annuelle') }} as ep
        on  ep.cod_ind = ins.cod_ind
        and ep.cod_anu = ins.cod_anu
    left join etapes as et
        on et.cod_etp = ep.cod_etp

),

bornes as (

    select min(cod_anu) as annee_min, max(cod_anu) as annee_max
    from inscriptions

),

valides as (

    select
        a.cod_ind,
        a.cod_anu,
        min(a.cod_anu)       over (partition by a.cod_ind)                  as premiere_annee,
        lag(a.cod_anu)       over (partition by a.cod_ind order by a.cod_anu) as annee_prec,
        lag(a.cod_etp)       over (partition by a.cod_ind order by a.cod_anu) as etape_prec,
        lead(a.cod_anu)      over (partition by a.cod_ind order by a.cod_anu) as annee_suiv,
        lead(a.cod_filiere)  over (partition by a.cod_ind order by a.cod_anu) as filiere_suiv,
        lead(a.annee_etude)  over (partition by a.cod_ind order by a.cod_anu) as niveau_suiv
    from annuel as a
    where a.est_comptabilise

)

select
    a.cod_ind,
    a.cod_anu,
    a.est_comptabilise,
    a.cod_etp,
    a.cle_etape,
    coalesce(a.nb_modules, 0) as nb_modules,

    case
        when not a.est_comptabilise         then null
        when a.cod_anu = b.annee_min        then 'Non déterminé'
        when a.cod_anu = v.premiere_annee   then 'Nouvel inscrit'
        else 'Réinscrit'
    end as type_inscription,

    case
        when not a.est_comptabilise   then null
        when a.cod_anu = b.annee_min  then null     -- année précédente inconnue
        else coalesce(v.annee_prec = a.cod_anu - 1 and v.etape_prec = a.cod_etp, false)
    end as est_redoublant,

    case
        when not a.est_comptabilise   then null
        when a.cod_anu = b.annee_max  then null
        else coalesce(v.annee_suiv = a.cod_anu + 1, false)
    end as est_reinscrit_annee_suivante,

    case
        when not a.est_comptabilise          then null
        when a.cod_anu = b.annee_max         then 'Non disponible'
        when v.annee_suiv = a.cod_anu + 1 then
            case
                when v.filiere_suiv is null or a.cod_filiere is null       then 'Réinscription'
                when v.filiere_suiv = a.cod_filiere
                     and v.niveau_suiv = a.annee_etude                     then 'Redoublement'
                when v.filiere_suiv = a.cod_filiere
                     and v.niveau_suiv = a.annee_etude + 1                 then 'Passage au niveau supérieur'
                when a.est_annee_terminale                                 then 'Poursuite des études'
                else 'Réorientation'
            end
        when a.est_annee_terminale           then 'Sortie en fin de cycle'
        else 'Sortie en cours de cycle'
    end as statut_annee_suivante

from annuel as a
cross join bornes as b
left join valides as v
    on  v.cod_ind = a.cod_ind
    and v.cod_anu = a.cod_anu