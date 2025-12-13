# Chaoxing Web - 超星学习通自动化助手 (Web扩展版)

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Upstream](https://img.shields.io/badge/upstream-Samueli924%2Fchaoxing-green.svg)](https://github.com/Samueli924/chaoxing)
[![Auto Sync](https://img.shields.io/badge/auto--sync-enabled-brightgreen.svg)](.github/workflows/sync-upstream.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 🎯 基于 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 的 Web 界面扩展版本
>
> ✨ 采用插件化架构，上游更新自动兼容，零代码冲突

一个功能强大的超星学习通/超星尔雅/泛雅超星全自动无人值守任务完成工具，在保留完整命令行功能的基础上，增加了现代化的 Web 操作界面。

## 🌟 主要特性

### 核心功能（继承自上游）
- 📚 **全自动课程学习** - 自动完成视频观看、文档阅读、测验答题等所有任务点
- 🤖 **智能答题系统** - 集成题库搜索，自动完成各类测验和考试
- 🎬 **视频加速播放** - 支持1-2倍速播放，大幅节省学习时间
- 🔔 **进度通知** - 实时推送学习进度和完成情况
- 🛡️ **安全可靠** - 模拟真实用户行为，降低检测风险
- ⚡ **多线程并发** - 支持同时处理多个章节，提升效率
- 📺 **直播回放支持** - 自动完成直播回放任务

### Web扩展功能（本项目特色）
- 🌐 **Web图形界面** - 提供友好的Web操作界面，实时查看进度
- 📱 **响应式设计** - 支持PC、平板、手机多端访问
- 🔄 **自动同步上游** - GitHub Actions 自动检测和合并上游更新
- 🔌 **插件化架构** - Web功能完全独立，不影响上游代码
- 📊 **实时日志** - WebSocket实时推送执行日志
- 🎨 **现代化UI** - Bootstrap 5 + XTerm.js 终端模拟器

## 🚀 快速开始

### 方式一：命令行模式（上游原生功能）

```bash
# 1. 克隆项目
git clone https://github.com/Razewang/chaoxing-web.git
cd chaoxing-web

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置账号
cp config_template.ini config.ini
nano config.ini  # 填入你的账号密码

# 4. 运行
python3 main.py -c config.ini
```

**命令行参数**:
```bash
# 查看帮助
python3 main.py --help

# 使用配置文件
python3 main.py -c config.ini

# 直接指定账号密码
python3 main.py -u 手机号 -p 密码

# 指定课程ID
python3 main.py -c config.ini -l 课程ID1,课程ID2

# 调整倍速
python3 main.py -c config.ini -s 1.5

# 多线程模式（同时处理4个章节）
python3 main.py -c config.ini -j 4

# 启用调试模式
python3 main.py -c config.ini -v
```

### 方式二：Web界面模式（扩展功能）

```bash
# 1-3步骤同上

# 4. 安装Web依赖
pip install -r web/requirements.txt

# 5. 启动Web服务
python3 start_web.py

# 6. 访问界面
open http://localhost:5000
```

**Web界面功能**:
- 📝 在线配置账号和课程
- 🎮 一键启动/停止学习任务
- 📺 实时查看终端日志输出
- 📊 监控任务执行进度
- 🔄 灵活控制学习流程

### 方式三：Docker部署

```bash
# 使用Docker Compose（推荐）
docker-compose up -d

# 或使用Docker命令
docker run -d \
  --name chaoxing-web \
  -p 5000:5000 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  ghcr.io/razewang/chaoxing-web:latest
```

访问: http://localhost:5000

## 📁 项目结构（插件化设计）

```
chaoxing-web/
├── main.py                      # 上游：命令行主程序
├── api/                         # 上游：核心API模块
│   ├── base.py                 # 主要的 Chaoxing 类
│   ├── answer.py               # 题库系统
│   ├── decode.py               # HTML解析
│   ├── live.py                 # 直播回放功能
│   └── ...
├── requirements.txt             # 上游：基础依赖
├── config_template.ini          # 上游：配置模板
│
├── web/                         # 🆕 Web扩展（本地维护）
│   ├── app.py                   # Flask Web应用
│   ├── requirements.txt         # Web专用依赖
│   ├── static/                  # 静态资源
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/               # HTML模板
│       └── index.html
│
├── start_web.py                 # 🆕 Web启动脚本
├── WEB_ARCHITECTURE.md          # 🆕 架构设计文档
├── UPSTREAM_SYNC_GUIDE.md       # 🆕 上游同步指南
└── .github/workflows/
    └── sync-upstream.yml        # 🆕 自动同步工作流
```

**设计原则**:
- ✅ 上游文件（`main.py`, `api/`, `requirements.txt`）**零修改**
- ✅ Web功能（`web/`, `start_web.py`）**完全独立**
- ✅ 上游更新**自动兼容**，无代码冲突
- ✅ 可随时移除 `web/` 目录恢复纯命令行版本

## 🔄 自动同步机制

### GitHub Actions 自动同步

项目配置了自动同步工作流，每天自动检查上游更新：

**工作流程**:
1. 🕐 每天 UTC 0:00 (北京时间 8:00) 自动检查
2. 🔍 检测上游 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 的更新
3. 🔀 自动创建同步分支并合并更新
4. 🛡️ 智能处理冲突：
   - `web/` 目录：保留本地版本
   - 上游文件：接受上游更新
5. 🧪 运行基础兼容性测试
6. 📬 创建 Pull Request 供审核

**手动触发**:
- 访问 Actions 页面
- 选择 "Sync with Upstream" workflow
- 点击 "Run workflow"

详见: [上游同步指南](./UPSTREAM_SYNC_GUIDE.md)

## 💻 配置说明

### config.ini 配置文件

```ini
[common]
; 手机号账号(必填)
username = 13800138000

; 登录密码(必填)
password = yourpassword

; 要学习的课程ID列表(选填，留空则学习所有课程)
course_list = 123456,789012

; 视频播放倍速(默认1，最大2)
speed = 1.5

; 同时进行的章节数(默认4)
jobs = 4

; 遇到关闭任务点时的行为: retry-重试, ask-询问, continue-继续
notopen_action = retry

[tiku]
; 题库选择: TikuYanxi / TikuLike / TikuAdapter / AI / SiliconFlow
tiku = TikuLike

; 是否自动提交答案
submit = true

; 答案覆盖率阈值(0-1)
cover_rate = 0.8

[notification]
; 通知服务: serverchan / qmsg / bark / telegram
notification =

; 通知URL或Token
url =
```

## 🧪 测试与验证

### 自动化测试

每次上游同步后自动运行：

```bash
# 文件完整性检查
ls main.py api/base.py web/app.py

# Python语法检查
python3 -m py_compile main.py
python3 -m py_compile web/app.py

# 命令行功能测试
python3 main.py --help
```

### 手动测试

```bash
# 1. 测试命令行模式
python3 main.py -c config.ini -v

# 2. 测试Web界面
python3 start_web.py
# 访问 http://localhost:5000

# 3. 测试依赖完整性
pip install -r requirements.txt
pip install -r web/requirements.txt
```

## 📚 文档索引

- 📖 [Web架构设计](./WEB_ARCHITECTURE.md) - 插件化架构详解
- 🔄 [上游同步指南](./UPSTREAM_SYNC_GUIDE.md) - 如何同步上游更新
- 🤖 [Claude项目指南](./CLAUDE.md) - 项目整体说明
- 🔗 [上游仓库](https://github.com/Samueli924/chaoxing) - 原始命令行项目

## 🛠️ 常见问题

### Q: Web界面和命令行有什么区别？
A: 功能完全相同，Web界面提供图形化操作和实时日志查看，命令行更适合自动化和服务器部署。

### Q: 上游更新会影响Web功能吗？
A: 不会。Web功能完全独立在 `web/` 目录，上游更新通过自动同步工作流处理，不会产生冲突。

### Q: 如何回退到纯命令行版本？
A: 删除 `web/` 目录和 `start_web.py` 即可，或直接克隆上游仓库。

### Q: 可以同时运行多个实例吗？
A: 可以。命令行模式支持多实例，Web模式需要修改端口。

### Q: 支持哪些题库？
A: 支持言溪题库、LIKE知识库、TikuAdapter、OpenAI兼容API、硅基流动等。详见配置文件。

## ⚠️ 免责声明

- 本项目仅供学习交流使用
- 请合理使用，遵守平台规则
- 使用本工具产生的任何后果由使用者自行承担
- 建议在个人课程上使用，不要用于商业用途

## 🤝 贡献指南

欢迎贡献代码和建议！

**贡献方向**:
- 🎨 Web界面美化和新功能
- 📝 文档完善和翻译
- 🐛 Bug修复和问题反馈
- 💡 新功能建议

**注意**：
- Web扩展功能请在本仓库提PR
- 核心功能改进请提交到[上游仓库](https://github.com/Samueli924/chaoxing)

## 📄 开源协议

本项目采用 MIT 协议开源。

## 🙏 致谢

- 感谢 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 提供核心功能
- 感谢所有贡献者的支持

## 📞 联系方式

- 上游项目Issue: https://github.com/Samueli924/chaoxing/issues
- 本项目Issue: https://github.com/Razewang/chaoxing-web/issues

---

⭐ 如果这个项目对你有帮助，请给一个Star支持！
