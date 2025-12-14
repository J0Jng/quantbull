# 启动 data-service 服务脚本
# 确保使用虚拟环境的 Python

$venvPython = "..\quantbull\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "使用虚拟环境 Python 启动服务..." -ForegroundColor Green
    & $venvPython -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
} else {
    Write-Host "虚拟环境未找到，使用系统 Python..." -ForegroundColor Yellow
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

