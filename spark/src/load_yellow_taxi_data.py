from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, year, month, dayofmonth, hour
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import os, time

# Các biến môi trường
TAXI_TYPE = os.environ.get("TAXI_TYPE", "yellow")
CHECKPOINT_PATH = os.environ.get("CHECKPOINT_PATH", f"hdfs://hadoop-namenode:9000/checkpoints")
HDFS_RAW_OUTPUT_PATH = os.environ.get("HDFS_RAW_OUTPUT_PATH", f"hdfs://hadoop-namenode:9000/raw_data")
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TRIGGER_TIME = os.environ.get("TRIGGER_TIME", "30 seconds")

def create_yellow_taxi_schema():
    return StructType([
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
        StructField("Airport_fee", DoubleType(), True)
    ])
def create_spark_session():
    return SparkSession.builder \
        .appName("LoadData") \
        .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5') \
        .getOrCreate()

def read_from_kafka(spark):
    """Đọc dữ liệu từ Kafka"""
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", f"{TAXI_TYPE}_trip_data") \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()

def parse_and_validate_data(df_raw, schema):
    # Parse JSON từ Kafka value
    df_parsed = df_raw \
        .selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), schema).alias("data")) \
        .select("data.*")
    
    # Định nghĩa điều kiện hợp lệ
    valid_conditions = (
        col("tpep_pickup_datetime").isNotNull() &
        col("tpep_dropoff_datetime").isNotNull() &
        (col("tpep_dropoff_datetime") >= col("tpep_pickup_datetime")) &
        col("passenger_count").between(1, 6) &
        (col("trip_distance") >= 0) &
        (col("fare_amount") >= 0) &
        (col("total_amount") >= 0) &
        col("PULocationID").between(1, 265) &
        col("DOLocationID").between(1, 265) &
        col("store_and_fwd_flag").isin("Y", "N") &
        col("payment_type").isin(0, 1, 2, 3, 4, 5, 6)
    )
    
    # Tách dữ liệu
    df_valid = df_parsed.filter(valid_conditions)
    df_error = df_parsed.filter(~valid_conditions)
    
    # Thêm cột phân vùng theo thời gian
    df_valid = df_valid \
        .withColumn("year", year(col("tpep_pickup_datetime"))) \
        .withColumn("month", month(col("tpep_pickup_datetime"))) \
        .withColumn("day", dayofmonth(col("tpep_pickup_datetime"))) \
        .withColumn("hour", hour(col("tpep_pickup_datetime")))
    
    df_error = df_error \
        .withColumn("year", year(col("tpep_pickup_datetime"))) \
        .withColumn("month", month(col("tpep_pickup_datetime"))) \
        .withColumn("day", dayofmonth(col("tpep_pickup_datetime"))) \
        .withColumn("hour", hour(col("tpep_pickup_datetime")))
    
    return df_valid, df_error

def write_to_hdfs(df, trigger_time, checkpoint_path, output_path, query_name, partition_cols=["year", "month"]):
    """Ghi dữ liệu ra HDFS dưới dạng Parquet"""
    return df.writeStream \
        .format("parquet") \
        .outputMode("append") \
        .trigger(processingTime=trigger_time) \
        .option("checkpointLocation", checkpoint_path) \
        .option("path", output_path) \
        .partitionBy(*partition_cols) \
        .queryName(query_name) \
        .start()

def main():
    schema = create_yellow_taxi_schema()
    spark = create_spark_session()

    df_raw = read_from_kafka(spark)
    df_valid, df_error = parse_and_validate_data(df_raw, schema)

    # Ghi ra HDFS
    query_valid = write_to_hdfs(
        df=df_valid,
        trigger_time=TRIGGER_TIME,
        checkpoint_path=f"{CHECKPOINT_PATH}/{TAXI_TYPE}/valid",
        output_path=f"{HDFS_RAW_OUTPUT_PATH}/{TAXI_TYPE}/valid",
        query_name="ValidStream"
    )

    query_error = write_to_hdfs(
        df=df_error,
        trigger_time=TRIGGER_TIME,
        checkpoint_path=f"{CHECKPOINT_PATH}/{TAXI_TYPE}/error",
        output_path=f"{HDFS_RAW_OUTPUT_PATH}/{TAXI_TYPE}/error",
        query_name="ErrorStream"
    )


    query_valid_console = df_valid.writeStream \
        .format("console") \
        .outputMode("append") \
        .trigger(processingTime='15 seconds') \
        .start()

    # Dừng job khi không còn dữ liệu mới
    idle_counter = 0
    max_idle_count = 5

    while query_valid_console.isActive:
        progress = query_valid_console.lastProgress
        if progress:
            input_rows = progress.get("numInputRows", 1)  # fallback = 1 để tránh None
            if input_rows == 0:
                idle_counter += 1
                print(f"[INFO] No new data. Idle {idle_counter}/{max_idle_count}")
            else:
                idle_counter = 0

            if idle_counter >= max_idle_count:
                print("[INFO] Reached max idle count. Stopping streaming query...")
                query_valid.stop()
                query_error.stop()
                query_valid_console.stop()
                break
        else:
            print("[INFO] Waiting for first progress...")

        time.sleep(10)

    spark.stop()


if __name__ == "__main__":
    main()