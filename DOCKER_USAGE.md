# Docker 镜像使用说明

## 快速启动

### 1. 拉取镜像

```bash
# 从 GitHub Container Registry 拉取最新版本
docker pull ghcr.io/razewang/chaoxing-web:latest

# 或指定版本
docker pull ghcr.io/razewang/chaoxing-web:v3.1.3
```

### 2. 创建配置文件

```bash
# 创建配置文件
cat > config.ini << EOF
[account]
username = 你的手机号
password = 你的密码

[course]
course_ids = 

[settings]
speed = 1.0
notopen_action = retry
debug = false
EOF
```

### 3. 运行容器

```bash
# 基本运行
docker run -d \
  --name chaoxing-web \
  -p 5000:5000 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  ghcr.io/razewang/chaoxing-web:latest

# 带日志持久化
docker run -d \
  --name chaoxing-web \
  -p 5000:5000 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  ghcr.io/razewang/chaoxing-web:latest
```

### 4. 访问服务

打开浏览器访问：http://localhost:5000

## 管理命令

```bash
# 查看日志
docker logs chaoxing-web
docker logs -f chaoxing-web  # 实时查看

# 停止容器
docker stop chaoxing-web

# 启动容器
docker start chaoxing-web

# 删除容器
docker rm chaoxing-web

# 更新镜像
docker pull ghcr.io/razewang/chaoxing-web:latest
docker stop chaoxing-web && docker rm chaoxing-web
# 然后重新运行容器命令
```

## 环境变量

```bash
docker run -d \
  --name chaoxing-web \
  -p 5000:5000 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  -e TZ=Asia/Shanghai \
  -e DEBUG=true \
  ghcr.io/razewang/chaoxing-web:latest
```

## Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'
services:
  chaoxing-web:
    image: ghcr.io/razewang/chaoxing-web:latest
    container_name: chaoxing-web
    ports:
      - "5000:5000"
    volumes:
      - ./config.ini:/app/config.ini:ro
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

运行：
```bash
docker-compose up -d
```