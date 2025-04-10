FROM apache/airflow:2.9.2

ARG SPARK_VERSION=3.5.5

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-jdk \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir \
    pyspark==${SPARK_VERSION} \
    apache-airflow-providers-apache-spark==5.1.1 \
    kafka-python \
    requests \
    pandas \
    pyarrow
