from pyspark.sql import SparkSession
import os

# Khởi tạo SparkSession
spark = SparkSession.builder \
    .appName("UploadLookupToHDFS") \
    .getOrCreate()

# Đường dẫn local (trong container Airflow)
local_path = "/opt/airflow/code/taxi_zone_lookup.csv"

# Đường dẫn đích trên HDFS
HDFS__URI = os.environ.get("HDFS__URI", "hdfs://hadoop-namenode:9000")
hdfs_path = f"{HDFS__URI}/resources/taxi_zone_lookup.csv"

# Đọc file CSV
df = spark.read.option("header", True).csv(local_path)

# Ghi lên HDFS (overwrite nếu đã tồn tại)
df.repartition(1).write.mode("overwrite").option("header", True).csv(hdfs_path)

spark.stop()
