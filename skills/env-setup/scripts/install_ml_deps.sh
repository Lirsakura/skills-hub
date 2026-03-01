#!/bin/bash
# install_ml_deps.sh - 安装 ML/AI 依赖（PyTorch / TensorFlow）
#
# 用法:
#   bash scripts/install_ml_deps.sh --type conda --name myenv --project /path/to/project
#   bash scripts/install_ml_deps.sh --type venv  --path /path/to/venv --project /path/to/project
#
# 行为:
#   1. 检测 GPU 和 CUDA 版本
#   2. 检测项目需要 torch 还是 tensorflow
#   3. 有 GPU → 只装 GPU 版，失败则输出 GPU_INSTALL_FAILED 让 agent 问用户
#   4. 无 GPU → 输出 NO_GPU_DETECTED 让 agent 问用户
#   5. 安装后验证 CUDA 可用性
#
# ⚠️ 不会自动降级到 CPU 版！降级需要用户确认。
#
# 返回值:
#   0 = GPU 版安装成功且验证通过
#   1 = 需要用户介入（看 stdout 最后一行的状态码）
#
# 状态码（stdout 最后一行）:
#   ML_GPU_OK              - GPU 版安装成功
#   ML_NO_GPU              - 未检测到 GPU，需用户确认装 CPU 版
#   ML_GPU_INSTALL_FAILED  - GPU 版安装失败，需用户确认是否降级 CPU
#   ML_GPU_VERIFY_FAILED   - 安装了但 CUDA 不可用，需用户确认
#   ML_NO_ML_DEPS          - 项目不需要 ML 依赖

set -e

# ── 参数解析 ──

ENV_TYPE=""
ENV_NAME=""
VENV_PATH=""
PROJECT_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --type)    ENV_TYPE="$2";    shift 2 ;;
        --name)    ENV_NAME="$2";    shift 2 ;;
        --path)    VENV_PATH="$2";   shift 2 ;;
        --project) PROJECT_DIR="$2"; shift 2 ;;
        *) shift ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/env_guard.sh"

guard() {
    if [ "$ENV_TYPE" = "conda" ]; then
        ensure_in_env conda "$ENV_NAME" || exit 1
    else
        ensure_in_env venv "$VENV_PATH" || exit 1
    fi
}

cd "$PROJECT_DIR"

# ── 检测项目需要什么 ──

NEEDS_TORCH=false
NEEDS_TF=false

grep -qi "torch\|torchvision" requirements*.txt pyproject.toml setup.py 2>/dev/null && NEEDS_TORCH=true
grep -qi "tensorflow" requirements*.txt pyproject.toml setup.py 2>/dev/null && NEEDS_TF=true

if [ "$NEEDS_TORCH" = "false" ] && [ "$NEEDS_TF" = "false" ]; then
    echo "ℹ️ 项目不需要 PyTorch/TensorFlow"
    echo "ML_NO_ML_DEPS"
    exit 0
fi

echo "检测到 ML 依赖: torch=${NEEDS_TORCH} tensorflow=${NEEDS_TF}"

# ── 检测 GPU ──

if ! nvidia-smi >/dev/null 2>&1; then
    echo ""
    echo "⚠️ 未检测到 GPU（nvidia-smi 不可用）"
    echo "   该项目依赖 ML 框架，没有 GPU 训练/推理会非常慢。"
    echo ""
    echo "   可能的情况："
    echo "   1. 确实没有 GPU → 需要你确认后安装 CPU 版本"
    echo "   2. 有 GPU 但驱动没装好 → 先装 NVIDIA 驱动再继续"
    echo ""
    echo "ML_NO_GPU"
    exit 1
fi

# ── 有 GPU ──

CUDA_VERSION=$(nvidia-smi | grep -oP 'CUDA Version: \K[\d.]+' | cut -d. -f1-2)
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)

echo ""
echo "🖥️ GPU: ${GPU_NAME} (${GPU_MEM}MiB)"
echo "   CUDA: ${CUDA_VERSION}"
echo "   正在安装 GPU 版本..."
echo ""

guard

# ── PyTorch GPU ──

if [ "$NEEDS_TORCH" = "true" ]; then
    echo "📦 安装 PyTorch GPU (CUDA ${CUDA_VERSION})..."
    guard

    if [ "$ENV_TYPE" = "conda" ]; then
        if ! conda install pytorch torchvision torchaudio pytorch-cuda="${CUDA_VERSION}" -c pytorch -c nvidia -y 2>&1; then
            echo ""
            echo "❌ PyTorch GPU 版安装失败 (CUDA ${CUDA_VERSION})"
            echo "   可能原因：CUDA 版本不兼容 / conda 源缺少对应版本"
            echo "ML_GPU_INSTALL_FAILED:torch:cuda${CUDA_VERSION}"
            exit 1
        fi
    else
        # venv 用 pip
        if ! pip install torch torchvision torchaudio --index-url "https://download.pytorch.org/whl/cu${CUDA_VERSION//./}" 2>&1; then
            echo ""
            echo "❌ PyTorch GPU 版 pip 安装失败"
            echo "ML_GPU_INSTALL_FAILED:torch:cuda${CUDA_VERSION}"
            exit 1
        fi
    fi

    # 验证
    guard
    echo "🔍 验证 PyTorch CUDA..."
    GPU_CHECK=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "Error")

    if [ "$GPU_CHECK" = "True" ]; then
        VRAM=$(python -c "import torch; print(f'{torch.cuda.get_device_properties(0).total_mem/1024**3:.1f}GB')" 2>/dev/null)
        echo "  ✅ PyTorch CUDA 可用 (显存 ${VRAM})"
    else
        echo "  ❌ PyTorch 已安装但 torch.cuda.is_available()=False"
        echo "  可能是 CUDA toolkit 版本与驱动不匹配"
        echo "ML_GPU_VERIFY_FAILED:torch"
        exit 1
    fi
fi

# ── TensorFlow GPU ──

if [ "$NEEDS_TF" = "true" ]; then
    echo "📦 安装 TensorFlow GPU..."
    guard

    if [ "$ENV_TYPE" = "conda" ]; then
        if ! conda install tensorflow-gpu -y 2>&1; then
            echo "❌ TensorFlow GPU 版安装失败"
            echo "ML_GPU_INSTALL_FAILED:tensorflow:cuda${CUDA_VERSION}"
            exit 1
        fi
    else
        if ! pip install tensorflow 2>&1; then
            echo "❌ TensorFlow 安装失败"
            echo "ML_GPU_INSTALL_FAILED:tensorflow:cuda${CUDA_VERSION}"
            exit 1
        fi
    fi

    # 验证
    guard
    echo "🔍 验证 TensorFlow GPU..."
    TF_GPUS=$(python -c "import tensorflow as tf; print(len(tf.config.list_physical_devices('GPU')))" 2>/dev/null || echo "0")

    if [ "$TF_GPUS" -gt 0 ] 2>/dev/null; then
        echo "  ✅ TensorFlow 检测到 ${TF_GPUS} 个 GPU"
    else
        echo "  ❌ TensorFlow 未检测到 GPU"
        echo "ML_GPU_VERIFY_FAILED:tensorflow"
        exit 1
    fi
fi

echo ""
echo "✅ ML GPU 依赖安装完成"
echo "ML_GPU_OK"
