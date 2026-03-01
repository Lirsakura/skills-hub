---
name: env-setup
description: >
  通用项目环境搭建。自动识别技术栈，按需加载子模块，搭建完整可运行环境。
  支持 conda（ML/AI 项目优先）、venv、Docker Compose、Node.js、Java。
---

# 项目环境搭建 Skill

将目标项目从源码变成可运行环境。遵循：**识别 → 路由 → 搭建 → 验证**。

**重要原则：只加载需要的子模块，不要读取不相关的文件。**

---

## 判断项目来源

用户提供项目的方式分三种，流程不同：

| 来源 | PROJECT_DIR 怎么定 | 是否 clone | 是否问安装位置 |
|------|-------------------|-----------|--------------|
| **A. 给了 Git URL** | `${SETUP_ROOT}/<name>` | 是 | 是，问放哪里 |
| **B. 模糊描述** | `${SETUP_ROOT}/<name>` | 是（搜索后） | 是 |
| **C. 给了本地路径** | **直接用用户给的路径** | 否 | 否 |

### 来源 A/B：需要 clone

**先问安装位置**（不要默认用 `/tmp`）：

1. 问用户："项目要放在哪个目录？"
2. 用户指定了 → 用用户的
3. 用户没偏好 → 建议 `~/projects/<project_name>`
4. 用户明确说临时用 → 才用 `/tmp/setup/`

```bash
PROJECT_NAME=$(basename "$GIT_URL" .git)
PROJECT_DIR="${SETUP_ROOT}/${PROJECT_NAME}"
WORKSPACE="${SETUP_ROOT}/.workspace/${PROJECT_NAME}"
mkdir -p "${WORKSPACE}"
```

然后执行**第零步网络检测**（见下方）再 clone。

### 来源 C：本地项目（直接就地安装）

```bash
# 用户说 "帮我装 /home/sakura/my-project 的环境"
PROJECT_DIR="/home/sakura/my-project"        # 直接用用户给的路径
PROJECT_NAME=$(basename "$PROJECT_DIR")
WORKSPACE="${PROJECT_DIR}/.workspace"         # workspace 放在项目目录内
mkdir -p "${WORKSPACE}"
```

**不移动、不复制用户的文件。跳过网络检测和 clone，直接进入第一步（识别项目）。**

---

## 第零步：网络检测（仅来源 A/B，本地项目跳过）

读取 `helpers/network-check.md`，按顺序执行：

1. `check_proxy` — 检测环境变量和 git 全局代理是否已配置
2. `test_connectivity` — 测试 GitHub 和国内网络连通性
3. 根据结果决定 clone 策略：
   - GitHub 可达 → 直接 `git clone`
   - GitHub 不可达但国内正常 → 用 `safe_git_clone`（自动尝试镜像站）
   - 完全断网 → 停止，提示用户检查网络

**clone 时始终使用 `safe_git_clone` 函数**，它内置了超时检测、镜像回退和代理引导。

---

## 第一步：识别项目

### 检测技术栈

```bash
cd "$PROJECT_DIR"

# 语言/框架
HAS_PYTHON=false; [ -f requirements.txt ] || [ -f pyproject.toml ] || [ -f setup.py ] || [ -f Pipfile ] || [ -f environment.yml ] || [ -f conda.yaml ] && HAS_PYTHON=true
HAS_NODE=false;   [ -f package.json ] && HAS_NODE=true
HAS_JAVA=false;   [ -f pom.xml ] || [ -f build.gradle ] && HAS_JAVA=true
HAS_DOCKER=false; [ -f docker-compose.yml ] || [ -f docker-compose.yaml ] || [ -f compose.yml ] && HAS_DOCKER=true
HAS_DOCKERFILE=false; [ -f Dockerfile ] && HAS_DOCKERFILE=true

# conda 相关（只检测 conda 命令是否可用和项目文件，不检测已有环境）
HAS_CONDA_ENV_FILE=false; [ -f environment.yml ] || [ -f environment.yaml ] || [ -f conda.yaml ] && HAS_CONDA_ENV_FILE=true
CONDA_AVAILABLE=false; which conda >/dev/null 2>&1 && CONDA_AVAILABLE=true
# ⚠️ 不要 conda env list —— 不检测/不复用用户已有的 conda 环境

# ML/AI 项目检测（决定是否需要 conda）
IS_ML_PROJECT=false
grep -qiE "torch|tensorflow|transformers|diffusers|accelerate|bitsandbytes|xformers|triton|jax|paddle|onnx|opencv|scikit-learn|keras" \
    requirements*.txt pyproject.toml setup.py Pipfile 2>/dev/null && IS_ML_PROJECT=true

# conda 需求判定：有 environment.yml 或 ML 项目 → 需要 conda（没装就装）
NEEDS_CONDA=false
[ "$HAS_CONDA_ENV_FILE" = "true" ] && NEEDS_CONDA=true
[ "$IS_ML_PROJECT" = "true" ] && NEEDS_CONDA=true

echo "Python=$HAS_PYTHON  Node=$HAS_NODE  Java=$HAS_JAVA  Docker=$HAS_DOCKER  Dockerfile=$HAS_DOCKERFILE"
echo "Conda可用=$CONDA_AVAILABLE  需要Conda=$NEEDS_CONDA  ML项目=$IS_ML_PROJECT"
```

### 检测数据库依赖

```bash
NEEDS_POSTGRES=false
NEEDS_MYSQL=false
NEEDS_REDIS=false
NEEDS_MONGO=false
NEEDS_SQLITE=false

FILES=$(find "$PROJECT_DIR" -maxdepth 3 \
    \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.yml" -o -name "*.yaml" \
       -o -name "*.env*" -o -name "*.cfg" -o -name "*.ini" -o -name "*.conf" \
       -o -name "requirements*.txt" -o -name "package.json" -o -name "Pipfile" \
       -o -name "pyproject.toml" -o -name "docker-compose*" \) 2>/dev/null)

grep -ril "psycopg\|postgres\|postgresql" $FILES 2>/dev/null && NEEDS_POSTGRES=true
grep -ril "mysqlclient\|pymysql\|mysql2\|mariadb" $FILES 2>/dev/null && NEEDS_MYSQL=true
grep -ril "redis" $FILES 2>/dev/null && NEEDS_REDIS=true
grep -ril "pymongo\|mongodb\|mongoose" $FILES 2>/dev/null && NEEDS_MONGO=true
grep -ril "sqlite" $FILES 2>/dev/null && NEEDS_SQLITE=true

echo "Postgres=$NEEDS_POSTGRES  MySQL=$NEEDS_MYSQL  Redis=$NEEDS_REDIS  Mongo=$NEEDS_MONGO  SQLite=$NEEDS_SQLITE"
```

### 读 README

提取：安装方式、启动命令、依赖服务、环境变量、特殊硬件要求（GPU 等）。

---

## 第二步：路由加载

根据识别结果，**只读取对应的子模块文件**：

### 必读

| 文件 | 说明 |
|------|------|
| `helpers/network-check.md` | 网络检测 + 代理处理 + 镜像回退（clone 前） |
| `helpers/port-isolation.md` | 端口查找 + Docker 网络隔离 |
| `output/status-output.md` | 最终输出模板 |

### 按数据库按需读取（只读命中的）

| 条件 | 读取文件 |
|------|---------|
| `NEEDS_POSTGRES=true` | `db/postgres.md` |
| `NEEDS_MYSQL=true` | `db/mysql.md` |
| `NEEDS_REDIS=true` | `db/redis.md` |
| `NEEDS_MONGO=true` | `db/mongo.md` |
| `NEEDS_SQLITE=true` | 无需额外文件 |

### 按应用类型按需读取（只读一个）

| 条件 | 读取文件 |
|------|---------|
| `HAS_DOCKER=true`（有 compose） | `app/docker-compose.md` |
| `HAS_DOCKERFILE=true`（只有 Dockerfile） | `app/docker-compose.md`（复用其中 Dockerfile 段落） |
| `HAS_PYTHON=true` | `app/python.md` |
| `HAS_NODE=true` | `app/node.md` |
| `HAS_JAVA=true` | `app/java.md` |

### 按需读取镜像检查

| 条件 | 读取文件 |
|------|---------|
| 需要拉取任何 Docker 镜像时 | `helpers/image-check.md` |

**优先级：Docker Compose > Dockerfile > 手动搭建。** 有 compose 时直接用 compose，不需要再读语言对应的手动搭建文件。

---

## 第三步：搭建

按加载的子模块执行。顺序：

1. 创建 Docker 网络（`helpers/port-isolation.md`）
2. 启动数据库（`db/*.md`）
3. 等待数据库就绪
4. 搭建应用（`app/*.md`）

---

## 第四步：验证

```bash
QUIET=true bash skills/env-setup/scripts/health_check.sh \
    "$PROJECT_NAME" "$WEB_PORT" \
    "postgres:${DB_PORT}:setup_${PROJECT_NAME}_postgres" \
    "redis:${REDIS_PORT}:setup_${PROJECT_NAME}_redis"

# 只用 sqlite 的项目
QUIET=true bash skills/env-setup/scripts/health_check.sh \
    "$PROJECT_NAME" "$WEB_PORT" sqlite
```

### 判定标准

| 状态 | 条件 |
|------|------|
| READY | 所有服务运行，HTTP 可达（或 ML 项目脚本可执行） |
| PARTIAL | 主应用可用，辅助服务有问题 |
| FAILED | 主应用无法启动 |

---

## 第五步：写入文档（强制，不可跳过）

搭建完成后，**必须**按照 `output/status-output.md` 的模板，将完整的环境文档写入 `${PROJECT_DIR}/ENVIRONMENT_SETUP.md`。

这一步不可省略。用户关闭终端后，这个文件是唯一的操作参考。

文档必须包含：
- 环境信息（语言/框架/版本/路径）
- 日常使用（激活、启动、停止、重启命令）
- 数据库连接信息（如适用）
- 环境变量说明
- 搭建过程中执行的关键步骤
- 遇到的问题及解决方法
- 清理方法

写入后在终端告知用户文件位置：`详细文档已保存到: ${PROJECT_DIR}/ENVIRONMENT_SETUP.md`

---

## 特殊情况：项目已在运行

不要重新搭建。确认端口后直接验证：

```bash
ss -tlnp | grep -E ":(3000|5000|8000|8080|8888) "
docker ps --format "table {{.Names}}\t{{.Ports}}" 2>/dev/null | grep -i setup
```

---

## 搭建失败通用处理

最多重试 3 轮：

| 问题 | 解决方案 |
|------|---------|
| git clone 超时 | `safe_git_clone` 自动尝试镜像站，全部失败则引导用户配代理 |
| GitHub 不可达 | 先用镜像站，不行则提示配置 http_proxy / git proxy |
| 缺系统依赖 | `apt-get update && apt-get install -y <pkg>` |
| pip/conda 超时 | 换源：pip 用清华源，conda 用清华 channel |
| npm 超时 | `npm config set registry https://registry.npmmirror.com` |
| Docker 镜像拉取失败 | `ensure_image` 自动回退阿里云/USTC 镜像 |
| 端口被占 | `find_free_port` 自动跳过 |
| 数据库连接拒绝 | `wait_for_port` 等待就绪 |
| CUDA 版本不匹配 | 检查 nvidia-smi，安装对应版本 torch |
| 无法解决 | 记录错误，报告用户 |
