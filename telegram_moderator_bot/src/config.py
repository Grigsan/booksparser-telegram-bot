"""
Конфигурация Telegram-бота "Господин Алладин"
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Конфигурация бота"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8477658027:AAFM14z-Vt4L0W4Ig_e6oeddk5hbAJf0n3M')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'moderator_bot')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'postgresql-grigson69.alwaysdata.net')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', 'grigson69')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'grigson96911')
    DB_NAME = os.getenv('DB_NAME', 'grigson69_2')
    DATABASE_URL = os.getenv('DATABASE_URL', 
        'postgresql+asyncpg://grigson69:grigson96911@postgresql-grigson69.alwaysdata.net:5432/grigson69_2')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/moderator_bot.log')
    
    # Bot Settings
    ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
    MODERATION_ENABLED = os.getenv('MODERATION_ENABLED', 'true').lower() == 'true'
    AUTO_DELETE_DELAY = int(os.getenv('AUTO_DELETE_DELAY', 5))
    MAX_WARNINGS = int(os.getenv('MAX_WARNINGS', 3))
    
    # Filter Settings
    PROFANITY_FILTER = os.getenv('PROFANITY_FILTER', 'true').lower() == 'true'
    SPAM_FILTER = os.getenv('SPAM_FILTER', 'true').lower() == 'true'
    LINK_FILTER = os.getenv('LINK_FILTER', 'false').lower() == 'true'
    
    # Нецензурные слова для фильтрации
    PROFANITY_WORDS = [
        'блядь', 'сука', 'пизда', 'хуй', 'ебать', 'блять', 'бля', 'сука', 'пиздец',
        'пидорас', 'пидор', 'гей', 'лесбиянка', 'транс', 'педик',
        'fuck', 'shit', 'bitch', 'damn', 'asshole', 'cunt', 'whore', 'slut',
        'дурак', 'идиот', 'тупой', 'дебил', 'кретин', 'мудак', 'говно'
    ]
    
    # Команды бота
    COMMANDS = {
        'start': 'Запустить бота',
        'help': 'Показать справку',
        'stats': 'Статистика модерации',
        'warn': 'Предупредить пользователя',
        'ban': 'Заблокировать пользователя',
        'unban': 'Разблокировать пользователя',
        'mute': 'Заглушить пользователя',
        'unmute': 'Разглушить пользователя'
    }
