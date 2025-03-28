import requests
import os
import json
import time
from kafka import KafkaProducer
from zoneinfo import ZoneInfo
from datetime import datetime

API_KEY = os.getenv("API_KEY", "")
BASE_URL = "https://api.waqi.info/feed/geo:{lat};{lon}/?token=" + API_KEY

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = "air_quality"
INTERVAL = int(os.getenv("INTERVAL_SECONDS", "3600"))

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None
)

CITIES = [
    {
        "name": "Hà Nội",
        "station_locations": [
            (21.0811211, 105.8180306),
            (21.01525, 105.80013),
            (21.0491, 105.8831),
            (21.0215063, 105.8188748),
            (21.035584, 105.852771),
            (21.04975, 105.74187),
            (21.148273, 105.913306),
            (21.002383, 105.718038)
        ]
    },
    {
        "name": "Hồ Chí Minh",
        "station_locations": [
            (10.65961, 106.727916)
        ]
    },
    {
        "name": "Huế",
        "station_locations": [
            (16.46226, 107.596351)
        ]
    },
    {
        "name": "Đà Nẵng",
        "station_locations": [
            (16.043252, 108.206826),
            (16.074, 108.217)
        ]
    },
    {
        "name": "Cần Thơ",
        "station_locations": [
            (10.026977, 105.768249)
        ]
    },
    {
        "name": "Vũng Tàu",
        "station_locations": [
            (10.589853, 107.131743)
        ]
    },
    {
        "name": "Cao Bằng",
        "station_locations": [
            (22.67953, 106.215361),
            (22.6782, 106.245)
        ]
    },
    {
        "name": "Nha Trang",
        "station_locations": [
            (12.284358, 109.192524)
        ]
    }
]

def get_vietnam_time():
    return datetime.now(ZoneInfo("Asia/Bangkok")).strftime("%Y-%m-%d %H:%M:%S")

def get_air_quality(lat, lon, city_name):
    url = BASE_URL.format(lat=lat, lon=lon)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return {
                    "timestamp": data["data"]["time"]["s"],
                    "station_id": data["data"]["idx"],
                    "station_name": data["data"]["city"]["name"],
                    "city_name": city_name,
                    "url": data["data"]["city"]["url"],
                    "latitude": lat,
                    "longitude": lon,
                    "aqi": data["data"].get("aqi"),
                    "co": data["data"].get("iaqi", {}).get("co", {}).get("v"),
                    "temperature": data["data"].get("iaqi", {}).get("t", {}).get("v"),
                    "wind": data["data"].get("iaqi", {}).get("w", {}).get("v"),
                    "atmospheric_pressure": data["data"].get("iaqi", {}).get("p", {}).get("v"),
                    "humidity": data["data"].get("iaqi", {}).get("h", {}).get("v"),
                    "pm25": data["data"].get("iaqi", {}).get("pm25", {}).get("v"),
                    "pm10": data["data"].get("iaqi", {}).get("pm10", {}).get("v"),
                    "o3": data["data"].get("iaqi", {}).get("o3", {}).get("v"),
                    "no2": data["data"].get("iaqi", {}).get("no2", {}).get("v")
                }
        return {"timestamp": get_vietnam_time(), "error": "No data", "latitude": lat, "longitude": lon}
    except Exception as e:
        return {"timestamp": get_vietnam_time(), "error": str(e), "latitude": lat, "longitude": lon}

def crawl_all_cities():
    for city in CITIES:
        city_name = city["name"]
        for lat, lon in city["station_locations"]:
            air_quality_data = get_air_quality(lat, lon, city_name)
            print(f"Sending data for {city_name}: {air_quality_data}")
            partition_key = f"station-{air_quality_data['station_id']}"
            producer.send(KAFKA_TOPIC, key=partition_key, value=air_quality_data)
            time.sleep(1)

if __name__ == "__main__":
    while True:
        print(f"[{get_vietnam_time()}] Starting data collector...")
        crawl_all_cities()
        print(f"[{get_vietnam_time()}] Sleeping for {INTERVAL} seconds...\n")
        time.sleep(INTERVAL)
