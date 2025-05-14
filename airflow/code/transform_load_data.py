from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType, LongType
import os, time, json
from redis import Redis
from redis.sentinel import Sentinel
from redis.connection import ConnectionPool

# Các biến môi trường
DATA_INGESTION__TAXI_TYPE           = os.environ.get("DATA_INGESTION__TAXI_TYPE", "yellow")
KAFKA__BOOTSTRAP_SERVERS            = os.environ.get("KAFKA__BOOTSTRAP_SERVERS", "kafka:9092")
SPARK_STREAMING__TRIGGER_TIME       = os.environ.get("SPARK_STREAMING__TRIGGER_TIME", "10 seconds")
HDFS__URI                           = os.environ.get("HDFS__URI", "hdfs://hadoop-hadoop-hdfs-nn:9000")
REDIS__SENTINEL_HOST                = os.environ.get("REDIS__SENTINEL_HOST", "redis-sentinel.bigdata.svc.cluster.local")
REDIS__SENTINEL_PORT                = int(os.environ.get("REDIS__SENTINEL_PORT", "26379"))
REDIS__MASTER_NAME                  = os.environ.get("REDIS__MASTER_NAME", "mymaster")
REDIS__PASSWORD                     = os.environ.get("REDIS__PASSWORD", "quanda")

REDIS__HOST='redis'
REDIS__PORT=6379
REDIS_POOL = ConnectionPool(
    host=REDIS__HOST,
    port=int(REDIS__PORT),
    # password=REDIS__PASSWORD,
    max_connections=10,
    decode_responses=True
)

sentinel = Sentinel(
    [(REDIS__SENTINEL_HOST, REDIS__SENTINEL_PORT)],
    sentinel_kwargs={"password": REDIS__PASSWORD},
    socket_timeout=1
)

def get_redis_connection():
    return sentinel.master_for(
        REDIS__MASTER_NAME,
        password=REDIS__PASSWORD,
        decode_responses=True
    )

# Định nghĩa schema
schema = StructType(
    [
        StructField("VendorID", IntegerType(), True),
        StructField("tpep_pickup_datetime", TimestampType(), True),
        StructField("tpep_dropoff_datetime", TimestampType(), True),
        StructField("passenger_count", LongType(), True),
        StructField("trip_distance", DoubleType(), True),
        StructField("RatecodeID", DoubleType(), True),
        StructField("store_and_fwd_flag", StringType(), True),
        StructField("PULocationID", IntegerType(), True),
        StructField("DOLocationID", IntegerType(), True),
        StructField("payment_type", LongType(), True),
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

lookup_df = spark.read.option("header", True).csv("/opt/airflow/code/taxi_zone_lookup.csv")

pickup_lookup = lookup_df.withColumnRenamed("LocationID", "PULocationID") \
                         .withColumnRenamed("Borough", "pickup_borough") \
                         .withColumnRenamed("Zone", "pickup_zone") \
                         .drop("service_zone")

dropoff_lookup = lookup_df.withColumnRenamed("LocationID", "DOLocationID") \
                          .withColumnRenamed("Borough", "dropoff_borough") \
                          .withColumnRenamed("Zone", "dropoff_zone") \
                          .drop("service_zone")

# Đọc dữ liệu từ Kafka
df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA__BOOTSTRAP_SERVERS) \
        .option("subscribe", f"{DATA_INGESTION__TAXI_TYPE}_trip_data") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()

# Biến đổi dữ liệu
df_parsed = df.selectExpr("CAST(value AS STRING) as json_str") \
              .select(from_json(col("json_str"), schema).alias("data")) \
              .select("data.*")

df_parsed = df_parsed \
        .withColumn("year", year(col("tpep_pickup_datetime"))) \
        .withColumn("month", month(col("tpep_pickup_datetime"))) \
        .withColumn("day", dayofmonth(col("tpep_pickup_datetime"))) \
        .withColumn("hour", hour(col("tpep_pickup_datetime")))

df_parsed = df_parsed.fillna({
    "passenger_count": 1,
    "airport_fee": 0.0,
    "congestion_surcharge": 0.0,
    "store_and_fwd_flag": "N",
    "RatecodeID": 99,
})

valid_conditions = (
        col("tpep_pickup_datetime").isNotNull() &
        col("tpep_dropoff_datetime").isNotNull() &
        (col("tpep_dropoff_datetime") > col("tpep_pickup_datetime")) &
        col("passenger_count").isNotNull() &
        col("RatecodeID").isNotNull() &
        (col("trip_distance") > 0) &
        (col("fare_amount") >= 0) &
        (col("total_amount") >= 0) &
        col("PULocationID").between(1, 263) &
        col("DOLocationID").between(1, 263) &
        col("store_and_fwd_flag").isin("Y", "N") &
        col("payment_type").isin(0, 1, 2, 3, 4, 5, 6)
    )

df_valid = df_parsed.filter(valid_conditions)
df_error = df_parsed.filter(~valid_conditions)

df_valid = df_valid \
        .join(broadcast(pickup_lookup), on="PULocationID", how="left") \
        .join(broadcast(dropoff_lookup), on="DOLocationID", how="left")


def write_to_redis(batch_df, batch_id):
    redis_conn = Redis(connection_pool=REDIS_POOL)
    # redis_conn = get_redis_connection()

    try:
        stats = batch_df.groupBy("pickup_zone").agg(
            count("*").alias("trip_count"),
            sum("total_amount").alias("total_revenue")
        ).collect()

        with redis_conn.pipeline() as pipe:
            for row in stats:
                zone = row["pickup_zone"]
                trips = int(row["trip_count"])
                revenue = float(row["total_revenue"])

                pipe.hincrby("pickup:trip_count", zone, trips)
                pipe.hincrbyfloat("pickup:total_revenue", zone, revenue)

            pipe.execute()

        trip_counts = redis_conn.hgetall("pickup:trip_count")
        total_revenues = redis_conn.hgetall("pickup:total_revenue")

        with redis_conn.pipeline() as pipe:
            for zone in trip_counts:
                pipe.publish("pickup-stats-channel", json.dumps({
                    "pickup_zone": zone,
                    "trip_count": int(trip_counts[zone]),
                    "total_revenue": float(total_revenues.get(zone, 0.0))
                }))
            pipe.execute()

    except Exception as e:
        print(f"Redis error: {str(e)}")
    finally:
        redis_conn.close()



# Lưu dữ liệu
# Streaming 1: HDFS
query_hdfs_valid = df_valid.writeStream \
        .format("parquet") \
        .outputMode("append") \
        .trigger(processingTime=SPARK_STREAMING__TRIGGER_TIME) \
        .option("checkpointLocation", f"{HDFS__URI}/checkpoints/hdfs/valid") \
        .option("path", f"{HDFS__URI}/raw_data/valid") \
        .partitionBy(["year", "month", "day", "hour"]) \
        .start()

query_hdfs_error = df_error.writeStream \
        .format("parquet") \
        .outputMode("append") \
        .trigger(processingTime=SPARK_STREAMING__TRIGGER_TIME) \
        .option("checkpointLocation", f"{HDFS__URI}/checkpoints/hdfs/error") \
        .option("path", f"{HDFS__URI}/raw_data/error") \
        .partitionBy(["year", "month", "day", "hour"]) \
        .start()

# Streaming 2: Redis
query_redis = df_valid.writeStream \
    .foreachBatch(write_to_redis) \
    .outputMode("append") \
    .option("checkpointLocation", f"{HDFS__URI}/checkpoints/redis") \
    .start()
    # .trigger(processingTime="10 seconds") \

# Dừng Session khi gửi xong
idle_counter = 0
max_idle_count = 5

try:
    while True:
        if not (query_redis.isActive and query_hdfs_valid.isActive and query_hdfs_error.isActive):
            break
        
        # Kiểm tra idle và xử lý
        redis_progress = query_redis.lastProgress or {}
        hdfs_progress = query_hdfs_valid.lastProgress or {}
        
        if redis_progress.get("numInputRows", 0) == 0 and hdfs_progress.get("numInputRows", 0) == 0:
            idle_counter += 1
            if idle_counter >= 5:
                print("No data for 50 seconds, stopping...")
                break
        else:
            idle_counter = 0
            
        time.sleep(10)
finally:
    query_redis.stop()
    query_hdfs_valid.stop()
    query_hdfs_error.stop()
    spark.stop()