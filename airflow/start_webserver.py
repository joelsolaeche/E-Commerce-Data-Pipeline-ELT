#!/usr/bin/env python3
"""
Windows-compatible Airflow webserver starter
"""
import os
import sys
import subprocess
from pathlib import Path

def start_webserver():
    # Set up environment
    airflow_home = Path(__file__).parent.absolute()
    os.environ['AIRFLOW_HOME'] = str(airflow_home)
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = str(airflow_home / 'dags')
    os.environ['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'False'
    os.environ['AIRFLOW__WEBSERVER__WEB_SERVER_PORT'] = '8080'
    
    print("🚀 Starting Airflow Webserver for Windows...")
    print(f"📁 AIRFLOW_HOME: {airflow_home}")
    print(f"🌐 Web UI: http://localhost:8080")
    print(f"🔑 Login: admin / admin")
    print()
    
    try:
        # Use webserver command with explicit port
        print("✅ Starting webserver...")
        cmd = [
            sys.executable, '-m', 'airflow', 'webserver',
            '--port', '8080',
            '--hostname', '0.0.0.0'
        ]
        
        # Run the command
        result = subprocess.run(cmd, check=False)
        
    except FileNotFoundError:
        print("❌ Airflow not found in PATH")
        print("💡 Make sure you activated the virtual environment:")
        print("   airflow_env\\Scripts\\Activate.ps1")
        
    except KeyboardInterrupt:
        print("\n🛑 Webserver stopped by user")
        
    except Exception as e:
        print(f"❌ Error starting webserver: {e}")
        print("\n💡 Alternative commands to try:")
        print("   python -m airflow standalone")
        print("   python -m airflow webserver --port 8080")
        print("   python -m airflow db init  # if database not initialized")

if __name__ == "__main__":
    start_webserver() 