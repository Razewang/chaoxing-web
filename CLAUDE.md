# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个超星学习通自动化完成任务点工具，旨在自动完成学习任务，包括视频、文档、测验和阅读作业。项目支持命令行和Web界面两种运行模式。

## 运行应用程序

### 命令行界面

**基础运行:**
```bash
python main.py
```

**使用配置文件运行:**
```bash
python main.py -c config.ini
```

**使用命令行参数运行:**
```bash
python main.py -u <手机号> -p <密码> -l <课程ID1,课程ID2> -a [retry|ask|continue]
```

**启用调试日志:**
```bash
python main.py -v
```

### Web界面

提供现代化的Web界面（Flask + SocketIO + Celery）:
```bash
# 首次运行需要安装Web依赖
pip install -r requirements_web.txt

# 启动Web服务
python app.py

# 访问 http://localhost:5000
```

### Docker运行

**构建和运行:**
```bash
docker build -t chaoxing .
docker run -it chaoxing

# 使用自定义配置
docker run -it -v /本地路径/config.ini:/config/config.ini chaoxing
```

### 安装依赖

```bash
pip install -r requirements.txt
# 或者
pip install .
```

Web专用依赖:
```bash
pip install -r requirements_web.txt
```

## 架构设计

### 核心模块结构

**`api/` - 核心API模块:**
- `base.py`: 主要的 `Chaoxing` 类和 `Account` 类；处理登录、课程管理、任务处理
- `decode.py`: HTML解析函数，从平台响应中提取课程列表、章节点、任务卡片和题目信息
- `process.py`: 视频/音频任务的进度显示工具
- `answer.py`: 题库系统（`Tiku`），支持多个题库提供商（言溪题库、LIKE知识库、TikuAdapter、AI、硅基流动）
- `answer_check.py`: 答案验证和格式检查
- `captcha.py`: 使用ddddocr库进行验证码识别
- `cipher.py`: 登录凭证的AES加密
- `config.py`: 全局常量和HTTP请求头
- `cookies.py`: Cookie持久化
- `font_decoder.py`: 字体解码，应对平台反爬虫
- `notification.py`: 外部通知服务（Server酱、Qmsg、Bark）
- `exceptions.py`: 自定义异常（LoginError、MaxRollBackExceeded、MaxRetryExceeded等）

**`main.py`**: 命令行入口；编排课程选择、章节处理和任务执行

**Web界面**: 基于Flask + SocketIO + Celery的现代化Web应用（app.py），提供实时通信和异步任务支持

### 核心执行流程

1. **登录**: `Chaoxing.login()` 使用加密凭证认证，保存cookies
2. **获取课程**: `Chaoxing.get_course_list()` 检索可用课程
3. **获取章节**: 对每门课程，使用 `decode_course_point()` 获取章节/任务点结构
4. **处理任务**: 对每个章节点，`Chaoxing.get_job_list()` 获取任务卡片，然后:
   - 视频/音频: `Chaoxing.study_video()` 支持倍速控制
   - 文档: `Chaoxing.study_document()`
   - 测验: `Chaoxing.study_work()` 支持题库答题
   - 阅读: `Chaoxing.strdy_read()`
5. **处理锁定章节**: `RollBackManager` 防止章节需要完成前置测试时出现无限循环

### 配置系统

项目使用INI格式配置文件，包含三个部分:

**`[common]`**: 用户凭证、课程列表、视频倍速、关闭任务点处理行为
**`[tiku]`**: 题库提供商、提交模式、覆盖率阈值、API令牌
**`[notification]`**: 外部通知服务提供商和URL

配置可以从以下来源加载:
- `config.ini` 文件（默认）
- 通过 `-c` 标志指定自定义路径
- 命令行参数（覆盖文件设置）

### 题库系统

`Tiku` 基类定义了题库接口。实现包括:
- **TikuYanxi**: 言溪题库 (tk.enncy.cn)
- **TikuLike**: LIKE知识库 (datam.site)
- **TikuAdapter**: 开源适配器项目
- **AI**: OpenAI兼容API端点
- **SiliconFlow**: 硅基流动AI平台

题库功能支持:
- 通过 `CacheDAO` 进行本地缓存（cache.json）
- 按题目类型验证答案
- 基于覆盖率的可配置提交阈值
- 未达到提交阈值时自动回滚

### 任务点处理

**关闭/锁定任务点** (`notopen_action`):
- `retry`: 重试上一章节（需要配置题库并启用自动提交）
- `ask`: 询问用户是否继续或停止
- `continue`: 自动跳过所有关闭的任务点

**任务类型**:
- 视频: 带倍速控制的进度跟踪（最大2倍速）
- 文档: 完成查看
- 测验/测试 (`workid`): 通过题库答题
- 阅读: 模拟阅读时间

## 测试

测试文件位于 `tests/` 目录:
```bash
python tests/test_connection.py   # 测试平台连接
python tests/test_deps.py          # 检查依赖安装
python tests/test_real_output.py   # 测试输出格式
```

## 重要实现细节

### 反爬虫对策

平台使用自定义字体编码数字和文本。`font_decoder.py` 和 `cxsecret_font.py` 模块处理字体解码以提取实际文本内容。

### 会话管理

- 会话使用 `requests.Session` 和重试适配器（最多3次重试）
- Cookies持久化到 `cookies.txt` 以供重用
- 视频/音频任务使用不同的请求头

### 进度跟踪

视频和音频任务通过 `show_progress()` 函数显示实时进度条，时间格式化通过 `sec2time()` 实现。

### 回滚保护

`RollBackManager` 通过跟踪每个任务点的回滚尝试次数（最多3次，超过后抛出 `MaxRollBackExceeded` 异常）来防止无限回滚循环。

### Web应用架构

Web界面 (app.py) 使用:
- **Flask 2.3.3** - HTTP路由和Web框架
- **Flask-SocketIO 5.3.6** - WebSocket实时通信，推送日志到浏览器
- **Celery 5.3.2** - 后台异步任务队列（消息代理: SQLite）
- **Bootstrap 5** - 现代化响应式UI
- **XTerm.js** - 终端模拟器
- 静态文件: `static/css/style.css`, `static/js/app.js`
- 模板文件: `templates/index.html`

## 开发指南

### 添加新题库提供商

1. 在 `api/answer.py` 中继承 `Tiku` 类
2. 实现 `_init_tiku()` 进行提供商特定的设置
3. 实现 `_query(q_info)` 来查询提供商的API
4. 将提供商名称添加到配置模板

### 添加新任务类型

1. 在 `Chaoxing.get_job_list()` 中识别任务类型
2. 在 `process_job()` 中添加检测逻辑
3. 实现 `Chaoxing.study_<任务类型>()` 方法
4. 如需要，更新任务类型枚举

### 添加新通知服务

1. 在 `api/notification.py` 中继承 `NotificationService` 类
2. 实现 `_init_service()` 和 `_send(message)` 方法
3. 将服务名称添加到 `Notification.get_notification_from_config()` 中

## 已知问题和限制

- 视频播放最大倍速: 2倍（平台限制）
- 每个任务点的回滚限制为3次
- 某些任务类型可能被归类为"异常任务"并被跳过
- 验证码识别需要ddddocr库（首次使用可能较慢）
- 如果平台更新字体编码方案，字体解码可能失败
- 对于需要解锁的章节，必须配置题库并启用提交才能自动继续下一章节
