# main.py
"""Main application launcher for Mini Games App - Python 3.14 compatible"""

from __future__ import annotations
import tkinter as tk
from typing import Final
import sys
from game_menu import GameMenu

class MiniGamesApp:
    """Main application class for Mini Games Collection"""
    
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("🎮 Mini Games Collection - Multiplayer Edition")
        
        self.MIN_WIDTH: Final[int] = 1000
        self.MIN_HEIGHT: Final[int] = 700
        self.WINDOW_WIDTH: Final[int] = 1200
        self.WINDOW_HEIGHT: Final[int] = 800
        
        self.setup_window()
        self.menu: GameMenu = GameMenu(self.root)
        self.show_welcome()
    
    def setup_window(self) -> None:
        """Setup the main application window"""
        # Hide window during setup to prevent flicker
        self.root.withdraw()
        
        # Set minimum size
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        
        # Force update to get accurate screen dimensions
        self.root.update_idletasks()
        
        screen_width: int = self.root.winfo_screenwidth()
        screen_height: int = self.root.winfo_screenheight()
        
        # Center the window
        x: int = (screen_width - self.WINDOW_WIDTH) // 2
        y: int = (screen_height - self.WINDOW_HEIGHT) // 2
        
        # Set geometry and force update
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x}+{y}")
        self.root.update_idletasks()
        
        self.root.configure(bg='#F8F9FA')
        
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.end_fullscreen)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.is_fullscreen: bool = False
        
        # Show window after setup complete
        self.root.deiconify()
    
    def show_welcome(self) -> None:
        """Show welcome message on first launch"""
        from pathlib import Path
        scores_file = Path('scores.json')
        
        if not scores_file.exists():
            welcome = tk.Toplevel(self.root)
            welcome.title("Welcome! 🎉")
            welcome.geometry("500x450")
            welcome.transient(self.root)
            
            welcome.update_idletasks()
            x = (welcome.winfo_screenwidth() - 500) // 2
            y = (welcome.winfo_screenheight() - 450) // 2
            welcome.geometry(f"+{x}+{y}")
            
            def close_welcome():
                try:
                    welcome.grab_release()
                    welcome.destroy()
                except:
                    pass
            
            welcome.protocol("WM_DELETE_WINDOW", close_welcome)
            welcome.after(100, lambda: welcome.grab_set())
            
            frame = tk.Frame(welcome, bg='#6C5CE7')
            frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(frame, text="🎮 Welcome to Mini Games!",
                    font=('Segoe UI', 24, 'bold'), bg='#6C5CE7',
                    fg='white').pack(pady=30)
            
            info = tk.Frame(frame, bg='white')
            info.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)
            
            features = [
                "✨ Multiplayer Support (1-4 players)",
                "🎯 Multi-Level Challenges",
                "🏆 Global Scoreboard",
                "🎨 7 Symbol Themes",
                "🔊 Sound Effects",
                "📜 Smooth Scrolling"
            ]
            
            for feature in features:
                tk.Label(info, text=feature, font=('Segoe UI', 14),
                        bg='white', fg='#2D3436', anchor='w').pack(pady=5, padx=20, fill=tk.X)
            
            tk.Label(frame, text="Made for fun with Python ❤️",
                    font=('Segoe UI', 12), bg='#6C5CE7',
                    fg='#DFE6E9').pack(pady=10)
            
            tk.Button(frame, text="Let's Play!", font=('Segoe UI', 16, 'bold'),
                     bg='#00B894', fg='white', bd=0, cursor='hand2',
                     padx=40, pady=15, command=close_welcome).pack(pady=20)
    
    def toggle_fullscreen(self, event: tk.Event | None = None) -> None:
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        status = "Fullscreen ON (Press ESC to exit)" if self.is_fullscreen else "Multiplayer Edition"
        self.root.title(f"🎮 Mini Games Collection - {status}")
    
    def end_fullscreen(self, event: tk.Event | None = None) -> None:
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
        self.root.title("🎮 Mini Games Collection - Multiplayer Edition")
    
    def on_closing(self) -> None:
        """Handle application closing"""
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error during shutdown: {e}", file=sys.stderr)
            sys.exit(0)
        
    def run(self) -> None:
        """Start the application main loop"""
        try:
            # Ensure window is visible and focused
            self.root.update_idletasks()
            self.root.lift()
            self.root.focus_force()
            
            # Force window to front on Windows
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Application closed by user.")
            self.on_closing()
        except Exception as e:
            print(f"❌ An error occurred: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            self.on_closing()

def check_dependencies() -> bool:
    """Check if all required dependencies are available"""
    try:
        import tkinter
        return True
    except ImportError:
        print("❌ Error: Tkinter is not installed!")
        print("\n📦 Installation instructions:")
        print("   Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   Fedora: sudo dnf install python3-tkinter")
        print("   macOS: Comes with Python from python.org")
        print("   Windows: Comes with Python installer")
        return False

def main() -> None:
    """Main entry point for the application"""
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required. You have Python {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    print("=" * 60)
    print("🎮 Mini Games Collection v2.0")
    print("=" * 60)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"✅ Platform: {sys.platform}")
    print("\n🎯 Features:")
    print("   • Multiplayer (1-4 players)")
    print("   • Multi-level challenges")
    print("   • Global scoreboard")
    print("   • 7 Symbol themes")
    print("   • Sound effects")
    print("   • Smooth scrolling")
    print("\n⌨️  Shortcuts:")
    print("   • F11 - Toggle fullscreen")
    print("   • ESC - Exit fullscreen")
    print("   • Mouse wheel - Scroll content")
    print("\n🚀 Launching game...")
    print("=" * 60)
    print()
    
    try:
        app = MiniGamesApp()
        app.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n👋 Thanks for playing! Made for fun with Python ❤️")

if __name__ == "__main__":
    main()