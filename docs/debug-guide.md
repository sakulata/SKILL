# WorkBuddy Bridge 调试指南

## 调试命令速查

```powershell
# 1. 检查 WorkBuddy 进程
tasklist /FI "IMAGENAME eq WorkBuddy.exe"

# 2. 检查端口
Test-NetConnection -ComputerName 127.0.0.1 -Port 18080

# 3. 检查服务状态
Invoke-RestMethod -Uri 'http://127.0.0.1:18080/status'

# 4. 检查 WorkBuddy 状态
Invoke-RestMethod -Uri 'http://127.0.0.1:18080/check'

# 5. 获取所有命令
Invoke-RestMethod -Uri 'http://127.0.0.1:18080/all-commands'

# 6. 查看日志
$log = Get-ChildItem 'C:\Users\Administrator\AppData\Roaming\WorkBuddy\logs\' -Recurse -Filter 'WorkBuddy.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Select-String -Path $log.FullName -Pattern 'Bridge|chat.sendMessage|CommandRegistry' | Select-Object -First 50
```

## 注入验证步骤

### 第 1 步：检查文件大小

```powershell
# 原始大小约 19823520 字节
$size = (Get-Item 'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js').Length
Write-Output "当前大小: $size"
Write-Output "差值: $($size - 19823520)"
```

差值应为 ~737 字节（inject_bridge.py）或 ~1000+ 字节（inject_bridge2.py）。

### 第 2 步：搜索注入标记

```powershell
Select-String -Path 'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js' -Pattern 'Bridge-Inject' -Encoding utf8
```

应找到 `[Bridge-Inject]` 日志输出语句。

### 第 3 步：重启后检查日志

重启 WorkBuddy 后，检查最新日志文件是否包含：
```
[Bridge-Inject] Pre-extracted: chatMsg=true, sendToChat=true
[Bridge-Inject] Registering chat.sendMessage
[Bridge-Inject] Registering sendToChat
```

## 常见问题排查

### 问题 1：Diff 为负数

**原因**：注入点字符串不匹配  
**解决**：
1. 恢复原始文件：`python inject_bridge2.py`（先恢复）
2. 用十六进制编辑器检查目标字符串实际内容
3. 修改脚本中的 target 变量

### 问题 2：Extension Host 崩溃

**原因**：注入代码使用了 setTimeout 或异步模式  
**解决**：
1. 立即恢复：`copy resources\app\extensions\genie\out\extension\index.js.bak _\resources\app\extensions\genie\out\extension\index.js`
2. 改用同步注入代码

### 问题 3：端口无响应

**排查步骤**：
1. WorkBuddy 是否运行？→ `tasklist /FI "IMAGENAME eq WorkBuddy.exe"`
2. bridge 扩展是否加载？→ 检查 product.json
3. 查看日志是否有加载失败信息

### 问题 4：命令未找到

**排查步骤**：
1. 检查命令是否在 all-commands 列表中
2. 查看日志是否有注册失败信息
3. 手动触发一次 Chat 发送，让命令初始化

## 日志文件位置

```
C:\Users\Administrator\AppData\Roaming\WorkBuddy\logs\
└── YYYYMMDDTHHMMSS\
    └── Claw--3\
        └── exthost\Tencent-Cloud.coding-copilot\WorkBuddy.log
```

日志文件名格式可能因版本而异，用 `*.log` 通配符搜索。

## 恢复原始文件

如需完全恢复 genie index.js：

```powershell
copy 'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\resources\app\extensions\genie\out\extension\index.js.bak' 'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js'
```

## 测试流程

```
1. 注入代码        → python inject_bridge.py
2. 重启 WorkBuddy  → Stop-Process WorkBuddy; Start-Process
3. 等待 10 秒      → Start-Sleep 10
4. 检查端口        → Test-NetConnection -Port 18080
5. 测试命令        → powershell test_bridge.ps1
6. 查看日志        → 日志文件中搜索 Bridge-Inject
```