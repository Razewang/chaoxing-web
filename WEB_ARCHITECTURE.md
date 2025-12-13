# Chaoxing Web - 插件化架构说明

## 🎯 项目定位

本项目是 [Samueli924/chaoxing](https://github.com/Samueli924/chaoxing) 的 **Web 界面扩展版本**，采用**插件化架构设计**，确保：
- ✅ 上游代码零修改
- ✅ Web 功能完全独立
- ✅ 上游更新自动兼容
- ✅ 可随时回退到纯命令行版本

## 📁 项目结构

```
chaoxing-web/
├── main.py                      # 上游：命令行主程序（不修改）
├── api/                         # 上游：核心API模块（不修改）
│   ├── base.py
│   ├── answer.py
│   ├── decode.py
│   └── ...
├── requirements.txt             # 上游：基础依赖（跟随上游）
├── config_template.ini          # 上游：配置模板（跟随上游）
│
├── web/                         # 🆕 Web扩展（本地维护）
│   ├── app.py                   # Flask Web应用
│   ├── professional_web_standalone.py
│   ├── requirements.txt         # Web专用依赖
│   ├── static/                  # 静态资源
│   │   ├── css/
│   │   └── js/
│   └── templates/               # HTML模板
│
├── start_web.py                 # 🆕 Web界面启动脚本
├── UPSTREAM_SYNC_GUIDE.md       # 🆕 上游同步指南
├── WEB_ARCHITECTURE.md          # 🆕 本文档
└── .github/
    └── workflows/
        └── sync-upstream.yml    # 🆕 自动同步工作流
```

## 🔌 插件化设计原则

### 1. 文件隔离
- **上游文件**：`main.py`, `api/`, `requirements.txt`, `config_template.ini`
  - 完全跟随上游，不做任何修改
  - 合并上游更新时直接覆盖，不会产生冲突

- **扩展文件**：`web/`, `start_web.py`, `requirements_web.txt`
  - 仅在本地维护
  - 上游更新不会影响这些文件

### 2. 依赖分离

**requirements.txt** (跟随上游)
```txt
# 命令行版本的基础依赖
requests>=2.32.5
pyaes>=1.6.1
beautifulsoup4>=4.14.2
...
```

**web/requirements.txt** (本地维护)
```txt
# Web界面额外依赖
Flask>=3.1.2
Flask-SocketIO>=5.3.6
Celery>=5.5.3
...
```

**安装方式**:
```bash
# 命令行版本
pip install -r requirements.txt

# Web版本（包含命令行功能）
pip install -r requirements.txt
pip install -r web/requirements.txt
```

### 3. 代码耦合最小化

Web 界面通过以下方式使用核心功能：

```python
# web/app.py
# 方式1: 通过 subprocess 调用 main.py
subprocess.Popen([sys.executable, 'main.py', '-c', 'config.ini'])

# 方式2: 导入 api 模块（未来可选）
from api.base import Chaoxing, Account
from api.answer import Tiku
```

**优势**:
- Web 代码不侵入上游代码
- 上游功能更新自动生效
- 两种模式独立运行

## 🚀 使用方式

### 命令行模式（上游原生功能）

```bash
# 直接使用上游功能
python3 main.py --help
python3 main.py -c config.ini
python3 main.py -u 手机号 -p 密码
```

### Web界面模式（扩展功能）

```bash
# 使用Web界面
python3 start_web.py

# 或直接运行
python3 web/app.py
```

**访问**: http://localhost:5000

## 🔄 自动同步机制

### GitHub Actions 工作流

`.github/workflows/sync-upstream.yml` 实现自动同步：

**触发条件**:
- 每天 UTC 0:00 (北京时间 8:00) 自动检查
- 手动触发

**工作流程**:
1. 检测上游更新
2. 创建同步分支 `auto-sync-upstream-YYYYMMDD-HHMMSS`
3. 自动合并上游更新
4. 智能处理冲突：
   - `web/` 目录：保留本地版本
   - 上游文件：接受上游更新
5. 运行基础测试
6. 创建 Pull Request

**冲突处理策略**:
```yaml
# 优先保留本地版本的文件
- web/*
- web/**/*
- start_web.py
- requirements_web.txt
- UPSTREAM_SYNC_GUIDE.md
- WEB_ARCHITECTURE.md

# 接受上游更新的文件
- main.py
- api/*
- requirements.txt
- config_template.ini
```

### 手动同步

如果自动同步失败，可以手动操作：

```bash
# 1. 获取上游更新
git fetch upstream

# 2. 查看变更
git log --oneline main..upstream/main

# 3. 创建合并分支
git checkout -b merge-upstream

# 4. 合并
git merge upstream/main

# 5. 解决冲突（如有）
# web/ 相关冲突：保留本地版本
git checkout --ours web/

# 其他冲突：根据情况处理

# 6. 提交并推送
git push origin merge-upstream
```

## 🛡️ 兼容性保证

### 测试检查清单

每次上游合并后，自动运行以下检查：

- [x] 文件完整性：`main.py`, `api/base.py`, `web/app.py` 等
- [x] Python 语法：`python3 -m py_compile`
- [x] 命令行功能：`python3 main.py --help`
- [ ] Web 界面启动：`python3 start_web.py`（手动测试）
- [ ] 实际刷课功能：完整流程测试（手动测试）

### 版本追踪

```bash
# 查看当前基于的上游版本
git log --oneline --graph main upstream/main -20

# 查看上游新增功能
git log --oneline main..upstream/main --grep="feat"

# 查看上游Bug修复
git log --oneline main..upstream/main --grep="fix"
```

## 📝 维护指南

### 添加新的 Web 功能

1. 所有新代码放在 `web/` 目录
2. 新依赖添加到 `web/requirements.txt`
3. 通过导入 `api` 模块使用核心功能
4. 不修改上游文件

### 更新上游依赖

当上游 `requirements.txt` 更新时：
```bash
# 1. 接受上游的 requirements.txt
git checkout upstream/main -- requirements.txt

# 2. 重新安装依赖
pip install -r requirements.txt -U

# 3. 测试功能
python3 main.py --help
```

### 自定义上游代码（不推荐）

如果必须修改上游代码：
1. 在 `UPSTREAM_SYNC_GUIDE.md` 中记录修改
2. 创建补丁文件保存修改
3. 每次合并后重新应用补丁

**更好的方案**：提交 PR 到上游仓库

## 🔧 故障排查

### Web 界面无法启动

```bash
# 检查依赖
pip install -r web/requirements.txt

# 检查端口占用
lsof -i :5000

# 检查项目路径
python3 -c "from pathlib import Path; print(Path('main.py').exists())"
```

### 命令行功能失效

```bash
# 检查上游文件
ls -la main.py api/

# 重新安装基础依赖
pip install -r requirements.txt -U

# 测试
python3 main.py --help
```

### 合并冲突

```bash
# 查看冲突文件
git diff --name-only --diff-filter=U

# Web相关冲突：保留本地
git checkout --ours web/

# 上游文件冲突：接受上游
git checkout --theirs main.py api/

# 标记已解决
git add .
git commit
```

## 📚 相关文档

- [上游同步指南](./UPSTREAM_SYNC_GUIDE.md) - 详细的同步操作说明
- [Claude 项目指南](./CLAUDE.md) - 项目整体说明
- [上游仓库](https://github.com/Samueli924/chaoxing) - 原始命令行项目

## 🎉 优势总结

✅ **零侵入**: 不修改上游代码，保持100%兼容
✅ **自动化**: GitHub Actions 自动检测和合并更新
✅ **模块化**: Web 功能完全独立，可插拔
✅ **易维护**: 清晰的文件组织，明确的职责划分
✅ **可回退**: 随时可以移除 web/ 目录恢复纯命令行版本
✅ **双模式**: 同时支持命令行和 Web 界面

## 📞 贡献指南

欢迎贡献 Web 界面相关功能！

**贡献方向**:
1. Web 界面美化
2. 新增 Web 功能
3. 性能优化
4. 文档完善
5. Bug 修复

**注意**：
- 核心功能改进请提交到上游仓库
- Web 扩展功能在本仓库维护
