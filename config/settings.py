"""
Модуль с конфигурационными параметрами для бота Sea of Conquest.
Централизованные настройки для всего проекта.
"""
import os
import logging
from pathlib import Path

# Базовые пути (относительно корня проекта, а не config директории)
BASE_DIR = Path(__file__).parent.parent.absolute()
IMAGES_DIR = BASE_DIR / 'images'
LOGS_DIR = BASE_DIR / 'logs'

# Создаем директории если их нет
IMAGES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Таймауты
DEFAULT_TIMEOUT = 3  # Минимальный таймаут между действиями
LOADING_TIMEOUT = 14  # Таймаут для ожидания загрузки
SCREENSHOT_TIMEOUT = 0.5  # Таймаут между скриншотами при поиске изображений

# Настройки игры
GAME_PACKAGE = "com.seaofconquest.global"
GAME_ACTIVITY = "com.kingsgroup.mo.KGUnityPlayerActivity"

# Пути к изображениям
IMAGE_PATHS = {
    'start_battle': str(IMAGES_DIR / 'start_battle.png'),
    'coins': str(IMAGES_DIR / 'coins.png'),
    'cannon_is_ready': str(IMAGES_DIR / 'cannon_is_ready.png'),
    'hell_henry': str(IMAGES_DIR / 'hell_henry.png'),
    'collect_items': str(IMAGES_DIR / 'collect_items.png'),
    'gold_compas': str(IMAGES_DIR / 'gold_compas.png'),
    'long_song': str(IMAGES_DIR / 'long_song.png'),
    'confirm_trade': str(IMAGES_DIR / 'confirm_trade.png'),
    'prepare_for_battle': str(IMAGES_DIR / 'prepare_for_battle.png'),
    'ship_waiting_zaliz': str(IMAGES_DIR / 'ship_waiting_zaliz.png'),
    'long_song_2': str(IMAGES_DIR / 'long_song_2.png'),
    'long_song_3': str(IMAGES_DIR / 'long_song_3.png'),
    'long_song_4': str(IMAGES_DIR / 'long_song_4.png'),
    'long_song_5': str(IMAGES_DIR / 'long_song_5.png'),
    'long_song_6': str(IMAGES_DIR / 'long_song_6.png'),
    'cannon_long': str(IMAGES_DIR / 'cannon_long.png'),
    'ship_song': str(IMAGES_DIR / 'ship_song.png'),
    'griffin': str(IMAGES_DIR / 'griffin.png'),
    'molly': str(IMAGES_DIR / 'molly.png')
}

# Координаты для кликов
COORDINATES = {
    # Основной интерфейс
    'profile_icon': (52, 50),
    'settings_icon': (1076, 31),
    'characters_icon': (643, 319),
    'add_character_icon': (271, 181),
    'skip_button': (1142, 42),

    # Координаты для скроллинга
    'season_scroll_start': (257, 550),
    'season_scroll_end': (257, 200),
    'server_scroll_start': (640, 550),
    'server_scroll_end': (640, 200),
    'server_small_scroll_start': (640, 380),
    'server_small_scroll_end': (640, 320),

    # Координаты сезонов
    'seasons': {
        'S1': (250, 180), 'S2': (250, 230), 'S3': (250, 280),
        'S4': (250, 380), 'S5': (250, 470), 'X1': (250, 520),
        'X2': (250, 230), 'X3': (250, 280), 'X4': (250, 330)
    },

    # Координаты серверов
    'servers': {
        'left_column_x': 466,
        'right_column_x': 816,
        'base_y': 136,
        'step_y': 90
    }
}

# Информация о сезонах и серверах
SEASONS = {
    'S1': {'min_server': 619, 'max_server': 598},
    'S2': {'min_server': 597, 'max_server': 571},
    'S3': {'min_server': 564, 'max_server': 541},
    'S4': {'min_server': 570, 'max_server': 505},
    'S5': {'min_server': 504, 'max_server': 457},
    'X1': {'min_server': 456, 'max_server': 433},
    'X2': {'min_server': 432, 'max_server': 363},
    'X3': {'min_server': 360, 'max_server': 97},
    'X4': {'min_server': 93, 'max_server': 1},
}

# Области для OCR распознавания
OCR_REGIONS = {
    'seasons': (150, 150, 220, 400),
    'servers': (400, 130, 570, 470),
    'skip_button': (900, 0, 380, 100),
    'skip_button_extended': (800, 0, 480, 120)
}

# Варианты текста кнопки ПРОПУСТИТЬ
SKIP_BUTTON_VARIANTS = [
    # Основные варианты
    "ПРОПУСТИТЬ", "ПРОПУСТИТЬ >>", "ПРОПУСТИТЬ>", "ПРОПУСТИТЬ >",
    "ПРОПУСТИTЬ", "ПРОПУСТИTЬ >>", "ПРОПУСТИTЬ>", "ПРОПУСТИTЬ >",

    # Варианты с возможными ошибками OCR
    "ПРОNYСТИТЬ", "ПРОПYСТИТЬ", "ПPОПУСТИТЬ", "ПРОПУCTИТЬ",
    "ПРOПУСТИТЬ", "ПPOПУСТИТЬ", "ПРОПУСТИTь",
    "ПРОПУСТИТЬ>>", "ПРОNYСТИТЬ >>", "ПРОПYСТИТЬ >>",

    # Английские варианты
    "SKIP", "SKIP >>", "SKIP>", "SKIP >",

    # Только стрелки
    ">>", "> >", "»", "» »",

    # Частичные совпадения
    "РОПУСТИТЬ", "ПРОПУСТИ", "РОПУСТИ", "ПУСТИ", "ПУСТ",

    # С пробелами
    "П Р О П У С Т И Т Ь", "П РОПУСТИТЬ", "ПРО ПУСТИТЬ",
]

# Настройки для пауз между действиями (в секундах)
PAUSE_SETTINGS = {
    'before_season_click': 0.5,
    'after_season_click': 1.5,
    'after_season_scroll': 2.0,
    'before_server_click': 0.5,
    'after_server_click': 1.5,
    'after_server_scroll': 1.5,
    'between_tutorial_steps': 1.0,
}

# Настройки для распознавания изображений
TEMPLATE_MATCHING_THRESHOLD = 0.7

# Настройки для улучшенного распознавания серверов
SERVER_RECOGNITION_SETTINGS = {
    'max_scroll_attempts': 10,
    'scroll_duration': 1000,
    'small_scroll_duration': 300,
    'recognition_attempts': 1,
    'servers_per_screen': 10,
    'small_scroll_distance': 50,
    'max_server_difference': 3,
    'overshoot_threshold': 20,
}

# Настройки для OCR
OCR_SETTINGS = {
    'language': 'rus+eng',
    'config': '--psm 6 -c tessedit_char_whitelist=0123456789#№Море ',
    'threshold_binary': 150,
    'threshold_adaptive_block_size': 11,
    'threshold_adaptive_c': 2,
    'resize_factor': 2,
    'min_server_number': 100,
    'max_server_number': 619,
    'max_difference_from_target': 50,
    'min_confidence': 40,
}

# Дополнительные координаты для шагов обучения
ADDITIONAL_COORDINATES = {
    'cannon_activation': (718, 438),
    'ship_icon': (58, 654),
    'lower_deck_build': (638, 403),
    'pub_build': (635, 373),
    'storage_repair': (635, 373),
    'upper_deck_build': (345, 386),
    'cannon_select': (77, 276),
    'travel_start': (741, 145),
    'quest_area': (93, 285),
    'screen_continue': (630, 413),
    'compass_icon': (1074, 88),
    'compass_pointer': (701, 258),
    'back_button': (145, 25),
    'trade_confirm': (151, 349),
    'hero_select': (85, 634),
    'battle_start': (1157, 604),
    'battle_area': (642, 334),
    'skull_dead_bay': (653, 403),
    'hammer_icon': (43, 481),
    'ship_upgrade': (127, 216),
    'upgrade_button': (1083, 638),
    'build_button': (639, 603),
    'rowers_cabin': (968, 507),
    'cannon_deck': (687, 514),
    'ship_compass': (652, 214),
    'coins_collect': (931, 620),
}


def validate_config():
    """
    Проверка корректности конфигурации.

    Returns:
        bool: True если конфигурация корректна
    """
    import logging
    logger = logging.getLogger('sea_conquest_bot.config')

    # Отладочная информация о путях
    logger.info(f"Базовая директория проекта: {BASE_DIR}")
    logger.info(f"Директория изображений: {IMAGES_DIR}")
    logger.info(f"Директория логов: {LOGS_DIR}")

    errors_found = False

    # Проверка существования директорий
    for dir_name, dir_path in [("images", IMAGES_DIR), ("logs", LOGS_DIR)]:
        if not dir_path.exists():
            logger.info(f"Создание директории {dir_name}: {dir_path}")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Директория {dir_name} создана успешно")
            except Exception as e:
                logger.error(f"Не удалось создать директорию {dir_name}: {e}")
                errors_found = True

    # Проверка корректности данных сезонов
    for season_id, season_data in SEASONS.items():
        if season_data['min_server'] < season_data['max_server']:
            logger.error(
                f"Ошибка: В сезоне {season_id} min_server ({season_data['min_server']}) "
                f"меньше max_server ({season_data['max_server']})"
            )
            errors_found = True

    # Проверка наличия обязательных изображений
    required_images = ['start_battle', 'coins']
    missing_images = []
    for img_key in required_images:
        if img_key in IMAGE_PATHS:
            img_path = Path(IMAGE_PATHS[img_key])
            if not img_path.exists():
                missing_images.append(img_key)

    if missing_images:
        logger.warning(f"Отсутствуют обязательные изображения: {missing_images}")
        logger.info("Бот может работать без них, но некоторые функции будут ограничены")

    # Проверка критических настроек
    critical_settings = [
        ('DEFAULT_TIMEOUT', DEFAULT_TIMEOUT),
        ('LOADING_TIMEOUT', LOADING_TIMEOUT),
        ('SCREENSHOT_TIMEOUT', SCREENSHOT_TIMEOUT),
    ]

    for setting_name, setting_value in critical_settings:
        if not isinstance(setting_value, (int, float)) or setting_value < 0:
            logger.error(f"Некорректное значение {setting_name}: {setting_value}")
            errors_found = True

    # Проверка наличия критических координат
    required_coords = ['seasons', 'servers']
    for coord_key in required_coords:
        if coord_key not in COORDINATES:
            logger.error(f"Отсутствует критическая конфигурация координат: {coord_key}")
            errors_found = True

    if errors_found:
        logger.error("Обнаружены критические ошибки конфигурации")
        return False
    else:
        logger.info("Конфигурация прошла валидацию успешно")
        return True


# Запуск валидации при импорте
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if validate_config():
        print("✅ Конфигурация прошла валидацию успешно")
    else:
        print("❌ Обнаружены ошибки в конфигурации")