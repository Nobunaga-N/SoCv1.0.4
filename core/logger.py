"""
Модуль для настройки системы логирования с поддержкой Unicode и цветного вывода.
"""
import logging
import os
import sys
import platform
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Форматтер с поддержкой цветов и Unicode символов."""

    # ANSI коды цветов
    COLORS = {
        'RESET': '\033[0m',
        'BLACK': '\033[30m',
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'BACKGROUND_RED': '\033[41m',
        'BACKGROUND_GREEN': '\033[42m',
        'BACKGROUND_YELLOW': '\033[43m',
    }

    # Соответствие уровней логов цветам
    LEVEL_COLORS = {
        logging.DEBUG: COLORS['BLUE'],
        logging.INFO: COLORS['WHITE'],
        logging.WARNING: COLORS['YELLOW'],
        logging.ERROR: COLORS['RED'],
        logging.CRITICAL: COLORS['BACKGROUND_RED'] + COLORS['WHITE'] + COLORS['BOLD'],
    }

    # Словарь соответствия эмодзи для разных уровней логирования
    LEVEL_EMOJI = {
        logging.DEBUG: '🔍',
        logging.INFO: 'ℹ️',
        logging.WARNING: '⚠️',
        logging.ERROR: '❌',
        logging.CRITICAL: '💥',
    }

    # Словарь замен эмодзи на текст для файлового лога
    EMOJI_REPLACEMENTS = {
        '🚀': '[START]',
        '🔍': '[DEBUG]',
        'ℹ️': '[INFO]',
        '✅': '[SUCCESS]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '🔧': '[INIT]',
        '📡': '[NETWORK]',
        '🎮': '[GAME]',
        '📊': '[STATS]',
        '💥': '[CRITICAL]',
        '⏹️': '[STOP]',
        '🏁': '[FINISH]',
        '👋': '[BYE]',
        '🧪': '[TEST]',
        '📋': '[LIST]',
        '🎯': '[TARGET]',
        '🌊': '[MAIN]',
        '🔄': '[RETRY]',
        '⚙️': '[CONFIG]',
        '📌': '[STEP]',
        '🔶': '[SECTION]',
    }

    def __init__(self, fmt=None, datefmt=None, use_colors=True, use_emoji=True):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
        self.use_emoji = use_emoji

        # Определяем, поддерживает ли терминал цвета
        if self.use_colors and platform.system() == 'Windows':
            # На Windows проверим поддержку ANSI цветов
            try:
                import colorama
                colorama.init()
            except ImportError:
                # Если colorama не установлена, отключаем цвета
                self.use_colors = False

    def format(self, record):
        # Форматируем запись стандартным способом
        formatted = super().format(record)

        # Если нужны цвета и у нас есть цвет для этого уровня логирования
        if self.use_colors and record.levelno in self.LEVEL_COLORS:
            color_start = self.LEVEL_COLORS[record.levelno]
            color_end = self.COLORS['RESET']
            formatted = f"{color_start}{formatted}{color_end}"

        # Если эмодзи отключены, заменяем их на текстовые аналоги
        if not self.use_emoji:
            for emoji, replacement in self.EMOJI_REPLACEMENTS.items():
                formatted = formatted.replace(emoji, replacement)

        return formatted

    def formatMessage(self, record):
        # Добавляем эмодзи в зависимости от уровня логирования, если они включены
        if self.use_emoji and record.levelno in self.LEVEL_EMOJI:
            level_emoji = self.LEVEL_EMOJI[record.levelno]
            record.message = f"{level_emoji} {record.message}"
        return super().formatMessage(record)


class StepHandler(logging.Handler):
    """Обработчик для выделения разделителей между шагами."""

    def __init__(self, formatter=None):
        super().__init__()
        if formatter:
            self.setFormatter(formatter)
        # Последний записанный номер шага
        self.last_step = None

    def emit(self, record):
        # Проверяем, содержит ли запись номер шага
        try:
            if "Выполняем шаг" in record.msg:
                # Извлекаем номер шага с помощью строкового поиска
                parts = record.msg.split("Выполняем шаг ")
                if len(parts) > 1:
                    step_part = parts[1].split(":", 1)[0].strip()
                    try:
                        step_num = int(step_part)
                        if step_num != self.last_step:
                            # Если номер шага изменился, выводим разделитель
                            self.last_step = step_num
                            divider = f"\n{'='*50}\n📌 ШАГ {step_num}\n{'='*50}\n"

                            # Применяем форматтер, если он задан
                            if self.formatter:
                                if hasattr(self.formatter, 'use_colors') and self.formatter.use_colors:
                                    divider = f"{ColoredFormatter.COLORS['CYAN']}{divider}{ColoredFormatter.COLORS['RESET']}"

                            # Выводим разделитель в консоль
                            sys.stdout.write(divider)
                            sys.stdout.flush()
                    except ValueError:
                        pass
        except Exception as e:
            # Игнорируем ошибки при обработке разделителей
            pass


def setup_logger(log_dir='logs', log_level=logging.INFO, use_emoji_in_file=False, use_colors=True):
    """
    Настройка системы логирования с поддержкой Unicode и цветного вывода.

    Args:
        log_dir: директория для хранения логов
        log_level: уровень логирования
        use_emoji_in_file: использовать ли эмодзи в файловом логе
        use_colors: использовать ли цвета в консоли

    Returns:
        logging.Logger: настроенный логгер
    """
    # Создание директории для логов, если она не существует
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Формирование имени файла лога с датой и временем
    log_filename = log_path / f'sea_conquest_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    # Настройка форматирования для консоли (с цветами и эмодзи)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        use_colors=use_colors,
        use_emoji=True
    )

    # Настройка форматирования для файла (без эмодзи, если не указано иное)
    file_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        use_colors=False,  # В файле никогда не используем цвета
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

    # Настройка обработчика для шагов
    step_handler = StepHandler(console_formatter)
    step_handler.setLevel(logging.INFO)  # Показываем разделители только для INFO и выше

    # Для Windows пытаемся настроить консоль для поддержки UTF-8
    if sys.platform.startswith('win'):
        try:
            # Попытка установить UTF-8 для вывода в консоль
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, OSError):
            # Если не удалось, используем минимальный набор эмодзи
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                use_colors=use_colors,
                use_emoji=False
            )
            console_handler.setFormatter(console_formatter)
            step_handler.setFormatter(console_formatter)

    # Настройка корневого логгера
    logger = logging.getLogger('sea_conquest_bot')
    logger.setLevel(log_level)

    # Очистка существующих обработчиков
    logger.handlers = []

    # Добавление обработчиков к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(step_handler)

    # Предотвращение дублирования логов в корневом логгере
    logger.propagate = False

    # Логируем без эмодзи для избежания ошибок инициализации
    logger.info(f"Логирование настроено. Уровень: {logging.getLevelName(log_level)}")
    logger.info(f"Лог сохраняется в: {log_filename}")
    logger.info(f"Кодировка файла лога: UTF-8")
    logger.info(f"Цветной вывод в консоли: {'Включен' if use_colors else 'Отключен'}")

    if use_emoji_in_file:
        logger.info("Эмодзи включены в файловом логе")
    else:
        logger.info("Эмодзи отключены в файловом логе")

    # Выводим разделитель при старте
    logger.info("\n" + "="*50)
    logger.info("🚀 БОТ SEA OF CONQUEST ЗАПУЩЕН")
    logger.info("="*50 + "\n")

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
            # Используем словарь замен из ColoredFormatter
            emoji_map = ColoredFormatter.EMOJI_REPLACEMENTS
            safe_message = message
            for emoji, replacement in emoji_map.items():
                safe_message = safe_message.replace(emoji, replacement)
            return safe_message


# Добавляем специальные методы для логирования с цветами
def log_success(logger, message):
    """Логирование успешного действия (зеленым цветом)."""
    # Добавляем эмодзи ✅ в начало сообщения
    logger.info(f"✅ {message}")


def log_failure(logger, message):
    """Логирование неудачного действия (красным цветом)."""
    # Добавляем эмодзи ❌ в начало сообщения
    logger.error(f"❌ {message}")


def log_step(logger, step_number, message):
    """Логирование начала шага с разделителем."""
    logger.info(f"Выполняем шаг {step_number}: {message}")


def log_section(logger, title):
    """Логирование начала раздела с разделителем."""
    # Используем эмодзи 🔶 для обозначения раздела
    divider = f"\n{'-'*50}\n🔶 {title}\n{'-'*50}"
    logger.info(divider)