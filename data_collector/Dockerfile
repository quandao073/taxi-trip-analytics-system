FROM python:3.9-alpine

WORKDIR /app

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt
RUN apk add --no-cache bash busybox-extras && \
    mkdir -p /app/logs && \
    echo '0 * * * * /bin/sh -c "export $(cat /app/.env | xargs) && python3 /app/data_collector.py >> /app/logs/cron.log 2>&1"' > /etc/crontabs/root

CMD ["crond", "-f", "-l", "2"]