"""
Продвинутый поиск кнопки ПРОПУСТИТЬ с множественными методами OCR.
"""
import cv2
import numpy as np
import logging
import time
from typing import List, Tuple, Dict, Optional


class SkipButtonFinder:
    """Класс для поиска кнопки ПРОПУСТИТЬ с использованием различных методов OCR."""

    def __init__(self, adb_controller, interface_controller):
        """
        Инициализация поисковика кнопки ПРОПУСТИТЬ.

        Args:
            adb_controller: контроллер ADB
            interface_controller: контроллер интерфейса
        """
        self.logger = logging.getLogger('sea_conquest_bot.skip_finder')
        self.adb = adb_controller
        self.interface = interface_controller
        self.ocr_available = self._check_ocr_availability()

    def _check_ocr_availability(self) -> bool:
        """Проверка доступности OCR."""
        try:
            import pytesseract
            return True
        except ImportError:
            self.logger.warning("OCR не доступен")
            return False

    def find_skip_button_infinite(self) -> bool:
        """
        Бесконечный поиск кнопки ПРОПУСТИТЬ с улучшенными методами OCR.

        Returns:
            bool: True когда кнопка найдена и нажата
        """
        self.logger.info("Запуск бесконечного поиска кнопки ПРОПУСТИТЬ")

        attempt = 0
        log_interval = 15  # Логируем каждые 15 попыток

        while True:
            attempt += 1

            if attempt % log_interval == 1:
                self.logger.info(f"Попытка поиска ПРОПУСТИТЬ #{attempt}")

            try:
                # Каждые 5 попыток используем продвинутый поиск по всем областям
                if attempt % 5 == 0:
                    if self._find_skip_with_advanced_ocr():
                        self.logger.info(f"ПРОПУСТИТЬ найден продвинутым методом на попытке #{attempt}")
                        return True
                else:
                    # Быстрый поиск в основной области
                    if self._find_skip_quick_search():
                        self.logger.info(f"ПРОПУСТИТЬ найден быстрым методом на попытке #{attempt}")
                        return True

            except Exception as e:
                self.logger.debug(f"Ошибка в попытке #{attempt}: {e}")

            # Короткая пауза между попытками
            time.sleep(0.3)

    def find_skip_button_with_timeout(self, timeout: int = 10) -> bool:
        """
        Поиск кнопки ПРОПУСТИТЬ с ограничением по времени.

        Args:
            timeout: максимальное время поиска в секундах

        Returns:
            bool: True если кнопка найдена и нажата
        """
        self.logger.info(f"Поиск кнопки ПРОПУСТИТЬ с таймаутом {timeout} сек")

        start_time = time.time()
        attempt = 0

        while time.time() - start_time < timeout:
            attempt += 1

            try:
                if self._find_skip_quick_search():
                    self.logger.info(f"ПРОПУСТИТЬ найден на попытке #{attempt}")
                    return True

                # Каждые 5 попыток используем продвинутый поиск
                if attempt % 5 == 0:
                    if self._find_skip_with_advanced_ocr():
                        self.logger.info(f"ПРОПУСТИТЬ найден продвинутым методом на попытке #{attempt}")
                        return True

            except Exception as e:
                self.logger.debug(f"Ошибка в попытке #{attempt}: {e}")

            time.sleep(0.3)

        self.logger.warning(f"ПРОПУСТИТЬ не найден за {timeout} секунд")
        return False

    def _find_skip_with_advanced_ocr(self) -> bool:
        """
        Продвинутый поиск кнопки ПРОПУСТИТЬ с множественными методами обработки.

        Returns:
            bool: True если кнопка найдена и нажата
        """
        from utils.config import OCR_REGIONS, SKIP_BUTTON_VARIANTS

        # Список областей для поиска (от узкой к широкой)
        search_regions = [
            OCR_REGIONS['skip_button'],
            OCR_REGIONS['skip_button_extended'],
            (700, 0, 580, 150),  # Очень широкая область правого верха
        ]

        # Получаем скриншот один раз
        screenshot = self.adb.screenshot()
        if screenshot is None or screenshot.size == 0:
            return False

        # Пробуем разные области поиска
        for region_idx, region in enumerate(search_regions):
            x, y, w, h = region
            # Проверяем границы
            x = max(0, x)
            y = max(0, y)
            w = min(screenshot.shape[1] - x, w)
            h = min(screenshot.shape[0] - y, h)

            if w <= 0 or h <= 0:
                continue

            roi = screenshot[y:y + h, x:x + w]

            # Применяем все методы обработки для этой области
            for method_name, method_func in self._get_ocr_methods().items():
                result = method_func(roi, SKIP_BUTTON_VARIANTS)
                if result:
                    coords = (x + result[0], y + result[1])
                    self.interface.click_coord(coords[0], coords[1])
                    self.logger.info(f"ПРОПУСТИТЬ найден {method_name} в области {region_idx + 1}")
                    return True

        return False

    def _find_skip_quick_search(self) -> bool:
        """
        Быстрый поиск только в основной области.

        Returns:
            bool: True если кнопка найдена и нажата
        """
        from utils.config import OCR_REGIONS, SKIP_BUTTON_VARIANTS

        screenshot = self.adb.screenshot()
        if screenshot is None or screenshot.size == 0:
            return False

        # Поиск только в основной области
        region = OCR_REGIONS['skip_button']
        x, y, w, h = region
        roi = screenshot[y:y + h, x:x + w]

        # Пробуем только самые эффективные методы для скорости
        result = self._ocr_method_inverted_binary(roi, SKIP_BUTTON_VARIANTS)
        if result:
            coords = (x + result[0], y + result[1])
            self.interface.click_coord(coords[0], coords[1])
            return True

        result = self._ocr_method_standard_binary(roi, SKIP_BUTTON_VARIANTS)
        if result:
            coords = (x + result[0], y + result[1])
            self.interface.click_coord(coords[0], coords[1])
            return True

        return False

    def _get_ocr_methods(self) -> Dict[str, callable]:
        """
        Возвращает словарь всех доступных методов OCR обработки.

        Returns:
            dict: словарь методов OCR
        """
        return {
            'standard_binary': self._ocr_method_standard_binary,
            'inverted_binary': self._ocr_method_inverted_binary,
            'adaptive_threshold': self._ocr_method_adaptive_threshold,
            'multi_threshold': self._ocr_method_multi_threshold,
            'contrast_enhanced': self._ocr_method_contrast_enhanced,
            'morphological': self._ocr_method_morphological,
            'color_isolation': self._ocr_method_color_isolation,
            'edge_detection': self._ocr_method_edge_detection,
        }

    def _ocr_method_standard_binary(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Стандартная бинаризация."""
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            thresholds = [120, 150, 180, 200]
            for threshold in thresholds:
                _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
                result = self._process_with_tesseract(binary, variants, scale=2)
                if result:
                    return result
            return None
        except:
            return None

    def _ocr_method_inverted_binary(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Инвертированная бинаризация."""
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            thresholds = [120, 150, 180]
            for threshold in thresholds:
                _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
                result = self._process_with_tesseract(binary, variants, scale=2)
                if result:
                    return result
            return None
        except:
            return None

    def _ocr_method_adaptive_threshold(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Адаптивная пороговая обработка."""
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            configs = [
                (cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 11, 2),
                (cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 15, 5),
                (cv2.ADAPTIVE_THRESH_MEAN_C, 11, 2),
                (cv2.ADAPTIVE_THRESH_MEAN_C, 15, 5),
            ]

            for method, block_size, c in configs:
                binary = cv2.adaptiveThreshold(gray, 255, method, cv2.THRESH_BINARY, block_size, c)
                result = self._process_with_tesseract(binary, variants, scale=2)
                if result:
                    return result

                binary_inv = cv2.adaptiveThreshold(gray, 255, method, cv2.THRESH_BINARY_INV, block_size, c)
                result = self._process_with_tesseract(binary_inv, variants, scale=2)
                if result:
                    return result
            return None
        except:
            return None

    def _ocr_method_multi_threshold(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Множественная пороговая обработка."""
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            _, binary1 = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
            _, binary2 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            _, binary3 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

            combined = cv2.bitwise_or(cv2.bitwise_or(binary1, binary2), binary3)
            result = self._process_with_tesseract(combined, variants, scale=2)
            if result:
                return result

            combined_inv = cv2.bitwise_not(combined)
            result = self._process_with_tesseract(combined_inv, variants, scale=2)
            return result
        except:
            return None

    def _ocr_method_contrast_enhanced(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Улучшение контраста с помощью CLAHE."""
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            clahe_configs = [
                (2.0, (8, 8)),
                (3.0, (8, 8)),
                (4.0, (8, 8)),
                (2.0, (16, 16)),
            ]

            for clip_limit, tile_grid_size in clahe_configs:
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
                enhanced = clahe.apply(gray)

                for threshold in [130, 160, 190]:
                    _, binary = cv2.threshold(enhanced, threshold, 255, cv2.THRESH_BINARY)
                    result = self._process_with_tesseract(binary, variants, scale=2)
                    if result:
                        return result

                    _, binary_inv = cv2.threshold(enhanced, threshold, 255, cv2.THRESH_BINARY_INV)
                    result = self._process_with_tesseract(binary_inv, variants, scale=2)
                    if result:
                        return result
            return None
        except:
            return None

    def _ocr_method_morphological(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Морфологическая обработка."""
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            kernels = [
                np.ones((2, 2), np.uint8),
                np.ones((3, 3), np.uint8),
                cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
            ]

            for kernel in kernels:
                closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
                result = self._process_with_tesseract(closed, variants, scale=2)
                if result:
                    return result

                opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
                result = self._process_with_tesseract(opened, variants, scale=2)
                if result:
                    return result
            return None
        except:
            return None

    def _ocr_method_color_isolation(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Изоляция определенных цветов."""
        try:
            import pytesseract
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            white_ranges = [
                ([0, 0, 180], [255, 30, 255]),
                ([0, 0, 200], [255, 50, 255]),
                ([0, 0, 150], [255, 40, 255]),
            ]

            for lower, upper in white_ranges:
                lower = np.array(lower)
                upper = np.array(upper)
                mask = cv2.inRange(hsv, lower, upper)
                result = self._process_with_tesseract(mask, variants, scale=2)
                if result:
                    return result

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            light_mask = gray > 180
            light_binary = np.where(light_mask, 255, 0).astype(np.uint8)
            result = self._process_with_tesseract(light_binary, variants, scale=2)
            return result
        except:
            return None

    def _ocr_method_edge_detection(self, roi: np.ndarray, variants: List[str]) -> Optional[Tuple[int, int]]:
        """Выделение границ символов."""
        try:
            import pytesseract
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            canny_configs = [
                (50, 150),
                (30, 100),
                (100, 200),
            ]

            for low, high in canny_configs:
                edges = cv2.Canny(gray, low, high)
                kernel = np.ones((2, 2), np.uint8)
                dilated = cv2.dilate(edges, kernel, iterations=1)
                result = self._process_with_tesseract(dilated, variants, scale=2)
                if result:
                    return result
            return None
        except:
            return None

    def _process_with_tesseract(self, processed_image: np.ndarray, variants: List[str],
                                scale: int = 1) -> Optional[Tuple[int, int]]:
        """
        Обработка изображения с помощью Tesseract.

        Args:
            processed_image: обработанное изображение
            variants: список вариантов текста для поиска
            scale: коэффициент увеличения изображения

        Returns:
            tuple: (x, y) координаты центра найденного текста или None
        """
        try:
            import pytesseract
            import re

            # Увеличиваем изображение для лучшего распознавания
            if scale > 1:
                h, w = processed_image.shape
                processed_image = cv2.resize(processed_image, (w * scale, h * scale),
                                             interpolation=cv2.INTER_CUBIC)

            # Разные конфигурации PSM для Tesseract
            psm_configs = [
                '--psm 6',  # Uniform block of text
                '--psm 8',  # Single word
                '--psm 7',  # Single text line
                '--psm 13',  # Raw line
            ]

            for psm in psm_configs:
                try:
                    config = f"{psm} -c tessedit_char_whitelist=АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789>»"

                    data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT,
                                                     lang='rus+eng', config=config)

                    result = self._parse_tesseract_results(data, variants, scale)
                    if result:
                        return result
                except:
                    continue

            return None
        except:
            return None

    def _parse_tesseract_results(self, data: dict, variants: List[str],
                                 scale: int) -> Optional[Tuple[int, int]]:
        """
        Парсинг результатов Tesseract с интеллектуальным поиском.

        Args:
            data: данные от Tesseract
            variants: список вариантов для поиска
            scale: коэффициент масштабирования

        Returns:
            tuple: (x, y) координаты центра или None
        """
        import re

        # Собираем все найденные тексты с их координатами
        found_texts = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            confidence = int(data['conf'][i])

            if confidence >= 30 and len(text) >= 2:
                found_texts.append({
                    'text': text.upper(),
                    'confidence': confidence,
                    'left': data['left'][i] // scale,
                    'top': data['top'][i] // scale,
                    'width': data['width'][i] // scale,
                    'height': data['height'][i] // scale,
                })

        # Сначала ищем точные совпадения
        for variant in variants:
            variant_upper = variant.upper()
            for item in found_texts:
                if item['text'] == variant_upper:
                    x = item['left'] + item['width'] // 2
                    y = item['top'] + item['height'] // 2
                    return (x, y)

        # Затем ищем частичные совпадения для высокой уверенности
        for variant in variants:
            variant_upper = variant.upper()
            variant_clean = re.sub(r'[^А-ЯЁA-Z0-9]', '', variant_upper)

            for item in found_texts:
                if item['confidence'] >= 50:
                    text_clean = re.sub(r'[^А-ЯЁA-Z0-9]', '', item['text'])

                    if (variant_clean in text_clean or text_clean in variant_clean) and len(text_clean) >= 3:
                        x = item['left'] + item['width'] // 2
                        y = item['top'] + item['height'] // 2
                        return (x, y)

        # Особая обработка для стрелок ">>"
        for item in found_texts:
            text_clean = re.sub(r'[^>»]', '', item['text'])
            if len(text_clean) >= 2:
                x = item['left'] + item['width'] // 2
                y = item['top'] + item['height'] // 2
                return (x, y)

        return None