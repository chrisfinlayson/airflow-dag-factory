from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
import tempfile
import pyhocon

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Example HOCON configuration
hocon_config = """
job-name = "example_parquet_to_iceberg"

input {
    type = file-source
    file-path = "/path/to/input/data"
    format = "parquet"
    filter = "date = '2024-01-01'"
}

output {
    catalog-name = "spark_catalog"
    database-name = "example_db"
    table-name = "output_table"
    partition-by = ["date"]
    properties {
        write.format.default = "parquet"
        write.metadata.compression-codec = "gzip"
    }
}

metrics-table = "spark_catalog.metrics.job_metrics"
write-mode = "overwrite"
"""

def create_temp_config():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(hocon_config)
        return f.name

with DAG('spark_input_sources_example',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    config_path = create_temp_config()

    submit_spark_job = SparkSubmitOperator(
        task_id='submit_spark_job',
        application='/path/to/spark-input-sources.jar',
        name='Spark Input Sources Job',
        java_class='dev.bigspark.SparkJobRunner',
        application_args=[config_path],
        conf={
            'spark.driver.memory': '2g',
            'spark.executor.memory': '2g',
            'spark.executor.cores': '2',
            'spark.executor.instances': '2',
            'spark.sql.extensions': 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions',
            'spark.sql.catalog.spark_catalog': 'org.apache.iceberg.spark.SparkCatalog',
            'spark.sql.catalog.spark_catalog.type': 'hive'
        }
    )