"""
Конфигурация и настройки бота Sea of Conquest.
"""

from .settings import *

__all__ = [
    # Базовые настройки
    'DEFAULT_TIMEOUT', 'LOADING_TIMEOUT', 'SCREENSHOT_TIMEOUT',
    'GAME_PACKAGE', 'GAME_ACTIVITY',

    # Пути и директории
    'BASE_DIR', 'IMAGES_DIR', 'IMAGE_PATHS',

    # Координаты и области
    'COORDINATES', 'OCR_REGIONS', 'SEASONS',

    # Настройки распознавания
    'SKIP_BUTTON_VARIANTS', 'SERVER_RECOGNITION_SETTINGS',
    'OCR_SETTINGS', 'TEMPLATE_MATCHING_THRESHOLD',

    # Паузы и тайминги
    'PAUSE_SETTINGS',

    # Валидация
    'validate_config'
]