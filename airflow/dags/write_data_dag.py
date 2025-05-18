from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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
        time_str = Variable.get("current_processing_time")
        time_dict = json.loads(time_str)
        time_dict.setdefault("year", 2023)
        time_dict.setdefault("month", 1)
        return time_dict
    except KeyError:
        initial_time = {"year": 2023, "month": 1}
        Variable.set("current_processing_time", json.dumps(initial_time))
        return initial_time

@dag(
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2025, 4, 16),
    catchup=False,
    tags=["write_data_2023"]
)
def write_data_2023():

    @task
    def get_or_create_time():
        current_time = get_or_create_time_var()
        print(f"⏳ Current processing time: {current_time}")
        return {
            "year": current_time["year"],
            "month": current_time["month"]
        }

    @task
    def increase_time_var():
        current_time = get_or_create_time_var()
        dt = datetime(current_time["year"], current_time["month"], 1) + relativedelta(months=1)

        if dt.year > 2023:
            raise ValueError("📅 Reached end of 2023. Stop here.")

        updated = {"year": dt.year, "month": dt.month}
        Variable.set("current_processing_time", json.dumps(updated))
        print(f"✅ Updated processing time to: {updated}")
        return updated

    # Phase 1: khởi tạo hoặc lấy thời gian hiện tại
    time_params = get_or_create_time()

    # Phase 2: các task xử lý
    extract_data = BashOperator(
        task_id="extract_streaming_data",
        bash_command=(
            "python /opt/airflow/code/extract_data.py "
            f"--type {DATA_INGESTION__TAXI_TYPE} "
            f"--year {{{{ task_instance.xcom_pull(task_ids='get_or_create_time')['year'] }}}} "
            f"--month {{{{ task_instance.xcom_pull(task_ids='get_or_create_time')['month'] }}}}"
        )
    )

    write_data = BashOperator(
        task_id="write_data",
        bash_command="spark-submit /opt/airflow/code/write_data_2023.py"
    )

    # Phase 3: tăng thời gian sau khi thành công
    next_time = increase_time_var()

    time_params >> [extract_data, write_data] >> next_time

write_data_dag = write_data_2023()
