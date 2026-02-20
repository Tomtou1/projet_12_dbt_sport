{{ config(
    materialized='incremental',
    unique_key='bu_salarie',
    on_schema_change='ignore'
) }}

WITH activities_bu_last_12_months AS (
    SELECT 
        id_activity,
        bu_salarie,
        date_start
    FROM {{ ref('silver_sport_activities_history') }}
    WHERE date_start >= CURRENT_DATE - INTERVAL '12 months'
    
    {% if is_incremental() %}
        AND bu_salarie IN (
            SELECT DISTINCT bu_salarie 
            FROM {{ ref('silver_sport_activities_history') }}
            WHERE date_start > (
                SELECT COALESCE(MAX(derniere_activite), '1900-01-01')
                FROM {{ this }}
            )
        )
    {% endif %}
)

SELECT 
    bu_salarie,
    COUNT(*) AS nombre_activites_12_mois,
    MAX(date_start) AS derniere_activite,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM activities_bu_last_12_months
GROUP BY bu_salarie

