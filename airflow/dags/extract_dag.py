from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def get_or_create_time_var():
    try:
        time_str = Variable.get("current_processing_time")
        return json.loads(time_str)
    except KeyError:
        initial_time = {
            "year": 2024,
            "month": 1,
            "day": 1,
            "hour": 1
        }
        Variable.set("current_processing_time", json.dumps(initial_time))
        return initial_time

@dag(
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2025, 4, 16),
    catchup=False,
    tags=["streaming_2024_data"]
)
def streaming_hourly_dag():

    @task
    def get_and_increment_time():
        current_time = get_or_create_time_var()
        
        dt = datetime(
            current_time['year'], 
            current_time['month'], 
            current_time['day'], 
            current_time['hour']
        )
        dt += timedelta(hours=1)
        
        updated_time = {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour
        }

        if dt.year > 2024:
            raise ValueError("Reached end of processing period.")
        
        # Lưu thời gian mới vào Variable
        Variable.set("current_processing_time", json.dumps(updated_time))    
        print(f"Processing data for time: {updated_time}")
        return updated_time

    time_params = get_and_increment_time()

    extract_data = BashOperator(
        task_id="extract_streaming_data",
        bash_command=(
            "python /opt/airflow/code/extract_data.py "
            "--type yellow "
            f"--year {{{{ task_instance.xcom_pull(task_ids='get_and_increment_time')['year'] }}}} "
            f"--month {{{{ task_instance.xcom_pull(task_ids='get_and_increment_time')['month'] }}}} "
            f"--day {{{{ task_instance.xcom_pull(task_ids='get_and_increment_time')['day'] }}}} "
            f"--hour {{{{ task_instance.xcom_pull(task_ids='get_and_increment_time')['hour'] }}}}"
        )
    )

    transform_stream_data = BashOperator(
        task_id="transform_stream_data",
        bash_command=(
            "spark-submit "
            "--conf spark.sql.streaming.stopTimeout=60s "
            "--conf spark.sql.streaming.stopActiveRunOnStop=true "
            "/opt/airflow/code/load_taxi_data.py"
        ),
    )

#     # transform_stream_data = SparkSubmitOperator(
#     #     task_id="test_kafka_job",
#     #     application="/opt/airflow/code/spark/load_yellow_taxi_data.py",
#     #     conn_id="spark_default",
#     #     conf={
#     #         "spark.sql.streaming.stopTimeout": "60s",
#     #         "spark.sql.streaming.stopActiveRunOnStop": "true"
#     #     },
#     #     packages="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5"
#     # )


    time_params >> [extract_data, transform_stream_data]

streaming_dag = streaming_hourly_dag()
