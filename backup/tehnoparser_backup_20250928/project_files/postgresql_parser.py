#!/usr/bin/env python3
"""
Парсер для работы с PostgreSQL базой данных
"""

import psycopg2
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PostgreSQLParser:
    """Парсер для работы с PostgreSQL базой данных"""
    
    def __init__(self):
        """Инициализация подключения к PostgreSQL"""
        self.postgres_config = {
            'host': 'postgresql-grigson69.alwaysdata.net',
            'port': 5432,
            'database': 'grigson69_2',
            'user': 'grigson69',
            'password': 'grigson96911'
        }
        self.connection = None
        
    def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.connection = psycopg2.connect(**self.postgres_config)
            logger.info("✅ Подключение к PostgreSQL установлено")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Отключение от PostgreSQL"""
        if self.connection:
            self.connection.close()
            logger.info("✅ Отключение от PostgreSQL")
    
    def get_unique_books_from_db(self, limit: int = 100) -> List[Dict]:
        """Получение уникальных книг из PostgreSQL (без дубликатов)"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            # Получаем уникальные книги по названию, берем самую новую запись для каждого
            query = """
            SELECT DISTINCT ON (title) 
                id, book_id, title, author, price, category, book_url, image_url, 
                rating, availability, parsed_date, created_at
            FROM books_table 
            ORDER BY title, created_at DESC 
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            columns = [desc[0] for desc in cursor.description]
            books = []
            
            for row in cursor.fetchall():
                book = dict(zip(columns, row))
                books.append(book)
            
            cursor.close()
            logger.info(f"📚 Получено {len(books)} уникальных книг из PostgreSQL")
            return books
            
        except Exception as e:
            logger.error(f"❌ Ошибка при получении книг из PostgreSQL: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Получение статистики из PostgreSQL"""
        if not self.connection:
            if not self.connect():
                return {"total_products": 0, "categories": {}, "average_price": 0}
        
        try:
            cursor = self.connection.cursor()
            
            # Общее количество уникальных книг
            cursor.execute("""
                SELECT COUNT(DISTINCT title) 
                FROM books_table
            """)
            total_products = cursor.fetchone()[0]
            
            # Статистика по категориям
            cursor.execute("""
                SELECT category, COUNT(DISTINCT title) as count
                FROM books_table 
                GROUP BY category
            """)
            categories = dict(cursor.fetchall())
            
            # Средняя цена
            cursor.execute("""
                SELECT AVG(price) 
                FROM books_table 
                WHERE price IS NOT NULL
            """)
            avg_price = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            return {
                "total_products": total_products,
                "categories": categories,
                "average_price": round(float(avg_price), 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка при получении статистики: {e}")
            return {"total_products": 0, "categories": {}, "average_price": 0}
    
    def search_books(self, query: str, limit: int = 50) -> List[Dict]:
        """Поиск книг в PostgreSQL"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor()
            
            # Поиск по названию и автору
            search_query = """
            SELECT DISTINCT ON (title) 
                id, book_id, title, author, price, category, book_url, image_url, 
                rating, availability, parsed_date, created_at
            FROM books_table 
            WHERE LOWER(title) LIKE LOWER(%s) OR LOWER(author) LIKE LOWER(%s)
            ORDER BY title, created_at DESC 
            LIMIT %s
            """
            
            search_term = f"%{query}%"
            cursor.execute(search_query, (search_term, search_term, limit))
            columns = [desc[0] for desc in cursor.description]
            books = []
            
            for row in cursor.fetchall():
                book = dict(zip(columns, row))
                books.append(book)
            
            cursor.close()
            logger.info(f"🔍 Найдено {len(books)} книг по запросу '{query}'")
            return books
            
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске книг: {e}")
            return []
