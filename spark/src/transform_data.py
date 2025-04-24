from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth, hour
import sys

if len(sys.argv) != 5:
    print("Usage: spark-submit transform_taxi_data.py <year> <month> <day> <hour>")
    sys.exit(1)

year_arg = int(sys.argv[1])
month_arg = int(sys.argv[2])
day_arg = int(sys.argv[3])
hour_arg = int(sys.argv[4])

INPUT_PATH = f"hdfs://hadoop-namenode:9000/raw_data/year={year_arg}/month={month_arg}/day={day_arg}/hour={hour_arg}"
OUTPUT_PATH = "hdfs://hadoop-namenode:9000/clean_data/"

spark = SparkSession.builder \
    .appName("TransformTaxiDataHourly") \
    .getOrCreate()

# Đọc dữ liệu thô
df = spark.read.parquet(INPUT_PATH) 
df.printSchema()

# Làm sạch dữ liệu
df = df.dropna(subset=["tpep_pickup_datetime", "total_amount"])
df = df.dropDuplicates()

# Lấp null bằng giá trị mặc định
df = df.fillna({
    "passenger_count": 1,
    "airport_fee": 0.0,
    "congestion_surcharge": 0.0,
    "store_and_fwd_flag": "N"
})

# Thêm cột thời gian từ tpep_pickup_datetime
# df = df.withColumn("pickup_year", year(col("tpep_pickup_datetime"))) \
#        .withColumn("pickup_month", month(col("tpep_pickup_datetime"))) \
#        .withColumn("pickup_day", dayofmonth(col("tpep_pickup_datetime"))) \
#        .withColumn("pickup_hour", hour(col("tpep_pickup_datetime")))

# Ghi lại dữ liệu sạch theo year/month
df.write.mode("overwrite") \
    .partitionBy("year", "month") \
    .parquet(OUTPUT_PATH)

print(f"✅ Transformed and saved clean data for {year_arg}-{month_arg:02d}-{day_arg:02d} hour {hour_arg} to {OUTPUT_PATH}")

spark.stop()
