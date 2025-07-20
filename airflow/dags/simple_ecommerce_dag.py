"""
Simple E-Commerce ELT Pipeline DAG

This is a simplified version that uses basic Airflow operators
to demonstrate the pipeline structure without custom dependencies.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

def print_step(step_name):
    """Simple function to demonstrate task execution"""
    print(f"Executing step: {step_name}")
    return f"Step {step_name} completed successfully!"

# Default arguments
default_args = {
    'owner': 'data-engineering-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

# Create the DAG
dag = DAG(
    dag_id='simple_ecommerce_etl',
    default_args=default_args,
    description='Simplified E-Commerce ETL Pipeline',
    schedule_interval=timedelta(days=1),
    tags=['ecommerce', 'etl', 'demo'],
)

# Define tasks
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=print_step,
    op_args=['Data Extraction'],
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=print_step,
    op_args=['Data Transformation'],
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=print_step,
    op_args=['Data Loading'],
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_data',
    python_callable=print_step,
    op_args=['Data Validation'],
    dag=dag
)

end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag
)

# Define dependencies
start_task >> extract_task >> transform_task >> load_task >> validate_task >> end_task 