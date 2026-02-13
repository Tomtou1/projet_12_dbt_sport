SELECT 
    id_salarie,
    salaire_brut,
    moyen_de_deplacement,
    distance_to_office_km,
    moyen_de_deplacement_valide,
    salaire_brut * 0.05 AS prime_mobilite_deplacement
FROM {{ ref('silver_rh_info') }}
WHERE moyen_de_deplacement_valide NOT IN ('Marche/running', 'Vélo/Trottinette/Autres', 'incorrect') AND distance_to_office_km < 25