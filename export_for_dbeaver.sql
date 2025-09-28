-- SQL скрипт для экспорта данных книг
-- Создан: 2025-09-28

-- 1. Просмотр всех книг
SELECT 
    id,
    book_id,
    title,
    author,
    price,
    category,
    rating,
    book_url,
    image_url,
    parsed_date
FROM books_table 
ORDER BY title;

-- 2. Статистика по категориям
SELECT 
    category,
    COUNT(*) as book_count,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM books_table 
GROUP BY category 
ORDER BY book_count DESC;

-- 3. Самые дорогие книги
SELECT 
    title,
    author,
    price,
    category,
    rating
FROM books_table 
WHERE price IS NOT NULL 
ORDER BY price DESC 
LIMIT 10;

-- 4. Книги с высоким рейтингом
SELECT 
    title,
    author,
    rating,
    price,
    category
FROM books_table 
WHERE rating >= 4.0 
ORDER BY rating DESC;

-- 5. Поиск по автору (пример)
SELECT 
    title,
    author,
    price,
    rating
FROM books_table 
WHERE author LIKE '%Shakespeare%';

-- 6. Книги в определенном ценовом диапазоне
SELECT 
    title,
    author,
    price,
    category
FROM books_table 
WHERE price BETWEEN 20.00 AND 50.00
ORDER BY price;

-- 7. Топ авторов по количеству книг
SELECT 
    author,
    COUNT(*) as book_count,
    AVG(price) as avg_price
FROM books_table 
WHERE author IS NOT NULL
GROUP BY author
ORDER BY book_count DESC
LIMIT 10;

-- 8. Общая статистика
SELECT 
    COUNT(*) as total_books,
    COUNT(DISTINCT category) as categories_count,
    COUNT(DISTINCT author) as authors_count,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price,
    AVG(rating) as avg_rating
FROM books_table;

-- 9. Экспорт в CSV формат (для копирования)
SELECT 
    '"' || title || '","' || 
    COALESCE(author, 'Unknown') || '","' || 
    COALESCE(CAST(price AS TEXT), 'N/A') || '","' || 
    COALESCE(category, 'Unknown') || '","' || 
    COALESCE(CAST(rating AS TEXT), 'N/A') || '","' || 
    COALESCE(book_url, '') || '","' || 
    COALESCE(image_url, '') || '"' as csv_row
FROM books_table 
ORDER BY title;
