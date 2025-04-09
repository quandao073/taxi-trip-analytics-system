from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("SimpleTestJob") \
        .getOrCreate()

    data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
    df = spark.createDataFrame(data, ["name", "value"])

    df.show()

    spark.stop()
