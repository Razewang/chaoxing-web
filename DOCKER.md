# Docker 快速部署指南

## 最简单的部署方式

### 1. 准备配置文件

```bash
# 复制配置模板
cp config_template.ini config.ini

# 编辑配置文件，填入你的学习通账号密码
nano config.ini
```

### 2. 启动服务

```bash
# 使用 docker-compose（推荐）
docker-compose up -d

# 或使用 docker 命令
docker build -t chaoxing-web .
docker run -d --name chaoxing-web -p 5000:5000 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  chaoxing-web
```

### 3. 访问服务

打开浏览器访问：http://localhost:5000

### 4. 查看日志

```bash
docker-compose logs -f
# 或
docker logs -f chaoxing-web
```

## 停止服务

```bash
docker-compose down
# 或
docker stop chaoxing-web && docker rm chaoxing-web
```

## 注意事项

- 确保Docker已正确安装
- 配置文件必须包含正确的账号密码
- 首次运行需要时间构建镜像