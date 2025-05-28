from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import json, os

DATA_INGESTION__TAXI_TYPE = os.environ.get("DATA_INGESTION__TAXI_TYPE", "yellow")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def get_or_create_time_var():
    try:
        time_str = Variable.get("current_stream_processing_time")
        time_dict = json.loads(time_str)
        time_dict.setdefault("year", 2024)
        time_dict.setdefault("month", 1)
        time_dict.setdefault("day", 1)
        time_dict.setdefault("hour", 0)

        return time_dict
    except KeyError:
        initial_time = {"year": 2024, "month": 1, "day": 1, "hour": 0}
        Variable.set("current_stream_processing_time", json.dumps(initial_time))
        return initial_time


@dag(
    default_args=default_args,
    start_date=datetime(2025, 4, 16),
    schedule_interval=None,
    # schedule_interval=timedelta(hours=1),
    catchup=False,
    tags=["streaming_data"]
)
def streaming_hourly_dag():

    @task
    def get_or_create_time():
        current_time = get_or_create_time_var()
        print(f"⏳ Current processing time: {current_time}")
        return {
            "year": current_time["year"],
            "month": current_time["month"],
            "day": current_time["day"],
            "hour": current_time["hour"]
        }

    @task
    def increase_time_var():
        current_time = get_or_create_time_var()
        dt = datetime(current_time["year"], current_time["month"], current_time["day"], current_time["hour"]) + timedelta(hours=1)

        if dt.year > 2024:
            raise ValueError("📅 Reached end of 2024. Stop here.")

        updated = {"year": dt.year, "month": dt.month, "day": dt.day, "hour": dt.hour}
        Variable.set("current_stream_processing_time", json.dumps(updated))
        print(f"✅ Updated processing time to: {updated}")
        return updated


    time_params = get_or_create_time()

    extract_data = BashOperator(
        task_id="extract_streaming_data",
        bash_command=(
            "python /opt/airflow/code/extract_data.py "
            f"--type {DATA_INGESTION__TAXI_TYPE} "
            f"--year {{{{ task_instance.xcom_pull(task_ids='get_or_create_time')['year'] }}}} "
            f"--month {{{{ task_instance.xcom_pull(task_ids='get_or_create_time')['month'] }}}} "
            f"--day {{{{ task_instance.xcom_pull(task_ids='get_or_create_time')['day'] }}}} "
            f"--hour {{{{ task_instance.xcom_pull(task_ids='get_or_create_time')['hour'] }}}}"
        )
    )

    transform_load_data = BashOperator(
        task_id="transform_load_data",
        bash_command="spark-submit /opt/airflow/code/transform_load_data.py",
    )

    next_time = increase_time_var()

    time_params >> [extract_data, transform_load_data] >> next_time

streaming_dag = streaming_hourly_dag()
