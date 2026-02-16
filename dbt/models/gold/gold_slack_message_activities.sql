{{ config(
    materialized='incremental',
    unique_key=['id_salarie', 'activity_date'],
    incremental_strategy='delete+insert'
) }}

SELECT
    id_salarie,
    DATE(date_start) AS activity_date,
    type_activity,
    distance_m,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('silver_sport_activities_history') }}
WHERE date_start >= CURRENT_DATE - INTERVAL '1 day'
