"""
Модуль для настройки системы логирования с поддержкой Unicode.
"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path


class UnicodeFormatter(logging.Formatter):
    """Кастомный форматер, который корректно обрабатывает Unicode символы."""

    def __init__(self, fmt=None, datefmt=None, use_emoji=True):
        super().__init__(fmt, datefmt)
        self.use_emoji = use_emoji

        # Словарь замен эмодзи на текст для файлового лога
        self.emoji_replacements = {
            '🚀': '[START]',
            '🔍': '[CHECK]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🔧': '[INIT]',
            '📡': '[NETWORK]',
            '🎮': '[GAME]',
            '📊': '[INFO]',
            '💥': '[CRITICAL]',
            '⏹️': '[STOP]',
            '🏁': '[FINISH]',
            '👋': '[BYE]',
            '🧪': '[TEST]',
            '📋': '[LIST]',
            '🎯': '[TARGET]',
            '🌊': '[MAIN]',
        }

    def format(self, record):
        # Форматируем запись стандартным способом
        formatted = super().format(record)

        # Если эмодзи отключены, заменяем их на текстовые аналоги
        if not self.use_emoji:
            for emoji, replacement in self.emoji_replacements.items():
                formatted = formatted.replace(emoji, replacement)

        return formatted


def setup_logger(log_dir='logs', log_level=logging.INFO, use_emoji_in_file=False):
    """
    Настройка системы логирования с поддержкой Unicode.

    Args:
        log_dir: директория для хранения логов
        log_level: уровень логирования
        use_emoji_in_file: использовать ли эмодзи в файловом логе

    Returns:
        logging.Logger: настроенный логгер
    """
    # Создание директории для логов, если она не существует
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Формирование имени файла лога с датой и временем
    log_filename = log_path / f'sea_conquest_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    # Настройка форматирования для консоли (с эмодзи)
    console_formatter = UnicodeFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        use_emoji=True
    )

    # Настройка форматирования для файла (без эмодзи, если не указано иное)
    file_formatter = UnicodeFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        use_emoji=use_emoji_in_file
    )

    # Настройка файлового обработчика с явным указанием кодировки UTF-8
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # Настройка консольного обработчика
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Для Windows пытаемся настроить консоль для поддержки UTF-8
    if sys.platform.startswith('win'):
        try:
            # Попытка установить UTF-8 для вывода в консоль
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, OSError):
            # Если не удалось, используем формат без эмодзи для консоли тоже
            console_formatter = UnicodeFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                use_emoji=False
            )
            console_handler.setFormatter(console_formatter)

    # Настройка корневого логгера
    logger = logging.getLogger('sea_conquest_bot')
    logger.setLevel(log_level)

    # Очистка существующих обработчиков
    logger.handlers = []

    # Добавление обработчиков к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Предотвращение дублирования логов в корневом логгере
    logger.propagate = False

    # Логируем без эмодзи для избежания ошибок инициализации
    logger.info(f"Логирование настроено. Уровень: {logging.getLevelName(log_level)}")
    logger.info(f"Лог сохраняется в: {log_filename}")
    logger.info(f"Кодировка файла лога: UTF-8")

    if use_emoji_in_file:
        logger.info("Эмодзи включены в файловом логе")
    else:
        logger.info("Эмодзи отключены в файловом логе")

    return logger


def get_safe_logger(name):
    """
    Получение логгера с безопасным форматированием сообщений.

    Args:
        name: имя логгера

    Returns:
        logging.Logger: настроенный логгер
    """
    return logging.getLogger(f'sea_conquest_bot.{name}')


# Функция для безопасного форматирования сообщений с эмодзи
def safe_log_message(message, fallback_message=None):
    """
    Безопасное форматирование сообщения лога.

    Args:
        message: сообщение с эмодзи
        fallback_message: запасное сообщение без эмодзи

    Returns:
        str: безопасное сообщение
    """
    try:
        # Пытаемся закодировать сообщение в UTF-8
        message.encode('utf-8')
        return message
    except UnicodeEncodeError:
        # Если не удалось, возвращаем запасное сообщение или удаляем эмодзи
        if fallback_message:
            return fallback_message
        else:
            # Простая замена известных эмодзи
            emoji_map = {
                '🚀': '[START]',
                '🔍': '[CHECK]',
                '✅': '[OK]',
                '❌': '[ERROR]',
                '⚠️': '[WARNING]',
                '🔧': '[INIT]',
            }
            safe_message = message
            for emoji, replacement in emoji_map.items():
                safe_message = safe_message.replace(emoji, replacement)
            return safe_message