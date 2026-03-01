# 端口隔离与网络管理

当任何子模块需要启动容器或服务时，先执行本文件中的操作。

---

## 查找空闲端口

```bash
find_free_port() {
    local port=${1:-8000}
    local max_port=$((port + 100))
    while [ "$port" -le "$max_port" ]; do
        if ! ss -tlnp 2>/dev/null | grep -q ":${port} "; then
            echo "$port"
            return 0
        fi
        port=$((port + 1))
    done
    echo "ERROR: 在 ${1}-${max_port} 范围内没有空闲端口" >&2
    return 1
}
```

---

## 创建项目专属 Docker 网络

```bash
SETUP_NETWORK="setup_net_${PROJECT_NAME}"

docker network rm "$SETUP_NETWORK" 2>/dev/null || true
docker network create "$SETUP_NETWORK"
echo "✅ 创建网络: $SETUP_NETWORK"
```

所有后续 `docker run` 必须加 `--network "$SETUP_NETWORK"`。

---

## 等待服务就绪

```bash
wait_for_port() {
    local port=$1
    local max_wait=${2:-30}
    local waited=0
    while [ "$waited" -lt "$max_wait" ]; do
        ss -tlnp 2>/dev/null | grep -q ":${port} " && return 0
        sleep 1
        waited=$((waited + 1))
    done
    return 1
}

wait_for_service() {
    local service_type=$1
    local port=$2
    local container_name=$3
    local max_wait=${4:-30}
    local waited=0

    wait_for_port "$port" "$max_wait" || return 1

    echo -n "验证 ${service_type} 服务就绪"
    while [ "$waited" -lt "$max_wait" ]; do
        case "$service_type" in
            postgres)
                docker exec "$container_name" pg_isready -h localhost -U setup 2>/dev/null && { echo " ✅"; return 0; } ;;
            mysql)
                docker exec "$container_name" mysqladmin ping -h localhost -u setup --password=setup123 2>/dev/null && { echo " ✅"; return 0; } ;;
            redis)
                docker exec "$container_name" redis-cli ping 2>/dev/null | grep -q "PONG" && { echo " ✅"; return 0; } ;;
            mongo)
                docker exec "$container_name" mongosh --eval "db.runCommand({ping:1})" 2>/dev/null && { echo " ✅"; return 0; } ;;
            *)
                echo " ⚠️ 未知服务类型"; return 0 ;;
        esac
        echo -n "."
        sleep 2
        waited=$((waited + 2))
    done
    echo " ❌ 超时（${max_wait}s）"
    return 1
}
```

---

## 清理网络

```bash
docker network rm "setup_net_${PROJECT_NAME}" 2>/dev/null
```
