-- Инициализация базы данных для Telegram-бота "Господин Алладин"

-- Таблица действий бота
CREATE TABLE IF NOT EXISTS bot_actions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    message_text TEXT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    warnings INTEGER DEFAULT 0,
    is_banned BOOLEAN DEFAULT FALSE,
    is_muted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица статистики
CREATE TABLE IF NOT EXISTS moderation_stats (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    messages_deleted INTEGER DEFAULT 0,
    users_warned INTEGER DEFAULT 0,
    users_banned INTEGER DEFAULT 0,
    users_muted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_bot_actions_user_id ON bot_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_actions_chat_id ON bot_actions(chat_id);
CREATE INDEX IF NOT EXISTS idx_bot_actions_created_at ON bot_actions(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_banned ON users(is_banned);
CREATE INDEX IF NOT EXISTS idx_users_is_muted ON users(is_muted);

-- Комментарии к таблицам
COMMENT ON TABLE bot_actions IS 'Логи всех действий бота-модератора';
COMMENT ON TABLE users IS 'Информация о пользователях чата';
COMMENT ON TABLE moderation_stats IS 'Статистика модерации по дням';

-- Вставка начальных данных
INSERT INTO moderation_stats (date, messages_deleted, users_warned, users_banned, users_muted)
VALUES (CURRENT_DATE, 0, 0, 0, 0)
ON CONFLICT (date) DO NOTHING;
