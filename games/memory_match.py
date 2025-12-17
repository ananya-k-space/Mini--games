# games/memory_match.py
"""Memory Match Game - Multilevel & Multiplayer - Python 3.14 compatible"""

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
import random
import sys
from typing import Callable, Final, TypedDict
from datetime import datetime

# Fallback implementations if utils modules don't exist
try:
    from utils.styles import COLORS, FONTS, SYMBOL_SETS, sound_manager
except ImportError:
    COLORS = {
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
        'text_light': '#636E72',
    }
    
    FONTS = {
        'heading': ('Segoe UI', 24, 'bold'),
        'subheading': ('Segoe UI', 18, 'bold'),
        'body': ('Segoe UI', 14),
        'small': ('Segoe UI', 12),
        'button': ('Segoe UI', 16, 'bold'),
    }
    
    SYMBOL_SETS = {
        'Animals': ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮'],
        'Fruits': ['🍎', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍒', '🍑', '🥭', '🍍'],
        'Numbers': ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🔢', '💯'],
        'Letters': ['🅰️', '🅱️', '🅾️', '🆎', '🆑', '🆒', '🆓', '🆔', '🆕', '🆖', '🆗', '🆘'],
        'Emojis': ['😀', '😎', '🤩', '😍', '🥳', '😊', '😂', '🤣', '😇', '🥰', '😋', '🤗'],
        'Sports': ['⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🏒', '🏑'],
        'Food': ['🍕', '🍔', '🌭', '🍟', '🍿', '🧁', '🍰', '🎂', '🍪', '🍩', '🍦', '🍨']
    }
    
    class SoundManager:
        """Fallback sound manager"""
        def __init__(self):
            self.enabled = True
        
        def play_click(self):
            pass
        
        def play_match(self):
            pass
        
        def play_error(self):
            pass
        
        def play_win(self):
            pass
        
        def toggle(self) -> bool:
            self.enabled = not self.enabled
            return self.enabled
    
    sound_manager = SoundManager()

try:
    from utils.scoreboard import scoreboard
except ImportError:
    class Scoreboard:
        """Fallback scoreboard"""
        def __init__(self):
            self.scores: dict[str, list] = {}
        
        def add_score(self, game: str, name: str, score: int, level: int) -> None:
            if game not in self.scores:
                self.scores[game] = []
            self.scores[game].append({
                'name': name,
                'score': score,
                'level': level,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            self.scores[game].sort(key=lambda x: x['score'], reverse=True)
        
        def get_top_scores(self, game: str, limit: int = 10) -> list:
            if game not in self.scores:
                return []
            return self.scores[game][:limit]
    
    scoreboard = Scoreboard()


class CardData(TypedDict):
    canvas: tk.Canvas
    symbol: str
    flipped: bool
    matched: bool


class PlayerData(TypedDict):
    name: str
    score: int
    matches: int
    streak: int


class MemoryMatchGame:
    """Memory Match Game - Find matching pairs of cards"""
    
    LEVELS: Final[dict[int, dict[str, int]]] = {
        1: {'grid': 4, 'pairs': 8, 'bonus': 100},
        2: {'grid': 4, 'pairs': 8, 'bonus': 150},
        3: {'grid': 5, 'pairs': 12, 'bonus': 200},
        4: {'grid': 6, 'pairs': 18, 'bonus': 300},
        5: {'grid': 6, 'pairs': 18, 'bonus': 500},
    }
    
    CARD_COLORS: Final[list[str]] = [
        '#6C5CE7', '#74B9FF', '#00B894', '#FDCB6E',
        '#E17055', '#A29BFE', '#81ECEC', '#FAB1A0'
    ]
    
    def __init__(self, parent: tk.Tk | tk.Frame, on_back: Callable[[], None]) -> None:
        self.parent: tk.Tk | tk.Frame = parent
        self.on_back: Callable[[], None] = on_back
        self.cards: list[CardData] = []
        self.flipped: list[int] = []
        self.matched: list[int] = []
        self.moves: int = 0
        self.check_id: str | None = None
        
        self.num_players: int = 1
        self.current_player: int = 0
        self.players: list[PlayerData] = []
        
        self.current_level: int = 1
        self.symbol_set: str = 'Animals'
        self.grid_size: int = 4
        self.total_pairs: int = 8
        
        # Initialize UI elements to None
        self.setup_frame: tk.Frame | None = None
        self.main_canvas: tk.Canvas | None = None
        self.scrollbar: tk.Scrollbar | None = None
        self.scrollable_frame: tk.Frame | None = None
        self.canvas_frame: int | None = None
        self.level_label: tk.Label | None = None
        self.moves_label: tk.Label | None = None
        self.pairs_label: tk.Label | None = None
        self.progress_bar: ttk.Progressbar | None = None
        self.progress_label: tk.Label | None = None
        self.sound_btn: tk.Button | None = None
        self.player_frame: tk.Frame | None = None
        self.player_cards: list[tuple[tk.Frame, tk.Label, tk.Label]] = []
        self.grid_container: tk.Frame | None = None
        
        self.show_smooth_setup()
    
    def show_smooth_setup(self) -> None:
        """Embedded setup screen - no Toplevel"""
        self.setup_frame = tk.Frame(self.parent, bg=COLORS['background'])
        self.setup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(self.setup_frame, bg=COLORS['primary'])
        header.pack(fill=tk.X)
        
        tk.Button(
            header, text="← Back to Menu", font=FONTS['body'],
            bg=COLORS['primary'], fg=COLORS['white'], bd=0,
            cursor='hand2', padx=15, pady=8,
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=self._cancel_setup
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(
            header, text="🧠 Memory Match Setup",
            font=('Segoe UI', 28, 'bold'), bg=COLORS['primary'],
            fg=COLORS['white']
        ).pack(pady=20)
        
        # Scrollable content
        canvas = tk.Canvas(self.setup_frame, bg=COLORS['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.setup_frame, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=COLORS['background'])
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make canvas window expand to fill width
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def on_mousewheel(e):
            if sys.platform == 'darwin':
                canvas.yview_scroll(int(-1 * e.delta), "units")
            else:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        
        def on_mousewheel_linux(e):
            if e.num == 4:
                canvas.yview_scroll(-1, "units")
            elif e.num == 5:
                canvas.yview_scroll(1, "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel_linux)
        canvas.bind_all("<Button-5>", on_mousewheel_linux)
        
        # Store canvas reference for cleanup
        self._setup_canvas = canvas
        
        # Center container
        center_frame = tk.Frame(content, bg=COLORS['background'])
        center_frame.pack(expand=True, pady=20)
        
        # === PLAYERS SECTION ===
        tk.Label(
            center_frame, text="👥 Number of Players", font=FONTS['heading'],
            bg=COLORS['background'], fg=COLORS['text']
        ).pack(pady=10)
        
        player_var = tk.IntVar(value=1)
        player_btns = tk.Frame(center_frame, bg=COLORS['background'])
        player_btns.pack(pady=8)
        
        for i in range(1, 5):
            tk.Radiobutton(
                player_btns, text=f"{i} {'Player' if i == 1 else 'Players'}",
                variable=player_var, value=i, font=FONTS['body'],
                bg=COLORS['background'], fg=COLORS['text'],
                selectcolor=COLORS['success'], cursor='hand2',
                activebackground=COLORS['background'],
                command=lambda: sound_manager.play_click()
            ).pack(side=tk.LEFT, padx=12)
        
        # === NAMES SECTION ===
        tk.Label(
            center_frame, text="📝 Player Names", font=FONTS['heading'],
            bg=COLORS['background'], fg=COLORS['text']
        ).pack(pady=(20, 10))
        
        names_frame = tk.Frame(center_frame, bg=COLORS['background'])
        names_frame.pack(pady=8, fill=tk.X, padx=40)
        
        entries: list[tk.Entry] = []
        entry_frames: list[tk.Frame] = []
        
        for i in range(4):
            row = tk.Frame(names_frame, bg=COLORS['card'], relief=tk.SOLID, bd=1)
            entry_frames.append(row)
            
            tk.Label(
                row, text=f"Player {i + 1}:", font=FONTS['body'],
                bg=COLORS['card'], width=10, anchor='w'
            ).pack(side=tk.LEFT, padx=10, pady=10)
            
            entry = tk.Entry(
                row, font=FONTS['body'], bg=COLORS['white'],
                fg=COLORS['text'], relief=tk.FLAT, bd=0
            )
            entry.insert(0, f"Player {i + 1}")
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
            entries.append(entry)
            
            # Select all on click
            def on_entry_click(e, ent=entry):
                ent.select_range(0, tk.END)
            entry.bind('<Button-1>', on_entry_click)
        
        def update_name_fields():
            sound_manager.play_click()
            for f in entry_frames:
                f.pack_forget()
            for i in range(player_var.get()):
                entry_frames[i].pack(pady=5, fill=tk.X)
        
        # Update radiobuttons to call update function
        for rb in player_btns.winfo_children():
            rb.config(command=update_name_fields)
        
        update_name_fields()
        
        # === THEME SECTION ===
        tk.Label(
            center_frame, text="🎨 Choose Theme", font=FONTS['heading'],
            bg=COLORS['background'], fg=COLORS['text']
        ).pack(pady=(20, 10))
        
        theme_var = tk.StringVar(value='Animals')
        themes_frame = tk.Frame(center_frame, bg=COLORS['background'])
        themes_frame.pack(pady=8)
        
        row_idx, col_idx = 0, 0
        for name, symbols in SYMBOL_SETS.items():
            card = tk.Frame(
                themes_frame, bg=COLORS['card'],
                relief=tk.SOLID, bd=1, cursor='hand2'
            )
            card.grid(row=row_idx, column=col_idx, padx=6, pady=6, sticky='ew')
            
            tk.Radiobutton(
                card, text=name, variable=theme_var, value=name,
                font=FONTS['small'], bg=COLORS['card'], fg=COLORS['text'],
                selectcolor=COLORS['primary'], cursor='hand2',
                activebackground=COLORS['card'],
                command=lambda: sound_manager.play_click()
            ).pack(pady=5)
            
            tk.Label(
                card, text=" ".join(symbols[:3]), font=('Segoe UI', 16),
                bg=COLORS['card']
            ).pack(pady=5)
            
            # Click on card to select
            def on_theme_click(e, n=name):
                theme_var.set(n)
                sound_manager.play_click()
            
            def on_theme_enter(e, c=card):
                c.config(bg=COLORS['light'])
                for child in c.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=COLORS['light'])
            
            def on_theme_leave(e, c=card):
                c.config(bg=COLORS['card'])
                for child in c.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=COLORS['card'])
            
            card.bind('<Button-1>', on_theme_click)
            card.bind('<Enter>', on_theme_enter)
            card.bind('<Leave>', on_theme_leave)
            
            col_idx += 1
            if col_idx > 2:
                col_idx, row_idx = 0, row_idx + 1
        
        # === DIFFICULTY SECTION ===
        tk.Label(
            center_frame, text="🎯 Difficulty", font=FONTS['heading'],
            bg=COLORS['background'], fg=COLORS['text']
        ).pack(pady=(20, 10))
        
        level_var = tk.IntVar(value=1)
        levels_frame = tk.Frame(center_frame, bg=COLORS['background'])
        levels_frame.pack(pady=8, fill=tk.X, padx=40)
        
        levels = [
            (1, "⭐ Easy", "4x4 Grid • 8 pairs", COLORS['success']),
            (2, "⭐⭐ Medium", "4x4 Grid • 8 pairs", COLORS['info']),
            (3, "⭐⭐⭐ Hard", "5x5 Grid • 12 pairs", COLORS['warning']),
            (4, "⭐⭐⭐⭐ Very Hard", "6x6 Grid • 18 pairs", COLORS['danger']),
            (5, "⭐⭐⭐⭐⭐ Expert", "6x6 Grid • 18 pairs", COLORS['primary']),
        ]
        
        for level, name, desc, color in levels:
            card = tk.Frame(levels_frame, bg=COLORS['card'], relief=tk.SOLID, bd=1, cursor='hand2')
            card.pack(pady=4, fill=tk.X)
            
            tk.Radiobutton(
                card, text=name, variable=level_var, value=level,
                font=FONTS['body'], bg=COLORS['card'], fg=color,
                selectcolor=color, cursor='hand2',
                activebackground=COLORS['card'],
                command=lambda: sound_manager.play_click()
            ).pack(side=tk.LEFT, padx=12, pady=10)
            
            tk.Label(
                card, text=desc, font=FONTS['small'], bg=COLORS['card'],
                fg=COLORS['text_light']
            ).pack(side=tk.LEFT)
            
            # Click on card to select
            def on_level_click(e, lv=level):
                level_var.set(lv)
                sound_manager.play_click()
            
            def on_level_enter(e, c=card):
                c.config(bg=COLORS['light'])
                for child in c.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=COLORS['light'])
            
            def on_level_leave(e, c=card):
                c.config(bg=COLORS['card'])
                for child in c.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=COLORS['card'])
            
            card.bind('<Button-1>', on_level_click)
            card.bind('<Enter>', on_level_enter)
            card.bind('<Leave>', on_level_leave)
        
        # === START BUTTON ===
        btn_frame = tk.Frame(center_frame, bg=COLORS['background'])
        btn_frame.pack(pady=30)
        
        def start_game():
            num = player_var.get()
            
            self.players.clear()
            for i in range(num):
                name = entries[i].get().strip() or f"Player {i + 1}"
                self.players.append({
                    'name': name,
                    'score': 0,
                    'matches': 0,
                    'streak': 0
                })
            
            self.num_players = num
            self.symbol_set = theme_var.get()
            self.current_level = level_var.get()
            self.grid_size = self.LEVELS[self.current_level]['grid']
            self.total_pairs = self.LEVELS[self.current_level]['pairs']
            
            sound_manager.play_click()
            
            # Clean up setup
            try:
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
            except tk.TclError:
                pass
            
            if self.setup_frame:
                self.setup_frame.destroy()
                self.setup_frame = None
            
            # Start game
            self.setup_ui()
            self.start_level()
        
        start_btn = tk.Button(
            btn_frame, text="🎮 START GAME", font=('Segoe UI', 18, 'bold'),
            bg=COLORS['success'], fg=COLORS['white'], bd=0,
            cursor='hand2', padx=60, pady=15,
            activebackground=COLORS['primary'],
            activeforeground=COLORS['white'],
            command=start_game
        )
        start_btn.pack()
        
        def on_start_enter(e):
            start_btn.config(bg=COLORS['primary'])
        
        def on_start_leave(e):
            start_btn.config(bg=COLORS['success'])
        
        start_btn.bind('<Enter>', on_start_enter)
        start_btn.bind('<Leave>', on_start_leave)
    
    def _cancel_setup(self) -> None:
        """Cancel setup and go back to menu"""
        # Clean up bindings
        if hasattr(self, '_setup_canvas'):
            try:
                self._setup_canvas.unbind_all("<MouseWheel>")
                self._setup_canvas.unbind_all("<Button-4>")
                self._setup_canvas.unbind_all("<Button-5>")
            except tk.TclError:
                pass
        
        if self.setup_frame:
            try:
                self.setup_frame.destroy()
            except tk.TclError:
                pass
            self.setup_frame = None
        
        self.on_back()
    
    def setup_ui(self) -> None:
        """Setup game UI"""
        self.main_canvas = tk.Canvas(self.parent, bg=COLORS['background'], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg=COLORS['background'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.canvas_frame = self.main_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Make scrollable frame expand to canvas width
        def configure_scroll_region(event):
            self.main_canvas.itemconfig(self.canvas_frame, width=event.width)
        
        self.main_canvas.bind('<Configure>', configure_scroll_region)
        
        # Cross-platform mouse wheel scrolling
        def on_mousewheel(event):
            if sys.platform == 'darwin':
                self.main_canvas.yview_scroll(int(-1 * event.delta), "units")
            else:
                self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def on_mousewheel_linux(event):
            if event.num == 4:
                self.main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(1, "units")
        
        self.main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.main_canvas.bind_all("<Button-4>", on_mousewheel_linux)
        self.main_canvas.bind_all("<Button-5>", on_mousewheel_linux)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Header
        header = tk.Frame(self.scrollable_frame, bg=COLORS['primary'])
        header.pack(fill=tk.X)
        
        top_bar = tk.Frame(header, bg=COLORS['primary'])
        top_bar.pack(fill=tk.X, pady=8)
        
        tk.Button(
            top_bar, text="← Back", font=FONTS['body'],
            bg=COLORS['primary'], fg=COLORS['white'],
            bd=0, cursor='hand2',
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=self.back_to_menu
        ).pack(side=tk.LEFT, padx=20)
        
        self.sound_btn = tk.Button(
            top_bar, text="🔊", font=FONTS['body'],
            bg=COLORS['primary'], fg=COLORS['white'],
            bd=0, cursor='hand2', width=3,
            activebackground=COLORS['dark'],
            command=self.toggle_sound
        )
        self.sound_btn.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            header, text="🧠 Memory Match", font=('Segoe UI', 32, 'bold'),
            bg=COLORS['primary'], fg=COLORS['white']
        ).pack(pady=15)
        
        # Progress bar
        prog_frame = tk.Frame(header, bg=COLORS['primary'])
        prog_frame.pack(fill=tk.X, padx=50, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=COLORS['light'],
            background=COLORS['success'],
            thickness=20
        )
        
        self.progress_bar = ttk.Progressbar(
            prog_frame, style="Custom.Horizontal.TProgressbar",
            mode='determinate', length=400
        )
        self.progress_bar.pack()
        
        self.progress_label = tk.Label(
            prog_frame, text="0% Complete",
            font=FONTS['body'], bg=COLORS['primary'],
            fg=COLORS['white']
        )
        self.progress_label.pack(pady=5)
        
        # Stats
        stats_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        stats_frame.pack(pady=20)
        
        # Level stat
        level_card = tk.Frame(stats_frame, bg=COLORS['card'], relief=tk.RAISED, bd=2)
        level_card.pack(side=tk.LEFT, padx=12)
        tk.Label(
            level_card, text="LEVEL", font=FONTS['small'],
            bg=COLORS['card'], fg=COLORS['text_light']
        ).pack(pady=(15, 5), padx=25)
        self.level_label = tk.Label(
            level_card, text=str(self.current_level),
            font=('Segoe UI', 36, 'bold'),
            bg=COLORS['card'], fg=COLORS['primary']
        )
        self.level_label.pack(pady=(5, 15), padx=25)
        
        # Moves stat
        moves_card = tk.Frame(stats_frame, bg=COLORS['card'], relief=tk.RAISED, bd=2)
        moves_card.pack(side=tk.LEFT, padx=12)
        tk.Label(
            moves_card, text="MOVES", font=FONTS['small'],
            bg=COLORS['card'], fg=COLORS['text_light']
        ).pack(pady=(15, 5), padx=25)
        self.moves_label = tk.Label(
            moves_card, text="0",
            font=('Segoe UI', 36, 'bold'),
            bg=COLORS['card'], fg=COLORS['info']
        )
        self.moves_label.pack(pady=(5, 15), padx=25)
        
        # Pairs stat
        pairs_card = tk.Frame(stats_frame, bg=COLORS['card'], relief=tk.RAISED, bd=2)
        pairs_card.pack(side=tk.LEFT, padx=12)
        tk.Label(
            pairs_card, text="PAIRS", font=FONTS['small'],
            bg=COLORS['card'], fg=COLORS['text_light']
        ).pack(pady=(15, 5), padx=25)
        self.pairs_label = tk.Label(
            pairs_card, text=f"0/{self.total_pairs}",
            font=('Segoe UI', 36, 'bold'),
            bg=COLORS['card'], fg=COLORS['success']
        )
        self.pairs_label.pack(pady=(5, 15), padx=25)
        
        # Player scores
        self.player_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        self.player_frame.pack(pady=15)
        
        self.player_cards = []
        for i, player in enumerate(self.players):
            card = tk.Frame(
                self.player_frame, bg=COLORS['card'],
                relief=tk.RAISED, bd=3
            )
            card.pack(side=tk.LEFT, padx=10)
            
            tk.Label(
                card, text=f"👤 {player['name']}", font=FONTS['subheading'],
                bg=COLORS['card'], fg=COLORS['text']
            ).pack(pady=(12, 5), padx=20)
            
            score_lbl = tk.Label(
                card, text="0 pts", font=('Segoe UI', 22, 'bold'),
                bg=COLORS['card'], fg=COLORS['success']
            )
            score_lbl.pack(pady=5)
            
            streak_lbl = tk.Label(
                card, text="", font=FONTS['body'],
                bg=COLORS['card'], fg=COLORS['warning']
            )
            streak_lbl.pack(pady=(5, 12))
            
            self.player_cards.append((card, score_lbl, streak_lbl))
        
        # Control buttons
        btn_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame, text="🔄 Restart", font=FONTS['button'],
            bg=COLORS['info'], fg=COLORS['white'],
            bd=0, cursor='hand2', padx=30, pady=12,
            activebackground=COLORS['primary'],
            activeforeground=COLORS['white'],
            command=self.start_level
        ).pack(side=tk.LEFT, padx=8)
        
        tk.Button(
            btn_frame, text="🏆 Leaderboard", font=FONTS['button'],
            bg=COLORS['warning'], fg=COLORS['white'],
            bd=0, cursor='hand2', padx=30, pady=12,
            activebackground=COLORS['primary'],
            activeforeground=COLORS['white'],
            command=self.show_scoreboard
        ).pack(side=tk.LEFT, padx=8)
        
        # Grid container
        self.grid_container = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        self.grid_container.pack(expand=True, pady=20)
        
        # Instructions
        tk.Label(
            self.scrollable_frame,
            text="💡 Match pairs to score! Get 3+ in a row for streak bonuses!",
            font=FONTS['body'], bg=COLORS['background'],
            fg=COLORS['text_light']
        ).pack(pady=15)
    
    def toggle_sound(self) -> None:
        """Toggle sound on/off"""
        enabled = sound_manager.toggle()
        if self.sound_btn:
            self.sound_btn.config(text="🔊" if enabled else "🔇")
        sound_manager.play_click()
    
    def start_level(self) -> None:
        """Start or restart the current level"""
        self.cards = []
        self.flipped = []
        self.matched = []
        self.moves = 0
        
        # Reset player stats for restart
        for player in self.players:
            player['matches'] = 0
            player['streak'] = 0
        
        self.current_player = 0
        
        self.update_stats()
        self.update_player_display()
        
        # Clear existing grid
        if self.grid_container:
            for widget in self.grid_container.winfo_children():
                widget.destroy()
        
        # Create card symbols
        symbols = SYMBOL_SETS[self.symbol_set][:self.total_pairs] * 2
        random.shuffle(symbols)
        
        # Create grid
        grid = tk.Frame(self.grid_container, bg=COLORS['background'])
        grid.pack()
        
        idx = 0
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if idx >= len(symbols):
                    break
                
                # Card canvas
                card_canvas = tk.Canvas(
                    grid, width=80, height=80, bg=COLORS['card'],
                    highlightthickness=3, highlightbackground=COLORS['light'],
                    cursor='hand2'
                )
                card_canvas.grid(row=i, column=j, padx=5, pady=5)
                
                # Draw card back (question mark)
                card_canvas.create_text(
                    40, 40, text="?",
                    font=('Segoe UI', 28, 'bold'),
                    fill=COLORS['text_light'],
                    tags="back"
                )
                
                # Bind click event
                card_canvas.bind('<Button-1>', lambda e, index=idx: self.flip_card(index))
                
                # Hover effects
                def on_enter(e, c=card_canvas):
                    if c.cget('highlightbackground') != COLORS['success']:
                        c.config(highlightbackground=COLORS['primary'])
                
                def on_leave(e, c=card_canvas):
                    if c.cget('highlightbackground') != COLORS['success']:
                        c.config(highlightbackground=COLORS['light'])
                
                card_canvas.bind('<Enter>', on_enter)
                card_canvas.bind('<Leave>', on_leave)
                
                self.cards.append({
                    'canvas': card_canvas,
                    'symbol': symbols[idx],
                    'flipped': False,
                    'matched': False
                })
                
                idx += 1
    
    def flip_card(self, idx: int) -> None:
        """Flip a card"""
        if idx >= len(self.cards):
            return
        
        card = self.cards[idx]
        
        # Ignore if already flipped, matched, or two cards already flipped
        if card['flipped'] or card['matched'] or len(self.flipped) >= 2:
            return
        
        sound_manager.play_click()
        
        # Flip the card - show symbol
        canvas = card['canvas']
        canvas.delete('all')
        
        # Draw colored background
        bg_color = random.choice(self.CARD_COLORS)
        canvas.create_rectangle(0, 0, 80, 80, fill=bg_color, outline='')
        
        # Draw symbol
        canvas.create_text(
            40, 40, text=card['symbol'],
            font=('Segoe UI', 32),
            fill=COLORS['white']
        )
        
        card['flipped'] = True
        self.flipped.append(idx)
        
        # Check for match if two cards flipped
        if len(self.flipped) == 2:
            self.moves += 1
            self.update_stats()
            self.check_id = self.parent.after(600, self.check_match)
    
    def check_match(self) -> None:
        """Check if the two flipped cards match"""
        if len(self.flipped) != 2:
            return
        
        idx1, idx2 = self.flipped
        card1, card2 = self.cards[idx1], self.cards[idx2]
        
        if card1['symbol'] == card2['symbol']:
            # Match found!
            sound_manager.play_match()
            
            card1['matched'] = card2['matched'] = True
            self.matched.extend([idx1, idx2])
            
            # Show matched state
            for i in [idx1, idx2]:
                canvas = self.cards[i]['canvas']
                canvas.delete('all')
                canvas.create_rectangle(0, 0, 80, 80, fill=COLORS['success'], outline='')
                canvas.create_text(
                    40, 40, text='✓',
                    font=('Segoe UI', 36, 'bold'),
                    fill=COLORS['white']
                )
                canvas.config(highlightbackground=COLORS['success'])
            
            # Update player score
            player = self.players[self.current_player]
            player['matches'] += 1
            player['streak'] += 1
            
            # Calculate score with streak bonus
            base_score = 10 * self.current_level
            streak_multiplier = 1 + (player['streak'] // 3)
            player['score'] += base_score * streak_multiplier
            
            self.update_player_display()
            self.update_stats()
            
            # Check for level complete
            if len(self.matched) >= len(self.cards):
                self.parent.after(500, self.level_complete)
        else:
            # No match
            sound_manager.play_error()
            
            # Flash red briefly
            for i in [idx1, idx2]:
                canvas = self.cards[i]['canvas']
                canvas.delete('all')
                canvas.create_rectangle(0, 0, 80, 80, fill=COLORS['danger'], outline='')
            
            # Reset streak and switch player
            self.players[self.current_player]['streak'] = 0
            
            if self.num_players > 1:
                self.current_player = (self.current_player + 1) % self.num_players
                self.update_player_display()
            
            # Flip cards back after delay
            self.parent.after(400, lambda: self.flip_back(idx1, idx2))
        
        self.flipped = []
    
    def flip_back(self, idx1: int, idx2: int) -> None:
        """Flip cards back to hidden state"""
        for i in [idx1, idx2]:
            if i < len(self.cards):
                card = self.cards[i]
                card['flipped'] = False
                canvas = card['canvas']
                canvas.delete('all')
                canvas.create_text(
                    40, 40, text="?",
                    font=('Segoe UI', 28, 'bold'),
                    fill=COLORS['text_light']
                )
                canvas.config(highlightbackground=COLORS['light'])
    
    def update_stats(self) -> None:
        """Update stats display"""
        try:
            if self.level_label:
                self.level_label.config(text=str(self.current_level))
            if self.moves_label:
                self.moves_label.config(text=str(self.moves))
            
            pairs_found = len(self.matched) // 2
            if self.pairs_label:
                self.pairs_label.config(text=f"{pairs_found}/{self.total_pairs}")
            
            # Update progress bar
            progress = (pairs_found / self.total_pairs) * 100 if self.total_pairs > 0 else 0
            if self.progress_bar:
                self.progress_bar['value'] = progress
            if self.progress_label:
                self.progress_label.config(text=f"{int(progress)}% Complete")
        except tk.TclError:
            pass
    
    def update_player_display(self) -> None:
        """Update player display"""
        for i, (card, score_lbl, streak_lbl) in enumerate(self.player_cards):
            try:
                player = self.players[i]
                
                # Highlight current player
                if i == self.current_player:
                    bg = COLORS['success']
                    fg = COLORS['white']
                    card.config(bg=bg, bd=4)
                else:
                    bg = COLORS['card']
                    fg = COLORS['text']
                    card.config(bg=bg, bd=2)
                
                score_lbl.config(text=f"{player['score']} pts", bg=bg, fg=fg)
                
                streak_text = f"🔥 {player['streak']}" if player['streak'] > 0 else ""
                streak_lbl.config(text=streak_text, bg=bg)
                
                # Update all labels in card
                for widget in card.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(bg=bg)
                        if '👤' in widget.cget('text'):
                            widget.config(fg=fg)
            except tk.TclError:
                pass
    
    def level_complete(self) -> None:
        """Handle level completion"""
        sound_manager.play_win()
        
        # Add bonus points
        bonus = self.LEVELS[self.current_level]['bonus']
        for player in self.players:
            if player['matches'] > 0:
                player['score'] += bonus
        
        self.update_player_display()
        
        if self.current_level < len(self.LEVELS):
            result = messagebox.askyesno(
                "Level Complete! 🎉",
                f"Level {self.current_level} complete!\n"
                f"Bonus: +{bonus} points for all players\n\n"
                f"Continue to Level {self.current_level + 1}?"
            )
            
            if result:
                self.current_level += 1
                self.grid_size = self.LEVELS[self.current_level]['grid']
                self.total_pairs = self.LEVELS[self.current_level]['pairs']
                self.start_level()
            else:
                self.save_results()
        else:
            messagebox.showinfo(
                "Congratulations! 🏆",
                "You've completed all levels!\n"
                f"Final bonus: +{bonus} points"
            )
            self.save_results()
    
    def save_results(self) -> None:
        """Save results and show final scores"""
        # Save to scoreboard
        for player in self.players:
            scoreboard.add_score(
                'Memory Match', player['name'],
                player['score'], self.current_level
            )
        
        # Sort players by score
        sorted_players = sorted(self.players, key=lambda x: x['score'], reverse=True)
        
        results = "🏆 FINAL RESULTS 🏆\n\n"
        for i, player in enumerate(sorted_players, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            results += f"{medal} {player['name']}: {player['score']} pts\n"
        
        messagebox.showinfo("Game Complete!", results)
        self.show_scoreboard()
    
    def show_scoreboard(self) -> None:
        """Show the scoreboard dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("🏆 Leaderboard")
        dialog.geometry("550x650")
        dialog.transient(self.parent)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 550) // 2
        y = (dialog.winfo_screenheight() - 650) // 2
        dialog.geometry(f"+{x}+{y}")
        
        def close():
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            try:
                dialog.destroy()
            except tk.TclError:
                pass
        
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.after(100, lambda: self._safe_grab(dialog))
        
        # Header
        header_frame = tk.Frame(dialog, bg=COLORS['primary'])
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame, text="🏆 Hall of Fame", font=('Segoe UI', 26, 'bold'),
            bg=COLORS['primary'], fg=COLORS['white'], pady=20
        ).pack()
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg=COLORS['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=COLORS['background'])
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scores = scoreboard.get_top_scores('Memory Match', 10)
        
        if not scores:
            tk.Label(
                frame, text="No scores yet!\nBe the first to play!",
                font=FONTS['body'], bg=COLORS['background'],
                fg=COLORS['text_light']
            ).pack(pady=50)
        else:
            for i, s in enumerate(scores, 1):
                card = tk.Frame(frame, bg=COLORS['card'], relief=tk.RAISED, bd=2)
                card.pack(pady=6, padx=25, fill=tk.X)
                
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                tk.Label(
                    card, text=medal, font=FONTS['heading'],
                    bg=COLORS['card'],
                    fg=COLORS['warning'] if i <= 3 else COLORS['text'],
                    width=4
                ).pack(side=tk.LEFT, padx=12)
                
                info = tk.Frame(card, bg=COLORS['card'])
                info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12, pady=12)
                
                tk.Label(
                    info, text=s['name'], font=FONTS['subheading'],
                    bg=COLORS['card'], anchor='w'
                ).pack(fill=tk.X)
                
                tk.Label(
                    info, text=f"{s['score']} pts • Level {s['level']} • {s['timestamp']}",
                    font=FONTS['small'], bg=COLORS['card'],
                    fg=COLORS['text_light'], anchor='w'
                ).pack(fill=tk.X)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        btn_frame = tk.Frame(dialog, bg=COLORS['background'])
        btn_frame.pack(fill=tk.X, pady=15)
        tk.Button(
            btn_frame, text="Close", font=FONTS['button'],
            bg=COLORS['primary'], fg=COLORS['white'],
            bd=0, cursor='hand2', padx=30, pady=8,
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=close
        ).pack()
    
    def _safe_grab(self, dialog: tk.Toplevel) -> None:
        """Safely grab focus on dialog"""
        try:
            if dialog.winfo_exists():
                dialog.grab_set()
        except tk.TclError:
            pass
    
    def back_to_menu(self) -> None:
        """Go back to main menu"""
        # Cancel any pending check
        if self.check_id:
            try:
                self.parent.after_cancel(self.check_id)
            except tk.TclError:
                pass
            self.check_id = None
        
        self._cleanup_bindings()
        self._destroy_widgets()
        self.on_back()
    
    def _cleanup_bindings(self) -> None:
        """Clean up event bindings"""
        try:
            if self.main_canvas:
                self.main_canvas.unbind_all("<MouseWheel>")
                self.main_canvas.unbind_all("<Button-4>")
                self.main_canvas.unbind_all("<Button-5>")
        except tk.TclError:
            pass
    
    def _destroy_widgets(self) -> None:
        """Destroy main widgets"""
        try:
            if self.main_canvas:
                self.main_canvas.destroy()
                self.main_canvas = None
        except tk.TclError:
            pass
        
        try:
            if self.scrollbar:
                self.scrollbar.destroy()
                self.scrollbar = None
        except tk.TclError:
            pass
    
    def destroy(self) -> None:
        """Clean up and destroy the game"""
        # Cancel any pending check
        if self.check_id:
            try:
                self.parent.after_cancel(self.check_id)
            except tk.TclError:
                pass
            self.check_id = None
        
        self._cleanup_bindings()
        self._destroy_widgets()


# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Memory Match Game")
    root.geometry("900x700")
    
    def on_back():
        root.destroy()
    
    game = MemoryMatchGame(root, on_back)
    root.mainloop()