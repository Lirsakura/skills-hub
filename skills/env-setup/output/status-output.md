# 输出规范

搭建完成后必须做两件事：**终端输出摘要** + **写入文件到项目目录**。

**写入文件是强制要求，不可跳过。** 用户关闭终端后，这个文件是唯一的参考。

---

## 1. 终端摘要

在终端输出以下内容，让用户立即看到结果：

```
环境状态: READY / PARTIAL / FAILED

运行服务
- Web 应用: http://localhost:<port> (<framework>)
- 数据库: localhost:<port> (<db_type>)

激活命令: conda activate <env_name> / source <path>/bin/activate
启动命令: <实际启动命令>
停止命令: <实际停止命令>

详细文档已保存到: ${PROJECT_DIR}/ENVIRONMENT_SETUP.md
```

---

## 2. 写入 ENVIRONMENT_SETUP.md（强制）

**必须**用 Write 工具将以下内容写入 `${PROJECT_DIR}/ENVIRONMENT_SETUP.md`。

这是用户日后的操作手册，写清楚、写完整。根据实际搭建情况填充，没有的章节跳过。

```markdown
# <项目名> 环境搭建文档

> 搭建时间：<日期>
> 搭建方式：env-setup agent

---

## 环境信息

| 项目 | 值 |
|------|-----|
| 项目位置 | <PROJECT_DIR 的绝对路径> |
| 语言 | <语言及版本> |
| 框架 | <框架及版本> |
| 环境类型 | conda / venv / Docker / 系统 |
| 环境名称 | <env_name>（如适用） |
| Python 版本 | <version>（如适用） |
| Node 版本 | <version>（如适用） |
| GPU | <型号及显存，或"无"> |

---

## 日常使用

### 激活环境

<根据实际情况写，例如：>

```bash
conda activate setup_<project_name>
# 或
source <PROJECT_DIR>/venv/bin/activate
```

### 启动项目

```bash
<实际的启动命令，如 python manage.py runserver 0.0.0.0:8000>
```

### 停止项目

```bash
<实际的停止命令，如 Ctrl+C 或 docker compose down>
```

### 重启项目

```bash
<实际的重启命令>
```

### 访问地址

- Web: http://localhost:<port>
- API: http://localhost:<port>/api（如适用）
- 数据库: localhost:<db_port>（如适用）

---

## 数据库信息（如适用）

| 项目 | 值 |
|------|-----|
| 类型 | PostgreSQL / MySQL / SQLite / MongoDB / Redis |
| 主机 | localhost |
| 端口 | <port> |
| 数据库名 | <db_name> |
| 用户名 | <username> |
| 密码 | <password> |
| 连接命令 | <如 psql -h localhost -p 5432 -U user -d dbname> |

---

## 环境变量

项目使用的环境变量文件：`<.env 文件路径>`

关键变量说明：

| 变量 | 值 | 说明 |
|------|-----|------|
| DATABASE_URL | <值> | 数据库连接串 |
| SECRET_KEY | <值> | 应用密钥 |
| ... | ... | ... |

---

## 搭建过程记录

以下是搭建过程中执行的关键操作，供排查问题或重新搭建时参考。

### 执行的关键步骤

1. <步骤1：如"创建 conda 环境 setup_xxx，Python 3.10">
2. <步骤2：如"pip install -r requirements.txt，使用清华源">
3. <步骤3：如"启动 PostgreSQL 容器，端口 5432">
4. <步骤4：如"执行数据库迁移 python manage.py migrate">
5. ...

### 遇到的问题及解决方法

<如果搭建过程中遇到了问题并解决了，记录在这里。没有问题则写"搭建过程顺利，未遇到问题。">

| 问题 | 解决方法 |
|------|---------|
| <问题描述> | <怎么解决的> |

---

## 清理方法

如需完全卸载此环境：

```bash
<按实际情况生成，例如：>

# 停止并删除容器
docker rm -f setup_<project_name>_postgres 2>/dev/null

# 删除 Docker 网络
docker network rm setup_net_<project_name> 2>/dev/null

# 删除 conda 环境
conda env remove -n setup_<project_name> -y

# 删除工作区（不删源码）
rm -rf <PROJECT_DIR>/.workspace
```
```

---

## 全量清理命令（跨项目）

以下命令清理所有 env-setup 创建的资源：

```bash
# 停止所有 setup 容器
docker rm -f $(docker ps -a --filter "name=setup_" -q) 2>/dev/null

# 删除所有 setup 网络
docker network ls --filter "name=setup_net_" -q | xargs -r docker network rm 2>/dev/null

# 删除 conda 环境（只删 setup_ 前缀的，不碰用户已有环境）
conda env list 2>/dev/null | grep "^setup_" | awk '{print $1}' | xargs -I{} conda env remove -n {} -y 2>/dev/null

# 删除搭建目录（本地项目模式下不要删源码目录，只删 .workspace）
# clone 模式: rm -rf ${SETUP_ROOT}/
# 本地模式:   rm -rf ${PROJECT_DIR}/.workspace

echo "所有环境已清理"
```
