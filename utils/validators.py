"""
Валидаторы и вспомогательные функции для проверки данных.
"""
import os
import re
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger('sea_conquest_bot.validators')


def validate_server_range(start_server: int, end_server: int) -> bool:
    """
    Валидация диапазона серверов.

    Args:
        start_server: начальный сервер
        end_server: конечный сервер

    Returns:
        bool: True если диапазон корректен
    """
    if not isinstance(start_server, int) or not isinstance(end_server, int):
        logger.error("Номера серверов должны быть целыми числами")
        return False

    if start_server < 1 or start_server > 619:
        logger.error(f"Начальный сервер {start_server} вне диапазона 1-619")
        return False

    if end_server < 1 or end_server > 619:
        logger.error(f"Конечный сервер {end_server} вне диапазона 1-619")
        return False

    if start_server < end_server:
        logger.error("Начальный сервер должен быть больше или равен конечному")
        return False

    return True


def validate_step_number(step: int) -> bool:
    """
    Валидация номера шага обучения.

    Args:
        step: номер шага

    Returns:
        bool: True если номер шага корректен
    """
    if not isinstance(step, int):
        logger.error("Номер шага должен быть целым числом")
        return False

    if step < 1 or step > 97:
        logger.error(f"Номер шага {step} вне диапазона 1-97")
        return False

    return True


def validate_coordinates(x: int, y: int, max_x: int = 1280, max_y: int = 720) -> bool:
    """
    Валидация координат экрана.

    Args:
        x: координата X
        y: координата Y
        max_x: максимальная ширина экрана
        max_y: максимальная высота экрана

    Returns:
        bool: True если координаты корректны
    """
    if not isinstance(x, int) or not isinstance(y, int):
        logger.error("Координаты должны быть целыми числами")
        return False

    if x < 0 or x > max_x:
        logger.error(f"Координата X {x} вне диапазона 0-{max_x}")
        return False

    if y < 0 or y > max_y:
        logger.error(f"Координата Y {y} вне диапазона 0-{max_y}")
        return False

    return True


def validate_image_path(image_path: str) -> bool:
    """
    Валидация пути к изображению.

    Args:
        image_path: путь к файлу изображения

    Returns:
        bool: True если путь корректен
    """
    if not isinstance(image_path, str):
        logger.error("Путь к изображению должен быть строкой")
        return False

    if not image_path.endswith(('.png', '.jpg', '.jpeg')):
        logger.warning(f"Неподдерживаемый формат изображения: {image_path}")
        return False

    path = Path(image_path)
    if not path.exists():
        logger.warning(f"Файл изображения не существует: {image_path}")
        return False

    return True


def sanitize_filename(filename: str) -> str:
    """
    Очистка имени файла от недопустимых символов.

    Args:
        filename: исходное имя файла

    Returns:
        str: очищенное имя файла
    """
    # Удаляем недопустимые символы для файловой системы
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Удаляем пробелы в начале и конце
    sanitized = sanitized.strip()

    # Ограничиваем длину
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."

    return sanitized


def validate_timeout(timeout: float) -> bool:
    """
    Валидация значения таймаута.

    Args:
        timeout: значение таймаута в секундах

    Returns:
        bool: True если таймаут корректен
    """
    if not isinstance(timeout, (int, float)):
        logger.error("Таймаут должен быть числом")
        return False

    if timeout < 0:
        logger.error("Таймаут не может быть отрицательным")
        return False

    if timeout > 300:  # 5 минут максимум
        logger.warning(f"Очень большой таймаут: {timeout} сек")

    return True


def validate_region(region: Tuple[int, int, int, int]) -> bool:
    """
    Валидация области на экране.

    Args:
        region: кортеж (x, y, width, height)

    Returns:
        bool: True если область корректна
    """
    if not isinstance(region, tuple) or len(region) != 4:
        logger.error("Область должна быть кортежем из 4 элементов (x, y, w, h)")
        return False

    x, y, w, h = region

    if not all(isinstance(coord, int) for coord in region):
        logger.error("Все координаты области должны быть целыми числами")
        return False

    if x < 0 or y < 0 or w <= 0 or h <= 0:
        logger.error("Недопустимые значения области")
        return False

    return True


def format_duration(seconds: float) -> str:
    """
    Форматирование длительности в читаемый вид.

    Args:
        seconds: количество секунд

    Returns:
        str: отформатированная строка
    """
    if seconds < 60:
        return f"{seconds:.1f} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        sec = seconds % 60
        return f"{int(minutes)}м {sec:.0f}с"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}ч {int(minutes)}м"