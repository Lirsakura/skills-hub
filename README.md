<div align="center">

# 🧠 Skill Hub

**开源 AI Agent Skill 社区 — 让 AI 真正会做事**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Platform](https://img.shields.io/badge/Platform-OpenCode-purple.svg)](https://opencode.ai)

[English](#english) · [中文](#中文)

</div>

---

## 中文

### 🤔 这是什么？

**Skill Hub** 是一个开源的 AI Agent Skill 仓库。

每个 Skill 是一份精心设计的 Markdown 指令文件，能让 AI 像专家一样完成特定任务——不是简单的 prompt，而是包含完整工作流、质量标准和错误处理的**专业级 Agent 方案**。

> 🎯 当前支持 [OpenCode](https://opencode.ai)，后续将扩展到 Claude Code、Cursor 等更多平台。

### ⚡ 30 秒上手

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/skill-hub.git

# 2. 复制你想要的 skill 到 OpenCode 配置目录
cp -r skill-hub/skills/advisor-agent ~/.config/opencode/skills/

# 3. 在 OpenCode 中直接使用
# "帮我查一下复旦大学的杨珉教授"
```

### 📦 可用 Skills

| Skill | 描述 | 适用场景 | 版本 |
|-------|------|----------|------|
| 🎓 [advisor-agent](skills/advisor-agent/) | 导师情报分析专家 | 查导师学术实力、口碑避雷、实验室生态 | v1 |
| 🔒 [code-auditor](skills/code-auditor/) | 白盒代码安全审计 | 深度安全审计：SQL注入、XSS、RCE、SSRF | v1 |
| ✈️ [travel-planner](skills/travel-planner/) | 旅行规划专家 | 从零规划旅行：行程、预算、穿搭、避坑 | v1 |

### 🎓 Advisor Agent — 导师情报分析专家

> **选错导师毁三年，这份报告帮你避坑。**

你是不是也有过这样的困惑：
- 想报某个导师的研究生，但不知道 TA 人怎么样？
- 网上信息散落在知乎、小红书、Reddit 各处，搜到累死也拼不出全貌？
- 听说有的导师很 push、不让毕业，但不知道是真是假？

Advisor Agent 帮你做一份完整的「导师尽职调查报告」：

**🔍 覆盖 11 个信息渠道**
- 研控 · PI Review · 知乎 · 小红书 · 一亩三分地 · RateMyProfessors · Reddit · GradCafe · PubPeer · 新闻媒体 · 官方通报

**📊 结构化输出**
- 学术实力评级（⭐1-5） + Top 5 论文
- 口碑避雷（🔴红旗 🟡黄旗 🟢绿旗）+ 可信度分级
- 实验室生态（学生去向、毕业年限、指导风格）
- 最终综合评估 + 行动建议

**🎯 多种使用模式**
```
"帮我查一下 MIT 的 XXX 教授"          → 完整调查报告
"XXX 导师有没有什么负面消息"          → 快速避雷
"对比 A 教授和 B 教授"                → 对比报告
"下周要面试 XXX 教授，帮我准备"       → 面试准备
```

**📁 提供三个版本**

| 版本 | 体量 | 适合 |
|------|------|------|
| 完整版（多子skill） | ~49K chars | Claude Opus/Sonnet 等大模型 |
| 精简版（多子skill） | ~11K chars | 中等参数模型 |
| 单文件版 | ~4K chars | 30B 以下本地模型 |

### 🔒 Code Auditor — 白盒安全审计专家

> **像人类安全研究员一样审计代码，不是正则匹配。**

- 6 阶段审计流程：代码接入 → 全量理解 → 深度分析 → 对抗验证 → 报告 → 协作
- 聚焦 5 大高危漏洞：SQLi / XSS / RCE / SSRF / 文件上传
- 跨文件数据流追踪 + 攻防对抗验证
- 输出可执行 PoC 的专业审计报告

### ✈️ Travel Planner — 旅行规划专家

> **旅游小白也能规划完美旅行。**

- 6 种场景：明确需求 / 小白探索 / 拍照穿搭 / MBTI定制 / 出境旅游 / 地图生成
- 具体到门牌号的酒店推荐 + 差评信息
- 出境游：三语名称 + 双币种 + 签证 + 租车 + 保险
- 预算贴合度 90%-105%，不会帮你省着花

### 🏗️ 项目结构

```
skill-hub/
├── README.md
├── CONTRIBUTING.md            # 贡献指南
├── skills/
│   ├── advisor-agent/         # 导师调查
│   │   ├── advisor-agent.md   # 入口文件
│   │   ├── SKILL.md           # 主调度
│   │   ├── advisor-agent-lite.md    # 精简版入口
│   │   ├── advisor-agent-single.md  # 单文件版（本地小模型）
│   │   └── skills/            # 子 skill
│   │       ├── scholar-search/
│   │       ├── professor-profile/
│   │       ├── reputation-check/
│   │       ├── paper-analysis/
│   │       ├── lab-intel/
│   │       └── report-gen/
│   ├── code-auditor/          # 代码审计
│   │   └── ...
│   └── travel-planner/        # 旅行规划
│       └── ...
└── templates/                 # Skill 开发模板
    └── skill-template.md
```

### 🤝 贡献

我们欢迎所有形式的贡献！

**提交新 Skill**：
1. Fork 本仓库
2. 参考 `templates/skill-template.md` 创建你的 Skill
3. 放到 `skills/你的skill名/` 目录下
4. 提交 PR，附上简单的使用说明和效果示例

**改进现有 Skill**：
- 发现 bug？搜索策略不够好？报告格式可以优化？直接提 Issue 或 PR

**Skill 灵感（欢迎认领）**：
- 📝 论文阅读助手 — 深度解析学术论文
- 📊 数据分析师 — 自动 EDA + 可视化 + 报告
- 🏠 租房调查员 — 房源信息 + 周边 + 避坑
- 💼 简历优化师 — 针对 JD 优化简历
- 🍳 菜谱规划师 — 根据冰箱库存推荐菜谱
- 🏋️ 健身教练 — 个性化训练计划
- 📰 新闻摘要员 — 每日新闻多源聚合

### 📄 License

MIT License — 随便用，记得给个 ⭐

---

## English

### 🤔 What is this?

**Skill Hub** is an open-source AI Agent Skill repository.

Each Skill is a carefully crafted Markdown instruction file that turns AI into a domain expert — not just a simple prompt, but a **production-grade Agent blueprint** with complete workflows, quality standards, and error handling.

> 🎯 Currently supports [OpenCode](https://opencode.ai). Expanding to Claude Code, Cursor, and more platforms soon.

### ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/你的用户名/skill-hub.git

# 2. Copy the skill you want
cp -r skill-hub/skills/advisor-agent ~/.config/opencode/skills/

# 3. Use it in OpenCode
# "Look up Professor XXX at MIT for me"
```

### 📦 Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| 🎓 [advisor-agent](skills/advisor-agent/) | Graduate advisor intelligence — academic strength, reputation, lab culture | v1 |
| 🔒 [code-auditor](skills/code-auditor/) | White-box security audit — SQLi, XSS, RCE, SSRF, file upload | v1 |
| ✈️ [travel-planner](skills/travel-planner/) | Travel planning expert — itinerary, budget, outfits, local tips | v1 |

### 🤝 Contributing

We welcome all contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Skill ideas (help wanted):**
- 📝 Paper Reader — Deep analysis of academic papers
- 📊 Data Analyst — Auto EDA + visualization + reports
- 💼 Resume Optimizer — Tailor resume to job descriptions
- 🏠 Apartment Hunter — Rental research + neighborhood analysis

### 📄 License

MIT License

---

<div align="center">

**如果觉得有用，请给个 ⭐ Star — 这是对开源最好的支持！**

**If you find this useful, please ⭐ Star — it means the world to open source!**

</div>
