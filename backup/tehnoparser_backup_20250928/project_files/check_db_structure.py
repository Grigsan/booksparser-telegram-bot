#!/usr/bin/env python3
"""
Проверка структуры базы данных
"""

import sqlite3

def check_database_structure():
    """Проверяем структуру базы данных"""
    
    try:
        conn = sqlite3.connect("books_products.db")
        cursor = conn.cursor()
        
        # Получаем информацию о таблицах
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("📋 Таблицы в базе данных:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Проверяем структуру таблицы products
        cursor.execute("PRAGMA table_info(products);")
        columns = cursor.fetchall()
        print("\n📊 Структура таблицы 'products':")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"\n📚 Всего записей: {count}")
        
        # Показываем несколько примеров
        cursor.execute("SELECT * FROM products LIMIT 3")
        examples = cursor.fetchall()
        print(f"\n📖 Примеры записей:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_database_structure()
