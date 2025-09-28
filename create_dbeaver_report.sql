-- Создание отчета по книгам для DBeaver
-- Выполните эти запросы по порядку

-- 1. Создание представления для удобного просмотра
CREATE VIEW books_summary AS
SELECT 
    id,
    title,
    author,
    CASE 
        WHEN price IS NULL THEN 'N/A'
        ELSE '£' || CAST(price AS TEXT)
    END as price_formatted,
    category,
    CASE 
        WHEN rating IS NULL THEN 'N/A'
        ELSE CAST(rating AS TEXT) || '/5'
    END as rating_formatted,
    CASE 
        WHEN LENGTH(title) > 50 THEN SUBSTR(title, 1, 47) || '...'
        ELSE title
    END as title_short,
    book_url,
    image_url
FROM books_table;

-- 2. Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_books_title ON books_table(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books_table(author);
CREATE INDEX IF NOT EXISTS idx_books_price ON books_table(price);
CREATE INDEX IF NOT EXISTS idx_books_rating ON books_table(rating);

-- 3. Создание представления для статистики
CREATE VIEW books_statistics AS
SELECT 
    'Всего книг' as metric,
    COUNT(*) as value
FROM books_table
UNION ALL
SELECT 
    'Категорий',
    COUNT(DISTINCT category)
FROM books_table
UNION ALL
SELECT 
    'Авторов',
    COUNT(DISTINCT author)
FROM books_table
UNION ALL
SELECT 
    'Средняя цена',
    ROUND(AVG(price), 2)
FROM books_table
WHERE price IS NOT NULL
UNION ALL
SELECT 
    'Средний рейтинг',
    ROUND(AVG(rating), 2)
FROM books_table
WHERE rating IS NOT NULL;

-- 4. Создание представления для топ-книг
CREATE VIEW top_books AS
SELECT 
    title,
    author,
    price,
    rating,
    category,
    ROW_NUMBER() OVER (ORDER BY price DESC) as price_rank,
    ROW_NUMBER() OVER (ORDER BY rating DESC) as rating_rank
FROM books_table
WHERE price IS NOT NULL AND rating IS NOT NULL;

-- 5. Создание представления для категорий
CREATE VIEW category_summary AS
SELECT 
    category,
    COUNT(*) as book_count,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(rating), 2) as avg_rating,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM books_table
GROUP BY category
ORDER BY book_count DESC;
