SELECT
    id_duo,
    id_salarie,
    type_activity,
    CURRENT_TIMESTAMP AS dbt_loaded_at
FROM {{ source('raw_data', 'sport_enterprise') }}
WHERE type_activity != 'NaN'
