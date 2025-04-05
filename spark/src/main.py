from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, year, month, dayofmonth, hour
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType

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
        StructField("Airport_fee", DoubleType(), True),
        StructField("event_time", TimestampType(), True)
    ])

def create_spark_session():
    return SparkSession.builder \
        .appName("TaxiTripStreamProcessor") \
        .config("spark.sql.files.maxPartitionBytes", "134217728") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.shuffle.partitions", "10") \
        .config("spark.memory.offHeap.enabled", "true") \
        .config("spark.memory.offHeap.size", "1g") \
        .getOrCreate()

def read_from_kafka(spark):
    """Đọc dữ liệu từ Kafka"""
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "yellow_trip_data") \
        .option("startingOffsets", "latest") \
        .option("maxOffsetsPerTrigger", 10000) \
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
        .withColumn("year", year(col("event_time"))) \
        .withColumn("month", month(col("event_time"))) \
        .withColumn("day", dayofmonth(col("event_time"))) \
        .withColumn("hour", hour(col("event_time")))
    
    df_error = df_error \
        .withColumn("year", year(col("event_time"))) \
        .withColumn("month", month(col("event_time"))) \
        .withColumn("day", dayofmonth(col("event_time"))) \
        .withColumn("hour", hour(col("event_time")))
    
    return df_valid, df_error

def write_to_hdfs(df, checkpoint_path, output_path, query_name, partition_cols=["year", "month", "day", "hour"]):
    """Ghi dữ liệu ra HDFS dưới dạng Parquet"""
    return df.writeStream \
        .format("parquet") \
        .outputMode("append") \
        .trigger(processingTime='1 minutes') \
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
    
    query_valid = write_to_hdfs(
        df_valid,
        "/tmp/spark-checkpoint/valid",
        "hdfs://hadoop-namenode:9000/raw_data/yellow_trips/valid",
        "ValidStream"
    )
    
    query_error = write_to_hdfs(
        df_error,
        "/tmp/spark-checkpoint/error",
        "hdfs://hadoop-namenode:9000/raw_data/yellow_trips/error",
        "ErrorStream"
    )
    
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()