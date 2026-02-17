import os
import time
import random
from datetime import datetime, timedelta
import psycopg2
import requests
from slack_sdk import WebClient
import os

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

    webhook_url = "https://hooks.slack.com/services/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"
    emoji_dict = {
        "Running": "🏃‍♂️",
        "Randonnée": "🚴‍♂️",
        "Natation": "🏊‍♂️",
        "Vélo": "🚴‍♂️",
        "Tennis": "🎾"
    }

    for row in rows:
        for i in range(10):
            try:
                print(f"row {i} :", row[i])
            except IndexError:
                print(f"row {i} : N/A")

        activity_emoji = emoji_dict.get(row[4], "🏅")

        if row[5] is not None:
            distance_activity = "Bravo pour avoir parcouru " + str(row[5] / 1000) + " kms !"
        else:
            distance_activity = ""

        payload = {
            "text": f"{activity_emoji} {row[1]} a fait du {row[4]} pendant {round(row[3])} minutes. {distance_activity}"
        }

        response = requests.post(webhook_url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Slack error: {response.text}")
    