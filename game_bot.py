"""
Главный класс бота - упрощенный и реорганизованный.
Теперь использует модульную архитектуру.
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
from utils.config import DEFAULT_TIMEOUT


class OptimizedGameBot:
    """Основной класс бота для прохождения обучения в игре Sea of Conquest."""

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
        self.logger.info("Инициализация компонентов бота...")

        # Контроллер интерфейса
        self.interface = InterfaceController(adb_controller, image_handler)

        # Обработчик OCR
        self.ocr = OCRHandler(adb_controller)

        # Селектор серверов
        self.server_selector = OptimizedServerSelector(adb_controller, self.ocr.ocr_available)

        # Исполнитель обучения
        self.tutorial_executor = TutorialExecutor(self.interface, self.ocr, self.server_selector)

        self.logger.info("Все компоненты бота инициализированы успешно")

    def start_game(self) -> None:
        """Запуск игры."""
        self.interface.start_app()

    def stop_game(self) -> None:
        """Остановка игры."""
        self.interface.stop_app()

    def perform_tutorial(self, server_id: int, start_step: int = 1) -> bool:
        """
        Выполнение обучения на сервере.

        Args:
            server_id: номер сервера
            start_step: начальный шаг

        Returns:
            bool: успех выполнения
        """
        return self.tutorial_executor.execute_tutorial(server_id, start_step)

    def run_bot(self, cycles: int = 1, start_server: int = 619,
                end_server: int = 1, first_server_start_step: int = 1) -> int:
        """
        Запуск бота на выполнение циклов обучения.

        Args:
            cycles: количество циклов
            start_server: начальный сервер
            end_server: конечный сервер
            first_server_start_step: начальный шаг для первого сервера

        Returns:
            int: количество успешно выполненных циклов
        """
        self.logger.info(f"Запуск бота: {cycles} циклов, сервера {start_server}-{end_server}")

        if start_server < end_server:
            self.logger.error("Начальный сервер должен быть больше конечного")
            return 0

        successful_cycles = 0
        current_server = start_server
        servers_to_process = min(cycles, start_server - end_server + 1)

        for cycle in range(1, servers_to_process + 1):
            self.logger.info(f"=== Цикл {cycle}/{servers_to_process}, сервер {current_server} ===")

            try:
                # Определяем начальный шаг
                current_step = first_server_start_step if cycle == 1 else 1

                # Выполняем обучение
                if self.perform_tutorial(current_server, start_step=current_step):
                    successful_cycles += 1
                    self.logger.info(f"Цикл {cycle} завершен успешно")
                else:
                    self.logger.error(f"Ошибка в цикле {cycle}")

                # Переход к следующему серверу
                if cycle < servers_to_process:
                    current_server -= 1
                    if current_server < end_server:
                        break
                    # Пауза между циклами
                    time.sleep(DEFAULT_TIMEOUT * 4)

            except Exception as e:
                self.logger.error(f"Критическая ошибка в цикле {cycle}: {e}", exc_info=True)

        self.logger.info(f"Завершено {successful_cycles}/{servers_to_process} циклов")
        return successful_cycles

    # Дополнительные удобные методы для отладки и тестирования

    def test_server_selection(self, server_id: int) -> bool:
        """
        Тестирование выбора сервера.

        Args:
            server_id: номер сервера для тестирования

        Returns:
            bool: успех выбора сервера
        """
        self.logger.info(f"Тестирование выбора сервера {server_id}")

        # Определяем сезон для сервера
        season_id = self.tutorial_executor._determine_season_for_server(server_id)
        if not season_id:
            self.logger.error(f"Сезон для сервера {server_id} не найден")
            return False

        # Выбираем сезон
        if not self.server_selector.select_season(season_id):
            self.logger.error(f"Не удалось выбрать сезон {season_id}")
            return False

        # Ищем сервер
        coords = self.server_selector.find_server_coordinates(server_id)
        if coords:
            self.logger.info(f"Сервер {server_id} найден на координатах {coords}")
            return True
        else:
            self.logger.warning(f"Сервер {server_id} не найден без скроллинга")
            return False

    def test_skip_button_search(self) -> bool:
        """
        Тестирование поиска кнопки ПРОПУСТИТЬ.

        Returns:
            bool: успех поиска кнопки
        """
        self.logger.info("Тестирование поиска кнопки ПРОПУСТИТЬ")
        return self.tutorial_executor.skip_finder.find_skip_button_with_timeout(timeout=10)

    def test_ocr_capability(self) -> str:
        """
        Тестирование возможностей OCR.

        Returns:
            str: статус OCR
        """
        if self.ocr.ocr_available:
            self.logger.info("OCR доступен и готов к использованию")
            return "OCR доступен"
        else:
            self.logger.warning("OCR недоступен")
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
            self.logger.error(f"Шаг {step_number} не найден")
            return False

        self.logger.info(f"Выполнение отдельного шага {step_number}: {step.description}")
        return self.tutorial_executor._execute_step(step, server_id)

    def get_current_screen_info(self) -> dict:
        """
        Получение информации о текущем экране для отладки.

        Returns:
            dict: информация об экране
        """
        info = {
            "screenshot_available": False,
            "visible_servers": [],
            "ocr_available": self.ocr.ocr_available
        }

        # Проверяем доступность скриншота
        screenshot = self.adb.screenshot()
        if screenshot is not None and screenshot.size > 0:
            info["screenshot_available"] = True
            info["screenshot_shape"] = screenshot.shape

        # Пробуем получить видимые сервера
        try:
            servers = self.server_selector.get_servers_with_coordinates()
            info["visible_servers"] = list(servers.keys())
        except Exception as e:
            self.logger.debug(f"Ошибка получения серверов: {e}")

        return info