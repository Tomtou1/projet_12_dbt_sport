SELECT
    id_duo,
    id_salarie,
    type_activity
FROM {{ source('raw_data', 'sport_enterprise') }}
WHERE type_activity != 'NaN'
