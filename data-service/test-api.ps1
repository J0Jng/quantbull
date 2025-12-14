# 测试 data-service API

$baseUrl = "http://localhost:8000"

Write-Host "=== 测试 GET /health ===" -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -UseBasicParsing
    Write-Host "状态码: $($response.StatusCode)" -ForegroundColor Cyan
    Write-Host "响应内容:" -ForegroundColor Cyan
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
}

Write-Host "`n=== 测试 POST /api/data/clean ===" -ForegroundColor Green
$body = @{
    source = "ec"
    content = "Sample text"
    tags = @("NEWS", "STOCK")
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/data/clean" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "状态码: $($response.StatusCode)" -ForegroundColor Cyan
    Write-Host "响应内容:" -ForegroundColor Cyan
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
} catch {
    Write-Host "错误: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "错误详情: $responseBody" -ForegroundColor Yellow
    }
}

