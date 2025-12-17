# game_menu.py
"""Main menu screen for game selection - Python 3.14 compatible"""

from __future__ import annotations
import tkinter as tk
from typing import Callable, TypedDict, Final
from utils.styles import COLORS, FONTS
from games.memory_match import MemoryMatchGame
from games.number_rush import NumberRushGame
from games.color_blast import ColorBlastGame

class GameInfo(TypedDict):
    name: str
    icon: str
    desc: str
    color: str
    command: Callable[[], None]

class GameMenu:
    """Main menu for game selection"""
    
    def __init__(self, parent: tk.Tk) -> None:
        self.parent: tk.Tk = parent
        self.current_game: MemoryMatchGame | NumberRushGame | ColorBlastGame | None = None
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup the user interface"""
        # Force parent to update
        self.parent.update_idletasks()
        
        self.frame = tk.Frame(self.parent, bg=COLORS['background'])
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(self.frame, bg=COLORS['primary'])
        header.pack(fill=tk.X)
        
        title_container = tk.Frame(header, bg=COLORS['primary'])
        title_container.pack(pady=30)
        
        title = tk.Label(
            title_container, text="🎮 Mini Games", 
            font=('Segoe UI', 48, 'bold'),
            bg=COLORS['primary'], fg=COLORS['white']
        )
        title.pack()
        
        subtitle = tk.Label(
            title_container, text="Choose your favorite game!",
            font=FONTS['subheading'], bg=COLORS['primary'],
            fg=COLORS['light']
        )
        subtitle.pack(pady=(5, 0))
        
        # Main content area - centered
        content_area = tk.Frame(self.frame, bg=COLORS['background'])
        content_area.pack(fill=tk.BOTH, expand=True)
        
        # Games container - centered within content area
        games_container = tk.Frame(content_area, bg=COLORS['background'])
        games_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        games: Final[list[GameInfo]] = [
            {
                'name': 'Memory Match',
                'icon': '🧠',
                'desc': 'Find matching pairs',
                'color': COLORS['primary'],
                'command': self.launch_memory_match
            },
            {
                'name': 'Number Rush',
                'icon': '⚡',
                'desc': 'Click numbers in order',
                'color': COLORS['info'],
                'command': self.launch_number_rush
            },
            {
                'name': 'Color Blast',
                'icon': '🎨',
                'desc': 'Match colors quickly',
                'color': COLORS['warning'],
                'command': self.launch_color_blast
            }
        ]
        
        for i, game in enumerate(games):
            self._create_game_card(games_container, game, i)
        
        # Footer
        footer = tk.Label(
            self.frame, text="Made for fun with Python ❤️",
            font=FONTS['small'], bg=COLORS['background'],
            fg=COLORS['text_light']
        )
        footer.pack(side=tk.BOTTOM, pady=20)
    
    def _create_game_card(
        self, 
        container: tk.Frame, 
        game: GameInfo, 
        column: int
    ) -> None:
        """Create a game card in the menu"""
        # Main card frame
        card = tk.Frame(
            container, 
            bg=COLORS['card'], 
            cursor='hand2',
            relief=tk.RAISED,
            bd=2
        )
        card.grid(row=0, column=column, padx=15, pady=15)
        
        # Icon area with game color
        icon_frame = tk.Frame(card, bg=game['color'], width=200, height=120)
        icon_frame.pack(fill=tk.X)
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(
            icon_frame, 
            text=game['icon'], 
            font=('Segoe UI', 50),
            bg=game['color'], 
            fg=COLORS['white']
        )
        icon_label.pack(expand=True)
        
        # Info area
        info_frame = tk.Frame(card, bg=COLORS['card'])
        info_frame.pack(fill=tk.BOTH, padx=20, pady=15)
        
        name_label = tk.Label(
            info_frame, 
            text=game['name'],
            font=FONTS['heading'], 
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        name_label.pack()
        
        desc_label = tk.Label(
            info_frame, 
            text=game['desc'],
            font=FONTS['body'], 
            bg=COLORS['card'],
            fg=COLORS['text_light']
        )
        desc_label.pack(pady=5)
        
        # Play button - using a frame to ensure proper background
        btn_container = tk.Frame(info_frame, bg=COLORS['card'])
        btn_container.pack(pady=10)
        
        play_btn = tk.Button(
            btn_container, 
            text="▶ Play Now",
            font=FONTS['button'], 
            bg=game['color'],
            fg=COLORS['white'], 
            bd=0, 
            cursor='hand2',
            padx=25, 
            pady=8, 
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=game['command']
        )
        play_btn.pack()
        
        # Hover effects for card
        def on_enter(e: tk.Event) -> None:
            card.config(relief=tk.GROOVE, bd=3)
        
        def on_leave(e: tk.Event) -> None:
            card.config(relief=tk.RAISED, bd=2)
        
        # Hover effects for button
        def on_btn_enter(e: tk.Event) -> None:
            play_btn.config(bg=COLORS['dark'])
        
        def on_btn_leave(e: tk.Event) -> None:
            play_btn.config(bg=game['color'])
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        play_btn.bind('<Enter>', on_btn_enter)
        play_btn.bind('<Leave>', on_btn_leave)
    
    def launch_memory_match(self) -> None:
        """Launch the Memory Match game"""
        self.frame.pack_forget()
        self.current_game = MemoryMatchGame(self.parent, self.show_menu)
    
    def launch_number_rush(self) -> None:
        """Launch the Number Rush game"""
        self.frame.pack_forget()
        self.current_game = NumberRushGame(self.parent, self.show_menu)
    
    def launch_color_blast(self) -> None:
        """Launch the Color Blast game"""
        self.frame.pack_forget()
        self.current_game = ColorBlastGame(self.parent, self.show_menu)
    
    def show_menu(self) -> None:
        """Show the main menu"""
        if self.current_game:
            self.current_game = None
        self.frame.pack(fill=tk.BOTH, expand=True)