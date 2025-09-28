#!/usr/bin/env python3
"""
Скрипт для экспорта данных книг в PostgreSQL
"""

import sqlite3
import psycopg2
import json
from datetime import datetime
import os

def export_to_postgresql():
    """Экспорт данных из SQLite в PostgreSQL"""
    
    # Параметры подключения к PostgreSQL
    POSTGRES_CONFIG = {
        'host': 'postgresql-grigson69.alwaysdata.net',
        'port': 5432,
        'database': 'grigson69_2',
        'user': 'grigson69',
        'password': 'grigson96911'
    }
    
    # Подключаемся к SQLite (используем исходную базу)
    sqlite_conn = sqlite3.connect("books_products.db")
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # Подключаемся к PostgreSQL
        postgres_conn = psycopg2.connect(**POSTGRES_CONFIG)
        postgres_cursor = postgres_conn.cursor()
        
        print("✅ Подключение к PostgreSQL установлено")
        
        # Создаем таблицу если не существует
        create_table_sql = """
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
        """
        
        postgres_cursor.execute(create_table_sql)
        postgres_conn.commit()
        print("✅ Таблица books_table создана/проверена")
        
        # Очищаем таблицу
        postgres_cursor.execute("DELETE FROM books_table")
        postgres_conn.commit()
        print("✅ Таблица очищена")
        
        # Получаем данные из SQLite (из таблицы products)
        sqlite_cursor.execute("""
            SELECT id, name, brand, price, category, product_url, image_url, rating, availability, created_at
            FROM products 
            ORDER BY id
        """)
        books = sqlite_cursor.fetchall()
        
        print(f"📚 Найдено {len(books)} книг для экспорта")
        
        # Вставляем данные в PostgreSQL
        insert_sql = """
        INSERT INTO books_table 
        (book_id, title, author, price, category, book_url, image_url, rating, availability, parsed_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for book in books:
            book_id, title, author, price, category, book_url, image_url, rating, availability, created_at = book
            
            postgres_cursor.execute(insert_sql, (
                book_id,
                title,
                author,
                price,
                category,
                book_url,
                image_url,
                rating,
                availability or 'In stock',
                created_at
            ))
        
        postgres_conn.commit()
        print(f"✅ Экспортировано {len(books)} книг в PostgreSQL")
        
        # Проверяем результат
        postgres_cursor.execute("SELECT COUNT(*) FROM books_table")
        count = postgres_cursor.fetchone()[0]
        print(f"📊 Всего записей в PostgreSQL: {count}")
        
        # Статистика по категориям
        postgres_cursor.execute("SELECT category, COUNT(*) FROM books_table GROUP BY category")
        categories = postgres_cursor.fetchall()
        
        print("\n📊 Статистика по категориям:")
        for cat, cat_count in categories:
            print(f"   - {cat}: {cat_count} книг")
        
        # Статистика по ценам
        postgres_cursor.execute("""
            SELECT 
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price) as avg_price
            FROM books_table 
            WHERE price IS NOT NULL
        """)
        price_stats = postgres_cursor.fetchone()
        
        print(f"\n💰 Статистика по ценам:")
        print(f"   - Минимальная цена: £{price_stats[0]:.2f}")
        print(f"   - Максимальная цена: £{price_stats[1]:.2f}")
        print(f"   - Средняя цена: £{price_stats[2]:.2f}")
        
        postgres_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте в PostgreSQL: {e}")
        return False
    
    finally:
        sqlite_conn.close()

def test_postgresql_connection():
    """Тестирование подключения к PostgreSQL"""
    
    POSTGRES_CONFIG = {
        'host': 'postgresql-grigson69.alwaysdata.net',
        'port': 5432,
        'database': 'grigson69_2',
        'user': 'grigson69',
        'password': 'grigson96911'
    }
    
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Подключение к PostgreSQL успешно!")
        print(f"📊 Версия: {version}")
        
        # Проверяем существующие таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print(f"📋 Существующие таблицы:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Начинаем экспорт книг в PostgreSQL...")
    
    # Сначала тестируем подключение
    if test_postgresql_connection():
        print("\n" + "="*50)
        
        # Экспортируем данные
        if export_to_postgresql():
            print("\n✅ Экспорт в PostgreSQL завершен успешно!")
        else:
            print("\n❌ Экспорт в PostgreSQL не удался!")
    else:
        print("\n❌ Не удалось подключиться к PostgreSQL!")
