import datetime as dt
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
import scripts.config as c

default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2018, 9, 24, 10, 00, 00),
    'concurrency': 1,
    'retries': 0
}

with DAG('google_api',
         catchup=False,
         default_args=default_args,
         schedule_interval='*/5 * * * *',
         ) as dag:

    run_this = BashOperator(
        task_id='update_table',
        bash_command=c.script_bash_command,
        dag=dag,
        )

run_this
