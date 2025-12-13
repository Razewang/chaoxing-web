#!/usr/bin/env python3
"""
学习通助手 Web界面 - 专业版（独立文件）
使用独立的前端HTML文件
"""

import os
import sys
import re
import json
import subprocess
import threading
import time
import signal
from pathlib import Path
import http.server
import socketserver
import urllib.parse

class ChaoxingWebInterface:
    def __init__(self):
        self.process = None
        self.is_running = False
        self.output_buffer = []
        self.courses = []
        self.selected_courses = set()
        self.course_progress = {}
        self.lock = threading.Lock()
        
    def start_chaoxing_process(self, course_list=None):
        """启动学习通进程"""
        if self.is_running:
            return False
            
        try:
            cmd = [sys.executable, 'main.py']
            
            # 如果有配置文件，使用配置文件
            if os.path.exists('config.ini'):
                cmd.extend(['-c', 'config.ini'])
            
            # 如果指定了课程列表，覆盖配置文件中的设置
            if course_list:
                # 临时修改配置文件
                self.update_config_course_list(course_list)
            
            self.is_running = True
            self.output_buffer = []
            
            # 在线程中启动进程
            thread = threading.Thread(target=self._run_process, args=(cmd,))
            thread.daemon = True
            thread.start()
            
            return True
        except Exception as e:
            self.is_running = False
            return False
    
    def _run_process(self, cmd):
        """运行进程并捕获输出"""
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时读取输出
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    with self.lock:
                        self.output_buffer.append(line)
                        self._parse_output(line)
            
            self.process.stdout.close()
            return_code = self.process.wait()
            
            if return_code != 0:
                with self.lock:
                    self.output_buffer.append(f'程序异常退出，返回码: {return_code}')
            
        except Exception as e:
            with self.lock:
                self.output_buffer.append(f'运行错误: {str(e)}')
        finally:
            self.is_running = False
            self.process = None
    
    def _parse_output(self, line):
        """解析输出，提取课程和进度信息"""
        # 解析课程列表
        course_match = re.match(r'ID:\s*(\d+)\s*课程名:\s*(.+)', line)
        if course_match:
            course_id = course_match.group(1)
            course_name = course_match.group(2).strip()
            self._add_course(course_id, course_name)
        
        # 解析课程数量
        count_match = re.search(r'找到\s*(\d+)\s*门课程', line)
        if count_match:
            course_count = int(count_match.group(1))
            self._add_to_output(f'Web界面: 检测到 {course_count} 门课程，请到课程标签页查看', 'course')
        
        # 解析进度信息
        progress_patterns = [
            r'(.*?)进度[:：]\s*(\d+\.?\d*)%?',
            r'(.*?)完成度[:：]\s*(\d+\.?\d*)%?',
            r'(.*?)已完成\s*(\d+\.?\d*)%',
        ]
        
        for pattern in progress_patterns:
            progress_match = re.search(pattern, line)
            if progress_match:
                course_name = progress_match.group(1).strip()
                progress = float(progress_match.group(2))
                self._update_progress(course_name, progress)
        
        # 解析任务完成
        if '已完成所有任务点' in line:
            course_match = re.search(r'章节：(.*?)已完成所有任务点', line)
            if course_match:
                course_name = course_match.group(1).strip()
                self._mark_course_completed(course_name)
        
        # 解析视频播放进度
        video_match = re.search(r'视频\s*(.*?)\s*[:：]\s*(\d+\.?\d*)%', line)
        if video_match:
            video_name = video_match.group(1).strip()
            progress = float(video_match.group(2))
            self._update_video_progress(video_name, progress)
    
    def _add_course(self, course_id, course_name):
        """添加课程到列表"""
        if not any(c['id'] == course_id for c in self.courses):
            course = {
                'id': course_id,
                'name': course_name,
                'progress': 0,
                'completed': False,
                'videos': []
            }
            self.courses.append(course)
    
    def _update_progress(self, course_name, progress):
        """更新课程进度"""
        for course in self.courses:
            if course_name in course['name'] or course['name'] in course_name:
                course['progress'] = min(100, max(0, progress))
                break
    
    def _update_video_progress(self, video_name, progress):
        """更新视频进度"""
        # 可以在这里添加视频进度跟踪逻辑
        pass
    
    def _mark_course_completed(self, course_name):
        """标记课程完成"""
        for course in self.courses:
            if course_name in course['name'] or course['name'] in course_name:
                course['completed'] = True
                course['progress'] = 100
                self._add_to_output(f'Web界面: 课程 "{course["name"]}" 已完成！', 'success')
                break
    
    def _add_to_output(self, message, msg_type='info'):
        """添加消息到输出缓冲区"""
        timestamp = time.strftime('%H:%M:%S')
        self.output_buffer.append(f'[{timestamp}] {message}')
    
    def update_config_course_list(self, course_list):
        """更新配置文件中的课程列表"""
        if not os.path.exists('config.ini'):
            return
            
        try:
            with open('config.ini', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 查找并更新course_list行
            for i, line in enumerate(lines):
                if line.startswith('course_list'):
                    lines[i] = f'course_list = {course_list}\n'
                    break
            
            with open('config.ini', 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"更新配置文件失败: {e}")
    
    def stop_process(self):
        """停止进程"""
        if self.process:
            try:
                self.process.terminate()
                time.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
            except:
                pass
        self.is_running = False
        self.process = None
    
    def send_input(self, text):
        """向进程发送输入"""
        if self.process and self.process.stdin and not self.process.stdin.closed:
            try:
                self.process.stdin.write(text + '\n')
                self.process.stdin.flush()
                return True
            except:
                return False
        return False
    
    def get_status(self):
        """获取状态"""
        return {
            'running': self.is_running,
            'output': self.output_buffer[-200:],  # 返回最近200行
            'courses': self.courses,
            'selected_courses': list(self.selected_courses)
        }

class WebHandler(http.server.SimpleHTTPRequestHandler):
    chaoxing_interface = ChaoxingWebInterface()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=".", **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_index()
        elif self.path == '/api/status':
            self.serve_status()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/start':
            self.handle_start()
        elif self.path == '/api/stop':
            self.handle_stop()
        elif self.path == '/api/input':
            self.handle_input()
        elif self.path == '/api/select_courses':
            self.handle_select_courses()
        else:
            self.send_error(404)
    
    def serve_index(self):
        """服务主页"""
        if os.path.exists('professional_web.html'):
            with open('professional_web.html', 'r', encoding='utf-8') as f:
                html = f.read()
        else:
            html = "<html><body><h1>错误：找不到前端文件</h1><p>请确保 professional_web.html 文件存在</p></body></html>"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_status(self):
        """服务状态API"""
        status = self.chaoxing_interface.get_status()
        self.send_json_response(status)
    
    def handle_start(self):
        """处理启动请求"""
        success = self.chaoxing_interface.start_chaoxing_process()
        self.send_json_response({'success': success})
    
    def handle_stop(self):
        """处理停止请求"""
        self.chaoxing_interface.stop_process()
        self.send_json_response({'success': True})
    
    def handle_input(self):
        """处理输入请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        success = self.chaoxing_interface.send_input(data.get('input', ''))
        self.send_json_response({'success': success})
    
    def handle_select_courses(self):
        """处理选择课程请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        course_list = ','.join(data['courses'])
        success = self.chaoxing_interface.start_chaoxing_process(course_list)
        self.send_json_response({'success': success})
    
    def send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def run_server():
    """运行服务器"""
    PORT = 5000
    
    # 获取本机IP
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\n学习通助手专业版 Web界面 - 独立文件版")
    print(f"=" * 60)
    print(f"服务器已启动!")
    print(f"\n访问地址:")
    print(f"- http://localhost:{PORT}")
    print(f"- http://127.0.0.1:{PORT}")
    print(f"- http://{local_ip}:{PORT}")
    print(f"\n前端文件:")
    print(f"- professional_web.html (可自由修改)")
    print(f"\n功能特点:")
    print(f"- 真实集成学习通脚本")
    print(f"- 实时显示课程列表")
    print(f"- 可选择特定课程学习")
    print(f"- 实时进度跟踪")
    print(f"\n按 Ctrl+C 停止服务器")
    
    with socketserver.TCPServer(("", PORT), WebHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n正在停止服务器...")
            WebHandler.chaoxing_interface.stop_process()
            print("服务器已停止")

if __name__ == "__main__":
    run_server()