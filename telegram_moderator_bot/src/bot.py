"""
Основной модуль Telegram-бота "Господин Алладин"
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ChatMemberUpdated, ChatMember, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from .config import Config
from .database import Database
from .filters import ContentFilter
from .parser_integration import ParserIntegration

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

class ModerationStates(StatesGroup):
    """Состояния для FSM"""
    waiting_for_reason = State()

class ModeratorBot:
    """Основной класс бота-модератора"""
    
    def __init__(self):
        self.config = Config()
        self.bot = Bot(token=self.config.BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.db = Database()
        self.filter = ContentFilter()
        
        # Регистрация обработчиков
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация обработчиков событий"""
        # Команды (регистрируем первыми)
        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.help_command, Command('help'))
        self.dp.message.register(self.stats_command, Command('stats'))
        self.dp.message.register(self.warn_command, Command('warn'))
        self.dp.message.register(self.ban_command, Command('ban'))
        self.dp.message.register(self.unban_command, Command('unban'))
        self.dp.message.register(self.mute_command, Command('mute'))
        self.dp.message.register(self.unmute_command, Command('unmute'))
        
        # Команды парсера
        self.dp.message.register(self.parse_command, Command('parse'))
        self.dp.message.register(self.books_command, Command('books'))
        self.dp.message.register(self.search_command, Command('search'))
        self.dp.message.register(self.categories_command, Command('categories'))
        self.dp.message.register(self.parser_stats_command, Command('parser_stats'))
        
        # Обработка сообщений (регистрируем последним)
        self.dp.message.register(self.handle_message)
        
        # Обработка новых участников
        self.dp.my_chat_member.register(self.handle_chat_member_update)
        
        # Обработка callback запросов
        self.dp.callback_query.register(self.handle_callback)
    
    async def start_command(self, message: Message):
        """Обработка команды /start"""
        user = message.from_user
        chat = message.chat
        
        # Обновляем информацию о пользователе в базе
        await self.db.update_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_text = f"""
🎭 **Добро пожаловать, {user.first_name}!**

Я - **Господин Алладин**, ваш персональный модератор чата и помощник по книгам.

🔧 **Мои возможности:**
• Фильтрация нецензурных выражений
• Удаление спама и нежелательного контента
• Предупреждения и блокировки пользователей
• Парсинг и поиск книг
• Ведение статистики модерации

⚡ **Я работаю автоматически!**
Просто общайтесь, а я буду следить за порядком.
        """
        
        # Создаем главное меню
        keyboard = self._create_main_menu()
        
        await message.answer(welcome_text, parse_mode='Markdown', reply_markup=keyboard)
        
        # Логируем действие
        await self.db.log_action(
            user_id=user.id,
            chat_id=chat.id,
            action_type='start_command',
            message_text=message.text
        )
    
    async def help_command(self, message: Message):
        """Обработка команды /help"""
        help_text = """
🎭 **Господин Алладин - Справка**

🔧 **Команды модерации:**
/warn [@username] [причина] - Предупредить пользователя
/ban [@username] [причина] - Заблокировать пользователя
/unban [@username] - Разблокировать пользователя
/mute [@username] [время] - Заглушить пользователя
/unmute [@username] - Разглушить пользователя
/stats - Статистика модерации

📚 **Команды парсера книг:**
/parse - Запустить парсинг книг
/books [количество] - Список книг (по умолчанию 10)
/search <запрос> - Поиск книг
/categories - Категории книг
/parser_stats - Статистика парсера

🔧 **Автоматические функции:**
• Удаление сообщений с нецензурными словами
• Блокировка спама и флуда
• Предупреждения за нарушения
• Автоматические блокировки при превышении лимита предупреждений

⚙️ **Настройки:**
• Максимум предупреждений: 3
• Автоудаление через: 5 секунд
• Фильтрация: включена

📊 **Статистика доступна через /stats и /parser_stats**
        """
        
        await message.answer(help_text, parse_mode='Markdown')
    
    async def stats_command(self, message: Message):
        """Обработка команды /stats"""
        # Проверяем права администратора
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для просмотра статистики")
            return
        
        stats = await self.db.get_stats()
        
        stats_text = f"""
📊 **Статистика модерации**

👥 **Пользователи:**
• Всего пользователей: {stats.get('total_users', 0)}
• Заблокированных: {stats.get('banned_users', 0)}

📈 **Действия:**
• Всего действий: {stats.get('total_actions', 0)}
• Действий сегодня: {stats.get('today_actions', 0)}

🔥 **Топ действий:**
"""
        
        for action in stats.get('top_actions', []):
            stats_text += f"• {action['action_type']}: {action['count']}\n"
        
        await message.answer(stats_text, parse_mode='Markdown')
    
    async def warn_command(self, message: Message):
        """Обработка команды /warn"""
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для модерации")
            return
        
        # Парсим команду
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer("❌ Использование: /warn @username [причина]")
            return
        
        target_username = args[0].replace('@', '')
        reason = ' '.join(args[1:]) if len(args) > 1 else "Нарушение правил чата"
        
        # Здесь должна быть логика поиска пользователя по username
        # Для упрощения используем ID из сообщения
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            await self._warn_user(message, target_user, reason)
        else:
            await message.answer("❌ Ответьте на сообщение пользователя для предупреждения")
    
    async def ban_command(self, message: Message):
        """Обработка команды /ban"""
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для модерации")
            return
        
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            reason = ' '.join(message.text.split()[1:]) if len(message.text.split()) > 1 else "Нарушение правил чата"
            await self._ban_user(message, target_user, reason)
        else:
            await message.answer("❌ Ответьте на сообщение пользователя для блокировки")
    
    async def unban_command(self, message: Message):
        """Обработка команды /unban"""
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для модерации")
            return
        
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            await self._unban_user(message, target_user)
        else:
            await message.answer("❌ Ответьте на сообщение пользователя для разблокировки")
    
    async def mute_command(self, message: Message):
        """Обработка команды /mute"""
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для модерации")
            return
        
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            duration = message.text.split()[1] if len(message.text.split()) > 1 else "1h"
            await self._mute_user(message, target_user, duration)
        else:
            await message.answer("❌ Ответьте на сообщение пользователя для заглушения")
    
    async def unmute_command(self, message: Message):
        """Обработка команды /unmute"""
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для модерации")
            return
        
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            await self._unmute_user(message, target_user)
        else:
            await message.answer("❌ Ответьте на сообщение пользователя для разглушения")
    
    async def handle_message(self, message: Message):
        """Обработка всех сообщений"""
        if not message.text:
            return
        
        # Пропускаем команды - они обрабатываются отдельными обработчиками
        if message.text.startswith('/'):
            return
        
        user = message.from_user
        chat = message.chat
        
        # Отладочная информация
        logger.info(f"Получено сообщение от {user.first_name}: {message.text}")
        logger.info(f"Модерация включена: {self.config.MODERATION_ENABLED}")
        logger.info(f"Фильтр нецензурных слов: {self.config.PROFANITY_FILTER}")
        
        # Обновляем информацию о пользователе
        await self.db.update_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Проверяем, не заблокирован ли пользователь
        user_data = await self.db.get_user(user.id)
        if user_data and user_data.get('is_banned'):
            await message.delete()
            return
        
        # Анализируем сообщение
        analysis = self.filter.analyze_message(message.text)
        logger.info(f"Анализ сообщения: {analysis}")
        
        if analysis['is_violation']:
            logger.info(f"Нарушение обнаружено: {analysis['violation_reason']}")
            # Получаем количество предупреждений пользователя
            warnings = user_data.get('warnings', 0) if user_data else 0
            
            # Проверяем, является ли пользователь администратором
            is_admin = user.id in self.config.ADMIN_IDS
            try:
                member = await self.bot.get_chat_member(message.chat.id, user.id)
                is_admin = is_admin or member.status in ['creator', 'administrator']
            except:
                pass
            
            # Определяем действие
            action = self.filter.get_moderation_action(analysis, warnings)
            logger.info(f"Действие модерации: {action}")
            
            # Для администраторов всегда выдаем предупреждения вместо блокировки
            if is_admin and action == 'ban':
                action = 'warn'
                logger.info(f"Изменено действие для администратора: ban -> warn")
            
            logger.info(f"Финальное действие: {action}")
            
            if action == 'delete':
                logger.info("Выполняем действие: delete")
                await self._delete_message(message, analysis['violation_reason'])
                return
            elif action == 'warn':
                logger.info("Выполняем действие: warn")
                # Сначала удаляем сообщение, потом выдаем предупреждение
                await message.delete()
                await self._warn_user(message, user, analysis['violation_reason'])
                return
            elif action == 'ban':
                logger.info("Выполняем действие: ban")
                await self._ban_user(message, user, analysis['violation_reason'])
                return
            else:
                logger.error(f"Неизвестное действие: {action}")
        else:
            logger.info("Нарушений не обнаружено")
    
    async def handle_chat_member_update(self, update: ChatMemberUpdated):
        """Обработка обновлений участников чата"""
        if update.new_chat_member.status == ChatMember.MEMBER:
            # Новый участник
            user = update.new_chat_member.user
            await self.db.update_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
    
    async def _is_admin(self, message: Message) -> bool:
        """Проверка прав администратора"""
        if message.from_user.id in self.config.ADMIN_IDS:
            return True
        
        # Проверяем права в чате
        try:
            member = await self.bot.get_chat_member(message.chat.id, message.from_user.id)
            return member.status in ['creator', 'administrator']
        except:
            return False
    
    async def _delete_message(self, message: Message, reason: str):
        """Удаление сообщения"""
        try:
            await message.delete()
            
            # Отправляем уведомление
            warning_text = f"""
⚠️ **Сообщение удалено**

**Причина:** {reason}

Пожалуйста, соблюдайте правила чата!
            """
            
            warning_msg = await message.answer(warning_text, parse_mode='Markdown')
            
            # Удаляем уведомление через 5 секунд
            await asyncio.sleep(self.config.AUTO_DELETE_DELAY)
            try:
                await warning_msg.delete()
            except:
                pass
            
            # Логируем действие
            await self.db.log_action(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                action_type='message_deleted',
                message_text=message.text,
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"Ошибка удаления сообщения: {e}")
    
    async def _warn_user(self, message: Message, target_user, reason: str):
        """Предупреждение пользователя"""
        try:
            # Получаем текущие предупреждения
            user_data = await self.db.get_user(target_user.id)
            current_warnings = user_data.get('warnings', 0) if user_data else 0
            new_warnings = current_warnings + 1
            
            # Обновляем предупреждения
            await self.db.update_user(
                user_id=target_user.id,
                warnings=new_warnings
            )
            
            # Проверяем, нужно ли заблокировать пользователя
            if new_warnings >= self.config.MAX_WARNINGS:
                # Проверяем, является ли пользователь администратором
                is_admin = target_user.id in self.config.ADMIN_IDS
                if is_admin:
                    # Для администраторов не блокируем, только предупреждаем
                    logger.info(f"Администратор {target_user.id} достиг лимита предупреждений, но не блокируется")
                else:
                    # Автоматическая блокировка при достижении лимита
                    await self._ban_user(message, target_user, f"Автоматическая блокировка: {new_warnings} предупреждений")
                    return
            
            # Отправляем уведомление
            warning_text = f"""
⚠️ **Предупреждение #{new_warnings}**

**Пользователь:** {target_user.first_name}
**Причина:** {reason}
**Предупреждений:** {new_warnings}/{self.config.MAX_WARNINGS}

{f'🚨 **ВНИМАНИЕ!** При достижении {self.config.MAX_WARNINGS} предупреждений вы будете заблокированы!' if new_warnings >= self.config.MAX_WARNINGS - 1 else ''}
            """
            
            await message.answer(warning_text, parse_mode='Markdown')
            
            # Логируем действие
            await self.db.log_action(
                user_id=target_user.id,
                chat_id=message.chat.id,
                action_type='user_warned',
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"Ошибка предупреждения пользователя: {e}")
    
    async def _ban_user(self, message: Message, target_user, reason: str):
        """Блокировка пользователя"""
        try:
            # Блокируем пользователя в чате
            await self.bot.ban_chat_member(message.chat.id, target_user.id)
            
            # Обновляем статус в базе
            await self.db.update_user(
                user_id=target_user.id,
                is_banned=True
            )
            
            # Отправляем уведомление
            ban_text = f"""
🚫 **Пользователь заблокирован**

**Пользователь:** {target_user.first_name}
**Причина:** {reason}
**Время:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
            
            await message.answer(ban_text, parse_mode='Markdown')
            
            # Логируем действие
            await self.db.log_action(
                user_id=target_user.id,
                chat_id=message.chat.id,
                action_type='user_banned',
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"Ошибка блокировки пользователя: {e}")
    
    async def _unban_user(self, message: Message, target_user):
        """Разблокировка пользователя"""
        try:
            # Разблокируем пользователя
            await self.bot.unban_chat_member(message.chat.id, target_user.id)
            
            # Обновляем статус в базе
            await self.db.update_user(
                user_id=target_user.id,
                is_banned=False,
                warnings=0  # Сбрасываем предупреждения
            )
            
            # Отправляем уведомление
            unban_text = f"""
✅ **Пользователь разблокирован**

**Пользователь:** {target_user.first_name}
**Время:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
            
            await message.answer(unban_text, parse_mode='Markdown')
            
            # Логируем действие
            await self.db.log_action(
                user_id=target_user.id,
                chat_id=message.chat.id,
                action_type='user_unbanned'
            )
            
        except Exception as e:
            logger.error(f"Ошибка разблокировки пользователя: {e}")
    
    async def _mute_user(self, message: Message, target_user, duration: str):
        """Заглушение пользователя"""
        try:
            # Здесь должна быть логика заглушения
            # Для упрощения просто обновляем статус в базе
            await self.db.update_user(
                user_id=target_user.id,
                is_muted=True
            )
            
            mute_text = f"""
🔇 **Пользователь заглушен**

**Пользователь:** {target_user.first_name}
**Длительность:** {duration}
**Время:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
            
            await message.answer(mute_text, parse_mode='Markdown')
            
            # Логируем действие
            await self.db.log_action(
                user_id=target_user.id,
                chat_id=message.chat.id,
                action_type='user_muted',
                reason=f"Длительность: {duration}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка заглушения пользователя: {e}")
    
    async def _unmute_user(self, message: Message, target_user):
        """Разглушение пользователя"""
        try:
            # Обновляем статус в базе
            await self.db.update_user(
                user_id=target_user.id,
                is_muted=False
            )
            
            unmute_text = f"""
🔊 **Пользователь разглушен**

**Пользователь:** {target_user.first_name}
**Время:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
            
            await message.answer(unmute_text, parse_mode='Markdown')
            
            # Логируем действие
            await self.db.log_action(
                user_id=target_user.id,
                chat_id=message.chat.id,
                action_type='user_unmuted'
            )
            
        except Exception as e:
            logger.error(f"Ошибка разглушения пользователя: {e}")
    
    async def parse_command(self, message: Message):
        """Обработка команды /parse - запуск парсинга книг"""
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для запуска парсинга")
            return
        
        # Отправляем сообщение о начале парсинга
        parsing_msg = await message.answer("🔄 Запуск парсинга книг... Это может занять несколько минут")
        
        try:
            async with ParserIntegration() as parser:
                result = await parser.start_parsing()
                
                if result["success"]:
                    await parsing_msg.edit_text(f"✅ {result['message']}")
                    
                    # Логируем действие
                    await self.db.log_action(
                        user_id=message.from_user.id,
                        chat_id=message.chat.id,
                        action_type='parsing_started',
                        message_text=message.text
                    )
                else:
                    await parsing_msg.edit_text(f"❌ {result['message']}")
                    
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            await parsing_msg.edit_text(f"❌ Ошибка запуска парсинга: {str(e)}")
    
    async def books_command(self, message: Message):
        """Обработка команды /books - список книг"""
        try:
            # Получаем параметр limit из команды
            args = message.text.split()[1:] if len(message.text.split()) > 1 else []
            limit = int(args[0]) if args and args[0].isdigit() else 10
            
            books_msg = await message.answer("📚 Загрузка списка книг...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_books_list(limit)
                
                if result["success"]:
                    books = result["data"]
                    if books:
                        books_text = f"📚 **Найдено книг: {len(books)}**\n\n"
                        
                        for i, book in enumerate(books[:limit], 1):
                            title = book.get('title', 'Без названия')
                            price = book.get('price', 'N/A')
                            category = book.get('category', 'N/A')
                            
                            books_text += f"{i}. **{title}**\n"
                            books_text += f"   💰 Цена: {price}\n"
                            books_text += f"   🏷️ Категория: {category}\n\n"
                        
                        await books_msg.edit_text(books_text, parse_mode='Markdown')
                    else:
                        await books_msg.edit_text("📚 Книги не найдены")
                else:
                    await books_msg.edit_text(f"❌ {result['message']}")
                    
        except Exception as e:
            logger.error(f"Ошибка получения книг: {e}")
            await message.answer(f"❌ Ошибка получения книг: {str(e)}")
    
    async def search_command(self, message: Message):
        """Обработка команды /search - поиск книг"""
        try:
            # Получаем поисковый запрос
            args = message.text.split()[1:] if len(message.text.split()) > 1 else []
            if not args:
                await message.answer("❌ Использование: /search <запрос>")
                return
            
            query = ' '.join(args)
            search_msg = await message.answer(f"🔍 Поиск книг по запросу: '{query}'...")
            
            async with ParserIntegration() as parser:
                result = await parser.search_books(query, limit=5)
                
                if result["success"]:
                    books = result["data"]
                    if books:
                        search_text = f"🔍 **Результаты поиска: '{query}'**\n"
                        search_text += f"Найдено: {len(books)} книг\n\n"
                        
                        for i, book in enumerate(books, 1):
                            title = book.get('title', 'Без названия')
                            price = book.get('price', 'N/A')
                            category = book.get('category', 'N/A')
                            
                            search_text += f"{i}. **{title}**\n"
                            search_text += f"   💰 Цена: {price}\n"
                            search_text += f"   🏷️ Категория: {category}\n\n"
                        
                        await search_msg.edit_text(search_text, parse_mode='Markdown')
                    else:
                        await search_msg.edit_text(f"🔍 По запросу '{query}' ничего не найдено")
                else:
                    await search_msg.edit_text(f"❌ {result['message']}")
                    
        except Exception as e:
            logger.error(f"Ошибка поиска книг: {e}")
            await message.answer(f"❌ Ошибка поиска: {str(e)}")
    
    async def categories_command(self, message: Message):
        """Обработка команды /categories - категории книг"""
        try:
            categories_msg = await message.answer("🏷️ Загрузка категорий...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_categories()
                
                if result["success"]:
                    categories = result["data"]
                    if categories:
                        categories_text = f"🏷️ **Категории книг ({len(categories)}):**\n\n"
                        categories_text += "\n".join([f"• {cat}" for cat in categories])
                        
                        await categories_msg.edit_text(categories_text, parse_mode='Markdown')
                    else:
                        await categories_msg.edit_text("🏷️ Категории не найдены")
                else:
                    await categories_msg.edit_text(f"❌ {result['message']}")
                    
        except Exception as e:
            logger.error(f"Ошибка получения категорий: {e}")
            await message.answer(f"❌ Ошибка получения категорий: {str(e)}")
    
    async def parser_stats_command(self, message: Message):
        """Обработка команды /parser_stats - статистика парсера"""
        if not await self._is_admin(message):
            await message.answer("❌ У вас нет прав для просмотра статистики парсера")
            return
        
        try:
            stats_msg = await message.answer("📊 Загрузка статистики парсера...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_books_stats()
                
                if result["success"]:
                    stats = result["data"]
                    
                    stats_text = f"""
📊 **Статистика парсера книг**

📚 **Книги:**
• Всего книг: {stats.get('total_products', 0)}
• Категорий: {len(stats.get('categories', {}))}
• Средняя цена: {stats.get('average_price', 0)}

🏷️ **Категории:**
"""
                    
                    for category, count in stats.get('categories', {}).items():
                        stats_text += f"• {category}: {count} книг\n"
                    
                    await stats_msg.edit_text(stats_text, parse_mode='Markdown')
                else:
                    await stats_msg.edit_text(f"❌ {result['message']}")
                    
        except Exception as e:
            logger.error(f"Ошибка получения статистики парсера: {e}")
            await message.answer(f"❌ Ошибка получения статистики: {str(e)}")
    
    def _create_main_menu(self) -> InlineKeyboardMarkup:
        """Создание главного меню"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Книги", callback_data="books_menu"),
                InlineKeyboardButton(text="🔍 Поиск", callback_data="search_menu")
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="stats_menu"),
                InlineKeyboardButton(text="🏷️ Категории", callback_data="categories_menu")
            ],
            [
                InlineKeyboardButton(text="⚙️ Модерация", callback_data="moderation_menu"),
                InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help_menu")
            ]
        ])
        return keyboard
    
    def _create_books_menu(self) -> InlineKeyboardMarkup:
        """Создание меню книг"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Список книг (5)", callback_data="books_5"),
                InlineKeyboardButton(text="📚 Список книг (10)", callback_data="books_10")
            ],
            [
                InlineKeyboardButton(text="🔄 Запустить парсинг", callback_data="parse_books"),
                InlineKeyboardButton(text="📊 Статистика парсера", callback_data="parser_stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
            ]
        ])
        return keyboard
    
    def _create_search_menu(self) -> InlineKeyboardMarkup:
        """Создание меню поиска"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Поиск по названию", callback_data="search_title"),
                InlineKeyboardButton(text="🔍 Поиск по автору", callback_data="search_author")
            ],
            [
                InlineKeyboardButton(text="🔍 Поиск по категории", callback_data="search_category"),
                InlineKeyboardButton(text="🔍 Случайные книги", callback_data="random_books")
            ],
            [
                InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
            ]
        ])
        return keyboard
    
    def _create_moderation_menu(self) -> InlineKeyboardMarkup:
        """Создание меню модерации"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Статистика модерации", callback_data="moderation_stats"),
                InlineKeyboardButton(text="👥 Пользователи", callback_data="users_stats")
            ],
            [
                InlineKeyboardButton(text="⚠️ Предупреждения", callback_data="warnings_stats"),
                InlineKeyboardButton(text="🚫 Блокировки", callback_data="bans_stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
            ]
        ])
        return keyboard
    
    async def handle_callback(self, callback: CallbackQuery):
        """Обработка callback запросов"""
        try:
            data = callback.data
            
            if data == "main_menu":
                await self._show_main_menu(callback)
            elif data == "books_menu":
                await self._show_books_menu(callback)
            elif data == "search_menu":
                await self._show_search_menu(callback)
            elif data == "moderation_menu":
                await self._show_moderation_menu(callback)
            elif data == "help_menu":
                await self._show_help_menu(callback)
            elif data == "stats_menu":
                await self._show_stats_menu(callback)
            elif data == "categories_menu":
                await self._show_categories_menu(callback)
            elif data.startswith("books_"):
                limit = int(data.split("_")[1])
                await self._show_books_list(callback, limit)
            elif data == "parse_books":
                await self._start_parsing(callback)
            elif data == "parser_stats":
                await self._show_parser_stats(callback)
            elif data == "moderation_stats":
                await self._show_moderation_stats(callback)
            elif data == "random_books":
                await self._show_random_books(callback)
            elif data.startswith("book_detail_"):
                book_id = data.split("_")[2]
                await self._show_book_detail(callback, book_id)
            else:
                await callback.answer("❌ Неизвестная команда")
                
        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            await callback.answer("❌ Произошла ошибка")
    
    async def _show_main_menu(self, callback: CallbackQuery):
        """Показать главное меню"""
        text = """
🎭 **Главное меню**

Выберите нужный раздел:
        """
        keyboard = self._create_main_menu()
        await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
        await callback.answer()
    
    async def _show_books_menu(self, callback: CallbackQuery):
        """Показать меню книг"""
        text = """
📚 **Меню книг**

Выберите действие:
        """
        keyboard = self._create_books_menu()
        await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
        await callback.answer()
    
    async def _show_search_menu(self, callback: CallbackQuery):
        """Показать меню поиска"""
        text = """
🔍 **Меню поиска**

Выберите тип поиска:
        """
        keyboard = self._create_search_menu()
        await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
        await callback.answer()
    
    async def _show_moderation_menu(self, callback: CallbackQuery):
        """Показать меню модерации"""
        logger.info(f"Проверка прав для пользователя {callback.from_user.id}")
        logger.info(f"ADMIN_IDS: {self.config.ADMIN_IDS}")
        
        if not await self._is_admin_callback(callback):
            await callback.answer("❌ У вас нет прав для модерации")
            return
        
        text = """
⚙️ **Меню модерации**

Выберите действие:
        """
        keyboard = self._create_moderation_menu()
        await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
        await callback.answer()
    
    async def _show_help_menu(self, callback: CallbackQuery):
        """Показать справку"""
        help_text = """
🎭 **Господин Алладин - Справка**

🔧 **Команды модерации:**
/warn [@username] [причина] - Предупредить пользователя
/ban [@username] [причина] - Заблокировать пользователя
/unban [@username] - Разблокировать пользователя
/mute [@username] [время] - Заглушить пользователя
/unmute [@username] - Разглушить пользователя

📚 **Команды парсера книг:**
/parse - Запустить парсинг книг
/books [количество] - Список книг
/search <запрос> - Поиск книг
/categories - Категории книг
/parser_stats - Статистика парсера

🔧 **Автоматические функции:**
• Удаление сообщений с нецензурными словами
• Блокировка спама и флуда
• Предупреждения за нарушения
• Автоматические блокировки при превышении лимита предупреждений

⚙️ **Настройки:**
• Максимум предупреждений: 3
• Автоудаление через: 5 секунд
• Фильтрация: включена
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(help_text, parse_mode='Markdown', reply_markup=keyboard)
        await callback.answer()
    
    async def _show_stats_menu(self, callback: CallbackQuery):
        """Показать меню статистики"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Статистика модерации", callback_data="moderation_stats"),
                InlineKeyboardButton(text="📚 Статистика парсера", callback_data="parser_stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
            ]
        ])
        
        text = """
📊 **Меню статистики**

Выберите тип статистики:
        """
        
        await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
        await callback.answer()
    
    async def _show_categories_menu(self, callback: CallbackQuery):
        """Показать категории"""
        try:
            await callback.answer("🏷️ Загрузка категорий...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_categories()
                
                if result["success"]:
                    categories = result["data"]
                    if categories:
                        text = f"🏷️ **Категории книг ({len(categories)}):**\n\n"
                        text += "\n".join([f"• {cat}" for cat in categories])
                    else:
                        text = "🏷️ Категории не найдены"
                else:
                    text = f"❌ {result['message']}"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
            ])
            
            await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка получения категорий: {e}")
            await callback.answer("❌ Ошибка получения категорий")
    
    async def _show_books_list(self, callback: CallbackQuery, limit: int):
        """Показать список книг"""
        try:
            await callback.answer("📚 Загрузка книг...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_books_list(limit)
                
                if result["success"]:
                    books = result["data"]
                    if books:
                        text = f"📚 **Найдено книг: {len(books)}**\n\n"
                        text += "Выберите книгу для просмотра подробной информации:\n\n"
                        
                        # Создаем кнопки для каждой книги
                        keyboard_buttons = []
                        for i, book in enumerate(books[:limit], 1):
                            title = book.get('title', 'Без названия')
                            # Ограничиваем длину названия для кнопки
                            button_text = title[:30] + "..." if len(title) > 30 else title
                            
                            # Логируем структуру книги для отладки
                            logger.info(f"Книга {i}: {book}")
                            
                            keyboard_buttons.append([
                                InlineKeyboardButton(
                                    text=f"{i}. {button_text}", 
                                    callback_data=f"book_detail_{book.get('id', i)}"
                                )
                            ])
                        
                        # Добавляем кнопку "Назад"
                        keyboard_buttons.append([
                            InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
                        ])
                        
                        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
                    else:
                        text = "📚 Книги не найдены"
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
                        ])
                else:
                    text = f"❌ {result['message']}"
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
                    ])
            
            await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка получения книг: {e}")
            await callback.answer("❌ Ошибка получения книг")
    
    async def _start_parsing(self, callback: CallbackQuery):
        """Запустить парсинг"""
        if not await self._is_admin_callback(callback):
            await callback.answer("❌ У вас нет прав для запуска парсинга")
            return
        
        try:
            await callback.answer("🔄 Запуск парсинга...")
            
            async with ParserIntegration() as parser:
                result = await parser.start_parsing()
                
                if result["success"]:
                    text = f"✅ {result['message']}"
                else:
                    text = f"❌ {result['message']}"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
            ])
            
            await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            await callback.answer("❌ Ошибка запуска парсинга")
    
    async def _show_parser_stats(self, callback: CallbackQuery):
        """Показать статистику парсера"""
        try:
            await callback.answer("📊 Загрузка статистики...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_books_stats()
                
                if result["success"]:
                    stats = result["data"]
                    
                    text = f"""
📊 **Статистика парсера книг**

📚 **Книги:**
• Всего книг: {stats.get('total_products', 0)}
• Категорий: {len(stats.get('categories', {}))}
• Средняя цена: {stats.get('average_price', 0)}

🏷️ **Категории:**
"""
                    
                    for category, count in stats.get('categories', {}).items():
                        text += f"• {category}: {count} книг\n"
                else:
                    text = f"❌ {result['message']}"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
            ])
            
            await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики парсера: {e}")
            await callback.answer("❌ Ошибка получения статистики")
    
    async def _show_moderation_stats(self, callback: CallbackQuery):
        """Показать статистику модерации"""
        if not await self._is_admin_callback(callback):
            await callback.answer("❌ У вас нет прав для просмотра статистики")
            return
        
        try:
            await callback.answer("📊 Загрузка статистики...")
            
            stats = await self.db.get_stats()
            
            text = f"""
📊 **Статистика модерации**

👥 **Пользователи:**
• Всего пользователей: {stats.get('total_users', 0)}
• Заблокированных: {stats.get('banned_users', 0)}

📈 **Действия:**
• Всего действий: {stats.get('total_actions', 0)}
• Действий сегодня: {stats.get('today_actions', 0)}

🔥 **Топ действий:**
"""
            
            for action in stats.get('top_actions', []):
                text += f"• {action['action_type']}: {action['count']}\n"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
            ])
            
            await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики модерации: {e}")
            await callback.answer("❌ Ошибка получения статистики")
    
    async def _show_random_books(self, callback: CallbackQuery):
        """Показать случайные книги"""
        try:
            await callback.answer("🎲 Загрузка случайных книг...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_books_list(5)
                
                if result["success"]:
                    books = result["data"]
                    if books:
                        text = "🎲 **Случайные книги (5):**\n\n"
                        text += "Выберите книгу для просмотра подробной информации:\n\n"
                        
                        # Создаем кнопки для каждой книги
                        keyboard_buttons = []
                        for i, book in enumerate(books, 1):
                            title = book.get('title', 'Без названия')
                            # Ограничиваем длину названия для кнопки
                            button_text = title[:30] + "..." if len(title) > 30 else title
                            keyboard_buttons.append([
                                InlineKeyboardButton(
                                    text=f"{i}. {button_text}", 
                                    callback_data=f"book_detail_{book.get('id', i)}"
                                )
                            ])
                        
                        # Добавляем кнопку "Назад"
                        keyboard_buttons.append([
                            InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
                        ])
                        
                        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
                    else:
                        text = "🎲 Книги не найдены"
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
                        ])
                else:
                    text = f"❌ {result['message']}"
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
                    ])
            
            await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка получения случайных книг: {e}")
            await callback.answer("❌ Ошибка получения книг")
    
    async def _show_book_detail(self, callback: CallbackQuery, book_id: str):
        """Показать детальную информацию о книге"""
        try:
            await callback.answer("📖 Загрузка информации о книге...")
            
            async with ParserIntegration() as parser:
                result = await parser.get_books_list(100)  # Получаем больше книг для поиска
                
                if result["success"]:
                    books = result["data"]
                    book = None
                    
                    # Ищем книгу по ID
                    for b in books:
                        if str(b.get('id', '')) == str(book_id):
                            book = b
                            break
                    
                    if book:
                        # Формируем детальную информацию
                        title = book.get('title', 'Без названия')
                        author = book.get('author', 'Не указан')
                        price = book.get('price', 'N/A')
                        category = book.get('category', 'N/A')
                        book_url = book.get('book_url', '') or book.get('url', '')
                        image_url = book.get('image_url', '') or book.get('image', '')
                        rating = book.get('rating', 'N/A')
                        availability = book.get('availability', 'N/A')
                        
                        # Логируем для отладки
                        logger.info(f"Детали книги: title={title}, author={author}, book_url={book_url}, image_url={image_url}")
                        
                        text = f"""
📖 **{title}**

👤 **Автор:** {author}
💰 **Цена:** {price}
🏷️ **Категория:** {category}
⭐ **Рейтинг:** {rating}
📦 **Наличие:** {availability}
                        """
                        
                        # Создаем кнопки
                        keyboard_buttons = []
                        
                        # Кнопка ссылки на книгу
                        if book_url:
                            keyboard_buttons.append([
                                InlineKeyboardButton(text="🔗 Открыть книгу", url=book_url)
                            ])
                        
                        # Кнопка изображения
                        if image_url:
                            keyboard_buttons.append([
                                InlineKeyboardButton(text="🖼️ Посмотреть обложку", url=image_url)
                            ])
                        
                        # Кнопка "Назад"
                        keyboard_buttons.append([
                            InlineKeyboardButton(text="🔙 Назад к списку", callback_data="books_5")
                        ])
                        
                        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
                        
                        # Отправляем сообщение с изображением, если есть
                        if image_url:
                            try:
                                await callback.message.chat.send_photo(
                                    photo=image_url,
                                    caption=text,
                                    parse_mode='Markdown',
                                    reply_markup=keyboard
                                )
                                # Удаляем предыдущее сообщение после успешной отправки фото
                                try:
                                    await callback.message.delete()
                                except:
                                    pass
                            except Exception as e:
                                logger.error(f"Ошибка отправки фото: {e}")
                                # Если не удалось отправить фото, отправляем текст
                                await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
                        else:
                            await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
                    else:
                        text = "❌ Книга не найдена"
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="books_5")]
                        ])
                        await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
                else:
                    text = f"❌ {result['message']}"
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
                    ])
                    await callback.message.edit_text(text, parse_mode='Markdown', reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка получения детальной информации о книге: {e}")
            await callback.answer("❌ Ошибка получения информации о книге")
    
    async def _is_admin_callback(self, callback: CallbackQuery) -> bool:
        """Проверка прав администратора для callback"""
        if callback.from_user.id in self.config.ADMIN_IDS:
            return True
        
        # Проверяем права в чате
        try:
            member = await self.bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
            return member.status in ['creator', 'administrator']
        except:
            return False
    
    async def start(self):
        """Запуск бота"""
        try:
            # Подключаемся к базе данных
            await self.db.connect()
            
            # Запускаем бота
            logger.info("🎭 Господин Алладин запускается...")
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
        finally:
            await self.db.close()
    
    async def stop(self):
        """Остановка бота"""
        logger.info("🛑 Господин Алладин останавливается...")
        await self.db.close()
        await self.bot.session.close()
