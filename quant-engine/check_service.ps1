# PowerShell 脚本：检查 quant-engine 服务状态

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Quant Engine 服务检查" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. 检查端口
Write-Host "`n[1] 检查端口 8003..." -ForegroundColor Yellow
$port = Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue
if ($port) {
    Write-Host "  ✓ 端口 8003 已被占用" -ForegroundColor Green
    Write-Host "  进程 ID: $($port.OwningProcess)" -ForegroundColor Gray
    $process = Get-Process -Id $port.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "  进程名: $($process.ProcessName)" -ForegroundColor Gray
        Write-Host "  路径: $($process.Path)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ 端口 8003 未被占用（服务可能未启动）" -ForegroundColor Red
}

# 2. 检查服务健康状态
Write-Host "`n[2] 检查服务健康状态..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ 服务运行正常" -ForegroundColor Green
    Write-Host "  服务: $($response.service)" -ForegroundColor Gray
    Write-Host "  环境: $($response.env)" -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 502) {
        Write-Host "  ✗ 502 Bad Gateway - 服务可能未正确启动" -ForegroundColor Red
    } elseif ($_.Exception.Response.StatusCode) {
        Write-Host "  ✗ HTTP $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    } else {
        Write-Host "  ✗ 无法连接到服务: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 3. 检查根路径
Write-Host "`n[3] 检查根路径..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8003/" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ 根路径可访问" -ForegroundColor Green
    Write-Host "  服务: $($response.service)" -ForegroundColor Gray
    Write-Host "  版本: $($response.version)" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ 无法访问根路径: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. 建议
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  建议" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not $port) {
    Write-Host "`n服务未运行，请执行:" -ForegroundColor Yellow
    Write-Host "  cd quant-engine" -ForegroundColor White
    Write-Host "  python run.py" -ForegroundColor White
} else {
    Write-Host "`n服务似乎正在运行，如果仍有问题:" -ForegroundColor Yellow
    Write-Host "  1. 检查服务日志" -ForegroundColor White
    Write-Host "  2. 重启服务: 停止当前进程后运行 python run.py" -ForegroundColor White
    Write-Host "  3. 检查依赖: pip install -r requirements.txt" -ForegroundColor White
}

Write-Host ""
