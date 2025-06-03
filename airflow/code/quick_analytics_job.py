
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

spark = SparkSession.builder.appName("QuickAnalyticsJob").getOrCreate()

df = spark.read.parquet(f"{HDFS__URI}/processed_data/year={input_year}/month={input_month}")

df_time_analytics = df.groupBy("year", "month") \
    .agg(
        count("*").alias("trip_count"),
        round(sum("total_amount"), 2).alias("total_revenue"),
        round(avg("trip_distance_km"), 2).alias("avg_distance_km"),
        round(avg("trip_duration_minutes"), 2).alias("avg_duration_minutes"),
        round(avg("trip_speed_kph"), 2).alias("avg_speed_kph")
    )

df_route_analytics = df.groupBy("year", "month", "pickup_zone", "dropoff_zone") \
    .agg(
        count("*").alias("trip_count"),
        round(avg("trip_distance_km"), 2).alias("avg_distance_km"),
        round(avg("trip_duration_minutes"), 2).alias("avg_duration_minutes"),
        round(avg("fare_amount"), 2).alias("avg_fare"),
        round(sum("total_amount"), 2).alias("total_revenue")
    )

db_properties = {
    "user": POSTGRES__USERNAME,
    "password": POSTGRES__PASSWORD,
    "driver": "org.postgresql.Driver"
}

df_time_analytics.write.jdbc(
    url=f"{POSTGRES__URI}/{POSTGRES__DATABASE}",
    table="analyze_by_time",
    mode="append",
    properties=db_properties
)

df_route_analytics.write.jdbc(
    url=f"{POSTGRES__URI}/{POSTGRES__DATABASE}",
    table="analyze_by_routes",
    mode="append",
    properties=db_properties
)
