from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, year, month, dayofmonth, hour
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import os, time

# Các biến môi trường
DATA_INGESTION__TAXI_TYPE           = os.environ.get("DATA_INGESTION__TAXI_TYPE", "yellow")
KAFKA__BOOTSTRAP_SERVERS            = os.environ.get("KAFKA__BOOTSTRAP_SERVERS", "kafka:9092")
SPARK_STREAMING__CHECKPOINT_PATH    = os.environ.get("SPARK_STREAMING__CHECKPOINT_PATH", f"hdfs://hadoop-namenode:9000/checkpoints")
SPARK_STREAMING__TRIGGER_TIME       = os.environ.get("SPARK_STREAMING__TRIGGER_TIME", "10 seconds")
HDFS__RAW_OUTPUT_PATH               = os.environ.get("HDFS__RAW_OUTPUT_PATH", f"hdfs://hadoop-namenode:9000/raw_data")

# Định nghĩa schema
schema = StructType(
    [
        StructField("VendorID", IntegerType(), True),
        StructField("tpep_pickup_datetime", TimestampType(), True),
        StructField("tpep_dropoff_datetime", TimestampType(), True),
        StructField("passenger_count", DoubleType(), True),
        StructField("trip_distance", DoubleType(), True),
        StructField("RatecodeID", DoubleType(), True),
        StructField("store_and_fwd_flag", StringType(), True),
        StructField("PULocationID", IntegerType(), True),
        StructField("DOLocationID", IntegerType(), True),
        StructField("payment_type", IntegerType(), True),
        StructField("fare_amount", DoubleType(), True),
        StructField("extra", DoubleType(), True),
        StructField("mta_tax", DoubleType(), True),
        StructField("tip_amount", DoubleType(), True),
        StructField("tolls_amount", DoubleType(), True),
        StructField("improvement_surcharge", DoubleType(), True),
        StructField("total_amount", DoubleType(), True),
        StructField("congestion_surcharge", DoubleType(), True),
        StructField("airport_fee", DoubleType(), True)
    ]
)

# Khởi tạo Spark Session
spark = SparkSession.builder \
        .appName("LoadData") \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5') \
        .getOrCreate()

# Đọc dữ liệu từ Kafka
df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA__BOOTSTRAP_SERVERS) \
        .option("subscribe", f"{DATA_INGESTION__TAXI_TYPE}_trip_data") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()

# Biến đổi dữ liệu về dạng json
df_parsed = df.selectExpr("CAST(value AS STRING) as json_str") \
              .select(from_json(col("json_str"), schema).alias("data")) \
              .select("data.*")

df_parsed = df_parsed \
        .withColumn("year", year(col("tpep_pickup_datetime"))) \
        .withColumn("month", month(col("tpep_pickup_datetime"))) \
        .withColumn("day", dayofmonth(col("tpep_pickup_datetime"))) \
        .withColumn("hour", hour(col("tpep_pickup_datetime")))

# Lưu dữ liệu lên HDFS
query = df_parsed.writeStream \
        .format("parquet") \
        .outputMode("append") \
        .trigger(processingTime=SPARK_STREAMING__TRIGGER_TIME) \
        .option("checkpointLocation", SPARK_STREAMING__CHECKPOINT_PATH) \
        .option("path", HDFS__RAW_OUTPUT_PATH) \
        .partitionBy(["year", "month"]) \
        .start()

# Dừng Session khi gửi xong
idle_counter = 0
max_idle_count = 5

while query.isActive:
    progress = query.lastProgress
    if progress:
        input_rows = progress.get("numInputRows", 1)  # fallback = 1 để tránh None
        if input_rows == 0:
            idle_counter += 1
            print(f"[INFO] No new data. Idle {idle_counter}/{max_idle_count}")
        else:
            idle_counter = 0
        if idle_counter >= max_idle_count:
            print("[INFO] Reached max idle count. Stopping streaming query...")
            query.stop()
            break
    else:
        print("[INFO] Waiting for first progress...")
    time.sleep(10)

spark.stop()