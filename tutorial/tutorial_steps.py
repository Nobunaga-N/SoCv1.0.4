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
        steps.append(TutorialStep(
            step_number=7,
            description="Ждем изображения step_7_skip_hell_henry.png, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_7_skip_hell_henry", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        steps.append(TutorialStep(
            step_number=8,
            description="Ждем изображения step_8_skip_ship_word.png, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_8_skip_ship_word", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        steps.append(TutorialStep(
            step_number=9,
            description="Ждем изображения step_9_skip_shark_word.png, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_9_skip_shark_word", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1.0}
        ))

        # Шаг 10: Активация боя
        steps.append(TutorialStep(
            step_number=10,
            description="Ждем изображения step_10_face.png, когда находим кликаем 710:448 (активируем пушку)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_10_face", "x": 710, "y": 448, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 11: Пропустить
        steps.append(TutorialStep(
            step_number=11,
            description="Ждем изображения step_11_skip.png, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_11_skip", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 2}
        ))

        # Шаг 12: Пропустить
        steps.append(TutorialStep(
            step_number=12,
            description="Ждем изображения step_12_skip.png, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_12_skip", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 13: Клик по иконке кораблика
        steps.append(TutorialStep(
            step_number=13,
            description="Ждем изображения step_13.png, когда находим кликаем 58:654 (Нажимаем на иконку кораблика)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_13", "x": 58, "y": 654, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 14: Пропустить
        steps.append(TutorialStep(
            step_number=14,
            description="Ждем изображения step_14_skip.png, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_14_skip", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 15: Нижняя палуба
        steps.append(TutorialStep(
            step_number=15,
            description="Ждем изображения step_15, клик 638:403, задержка 0,5 сек после клика (отстраиваем нижнюю палубу)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_15", "x": 638, "y": 403, "image_timeout": 40, "wait_after": 1.5}
        ))

        # Шаг 16: Паб в нижней палубе
        steps.append(TutorialStep(
            step_number=16,
            description="Ждем изображения step_16, когда находим кликаем 635:373, тайм слип 0,5 сек (Отстраиваем паб в нижней палубе)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_16", "x": 635, "y": 373, "image_timeout": 40, "wait_after": 1.5}
        ))

        # Шаг 17: Латаем дыры в складе
        steps.append(TutorialStep(
            step_number=17,
            description="Ждем изображения step_17, когда находим кликаем 635:373 (Латаем дыры в складе)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_17", "x": 635, "y": 373, "image_timeout": 40, "wait_after": 1.5}
        ))

        # Шаг 18: Пропустить
        steps.append(TutorialStep(
            step_number=18,
            description="Ждем изображения step_18, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_18", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 19: Верхняя палуба
        steps.append(TutorialStep(
            step_number=19,
            description="Ждем изображения step_19, когда находим кликаем 345:386 (Отстраиваем верхнюю палубу)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_19", "x": 345, "y": 386, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 20: Выбираем пушку
        steps.append(TutorialStep(
            step_number=20,
            description="Ждем изображения step_20, когда находим кликаем 77:276 (Выбираем пушку)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_20", "x": 77, "y": 276, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 21: Пропустить
        steps.append(TutorialStep(
            step_number=21,
            description="Ждем изображения step_21, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 22: Сбор предметов
        steps.append(TutorialStep(
            step_number=22,
            description="Ждем изображения step_22, когда находим кликаем 741:145 (квест - собираем предметы)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_22", "x": 741, "y": 145, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 23: Пропустить
        steps.append(TutorialStep(
            step_number=23,
            description="Ждем изображения step_21, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 24: Квест "Старый соперник"
        steps.append(TutorialStep(
            step_number=24,
            description="Ждем изображения step_24, когда находим кликаем 93:285 (Начинаем квест 'Старый соперник')",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_24", "x": 93, "y": 285, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 25: Пропустить
        steps.append(TutorialStep(
            step_number=25,
            description="Ждем изображения step_18, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_18", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 26: Повторная активация квеста "Старый соперник"
        steps.append(TutorialStep(
            step_number=26,
            description="Ждем изображения step_26, когда находим кликаем 93:285 (Повторно активируем квест 'Старый соперник')",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_26", "x": 93, "y": 285, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 27: Пропустить
        steps.append(TutorialStep(
            step_number=27,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 28: Пропустить
        steps.append(TutorialStep(
            step_number=28,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 29: Продолжить после победы
        steps.append(TutorialStep(
            step_number=29,
            description="Ждем изображения step_29, когда находим кликаем 630:413 (Продолжаем после победы - клик по центру экрана)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_29", "x": 630, "y": 413, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 30: Пропустить
        steps.append(TutorialStep(
            step_number=30,
            description="Ждем изображения step_21, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 31: Активируем компас
        steps.append(TutorialStep(
            step_number=31,
            description="Ждем изображения step_31, когда находим кликаем 1074:88 (Активируем компас)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_31", "x": 1074, "y": 88, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 32: Повторно активируем компас
        steps.append(TutorialStep(
            step_number=32,
            description="Ждем изображения step_32, когда находим кликаем 701:258 (Повторно активируем компас)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_32", "x": 701, "y": 258, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 33: Пропустить
        steps.append(TutorialStep(
            step_number=33,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 34: Выход из вкладки компаса
        steps.append(TutorialStep(
            step_number=34,
            description="Ждем изображения step_34, когда находим кликаем 145:25 (Выходим из вкладки компаса)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_34", "x": 145, "y": 25, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 35: Пропустить
        steps.append(TutorialStep(
            step_number=35,
            description="Ждем изображения step_27, когда находим кликаем 1169:42, тайм слип 1.5 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1.5}
        ))

        # Шаг 36: Активация квеста "Далекая песня"
        steps.append(TutorialStep(
            step_number=36,
            description="клик 93:285 (Активируем квест 'Далекая песня')",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 93, "y": 285, "delay": 0, "wait_after": 0.25}
        ))

        # Шаг 37: Пропустить
        steps.append(TutorialStep(
            step_number=37,
            description="Ждем изображения step_18, когда находим кликаем 1169:42, тайм слип 1.5 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_18", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1.5}
        ))

        # Шаг 38: Повторная активация квеста "Далекая песня"
        steps.append(TutorialStep(
            step_number=38,
            description="клик 93:285 (Повторно активируем квест 'Далекая песня')",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 93, "y": 285, "delay": 0, "wait_after": 0.25}
        ))

        # Шаг 39: Пропустить
        steps.append(TutorialStep(
            step_number=39,
            description="Ждем изображения step_39, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_39", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 40: Согласие на обмен
        steps.append(TutorialStep(
            step_number=40,
            description="Ждем изображения step_40, когда находим кликаем 151:349 (Соглашаемся на обмен)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_40", "x": 151, "y": 349, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 41: Пропустить
        steps.append(TutorialStep(
            step_number=41,
            description="Ждем изображения step_21, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 42: Исследование залива Мертвецов
        steps.append(TutorialStep(
            step_number=42,
            description="Ждем изображения step_24, когда находим кликаем 93:285 (Начинаем исследование залива Мертвецов)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_24", "x": 93, "y": 285, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 43: Пропустить
        steps.append(TutorialStep(
            step_number=43,
            description="Ждем изображения step_21, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 44: Подготовка к битве
        steps.append(TutorialStep(
            step_number=44,
            description="Ждем изображения step_44, когда находим кликаем 85:634, тайм слип 1.5 сек (Подготавливаемся к битве)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_44", "x": 85, "y": 634, "image_timeout": 40, "wait_after": 1.5}
        ))

        # Шаг 45: Начало битвы
        steps.append(TutorialStep(
            step_number=45,
            description="клик 1157:604 (начинаем битву)",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 1157, "y": 604, "delay": 0, "wait_after": 2}
        ))

        # Шаг 46: Дожидаемся готовности к битве
        steps.append(TutorialStep(
            step_number=46,
            description="Дожидаемся готовности к битве - ищем step_46",
            action_type="wait_for_battle_ready",
            params={"image_key": "step_46", "max_attempts": 20}
        ))

        # Шаг 47: Дожидаемся корабля
        steps.append(TutorialStep(
            step_number=47,
            description="Продолжаем кликать по центру экрана, пока не увидим step_48, когда находим кликаем 136:283",
            action_type="wait_for_ship",
            params={"image_key": "step_48", "click_x": 136, "click_y": 283, "max_attempts": 30}
        ))

        # Шаг 48: Пропустить
        steps.append(TutorialStep(
            step_number=48,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 49: Активируем следующий этап квеста
        steps.append(TutorialStep(
            step_number=49,
            description="Ждем изображения step_50, когда находим кликаем 136:283 (Активируем следующий этап квеста)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_50", "x": 136, "y": 283, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 50: Пропустить
        steps.append(TutorialStep(
            step_number=50,
            description="Ждем изображения step_27, когда находим кликаем 1169:42, тайм слип 3 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 3.5}
        ))

        # Шаг 51: Активация черепа
        steps.append(TutorialStep(
            step_number=51,
            description="клик 653:403 (Активируем череп в заливе мертвецов)",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 653, "y": 403, "delay": 0, "wait_after": 1.0}
        ))

        # Шаг 52: Пропустить
        steps.append(TutorialStep(
            step_number=52,
            description="Ждем изображения step_18, когда находим кликаем 1169:42,тайм слип 2 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_18", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 2.0}
        ))

        # Шаг 53: Пропустить
        steps.append(TutorialStep(
            step_number=53,
            description="Ждем изображения step_18, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_18", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 2.0}
        ))

        # Шаг 54: Пропустить
        steps.append(TutorialStep(
            step_number=54,
            description="Ждем изображения step_55, когда находим кликаем 1169:42, тайм слип 2 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_55", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 2.5}
        ))

        # Шаг 55: Пропустить
        steps.append(TutorialStep(
            step_number=55,
            description="Ждем изображения step_55, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_55", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 2.0}
        ))

        # Шаг 56: Пропустить
        steps.append(TutorialStep(
            step_number=56,
            description="Ждем изображения step_21, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 57: Продолжить квест
        steps.append(TutorialStep(
            step_number=57,
            description="Ждем изображения step_48, когда находим кликаем 136:283 (Продолжаем квест - 'покинуть залив мертвецов')",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_48", "x": 136, "y": 283, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 58: Пропустить
        steps.append(TutorialStep(
            step_number=58,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 59: Открытие вкладки корабля
        steps.append(TutorialStep(
            step_number=59,
            description="Ждем изображения step_60, когда находим кликаем 125:283 (Открываем вкладку корабля)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_60", "x": 125, "y": 283, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 60: Открытие вкладки построек
        steps.append(TutorialStep(
            step_number=60,
            description="Ждем изображения step_61, когда находим кликаем 42:479 (заходим во вкладку построек)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_61", "x": 42, "y": 479, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 61: Выбор корабля для улучшения
        steps.append(TutorialStep(
            step_number=61,
            description="Ждем изображения step_62, когда находим кликаем 127:216 (Выбираем корабль для улучшения)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_62", "x": 127, "y": 216, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 62: Улучшение корабля
        steps.append(TutorialStep(
            step_number=62,
            description="Ждем изображения step_63, когда находим кликаем 1079:646, тайм слип 2.5 сек (Улучшаем корабль)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_63", "x": 1079, "y": 646, "image_timeout": 40, "wait_after": 3.5}
        ))

        # Шаг 63: Выход из вкладки корабля
        steps.append(TutorialStep(
            step_number=63,
            description="клик 145:25 (Выходим из вкладки корабля)",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 145, "y": 25, "delay": 0, "wait_after": 2}
        ))

        # Шаг 64: Открытие меню постройки
        steps.append(TutorialStep(
            step_number=64,
            description="Ждем изображения step_61, когда находим кликаем 639:603 (Открываем меню постройки)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_61", "x": 639, "y": 603, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 65: Пропустить
        steps.append(TutorialStep(
            step_number=65,
            description="Ждем изображения step_21, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 66: Открытие компаса
        steps.append(TutorialStep(
            step_number=66,
            description="Ждем изображения step_61, когда находим кликаем 1072:87, тайм слип 3 (Открываем вкладку компаса)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_61", "x": 1072, "y": 87, "image_timeout": 40, "wait_after": 9}
        ))

        # Шаг 67: Открытие вкладки строительства
        steps.append(TutorialStep(
            step_number=67,
            description="Ждем изображения step_68, когда находим кликаем 43:481 (открываем вкладку строительства)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_68", "x": 43, "y": 481, "image_timeout": 40, "wait_after": 2}
        ))

        # Шаг 68: Выбор постройки
        steps.append(TutorialStep(
            step_number=68,
            description="Ждем изображения step_69, когда находим кликаем 983:405 (выбираем постройку - каюта гребцов)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_69", "x": 983, "y": 405, "image_timeout": 40, "wait_after": 2.5}
        ))

        # Шаг 69: Подтверждение постройки
        steps.append(TutorialStep(
            step_number=69,
            description="Ждем изображения step_68, когда находим кликаем 676:580, тайм слип 4.5 сек (Подтверждаем постройку каюты гребцов)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_68", "x": 676, "y": 580, "image_timeout": 40, "wait_after": 4.5}
        ))

        # Шаг 70: Активация квеста
        steps.append(TutorialStep(
            step_number=70,
            description="клик 123:280, тайм слип 3 сек (Активируем квест 'Заполучи кают гребцов: 1')",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 123, "y": 280, "delay": 0, "wait_after": 3.0}
        ))

        # Шаг 71: Открытие вкладки построек
        steps.append(TutorialStep(
            step_number=71,
            description="клик 42:479 (открываем вкладку построек)",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 42, "y": 479, "delay": 0, "wait_after": 3}
        ))

        # Шаг 72: Выбор орудийной палубы
        steps.append(TutorialStep(
            step_number=72,
            description="Ждем изображения step_69, когда находим кликаем 687:514 (Выбираем орудийную палубу)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_69", "x": 687, "y": 514, "image_timeout": 40, "wait_after": 3}
        ))

        # Шаг 73: Подтверждение постройки орудийной палубы
        steps.append(TutorialStep(
            step_number=73,
            description="Ждем изображения step_68, когда находим кликаем 679:581, тайм слип 4.5 сек (Подтверждаем постройку орудийной палубы)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_68", "x": 679, "y": 581, "image_timeout": 40, "wait_after": 5.5}
        ))

        # Шаг 74: Завершение квеста орудийных палуб
        steps.append(TutorialStep(
            step_number=74,
            description="клик 119:279, тайм слип 2 сек (Завершаем квест орудийных палуб)",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 119, "y": 279, "delay": 0, "wait_after": 3.5}
        ))

        # Шаг 75: Нажимаем на квест с компасом
        steps.append(TutorialStep(
            step_number=75,
            description="клик 119:279, тайм слип 2 сек (Нажимаем на квест с компасом)",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 119, "y": 279, "delay": 0, "wait_after": 1.5}
        ))

        # Шаг 76: Открытие компаса
        steps.append(TutorialStep(
            step_number=76,
            description="клик 1072:87 (Открываем компас)",
            action_type="click_coord_with_delay_and_wait",
            params={"x": 1072, "y": 87, "delay": 0, "wait_after": 2}
        ))

        # Шаг 77: Активация указателя
        steps.append(TutorialStep(
            step_number=77,
            description="Ждем изображения step_77, когда находим кликаем 698:273 (Активируем указатель)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_77", "x": 698, "y": 273, "image_timeout": 40, "wait_after": 2}
        ))

        # Шаг 78: Пропустить
        steps.append(TutorialStep(
            step_number=78,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1}
        ))

        # Шаг 79: Активация компаса над кораблем
        steps.append(TutorialStep(
            step_number=79,
            description="Ждем изображения step_79, когда находим кликаем 652:214 (Активируем компас над кораблем)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_79", "x": 652, "y": 214, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 80: Пропустить
        steps.append(TutorialStep(
            step_number=80,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 4.5}
        ))

        # Шаг 81: Пропустить
        steps.append(TutorialStep(
            step_number=81,
            description="Ждем изображения step_21, когда находим кликаем 1169:42, тайм слип 1 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1.5}
        ))

        # Шаг 82: Пропустить
        steps.append(TutorialStep(
            step_number=82,
            description="Ждем изображения step_21, когда находим кликаем 1169:42, тайм слип 1 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_21", "x": 1169, "y": 42, "image_timeout": 40, "click_delay": 1.5,
                    "wait_after": 1.5}
        ))

        # Шаг 83: Активация квеста "Богатая добыча"
        steps.append(TutorialStep(
            step_number=83,
            description="Ждем изображения step_82, когда находим кликаем 151:280 (Активируем квест 'Богатая добыча')",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_82", "x": 151, "y": 280, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 84: Пропустить
        steps.append(TutorialStep(
            step_number=84,
            description="Ждем изображения step_27, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_27", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.5}
        ))

        # Шаг 85: Пропустить
        steps.append(TutorialStep(
            step_number=85,
            description="Ждем изображения step_84, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_84", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 0.25}
        ))

        # Шаг 86: Пропустить
        steps.append(TutorialStep(
            step_number=86,
            description="Ждем изображения step_85, когда находим кликаем 1169:42, тайм слип 1 сек (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_85", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 2.0}
        ))

        # Шаг 87: Пропустить
        steps.append(TutorialStep(
            step_number=87,
            description="Ждем изображения step_85, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_85", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 2.0}
        ))

        # Шаг 88: Сбор монет
        steps.append(TutorialStep(
            step_number=88,
            description="Ждем изображения step_87, когда находим кликаем 931:620 (Собираем монеты)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_87", "x": 931, "y": 620, "image_timeout": 40, "wait_after": 2.0}
        ))

        # Шаг 89: Пропустить
        steps.append(TutorialStep(
            step_number=89,
            description="Ждем изображения step_88, когда находим кликаем 1169:42 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_88", "x": 1169, "y": 42, "image_timeout": 40, "wait_after": 1.0}
        ))

        # Шаг 90: Пропустить
        steps.append(TutorialStep(
            step_number=90,
            description="Ждем изображения step_89, когда находим кликаем 150:277 (скип)",
            action_type="click_with_image_check_and_wait",
            params={"image_key": "step_89", "x": 150, "y": 277, "image_timeout": 40, "wait_after": 0.25}
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