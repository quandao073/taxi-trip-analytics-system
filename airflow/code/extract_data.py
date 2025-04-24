import requests
import time
import json
import argparse
from kafka import KafkaProducer
import pandas as pd
import os

KAFKA__BOOTSTRAP_SERVERS = os.environ.get("KAFKA__BOOTSTRAP_SERVERS", "kafka:9092")
DATA_INGESTION__API_HOST = os.environ.get("DATA_INGESTION__API_HOST", "http://fast-api:5000")
DATA_INGESTION__SPEED = float(os.environ.get("DATA_INGESTION__SPEED", "100.0"))
DATA_INGESTION__QUERY_PAGE_SIZE = int(os.environ.get("DATA_INGESTION__QUERY_PAGE_SIZE", "100000"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, help="Hãng taxi (vd: yellow)")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--day", type=int, required=False)
    parser.add_argument("--hour", type=int, required=False)
    args = parser.parse_args()

    if args.type == "yellow":
        pickup_field = "tpep_pickup_datetime"
        dropoff_field = "tpep_dropoff_datetime"
    elif args.type == "green":
        pickup_field = "lpep_pickup_datetime"
        dropoff_field = "lpep_dropoff_datetime"
    else:
        print(f"Không hỗ trợ loại taxi: {args.type}")
        return

    topic = f"{args.type}_trip_data"
    url_template = f"{DATA_INGESTION__API_HOST}/api/taxi_trip"
    offset = 0
    prev_time = None

    producer = KafkaProducer(
        bootstrap_servers=KAFKA__BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None
    )

    while True:
        url = f"{url_template}?type={args.type}&year={args.year}&month={args.month}&day={args.day}&hour={args.hour}&offset={offset}&limit={DATA_INGESTION__QUERY_PAGE_SIZE}"
        # url = f"{url_template}?type={args.type}&year={args.year}&month={args.month}&offset={offset}&limit={DATA_INGESTION__QUERY_PAGE_SIZE}"
        print(f"Fetching: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"API error {response.status_code}: {response.text}")
            break

        payload = response.json()
        status = payload.get("status", "")
        records = payload.get("data", [])

        if status == "done" or not records:
            print("Gửi xong toàn bộ dữ liệu.")
            break

        print(f"Đã gửi {len(records)} bản ghi vào Kafka topic '{topic}' (offset={offset})")

        for data in records:
            current_time = data.get(pickup_field)
            if isinstance(current_time, str):
                current_time = pd.to_datetime(current_time)

            if prev_time and current_time:
                delay = (current_time - prev_time).total_seconds()
                time.sleep(min(delay / DATA_INGESTION__SPEED, 10))

            key = str(data.get("PULocationID", "default"))
            producer.send(topic, key=key, value=data)
            prev_time = current_time

        offset += DATA_INGESTION__QUERY_PAGE_SIZE
        time.sleep(0.2)

    producer.flush()

if __name__ == "__main__":
    main()
