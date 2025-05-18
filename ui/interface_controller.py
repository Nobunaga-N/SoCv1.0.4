"""
Базовый контроллер интерфейса - содержит основные методы взаимодействия с UI.
"""
import time
import logging
from typing import Optional, Tuple


class InterfaceController:
    """Базовый класс для взаимодействия с интерфейсом игры."""

    def __init__(self, adb_controller, image_handler):
        """
        Инициализация контроллера интерфейса.

        Args:
            adb_controller: контроллер ADB
            image_handler: обработчик изображений
        """
        self.logger = logging.getLogger('sea_conquest_bot.interface')
        self.adb = adb_controller
        self.image = image_handler

    def click_coord(self, x: int, y: int) -> None:
        """
        Клик по координатам.

        Args:
            x: координата x
            y: координата y
        """
        self.logger.debug(f"Клик по координатам ({x}, {y})")
        self.adb.tap(x, y)

    def click_coord_with_delay(self, x: int, y: int, delay: float = 0.0) -> None:
        """
        Клик по координатам с задержкой.

        Args:
            x: координата x
            y: координата y
            delay: задержка перед кликом в секундах
        """
        if delay > 0:
            self.logger.debug(f"Ожидание {delay} сек перед кликом по ({x}, {y})")
            time.sleep(delay)
        self.click_coord(x, y)

    def click_image(self, image_key: str, timeout: int = 30) -> bool:
        """
        Поиск и клик по изображению.

        Args:
            image_key: ключ изображения в IMAGE_PATHS
            timeout: таймаут поиска

        Returns:
            bool: True если изображение найдено и клик выполнен
        """
        from config import IMAGE_PATHS

        if image_key not in IMAGE_PATHS:
            self.logger.error(f"Изображение '{image_key}' не найдено в конфигурации")
            return False

        return self.image.tap_on_template(IMAGE_PATHS[image_key], timeout)

    def wait_for_image(self, image_key: str, timeout: int = 30) -> Optional[Tuple[int, int, int, int]]:
        """
        Ожидание появления изображения.

        Args:
            image_key: ключ изображения
            timeout: таймаут ожидания

        Returns:
            tuple: координаты найденного изображения или None
        """
        from config import IMAGE_PATHS

        if image_key not in IMAGE_PATHS:
            self.logger.error(f"Изображение '{image_key}' не найдено в конфигурации")
            return None

        return self.image.wait_for_template(IMAGE_PATHS[image_key], timeout)

    def click_with_image_check(self, image_key: str, x: int, y: int,
                               image_timeout: int = 15, click_delay: float = 0.0) -> bool:
        """
        Комбинированный метод: ждет изображение и выполняет клик по координатам.

        Args:
            image_key: ключ изображения для ожидания
            x: координата x для клика
            y: координата y для клика
            image_timeout: таймаут ожидания изображения
            click_delay: задержка перед кликом

        Returns:
            bool: True если изображение найдено
        """
        if self.wait_for_image(image_key, timeout=image_timeout):
            self.logger.info(f"Изображение {image_key} найдено, выполняем клик по ({x}, {y})")
            self.click_coord_with_delay(x, y, click_delay)
            return True
        else:
            self.logger.warning(f"Изображение {image_key} не найдено, выполняем клик по координатам")
            self.click_coord_with_delay(x, y, click_delay)
            return False

    def perform_swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
                      duration: int = 1000) -> None:
        """
        Выполнение свайпа.

        Args:
            start_x: начальная координата x
            start_y: начальная координата y
            end_x: конечная координата x
            end_y: конечная координата y
            duration: продолжительность свайпа в миллисекундах
        """
        self.logger.debug(f"Свайп от ({start_x}, {start_y}) к ({end_x}, {end_y})")
        self.adb.swipe(start_x, start_y, end_x, end_y, duration)

    def press_back(self) -> None:
        """Нажатие кнопки назад."""
        self.logger.debug("Нажатие кнопки назад")
        self.adb.press_esc()

    def start_app(self) -> None:
        """Запуск игры."""
        from config import GAME_PACKAGE, GAME_ACTIVITY, LOADING_TIMEOUT

        self.logger.info("Запуск игры")
        self.adb.start_app(GAME_PACKAGE, GAME_ACTIVITY)
        time.sleep(LOADING_TIMEOUT)

    def stop_app(self) -> None:
        """Остановка игры."""
        from config import GAME_PACKAGE

        self.logger.info("Остановка игры")
        self.adb.stop_app(GAME_PACKAGE)