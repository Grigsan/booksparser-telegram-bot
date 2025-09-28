#!/usr/bin/env python3
"""
MCP Server для парсера книг Books to Scrape
Предоставляет инструменты для работы с базой данных книг
"""

import asyncio
import json
import sqlite3
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Инициализация MCP сервера
server = Server("books-parser")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """Список доступных ресурсов"""
    return [
        Resource(
            uri="books://database",
            name="Books Database",
            description="База данных с информацией о книгах",
            mimeType="application/sqlite"
        ),
        Resource(
            uri="books://export/csv",
            name="Books CSV Export",
            description="CSV файл с экспортированными данными книг",
            mimeType="text/csv"
        ),
        Resource(
            uri="books://export/json",
            name="Books JSON Export", 
            description="JSON файл с экспортированными данными книг",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Чтение ресурсов"""
    if uri == "books://database":
        # Возвращаем информацию о базе данных
        try:
            conn = sqlite3.connect("books_table.db")
            cursor = conn.cursor()
            
            # Получаем статистику
            cursor.execute("SELECT COUNT(*) FROM books_table")
            total_books = cursor.fetchone()[0]
            
            cursor.execute("SELECT category, COUNT(*) FROM books_table GROUP BY category")
            categories = cursor.fetchall()
            
            stats = {
                "total_books": total_books,
                "categories": dict(categories),
                "database_file": "books_table.db"
            }
            
            conn.close()
            return json.dumps(stats, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return f"Ошибка при чтении базы данных: {e}"
    
    elif uri == "books://export/csv":
        try:
            with open("books_export.csv", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Ошибка при чтении CSV: {e}"
    
    elif uri == "books://export/json":
        try:
            with open("books_export.json", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Ошибка при чтении JSON: {e}"
    
    else:
        return f"Неизвестный ресурс: {uri}"

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Список доступных инструментов"""
    return [
        Tool(
            name="search_books",
            description="Поиск книг в базе данных",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Поисковый запрос (название, автор, категория)"
                    },
                    "category": {
                        "type": "string", 
                        "description": "Фильтр по категории"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Минимальная цена"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Максимальная цена"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимальное количество результатов",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_book_stats",
            description="Получить статистику по книгам",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_books_by_category",
            description="Получить книги по категории",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Категория книг"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимальное количество результатов",
                        "default": 20
                    }
                },
                "required": ["category"]
            }
        ),
        Tool(
            name="get_expensive_books",
            description="Получить самые дорогие книги",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Количество книг",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_high_rated_books",
            description="Получить книги с высоким рейтингом",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_rating": {
                        "type": "number",
                        "description": "Минимальный рейтинг",
                        "default": 4.0
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Количество книг",
                        "default": 10
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Выполнение инструментов"""
    
    try:
        conn = sqlite3.connect("books_table.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if name == "search_books":
            query = arguments.get("query", "")
            category = arguments.get("category")
            min_price = arguments.get("min_price")
            max_price = arguments.get("max_price")
            limit = arguments.get("limit", 10)
            
            sql = "SELECT * FROM books_table WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (title LIKE ? OR author LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            if min_price is not None:
                sql += " AND price >= ?"
                params.append(min_price)
            
            if max_price is not None:
                sql += " AND price <= ?"
                params.append(max_price)
            
            sql += " ORDER BY title LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            books = cursor.fetchall()
            
            result = []
            for book in books:
                result.append({
                    "id": book["id"],
                    "title": book["title"],
                    "author": book["author"],
                    "price": book["price"],
                    "category": book["category"],
                    "rating": book["rating"],
                    "book_url": book["book_url"]
                })
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "get_book_stats":
            cursor.execute("SELECT COUNT(*) FROM books_table")
            total_books = cursor.fetchone()[0]
            
            cursor.execute("SELECT category, COUNT(*) FROM books_table GROUP BY category")
            categories = dict(cursor.fetchall())
            
            cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM books_table WHERE price IS NOT NULL")
            price_stats = cursor.fetchone()
            
            cursor.execute("SELECT AVG(rating) FROM books_table WHERE rating IS NOT NULL")
            avg_rating = cursor.fetchone()[0]
            
            stats = {
                "total_books": total_books,
                "categories": categories,
                "price_stats": {
                    "min_price": price_stats[0],
                    "max_price": price_stats[1], 
                    "avg_price": price_stats[2]
                },
                "avg_rating": avg_rating
            }
            
            return [TextContent(type="text", text=json.dumps(stats, ensure_ascii=False, indent=2))]
        
        elif name == "get_books_by_category":
            category = arguments["category"]
            limit = arguments.get("limit", 20)
            
            cursor.execute("""
                SELECT * FROM books_table 
                WHERE category = ? 
                ORDER BY title 
                LIMIT ?
            """, (category, limit))
            
            books = cursor.fetchall()
            result = []
            for book in books:
                result.append({
                    "id": book["id"],
                    "title": book["title"],
                    "author": book["author"],
                    "price": book["price"],
                    "rating": book["rating"]
                })
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "get_expensive_books":
            limit = arguments.get("limit", 10)
            
            cursor.execute("""
                SELECT * FROM books_table 
                WHERE price IS NOT NULL 
                ORDER BY price DESC 
                LIMIT ?
            """, (limit,))
            
            books = cursor.fetchall()
            result = []
            for book in books:
                result.append({
                    "title": book["title"],
                    "author": book["author"],
                    "price": book["price"],
                    "category": book["category"]
                })
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "get_high_rated_books":
            min_rating = arguments.get("min_rating", 4.0)
            limit = arguments.get("limit", 10)
            
            cursor.execute("""
                SELECT * FROM books_table 
                WHERE rating >= ? 
                ORDER BY rating DESC, title 
                LIMIT ?
            """, (min_rating, limit))
            
            books = cursor.fetchall()
            result = []
            for book in books:
                result.append({
                    "title": book["title"],
                    "author": book["author"],
                    "rating": book["rating"],
                    "price": book["price"]
                })
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Неизвестный инструмент: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Ошибка: {e}")]
    
    finally:
        if 'conn' in locals():
            conn.close()

async def main():
    """Главная функция"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="books-parser",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
