<div align="center">

```
   ███████╗██╗  ██╗██╗██╗     ██╗         ██╗  ██╗██╗   ██╗██████╗
   ██╔════╝██║ ██╔╝██║██║     ██║         ██║  ██║██║   ██║██╔══██╗
   ███████╗█████╔╝ ██║██║     ██║         ███████║██║   ██║██████╔╝
   ╚════██║██╔═██╗ ██║██║     ██║         ██╔══██║██║   ██║██╔══██╗
   ███████║██║  ██╗██║███████╗███████╗    ██║  ██║╚██████╔╝██████╔╝
   ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝
```

**Plug-and-play skill packs for AI Agents.**

**给 AI 装技能包。不调 prompt，直接上专家。**

<br/>

[![MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![PRs](https://img.shields.io/badge/PRs-welcome-FF6B6B?style=flat-square)](CONTRIBUTING.md)
[![Idea?](https://img.shields.io/badge/💡_Idea%3F-Open_Issue-FFD93D?style=flat-square)](https://github.com/Lirsakura/skill-hub/issues/new)

**[中文](#中文)** · **[English](#english)**

</div>

---

<a name="中文"></a>

## 什么是 Skill？

```
Prompt = 一句话指令          →  "帮我分析这份数据"  →  AI 随便聊两句
Skill  = 一套完整的 SOP 手册  →  流程 + 策略 + 质量红线 + 错误兜底 + 结构化输出
```

**复制粘贴即装。** 零依赖，零配置。当前适配 [OpenCode](https://opencode.ai)，本质是 Markdown，任何支持 system prompt 的平台都能用。

```bash
git clone https://github.com/Lirsakura/skill-hub.git
cp skill-hub/agents/advisor-agent.md  ~/.config/opencode/agents/
cp -r skill-hub/skills/advisor-agent/ ~/.config/opencode/skills/
# 完事。打开 OpenCode 说人话就行。
```

---

## Skill 目录

> `✅ 可用` `🚧 开发中` `💡 待认领 — 欢迎 PR 或 Issue 投票 👍`

### 🔍 `research/` — 调研与情报

| 状态 | Skill | 简介 | 亮点 |
|:---:|-------|------|------|
| ✅ | **[advisor-agent](skills/advisor-agent/)** | 导师情报分析 | 11 源扫描 · 🔴🟡🟢 风险标记 · 对比/面试模式 |
| 💡 | paper-reader | 学术论文深度拆解 | 核心贡献 · 方法论 · 局限性 · 可复现性评估 |
| 💡 | market-analyst | 行业/产品调研 | 竞品分析 · 市场规模 · 趋势预测 |

### 🛡️ `security/` — 安全攻防

| 状态 | Skill | 简介 | 亮点 |
|:---:|-------|------|------|
| ✅ | **[code-auditor](skills/code-auditor/)** | 白盒代码安全审计 | 6 阶段流程 · 跨文件追踪 · 可执行 PoC |
| 💡 | vuln-scanner | 漏洞扫描与验证 | 自动化扫描 · CVE 匹配 · 修复建议 |

### ✈️ `lifestyle/` — 生活助手

| 状态 | Skill | 简介 | 亮点 |
|:---:|-------|------|------|
| ✅ | **[travel-agent](skills/travel-agent/)** | AI 旅行规划师 | 6 种模式 · 门牌号精度 · 出境三语 · MBTI 路线 |
| 💡 | meal-planner | 冰箱有什么→做什么菜 | 食材匹配 · 营养均衡 · 难度分级 |
| 💡 | fitness-coach | 个性化训练计划 | 目标导向 · 器材适配 · 渐进超负荷 |

### 🔧 `devtools/` — 开发工具

| 状态 | Skill | 简介 | 亮点 |
|:---:|-------|------|------|
| ✅ | **[env-setup](skills/env-setup/)** | GitHub 项目一键配环境 | conda/venv/docker · GPU 自检 · 镜像回退 · 18 个子模块 |
| ✅ | **[git-sync](skills/git-sync/)** | Git 仓库同步管理 | push/pull/sync-log · 冲突处理 · 日志追踪 |
| 💡 | data-analyst | 自动 EDA + 可视化 | 数据画像 · 异常检测 · 洞察报告 |

### 💼 `career/` — 求职与学术

| 状态 | Skill | 简介 | 亮点 |
|:---:|-------|------|------|
| 💡 | resume-tailor | 根据 JD 定制简历 | 逐条匹配 · ATS 友好 · 量化建议 |
| 💡 | mock-interview | 模拟技术面试 | 实时追问 · 评分反馈 · 知识点定位 |

### 📰 `information/` — 信息聚合

| 状态 | Skill | 简介 | 亮点 |
|:---:|-------|------|------|
| 💡 | news-digest | 每日多源新闻聚合 | 去重 · 摘要 · 观点对比 · 趋势追踪 |
| 💡 | apartment-hunter | 租房情报调查 | 房源分析 · 周边设施 · 差评避坑 |

---

## 已上线 Skill 速览

<details>
<summary><b>🎓 advisor-agent — 选导师前必看</b></summary>

<br/>

**选错导师毁三年。** 11 个平台（研控 · PI Review · 知乎 · 小红书 · RateMyProfessors · Reddit · GradCafe · PubPeer...）交叉验证，输出结构化尽职调查报告。

```
"查一下 MIT 的 XXX 教授"        → 完整报告
"对比 A 教授和 B 教授"          → 对比分析
"下周面试 XXX，帮我准备"        → 面试情报
```

三个体量版本：完整版 49K（大模型）· 精简版 11K（中等模型）· 单文件 4K（本地小模型）

</details>

<details>
<summary><b>🔒 code-auditor — 人类级白盒审计</b></summary>

<br/>

不是 `grep 'eval('`。6 阶段流程：代码接入 → 全量理解 → 深度分析 → 对抗验证 → 报告 → 协作。聚焦 SQLi / XSS / RCE / SSRF / 文件上传，跨文件数据流追踪，输出可执行 PoC。

</details>

<details>
<summary><b>✈️ travel-agent — 拿着手机就能走</b></summary>

<br/>

6 种模式（小白探索 / 拍照穿搭 / MBTI 定制 / 出境 / 地图生成...），酒店精确到门牌号 + 差评，出境三语 + 双币种 + 签证 + 租车，预算贴合度 90%-105%。

</details>

<details>
<summary><b>🔧 env-setup — 给个链接就能跑</b></summary>

<br/>

给一个 GitHub URL 或本地路径，自动识别技术栈（Python/Node/Java/Docker），搭建完整可运行环境。conda 优先，支持 GPU 自检、镜像回退、端口隔离。18 个子模块覆盖 app/db/helpers/scripts。

```
"帮我装一下 https://github.com/xxx/yyy"    → clone + 识别 + 搭建
"当前目录的环境帮我装一下"                  → 就地搭建
"找个 stable diffusion webui 装一下"       → 搜索 + 选择 + 搭建
```

</details>

<details>
<summary><b>🔄 git-sync — Git 操作不用记命令</b></summary>

<br/>

push / pull / sync-log 三个子 skill，处理日常 Git 同步。自动处理冲突、生成同步日志。

</details>

---

## 💡 想要新 Skill？

**开 [Issue](https://github.com/Lirsakura/skill-hub/issues/new) 就行。哪怕一句 "要是有个 XX 就好了" 也够。**

- 标题：`[Skill Request] 你想要什么`
- 👍 投票越多，越优先实现
- 想自己做？直接认领，PR 提过来

每一条 Issue 我都会看。好的 Skill 都是从一个真实痛点开始的。

---

## 🤝 贡献

```
💡 提想法（Issue）· 🐛 报 Bug · ⭐ Star · 📢 转发 · 📝 提交 Skill（PR）
```

不会写代码也能贡献——**一个好需求比十个 demo 更有价值。**

提交 Skill：`Fork → 参考 templates/skill-template.md → PR`　详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

<br/>
<br/>

<a name="english"></a>

<div align="center">

```
   ███████╗██╗  ██╗██╗██╗     ██╗         ██╗  ██╗██╗   ██╗██████╗
   ██╔════╝██║ ██╔╝██║██║     ██║         ██║  ██║██║   ██║██╔══██╗
   ███████╗█████╔╝ ██║██║     ██║         ███████║██║   ██║██████╔╝
   ╚════██║██╔═██╗ ██║██║     ██║         ██╔══██║██║   ██║██╔══██╗
   ███████║██║  ██╗██║███████╗███████╗    ██║  ██║╚██████╔╝██████╔╝
   ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝
```

**Plug-and-play skill packs for AI Agents.**

</div>

<br/>

## What is a Skill?

```
Prompt = one-line instruction    →  "analyze this data"  →  AI rambles
Skill  = a complete SOP manual   →  workflow + strategy + quality gates + error handling + structured output
```

**Copy-paste to install.** Zero deps. Zero config. Built for [OpenCode](https://opencode.ai). Works anywhere with system prompts (it's just Markdown).

```bash
git clone https://github.com/Lirsakura/skill-hub.git
cp skill-hub/agents/advisor-agent.md  ~/.config/opencode/agents/
cp -r skill-hub/skills/advisor-agent/ ~/.config/opencode/skills/
# Done. Open OpenCode. Talk normally.
```

---

## Skill Catalog

> `✅ Available` `🚧 WIP` `💡 Open — PRs welcome or 👍 upvote to prioritize`

### 🔍 `research/` — Research & Intelligence

| Status | Skill | Description | Highlights |
|:---:|-------|-------------|------------|
| ✅ | **[advisor-agent](skills/advisor-agent/)** | Grad advisor intelligence | 11 sources · 🔴🟡🟢 risk flags · Compare & interview prep |
| 💡 | paper-reader | Academic paper deep-dive | Core contributions · Methodology · Limitations |
| 💡 | market-analyst | Industry/product research | Competitive analysis · Market sizing · Trends |

### 🛡️ `security/` — Security & Offense

| Status | Skill | Description | Highlights |
|:---:|-------|-------------|------------|
| ✅ | **[code-auditor](skills/code-auditor/)** | White-box security audit | 6-stage pipeline · Cross-file tracing · Executable PoCs |
| 💡 | vuln-scanner | Vulnerability scan & verify | Auto-scan · CVE matching · Fix suggestions |

### ✈️ `lifestyle/` — Life & Planning

| Status | Skill | Description | Highlights |
|:---:|-------|-------------|------------|
| ✅ | **[travel-agent](skills/travel-agent/)** | AI travel planner | 6 modes · Street-level picks · Trilingual · MBTI routes |
| 💡 | meal-planner | Fridge → recipe suggestions | Ingredient matching · Nutrition · Difficulty tiers |
| 💡 | fitness-coach | Custom training plans | Goal-based · Equipment-aware · Progressive overload |

### 🔧 `devtools/` — Developer Tools

| Status | Skill | Description | Highlights |
|:---:|-------|-------------|------------|
| ✅ | **[env-setup](skills/env-setup/)** | One-click dev env for any repo | conda/venv/docker · GPU detection · Mirror fallback · 18 submodules |
| ✅ | **[git-sync](skills/git-sync/)** | Git repo sync management | push/pull/sync-log · Conflict handling · Log tracking |
| 💡 | data-analyst | Auto EDA + visualization | Data profiling · Anomaly detection · Insight reports |

### 💼 `career/` — Career & Academia

| Status | Skill | Description | Highlights |
|:---:|-------|-------------|------------|
| 💡 | resume-tailor | Tailor resume to JD | Line-by-line match · ATS-friendly · Quantification |
| 💡 | mock-interview | Simulate tech interviews | Follow-ups · Scoring · Knowledge gap analysis |

### 📰 `information/` — Information & Aggregation

| Status | Skill | Description | Highlights |
|:---:|-------|-------------|------------|
| 💡 | news-digest | Multi-source daily news | Dedup · Summaries · Opinion contrast · Trends |
| 💡 | apartment-hunter | Rental intelligence | Listing analysis · Neighborhood · Red flags |

---

## Live Skill Details

<details>
<summary><b>🎓 advisor-agent — Due diligence before choosing your advisor</b></summary>

<br/>

**Bad advisor = bad grad school.** Cross-references 11 platforms (PI Review · RateMyProfessors · Reddit · GradCafe · PubPeer...) into a structured due diligence report.

```
"Look up Professor XXX at MIT"       → Full report
"Compare Professor A vs B"           → Side-by-side
"Interview with XXX next week"       → Interview intel
```

Three sizes: Full 49K (frontier) · Compact 11K (mid-range) · Single-file 4K (local models)

</details>

<details>
<summary><b>🔒 code-auditor — Human-level white-box audit</b></summary>

<br/>

Not `grep 'eval('`. 6-stage pipeline: intake → comprehension → deep analysis → adversarial verification → report → collaboration. Targets SQLi / XSS / RCE / SSRF / file upload. Cross-file data flow tracing. Executable PoCs.

</details>

<details>
<summary><b>✈️ travel-agent — Follow your phone and go</b></summary>

<br/>

6 modes (explore / photo outfits / MBTI / international / map gen...). Street-level hotel picks with negative reviews. Trilingual + dual currency + visa + car rental for international trips. Budget accuracy 90%-105%.

</details>

<details>
<summary><b>🔧 env-setup — Give it a URL, get a running env</b></summary>

<br/>

Give a GitHub URL or local path, auto-detect tech stack (Python/Node/Java/Docker), build a complete runnable environment. Conda-first, GPU detection, mirror fallback, port isolation. 18 submodules covering app/db/helpers/scripts.

</details>

<details>
<summary><b>🔄 git-sync — Git without remembering commands</b></summary>

<br/>

push / pull / sync-log sub-skills for everyday Git sync. Auto conflict handling and sync logging.

</details>

---

## 💡 Want a new Skill?

**[Open an Issue](https://github.com/Lirsakura/skill-hub/issues/new). Even "wish there was a XX" is enough.**

- Title: `[Skill Request] What you want`
- 👍 upvotes = priority
- Want to build it yourself? Claim it and PR

I read every Issue. Every great Skill starts with a real pain point.

---

## 🤝 Contributing

```
💡 Ideas (Issue) · 🐛 Bugs · ⭐ Star · 📢 Share · 📝 Submit a Skill (PR)
```

No code? No problem — **a great request is worth more than ten demos.**

Submit a Skill: `Fork → Use templates/skill-template.md → PR`　See [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

<br/>

⭐ **Star = 让更多人发现 · helps more people find this**

💬 **[Open an Issue](https://github.com/Lirsakura/skill-hub/issues/new) — 任何想法我都看 · I read them all**

<br/>

<sub>Built with obsession. Skills > Prompts.</sub>

</div>
