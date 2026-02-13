CREATE TABLE sport_activities_history (
    id_activity INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_salarie INT NOT NULL,
    date_start TIMESTAMP NOT NULL,
    type_activity VARCHAR(50) NOT NULL,
    distance_m INT,
    date_end TIMESTAMP NOT NULL,
    comments TEXT
);

ALTER TABLE sport_activities_history
REPLICA IDENTITY FULL;

-- 1ère insertion de données pour la table sport_activities
INSERT INTO sport_activities_history (id_salarie, date_start, type_activity, distance_m, date_end, comments)
VALUES
( 56482, '2025-01-02 10:00:00', 'Tennis', NULL, '2025-01-02 11:00:00', 'Super match avec mon frère!');