FROM apache/airflow:2.9.2

ARG SPARK_VERSION=3.5.5

USER root

RUN apt update && apt install -y default-jdk wget curl
RUN wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin

USER airflow

RUN pip install pyspark==3.5.5 apache-airflow-providers-apache-spark==5.1.1