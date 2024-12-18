from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import os

def get_vault_credentials(vault_path):
    """Get credentials from Vault"""
    VAULT_ADDR = os.getenv('VAULT_ADDR', 'http://vault:8200')
    VAULT_TOKEN = os.getenv('VAULT_TOKEN', 'root')
    
    response = requests.get(
        f"{VAULT_ADDR}/v1/{vault_path}",
        headers={"X-Vault-Token": VAULT_TOKEN}
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get credentials from Vault: {response.text}")
    
    return response.json()['data']['data']

def run_spark_job():
    # Get credentials from Vault
    airflow_creds = get_vault_credentials("postgres/data/airflow-db")
    dbt_creds = get_vault_credentials("postgres/data/dbt-db")
    
    # Configure Spark job with credentials from Vault
    spark_config = {
        "airflow_source": {
            "url": "jdbc:postgresql://postgres-airflow:5432/airflowdb",
            "table": "dag_run",
            "credentials": {
                "vaultAddress": os.getenv('VAULT_ADDR', 'http://vault:8200'),
                "vaultToken": os.getenv('VAULT_TOKEN', 'root'),
                "vaultPath": "postgres"
            }
        },
        "dbt_source": {
            "url": "jdbc:postgresql://postgres-dbt:5432/dbtdb",
            "table": "orders",
            "credentials": {
                "vaultAddress": os.getenv('VAULT_ADDR', 'http://vault:8200'),
                "vaultToken": os.getenv('VAULT_TOKEN', 'root'),
                "vaultPath": "postgres"
            }
        }
    }
    
    # Your existing Spark job execution code here...

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'spark_postgres_vault_example',
    default_args=default_args,
    description='Example DAG using Spark with Vault credentials',
    schedule_interval=timedelta(days=1),
)

run_spark = PythonOperator(
    task_id='run_spark_job',
    python_callable=run_spark_job,
    dag=dag,
)

run_spark