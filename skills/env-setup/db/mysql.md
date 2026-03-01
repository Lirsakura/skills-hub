# MySQL 搭建

前置依赖：`helpers/port-isolation.md` + `helpers/image-check.md`。

---

## 启动

```bash
ensure_image "mysql:8"
DB_PORT=$(find_free_port 3306)
DB_TYPE="mysql"

docker run -d \
    --name "setup_${PROJECT_NAME}_mysql" \
    --network "$SETUP_NETWORK" \
    -p ${DB_PORT}:3306 \
    -e MYSQL_ROOT_PASSWORD=setup123 \
    -e MYSQL_DATABASE="${PROJECT_NAME}" \
    -e MYSQL_USER=setup \
    -e MYSQL_PASSWORD=setup123 \
    mysql:8

wait_for_service "mysql" "$DB_PORT" "setup_${PROJECT_NAME}_mysql" 30
echo "MySQL → localhost:${DB_PORT}"
```

## 连接信息

```
HOST=localhost / setup_${PROJECT_NAME}_mysql（容器间）
PORT=${DB_PORT} / 3306（容器间）
USER=setup  PASSWORD=setup123  DATABASE=${PROJECT_NAME}
CONNECTION_STRING=mysql://setup:setup123@localhost:${DB_PORT}/${PROJECT_NAME}
```

## 清理

```bash
docker rm -f "setup_${PROJECT_NAME}_mysql" 2>/dev/null
```
