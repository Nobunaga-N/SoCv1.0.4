"""
Исполнитель обучения - выполняет шаги согласно их конфигурации.
Обновленная версия с оптимизированным поисковиком кнопки ПРОПУСТИТЬ.
"""
import time
import logging
from typing import Dict, Any

from .tutorial_steps import TutorialSteps, TutorialStep
from .skip_button_finder import UltraFastSkipButtonFinder


class TutorialExecutor:
    """Класс для выполнения шагов обучения согласно их конфигурации."""

    def __init__(self, interface_controller, ocr_handler, server_selector, debug_mode=False):
        """
        Инициализация исполнителя обучения.

        Args:
            interface_controller: контроллер интерфейса
            ocr_handler: обработчик OCR
            server_selector: селектор серверов
            debug_mode: режим отладки для сохранения изображений
        """
        self.logger = logging.getLogger('sea_conquest_bot.tutorial_executor')
        self.interface = interface_controller
        self.ocr = ocr_handler
        self.server_selector = server_selector
        self.skip_finder = UltraFastSkipButtonFinder(
            interface_controller.adb,
            interface_controller,
            debug_mode=debug_mode
        )
        self.tutorial_steps = TutorialSteps()

        # Валидация шагов при инициализации
        if not self.tutorial_steps.validate_steps():
            self.logger.warning("Обнаружены проблемы в конфигурации шагов")

    def execute_tutorial(self, server_id: int, start_step: int = 1) -> bool:
        """
        Выполнение обучения на сервере.

        Args:
            server_id: номер сервера
            start_step: начальный шаг

        Returns:
            bool: успех выполнения
        """
        self.logger.info(f"Начало обучения на сервере {server_id} с шага {start_step}")

        try:
            # Получаем шаги для выполнения
            steps_to_execute = self.tutorial_steps.get_steps_from_range(start_step, 97)

            for step in steps_to_execute:
                self.logger.info(f"Выполняем шаг {step.step_number}: {step.description}")

                # Выполняем шаг с передачей server_id для шага выбора сервера
                success = self._execute_step(step, server_id)

                if not success:
                    self.logger.error(f"Ошибка выполнения шага {step.step_number}")
                    return False

                self.logger.info(f"Шаг {step.step_number}: ВЫПОЛНЕН")

            self.logger.info(f"Обучение на сервере {server_id} завершено успешно")
            return True

        except Exception as e:
            self.logger.error(f"Критическая ошибка выполнения обучения: {e}", exc_info=True)
            return False

    def _execute_step(self, step: TutorialStep, server_id: int = None) -> bool:
        """
        Выполнение одного шага обучения.

        Args:
            step: шаг для выполнения
            server_id: номер сервера (для шага выбора сервера)

        Returns:
            bool: успех выполнения шага
        """
        try:
            # Проверяем условие выполнения шага, если оно есть
            if step.condition and not step.condition():
                self.logger.info(f"Условие для шага {step.step_number} не выполнено, пропускаем")
                return True

            # Выполняем шаг согласно его типу
            action_method = getattr(self, f'_action_{step.action_type}', None)
            if not action_method:
                self.logger.error(f"Неизвестный тип действия: {step.action_type}")
                return False

            # Добавляем server_id в параметры для действия выбора сервера
            params = step.params.copy()
            if step.action_type == 'select_server' and server_id:
                params['server_id'] = server_id

            return action_method(**params)

        except Exception as e:
            self.logger.error(f"Ошибка выполнения шага {step.step_number}: {e}", exc_info=True)
            return False

    # Методы действий для различных типов шагов

    def _action_click_coord(self, x: int, y: int, **kwargs) -> bool:
        """Клик по координатам."""
        self.interface.click_coord(x, y)
        return True

    def _action_click_coord_with_delay(self, x: int, y: int, delay: float = 0.0, **kwargs) -> bool:
        """Клик по координатам с задержкой."""
        self.interface.click_coord_with_delay(x, y, delay)
        return True

    def _action_click_coord_with_delay_and_wait(self, x: int, y: int, delay: float = 0.0,
                                                wait_after: float = 0.0, **kwargs) -> bool:
        """Клик по координатам с задержкой и ожиданием после."""
        self.interface.click_coord_with_delay(x, y, delay)
        if wait_after > 0:
            self.logger.info(f"Ожидание {wait_after} секунд после клика...")
            time.sleep(wait_after)
        return True

    def _action_select_server(self, server_id: int, **kwargs) -> bool:
        """Выбор сервера."""
        # Определяем сезон для сервера
        season_id = self._determine_season_for_server(server_id)
        if not season_id:
            self.logger.error(f"Сезон для сервера {server_id} не найден")
            return False

        # Выбираем сезон
        if not self.server_selector.select_season(season_id):
            return False

        # Ищем и выбираем сервер
        return self._find_and_click_server(server_id)

    def _action_find_skip_infinite(self, wait_after: float = 0.0, **kwargs) -> bool:
        """
        Бесконечный поиск кнопки ПРОПУСТИТЬ с оптимизированным алгоритмом.

        ВАЖНО: Этот метод НЕ завершается пока не найдет кнопку!
        Никаких fallback-ов на координаты!
        """
        self.logger.info("🔍 Поиск кнопки ПРОПУСТИТЬ (обязательный поиск)")

        success = self.skip_finder.find_skip_button_infinite()

        if success:
            self.logger.info("✅ ПРОПУСТИТЬ найден и нажат")
            if wait_after > 0:
                time.sleep(wait_after)
            return True
        else:
            # Этого не должно произойти при бесконечном поиске
            self.logger.error("❌ Критическая ошибка: бесконечный поиск завершился без результата")
            return False

    def _action_click_with_image_check(self, image_key: str, x: int, y: int,
                                       image_timeout: int = 15, click_delay: float = 0.0, **kwargs) -> bool:
        """Ожидание изображения и клик по координатам."""
        return self.interface.click_with_image_check(image_key, x, y, image_timeout, click_delay)

    def _action_click_with_image_check_and_wait(self, image_key: str, x: int, y: int,
                                                image_timeout: int = 15, wait_after: float = 0.0, **kwargs) -> bool:
        """Ожидание изображения, клик и ожидание после."""
        success = self.interface.click_with_image_check(image_key, x, y, image_timeout)
        if wait_after > 0:
            time.sleep(wait_after)
        return success

    def _action_wait_image_then_skip(self, image_key: str, image_timeout: int = 15, **kwargs) -> bool:
        """
        Ожидание изображения и затем ОБЯЗАТЕЛЬНЫЙ поиск кнопки ПРОПУСТИТЬ.

        ВАЖНО: Поиск ПРОПУСТИТЬ обязательный, без fallback-ов!
        """
        # Ждем изображение
        if self.interface.wait_for_image(image_key, timeout=image_timeout):
            self.logger.info(f"Изображение {image_key} найдено, запускаем поиск ПРОПУСТИТЬ")
        else:
            self.logger.warning(f"Изображение {image_key} не найдено, но запускаем поиск ПРОПУСТИТЬ")

        # ОБЯЗАТЕЛЬНЫЙ поиск ПРОПУСТИТЬ
        return self.skip_finder.find_skip_button_infinite()

    def _action_wait_for_battle_ready(self, image_key: str, max_attempts: int = 20, **kwargs) -> bool:
        """Ожидание готовности к битве."""
        for attempt in range(max_attempts):
            self.logger.debug(f"Попытка {attempt + 1}/{max_attempts} - ищем {image_key}")
            if self.interface.click_image(image_key, timeout=1):
                self.logger.info(f"{image_key} найден и нажат на попытке {attempt + 1}")
                return True
            self.logger.debug(f"{image_key} не найден, кликаем по центру экрана")
            self.interface.click_coord(642, 334)
            time.sleep(1.5)

        self.logger.warning(f"{image_key} не найден за {max_attempts} попыток")
        return True  # Продолжаем выполнение

    def _action_wait_for_ship(self, image_key: str, max_attempts: int = 20,
                              click_x: int = 93, click_y: int = 285, **kwargs) -> bool:
        """Ожидание корабля."""
        for attempt in range(max_attempts):
            self.logger.debug(f"Попытка {attempt + 1}/{max_attempts} - ищем {image_key}")
            if self.interface.wait_for_image(image_key, timeout=1):
                self.logger.info(f"{image_key} найден на попытке {attempt + 1}, кликаем по ({click_x}, {click_y})")
                self.interface.click_coord(click_x, click_y)
                return True
            self.logger.debug(f"{image_key} не найден, кликаем по центру экрана")
            self.interface.click_coord(642, 334)
            time.sleep(1.5)

        self.logger.warning(f"{image_key} не найден за {max_attempts} попыток, кликаем по квесту")
        self.interface.click_coord(click_x, click_y)
        return True  # Продолжаем выполнение

    def _action_find_and_click_text(self, text: str, region: tuple, timeout: int = 5,
                                    fallback_x: int = None, fallback_y: int = None, **kwargs) -> bool:
        """Поиск и клик по тексту с резервными координатами."""
        if not self.ocr.find_and_click_text(text, region, timeout):
            if fallback_x and fallback_y:
                self.logger.warning(f'Текст "{text}" не найден, кликаем по резервным координатам')
                self.interface.click_coord(fallback_x, fallback_y)
                return True
            return False
        return True

    def _action_click_image_or_coord(self, image_key: str, x: int, y: int, timeout: int = 25, **kwargs) -> bool:
        """Клик по изображению или координатам как резерв."""
        if self.interface.click_image(image_key, timeout=timeout):
            return True
        else:
            self.logger.warning(f"Изображение {image_key} не найдено, выполняем клик по координатам")
            self.interface.click_coord(x, y)
            return True

    def _action_wait_image_click_and_wait(self, image_key: str, x: int, y: int,
                                          wait_before: float = 0.0, image_timeout: int = 15,
                                          wait_after: float = 0.0, **kwargs) -> bool:
        """Ожидание, поиск изображения, клик и ожидание после."""
        if wait_before > 0:
            time.sleep(wait_before)

        if self.interface.wait_for_image(image_key, timeout=image_timeout):
            self.logger.info(f"Изображение {image_key} найдено, выполняем клик по ({x}, {y})")
            self.interface.click_coord(x, y)
        else:
            self.logger.warning(f"Изображение {image_key} не найдено, выполняем клик по координатам")
            self.interface.click_coord(x, y)

        if wait_after > 0:
            time.sleep(wait_after)
        return True

    def _action_final_quest_activation(self, x: int, y: int, wait_before: float = 6,
                                       skip_timeout: int = 5, wait_after_skip: float = 4, **kwargs) -> bool:
        """
        Финальная активация квеста с ОБЯЗАТЕЛЬНОЙ проверкой ПРОПУСТИТЬ.

        ВАЖНО: Если ПРОПУСТИТЬ найден, то он ОБЯЗАТЕЛЬНО будет нажат!
        """
        if wait_before > 0:
            time.sleep(wait_before)

        # Проверяем наличие кнопки ПРОПУСТИТЬ с ограниченным таймаутом
        if self.skip_finder.find_skip_button_with_timeout(timeout=skip_timeout):
            self.logger.info('✅ ПРОПУСТИТЬ найден и нажат, ждем перед активацией квеста')
            time.sleep(wait_after_skip)
            self.interface.click_coord(x, y)
            self.logger.info('Финальный квест активирован (после ПРОПУСТИТЬ)')
        else:
            self.logger.info('ПРОПУСТИТЬ не найден за отведенное время, сразу активируем финальный квест')
            self.interface.click_coord(x, y)
            self.logger.info('Финальный квест активирован (без ПРОПУСТИТЬ)')

        return True

    # Вспомогательные методы

    def _determine_season_for_server(self, server_id: int) -> str:
        """Определение сезона для сервера."""
        from config import SEASONS

        for season_id, season_data in SEASONS.items():
            if season_data['min_server'] >= server_id >= season_data['max_server']:
                return season_id
        return None

    def _find_and_click_server(self, server_id: int) -> bool:
        """Поиск и клик по серверу с улучшенной логикой."""
        # Попытка найти без скроллинга
        coords = self.server_selector.find_server_coordinates(server_id)
        if coords:
            self._click_server_at_coordinates(coords)
            return True

        # Если не найден, используем скроллинг
        return self._scroll_and_find_server(server_id)

    def _scroll_and_find_server(self, server_id: int) -> bool:
        """Скроллинг и поиск сервера."""
        self.logger.info(f"Поиск сервера {server_id} со скроллингом")

        # Получаем текущие видимые сервера
        current_servers = self.server_selector.get_servers_with_coordinates(force_refresh=True)
        if not current_servers:
            self.logger.warning("Не удалось получить список серверов")
            return False

        current_servers_list = list(current_servers.keys())

        # Быстрая проверка наличия сервера
        coords = self.server_selector.find_server_coordinates(server_id)
        if coords:
            self._click_server_at_coordinates(coords)
            return True

        # Проверяем, есть ли в видимой области ближайшие к целевому серверы
        # Если у нас уже видны сервера как выше, так и ниже целевого - выбираем сразу
        if current_servers_list:
            min_server = min(current_servers_list)
            max_server = max(current_servers_list)

            if min_server < server_id < max_server:
                self.logger.info(
                    f"Сервер {server_id} не найден, но находится между видимыми серверами {min_server} и {max_server}")
                # Выбираем ближайший сервер НИЖЕ целевого
                lower_servers = [s for s in current_servers_list if s < server_id]
                if lower_servers:
                    closest_lower = max(lower_servers)  # Ближайший снизу
                    difference = server_id - closest_lower
                    self.logger.info(f"Выбираем ближайший сервер НИЖЕ: {closest_lower} (разница: {difference})")
                    coords = current_servers[closest_lower]
                    self._click_server_at_coordinates(coords)
                    return True

        # Основной цикл скроллинга - выполняем до 10 попыток, если не нашли ближайшие серверы
        max_attempts = 10
        for attempt in range(max_attempts):
            self.logger.info(f"Попытка скроллинга {attempt + 1}/{max_attempts}")

            # Определяем тип скроллинга
            scroll_result = self.server_selector.scroll_to_server_range(server_id, current_servers_list)

            if scroll_result == 'found':
                coords = self.server_selector.find_server_coordinates(server_id)
                if coords:
                    self._click_server_at_coordinates(coords)
                    return True

            # Получаем новый список серверов после скроллинга
            time.sleep(0.5)
            new_servers = self.server_selector.get_servers_with_coordinates(force_refresh=True)
            if new_servers:
                current_servers_list = list(new_servers.keys())

                # Проверяем, нашли ли целевой сервер
                if server_id in new_servers:
                    self.logger.info(f"Найден сервер {server_id} после скроллинга!")
                    coords = new_servers[server_id]
                    self._click_server_at_coordinates(coords)
                    return True

                # Проверяем, есть ли уже сервера по обе стороны от целевого
                min_server = min(current_servers_list)
                max_server = max(current_servers_list)

                if min_server < server_id < max_server:
                    self.logger.info(
                        f"После скроллинга найдены сервера по обе стороны от {server_id}: {min_server}-{max_server}")
                    # Выбираем ближайший сервер НИЖЕ целевого
                    lower_servers = [s for s in current_servers_list if s < server_id]
                    if lower_servers:
                        closest_lower = max(lower_servers)  # Ближайший снизу
                        difference = server_id - closest_lower
                        self.logger.info(f"Выбираем ближайший сервер НИЖЕ: {closest_lower} (разница: {difference})")
                        coords = new_servers[closest_lower]
                        self._click_server_at_coordinates(coords)
                        return True

            current_servers = new_servers

        # Если не удалось найти точный сервер, выбираем ближайший НИЖЕ
        if current_servers_list:
            # Ищем сервера с номерами НИЖЕ целевого
            lower_servers = [s for s in current_servers_list if s < server_id]

            if lower_servers:
                # Берем максимальный из серверов ниже целевого (т.е. ближайший)
                closest_lower = max(lower_servers)
                difference = server_id - closest_lower
                self.logger.info(f"Выбираем ближайший сервер НИЖЕ: {closest_lower} (разница: {difference})")
                final_servers = self.server_selector.get_servers_with_coordinates()
                if closest_lower in final_servers:
                    coords = final_servers[closest_lower]
                    self._click_server_at_coordinates(coords)
                    return True
            else:
                # Если серверов ниже нет, берем минимальный из доступных
                min_server = min(current_servers_list)
                difference = server_id - min_server
                self.logger.info(
                    f"Нет серверов ниже {server_id}, выбираем наименьший: {min_server} (разница: {difference})")
                final_servers = self.server_selector.get_servers_with_coordinates()
                if min_server in final_servers:
                    coords = final_servers[min_server]
                    self._click_server_at_coordinates(coords)
                    return True

        self.logger.error(f"Не удалось найти подходящий сервер для {server_id}")
        return False

    def _click_server_at_coordinates(self, coords: tuple) -> None:
        """Клик по серверу с паузами."""
        from config import PAUSE_SETTINGS

        time.sleep(PAUSE_SETTINGS['before_server_click'])
        self.interface.click_coord(coords[0], coords[1])
        time.sleep(PAUSE_SETTINGS['after_server_click'])

    def get_skip_finder_statistics(self) -> dict:
        """
        Получение статистики работы поисковика кнопки ПРОПУСТИТЬ.

        Returns:
            dict: статистика работы
        """
        return self.skip_finder.get_statistics()

    def reset_skip_finder_statistics(self):
        """Сброс статистики поисковика."""
        self.skip_finder.reset_statistics()
        self.logger.info("🔄 Статистика поисковика ПРОПУСТИТЬ сброшена")

    def enable_debug_mode(self):
        """Включение режима отладки для сохранения изображений."""
        self.skip_finder.debug_mode = True
        self.logger.info("🧪 Режим отладки поисковика ПРОПУСТИТЬ включен")

    def disable_debug_mode(self):
        """Отключение режима отладки."""
        self.skip_finder.debug_mode = False
        self.logger.info("Режим отладки поисковика ПРОПУСТИТЬ отключен")