{{ config(
    materialized='incremental',
    unique_key=['id_salarie', 'activity_date'],
    incremental_strategy='delete+insert'
) }}

SELECT
    id_salarie,
    name_salarie,
    date_start::DATE AS activity_date,
    EXTRACT(EPOCH FROM (date_end - date_start)) / 60 AS duration_minutes,
    type_activity,
    distance_m,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ ref('silver_sport_activities_history') }}
WHERE date_start >= CURRENT_DATE - INTERVAL '1 day'
