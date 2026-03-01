#!/bin/bash
# setup_python_env.sh - 创建并配置 Python 环境
#
# 用法:
#   bash scripts/setup_python_env.sh --type conda --name myenv --project /path/to/project [--yml environment.yml] [--python 3.10]
#   bash scripts/setup_python_env.sh --type venv  --path /path/to/venv --project /path/to/project
#
# 功能:
#   1. 创建 conda/venv 环境
#   2. 安装依赖（requirements.txt / pyproject.toml / setup.py / Pipfile）
#   3. 每步安装前自动验证环境
#
# 不做的事:
#   - 不装 ML/GPU 相关包（由 install_ml_deps.sh 处理）
#   - 不做数据库迁移（由 agent 根据框架判断）
#   - 不启动应用
#
# 返回值: 0=成功, 1=失败
# 最后输出: ENV_READY=<conda:name|venv:path>

set -e

# ── 参数解析 ──

ENV_TYPE=""
ENV_NAME=""
VENV_PATH=""
PROJECT_DIR=""
YML_FILE=""
PYTHON_VER="3.10"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --type)    ENV_TYPE="$2";    shift 2 ;;
        --name)    ENV_NAME="$2";    shift 2 ;;
        --path)    VENV_PATH="$2";   shift 2 ;;
        --project) PROJECT_DIR="$2"; shift 2 ;;
        --yml)     YML_FILE="$2";    shift 2 ;;
        --python)  PYTHON_VER="$2";  shift 2 ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

if [ -z "$PROJECT_DIR" ]; then
    echo "❌ 必须指定 --project"
    exit 1
fi

# ── 加载环境守卫 ──

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/env_guard.sh"

# ── 辅助函数 ──

guard() {
    if [ "$ENV_TYPE" = "conda" ]; then
        ensure_in_env conda "$ENV_NAME" || { echo "❌ 环境丢失，中止"; exit 1; }
    elif [ "$ENV_TYPE" = "venv" ]; then
        ensure_in_env venv "$VENV_PATH" || { echo "❌ 环境丢失，中止"; exit 1; }
    fi
}

install_pip_deps() {
    guard
    cd "$PROJECT_DIR"

    if [ -f requirements.txt ]; then
        echo "📦 pip install -r requirements.txt"
        pip install -r requirements.txt
    elif [ -f pyproject.toml ]; then
        echo "📦 pip install -e . (pyproject.toml)"
        pip install -e .
    elif [ -f setup.py ]; then
        echo "📦 pip install -e . (setup.py)"
        pip install -e .
    elif [ -f Pipfile ]; then
        echo "📦 pipenv install"
        pip install pipenv && pipenv install --system
    else
        echo "ℹ️ 未找到 Python 依赖文件"
    fi
}

# ── 创建环境 ──

cd "$PROJECT_DIR"

if [ "$ENV_TYPE" = "conda" ]; then

    if [ -z "$ENV_NAME" ]; then
        echo "❌ conda 模式必须指定 --name"
        exit 1
    fi

    # 自动检测 python 版本
    if [ -f .python-version ]; then
        PYTHON_VER=$(head -1 .python-version | tr -d '[:space:]')
        echo "ℹ️ 从 .python-version 读取: Python ${PYTHON_VER}"
    fi

    if [ -n "$YML_FILE" ] && [ -f "$YML_FILE" ]; then
        # 从 yml 创建
        echo "📦 conda env create -f ${YML_FILE} -n ${ENV_NAME}"
        echo "   可能需要 5-15 分钟..."
        conda env remove -n "$ENV_NAME" -y 2>/dev/null || true
        conda env create -f "$YML_FILE" -n "$ENV_NAME"
    else
        # 空环境
        echo "📦 conda create -n ${ENV_NAME} python=${PYTHON_VER}"
        conda env remove -n "$ENV_NAME" -y 2>/dev/null || true
        conda create -n "$ENV_NAME" python="${PYTHON_VER}" -y
    fi

    conda activate "$ENV_NAME"
    guard

    # yml 可能不包含所有 pip 依赖
    install_pip_deps

elif [ "$ENV_TYPE" = "venv" ]; then

    if [ -z "$VENV_PATH" ]; then
        VENV_PATH="${PROJECT_DIR}/venv"
    fi

    echo "📦 python3 -m venv ${VENV_PATH}"
    python3 -m venv "$VENV_PATH"
    source "${VENV_PATH}/bin/activate"
    guard

    pip install --upgrade pip
    guard

    install_pip_deps

else
    echo "❌ --type 必须是 conda 或 venv"
    exit 1
fi

# ── 完成 ──

guard
echo ""
echo "✅ Python 环境就绪"
python --version
echo "   pip packages: $(pip list --format=columns 2>/dev/null | wc -l) 个"

if [ "$ENV_TYPE" = "conda" ]; then
    echo "ENV_READY=conda:${ENV_NAME}"
else
    echo "ENV_READY=venv:${VENV_PATH}"
fi
