# utils/__init__.py
"""Utilities package - Python 3.14 compatible"""

from __future__ import annotations
from .styles import COLORS, FONTS, GAME_COLORS, SYMBOL_SETS, sound_manager, create_card_shadow
from .scoreboard import scoreboard, ScoreboardManager

__all__: list[str] = [
    'COLORS', 'FONTS', 'GAME_COLORS', 'SYMBOL_SETS',
    'sound_manager', 'create_card_shadow', 'scoreboard', 'ScoreboardManager'
]
__version__: str = '2.0.0'