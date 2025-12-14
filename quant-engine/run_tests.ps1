# Quant Engine 测试运行脚本 (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quant Engine 测试套件" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否安装了 pytest
Write-Host "检查依赖..." -ForegroundColor Yellow
try {
    $pytestVersion = python -m pytest --version 2>&1
    Write-Host "✓ pytest 已安装" -ForegroundColor Green
} catch {
    Write-Host "✗ pytest 未安装，正在安装..." -ForegroundColor Red
    pip install pytest pytest-asyncio
}

Write-Host ""
Write-Host "运行测试..." -ForegroundColor Yellow
Write-Host ""

# 运行测试
python -m pytest tests/ -v --tb=short

# 检查测试结果
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ 所有测试通过！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ 部分测试失败" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit $LASTEXITCODE
}
