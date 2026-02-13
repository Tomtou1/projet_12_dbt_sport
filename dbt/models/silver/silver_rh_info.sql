SELECT 
    *,
    CASE
        WHEN moyen_de_deplacement = 'Marche/running' AND distance_to_office_km > 15 THEN 'incorrect'
        WHEN moyen_de_deplacement = 'Vélo/Trottinette/Autres' AND distance_to_office_km > 25 THEN 'incorrect'
        ELSE moyen_de_deplacement
    END AS moyen_de_deplacement_valide
FROM {{ source('raw_data', 'rh_info') }}
WHERE distance_to_office_km IS NOT NULL