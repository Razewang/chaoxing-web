# 上游同步指南

## 📋 项目结构说明

### 当前项目定位
- **项目名称**: chaoxing-web
- **基于**: Samueli924/chaoxing (命令行版本)
- **扩展**: 添加了Web界面和相关功能
- **分叉点**: commit 807a89e (build: 更新镜像，兼容onnxruntime #518)

### 仓库配置
```bash
origin   -> git@github.com:Razewang/chaoxing-web.git (你的仓库)
upstream -> https://gh-proxy.org/https://github.com/Samueli924/chaoxing.git (上游仓库)
```

## 📊 上游更新分析 (截至检查时间)

### 版本信息
- **上游最新版本**: v3.1.4
- **当前基础版本**: 约 v3.0.8 左右
- **上游新增提交**: 53个提交
- **主要文件变化**: 25个文件，+1560行，-616行

### 🎯 主要功能更新

#### 1. 核心功能增强
- ✅ **多线程并发**: 支持同时处理多个章节 (`-j/--jobs` 参数)
- ✅ **直播回放功能**: 新增 `api/live.py` 和 `api/live_process.py`
- ✅ **进度条显示**: 使用 tqdm 库提供更好的进度展示
- ✅ **Cookie登录**: 支持使用 cookies 登录 (`--use-cookies`)

#### 2. 题库系统优化
- ✅ **LIKE知识库优化**: 新增自动重试功能，优化代码结构
- ✅ **答案缓存优化**: 在检查完答案之后才缓存
- ✅ **题目匹配改进**: 解决题库给出答案但无法匹配的问题

#### 3. 通知系统扩展
- ✅ **Telegram Bot支持**: 新增 Telegram 消息推送
- ✅ **通知系统重构**: 优化通知模块代码结构

#### 4. 依赖管理
- ❌ **移除 ddddocr**: 验证码识别依赖已移除
- ✅ **新增依赖**: tqdm, httpx, urllib3
- ✅ **版本锁定**: 所有依赖添加了最低版本要求

#### 5. Bug修复
- ✅ 修复选项乱序时提交选项与实际选项不一致
- ✅ 修复 LIKE 知识库判断题问题
- ✅ 修复使用 cookie 登录时的 bug
- ✅ 修复在 Python 3.13 中无法安装 ddddocr 的问题

## 🔀 合并策略

### 方案一：完全合并（推荐）

**适用场景**: 想要获取所有上游更新，愿意解决冲突

**操作步骤**:
```bash
# 1. 创建合并分支
git checkout -b merge-upstream-v3.1.4

# 2. 合并上游 main 分支
git merge upstream/main

# 3. 解决冲突（主要关注以下文件）
#    - main.py (并发逻辑 vs Web界面)
#    - requirements.txt (依赖合并)
#    - config_template.ini (配置格式统一)
#    - api/base.py (核心功能合并)
#    - api/answer.py (题库系统合并)

# 4. 测试合并结果
python3 main.py --help
python3 app.py  # 测试Web界面

# 5. 合并到主分支
git checkout main
git merge merge-upstream-v3.1.4

# 6. 推送到远程
git push origin main
```

**预期冲突文件**:
- `main.py` - 上游增加并发，本地可能有自定义
- `requirements.txt` - 依赖列表不同
- `config_template.ini` - 配置格式可能不同
- `app.py` - 本地特有，无冲突
- `static/`, `templates/` - 本地特有，无冲突

### 方案二：选择性合并（稳妥）

**适用场景**: 只想要特定功能更新，避免大规模冲突

**操作步骤**:
```bash
# 1. 创建功能分支
git checkout -b selective-merge

# 2. 挑选特定提交（cherry-pick）
# 示例：合并直播功能
git cherry-pick 1dc0b54  # 添加直播回放任务点时长功能支持

# 示例：合并LIKE知识库优化
git cherry-pick 759ff6b  # LIKE知识库优化

# 示例：合并Telegram支持
git cherry-pick fcb7e86  # 推送支持Telegram Bot

# 3. 解决每个 cherry-pick 的冲突
# 4. 测试功能
# 5. 合并回主分支
```

**推荐 cherry-pick 的提交**:
```bash
759ff6b  # LIKE知识库优化
04baede  # 更新LIKE知识库相关API
fcb7e86  # Telegram Bot支持
1dc0b54  # 直播回放功能
595b7e6  # 答案缓存优化
```

### 方案三：手动迁移（最安全）

**适用场景**: 代码差异太大，想完全控制每个变化

**操作步骤**:
```bash
# 1. 查看上游特定文件
git show upstream/main:api/live.py > /tmp/live.py

# 2. 手动将需要的代码复制到本地
cp /tmp/live.py api/live.py

# 3. 根据上游代码手动调整本地代码
# 4. 逐个文件/功能进行迁移
# 5. 测试每个迁移的功能
```

## 🛠️ 具体合并建议

### 必须合并的更新
1. **Bug 修复**: 所有 fix 类型的提交都应该合并
2. **题库优化**: LIKE 知识库和答案缓存相关的优化
3. **依赖更新**: 移除 ddddocr，更新其他依赖版本

### 可选合并的功能
1. **多线程支持**: 如果需要性能提升，建议合并
2. **直播回放功能**: 如果用户需要此功能
3. **Telegram 通知**: 如果需要更多通知方式

### 需要保留的本地功能
1. **Web 界面**: `app.py`, `static/`, `templates/`
2. **Web 依赖**: `requirements_web.txt`
3. **项目文档**: `CLAUDE.md`
4. **Docker 配置**: 本地的 Docker 相关配置
5. **GitHub Actions**: 本地的 CI/CD 配置

## 📝 冲突处理指南

### main.py 冲突处理

**冲突原因**: 上游增加了并发和直播功能，结构变化较大

**处理建议**:
1. 优先采用上游的新版本 main.py
2. 确保保留本地的 Web 界面相关配置读取逻辑
3. 测试命令行功能是否正常

### requirements.txt 冲突处理

**冲突原因**: 依赖列表差异

**处理建议**:
```txt
# 合并策略：基础依赖 + Web依赖分离
# requirements.txt - 命令行版本依赖
requests>=2.32.5
pyaes>=1.6.1
beautifulsoup4>=4.14.2
lxml
argparse>=1.4.0
loguru>=0.7.3
fonttools>=4.60.1
openai>=1.109.1
tqdm>=4.67.1
httpx>=0.28.1
urllib3>=2.5.0

# requirements_web.txt - Web专用依赖
Flask>=3.1.2
Flask-SocketIO>=5.3.6
Celery>=5.5.3
redis>=5.0.0
eventlet>=0.33.3
python-socketio>=5.9.0
```

### config_template.ini 冲突处理

**冲突原因**: 配置格式可能不同

**处理建议**:
1. 检查上游的配置格式
2. 保持 `[common]`, `[tiku]`, `[notification]` 结构（与 main.py 兼容）
3. 可以创建 `config_web_template.ini` 作为 Web 界面专用配置

### api/ 模块冲突处理

**主要冲突文件**:
- `api/base.py` - 核心功能，优先采用上游
- `api/answer.py` - 题库系统，优先采用上游
- `api/decode.py` - 解析功能，优先采用上游
- `api/notification.py` - 通知系统，优先采用上游

**处理建议**:
1. 优先采用上游版本（功能更新更及时）
2. 如果本地有自定义修改，在上游版本基础上重新应用
3. 详细测试 API 模块的功能

## 🔄 未来同步流程

### 定期同步（推荐每月一次）

```bash
# 1. 获取上游更新
git fetch upstream

# 2. 查看新的提交
git log --oneline main..upstream/main

# 3. 查看详细变更
git diff --stat main..upstream/main

# 4. 决定合并策略（完全/选择性/手动）

# 5. 执行合并

# 6. 测试并推送
```

### 监控上游变化

**方法1: GitHub Watch**
- 在 https://github.com/Samueli924/chaoxing 点击 Watch
- 选择 "Releases only" 或 "All Activity"

**方法2: RSS订阅**
- 订阅: `https://github.com/Samueli924/chaoxing/commits/main.atom`

**方法3: 定期检查**
```bash
# 每周运行一次
git fetch upstream
git log --oneline main..upstream/main --since="1 week ago"
```

## ⚠️ 注意事项

### 兼容性检查
每次合并后必须测试：
1. ✅ 命令行模式: `python3 main.py --help`
2. ✅ 配置文件读取: `python3 main.py -c config.ini`
3. ✅ Web 界面: `python3 app.py`
4. ✅ 核心功能: 登录、获取课程、处理任务
5. ✅ 题库功能: 各个题库接口
6. ✅ 通知功能: 各个通知服务

### 回滚策略
如果合并出现问题：
```bash
# 回滚到合并前
git reset --hard HEAD~1

# 或回滚到特定提交
git reset --hard <commit-hash>

# 强制推送（谨慎使用）
git push -f origin main
```

### 文档维护
每次合并后更新：
1. `CLAUDE.md` - 项目指南
2. `README.md` - 使用说明
3. `UPSTREAM_SYNC_GUIDE.md` - 本文档（更新同步记录）

## 📚 相关资源

- **上游仓库**: https://github.com/Samueli924/chaoxing
- **当前仓库**: https://github.com/Razewang/chaoxing-web
- **Git 合并文档**: https://git-scm.com/docs/git-merge
- **Git Cherry-pick 文档**: https://git-scm.com/docs/git-cherry-pick

## 📅 同步记录

### 最近一次检查
- **日期**: 2025-12-13
- **上游版本**: v3.1.4
- **本地版本**: 基于 807a89e (约 v3.0.8)
- **待合并提交数**: 53个
- **主要更新**: 多线程、直播回放、题库优化、依赖更新

### 下次同步计划
- **建议时间**: 2026-01-13 (一个月后)
- **关注重点**: 新功能、Bug修复、依赖更新
