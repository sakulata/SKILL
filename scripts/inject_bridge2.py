"""
WorkBuddy Bridge 注入脚本 v2（恢复+注入双功能）
功能：从备份恢复原始文件，然后执行双注入
- 注入点1：在 for(const tn of ar) 之前（提取 handler）
- 注入点2：在 All commands registered 之后（注册命令）

作者：AI Assistant
日期：2026-04
"""

import os

filepath = r'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\_\resources\app\extensions\genie\out\extension\index.js'
backup = r'C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\resources\app\extensions\genie\out\extension\index.js.bak'

# ===== 恢复原始文件 =====
print('=== 恢复原始文件 ===')
with open(backup, 'r', encoding='utf-8') as f:
    content = f.read()
print(f'从备份加载: {len(content)} 字节')

# ===== 第一处注入：for 循环之前 =====
print('=== 第一处注入 ===')
target1 = 'class CommandRegistry{activate(){const ir=new Map,ar=this.commandProvider.get();this.logger.info(`[CommandRegistry] Total commands to register: ${ar.length}`);for(const tn of ar)'
pos1 = content.find(target1)
if pos1 == -1:
    print('ERROR: Target1 not found!')
    exit(1)
print(f'Target1 位置: {pos1}')

# 在 for(const tn of ar) 之前插入
inject1 = '''
// [Bridge-Inject] 提取 chatHandler 和 sendToChatHandler（在 ar 被 shadow 前）
const _chatMsgHandler=ar.find(c=>{try{const ids=typeof c.id==='string'?[c.id]:c.id;return ids.includes('tencentcloud.codingcopilot.chat.sendMessage')}catch(e){return false}});
const _sendToChatHandler=ar.find(c=>{try{const ids=typeof c.id==='string'?[c.id]:c.id;return ids.includes('tencentcloud.codingcopilot.sendToChat')}catch(e){return false}});
this.logger.info('[Bridge-Inject] Pre-extracted: chatMsg='+!!_chatMsgHandler+', sendToChat='+!!_sendToChatHandler);
'''
insert_pos1 = pos1 + len(target1) - len('for(const tn of ar)')
content = content[:insert_pos1] + inject1 + content[insert_pos1:]
print(f'注入1完成，长度变为: {len(content)}')

# ===== 第二处注入：注册成功后 =====
print('=== 第二处注入 ===')
target2 = 'this.logger.info("[CommandRegistry] All commands registered successfully")'
pos2 = content.find(target2)
if pos2 == -1:
    print('ERROR: Target2 not found!')
    exit(1)
print(f'Target2 位置: {pos2}')

inject2 = ''';
if(_chatMsgHandler){this.logger.info('[Bridge-Inject] Registering chat.sendMessage');ir.set('tencentcloud.codingcopilot.chat.sendMessage',mn.commands.registerCommand('tencentcloud.codingcopilot.chat.sendMessage',(...a)=>_chatMsgHandler.handler(...a)))}
if(_sendToChatHandler){this.logger.info('[Bridge-Inject] Registering sendToChat');ir.set('tencentcloud.codingcopilot.sendToChat',mn.commands.registerCommand('tencentcloud.codingcopilot.sendToChat',(...a)=>_sendToChatHandler.handler(...a)))}'''
insert_pos2 = pos2 + len(target2)
content = content[:insert_pos2] + inject2 + content[insert_pos2:]
print(f'注入2完成，长度变为: {len(content)}')

# ===== 写入文件 =====
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('文件写入成功')

# ===== 验证 =====
with open(filepath, 'r', encoding='utf-8') as f:
    verify = f.read()
idx1 = verify.find('[Bridge-Inject] Pre-extracted')
idx2 = verify.find('[Bridge-Inject] Registering')
print(f'验证 - 注入点1位置: {idx1}')
print(f'验证 - 注入点2位置: {idx2}')
print(f'总长度差值: {len(verify) - 19823520} 字节（原始 19823520）')
print('完成。请重启 WorkBuddy。')