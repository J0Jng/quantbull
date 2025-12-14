# 测试 PostgreSQL 容器连接
Write-Host "测试 PostgreSQL 容器连接..." -ForegroundColor Cyan

# 检查容器是否运行
$containerStatus = docker ps --filter "name=postgres-quantbull" --format "{{.Status}}"
if ($containerStatus) {
    Write-Host "容器状态: $containerStatus" -ForegroundColor Green
} else {
    Write-Host "容器未运行！" -ForegroundColor Red
    exit 1
}

# 测试数据库连接
Write-Host "`n测试数据库连接..." -ForegroundColor Cyan
try {
    $result = docker exec postgres-quantbull psql -U postgres -d quantbull -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "数据库连接成功！" -ForegroundColor Green
        Write-Host $result
    } else {
        Write-Host "数据库连接失败！" -ForegroundColor Red
        Write-Host $result
    }
} catch {
    Write-Host "连接测试出错: $_" -ForegroundColor Red
}

# 测试端口是否可访问
Write-Host "`n测试端口 5432..." -ForegroundColor Cyan
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 5432)
    if ($tcpClient.Connected) {
        Write-Host "端口 5432 可访问！" -ForegroundColor Green
        $tcpClient.Close()
    }
} catch {
    Write-Host "端口 5432 不可访问: $_" -ForegroundColor Yellow
}
