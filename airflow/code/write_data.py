from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import sys

# Đọc tham số dòng lệnh
if len(sys.argv) < 3:
    print("Usage: spark-submit test.py <year> <month>")
    sys.exit(1)

input_year = int(sys.argv[1])
input_month = int(sys.argv[2])
input_month_str = f"{input_month:02d}"

# Khởi tạo Spark Session
spark = SparkSession.builder \
        .appName("WriteData") \
        .getOrCreate()

HDFS__URI = os.environ.get("HDFS__URI", "hdfs://hadoop-namenode:9000")

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

# Đọc dữ liệu tháng cụ thể
input_path = f"/tmp/data/yellow_tripdata_{input_year}-{input_month_str}.csv"
df = spark.read.option("header", "true").schema(schema).csv(input_path)

df = df.withColumn("year", year(col("tpep_pickup_datetime"))) \
       .withColumn("month", month(col("tpep_pickup_datetime"))) \
       .withColumn("day", dayofmonth(col("tpep_pickup_datetime"))) \
       .withColumn("hour", hour(col("tpep_pickup_datetime")))

df = df.fillna({
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

df_valid = df.filter(valid_conditions)
df_error = df.filter(~valid_conditions)

df_valid = df_valid.filter((col("year") == input_year) & (col("month") == input_month))

# Ghi ra HDFS
df_valid.repartition(1).write.partitionBy("year", "month").mode("append").parquet(f"{HDFS__URI}/raw_data/valid")
df_error.repartition(1).write.partitionBy("year", "month").mode("append").parquet(f"{HDFS__URI}/raw_data/error")
