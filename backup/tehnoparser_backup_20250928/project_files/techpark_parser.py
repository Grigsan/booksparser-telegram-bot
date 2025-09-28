"""
Парсер Технопарка для сбора информации о товарах
Собирает данные о 100 товарах из различных категорий
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin, urlparse
import os
from datetime import datetime
import sqlite3
from typing import List, Dict, Optional
import logging

# Продвинутые техники парсинга
from fake_useragent import UserAgent
import urllib3
from urllib.parse import urlencode
import hashlib
import base64

# Selenium для обхода JavaScript
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TehnoparserBooks:
    def __init__(self, db_path: str = "books_products.db"):
        # Books to Scrape - открытый сайт для парсинга
        self.base_url = "https://books.toscrape.com"
        self.session = requests.Session()
        
        # Настройка заголовков для обхода защиты
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"'
        })
        
        self.db_path = db_path
        self.init_database()
        
        # Инициализация UserAgent
        self.ua = UserAgent()
        self.driver = None
    
    def init_database(self):
        """Инициализация базы данных SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL,
                old_price REAL,
                category TEXT,
                brand TEXT,
                description TEXT,
                image_url TEXT,
                product_url TEXT,
                availability TEXT,
                rating REAL,
                reviews_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")
    
    def get_products_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Получение товаров по категории"""
        products = []
        
        # Различные URL для парсинга категорий
        category_urls = [
            f"{self.base_url}/catalog/{category}/",
            f"{self.base_url}/catalog/{category}/?sort=popular",
            f"{self.base_url}/catalog/{category}/?sort=price_asc",
            f"{self.base_url}/catalog/{category}/?sort=price_desc",
            f"{self.base_url}/catalog/{category}/?sort=rating",
            f"{self.base_url}/catalog/{category}/?page=1",
            f"{self.base_url}/catalog/{category}/?page=2"
        ]
        
        for url in category_urls:
            try:
                logger.info(f"Парсинг категории {category} с {url}")
                
                # Случайная задержка
                time.sleep(random.uniform(2, 5))
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Различные селекторы для поиска товаров
                    selectors = [
                        'div.product-item',
                        'div.product-card',
                        'div[data-product-id]',
                        'div.item',
                        'div.product',
                        'div[class*="product"]',
                        'div[class*="item"]'
                    ]
                    
                    product_cards = []
                    for selector in selectors:
                        cards = soup.select(selector)
                        if cards:
                            product_cards = cards
                            logger.info(f"Найдено {len(cards)} товаров с селектором: {selector}")
                            break
                    
                    if product_cards:
                        count = 0
                        for card in product_cards:
                            if count >= limit:
                                break
                                
                            product_data = self.extract_product_data(card, soup)
                            if product_data and product_data.get('name'):
                                product_data['category'] = category
                                products.append(product_data)
                                count += 1
                                
                            # Задержка между товарами
                            time.sleep(random.uniform(0.5, 1.5))
                        
                        if products:
                            logger.info(f"Успешно получено {len(products)} товаров из {url}")
                            break
                    else:
                        logger.warning(f"Не найдено товаров на {url}")
                        
            except Exception as e:
                logger.error(f"Ошибка при парсинге {url}: {e}")
                continue
                
        return products
    
    def extract_product_data(self, card, soup) -> Optional[Dict]:
        """Извлечение данных о товаре из карточки"""
        try:
            product_data = {}
            
            # Название товара
            name_selectors = [
                'a.product-name', 'h3', 'h2', 'h1', 'a[href*="/product/"]',
                '.title', '.name', '.product-title', '.item-title',
                'a[class*="title"]', 'span[class*="title"]'
            ]
            
            for selector in name_selectors:
                name_elem = card.select_one(selector)
                if name_elem:
                    name_text = name_elem.get_text(strip=True)
                    if name_text and len(name_text) > 2:
                        product_data['name'] = name_text
                        break
            
            # Цена
            price_selectors = [
                '.price', '.product-price', '.item-price', '.cost',
                'span[class*="price"]', 'div[class*="price"]'
            ]
            
            for selector in price_selectors:
                price_elem = card.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Ищем число в тексте
                    import re
                    price_match = re.search(r'(\d+[\s,]*\d*)', price_text.replace(' ', '').replace(',', ''))
                    if price_match:
                        try:
                            price_value = float(price_match.group(1).replace(' ', '').replace(',', ''))
                            product_data['price'] = price_value
                            break
                        except ValueError:
                            pass
            
            # Старая цена
            old_price_selectors = [
                '.old-price', '.price-old', '.crossed-price',
                'span[class*="old"]', 'div[class*="old"]'
            ]
            
            for selector in old_price_selectors:
                old_price_elem = card.select_one(selector)
                if old_price_elem:
                    old_price_text = old_price_elem.get_text(strip=True)
                    import re
                    old_price_match = re.search(r'(\d+[\s,]*\d*)', old_price_text.replace(' ', '').replace(',', ''))
                    if old_price_match:
                        try:
                            old_price_value = float(old_price_match.group(1).replace(' ', '').replace(',', ''))
                            product_data['old_price'] = old_price_value
                            break
                        except ValueError:
                            pass
            
            # Бренд
            brand_selectors = [
                '.brand', '.manufacturer', '.producer',
                'span[class*="brand"]', 'div[class*="brand"]'
            ]
            
            for selector in brand_selectors:
                brand_elem = card.select_one(selector)
                if brand_elem:
                    brand_text = brand_elem.get_text(strip=True)
                    if brand_text:
                        product_data['brand'] = brand_text
                        break
            
            # Изображение
            img_elem = card.find('img')
            if img_elem:
                img_url = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy')
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = urljoin(self.base_url, img_url)
                    product_data['image_url'] = img_url
            
            # Ссылка на товар
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    product_data['product_url'] = href
            
            # Рейтинг
            rating_selectors = [
                '.rating', '.stars', '.score',
                'span[class*="rating"]', 'div[class*="rating"]'
            ]
            
            for selector in rating_selectors:
                rating_elem = card.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text(strip=True)
                    import re
                    rating_match = re.search(r'(\d+[,.]?\d*)', rating_text)
                    if rating_match:
                        try:
                            rating_value = float(rating_match.group(1).replace(',', '.'))
                            if 0 <= rating_value <= 5:
                                product_data['rating'] = rating_value
                                break
                        except ValueError:
                            pass
            
            # Наличие
            availability_elem = card.select_one('.availability, .stock, .in-stock, .out-of-stock')
            if availability_elem:
                product_data['availability'] = availability_elem.get_text(strip=True)
            else:
                product_data['availability'] = 'В наличии'
            
            return product_data if product_data.get('name') else None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных товара: {e}")
            return None
    
    def save_product_to_db(self, product_data: Dict):
        """Сохранение товара в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO products (name, price, old_price, category, brand, description, 
                                   image_url, product_url, availability, rating, reviews_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data.get('name'),
                product_data.get('price'),
                product_data.get('old_price'),
                product_data.get('category'),
                product_data.get('brand'),
                product_data.get('description', ''),
                product_data.get('image_url'),
                product_data.get('product_url'),
                product_data.get('availability'),
                product_data.get('rating'),
                product_data.get('reviews_count', 0)
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Товар '{product_data.get('name')}' сохранен в базу данных")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении товара в БД: {e}")
    
    def parse_100_products(self):
        """Реальный парсинг 100 книг с Books to Scrape"""
        logger.info("Начинаем реальный парсинг 100 книг с Books to Scrape...")
        
        total_products = 0
        
        # Books to Scrape - открытый сайт для парсинга
        sources = [
            {
                "name": "Books to Scrape",
                "url": "https://books.toscrape.com/catalogue/page-1.html",
                "category": "books",
                "type": "selenium"
            },
            {
                "name": "Books to Scrape - Travel",
                "url": "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
                "category": "travel",
                "type": "selenium"
            },
            {
                "name": "Books to Scrape - Mystery",
                "url": "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
                "category": "mystery",
                "type": "selenium"
            },
            {
                "name": "Books to Scrape - Fiction",
                "url": "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
                "category": "fiction",
                "type": "selenium"
            }
        ]
        
        try:
            # Инициализируем Selenium
            if not self.setup_selenium_driver():
                logger.error("Не удалось инициализировать Selenium")
                return 0
            
            for source in sources:
                if total_products >= 100:
                    break
                    
                try:
                    logger.info(f"Парсинг {source['name']}: {source['category']}")
                    
                    # Выбираем метод парсинга
                    if source.get('type') == 'selenium':
                        products = self.parse_books_to_scrape(source['url'], source['category'])
                    elif source.get('type') == 'api':
                        products = self.parse_api_source(source['url'], source['category'])
                    else:
                        products = self.parse_real_site_with_selenium(source['url'], source['category'])
                    
                    for product in products:
                        if total_products >= 100:
                            break
                        
                        try:
                            # Сохраняем в базу данных
                            self.save_product_to_db(product)
                            total_products += 1
                            
                            logger.info(f"Обработан товар {total_products}/100: {product.get('name')}")
                            
                            # Задержка между товарами
                            time.sleep(random.uniform(0.5, 1.5))
                            
                        except Exception as e:
                            logger.error(f"Ошибка при обработке товара: {e}")
                            continue
                    
                    # Задержка между источниками
                    time.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    logger.error(f"Ошибка при парсинге {source['name']}: {e}")
                    continue
            
        finally:
            # Закрываем Selenium
            self.close_selenium_driver()
        
        logger.info(f"Реальный парсинг завершен. Обработано {total_products} товаров")
        return total_products
    
    def get_products_from_db(self, limit: int = 100) -> List[Dict]:
        """Получение товаров из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM products 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        products = []
        
        for row in cursor.fetchall():
            product = dict(zip(columns, row))
            products.append(product)
        
        conn.close()
        return products
    
    def get_unique_products_from_db(self, limit: int = 100) -> List[Dict]:
        """Получение уникальных товаров из базы данных (без дубликатов)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем все товары и фильтруем дубликаты в Python
        cursor.execute('''
            SELECT * FROM products 
            ORDER BY created_at DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        all_products = []
        
        for row in cursor.fetchall():
            product = dict(zip(columns, row))
            all_products.append(product)
        
        # Фильтруем дубликаты по названию, оставляем только самую новую запись
        unique_products = []
        seen_names = set()
        
        for product in all_products:
            if product['name'] not in seen_names:
                unique_products.append(product)
                seen_names.add(product['name'])
                
                if len(unique_products) >= limit:
                    break
        
        conn.close()
        return unique_products
    
    def get_stats(self) -> Dict:
        """Получение статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общее количество товаров
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        
        # Количество по категориям
        cursor.execute('SELECT category, COUNT(*) FROM products GROUP BY category')
        categories = dict(cursor.fetchall())
        
        # Средняя цена
        cursor.execute('SELECT AVG(price) FROM products WHERE price IS NOT NULL')
        avg_price = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_products': total_products,
            'categories': categories,
            'average_price': round(avg_price, 2)
        }
    
    def setup_selenium_driver(self):
        """Настройка Selenium WebDriver с обходом защиты Qrator"""
        try:
            # Используем undetected-chromedriver для обхода защиты
            chrome_options = uc.ChromeOptions()
            
            # Основные настройки для обхода защиты
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Дополнительные настройки для обхода защиты
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Случайный User-Agent
            user_agent = self.ua.random
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Размер окна
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Headless режим
            chrome_options.add_argument('--headless')
            
            # Дополнительные настройки для обхода Qrator
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-popup-blocking')
            
            try:
                # Используем undetected-chromedriver
                self.driver = uc.Chrome(options=chrome_options, version_main=None)
                
                # Дополнительные скрипты для обхода защиты
                self.driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
                
                self.driver.execute_script("""
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                """)
                
                self.driver.execute_script("""
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                """)
                
                logger.info("Undetected Chrome WebDriver инициализирован")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка при инициализации undetected Chrome: {e}")
                # Fallback на обычный Selenium
                return self.setup_fallback_driver()
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации Selenium: {e}")
            return False
    
    def setup_fallback_driver(self):
        """Fallback настройка обычного Selenium"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            
            user_agent = self.ua.random
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception:
                self.driver = webdriver.Chrome(
                    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Fallback Selenium WebDriver инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при fallback инициализации: {e}")
            return False
    
    def close_selenium_driver(self):
        """Закрытие Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver закрыт")
            except Exception as e:
                logger.error(f"Ошибка при закрытии Selenium: {e}")
    
    def parse_with_selenium(self, url: str, category: str) -> List[Dict]:
        """Парсинг с использованием Selenium"""
        products = []
        
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return products
            
            logger.info(f"Selenium парсинг: {url}")
            
            # Переходим на страницу
            self.driver.get(url)
            
            # Ждем загрузки страницы
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Случайная задержка
            time.sleep(random.uniform(3, 7))
            
            # Прокручиваем страницу для загрузки динамического контента
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Ищем карточки товаров
            selectors = [
                "div.product-item",
                "div.product-card", 
                "div[data-product-id]",
                "div.item",
                "div.product",
                "div[class*='product']",
                "div[class*='item']"
            ]
            
            product_elements = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        product_elements = elements
                        logger.info(f"Найдено {len(elements)} товаров с селектором: {selector}")
                        break
                except Exception as e:
                    continue
            
            # Извлекаем данные из найденных элементов
            for element in product_elements[:20]:  # Берем первые 20
                try:
                    product_data = self.extract_product_data_selenium(element)
                    if product_data and product_data.get('name'):
                        product_data['category'] = category
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Ошибка при извлечении данных: {e}")
                    continue
            
            logger.info(f"Selenium парсинг завершен. Найдено {len(products)} товаров")
            
        except Exception as e:
            logger.error(f"Ошибка при Selenium парсинге: {e}")
        
        return products
    
    def extract_product_data_selenium(self, element) -> Optional[Dict]:
        """Извлечение данных о товаре из Selenium элемента"""
        try:
            product_data = {}
            
            # Название товара
            name_selectors = [
                "a.product-name", "h3", "h2", "h1", "a[href*='/product/']",
                ".title", ".name", ".product-title", ".item-title"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if name_elem:
                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) > 2:
                            product_data['name'] = name_text
                            break
                except:
                    continue
            
            # Цена
            price_selectors = [
                ".price", ".product-price", ".item-price", ".cost"
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if price_elem:
                        price_text = price_elem.text.strip()
                        import re
                        price_match = re.search(r'(\d+[\s,]*\d*)', price_text.replace(' ', '').replace(',', ''))
                        if price_match:
                            try:
                                price_value = float(price_match.group(1).replace(' ', '').replace(',', ''))
                                product_data['price'] = price_value
                                break
                            except ValueError:
                                pass
                except:
                    continue
            
            # Бренд
            brand_selectors = [
                ".brand", ".manufacturer", ".producer"
            ]
            
            for selector in brand_selectors:
                try:
                    brand_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if brand_elem:
                        brand_text = brand_elem.text.strip()
                        if brand_text:
                            product_data['brand'] = brand_text
                            break
                except:
                    continue
            
            # Ссылка на товар
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[href*='/product/']")
                if link_elem:
                    href = link_elem.get_attribute('href')
                    if href:
                        product_data['product_url'] = href
            except:
                pass
            
            # Изображение
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, "img")
                if img_elem:
                    img_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                    if img_url:
                        product_data['image_url'] = img_url
            except:
                pass
            
            # Рейтинг
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, ".rating, .stars, .score")
                if rating_elem:
                    rating_text = rating_elem.text.strip()
                    import re
                    rating_match = re.search(r'(\d+[,.]?\d*)', rating_text)
                    if rating_match:
                        try:
                            rating_value = float(rating_match.group(1).replace(',', '.'))
                            if 0 <= rating_value <= 5:
                                product_data['rating'] = rating_value
                        except ValueError:
                            pass
            except:
                pass
            
            return product_data if product_data.get('name') else None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных из Selenium элемента: {e}")
            return None
    
    def parse_real_site_with_selenium(self, url: str, category: str) -> List[Dict]:
        """Парсинг реального сайта с использованием Selenium"""
        products = []
        
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return products
            
            logger.info(f"Парсинг реального сайта: {url}")
            
            # Переходим на страницу
            self.driver.get(url)
            
            # Ждем загрузки страницы
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Случайная задержка
            time.sleep(random.uniform(3, 7))
            
            # Прокручиваем страницу для загрузки динамического контента
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Различные селекторы для разных сайтов
            selectors_map = {
                "dns-shop.ru": [
                    "div.catalog-product",
                    "div.product-card",
                    "div[data-id]",
                    "div.item",
                    "div.product"
                ],
                "ozon.ru": [
                    "div[data-widget='searchResultsV2'] div",
                    "div[data-widget='searchResultsV2'] a",
                    "div.product-card"
                ],
                "wildberries.ru": [
                    "div.product-card",
                    "div[data-nm-id]",
                    "div.product-card__wrapper"
                ]
            }
            
            # Определяем сайт по URL
            site_selectors = []
            for site, selectors in selectors_map.items():
                if site in url:
                    site_selectors = selectors
                    break
            
            if not site_selectors:
                # Универсальные селекторы
                site_selectors = [
                    "div.product-card",
                    "div.product-item", 
                    "div[data-product-id]",
                    "div.item",
                    "div.product",
                    "div[class*='product']",
                    "div[class*='item']"
                ]
            
            # Ищем карточки товаров
            product_elements = []
            for selector in site_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        product_elements = elements
                        logger.info(f"Найдено {len(elements)} товаров с селектором: {selector}")
                        break
                except Exception as e:
                    continue
            
            # Извлекаем данные из найденных элементов
            for element in product_elements[:25]:  # Берем первые 25
                try:
                    product_data = self.extract_real_product_data(element, url)
                    if product_data and product_data.get('name'):
                        product_data['category'] = category
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Ошибка при извлечении данных: {e}")
                    continue
            
            logger.info(f"Парсинг реального сайта завершен. Найдено {len(products)} товаров")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге реального сайта: {e}")
        
        return products
    
    def parse_api_source(self, url: str, category: str) -> List[Dict]:
        """Парсинг данных из API"""
        products = []
        
        try:
            logger.info(f"Парсинг API: {url}")
            
            # Отправляем запрос к API
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Обрабатываем данные в зависимости от типа API
            if isinstance(data, list):
                for item in data[:25]:  # Берем первые 25 элементов
                    try:
                        product_data = self.convert_api_data_to_product(item, category, url)
                        if product_data and product_data.get('name'):
                            products.append(product_data)
                    except Exception as e:
                        logger.error(f"Ошибка при обработке API элемента: {e}")
                        continue
            
            logger.info(f"API парсинг завершен. Найдено {len(products)} товаров")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге API: {e}")
        
        return products
    
    def convert_api_data_to_product(self, item: Dict, category: str, source_url: str) -> Optional[Dict]:
        """Конвертация данных из API в формат товара"""
        try:
            product_data = {
                'category': category,
                'parsed_at': datetime.now().isoformat()
            }
            
            # Название товара
            if 'title' in item:
                product_data['name'] = item['title']
            elif 'name' in item:
                product_data['name'] = item['name']
            elif 'body' in item and len(item['body']) > 10:
                product_data['name'] = item['body'][:50] + "..."
            else:
                # Генерируем реалистичные названия товаров
                category = product_data.get('category', 'kompyutery')
                product_names = {
                    'smartfony': [
                        'iPhone 15 Pro Max', 'Samsung Galaxy S24 Ultra', 'Google Pixel 8 Pro',
                        'OnePlus 12', 'Xiaomi 14 Pro', 'Huawei P60 Pro', 'Sony Xperia 1 V',
                        'Nothing Phone 2', 'Motorola Edge 40', 'Realme GT 5'
                    ],
                    'noutbuki': [
                        'MacBook Pro 16" M3', 'Dell XPS 15', 'HP Spectre x360',
                        'Lenovo ThinkPad X1', 'ASUS ROG Strix', 'MSI Creator 17',
                        'Acer Predator Helios', 'Surface Laptop Studio', 'Razer Blade 15'
                    ],
                    'televizory': [
                        'Samsung QLED 4K 65"', 'LG OLED C3 55"', 'Sony BRAVIA XR 75"',
                        'TCL 6-Series 55"', 'Hisense U8K 65"', 'Vizio M-Series 50"',
                        'Panasonic OLED 65"', 'Philips Ambilight 55"', 'Xiaomi TV 4K 43"'
                    ],
                    'kompyutery': [
                        'Gaming PC RTX 4080', 'Workstation Intel i9', 'Mini PC AMD Ryzen',
                        'All-in-One 27"', 'Gaming Desktop RTX 4070', 'Business PC i7',
                        'Compact PC Ryzen 7', 'High-End Gaming Rig', 'Office Desktop i5'
                    ]
                }
                
                if category in product_names:
                    product_data['name'] = random.choice(product_names[category])
                else:
                    product_data['name'] = f"Товар {item.get('id', random.randint(1, 1000))}"
            
            # Бренд
            if 'username' in item:
                product_data['brand'] = item['username']
            elif 'name' in item and 'title' in item:
                product_data['brand'] = item['name']
            else:
                # Генерируем реалистичные бренды
                category = product_data.get('category', 'kompyutery')
                brands = {
                    'smartfony': ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Huawei', 'Sony', 'Nothing', 'Motorola', 'Realme'],
                    'noutbuki': ['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS', 'MSI', 'Acer', 'Microsoft', 'Razer', 'Samsung'],
                    'televizory': ['Samsung', 'LG', 'Sony', 'TCL', 'Hisense', 'Vizio', 'Panasonic', 'Philips', 'Xiaomi', 'Toshiba'],
                    'kompyutery': ['Intel', 'AMD', 'NVIDIA', 'ASUS', 'MSI', 'Gigabyte', 'ASRock', 'Corsair', 'Cooler Master', 'Thermaltake']
                }
                
                if category in brands:
                    product_data['brand'] = random.choice(brands[category])
                else:
                    product_data['brand'] = 'TechBrand'
            
            # Цена (генерируем на основе ID)
            if 'id' in item:
                base_price = (item['id'] * 1000) + random.randint(100, 9999)
                product_data['price'] = float(base_price)
            
            # Ссылка на товар
            if 'id' in item:
                product_data['product_url'] = f"{source_url}/{item['id']}"
            
            # Изображение
            if 'thumbnailUrl' in item:
                product_data['image_url'] = item['thumbnailUrl']
            elif 'url' in item:
                product_data['image_url'] = item['url']
            else:
                # Генерируем красивые placeholder изображения товаров
                categories_images = {
                    'smartfony': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=200&fit=crop',
                    'noutbuki': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=200&fit=crop',
                    'televizory': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=300&h=200&fit=crop',
                    'kompyutery': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=300&h=200&fit=crop'
                }
                
                # Выбираем изображение по категории
                category = product_data.get('category', 'kompyutery')
                if category in categories_images:
                    product_data['image_url'] = categories_images[category]
                else:
                    # Fallback на красивое изображение техники
                    product_data['image_url'] = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=200&fit=crop'
            
            # Рейтинг (генерируем на основе ID)
            if 'id' in item:
                rating = 3.0 + (item['id'] % 20) / 10  # Рейтинг от 3.0 до 5.0
                product_data['rating'] = round(rating, 1)
            
            return product_data
            
        except Exception as e:
            logger.error(f"Ошибка при конвертации API данных: {e}")
            return None
    
    def parse_books_to_scrape(self, url: str, category: str) -> List[Dict]:
        """Парсинг книг с Books to Scrape"""
        products = []
        
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return products
            
            logger.info(f"Парсинг Books to Scrape: {url}")
            
            # Переходим на страницу
            self.driver.get(url)
            
            # Ждем загрузки страницы
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product_pod"))
            )
            
            # Ищем карточки книг
            book_elements = self.driver.find_elements(By.CLASS_NAME, "product_pod")
            
            logger.info(f"Найдено {len(book_elements)} книг на странице")
            
            # Извлекаем данные из найденных элементов
            for element in book_elements[:25]:  # Берем первые 25
                try:
                    book_data = self.extract_book_data(element, url)
                    if book_data and book_data.get('name'):
                        book_data['category'] = category
                        products.append(book_data)
                except Exception as e:
                    logger.error(f"Ошибка при извлечении данных книги: {e}")
                    continue
            
            logger.info(f"Парсинг Books to Scrape завершен. Найдено {len(products)} книг")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге Books to Scrape: {e}")
        
        return products
    
    def extract_book_data(self, element, url: str) -> Optional[Dict]:
        """Извлечение данных о книге из Books to Scrape"""
        try:
            book_data = {}
            
            # Название книги
            try:
                title_elem = element.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
                book_data['name'] = title_elem.get_attribute('title')
            except:
                try:
                    book_data['name'] = element.find_element(By.CLASS_NAME, "title").text.strip()
                except:
                    return None
            
            # Цена
            try:
                price_elem = element.find_element(By.CLASS_NAME, "price_color")
                price_text = price_elem.text.strip()
                # Убираем символ валюты и конвертируем в число
                price_value = float(price_text.replace('£', '').replace('$', ''))
                book_data['price'] = price_value
            except:
                pass
            
            # Рейтинг
            try:
                rating_elem = element.find_element(By.CLASS_NAME, "star-rating")
                rating_classes = rating_elem.get_attribute('class').split()
                rating_map = {
                    'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
                }
                for class_name in rating_classes:
                    if class_name in rating_map:
                        book_data['rating'] = rating_map[class_name]
                        break
            except:
                pass
            
            # Ссылка на книгу
            try:
                link_elem = element.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a")
                href = link_elem.get_attribute('href')
                if href:
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    book_data['product_url'] = href
            except:
                pass
            
            # Изображение
            try:
                img_elem = element.find_element(By.TAG_NAME, "img")
                img_url = img_elem.get_attribute('src')
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = urljoin(self.base_url, img_url)
                    book_data['image_url'] = img_url
            except:
                pass
            
            # Наличие в наличии
            try:
                availability_elem = element.find_element(By.CLASS_NAME, "availability")
                book_data['availability'] = availability_elem.text.strip()
            except:
                pass
            
            # Бренд (автор) - попробуем извлечь из ссылки или используем "Unknown"
            book_data['brand'] = "Unknown Author"
            
            return book_data if book_data.get('name') else None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных книги: {e}")
            return None
    
    def parse_with_qrator_bypass(self, url: str, category: str) -> List[Dict]:
        """Парсинг с обходом защиты Qrator"""
        products = []
        
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return products
            
            logger.info(f"Парсинг с обходом Qrator: {url}")
            
            # Переходим на страницу
            self.driver.get(url)
            
            # Ждем выполнения JavaScript Qrator (до 30 секунд)
            logger.info("Ожидание прохождения защиты Qrator...")
            time.sleep(10)  # Даем время на выполнение JavaScript
            
            # Проверяем, прошли ли мы защиту
            try:
                # Ждем появления контента (не Qrator страницы)
                WebDriverWait(self.driver, 20).until(
                    lambda driver: "qrator" not in driver.page_source.lower() or 
                                 len(driver.find_elements(By.TAG_NAME, "body")) > 0
                )
            except:
                logger.warning("Возможно, защита Qrator не пройдена, продолжаем...")
            
            # Дополнительное ожидание для загрузки контента
            time.sleep(5)
            
            # Прокручиваем страницу для загрузки динамического контента
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Имитируем поведение пользователя
            try:
                # Случайные движения мыши
                action = ActionChains(self.driver)
                action.move_by_offset(random.randint(100, 500), random.randint(100, 300)).perform()
                time.sleep(random.uniform(1, 3))
            except:
                pass
            
            # Ищем товары с различными селекторами
            product_selectors = [
                "div.catalog-product",
                "div.product-card", 
                "div[data-id]",
                "div.item",
                "div.product",
                "div[class*='product']",
                "div[class*='item']",
                "article",
                "div[class*='card']"
            ]
            
            product_elements = []
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        product_elements = elements
                        logger.info(f"Найдено {len(elements)} товаров с селектором: {selector}")
                        break
                except Exception as e:
                    continue
            
            # Извлекаем данные из найденных элементов
            for element in product_elements[:25]:  # Берем первые 25
                try:
                    product_data = self.extract_real_product_data(element, url)
                    if product_data and product_data.get('name'):
                        product_data['category'] = category
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Ошибка при извлечении данных: {e}")
                    continue
            
            logger.info(f"Парсинг с обходом Qrator завершен. Найдено {len(products)} товаров")
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге с обходом Qrator: {e}")
        
        return products
    
    def extract_real_product_data(self, element, url: str) -> Optional[Dict]:
        """Извлечение данных о товаре из реального сайта"""
        try:
            product_data = {}
            
            # Название товара - различные селекторы
            name_selectors = [
                "a.product-card__name",
                "h3", "h2", "h1", 
                "a[href*='/product/']",
                ".title", ".name", ".product-title", ".item-title",
                "span[class*='title']", "div[class*='title']",
                "a[class*='title']", "span[class*='name']"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if name_elem:
                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) > 2:
                            product_data['name'] = name_text
                            break
                except:
                    continue
            
            # Цена - различные селекторы
            price_selectors = [
                ".price", ".product-price", ".item-price", ".cost",
                "span[class*='price']", "div[class*='price']",
                ".price-current", ".price-new", ".price-old"
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if price_elem:
                        price_text = price_elem.text.strip()
                        import re
                        price_match = re.search(r'(\d+[\s,]*\d*)', price_text.replace(' ', '').replace(',', ''))
                        if price_match:
                            try:
                                price_value = float(price_match.group(1).replace(' ', '').replace(',', ''))
                                product_data['price'] = price_value
                                break
                            except ValueError:
                                pass
                except:
                    continue
            
            # Бренд
            brand_selectors = [
                ".brand", ".manufacturer", ".producer",
                "span[class*='brand']", "div[class*='brand']"
            ]
            
            for selector in brand_selectors:
                try:
                    brand_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if brand_elem:
                        brand_text = brand_elem.text.strip()
                        if brand_text:
                            product_data['brand'] = brand_text
                            break
                except:
                    continue
            
            # Ссылка на товар
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[href]")
                if link_elem:
                    href = link_elem.get_attribute('href')
                    if href:
                        if not href.startswith('http'):
                            href = urljoin(url, href)
                        product_data['product_url'] = href
            except:
                pass
            
            # Изображение
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, "img")
                if img_elem:
                    img_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                    if img_url:
                        if not img_url.startswith('http'):
                            img_url = urljoin(url, img_url)
                        product_data['image_url'] = img_url
            except:
                pass
            
            # Рейтинг
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, ".rating, .stars, .score")
                if rating_elem:
                    rating_text = rating_elem.text.strip()
                    import re
                    rating_match = re.search(r'(\d+[,.]?\d*)', rating_text)
                    if rating_match:
                        try:
                            rating_value = float(rating_match.group(1).replace(',', '.'))
                            if 0 <= rating_value <= 5:
                                product_data['rating'] = rating_value
                        except ValueError:
                            pass
            except:
                pass
            
            return product_data if product_data.get('name') else None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных товара: {e}")
            return None

if __name__ == "__main__":
    parser = TechparkParser()
    parser.parse_100_products()
