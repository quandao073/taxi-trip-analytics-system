from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType

spark = SparkSession.builder \
    .appName("KafkaStream") \
    .config("spark.sql.encoding", "UTF-8") \
    .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .getOrCreate()

schema = StructType() \
    .add("timestamp", StringType()) \
    .add("station_id", IntegerType()) \
    .add("station_name", StringType()) \
    .add("city_name", StringType()) \
    .add("url", StringType()) \
    .add("latitude", DoubleType()) \
    .add("longitude", DoubleType()) \
    .add("aqi", IntegerType()) \
    .add("co", DoubleType()) \
    .add("temperature", DoubleType()) \
    .add("wind", DoubleType()) \
    .add("atmospheric_pressure", DoubleType()) \
    .add("humidity", DoubleType()) \
    .add("pm25", DoubleType()) \
    .add("pm10", DoubleType()) \
    .add("o3", DoubleType()) \
    .add("no2", DoubleType())

df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "air_quality") \
    .option("startingOffsets", "latest") \
    .load()

df_parsed = df_raw \
    .selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

query = df_parsed.writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("append") \
    .start()

query.awaitTermination()