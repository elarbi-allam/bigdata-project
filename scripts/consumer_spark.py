from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, max, min, count
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# Session Spark en mode local
spark = SparkSession.builder \
    .appName("IoT Temperature Streaming") \
    .master("local[2]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("=" * 70)
print("🚀 SPARK STREAMING - MONITORING IoT")
print("=" * 70)

# Schéma des données
schema = StructType([
    StructField("sensor_id", StringType(), True),
    StructField("city", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

# Lire depuis Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "iot-temperature") \
    .option("startingOffsets", "latest") \
    .load()

# Parser JSON
parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")
parsed_df = parsed_df.withColumn("timestamp", col("timestamp").cast(TimestampType()))
parsed_df_with_watermark = parsed_df.withWatermark("timestamp", "1 minute")

# Agrégations
aggregated_df = parsed_df_with_watermark \
    .groupBy(window(col("timestamp"), "30 seconds"), "city") \
    .agg(
        avg("temperature").alias("avg_temp"),
        max("temperature").alias("max_temp"),
        min("temperature").alias("min_temp"),
        avg("humidity").alias("avg_humidity"),
        count("sensor_id").alias("num_readings")
    )

# Affichage console - Données brutes
query_console = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime='10 seconds') \
    .start()

# Affichage console - Agrégations
query_aggregated = aggregated_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime='30 seconds') \
    .start()

# Sauvegarde HDFS
query_hdfs = parsed_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "/tmp/iot-data/raw") \
    .option("checkpointLocation", "/tmp/iot-data/checkpoints") \
    .trigger(processingTime='30 seconds') \
    .start()

print("✅ Pipeline actif !")
print("📊 Console : Données brutes (10s)")
print("📈 Console : Agrégations (30s)")
print("💾 HDFS : /tmp/iot-data/raw")
print("🛑 Ctrl+C pour arrêter")
print("=" * 70)

query_console.awaitTermination()