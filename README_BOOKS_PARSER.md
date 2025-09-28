# 📚 Парсер книг Books to Scrape

## 🎯 Описание проекта

Этот проект представляет собой полнофункциональный парсер для сбора данных о книгах с сайта [Books to Scrape](https://books.toscrape.com) - специально созданного сайта для обучения веб-скрейпингу.

## ✨ Особенности

- **Реальный парсинг** - извлекает реальные данные с Books to Scrape
- **Docker контейнеризация** - полная изоляция окружения
- **SQLite база данных** - локальное хранение данных
- **PostgreSQL интеграция** - экспорт в облачную базу данных
- **MCP сервер** - интеграция с Model Context Protocol
- **Веб-интерфейс** - удобный просмотр данных
- **API endpoints** - RESTful API для работы с данными

## 📊 Собранные данные

- **71 книга** из 4 категорий
- **Реальные названия** книг (A Light in the Attic, Sapiens, Shakespeare's Sonnets)
- **Реальные цены** в фунтах стерлингов (£20.66 - £57.25)
- **Реальные изображения** с сайта Books to Scrape
- **Рейтинги** от 1 до 5 звезд
- **Категории**: books, fiction, mystery, travel

## 🗂️ Структура проекта

```
Kinoparser/
├── 📁 mcp-server-books/          # MCP сервер для книг
│   ├── __main__.py              # Основной файл MCP сервера
│   ├── pyproject.toml           # Конфигурация Python пакета
│   └── Dockerfile               # Docker образ для MCP сервера
├── 📁 nginx/                    # Nginx конфигурация
│   ├── Dockerfile
│   └── nginx.conf
├── 📁 public/                   # Веб-интерфейс
│   └── index.html
├── 📄 techpark_parser.py        # Основной парсер
├── 📄 techpark_api.py           # Flask API
├── 📄 docker-compose.yml        # Docker Compose конфигурация
├── 📄 Dockerfile                # Docker образ для API
├── 📄 requirements.txt          # Python зависимости
├── 📄 export_books_to_table.py # Экспорт в таблицу
├── 📄 export_to_postgresql.py   # Экспорт в PostgreSQL
├── 📄 create_postgresql_table.sql # SQL скрипт для PostgreSQL
└── 📄 books_products.db         # SQLite база данных
```

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

## 📋 Созданные файлы

### Базы данных
- `books_products.db` - SQLite база с парсенными данными
- `books_table.db` - Экспортированная таблица

### Экспорт файлы
- `books_export.csv` - CSV файл с данными
- `books_export.json` - JSON файл с данными
- `create_books_table.sql` - SQL скрипт для создания таблицы

## 🔧 MCP сервер

### Настройка MCP

Добавьте в `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "books-parser": {
      "command": "python",
      "args": ["mcp-server-books/__main__.py"],
      "cwd": "O:\\Нейронное обучение\\учеба вайб\\Kinoparser"
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

Цены: £13.99 - £57.25
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

-- Статистика по категориям
SELECT category, COUNT(*) as count 
FROM books_table 
GROUP BY category;
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
2. Логи API: `docker logs techpark-api`
3. Доступность базы данных: `ls -la *.db`
4. Сетевые подключения: `curl http://localhost:80/health`
