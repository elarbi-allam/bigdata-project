# 🌡️ Projet Big Data - Monitoring IoT de Température en Temps Réel

> **Étudiant :** ELARBI ALLAM  
> **Établissement :** ENSA  
> **Année Universitaire :** 2025-2026  
> **Encadrant :** Professeur Hassan BADIR

---

## 📋 Table des Matières

- [Vue d'Ensemble](#vue-densemble)
- [Architecture Technique](#architecture-technique)
- [Technologies Utilisées](#technologies-utilisées)
- [Installation et Configuration](#installation-et-configuration)
- [Exécution du Projet](#exécution-du-projet)
- [Résultats](#résultats)
- [Structure du Projet](#structure-du-projet)

---

## 🎯 Vue d'Ensemble

Ce projet implémente un **pipeline Big Data complet** pour le monitoring en temps réel de capteurs IoT de température, utilisant les technologies Apache Kafka, Spark Streaming et HDFS dans un environnement containerisé Docker.

### Objectifs

✅ Ingestion de données IoT en temps réel avec **Apache Kafka**  
✅ Traitement streaming avec **Apache Spark Streaming**  
✅ Stockage distribué avec **HDFS** (format Parquet)  
✅ Agrégations par fenêtres temporelles  
✅ Analyse statistique et génération de rapports  

### Cas d'Usage

**Monitoring de température** dans 6 villes marocaines (Casablanca, Rabat, Marrakech, Fès, Tanger, Agadir) via 20 capteurs IoT simulés générant des mesures de température et d'humidité toutes les secondes.

---

## 🏗️ Architecture Technique
```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE BIG DATA IoT                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📡 Producteur Python (20 capteurs IoT)                     │
│      ↓                                                      │
│  🔄 Apache Kafka (Topic: iot-temperature)                   │
│      ↓                                                      │
│  ⚡ Apache Spark Streaming (Mode Local)                     │
│      ├─ Console (Affichage temps réel)                     │
│      └─ HDFS (Stockage Parquet)                            │
│      ↓                                                      │
│  💾 HDFS (/tmp/iot-data/raw/*.parquet)                      │
│      ↓                                                      │
│  📊 Analyse Spark SQL (Statistiques & Alertes)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Composants du Cluster Docker

| Conteneur | Rôle | Ports |
|-----------|------|-------|
| **zookeeper** | Coordination Kafka | 2181 |
| **kafka** | Message Broker | 9092 |
| **spark-master** | Nœud Maître Spark | 8080, 7077, 4040 |
| **spark-worker** | Nœud Worker Spark | - |
| **namenode** | HDFS NameNode | 9870, 9000 |
| **datanode** | HDFS DataNode | - |

---

## 🛠️ Technologies Utilisées

### Big Data Stack

- **Apache Kafka 7.5.0** - Ingestion streaming
- **Apache Spark 3.5.0** - Traitement distribué
- **Apache Hadoop 3.2.1** - Stockage HDFS
- **Apache Zookeeper 7.5.0** - Coordination

### Développement

- **Python 3.x** - Scripts producteur/analyse
- **Docker & Docker Compose** - Containerisation
- **kafka-python** - Client Kafka Python

### Formats de Données

- **JSON** - Format des messages Kafka
- **Parquet + Snappy** - Stockage compressé HDFS

---

## 📦 Installation et Configuration

### Prérequis

- Docker Desktop installé et démarré
- Python 3.x avec pip
- 8 GB RAM minimum
- 20 GB espace disque

### Étape 1 : Cloner le Projet
```bash
git clone https://github.com/elarbi-allam/bigdata-project.git
cd bigdata-project
```

### Étape 2 : Démarrer l'Infrastructure Docker
```powershell
# Démarrer tous les conteneurs
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

**Résultat attendu :** Tous les conteneurs doivent être **Up**

### Étape 3 : Installer les Dépendances
```powershell
# Installer kafka-python dans Spark
docker exec -it -u root spark-master pip install kafka-python

# Fixer les permissions Ivy (pour Spark)
docker exec -it -u root spark-master bash -c "mkdir -p /home/spark/.ivy2/cache /home/spark/.ivy2/jars && chown -R spark:spark /home/spark/.ivy2 && chmod -R 777 /home/spark/.ivy2"
```

### Étape 4 : Créer le Topic Kafka
```powershell
docker exec -it kafka kafka-topics --create --topic iot-temperature --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

---

## 🚀 Exécution du Projet

### Terminal 1 : Lancer le Producteur IoT
```powershell
docker exec -it spark-master python3 /opt/spark-apps/producer.py
```

**Sortie attendue :**
```
============================================================
🌡️  PRODUCTEUR IoT - DÉMARRAGE
============================================================
📍 Villes : Casablanca, Rabat, Marrakech, Fes, Tanger, Agadir
🔧 Capteurs : 20
📡 Topic Kafka : iot-temperature
============================================================
✅ 10 messages envoyés - Dernier: Marrakech 26.79°C
✅ 20 messages envoyés - Dernier: Agadir 32.15°C
```

### Terminal 2 : Lancer Spark Streaming
```powershell
docker exec -it spark-master /opt/spark/bin/spark-submit --master local[2] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /opt/spark-apps/consumer_spark.py
```

**Sortie attendue :**
```
======================================================================
🚀 SPARK STREAMING - MONITORING IoT
======================================================================
✅ Pipeline actif !
📊 Console : Données brutes (10s)
📈 Console : Agrégations (30s)
💾 HDFS : /tmp/iot-data/raw
```

### Laisser Tourner 2-3 Minutes

Les deux terminaux doivent rester actifs pour collecter des données.

### Arrêter les Processus

Appuyez sur **Ctrl+C** dans chaque terminal (producteur et consumer).

### Terminal 3 : Lancer l'Analyse
```powershell
docker exec -it spark-master /opt/spark/bin/spark-submit --master local[2] /opt/spark-apps/analysis.py
```

### Récupérer le Rapport
```powershell
docker cp spark-master:/tmp/rapport.md ./rapport_final.md
```

---

## 📊 Résultats

### Métriques de Performance

| Métrique | Valeur |
|----------|--------|
| **Messages traités** | 200+ |
| **Villes surveillées** | 6 |
| **Capteurs actifs** | 20 |
| **Latence moyenne** | < 10 secondes |
| **Fichiers Parquet générés** | 30+ |
| **Format de compression** | Snappy |

### Exemple de Données Collectées
```
+----------+----------+-----------+--------+--------------------------+
|sensor_id |city      |temperature|humidity|timestamp                 |
+----------+----------+-----------+--------+--------------------------+
|SENSOR_003|Casablanca|32.45      |67.8    |2025-12-28 20:15:12       |
|SENSOR_012|Marrakech |26.79      |45.2    |2025-12-28 20:15:13       |
|SENSOR_007|Rabat     |29.34      |58.6    |2025-12-28 20:15:14       |
+----------+----------+-----------+--------+--------------------------+
```

### Agrégations par Ville
```
+----------+------------------+--------+--------+------------+
|city      |avg_temp          |max_temp|min_temp|num_readings|
+----------+------------------+--------+--------+------------+
|Marrakech |33.45             |44.2    |18.5    |45          |
|Casablanca|31.23             |42.8    |16.3    |52          |
|Agadir    |29.87             |39.5    |19.2    |38          |
+----------+------------------+--------+--------+------------+
```

### Alertes Détectées

- 🔥 **Températures > 40°C :** 23 occurrences
- ❄️ **Températures < 20°C :** 18 occurrences

---

## 📁 Structure du Projet
```
bigdata-project/
├── docker-compose.yml          # Configuration Docker
├── README.md                   # Ce fichier
├── rapport_bigdata_iot.tex     # Rapport LaTeX
├── data/                       # (vide - données temporaires)
└── scripts/
    ├── producer.py             # Producteur Kafka
    ├── consumer_spark.py       # Consumer Spark Streaming
    └── analysis.py             # Analyse finale
```

### Description des Scripts

#### 1. `producer.py`

Simule 20 capteurs IoT envoyant des données de température et d'humidité à Kafka.

**Fonctionnalités :**
- Génération aléatoire de température (15-45°C)
- Génération aléatoire d'humidité (20-90%)
- Envoi à Kafka toutes les 1 seconde
- 6 villes différentes

#### 2. `consumer_spark.py`

Consumer Spark Streaming qui traite les données en temps réel.

**Fonctionnalités :**
- Lecture depuis Kafka
- Agrégations par fenêtres de 30 secondes
- Affichage console (données brutes + agrégations)
- Sauvegarde HDFS en format Parquet

#### 3. `analysis.py`

Script d'analyse batch des données stockées.

**Fonctionnalités :**
- Lecture des fichiers Parquet
- Calcul de statistiques par ville
- Détection d'alertes (températures extrêmes)
- Génération de rapport Markdown

---

## 🌐 Interfaces Web

- **Spark Master UI :** http://localhost:8080
- **Spark Application UI :** http://localhost:4040
- **HDFS NameNode UI :** http://localhost:9870

---

## 🔧 Dépannage

### Problème : Conteneurs ne démarrent pas
```powershell
docker-compose down
docker system prune -f
docker-compose up -d
```

### Problème : Permissions Ivy Cache
```powershell
docker exec -it -u root spark-master bash -c "mkdir -p /home/spark/.ivy2/cache && chown -R spark:spark /home/spark/.ivy2 && chmod -R 777 /home/spark/.ivy2"
```

### Problème : Topic Kafka existe déjà
```powershell
docker exec -it kafka kafka-topics --delete --topic iot-temperature --bootstrap-server localhost:9092
```

---

## 📚 Références

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Streaming Guide](https://spark.apache.org/docs/latest/streaming-programming-guide.html)
- [Hadoop HDFS Architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)

---

## 👨‍💻 Auteur

**ELARBI ALLAM**  
Étudiant en Big Data  
ENSA - 2025/2026

---

## 📄 Licence

Ce projet est réalisé dans le cadre d'un travail pratique universitaire.

---

**Dernière mise à jour :** Décembre 2025