# Airflow Docker Startup Script for Windows
Write-Host "🐳 Starting Airflow with Docker..." -ForegroundColor Green
Write-Host "🌐 Web UI will be available at: http://localhost:8080" -ForegroundColor Cyan
Write-Host "🔑 Login: admin / admin" -ForegroundColor Yellow
Write-Host ""

# Set environment variables for Docker
$env:AIRFLOW_UID = "50000"

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    Write-Host "📁 Creating logs directory..."
    New-Item -ItemType Directory -Path "logs"
}

# Start Docker Compose
Write-Host "🚀 Starting Docker containers..." -ForegroundColor Green
Write-Host "⏳ First startup may take 5-10 minutes to download images and initialize..."
Write-Host ""

try {
    docker-compose up -d
    
    Write-Host ""
    Write-Host "✅ Airflow is starting up!" -ForegroundColor Green
    Write-Host "🌐 Web UI: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "🔑 Username: admin" -ForegroundColor Yellow
    Write-Host "🔑 Password: admin" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📊 Check status with: docker-compose ps" -ForegroundColor Gray
    Write-Host "📋 View logs with: docker-compose logs -f airflow-webserver" -ForegroundColor Gray
    Write-Host "🛑 Stop with: docker-compose down" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error starting Docker containers:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Make sure Docker Desktop is running!" -ForegroundColor Yellow
} 