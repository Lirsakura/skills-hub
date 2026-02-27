---
name: pull
description: 从 GitHub 拉取最新代码。展示将要拉取的内容，用户确认后执行 pull。
---

# Pull 流程

## 1. 获取远端信息

```bash
cd [仓库路径]
git fetch origin
```

查看有哪些新提交：

```bash
git log HEAD..origin/[分支名] --oneline
```

将结果展示给用户，格式：

```
📂 仓库：[路径]
🌿 分支：[当前分支]

⬇️ 远端有 X 个新提交：
  def5678  add new attraction skill
  abc1234  fix typo in destination-explore
```

如果没有新提交：
```
✅ 本地已是最新，无需拉取。
```

## 2. 检查本地状态

如果本地有未提交的改动，提醒用户：

```bash
git status --short
```

如果有改动，告知：
```
⚠️  本地有未提交的改动，pull 可能会产生冲突：
  [列出改动文件]

建议：
1. 先推送本地改动，再拉取
2. 或先 stash 暂存：git stash
3. 或直接继续（可能需要手动解决冲突）

如何处理？
```

等用户选择后再继续。

## 3. 确认

```
准备从 origin/[分支名] 拉取 X 个新提交，确认吗？
```

## 4. 执行 Pull

```bash
cd [仓库路径]
git pull origin [分支名]
```

### 成功输出

```
✅ 拉取成功！

📥 已同步 X 个新提交
📄 更新了以下文件：
  [git show --stat 的输出，简化版]
```

### 失败处理

**网络错误** → 询问代理端口，然后：
```bash
https_proxy=http://127.0.0.1:[PORT] git pull origin [分支名]
```

**合并冲突** → 列出冲突文件，提示：
```
⚠️  产生了合并冲突，需要手动解决：
  [冲突文件列表]

解决冲突后，运行：
  git add -A
  git commit
```

## 5. 记录日志

Pull 完成后调用 `sync-log` skill 写入日志。
