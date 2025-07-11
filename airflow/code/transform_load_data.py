from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType, LongType
from pyspark.ml import PipelineModel
from datetime import timedelta
import os, time, json
from redis import Redis
from redis.connection import ConnectionPool

# Các biến môi trường
DATA_INGESTION__TAXI_TYPE           = os.environ.get("DATA_INGESTION__TAXI_TYPE", "yellow")
KAFKA__BOOTSTRAP_SERVERS            = os.environ.get("KAFKA__BOOTSTRAP_SERVERS", "kafka:9092")
SPARK_STREAMING__TRIGGER_TIME       = os.environ.get("SPARK_STREAMING__TRIGGER_TIME", "10 seconds")
HDFS__URI                           = os.environ.get("HDFS__URI", "hdfs://hadoop-hadoop-hdfs-nn:9000")
REDIS__PASSWORD                     = os.environ.get("REDIS__PASSWORD", "quanda")

REDIS__HOST                         = os.environ.get("REDIS__HOST", "redis-master.bigdata.svc.cluster.local")
REDIS__PORT                         = os.environ.get("REDIS__PORT", "6379")

REDIS_POOL = ConnectionPool(
    host=REDIS__HOST,
    port=int(REDIS__PORT),
    password=REDIS__PASSWORD,
    decode_responses=True
)

# Định nghĩa schema
schema = StructType(
    [
        StructField("VendorID", IntegerType(), True),
        StructField("tpep_pickup_datetime", TimestampType(), True),
        StructField("tpep_dropoff_datetime", TimestampType(), True),
        StructField("passenger_count", IntegerType(), True),
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

model = PipelineModel.load(f"{HDFS__URI}/models/trip_forecast_model")

# Khởi tạo Spark Session
spark = SparkSession.builder \
        .appName("TransformLoadData") \
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

# Biến đổi, làm sạch dữ liệu
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

df_valid.printSchema()

def write_to_redis(batch_df, batch_id):
    redis_conn = Redis(connection_pool=REDIS_POOL)
    # redis_conn = get_redis_connection()

    try:
        timestamp_df = batch_df.select(max("tpep_pickup_datetime").alias("max_pickup_time")).collect()
        current_pickup_time = timestamp_df[0]["max_pickup_time"]

        if current_pickup_time is not None:
            formatted_time = current_pickup_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Tổng số chuyến đi trong batch hiện tại
            trip_count_df = batch_df.select(count("*").alias("batch_trip_count")).collect()
            batch_trip_count = int(trip_count_df[0]["batch_trip_count"])

            # Cộng dồn chuyến đi
            total_trips_key = "total_trips"
            current_total = redis_conn.get(total_trips_key)
            current_total = int(current_total) if current_total else 0
            new_total = current_total + batch_trip_count
            redis_conn.set(total_trips_key, new_total)

            if redis_conn.ttl(total_trips_key) == -1:
                redis_conn.expire(total_trips_key, 86400)
            
            # Dự đoán số chuyến đi phát sinh trong 1 giờ tới
            future_time = current_pickup_time + timedelta(hours=1)
            predict_input = spark.createDataFrame([{
                "hour": future_time.hour,
                "day_of_week": future_time.isoweekday(),
                "is_weekend": 1 if future_time.weekday() >= 5 else 0,
                "trip_count": new_total
            }])

            predicted_df = model.transform(predict_input)
            predicted_increment = int(predicted_df.select("prediction").first()["prediction"])
            predicted_trip_count = new_total + predicted_increment

            predicted_time = (current_pickup_time + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

            redis_conn.publish("realtime-trip-channel", json.dumps({
                "timestamp": formatted_time,
                "trip_count": new_total,
                "predicted_timestamp": predicted_time,
                "predicted_trip_count": predicted_trip_count
            }))

            print(f"Published: {formatted_time}, total={new_total}, predict@+1h={predicted_trip_count}")

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
    .trigger(processingTime="3 seconds") \
    .option("checkpointLocation", f"{HDFS__URI}/checkpoints/redis") \
    .start()

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