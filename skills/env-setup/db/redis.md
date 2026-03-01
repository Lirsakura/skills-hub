# Redis 搭建

前置依赖：`helpers/port-isolation.md` + `helpers/image-check.md`。

---

## 启动

```bash
ensure_image "redis:7"
REDIS_PORT=$(find_free_port 6379)

docker run -d \
    --name "setup_${PROJECT_NAME}_redis" \
    --network "$SETUP_NETWORK" \
    -p ${REDIS_PORT}:6379 \
    redis:7

wait_for_service "redis" "$REDIS_PORT" "setup_${PROJECT_NAME}_redis" 15
echo "Redis → localhost:${REDIS_PORT}"
```

## 连接信息

```
HOST=localhost / setup_${PROJECT_NAME}_redis（容器间）
PORT=${REDIS_PORT} / 6379（容器间）
URL=redis://localhost:${REDIS_PORT}/0
```

## 清理

```bash
docker rm -f "setup_${PROJECT_NAME}_redis" 2>/dev/null
```
