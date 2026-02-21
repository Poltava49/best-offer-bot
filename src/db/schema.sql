-- Расширение для UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица пользователей Telegram
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица логирования парсинга
CREATE TABLE IF NOT EXISTS parsing_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    marketplace_id INTEGER NOT NULL,
    product_id UUID NOT NULL
);

-- Таблица кэша
CREATE TABLE IF NOT EXISTS cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_url TEXT NOT NULL,
    request_body TEXT NULL,
    response_status_code INTEGER NOT NULL,
    response_body TEXT NULL,
    is_file BOOLEAN NOT NULL,
    file_name VARCHAR(40) NULL
);