"""
Custom Airflow operators for the E-Commerce ELT Pipeline.

These operators wrap the existing ELT functions from the src/ module
without modifying the original code structure.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import sqlite3

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from pandas import DataFrame

# Add the project root to Python path to import existing modules
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.extract import extract
from src.load import load
from src.transform import run_queries
from src import config


class ExtractDataOperator(BaseOperator):
    """
    Operator to extract data from CSV files and API.
    
    This operator wraps the existing extract() function from src.extract.
    """
    
    template_fields = ['csv_folder', 'public_holidays_url']
    
    @apply_defaults
    def __init__(
        self,
        csv_folder: str = None,
        public_holidays_url: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.csv_folder = csv_folder or config.DATASET_ROOT_PATH
        self.public_holidays_url = public_holidays_url or config.PUBLIC_HOLIDAYS_URL
    
    def execute(self, context):
        """Execute the data extraction."""
        self.log.info("Starting data extraction...")
        
        try:
            # Get CSV to table mapping
            csv_table_mapping = config.get_csv_to_table_mapping()
            
            # Extract data using existing function
            dataframes = extract(
                csv_folder=self.csv_folder,
                csv_table_mapping=csv_table_mapping,
                public_holidays_url=self.public_holidays_url
            )
            
            self.log.info(f"Successfully extracted {len(dataframes)} datasets")
            for table_name, df in dataframes.items():
                self.log.info(f"  - {table_name}: {df.shape}")
            
            # Store extracted data in XCom for next tasks
            context['task_instance'].xcom_push(
                key='extracted_dataframes_info',
                value={table_name: df.shape for table_name, df in dataframes.items()}
            )
            
            return "extraction_completed"
            
        except Exception as e:
            self.log.error(f"Data extraction failed: {str(e)}")
            raise AirflowException(f"Extract operation failed: {str(e)}")


class LoadDataOperator(BaseOperator):
    """
    Operator to load data into SQLite database.
    
    This operator wraps the existing load() function from src.load.
    """
    
    template_fields = ['database_path']
    
    @apply_defaults
    def __init__(
        self,
        database_path: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.database_path = database_path or config.SQLITE_BD_ABSOLUTE_PATH
    
    def execute(self, context):
        """Execute the data loading."""
        self.log.info("Starting data loading...")
        
        try:
            # Re-extract data (in production, you might want to cache this)
            csv_table_mapping = config.get_csv_to_table_mapping()
            dataframes = extract(
                csv_folder=config.DATASET_ROOT_PATH,
                csv_table_mapping=csv_table_mapping,
                public_holidays_url=config.PUBLIC_HOLIDAYS_URL
            )
            
            # Create database engine
            engine = create_engine(f"sqlite:///{self.database_path}", echo=False)
            
            # Load data using existing function
            load(data_frames=dataframes, database=engine)
            
            self.log.info("Successfully loaded data into SQLite database")
            
            # Verify tables were created
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
            self.log.info(f"Created {len(tables)} tables in database:")
            for table in tables:
                self.log.info(f"  - {table[0]}")
            
            context['task_instance'].xcom_push(
                key='loaded_tables',
                value=[table[0] for table in tables]
            )
            
            return "loading_completed"
            
        except Exception as e:
            self.log.error(f"Data loading failed: {str(e)}")
            raise AirflowException(f"Load operation failed: {str(e)}")


class TransformDataOperator(BaseOperator):
    """
    Operator to execute SQL transformations.
    
    This operator wraps the existing run_queries() function from src.transform.
    """
    
    template_fields = ['database_path']
    
    @apply_defaults
    def __init__(
        self,
        database_path: str = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.database_path = database_path or config.SQLITE_BD_ABSOLUTE_PATH
    
    def execute(self, context):
        """Execute the data transformations."""
        self.log.info("Starting data transformations...")
        
        try:
            # Create database engine
            engine = create_engine(f"sqlite:///{self.database_path}", echo=False)
            
            # Run queries using existing function
            query_results = run_queries(database=engine)
            
            self.log.info(f"Successfully executed {len(query_results)} queries")
            for query_name, result_df in query_results.items():
                self.log.info(f"  - {query_name}: {result_df.shape}")
            
            # Store query results info in XCom
            context['task_instance'].xcom_push(
                key='query_results_info',
                value={query_name: df.shape for query_name, df in query_results.items()}
            )
            
            return "transformation_completed"
            
        except Exception as e:
            self.log.error(f"Data transformation failed: {str(e)}")
            raise AirflowException(f"Transform operation failed: {str(e)}")


class ValidateDataOperator(BaseOperator):
    """
    Operator to validate the ELT pipeline completion.
    
    This operator performs basic validation checks on the pipeline results.
    """
    
    template_fields = ['database_path']
    
    @apply_defaults
    def __init__(
        self,
        database_path: str = None,
        expected_tables: int = 10,  # Based on current pipeline
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.database_path = database_path or config.SQLITE_BD_ABSOLUTE_PATH
        self.expected_tables = expected_tables
    
    def execute(self, context):
        """Execute pipeline validation."""
        self.log.info("Starting pipeline validation...")
        
        try:
            # Check if database file exists
            db_path = Path(self.database_path)
            if not db_path.exists():
                raise AirflowException(f"Database file not found: {self.database_path}")
            
            # Check tables in database
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
            
            table_count = len(tables)
            if table_count < self.expected_tables:
                raise AirflowException(
                    f"Expected at least {self.expected_tables} tables, found {table_count}"
                )
            
            # Get data from XCom to validate previous tasks
            extracted_info = context['task_instance'].xcom_pull(
                task_ids='extract_data',
                key='extracted_dataframes_info'
            )
            
            loaded_tables = context['task_instance'].xcom_pull(
                task_ids='load_data',
                key='loaded_tables'
            )
            
            query_results = context['task_instance'].xcom_pull(
                task_ids='transform_data',
                key='query_results_info'
            )
            
            self.log.info("Pipeline validation successful!")
            self.log.info(f"  - Extracted {len(extracted_info)} datasets")
            self.log.info(f"  - Loaded {len(loaded_tables)} tables")
            self.log.info(f"  - Executed {len(query_results)} transformations")
            
            # Summary for monitoring
            validation_summary = {
                'database_path': self.database_path,
                'table_count': table_count,
                'extracted_datasets': len(extracted_info) if extracted_info else 0,
                'loaded_tables': len(loaded_tables) if loaded_tables else 0,
                'transformation_queries': len(query_results) if query_results else 0,
                'validation_status': 'PASSED'
            }
            
            context['task_instance'].xcom_push(
                key='validation_summary',
                value=validation_summary
            )
            
            return "validation_completed"
            
        except Exception as e:
            self.log.error(f"Pipeline validation failed: {str(e)}")
            raise AirflowException(f"Validation failed: {str(e)}") 