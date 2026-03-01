# Docker Compose / Dockerfile 搭建

当项目自带 `docker-compose.yml` 或 `Dockerfile` 时使用。
最优先的搭建方案，使用本方案时不需要再读取语言对应的手动搭建文件。

前置依赖：`helpers/port-isolation.md`。
如果 compose 中引用了外部镜像，还需 `helpers/image-check.md`。

---

## 方案 A：有 Docker Compose 文件

### 分析 compose 文件

```bash
cd "$PROJECT_DIR"

COMPOSE_FILE=""
for f in docker-compose.yml docker-compose.yaml compose.yml compose.yaml; do
    [ -f "$f" ] && COMPOSE_FILE="$f" && break
done

echo "Compose 文件: $COMPOSE_FILE"
docker compose -f "$COMPOSE_FILE" config --services 2>/dev/null
```

### 处理端口冲突

```bash
WEB_PORT=$(find_free_port 8000)
export WEB_PORT=${WEB_PORT}
export DB_PORT=$(find_free_port 5432)

# 如果端口写死了
cp "$COMPOSE_FILE" "${COMPOSE_FILE}.bak"
sed -i "s/\"8000:8000\"/\"${WEB_PORT}:8000\"/g" "$COMPOSE_FILE"
sed -i "s/\"8080:8080\"/\"${WEB_PORT}:8080\"/g" "$COMPOSE_FILE"
sed -i "s/\"3000:3000\"/\"${WEB_PORT}:3000\"/g" "$COMPOSE_FILE"
```

### 启动

```bash
if [ -f .env.example ] && [ ! -f .env ]; then
    cp .env.example .env
fi

docker compose -f "$COMPOSE_FILE" up -d --build
docker compose -f "$COMPOSE_FILE" ps
```

---

## 方案 B：只有 Dockerfile

```bash
cd "$PROJECT_DIR"
WEB_PORT=$(find_free_port 8000)

EXPOSE_PORT=$(grep -i "^EXPOSE" Dockerfile | head -1 | grep -oE "[0-9]+" | head -1)
EXPOSE_PORT=${EXPOSE_PORT:-8000}

docker build -t "setup_${PROJECT_NAME}" .

docker run -d \
    --name "setup_${PROJECT_NAME}_web" \
    --network "$SETUP_NETWORK" \
    -p ${WEB_PORT}:${EXPOSE_PORT} \
    "setup_${PROJECT_NAME}"

echo "应用 → localhost:${WEB_PORT} (容器内端口 ${EXPOSE_PORT})"
```

---

## 清理

```bash
# Compose 方式
docker compose -f "$COMPOSE_FILE" down -v 2>/dev/null
[ -f "${COMPOSE_FILE}.bak" ] && mv "${COMPOSE_FILE}.bak" "$COMPOSE_FILE"

# Dockerfile 方式
docker rm -f "setup_${PROJECT_NAME}_web" 2>/dev/null
docker rmi "setup_${PROJECT_NAME}" 2>/dev/null
```
