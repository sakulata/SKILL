# WorkBuddy Bridge 技术细节

## 核心问题

genie 扩展的 `CommandRegistry` 类在注册命令时，由于混淆代码中变量 shadow 问题，
导致 `chat.sendMessage` 和 `sendToChat` 命令无法正确注册到 VSCode 命令系统。

## 解决方案：手动注册

在 `CommandRegistry.activate()` 方法的 `doActivate` 函数末尾，在 `ar` 变量被清理前，
手动注册缺失的命令：

```javascript
// 在 IIFE 内部执行，此时 ar 仍然是命令数组
const _cmd = ar.find(c => {
    try {
        const ids = typeof c.id === 'string' ? [c.id] : c.id;
        return ids.indexOf('chat.sendMessage') > -1;
    } catch(e) { return false; }
});

if (_cmd) {
    mn.commands.registerCommand(
        'tencentcloud.codingcopilot.chat.sendMessage',
        (...args) => _cmd.handler(...args)
    );
}
```

## 关键变量分析

```javascript
class CommandRegistry {
    activate() {
        // ar 是命令数组（来自 this.commandProvider.get()）
        const ir = new Map();
        const ar = this.commandProvider.get();
        
        this.logger.info(`[CommandRegistry] Total commands: ${ar.length}`);
        
        for (const tn of ar) {
            // ⚠️ 在循环内，ar 被 shadow 成 ID 数组
            // 循环结束后 ar 不再是命令数组
            const ar = tn.ids; // shadow！
        }
        
        // 此时 ar 已被 shadow，原命令数组丢失
        // 所以注入必须在 for 循环之前执行
    }
}
```

## 注入点分析

### 注入点 1：for 循环之前

```javascript
// 原代码
for(const tn of ar)

// 注入后
const _chatMsgHandler=ar.find(...);
const _sendToChatHandler=ar.find(...);
for(const tn of ar)
```

### 注入点 2：注册成功日志之后

```javascript
// 原代码
this.logger.info("[CommandRegistry] All commands registered successfully")

// 注入后
this.logger.info("[CommandRegistry] All commands registered successfully");
if(_chatMsgHandler){...}
if(_sendToChatHandler){...}
```

## 命令 ID 映射

| 内部 ID | 注册后的命令 ID |
|---------|----------------|
| `chat.sendMessage` | `tencentcloud.codingcopilot.chat.sendMessage` |
| `sendToChat` | `tencentcloud.codingcopilot.sendToChat` |
| `addToChat` | `tencentcloud.codingcopilot.addToChat`（无需注入，可用） |

## 注入差值

- inject_bridge.py（单点注入）：约 737 字节
- inject_bridge2.py（双点注入）：约 1000+ 字节

## 扩展 Host 崩溃原因

WorkBuddy 基于 VSCode Code 1.77.3，其 Extension Host 是修改过的 Node.js 环境：
- 有事件循环基础（require('events')）
- **不支持** `setTimeout` / `setImmediate` / `process.nextTick`
- 不支持 Promise 异步延迟

任何使用异步调度的代码都会导致 Extension Host 进程崩溃。

## DI 容器机制

genie 扩展使用自定义 DI 容器：

```javascript
// 装饰器
@Component(Command)      // 注册到容器
@Autowired               // 注入依赖
@AutowiredProvider(Command)  // 获取所有 Command 实例

// 获取实例
ContainerUtil.get(SomeClass)
ContainerUtil.getAllInstances(SomeClass)
```

## 命令参数格式

```javascript
{
    message: string,          // 用户消息
    options: {
        headless: boolean,     // 无 UI 模式
        waitForCompletion: boolean,  // 等待 AI 完成
        timeout: number        // 超时毫秒
    }
}
```

## 返回数据流

```
HTTP POST /execute
    ↓
bridge 扩展接收请求
    ↓
vscode.commands.executeCommand('tencentcloud.codingcopilot.chat.sendMessage', args)
    ↓
CommandRegistry 执行 handler（调用 genie AI）
    ↓
AI 处理并返回 completion 事件
    ↓
bridge 解析 completion.messages
    ↓
HTTP 响应 JSON
```