SELECT 
    id_salarie,
    salaire_brut,
    moyen_de_deplacement,
    distance_to_office_km,
    moyen_de_deplacement_valide,
    salaire_brut * 0.05 AS prime_mobilite_deplacement,
    CASE
        WHEN distance_to_office_km < 5 
        THEN salaire_brut * 0.05
        ELSE 0
    END AS prime_mobilite_deplacement_proche
FROM {{ ref('silver_rh_info') }}
WHERE moyen_de_deplacement_valide NOT IN ('Marche/running', 'Vélo/Trottinette/Autres', 'incorrect') AND distance_to_office_km < 25