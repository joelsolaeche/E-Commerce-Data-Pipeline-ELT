from typing import Dict

from pandas import DataFrame
from sqlalchemy.engine.base import Engine


def load(data_frames: Dict[str, DataFrame], database: Engine):
    """Load the dataframes into the sqlite database.

    Args:
        data_frames (Dict[str, DataFrame]): A dictionary with keys as the table names
        and values as the dataframes.
    """
    # Get the raw connection for pandas compatibility
    import sqlite3
    
    # Extract the database path from the engine URL
    database_url = str(database.url)
    if "sqlite:///" in database_url:
        db_path = database_url.replace("sqlite:///", "")
        
        # Use direct sqlite3 connection for pandas
        with sqlite3.connect(db_path) as conn:
            for table_name, df in data_frames.items():
                df.to_sql(name=table_name, con=conn, if_exists='replace', index=False)
    else:
        # Fallback to engine for non-SQLite databases
        for table_name, df in data_frames.items():
            df.to_sql(name=table_name, con=database, if_exists='replace', index=False)
    
