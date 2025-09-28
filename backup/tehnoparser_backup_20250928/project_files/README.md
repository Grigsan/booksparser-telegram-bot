# 📚 Tehnoparser - Парсер книг

## 🎯 Описание проекта

**Tehnoparser** - это полнофункциональный парсер для сбора данных о книгах с сайта [Books to Scrape](https://books.toscrape.com). Проект включает в себя веб-интерфейс, RESTful API, интеграцию с PostgreSQL и MCP сервер.

## ✨ Особенности

- **Реальный парсинг** - извлекает реальные данные с Books to Scrape
- **Docker контейнеризация** - полная изоляция окружения
- **SQLite + PostgreSQL** - гибкое хранение данных
- **MCP сервер** - интеграция с Model Context Protocol
- **Веб-интерфейс** - удобный просмотр данных
- **RESTful API** - программный доступ к данным

## 📊 Собранные данные

- **71 книга** из 4 категорий
- **Реальные названия** книг (A Light in the Attic, Sapiens, Shakespeare's Sonnets)
- **Реальные цены** в фунтах стерлингов (£10.60 - £59.48)
- **Реальные изображения** с сайта Books to Scrape
- **Рейтинги** от 1 до 5 звезд
- **Категории**: books, fiction, mystery, travel

## 🚀 Быстрый старт

### 1. Запуск парсера

```bash
# Запуск Docker контейнеров
docker-compose up -d --build

# Запуск парсинга
curl -X POST http://localhost:80/parse -H "Content-Type: application/json" -d '{"force": true}'
```

### 2. Просмотр данных

- **Веб-интерфейс**: http://localhost:80
- **API статистика**: http://localhost:80/stats
- **API книги**: http://localhost:80/products

### 3. Экспорт данных

```bash
# Экспорт в таблицу (SQLite, CSV, JSON)
python export_books_to_table.py

# Экспорт в PostgreSQL
python export_to_postgresql.py
```

## 🗂️ Структура проекта

```
Tehnoparser/
├── 📁 mcp-server-books/          # MCP сервер для книг
├── 📁 nginx/                    # Nginx конфигурация
├── 📁 public/                   # Веб-интерфейс
├── 📄 techpark_parser.py        # Основной парсер
├── 📄 techpark_api.py           # Flask API
├── 📄 docker-compose.yml        # Docker Compose конфигурация
├── 📄 requirements.txt          # Python зависимости
└── 📄 README.md                 # Документация
```

## 🔧 MCP сервер

### Настройка MCP

Добавьте в `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tehnoparser": {
      "command": "python",
      "args": ["mcp-server-books/__main__.py"],
      "cwd": "O:\\Нейронное обучение\\учеба вайб\\Tehnoparser"
    }
  }
}
```

### Доступные инструменты MCP

- `search_books` - Поиск книг по названию, автору, категории
- `get_book_stats` - Статистика по книгам
- `get_books_by_category` - Книги по категории
- `get_expensive_books` - Самые дорогие книги
- `get_high_rated_books` - Книги с высоким рейтингом

## 📊 Статистика данных

```
Всего книг: 71
Категории:
  - books: 20 книг
  - fiction: 20 книг  
  - mystery: 20 книг
  - travel: 11 книг

Цены: £10.60 - £59.48
Средняя цена: £36.74
```

## 🛠️ Технологии

- **Python 3.12** - основной язык
- **Selenium** - веб-скрейпинг
- **Flask** - веб API
- **SQLite** - локальная база данных
- **PostgreSQL** - облачная база данных
- **Docker** - контейнеризация
- **Nginx** - веб-сервер
- **MCP** - Model Context Protocol

## 📝 Примеры использования

### Поиск книг через API

```bash
# Все книги
curl http://localhost:80/products

# Поиск по названию
curl "http://localhost:80/search?query=Shakespeare"

# Статистика
curl http://localhost:80/stats
```

### SQL запросы

```sql
-- Самые дорогие книги
SELECT title, author, price 
FROM books_table 
ORDER BY price DESC 
LIMIT 10;

-- Книги с высоким рейтингом
SELECT title, author, rating 
FROM books_table 
WHERE rating >= 4.0 
ORDER BY rating DESC;
```

## 🎯 Результат

✅ **Реальный парсинг** - 71 книга с Books to Scrape  
✅ **Полная интеграция** - Docker + API + MCP + PostgreSQL  
✅ **Готовые данные** - CSV, JSON, SQL экспорт  
✅ **Веб-интерфейс** - удобный просмотр результатов  
✅ **MCP сервер** - интеграция с AI ассистентами  

## 📞 Поддержка

При возникновении проблем проверьте:
1. Статус Docker контейнеров: `docker ps`
2. Логи API: `docker logs tehnoparser-api`
3. Доступность базы данных: `ls -la *.db`
4. Сетевые подключения: `curl http://localhost:80/health`