# ================================================================
# Java Spring Boot 生产 Dockerfile
#
# 多阶段构建:
#   Stage 1 (builder): Maven 编译打包
#   Stage 2 (runtime): JRE 运行时镜像，最小化体积
# ================================================================

# ---- 构建阶段 ----
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /build

# 先复制 pom.xml 利用 Docker 层缓存（依赖不变时跳过下载）
COPY pom.xml ./
COPY .mvn/ .mvn/
COPY mvnw ./
RUN chmod +x mvnw && ./mvnw dependency:go-offline -q

# 复制源代码并编译
COPY src/ ./src/
RUN ./mvnw package -DskipTests -q

# ---- 运行阶段 ----
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 创建非 root 用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 创建代码输出和部署目录
RUN mkdir -p /app/output /app/deploy && \
    chown -R appuser:appgroup /app/output /app/deploy

# 复制 jar 包
COPY --from=builder /build/target/*.jar app.jar

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8123

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
    CMD wget -qO- http://localhost:8123/api/health || exit 1

# 启动命令（JVM 参数针对容器环境优化）
ENTRYPOINT ["java", \
    "-XX:+UseContainerSupport", \
    "-XX:MaxRAMPercentage=75.0", \
    "-Djava.security.egd=file:/dev/./urandom", \
    "-jar", "app.jar"]
