import pandas as pd
import time
import json
import os
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "yellow_tripdata")
SPEED = float(os.environ.get("SPEED", 2.0))

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda x: json.dumps(x, default=str).encode("utf-8")
)

data_dir = "./data"
parquet_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".parquet")])

for file_name in parquet_files:
    print(f"📦 Đang gửi file: {file_name}")
    file_path = os.path.join(data_dir, file_name)
    df = pd.read_parquet(file_path)
    df = df.sort_values("tpep_pickup_datetime")

    prev_time = None
    for _, row in df.iterrows():
        data = row.to_dict()
        current_time = data["tpep_pickup_datetime"]

        if prev_time:
            delay = (current_time - prev_time).total_seconds()
            time.sleep(min(delay / SPEED, 10))

        data["event_time"] = current_time.isoformat()
        producer.send(KAFKA_TOPIC, value=data)

        prev_time = current_time
