# 测试 Tushare API

$baseUrl = "http://localhost:8000"

Write-Host "=== 测试 POST /api/tushare/daily ===" -ForegroundColor Green

# 测试日线行情
$body = @{
    codes = @("000001", "600000")
    start_date = "20250101"
    end_date = "20250131"
} | ConvertTo-Json

Write-Host "请求体:" -ForegroundColor Cyan
$body | Write-Host

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/tushare/daily" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "`n状态码: $($response.StatusCode)" -ForegroundColor Cyan
    Write-Host "响应内容:" -ForegroundColor Cyan
    $jsonResponse = $response.Content | ConvertFrom-Json
    $jsonResponse | ConvertTo-Json -Depth 10
    
    Write-Host "`n=== 统计 ===" -ForegroundColor Yellow
    Write-Host "数据条数: $($jsonResponse.data.Count)" -ForegroundColor Green
    Write-Host "成功: $($jsonResponse.success_codes.Count) 个" -ForegroundColor Green
    Write-Host "失败: $($jsonResponse.failed_codes.Count) 个" -ForegroundColor $(if ($jsonResponse.failed_codes.Count -gt 0) { "Red" } else { "Green" })
    
    if ($jsonResponse.data.Count -gt 0) {
        Write-Host "`n=== 数据示例 ===" -ForegroundColor Yellow
        $jsonResponse.data[0] | ConvertTo-Json -Depth 5
    }
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "错误详情: $responseBody" -ForegroundColor Yellow
    }
}

Write-Host "`n=== 测试 GET /api/tushare/stock_basic ===" -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/tushare/stock_basic" -Method GET -UseBasicParsing
    Write-Host "状态码: $($response.StatusCode)" -ForegroundColor Cyan
    $jsonResponse = $response.Content | ConvertFrom-Json
    Write-Host "股票数量: $($jsonResponse.data.Count)" -ForegroundColor Green
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

