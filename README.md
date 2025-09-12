# Chaoxing Web - 超星学习通自动化助手

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.1.3-orange.svg)](pyproject.toml)

一个功能强大的超星学习通/超星尔雅/泛雅超星全自动无人值守任务完成工具。

## 🌟 主要功能

- 📚 **全自动课程学习** - 自动完成视频观看、文档阅读、测验答题等所有任务点
- 🤖 **智能答题系统** - 集成题库搜索，自动完成各类测验和考试
- 🎬 **视频加速播放** - 支持1-2倍速播放，大幅节省学习时间
- 🌐 **Web图形界面** - 提供友好的Web操作界面，实时查看进度
- 📱 **多账户支持** - 支持配置多个账户同时管理
- 🔔 **进度通知** - 实时推送学习进度和完成情况
- 🛡️ **安全可靠** - 模拟真实用户行为，降低检测风险

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- 推荐使用虚拟环境

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/Samueli924/chaoxing.git
   cd chaoxing
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   # 或使用 pyproject.toml
   pip install .
   ```

### 配置文件

创建配置文件 `config.ini`：

## 🐳 Docker部署（推荐）

Docker部署是最简单快捷的方式，无需手动配置Python环境。

### 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)（可选）

### 快速启动

1. **创建配置文件**
   ```bash
   # 复制配置模板
   cp config_template.ini config.ini
   
   # 编辑配置文件，填入你的账号信息
   nano config.ini
   ```

2. **使用Docker Compose启动（推荐）**
   ```bash
   # 启动服务
   docker-compose up -d
   
   # 查看日志
   docker-compose logs -f
   
   # 停止服务
   docker-compose down
   ```

3. **使用Docker命令启动**
   ```bash
   # 构建镜像
   docker build -t chaoxing-web .
   
   # 运行容器
   docker run -d \
     --name chaoxing-web \
     -p 5000:5000 \
     -v $(pwd)/config.ini:/app/config.ini:ro \
     -v $(pwd)/logs:/app/logs \
     --restart unless-stopped \
     chaoxing-web
   ```

### 访问Web界面

启动成功后，访问：http://localhost:5000

### Docker Compose高级配置

#### 启用反向代理

```bash
# 使用nginx反向代理
docker-compose --profile proxy up -d
```

这将在80端口提供HTTP服务，支持后续配置HTTPS。

#### 自定义配置

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  chaoxing-web:
    environment:
      - TZ=America/New_York  # 修改时区
    ports:
      - "5001:5000"         # 修改端口
```

### Docker管理命令

```bash
# 查看运行状态
docker ps

# 查看容器日志
docker logs chaoxing-web

# 进入容器
docker exec -it chaoxing-web bash

# 重启容器
docker restart chaoxing-web

# 删除容器
docker stop chaoxing-web && docker rm chaoxing-web
```

### 配置文件

创建配置文件 `config.ini`：

```ini
[account]
username = 你的手机号
password = 你的密码

[course]
# 指定要学习的课程ID，留空则学习所有课程
course_ids = 

[settings]
# 视频播放倍速（1.0-2.0）
speed = 1.0
# 遇到关闭任务点的行为：retry/ask/continue
notopen_action = retry
# 是否启用调试模式
debug = false

[notification]
# 通知设置（可选）
enable = false
type = 
webhook = 
```

## 💻 使用方法

### 命令行模式

```bash
# 使用配置文件运行
python main.py -c config.ini

# 直接指定账号密码
python main.py -u 13800138000 -p yourpassword

# 指定特定课程
python main.py -c config.ini -l course1,course2,course3

# 调整播放速度
python main.py -c config.ini -s 1.5

# 启用调试模式
python main.py -c config.ini -v
```

### Web界面模式

1. **启动Web服务器**
   ```bash
   python professional_web_standalone.py
   ```

2. **访问界面**
   打开浏览器访问：http://localhost:5000

3. **功能特点**
   - 实时查看课程列表和学习进度
   - 动态选择要学习的课程
   - 在线控制学习进程
   - 查看详细日志输出

## 📁 项目结构

```
chaoxing-web/
├── main.py                    # 主程序入口
├── professional_web.html      # Web界面前端
├── professional_web_standalone.py  # Web服务器独立脚本
├── config.ini                 # 配置文件（用户创建）
├── config_template.ini        # 配置文件模板
├── Dockerfile                 # Docker镜像构建文件
├── docker-compose.yml         # Docker Compose配置
├── nginx.conf                 # Nginx配置模板（可选）
├── .dockerignore              # Docker构建忽略文件
├── api/                       # 核心API模块
│   ├── base.py               # 基础类和账户管理
│   ├── answer.py             # 答题系统
│   ├── exceptions.py         # 异常定义
│   ├── logger.py             # 日志模块
│   └── notification.py       # 通知系统
├── resource/                  # 资源文件
├── venv/                      # 虚拟环境（本地开发）
├── logs/                      # 日志目录（Docker映射）
└── README.md                  # 项目说明
```

## ⚙️ 详细配置

### 账户配置

- `username`: 超星学习通手机号
- `password`: 登录密码

### 课程配置

- `course_ids`: 课程ID列表，用逗号分隔
- 留空则自动学习所有课程

### 高级设置

- `speed`: 视频播放速度（1.0-2.0）
- `notopen_action`: 
  - `retry`: 遇到未开放任务点时重试
  - `ask`: 询问用户如何处理
  - `continue`: 跳过并继续下一个
- `debug`: 启用详细日志输出

## 🔧 故障排除

### 常见问题

1. **登录失败**
   - 检查账号密码是否正确
   - 确认是否需要验证码
   - 尝试手动登录网页版

2. **视频播放异常**
   - 检查网络连接
   - 调整播放速度
   - 查看详细日志

3. **题库搜索失败**
   - 检查网络连接
   - 确认题库服务是否可用
   - 更新题库索引

4. **Web界面无法访问**
   - 确认端口5000未被占用
   - 检查防火墙设置
   - 尝试使用127.0.0.1:5000

### Docker相关问题

1. **容器启动失败**
   ```bash
   # 查看容器状态
   docker ps -a
   
   # 查看错误日志
   docker logs chaoxing-web
   ```

2. **配置文件挂载失败**
   - 确认config.ini文件存在
   - 检查文件路径是否正确
   - 确保有读取权限

3. **端口冲突**
   ```bash
   # 修改docker-compose.yml中的端口映射
   ports:
     - "5001:5000"  # 使用5001端口
   ```

4. **权限问题**
   ```bash
   # 创建日志目录并设置权限
   mkdir -p logs
   chmod 755 logs
   ```

### 调试模式

启用调试模式获取详细信息：
```bash
python main.py -v
```

## 📝 更新日志

### v3.1.3 (最新)
- 修复选项乱序问题
- 优化like知识库功能
- 新增验证码识别模块
- 改进错误处理机制

### v3.1.2
- 新增Web图形界面
- 支持实时进度查看
- 优化视频播放逻辑
- 增加通知功能

## ⚠️ 免责声明

本项目仅供学习和研究使用，请勿用于商业用途。

- 使用本工具造成的任何后果由使用者自行承担
- 建议合理使用，避免过度自动化导致账号风险
- 请遵守各平台的使用条款和规定

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢所有贡献者和以下开源项目：

- [requests](https://github.com/psf/requests) - HTTP库
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML解析
- [loguru](https://github.com/Delgan/loguru) - 日志库

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**