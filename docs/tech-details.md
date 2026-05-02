# WorkBuddy Web Control Bridge — Technical Details

## Problem Statement

The genie extension's `CommandRegistry` class fails to register `chat.sendMessage` and `sendToChat` commands due to variable shadowing in the minified/obfuscated code.

## Solution: Manual Registration

Inject code at the end of `CommandRegistry.activate()`'s `doActivate` function, before `ar` variable goes out of scope:

```javascript
// Extract handler while ar is still the command array
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

## Variable Shadow Analysis

```javascript
class CommandRegistry {
    activate() {
        const ir = new Map();
        const ar = this.commandProvider.get();  // ar = command array
        
        for (const tn of ar) {
            const ar = tn.ids;  // ⚠️ shadow! ar is now ID array
        }
        // ar is shadowed, original command array lost
        // → injection must happen BEFORE this loop
    }
}
```

## Injection Points

### Point 1: Before for-loop

```javascript
// Before
for(const tn of ar)

// After injection
const _chatMsgHandler=ar.find(...);
const _sendToChatHandler=ar.find(...);
for(const tn of ar)
```

### Point 2: After successful registration

```javascript
// Before
this.logger.info("[CommandRegistry] All commands registered successfully")

// After
this.logger.info("[CommandRegistry] All commands registered successfully");
if(_chatMsgHandler){...}
if(_sendToChatHandler){...}
```

## Command ID Mapping

| Internal ID | Registered Command ID |
|-------------|----------------------|
| `chat.sendMessage` | `tencentcloud.codingcopilot.chat.sendMessage` |
| `sendToChat` | `tencentcloud.codingcopilot.sendToChat` |
| `addToChat` | `tencentcloud.codingcopilot.addToChat` (no injection needed) |

## Extension Host Limitations

WorkBuddy is based on VSCode Code 1.77.3. Its Extension Host environment:

- ✅ Has basic event loop (`require('events')`)
- ❌ **No** `setTimeout` / `setImmediate` / `process.nextTick`
- ❌ No Promise-based async scheduling

Using async scheduling causes Extension Host crash. **All injection code must be synchronous.**

## DI Container

genie uses a custom DI container:

```javascript
@Component(Command)      // Register to container
@Autowired               // Inject dependency
@AutowiredProvider(Command)  // Get all instances

ContainerUtil.get(SomeClass)
ContainerUtil.getAllInstances(SomeClass)
```

## Command Parameter Format

```javascript
{
    message: string,
    options: {
        headless: boolean,
        waitForCompletion: boolean,
        timeout: number  // milliseconds
    }
}
```

## Data Flow

```
HTTP POST /execute
    ↓
bridge extension receives request
    ↓
vscode.commands.executeCommand('tencentcloud.codingcopilot.chat.sendMessage', args)
    ↓
CommandRegistry executes handler (calls genie AI)
    ↓
AI processes and returns completion event
    ↓
bridge parses completion.messages
    ↓
HTTP JSON response
```