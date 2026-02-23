{{ config(
    materialized='incremental',
    unique_key='id_salarie',
    on_schema_change='ignore'
) }}

WITH activities_this_year AS (
    SELECT 
        id_activity,
        id_salarie,
        name_salarie,
        bu_salarie,
        type_activity,
        date_start
    FROM {{ ref('silver_sport_activities_history') }}
    WHERE date_start >= '2026-01-01'
    
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
        COUNT(*) AS nombre_activites_this_year,
        COUNT(DISTINCT type_activity) AS nombre_types_activites,
        MAX(date_start) AS derniere_activite
    FROM activities_this_year
    GROUP BY id_salarie, name_salarie, bu_salarie
)

SELECT 
    id_salarie,
    name_salarie,
    bu_salarie,
    nombre_activites_this_year,
    nombre_types_activites,
    derniere_activite,
    CASE
        WHEN nombre_activites_this_year > ((CURRENT_DATE - DATE '2026-01-01') / 365.0 * 14)
        THEN 5
        ELSE 0
    END AS journee_bien_etre,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM aggregated_activities