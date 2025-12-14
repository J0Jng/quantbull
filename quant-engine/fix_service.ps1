# PowerShell 脚本：修复 quant-engine 服务

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Quant Engine 服务修复" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. 检查并停止占用端口的进程
Write-Host "`n[1] 检查占用端口 8003 的进程..." -ForegroundColor Yellow
$connections = Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue

if ($connections) {
    $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $processIds) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  发现进程: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
            Write-Host "  路径: $($process.Path)" -ForegroundColor Gray
            
            # 询问是否停止
            Write-Host "  正在停止进程 $pid..." -ForegroundColor Yellow
            try {
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host "  ✓ 进程已停止" -ForegroundColor Green
                Start-Sleep -Seconds 2
            } catch {
                Write-Host "  ✗ 无法停止进程: $($_.Exception.Message)" -ForegroundColor Red
                Write-Host "  请手动停止进程或重启计算机" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "  ✓ 端口 8003 未被占用" -ForegroundColor Green
}

# 2. 验证端口已释放
Write-Host "`n[2] 验证端口已释放..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
$check = Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue
if ($check) {
    Write-Host "  ⚠ 端口仍被占用，请手动处理" -ForegroundColor Red
} else {
    Write-Host "  ✓ 端口已释放" -ForegroundColor Green
}

# 3. 检查依赖
Write-Host "`n[3] 检查 Python 依赖..." -ForegroundColor Yellow
$required = @("fastapi", "uvicorn", "backtrader", "pandas", "numpy")
$missing = @()

foreach ($pkg in $required) {
    $installed = pip show $pkg 2>$null
    if (-not $installed) {
        $missing += $pkg
        Write-Host "  ✗ $pkg 未安装" -ForegroundColor Red
    } else {
        Write-Host "  ✓ $pkg 已安装" -ForegroundColor Green
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n  缺少依赖，正在安装..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 4. 启动服务
Write-Host "`n[4] 准备启动服务..." -ForegroundColor Yellow
Write-Host "  请在新的终端窗口运行以下命令启动服务:" -ForegroundColor Cyan
Write-Host "  cd $PWD" -ForegroundColor White
Write-Host "  python run.py" -ForegroundColor White
Write-Host "`n  或者直接运行:" -ForegroundColor Cyan
Write-Host "  Start-Process python -ArgumentList 'run.py' -WorkingDirectory '$PWD'" -ForegroundColor White

# 询问是否立即启动
$response = Read-Host "`n是否立即启动服务? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`n  正在启动服务..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "run.py" -WorkingDirectory $PWD -WindowStyle Normal
    Write-Host "  ✓ 服务已在新窗口启动" -ForegroundColor Green
    Write-Host "`n  等待 3 秒后测试服务..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    # 测试服务
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ 服务运行正常!" -ForegroundColor Green
        Write-Host "  服务: $($health.service)" -ForegroundColor Gray
    } catch {
        Write-Host "  ⚠ 服务可能还在启动中，请稍后运行测试脚本" -ForegroundColor Yellow
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  修复完成" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`n下一步:" -ForegroundColor Yellow
Write-Host "  1. 确保服务已启动" -ForegroundColor White
Write-Host "  2. 运行测试: python test_backtest_simple.py" -ForegroundColor White
Write-Host "  3. 查看 API 文档: http://localhost:8003/docs" -ForegroundColor White
Write-Host ""
