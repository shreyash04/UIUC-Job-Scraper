# Filename: scrape_jobs_dag.py
import os, sys
sys.path.append("/home/shreyash_shinkar04/airflow/dags")
from datetime import datetime, timedelta
from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
from airflow.operators.python import PythonOperator
from job_scraper_uiuc_student_aid import run_scraping_uiuc_student_aid  # Import the refactored function
from job_scraper_uiuc_research import run_scraping_uiuc_research  # Import the refactored function
from airflow.providers.mongo.hooks.mongo import MongoHook
from email_jobs import fetch_users_and_send_emails  # Import from the new script

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'schedule_interval': '0 * * * *'
}

dag = DAG(
    'scrape_jobs_dag',
    default_args=default_args,
    description='A simple DAG to scrape job listings',
    is_paused_upon_creation=True
)

def checkMongoDBConnection():
    mongo_hook = MongoHook(mongo_conn_id='mongo_default')  # Define your Airflow MongoDB connection ID
    client = mongo_hook.get_conn()
    print(client)
    
check_mongodb_connection_task = PythonOperator(
    task_id='mongodb_connection',
    python_callable=checkMongoDBConnection,
    provide_context=True,
    dag=dag,
)

scrape_uiuc_student_jobs_task = PythonOperator(
    task_id='scrape_uiuc_student_jobs_task',
    python_callable=run_scraping_uiuc_student_aid,
    provide_context=True,
    dag=dag,
)

scrape_uiuc_research_task = PythonOperator(
    task_id='scrape_uiuc_research_task',
    python_callable=run_scraping_uiuc_research,
    provide_context=True,
    dag=dag,
)

send_emails_task = PythonOperator(
    task_id='send_emails_task',
    python_callable=fetch_users_and_send_emails,
    provide_context=True,
    dag=dag,
)

check_mongodb_connection_task >> [scrape_uiuc_student_jobs_task, scrape_uiuc_research_task] >> send_emails_task
