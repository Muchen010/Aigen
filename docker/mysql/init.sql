-- Aigen 数据库初始化脚本
-- 此文件由 Docker Compose 首次启动时自动执行

CREATE DATABASE IF NOT EXISTS aigen
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE aigen;

-- 其他初始化 SQL (如需要) 可追加在此处
-- 表结构由 MyBatisX 自动生成，通常通过 Flyway/Liquibase 管理
