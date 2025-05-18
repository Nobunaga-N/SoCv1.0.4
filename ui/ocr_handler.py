"""
Обработчик OCR и работы с текстом на экране.
"""
import cv2
import numpy as np
import logging
import time
from typing import Optional, Tuple


class OCRHandler:
    """Класс для работы с распознаванием текста и поиска элементов по тексту."""

    def __init__(self, adb_controller):
        """
        Инициализация обработчика OCR.

        Args:
            adb_controller: контроллер ADB
        """
        self.logger = logging.getLogger('sea_conquest_bot.ocr')
        self.adb = adb_controller
        self.ocr_available = self._check_ocr_availability()

    def _check_ocr_availability(self) -> bool:
        """Проверка доступности OCR."""
        try:
            import pytesseract
            return True
        except ImportError:
            self.logger.warning("OCR не доступен - pytesseract не установлен")
            return False

    def find_text_on_screen(self, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                           timeout: Optional[int] = None) -> Optional[Tuple[int, int, int, int]]:
        """
        Поиск текста на экране с использованием OCR.

        Args:
            text: искомый текст
            region: область поиска (x, y, w, h)
            timeout: время ожидания

        Returns:
            tuple: координаты найденного текста (x, y, w, h) или None
        """
        if not self.ocr_available:
            return None

        start_time = time.time()
        while timeout is None or time.time() - start_time < timeout:
            screenshot = self.adb.screenshot()
            if screenshot is None:
                time.sleep(0.5)
                continue

            # Определяем область поиска
            if region:
                x, y, w, h = region
                roi = screenshot[y:y + h, x:x + w]
                offset_x, offset_y = x, y
            else:
                roi = screenshot
                offset_x, offset_y = 0, 0

            # Поиск текста
            if self._find_text_in_image(roi, text):
                center_x = offset_x + roi.shape[1] // 2
                center_y = offset_y + roi.shape[0] // 2
                return (center_x, center_y, roi.shape[1], roi.shape[0])

            time.sleep(0.5)

        return None

    def find_and_click_text(self, text: str, region: Optional[Tuple[int, int, int, int]] = None,
                          timeout: Optional[int] = None) -> bool:
        """
        Поиск и клик по тексту.

        Args:
            text: искомый текст
            region: область поиска
            timeout: время ожидания

        Returns:
            bool: True если текст найден и клик выполнен
        """
        result = self.find_text_on_screen(text, region, timeout)
        if result:
            x, y, _, _ = result
            self.adb.tap(x, y)
            return True
        return False

    def _find_text_in_image(self, image: np.ndarray, target_text: str) -> bool:
        """
        Поиск текста в изображении.

        Args:
            image: изображение для поиска
            target_text: искомый текст

        Returns:
            bool: True если текст найден
        """
        try:
            import pytesseract

            # Предобработка изображения
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Несколько методов обработки для повышения точности
            methods = [
                cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1],
                cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 11, 2)
            ]

            # Проверяем каждый метод
            target_lower = target_text.lower()
            for processed in methods:
                result = pytesseract.image_to_string(processed, lang='rus+eng')
                if target_lower in result.lower():
                    return True

            return False
        except Exception as e:
            self.logger.error(f"Ошибка поиска текста: {e}")
            return False

    def get_text_from_region(self, region: Tuple[int, int, int, int]) -> str:
        """
        Получение текста из указанной области экрана.

        Args:
            region: область (x, y, w, h)

        Returns:
            str: распознанный текст
        """
        if not self.ocr_available:
            return ""

        try:
            import pytesseract

            screenshot = self.adb.screenshot()
            if screenshot is None:
                return ""

            x, y, w, h = region
            roi = screenshot[y:y + h, x:x + w]

            # Предобработка
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            # Распознавание
            text = pytesseract.image_to_string(binary, lang='rus+eng')
            return text.strip()

        except Exception as e:
            self.logger.error(f"Ошибка получения текста: {e}")
            return ""