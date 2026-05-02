# workbuddy-bridge 技能

## 概述

本技能用于将 WorkBuddy 的 genie 扩展（腾讯 AI 助手）中的 `chat.sendMessage` 命令通过桥接扩展 HTTP API 暴露出来，供外部程序调用，实现全自动 AI 对话。

## 工作流程

```
注入 genie index.js（注册缺失命令）
    ↓
桥接扩展 HTTP 服务启动（端口 18080）
    ↓
外部请求 → /execute 端点
    ↓
调用 VSCode 命令 → genie 扩展处理
    ↓
返回 AI 回答
```

## 环境要求

- Windows x64
- Python 3.10+
- 已安装 WorkBuddy（路径：`C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\`）
- Git（用于上传）

## 一、注入命令（注入 genie 扩展）

### 第一步：注入

```powershell
C:\Python314\python.exe C:\Users\Administrator\.qclaw\workspace\inject_bridge.py
```

**预期输出**：`Diff: 737 bytes (expected ~737)`

### 第二步：重启 WorkBuddy

```powershell
Stop-Process -Name WorkBuddy -Force -ErrorAction SilentlyContinue; Start-Process WorkBuddy.exe; Start-Sleep -Seconds 5
```

### 第三步：验证注入

```powershell
# 检查端口
Test-NetConnection -ComputerName 127.0.0.1 -Port 18080

# 测试命令
$body = @{
    command = "tencentcloud.codingcopilot.chat.sendMessage"
    message = "1+1等于几？"
    options = @{
        headless = $true
        waitForCompletion = $true
        timeout = 120000
    }
} | ConvertTo-Json -Compress

$r = Invoke-RestMethod -Uri 'http://127.0.0.1:18080/execute' -Method POST -ContentType 'application/json' -Body $body -TimeoutSec 130
$r.completion.messages[-1].content
```

## 二、可用命令

| 命令 ID | 功能 | 参数 |
|--------|------|------|
| `tencentcloud.codingcopilot.chat.sendMessage` | 全自动发送，返回 AI 回答 | message + options |
| `tencentcloud.codingcopilot.sendToChat` | 新建对话+发送 | message + options |

## 三、API 端点

桥接扩展运行在端口 **18080**：

| 端点 | 方法 | 功能 |
|------|------|------|
| `/status` | GET | 服务状态 |
| `/check` | GET | 检查 WorkBuddy 运行状态 |
| `/execute` | POST | 执行 VSCode 命令 |
| `/all-commands` | GET | 所有命令列表 |
| `/commands` | GET | 过滤命令列表 |

### /execute 请求格式

```json
POST http://127.0.0.1:18080/execute
Content-Type: application/json

{
  "command": "tencentcloud.codingcopilot.chat.sendMessage",
  "message": "用户消息",
  "options": {
    "headless": true,
    "waitForCompletion": true,
    "timeout": 120000
  }
}
```

### /execute 响应格式

```json
{
  "id": "session_id",
  "message": { "content": "用户消息" },
  "state": { "agentStatus": "running|completed" },
  "completion": {
    "success": true,
    "state": "completed",
    "messages": [
      { "role": "assistant", "content": "{\"text\":\"AI回答\"}" }
    ]
  }
}
```

## 四、重置（恢复原始状态）

如需恢复 genie index.js 到原始状态，运行：

```powershell
C:\Python314\python.exe D:\SKILL\scripts\inject_bridge2.py
```

此脚本会从 WorkBuddy 自带的 `resources\app\extensions\genie\out\extension\index.js.bak` 备份文件恢复。

## 五、文件位置

| 文件 | 路径 |
|------|------|
| genie index.js | `C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js` |
| product.json | `C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\product.json` |
| 原始备份 | `C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\resources\app\extensions\genie\out\extension\index.js.bak` |

## 六、调试

```powershell
# 查看日志文件
$logFile = Get-ChildItem 'C:\Users\Administrator\AppData\Roaming\WorkBuddy\logs\' -Recurse -Filter 'WorkBuddy.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Select-String -Path $logFile.FullName -Pattern 'Bridge|chat.sendMessage'

# 检查命令是否注册
Invoke-WebRequest -Uri 'http://127.0.0.1:18080/all-commands' | ConvertFrom-Json

# 检查 WorkBuddy 状态
Invoke-WebRequest -Uri 'http://127.0.0.1:18080/check' | ConvertFrom-Json
```

## 七、常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Diff 为负数 | 目标字符串位置不对 | 检查 `}(ir)},ar.deactivate` 是否精确匹配 |
| 端口无响应 | bridge 扩展未加载 | 检查 product.json 是否添加了桥接扩展 |
| 超时 | AI 处理时间过长 | 增加 timeout 参数，最大 300000ms |
| Extension Host 崩溃 | 使用了 setTimeout | 注入代码必须同步执行，不能用 setTimeout |

## 八、架构图

```
┌─────────────────────────────────────────────┐
│  外部程序 (Python/Curl/API)                  │
└──────────────┬──────────────────────────────┘
               │ HTTP POST :18080/execute
               ▼
┌──────────────────────────────────────────────┐
│  bridge 扩展 (workbuddy-bridge)              │
│  - HTTP Server (Node.js)                    │
│  - 注册 VSCode 命令                          │
└──────────┬───────────────────────────────────┘
            │ VSCode 命令调用
            ▼
┌──────────────────────────────────────────────┐
│  genie 扩展 (注入后)                         │
│  - CommandRegistry.activate()                │
│  - chat.sendMessage 命令                     │
│  - AI 模型调用                               │
└──────────────────────────────────────────────┘
```