"""
Оптимизированный главный класс бота с улучшенной архитектурой.
Использует модульную структуру и централизованную конфигурацию.
"""
import logging
import time
from typing import Optional

from core.adb_controller import ADBController
from core.image_handler import ImageHandler
from ui.interface_controller import InterfaceController
from ui.ocr_handler import OCRHandler
from ui.server_selector import OptimizedServerSelector
from tutorial.tutorial_executor import TutorialExecutor
from config.settings import DEFAULT_TIMEOUT, GAME_PACKAGE, GAME_ACTIVITY


class OptimizedGameBot:
    """
    Основной класс бота для прохождения обучения в игре Sea of Conquest.
    Использует модульную архитектуру для лучшей поддержки и расширяемости.
    """

    def __init__(self, adb_controller: ADBController, image_handler: ImageHandler):
        """
        Инициализация бота.

        Args:
            adb_controller: контроллер ADB
            image_handler: обработчик изображений
        """
        self.logger = logging.getLogger('sea_conquest_bot.main')
        self.adb = adb_controller
        self.image = image_handler

        # Инициализация компонентов
        self.logger.info("🔧 Инициализация компонентов бота...")

        # Контроллер интерфейса
        self.interface = InterfaceController(adb_controller, image_handler)

        # Обработчик OCR
        self.ocr = OCRHandler(adb_controller)

        # Селектор серверов
        self.server_selector = OptimizedServerSelector(adb_controller, self.ocr.ocr_available)

        # Исполнитель обучения
        self.tutorial_executor = TutorialExecutor(
            self.interface,
            self.ocr,
            self.server_selector
        )

        self.logger.info("✅ Все компоненты бота инициализированы успешно")

    # Основные методы управления игрой

    def start_game(self) -> None:
        """Запуск игры."""
        self.logger.info("🎮 Запуск игры...")
        self.interface.start_app()

    def stop_game(self) -> None:
        """Остановка игры."""
        self.logger.info("⏹️  Остановка игры...")
        self.interface.stop_app()

    # Основные методы выполнения обучения

    def perform_tutorial(self, server_id: int, start_step: int = 1) -> bool:
        """
        Выполнение обучения на сервере.

        Args:
            server_id: номер сервера
            start_step: начальный шаг

        Returns:
            bool: успех выполнения
        """
        self.logger.info(f"📚 Начало обучения на сервере {server_id} с шага {start_step}")
        return self.tutorial_executor.execute_tutorial(server_id, start_step)

    def run_bot(self, cycles: int = 1, start_server: int = 619,
                end_server: int = 1, first_server_start_step: int = 1) -> int:
        """
        Запуск бота на выполнение циклов обучения.

        Args:
            cycles: количество циклов (повторений всего диапазона серверов)
            start_server: начальный сервер
            end_server: конечный сервер
            first_server_start_step: начальный шаг для первого сервера

        Returns:
            int: количество успешно выполненных циклов
        """
        self.logger.info(f"🚀 Запуск бота: {cycles} циклов, сервера {start_server}-{end_server}")

        # Валидация параметров
        if start_server < end_server:
            self.logger.error("❌ Начальный сервер должен быть больше конечного")
            return 0

        # Подготовка к выполнению
        successful_cycles = 0
        servers_in_range = start_server - end_server + 1
        total_servers_to_process = servers_in_range * cycles

        self.logger.info(f"📋 Всего серверов в диапазоне: {servers_in_range}")
        self.logger.info(f"📋 Всего будет обработано: {total_servers_to_process} серверов")

        # Основной цикл выполнения
        total_count = 0
        for cycle in range(1, cycles + 1):
            current_server = start_server  # Начинаем с верхней границы диапазона в каждом цикле

            self.logger.info(f"🔄 Начало цикла {cycle}/{cycles}")

            # Проходим по всем серверам в текущем цикле
            while current_server >= end_server:
                total_count += 1
                cycle_start_time = time.time()
                self.logger.info(
                    f"🔄 Обработка {total_count}/{total_servers_to_process}, сервер {current_server}, цикл {cycle}/{cycles}")

                try:
                    # Определяем начальный шаг (только для первого сервера в первом цикле используем custom шаг)
                    current_step = first_server_start_step if (cycle == 1 and current_server == start_server) else 1

                    self.logger.info(f"📍 Начальный шаг: {current_step}")

                    # Выполняем обучение
                    if self.perform_tutorial(current_server, start_step=current_step):
                        successful_cycles += 1
                        cycle_time = time.time() - cycle_start_time
                        self.logger.info(f"✅ Сервер {current_server} завершен успешно за {cycle_time:.1f}с")
                    else:
                        self.logger.error(f"❌ Ошибка на сервере {current_server}")

                    # Переход к следующему серверу
                    current_server -= 1

                    # Пауза между серверами для стабильности
                    if current_server >= end_server:
                        self.logger.info(f"⏳ Пауза {DEFAULT_TIMEOUT * 2}с между серверами...")
                        time.sleep(DEFAULT_TIMEOUT * 2)

                except Exception as e:
                    self.logger.error(f"💥 Критическая ошибка на сервере {current_server}: {e}", exc_info=True)
                    current_server -= 1  # Переходим к следующему серверу даже при ошибке

            # Пауза между циклами
            if cycle < cycles:
                self.logger.info(f"⏳ Пауза {DEFAULT_TIMEOUT * 4}с между циклами...")
                time.sleep(DEFAULT_TIMEOUT * 4)

        # Итоговая статистика
        success_rate = (successful_cycles / total_servers_to_process) * 100 if total_servers_to_process > 0 else 0
        self.logger.info(f"📊 Итог: {successful_cycles}/{total_servers_to_process} серверов ({success_rate:.1f}%)")

        return successful_cycles

    # Методы для тестирования и отладки

    def test_server_selection(self, server_id: int) -> bool:
        """
        Тестирование выбора сервера.

        Args:
            server_id: номер сервера для тестирования

        Returns:
            bool: успех выбора сервера
        """
        self.logger.info(f"🧪 Тестирование выбора сервера {server_id}")

        # Определяем сезон для сервера
        season_id = self.tutorial_executor._determine_season_for_server(server_id)
        if not season_id:
            self.logger.error(f"❌ Сезон для сервера {server_id} не найден")
            return False

        self.logger.info(f"📡 Сервер {server_id} принадлежит сезону {season_id}")

        # Выбираем сезон
        if not self.server_selector.select_season(season_id):
            self.logger.error(f"❌ Не удалось выбрать сезон {season_id}")
            return False

        # Ищем сервер
        coords = self.server_selector.find_server_coordinates(server_id)
        if coords:
            self.logger.info(f"✅ Сервер {server_id} найден на координатах {coords}")
            return True
        else:
            self.logger.warning(f"⚠️  Сервер {server_id} не найден без скроллинга")

            # Попробуем с более агрессивным поиском
            self.logger.info("🔍 Пробуем поиск со скроллингом...")
            return self.tutorial_executor._find_and_click_server(server_id)

    def test_skip_button_search(self) -> bool:
        """
        Тестирование поиска кнопки ПРОПУСТИТЬ.

        Returns:
            bool: успех поиска кнопки
        """
        self.logger.info("🧪 Тестирование поиска кнопки ПРОПУСТИТЬ")
        return self.tutorial_executor.skip_finder.find_skip_button_with_timeout(timeout=10)

    def test_ocr_capability(self) -> str:
        """
        Тестирование возможностей OCR.

        Returns:
            str: статус OCR
        """
        if self.ocr.ocr_available:
            self.logger.info("✅ OCR доступен и готов к использованию")
            return "OCR доступен"
        else:
            self.logger.warning("⚠️  OCR недоступен")
            return "OCR недоступен"

    def execute_single_step(self, step_number: int, server_id: int = None) -> bool:
        """
        Выполнение одного шага обучения для отладки.

        Args:
            step_number: номер шага
            server_id: номер сервера (для шага выбора сервера)

        Returns:
            bool: успех выполнения шага
        """
        step = self.tutorial_executor.tutorial_steps.get_step_by_number(step_number)
        if not step:
            self.logger.error(f"❌ Шаг {step_number} не найден")
            return False

        self.logger.info(f"🧪 Выполнение шага {step_number}: {step.description}")
        return self.tutorial_executor._execute_step(step, server_id)

    def get_current_screen_info(self) -> dict:
        """
        Получение информации о текущем экране для отладки.

        Returns:
            dict: информация об экране
        """
        self.logger.info("📊 Анализ текущего экрана...")

        info = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "screenshot_available": False,
            "screenshot_shape": None,
            "visible_servers": [],
            "ocr_available": self.ocr.ocr_available,
            "device_connected": True
        }

        # Проверяем доступность скриншота
        try:
            screenshot = self.adb.screenshot()
            if screenshot is not None and screenshot.size > 0:
                info["screenshot_available"] = True
                info["screenshot_shape"] = screenshot.shape
                self.logger.info(f"✅ Скриншот доступен: {screenshot.shape}")
            else:
                self.logger.warning("⚠️  Скриншот не доступен")
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения скриншота: {e}")
            info["device_connected"] = False

        # Пробуем получить видимые сервера
        try:
            servers = self.server_selector.get_servers_with_coordinates()
            info["visible_servers"] = list(servers.keys())
            if servers:
                self.logger.info(f"🎯 Найдено серверов на экране: {len(servers)}")
                self.logger.info(f"📋 Номера серверов: {sorted(servers.keys(), reverse=True)}")
            else:
                self.logger.info("📭 Сервера на экране не обнаружены")
        except Exception as e:
            self.logger.debug(f"🔍 Ошибка получения серверов: {e}")

        # Тестируем OCR
        if self.ocr.ocr_available:
            try:
                from config.settings import OCR_REGIONS
                test_region = OCR_REGIONS['skip_button']
                test_text = self.ocr.get_text_from_region(test_region)
                info["ocr_test_result"] = test_text.strip() if test_text else "Текст не распознан"
                self.logger.info(f"📝 OCR тест: {len(test_text)} символов распознано")
            except Exception as e:
                self.logger.debug(f"📝 Ошибка тестирования OCR: {e}")
                info["ocr_test_result"] = f"Ошибка: {e}"

        return info

    # Вспомогательные методы

    def get_bot_status(self) -> dict:
        """
        Получение статуса всех компонентов бота.

        Returns:
            dict: статус компонентов
        """
        return {
            "adb_controller": self.adb is not None,
            "image_handler": self.image is not None,
            "interface_controller": self.interface is not None,
            "ocr_handler": self.ocr is not None and self.ocr.ocr_available,
            "server_selector": self.server_selector is not None,
            "tutorial_executor": self.tutorial_executor is not None
        }

    def __str__(self) -> str:
        """Строковое представление бота."""
        return f"OptimizedGameBot(device={getattr(self.adb, 'device_serial', 'Unknown')})"

    def __repr__(self) -> str:
        """Подробное представление бота."""
        status = self.get_bot_status()
        active_components = sum(status.values())
        total_components = len(status)
        return f"OptimizedGameBot({active_components}/{total_components} компонентов активны)"