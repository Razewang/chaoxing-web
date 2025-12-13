#!/usr/bin/env python3
import socket
import sys

def test_port(host, port):
    """测试端口是否可访问"""
    try:
        # 创建socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5秒超时
        
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ 端口 {port} 可以访问")
            return True
        else:
            print(f"✗ 端口 {port} 无法访问")
            return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

def check_listening_ports():
    """检查所有监听的端口"""
    try:
        import subprocess
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        print("\n当前监听的端口:")
        print("=" * 50)
        for line in result.stdout.split('\n'):
            if 'LISTEN' in line:
                print(line)
    except:
        print("无法获取端口信息")

if __name__ == "__main__":
    print("网络连接诊断工具")
    print("=" * 50)
    
    # 检查监听的端口
    check_listening_ports()
    
    # 测试各种连接方式
    print("\n测试连接:")
    print("-" * 30)
    
    # 测试localhost
    test_port('localhost', 5000)
    test_port('127.0.0.1', 5000)
    
    # 获取本机IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"\n本机IP: {local_ip}")
        test_port(local_ip, 5000)
        test_port('0.0.0.0', 5000)
    except:
        pass
    
    # 测试外部访问
    print(f"\n从外部访问请尝试:")
    print(f"- http://localhost:5000")
    print(f"- http://127.0.0.1:5000")
    
    # 获取本机IP地址
    try:
        import subprocess
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ips = result.stdout.strip().split()
        for ip in ips:
            print(f"- http://{ip}:5000")
    except:
        pass