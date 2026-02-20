WITH base_data AS (
    SELECT 
        *,
        CASE
            WHEN moyen_de_deplacement = 'Marche/running' AND distance_to_office_km > 15 THEN 'incorrect'
            WHEN moyen_de_deplacement = 'Vélo/Trottinette/Autres' AND distance_to_office_km > 25 THEN 'incorrect'
            ELSE moyen_de_deplacement
        END AS moyen_de_deplacement_valide
    FROM {{ source('raw_data', 'rh_info') }}
    WHERE distance_to_office_km IS NOT NULL
),

name_candidates AS (
    SELECT 
        *,
        first_name_salarie AS candidate_name,
        0 AS last_name_chars,
        COUNT(*) OVER (PARTITION BY first_name_salarie) AS name_count_0
    FROM base_data
    
    UNION ALL
    
    SELECT 
        *,
        first_name_salarie || ' ' || LEFT(last_name_salarie, 1) AS candidate_name,
        1 AS last_name_chars,
        COUNT(*) OVER (PARTITION BY first_name_salarie || ' ' || LEFT(last_name_salarie, 1)) AS name_count_0
    FROM base_data
    
    UNION ALL
    
    SELECT 
        *,
        first_name_salarie || ' ' || LEFT(last_name_salarie, 2) AS candidate_name,
        2 AS last_name_chars,
        COUNT(*) OVER (PARTITION BY first_name_salarie || ' ' || LEFT(last_name_salarie, 2)) AS name_count_0
    FROM base_data
    
    UNION ALL
    
    SELECT 
        *,
        first_name_salarie || ' ' || LEFT(last_name_salarie, 3) AS candidate_name,
        3 AS last_name_chars,
        COUNT(*) OVER (PARTITION BY first_name_salarie || ' ' || LEFT(last_name_salarie, 3)) AS name_count_0
    FROM base_data
    
    UNION ALL
    
    SELECT 
        *,
        first_name_salarie || ' ' || last_name_salarie AS candidate_name,
        LENGTH(last_name_salarie) AS last_name_chars,
        COUNT(*) OVER (PARTITION BY first_name_salarie || ' ' || last_name_salarie) AS name_count_0
    FROM base_data
),

-- Select the shortest unique name for each employee
ranked_names AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id_salarie 
            ORDER BY 
                CASE WHEN name_count_0 = 1 THEN 0 ELSE 1 END,
                last_name_chars
        ) AS rn
    FROM name_candidates
)

SELECT 
    id_salarie,
    candidate_name AS name_salarie,
    bu_salarie,
    salaire_brut,
    type_contrat,
    jours_cp,
    adresse_domicile,
    moyen_de_deplacement,
    moyen_de_deplacement_valide,
    distance_to_office_km,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM ranked_names
WHERE rn = 1