# WorkBuddy Bridge

通过注入 genie 扩展，手动注册 `chat.sendMessage` 命令，实现全自动 AI 对话的桥接技能。

## 功能

- 向 genie 扩展注入代码，注册缺失的 VSCode 命令
- 提供 HTTP API（端口 18080）供外部调用
- 支持全自动发送消息并获取 AI 回答

## 快速开始

### 1. 注入命令

```powershell
python scripts/inject_bridge.py
```

### 2. 重启 WorkBuddy

```powershell
Stop-Process -Name WorkBuddy -Force; Start-Process WorkBuddy.exe; Start-Sleep -Seconds 5
```

### 3. 测试

```powershell
powershell scripts/test_bridge.ps1
```

## 文件说明

```
SKILL/                    # 技能根目录
├── SKILL.md              # 主技能文件
├── README.md             # 本文件
├── .gitignore            # Git 忽略配置
├── scripts/              # 脚本目录
│   ├── inject_bridge.py # 注入脚本（单点注入，~737字节）
│   ├── inject_bridge2.py# 注入脚本（双点注入+恢复）
│   ├── bridge-service.js# 独立 HTTP 服务（Node.js）
│   └── test_bridge.ps1  # 测试脚本
└── docs/                # 文档目录
    ├── tech-details.md  # 技术细节
    └── debug-guide.md   # 调试指南
```

## 技术栈

- Python 3.10+（注入脚本）
- Node.js（HTTP 服务）
- PowerShell（测试脚本）
- VSCode Extension API（命令调用）

## License

MIT