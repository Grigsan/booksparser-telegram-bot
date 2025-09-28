"""
Flask API для парсера Технопарка
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from techpark_parser import TehnoparserBooks
from postgresql_parser import PostgreSQLParser
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Инициализация парсеров
parser = TehnoparserBooks()
postgres_parser = PostgreSQLParser()

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья API"""
    return jsonify({
        "status": "healthy",
        "service": "techpark-api",
        "timestamp": parser.get_stats()
    })

@app.route('/products', methods=['GET'])
def get_products():
    """Получение списка товаров из PostgreSQL (только уникальные)"""
    try:
        limit = request.args.get('limit', 100, type=int)
        products = postgres_parser.get_unique_books_from_db(limit)
        
        return jsonify({
            "products": products,
            "count": len(products),
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Ошибка при получении товаров: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/parse', methods=['POST'])
def parse_products():
    """Запуск парсинга товаров"""
    try:
        data = request.get_json() or {}
        force = data.get('force', False)
        
        # Проверяем, есть ли уже товары в базе
        stats = parser.get_stats()
        if stats['total_products'] > 0 and not force:
            return jsonify({
                "message": "Товары уже загружены. Используйте force=true для повторной загрузки",
                "total_products": stats['total_products'],
                "timestamp": parser.get_stats()
            })
        
        # Запускаем парсинг
        parsed_count = parser.parse_100_products()
        
        # Получаем обновленную статистику
        updated_stats = parser.get_stats()
        
        return jsonify({
            "message": "Парсинг завершен",
            "parsed_count": parsed_count,
            "total_products": updated_stats['total_products'],
            "timestamp": updated_stats
        })
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Получение статистики из PostgreSQL"""
    try:
        stats = postgres_parser.get_stats()
        return jsonify({
            "stats": stats,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_products():
    """Поиск товаров"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        limit = request.args.get('limit', 50, type=int)
        
        if not query and not category:
            return jsonify({"error": "Необходимо указать поисковый запрос или категорию"}), 400
        
        # Поиск в PostgreSQL
        if query:
            products = postgres_parser.search_books(query, limit)
        else:
            products = postgres_parser.get_unique_books_from_db(limit)
        
        # Фильтруем по категории
        if category:
            products = [p for p in products if category.lower() in p.get('category', '').lower()]
        
        return jsonify({
            "products": products,
            "count": len(products),
            "query": query,
            "category": category,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Получение списка категорий из PostgreSQL"""
    try:
        stats = postgres_parser.get_stats()
        categories = list(stats.get('categories', {}).keys())
        
        return jsonify({
            "categories": categories,
            "count": len(categories),
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Ошибка при получении категорий: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
