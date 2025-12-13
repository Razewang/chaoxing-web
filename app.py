import os
import sys
import subprocess
import threading
import time
import json
import configparser
from pathlib import Path
from celery import Celery, Task
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import logging
from logging.handlers import RotatingFileHandler


class ChaoxingWebApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'chaoxing-web-secret-key'
        self.app.config['CELERY'] = dict(
            broker_url="db+sqlite:///celeryresults.sqlite3",
            result_backend="sqlite:///celeryresults.sqlite3",
            task_ignore_result=True,
        )

        # 初始化SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # 程序状态（添加线程锁保护）
        self.process = None
        self.is_running = False
        self.output_buffer = []
        self.output_lock = threading.Lock()
        self.status_lock = threading.Lock()

        # 初始化Celery
        self.celery_app = celery_init_app(self.app)

        # 设置路由
        self.setup_routes()
        self.setup_socket_events()

        # 配置日志
        self.setup_logging()
    
    def setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        handler = RotatingFileHandler('logs/web_app.log', maxBytes=10240, backupCount=10)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        handler.setLevel(logging.INFO)
        self.app.logger.addHandler(handler)
        self.app.logger.setLevel(logging.INFO)
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            config = configparser.ConfigParser()
            if os.path.exists('config.ini'):
                config.read('config.ini', encoding='utf-8')
                return jsonify({
                    'common': dict(config['common']) if 'common' in config else {},
                    'tiku': dict(config['tiku']) if 'tiku' in config else {},
                    'notification': dict(config['notification']) if 'notification' in config else {}
                })
            return jsonify({})
        
        @self.app.route('/api/config', methods=['POST'])
        def save_config():
            data = request.json
            config = configparser.ConfigParser()
            
            # 读取现有配置
            if os.path.exists('config.ini'):
                config.read('config.ini', encoding='utf-8')
            
            # 更新配置
            for section in ['common', 'tiku', 'notification']:
                if section not in config:
                    config[section] = {}
                if section in data:
                    for key, value in data[section].items():
                        config[section][key] = str(value)
            
            # 保存配置
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            
            return jsonify({'success': True})
        
        @self.app.route('/api/start', methods=['POST'])
        def start_program():
            with self.status_lock:
                if self.is_running:
                    return jsonify({'error': '程序正在运行中'})

                # 启动程序
                self.is_running = True

            try:
                with self.output_lock:
                    self.output_buffer = []

                # 使用线程运行程序
                thread = threading.Thread(target=self.run_program)
                thread.daemon = True
                thread.start()

                return jsonify({'success': True})
            except Exception as e:
                with self.status_lock:
                    self.is_running = False
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_program():
            with self.status_lock:
                if self.process:
                    self.process.terminate()
                    self.process = None
                self.is_running = False
            return jsonify({'success': True})
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            with self.status_lock:
                running = self.is_running
            with self.output_lock:
                output = self.output_buffer[-100:]  # 返回最近100行输出
            return jsonify({
                'running': running,
                'output': output
            })
        
        @self.app.route('/api/send-input', methods=['POST'])
        def send_input():
            if self.process and self.is_running:
                data = request.json
                input_text = data.get('input', '')
                try:
                    self.process.stdin.write(input_text + '\n')
                    self.process.stdin.flush()
                    return jsonify({'success': True})
                except Exception as e:
                    return jsonify({'error': str(e)})
            return jsonify({'error': '程序未运行'})
        
        @self.app.route('/static/<path:path>')
        def send_static(path):
            return send_from_directory('static', path)
    
    def setup_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            emit('status', {'running': self.is_running})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            pass
    
    def run_program(self):
        try:
            # 检查main.py是否存在
            if not os.path.exists('main.py'):
                error_msg = '错误: main.py文件不存在'
                with self.output_lock:
                    self.output_buffer.append(error_msg)
                self.socketio.emit('output', {'data': error_msg})
                return

            # 运行main.py（使用sys.executable确保使用正确的Python解释器）
            self.process = subprocess.Popen(
                [sys.executable, 'main.py', '-c', 'config.ini'],
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
                    with self.output_lock:
                        self.output_buffer.append(line.strip())
                    # 通过WebSocket发送输出
                    self.socketio.emit('output', {'data': line.strip()})

            self.process.stdout.close()
            return_code = self.process.wait()

            if return_code != 0:
                error_msg = f'程序异常退出，返回码: {return_code}'
                with self.output_lock:
                    self.output_buffer.append(error_msg)
                self.socketio.emit('output', {'data': error_msg})

        except Exception as e:
            error_msg = f'运行错误: {str(e)}'
            with self.output_lock:
                self.output_buffer.append(error_msg)
            self.socketio.emit('output', {'data': error_msg})
        finally:
            with self.status_lock:
                self.is_running = False
                self.process = None
            self.socketio.emit('status', {'running': False})
    
    def run(self, debug=False, port=5000):
        self.socketio.run(self.app, debug=debug, port=port, host='0.0.0.0', allow_unsafe_werkzeug=True)


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


if __name__ == "__main__":
    # 从环境变量读取DEBUG设置，默认为False（生产环境）
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    web_app = ChaoxingWebApp()
    web_app.run(debug=debug_mode)