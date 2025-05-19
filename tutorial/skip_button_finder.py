"""
Супер-оптимизированный поисковик кнопки ПРОПУСТИТЬ с мгновенным распознаванием.
Создан специально для кнопки Sea of Conquest с учетом визуальных особенностей.
"""
import cv2
import numpy as np
import logging
import time
import os
from typing import Optional, Tuple, List
from pathlib import Path


class UltraFastSkipButtonFinder:
    """Супер-быстрый поисковик кнопки ПРОПУСТИТЬ с мгновенным распознаванием."""

    def __init__(self, adb_controller, interface_controller, debug_mode=False):
        """
        Инициализация супер-быстрого поисковика кнопки ПРОПУСТИТЬ.

        Args:
            adb_controller: контроллер ADB
            interface_controller: контроллер интерфейса
            debug_mode: режим отладки с сохранением изображений
        """
        self.logger = logging.getLogger('sea_conquest_bot.ultra_skip_finder')
        self.adb = adb_controller
        self.interface = interface_controller
        self.debug_mode = debug_mode
        self.ocr_available = self._check_ocr_availability()

        # Создаем папку для отладки если нужно
        if self.debug_mode:
            self.debug_dir = Path("debug_skip_screenshots")
            self.debug_dir.mkdir(exist_ok=True)

        # Точная область поиска кнопки (на основе скриншотов)
        # Кнопка находится в правом верхнем углу
        self.primary_region = (1020, 15, 240, 70)  # Основная область
        self.fallback_region = (980, 10, 280, 80)  # Резервная область

        # Варианты текста (упорядочены по вероятности)
        self.skip_variants = [
            "ПРОПУСТИТЬ",
            "пропустить",
            "Пропустить",
            ">>",
            "SKIP",
            "Skip"
        ]

        # Счетчик попыток
        self.attempt_counter = 0
        self.total_search_time = 0
        self.successful_searches = 0

    def _check_ocr_availability(self) -> bool:
        """Проверка доступности OCR."""
        try:
            import pytesseract
            return True
        except ImportError:
            self.logger.error("OCR не доступен - pytesseract не установлен")
            return False

    def find_skip_button_infinite(self) -> bool:
        """
        Супер-быстрый бесконечный поиск кнопки ПРОПУСТИТЬ.
        Оптимизирован для мгновенного распознавания.

        Returns:
            bool: True когда кнопка найдена и нажата
        """
        if not self.ocr_available:
            self.logger.error("OCR не доступен, невозможно найти кнопку ПРОПУСТИТЬ")
            return False

        self.logger.info("🚀 Запуск супер-быстрого поиска кнопки ПРОПУСТИТЬ")

        self.attempt_counter = 0
        start_time = time.time()
        last_log_time = start_time

        while True:
            self.attempt_counter += 1
            attempt_start = time.time()

            try:
                # Супер-быстрый поиск
                coords = self._ultra_fast_search()

                if coords:
                    elapsed = time.time() - start_time
                    self.total_search_time += elapsed
                    self.successful_searches += 1
                    avg_time = self.total_search_time / self.successful_searches

                    self.logger.info(
                        f"⚡ ПРОПУСТИТЬ найден за {elapsed:.2f}с на попытке {self.attempt_counter} "
                        f"(среднее время: {avg_time:.2f}с)"
                    )
                    self.interface.click_coord(coords[0], coords[1])
                    return True

            except Exception as e:
                self.logger.debug(f"Ошибка в попытке {self.attempt_counter}: {e}")

            # Логируем прогресс каждые 5 секунд
            current_time = time.time()
            if current_time - last_log_time >= 5:
                self.logger.info(f"🔍 Поиск продолжается... Попытка {self.attempt_counter} (время: {current_time - start_time:.1f}с)")
                last_log_time = current_time

            # Минимальная пауза между попытками
            time.sleep(0.05)  # Еще меньше паузы для максимальной скорости

    def find_skip_button_with_timeout(self, timeout: int = 10) -> bool:
        """
        Супер-быстрый поиск кнопки ПРОПУСТИТЬ с таймаутом.

        Args:
            timeout: максимальное время поиска в секундах

        Returns:
            bool: True если кнопка найдена и нажата
        """
        if not self.ocr_available:
            return False

        self.logger.info(f"⚡ Супер-быстрый поиск ПРОПУСТИТЬ с таймаутом {timeout}с")

        start_time = time.time()
        self.attempt_counter = 0

        while time.time() - start_time < timeout:
            self.attempt_counter += 1

            try:
                coords = self._ultra_fast_search()

                if coords:
                    elapsed = time.time() - start_time
                    self.logger.info(f"⚡ ПРОПУСТИТЬ найден за {elapsed:.2f}с на попытке {self.attempt_counter}")
                    self.interface.click_coord(coords[0], coords[1])
                    return True

            except Exception as e:
                self.logger.debug(f"Ошибка в попытке {self.attempt_counter}: {e}")

            time.sleep(0.05)

        self.logger.warning(f"ПРОПУСТИТЬ не найден за {timeout}с ({self.attempt_counter} попыток)")
        return False

    def _ultra_fast_search(self) -> Optional[Tuple[int, int]]:
        """
        Супер-быстрый поиск кнопки ПРОПУСТИТЬ с минимальной обработкой.

        Returns:
            tuple: (x, y) координаты центра кнопки или None
        """
        # Получаем скриншот
        screenshot = self.adb.screenshot()
        if screenshot is None or screenshot.size == 0:
            return None

        # Сохраняем для отладки
        if self.debug_mode and self.attempt_counter % 20 == 1:
            self._save_debug_image(screenshot, f"original_{self.attempt_counter}.png")

        # Сначала ищем в основной области
        coords = self._search_in_region_ultra_fast(screenshot, self.primary_region, "primary")
        if coords:
            return coords

        # Если не найден, ищем в резервной области
        coords = self._search_in_region_ultra_fast(screenshot, self.fallback_region, "fallback")
        return coords

    def _search_in_region_ultra_fast(self, screenshot: np.ndarray, region: Tuple[int, int, int, int],
                                    region_name: str) -> Optional[Tuple[int, int]]:
        """
        Супер-быстрый поиск в конкретной области.

        Args:
            screenshot: скриншот экрана
            region: область поиска (x, y, w, h)
            region_name: название области для отладки

        Returns:
            tuple: (x, y) координаты или None
        """
        x, y, w, h = region

        # Проверяем границы
        x = max(0, x)
        y = max(0, y)
        w = min(screenshot.shape[1] - x, w)
        h = min(screenshot.shape[0] - y, h)

        if w <= 0 or h <= 0:
            return None

        # Вырезаем область
        roi = screenshot[y:y + h, x:x + w]

        # Сохраняем ROI для отладки
        if self.debug_mode and self.attempt_counter % 20 == 1:
            self._save_debug_image(roi, f"roi_{region_name}_{self.attempt_counter}.png")

        # Применяем только самые быстрые и эффективные методы
        # Белый текст на темном фоне - идеальный случай для инвертированной бинаризации
        coords = self._method_inverted_threshold(roi)
        if coords:
            return (x + coords[0], y + coords[1])

        # Если не найден, пробуем адаптивный порог
        coords = self._method_adaptive_threshold(roi)
        if coords:
            return (x + coords[0], y + coords[1])

        # Последний шанс - поиск по цвету
        coords = self._method_color_detection(roi)
        if coords:
            return (x + coords[0], y + coords[1])

        return None

    def _method_inverted_threshold(self, roi: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Метод инвертированной бинаризации - самый эффективный для белого текста на темном фоне.

        Args:
            roi: область интереса

        Returns:
            tuple: (x, y) координаты или None
        """
        try:
            import pytesseract

            # Конвертируем в оттенки серого
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Инвертированная бинаризация (белый текст становится черным на белом фоне)
            _, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)

            # Сохраняем для отладки
            if self.debug_mode and self.attempt_counter % 20 == 1:
                self._save_debug_image(binary, f"binary_inv_{self.attempt_counter}.png")

            # Быстрая конфигурация OCR
            config = '--psm 7 --oem 3'  # PSM 7 - одна строка текста

            # Получаем текст
            text = pytesseract.image_to_string(binary, lang='rus+eng', config=config).strip()

            # Проверяем совпадения
            if self._is_skip_text(text):
                # Возвращаем центр области
                return (roi.shape[1] // 2, roi.shape[0] // 2)

            return None

        except Exception as e:
            self.logger.debug(f"Ошибка в методе инвертированного порога: {e}")
            return None

    def _method_adaptive_threshold(self, roi: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Метод адаптивной бинаризации.

        Args:
            roi: область интереса

        Returns:
            tuple: (x, y) координаты или None
        """
        try:
            import pytesseract

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Адаптивная бинаризация
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, 11, 2)

            # Сохраняем для отладки
            if self.debug_mode and self.attempt_counter % 20 == 1:
                self._save_debug_image(adaptive, f"adaptive_{self.attempt_counter}.png")

            config = '--psm 7 --oem 3'
            text = pytesseract.image_to_string(adaptive, lang='rus+eng', config=config).strip()

            if self._is_skip_text(text):
                return (roi.shape[1] // 2, roi.shape[0] // 2)

            return None

        except Exception as e:
            self.logger.debug(f"Ошибка в методе адаптивного порога: {e}")
            return None

    def _method_color_detection(self, roi: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Метод поиска по цвету - выделяем белые пиксели на темном фоне.

        Args:
            roi: область интереса

        Returns:
            tuple: (x, y) координаты или None
        """
        try:
            import pytesseract

            # Конвертируем в HSV для лучшего выделения белого цвета
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # Маска для белого цвета
            lower_white = np.array([0, 0, 180])
            upper_white = np.array([255, 30, 255])
            white_mask = cv2.inRange(hsv, lower_white, upper_white)

            # Сохраняем для отладки
            if self.debug_mode and self.attempt_counter % 20 == 1:
                self._save_debug_image(white_mask, f"white_mask_{self.attempt_counter}.png")

            config = '--psm 7 --oem 3'
            text = pytesseract.image_to_string(white_mask, lang='rus+eng', config=config).strip()

            if self._is_skip_text(text):
                return (roi.shape[1] // 2, roi.shape[0] // 2)

            return None

        except Exception as e:
            self.logger.debug(f"Ошибка в методе поиска по цвету: {e}")
            return None

    def _is_skip_text(self, text: str) -> bool:
        """
        Проверка является ли текст кнопкой пропустить.

        Args:
            text: распознанный текст

        Returns:
            bool: True если это кнопка пропустить
        """
        import re

        if not text:
            return False

        # Удаляем лишние символы и приводим к верхнему регистру
        clean_text = re.sub(r'[^\w>»]', '', text.upper())

        # Проверяем точные совпадения
        for variant in self.skip_variants:
            clean_variant = re.sub(r'[^\w>»]', '', variant.upper())
            if clean_variant == clean_text:
                self.logger.debug(f"✅ Найдено точное совпадение: '{text}' -> '{variant}'")
                return True

        # Проверяем частичные совпадения для длинного текста
        if len(clean_text) >= 6:  # Минимальная длина для "ПРОПУСТИТЬ"
            for variant in ["ПРОПУСТИТЬ", "SKIP"]:
                if variant in clean_text:
                    self.logger.debug(f"✅ Найдено частичное совпадение: '{text}' содержит '{variant}'")
                    return True

        # Проверяем стрелки
        if '>>' in text or '»' in text:
            self.logger.debug(f"✅ Найдены стрелки: '{text}'")
            return True

        return False

    def _save_debug_image(self, image: np.ndarray, filename: str):
        """Сохранение изображения для отладки."""
        if not self.debug_mode:
            return

        try:
            filepath = self.debug_dir / filename
            cv2.imwrite(str(filepath), image)
            self.logger.debug(f"💾 Сохранено отладочное изображение: {filepath}")
        except Exception as e:
            self.logger.debug(f"Ошибка сохранения изображения: {e}")

    def get_statistics(self) -> dict:
        """
        Получение статистики работы поисковика.

        Returns:
            dict: статистика
        """
        avg_time = (self.total_search_time / self.successful_searches) if self.successful_searches > 0 else 0

        return {
            'total_attempts': self.attempt_counter,
            'successful_searches': self.successful_searches,
            'total_search_time': self.total_search_time,
            'average_search_time': avg_time,
            'success_rate': (self.successful_searches / max(1, self.attempt_counter)) * 100,
            'ocr_available': self.ocr_available,
            'debug_mode': self.debug_mode
        }

    def reset_statistics(self):
        """Сброс статистики."""
        self.attempt_counter = 0
        self.total_search_time = 0
        self.successful_searches = 0
        self.logger.info("📊 Статистика поисковика сброшена")

    def enable_debug_mode(self):
        """Включение режима отладки."""
        self.debug_mode = True
        if not self.debug_dir.exists():
            self.debug_dir.mkdir(exist_ok=True)
        self.logger.info("🐛 Режим отладки включен")

    def disable_debug_mode(self):
        """Отключение режима отладки."""
        self.debug_mode = False
        self.logger.info("Режим отладки отключен")