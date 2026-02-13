SELECT 
    id_salarie,
    COUNT(*) AS nombre_activites_12_mois,
    COUNT(DISTINCT type_activity) AS nombre_types_activites
FROM {{ ref('silver_sport_activities_history') }}
WHERE date_start >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY id_salarie