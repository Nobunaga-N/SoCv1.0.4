"""
Компоненты пользовательского интерфейса.
"""

from .interface_controller import InterfaceController
from .ocr_handler import OCRHandler
from .server_selector import OptimizedServerSelector

__all__ = ['InterfaceController', 'OCRHandler', 'OptimizedServerSelector']