"""
Определение и конфигурация шагов обучения.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional, Callable, Any


@dataclass
class TutorialStep:
    """Класс для описания одного шага обучения."""
    step_number: int
    description: str
    action_type: str
    params: dict
    condition: Optional[Callable] = None


class TutorialSteps:
    """Класс для управления и определения всех шагов обучения."""

    def __init__(self):
        """Инициализация конфигурации шагов."""
        self.logger = logging.getLogger('sea_conquest_bot.tutorial_steps')
        self._steps = self._define_all_steps()

    def _define_all_steps(self) -> List[TutorialStep]:
        """
        Определение всех шагов обучения согласно ТЗ.

        Returns:
            list: список шагов обучения
        """
        steps = []

        # НАЧАЛЬНЫЕ ШАГИ (1-6)
        steps.append(TutorialStep(
            step_number=1,
            description="Клик по координатам (52, 50) - открываем профиль",
            action_type="click_coord",
            params={"x": 52, "y": 50}
        ))

        steps.append(TutorialStep(
            step_number=2,
            description="Ждем 1.5 сек и открываем настройки",
            action_type="click_coord_with_delay",
            params={"x": 1076, "y": 31, "delay": 1.5}
        ))

        steps.append(TutorialStep(
            step_number=3,
            description="Ждем 1.5 сек и открываем вкладку персонажей",
            action_type="click_coord_with_delay",
            params={"x": 643, "y": 319, "delay": 1.5}
        ))

        steps.append(TutorialStep(
            step_number=4,
            description="Ждем 1.5 сек и создаем персонажа на новом сервере",
            action_type="click_coord_with_delay",
            params={"x": 271, "y": 181, "delay": 1.5}
        ))

        steps.append(TutorialStep(
            step_number=5,
            description="Выбор сервера",
            action_type="select_server",
            params={}
        ))

        steps.append(TutorialStep(
            step_number=6,
            description="Ждем 2.5 сек и подтверждаем создание персонажа + ждем загрузки 17 сек",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 787, "y": 499, "delay": 2.5, "wait_after": 17}
        ))

        # ОСНОВНЫЕ ШАГИ (7-97)

        # Шаги 7-9: Пропустить
        for i in [7, 8, 9]:
            steps.append(TutorialStep(
                step_number=i,
                description=f"Шаг {i}: Ищем и нажимаем ПРОПУСТИТЬ",
                action_type="find_skip_infinite",
                params={"wait_after": 1 if i in [7, 8, 9] else 0}
            ))

        # Шаг 10: Активация боя
        steps.append(TutorialStep(
            step_number=10,
            description="Активируем бой - ищем cannon_is_ready.png и нажимаем (718, 438)",
            action_type="click_with_image_check",
            params={"image_key": "cannon_is_ready", "x": 718, "y": 438, "image_timeout": 20}
        ))

        # Шаг 11: Пропустить
        steps.append(TutorialStep(
            step_number=11,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 12: Ждем hell_henry и пропускаем
        steps.append(TutorialStep(
            step_number=12,
            description="Дождаться hell_henry.png и нажать ПРОПУСТИТЬ",
            action_type="wait_image_then_skip",
            params={"image_key": "hell_henry", "image_timeout": 15}
        ))

        # Шаг 13: Пропустить
        steps.append(TutorialStep(
            step_number=13,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 14: Клик по иконке кораблика
        steps.append(TutorialStep(
            step_number=14,
            description="Нажимаем на иконку кораблика (58, 654) через 3 секунды",
            action_type="click_coord_with_delay",
            params={"x": 58, "y": 654, "delay": 3}
        ))

        # Шаг 15: Пропустить
        steps.append(TutorialStep(
            step_number=15,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаги 16-18: Постройки
        steps.append(TutorialStep(
            step_number=16,
            description="Отстраиваем нижнюю палубу - клик по (638, 403) через 2 секунды",
            action_type="click_coord_with_delay",
            params={"x": 638, "y": 403, "delay": 2}
        ))

        steps.append(TutorialStep(
            step_number=17,
            description="Отстраиваем паб в нижней палубе - клик по (635, 373) через 2.5 секунды",
            action_type="click_coord_with_delay",
            params={"x": 635, "y": 373, "delay": 2.5}
        ))

        steps.append(TutorialStep(
            step_number=18,
            description="Латаем дыры в складе - клик по (635, 373) через 2.5 секунды",
            action_type="click_coord_with_delay",
            params={"x": 635, "y": 373, "delay": 2.5}
        ))

        # Шаг 19: Пропустить
        steps.append(TutorialStep(
            step_number=19,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаги 20-21: Верхняя палуба и пушка
        steps.append(TutorialStep(
            step_number=20,
            description="Отстраиваем верхнюю палубу - клик по (345, 386) через 2.5 секунды",
            action_type="click_coord_with_delay",
            params={"x": 345, "y": 386, "delay": 2.5}
        ))

        steps.append(TutorialStep(
            step_number=21,
            description="Выбираем пушку - клик по (77, 276) через 1.5 секунды",
            action_type="click_coord_with_delay",
            params={"x": 77, "y": 276, "delay": 1.5}
        ))

        # Шаг 22: Пропустить
        steps.append(TutorialStep(
            step_number=22,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 23: Сбор предметов
        steps.append(TutorialStep(
            step_number=23,
            description="Собираем предметы - ищем collect_items.png и нажимаем (741, 145)",
            action_type="click_with_image_check",
            params={"image_key": "collect_items", "x": 741, "y": 145, "image_timeout": 15}
        ))

        # Шаг 24: Пропустить
        steps.append(TutorialStep(
            step_number=24,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={"wait_after": 0.5}
        ))

        # Шаги 25-27: Квест "Старый соперник"
        steps.append(TutorialStep(
            step_number=25,
            description='Начинаем квест "Старый соперник" - клик по (93, 285) через 1.5 секунды',
            action_type="click_coord_with_delay",
            params={"x": 93, "y": 285, "delay": 1.5}
        ))

        steps.append(TutorialStep(
            step_number=26,
            description="Закрываем диалог - клик по (1142, 42) через 8 секунд",
            action_type="click_coord_with_delay",
            params={"x": 1142, "y": 42, "delay": 8}
        ))

        steps.append(TutorialStep(
            step_number=27,
            description='Повторно активируем квест "Старый соперник" - клик по (93, 285) через 1.5 секунды',
            action_type="click_coord_with_delay",
            params={"x": 93, "y": 285, "delay": 1.5}
        ))

        # Шаги 28-29: Пропустить
        for i in [28, 29]:
            steps.append(TutorialStep(
                step_number=i,
                description=f"Шаг {i}: Ищем и нажимаем ПРОПУСТИТЬ",
                action_type="find_skip_infinite",
                params={"wait_after": 1 if i == 28 else 3}
            ))

        # Шаг 30: Продолжить после победы
        steps.append(TutorialStep(
            step_number=30,
            description="Продолжаем после победы - клик по центру экрана (630, 413)",
            action_type="click_coord",
            params={"x": 630, "y": 413}
        ))

        # Шаг 31: Пропустить
        steps.append(TutorialStep(
            step_number=31,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={"wait_after": 0.5}
        ))

        # Шаги 32-33: Компас
        steps.append(TutorialStep(
            step_number=32,
            description="Активируем компас - ожидаем gold_compas.png и нажимаем (1074, 88)",
            action_type="click_with_image_check",
            params={"image_key": "gold_compas", "x": 1074, "y": 88, "image_timeout": 15, "click_delay": 0.5}
        ))

        steps.append(TutorialStep(
            step_number=33,
            description="Повторно активируем компас - клик по (701, 258) через 1.5 секунды",
            action_type="click_coord_with_delay",
            params={"x": 701, "y": 258, "delay": 1.5}
        ))

        # Шаг 34: Пропустить
        steps.append(TutorialStep(
            step_number=34,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 35: Выход из компаса
        steps.append(TutorialStep(
            step_number=35,
            description="Выходим из вкладки компаса - клик по кнопке назад (145, 25)",
            action_type="click_coord",
            params={"x": 145, "y": 25}
        ))

        # Шаг 36: Пропустить
        steps.append(TutorialStep(
            step_number=36,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаги 37-39: Квест "Далекая песня"
        steps.append(TutorialStep(
            step_number=37,
            description='Активируем квест "Далекая песня" - ожидаем long_song.png и нажимаем (93, 285)',
            action_type="click_with_image_check",
            params={"image_key": "long_song", "x": 93, "y": 285, "image_timeout": 15}
        ))

        steps.append(TutorialStep(
            step_number=38,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        steps.append(TutorialStep(
            step_number=39,
            description='Повторно активируем квест "Далекая песня" - ожидаем long_song.png и нажимаем (93, 285)',
            action_type="click_with_image_check",
            params={"image_key": "long_song", "x": 93, "y": 285, "image_timeout": 15}
        ))

        # Шаг 40: Пропустить
        steps.append(TutorialStep(
            step_number=40,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 41: Согласие на обмен
        steps.append(TutorialStep(
            step_number=41,
            description='Соглашаемся на обмен - ожидаем confirm_trade.png и нажимаем (151, 349)',
            action_type="click_with_image_check",
            params={"image_key": "confirm_trade", "x": 151, "y": 349, "image_timeout": 15}
        ))

        # Шаг 42: Пропустить
        steps.append(TutorialStep(
            step_number=42,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 43: Исследование залива Мертвецов
        steps.append(TutorialStep(
            step_number=43,
            description='Начинаем исследование залива Мертвецов - ожидаем long_song.png и нажимаем (93, 285)',
            action_type="click_with_image_check",
            params={"image_key": "long_song", "x": 93, "y": 285, "image_timeout": 15}
        ))

        # Шаг 44: Пропустить
        steps.append(TutorialStep(
            step_number=44,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаги 45-46: Подготовка к битве
        steps.append(TutorialStep(
            step_number=45,
            description='Подготавливаемся к битве - ожидаем prepare_for_battle.png и нажимаем (85, 634)',
            action_type="click_with_image_check",
            params={"image_key": "prepare_for_battle", "x": 85, "y": 634, "image_timeout": 15}
        ))

        steps.append(TutorialStep(
            step_number=46,
            description="Начинаем битву - клик по (1157, 604) через 0.5 секунды + ждем 3 сек",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 1157, "y": 604, "delay": 0.5, "wait_after": 3}
        ))

        # Шаг 47: Ожидание готовности к битве
        steps.append(TutorialStep(
            step_number=47,
            description="Дожидаемся готовности к битве - ищем start_battle.png",
            action_type="wait_for_battle_ready",
            params={"image_key": "start_battle", "max_attempts": 20}
        ))

        # Шаг 48: Ожидание корабля
        steps.append(TutorialStep(
            step_number=48,
            description="Дожидаемся корабля - ищем ship_waiting_zaliz.png",
            action_type="wait_for_ship",
            params={"image_key": "ship_waiting_zaliz", "max_attempts": 20, "click_x": 93, "click_y": 285}
        ))

        # Шаг 49: Пропустить
        steps.append(TutorialStep(
            step_number=49,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 50: Следующий этап квеста
        steps.append(TutorialStep(
            step_number=50,
            description='Активируем следующий этап квеста - ожидаем long_song_2.png и нажимаем (93, 285)',
            action_type="click_with_image_check",
            params={"image_key": "long_song_2", "x": 93, "y": 285, "image_timeout": 15}
        ))

        # Шаг 51: Пропустить
        steps.append(TutorialStep(
            step_number=51,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 52: Активация черепа
        steps.append(TutorialStep(
            step_number=52,
            description="Активируем череп в заливе мертвецов - клик по (653, 403) через 2 секунды",
            action_type="click_coord_with_delay",
            params={"x": 653, "y": 403, "delay": 2}
        ))

        # Шаги 53-57: Последовательно пропускаем
        for i in range(53, 58):
            wait_after = 0.5 if 53 <= i <= 56 else 0
            steps.append(TutorialStep(
                step_number=i,
                description=f"Шаг {i}: Ищем и нажимаем ПРОПУСТИТЬ",
                action_type="find_skip_infinite",
                params={"wait_after": wait_after}
            ))

        # Шаг 58: Продолжение квеста
        steps.append(TutorialStep(
            step_number=58,
            description='Продолжаем квест - ожидаем long_song_3.png и нажимаем (93, 285)',
            action_type="click_with_image_check",
            params={"image_key": "long_song_3", "x": 93, "y": 285, "image_timeout": 15}
        ))

        # Шаг 59: Пропустить
        steps.append(TutorialStep(
            step_number=59,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 60: Возврат к исходному квесту
        steps.append(TutorialStep(
            step_number=60,
            description='Возвращаемся к исходному квесту - ожидаем long_song.png и нажимаем (93, 285)',
            action_type="click_with_image_check",
            params={"image_key": "long_song", "x": 93, "y": 285, "image_timeout": 15}
        ))

        # Шаги 61-62: Строительство
        steps.append(TutorialStep(
            step_number=61,
            description='Открываем меню строительства - ожидаем long_song_4.png и нажимаем (43, 481)',
            action_type="click_with_image_check",
            params={"image_key": "long_song_4", "x": 43, "y": 481, "image_timeout": 15}
        ))

        steps.append(TutorialStep(
            step_number=62,
            description='Выбираем корабль для улучшения - ожидаем long_song_5.png и нажимаем (127, 216)',
            action_type="click_with_image_check",
            params={"image_key": "long_song_5", "x": 127, "y": 216, "image_timeout": 15}
        ))

        # Шаг 63: Улучшение корабля
        steps.append(TutorialStep(
            step_number=63,
            description='Улучшаем корабль - ищем текст "УЛУЧШИТЬ"',
            action_type="find_and_click_text",
            params={"text": "УЛУЧШИТЬ", "region": (983, 588, 200, 100), "timeout": 5, "fallback_x": 1083,
                    "fallback_y": 638}
        ))

        # Шаг 64: Выход из вкладки корабля
        steps.append(TutorialStep(
            step_number=64,
            description="Выходим из вкладки корабля - клик по кнопке назад (145, 25) через 3 секунды",
            action_type="click_coord_with_delay",
            params={"x": 145, "y": 25, "delay": 3}
        ))

        # Шаг 65: Открытие меню постройки
        steps.append(TutorialStep(
            step_number=65,
            description="Открываем меню постройки - клик по (639, 603) через 1.5 секунды",
            action_type="click_coord_with_delay",
            params={"x": 639, "y": 603, "delay": 1.5}
        ))

        # Шаг 66: Пропустить
        steps.append(TutorialStep(
            step_number=66,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 67: Открытие компаса
        steps.append(TutorialStep(
            step_number=67,
            description="Открываем компас - клик по (1072, 87) через 1.5 секунды + ждем 5 сек",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 1072, "y": 87, "delay": 1.5, "wait_after": 5}
        ))

        # Шаг 68: Активация нового квеста
        steps.append(TutorialStep(
            step_number=68,
            description='Активируем новый квест - ожидаем long_song_6.png и нажимаем (101, 284) через 1.5 сек',
            action_type="click_with_image_check",
            params={"image_key": "long_song_6", "x": 101, "y": 284, "image_timeout": 25, "click_delay": 1.5}
        ))

        # Шаг 70: Меню строительства (пропускаем 69)
        steps.append(TutorialStep(
            step_number=70,
            description="Открываем меню строительства - клик по (43, 481) через 2.5 секунды",
            action_type="click_coord_with_delay",
            params={"x": 43, "y": 481, "delay": 2.5}
        ))

        # Шаги 71-72: Каюта гребцов
        steps.append(TutorialStep(
            step_number=71,
            description='Выбираем каюту гребцов - ожидаем cannon_long.png и нажимаем (968, 436) через 2.5 сек',
            action_type="click_with_image_check",
            params={"image_key": "cannon_long", "x": 968, "y": 436, "image_timeout": 15, "click_delay": 2.5}
        ))

        steps.append(TutorialStep(
            step_number=72,
            description='Подтверждаем постройку каюты гребцов - ожидаем long_song_6.png и нажимаем (676, 580) через 2.5 сек',
            action_type="click_with_image_check",
            params={"image_key": "long_song_6", "x": 676, "y": 580, "image_timeout": 15, "click_delay": 2.5}
        ))

        # Шаги 74-75: Квесты кают (пропускаем 73)
        steps.append(TutorialStep(
            step_number=74,
            description='Активируем квест "Заполучи кают гребцов: 1" - клик по (123, 280) через 5 секунд',
            action_type="click_coord_with_delay",
            params={"x": 123, "y": 280, "delay": 5}
        ))

        steps.append(TutorialStep(
            step_number=75,
            description='Активируем квест "Заполучи орудийных палуб: 1" - клик по (123, 280) через 3.5 секунды',
            action_type="click_coord_with_delay",
            params={"x": 123, "y": 280, "delay": 3.5}
        ))

        # Шаг 76: Меню строительства
        steps.append(TutorialStep(
            step_number=76,
            description='Открываем меню строительства - клик по (43, 481) через 2.5 секунды',
            action_type="click_coord_with_delay",
            params={"x": 43, "y": 481, "delay": 2.5}
        ))

        # Шаги 77-78: Орудийная палуба
        steps.append(TutorialStep(
            step_number=77,
            description='Выбираем орудийную палубу - ожидаем cannon_long.png и нажимаем (687, 514) + ждем 2.5 сек',
            action_type="click_with_image_check_and_wait",
            params={"image_key": "cannon_long", "x": 687, "y": 514, "image_timeout": 15, "wait_after": 2.5}
        ))

        steps.append(TutorialStep(
            step_number=78,
            description='Подтверждаем постройку орудийной палубы - ожидаем long_song_6.png и нажимаем (679, 581) + ждем 2.5 сек',
            action_type="click_with_image_check_and_wait",
            params={"image_key": "long_song_6", "x": 679, "y": 581, "image_timeout": 15, "wait_after": 2.5}
        ))

        # Шаг 80: Завершение квеста (пропускаем 79)
        steps.append(TutorialStep(
            step_number=80,
            description='Завершаем квест орудийных палуб - клик по (134, 280) через 3 секунды',
            action_type="click_coord_with_delay",
            params={"x": 134, "y": 280, "delay": 3}
        ))

        # Шаги 82-83: Компас и указатель (пропускаем 81)
        steps.append(TutorialStep(
            step_number=82,
            description='Открываем компас - клик по (1072, 87) через 1.5 секунды',
            action_type="click_coord_with_delay",
            params={"x": 1072, "y": 87, "delay": 1.5}
        ))

        steps.append(TutorialStep(
            step_number=83,
            description='Активируем указатель - клик по (698, 273) через 2.5 секунды',
            action_type="click_coord_with_delay",
            params={"x": 698, "y": 273, "delay": 2.5}
        ))

        # Шаг 84: Пропустить
        steps.append(TutorialStep(
            step_number=84,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 86: Компас над кораблем (пропускаем 85)
        steps.append(TutorialStep(
            step_number=86,
            description='Активируем компас над кораблем - ожидаем ship_song.png и нажимаем (652, 214)',
            action_type="click_with_image_check",
            params={"image_key": "ship_song", "x": 652, "y": 214, "image_timeout": 5}
        ))

        # Шаги 87-89: Последовательно пропускаем
        for i in range(87, 90):
            steps.append(TutorialStep(
                step_number=i,
                description=f"Шаг {i}: Ищем и нажимаем ПРОПУСТИТЬ",
                action_type="find_skip_infinite",
                params={"wait_after": 1}
            ))

        # Шаг 90: Квест "Богатая добыча"
        steps.append(TutorialStep(
            step_number=90,
            description='Активируем квест "Богатая добыча" - клик по (89, 280) через 2.5 секунды',
            action_type="click_coord_with_delay",
            params={"x": 89, "y": 280, "delay": 2.5}
        ))

        # Шаг 91: Пропустить
        steps.append(TutorialStep(
            step_number=91,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 92: Диалог с грифоном
        steps.append(TutorialStep(
            step_number=92,
            description="Закрываем диалог с грифоном - ищем griffin.png и нажимаем (1142, 42)",
            action_type="click_with_image_check",
            params={"image_key": "griffin", "x": 1142, "y": 42, "image_timeout": 30}
        ))

        # Шаг 93: Диалог с Молли
        steps.append(TutorialStep(
            step_number=93,
            description="Дожидаемся Молли - ждем 7 сек, затем ищем molly.png и нажимаем (1142, 42) + ждем 3 сек",
            action_type="wait_image_click_and_wait",
            params={"image_key": "molly", "x": 1142, "y": 42, "wait_before": 7, "image_timeout": 40, "wait_after": 3}
        ))

        # Шаг 94: Пропустить
        steps.append(TutorialStep(
            step_number=94,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 95: Сбор монет
        steps.append(TutorialStep(
            step_number=95,
            description="Собираем монеты - ищем coins.png и нажимаем (931, 620)",
            action_type="click_image_or_coord",
            params={"image_key": "coins", "x": 931, "y": 620, "timeout": 25}
        ))

        # Шаг 96: Пропустить
        steps.append(TutorialStep(
            step_number=96,
            description="Ищем и нажимаем ПРОПУСТИТЬ",
            action_type="find_skip_infinite",
            params={}
        ))

        # Шаг 97: Завершение обучения
        steps.append(TutorialStep(
            step_number=97,
            description='Завершаем обучение - ждем 6 сек, проверяем ПРОПУСТИТЬ, затем активируем финальный квест',
            action_type="final_quest_activation",
            params={"x": 89, "y": 280, "wait_before": 6, "skip_timeout": 5, "wait_after_skip": 4}
        ))

        return steps

    def get_steps_from_range(self, start_step: int, end_step: int = 97) -> List[TutorialStep]:
        """
        Получение шагов в указанном диапазоне.

        Args:
            start_step: начальный шаг
            end_step: конечный шаг

        Returns:
            list: список шагов в диапазоне
        """
        return [step for step in self._steps
                if start_step <= step.step_number <= end_step]

    def get_step_by_number(self, step_number: int) -> Optional[TutorialStep]:
        """
        Получение шага по номеру.

        Args:
            step_number: номер шага

        Returns:
            TutorialStep: шаг или None если не найден
        """
        for step in self._steps:
            if step.step_number == step_number:
                return step
        return None

    def get_all_steps(self) -> List[TutorialStep]:
        """
        Получение всех шагов.

        Returns:
            list: список всех шагов
        """
        return self._steps.copy()

    def validate_steps(self) -> bool:
        """
        Валидация конфигурации шагов.

        Returns:
            bool: True если все шаги корректны
        """
        step_numbers = [step.step_number for step in self._steps]

        # Проверка на дубликаты
        if len(step_numbers) != len(set(step_numbers)):
            self.logger.error("Найдены дублирующиеся номера шагов")
            return False

        # Проверка последовательности (с учетом пропущенных шагов)
        step_numbers.sort()
        expected_steps = set(range(1, 98))  # Шаги 1-97
        missing_steps = expected_steps - set(step_numbers)

        if missing_steps:
            self.logger.warning(f"Отсутствуют шаги: {sorted(missing_steps)}")

        return True