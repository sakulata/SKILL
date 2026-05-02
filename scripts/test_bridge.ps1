# WorkBuddy Bridge 测试脚本
# 功能：轮询检查 18080 端口是否就绪

for ($i = 1; $i -le 6; $i++) {
    Start-Sleep -Seconds 10
    try {
        $r = Invoke-RestMethod -Uri 'http://127.0.0.1:18080/status' -ErrorAction Stop
        Write-Output "OK: $($r | ConvertTo-Json)"
        break
    } catch {
        Write-Output "尝试 $i : 端口未就绪"
    }
}

# 测试完整命令调用
Write-Output "`n=== 测试 chat.sendMessage ==="
$body = @{
    command = "tencentcloud.codingcopilot.chat.sendMessage"
    message = "Hello"
    options = @{
        headless = $true
        waitForCompletion = $true
        timeout = 60000
    }
} | ConvertTo-Json -Compress

try {
    $r = Invoke-RestMethod -Uri 'http://127.0.0.1:18080/execute' -Method POST -ContentType 'application/json' -Body $body -TimeoutSec 70
    Write-Output "Success: $($r | ConvertTo-Json -Depth 3)"
} catch {
    Write-Output "失败: $_"
}