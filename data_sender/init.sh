#!/bin/bash

KAFKA_HOST=${KAFKA_HOST:-kafka}
KAFKA_PORT=${KAFKA_PORT:-9092}
TIMEOUT=${TIMEOUT:-60}

echo "🔍 Waiting for Kafka at $KAFKA_HOST:$KAFKA_PORT (timeout: ${TIMEOUT}s)..."

start_time=$(date +%s)

while :
do
  (echo > /dev/tcp/$KAFKA_HOST/$KAFKA_PORT) >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "✅ Kafka is up! Starting producer..."
    break
  fi

  now=$(date +%s)
  if [ $((now - start_time)) -ge $TIMEOUT ]; then
    echo "❌ Timeout waiting for Kafka ($TIMEOUT seconds)."
    exit 1
  fi

  sleep 1
done

python producer.py
