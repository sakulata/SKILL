# WorkBuddy Web Control Bridge — Debug Guide

## Quick Commands

```powershell
# Check WorkBuddy process
tasklist /FI "IMAGENAME eq WorkBuddy.exe"

# Check port 18080
Test-NetConnection -ComputerName 127.0.0.1 -Port 18080

# Check service status
Invoke-RestMethod -Uri 'http://127.0.0.1:18080/status'

# View logs
$log = Get-ChildItem 'C:\Users\Administrator\AppData\Roaming\WorkBuddy\logs\' -Recurse -Filter 'WorkBuddy.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Select-String -Path $log.FullName -Pattern 'Bridge|chat.sendMessage|CommandRegistry'
```

## Injection Verification

```powershell
# Check file size (original: 19823520 bytes)
$size = (Get-Item 'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js').Length
Write-Output "Current: $size | Diff: $($size - 19823520) bytes"
```

Expected diff: ~737 bytes (inject_bridge.py) or ~1000+ bytes (inject_bridge2.py).

## Log File Locations

```
C:\Users\Administrator\AppData\Roaming\WorkBuddy\logs\
└── YYYYMMDDTHHMMSS\
    └── Claw--3\
        └── exthost\Tencent-Cloud.coding-copilot\WorkBuddy.log
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Diff is negative | Wrong target string | Check `}(ir)},ar.deactivate` exact match |
| Extension Host crash | Used setTimeout | Run `inject_bridge2.py` to restore from backup |
| Port no response | Bridge extension not loaded | Check product.json |
| Command not found | Not registered | Check logs for `[Bridge-Inject]` entries |

## Recovery

Restore original file:

```powershell
copy 'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\resources\app\extensions\genie\out\extension\index.js.bak' 'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js'
```