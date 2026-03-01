# Docker 镜像检查与拉取

当需要使用任何 Docker 镜像时，用此函数确保镜像可用。

---

## ensure_image 函数

先查本地，本地没有再拉远程，远程失败则尝试国内备用源：

```bash
ensure_image() {
    local image="$1"

    if docker image inspect "$image" > /dev/null 2>&1; then
        echo "✅ 本地已有镜像: $image"
        return 0
    fi

    echo "⬇️  拉取: $image"
    if docker pull "$image" 2>/dev/null; then
        echo "✅ 拉取成功: $image"
        return 0
    fi

    echo "⚠️  默认源失败，尝试备用源..."
    local short_name
    short_name=$(echo "$image" | sed 's|.*/||')

    local mirrors=(
        "registry.cn-hangzhou.aliyuncs.com/library/${short_name}"
        "docker.mirrors.ustc.edu.cn/library/${short_name}"
    )

    for mirror_image in "${mirrors[@]}"; do
        if docker pull "$mirror_image" 2>/dev/null; then
            docker tag "$mirror_image" "$image"
            echo "✅ 通过备用源拉取成功: $image"
            return 0
        fi
    done

    echo "❌ 无法获取镜像: $image" >&2
    return 1
}
```

只在实际需要对应镜像时调用，不要预拉取不需要的镜像。
