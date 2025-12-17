# games/color_blast.py
"""Color Blast Game - Multilevel & Multiplayer - Python 3.14 compatible"""

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk
import random
import sys
from typing import Callable, Final, TypedDict
from datetime import datetime

# Fallback implementations if utils modules don't exist
try:
    from utils.styles import COLORS, FONTS, sound_manager
except ImportError:
    # Default colors
    COLORS = {
        'primary': '#3498DB',
        'secondary': '#2ECC71',
        'success': '#27AE60',
        'warning': '#F39C12',
        'danger': '#E74C3C',
        'info': '#17A2B8',
        'light': '#ECF0F1',
        'dark': '#2C3E50',
        'white': '#FFFFFF',
        'black': '#000000',
        'background': '#F5F6FA',
        'card': '#FFFFFF',
        'text': '#2C3E50',
        'text_light': '#7F8C8D',
    }
    
    FONTS = {
        'heading': ('Segoe UI', 18, 'bold'),
        'subheading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 12),
        'small': ('Segoe UI', 10),
        'button': ('Segoe UI', 12, 'bold'),
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


class PlayerData(TypedDict):
    name: str
    score: int
    completed: bool


class ColorBlastGame:
    """Color Blast Game - Multilevel & Multiplayer"""
    
    LEVELS: Final[dict[int, dict[str, int]]] = {
        1: {'time': 45, 'target': 10},
        2: {'time': 40, 'target': 15},
        3: {'time': 35, 'target': 20},
        4: {'time': 30, 'target': 25},
        5: {'time': 25, 'target': 30},
    }
    
    def __init__(self, parent: tk.Tk | tk.Frame, on_back: Callable[[], None]) -> None:
        self.parent: tk.Tk | tk.Frame = parent
        self.on_back: Callable[[], None] = on_back
        self.score: int = 0
        self.time_left: int = 45
        self.game_active: bool = False
        self.correct_answer: int = 0
        self.timer_id: str | None = None
        
        self.num_players: int = 1
        self.current_player: int = 0
        self.players: list[PlayerData] = []
        
        self.current_level: int = 1
        self.target_score: int = 10
        
        # Initialize UI elements to None
        self.setup_frame: tk.Frame | None = None
        self.main_canvas: tk.Canvas | None = None
        self.scrollbar: tk.Scrollbar | None = None
        self.scrollable_frame: tk.Frame | None = None
        self.canvas_frame: int | None = None
        self.player_labels: list[tk.Label] = []
        self.answer_buttons: list[tk.Button] = []
        self.level_label: tk.Label | None = None
        self.score_label: tk.Label | None = None
        self.timer_label: tk.Label | None = None
        self.target_label: tk.Label | None = None
        self.word_label: tk.Label | None = None
        self.start_btn: tk.Button | None = None
        self.sound_btn: tk.Button | None = None
        self.player_frame: tk.Frame | None = None
        self.game_container: tk.Frame | None = None
        self.buttons_frame: tk.Frame | None = None
        
        self.color_names: Final[dict[str, str]] = {
            'RED': '#E74C3C',
            'BLUE': '#3498DB',
            'GREEN': '#2ECC71',
            'YELLOW': '#F1C40F',
            'PURPLE': '#9B59B6',
            'ORANGE': '#E67E22',
            'PINK': '#FF69B4',
            'CYAN': '#00CED1'
        }
        
        self.show_smooth_setup()
    
    def show_smooth_setup(self) -> None:
        """Embedded setup screen - no Toplevel"""
        self.setup_frame = tk.Frame(self.parent, bg=COLORS['background'])
        self.setup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(self.setup_frame, bg=COLORS['warning'])
        header.pack(fill=tk.X)
        
        tk.Button(
            header, text="← Back to Menu", font=FONTS['body'],
            bg=COLORS['warning'], fg=COLORS['white'], bd=0,
            cursor='hand2', padx=15, pady=8,
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=self._cancel_setup
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(
            header, text="🎨 Color Blast Setup",
            font=('Segoe UI', 28, 'bold'), bg=COLORS['warning'],
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
            (1, "⭐ Easy", "45s • Target: 10", COLORS['success']),
            (2, "⭐⭐ Medium", "40s • Target: 15", COLORS['info']),
            (3, "⭐⭐⭐ Hard", "35s • Target: 20", COLORS['warning']),
            (4, "⭐⭐⭐⭐ Very Hard", "30s • Target: 25", COLORS['danger']),
            (5, "⭐⭐⭐⭐⭐ Expert", "25s • Target: 30", COLORS['primary']),
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
                    'completed': False
                })
            
            self.num_players = num
            self.current_level = level_var.get()
            self.time_left = self.LEVELS[self.current_level]['time']
            self.target_score = self.LEVELS[self.current_level]['target']
            
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
        header = tk.Frame(self.scrollable_frame, bg=COLORS['warning'])
        header.pack(fill=tk.X)
        
        top_bar = tk.Frame(header, bg=COLORS['warning'])
        top_bar.pack(fill=tk.X, pady=8)
        
        tk.Button(
            top_bar, text="← Back", font=FONTS['body'],
            bg=COLORS['warning'], fg=COLORS['white'],
            bd=0, cursor='hand2',
            activebackground=COLORS['dark'],
            activeforeground=COLORS['white'],
            command=self.back_to_menu
        ).pack(side=tk.LEFT, padx=20)
        
        self.sound_btn = tk.Button(
            top_bar, text="🔊", font=FONTS['body'],
            bg=COLORS['warning'], fg=COLORS['white'],
            bd=0, cursor='hand2', width=3,
            activebackground=COLORS['dark'],
            command=self.toggle_sound
        )
        self.sound_btn.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            header, text="🎨 Color Blast", font=('Segoe UI', 32, 'bold'),
            bg=COLORS['warning'], fg=COLORS['white']
        ).pack(pady=20)
        
        # Stats
        stats_frame = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        stats_frame.pack(pady=15)
        
        self.level_label = tk.Label(
            stats_frame, text=f"Level {self.current_level}",
            font=FONTS['heading'], bg=COLORS['background'],
            fg=COLORS['warning']
        )
        self.level_label.pack(side=tk.LEFT, padx=15)
        
        self.score_label = tk.Label(
            stats_frame, text="Score: 0",
            font=FONTS['heading'], bg=COLORS['background'],
            fg=COLORS['success']
        )
        self.score_label.pack(side=tk.LEFT, padx=15)
        
        self.timer_label = tk.Label(
            stats_frame, text=f"Time: {self.time_left}s",
            font=FONTS['heading'], bg=COLORS['background'],
            fg=COLORS['danger']
        )
        self.timer_label.pack(side=tk.LEFT, padx=15)
        
        self.target_label = tk.Label(
            stats_frame, text=f"Target: {self.target_score}",
            font=FONTS['subheading'], bg=COLORS['background'],
            fg=COLORS['text_light']
        )
        self.target_label.pack(side=tk.LEFT, padx=15)
        
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
            bg=COLORS['info'], fg=COLORS['white'],
            bd=0, cursor='hand2', padx=20, pady=10,
            activebackground=COLORS['primary'],
            activeforeground=COLORS['white'],
            command=self.show_scoreboard
        ).pack(side=tk.LEFT, padx=5)
        
        # Game area
        self.game_container = tk.Frame(self.scrollable_frame, bg=COLORS['background'])
        self.game_container.pack(expand=True, pady=30)
        
        # Question card
        card_frame = tk.Frame(self.game_container, bg=COLORS['card'], relief=tk.RAISED, bd=2)
        card_frame.pack(pady=20)
        
        instruction = tk.Label(
            card_frame, text="What COLOR is this word?",
            font=FONTS['body'], bg=COLORS['card'],
            fg=COLORS['text_light']
        )
        instruction.pack(pady=20, padx=40)
        
        self.word_label = tk.Label(
            card_frame, text="COLOR",
            font=('Segoe UI', 48, 'bold'),
            bg=COLORS['card'], fg=COLORS['text']
        )
        self.word_label.pack(pady=30, padx=60)
        
        # Answer buttons
        self.buttons_frame = tk.Frame(self.game_container, bg=COLORS['background'])
        self.buttons_frame.pack(pady=20)
        
        self.answer_buttons = []
        for i in range(4):
            row: int = i // 2
            col: int = i % 2
            
            btn = tk.Button(
                self.buttons_frame, text="COLOR", font=FONTS['button'],
                width=12, height=2, bd=0, cursor='hand2',
                activeforeground=COLORS['white'],
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
            self.answer_buttons.append(btn)
        
        # Instructions
        tk.Label(
            self.scrollable_frame,
            text="Click the button with the COLOR of the word (not the text)!",
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
        
        self.score = 0
        self.time_left = self.LEVELS[self.current_level]['time']
        self.game_active = True
        
        # Hide start button during game
        if self.start_btn:
            try:
                self.start_btn.pack_forget()
            except tk.TclError:
                pass
        
        self.update_stats()
        self.update_player_display()
        self.new_question()
        self.countdown()
        
        sound_manager.play_click()
    
    def new_question(self) -> None:
        """Generate a new question"""
        if not self.game_active:
            return
        
        color_list = list(self.color_names.keys())
        word_name: str = random.choice(color_list)
        word_color: str = random.choice(list(self.color_names.values()))
        
        if self.word_label:
            self.word_label.config(text=word_name, fg=word_color)
        
        # Find the name of the color being displayed
        correct_color_name: str = next(
            name for name, color in self.color_names.items()
            if color == word_color
        )
        
        # Create options with correct answer
        options: list[str] = [correct_color_name]
        while len(options) < 4:
            opt: str = random.choice(color_list)
            if opt not in options:
                options.append(opt)
        
        random.shuffle(options)
        self.correct_answer = options.index(correct_color_name)
        
        # Update buttons
        for i, btn in enumerate(self.answer_buttons):
            color_name: str = options[i]
            btn.config(
                text=color_name,
                bg=self.color_names[color_name],
                fg=COLORS['white'],
                state=tk.NORMAL,
                activebackground=self.color_names[color_name]
            )
    
    def check_answer(self, idx: int) -> None:
        """Check if the answer is correct"""
        if not self.game_active:
            return
        
        if idx == self.correct_answer:
            sound_manager.play_match()
            self.score += 1
            self.update_stats()
            
            # Flash green briefly
            self.answer_buttons[idx].config(bg=COLORS['success'])
            self.parent.after(200, self.new_question)
        else:
            sound_manager.play_error()
            
            # Show wrong (red) and correct (green)
            self.answer_buttons[idx].config(bg=COLORS['danger'])
            self.answer_buttons[self.correct_answer].config(bg=COLORS['success'])
            
            # Disable all buttons briefly
            for btn in self.answer_buttons:
                btn.config(state=tk.DISABLED)
            
            self.parent.after(800, self.new_question)
    
    def countdown(self) -> None:
        """Countdown timer"""
        if not self.game_active:
            return
        
        if self.time_left > 0:
            self.time_left -= 1
            self.update_stats()
            self.timer_id = self.parent.after(1000, self.countdown)
        else:
            self.round_over()
    
    def update_stats(self) -> None:
        """Update stats display"""
        try:
            if self.level_label:
                self.level_label.config(text=f"Level {self.current_level}")
            if self.score_label:
                self.score_label.config(text=f"Score: {self.score}")
            if self.timer_label:
                self.timer_label.config(text=f"Time: {self.time_left}s")
            if self.target_label:
                self.target_label.config(text=f"Target: {self.target_score}")
        except tk.TclError:
            pass
    
    def round_over(self) -> None:
        """Handle end of round"""
        self.game_active = False
        
        if self.current_player >= len(self.players):
            self.end_game()
            return
        
        player = self.players[self.current_player]
        player['score'] = self.score * self.current_level * 10
        player['completed'] = True
        
        self.update_player_display()
        
        if self.score >= self.target_score:
            sound_manager.play_win()
            messagebox.showinfo(
                f"{player['name']} - Success! 🎉",
                f"Score: {self.score}\nTarget Reached!\nPoints: {player['score']}"
            )
        else:
            messagebox.showinfo(
                f"{player['name']} - Time's Up!",
                f"Score: {self.score}\nTarget: {self.target_score}\nPoints: {player['score']}"
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
                    text = f"{player['name']}: {player['score']} pts"
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
                    'Color Blast', player['name'],
                    player['score'], self.current_level
                )
        
        # Sort players by score
        sorted_players = sorted(
            [p for p in self.players if p['completed']],
            key=lambda p: p['score'], reverse=True
        )
        
        if sorted_players:
            results = "🏆 Final Results 🏆\n\n"
            for i, player in enumerate(sorted_players, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                results += f"{medal} {player['name']}: {player['score']} pts\n"
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
        header_frame = tk.Frame(dialog, bg=COLORS['warning'])
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame, text="🏆 Top Players", font=('Segoe UI', 26, 'bold'),
            bg=COLORS['warning'], fg=COLORS['white'], pady=20
        ).pack()
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg=COLORS['background'], highlightthickness=0)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=COLORS['background'])
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scores = scoreboard.get_top_scores('Color Blast', 10)
        
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
            bg=COLORS['warning'], fg=COLORS['white'],
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
    root.title("Color Blast Game")
    root.geometry("900x700")
    
    def on_back():
        root.destroy()
    
    game = ColorBlastGame(root, on_back)
    root.mainloop()