# 财经频道 API 测试脚本
# 测试所有财经频道相关接口

$baseUrl = "http://localhost:8000/api/finance-channel"
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsImV4cCI6MTc2OTAxNjI1OX0.QmSLOOxdrQ4LKnyYJT8uPT0ix-FHr3UKRGQTBuVdJik"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "财经频道 API 测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 测试市场数据
Write-Host "1. 测试市场数据接口..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/market" -Method GET -Headers $headers
    $count = $response.data.items.Count
    Write-Host "   成功! 返回 $count 个指数" -ForegroundColor Green
    if ($count -gt 0) {
        $item = $response.data.items[0]
        Write-Host "   示例: $($item.title) = $($item.value)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试财经日历
Write-Host "2. 测试财经日历接口..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/calendar" -Method GET -Headers $headers
    $count = $response.data.items.Count
    Write-Host "   成功! 返回 $count 个事件" -ForegroundColor Green
    if ($count -gt 0) {
        $item = $response.data.items[0]
        Write-Host "   示例: $($item.title) - $($item.time)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试投资观点
Write-Host "3. 测试投资观点接口..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/ideas" -Method GET -Headers $headers
    $count = $response.data.items.Count
    Write-Host "   成功! 返回 $count 个观点" -ForegroundColor Green
    if ($count -gt 0) {
        $item = $response.data.items[0]
        Write-Host "   示例: $($item.title) - $($item.source)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试政策发布
Write-Host "4. 测试政策发布接口..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/policies" -Method GET -Headers $headers
    $count = $response.data.items.Count
    Write-Host "   成功! 返回 $count 个政策" -ForegroundColor Green
    if ($count -gt 0) {
        $item = $response.data.items[0]
        Write-Host "   示例: $($item.title) - $($item.source)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试综合概览
Write-Host "5. 测试综合概览接口..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/overview" -Method GET -Headers $headers
    Write-Host "   成功! 获取综合数据" -ForegroundColor Green
    Write-Host "   - 市场行情: $($response.data.market.items.Count) 个指数" -ForegroundColor Gray
    Write-Host "   - 财经日历: $($response.data.calendar.items.Count) 个事件" -ForegroundColor Gray
    Write-Host "   - 投资观点: $($response.data.ideas.items.Count) 个观点" -ForegroundColor Gray
    Write-Host "   - 政策发布: $($response.data.policies.items.Count) 个政策" -ForegroundColor Gray
} catch {
    Write-Host "   失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "测试完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
