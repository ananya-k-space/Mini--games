# games/number_rush.py
"""Number Rush Game - Multilevel & Multiplayer - Python 3.14 compatible"""

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import sys
from typing import Callable, Final, TypedDict
from datetime import datetime

# Fallback implementations if utils modules don't exist
try:
    from utils.styles import COLORS, FONTS, GAME_COLORS, sound_manager
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
    
    GAME_COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
        '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
        '#F8B739', '#52B788', '#E76F51', '#264653'
    ]
    
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


class ButtonData(TypedDict):
    widget: tk.Label
    number: int
    clicked: bool


class PlayerData(TypedDict):
    name: str
    score: int
    time: float
    completed: bool


class NumberRushGame:
    """Number Rush Game - Click numbers in order as fast as possible"""
    
    LEVELS: Final[dict[int, dict[str, int]]] = {
        1: {'numbers': 15, 'time': 30},
        2: {'numbers': 20, 'time': 35},
        3: {'numbers': 25, 'time': 40},
        4: {'numbers': 30, 'time': 45},
        5: {'numbers': 40, 'time': 60},
    }
    
    def __init__(self, parent: tk.Tk | tk.Frame, on_back: Callable[[], None]) -> None:
        self.parent: tk.Tk | tk.Frame = parent
        self.on_back: Callable[[], None] = on_back
        self.buttons: list[ButtonData] = []
        self.current_number: int = 1
        self.start_time: float | None = None
        self.game_active: bool = False
        self.timer_id: str | None = None
        
        self.num_players: int = 1
        self.current_player: int = 0
        self.players: list[PlayerData] = []
        
        self.current_level: int = 1
        self.total_numbers: int = 15
        
        # Initialize UI elements to None
        self.setup_frame: tk.Frame | None = None
        self.main_canvas: tk.Canvas | None = None
        self.scrollbar: tk.Scrollbar | None = None
        self.scrollable_frame: tk.Frame | None = None
        self.canvas_frame: int | None = None
        self.player_labels: list[tk.Label] = []
        self.level_label: tk.Label | None = None
        self.progress_label: tk.Label | None = None
        self.timer_label: tk.Label | None = None
        self.start_btn: tk.Button | None = None
        self.sound_btn: tk.Button | None = None
        self.player_frame: tk.Frame | None = None
        self.grid_container: tk.Frame | None = None
        
        self.show_smooth_setup()
    
    def show_smooth_setup(self) -> None:
        """Embedded setup screen - no Toplevel"""
        self.setup_frame = tk.Frame(self.parent, bg=COLORS['background'])
        self.setup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(self.setup_frame, bg=COLORS['info'])
        header.pack(fill=tk.X)
        
        tk.Button(
            header, text="← Back to Menu", font=FONTS['body'],
            bg=COLORS['info'], fg=COLORS['white'], bd=0,
            cursor='hand2', padx=15, pady=8,
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=self._cancel_setup
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(
            header, text="⚡ Number Rush Setup",
            font=('Segoe UI', 28, 'bold'), bg=COLORS['info'],
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
        
        # === DIFFICULTY SECTION ===
        tk.Label(
            center_frame, text="🎯 Difficulty", font=FONTS['heading'],
            bg=COLORS['background'], fg=COLORS['text']
        ).pack(pady=(20, 10))
        
        level_var = tk.IntVar(value=1)
        levels_frame = tk.Frame(center_frame, bg=COLORS['background'])
        levels_frame.pack(pady=8, fill=tk.X, padx=40)
        
        levels = [
            (1, "⭐ Easy", "15 numbers • 30s", COLORS['success']),
            (2, "⭐⭐ Medium", "20 numbers • 35s", COLORS['info']),
            (3, "⭐⭐⭐ Hard", "25 numbers • 40s", COLORS['warning']),
            (4, "⭐⭐⭐⭐ Very Hard", "30 numbers • 45s", COLORS['danger']),
            (5, "⭐⭐⭐⭐⭐ Expert", "40 numbers • 60s", COLORS['primary']),
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
            def on_card_click(e, lv=level):
                level_var.set(lv)
                sound_manager.play_click()
            
            def on_card_enter(e, c=card):
                c.config(bg=COLORS['light'])
                for child in c.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=COLORS['light'])
            
            def on_card_leave(e, c=card):
                c.config(bg=COLORS['card'])
                for child in c.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=COLORS['card'])
            
            card.bind('<Button-1>', on_card_click)
            card.bind('<Enter>', on_card_enter)
            card.bind('<Leave>', on_card_leave)
        
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
                    'time': 0.0,
                    'completed': False
                })
            
            self.num_players = num
            self.current_level = level_var.get()
            self.total_numbers = self.LEVELS[self.current_level]['numbers']
            
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
            self.start_round()
        
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
        header = tk.Frame(self.scrollable_frame, bg=COLORS['info'])
        header.pack(fill=tk.X)
        
        top_bar = tk.Frame(header, bg=COLORS['info'])
        top_bar.pack(fill=tk.X, pady=8)
        
        tk.Button(
            top_bar, text="← Back", font=FONTS['body'],
            bg=COLORS['info'], fg=COLORS['white'],
            bd=0, cursor='hand2',
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=self.back_to_menu
        ).pack(side=tk.LEFT, padx=20)
        
        self.sound_btn = tk.Button(
            top_bar, text="🔊", font=FONTS['body'],
            bg=COLORS['info'], fg=COLORS['white'],
            bd=0, cursor='hand2', width=3,
            activebackground=COLORS['dark'],
            command=self.toggle_sound
        )
        self.sound_btn.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            header, text="⚡ Number Rush", font=('Segoe UI', 32, 'bold'),
            bg=COLORS['info'], fg=COLORS['white']
        ).pack(pady=20)
        
        # Stats
        stats_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        stats_frame.pack(pady=15)
        
        self.level_label = tk.Label(
            stats_frame, text=f"Level {self.current_level}",
            font=FONTS['heading'], bg=COLORS['background'],
            fg=COLORS['info']
        )
        self.level_label.pack(side=tk.LEFT, padx=15)
        
        self.progress_label = tk.Label(
            stats_frame, text="Ready!",
            font=FONTS['subheading'], bg=COLORS['background'],
            fg=COLORS['text']
        )
        self.progress_label.pack(side=tk.LEFT, padx=15)
        
        self.timer_label = tk.Label(
            stats_frame, text="Time: 0.00s",
            font=FONTS['subheading'], bg=COLORS['background'],
            fg=COLORS['danger']
        )
        self.timer_label.pack(side=tk.LEFT, padx=15)
        
        # Player scores
        self.player_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        self.player_frame.pack(pady=10)
        
        self.player_labels = []
        for player in self.players:
            label = tk.Label(
                self.player_frame, text=f"{player['name']}: --",
                font=FONTS['body'], bg=COLORS['card'],
                fg=COLORS['text'], padx=15, pady=8,
                relief=tk.RAISED, bd=2
            )
            label.pack(side=tk.LEFT, padx=5)
            self.player_labels.append(label)
        
        # Control buttons
        btn_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            btn_frame, text="🎮 Start Round", font=FONTS['button'],
            bg=COLORS['success'], fg=COLORS['white'],
            bd=0, cursor='hand2', padx=20, pady=10,
            activebackground=COLORS['primary'],
            activeforeground=COLORS['white'],
            command=self.start_round
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame, text="🏆 Scoreboard", font=FONTS['button'],
            bg=COLORS['warning'], fg=COLORS['white'],
            bd=0, cursor='hand2', padx=20, pady=10,
            activebackground=COLORS['primary'],
            activeforeground=COLORS['white'],
            command=self.show_scoreboard
        ).pack(side=tk.LEFT, padx=5)
        
        # Grid container for number buttons
        self.grid_container = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        self.grid_container.pack(expand=True, pady=20)
        
        # Instructions
        tk.Label(
            self.scrollable_frame,
            text="Click numbers in order from 1 onwards. Fastest time wins!",
            font=FONTS['body'], bg=COLORS['background'],
            fg=COLORS['text_light']
        ).pack(pady=10)
    
    def toggle_sound(self) -> None:
        """Toggle sound on/off"""
        enabled = sound_manager.toggle()
        if self.sound_btn:
            self.sound_btn.config(text="🔊" if enabled else "🔇")
        sound_manager.play_click()
    
    def start_round(self) -> None:
        """Start a round for current player"""
        if self.current_player >= len(self.players):
            self.end_game()
            return
        
        player = self.players[self.current_player]
        
        if player['completed']:
            self.current_player += 1
            self.start_round()
            return
        
        self.current_number = 1
        self.start_time = time.time()
        self.game_active = True
        
        # Hide start button during game
        if self.start_btn:
            try:
                self.start_btn.pack_forget()
            except tk.TclError:
                pass
        
        self.update_player_display()
        self.create_game_grid()
        self.update_display()
        self.update_timer()
        
        sound_manager.play_click()
    
    def create_game_grid(self) -> None:
        """Create the grid of number buttons"""
        # Clear existing grid
        if self.grid_container:
            for widget in self.grid_container.winfo_children():
                widget.destroy()
        
        self.buttons = []
        numbers: list[int] = list(range(1, self.total_numbers + 1))
        random.shuffle(numbers)
        
        grid_frame = tk.Frame(self.grid_container, bg=COLORS['background'])
        grid_frame.pack()
        
        # Calculate grid dimensions
        cols = 5
        if self.total_numbers > 30:
            cols = 8
        elif self.total_numbers > 20:
            cols = 6
        
        rows = (self.total_numbers + cols - 1) // cols
        
        for i in range(rows):
            for j in range(cols):
                idx: int = i * cols + j
                if idx >= len(numbers):
                    break
                
                num: int = numbers[idx]
                color: str = random.choice(GAME_COLORS)
                
                # Button container with slight shadow effect
                btn_container = tk.Frame(grid_frame, bg=COLORS['light'])
                btn_container.grid(row=i, column=j, padx=4, pady=4)
                
                btn = tk.Label(
                    btn_container, text=str(num), width=4, height=2,
                    bg=color, fg=COLORS['white'], font=FONTS['heading'],
                    cursor='hand2', relief=tk.RAISED, bd=3
                )
                btn.pack(padx=2, pady=2)
                btn.bind('<Button-1>', lambda e, n=num: self.number_clicked(n))
                
                # Hover effects
                def on_enter(e, b=btn, original_color=color):
                    if b.cget('bg') != COLORS['success'] and b.cget('bg') != COLORS['danger']:
                        b.config(relief=tk.GROOVE)
                
                def on_leave(e, b=btn, original_color=color):
                    if b.cget('bg') != COLORS['success'] and b.cget('bg') != COLORS['danger']:
                        b.config(relief=tk.RAISED)
                
                btn.bind('<Enter>', on_enter)
                btn.bind('<Leave>', on_leave)
                
                self.buttons.append({
                    'widget': btn,
                    'number': num,
                    'clicked': False
                })
    
    def number_clicked(self, num: int) -> None:
        """Handle number button click"""
        if not self.game_active:
            return
        
        if num == self.current_number:
            sound_manager.play_click()
            
            # Mark as clicked
            for btn_data in self.buttons:
                if btn_data['number'] == num:
                    btn_data['clicked'] = True
                    btn_data['widget'].config(
                        bg=COLORS['success'],
                        text="✓",
                        relief=tk.SUNKEN
                    )
                    break
            
            self.current_number += 1
            self.update_display()
            
            # Check if all numbers clicked
            if self.current_number > self.total_numbers:
                self.round_complete()
        else:
            sound_manager.play_error()
            
            # Flash wrong button red
            for btn_data in self.buttons:
                if btn_data['number'] == num and not btn_data['clicked']:
                    original_bg: str = btn_data['widget'].cget('bg')
                    btn_data['widget'].config(bg=COLORS['danger'])
                    self.parent.after(
                        200,
                        lambda w=btn_data['widget'], bg=original_bg: w.config(bg=bg)
                    )
                    break
    
    def update_display(self) -> None:
        """Update progress display"""
        if self.progress_label:
            try:
                self.progress_label.config(
                    text=f"Next: {self.current_number} / {self.total_numbers}"
                )
            except tk.TclError:
                pass
    
    def update_timer(self) -> None:
        """Update timer display"""
        if self.game_active and self.start_time is not None:
            elapsed: float = time.time() - self.start_time
            if self.timer_label:
                try:
                    self.timer_label.config(text=f"Time: {elapsed:.2f}s")
                except tk.TclError:
                    return
            self.timer_id = self.parent.after(50, self.update_timer)
    
    def round_complete(self) -> None:
        """Handle round completion"""
        self.game_active = False
        sound_manager.play_win()
        
        # Cancel timer
        if self.timer_id:
            try:
                self.parent.after_cancel(self.timer_id)
            except tk.TclError:
                pass
            self.timer_id = None
        
        if self.start_time is not None:
            elapsed: float = time.time() - self.start_time
            player = self.players[self.current_player]
            player['time'] = elapsed
            player['completed'] = True
            # Score based on speed - faster = higher score
            player['score'] = int(10000 / elapsed) * self.current_level
            
            self.update_player_display()
            
            messagebox.showinfo(
                f"{player['name']} Complete! 🎉",
                f"Time: {elapsed:.2f} seconds\nScore: {player['score']} pts"
            )
        
        self.current_player += 1
        
        if self.current_player < self.num_players:
            if self.start_btn:
                self.start_btn.config(text="🎮 Next Player")
                self.start_btn.pack(pady=20)
        else:
            self.end_game()
    
    def update_player_display(self) -> None:
        """Update player display labels"""
        if not self.player_labels or not self.players:
            return
        
        for i, (player, label) in enumerate(zip(self.players, self.player_labels)):
            try:
                if player['completed']:
                    text = f"{player['name']}: {player['time']:.2f}s ({player['score']} pts)"
                    bg = COLORS['success']
                    fg = COLORS['white']
                elif i == self.current_player:
                    text = f"{player['name']}: Playing..."
                    bg = COLORS['warning']
                    fg = COLORS['white']
                else:
                    text = f"{player['name']}: Waiting"
                    bg = COLORS['card']
                    fg = COLORS['text']
                
                label.config(
                    text=text, bg=bg, fg=fg,
                    font=FONTS['heading'] if i == self.current_player else FONTS['body']
                )
            except tk.TclError:
                pass
    
    def end_game(self) -> None:
        """End the game and show results"""
        self.game_active = False
        
        # Cancel any pending timer
        if self.timer_id:
            try:
                self.parent.after_cancel(self.timer_id)
            except tk.TclError:
                pass
            self.timer_id = None
        
        # Save scores
        for player in self.players:
            if player['completed']:
                scoreboard.add_score(
                    'Number Rush', player['name'],
                    player['score'], self.current_level
                )
        
        # Sort players by time (fastest first)
        sorted_players = sorted(
            [p for p in self.players if p['completed']],
            key=lambda p: p['time']
        )
        
        if sorted_players:
            results = "🏆 Final Results 🏆\n\n"
            for i, player in enumerate(sorted_players, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                results += f"{medal} {player['name']}: {player['time']:.2f}s ({player['score']} pts)\n"
        else:
            results = "No players completed the game."
        
        messagebox.showinfo("Game Over", results)
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
        header_frame = tk.Frame(dialog, bg=COLORS['info'])
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame, text="🏆 Top Players", font=('Segoe UI', 26, 'bold'),
            bg=COLORS['info'], fg=COLORS['white'], pady=20
        ).pack()
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg=COLORS['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=COLORS['background'])
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scores = scoreboard.get_top_scores('Number Rush', 10)
        
        if not scores:
            tk.Label(
                frame, text="No scores yet!\nPlay a game to see your scores here.",
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
            bg=COLORS['info'], fg=COLORS['white'],
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
        self.game_active = False
        
        # Cancel any pending timer
        if self.timer_id:
            try:
                self.parent.after_cancel(self.timer_id)
            except tk.TclError:
                pass
            self.timer_id = None
        
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
        self.game_active = False
        
        # Cancel any pending timer
        if self.timer_id:
            try:
                self.parent.after_cancel(self.timer_id)
            except tk.TclError:
                pass
            self.timer_id = None
        
        self._cleanup_bindings()
        self._destroy_widgets()


# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Number Rush Game")
    root.geometry("900x700")
    
    def on_back():
        root.destroy()
    
    game = NumberRushGame(root, on_back)
    root.mainloop()