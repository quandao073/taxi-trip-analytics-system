from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="test_hello_dag",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["test"],
    description="DAG test đơn giản in ra dòng chữ Hello",
) as dag:

    hello_task = BashOperator(
        task_id="say_hello",
        bash_command='echo "👋 Hello from Airflow!"'
    )
