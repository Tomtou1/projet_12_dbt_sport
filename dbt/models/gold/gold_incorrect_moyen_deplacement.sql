SELECT 
    id_salarie,
    salaire_brut,
    moyen_de_deplacement,
    distance_to_office_km, 
    moyen_de_deplacement_valide
FROM {{ ref('silver_rh_info') }}
WHERE moyen_de_deplacement_valide = 'incorrect'