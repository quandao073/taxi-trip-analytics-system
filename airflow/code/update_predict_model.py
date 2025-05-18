from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml import Pipeline
import os

HDFS__URI                           = os.environ.get("HDFS__URI", "hdfs://hadoop-hadoop-hdfs-nn:9000")

# Khởi tạo Spark Session
spark = SparkSession.builder \
        .appName("UpdateModel") \
        .getOrCreate()

# Đọc dữ liệu
df = spark.read.parquet(f"{HDFS__URI}/raw_data/valid")

df.printSchema()
df.show()

df = df.withColumn("pickup_hour", date_trunc("hour", col("tpep_pickup_datetime")))

df_hourly = df.groupBy("pickup_hour") \
    .agg(count("*").alias("trip_count"))

# Tạo feature thời gian
df_features = df_hourly.withColumn("hour", hour("pickup_hour")) \
    .withColumn("day_of_week", dayofweek("pickup_hour")) \
    .withColumn("is_weekend", (dayofweek("pickup_hour").isin(1, 7)).cast("int"))  # 1: CN, 7: Thứ 7

# 1. Thêm nhãn future_trip_count (số chuyến đi trong 1 giờ kế tiếp)
w = Window.orderBy("pickup_hour")
df_lagged = df_features.withColumn("future_trip_count", lead("trip_count").over(w))
df_train = df_lagged.dropna(subset=["future_trip_count"])

# 2. Tạo vector đặc trưng
feature_cols = ["hour", "day_of_week", "is_weekend", "trip_count"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

# 3. Mô hình RandomForestRegressor
regressor = RandomForestRegressor(featuresCol="features", labelCol="future_trip_count")

# 4. Pipeline huấn luyện
pipeline = Pipeline(stages=[assembler, regressor])
model = pipeline.fit(df_train)

# 5. Lưu mô hình lên HDFS
model.write().overwrite().save(f"{HDFS__URI}/models/trip_forecast_model")

print("✅ Đã huấn luyện và lưu model thành công.")
