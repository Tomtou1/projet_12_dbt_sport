-- Clean and standardize HR employee data
SELECT
    id_salarie,
    bu_salarie,
    salaire_brut,
    type_contrat,
    jours_cp,
    adresse_domicile,
    moyen_de_deplacement
FROM {{ source('raw_data', 'rh_info') }}