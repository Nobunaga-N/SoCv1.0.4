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

from core.logger import setup_logger, safe_log_message
from core.adb_controller import ADBController
from core.image_handler import ImageHandler
from game.game_bot import OptimizedGameBot
from config.settings import validate_config
from utils.validators import validate_server_range, validate_step_number


def open_terminal_if_needed():
    """
    Открывает новый терминал, если программа запущена не из терминала.
    Использует PowerShell на Windows вместо CMD.
    """
    import os
    import sys
    import platform
    import subprocess
    import shutil

    # Проверяем, запущена ли программа уже из терминала
    is_terminal = os.isatty(sys.stdout.fileno()) if hasattr(sys.stdout, 'fileno') else False

    if not is_terminal:
        logger = logging.getLogger('sea_conquest_bot.main')
        logger.info("Открываем терминал для вывода логов")

        system = platform.system()
        try:
            # Получаем абсолютный путь к скрипту
            script_path = os.path.abspath(sys.argv[0])

            if system == 'Windows':
                # Определяем, использовать pwsh (PowerShell Core) или powershell (Windows PowerShell)
                powershell_exe = 'pwsh.exe' if shutil.which('pwsh.exe') else 'powershell.exe'

                # Формируем команду для PowerShell
                # Используем -NoExit, чтобы окно оставалось открытым после выполнения скрипта
                # Используем -Command для запуска нашего скрипта
                command = f'python "{script_path}" {" ".join(sys.argv[1:])}'
                subprocess.Popen([powershell_exe, '-NoExit', '-Command', command],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif system == 'Darwin':  # macOS
                # Открываем Terminal с командой запуска скрипта
                applescript = (
                    f'tell application "Terminal" to do script "cd {os.path.dirname(script_path)} && '
                    f'python3 {script_path} {" ".join(sys.argv[1:])}"'
                )
                subprocess.Popen(['osascript', '-e', applescript])
            else:  # Linux и другие Unix-подобные
                # Пробуем различные терминалы
                terminals = ['gnome-terminal', 'xterm', 'konsole', 'terminator']
                for terminal in terminals:
                    try:
                        subprocess.Popen([terminal, '--', 'python3', script_path] + sys.argv[1:])
                        break
                    except FileNotFoundError:
                        continue

            # Завершаем текущий процесс, так как новый запущен в терминале
            sys.exit(0)

        except Exception as e:
            print(f"Ошибка при открытии терминала: {e}")


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

    main_group.add_argument(
        '--use-emoji',
        action='store_true',
        help='Включение эмодзи в файловых логах (может вызвать проблемы на Windows)'
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

    # Используем безопасные сообщения
    logger.info(safe_log_message("🔍 Проверка окружения...", "Проверка окружения..."))

    # Проверка конфигурации
    logger.info("Проверка конфигурации...")
    try:
        if not validate_config():
            logger.error(safe_log_message("❌ Конфигурация содержит критические ошибки",
                                        "ОШИБКА: Конфигурация содержит критические ошибки"))
            return False
        logger.info(safe_log_message("✅ Конфигурация прошла валидацию",
                                   "ОК: Конфигурация прошла валидацию"))
    except Exception as e:
        logger.error(f"Ошибка при валидации конфигурации: {e}", exc_info=True)
        return False

    # Проверка наличия ADB
    logger.info("Проверка наличия ADB...")
    try:
        import subprocess
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(safe_log_message("❌ ADB не найден или не работает корректно",
                                        "ОШИБКА: ADB не найден или не работает корректно"))
            return False
        version_line = result.stdout.splitlines()[0]
        logger.info(safe_log_message(f"✅ Обнаружен ADB: {version_line}",
                                   f"ОК: Обнаружен ADB: {version_line}"))
    except Exception as e:
        logger.error(f"Ошибка при проверке ADB: {e}")
        return False

    # Проверка наличия необходимых библиотек
    logger.info("Проверка зависимостей...")
    try:
        import cv2
        import numpy
        logger.info(safe_log_message("✅ OpenCV и NumPy доступны",
                                   "ОК: OpenCV и NumPy доступны"))
    except ImportError as e:
        logger.error(f"Отсутствует необходимая библиотека: {e}")
        logger.error("Установите зависимости: pip install -r requirements.txt")
        return False

    # Проверка наличия Tesseract OCR (опционально)
    try:
        import pytesseract
        logger.info(safe_log_message("✅ OCR (Tesseract) доступен",
                                   "ОК: OCR (Tesseract) доступен"))
    except ImportError:
        logger.warning(safe_log_message("⚠️ OCR (Tesseract) не доступен. Некоторые функции могут работать ограниченно",
                                      "ВНИМАНИЕ: OCR (Tesseract) не доступен. Некоторые функции могут работать ограниченно"))

    logger.info(safe_log_message("✅ Все проверки окружения пройдены успешно",
                               "ОК: Все проверки окружения пройдены успешно"))
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
        logger.info(safe_log_message(f"🧪 Тестирование выбора сервера {args.test_server}",
                                   f"ТЕСТ: Тестирование выбора сервера {args.test_server}"))
        result = game_bot.test_server_selection(args.test_server)
        status = safe_log_message("✅ Успех", "УСПЕХ") if result else safe_log_message("❌ Неудача", "НЕУДАЧА")
        print(f"Результат тестирования: {status}")

    if args.test_skip:
        logger.info(safe_log_message("🧪 Тестирование поиска кнопки ПРОПУСТИТЬ",
                                   "ТЕСТ: Тестирование поиска кнопки ПРОПУСТИТЬ"))
        result = game_bot.test_skip_button_search()
        status = safe_log_message("✅ Кнопка найдена", "УСПЕХ: Кнопка найдена") if result else safe_log_message("❌ Кнопка не найдена", "НЕУДАЧА: Кнопка не найдена")
        print(f"Результат тестирования: {status}")

    if args.test_step:
        logger.info(safe_log_message(f"🧪 Тестирование выполнения шага {args.test_step}",
                                   f"ТЕСТ: Тестирование выполнения шага {args.test_step}"))
        result = game_bot.execute_single_step(args.test_step)
        status = safe_log_message("✅ Успех", "УСПЕХ") if result else safe_log_message("❌ Неудача", "НЕУДАЧА")
        print(f"Результат тестирования: {status}")

    if args.info:
        logger.info(safe_log_message("📊 Получение информации о текущем экране",
                                   "ИНФО: Получение информации о текущем экране"))
        info = game_bot.get_current_screen_info()
        print("\nИнформация об экране:")
        for key, value in info.items():
            print(f"  • {key}: {value}")


def get_user_input():
    """
    Получение параметров от пользователя через интерактивный интерфейс.

    Returns:
        tuple: (start_server, end_server, start_step)
    """
    print("\n" + "="*50)
    print(safe_log_message("🎮 Настройка параметров бота Sea of Conquest",
                          "Настройка параметров бота Sea of Conquest"))
    print("="*50)

    # Получение диапазона серверов
    while True:
        try:
            print(safe_log_message("\n📡 Настройка диапазона серверов:",
                                 "\nНастройка диапазона серверов:"))
            start_server = int(input("  Начальный сервер (по умолчанию 619): ") or "619")
            end_server = int(input("  Конечный сервер (по умолчанию 1): ") or "1")

            if validate_server_range(start_server, end_server):
                break
            else:
                print(safe_log_message("  ❌ Некорректный диапазон серверов. Попробуйте снова.",
                                      "  ОШИБКА: Некорректный диапазон серверов. Попробуйте снова."))
        except ValueError:
            print(safe_log_message("  ❌ Введите корректные числовые значения.",
                                 "  ОШИБКА: Введите корректные числовые значения."))

    # Получение начального шага
    while True:
        try:
            print(safe_log_message("\n🚀 Настройка начального шага (только для первого сервера):",
                                 "\nНастройка начального шага (только для первого сервера):"))
            start_step = int(input("  Начальный шаг (1-97, по умолчанию 1): ") or "1")

            if validate_step_number(start_step):
                break
            else:
                print(safe_log_message("  ❌ Некорректный номер шага. Введите число от 1 до 97.",
                                      "  ОШИБКА: Некорректный номер шага. Введите число от 1 до 97."))
        except ValueError:
            print(safe_log_message("  ❌ Введите корректное числовое значение.",
                                 "  ОШИБКА: Введите корректное числовое значение."))

    print(safe_log_message(f"\n✅ Настройка завершена:", f"\nНастройка завершена:"))
    print(f"  • Диапазон серверов: {start_server} → {end_server}")
    print(f"  • Начальный шаг: {start_step}")

    return start_server, end_server, start_step


def main():
    """Главная функция запуска бота."""
    print(safe_log_message("🌊 Запуск бота Sea of Conquest...", "Запуск бота Sea of Conquest..."))

    # Проверяем необходимость открытия терминала
    open_terminal_if_needed()

    # Парсинг аргументов командной строки
    args = parse_arguments()

    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_level=log_level, use_emoji_in_file=args.use_emoji)
    logger.info(safe_log_message("🚀 Запуск бота для прохождения обучения в игре Sea of Conquest",
                               "Запуск бота для прохождения обучения в игре Sea of Conquest"))

    # Проверка окружения
    if not check_environment():
        logger.error("Проверка окружения не пройдена. Выход.")
        sys.exit(1)

    try:
        # Инициализация компонентов
        logger.info(safe_log_message("🔧 Инициализация компонентов...",
                                   "Инициализация компонентов..."))

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
        logger.info(safe_log_message("✅ Все компоненты инициализированы успешно",
                                   "ОК: Все компоненты инициализированы успешно"))

        # Проверка на тестовые режимы
        if any([args.test_server, args.test_skip, args.test_step, args.info]):
            run_test_mode(args, game_bot)
            return

        # Получение параметров для обычного режима
        start_server, end_server, start_step = get_user_input()

        # Подтверждение запуска
        server_count = start_server - end_server + 1
        cycles_to_run = min(args.cycles, server_count)

        print(safe_log_message(f"\n🎯 Готов к запуску:", f"\nГотов к запуску:"))
        print(f"  • Циклов для выполнения: {cycles_to_run}")
        print(f"  • Серверов для обработки: {server_count}")

        confirm = input("\nПродолжить? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes', 'да']:
            print(safe_log_message("❌ Выполнение отменено пользователем",
                                  "Выполнение отменено пользователем"))
            return

        # Запуск бота
        logger.info(safe_log_message(f"🚀 Запуск бота на {cycles_to_run} циклов (сервера {start_server}→{end_server})",
                                   f"Запуск бота на {cycles_to_run} циклов (сервера {start_server}→{end_server})"))
        logger.info(f"Начальный шаг для первого сервера: {start_step}")

        successful_cycles = game_bot.run_bot(
            cycles=args.cycles,
            start_server=start_server,
            end_server=end_server,
            first_server_start_step=start_step
        )

        # Результаты выполнения
        print(safe_log_message(f"\n🏁 Выполнение завершено!", f"\nВыполнение завершено!"))
        print(f"  • Успешно выполнено: {successful_cycles} из {cycles_to_run} циклов")

        if successful_cycles < cycles_to_run:
            print(f"  • Не выполнено: {cycles_to_run - successful_cycles} циклов")

        logger.info(f"Итоги: {successful_cycles}/{cycles_to_run} циклов выполнено успешно")

    except KeyboardInterrupt:
        logger.info(safe_log_message("⏹️ Работа бота прервана пользователем (Ctrl+C)",
                                   "Работа бота прервана пользователем (Ctrl+C)"))
        print(safe_log_message("\n⏹️ Выполнение прервано пользователем",
                              "\nВыполнение прервано пользователем"))
    except Exception as e:
        logger.error(f"Критическая ошибка при работе бота: {e}", exc_info=True)
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)
    finally:
        logger.info(safe_log_message("🏁 Работа бота завершена", "Работа бота завершена"))
        print(safe_log_message("👋 До свидания!", "До свидания!"))


if __name__ == "__main__":
    main()