# MongoDB 搭建

前置依赖：`helpers/port-isolation.md` + `helpers/image-check.md`。

---

## 启动

```bash
ensure_image "mongo:7"
MONGO_PORT=$(find_free_port 27017)

docker run -d \
    --name "setup_${PROJECT_NAME}_mongo" \
    --network "$SETUP_NETWORK" \
    -p ${MONGO_PORT}:27017 \
    mongo:7

wait_for_service "mongo" "$MONGO_PORT" "setup_${PROJECT_NAME}_mongo" 20
echo "MongoDB → localhost:${MONGO_PORT}"
```

## 连接信息

```
HOST=localhost / setup_${PROJECT_NAME}_mongo（容器间）
PORT=${MONGO_PORT} / 27017（容器间）
URL=mongodb://localhost:${MONGO_PORT}/${PROJECT_NAME}
```

## 清理

```bash
docker rm -f "setup_${PROJECT_NAME}_mongo" 2>/dev/null
```
