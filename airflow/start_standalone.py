#!/usr/bin/env python3
"""
Windows-compatible Airflow standalone starter (webserver + scheduler)
"""
import os
import sys
import subprocess
from pathlib import Path

def start_standalone():
    # Set up environment
    airflow_home = Path(__file__).parent.absolute()
    os.environ['AIRFLOW_HOME'] = str(airflow_home)
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = str(airflow_home / 'dags')
    os.environ['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'False'
    
    # Override database connection - use simple path to avoid Windows issues
    db_path = airflow_home / 'airflow.db'
    # Use a simpler path - just the filename relative to AIRFLOW_HOME
    os.environ['AIRFLOW__DATABASE__SQL_ALCHEMY_CONN'] = 'sqlite:///airflow.db'
    
    print("🚀 Starting Airflow in Standalone Mode...")
    print(f"📁 AIRFLOW_HOME: {airflow_home}")
    print(f"💾 Database: {db_path}")
    print(f"🔗 SQLite URL: sqlite:///airflow.db (relative to AIRFLOW_HOME)")
    print(f"🌐 Web UI: http://localhost:8080")
    print(f"🔑 Login: admin / admin (auto-created)")
    print()
    print("✅ This will start BOTH webserver AND scheduler")
    print("⏳ First startup may take a minute to initialize database...")
    print()
    
    try:
        # Use standalone mode - includes webserver + scheduler
        cmd = [sys.executable, '-m', 'airflow', 'standalone']
        
        # Run the command
        result = subprocess.run(cmd, check=False)
        
    except FileNotFoundError:
        print("❌ Airflow not found in PATH")
        print("💡 Make sure you activated the virtual environment:")
        print("   airflow_env\\Scripts\\Activate.ps1")
        
    except KeyboardInterrupt:
        print("\n🛑 Standalone mode stopped by user")
        
    except Exception as e:
        print(f"❌ Error starting standalone mode: {e}")
        print("\n💡 Alternative commands to try:")
        print("   python -m airflow db init  # initialize database first")
        print("   python -m airflow webserver --port 8080  # webserver only")

if __name__ == "__main__":
    start_standalone() 