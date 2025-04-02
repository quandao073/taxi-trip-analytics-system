from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, round
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType

# Schema của Yellow Taxi
schema = StructType([
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
    StructField("Airport_fee", DoubleType(), True),
    StructField("event_time", TimestampType(), True)
])

# Tạo Spark session
spark = SparkSession.builder \
    .appName("TaxiTripStreamProcessor") \
    .getOrCreate()

# Đọc từ Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "yellow_trip_data") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON từ Kafka value
df_parsed = df_raw \
    .selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \

df_parsed.printSchema()

# Tách bản ghi hợp lệ và bản ghi lỗi
df_valid = df_parsed \
    .filter(col("tpep_pickup_datetime").isNotNull()) \
    .filter(col("tpep_dropoff_datetime").isNotNull()) \
    .filter(col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime")) \
    .filter(col("passenger_count").between(1, 6)) \
    .filter(col("trip_distance") >= 0) \
    .filter(col("fare_amount") >= 0) \
    .filter(col("total_amount") >= 0) \
    .filter(col("PULocationID").between(1, 265)) \
    .filter(col("DOLocationID").between(1, 265)) \
    .filter(col("store_and_fwd_flag").isin("Y", "N")) \
    .filter(col("payment_type").isin(0, 1, 2, 3, 4, 5, 6))


df_error = df_parsed \
    .filter(
        col("tpep_pickup_datetime").isNull() |
        col("tpep_dropoff_datetime").isNull() |
        (col("tpep_dropoff_datetime") < col("tpep_pickup_datetime")) |
        (col("passenger_count").isNull() | ~col("passenger_count").between(1, 6)) |
        (col("trip_distance") < 0) |
        (col("fare_amount") < 0) |
        (col("total_amount") < 0) |
        (col("PULocationID").isNull() | ~col("PULocationID").between(1, 265)) |
        (col("DOLocationID").isNull() | ~col("DOLocationID").between(1, 265)) |
        (col("store_and_fwd_flag").isNotNull() & ~col("store_and_fwd_flag").isin("Y", "N")) |
        (col("payment_type").isNull() | ~col("payment_type").isin(0, 1, 2, 3, 4, 5, 6))
    )

# Ghi các bản ghi ra console
query_valid_df = df_valid.writeStream \
        .format("console") \
        .outputMode("append") \
        .trigger(processingTime='10 seconds') \
        .queryName("ValidStream") \
        .start()

query_error_df = df_error.writeStream \
        .format("console") \
        .outputMode("append") \
        .trigger(processingTime='10 seconds') \
        .queryName("ErrorStream") \
        .start()

spark.streams.awaitAnyTermination()