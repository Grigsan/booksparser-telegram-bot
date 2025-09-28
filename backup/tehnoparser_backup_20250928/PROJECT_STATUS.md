# 📚 Tehnoparser - Состояние проекта на 28.09.2025

## ✅ **Текущий статус: РАБОТАЕТ**

### 🚀 **Запущенные сервисы:**
- **Frontend**: http://localhost:80 (Nginx)
- **API**: http://localhost:5000 (Flask + PostgreSQL)
- **База данных**: PostgreSQL (grigson69_2)

### 📊 **Данные в системе:**
- **Всего книг**: 71 запись в PostgreSQL
- **Уникальных книг**: 68 (API фильтрует дубликаты)
- **Категории**: 4 (books: 20, fiction: 20, mystery: 20, travel: 11)
- **Средняя цена**: £36.74

### 🐳 **Docker контейнеры:**
```
tehnoparser-api      - Up (healthy)     - Порт 5000
tehnoparser-frontend - Up (unhealthy)   - Порт 80  
dbhub                - Up               - Порт 8081
```

### 📁 **Структура проекта:**
```
Tehnoparser/
├── techpark_api.py          # Flask API сервер
├── techpark_parser.py       # Парсер для SQLite
├── postgresql_parser.py     # Парсер для PostgreSQL
├── docker-compose.yml       # Docker конфигурация
├── nginx/                   # Nginx конфигурация
├── public/                  # Веб-интерфейс
└── backup/                  # Резервные копии
```

### 🔧 **Технологии:**
- **Backend**: Python, Flask, PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL (grigson69_2)
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx

### 📋 **API эндпоинты:**
- `GET /products` - Список книг (68 уникальных)
- `GET /stats` - Статистика
- `GET /categories` - Категории (4 шт.)
- `GET /search?q=query` - Поиск книг
- `POST /parse` - Запуск парсинга

### 🎯 **Особенности:**
- ✅ Фильтрация дубликатов по названию
- ✅ Работа с PostgreSQL базой данных
- ✅ Веб-интерфейс с поиском и фильтрацией
- ✅ Docker контейнеризация
- ✅ Nginx проксирование

### 🚨 **Известные проблемы:**
- Frontend контейнер показывает "unhealthy" (но работает)
- 3 дубликата в базе данных (Soumission, It's Only the Himalayas, Sharp Objects)

### 📦 **Резервные копии:**
- **Файлы проекта**: `backup/tehnoparser_backup_20250928/project_files/`
- **База данных**: `backup/tehnoparser_backup_20250928/postgresql_backup.json`
- **Архив**: `backup/tehnoparser_backup_20250928.zip`

### 🔄 **Восстановление проекта:**
1. Распаковать архив `tehnoparser_backup_20250928.zip`
2. Восстановить файлы из `project_files/`
3. Импортировать данные из `postgresql_backup.json`
4. Запустить: `docker-compose up -d`

---
**Дата создания резервной копии**: 28.09.2025 18:30
**Статус**: ✅ Все системы работают
