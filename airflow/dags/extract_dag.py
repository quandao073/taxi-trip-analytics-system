from airflow.decorators import dag, task
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

@dag(
    schedule="@hourly",
    start_date=datetime(2024, 1, 1),
    catchup=False
)
def my_dag():
    # year = "{{ execution_date.year }}"
    # month = "{{ execution_date.month }}"
    # day = "{{ execution_date.day }}"
    # hour = "{{ execution_date.hour }}"

    extract_task = BashOperator(
        task_id="extract_streaming_data",
        bash_command="python /opt/airflow/code/kafka_producer/producer.py --type yellow --year 2024 --month 2 --day 15 --hour 9"
        # bash_command=f"python /opt/airflow/code/kafka_producer/producer.py --type yellow --year {year} --month {month} --day {day} --hour {hour}"
    )

    transform_stream_data = SparkSubmitOperator(
        task_id="test_kafka_job",
        application="/opt/airflow/code/spark/load_yellow_taxi_data.py",
        conn_id="spark_default",
        packages="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5"
    )


my_dag()
