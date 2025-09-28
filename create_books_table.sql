
-- Скрипт для создания таблицы книг
-- Создан: 2025-09-28 16:58:49

CREATE TABLE IF NOT EXISTS books_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    title TEXT NOT NULL,
    author TEXT,
    price REAL,
    category TEXT,
    book_url TEXT,
    image_url TEXT,
    rating REAL,
    availability TEXT DEFAULT 'In stock',
    parsed_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_books_category ON books_table(category);
CREATE INDEX IF NOT EXISTS idx_books_author ON books_table(author);
CREATE INDEX IF NOT EXISTS idx_books_price ON books_table(price);

-- Примеры запросов:

-- 1. Все книги
SELECT * FROM books_table ORDER BY title;

-- 2. Книги по категориям
SELECT category, COUNT(*) as count 
FROM books_table 
GROUP BY category 
ORDER BY count DESC;

-- 3. Самые дорогие книги
SELECT title, author, price 
FROM books_table 
WHERE price IS NOT NULL 
ORDER BY price DESC 
LIMIT 10;

-- 4. Книги с высоким рейтингом
SELECT title, author, rating, price 
FROM books_table 
WHERE rating >= 4.0 
ORDER BY rating DESC;

-- 5. Поиск по автору
SELECT title, price, rating 
FROM books_table 
WHERE author LIKE '%Shakespeare%';

-- 6. Статистика по ценам
SELECT 
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price,
    COUNT(*) as total_books
FROM books_table 
WHERE price IS NOT NULL;
