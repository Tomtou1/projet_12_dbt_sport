{{ config(
    materialized='incremental',
    unique_key='id_salarie',
    on_schema_change='ignore'
) }}

WITH activities_2025 AS (
    SELECT 
        id_activity,
        id_salarie,
        name_salarie,
        bu_salarie,
        type_activity,
        date_start
    FROM {{ ref('silver_sport_activities_history') }}
    WHERE date_start >= '2025-01-01' AND date_start <= '2025-12-31'
    
    {% if is_incremental() %}
        AND id_salarie IN (
            SELECT DISTINCT id_salarie 
            FROM {{ ref('silver_sport_activities_history') }}
            WHERE date_start > (
                SELECT COALESCE(MAX(derniere_activite), '1900-01-01')
                FROM {{ this }}
            )
        )
    {% endif %}
),

aggregated_activities AS (
    SELECT 
        id_salarie,
        name_salarie,
        bu_salarie,
        COUNT(*) AS nombre_activites_2025,
        COUNT(DISTINCT type_activity) AS nombre_types_activites,
        MAX(date_start) AS derniere_activite
    FROM activities_2025
    GROUP BY id_salarie, name_salarie, bu_salarie
    HAVING COUNT(*) > 3
)

SELECT 
    id_salarie,
    name_salarie,
    bu_salarie,
    nombre_activites_2025,
    nombre_types_activites,
    derniere_activite,
    CASE
        WHEN nombre_activites_2025 > 14 
        THEN 5
        ELSE 0
    END AS journee_bien_etre
FROM aggregated_activities
ORDER BY nombre_activites_2025 DESC