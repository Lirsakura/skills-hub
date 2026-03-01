#!/bin/bash
# install_conda.sh - 安装 Miniforge (conda)
#
# 用法:
#   bash scripts/install_conda.sh [安装路径]
#
# 默认安装到 ~/miniforge3
# 安装后在当前 shell 中可用（不修改 .bashrc）
#
# 返回值: 0=成功, 1=失败
# 输出: 最后一行是 CONDA_PATH=<路径>（供调用方 eval）

set -e

INSTALL_DIR="${1:-$HOME/miniforge3}"
ARCH=$(uname -m)
OS=$(uname -s)

echo "📦 正在安装 Miniforge → ${INSTALL_DIR}"
echo "   预计需要 2-5 分钟..."

# ── 下载 ──

INSTALLER="/tmp/miniforge_installer_$$.sh"

PRIMARY_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-${OS}-${ARCH}.sh"
MIRROR_URL="https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-${OS}-${ARCH}.sh"

download_ok=false
for url in "$PRIMARY_URL" "$MIRROR_URL"; do
    echo "   尝试: $url"
    if curl -fSL --connect-timeout 10 --max-time 300 -o "$INSTALLER" "$url" 2>&1; then
        download_ok=true
        break
    fi
done

if [ "$download_ok" = "false" ]; then
    echo "❌ Miniforge 下载失败"
    rm -f "$INSTALLER"
    exit 1
fi

# ── 安装 ──

bash "$INSTALLER" -b -p "$INSTALL_DIR"
rm -f "$INSTALLER"

# ── 初始化（当前 shell） ──

eval "$("${INSTALL_DIR}/bin/conda" shell.bash hook)"

# ── 配置国内镜像 ──

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
conda config --set show_channel_urls yes

echo "✅ Miniforge 安装完成: $(conda --version)"
echo "CONDA_PATH=${INSTALL_DIR}"
