#!/usr/bin/env python3
"""
Simple test script to verify dependencies are working
"""
import sys
import subprocess

print("测试依赖安装情况...")
print("-" * 40)

# Test basic dependencies
deps = ['requests', 'beautifulsoup4', 'lxml', 'loguru', 'fonttools']

for dep in deps:
    try:
        if dep == 'beautifulsoup4':
            import bs4
            print(f"✓ {dep} (bs4) 已安装")
        else:
            __import__(dep)
            print(f"✓ {dep} 已安装")
    except ImportError as e:
        print(f"✗ {dep} 未安装: {e}")

print("-" * 40)
print("依赖测试完成")

# Test if main.py can be imported
print("\n测试 main.py 是否可以运行...")
try:
    import subprocess
    result = subprocess.run([sys.executable, '-c', 'import main; print("main.py 可以导入")'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✓ main.py 可以正常导入")
    else:
        print(f"✗ main.py 导入失败: {result.stderr}")
except Exception as e:
    print(f"✗ 测试失败: {e}")

print("\n现在可以启动 web 界面了！")
print("运行命令: python3 styled_web.py")