-- Скрипт для создания таблицы книг в PostgreSQL
-- Создан: 2025-09-28

-- Создание таблицы книг
CREATE TABLE IF NOT EXISTS books_table (
    id SERIAL PRIMARY KEY,
    book_id INTEGER,
    title TEXT NOT NULL,
    author TEXT,
    price DECIMAL(10,2),
    category TEXT,
    book_url TEXT,
    image_url TEXT,
    rating DECIMAL(3,1),
    availability TEXT DEFAULT 'In stock',
    parsed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_books_category ON books_table(category);
CREATE INDEX IF NOT EXISTS idx_books_author ON books_table(author);
CREATE INDEX IF NOT EXISTS idx_books_price ON books_table(price);
CREATE INDEX IF NOT EXISTS idx_books_rating ON books_table(rating);

-- Комментарии к таблице
COMMENT ON TABLE books_table IS 'Таблица с информацией о книгах из Books to Scrape';
COMMENT ON COLUMN books_table.book_id IS 'ID книги из исходной базы';
COMMENT ON COLUMN books_table.title IS 'Название книги';
COMMENT ON COLUMN books_table.author IS 'Автор книги';
COMMENT ON COLUMN books_table.price IS 'Цена в фунтах стерлингов';
COMMENT ON COLUMN books_table.category IS 'Категория книги';
COMMENT ON COLUMN books_table.book_url IS 'Ссылка на страницу книги';
COMMENT ON COLUMN books_table.image_url IS 'Ссылка на изображение книги';
COMMENT ON COLUMN books_table.rating IS 'Рейтинг книги (1-5 звезд)';
COMMENT ON COLUMN books_table.availability IS 'Наличие в наличии';
COMMENT ON COLUMN books_table.parsed_date IS 'Дата парсинга';
COMMENT ON COLUMN books_table.created_at IS 'Дата создания записи';

-- Примеры запросов:

-- 1. Все книги
-- SELECT * FROM books_table ORDER BY title;

-- 2. Книги по категориям
-- SELECT category, COUNT(*) as count 
-- FROM books_table 
-- GROUP BY category 
-- ORDER BY count DESC;

-- 3. Самые дорогие книги
-- SELECT title, author, price 
-- FROM books_table 
-- WHERE price IS NOT NULL 
-- ORDER BY price DESC 
-- LIMIT 10;

-- 4. Книги с высоким рейтингом
-- SELECT title, author, rating, price 
-- FROM books_table 
-- WHERE rating >= 4.0 
-- ORDER BY rating DESC;

-- 5. Поиск по автору
-- SELECT title, price, rating 
-- FROM books_table 
-- WHERE author LIKE '%Shakespeare%';

-- 6. Статистика по ценам
-- SELECT 
--     MIN(price) as min_price,
--     MAX(price) as max_price,
--     AVG(price) as avg_price,
--     COUNT(*) as total_books
-- FROM books_table 
-- WHERE price IS NOT NULL;

-- 7. Книги по категории с пагинацией
-- SELECT title, author, price, rating
-- FROM books_table 
-- WHERE category = 'fiction'
-- ORDER BY title
-- LIMIT 20 OFFSET 0;

-- 8. Поиск книг по названию
-- SELECT title, author, price, category
-- FROM books_table 
-- WHERE title ILIKE '%python%'
-- ORDER BY title;

-- 9. Топ авторов по количеству книг
-- SELECT author, COUNT(*) as book_count
-- FROM books_table 
-- WHERE author IS NOT NULL
-- GROUP BY author
-- ORDER BY book_count DESC
-- LIMIT 10;

-- 10. Книги в определенном ценовом диапазоне
-- SELECT title, author, price, category
-- FROM books_table 
-- WHERE price BETWEEN 20.00 AND 50.00
-- ORDER BY price;
