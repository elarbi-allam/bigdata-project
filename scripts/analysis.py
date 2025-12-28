from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc, avg, max, min, count
from datetime import datetime

spark = SparkSession.builder \
    .appName("IoT Analysis") \
    .master("local[2]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("=" * 70)
print("📊 ANALYSE DES DONNÉES IoT")
print("=" * 70)

try:
    # Lire les données
    df = spark.read.parquet("/tmp/iot-data/raw/*.parquet")
    
    total = df.count()
    villes = df.select('city').distinct().count()
    capteurs = df.select('sensor_id').distinct().count()
    
    print(f"\n✅ {total:,} lectures analysées")
    print(f"📍 {villes} villes surveillées")
    print(f"🔧 {capteurs} capteurs actifs\n")
    
    # Statistiques globales
    print("=" * 70)
    print("🌡️  STATISTIQUES GLOBALES")
    print("=" * 70)
    
    stats = df.select(
        avg("temperature").alias("temp_moy"),
        max("temperature").alias("temp_max"),
        min("temperature").alias("temp_min"),
        avg("humidity").alias("hum_moy")
    ).collect()[0]
    
    print(f"Température moyenne : {stats['temp_moy']:.2f}°C")
    print(f"Température max     : {stats['temp_max']:.2f}°C")
    print(f"Température min     : {stats['temp_min']:.2f}°C")
    print(f"Humidité moyenne    : {stats['hum_moy']:.2f}%")
    
    # Par ville
    print("\n" + "=" * 70)
    print("📍 ANALYSE PAR VILLE")
    print("=" * 70)
    
    df.groupBy("city") \
        .agg(
            avg("temperature").alias("temp_moy"),
            max("temperature").alias("temp_max"),
            min("temperature").alias("temp_min"),
            count("*").alias("lectures")
        ) \
        .orderBy(desc("temp_moy")) \
        .show(truncate=False)
    
    # Alertes
    print("=" * 70)
    print("⚠️  ALERTES")
    print("=" * 70)
    
    hot = df.filter(col("temperature") > 40).count()
    cold = df.filter(col("temperature") < 20).count()
    
    print(f"🔥 Températures > 40°C : {hot}")
    print(f"❄️  Températures < 20°C : {cold}")
    
    if hot > 0:
        print("\n🔥 Top 5 températures élevées :")
        df.filter(col("temperature") > 40) \
            .select("city", "temperature", "timestamp") \
            .orderBy(desc("temperature")) \
            .show(5, truncate=False)
    
    # Générer rapport
    rapport = f"""# RAPPORT IoT - {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Résumé
- **Lectures** : {total:,}
- **Villes** : {villes}
- **Capteurs** : {capteurs}

## Statistiques
- Temp. moyenne : {stats['temp_moy']:.2f}°C
- Temp. max : {stats['temp_max']:.2f}°C
- Temp. min : {stats['temp_min']:.2f}°C
- Humidité moy. : {stats['hum_moy']:.2f}%

## Alertes
- 🔥 > 40°C : {hot}
- ❄️ < 20°C : {cold}

**Projet Big Data - ENSA 2024/2025**
"""
    
    with open("/tmp/rapport.md", "w") as f:
        f.write(rapport)
    
    print("\n" + "=" * 70)
    print("✅ Rapport sauvegardé : /tmp/rapport.md")
    print("📋 Copier : docker cp spark-master:/tmp/rapport.md ./")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Erreur : {e}")

spark.stop()