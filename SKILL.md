# WorkBuddy 网络控制桥接

> **让 WorkBuddy 拥有远程控制能力——通过网页随时随地唤醒 AI 对话**

## 一句话说明

本技能为 WorkBuddy 打通 HTTP 接口，使外部网页或程序可以远程发送指令、触发 AI 对话、获取回答，实现真正的**网络化 AI 控制**。

## 核心能力

- 🌐 **远程唤醒**：通过 HTTP 请求唤醒 WorkBuddy，无需打开软件界面
- 🔌 **标准化 API**：提供 REST 接口，任何支持 HTTP 的平台均可调用
- 🤖 **全自动对话**：发送消息后自动等待 AI 处理完成，无需人工干预
- 🔒 **本地优先**：所有请求仅在本机 18080 端口响应，安全可靠

## 工作原理

```
[你的网页/程序]
    ↓ HTTP POST :18080/execute
[桥接服务] → [VSCode 命令系统] → [genie AI 扩展] → [AI 处理]
    ↓ HTTP JSON 响应
[返回 AI 回答]
```

## 快速开始

### 第一步：安装桥接（一次性操作）

```powershell
python D:\SKILL\scripts\inject_bridge.py
```

### 第二步：重启 WorkBuddy

```powershell
Stop-Process -Name WorkBuddy -Force -ErrorAction SilentlyContinue
Start-Process WorkBuddy.exe
Start-Sleep -Seconds 5
```

### 第三步：发送测试请求

```powershell
$body = @{
    command = "tencentcloud.codingcopilot.chat.sendMessage"
    message = "你好，介绍一下你自己"
    options = @{
        headless = $true
        waitForCompletion = $true
        timeout = 60000
    }
} | ConvertTo-Json -Compress

$r = Invoke-RestMethod -Uri 'http://127.0.0.1:18080/execute' -Method POST -ContentType 'application/json' -Body $body
$r.completion.messages[-1].content
```

## API 文档

### 基础信息

| 项目 | 值 |
|------|-----|
| 协议 | HTTP |
| 端口 | 18080 |
| 地址 | `127.0.0.1:18080` |
| 格式 | JSON |

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/status` | GET | 查询桥接服务运行状态 |
| `/check` | GET | 检查 WorkBuddy 是否在运行 |
| `/execute` | POST | 发送命令给 WorkBuddy |
| `/all-commands` | GET | 获取所有可用命令 |

### 执行命令（核心）

**请求**

```http
POST http://127.0.0.1:18080/execute
Content-Type: application/json

{
  "command": "tencentcloud.codingcopilot.chat.sendMessage",
  "message": "你的问题",
  "options": {
    "headless": true,
    "waitForCompletion": true,
    "timeout": 120000
  }
}
```

**响应**

```json
{
  "id": "session_xxx",
  "completion": {
    "success": true,
    "state": "completed",
    "messages": [
      {
        "role": "assistant",
        "content": "AI 的回答内容"
      }
    ]
  }
}
```

### 查询状态

```http
GET http://127.0.0.1:18080/status
```

```json
{
  "status": "running",
  "port": 18080,
  "workbuddy": true,
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

## 应用场景

### 场景 1：网页控制台

通过自定义网页发送指令到 WorkBuddy，实时显示 AI 回答。

```
用户网页 → http://127.0.0.1:18080/execute → WorkBuddy AI
     ↑                                            ↓
     └───────────── 展示回答 ←────────────────────┘
```

### 场景 2：自动化脚本

在 Python、Shell 中调用 WorkBuddy AI，无需启动 GUI。

```python
import requests

response = requests.post(
    'http://127.0.0.1:18080/execute',
    json={
        'command': 'tencentcloud.codingcopilot.chat.sendMessage',
        'message': '帮我写一个求和函数',
        'options': {'headless': True, 'waitForCompletion': True, 'timeout': 60000}
    }
)

result = response.json()
print(result['completion']['messages'][-1]['content'])
```

### 场景 3：远程唤醒

配合内网穿透工具（如 frp），在任意设备上控制本地 WorkBuddy AI。

## 完整文件结构

```
D:\SKILL\
├── SKILL.md              # 本文件
├── README.md             # 英文简介
├── .gitignore            # Git 忽略配置
├── scripts/              # 脚本目录
│   ├── inject_bridge.py  # 注入脚本（单次注入约 737 字节）
│   ├── inject_bridge2.py # 完整注入（含恢复）版本
│   ├── bridge-service.js # Node.js 独立服务
│   └── test_bridge.ps1   # 测试脚本
└── docs/                 # 文档目录
    ├── tech-details.md   # 技术细节
    └── debug-guide.md    # 调试指南
```

## 常见问题

| 问题 | 解答 |
|------|------|
| 端口 18080 被占用？ | 关闭其他占用程序或修改 `bridge-service.js` 中的 PORT |
| 提示"权限不足"？ | 确保 sakulata 账户有仓库写入权限 |
| 推送超时？ | 检查网络代理设置，确保 443 端口可访问 GitHub |
| 注入后 WorkBuddy 崩溃？ | 运行 `inject_bridge2.py` 从备份恢复 |

## 技术栈

| 组件 | 技术 |
|------|------|
| 注入工具 | Python 3.10+ |
| 桥接服务 | Node.js HTTP Server |
| 测试脚本 | PowerShell |
| AI 对话 | WorkBuddy genie 扩展 |
| 版本控制 | Git + GitHub |

---

**远程控制，一触即达**