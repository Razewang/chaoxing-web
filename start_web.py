#!/usr/bin/env python3
"""
Chaoxing Web Interface Launcher
启动超星学习通 Web 界面
"""
import sys
from pathlib import Path

# 确保在项目根目录运行
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# 切换到 web 目录并启动应用
web_dir = project_root / 'web'
sys.path.insert(0, str(web_dir))

import os
os.chdir(str(project_root))

# 导入并运行Web应用
from web.app import ChaoxingWebApp

if __name__ == '__main__':
    print("🚀 启动 Chaoxing Web 界面...")
    print(f"📁 项目根目录: {project_root}")
    print(f"🌐 Web 界面将在 http://localhost:5000 启动")
    print()

    app = ChaoxingWebApp()
    app.socketio.run(app.app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
