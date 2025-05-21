from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import os
import sys

POSTGRES__URI           = os.environ.get("POSTGRES__URI", "jdbc:postgresql://postgres-db:5432")
POSTGRES__USERNAME      = os.environ.get("POSTGRES__USERNAME", "quanda")
POSTGRES__PASSWORD      = os.environ.get("POSTGRES__PASSWORD", "quanda")
POSTGRES__DATABASE      = os.environ.get("POSTGRES__DATABASE", "taxi_trip_db")
HDFS__URI               = os.environ.get("HDFS__URI", "hdfs://hadoop-namenode:9000")

if len(sys.argv) < 3:
    sys.exit(1)

input_year = int(sys.argv[1])
input_month = int(sys.argv[2])
# input_month_str = f"{input_month:02d}"

spark = SparkSession.builder.appName("MonthlyBatchProcessing").getOrCreate()

df = spark.read.parquet(f"{HDFS__URI}/raw_data/valid/year={input_year}/month={input_month}")

df.printSchema()

# Thêm thông tin về địa điểm
lookup_df = spark.read.option("header", True).csv(f"{HDFS__URI}/resources/taxi_zone_lookup.csv")
pickup_lookup = lookup_df.withColumnRenamed("LocationID", "PULocationID") \
                         .withColumnRenamed("Borough", "pickup_borough") \
                         .withColumnRenamed("Zone", "pickup_zone") \
                         .drop("service_zone")

dropoff_lookup = lookup_df.withColumnRenamed("LocationID", "DOLocationID") \
                          .withColumnRenamed("Borough", "dropoff_borough") \
                          .withColumnRenamed("Zone", "dropoff_zone") \
                          .drop("service_zone")

df = df.join(broadcast(pickup_lookup), on="PULocationID", how="left") \
       .join(broadcast(dropoff_lookup), on="DOLocationID", how="left")

df = df.withColumn("year", year(col("tpep_pickup_datetime"))) \
       .withColumn("month", month(col("tpep_pickup_datetime"))) \
       .withColumn("day", dayofmonth(col("tpep_pickup_datetime"))) \
       .withColumn("hour", hour(col("tpep_pickup_datetime")))

# Thêm các trường dữ liệu cần thiết
df = df.withColumn("hour_label", format_string("%02d:00", col("hour"))) \
       .withColumn("payment_type_name", when(col("payment_type") == 0, "Flex Fare trip")
                                       .when(col("payment_type") == 1, "Credit card")
                                       .when(col("payment_type") == 2, "Cash")
                                       .when(col("payment_type") == 3, "No charge")
                                       .when(col("payment_type") == 4, "Dispute")
                                       .when(col("payment_type") == 5, "Unknown")
                                       .when(col("payment_type") == 6, "Voided trip")
                                       .otherwise("Other")
                  ) \
       .withColumn("trip_distance_km", round(col("trip_distance") * 1.60934, 2)) \
       .withColumn("trip_duration_minutes",
                      round((unix_timestamp("tpep_dropoff_datetime") - unix_timestamp("tpep_pickup_datetime")) / 60, 2)) \
       .withColumn("trip_speed_mph", round((col("trip_distance") / (col("trip_duration_minutes") / 60)), 2)) \

# Loại bỏ dữ liệu bất thường
df_processed = df.filter((col("trip_speed_mph") > 1) & (col("trip_speed_mph") < 70)) \
                 .filter(col("trip_distance") <= 100)

# Lưu lại dữ liệu chuẩn
df_processed.repartition("day").write \
    .partitionBy("year", "month") \
    .mode("append") \
    .parquet(f"{HDFS__URI}/processed_data/")

df_processed.printSchema()

# lưu dữ liệu lên PostgreSQL
df_processed.write.jdbc(
    url=f"{POSTGRES__URI}/{POSTGRES__DATABASE}",
    table="fact_trips",
    mode="overwrite",
    properties={"user": f"{POSTGRES__USERNAME}", "password": f"{POSTGRES__PASSWORD}", "driver": "org.postgresql.Driver"}
)
