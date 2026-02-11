import time
import random
from datetime import datetime, timedelta
import psycopg2
import pandas as pd

def connexion_sql():
    hostname = "postgres"
    port_id = 5432
    username = "postgresuser"
    password = "postgrespw"
    database = "sport_activities_db"

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
    # Create the table
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS sport_enterprise (
    id_duo INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_salarie INT NOT NULL,
    type_activity VARCHAR(50) NOT NULL
    );''')
    conn.commit()
    
    # Read the Excel file
    excel_file_path = 'data/Donnees_Sportive.xlsx'
    df = pd.read_excel(excel_file_path)
    
    # Insert data into the table
    inserted_count = 0
    for row in df.iterrows():
        id_salarie = row[1]['ID salarié']
        type_activity = row[1]['Pratique d\'un sport']
        
        if type(type_activity) == str:
            print((int(id_salarie), type_activity))
            cur.execute(
                "INSERT INTO sport_enterprise (id_salarie, type_activity) VALUES (%s, %s)",
                (int(id_salarie), type_activity)
            )
            inserted_count += 1 
        conn.commit()
    print(f"{inserted_count} activités sportives insérées")

def generate_history_activity(conn):
    range_start_date = datetime(2025, 1, 1).timestamp()
    range_end_date = datetime(2025, 12, 31).timestamp()

    start_dt = datetime.fromtimestamp(random.uniform(range_start_date, range_end_date))
    end_dt = start_dt + timedelta(hours=random.randint(1, 3))  


    cur = conn.cursor()
    # Get all employee IDs and their sports activities
    cur.execute("SELECT id_salarie, type_activity FROM sport_enterprise")
    employees = cur.fetchall()
    random_employee = random.choice(employees)
    id_salarie = random_employee[0]
    date_start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    type_activity = random_employee[1]
    distance_m = random.randint(1000, 20000) if type_activity in ['Randonnée', 'Running', 'Natation'] else None
    date_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    comments = f"Score: {random.randint(0, 10)}/10"

    print(f"Generated activity for employee {id_salarie}: {type_activity} from {date_start} to {date_end} with distance {distance_m}m and comments '{comments}'")
    cur.execute(
        "INSERT INTO sport_activities (id_salarie, date_start, type_activity, distance_m, date_end, comments) VALUES (%s, %s, %s, %s, %s, %s)",
        (id_salarie, date_start, type_activity, distance_m, date_end, comments)
        )
    conn.commit()

if __name__ == "__main__":
    print("Démarrage du producteur d'activités sportives...")
    conn = connexion_sql()
    cur = conn.cursor()
    
    #Create table wih activities of each employee
    create_sql_table_sport_enterprise(conn)

    #Create history of activity
    n_history_activities = 10
    for _ in range(n_history_activities):
        generate_history_activity(conn)

    while True:
        generate_history_activity(conn)
        time.sleep(2)  # Wait for 2 seconds before generating the next activity
    # Close connection
    cur.close()
    conn.close()
    print("Connexion fermée.")