# 🏃‍♂️ Plateforme d'Analyse des Activités Sportives

## Description

Cette pipeline permet de charger, analyser et récompenser les activités sportives des salariés. 
Elle est orchestrée par Airflow, monitoré avec Prometheus/Grafana.

### Diagramme des Flux

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#fff','primaryTextColor':'#000','primaryBorderColor':'#000','lineColor':'#888','secondaryColor':'#fff','tertiaryColor':'#fff','clusterBkg':'#fff','clusterBorder':'#000','titleColor':'#000','edgeLabelBackground':'#fff'}}}%%
graph LR
    subgraph Sources["Sources de Données"]
        RH[Excel RH]
        Sport[Excel Sport]
        API[API Google Maps]
    end
    
    subgraph Airflow["Apache Airflow - Orchestration"]
        Sched[Scheduler<br/>Tous les jours à 9h]
        DAG[DAG sport_pipeline]
    end
    
    subgraph Pipeline["Pipeline ETL"]
        direction LR
        Extract[Producer Strava]
        Transform[dbt Transform]
        Notify[Slack Sender]
    end
    
    subgraph Storage["Stockage"]
        PG[(PostgreSQL 16)]
        Bronze[Couche Bronze<br/>Données brutes]
        Silver[Couche Silver<br/>Données nettoyées]
        Gold[Couche Gold<br/>Agrégats business]
    end
    
    subgraph Monitoring["Monitoring"]
        Prom[Prometheus]
        Graf[Grafana]
        Stats[StatsD]
    end
    
    subgraph Viz["Visualisation"]
        Superset[Apache Superset<br/>:8088]
    end
    
    subgraph Notif["Notifications"]
        Slack[Slack Webhook]
    end
    
    RH --> Extract
    Sport --> Extract
    API --> Extract
    
    Sched --> DAG
    DAG --> Extract
    Extract --> PG
    PG --> Bronze
    
    DAG --> Transform
    Bronze --> Transform
    Transform --> Silver
    Silver --> Gold
    
    DAG --> Notify
    Gold --> Notify
    Notify --> Slack
    
    Gold --> Superset
    
    Airflow -. " " .-> Stats
    Stats --> Prom
    Prom --> Graf
    PG -. " " .-> Prom
    
    style Airflow fill:#e1f5ff,stroke:#000,color:#000
    style Pipeline fill:#fff4e1,stroke:#000,color:#000
    style Storage fill:#e8f5e9,stroke:#000,color:#000
    style Monitoring fill:#f3e5f5,stroke:#000,color:#000
    style Viz fill:#ffe0e0,stroke:#000,color:#000
    style Notif fill:#fff,stroke:#000,color:#000
    style Sources fill:#fff,stroke:#000,color:#000
```

### Fonctionnalités Principales

- **Suivi des Activités** : Running, natation, cyclisme, randonnée, tennis etc..
- **Données RH** : Business units, salaires, trajets domicile-travail
- **Calcul des Primes** : Mobilité et activités sportives
- **Orchestration Airflow** : Pipeline automatisé - tous les jours à 9h
- **Monitoring** : Prometheus, Grafana
- **Notifications Slack** : Notifications quotidiennes 
- **Conformité RGPD** : Minimisation des données

---

## 🔄 Orchestration avec Apache Airflow

### DAG `sport_pipeline`

```python
# Flux : load_data → run_dbt → notify_slack
1. load_strava_data    # Extraction données (image: producer_history_strava)
2. run_dbt             # Transformations dbt (image: elt_dbt)
3. notify_slack        # Notifications (image: slack_sender)
```

### Airflow

```bash
# Interface web
http://localhost:8080
```


## Monitoring 

| Composant | Port | Fonction |
|-----------|------|----------|
| **Prometheus** | 9090 | Collecte et stockage métriques |
| **Grafana** | 3000 | Dashboards de visualisation |
| **StatsD** | 9125/8125 | Export métriques Airflow |

### Dashboards Grafana

Accéder à Grafana : `http://localhost:3000`

**Dashboards disponibles :**
- Airflow 
- Airflow DAG Performance
- PostgreSQL Metrics


## Architecture des Données

### Bronze → Silver → Gold

```
Bronze (Raw)              Silver (Clean)           Gold (Aggregate)
├─ sport_activities   →   silver_activities    →  gold_slack_messages_activities / gold_sport_activities_prime_last_year / gold_sport_activities_history_current_year
├─ sport_enterprise   →   silver_enterprise   
└─ rh_info            →   silver_rh_info       →  gold_rh_info / gold_incorrect_moyen_deplacement / gold_potential_moyen_deplac_bonus
```

### Tables Gold - Business Logic

| Table | Description | Refresh |
|-------|-------------|---------|
| `gold_incorrect_moyen_deplacement` | Remplissage incorrect moyen déplacement |  |
| `gold_potential_moyen_deplac_bonus` | Possiblement Éligibles prime déplacement |  |
| `gold_rh_info` | Éligibles prime déplacement |  |
| `gold_slack_message_activities` | Activités du jour | Delete_Insert |
| `gold_sport_activities_history_current_year` | Éligibles prime Sport | Incrémental |
| `gold_sport_activities_prime_last_year` | Prévisionnel prime Sport | Incrémental |

**Règles de Primes :**
- **Prime Sportive** : > 15 activités en 2025
- **Prime Mobilité** : Distance < 25km, transport ≠ marche/vélo, 5% salaire brut

---

## 🛠️ Installation & Configuration

### Prérequis

- Docker & Docker Compose
- Fichier `.env` 

```bash
# PostgreSQL
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# Superset
SUPERSET_SECRET_KEY=

# Slack
SLACK_WEBHOOK_URL=

# Google Maps 
GCP_key=

# Airflow
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=
_AIRFLOW_WWW_USER_PASSWORD=
```

### Démarrage Rapide

```bash
# Créer les images des 3 conteneurs de la pipeline
docker compose --profile build_only build

# Lancer la stack complète
docker compose up 

# Vérifier les services
docker compose ps

# Accès aux interfaces
open http://localhost:8080  # Airflow
open http://localhost:8088  # Superset
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus

# Arrêter le service
docker compose down

# Arrêter le service avec suppression des volumes
docker compose down -v
```
