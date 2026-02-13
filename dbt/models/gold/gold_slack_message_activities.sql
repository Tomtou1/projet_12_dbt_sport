SELECT *
FROM {{ ref('silver_sport_activities_history') }}
WHERE DATE(date_start) = CURRENT_DATE - INTERVAL '1 day'