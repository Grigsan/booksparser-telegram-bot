"""
Модуль фильтрации контента для модерации
"""

import re
import logging
from typing import List, Tuple, Optional
from .config import Config

logger = logging.getLogger(__name__)

class ContentFilter:
    """Класс для фильтрации контента"""
    
    def __init__(self):
        self.config = Config()
        self.profanity_words = self.config.PROFANITY_WORDS
        self.spam_patterns = [
            r'(.)\1{4,}',  # Повторяющиеся символы (aaaaa)
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # Ссылки
            r'@\w+',  # Упоминания
            r'#\w+',  # Хештеги
        ]
        
    def check_profanity(self, text: str) -> Tuple[bool, List[str]]:
        """Проверка на нецензурные слова"""
        if not self.config.PROFANITY_FILTER:
            return False, []
        
        found_words = []
        text_lower = text.lower()
        
        # Простой поиск подстроки
        for word in self.profanity_words:
            word_lower = word.lower()
            if word_lower in text_lower:
                found_words.append(word)
        
        logger.info(f"Проверка текста '{text}' на слова {self.profanity_words[:5]}...")
        logger.info(f"Найденные слова: {found_words}")
        
        return len(found_words) > 0, found_words
    
    def check_spam(self, text: str) -> Tuple[bool, str]:
        """Проверка на спам"""
        if not self.config.SPAM_FILTER:
            return False, ""
        
        # Проверка на повторяющиеся символы
        if re.search(r'(.)\1{4,}', text):
            return True, "Повторяющиеся символы"
        
        # Проверка на длинные сообщения
        if len(text) > 1000:
            return True, "Слишком длинное сообщение"
        
        # Проверка на капс
        if len(text) > 10 and text.isupper():
            return True, "Слишком много заглавных букв"
        
        return False, ""
    
    def check_links(self, text: str) -> Tuple[bool, List[str]]:
        """Проверка на ссылки"""
        if not self.config.LINK_FILTER:
            return False, []
        
        link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        links = re.findall(link_pattern, text)
        
        return len(links) > 0, links
    
    def analyze_message(self, text: str) -> dict:
        """Полный анализ сообщения"""
        result = {
            'is_violation': False,
            'violation_type': None,
            'violation_reason': '',
            'found_words': [],
            'found_links': [],
            'confidence': 0
        }
        
        # Проверка на нецензурные слова
        profanity_found, profanity_words = self.check_profanity(text)
        if profanity_found:
            result['is_violation'] = True
            result['violation_type'] = 'profanity'
            result['violation_reason'] = f"Нецензурные слова: {', '.join(profanity_words)}"
            result['found_words'] = profanity_words
            result['confidence'] = 90
            return result
        
        # Проверка на спам
        spam_found, spam_reason = self.check_spam(text)
        if spam_found:
            result['is_violation'] = True
            result['violation_type'] = 'spam'
            result['violation_reason'] = f"Спам: {spam_reason}"
            result['confidence'] = 80
            return result
        
        # Проверка на ссылки
        links_found, links = self.check_links(text)
        if links_found:
            result['is_violation'] = True
            result['violation_type'] = 'links'
            result['violation_reason'] = f"Ссылки: {', '.join(links)}"
            result['found_links'] = links
            result['confidence'] = 70
            return result
        
        return result
    
    def get_moderation_action(self, analysis: dict, user_warnings: int) -> str:
        """Определение действия модерации"""
        if not analysis['is_violation']:
            return 'none'
        
        violation_type = analysis['violation_type']
        confidence = analysis['confidence']
        
        # Высокая уверенность - удаление + предупреждение
        if confidence >= 80:
            if user_warnings >= self.config.MAX_WARNINGS:
                return 'ban'
            else:
                return 'warn'
        
        # Средняя уверенность - только удаление
        elif confidence >= 60:
            return 'delete'
        
        # Низкая уверенность - игнорировать
        else:
            return 'none'
