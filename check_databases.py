#!/usr/bin/env python3
"""
Проверка доступных баз данных PostgreSQL
"""

import psycopg2

def check_available_databases():
    """Проверяем доступные базы данных"""
    
    # Подключаемся к основной базе postgres для получения списка баз
    try:
        conn = psycopg2.connect(
            host='postgresql-grigson69.alwaysdata.net',
            port=5432,
            database='postgres',  # Подключаемся к системной базе
            user='grigson69',
            password='grigson96911'
        )
        cursor = conn.cursor()
        
        # Получаем список баз данных
        cursor.execute("""
            SELECT datname 
            FROM pg_database 
            WHERE datistemplate = false 
            AND datname NOT IN ('postgres', 'template0', 'template1')
            ORDER BY datname
        """)
        
        databases = cursor.fetchall()
        
        print("📋 Доступные базы данных:")
        for db in databases:
            print(f"   - {db[0]}")
        
        conn.close()
        return [db[0] for db in databases]
        
    except Exception as e:
        print(f"❌ Ошибка при проверке баз данных: {e}")
        return []

def test_connection_to_database(db_name):
    """Тестируем подключение к конкретной базе"""
    
    try:
        conn = psycopg2.connect(
            host='postgresql-grigson69.alwaysdata.net',
            port=5432,
            database=db_name,
            user='grigson69',
            password='grigson96911'
        )
        cursor = conn.cursor()
        
        # Получаем информацию о базе
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Получаем список таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print(f"✅ Подключение к базе '{db_name}' успешно!")
        print(f"📊 Версия: {version}")
        print(f"📋 Таблицы: {[table[0] for table in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе '{db_name}': {e}")
        return False

if __name__ == "__main__":
    print("🔍 Проверяем доступные базы данных...")
    
    # Проверяем доступные базы
    databases = check_available_databases()
    
    if databases:
        print(f"\n📊 Найдено {len(databases)} баз данных")
        
        # Тестируем подключение к каждой базе
        for db in databases:
            print(f"\n🔗 Тестируем подключение к '{db}':")
            test_connection_to_database(db)
    else:
        print("❌ Не удалось получить список баз данных")
