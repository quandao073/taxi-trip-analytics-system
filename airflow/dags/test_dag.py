from airflow.decorators import dag, task
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

@dag(
    schedule=None,
    catchup=False
)

def my_dag():
    test = SparkSubmitOperator(
        task_id="test",
        application="/opt/airflow/code/test.py",
        conn_id="spark_default"
    )

    test_kafka = SparkSubmitOperator(
        task_id="test_kafka_job",
        application="/opt/airflow/code/main.py",
        conn_id="spark_default",
        packages="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5"
    )

    test >> test_kafka

my_dag()