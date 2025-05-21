from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import os

HDFS__URI                           = os.environ.get("HDFS__URI", "hdfs://hadoop-hadoop-hdfs-nn:9000")

# Khởi tạo Spark Session
spark = SparkSession.builder \
        .appName("OptimizeStorage") \
        .getOrCreate()

# Đọc dữ liệu
df = spark.read.parquet(f"{HDFS__URI}/raw_data/valid")
df.printSchema()
df.repartition(1).write.partitionBy("year", "month").mode("overwrite").parquet(f"{HDFS__URI}/optimized_data/valid")

