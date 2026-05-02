"""
WorkBuddy Bridge 注入脚本
功能：向 genie 扩展的 index.js 注入代码，注册缺失的 chat.sendMessage 命令

注入点：}(ir)},ar.deactivate=function
注入位置：CommandRegistry.activate() 末尾，在 doActivate 函数结束前

注意：WorkBuddy 扩展运行在 VSCode 的 Extension Host 环境，
Extension Host 没有 Node.js 事件循环，不支持 setTimeout/IIFE 延迟执行，
因此注入代码必须同步立即执行。
"""

import os

filepath = r'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js'

# 检查文件
if not os.path.exists(filepath):
    print(f'ERROR: 文件不存在 {filepath}')
    exit(1)

with open(filepath, 'rb') as f:
    content = f.read()

print(f'Original length: {len(content)}')

# 查找注入点：doActivate 函数末尾，ar.deactivate 之前
# 在 IIFE (function(ir,ar){...})(ir,ar) 之后、}ir)},ar.deactivate 之前
target = b'}(ir)},ar.deactivate=function'
pos = content.find(target)

if pos == -1:
    print('Target not found! 尝试其他位置...')
    # 备选注入点
    alt1 = b'}(ir)},ar.deactivate'
    pos = content.find(alt1)
    if pos != -1:
        target = alt1
        print(f'Found alt target at {pos}')
    else:
        print('ERROR: 无法找到注入点')
        exit(1)

print(f'Target found at: {pos}')

# 注入的代码：
# 在 IIFE 末尾 (}).之前插入我们的代码
# 这样可以在 ar 变量还在作用域时执行查找并注册命令
inject_body = b'try{var _cmd=ar.find(function(c){try{var i="string"==typeof c.id?[c.id]:c.id;return i.indexOf("chat.sendMessage")>-1}catch(e){return false}});if(_cmd){mn.commands.registerCommand("tencentcloud.codingcopilot.chat.sendMessage",function(m,o){return _cmd.handler(m,o)});mn.commands.registerCommand("tencentcloud.codingcopilot.sendToChat",function(m,o){return _cmd.handler(m,o)})}}catch(e){console.error("[Bridge-Inject]",e)}'
inject = b'(function(ir,ar){' + inject_body + b'})(ir,ar);'

# 在 target 末尾的 } 之前插入，替换为 }; inject_code }
# 找到 target 中的 } 位置，在 } 之前插入
# target = }(ir)},ar.deactivate=function
# 我们在第一个 } 之前插入，即在 }( 之前

# 找到 target 中第一个 } 的位置
first_brace = target.find(b'}')
if first_brace == -1:
    print('ERROR: cannot find brace')
    exit(1)

# 在第一个 } 之前插入 inject
insert_pos = pos + first_brace
new_content = content[:insert_pos] + inject + content[insert_pos:]

print(f'Inject ends with: {repr(inject[-20:])}')
print(f'Diff: {len(new_content) - len(content)} bytes')

if len(new_content) - len(content) < 500 or len(new_content) - len(content) > 1000:
    print('WARNING: 差值异常，请检查注入点是否正确')

with open(filepath, 'wb') as f:
    f.write(new_content)
print('Done. 请重启 WorkBuddy 使注入生效。')