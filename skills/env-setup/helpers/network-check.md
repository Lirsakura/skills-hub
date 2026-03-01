# 网络检测与代理处理

在 clone 项目或任何网络操作之前，先执行本文件中的检测。

---

## 第一步：检测现有代理配置

```bash
check_proxy() {
    # 检查环境变量
    if [ -n "$http_proxy" ] || [ -n "$https_proxy" ] || [ -n "$HTTP_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
        echo "✅ 检测到代理配置:"
        [ -n "$http_proxy" ]  && echo "  http_proxy=$http_proxy"
        [ -n "$https_proxy" ] && echo "  https_proxy=$https_proxy"
        [ -n "$HTTP_PROXY" ]  && echo "  HTTP_PROXY=$HTTP_PROXY"
        [ -n "$HTTPS_PROXY" ] && echo "  HTTPS_PROXY=$HTTPS_PROXY"
        return 0
    fi

    # 检查 git 全局代理
    GIT_PROXY=$(git config --global http.proxy 2>/dev/null)
    if [ -n "$GIT_PROXY" ]; then
        echo "✅ 检测到 git 代理: $GIT_PROXY"
        return 0
    fi

    echo "ℹ️ 未检测到代理配置"
    return 1
}
```

---

## 第二步：网络连通性测试

```bash
test_connectivity() {
    echo "🔍 测试网络连通性..."

    # 测试 GitHub（国内最常超时的）
    GITHUB_OK=false
    if curl -s --connect-timeout 5 --max-time 10 -o /dev/null -w "%{http_code}" https://github.com 2>/dev/null | grep -qE "^(200|301|302)"; then
        GITHUB_OK=true
        echo "  ✅ GitHub 可直连"
    else
        echo "  ❌ GitHub 连接超时或不可达"
    fi

    # 测试国内站点（确认不是完全断网）
    DOMESTIC_OK=false
    if curl -s --connect-timeout 5 --max-time 10 -o /dev/null https://www.baidu.com 2>/dev/null; then
        DOMESTIC_OK=true
        echo "  ✅ 国内网络正常"
    else
        echo "  ❌ 国内网络也不通（可能完全断网）"
    fi

    # 诊断结论
    if [ "$GITHUB_OK" = "true" ]; then
        echo "📋 结论: 网络正常，可直接 clone"
        return 0
    elif [ "$DOMESTIC_OK" = "true" ]; then
        echo "📋 结论: 国内网络正常但 GitHub 不可达，需要代理或镜像"
        return 1
    else
        echo "📋 结论: 网络不通，请检查网络连接"
        return 2
    fi
}
```

---

## 第三步：Git Clone（带超时检测和自动回退）

```bash
safe_git_clone() {
    local url="$1"
    local dest="$2"
    local timeout=${3:-120}  # 默认 120 秒超时

    echo "📥 正在 clone: $url"

    # 尝试 1: 直接 clone
    if timeout ${timeout} git clone --depth 1 "$url" "$dest" 2>&1; then
        echo "✅ Clone 成功"
        return 0
    fi

    echo "⚠️ 直接 clone 失败，诊断网络..."

    # 检查是不是网络问题
    if ! curl -s --connect-timeout 5 -o /dev/null https://github.com 2>/dev/null; then
        echo "❌ 确认是网络问题（GitHub 不可达）"

        # 尝试 2: GitHub 镜像站
        local repo_path
        repo_path=$(echo "$url" | sed -E 's|https?://github\.com/||; s|\.git$||')

        local mirrors=(
            "https://ghfast.top/https://github.com/${repo_path}.git"
            "https://github.moeyy.xyz/https://github.com/${repo_path}.git"
            "https://gitclone.com/github.com/${repo_path}.git"
        )

        for mirror_url in "${mirrors[@]}"; do
            echo "  🔄 尝试镜像: $mirror_url"
            rm -rf "$dest" 2>/dev/null
            if timeout ${timeout} git clone --depth 1 "$mirror_url" "$dest" 2>&1; then
                # 修正 remote 指向原始地址
                cd "$dest" && git remote set-url origin "$url" && cd -
                echo "✅ 通过镜像 clone 成功"
                return 0
            fi
        done

        # 尝试 3: 询问用户代理
        echo ""
        echo "❌ 所有镜像都失败了。请配置代理后重试："
        echo ""
        echo "  方法 A: 设置环境变量"
        echo "    export https_proxy=http://127.0.0.1:<端口>"
        echo "    export http_proxy=http://127.0.0.1:<端口>"
        echo ""
        echo "  方法 B: 设置 git 代理"
        echo "    git config --global http.proxy http://127.0.0.1:<端口>"
        echo "    git config --global https.proxy http://127.0.0.1:<端口>"
        echo ""
        echo "  方法 C: 如果有 socks5 代理"
        echo "    git config --global http.proxy socks5://127.0.0.1:<端口>"
        echo ""
        echo "  配置好后告诉我，我会重新 clone。"
        return 1
    else
        # GitHub 能连但 clone 失败（可能是仓库不存在、权限问题等）
        echo "❌ GitHub 可达但 clone 失败，可能是仓库地址错误或需要认证"
        return 1
    fi
}
```

---

## 使用方式

agent 在 clone 之前按以下顺序调用：

```bash
# 1. 检查有没有现成的代理
check_proxy

# 2. 测试连通性
test_connectivity
NETWORK_STATUS=$?

# 3. 如果 GitHub 不通且没有代理，先提醒用户
if [ "$NETWORK_STATUS" -eq 1 ]; then
    echo "⚠️ GitHub 不可达，clone 时会自动尝试镜像站"
elif [ "$NETWORK_STATUS" -eq 2 ]; then
    echo "❌ 网络完全不通，请先检查网络连接"
    exit 1
fi

# 4. Clone（内部自动处理超时和镜像回退）
safe_git_clone "https://github.com/user/repo.git" "${SETUP_ROOT}/repo"
```

---

## 代理设置后的验证

用户配置代理后，用以下命令快速验证：

```bash
curl -s --connect-timeout 5 -o /dev/null -w "GitHub: HTTP %{http_code} (%{time_total}s)\n" https://github.com
git ls-remote --exit-code https://github.com/torvalds/linux.git HEAD >/dev/null 2>&1 && echo "✅ Git 代理生效" || echo "❌ Git 仍然不通"
```
