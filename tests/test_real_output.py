#!/usr/bin/env python3
"""
学习通助手 Web界面 - 测试真实输出
"""

import os
import sys
import subprocess
import threading
import time
import json
import http.server
import socketserver
from urllib.parse import parse_qs

# 全局变量
chaoxing_process = None
output_lines = []
is_running = False
output_lock = threading.Lock()

def start_chaoxing():
    """启动学习通脚本"""
    global chaoxing_process, is_running, output_lines
    
    if is_running:
        return False
    
    try:
        # 清空输出
        with output_lock:
            output_lines = []
            output_lines.append("正在启动学习通脚本...")
        
        # 启动进程
        chaoxing_process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        is_running = True
        
        # 启动读取线程
        thread = threading.Thread(target=read_output)
        thread.daemon = True
        thread.start()
        
        return True
    except Exception as e:
        with output_lock:
            output_lines.append(f"启动失败: {str(e)}")
        return False

def read_output():
    """读取进程输出"""
    global chaoxing_process, is_running
    
    try:
        while is_running and chaoxing_process:
            line = chaoxing_process.stdout.readline()
            if line:
                line = line.rstrip()
                with output_lock:
                    output_lines.append(line)
                    # 限制行数
                    if len(output_lines) > 500:
                        output_lines = output_lines[-500:]
            else:
                # 进程结束
                break
        
        if chaoxing_process:
            return_code = chaoxing_process.poll()
            if return_code is not None:
                with output_lock:
                    output_lines.append(f"\n程序已退出，返回码: {return_code}")
        
    except Exception as e:
        with output_lock:
            output_lines.append(f"读取输出错误: {str(e)}")
    finally:
        is_running = False
        chaoxing_process = None

def stop_chaoxing():
    """停止学习通脚本"""
    global chaoxing_process, is_running
    
    is_running = False
    
    if chaoxing_process:
        try:
            chaoxing_process.terminate()
            time.sleep(0.5)
            if chaoxing_process.poll() is None:
                chaoxing_process.kill()
            chaoxing_process.stdin.close()
        except:
            pass
        chaoxing_process = None

def send_input(text):
    """发送输入到进程"""
    global chaoxing_process
    
    if chaoxing_process and chaoxing_process.stdin and not chaoxing_process.stdin.closed:
        try:
            chaoxing_process.stdin.write(text + '\n')
            chaoxing_process.stdin.flush()
            return True
        except:
            return False
    return False

def get_output():
    """获取所有输出"""
    with output_lock:
        return '\n'.join(output_lines)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_html()
        elif self.path == '/api/output':
            self.send_output()
        elif self.path == '/api/status':
            self.send_status()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/start':
            self.handle_start()
        elif self.path == '/api/stop':
            self.handle_stop()
        elif self.path == '/api/input':
            self.handle_input()
        else:
            self.send_error(404)
    
    def send_html(self):
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>学习通助手 - 真实输出测试</title>
    <style>
        body { font-family: monospace; background: #000; color: #0f0; margin: 0; padding: 20px; }
        #output { background: #111; padding: 20px; border-radius: 5px; height: 500px; overflow-y: auto; white-space: pre-wrap; }
        #input { background: #222; color: #0f0; border: 1px solid #0f0; padding: 10px; width: 80%; margin: 10px 0; }
        button { background: #0f0; color: #000; border: none; padding: 10px 20px; margin: 5px; cursor: pointer; }
        button:disabled { background: #666; color: #999; cursor: not-allowed; }
        .status { margin: 10px 0; }
        .running { color: #0f0; }
        .stopped { color: #f00; }
    </style>
</head>
<body>
    <h1>学习通助手 - 真实输出测试</h1>
    
    <div class="status">
        状态: <span id="status" class="stopped">未运行</span>
    </div>
    
    <div>
        <button id="startBtn" onclick="start()">启动程序</button>
        <button id="stopBtn" onclick="stop()" disabled>停止程序</button>
        <button onclick="clearOutput()">清空输出</button>
    </div>
    
    <div id="output">等待启动...</div>
    
    <div>
        <input type="text" id="input" placeholder="输入命令..." disabled>
        <button id="sendBtn" onclick="send()" disabled>发送</button>
    </div>
    
    <div style="margin-top: 20px;">
        <h3>快速操作：</h3>
        <button onclick="quickSend('1')">1. 登录</button>
        <button onclick="quickSend('2')">2. 查看课程</button>
        <button onclick="quickSend('3')">3. 查看进度</button>
        <button onclick="showFull()">4. 查看完整输出</button>
    </div>
    
    <script>
        let updateInterval;
        
        function startUpdate() {
            updateInterval = setInterval(updateOutput, 1000);
        }
        
        function updateOutput() {
            fetch('/api/output')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('output').textContent = data.output;
                    document.getElementById('output').scrollTop = 999999;
                });
            
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    const status = document.getElementById('status');
                    const startBtn = document.getElementById('startBtn');
                    const stopBtn = document.getElementById('stopBtn');
                    const input = document.getElementById('input');
                    const sendBtn = document.getElementById('sendBtn');
                    
                    if (data.running) {
                        status.textContent = '运行中';
                        status.className = 'running';
                        startBtn.disabled = true;
                        stopBtn.disabled = false;
                        input.disabled = false;
                        sendBtn.disabled = false;
                    } else {
                        status.textContent = '未运行';
                        status.className = 'stopped';
                        startBtn.disabled = false;
                        stopBtn.disabled = true;
                        input.disabled = true;
                        sendBtn.disabled = true;
                    }
                });
        }
        
        async function start() {
            const response = await fetch('/api/start', {method: 'POST'});
            const result = await response.json();
            if (result.success) {
                console.log('启动成功');
            } else {
                alert('启动失败');
            }
        }
        
        async function stop() {
            const response = await fetch('/api/stop', {method: 'POST'});
            const result = await response.json();
            console.log('停止成功');
        }
        
        async function send() {
            const input = document.getElementById('input');
            const text = input.value.trim();
            if (!text) return;
            
            const response = await fetch('/api/input', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'input=' + encodeURIComponent(text)
            });
            
            input.value = '';
        }
        
        function quickSend(text) {
            document.getElementById('input').value = text;
            send();
        }
        
        function clearOutput() {
            document.getElementById('output').textContent = '';
        }
        
        function showFull() {
            const output = document.getElementById('output').textContent;
            const win = window.open('', '_blank');
            win.document.write('<pre style="background: #000; color: #0f0; padding: 20px;">' + output + '</pre>');
        }
        
        // 开始更新
        startUpdate();
        
        // 回车发送
        document.getElementById('input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_output(self):
        output = get_output()
        self.send_json({'output': output})
    
    def send_status(self):
        self.send_json({'running': is_running})
    
    def handle_start(self):
        success = start_chaoxing()
        self.send_json({'success': success})
    
    def handle_stop(self):
        stop_chaoxing()
        self.send_json({'success': True})
    
    def handle_input(self):
        content_length = int(self.headers['Content-Length'])
        data = parse_qs(self.rfile.read(content_length).decode('utf-8'))
        input_text = data.get('input', [''])[0]
        success = send_input(input_text)
        self.send_json({'success': success})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    PORT = 5000
    
    print(f"启动服务器在端口 {PORT}")
    print(f"访问: http://localhost:{PORT}")
    print("按 Ctrl+C 停止")
    
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            stop_chaoxing()
            print("\n服务器已停止")