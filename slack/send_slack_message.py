import os
from datetime import datetime, timedelta
import psycopg2
import requests
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

def read_sql_table_history(cur):
    cur.execute("SELECT * FROM public_gold.gold_slack_message_activities")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    return rows


if __name__ == "__main__":
    print("Démarrage du producteur d'activités sportives...")
    conn = connexion_sql()
    cur = conn.cursor()
    rows = read_sql_table_history(cur)
    cur.close()
    conn.close()
    print("Connexion fermée.")

    load_dotenv()
    webhook_url = os.getenv("webhook_url")
    emoji_dict = {
        "Runing": "🏃‍♂️",
        "Randonnée": "🏃‍♂️",
        "Natation": "🏊‍♂️",
        "Vélo": "🚴‍♂️",
        "Tennis": "🎾",
        "Escalade": "🧗‍♂️",
        "Badminton": "🏸",
        "Football": "⚽",
        "Basketball": "🏀",
        "Équitation": "🐎",
        "Boxe": "🥊",
        "Triathlon": "🏊‍♂️🚴‍♂️🏃‍♂️",
        "Tennis de table": "🏓", 
        "Rugby": "🏉",
        "Judo": "🥋",
    }

    fem_dict = {        
        "Randonnée": "de la",
        "Natation": "de la",
        "Escalade": "de l'",
        "Équitation": "de l'",
        "Boxe": "de la",
        }

    for row in rows:
        # if the table is up to date, and is the day before
        yesterday = (datetime.now() - timedelta(days=1)).date()
        if row[2] == yesterday:
            activity_emoji = emoji_dict.get(row[4], "🏅")

            if row[5] is not None:
                distance_activity = "Bravo pour avoir parcouru " + str(row[5] / 1000) + " kms !"
            else:
                distance_activity = ""

            masc_fem = "du"
            if row[4] in fem_dict:
                masc_fem = fem_dict[row[4]]

            payload = {
                "text": f"{activity_emoji} {row[1]} a fait {masc_fem} {row[4].lower()} pendant {round(row[3])} minutes. {distance_activity}"
            }

            response = requests.post(webhook_url, json=payload)

            if response.status_code != 200:
                raise Exception(f"Slack error: {response.text}")
    