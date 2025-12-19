-- 1. 启用向量扩展 (相当于给数据库安装向量插件)
-- 这步通常需要管理员权限
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 创建向量存储表
CREATE TABLE IF NOT EXISTS aigen_rag.embeddings (
                                                    id UUID PRIMARY KEY,           -- 建议去掉 default gen_random_uuid()，由 Java 层生成 ID，避免依赖 pgcrypto 扩展
                                                    content TEXT,
                                                    metadata JSONB,
                                                    embedding vector(1536)         -- 对应阿里通义千问 v2
);

-- 3. 创建索引 (为了让搜索更快)
-- 这一步如果报错，可能是因为表里还没数据，可以先跳过，等有数据了再加
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);