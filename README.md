# WorkBuddy Web Control Bridge

> **Connect your WorkBuddy to the web — remote AI control at your fingertips**

## What It Does

Exposes WorkBuddy's AI capabilities via HTTP API, enabling remote control through any web interface or program.

## Quick Start

```powershell
# 1. Inject (one-time)
python D:\SKILL\scripts\inject_bridge.py

# 2. Restart WorkBuddy
Stop-Process -Name WorkBuddy -Force
Start-Process WorkBuddy.exe

# 3. Send a message
$body = @{
    command = "tencentcloud.codingcopilot.chat.sendMessage"
    message = "Hello"
    options = @{headless=$true; waitForCompletion=$true; timeout=60000}
} | ConvertTo-Json -Compress

Invoke-RestMethod -Uri 'http://127.0.0.1:18080/execute' -Method POST -ContentType 'application/json' -Body $body
```

## API

- `GET /status` — Service status
- `POST /execute` — Send command

## Files

```
D:\SKILL\
├── SKILL.md              # Main documentation
├── README.md             # This file
├── scripts/
│   ├── inject_bridge.py  # Injection script
│   ├── inject_bridge2.py  # Full version with restore
│   ├── bridge-service.js # HTTP service
│   └── test_bridge.ps1   # Test script
└── docs/
    ├── tech-details.md   # Technical details
    └── debug-guide.md     # Debug guide
```

## License

MIT