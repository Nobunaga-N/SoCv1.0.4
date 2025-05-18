"""
Главный модуль бота для прохождения обучения в игре Sea of Conquest.
Оптимизированная версия с модульной архитектурой и улучшенной структурой.
"""
import sys
import argparse
import logging
from pathlib import Path

# Добавляем корневую директорию проекта в Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import setup_logger
from core.adb_controller import ADBController
from core.image_handler import ImageHandler
from game.game_bot import OptimizedGameBot
from config.settings import validate_config
from utils.validators import validate_server_range, validate_step_number


def parse_arguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description='Бот для прохождения обучения в игре Sea of Conquest',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py                              # Запуск с интерактивным вводом
  python main.py -c 5 -v                      # 5 циклов с подробным логированием
  python main.py --test-server 505            # Тестирование выбора сервера 505
  python main.py --test-skip                  # Тестирование поиска кнопки ПРОПУСТИТЬ
  python main.py --info                       # Информация о текущем экране
        """
    )

    # Основные параметры
    main_group = parser.add_argument_group('Основные параметры')
    main_group.add_argument(
        '-c', '--cycles',
        type=int,
        default=1,
        help='Количество циклов обучения (по умолчанию: 1)'
    )

    main_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Включение подробного логирования'
    )

    # Настройки подключения
    connection_group = parser.add_argument_group('Настройки подключения')
    connection_group.add_argument(
        '-d', '--device',
        type=str,
        default=None,
        help='Имя устройства ADB (по умолчанию: первое доступное)'
    )

    connection_group.add_argument(
        '-H', '--host',
        type=str,
        default='127.0.0.1',
        help='Хост ADB сервера (по умолчанию: 127.0.0.1)'
    )

    connection_group.add_argument(
        '-p', '--port',
        type=int,
        default=5037,
        help='Порт ADB сервера (по умолчанию: 5037)'
    )

    # Тестовые режимы
    test_group = parser.add_argument_group('Режимы тестирования')
    test_group.add_argument(
        '--test-server',
        type=int,
        help='Тестирование выбора указанного сервера (без выполнения обучения)'
    )

    test_group.add_argument(
        '--test-skip',
        action='store_true',
        help='Тестирование поиска кнопки ПРОПУСТИТЬ'
    )

    test_group.add_argument(
        '--test-step',
        type=int,
        help='Выполнение одного шага обучения для тестирования'
    )

    test_group.add_argument(
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
    logger.info("🔍 Проверка окружения...")

    # Проверка конфигурации
    logger.info("Проверка конфигурации...")
    try:
        if not validate_config():
            logger.error("❌ Конфигурация содержит критические ошибки")
            return False
        logger.info("✅ Конфигурация прошла валидацию")
    except Exception as e:
        logger.error(f"❌ Ошибка при валидации конфигурации: {e}", exc_info=True)
        return False

    # Проверка наличия ADB
    logger.info("Проверка наличия ADB...")
    try:
        import subprocess
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ ADB не найден или не работает корректно")
            return False
        version_line = result.stdout.splitlines()[0]
        logger.info(f"✅ Обнаружен ADB: {version_line}")
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке ADB: {e}")
        return False

    # Проверка наличия необходимых библиотек
    logger.info("Проверка зависимостей...")
    try:
        import cv2
        import numpy
        logger.info("✅ OpenCV и NumPy доступны")
    except ImportError as e:
        logger.error(f"❌ Отсутствует необходимая библиотека: {e}")
        logger.error("Установите зависимости: pip install -r requirements.txt")
        return False

    # Проверка наличия Tesseract OCR (опционально)
    try:
        import pytesseract
        logger.info("✅ OCR (Tesseract) доступен")
    except ImportError:
        logger.warning("⚠️  OCR (Tesseract) не доступен. Некоторые функции могут работать ограниченно")

    logger.info("✅ Все проверки окружения пройдены успешно")
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
        logger.info(f"🧪 Тестирование выбора сервера {args.test_server}")
        result = game_bot.test_server_selection(args.test_server)
        status = "✅ Успех" if result else "❌ Неудача"
        print(f"Результат тестирования: {status}")

    if args.test_skip:
        logger.info("🧪 Тестирование поиска кнопки ПРОПУСТИТЬ")
        result = game_bot.test_skip_button_search()
        status = "✅ Кнопка найдена" if result else "❌ Кнопка не найдена"
        print(f"Результат тестирования: {status}")

    if args.test_step:
        logger.info(f"🧪 Тестирование выполнения шага {args.test_step}")
        result = game_bot.execute_single_step(args.test_step)
        status = "✅ Успех" if result else "❌ Неудача"
        print(f"Результат тестирования: {status}")

    if args.info:
        logger.info("📊 Получение информации о текущем экране")
        info = game_bot.get_current_screen_info()
        print("\n📋 Информация об экране:")
        for key, value in info.items():
            print(f"  • {key}: {value}")


def get_user_input():
    """
    Получение параметров от пользователя через интерактивный интерфейс.

    Returns:
        tuple: (start_server, end_server, start_step)
    """
    print("\n" + "="*50)
    print("🎮 Настройка параметров бота Sea of Conquest")
    print("="*50)

    # Получение диапазона серверов
    while True:
        try:
            print("\n📡 Настройка диапазона серверов:")
            start_server = int(input("  Начальный сервер (по умолчанию 619): ") or "619")
            end_server = int(input("  Конечный сервер (по умолчанию 1): ") or "1")

            if validate_server_range(start_server, end_server):
                break
            else:
                print("  ❌ Некорректный диапазон серверов. Попробуйте снова.")
        except ValueError:
            print("  ❌ Введите корректные числовые значения.")

    # Получение начального шага
    while True:
        try:
            print("\n🚀 Настройка начального шага (только для первого сервера):")
            start_step = int(input("  Начальный шаг (1-97, по умолчанию 1): ") or "1")

            if validate_step_number(start_step):
                break
            else:
                print("  ❌ Некорректный номер шага. Введите число от 1 до 97.")
        except ValueError:
            print("  ❌ Введите корректное числовое значение.")

    print(f"\n✅ Настройка завершена:")
    print(f"  • Диапазон серверов: {start_server} → {end_server}")
    print(f"  • Начальный шаг: {start_step}")

    return start_server, end_server, start_step


def main():
    """Главная функция запуска бота."""
    print("🌊 Запуск бота Sea of Conquest...")

    # Парсинг аргументов командной строки
    args = parse_arguments()

    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_level=log_level)
    logger.info("🚀 Запуск бота для прохождения обучения в игре Sea of Conquest")

    # Проверка окружения
    if not check_environment():
        logger.error("❌ Проверка окружения не пройдена. Выход.")
        sys.exit(1)

    try:
        # Инициализация компонентов
        logger.info("🔧 Инициализация компонентов...")

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
        logger.info("✅ Все компоненты инициализированы успешно")

        # Проверка на тестовые режимы
        if any([args.test_server, args.test_skip, args.test_step, args.info]):
            run_test_mode(args, game_bot)
            return

        # Получение параметров для обычного режима
        start_server, end_server, start_step = get_user_input()

        # Подтверждение запуска
        server_count = start_server - end_server + 1
        cycles_to_run = min(args.cycles, server_count)

        print(f"\n🎯 Готов к запуску:")
        print(f"  • Циклов для выполнения: {cycles_to_run}")
        print(f"  • Серверов для обработки: {server_count}")

        confirm = input("\nПродолжить? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes', 'да']:
            print("❌ Выполнение отменено пользователем")
            return

        # Запуск бота
        logger.info(f"🚀 Запуск бота на {cycles_to_run} циклов (сервера {start_server}→{end_server})")
        logger.info(f"📍 Начальный шаг для первого сервера: {start_step}")

        successful_cycles = game_bot.run_bot(
            cycles=args.cycles,
            start_server=start_server,
            end_server=end_server,
            first_server_start_step=start_step
        )

        # Результаты выполнения
        print(f"\n🏁 Выполнение завершено!")
        print(f"  ✅ Успешно выполнено: {successful_cycles} из {cycles_to_run} циклов")

        if successful_cycles < cycles_to_run:
            print(f"  ⚠️  Не выполнено: {cycles_to_run - successful_cycles} циклов")

        logger.info(f"📊 Итоги: {successful_cycles}/{cycles_to_run} циклов выполнено успешно")

    except KeyboardInterrupt:
        logger.info("⏹️  Работа бота прервана пользователем (Ctrl+C)")
        print("\n⏹️  Выполнение прервано пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при работе бота: {e}", exc_info=True)
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        logger.info("🏁 Работа бота завершена")
        print("👋 До свидания!")


if __name__ == "__main__":
    main()