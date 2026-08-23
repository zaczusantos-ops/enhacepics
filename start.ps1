# ChurchPhoto Pro - Script de Inicialização Rápida
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   ChurchPhoto Pro - Pós-Processamento Fotográfico" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "Python nao encontrado no PATH." -ForegroundColor Red
    exit 1
}

Write-Host "[1/2] Iniciando Servidor FastAPI & Engine Determinística..." -ForegroundColor Green
Write-Host "Acesse o estúdio web em: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Documentação OpenAPI:    http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
