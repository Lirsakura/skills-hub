#!/bin/bash
# health_check.sh - 验证项目环境是否就绪
#
# 用法:
#   bash health_check.sh <project_name> <web_port> [services...]
#
# services 格式: <type>:<port>:<container_name>
#
# 示例:
#   bash health_check.sh myapp 8000
#   bash health_check.sh myapp 8000 postgres:5432:setup_myapp_postgres
#   bash health_check.sh myapp 8000 sqlite
#   bash health_check.sh myapp none   # ML 项目无 Web 端口
#
# 环境变量:
#   QUIET=true  → 安静模式，只输出机器可读结果
#   QUIET=false → 完整模式，带颜色（默认）

PROJECT_NAME=${1:?"用法: health_check.sh <project_name> <web_port|none> [services...]"}
WEB_PORT=${2:?"缺少 web_port 参数（无 Web 端口填 none）"}
shift 2
SERVICES=("$@")

QUIET=${QUIET:-false}

# 颜色 & 计数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS=0; FAIL=0; WARN=0
FAILURE_MSGS=()
WARN_MSGS=()

check() {
    local name="$1" result="$2" msg="$3"
    if [ "$result" -eq 0 ]; then
        ((PASS++))
        [ "$QUIET" != "true" ] && echo -e "  ${GREEN}✅ $name${NC}: $msg"
    elif [ "$result" -eq 2 ]; then
        ((WARN++))
        WARN_MSGS+=("${name}: ${msg}")
        [ "$QUIET" != "true" ] && echo -e "  ${YELLOW}⚠️  $name${NC}: $msg"
    else
        ((FAIL++))
        FAILURE_MSGS+=("${name}: ${msg}")
        [ "$QUIET" != "true" ] && echo -e "  ${RED}❌ $name${NC}: $msg"
    fi
}

detail() { [ "$QUIET" != "true" ] && echo -e "$1"; }

port_listening() { ss -tlnp 2>/dev/null | grep -q ":${1} "; }

verify_db_connection() {
    local db_type="$1" port="$2" container="$3"
    case "$db_type" in
        postgres)
            [ -n "$container" ] && { docker exec "$container" pg_isready -h localhost -U setup 2>/dev/null; return $?; }
            PGPASSWORD=setup123 psql -h localhost -p "$port" -U setup -c "SELECT 1;" >/dev/null 2>&1; return $? ;;
        mysql)
            [ -n "$container" ] && { docker exec "$container" mysqladmin ping -h localhost -u setup --password=setup123 2>/dev/null; return $?; }
            mysqladmin ping -h localhost -P "$port" -u setup --password=setup123 2>/dev/null; return $? ;;
        redis)
            [ -n "$container" ] && { docker exec "$container" redis-cli ping 2>/dev/null | grep -q "PONG"; return $?; }
            redis-cli -p "$port" ping 2>/dev/null | grep -q "PONG"; return $? ;;
        mongo)
            [ -n "$container" ] && { docker exec "$container" mongosh --quiet --eval "db.runCommand({ping:1})" >/dev/null 2>&1; return $?; }
            mongosh --port "$port" --quiet --eval "db.runCommand({ping:1})" >/dev/null 2>&1; return $? ;;
        sqlite) return 0 ;;
        *) return 1 ;;
    esac
}

# ── 开始检查 ──

detail ""
detail "========================================="
detail " 🔍 环境健康检查: ${PROJECT_NAME}"
detail "========================================="

# 1. Web 应用检查（web_port=none 时跳过）
if [ "$WEB_PORT" != "none" ]; then
    detail ""
    detail " ${CYAN}[Web 应用]${NC}"

    if port_listening "$WEB_PORT"; then
        check "端口 ${WEB_PORT}" 0 "正在监听"
    else
        check "端口 ${WEB_PORT}" 1 "未监听"
    fi

    HTTP_OK=false
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://localhost:${WEB_PORT}/" 2>/dev/null)

    if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 500 ]; then
        check "HTTP 响应" 0 "状态码 ${HTTP_CODE}"
        HTTP_OK=true
    else
        for path in "/api" "/health" "/login" "/admin" "/index.html"; do
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://localhost:${WEB_PORT}${path}" 2>/dev/null)
            if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 500 ]; then
                check "HTTP 响应" 0 "状态码 ${HTTP_CODE} (via ${path})"
                HTTP_OK=true
                break
            fi
        done
        [ "$HTTP_OK" = "false" ] && check "HTTP 响应" 1 "无法连接"
    fi
else
    detail ""
    detail " ${CYAN}[ML/脚本项目 - 无 Web 端口]${NC}"
    check "项目类型" 0 "ML/脚本项目，跳过 HTTP 检查"
fi

# 2. 数据库 & 服务检查
if [ ${#SERVICES[@]} -gt 0 ]; then
    detail ""
    detail " ${CYAN}[数据库 & 服务]${NC}"

    for svc in "${SERVICES[@]}"; do
        IFS=':' read -r SVC_TYPE SVC_PORT SVC_CONTAINER <<< "$svc"

        if [ "$SVC_TYPE" = "sqlite" ]; then
            check "SQLite" 0 "文件数据库，无需网络服务"
            continue
        fi

        if port_listening "$SVC_PORT"; then
            check "${SVC_TYPE} 端口 ${SVC_PORT}" 0 "正在监听"
        else
            check "${SVC_TYPE} 端口 ${SVC_PORT}" 1 "未监听"
            continue
        fi

        if [ -n "$SVC_CONTAINER" ]; then
            CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' "$SVC_CONTAINER" 2>/dev/null)
            if [ "$CONTAINER_STATUS" = "running" ]; then
                check "${SVC_TYPE} 容器" 0 "${SVC_CONTAINER} 运行中"
            elif [ -n "$CONTAINER_STATUS" ]; then
                check "${SVC_TYPE} 容器" 1 "${SVC_CONTAINER} 状态: ${CONTAINER_STATUS}"
                continue
            fi
        fi

        if verify_db_connection "$SVC_TYPE" "$SVC_PORT" "$SVC_CONTAINER"; then
            check "${SVC_TYPE} 连接验证" 0 "服务可用"
        else
            check "${SVC_TYPE} 连接验证" 2 "端口开放但服务未就绪"
        fi
    done
fi

# 3. Docker 环境检查
detail ""
detail " ${CYAN}[Docker 环境]${NC}"

RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}' 2>/dev/null | grep "setup_${PROJECT_NAME}" || true)
RUNNING_COUNT=0
[ -n "$RUNNING_CONTAINERS" ] && RUNNING_COUNT=$(echo "$RUNNING_CONTAINERS" | wc -l)

if [ "$RUNNING_COUNT" -gt 0 ]; then
    check "运行中容器" 0 "${RUNNING_COUNT} 个"
else
    check "运行中容器" 0 "无 Docker 容器（可能是本地部署）"
fi

EXITED_CONTAINERS=$(docker ps -a --filter "status=exited" --format '{{.Names}}' 2>/dev/null | grep "setup_${PROJECT_NAME}" || true)
EXITED_COUNT=0
[ -n "$EXITED_CONTAINERS" ] && EXITED_COUNT=$(echo "$EXITED_CONTAINERS" | wc -l)

[ "$EXITED_COUNT" -gt 0 ] && check "崩溃容器" 1 "${EXITED_COUNT} 个已退出"

SETUP_NET="setup_net_${PROJECT_NAME}"
if docker network inspect "$SETUP_NET" >/dev/null 2>&1; then
    check "Docker 网络" 0 "${SETUP_NET} 存在"
else
    check "Docker 网络" 2 "${SETUP_NET} 不存在（可能是本地部署）"
fi

# 4. 系统资源
detail ""
detail " ${CYAN}[系统资源]${NC}"

DISK_PCT=$(df / | awk 'NR==2{print $5}' | tr -d '%')
DISK_AVAIL=$(df -h / | awk 'NR==2{print $4}')
[ "$DISK_PCT" -gt 90 ] && check "磁盘空间" 2 "可用 ${DISK_AVAIL} (${DISK_PCT}% 已用)" || check "磁盘空间" 0 "可用 ${DISK_AVAIL}"

MEM_AVAIL=$(free -h 2>/dev/null | awk '/Mem:/{print $7}' || echo "未知")
check "可用内存" 0 "${MEM_AVAIL}"

# GPU 检查（ML 项目有用）
if nvidia-smi >/dev/null 2>&1; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader 2>/dev/null | head -1)
    check "GPU" 0 "${GPU_INFO}"
fi

# ── 最终结果 ──

if [ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ]; then
    STATUS="READY"
elif [ "$FAIL" -eq 0 ]; then
    STATUS="PARTIAL"
else
    STATUS="FAILED"
fi

if [ "$QUIET" = "true" ]; then
    echo "HEALTH_STATUS=${STATUS}"
    echo "HEALTH_PASS=${PASS}"
    echo "HEALTH_FAIL=${FAIL}"
    echo "HEALTH_WARN=${WARN}"
    [ "$FAIL" -gt 0 ] && { echo "FAILURES:"; printf '  %s\n' "${FAILURE_MSGS[@]}"; }
    [ "$WARN" -gt 0 ] && { echo "WARNINGS:"; printf '  %s\n' "${WARN_MSGS[@]}"; }
else
    echo ""
    echo "========================================="
    if [ "$STATUS" = "READY" ]; then
        echo -e " 结果: ${GREEN}✅ READY${NC} (${PASS} 项通过)"
    elif [ "$STATUS" = "PARTIAL" ]; then
        echo -e " 结果: ${YELLOW}⚠️  PARTIAL${NC} (${PASS} 通过, ${WARN} 警告)"
    else
        echo -e " 结果: ${RED}❌ FAILED${NC} (${PASS} 通过, ${FAIL} 失败, ${WARN} 警告)"
    fi
    echo "========================================="
    echo ""
fi

exit $FAIL
