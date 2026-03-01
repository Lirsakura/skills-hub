# PostgreSQL 搭建

前置依赖：`helpers/port-isolation.md` + `helpers/image-check.md`。

---

## 启动

```bash
ensure_image "postgres:15"
DB_PORT=$(find_free_port 5432)
DB_TYPE="postgres"

docker run -d \
    --name "setup_${PROJECT_NAME}_postgres" \
    --network "$SETUP_NETWORK" \
    -p ${DB_PORT}:5432 \
    -e POSTGRES_USER=setup \
    -e POSTGRES_PASSWORD=setup123 \
    -e POSTGRES_DB="${PROJECT_NAME}" \
    postgres:15

wait_for_service "postgres" "$DB_PORT" "setup_${PROJECT_NAME}_postgres" 30
echo "PostgreSQL → localhost:${DB_PORT}"
```

## 连接信息

```
HOST=localhost / setup_${PROJECT_NAME}_postgres（容器间）
PORT=${DB_PORT} / 5432（容器间）
USER=setup  PASSWORD=setup123  DATABASE=${PROJECT_NAME}
CONNECTION_STRING=postgresql://setup:setup123@localhost:${DB_PORT}/${PROJECT_NAME}
```

## 清理

```bash
docker rm -f "setup_${PROJECT_NAME}_postgres" 2>/dev/null
```
