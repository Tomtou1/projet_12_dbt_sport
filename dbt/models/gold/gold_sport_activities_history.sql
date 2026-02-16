{{ config(
    materialized='incremental',
    unique_key='id_salarie',
    on_schema_change='ignore'
) }}

WITH activities_last_12_months AS (
    SELECT 
        id_activity,
        id_salarie,
        type_activity,
        date_start
    FROM {{ ref('silver_sport_activities_history') }}
    WHERE date_start >= CURRENT_DATE - INTERVAL '12 months'
    
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
)

SELECT 
    id_salarie,
    COUNT(*) AS nombre_activites_12_mois,
    COUNT(DISTINCT type_activity) AS nombre_types_activites,
    MAX(date_start) AS derniere_activite,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM activities_last_12_months
GROUP BY id_salarie