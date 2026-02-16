SELECT 
    id_salarie,
    salaire_brut,
    moyen_de_deplacement_valide,
    CASE
        WHEN moyen_de_deplacement_valide IN ('Marche/running', 'Vélo/Trottinette/Autres') 
        THEN salaire_brut * 0.05
        ELSE 0
    END AS prime_mobilite_deplacement
FROM {{ ref('silver_rh_info') }}
WHERE moyen_de_deplacement_valide IN ('Marche/running', 'Vélo/Trottinette/Autres')
