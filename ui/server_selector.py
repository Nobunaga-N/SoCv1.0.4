"""
Оптимизированный модуль для выбора серверов с улучшенным OCR и логикой скроллинга.
Исправления: точный скроллинг, лучшая фильтрация OCR, адаптивный поиск.
Добавлено: динамическое определение сезонов через OCR и интеллектуальный скроллинг для сезонов.
"""
import cv2
import numpy as np
import re
import logging
import time
from typing import Optional, List, Tuple, Dict
from pathlib import Path

from config import SEASONS, COORDINATES, PAUSE_SETTINGS, OCR_REGIONS, SERVER_RECOGNITION_SETTINGS


class OptimizedServerSelector:
    """
    Оптимизированный класс для выбора серверов с точным определением координат.
    """

    def __init__(self, adb_controller, ocr_available=True, debug_mode=True):
        """
        Инициализация селектора серверов.

        Args:
            adb_controller: контроллер ADB
            ocr_available: доступность OCR
            debug_mode: режим отладки для сохранения изображений
        """
        self.logger = logging.getLogger('sea_conquest_bot.server_selector')
        self.adb = adb_controller
        self.ocr_available = ocr_available
        self.debug_mode = debug_mode
        self.last_servers = []  # История последних найденных серверов для отслеживания движения
        self.current_season = None  # Текущий выбранный сезон
        self.cached_servers = {}  # Кеш для результатов OCR серверов
        self.cached_seasons = {}  # Кеш для результатов OCR сезонов
        self.last_screenshot_time = 0  # Время последнего скриншота
        self.last_seasons_screenshot_time = 0  # Время последнего скриншота сезонов
        self.cache_timeout = 1.0  # Таймаут кеша в секундах

        # Создаем директорию для отладочных скриншотов
        if self.debug_mode:
            self.debug_dir = Path("debug_seasons")
            self.debug_dir.mkdir(exist_ok=True)
            self.logger.info(f"Режим отладки включен. Скриншоты будут сохраняться в: {self.debug_dir}")

    #
    # ОСНОВНЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С СЕЗОНАМИ
    #

    def select_season(self, season_id: str) -> bool:
        """
        Выбор сезона с динамическим определением координат и интеллектуальным скроллингом.

        Args:
            season_id: идентификатор сезона (S1, S2, S3, S4, S5, X1, X2, X3, X4)

        Returns:
            bool: True если сезон выбран успешно
        """
        self.logger.info(f"Выбор сезона: {season_id}")

        if season_id not in SEASONS:
            self.logger.error(f"Неизвестный сезон: {season_id}")
            return False

        # Сохраняем текущий сезон для валидации
        self.current_season = season_id
        self.cached_servers = {}  # Очищаем кеш при смене сезона

        # Создаем снимок экрана для целей отладки
        if self.debug_mode:
            screenshot = self.adb.screenshot()
            if screenshot is not None:
                self._save_debug_image(screenshot, f"season_selection_{season_id}_start.png")

        # Получаем видимые сезоны
        visible_seasons = self.get_seasons_with_coordinates(force_refresh=True)
        if not visible_seasons:
            self.logger.warning("Не удалось определить видимые сезоны на экране")
            # Пробуем получить с более широкими параметрами поиска
            visible_seasons = self._emergency_season_scan()

            if not visible_seasons:
                self.logger.warning("Экстренное сканирование сезонов также не дало результатов")
                # Пробуем использовать резервный метод с предустановленными координатами
                return self._legacy_click_season(season_id)

        # Проверяем, видим ли нужный сезон
        if season_id in visible_seasons:
            self.logger.info(f"Сезон {season_id} найден на экране")
            x, y = visible_seasons[season_id]

            # Сохраняем скриншот с выделенным сезоном для отладки
            if self.debug_mode:
                screenshot = self.adb.screenshot()
                if screenshot is not None:
                    self._visualize_season_click(screenshot, x, y, f"season_click_{season_id}.png")

            time.sleep(PAUSE_SETTINGS['before_season_click'])
            self.adb.tap(x, y)
            time.sleep(PAUSE_SETTINGS['after_season_click'])
            return True

        # Если сезон не виден, пробуем скроллинг
        return self._scroll_and_find_season(season_id)

    def get_seasons_with_coordinates(self, force_refresh=False) -> Dict[str, Tuple[int, int]]:
        """
        Получение видимых сезонов с точными координатами через OCR.

        Args:
            force_refresh: принудительно обновить кеш

        Returns:
            dict: словарь {season_id: (click_x, click_y)}
        """
        current_time = time.time()

        # Проверяем кеш
        if not force_refresh and current_time - self.last_seasons_screenshot_time < self.cache_timeout:
            if self.cached_seasons:
                return self.cached_seasons

        if not self.ocr_available:
            self.logger.warning("OCR не доступен для определения сезонов")
            return {}

        try:
            import pytesseract

            screenshot = self.adb.screenshot()
            if screenshot is None or screenshot.size == 0:
                self.logger.warning("Получен пустой скриншот при поиске сезонов")
                return {}

            # Сохраняем полный скриншот для отладки
            if self.debug_mode:
                self._save_debug_image(screenshot, "full_screenshot.png")

            # Определяем область поиска сезонов
            # По умолчанию берем из OCR_REGIONS, но можно настроить и отдельный регион для сезонов
            if 'seasons' in OCR_REGIONS:
                x, y, w, h = OCR_REGIONS['seasons']
            else:
                # Предполагаемый регион для сезонов, если не указан явно
                x, y, w, h = 0, 200, 1280, 300  # Пример региона, нужно настроить под конкретное положение

            roi = screenshot[y:y + h, x:x + w]

            # Сохраняем регион интереса для отладки
            if self.debug_mode:
                self._save_debug_image(roi, "seasons_roi.png")

            # Обработка изображения для OCR
            seasons_with_coords = {}
            processed_images = self._preprocess_image_for_seasons(roi, w, h)

            for method_name, img, scale in processed_images:
                # Сохраняем обработанное изображение для отладки
                if self.debug_mode:
                    self._save_debug_image(img, f"seasons_processed_{method_name}.png")

                # OCR анализ
                data = pytesseract.image_to_data(
                    img, output_type=pytesseract.Output.DICT,
                    lang='rus+eng', config='--psm 11 --oem 3'  # PSM 11 для распознавания отдельных слов/сезонов
                )

                # Сохраняем результаты OCR для отладки
                if self.debug_mode:
                    self._save_ocr_results(data, f"seasons_ocr_{method_name}.txt")

                # Поиск сезонов
                self._extract_seasons_from_ocr_data(data, seasons_with_coords, x, y, scale)

            # Фильтрация и проверка результатов
            validated_seasons = self._validate_seasons(seasons_with_coords)

            # Обновляем кеш и время
            self.cached_seasons = validated_seasons
            self.last_seasons_screenshot_time = current_time

            if validated_seasons:
                self.logger.info(f"Найдены сезоны: {list(validated_seasons.keys())}")
                # Сохраняем визуализацию найденных сезонов для отладки
                if self.debug_mode:
                    self._visualize_seasons(screenshot, validated_seasons, "seasons_found.png")
            else:
                self.logger.warning("Не найдено сезонов на экране")

            return validated_seasons

        except Exception as e:
            self.logger.error(f"Ошибка получения координат сезонов: {e}", exc_info=True)
            return {}

    #
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С СЕЗОНАМИ
    #

    def _legacy_click_season(self, season_id: str) -> bool:
        """
        Резервный метод выбора сезона по предустановленным координатам.

        Args:
            season_id: идентификатор сезона

        Returns:
            bool: True если сезон выбран успешно
        """
        self.logger.warning(f"Используем резервный метод выбора сезона {season_id} по предустановленным координатам")

        # Проверяем, нужен ли скроллинг для нижних сезонов
        if season_id in ['X2', 'X3', 'X4']:
            self._scroll_to_lower_seasons()

        # Получаем координаты сезона
        season_coords = COORDINATES['seasons']
        if season_id not in season_coords:
            self.logger.error(f"Координаты для сезона {season_id} не найдены")
            return False

        x, y = season_coords[season_id]
        time.sleep(PAUSE_SETTINGS['before_season_click'])
        self.adb.tap(x, y)
        time.sleep(PAUSE_SETTINGS['after_season_click'])
        return True

    def _scroll_and_find_season(self, season_id: str) -> bool:
        """
        Скроллинг и поиск сезона.

        Args:
            season_id: идентификатор сезона

        Returns:
            bool: True если сезон найден и выбран успешно
        """
        self.logger.info(f"Скроллинг для поиска сезона {season_id}")

        max_attempts = 3  # Максимальное количество попыток скроллинга
        for attempt in range(max_attempts):
            self.logger.info(f"Попытка скроллинга {attempt + 1}/{max_attempts}")

            # Скроллим вниз для поиска сезона
            self._scroll_seasons_down()
            time.sleep(PAUSE_SETTINGS['after_season_scroll'])

            # Получаем обновленный список сезонов
            visible_seasons = self.get_seasons_with_coordinates(force_refresh=True)

            # Добавить детальное логирование
            season_coords = ", ".join([f"{s}:({x},{y})" for s, (x, y) in visible_seasons.items()])
            self.logger.info(f"Видимые сезоны и их координаты: {season_coords}")

            if season_id in visible_seasons:
                self.logger.info(f"Сезон {season_id} найден после скроллинга!")
                x, y = visible_seasons[season_id]
                time.sleep(PAUSE_SETTINGS['before_season_click'])
                self.adb.tap(x, y)
                time.sleep(PAUSE_SETTINGS['after_season_click'])
                return True

        # Если не нашли после нескольких попыток, используем резервный метод
        self.logger.warning(f"Не удалось найти сезон {season_id} после {max_attempts} попыток скроллинга, используем резервный метод")
        return self._legacy_click_season(season_id)

    def _scroll_seasons_down(self):
        """Скроллинг вниз для отображения нижних сезонов."""
        self.logger.info("Скроллинг вниз для отображения дополнительных сезонов")

        # Используем координаты из конфигурации
        start_x, start_y = COORDINATES['season_scroll_start']
        end_x, end_y = COORDINATES['season_scroll_end']

        self.adb.swipe(start_x, start_y, end_x, end_y, duration=1000)

    def _scroll_seasons_up(self):
        """Скроллинг вверх для отображения верхних сезонов."""
        self.logger.info("Скроллинг вверх для отображения верхних сезонов")

        # Используем обратные координаты для скроллинга вверх
        start_x, start_y = COORDINATES['season_scroll_end']
        end_x, end_y = COORDINATES['season_scroll_start']

        self.adb.swipe(start_x, start_y, end_x, end_y, duration=1000)

    def _scroll_to_lower_seasons(self):
        """Скроллинг для показа нижних сезонов (устаревший метод)."""
        self.logger.info("Скроллинг для отображения нижних сезонов (устаревший метод)")

        start_x, start_y = COORDINATES['season_scroll_start']
        end_x, end_y = COORDINATES['season_scroll_end']

        self.adb.swipe(start_x, start_y, end_x, end_y, duration=1000)
        time.sleep(PAUSE_SETTINGS['after_season_scroll'])

    def _preprocess_image_for_seasons(self, roi, w, h) -> List[Tuple[str, np.ndarray, int]]:
        """
        Предобработка изображения для OCR сезонов.

        Args:
            roi: область интереса изображения
            w: ширина области
            h: высота области

        Returns:
            List: список кортежей (название_метода, обработанное_изображение, масштаб)
        """
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        processed = []

        # Сохраняем серое изображение для отладки
        if self.debug_mode:
            self._save_debug_image(gray, "seasons_gray.png")

        # Стандартная бинаризация
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        processed.append(("binary", binary, 1))

        # Адаптивная бинаризация
        binary_adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        processed.append(("adaptive", binary_adaptive, 1))

        # Увеличенное изображение
        scale_factor = 2
        resized = cv2.resize(gray, (w * scale_factor, h * scale_factor),
                           interpolation=cv2.INTER_CUBIC)
        _, binary_resized = cv2.threshold(resized, 150, 255, cv2.THRESH_BINARY_INV)
        processed.append(("resized", binary_resized, scale_factor))

        # Экспериментальные методы обработки
        # 1. Гауссово размытие + адаптивная бинаризация
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        binary_blurred = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        processed.append(("blurred_adaptive", binary_blurred, 1))

        # 2. Морфологические операции
        kernel = np.ones((2, 2), np.uint8)
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated = cv2.dilate(eroded, kernel, iterations=1)
        processed.append(("morphology", dilated, 1))

        # 3. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(gray)
        _, binary_clahe = cv2.threshold(clahe_img, 150, 255, cv2.THRESH_BINARY_INV)
        processed.append(("clahe", binary_clahe, 1))

        return processed

    def _extract_seasons_from_ocr_data(self, data, seasons_dict, offset_x, offset_y, scale):
        """
        Извлечение сезонов из данных OCR.

        Args:
            data: данные OCR от pytesseract
            seasons_dict: словарь для заполнения найденными сезонами
            offset_x: смещение по X
            offset_y: смещение по Y
            scale: масштаб изображения
        """
        if self.debug_mode:
            debug_info = []

        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            confidence = int(data['conf'][i])

            # Если включен отладочный режим, сохраняем все распознанные тексты
            if self.debug_mode and text and confidence > 0:
                x = data['left'][i] // scale
                y = data['top'][i] // scale
                w = data['width'][i] // scale
                h = data['height'][i] // scale
                debug_info.append(f"Text: '{text}', Conf: {confidence}, Pos: ({x+offset_x}, {y+offset_y}, {w}, {h})")

            # Фильтр по уверенности OCR
            if confidence < 30:  # Снижаем минимальный порог уверенности для сезонов
                continue

            # Ищем сезоны в тексте
            season_ids = self._parse_season_ids(text)

            for season_id in season_ids:
                if season_id in SEASONS and season_id not in seasons_dict:
                    # Вычисляем координаты центра текста
                    text_x = data['left'][i] // scale
                    text_y = data['top'][i] // scale
                    text_w = data['width'][i] // scale
                    text_h = data['height'][i] // scale

                    abs_x = offset_x + text_x + text_w // 2
                    abs_y = offset_y + text_y + text_h // 2

                    seasons_dict[season_id] = (abs_x, abs_y)

                    if self.debug_mode:
                        debug_info.append(f"FOUND SEASON: '{season_id}' from text '{text}', Conf: {confidence}, Coords: ({abs_x}, {abs_y})")

        # Сохраняем отладочную информацию
        if self.debug_mode and debug_info:
            self._save_text_file("\n".join(debug_info), "seasons_extracted_debug.txt")

    def _parse_season_ids(self, text: str) -> List[str]:
        """Улучшенный парсинг идентификаторов сезонов из текста"""
        if not text:
            return []

        # Логируем входной текст для отладки
        if self.debug_mode:
            self.logger.debug(f"Парсинг сезона из текста: '{text}'")

        # Проверка на прямое совпадение для коротких текстов
        normalized_text = text.upper().strip()

        # Набор известных сезонов
        known_seasons = ["S1", "S2", "S3", "S4", "S5", "X1", "X2", "X3", "X4"]

        # Замены похожих символов
        normalized_text = normalized_text.replace('С', 'S')  # Кириллическая С → S
        normalized_text = normalized_text.replace('Х', 'X')  # Кириллическая Х → X
        normalized_text = normalized_text.replace('с', 'S')  # Кириллическая с → S
        normalized_text = normalized_text.replace('х', 'X')  # Кириллическая х → X

        # Явная проверка на сезоны
        for season in known_seasons:
            # Проверка для S сезонов
            if season.startswith('S') and season in normalized_text:
                if self.debug_mode:
                    self.logger.debug(f"Найден точный сезон S: '{text}' → '{season}'")
                return [season]

            # Специальные проверки для X сезонов, которые часто путаются
            if season.startswith('X'):
                # Различные варианты написания X
                patterns = ['X', 'Х', '×', 'x', 'х']
                digit = season[1]

                for pattern in patterns:
                    if f"{pattern}{digit}" in normalized_text:
                        correct_season = f"X{digit}"
                        if self.debug_mode:
                            self.logger.debug(f"Найден X сезон: '{text}' → '{correct_season}'")
                        return [correct_season]

        # Если до сих пор не нашли сезон, пробуем искать по цифрам
        # Есть риск путаницы из-за номеров серверов, поэтому оставляем как запасной вариант
        for digit in "12345":
            if digit in normalized_text:
                # Определяем тип сезона по наличию признаков X или S
                if any(x_char in normalized_text for x_char in ['X', 'Х', '×', 'x', 'х']):
                    season_id = f"X{digit}"
                else:
                    season_id = f"S{digit}"

                if season_id in known_seasons:
                    if self.debug_mode:
                        self.logger.debug(f"Найден сезон по цифре: '{text}' → '{season_id}'")
                    return [season_id]

        return []

    def _check_missing_seasons(self, seasons_found: Dict[str, Tuple[int, int]]) -> None:
        """
        Проверяет, какие сезоны не были найдены, и логирует их.
        Можно использовать для отладки.
        """
        all_seasons = ["S1", "S2", "S3", "S4", "S5", "X1", "X2", "X3", "X4"]
        found_seasons = list(seasons_found.keys())
        missing_seasons = [s for s in all_seasons if s not in found_seasons]

        if missing_seasons:
            self.logger.debug(f"Не найдены следующие сезоны: {missing_seasons}")

        # Проверка на путаницу X и S
        xs_confusion = False
        for season in seasons_found:
            if season.startswith('S') and season.replace('S', 'X') in all_seasons and season.replace('S',
                                                                                                     'X') not in found_seasons:
                xs_confusion = True
                self.logger.debug(f"Возможная путаница: найден {season}, но не найден {season.replace('S', 'X')}")

        if xs_confusion:
            self.logger.warning("Обнаружена возможная путаница между буквами S и X")

    def _validate_seasons(self, seasons_dict: Dict[str, Tuple[int, int]]) -> Dict[str, Tuple[int, int]]:
        """
        Валидация найденных сезонов.

        Args:
            seasons_dict: словарь сезонов {season_id: (x, y)}

        Returns:
            Dict: валидированный словарь сезонов
        """
        validated = {}

        # Логируем полный список найденных сезонов
        if self.debug_mode:
            season_list = [f"{sid}: ({x}, {y})" for sid, (x, y) in seasons_dict.items()]
            self.logger.debug(f"Найдено {len(seasons_dict)} сезонов до валидации: {', '.join(season_list)}")

        for season_id, coords in seasons_dict.items():
            # Базовая проверка, что сезон существует в конфигурации
            if season_id not in SEASONS:
                self.logger.debug(f"Сезон {season_id} не найден в конфигурации SEASONS")
                continue

            # Проверка координат (что они в разумных пределах экрана)
            x, y = coords
            if not (0 <= x <= 1280 and 0 <= y <= 720):  # Предполагаемые размеры экрана
                self.logger.debug(f"Сезон {season_id} имеет недопустимые координаты ({x}, {y})")
                continue

            # Дополнительная проверка на Y-координату (обычно сезоны находятся в верхней половине экрана)
            if not (100 <= y <= 500):
                self.logger.debug(f"Сезон {season_id} вероятно найден неверно, Y-координата за пределами ожидаемого диапазона: {y}")
                # Не пропускаем, только логируем

            validated[season_id] = coords

        # Логируем результаты валидации
        if self.debug_mode:
            if validated:
                valid_seasons = [f"{sid}: ({x}, {y})" for sid, (x, y) in validated.items()]
                self.logger.debug(f"После валидации осталось {len(validated)} сезонов: {', '.join(valid_seasons)}")
            else:
                self.logger.debug("После валидации не осталось ни одного сезона")

        return validated

    def _emergency_season_scan(self) -> Dict[str, Tuple[int, int]]:
        """
        Экстренное сканирование сезонов с использованием более агрессивных параметров поиска.
        Вызывается, когда стандартный метод не находит сезоны.

        Returns:
            dict: словарь {season_id: (click_x, click_y)}
        """
        self.logger.info("Запуск экстренного сканирования сезонов")

        try:
            import pytesseract

            screenshot = self.adb.screenshot()
            if screenshot is None or screenshot.size == 0:
                self.logger.warning("Получен пустой скриншот при экстренном сканировании")
                return {}

            # Сохраняем скриншот для отладки
            if self.debug_mode:
                self._save_debug_image(screenshot, "emergency_scan_full.png")

            # Используем более широкую область для поиска сезонов
            # Сканируем почти весь экран
            x, y, w, h = 0, 0, 1280, 600
            roi = screenshot[y:y + h, x:x + w]

            # Сохраняем ROI для отладки
            if self.debug_mode:
                self._save_debug_image(roi, "emergency_scan_roi.png")

            # Используем PSM 3 (полная страница) и пониженный порог уверенности
            try:
                # Преобразуем в оттенки серого
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                # Сохраняем серое изображение
                if self.debug_mode:
                    self._save_debug_image(gray, "emergency_scan_gray.png")

                # Применяем несколько методов предобработки
                methods = [
                    # Стандартная бинаризация
                    cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1],
                    # Адаптивная бинаризация
                    cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2),
                    # Исходное изображение в оттенках серого
                    gray
                ]

                seasons_with_coords = {}

                for idx, img in enumerate(methods):
                    method_name = ["binary", "adaptive", "gray"][idx]

                    # Сохраняем обработанное изображение для отладки
                    if self.debug_mode:
                        self._save_debug_image(img, f"emergency_scan_{method_name}.png")

                    # Агрессивная конфигурация OCR
                    configs = [
                        '--psm 11 --oem 3',  # Отдельные слова
                        '--psm 3 --oem 3',   # Полная страница
                        '--psm 6 --oem 3'    # Единый блок текста
                    ]

                    for config in configs:
                        data = pytesseract.image_to_data(
                            img, output_type=pytesseract.Output.DICT,
                            lang='rus+eng', config=config
                        )

                        # Сохраняем результаты OCR для отладки
                        if self.debug_mode:
                            self._save_ocr_results(data, f"emergency_scan_{method_name}_{config.replace(' ', '_')}.txt")

                        # Извлечение сезонов с пониженным порогом уверенности
                        for i in range(len(data['text'])):
                            text = data['text'][i].strip()
                            confidence = int(data['conf'][i])

                            # Логируем все найденные тексты для отладки
                            if self.debug_mode and text and confidence > 10:
                                self.logger.debug(f"OCR текст: '{text}', уверенность: {confidence}")

                            # Пониженный порог уверенности для экстренного сканирования
                            if confidence < 20 or not text:
                                continue

                            # Ищем сезоны напрямую, используя прямые сравнения и шаблоны
                            clean_text = text.upper().replace(' ', '')

                            # Прямая проверка на S1-S5, X1-X4
                            for s_id in ["S1", "S2", "S3", "S4", "S5", "X1", "X2", "X3", "X4"]:
                                if s_id in clean_text or s_id.replace('S', 'С').replace('X', 'Х') in clean_text:
                                    # Кириллическая замена для проверки
                                    season_id = s_id
                                    # Вычисляем координаты центра текста
                                    text_x = data['left'][i]
                                    text_y = data['top'][i]
                                    text_w = data['width'][i]
                                    text_h = data['height'][i]

                                    abs_x = x + text_x + text_w // 2
                                    abs_y = y + text_y + text_h // 2

                                    if self.debug_mode:
                                        self.logger.info(f"Найден сезон в экстренном режиме: {season_id} из '{text}' (conf: {confidence}) на координатах ({abs_x}, {abs_y})")

                                    seasons_with_coords[season_id] = (abs_x, abs_y)
                                    break

                if self.debug_mode:
                    self.logger.info(f"Результаты экстренного сканирования: найдено {len(seasons_with_coords)} сезонов")

                # Валидация результатов
                return self._validate_seasons(seasons_with_coords)

            except Exception as e:
                self.logger.error(f"Ошибка при экстренном сканировании: {e}")
                return {}

        except Exception as e:
            self.logger.error(f"Критическая ошибка при экстренном сканировании: {e}")
            return {}

    #
    # МЕТОДЫ ДЛЯ РАБОТЫ С СЕРВЕРАМИ
    #

    def get_servers_with_coordinates(self, force_refresh=False) -> Dict[int, Tuple[int, int]]:
        """
        Получение видимых серверов с точными координатами через OCR.
        Добавлено кеширование для уменьшения количества вызовов OCR.

        Args:
            force_refresh: принудительно обновить кеш

        Returns:
            dict: словарь {server_id: (click_x, click_y)}
        """
        current_time = time.time()

        # Проверяем кеш
        if not force_refresh and current_time - self.last_screenshot_time < self.cache_timeout:
            if self.cached_servers:
                return self.cached_servers

        if not self.ocr_available:
            self.logger.warning("OCR не доступен")
            return {}

        try:
            import pytesseract

            screenshot = self.adb.screenshot()
            if screenshot is None or screenshot.size == 0:
                self.logger.warning("Получен пустой скриншот")
                return {}

            x, y, w, h = OCR_REGIONS['servers']
            roi = screenshot[y:y + h, x:x + w]

            # Обработка изображения
            servers_with_coords = {}
            processed_images = self._preprocess_image(roi, w, h)

            for method_name, img, scale in processed_images:

                # OCR анализ
                data = pytesseract.image_to_data(
                    img, output_type=pytesseract.Output.DICT,
                    lang='rus+eng', config='--psm 6'
                )

                # Поиск серверов
                self._extract_servers_from_ocr_data(
                    data, servers_with_coords, x, y, scale
                )

            # Фильтрация и валидация результатов с учетом текущего сезона
            validated_servers = self._validate_servers_with_season(servers_with_coords)
            sorted_servers = dict(sorted(validated_servers.items(), reverse=True))

            # Обновляем кеш и время
            self.cached_servers = sorted_servers
            self.last_screenshot_time = current_time

            if sorted_servers:
                # Логируем только если результат отличается от предыдущего
                if list(sorted_servers.keys()) != self.last_servers:
                    self.logger.info(f"Найдены валидные сервера: {list(sorted_servers.keys())}")
                    self.last_servers = list(sorted_servers.keys())
            else:
                self.logger.warning("Не найдено валидных серверов")

            return sorted_servers

        except Exception as e:
            self.logger.error(f"Ошибка получения координат серверов: {e}")
            return {}

    def find_server_coordinates(self, server_id: int, attempts: int = 1) -> Optional[Tuple[int, int]]:
        """
        Поиск координат конкретного сервера с уменьшенным количеством попыток.

        Args:
            server_id: номер сервера
            attempts: количество попыток поиска (уменьшено с 3 до 1)

        Returns:
            tuple: (x, y) координаты сервера или None
        """
        for attempt in range(attempts):
            # Принудительно обновляем данные только на первой попытке
            servers_dict = self.get_servers_with_coordinates(force_refresh=(attempt == 0))

            # Прямой поиск целевого сервера
            if server_id in servers_dict:
                self.logger.info(f"Сервер {server_id} найден точно на попытке {attempt + 1}")
                return servers_dict[server_id]

            # Небольшая пауза между попытками
            if attempt < attempts - 1:
                time.sleep(0.3)

        return None

    def scroll_to_server_range(self, target_server: int, current_servers: List[int]) -> str:
        """
        Интеллектуальный скроллинг к диапазону сервера.

        Args:
            target_server: целевой сервер
            current_servers: текущие видимые сервера

        Returns:
            str: 'found' если цель видна, 'small' если выполнен мелкий скроллинг,
                 'regular' если обычный, 'none' если скроллинг не нужен
        """
        if not current_servers:
            self.logger.warning("Нет текущих серверов для определения направления скроллинга")
            self._perform_regular_scroll(target_server, [])
            return 'regular'

        min_visible = min(current_servers)
        max_visible = max(current_servers)

        self.logger.debug(f"Целевой сервер: {target_server}, видимые: {min_visible}-{max_visible}")

        # Если целевой сервер уже видимый
        if min_visible <= target_server <= max_visible:
            return 'found'

        # Определяем расстояние до цели
        distance_to_min = abs(target_server - min_visible)
        distance_to_max = abs(target_server - max_visible)
        min_distance = min(distance_to_min, distance_to_max)

        # Если очень близко (1-3 сервера), используем мелкий скроллинг
        if min_distance <= 3:
            self._perform_small_scroll(target_server, current_servers)
            return 'small'
        # Если близко (4-8 серверов), пробуем мелкий скроллинг
        elif min_distance <= 8:
            self._perform_small_scroll(target_server, current_servers)
            return 'small'
        # Если далеко, используем обычный скроллинг
        else:
            self._perform_regular_scroll(target_server, current_servers)
            return 'regular'

    def _perform_small_scroll(self, target_server: int, current_servers: List[int]) -> bool:
        """Выполнение мелкого скроллинга с улучшенной точностью."""
        self.logger.debug(f"Выполняем мелкий скроллинг к серверу {target_server}")

        if not current_servers:
            # Если нет данных о текущих серверах, делаем скроллинг вниз
            scroll_down = True
        else:
            min_visible = min(current_servers)
            max_visible = max(current_servers)
            # Определяем направление более точно
            if target_server < min_visible:
                scroll_down = True
            elif target_server > max_visible:
                scroll_down = False
            else:
                # Цель в диапазоне, но не найдена - возможно нужно небольшой сдвиг
                # Определяем к какому краю диапазона ближе
                scroll_down = abs(target_server - min_visible) < abs(target_server - max_visible)

        # Используем более мелкий шаг скроллинга
        if scroll_down:
            start_coords = COORDINATES['server_small_scroll_start']
            end_coords = COORDINATES['server_small_scroll_end']
        else:
            start_coords = COORDINATES['server_small_scroll_end']
            end_coords = COORDINATES['server_small_scroll_start']

        # Выполняем еще более мелкий скроллинг
        small_duration = SERVER_RECOGNITION_SETTINGS['small_scroll_duration'] // 2  # Половина обычного времени
        self.adb.swipe(*start_coords, *end_coords, duration=small_duration)
        time.sleep(PAUSE_SETTINGS['after_server_scroll'])

        # Очищаем кеш после скроллинга
        self.cached_servers = {}
        return True

    def _perform_regular_scroll(self, target_server: int, current_servers: List[int]) -> bool:
        """Выполнение обычного скроллинга."""
        min_visible = min(current_servers) if current_servers else 500
        scroll_down = target_server < min_visible

        self.logger.debug(f"Выполняем {'вниз' if scroll_down else 'вверх'} скроллинг к серверу {target_server}")

        if scroll_down:
            start_coords = COORDINATES['server_scroll_start']
            end_coords = COORDINATES['server_scroll_end']
        else:
            start_coords = COORDINATES['server_scroll_end']
            end_coords = COORDINATES['server_scroll_start']

        self.adb.swipe(*start_coords, *end_coords,
                      duration=SERVER_RECOGNITION_SETTINGS['scroll_duration'])
        time.sleep(PAUSE_SETTINGS['after_server_scroll'])

        # Очищаем кеш после скроллинга
        self.cached_servers = {}
        return True

    def _preprocess_image(self, roi, w, h) -> List[Tuple[str, np.ndarray, int]]:
        """Предобработка изображения для OCR с улучшенной фильтрацией."""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        processed = []

        # Применение размытия для уменьшения шума
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Стандартная бинаризация с предварительным размытием
        _, binary = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
        processed.append(("binary_blur", binary, 1))

        # Адаптивная бинаризация
        binary_adaptive = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        processed.append(("adaptive_blur", binary_adaptive, 1))

        # Увеличенное изображение для лучшего распознавания мелких символов
        scale_factor = 2
        resized = cv2.resize(blurred, (w * scale_factor, h * scale_factor),
                           interpolation=cv2.INTER_CUBIC)
        _, binary_resized = cv2.threshold(resized, 150, 255, cv2.THRESH_BINARY_INV)
        processed.append(("resized_blur", binary_resized, scale_factor))

        return processed

    def _extract_servers_from_ocr_data(self, data, servers_dict, offset_x, offset_y, scale):
        """Извлечение серверов из данных OCR с улучшенной фильтрацией."""
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            confidence = int(data['conf'][i])

            # Повышаем минимальную уверенность для лучшей фильтрации
            if confidence < 40:
                continue

            server_numbers = self._parse_server_numbers(text)

            for server_id in server_numbers:
                # Дополнительная проверка на разумность номера сервера
                if 100 <= server_id <= 619 and server_id not in servers_dict:
                    # Вычисляем координаты центра текста
                    text_x = data['left'][i] // scale
                    text_y = data['top'][i] // scale
                    text_w = data['width'][i] // scale
                    text_h = data['height'][i] // scale

                    abs_x = offset_x + text_x + text_w // 2
                    abs_y = offset_y + text_y + text_h // 2

                    servers_dict[server_id] = (abs_x, abs_y)

    def _parse_server_numbers(self, text: str) -> List[int]:
        """Парсинг номеров серверов из текста с улучшенной логикой."""
        # Очистка текста от лишних символов
        clean_text = re.sub(r'[^\w\s#№:]', ' ', text)

        patterns = [
            r"Море\s*[#№]\s*(\d{3})",  # "Море #504"
            r"[#№]\s*(\d{3})",          # "#504"
            r"\b(\d{3})\b",             # Трехзначное число отдельно
        ]

        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, clean_text)
            for match in matches:
                try:
                    num = int(match)
                    # Более строгая проверка диапазона
                    if 100 <= num <= 619:
                        numbers.append(num)
                except ValueError:
                    continue

        # Убираем дубликаты, сохраняя порядок
        unique_numbers = []
        for num in numbers:
            if num not in unique_numbers:
                unique_numbers.append(num)

        return unique_numbers

    def _validate_servers_with_season(self, servers_dict: Dict[int, Tuple[int, int]]) -> Dict[int, Tuple[int, int]]:
        """
        Валидация найденных серверов с учетом текущего сезона.

        Args:
            servers_dict: словарь серверов {server_id: (x, y)}

        Returns:
            dict: отфильтрованный словарь валидных серверов
        """
        validated = {}

        # Получаем диапазон серверов для текущего сезона
        if self.current_season and self.current_season in SEASONS:
            season_data = SEASONS[self.current_season]
            season_min = min(season_data['min_server'], season_data['max_server'])
            season_max = max(season_data['min_server'], season_data['max_server'])
        else:
            # Если сезон не установлен, используем полный диапазон
            season_min = 1
            season_max = 619

        for server_id, coords in servers_dict.items():
            # Базовая проверка диапазона
            if not (1 <= server_id <= 619):
                self.logger.debug(f"Сервер {server_id} вне общего диапазона")
                continue

            # Проверка принадлежности к текущему сезону
            if not (season_min <= server_id <= season_max):
                self.logger.debug(f"Сервер {server_id} не принадлежит сезону {self.current_season} ({season_min}-{season_max})")
                continue

            # Проверка координат
            x, y = coords
            roi_x, roi_y, roi_w, roi_h = OCR_REGIONS['servers']
            if not (roi_x <= x <= roi_x + roi_w and roi_y <= y <= roi_y + roi_h):
                self.logger.debug(f"Сервер {server_id} имеет координаты вне области поиска")
                continue

            # Проверка логичности последовательности (более мягкая для серверов в пределах сезона)
            if self.last_servers:
                min_last = min(self.last_servers)
                max_last = max(self.last_servers)

                # Для серверов в пределах сезона используем более мягкий критерий
                reasonable_range = 50
                if server_id < min_last - reasonable_range or server_id > max_last + reasonable_range:
                    self.logger.debug(f"Сервер {server_id} далеко от предыдущих результатов ({min_last}-{max_last})")
                    continue

            validated[server_id] = coords

        # Если найдено мало валидных серверов, логируем для отладки
        if len(validated) < 3:
            self.logger.debug(f"Мало валидных серверов ({len(validated)}), сезон: {self.current_season}")

        return validated

    #
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ОТЛАДКИ
    #

    def _save_debug_image(self, image, filename):
        """Сохранение изображения для отладки."""
        if not self.debug_mode:
            return

        try:
            filepath = self.debug_dir / filename
            cv2.imwrite(str(filepath), image)
            self.logger.debug(f"Сохранено отладочное изображение: {filepath}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении изображения {filename}: {e}")

    def _save_ocr_results(self, data, filename):
        """Сохранение результатов OCR для отладки."""
        if not self.debug_mode:
            return

        try:
            filepath = self.debug_dir / filename

            lines = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    lines.append(f"Текст: '{data['text'][i].strip()}', "
                               f"Уверенность: {data['conf'][i]}, "
                               f"Координаты: ({data['left'][i]}, {data['top'][i]}, "
                               f"{data['width'][i]}, {data['height'][i]})")

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.logger.debug(f"Сохранены результаты OCR: {filepath}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении результатов OCR {filename}: {e}")

    def _save_text_file(self, text, filename):
        """Сохранение текстового файла для отладки."""
        if not self.debug_mode:
            return

        try:
            filepath = self.debug_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)

            self.logger.debug(f"Сохранен текстовый файл: {filepath}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении текстового файла {filename}: {e}")

    def _visualize_seasons(self, image, seasons_dict, filename):
        """Визуализация найденных сезонов на изображении."""
        if not self.debug_mode:
            return

        try:
            # Создаем копию изображения
            viz_image = image.copy()

            # Отображаем каждый найденный сезон
            for season_id, (x, y) in seasons_dict.items():
                # Рисуем круг на координатах сезона
                cv2.circle(viz_image, (x, y), 20, (0, 255, 0), 2)
                # Добавляем текст с ID сезона
                cv2.putText(viz_image, season_id, (x - 10, y - 25),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Сохраняем визуализированное изображение
            self._save_debug_image(viz_image, filename)

        except Exception as e:
            self.logger.error(f"Ошибка при визуализации сезонов: {e}")

    def _visualize_season_click(self, image, x, y, filename):
        """Визуализация клика по сезону."""
        if not self.debug_mode:
            return

        try:
            # Создаем копию изображения
            viz_image = image.copy()

            # Рисуем большой круг для обозначения клика
            cv2.circle(viz_image, (x, y), 30, (0, 0, 255), 3)
            # Рисуем перекрестие
            cv2.line(viz_image, (x - 20, y), (x + 20, y), (0, 0, 255), 2)
            cv2.line(viz_image, (x, y - 20), (x, y + 20), (0, 0, 255), 2)
            # Добавляем текст "КЛИК"
            cv2.putText(viz_image, "КЛИК", (x - 30, y - 35),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Сохраняем визуализированное изображение
            self._save_debug_image(viz_image, filename)

        except Exception as e:
            self.logger.error(f"Ошибка при визуализации клика: {e}")

    def enable_debug_mode(self):
        """Включение режима отладки."""
        if not self.debug_mode:
            from pathlib import Path
            self.debug_mode = True
            self.debug_dir = Path("debug_seasons")
            self.debug_dir.mkdir(exist_ok=True)
            self.logger.info(f"Режим отладки включен. Скриншоты будут сохраняться в: {self.debug_dir}")

    def disable_debug_mode(self):
        """Отключение режима отладки."""
        self.debug_mode = False
        self.logger.info("Режим отладки отключен")