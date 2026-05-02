/**
 * WorkBuddy Bridge HTTP 服务
 * 在端口 18080 启动 HTTP 服务，提供 WorkBuddy 状态查询和命令执行接口
 * 
 * 注意：此文件是独立服务，不是 VSCode 扩展。
 * 如需作为 VSCode 扩展运行，需要创建完整的 package.json 和 extension.js
 */

const http = require('http');
const { execSync } = require('child_process');

// 配置
const PORT = 18080;
const WORKBUDDY_PATH = 'C:\\Users\\Administrator\\AppData\\Local\\Programs\\WorkBuddy\\WorkBuddy.exe';

// 检查 WorkBuddy 是否运行
function checkWorkBuddy() {
    try {
        const result = execSync('tasklist /FI "IMAGENAME eq WorkBuddy.exe" /NH', { 
            encoding: 'utf8',
            timeout: 5000
        });
        return result.includes('WorkBuddy.exe');
    } catch {
        return false;
    }
}

// 解析请求体
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// 发送 JSON 响应
function jsonResponse(res, status, data) {
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

// 创建 HTTP 服务器
const server = http.createServer(async (req, res) => {
    // CORS 头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    const url = req.url.split('?')[0];

    try {
        // GET /status - 服务状态
        if (req.method === 'GET' && url === '/status') {
            jsonResponse(res, 200, {
                status: 'running',
                port: PORT,
                workbuddy: checkWorkBuddy(),
                timestamp: new Date().toISOString()
            });
            return;
        }

        // GET /check - WorkBuddy 状态
        if (req.method === 'GET' && url === '/check') {
            const running = checkWorkBuddy();
            jsonResponse(res, 200, {
                workbuddyRunning: running,
                message: running ? 'WorkBuddy is running' : 'WorkBuddy is NOT running'
            });
            return;
        }

        // POST /execute - 执行命令（需要桥接扩展支持）
        if (req.method === 'POST' && url === '/execute') {
            const body = await parseBody(req);
            
            // 此端点需要 workbuddy-bridge VSCode 扩展支持
            // 目前通过 vscode.commands.executeCommand 调用
            jsonResponse(res, 200, {
                error: '需要桥接扩展支持',
                hint: '请确保 WorkBuddy 已启动且桥接扩展已加载'
            });
            return;
        }

        // GET /all-commands - 所有命令
        if (req.method === 'GET' && url === '/all-commands') {
            jsonResponse(res, 200, {
                message: '需要桥接扩展支持才能获取命令列表',
                available: false
            });
            return;
        }

        // 其他路由
        jsonResponse(res, 404, { error: 'Not found', path: url });
    } catch (e) {
        jsonResponse(res, 500, { error: e.message });
    }
});

// 启动服务器
server.listen(PORT, '127.0.0.1', () => {
    console.log(`[Bridge Service] 运行在端口 ${PORT}`);
    console.log(`[Bridge Service] WorkBuddy 状态: ${checkWorkBuddy() ? '运行中' : '未运行'}`);
});

server.on('error', (e) => {
    if (e.code === 'EADDRINUSE') {
        console.error(`错误: 端口 ${PORT} 已被占用`);
        process.exit(1);
    }
});

// 优雅退出
process.on('SIGINT', () => {
    console.log('\n[Bridge Service] 关闭中...');
    server.close(() => process.exit(0));
});