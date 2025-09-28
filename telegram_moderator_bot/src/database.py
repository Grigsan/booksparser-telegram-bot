"""
Модуль для работы с базой данных PostgreSQL
"""

import asyncio
import asyncpg
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from .config import Config

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.config = Config()
    
    async def connect(self):
        """Подключение к базе данных"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                database=self.config.DB_NAME,
                min_size=1,
                max_size=10
            )
            logger.info("✅ Подключение к PostgreSQL установлено")
            await self.create_tables()
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к базе данных: {e}")
            raise
    
    async def close(self):
        """Закрытие соединения с базой данных"""
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Соединение с базой данных закрыто")
    
    async def create_tables(self):
        """Создание таблиц в базе данных"""
        try:
            async with self.pool.acquire() as conn:
                # Таблица действий бота
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_actions (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        chat_id BIGINT NOT NULL,
                        action_type VARCHAR(50) NOT NULL,
                        message_text TEXT,
                        reason TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Таблица пользователей
                await conn.execute("""
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
                    )
                """)
                
                # Таблица статистики
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS moderation_stats (
                        id SERIAL PRIMARY KEY,
                        date DATE DEFAULT CURRENT_DATE,
                        messages_deleted INTEGER DEFAULT 0,
                        users_warned INTEGER DEFAULT 0,
                        users_banned INTEGER DEFAULT 0,
                        users_muted INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                logger.info("✅ Таблицы в базе данных созданы/проверены")
        except Exception as e:
            logger.error(f"❌ Ошибка создания таблиц: {e}")
            raise
    
    async def log_action(self, user_id: int, chat_id: int, action_type: str, 
                        message_text: str = None, reason: str = None):
        """Логирование действия бота"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO bot_actions (user_id, chat_id, action_type, message_text, reason)
                    VALUES ($1, $2, $3, $4, $5)
                """, user_id, chat_id, action_type, message_text, reason)
                logger.info(f"📝 Действие записано: {action_type} для пользователя {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка записи действия: {e}")
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM users WHERE user_id = $1
                """, user_id)
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя: {e}")
            return None
    
    async def update_user(self, user_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None,
                         warnings: int = None, is_banned: bool = None, 
                         is_muted: bool = None):
        """Обновление информации о пользователе"""
        try:
            async with self.pool.acquire() as conn:
                # Проверяем, существует ли пользователь
                user = await self.get_user(user_id)
                
                if user:
                    # Обновляем существующего пользователя
                    await conn.execute("""
                        UPDATE users SET 
                            username = COALESCE($2, username),
                            first_name = COALESCE($3, first_name),
                            last_name = COALESCE($4, last_name),
                            warnings = COALESCE($5, warnings),
                            is_banned = COALESCE($6, is_banned),
                            is_muted = COALESCE($7, is_muted),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = $1
                    """, user_id, username, first_name, last_name, warnings, is_banned, is_muted)
                else:
                    # Создаем нового пользователя
                    await conn.execute("""
                        INSERT INTO users (user_id, username, first_name, last_name, warnings, is_banned, is_muted)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, user_id, username, first_name, last_name, warnings or 0, is_banned or False, is_muted or False)
                
                logger.info(f"👤 Пользователь {user_id} обновлен")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики модерации"""
        try:
            async with self.pool.acquire() as conn:
                # Общая статистика
                total_actions = await conn.fetchval("SELECT COUNT(*) FROM bot_actions")
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                banned_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_banned = TRUE")
                
                # Статистика за сегодня
                today_actions = await conn.fetchval("""
                    SELECT COUNT(*) FROM bot_actions 
                    WHERE DATE(created_at) = CURRENT_DATE
                """)
                
                # Топ действий
                top_actions = await conn.fetch("""
                    SELECT action_type, COUNT(*) as count 
                    FROM bot_actions 
                    GROUP BY action_type 
                    ORDER BY count DESC 
                    LIMIT 5
                """)
                
                return {
                    'total_actions': total_actions or 0,
                    'total_users': total_users or 0,
                    'banned_users': banned_users or 0,
                    'today_actions': today_actions or 0,
                    'top_actions': [dict(row) for row in top_actions]
                }
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {}
    
    async def get_user_actions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение действий пользователя"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM bot_actions 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2
                """, user_id, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Ошибка получения действий пользователя: {e}")
            return []
