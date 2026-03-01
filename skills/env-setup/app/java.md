# Java 项目搭建

当项目没有 Docker Compose / Dockerfile，且识别为 Java 项目时使用。

前置依赖：`helpers/port-isolation.md`。
数据库已由 `db/*.md` 启动完毕。

---

## 检测构建工具

```bash
cd "$PROJECT_DIR"

if [ -f pom.xml ]; then
    BUILD_TOOL="maven"
elif [ -f build.gradle ] || [ -f build.gradle.kts ]; then
    BUILD_TOOL="gradle"
else
    echo "❌ 未识别的 Java 构建工具"
fi
```

---

## 编译

```bash
if [ "$BUILD_TOOL" = "maven" ]; then
    if [ -f mvnw ]; then
        chmod +x mvnw && ./mvnw clean package -DskipTests
    else
        mvn clean package -DskipTests
    fi
    JAR_FILE=$(find target -name "*.jar" -not -name "*-sources.jar" | head -1)
elif [ "$BUILD_TOOL" = "gradle" ]; then
    if [ -f gradlew ]; then
        chmod +x gradlew && ./gradlew build -x test
    else
        gradle build -x test
    fi
    JAR_FILE=$(find build/libs -name "*.jar" -not -name "*-plain.jar" | head -1)
fi

echo "构建产物: $JAR_FILE"
```

### 编译失败处理

```bash
# 检查 Java 版本
java -version
grep -o "<java.version>.*</java.version>" pom.xml 2>/dev/null

# Maven 换阿里云源
mvn clean package -DskipTests -Dmaven.repo.remote=https://maven.aliyun.com/repository/public
```

---

## 配置数据库连接

```bash
CONFIG_FILE=$(find "$PROJECT_DIR" -path "*/resources/application*.properties" -o -path "*/resources/application*.yml" | head -1)

if [ -n "$CONFIG_FILE" ] && [ -n "$DB_PORT" ]; then
    sed -i "s|localhost:5432|localhost:${DB_PORT}|g" "$CONFIG_FILE" 2>/dev/null
    sed -i "s|localhost:3306|localhost:${DB_PORT}|g" "$CONFIG_FILE" 2>/dev/null
fi
```

---

## 启动

```bash
WEB_PORT=$(find_free_port 8080)
java -jar "$JAR_FILE" --server.port=${WEB_PORT} &
echo "Java 应用 → localhost:${WEB_PORT}"
```

---

## 清理

```bash
pkill -f "java.*${JAR_FILE}" 2>/dev/null
rm -rf "${PROJECT_DIR}/target" "${PROJECT_DIR}/build"
```
