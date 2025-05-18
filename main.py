"""
Главный модуль бота для прохождения обучения в игре Sea of Conquest.
Обновленная версия с модульной архитектурой.
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path

from core.logger import setup_logger
from core.adb_controller import ADBController
from core.image_handler import ImageHandler
from game_bot import OptimizedGameBot
from utils.config import validate_config


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Бот для прохождения обучения в игре Sea of Conquest')

    parser.add_argument(
        '-c', '--cycles',
        type=int,
        default=1,
        help='Количество циклов обучения (по умолчанию: 1)'
    )

    parser.add_argument(
        '-d', '--device',
        type=str,
        default=None,
        help='Имя устройства ADB (по умолчанию: первое доступное)'
    )

    parser.add_argument(
        '-H', '--host',
        type=str,
        default='127.0.0.1',
        help='Хост ADB сервера (по умолчанию: 127.0.0.1)'
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=5037,
        help='Порт ADB сервера (по умолчанию: 5037)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Включение подробного логирования'
    )

    parser.add_argument(
        '--test-server',
        type=int,
        help='Тестирование выбора указанного сервера (без выполнения обучения)'
    )

    parser.add_argument(
        '--test-skip',
        action='store_true',
        help='Тестирование поиска кнопки ПРОПУСТИТЬ'
    )

    parser.add_argument(
        '--test-step',
        type=int,
        help='Выполнение одного шага обучения для тестирования'
    )

    parser.add_argument(
        '--info',
        action='store_true',
        help='Получение информации о текущем экране'
    )

    return parser.parse_args()


def check_environment():
    """
    Проверка окружения перед запуском бота.

    Returns:
        bool: True если все проверки пройдены
    """
    logger = logging.getLogger('sea_conquest_bot.main')

    # Проверка конфигурации
    logger.info("Проверка конфигурации...")
    try:
        if not validate_config():
            logger.error("Конфигурация содержит критические ошибки")
            return False
    except Exception as e:
        logger.error(f"Ошибка при валидации конфигурации: {e}", exc_info=True)
        return False

    # Проверка наличия ADB
    logger.info("Проверка наличия ADB...")
    try:
        import subprocess
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("ADB не найден или не работает корректно")
            return False
        logger.info(f"Обнаружен ADB: {result.stdout.splitlines()[0]}")
    except Exception as e:
        logger.error(f"Ошибка при проверке ADB: {e}")
        return False

    # Проверка наличия необходимых библиотек
    try:
        import cv2
        import numpy
        logger.info("Библиотеки OpenCV и NumPy доступны")
    except ImportError as e:
        logger.error(f"Отсутствует необходимая библиотека: {e}")
        logger.error("Установите необходимые библиотеки: pip install -r requirements.txt")
        return False

    # Проверка наличия Tesseract OCR (опционально)
    try:
        import pytesseract
        logger.info("OCR (Tesseract) доступен для использования")
    except ImportError:
        logger.warning("OCR (Tesseract) не доступен. Некоторые функции могут работать ограниченно")

    logger.info("Все проверки пройдены успешно")
    return True


def run_test_mode(args, game_bot):
    """
    Выполнение тестовых режимов.

    Args:
        args: аргументы командной строки
        game_bot: экземпляр бота
    """
    logger = logging.getLogger('sea_conquest_bot.main')

    if args.test_server:
        logger.info(f"=== Тестирование выбора сервера {args.test_server} ===")
        result = game_bot.test_server_selection(args.test_server)
        print(f"Результат тестирования: {'Успех' if result else 'Неудача'}")

    if args.test_skip:
        logger.info("=== Тестирование поиска кнопки ПРОПУСТИТЬ ===")
        result = game_bot.test_skip_button_search()
        print(f"Результат тестирования: {'Кнопка найдена' if result else 'Кнопка не найдена'}")

    if args.test_step:
        logger.info(f"=== Тестирование выполнения шага {args.test_step} ===")
        result = game_bot.execute_single_step(args.test_step)
        print(f"Результат тестирования: {'Успех' if result else 'Неудача'}")

    if args.info:
        logger.info("=== Информация о текущем экране ===")
        info = game_bot.get_current_screen_info()
        print("Информация об экране:")
        for key, value in info.items():
            print(f"  {key}: {value}")


def get_user_input():
    """Получение параметров от пользователя."""
    while True:
        try:
            print("\n=== Настройка диапазона серверов ===")
            start_server = int(input("Введите начальный сервер (по умолчанию 619): ") or "619")
            end_server = int(input("Введите конечный сервер (по умолчанию 1): ") or "1")

            if start_server < end_server:
                print("Ошибка: Начальный сервер должен быть больше или равен конечному.")
                continue

            break
        except ValueError:
            print("Ошибка: Введите корректные числовые значения.")

    # Запрос начального шага для первого сервера
    start_step = 1
    try:
        print("\n=== Настройка начального шага (только для первого сервера) ===")
        start_step = int(input("Введите начальный шаг для первого сервера (по умолчанию 1): ") or "1")

        if start_step < 1 or start_step > 97:
            print(f"Предупреждение: Введен шаг {start_step} вне диапазона 1-97. Будет использован шаг 1.")
            start_step = 1
    except ValueError:
        print("Ошибка при вводе начального шага. Будет использован шаг 1.")
        start_step = 1

    return start_server, end_server, start_step


def main():
    """Главная функция запуска бота."""
    # Парсинг аргументов командной строки
    args = parse_arguments()

    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_level=log_level)
    logger.info("Запуск бота для прохождения обучения в игре Sea of Conquest")

    # Проверка окружения
    if not check_environment():
        logger.error("Проверка окружения не пройдена. Выход.")
        sys.exit(1)

    try:
        # Инициализация компонентов
        logger.info("Инициализация компонентов...")

        # Создание контроллера ADB
        adb_controller = ADBController(
            host=args.host,
            port=args.port,
            device_name=args.device
        )

        # Создание обработчика изображений
        image_handler = ImageHandler(adb_controller)

        # Создание бота
        game_bot = OptimizedGameBot(adb_controller, image_handler)

        # Проверка на тестовые режимы
        if any([args.test_server, args.test_skip, args.test_step, args.info]):
            run_test_mode(args, game_bot)
            return

        # Получение параметров от пользователя для обычного режима
        start_server, end_server, start_step = get_user_input()

        # Запуск бота на выполнение заданного количества циклов
        logger.info(f"Запуск бота на {args.cycles} циклов с серверами от {start_server} до {end_server}")
        logger.info(f"Начальный шаг для первого сервера: {start_step}")

        successful_cycles = game_bot.run_bot(
            cycles=args.cycles,
            start_server=start_server,
            end_server=end_server,
            first_server_start_step=start_step
        )

        logger.info(f"Успешно выполнено {successful_cycles} из {args.cycles} циклов")

    except KeyboardInterrupt:
        logger.info("Работа бота прервана пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка при работе бота: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Работа бота завершена")


if __name__ == "__main__":
    main()