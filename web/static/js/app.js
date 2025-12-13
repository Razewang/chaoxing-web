// 全局变量
let socket;
let terminal;
let isProgramRunning = false;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeTerminal();
    loadConfig();
    setupEventListeners();
});

// 初始化Socket连接
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('WebSocket连接成功');
        updateStatus();
    });
    
    socket.on('disconnect', function() {
        console.log('WebSocket连接断开');
    });
    
    socket.on('status', function(data) {
        updateProgramStatus(data.running);
    });
    
    socket.on('output', function(data) {
        appendToTerminal(data.data);
    });
}

// 初始化终端
function initializeTerminal() {
    const terminalElement = document.getElementById('terminal');
    
    // 使用自定义终端实现而不是xterm.js，以便更好地控制输入输出
    terminalElement.innerHTML = '<div id="terminal-output" class="terminal-output"></div>';
}

// 设置事件监听器
function setupEventListeners() {
    // 配置表单提交
    document.getElementById('config-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveConfig();
    });
    
    // 启动按钮
    document.getElementById('start-btn').addEventListener('click', startProgram);
    
    // 停止按钮
    document.getElementById('stop-btn').addEventListener('click', stopProgram);
    
    // 清空按钮
    document.getElementById('clear-btn').addEventListener('click', clearTerminal);
    
    // 发送按钮
    document.getElementById('send-btn').addEventListener('click', sendInput);
    
    // 终端输入框回车事件
    document.getElementById('terminal-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendInput();
        }
    });
    
    // 快捷操作按钮
    document.querySelectorAll('.quick-action').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            handleQuickAction(action);
        });
    });
}

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // 填充表单
        if (config.common) {
            document.getElementById('username').value = config.common.username || '';
            document.getElementById('password').value = config.common.password || '';
            document.getElementById('course_list').value = config.common.course_list || '';
            document.getElementById('speed').value = config.common.speed || '2';
            document.getElementById('notopen_action').value = config.common.notopen_action || 'continue';
        }
        
        if (config.tiku) {
            document.getElementById('tiku_provider').value = config.tiku.provider || 'TikuYanxi';
            document.getElementById('tiku_submit').value = config.tiku.submit || 'false';
            document.getElementById('tiku_tokens').value = config.tiku.tokens || '';
        }
        
        if (config.notification) {
            document.getElementById('notification_provider').value = config.notification.provider || '';
            document.getElementById('notification_url').value = config.notification.url || '';
        }
    } catch (error) {
        console.error('加载配置失败:', error);
        showToast('加载配置失败', 'danger');
    }
}

// 保存配置
async function saveConfig() {
    const config = {
        common: {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            course_list: document.getElementById('course_list').value,
            speed: document.getElementById('speed').value,
            notopen_action: document.getElementById('notopen_action').value
        },
        tiku: {
            provider: document.getElementById('tiku_provider').value,
            submit: document.getElementById('tiku_submit').value,
            tokens: document.getElementById('tiku_tokens').value
        },
        notification: {
            provider: document.getElementById('notification_provider').value,
            url: document.getElementById('notification_url').value
        }
    };
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('配置保存成功', 'success');
        } else {
            showToast('配置保存失败: ' + (result.error || '未知错误'), 'danger');
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        showToast('保存配置失败', 'danger');
    }
}

// 启动程序
async function startProgram() {
    try {
        const response = await fetch('/api/start', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateProgramStatus(true);
            showToast('程序启动成功', 'success');
        } else {
            showToast('启动失败: ' + (result.error || '未知错误'), 'danger');
        }
    } catch (error) {
        console.error('启动程序失败:', error);
        showToast('启动程序失败', 'danger');
    }
}

// 停止程序
async function stopProgram() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateProgramStatus(false);
            showToast('程序已停止', 'info');
        } else {
            showToast('停止失败: ' + (result.error || '未知错误'), 'danger');
        }
    } catch (error) {
        console.error('停止程序失败:', error);
        showToast('停止程序失败', 'danger');
    }
}

// 更新程序状态
function updateProgramStatus(running) {
    isProgramRunning = running;
    
    const statusIndicator = document.getElementById('status-indicator');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const terminalInput = document.getElementById('terminal-input');
    const sendBtn = document.getElementById('send-btn');
    
    if (running) {
        statusIndicator.innerHTML = '<i class="fas fa-circle text-success"></i> 运行中';
        startBtn.disabled = true;
        stopBtn.disabled = false;
        terminalInput.disabled = false;
        sendBtn.disabled = false;
    } else {
        statusIndicator.innerHTML = '<i class="fas fa-circle text-danger"></i> 未运行';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        terminalInput.disabled = true;
        sendBtn.disabled = true;
    }
}

// 更新状态
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        updateProgramStatus(status.running);
        
        // 加载历史输出
        if (status.output && status.output.length > 0) {
            const outputElement = document.getElementById('terminal-output');
            outputElement.innerHTML = status.output.map(line => {
                return `<div>${escapeHtml(line)}</div>`;
            }).join('');
            scrollToBottom();
        }
    } catch (error) {
        console.error('获取状态失败:', error);
    }
}

// 添加输出到终端
function appendToTerminal(data) {
    const outputElement = document.getElementById('terminal-output');
    const line = document.createElement('div');
    line.textContent = data;
    
    // 根据内容添加样式类
    if (data.includes('[TRACE]')) {
        line.className = 'log-trace';
    } else if (data.includes('[DEBUG]')) {
        line.className = 'log-debug';
    } else if (data.includes('[INFO]')) {
        line.className = 'log-info';
    } else if (data.includes('[WARNING]')) {
        line.className = 'log-warning';
    } else if (data.includes('[ERROR]')) {
        line.className = 'log-error';
    }
    
    outputElement.appendChild(line);
    scrollToBottom();
}

// 清空终端
function clearTerminal() {
    document.getElementById('terminal-output').innerHTML = '';
}

// 发送输入
async function sendInput() {
    const input = document.getElementById('terminal-input');
    const text = input.value.trim();
    
    if (text && isProgramRunning) {
        try {
            const response = await fetch('/api/send-input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input: text })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 显示输入的命令
                appendToTerminal(`> ${text}`);
                input.value = '';
            } else {
                showToast('发送失败: ' + (result.error || '未知错误'), 'danger');
            }
        } catch (error) {
            console.error('发送输入失败:', error);
            showToast('发送输入失败', 'danger');
        }
    }
}

// 处理快捷操作
function handleQuickAction(action) {
    const actions = {
        'login': '1',
        'courses': '2',
        'progress': '3',
        'status': '4'
    };
    
    if (actions[action] && isProgramRunning) {
        document.getElementById('terminal-input').value = actions[action];
        sendInput();
    } else if (!isProgramRunning) {
        showToast('请先启动程序', 'warning');
    }
}

// 滚动到底部
function scrollToBottom() {
    const terminal = document.getElementById('terminal');
    terminal.scrollTop = terminal.scrollHeight;
}

// HTML转义
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// 显示提示信息
function showToast(message, type = 'info') {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);
    
    // 3秒后自动移除
    setTimeout(() => {
        toastContainer.remove();
    }, 3000);
    
    // 点击关闭按钮
    toast.querySelector('.btn-close').addEventListener('click', () => {
        toastContainer.remove();
    });
}