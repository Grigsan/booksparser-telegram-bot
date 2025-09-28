"""
Главный файл для запуска Telegram-бота "Господин Алладин"
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent / "src"))

from src.bot import ModeratorBot
from src.config import Config

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotRunner:
    """Класс для управления ботом"""
    
    def __init__(self):
        self.bot = None
        self.running = False
    
    async def start(self):
        """Запуск бота"""
        try:
            logger.info("🎭 Инициализация Господина Алладина...")
            self.bot = ModeratorBot()
            self.running = True
            
            # Настройка обработчиков сигналов
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            logger.info("✅ Господин Алладин готов к работе!")
            await self.bot.start()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
            sys.exit(1)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        logger.info(f"🛑 Получен сигнал {signum}, завершение работы...")
        self.running = False
        if self.bot:
            asyncio.create_task(self.bot.stop())
        sys.exit(0)
    
    async def stop(self):
        """Остановка бота"""
        if self.bot:
            await self.bot.stop()
        self.running = False

async def main():
    """Главная функция"""
    runner = BotRunner()
    
    try:
        await runner.start()
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await runner.stop()
        logger.info("👋 Господин Алладин завершил работу")

if __name__ == "__main__":
    # Создаем директорию для логов
    Path("logs").mkdir(exist_ok=True)
    
    # Запускаем бота
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Принудительное завершение")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")
        sys.exit(1)
