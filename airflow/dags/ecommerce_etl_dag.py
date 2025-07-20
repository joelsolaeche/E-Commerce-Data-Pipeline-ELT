"""
E-Commerce ELT Pipeline DAG

This DAG orchestrates the existing ELT pipeline using Apache Airflow.
It maintains the same logic flow as the original manual process but adds:
- Task dependencies and orchestration
- Error handling and retries
- Monitoring and logging
- Parallel execution where possible

Schedule: Daily at 2:00 AM
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Add the airflow directory to Python path
AIRFLOW_ROOT = Path(__file__).parent.parent
sys.path.append(str(AIRFLOW_ROOT))

# Import our custom operators
from operators.etl_operators import (
    ExtractDataOperator,
    LoadDataOperator,
    TransformDataOperator,
    ValidateDataOperator
)

# Default arguments for all tasks
default_args = {
    'owner': 'data-engineering-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,  # Don't backfill historical runs
}

# Create the DAG
dag = DAG(
    dag_id='ecommerce_etl_pipeline',
    default_args=default_args,
    description='E-Commerce ELT Pipeline with Extract, Load, Transform, and Validation',
    schedule_interval='0 2 * * *',  # Daily at 2:00 AM
    max_active_runs=1,  # Only one instance running at a time
    tags=['ecommerce', 'etl', 'data-pipeline', 'olist'],
    doc_md=__doc__,
)

# Task 1: Start Pipeline
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag,
    doc_md="""
    ### Pipeline Start
    
    This dummy task marks the beginning of the ELT pipeline execution.
    It serves as a visual indicator in the Airflow UI and can be used
    for timing measurements.
    """
)

# Task 2: Extract Data
extract_task = ExtractDataOperator(
    task_id='extract_data',
    dag=dag,
    doc_md="""
    ### Data Extraction
    
    This task extracts data from:
    - CSV files in the dataset/ folder (9 files)
    - Brazil public holidays API for 2017
    
    **Datasets extracted:**
    - olist_customers_dataset.csv
    - olist_geolocation_dataset.csv
    - olist_order_items_dataset.csv
    - olist_order_payments_dataset.csv
    - olist_order_reviews_dataset.csv
    - olist_orders_dataset.csv
    - olist_products_dataset.csv
    - olist_sellers_dataset.csv
    - product_category_name_translation.csv
    
    The task reuses the existing `extract()` function from src/extract.py
    """
)

# Task 3: Load Data
load_task = LoadDataOperator(
    task_id='load_data',
    dag=dag,
    doc_md="""
    ### Data Loading
    
    This task loads all extracted DataFrames into the SQLite database.
    It creates/replaces tables for each dataset using pandas.to_sql().
    
    **Output:** SQLite database with 10 tables ready for transformations
    
    The task reuses the existing `load()` function from src/load.py
    """
)

# Task 4: Transform Data
transform_task = TransformDataOperator(
    task_id='transform_data',
    dag=dag,
    doc_md="""
    ### Data Transformation
    
    This task executes all SQL queries from the queries/ folder to create
    business intelligence views and aggregations.
    
    **Queries executed:**
    - delivery_date_difference.sql
    - global_amount_order_status.sql
    - real_vs_estimated_delivered_time.sql
    - revenue_by_month_year.sql
    - revenue_per_state.sql
    - top_10_least_revenue_categories.sql
    - top_10_revenue_categories.sql
    
    The task reuses the existing `run_queries()` function from src/transform.py
    """
)

# Task 5: Validate Pipeline
validate_task = ValidateDataOperator(
    task_id='validate_pipeline',
    dag=dag,
    expected_tables=10,
    doc_md="""
    ### Pipeline Validation
    
    This task validates the entire ELT pipeline execution by checking:
    - Database file exists
    - Expected number of tables were created
    - All transformations completed successfully
    - Data integrity checks
    
    **Validation criteria:**
    - Minimum 10 tables in database
    - All extraction, loading, and transformation steps completed
    - No data corruption detected
    """
)

# Task 6: Generate Report
def generate_execution_report(**context):
    """Generate a summary report of the pipeline execution."""
    
    # Get validation summary from XCom
    validation_summary = context['task_instance'].xcom_pull(
        task_ids='validate_pipeline',
        key='validation_summary'
    )
    
    # Create execution report
    execution_time = datetime.now()
    dag_run = context['dag_run']
    
    report = f"""
    ========================================
    E-COMMERCE ELT PIPELINE EXECUTION REPORT
    ========================================
    
    Execution Date: {execution_time.strftime('%Y-%m-%d %H:%M:%S')}
    DAG Run ID: {dag_run.run_id}
    Schedule Interval: {dag.schedule_interval}
    
    PIPELINE RESULTS:
    ================
    Database Path: {validation_summary.get('database_path', 'N/A')}
    Tables Created: {validation_summary.get('table_count', 'N/A')}
    Datasets Extracted: {validation_summary.get('extracted_datasets', 'N/A')}
    Tables Loaded: {validation_summary.get('loaded_tables', 'N/A')}
    Transformations: {validation_summary.get('transformation_queries', 'N/A')}
    
    Status: {validation_summary.get('validation_status', 'UNKNOWN')}
    
    TASK EXECUTION SUMMARY:
    ======================
    ✓ Extract Data: COMPLETED
    ✓ Load Data: COMPLETED  
    ✓ Transform Data: COMPLETED
    ✓ Validate Pipeline: COMPLETED
    
    ========================================
    Pipeline executed successfully!
    Data is ready for analysis and visualization.
    ========================================
    """
    
    print(report)
    return report

report_task = PythonOperator(
    task_id='generate_report',
    dag=dag,
    python_callable=generate_execution_report,
    provide_context=True,
    doc_md="""
    ### Execution Report
    
    This task generates a comprehensive report of the pipeline execution,
    including statistics, timing information, and validation results.
    
    The report is logged and can be viewed in the Airflow UI task logs.
    """
)

# Task 7: End Pipeline
end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag,
    doc_md="""
    ### Pipeline End
    
    This dummy task marks the successful completion of the ELT pipeline.
    All data has been extracted, loaded, transformed, and validated.
    
    The data is now ready for analysis and visualization.
    """
)

# Optional: Cleanup Task (commented out by default)
# cleanup_task = BashOperator(
#     task_id='cleanup_temp_files',
#     dag=dag,
#     bash_command='echo "Cleaning up temporary files..." && find /tmp -name "*olist*" -type f -delete',
#     doc_md="Optional cleanup task to remove temporary files created during processing"
# )

# Define task dependencies
# Sequential flow: Extract → Load → Transform → Validate → Report → End
start_task >> extract_task >> load_task >> transform_task >> validate_task >> report_task >> end_task

# Alternative: If you want some parallel execution, you could do:
# start_task >> extract_task >> load_task >> [transform_task, other_parallel_task] >> validate_task >> report_task >> end_task

# Task documentation at DAG level
dag.doc_md = """
# E-Commerce ELT Pipeline

This DAG orchestrates the complete ELT (Extract, Load, Transform) pipeline for the Olist e-commerce dataset.

## Pipeline Overview

1. **Extract**: Load data from CSV files and external API
2. **Load**: Store data in SQLite data warehouse  
3. **Transform**: Execute business intelligence queries
4. **Validate**: Ensure data quality and completeness
5. **Report**: Generate execution summary

## Schedule

- **Frequency**: Daily at 2:00 AM
- **Catchup**: Disabled (only runs for current date)
- **Max Active Runs**: 1 (prevents overlapping executions)

## Monitoring

- Task logs contain detailed execution information
- XCom stores intermediate results for debugging
- Email notifications can be enabled in default_args
- Pipeline validation ensures data integrity

## Dependencies

This DAG reuses existing code from the `src/` module without modification,
ensuring compatibility with existing tests and functionality.
"""

if __name__ == "__main__":
    # This section is useful for local testing
    print("DAG Definition Complete")
    print(f"DAG ID: {dag.dag_id}")
    print(f"Tasks: {[task.task_id for task in dag.tasks]}")
    print(f"Schedule: {dag.schedule_interval}") 