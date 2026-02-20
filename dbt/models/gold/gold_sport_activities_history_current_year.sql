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
)

SELECT 
    id_salarie,
    name_salarie,
    bu_salarie,
    COUNT(*) AS nombre_activites_12_mois,
    COUNT(DISTINCT type_activity) AS nombre_types_activites,
    MAX(date_start) AS derniere_activite,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM activities_this_year
GROUP BY id_salarie,name_salarie,bu_salarie