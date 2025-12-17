# utils/styles.py
"""Shared styles and color schemes for the gaming app - Python 3.14 compatible"""

from __future__ import annotations
import tkinter as tk
from typing import Final, TypedDict
import random
import winsound
import sys
import platform

class ColorScheme(TypedDict):
    primary: str
    secondary: str
    success: str
    danger: str
    warning: str
    info: str
    dark: str
    light: str
    white: str
    background: str
    card: str
    text: str
    text_light: str

class FontStyles(TypedDict):
    title: tuple[str, int, str]
    heading: tuple[str, int, str]
    subheading: tuple[str, int, str]
    body: tuple[str, int]
    button: tuple[str, int, str]
    small: tuple[str, int]

COLORS: Final[ColorScheme] = {
    'primary': '#6C5CE7',
    'secondary': '#A29BFE',
    'success': '#00B894',
    'danger': '#FF7675',
    'warning': '#FDCB6E',
    'info': '#74B9FF',
    'dark': '#2D3436',
    'light': '#DFE6E9',
    'white': '#FFFFFF',
    'background': '#F8F9FA',
    'card': '#FFFFFF',
    'text': '#2D3436',
    'text_light': '#636E72'
}

GAME_COLORS: Final[list[str]] = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
    '#F8B739', '#52B788', '#E76F51', '#264653'
]

FONTS: Final[FontStyles] = {
    'title': ('Segoe UI', 36, 'bold'),
    'heading': ('Segoe UI', 24, 'bold'),
    'subheading': ('Segoe UI', 18, 'bold'),
    'body': ('Segoe UI', 14),
    'button': ('Segoe UI', 16, 'bold'),
    'small': ('Segoe UI', 12)
}

SYMBOL_SETS: Final[dict[str, list[str]]] = {
    'Animals': ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮'],
    'Fruits': ['🍎', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍒', '🍑', '🥭', '🍍'],
    'Numbers': ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🔢', '💯'],
    'Letters': ['🅰️', '🅱️', '🅾️', '🆎', '🆑', '🆒', '🆓', '🆔', '🆕', '🆖', '🆗', '🆘'],
    'Emojis': ['😀', '😎', '🤩', '😍', '🥳', '😊', '😂', '🤣', '😇', '🥰', '😋', '🤗'],
    'Sports': ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🏒', '🏑'],
    'Food': ['🍕', '🍔', '🌭', '🍟', '🍿', '🧁', '🍰', '🎂', '🍪', '🍩', '🍦', '🍨']
}

class SoundManager:
    """Manages game sound effects"""
    
    def __init__(self) -> None:
        self.enabled: bool = True
        self.system: str = platform.system()
    
    def play_click(self) -> None:
        """Play click sound"""
        if not self.enabled:
            return
        try:
            if self.system == 'Windows':
                winsound.Beep(800, 100)
        except Exception:
            pass
    
    def play_match(self) -> None:
        """Play match found sound"""
        if not self.enabled:
            return
        try:
            if self.system == 'Windows':
                winsound.Beep(1000, 200)
        except Exception:
            pass
    
    def play_win(self) -> None:
        """Play win sound"""
        if not self.enabled:
            return
        try:
            if self.system == 'Windows':
                for freq in [523, 659, 784, 1047]:
                    winsound.Beep(freq, 150)
        except Exception:
            pass
    
    def play_error(self) -> None:
        """Play error sound"""
        if not self.enabled:
            return
        try:
            if self.system == 'Windows':
                winsound.Beep(300, 200)
        except Exception:
            pass
    
    def toggle(self) -> bool:
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled

sound_manager = SoundManager()

def create_card_shadow(parent: tk.Widget, bg_color: str = COLORS['card']) -> tuple[tk.Frame, tk.Frame]:
    """Create a card with shadow effect"""
    shadow = tk.Frame(parent, bg=COLORS['light'], bd=0)
    card = tk.Frame(shadow, bg=bg_color, bd=0)
    card.pack(padx=3, pady=3)
    return shadow, card