---
name: sync-log
description: 记录每次 push/pull 操作到本地日志文件，用于溯源。在每次同步操作完成后调用。
---

# 同步日志记录

## 日志位置

- 默认路径：仓库根目录下的 `sync-logs/` 文件夹
- 文件命名：`YYYY-MM.md`（按月分文件）
- 示例：`sync-logs/2026-02.md`
- **日志只保留在本地，不上传 GitHub**

## 初始化（首次使用时）

**第一步：确保 `sync-logs/` 在 `.gitignore` 中**

```bash
cd [仓库路径]
grep -q "sync-logs/" .gitignore 2>/dev/null || echo "sync-logs/" >> .gitignore
```

如果 `.gitignore` 不存在，会自动创建并写入。

> ⚠️ 这一步必须在第一次写日志前执行，确保日志目录永远不会被 git 追踪。

**第二步：创建日志目录**

```bash
mkdir -p [仓库路径]/sync-logs
```

## 获取日志所需信息

```bash
# 当前 commit hash（短）
git rev-parse --short HEAD

# 上次 commit hash（短）
git rev-parse --short HEAD~1

# 本次 commit 的改动文件列表
git show --stat --format="" HEAD

# 当前分支
git branch --show-current

# 当前时间（由 AI 从系统获取）
date "+%Y-%m-%d %H:%M"
```

对于 pull 操作，"本次"和"上次"的含义：
- 上次 = pull 之前本地的 HEAD（需在 pull 前记录）
- 本次 = pull 之后的 HEAD

## 日志条目格式

每次追加到当月文件末尾：

```markdown
## [YYYY-MM-DD HH:MM] | [Push/Pull] | [✅ 成功 / ❌ 失败]

- **仓库**: [仓库路径]
- **分支**: [分支名]
- **上次 commit**: `[hash]` [上次 commit message 的第一行]
- **本次 commit**: `[hash]` [本次 commit message 的第一行]
- **改动文件** ([N] 个):
  - `[状态]` [文件路径]
  - `[状态]` [文件路径]

---
```

**状态标记：**
- `A` = 新增文件
- `M` = 修改文件
- `D` = 删除文件
- `R` = 重命名文件

**失败时的格式：**

```markdown
## [YYYY-MM-DD HH:MM] | [Push/Pull] | ❌ 失败

- **仓库**: [仓库路径]
- **分支**: [分支名]
- **失败原因**: [错误信息简述，如：网络超时 / 认证失败 / 合并冲突]
- **处理结果**: [用户选择了什么，如：走代理重试成功 / 用户取消]

---
```

## 注意事项

1. **改动文件最多列 10 个**，超过则写 `...以及其他 N 个文件`
2. **commit message 只取第一行**（不超过 60 字）
3. 日志只追加，不修改历史记录
4. 如果是 pull 操作且没有新内容，不写日志（`Already up to date` 忽略）

## 写入方法

使用 write/edit 工具追加到日志文件。

如果当月文件不存在，先写入文件头：

```markdown
# Sync Log — [YYYY 年 MM 月]

> 记录每次 GitHub 同步操作，用于改动溯源。

---

```

然后追加本次条目。
