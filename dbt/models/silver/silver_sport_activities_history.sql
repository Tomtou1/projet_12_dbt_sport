SELECT
    id_salarie,
    date_start,
    type_activity,
    distance_m,
    date_end,
    comments
FROM {{ source('raw_data', 'sport_activities_history') }}