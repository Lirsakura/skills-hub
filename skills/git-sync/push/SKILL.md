---
name: push
description: 将本地改动推送到 GitHub。展示改动内容，生成 commit message，用户确认后执行 push。
---

# Push 流程

## 1. 查看本地改动

```bash
cd [仓库路径]
git status --short
git diff --stat HEAD
```

将结果展示给用户，格式：

```
📂 仓库：[路径]
🌿 分支：[当前分支]

📝 改动文件（共 X 个）：
  M  skills/travel-agent/food/SKILL.md
  A  skills/git-sync/push/SKILL.md
  D  old-file.md
```

如果没有任何改动（`nothing to commit`），告知用户并停止：
```
✅ 没有需要推送的改动，本地已是最新。
```

## 2. 生成 Commit Message

读取完整 diff 内容生成简洁的 commit message：

```bash
git diff HEAD
```

**Commit message 规范：**
- 用中文或英文（跟随用户语言）
- 一行主标题（50字以内），概括做了什么
- 如果改动较多，加一行空行后列出要点（最多3条）

示例：
```
update travel-agent skills: fix hallucination risks in food/hotel

- remove phone/rating fields from food and hotel templates
- fix corrupted character in photo-style Tokyo section
- add query guidance for real-time data
```

## 3. 确认

向用户展示：

```
📋 准备推送以下改动：

[改动文件列表]

💬 Commit message：
"[生成的 message]"

确认推送吗？（可以修改 commit message）
```

等待用户确认。如果用户想修改 message，使用用户提供的版本。

## 4. 执行 Push

> 如果 `.gitignore` 刚被修改过（首次添加 `sync-logs/`），它会一并被提交，这是正常的。

```bash
cd [仓库路径]
git add -A
git commit -m "[commit message]"
git push origin [分支名]
```

### 成功输出

```
✅ 推送成功！

🔗 commit：[git rev-parse --short HEAD 的输出]
📤 已推送到 origin/[分支名]
```

### 失败处理

**网络错误** → 询问代理端口，然后：
```bash
https_proxy=http://127.0.0.1:[PORT] git push origin [分支名]
```

**认证失败** → 提示检查 GitHub Token 或 SSH 配置

**冲突/rejected** → 建议先 pull：
```
推送被拒绝，可能是远端有新的提交。建议先执行 pull 合并，再推送。
```

## 5. 记录日志

Push 完成后调用 `sync-log` skill 写入日志。
