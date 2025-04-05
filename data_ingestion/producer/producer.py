import requests
import time
import json
import argparse
from kafka import KafkaProducer
import pandas as pd
import os

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
API_HOST = os.environ.get("API_HOST", "http://fast-api:5000")
SPEED = float(os.environ.get("SPEED", "2.0"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, help="Hãng taxi (vd: yellow)")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    args = parser.parse_args()


    topic = f"{args.type}_trip_data"
    url_template = f"{API_HOST}/api/taxi_trip"
    offset = 0
    page_size = 100

    prev_time = None

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None
    )

    while True:
        url = f"{url_template}?type={args.type}&year={args.year}&month={args.month}&offset={offset}&limit={page_size}"
        print(f"Fetching: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            break

        payload = response.json()
        records = payload.get("data", [])
        if not records:
            print("Gửi xong toàn bộ dữ liệu.")
            break

        for data in records:
            current_time = data.get("tpep_pickup_datetime")
            if isinstance(current_time, str):
                current_time = pd.to_datetime(current_time)

            if prev_time and current_time:
                delay = (current_time - prev_time).total_seconds()
                time.sleep(min(delay / SPEED, 10))

            data["event_time"] = current_time.isoformat() if current_time else None
            key = str(data.get("PULocationID", "default"))
            producer.send(topic, key=key, value=data)
            prev_time = current_time

        offset += page_size

    producer.flush()

if __name__ == "__main__":
    main()
