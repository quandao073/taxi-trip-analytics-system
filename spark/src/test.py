from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month
import sys

if len(sys.argv) < 2:
    print("Usage: spark-submit batch_transform_test.py <year>")
    sys.exit(1)

year_arg = sys.argv[1]
month_arg = sys.argv[2]
input_path = f"/tmp/data/{year_arg}/yellow_tripdata_{year_arg}-{int(month_arg):02d}.parquet"
output_path = "hdfs://hadoop-namenode:9000/raw_data"

# Tạo SparkSession
spark = SparkSession.builder \
    .appName(f"BatchTransform_{year_arg}") \
    .getOrCreate()

# Đọc dữ liệu
df = spark.read \
    .option("mergeSchema", True) \
    .parquet(input_path)

df = df.withColumnRenamed("Airport_fee", "airport_fee")
df = df.withColumn("year", year(col("tpep_pickup_datetime"))) \
       .withColumn("month", month(col("tpep_pickup_datetime")))

df = df.filter((col("year") == year_arg) & (col("month") == month_arg))

df.write.mode("append") \
    .partitionBy("year", "month") \
    .parquet(output_path)

spark.stop()
