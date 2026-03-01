# Node.js 项目搭建

当项目没有 Docker Compose / Dockerfile，且识别为 Node.js 项目时使用。

前置依赖：`helpers/port-isolation.md`。
数据库已由 `db/*.md` 启动完毕。

---

## 安装依赖

```bash
cd "$PROJECT_DIR"

if [ -f yarn.lock ]; then
    yarn install
elif [ -f pnpm-lock.yaml ]; then
    pnpm install
else
    npm install
fi
```

### 安装失败处理

```bash
# peer 依赖冲突
npm install --legacy-peer-deps

# 网络超时
npm config set registry https://registry.npmmirror.com
npm install

# node-gyp 编译失败
apt-get update && apt-get install -y build-essential python3
npm install
```

---

## 环境变量

```bash
if [ -f .env.example ] && [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  已复制 .env.example → .env"
fi

if [ -n "$DB_PORT" ]; then
    sed -i "s|localhost:5432|localhost:${DB_PORT}|g" .env 2>/dev/null
    sed -i "s|localhost:3306|localhost:${DB_PORT}|g" .env 2>/dev/null
    sed -i "s|localhost:27017|localhost:${MONGO_PORT}|g" .env 2>/dev/null
fi

if [ -n "$REDIS_PORT" ]; then
    sed -i "s|localhost:6379|localhost:${REDIS_PORT}|g" .env 2>/dev/null
fi
```

---

## 数据库迁移（如需要）

```bash
npx prisma migrate deploy 2>/dev/null || npx prisma db push 2>/dev/null
npx typeorm migration:run 2>/dev/null
npx sequelize-cli db:migrate 2>/dev/null
npx knex migrate:latest 2>/dev/null
```

---

## 启动

```bash
WEB_PORT=$(find_free_port 3000)
export PORT=$WEB_PORT

START_SCRIPT=$(node -e "const p=require('./package.json'); console.log(p.scripts?.start || '')" 2>/dev/null)
DEV_SCRIPT=$(node -e "const p=require('./package.json'); console.log(p.scripts?.dev || '')" 2>/dev/null)

if [ -n "$DEV_SCRIPT" ]; then
    npm run dev &
elif [ -n "$START_SCRIPT" ]; then
    npm start &
else
    node app.js &
fi

echo "Node.js 应用 → localhost:${WEB_PORT}"
```

---

## 清理

```bash
pkill -f "node.*${WEB_PORT}" 2>/dev/null
rm -rf "${PROJECT_DIR}/node_modules"
```
