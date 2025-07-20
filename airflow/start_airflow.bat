@echo off
echo 🚀 Starting Airflow Web UI...
echo 📁 Make sure you're in the airflow directory
echo 🔑 Default login: admin / admin
echo.

REM Set environment variables
set AIRFLOW_HOME=%CD%
set AIRFLOW__CORE__DAGS_FOLDER=%CD%\dags
set AIRFLOW__CORE__LOAD_EXAMPLES=False
set AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080

REM Start Airflow webserver
echo ✅ Starting Airflow webserver...
echo 🌐 Web UI will be available at: http://localhost:8080
echo.
python -m airflow webserver --port 8080 