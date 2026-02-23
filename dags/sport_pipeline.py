from datetime import datetime, timedelta
from airflow.providers.docker.operators.docker import DockerOperator
import os

# The DAG object; we'll need this to instantiate a DAG
from airflow.sdk import DAG
with DAG(
    dag_id="sport_pipeline",
    default_args={
        "depends_on_past": False,
        "is_paused_upon_creation": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A simple tutorial DAG",
    schedule="0 9 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:


    load_data = DockerOperator(
        task_id="load_strava_data",
        image="producer_history_strava",
        docker_url="unix://var/run/docker.sock",
        network_mode="projet_12_dbt_sport_sport_network",
        auto_remove="success",
        mount_tmp_dir=False,
    )

    run_dbt = DockerOperator(
        task_id="run_dbt",
        image="elt_dbt",
        docker_url="unix://var/run/docker.sock",
        network_mode="projet_12_dbt_sport_sport_network",
        auto_remove="success",
        trigger_rule="all_done",
        environment={
        "DBT_PROFILES_DIR": "/app/profiles",
        "POSTGRES_HOST": "postgres_sport",
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "POSTGRES_SCHEMA": "public",
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        },
        mount_tmp_dir=False,
    )

    notify_slack = DockerOperator(
        task_id="notify_slack",
        image="slack_sender",
        docker_url="unix://var/run/docker.sock",
        network_mode="projet_12_dbt_sport_sport_network",
        auto_remove="success",
        trigger_rule="all_done",
        environment={"SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL") },
        mount_tmp_dir=False,
    )

    load_data >> run_dbt >> notify_slack