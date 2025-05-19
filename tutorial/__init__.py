"""
Компоненты обучения.
"""


from .tutorial_executor import TutorialExecutor
from .tutorial_steps import TutorialSteps, TutorialStep
from .skip_button_finder import UltraFastSkipButtonFinder

__all__ = ['TutorialExecutor', 'TutorialSteps', 'TutorialStep', 'UltraFastSkipButtonFinder']