#!/bin/bash
# env_guard.sh - 环境守卫
#
# 用法（两种模式）:
#
#   1. source 模式（定义函数供后续调用）:
#      source scripts/env_guard.sh
#      ensure_in_env conda myenv
#      pip install xxx
#
#   2. 独立检查模式:
#      bash scripts/env_guard.sh conda myenv
#      bash scripts/env_guard.sh venv /path/to/venv
#
# 返回值: 0=环境正确, 1=环境错误且修复失败

ensure_in_env() {
    local env_type="$1"   # conda 或 venv
    local env_id="$2"     # conda 环境名 或 venv 路径

    if [ -z "$env_type" ] || [ -z "$env_id" ]; then
        echo "❌ ensure_in_env: 缺少参数 (env_type, env_id)"
        return 1
    fi

    if [ "$env_type" = "conda" ]; then
        # 获取当前激活的 conda 环境
        local current_env
        current_env=$(basename "${CONDA_PREFIX:-}" 2>/dev/null)

        if [ "$current_env" = "$env_id" ]; then
            echo "✓ conda:${env_id} | python:$(which python)"
            return 0
        fi

        echo "⚠️ 环境漂移！当前: ${current_env:-base}，应为: $env_id"
        echo "   正在重新激活..."
        conda activate "$env_id" 2>/dev/null

        current_env=$(basename "${CONDA_PREFIX:-}" 2>/dev/null)
        if [ "$current_env" = "$env_id" ]; then
            echo "✓ 已恢复 conda:${env_id} | python:$(which python)"
            return 0
        else
            echo "❌ conda activate $env_id 失败"
            return 1
        fi

    elif [ "$env_type" = "venv" ]; then
        if [ "$VIRTUAL_ENV" = "$env_id" ]; then
            echo "✓ venv:${env_id} | python:$(which python)"
            return 0
        fi

        echo "⚠️ 环境漂移！当前: ${VIRTUAL_ENV:-无}，应为: $env_id"
        echo "   正在重新激活..."

        if [ ! -f "${env_id}/bin/activate" ]; then
            echo "❌ venv 不存在: ${env_id}/bin/activate"
            return 1
        fi

        source "${env_id}/bin/activate"
        if [ "$VIRTUAL_ENV" = "$env_id" ]; then
            echo "✓ 已恢复 venv:${env_id} | python:$(which python)"
            return 0
        else
            echo "❌ venv activate 失败"
            return 1
        fi
    else
        echo "❌ 未知环境类型: $env_type（应为 conda 或 venv）"
        return 1
    fi
}

# 独立运行模式
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    ensure_in_env "$@"
fi
