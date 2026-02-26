import time
import random
from datetime import datetime, timedelta
from unittest import case
import psycopg2
import pandas as pd
import googlemaps
import os
from dotenv import load_dotenv


def connexion_sql():
    load_dotenv()
    
    hostname = "postgres_sport"
    port_id = 5432
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")

    conn  = psycopg2.connect(
        host=hostname,
        port=port_id,
        user=username,
        password=password,
        database=database
    )
    print(f"Connecté à la base de données {database} sur {hostname}:{port_id} en tant qu'utilisateur {username}.")
    return conn

def create_sql_table_sport_enterprise(conn):
    # Create the table sport_enterprise
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS sport_enterprise (
    id_duo INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_salarie INT NOT NULL,
    type_activity VARCHAR(50)
    );''')
    conn.commit()
    
    # Check if table exist
    cur.execute("SELECT COUNT(*) FROM sport_enterprise")
    existing_count = cur.fetchone()[0]

    if existing_count > 0:
        print(f"✓ Table sport_enterprise existe et contient {existing_count} lignes.")
        return 
    
    # Read the Excel file
    excel_file_path = 'data/Donnees_Sportive.xlsx'
    df = pd.read_excel(excel_file_path)
    
    # Insert data into the table
    inserted_count = 0
    for row in df.iterrows():
        id_salarie = row[1]['ID salarié']
        type_activity = row[1]['Pratique d\'un sport']

        cur.execute("INSERT INTO sport_enterprise (id_salarie, type_activity) VALUES (%s, %s)",
                    (int(id_salarie), type_activity)
                   )
        inserted_count += 1
    conn.commit()
    print(f"{inserted_count} activités sportives insérées")

def create_sql_table_RH(conn):
    # Create the table RH_info
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS RH_info (
    id_salarie INT NOT NULL PRIMARY KEY,
    first_name_salarie VARCHAR(50) NOT NULL,
    last_name_salarie VARCHAR(50) NOT NULL,
    bu_salarie VARCHAR(50) NOT NULL,
    salaire_brut INT NOT NULL,
    type_contrat VARCHAR(10) NOT NULL,
    jours_cp INT NOT NULL,
    adresse_domicile TEXT, 
    moyen_de_deplacement VARCHAR(50) NOT NULL
    );''')
    conn.commit()
    
    # Check if table exist
    cur.execute("SELECT COUNT(*) FROM RH_info")
    existing_count = cur.fetchone()[0]

    if existing_count > 0:
        print(f"✓ Table RH_info existe et contient {existing_count} lignes.")
        return
    
    # Read the Excel file
    excel_file_path = 'data/Donnees_RH.xlsx'
    df = pd.read_excel(excel_file_path)
    
    # Insert data into the table
    inserted_count = 0
    for row in df.iterrows():
        id_salarie = row[1]['ID salarié']
        first_name_salarie = row[1]['Prénom']
        last_name_salarie = row[1]['Nom']
        bu_salarie = row[1]['BU']
        salaire_brut = row[1]['Salaire brut']
        type_contrat = row[1]['Type de contrat']
        jours_cp = row[1]['Nombre de jours de CP']
        adresse_domicile = row[1]['Adresse du domicile']
        moyen_de_deplacement = row[1]['Moyen de déplacement']

        cur.execute("""
            INSERT INTO RH_info 
            (id_salarie, first_name_salarie, last_name_salarie, bu_salarie, salaire_brut, type_contrat, jours_cp, adresse_domicile, moyen_de_deplacement) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_salarie) DO NOTHING
            """,
            (int(id_salarie), first_name_salarie, last_name_salarie, bu_salarie, salaire_brut, type_contrat, jours_cp, adresse_domicile, moyen_de_deplacement)
        )
        inserted_count += 1
        conn.commit()
    print(f"{inserted_count} informations RH insérées")

def add_distance_to_office(conn, api_use):
    cur = conn.cursor()
    cur.execute("ALTER TABLE RH_info ADD COLUMN IF NOT EXISTS distance_to_office_km FLOAT")
    conn.commit()

    #Get employee where distance is not yet calculated
    cur.execute("SELECT id_salarie, moyen_de_deplacement, adresse_domicile FROM RH_info WHERE distance_to_office_km IS NULL")
    employees = cur.fetchall()
    gmaps_dict_mode = {
        "véhicule thermique/électrique": "driving",
        "Transports en commun": "transit",
        "Vélo/Trottinette/Autres": "bicycling",
        "Marche/running": "walking"
    }

    if len(employees) == 0:
        print("Toutes les distances sont déjà calculées.")
        return
    else:
        print(f"Calcul de la distance pour {len(employees)} employés...")
        for employee in employees:
            id_salarie = employee[0]
            moyen_de_deplacement = employee[1]  
            adresse_domicile = employee[2]  

            print(f" {id_salarie} a le mode de deplacement: {moyen_de_deplacement}, le mode gmaps est donc {gmaps_dict_mode.get(moyen_de_deplacement, 'driving')}")
            if api_use:
                load_dotenv()
                gmaps = googlemaps.Client(key=os.getenv("GCP_key"))
                adresse_entreprise = "1362 Av. des Platanes, 34970 Lattes"
                result = gmaps.distance_matrix(adresse_entreprise, adresse_domicile, mode=gmaps_dict_mode.get(moyen_de_deplacement, "driving"), units='metric')
                distance_to_office_km = result["rows"][0]["elements"][0]["distance"]["value"] / 1000  # Convert to km
            else:
                # Simulate distance calculation (replace with actual API call if needed)
                distance_to_office_km = random.uniform(1, 50)  # Simulated distance in km

            cur.execute("UPDATE RH_info SET distance_to_office_km = %s WHERE id_salarie = %s",
                        (distance_to_office_km, id_salarie))
        conn.commit()

def clean_adresses(conn):
    cur = conn.cursor()
    cur.execute("SELECT id_salarie, adresse_domicile, distance_to_office_km FROM RH_info")
    employees = cur.fetchall()

    for employee in employees:
        id_salarie = employee[0]
        distance_office = employee[2]

        if distance_office >0:
            cur.execute("UPDATE RH_info SET adresse_domicile = NULL WHERE id_salarie = %s", (id_salarie,))
                    
    conn.commit()       

def generate_history_activity(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sport_activities_history")
    existing_count = cur.fetchone()[0]

    if existing_count < 2000:
        range_start_date = datetime(2025, 1, 1).timestamp()
        range_end_date = datetime(2026, 1, 15).timestamp()
    elif existing_count >= 2000 and existing_count < 2250:
        range_start_date = datetime(2026, 1, 16).timestamp()
        range_end_date = datetime(2026, 1, 31).timestamp() # January 2026
    else:
        range_start_date = datetime(2026, 2, 1).timestamp()
        range_end_date = datetime.now().timestamp() - 24*3600  # Up to yesterday
    

    start_dt = datetime.fromtimestamp(random.uniform(range_start_date, range_end_date))
    time_activity = random.randint(30, 180)  # Duration between 30 minutes and 3 hours
    end_dt = start_dt + timedelta(minutes=time_activity)

    cur = conn.cursor()
    # Get all employee IDs and their sports activities
    cur.execute("SELECT id_salarie, type_activity FROM sport_enterprise")
    employees = cur.fetchall()

    random_employee = random.choice(employees)
    while random_employee[1] == "NaN":
        random_employee = random.choice(employees)

    id_salarie = random_employee[0]
    type_activity = random_employee[1]
    
    date_start = start_dt.strftime("%Y-%m-%d %H:%M:%S")

    # depending which activity, we decide the distance:
    match type_activity:
        case "Randonnée":
            distance_m = random.randint(3000, 6000)/60*time_activity  # between 3000 and 6000 meters per hour
        case "Runing":
            distance_m = random.randint(5000, 15000)/60*time_activity  # between 5000 and 15000 meters per hour
        case "Natation":
            distance_m = random.randint(600, 2500)/60*time_activity  # between 600 and 2500 meters per hour
        case _:
            distance_m = None

    date_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    comments = f"Score: {random.randint(0, 10)}/10"

    cur.execute(
        "INSERT INTO sport_activities_history (id_salarie, date_start, type_activity, distance_m, date_end, comments) VALUES (%s, %s, %s, %s, %s, %s)",
        (id_salarie, date_start, type_activity, distance_m, date_end, comments)
        )
    conn.commit()

if __name__ == "__main__":
    print("Démarrage du producteur d'activités sportives...")
    conn = connexion_sql()
    cur = conn.cursor()
    
    #Create table wih activities of each employee, and RH table with info about employees
    create_sql_table_sport_enterprise(conn)
    create_sql_table_RH(conn)
    add_distance_to_office(conn, True)
    clean_adresses(conn)

    #Create history of activity 
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sport_activities_history")
    existing_count = cur.fetchone()[0]

    if existing_count < 5:
        n_history_activities = 1999
    else:
        n_history_activities = 250
        
    for _ in range(n_history_activities):
        generate_history_activity(conn)

    print(f"{n_history_activities} activités générées.")
    #while True:
    #    generate_history_activity(conn)
    #    time.sleep(2)  # Wait for 2 seconds before generating the next activity
    # Close connection
    cur.close()
    conn.close()
    print("Connexion fermée.")