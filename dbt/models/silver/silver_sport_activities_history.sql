{{ config(
    materialized='incremental',
    unique_key='id_activity',
    on_schema_change='ignore'
) }}

WITH sport_activities AS (
    SELECT
        id_activity,
        id_salarie,
        date_start,
        type_activity,
        distance_m,
        date_end,
        comments
    FROM {{ source('raw_data', 'sport_activities_history') }}
    
    {% if is_incremental() %}
        WHERE date_start > (SELECT COALESCE(MAX(date_start), '1900-01-01') FROM {{ this }})
    {% endif %}
)

SELECT
    sa.id_activity,
    sa.id_salarie,
    rh.name_salarie,
    rh.bu_salarie,
    sa.date_start,
    sa.type_activity,
    sa.distance_m,
    sa.date_end,
    sa.comments,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM sport_activities sa
LEFT JOIN {{ ref('silver_rh_info') }} rh 
    ON sa.id_salarie = rh.id_salarie