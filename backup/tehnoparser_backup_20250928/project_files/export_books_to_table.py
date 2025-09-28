#!/usr/bin/env python3
"""
Скрипт для экспорта данных книг из SQLite в таблицу
Создает SQL таблицу и вставляет все спарсенные данные
"""

import sqlite3
import json
import csv
from datetime import datetime
import os

def export_books_to_sql_table():
    """Экспорт книг в SQL таблицу"""
    
    # Подключаемся к базе данных парсера
    source_db = "books_products.db"
    if not os.path.exists(source_db):
        print(f"❌ База данных {source_db} не найдена!")
        return False
    
    try:
        # Подключаемся к исходной базе
        source_conn = sqlite3.connect(source_db)
        source_cursor = source_conn.cursor()
        
        # Получаем все книги
        source_cursor.execute("""
            SELECT id, name, brand, price, category, product_url, image_url, rating, created_at
            FROM products 
            ORDER BY id
        """)
        
        books = source_cursor.fetchall()
        print(f"📚 Найдено {len(books)} книг для экспорта")
        
        # Создаем новую базу данных для таблицы
        output_db = "books_table.db"
        output_conn = sqlite3.connect(output_db)
        output_cursor = output_conn.cursor()
        
        # Создаем таблицу книг
        output_cursor.execute("""
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
                availability TEXT,
                parsed_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Очищаем таблицу перед вставкой
        output_cursor.execute("DELETE FROM books_table")
        
        # Вставляем данные
        for book in books:
            book_id, name, brand, price, category, product_url, image_url, rating, created_at = book
            
            output_cursor.execute("""
                INSERT INTO books_table 
                (book_id, title, author, price, category, book_url, image_url, rating, parsed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                book_id,
                name,
                brand or "Unknown Author",
                price,
                category,
                product_url,
                image_url,
                rating,
                created_at
            ))
        
        output_conn.commit()
        print(f"✅ Экспортировано {len(books)} книг в таблицу {output_db}")
        
        # Создаем также CSV файл
        csv_filename = "books_export.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Заголовки
            writer.writerow([
                'ID', 'Title', 'Author', 'Price (£)', 'Category', 
                'Book URL', 'Image URL', 'Rating', 'Parsed Date'
            ])
            
            # Данные
            for book in books:
                book_id, name, brand, price, category, product_url, image_url, rating, created_at = book
                writer.writerow([
                    book_id,
                    name,
                    brand or "Unknown Author",
                    f"£{price:.2f}" if price else "N/A",
                    category,
                    product_url,
                    image_url,
                    f"{rating}/5" if rating else "N/A",
                    created_at
                ])
        
        print(f"📄 Создан CSV файл: {csv_filename}")
        
        # Создаем JSON файл
        json_filename = "books_export.json"
        books_data = []
        
        for book in books:
            book_id, name, brand, price, category, product_url, image_url, rating, created_at = book
            books_data.append({
                "id": book_id,
                "title": name,
                "author": brand or "Unknown Author",
                "price": price,
                "price_formatted": f"£{price:.2f}" if price else "N/A",
                "category": category,
                "book_url": product_url,
                "image_url": image_url,
                "rating": rating,
                "rating_formatted": f"{rating}/5" if rating else "N/A",
                "parsed_date": created_at
            })
        
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(books_data, jsonfile, ensure_ascii=False, indent=2)
        
        print(f"📄 Создан JSON файл: {json_filename}")
        
        # Статистика
        output_cursor.execute("SELECT COUNT(*) FROM books_table")
        count = output_cursor.fetchone()[0]
        
        output_cursor.execute("SELECT category, COUNT(*) FROM books_table GROUP BY category")
        categories = output_cursor.fetchall()
        
        print(f"\n📊 Статистика таблицы:")
        print(f"   Всего книг: {count}")
        print(f"   Категории:")
        for cat, cat_count in categories:
            print(f"     - {cat}: {cat_count} книг")
        
        # Закрываем соединения
        source_conn.close()
        output_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        return False

def create_sql_script():
    """Создает SQL скрипт для создания таблицы"""
    
    sql_script = """
-- Скрипт для создания таблицы книг
-- Создан: {date}

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
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with open("create_books_table.sql", "w", encoding="utf-8") as f:
        f.write(sql_script)
    
    print("📄 Создан SQL скрипт: create_books_table.sql")

if __name__ == "__main__":
    print("🚀 Начинаем экспорт книг в таблицу...")
    
    # Создаем SQL скрипт
    create_sql_script()
    
    # Экспортируем данные
    if export_books_to_sql_table():
        print("\n✅ Экспорт завершен успешно!")
        print("\n📁 Созданные файлы:")
        print("   - books_table.db (SQLite база данных)")
        print("   - books_export.csv (CSV файл)")
        print("   - books_export.json (JSON файл)")
        print("   - create_books_table.sql (SQL скрипт)")
    else:
        print("\n❌ Экспорт не удался!")
