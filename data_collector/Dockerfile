FROM python:3.9-alpine

WORKDIR /app

COPY . .

ENV API_KEY="aa3d3d0651c5e4211c71196913dcc929f6891ad4"

RUN pip3 install -r requirements.txt
RUN apk add --no-cache bash busybox-extras && \
    rm -rf /var/cache/apk/*
RUN mkdir -p /app/logs
RUN echo "*/30 * * * * python3 /app/data_collector.py >> /app/logs/cron.log 2>&1" > /etc/crontabs/root

CMD ["crond", "-f", "-l", "2"]