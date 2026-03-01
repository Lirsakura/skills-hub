# Python 项目搭建

没有 Docker Compose / Dockerfile 时，识别为 Python 项目后使用。

---

## 第一步：问用户用什么环境（必须先问）

安装任何东西之前，先确认：

1. 用 conda 还是 venv？
2. 装到已有环境，还是新建？
3. 新建的话，环境名/路径是什么？（默认建议 `setup_<project_name>`）

| 用户回答 | 参数 |
|---------|------|
| "装到我的 conda 环境 myenv 里" | `--type conda --name myenv` |
| "用 conda 新建一个" | `--type conda --name setup_<project_name>` |
| "用我的 venv /data/envs/xxx" | `--type venv --path /data/envs/xxx` |
| "用 venv 就行" | `--type venv --path ${PROJECT_DIR}/venv` |
| "随便" | 按自动策略（见下方） |

### 自动策略（用户说"随便"时）

```
有 environment.yml → conda
ML/AI 项目        → conda
普通 + conda 可用  → conda
普通 + conda 不可用 → venv
```

---

## 第二步：确保 conda 可用（仅 conda 方案）

如果决定用 conda 但系统没装：

```bash
# 自动安装 miniforge（2-5 分钟），失败则回退 venv
source <(bash skills/env-setup/scripts/install_conda.sh)
```

脚本会自动配置清华源，不改 .bashrc。

---

## 第三步：创建环境 + 安装依赖

```bash
# conda + 有 environment.yml
bash skills/env-setup/scripts/setup_python_env.sh \
    --type conda --name "$ENV_NAME" --project "$PROJECT_DIR" --yml environment.yml

# conda + 无 yml
bash skills/env-setup/scripts/setup_python_env.sh \
    --type conda --name "$ENV_NAME" --project "$PROJECT_DIR"

# venv
bash skills/env-setup/scripts/setup_python_env.sh \
    --type venv --path "$VENV_PATH" --project "$PROJECT_DIR"

# 指定 python 版本
bash skills/env-setup/scripts/setup_python_env.sh \
    --type conda --name "$ENV_NAME" --project "$PROJECT_DIR" --python 3.11
```

脚本内部**每次 pip/conda install 前自动调用 `env_guard.sh` 验证环境**，漂移时自动修复。

---

## 第四步：ML 依赖（仅 ML/AI 项目）

```bash
bash skills/env-setup/scripts/install_ml_deps.sh \
    --type "$ENV_TYPE" --name "$ENV_NAME" --project "$PROJECT_DIR"
# 或 venv:
bash skills/env-setup/scripts/install_ml_deps.sh \
    --type venv --path "$VENV_PATH" --project "$PROJECT_DIR"
```

### 脚本返回的状态码及 agent 应对

| 状态码 | 含义 | agent 行动 |
|-------|------|-----------|
| `ML_GPU_OK` | GPU 版安装成功 | 继续 |
| `ML_NO_GPU` | 没检测到 GPU | **问用户**：确实没 GPU？还是驱动没装？用户确认后手动执行 CPU 版安装 |
| `ML_GPU_INSTALL_FAILED` | GPU 版安装失败 | **问用户**：是否降级 CPU 版？用户同意后手动执行 CPU 版安装 |
| `ML_GPU_VERIFY_FAILED` | 装了但 CUDA 不可用 | **问用户**：是否继续？可能驱动不匹配 |
| `ML_NO_ML_DEPS` | 项目不需要 ML | 跳过 |

### 用户确认后装 CPU 版（手动执行）

```bash
# 先验证环境
source skills/env-setup/scripts/env_guard.sh
ensure_in_env conda "$ENV_NAME"   # 或 venv "$VENV_PATH"

# PyTorch CPU
conda install pytorch torchvision torchaudio cpuonly -c pytorch -y
# 或 pip:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# TensorFlow CPU
pip install tensorflow-cpu
```

---

## 第五步：数据库迁移（按需）

```bash
# 先验证环境！
source skills/env-setup/scripts/env_guard.sh
ensure_in_env "$ENV_TYPE" "$ENV_ID"

# 按框架执行
python manage.py migrate            # Django
flask db upgrade                     # Flask + Alembic
python manage.py init_db             # 通用
```

---

## 第六步：启动应用

```bash
# 先验证环境！
source skills/env-setup/scripts/env_guard.sh
ensure_in_env "$ENV_TYPE" "$ENV_ID"

WEB_PORT=$(find_free_port 5000)

# 按框架启动（agent 根据检测结果选一个）
python manage.py runserver 0.0.0.0:${WEB_PORT} &    # Django
flask run --host 0.0.0.0 --port ${WEB_PORT} &        # Flask
uvicorn app.main:app --host 0.0.0.0 --port ${WEB_PORT} &  # FastAPI
python app.py &                                       # Gradio (默认 7860)
streamlit run app.py --server.port ${WEB_PORT} &       # Streamlit
```

ML 脚本项目无需启动服务，验证环境可用即可报告 READY。

---

## 环境隔离原则

- **用户指定了环境** → 用用户的，不新建，不改名，**清理时绝不删除**
- **自动新建 conda** → 环境名加 `setup_` 前缀，不复用已有环境
- **清理时** → 只删 `setup_` 前缀的

---

## 清理

```bash
# conda（只清 setup_ 前缀）
conda deactivate && conda env remove -n "setup_${PROJECT_NAME}" -y

# venv（只清自动创建的）
deactivate && rm -rf "${PROJECT_DIR}/venv"

# 后台进程
pkill -f "python.*${WEB_PORT}" 2>/dev/null
pkill -f "uvicorn.*${WEB_PORT}" 2>/dev/null
pkill -f "flask.*${WEB_PORT}" 2>/dev/null
```

---

## pip/conda 安装失败处理

```bash
# 缺编译依赖
apt-get update && apt-get install -y gcc g++ python3-dev libffi-dev libssl-dev libpq-dev

# pip 网络超时
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# conda 解依赖太慢 → 换 mamba
conda install mamba -n base -c conda-forge -y
mamba install <package> -y
```
