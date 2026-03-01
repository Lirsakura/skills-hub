# Contributing to Skill Hub

**[中文](#中文)** · **[English](#english)**

---

<a name="中文"></a>

## 中文

感谢你对 Skill Hub 的关注！欢迎提交 Issue 和 Pull Request。

在提交之前，请花几分钟读完这份指南。

### 这个项目接受什么

Skill Hub 的定位是 **轻量级 Markdown SOP**——用纯文本文件给 AI Agent 写操作手册。

**我们欢迎：**

- 新的 Skill（Markdown 编写的 Agent 操作流程）
- 对现有 Skill 的改进（修复流程缺陷、补充边界情况处理）
- Bug 报告和使用反馈（Issue）
- 文档改进

**我们不接受：**

- 大型 Python/Node.js 框架或运行时依赖
- 预编译的二进制文件（`.pyc`、`.so`、`.exe`、`.whl` 等）
- 需要完整系统权限的脚本（除非有充分理由）
- 与第三方商业平台强绑定的集成
- 与项目定位不符的内容

### 提交流程

> **重要：请先开 Issue 讨论，对齐方向后再动手写代码。**
> 直接提交大型 PR 而没有事先沟通，大概率会被关闭。

1. **开 Issue** — 描述你想做什么、为什么、大致思路
2. **等待回复** — maintainer 确认方向可行后再开始
3. **Fork & 分支** — 基于 `main` 创建功能分支：`git checkout -b feat/your-skill-name`
4. **编写 Skill** — 确保符合下面的规范
5. **提交 PR** — 按模板填写说明，关联对应的 Issue

### Skill 文件规范

一个 Skill 由两部分组成：

```
agents/<skill-name>.md              # Agent 入口（简短，描述能力和工具权限）
skills/<skill-name>/
├── SKILL.md                        # 主流程文件（必须）
├── <子模块>/                        # 按需拆分的模块（可选）
│   └── *.md
├── scripts/                        # 辅助脚本（可选，仅限 shell）
│   └── *.sh
└── reference/                      # 参考数据（可选，JSON/YAML）
    └── *.json
```

**命名规范：**

- Skill 名使用 **英文小写 + 连字符**：`env-setup`、`code-review`
- 文件名使用英文，避免中文或 Unicode 字符

**质量标准：**

1. **明确的角色定义** — 开头说清楚"你是谁、你做什么"
2. **结构化的工作流程** — 分步骤执行，每步有清晰的输入输出
3. **具体的操作策略** — 给出实际的命令和模板，不要模糊指令
4. **错误处理** — 每一步出错了怎么回退、怎么重试
5. **输出格式** — 明确最终交付物的格式
6. **质量红线** — 定义什么是不可接受的输出

**工具权限最小化：**

在 Agent 入口文件中，**只声明你实际需要的工具**。不要无脑全开：

```yaml
# 好 — 只要需要的
tools:
  read: true
  websearch: true
  fetch: true

# 不好 — 全开
tools:
  read: true
  write: true
  edit: true
  bash: true
  fetch: true
  websearch: true
```

### 不允许提交的文件

| 类型 | 示例 | 原因 |
|------|------|------|
| 编译产物 | `.pyc`, `.class`, `.o`, `.so` | 无法 review，可能包含恶意代码 |
| 依赖目录 | `node_modules/`, `venv/`, `__pycache__/` | 不应纳入版本控制 |
| 敏感信息 | `.env`, `credentials.json`, API keys | 安全风险 |
| 大型二进制 | 图片、视频、模型权重 | 仓库体积 |

### Commit 规范

```
feat: 添加 xxx skill
fix: 修复 env-setup 中的 xxx 问题
docs: 更新 README
refactor: 重构 xxx 模块
```

一个 PR 只做一件事。不要混合多个不相关的改动。

### 行为准则

- 尊重每个贡献者
- 建设性的反馈，就事论事
- 不提交恶意或有害的 Skill
- 不修改其他人的 Skill（除非是修 bug 并在 Issue 中说明）

如果你不确定某个想法是否合适，直接开 Issue 聊就行。

---

<a name="english"></a>

## English

Thanks for your interest in Skill Hub! Issues and Pull Requests are welcome.

Please take a few minutes to read this guide before submitting.

### What We Accept

Skill Hub is a collection of **lightweight Markdown SOPs** — plain-text operation manuals for AI Agents.

**We welcome:**

- New Skills (Agent workflows written in Markdown)
- Improvements to existing Skills (fixing workflow gaps, handling edge cases)
- Bug reports and feedback (Issues)
- Documentation improvements

**We do NOT accept:**

- Large Python/Node.js frameworks or runtime dependencies
- Pre-compiled binaries (`.pyc`, `.so`, `.exe`, `.whl`, etc.)
- Scripts requiring full system permissions (unless well-justified)
- Tight integrations with third-party commercial platforms
- Content that doesn't fit the project's scope

### Submission Process

> **Important: Open an Issue first to discuss your idea before writing code.**
> Large PRs submitted without prior discussion will likely be closed.

1. **Open an Issue** — Describe what you want to do, why, and your general approach
2. **Wait for feedback** — A maintainer will confirm the direction is viable
3. **Fork & branch** — Create a feature branch from `main`: `git checkout -b feat/your-skill-name`
4. **Write the Skill** — Follow the specifications below
5. **Submit a PR** — Fill in the template and link the corresponding Issue

### Skill File Structure

A Skill consists of two parts:

```
agents/<skill-name>.md              # Agent entry (brief, describes capabilities and tool permissions)
skills/<skill-name>/
├── SKILL.md                        # Main workflow file (required)
├── <submodules>/                   # Split modules as needed (optional)
│   └── *.md
├── scripts/                        # Helper scripts (optional, shell only)
│   └── *.sh
└── reference/                      # Reference data (optional, JSON/YAML)
    └── *.json
```

**Naming conventions:**

- Skill names use **lowercase English + hyphens**: `env-setup`, `code-review`
- File names must be in English — avoid CJK or Unicode characters

**Quality standards:**

1. **Clear role definition** — State upfront who you are and what you do
2. **Structured workflow** — Step-by-step execution with clear inputs/outputs
3. **Concrete strategies** — Provide actual commands and templates, not vague instructions
4. **Error handling** — How to roll back and retry at each step
5. **Output format** — Define the expected deliverables clearly
6. **Quality gates** — Define what constitutes unacceptable output

**Minimal tool permissions:**

In the Agent entry file, **only declare the tools you actually need**:

```yaml
# Good — only what's needed
tools:
  read: true
  websearch: true
  fetch: true

# Bad — everything enabled
tools:
  read: true
  write: true
  edit: true
  bash: true
  fetch: true
  websearch: true
```

### Prohibited Files

| Type | Examples | Reason |
|------|----------|--------|
| Compiled artifacts | `.pyc`, `.class`, `.o`, `.so` | Cannot be reviewed, may contain malicious code |
| Dependency dirs | `node_modules/`, `venv/`, `__pycache__/` | Should not be version-controlled |
| Sensitive data | `.env`, `credentials.json`, API keys | Security risk |
| Large binaries | Images, videos, model weights | Repository bloat |

### Commit Convention

```
feat: add xxx skill
fix: fix xxx issue in env-setup
docs: update README
refactor: refactor xxx module
```

One PR = one thing. Don't mix unrelated changes.

### Code of Conduct

- Respect every contributor
- Provide constructive, objective feedback
- Do not submit malicious or harmful Skills
- Do not modify other people's Skills (unless fixing a bug with an Issue explaining why)

If you're not sure whether an idea fits, just open an Issue and let's talk.
