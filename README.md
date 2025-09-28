# Tehnoparser + Telegram Moderator Bot

Полнофункциональный проект, состоящий из веб-парсера книг и Telegram-бота с функциями модерации.

## 🚀 Компоненты проекта

### 1. Tehnoparser - Веб-парсер книг
- **Flask API** для парсинга книг с сайта
- **PostgreSQL** база данных для хранения данных
- **Nginx** веб-сервер для фронтенда
- **Docker** контейнеризация всех сервисов

### 2. Telegram Moderator Bot - "Господин Алладин"
- **Модерация чата** - фильтрация нецензурных выражений
- **Система предупреждений** с автоматической блокировкой
- **Интеграция с парсером** - возможность парсить книги через бота
- **Логирование действий** в PostgreSQL
- **Интерактивные меню** с кнопками управления

## 📁 Структура проекта

```
Tehnoparser/
├── 📁 telegram_moderator_bot/     # Telegram бот
│   ├── src/                       # Исходный код бота
│   ├── docker-compose.yml         # Docker конфигурация
│   ├── Dockerfile                 # Docker образ
│   └── requirements.txt           # Python зависимости
├── 📁 nginx/                      # Nginx конфигурация
├── techpark_parser.py             # Парсер книг
├── techpark_api.py                # Flask API
├── postgresql_parser.py           # PostgreSQL интеграция
├── docker-compose.yml             # Основная Docker конфигурация
└── requirements.txt               # Python зависимости
```

## 🛠️ Технологии

- **Backend**: Python, Flask, PostgreSQL
- **Bot**: Python, aiogram, asyncpg
- **Frontend**: HTML, CSS, JavaScript
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Database**: PostgreSQL (AlwaysData)

## 🚀 Быстрый старт

### 1. Запуск Tehnoparser

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd Tehnoparser

# Запустите парсер
docker-compose up -d

# Парсинг данных
curl -X POST "http://localhost:5000/parse" -H "Content-Type: application/json" -d '{"force": true}'
```

### 2. Запуск Telegram бота

```bash
cd telegram_moderator_bot

# Настройте переменные окружения
cp env.example .env
# Отредактируйте .env файл с вашими данными

# Запустите бота
docker-compose up -d
```

## ⚙️ Конфигурация

### Переменные окружения для бота (.env)

```env
BOT_TOKEN=your_telegram_bot_token
DB_HOST=your_postgresql_host
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
ADMIN_IDS=your_telegram_id
```

## 🎯 Функции

### Tehnoparser
- ✅ Парсинг книг с веб-сайта
- ✅ Удаление дубликатов
- ✅ REST API для доступа к данным
- ✅ Веб-интерфейс для просмотра
- ✅ PostgreSQL интеграция

### Telegram Bot
- ✅ Фильтрация нецензурных выражений
- ✅ Система предупреждений (3 предупреждения = блокировка)
- ✅ Защита администраторов от блокировки
- ✅ Логирование всех действий
- ✅ Интерактивные меню с кнопками
- ✅ Интеграция с парсером книг
- ✅ Просмотр книг с деталями (автор, цена, фото, ссылки)

## 📊 API Endpoints

### Tehnoparser API
- `GET /products` - Получить все книги
- `GET /search?q=query` - Поиск книг
- `GET /categories` - Получить категории
- `GET /stats` - Статистика
- `POST /parse` - Запустить парсинг

### Telegram Bot Commands
- `/start` - Главное меню
- `/help` - Справка
- `/parse` - Запустить парсинг
- `/books` - Показать книги
- `/search` - Поиск книг
- `/categories` - Категории
- `/parser_stats` - Статистика парсера

## 🐳 Docker

Проект полностью контейнеризован:

```bash
# Основной парсер
docker-compose up -d

# Telegram бот
cd telegram_moderator_bot
docker-compose up -d
```

## 📝 Логирование

Все действия бота логируются в PostgreSQL:
- Удаления сообщений
- Предупреждения пользователей
- Блокировки
- Команды администраторов

## 🔧 Разработка

### Структура бота
- `src/bot.py` - Основная логика бота
- `src/config.py` - Конфигурация
- `src/database.py` - Работа с БД
- `src/filters.py` - Фильтры контента
- `src/parser_integration.py` - Интеграция с парсером

### Структура парсера
- `techpark_parser.py` - Парсер
- `techpark_api.py` - Flask API
- `postgresql_parser.py` - PostgreSQL интеграция

## 📄 Лицензия

MIT License

## 👨‍💻 Автор

Grigson69

---

**Готово к продакшену!** 🚀