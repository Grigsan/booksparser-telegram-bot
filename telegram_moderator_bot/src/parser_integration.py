"""
Модуль интеграции с парсером книг
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional
from .config import Config

logger = logging.getLogger(__name__)

class ParserIntegration:
    """Класс для интеграции с парсером книг"""
    
    def __init__(self):
        self.config = Config()
        # URL API парсера (из docker-compose сети)
        self.parser_api_url = "http://tehnoparser-api:5000"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Выполнение HTTP запроса с retry логикой"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession()
                
                async with self.session.request(method, url, **kwargs) as response:
                    return response
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Попытка {attempt + 1} неудачна, повторяем через 2 секунды: {e}")
                await asyncio.sleep(2)
    
    async def start_parsing(self) -> Dict:
        """Запуск парсинга книг"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Проверяем доступность API перед запросом
            health_check = await self.check_parser_health()
            if not health_check["success"]:
                return {
                    "success": False,
                    "message": f"Парсер недоступен: {health_check['message']}",
                    "error": "parser_unavailable"
                }
            
            response = await self._make_request(
                "POST",
                f"{self.parser_api_url}/parse",
                json={"force": True},
                timeout=aiohttp.ClientTimeout(total=300)  # 5 минут таймаут
            )
            
            if response.status == 200:
                result = await response.json()
                logger.info(f"✅ Парсинг запущен: {result}")
                return {
                    "success": True,
                    "message": f"Парсинг запущен! Обработано: {result.get('parsed_count', 0)} книг",
                    "data": result
                }
            else:
                error_text = await response.text()
                logger.error(f"❌ Ошибка парсинга: {response.status} - {error_text}")
                return {
                    "success": False,
                    "message": f"Ошибка запуска парсинга: {response.status}",
                    "error": error_text
                }
        except asyncio.TimeoutError:
            logger.error("⏰ Таймаут парсинга")
            return {
                "success": False,
                "message": "Парсинг занял слишком много времени",
                "error": "timeout"
            }
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к парсеру: {e}")
            return {
                "success": False,
                "message": f"Ошибка подключения к парсеру: {str(e)}",
                "error": str(e)
            }
    
    async def get_books_stats(self) -> Dict:
        """Получение статистики книг"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.parser_api_url}/stats",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"📊 Статистика получена: {result}")
                    return {
                        "success": True,
                        "data": result.get("stats", {}),
                        "message": "Статистика загружена"
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка получения статистики: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "message": f"Ошибка получения статистики: {response.status}",
                        "error": error_text
                    }
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {
                "success": False,
                "message": f"Ошибка подключения к парсеру: {str(e)}",
                "error": str(e)
            }
    
    async def get_books_list(self, limit: int = 10) -> Dict:
        """Получение списка книг"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.parser_api_url}/products?limit={limit}",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    books = result.get("products", [])
                    logger.info(f"📚 Получено книг: {len(books)}")
                    return {
                        "success": True,
                        "data": books,
                        "count": len(books),
                        "message": f"Найдено {len(books)} книг"
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка получения книг: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "message": f"Ошибка получения книг: {response.status}",
                        "error": error_text
                    }
        except Exception as e:
            logger.error(f"❌ Ошибка получения книг: {e}")
            return {
                "success": False,
                "message": f"Ошибка подключения к парсеру: {str(e)}",
                "error": str(e)
            }
    
    async def search_books(self, query: str, limit: int = 10) -> Dict:
        """Поиск книг"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.parser_api_url}/search?q={query}&limit={limit}",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    books = result.get("products", [])
                    logger.info(f"🔍 Найдено книг по запросу '{query}': {len(books)}")
                    return {
                        "success": True,
                        "data": books,
                        "count": len(books),
                        "query": query,
                        "message": f"Найдено {len(books)} книг по запросу '{query}'"
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка поиска книг: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "message": f"Ошибка поиска книг: {response.status}",
                        "error": error_text
                    }
        except Exception as e:
            logger.error(f"❌ Ошибка поиска книг: {e}")
            return {
                "success": False,
                "message": f"Ошибка подключения к парсеру: {str(e)}",
                "error": str(e)
            }
    
    async def get_categories(self) -> Dict:
        """Получение категорий книг"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.parser_api_url}/categories",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    categories = result.get("categories", [])
                    logger.info(f"🏷️ Получено категорий: {len(categories)}")
                    return {
                        "success": True,
                        "data": categories,
                        "count": len(categories),
                        "message": f"Найдено {len(categories)} категорий"
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка получения категорий: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "message": f"Ошибка получения категорий: {response.status}",
                        "error": error_text
                    }
        except Exception as e:
            logger.error(f"❌ Ошибка получения категорий: {e}")
            return {
                "success": False,
                "message": f"Ошибка подключения к парсеру: {str(e)}",
                "error": str(e)
            }
    
    async def check_parser_health(self) -> Dict:
        """Проверка состояния парсера"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.parser_api_url}/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "status": "healthy",
                        "data": result,
                        "message": "Парсер работает нормально"
                    }
                else:
                    return {
                        "success": False,
                        "status": "unhealthy",
                        "message": f"Парсер недоступен: {response.status}"
                    }
        except Exception as e:
            logger.error(f"❌ Ошибка проверки парсера: {e}")
            return {
                "success": False,
                "status": "error",
                "message": f"Ошибка подключения к парсеру: {str(e)}"
            }
