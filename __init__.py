"""
Sea of Conquest Bot - Автоматизированный бот для прохождения обучения.

Основные компоненты:
- core: базовые компоненты (ADB, обработка изображений, логирование)
- ui: компоненты интерфейса (OCR, селектор серверов)
- tutorial: система выполнения обучения
- game: основной класс бота
- config: конфигурация и настройки
- utils: вспомогательные функции
"""

__version__ = "1.0.4"
__author__ = "SeaConquest Bot Developer"

# Основные экспорты для удобного импорта
from game.game_bot import OptimizedGameBot
from core.adb_controller import ADBController
from core.image_handler import ImageHandler
from core.logger import setup_logger

__all__ = [
    'OptimizedGameBot',
    'ADBController',
    'ImageHandler',
    'setup_logger'
]