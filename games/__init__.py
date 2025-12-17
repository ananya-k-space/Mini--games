# games/__init__.py
"""Games package - Python 3.14 compatible"""

from __future__ import annotations
from .memory_match import MemoryMatchGame
from .number_rush import NumberRushGame
from .color_blast import ColorBlastGame

__all__: list[str] = ['MemoryMatchGame', 'NumberRushGame', 'ColorBlastGame']
__version__: str = '2.0.0'