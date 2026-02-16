{{ config(
    materialized='incremental',
    unique_key='id_activity',
    on_schema_change='ignore'
) }}

SELECT
    id_activity,
    id_salarie,
    date_start,
    type_activity,
    distance_m,
    date_end,
    comments,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ source('raw_data', 'sport_activities_history') }}

{% if is_incremental() %}
    WHERE date_start > (SELECT COALESCE(MAX(date_start), '1900-01-01') FROM {{ this }})
{% endif %}