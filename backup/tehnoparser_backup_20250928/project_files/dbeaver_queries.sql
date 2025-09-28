-- Готовые запросы для анализа в DBeaver
-- Копируйте и выполняйте по одному

-- 📊 ОБЩАЯ СТАТИСТИКА
SELECT 
    'Всего книг' as "Метрика",
    COUNT(*) as "Значение"
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
    'Средняя цена (£)',
    ROUND(AVG(price), 2)
FROM books_table
WHERE price IS NOT NULL
UNION ALL
SELECT 
    'Средний рейтинг',
    ROUND(AVG(rating), 2)
FROM books_table
WHERE rating IS NOT NULL;

-- 📚 ВСЕ КНИГИ (с форматированием)
SELECT 
    id as "ID",
    title as "Название",
    author as "Автор",
    CASE 
        WHEN price IS NULL THEN 'N/A'
        ELSE '£' || CAST(price AS TEXT)
    END as "Цена",
    category as "Категория",
    CASE 
        WHEN rating IS NULL THEN 'N/A'
        ELSE CAST(rating AS TEXT) || '/5'
    END as "Рейтинг",
    book_url as "Ссылка"
FROM books_table 
ORDER BY title;

-- 🏷️ СТАТИСТИКА ПО КАТЕГОРИЯМ
SELECT 
    category as "Категория",
    COUNT(*) as "Количество книг",
    ROUND(AVG(price), 2) as "Средняя цена",
    ROUND(AVG(rating), 2) as "Средний рейтинг",
    MIN(price) as "Мин. цена",
    MAX(price) as "Макс. цена"
FROM books_table
GROUP BY category 
ORDER BY COUNT(*) DESC;

-- 💰 САМЫЕ ДОРОГИЕ КНИГИ
SELECT 
    title as "Название",
    author as "Автор",
    '£' || CAST(price AS TEXT) as "Цена",
    category as "Категория",
    CAST(rating AS TEXT) || '/5' as "Рейтинг"
FROM books_table 
WHERE price IS NOT NULL 
ORDER BY price DESC 
LIMIT 10;

-- ⭐ КНИГИ С ВЫСОКИМ РЕЙТИНГОМ
SELECT 
    title as "Название",
    author as "Автор",
    CAST(rating AS TEXT) || '/5' as "Рейтинг",
    '£' || CAST(price AS TEXT) as "Цена",
    category as "Категория"
FROM books_table 
WHERE rating >= 4.0 
ORDER BY rating DESC;

-- 🔍 ПОИСК ПО НАЗВАНИЮ (замените 'Shakespeare' на нужное)
SELECT 
    title as "Название",
    author as "Автор",
    '£' || CAST(price AS TEXT) as "Цена",
    category as "Категория"
FROM books_table 
WHERE title LIKE '%Shakespeare%'
ORDER BY title;

-- 📈 ЦЕНОВЫЕ ДИАПАЗОНЫ
SELECT 
    CASE 
        WHEN price < 20 THEN 'До £20'
        WHEN price BETWEEN 20 AND 40 THEN '£20-40'
        WHEN price BETWEEN 40 AND 60 THEN '£40-60'
        ELSE 'Свыше £60'
    END as "Ценовой диапазон",
    COUNT(*) as "Количество книг",
    ROUND(AVG(rating), 2) as "Средний рейтинг"
FROM books_table 
WHERE price IS NOT NULL
GROUP BY 
    CASE 
        WHEN price < 20 THEN 'До £20'
        WHEN price BETWEEN 20 AND 40 THEN '£20-40'
        WHEN price BETWEEN 40 AND 60 THEN '£40-60'
        ELSE 'Свыше £60'
    END
ORDER BY MIN(price);

-- 👥 ТОП АВТОРОВ
SELECT 
    author as "Автор",
    COUNT(*) as "Количество книг",
    ROUND(AVG(price), 2) as "Средняя цена",
    ROUND(AVG(rating), 2) as "Средний рейтинг"
FROM books_table 
WHERE author IS NOT NULL
GROUP BY author
ORDER BY COUNT(*) DESC
LIMIT 10;

-- 📊 РЕЙТИНГОВОЕ РАСПРЕДЕЛЕНИЕ
SELECT 
    CAST(rating AS TEXT) || '/5' as "Рейтинг",
    COUNT(*) as "Количество книг",
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM books_table WHERE rating IS NOT NULL), 1) as "Процент"
FROM books_table 
WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY rating DESC;
