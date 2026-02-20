# 🏃‍♂️ Plateforme d'Analyse des Activités Sportives

## 📋 Description

Ce projet est une **plateforme moderne de data engineering** conçue pour suivre, analyser et récompenser les activités sportives des salariés au sein d'une organisation. Construite avec un accent sur la **qualité des données**, la **confidentialité** et la **scalabilité**, elle implémente un pipeline complet ELT (Extract, Load, Transform) en utilisant des outils standards de l'industrie et les meilleures pratiques.

### Fonctionnalités Principales

- **📊 Suivi des Activités Sportives des Salariés** : Collecte et stockage automatisés des activités sportives incluant running, natation, cyclisme, randonnée et tennis
- **🏢 Intégration des Données RH** : Gestion complète des informations des salariés incluant les business units, salaires et détails de trajets domicile-travail
- **💰 Calcul des Primes de Mobilité** : Validation intelligente des moyens de transport et calcul automatique des primes
- **📈 Analytics en Temps Réel** : Tableaux de bord de business intelligence propulsés par Apache Superset
- **💬 Intégration Slack** : Notifications automatisées des activités sportives quotidiennes
- **🔄 Traitement Incrémental des Données** : Mises à jour quotidiennes efficaces utilisant la stratégie de matérialisation incrémentale de dbt

### Stack Technologique

- **Base de données** : PostgreSQL 16 avec Write-Ahead Logging (WAL) pour la durabilité des données
- **Transformation de données** : dbt (data build tool) avec architecture médaillon (couches Bronze/Silver/Gold)
- **Orchestration** : Docker Compose pour l'orchestration des conteneurs
- **BI/Visualisation** : Apache Superset pour les tableaux de bord et analytics
- **Qualité des données** : Tests dbt pour la validation des schémas et l'intégrité des données
- **Automatisation** : Exécution quotidienne du pipeline via cron
- **Communication** : Webhooks Slack pour les notifications d'activités

---

## 🚀 Performance & Scalabilité

### Optimisations de Performance

1. **Traitement Incrémental**
   - Les modèles incrémentaux dbt ne traitent que les données nouvelles/modifiées
   - Réduit le temps de traitement d'heures à minutes pour les grands volumes de données
   - Exemple : `silver_sport_activities_history` utilise `unique_key='id_activity'` pour des mises à jour efficaces

2. **Stratégie de Vues Matérialisées**
   - Couche Silver : Tables matérialisées pour données nettoyées et dédupliquées
   - Couche Gold : Tables agrégées prêtes pour le business
   - Minimise le temps d'exécution des requêtes pour les analytics utilisateurs

3. **Indexation de la Base de Données**
   - Clés primaires sur toutes les tables (`id_activity`, `id_salarie`, `id_duo`)
   - Optimisé pour les opérations JOIN entre activités, données RH et enregistrements sportifs

4. **Pooling de Connexions**
   - PostgreSQL configuré avec health checks et logique de retry
   - Volumes persistants (`postgres_data`) préviennent la perte de données et réduisent le temps de démarrage

### Caractéristiques de Scalabilité

#### Scalabilité Horizontale
- **Architecture Conteneurisée** : Chaque service (PostgreSQL, dbt, Superset, Slack) s'exécute dans des conteneurs isolés
- **Pattern Microservices** : Mise à l'échelle indépendante des producteurs, transformateurs et consommateurs de données
- **Isolation Réseau** : Bridge personnalisé `sport_network` pour une communication inter-services efficace

#### Scalabilité Verticale
- **Configuration PostgreSQL WAL** : `wal_level=logical` active le Change Data Capture (CDC) pour de futures architectures événementielles
- **Configuration des Threads dbt** : Traitement parallèle ajustable (actuellement 1 thread, peut monter à N threads)
- **Gestion des Volumes** : Les volumes persistants séparent le calcul du stockage

#### Gestion du Volume de Données
- **Capacité Actuelle** : Gère 100+ activités pour 2025 + 25+ pour 2026 (125 enregistrements)
- **Capacité Projetée** : L'architecture supporte des millions d'enregistrements grâce à :
  - Capacité de partitionnement (natif PostgreSQL)
  - Traitement incrémental (uniquement nouvelles données)
  - Agrégation efficace dans la couche gold

#### Extensibilité
- **Nouvelles Sources de Données** : Intégration facile via de nouvelles définitions de sources dbt
- **Métriques Additionnelles** : La couche gold modulaire permet d'ajouter de nouveaux KPIs sans perturber les pipelines existants
- **Prêt Multi-tenant** : La séparation par business unit (`bu_salarie`) permet des analytics par département

---

## 🔒 Sécurité & Gestion des Mots de Passe

### Protection des Mots de Passe

1. **Variables d'Environnement**
   - Tous les identifiants stockés dans un fichier `.env` (exclu du contrôle de version via `.gitignore`)
   - Docker Compose utilise les variables `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}`, `${POSTGRES_DB}`
   - Les profils dbt utilisent la fonction Jinja `env_var()` pour l'injection des identifiants au runtime

2. **Aucun Secret en Dur**
   - Identifiants de base de données : Variables d'environnement uniquement
   - Webhook Slack : Stocké comme variable d'environnement `${SLACK_WEBHOOK_URL}`
   - Clé secrète Superset : `${SUPERSET_SECRET_KEY}` pour le chiffrement des sessions
   - Clé API Google Maps : `os.getenv("GCP_key")` dans les scripts Python

3. **Isolation des Conteneurs**
   - Les services communiquent via le réseau Docker interne (`sport_network`)
   - PostgreSQL non exposé à l'hôte (port interne 5432, externe 5433 pour accès admin uniquement)
   - Mot de passe admin Superset défini programmatiquement, non stocké dans le code

4. **Contrôle d'Accès**
   - Identifiants utilisateur de base de données configurés par environnement
   - Contrôle d'accès basé sur les rôles Superset (RBAC)
   - Les scripts Python utilisent la bibliothèque `dotenv` pour le chargement sécurisé des identifiants

### Bonnes Pratiques de Sécurité

- **Segmentation Réseau** : Le réseau bridge personnalisé empêche l'accès externe non autorisé
- **Health Checks** : S'assure que les services sont prêts avant le démarrage des services dépendants
- **Sécurité des Images** : Utilise des images officielles (`debezium/postgres:16`, `apache/superset:latest-dev`)
- **Permissions des Volumes** : Les volumes de données PostgreSQL appartiennent à l'utilisateur du conteneur

---

## 🇫🇷 Conformité RGPD

### Protection des Données Personnelles

1. **Minimisation des Données**
   - **Les adresses domicile sont anonymisées** : La fonction `clean_adresses()` supprime les adresses complètes après calcul de distance
   - Seule la distance au bureau (`distance_to_office_km`) est conservée, pas la localisation précise
   - Les salaires sont stockés comme agrégats pour les calculs de primes, non exposés dans les tableaux de bord

2. **Pseudonymisation des Noms**
   - Les noms des salariés utilisent un algorithme de divulgation progressive dans `silver_rh_info.sql` :
     - Prénom uniquement si unique
     - Prénom + 1 lettre du nom si nécessaire
     - Ajout progressif de caractères du nom jusqu'à unicité
   - Réduit l'identifiabilité tout en maintenant l'utilité des données

3. **Limitation de la Finalité**
   - **Activités sportives** : Utilisées uniquement pour le suivi du programme bien-être et les primes
   - **Données RH** : Limitées au salaire, BU, type de contrat et informations de trajet
   - **Données de mobilité** : Uniquement pour la validation de la prime de transport

4. **Conservation des Données**
   - Activités historiques stockées indéfiniment pour l'analyse des tendances (envisager d'implémenter une politique de rétention)
   - Les modèles incrémentaux maintiennent uniquement les fenêtres temporelles pertinentes (ex: 12 derniers mois pour les analytics BU)

5. **Droit d'Accès & Portabilité**
   - Tables PostgreSQL facilement interrogeables par `id_salarie`
   - Les tableaux de bord Superset fournissent un accès en self-service aux données d'activité personnelles
   - Données exportables via requêtes SQL ou fonctionnalité d'export Superset

6. **Qualité & Exactitude des Données**
   - Les tests dbt assurent l'intégrité des données (`not_null`, `unique`, `accepted_values`)
   - Validation des moyens de transport (`gold_incorrect_moyen_deplacement`) pour l'exactitude
   - Les salariés peuvent vérifier et corriger leurs informations via les systèmes RH

7. **Sécurité du Traitement**
   - Connexions chiffrées (possibilité d'activer SSL/TLS pour PostgreSQL)
   - Logs d'accès via les capacités d'audit PostgreSQL
   - L'environnement conteneurisé réduit la surface d'attaque

### Fonctionnalités Conformes RGPD

✅ **Consentement** : Les salariés adhèrent volontairement au programme de suivi sportif  
✅ **Transparence** : Utilisation claire des données pour le bien-être et les primes de mobilité  
✅ **Droits des Personnes Concernées** : Capacités de consultation et d'export  
✅ **Privacy by Design** : Pseudonymisation et minimisation des données intégrées  
✅ **Responsabilité** : Traçabilité de la lignée dbt (`manifest.json`) pour la provenance des données  

### Améliorations Recommandées pour une Conformité RGPD Complète

- [ ] Implémenter une politique de rétention des données (ex: supprimer les activités de plus de 7 ans)
- [ ] Ajouter la journalisation d'audit pour tous les accès aux données
- [ ] Créer un système de gestion du consentement des salariés
- [ ] Documenter les accords de traitement des données (DPA) avec les tiers (API Google Maps, Slack)
- [ ] Implémenter un workflow automatisé de suppression pour le "droit à l'oubli"
- [ ] Activer le chiffrement SSL/TLS PostgreSQL pour les données en transit
- [ ] Ajouter le masquage des données pour les visualiseurs Superset sans permissions RH

---

## 🏗️ Aperçu de l'Architecture

### Architecture Médaillon (Bronze → Silver → Gold)

```
┌─────────────────┐
│  Couche Bronze  │  Sources de données brutes
│  (PostgreSQL)   │  - sport_activities_history
└────────┬────────┘  - sport_enterprise
         │           - rh_info
         ↓
┌─────────────────┐
│  Couche Silver  │  Données nettoyées & dédupliquées
│ (modèles dbt)   │  - silver_sport_activities_history
└────────┬────────┘  - silver_rh_info
         │           - silver_sport_enterprise
         ↓
┌─────────────────┐
│  Couche Gold    │  Agrégats prêts pour le business
│ (modèles dbt)   │  - gold_sport_activities_per_bu
└─────────────────┘  - gold_sport_activities_prime_last_year
                     - gold_slack_message_activities
                     - gold_potential_moyen_deplac_bonus
                     - gold_incorrect_moyen_deplacement
```

### Flux d'Exécution du Pipeline

1. **Extraction de Données** (`producer_history_strava`)
   - Charge les données RH depuis Excel (`Donnees_RH.xlsx`)
   - Charge les préférences sportives depuis Excel (`Donnees_Sportive.xlsx`)
   - Génère les activités historiques (100 pour 2025, 25 pour 2026)
   - Calcule les distances au bureau via l'API Google Maps (simulé)
   - Anonymise les adresses domicile

2. **Transformation de Données** (`elt_dbt`)
   - Exécute les modèles dbt dans l'ordre de dépendance
   - Applique la logique incrémentale pour des mises à jour efficaces
   - Exécute les tests de qualité des données
   - Crée les tables silver et gold

3. **Notification** (`slack_sender`)
   - Lit la table `gold_slack_message_activities`
   - Envoie des messages formatés vers le webhook Slack
   - Inclut emojis, durée et distance

4. **Visualisation** (`superset`)
   - Se connecte à la couche gold PostgreSQL
   - Importe les tableaux de bord pré-configurés depuis `export.zip`
   - Sert les analytics sur le port 8088

### Automatisation Quotidienne

```bash
# cron/daily_pipeline.sh
docker compose up --force-recreate --no-deps \
  producer_history_strava dbt strava_sender
```

Planifié via cron job pour exécuter les mises à jour incrémentales quotidiennes.

---

## 🛠️ Installation & Configuration

### Prérequis

- Docker & Docker Compose
- Fichier `.env` avec les identifiants requis :

```bash
# Base de données
POSTGRES_USER=postgresuser
POSTGRES_PASSWORD=postgrespw
POSTGRES_DB=sport_activities_db

# Superset
SUPERSET_SECRET_KEY=votre_cle_secrete_ici

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/VOTRE/WEBHOOK/URL

# API Google Maps (optionnel)
GCP_key=votre_cle_api_google_maps
```

### Démarrage Rapide

```bash
# Rendre le script pipeline exécutable
chmod +x cron/daily_pipeline.sh

# Lancer la stack complète
docker compose up -d

# Accéder à Superset
open http://localhost:8088
# Login: admin / admin

# Voir les logs
docker compose logs -f dbt
```

### Exécution Manuelle de dbt

```bash
# Exécuter les transformations
docker exec -it elt_dbt dbt run

# Exécuter les tests
docker exec -it elt_dbt dbt test

# Générer la documentation
docker exec -it elt_dbt dbt docs generate
docker exec -it elt_dbt dbt docs serve
```

---

## 📊 Modèles de Données

### Tables de la Couche Gold

| Table | Description | Matérialisation | Clé Incrémentale |
|-------|-------------|-----------------|------------------|
| `gold_sport_activities_per_bu` | Activités par BU (12 derniers mois) | Incrémentale | `bu_salarie` |
| `gold_sport_activities_prime_last_year` | Salariés éligibles à la prime 2025 (>3 activités) | Incrémentale | `id_salarie` |
| `gold_slack_message_activities` | Activités du jour pour notification Slack | Incrémentale | `[id_salarie, activity_date]` |
| `gold_potential_moyen_deplac_bonus` | Salariés éligibles à la prime de mobilité | Table | - |
| `gold_incorrect_moyen_deplacement` | Déclarations de transport invalides | Table | - |
| `gold_rh_info` | Données RH maîtres avec noms pseudonymisés | Table | - |

### Logique Business Clé

- **Éligibilité Prime de Mobilité** : 
  - Le moyen de transport ne doit pas être marche/vélo (déjà subventionnés)
  - Distance au bureau < 25km
  - Prime = 5% du salaire brut
  
- **Éligibilité Prime Sportive** :
  - >3 activités en 2025
  - Plusieurs types de sports pratiqués

- **Pseudonymisation des Noms** :
  - L'algorithme de divulgation progressive assure l'unicité avec un minimum de données personnelles

---

## 📈 Monitoring & Logs

- **Logs dbt** : `dbt/logs/dbt.log`
- **Logs pipeline** : `cron/logs/pipeline.log`
- **Logs conteneurs** : `docker compose logs <nom_service>`
- **Artefacts dbt** : `dbt/target/` (manifest, résultats d'exécution, SQL compilé)

---

## 🔮 Prochaines Étapes & Feuille de Route

### Améliorations Court Terme (3-6 mois)

1. **Architecture de Streaming Temps Réel**
   - Implémenter Apache Kafka pour l'ingestion événementielle des activités
   - Utiliser le connecteur CDC Debezium (déjà compatible avec l'image `debezium/postgres`)
   - Activer les notifications Slack en temps réel au lieu du batch quotidien

2. **Analytics Avancées**
   - Modèle ML pour la détection de fraude aux activités (ex: distances/temps impossibles)
   - Analytics prédictives pour les tendances de bien-être des salariés
   - Analyse de cohorte par BU, type de contrat et moyen de transport

3. **Améliorations Qualité des Données**
   - Implémenter dbt-expectations pour des tests statistiques avancés
   - Ajouter le profilage de données avec Great Expectations
   - Créer un système d'alertes pour les tests dbt échoués (intégration Slack/email)

4. **Interface Utilisateur**
   - Construire un portail self-service pour les salariés (Flask/Streamlit)
   - Application mobile pour la journalisation des activités (API REST avec FastAPI)
   - Classements en temps réel et gamification

### Objectifs Moyen Terme (6-12 mois)

5. **Intégration Multi-sources**
   - Intégration directe API Strava (remplacer les données simulées)
   - Connecteurs Garmin, Fitbit, Apple Health
   - Authentification OAuth2 pour les appareils des salariés

6. **Conformité RGPD Renforcée**
   - Politiques de rétention des données automatisées (partitionnement + suppression planifiée)
   - Tableau de bord de gestion du consentement
   - Pipeline d'anonymisation des données pour les datasets d'analytics
   - Piste d'audit complète avec logs immuables

7. **Infrastructure as Code**
   - Terraform pour le déploiement cloud (AWS RDS, ECS, S3)
   - Migration Kubernetes pour la scalabilité en production
   - Pipeline CI/CD (GitHub Actions) pour les tests de modèles dbt

8. **Optimisation des Performances**
   - Optimisation des requêtes PostgreSQL (EXPLAIN ANALYZE)
   - Exécution parallèle dbt (augmenter les threads)
   - Stratégie de rafraîchissement des vues matérialisées
   - Couche de cache (Redis) pour les requêtes Superset

### Vision Long Terme (12+ mois)

9. **Fonctionnalités Entreprise**
   - Architecture multi-tenant pour plusieurs entreprises
   - Tableaux de bord Superset en marque blanche
   - Monitoring SLA personnalisé et alertes
   - Reprise après sinistre et configuration haute disponibilité

10. **Capacités IA/ML**
    - Recommandations d'activités personnalisées
    - Prédiction du désengagement du programme bien-être
    - Détection d'anomalies pour les patterns d'activités suspects
    - Interface de requête en langage naturel (analytics propulsées par LLM)

11. **Conformité & Gouvernance**
    - Certification de sécurité ISO 27001
    - Conformité SOC 2 pour l'offre SaaS
    - Visualisation de la lignée des données (DAG dbt + Apache Atlas)
    - Reporting de conformité automatisé

12. **Expansion de l'Écosystème**
    - API publique pour intégrations tierces
    - Webhooks pour notifications personnalisées
    - Architecture de plugins pour types de sports personnalisés
    - Marketplace pour templates d'analytics

---

## 🤝 Contribuer

1. Forker le dépôt
2. Créer une branche de fonctionnalité (`git checkout -b feature/fonctionnalite-incroyable`)
3. Commiter les changements (`git commit -m 'Ajout fonctionnalité incroyable'`)
4. Pousser vers la branche (`git push origin feature/fonctionnalite-incroyable`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est développé dans le cadre du cursus Data Engineering d'OpenClassrooms.

---

## 👥 Support & Contact

Pour toute question ou problème :
- Créer une issue sur GitHub
- Contact : thomas.leroy@example.com

---

**⚠️ Note Importante de Configuration :**
```bash
chmod +x cron/daily_pipeline.sh
```
Cette commande doit être exécutée avant de lancer le pipeline pour assurer les permissions appropriées.

---

*Dernière mise à jour : Février 2026*
