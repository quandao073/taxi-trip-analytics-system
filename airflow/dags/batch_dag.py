from airflow.decorators import dag, task
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
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
        time_str = Variable.get("batch_processing_time")
        time_dict = json.loads(time_str)
        time_dict.setdefault("year", 2019)
        time_dict.setdefault("month", 1)
        return time_dict
    except KeyError:
        initial_time = {"year": 2019, "month": 1}
        Variable.set("batch_processing_time", json.dumps(initial_time))
        return initial_time

@dag(
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2019, 1, 1),
    catchup=False,
    tags=["monthly_batch_processing"]
)
def batch_processing_dag():

    @task
    def get_or_create_time():
        current_time = get_or_create_time_var()
        print(f"⏳ Current batch processing time: {current_time}")
        return {
            "year": current_time["year"],
            "month": current_time["month"]
        }

    @task
    def increase_time_var():
        current_time = get_or_create_time_var()
        dt = datetime(current_time["year"], current_time["month"], 1) + relativedelta(months=1)
        updated = {"year": dt.year, "month": dt.month}
        Variable.set("batch_processing_time", json.dumps(updated))
        print(f"✅ Updated batch processing time to: {updated}")
        return updated


    time_params = get_or_create_time()

    batch_processing = SparkSubmitOperator(
        task_id="batch_processing",
        application="/opt/airflow/code/batch_processing.py",
        name="BatchProcessing",
        packages="org.postgresql:postgresql:42.7.5",
        application_args=[
            "{{ ti.xcom_pull(task_ids='get_or_create_time')['year'] }}",
            "{{ ti.xcom_pull(task_ids='get_or_create_time')['month'] }}"
        ],
        conn_id="spark_default",
        verbose=True
    )

    update_models = SparkSubmitOperator(
        task_id="update_models",
        application="/opt/airflow/code/update_predict_model.py",
        name="UpdateModel",
        conn_id="spark_default",
        verbose=True
    )

    next_time = increase_time_var()

    time_params >> batch_processing >> update_models >> next_time

batch_processing_dag = batch_processing_dag()
