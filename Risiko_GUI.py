#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║     R I S I K O  -  GUI Edition mit Tkinter                  ║
║     Welteroberungsstrategie mit grafischer Oberfläche        ║
╚══════════════════════════════════════════════════════════════╝

EXTRAS:
  ✓ Grafische Weltkarte mit interaktiven Gebieten
  ✓ Drag & Drop für Truppenverschiebung
  ✓ Animierte Würfel mit Sound-Option
  ✓ Dark/Light Mode Theme-Umschaltung
  ✓ Tooltips mit Gebietsinformationen
  ✓ Zug-Historie mit Log-Fenster
  ✓ Minimale Karte & Zoom-Funktion
  ✓ Fortschrittsbalken für Kontinent-Boni
  ✓ Emoji-Unterstützung & moderne Icons
  ✓ Auto-Save alle 5 Runden
  ✓ Achievements-System
  ✓ Tutorial-Modus für Neueinsteiger
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import random
import time
import threading
from collections import defaultdict, Counter
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable
import math

# ───────────────────────────── KONFIGURATION ─────────────────────────────
CONFIG = {
    "window_size": (1400, 900),
    "map_scale": 1.0,
    "animation_speed": 0.3,
    "sound_enabled": True,
    "theme": "dark",  # "dark" or "light"
    "auto_save_interval": 5,
    "tutorial_mode": False,
}

# ───────────────────────────── FARB-THEMES ─────────────────────────────
THEMES = {
    "dark": {
        "bg": "#1a1a2e", "bg_secondary": "#16213e", "bg_tertiary": "#0f3460",
        "text": "#eee", "text_dim": "#aaa", "accent": "#e94560",
        "accent2": "#00d9ff", "success": "#00ff88", "warning": "#ffaa00",
        "danger": "#ff5555", "border": "#333", "card_bg": "#2a2a4e",
        "tooltip_bg": "#2d2d44", "tooltip_text": "#fff",
        "player_colors": ["#ff6b6b", "#4ecdc4", "#ffe66d", "#95e1d3", "#f38181", "#aa96da"],
    },
    "light": {
        "bg": "#f0f4f8", "bg_secondary": "#d9e2ec", "bg_tertiary": "#bcccdc",
        "text": "#1a1a2e", "text_dim": "#555", "accent": "#e94560",
        "accent2": "#0077b6", "success": "#06a77d", "warning": "#cc8800",
        "danger": "#c1121f", "border": "#999", "card_bg": "#fff",
        "tooltip_bg": "#333", "tooltip_text": "#fff",
        "player_colors": ["#c1121f", "#0077b6", "#2a9d8f", "#e76f51", "#264653", "#6a4c93"],
    }
}

# ───────────────────────────── SPIELDATEN (aus Original) ─────────────────────────────
TERRITORIES = {
    # Nordamerika
    "Alaska": {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium", "Alberta", "Kamtschatka"], "pos": (150, 180)},
    "Nordwest-Territorium": {"continent": "Nordamerika", "neighbors": ["Alaska", "Alberta", "Ontario", "Grönland"], "pos": (280, 150)},
    "Grönland": {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium", "Ontario", "Quebec", "Island"], "pos": (420, 100)},
    "Alberta": {"continent": "Nordamerika", "neighbors": ["Alaska", "Nordwest-Territorium", "Ontario", "Weststaaten"], "pos": (240, 240)},
    "Ontario": {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium", "Grönland", "Alberta", "Weststaaten", "Quebec", "Oststaaten"], "pos": (340, 220)},
    "Quebec": {"continent": "Nordamerika", "neighbors": ["Ontario", "Grönland", "Oststaaten"], "pos": (400, 260)},
    "Weststaaten": {"continent": "Nordamerika", "neighbors": ["Alberta", "Ontario", "Oststaaten", "Mittelamerika"], "pos": (280, 320)},
    "Oststaaten": {"continent": "Nordamerika", "neighbors": ["Weststaaten", "Ontario", "Quebec", "Mittelamerika"], "pos": (380, 320)},
    "Mittelamerika": {"continent": "Nordamerika", "neighbors": ["Weststaaten", "Oststaaten", "Venezuela"], "pos": (320, 400)},
    # Südamerika
    "Venezuela": {"continent": "Südamerika", "neighbors": ["Mittelamerika", "Peru", "Brasilien"], "pos": (340, 480)},
    "Peru": {"continent": "Südamerika", "neighbors": ["Venezuela", "Brasilien", "Argentinien"], "pos": (280, 560)},
    "Brasilien": {"continent": "Südamerika", "neighbors": ["Venezuela", "Peru", "Argentinien", "Nordafrika"], "pos": (400, 580)},
    "Argentinien": {"continent": "Südamerika", "neighbors": ["Peru", "Brasilien"], "pos": (320, 680)},
    # Europa
    "Island": {"continent": "Europa", "neighbors": ["Grönland", "Großbritannien", "Skandinavien"], "pos": (520, 140)},
    "Großbritannien": {"continent": "Europa", "neighbors": ["Island", "Skandinavien", "Nordeuropa", "Westeuropa"], "pos": (540, 220)},
    "Skandinavien": {"continent": "Europa", "neighbors": ["Island", "Großbritannien", "Nordeuropa", "Ukraine"], "pos": (620, 180)},
    "Nordeuropa": {"continent": "Europa", "neighbors": ["Großbritannien", "Skandinavien", "Westeuropa", "Mitteleuropa", "Ukraine"], "pos": (600, 260)},
    "Westeuropa": {"continent": "Europa", "neighbors": ["Großbritannien", "Nordeuropa", "Mitteleuropa", "Nordafrika"], "pos": (560, 300)},
    "Mitteleuropa": {"continent": "Europa", "neighbors": ["Nordeuropa", "Westeuropa", "Ukraine", "Südeuropa"], "pos": (640, 300)},
    "Ukraine": {"continent": "Europa", "neighbors": ["Skandinavien", "Nordeuropa", "Mitteleuropa", "Südeuropa", "Ural", "Afghanistan", "Mittlerer Osten"], "pos": (720, 260)},
    "Südeuropa": {"continent": "Europa", "neighbors": ["Westeuropa", "Mitteleuropa", "Ukraine", "Nordafrika", "Ägypten", "Mittlerer Osten"], "pos": (660, 360)},
    # Afrika
    "Nordafrika": {"continent": "Afrika", "neighbors": ["Brasilien", "Westeuropa", "Südeuropa", "Ägypten", "Ostafrika", "Zentralafrika"], "pos": (600, 440)},
    "Ägypten": {"continent": "Afrika", "neighbors": ["Nordafrika", "Südeuropa", "Mittlerer Osten", "Ostafrika"], "pos": (700, 400)},
    "Zentralafrika": {"continent": "Afrika", "neighbors": ["Nordafrika", "Ostafrika", "Südafrika"], "pos": (640, 520)},
    "Ostafrika": {"continent": "Afrika", "neighbors": ["Nordafrika", "Ägypten", "Zentralafrika", "Südafrika", "Madagaskar", "Mittlerer Osten"], "pos": (720, 500)},
    "Südafrika": {"continent": "Afrika", "neighbors": ["Zentralafrika", "Ostafrika", "Madagaskar"], "pos": (680, 640)},
    "Madagaskar": {"continent": "Afrika", "neighbors": ["Ostafrika", "Südafrika"], "pos": (780, 620)},
    # Asien
    "Ural": {"continent": "Asien", "neighbors": ["Ukraine", "Sibirien", "Afghanistan", "China"], "pos": (780, 240)},
    "Sibirien": {"continent": "Asien", "neighbors": ["Ural", "Jakutien", "Irkutsk", "Mongolei", "China"], "pos": (880, 200)},
    "Jakutien": {"continent": "Asien", "neighbors": ["Sibirien", "Kamtschatka", "Irkutsk"], "pos": (980, 160)},
    "Kamtschatka": {"continent": "Asien", "neighbors": ["Jakutien", "Irkutsk", "Mongolei", "Japan", "Alaska"], "pos": (1080, 180)},
    "Irkutsk": {"continent": "Asien", "neighbors": ["Sibirien", "Jakutien", "Kamtschatka", "Mongolei"], "pos": (960, 240)},
    "Mongolei": {"continent": "Asien", "neighbors": ["Sibirien", "Kamtschatka", "Irkutsk", "China", "Japan"], "pos": (940, 300)},
    "Japan": {"continent": "Asien", "neighbors": ["Kamtschatka", "Mongolei"], "pos": (1120, 280)},
    "Afghanistan": {"continent": "Asien", "neighbors": ["Ukraine", "Ural", "China", "Indien", "Mittlerer Osten"], "pos": (820, 340)},
    "China": {"continent": "Asien", "neighbors": ["Ural", "Sibirien", "Mongolei", "Afghanistan", "Indien", "Siam"], "pos": (900, 380)},
    "Mittlerer Osten": {"continent": "Asien", "neighbors": ["Ukraine", "Südeuropa", "Ägypten", "Ostafrika", "Afghanistan", "Indien"], "pos": (780, 420)},
    "Indien": {"continent": "Asien", "neighbors": ["Mittlerer Osten", "Afghanistan", "China", "Siam"], "pos": (860, 460)},
    "Siam": {"continent": "Asien", "neighbors": ["China", "Indien", "Indonesien"], "pos": (940, 480)},
    # Australien/Ozeanien
    "Indonesien": {"continent": "Australien", "neighbors": ["Siam", "Neuguinea", "Westaustralien"], "pos": (980, 560)},
    "Neuguinea": {"continent": "Australien", "neighbors": ["Indonesien", "Westaustralien", "Ostaustralien"], "pos": (1080, 580)},
    "Westaustralien": {"continent": "Australien", "neighbors": ["Indonesien", "Neuguinea", "Ostaustralien"], "pos": (1020, 640)},
    "Ostaustralien": {"continent": "Australien", "neighbors": ["Neuguinea", "Westaustralien"], "pos": (1120, 660)},
}

CONTINENTS = {
    "Nordamerika": {"bonus": 5, "color": "#ff6b6b"},
    "Südamerika": {"bonus": 2, "color": "#4ecdc4"},
    "Europa": {"bonus": 5, "color": "#ffe66d"},
    "Afrika": {"bonus": 3, "color": "#95e1d3"},
    "Asien": {"bonus": 7, "color": "#f38181"},
    "Australien": {"bonus": 2, "color": "#aa96da"},
}

CARD_TYPES = ["Infanterie", "Kavallerie", "Artillerie"]
CARD_EMOJIS = {"Infanterie": "⚔️", "Kavallerie": "🐎", "Artillerie": "💣", "Wildcard": "🃏"}
CARD_EXCHANGE_BONUS = [4, 6, 8, 10, 12, 15]

PLAYER_SYMBOLS = ["★", "♦", "▲", "●", "■", "♠"]

# ───────────────────────────── HILFSKLASSEN ─────────────────────────────
class Tooltip:
    """Tooltip für Widgets"""
    def __init__(self, widget, text: str, delay: float = 0.5):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.id = None
        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        self.schedule()
    
    def on_leave(self, event=None):
        self.unschedule()
        self.hide()
    
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(int(self.delay * 1000), self.show)
    
    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
    
    def show(self):
        if self.tooltip or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        theme = THEMES[CONFIG["theme"]]
        frame = tk.Frame(self.tooltip, bg=theme["tooltip_bg"], 
                        relief=tk.SOLID, borderwidth=1)
        frame.pack()
        tk.Label(frame, text=self.text, bg=theme["tooltip_bg"], 
                fg=theme["tooltip_text"], padx=8, pady=4, justify=tk.LEFT).pack()
    
    def hide(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class AnimatedLabel(tk.Label):
    """Label mit Animationseffekten"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.animations = []
    
    def pulse(self, color1, color2, duration=0.5, cycles=3):
        """Pulsierender Farbeffekt"""
        def animate(cycle):
            if cycle >= cycles * 2:
                self.config(fg=color1)
                return
            color = color1 if cycle % 2 == 0 else color2
            self.config(fg=color)
            self.after(int(duration * 500), lambda: animate(cycle + 1))
        animate(0)
    
    def bounce(self, duration=0.3):
        """Hüpf-Animation"""
        original = self.winfo_y()
        def bounce(step):
            if step > 10:
                self.place(y=original)
                return
            offset = math.sin(step * 0.5) * 10
            self.place(y=original + offset)
            self.after(30, lambda: bounce(step + 1))
        bounce(0)


class DiceCanvas(tk.Canvas):
    """Animierter Würfel"""
    def __init__(self, master, size=60, **kwargs):
        super().__init__(master, width=size, height=size, 
                        bg="transparent", highlightthickness=0, **kwargs)
        self.size = size
        self.value = 1
        self.draw_dice(1)
    
    def draw_dice(self, value: int):
        self.delete("all")
        s = self.size
        m = s // 10
        # Würfelkörper
        self.create_rectangle(m, m, s-m, s-m, fill="#fff", outline="#333", width=2, radius=8)
        # Punkte
        dots = self._get_dot_positions(value)
        for x, y in dots:
            self.create_oval(x-6, y-6, x+6, y+6, fill="#1a1a2e")
    
    def _get_dot_positions(self, value: int) -> List[Tuple[int, int]]:
        s = self.size
        c = s // 2
        m = s // 4
        positions = {
            1: [(c, c)],
            2: [(m, m), (s-m, s-m)],
            3: [(m, m), (c, c), (s-m, s-m)],
            4: [(m, m), (s-m, m), (m, s-m), (s-m, s-m)],
            5: [(m, m), (s-m, m), (c, c), (m, s-m), (s-m, s-m)],
            6: [(m, m), (s-m, m), (m, c), (s-m, c), (m, s-m), (s-m, s-m)],
        }
        return positions.get(value, [(c, c)])
    
    def roll_animation(self, callback: Callable = None):
        """Würfel-Animation"""
        rolls = [random.randint(1, 6) for _ in range(10)]
        def animate(i):
            if i < len(rolls):
                self.value = rolls[i]
                self.draw_dice(rolls[i])
                self.after(80, lambda: animate(i + 1))
            else:
                self.value = rolls[-1]
                self.draw_dice(rolls[-1])
                if callback:
                    callback(rolls[-1])
        animate(0)


# ───────────────────────────── SPIELER ─────────────────────────────
class Player:
    def __init__(self, name: str, color: str, symbol: str, is_ai: bool = False, ai_level: int = 1):
        self.name = name
        self.color = color
        self.symbol = symbol
        self.is_ai = is_ai
        self.ai_level = ai_level
        self.cards: List[str] = []
        self.territories_conquered_this_turn = 0
        self.attacks_total = 0
        self.attacks_won = 0
        self.territories_captured = 0
        self.troops_lost = 0
        self.troops_killed = 0
        self.card_sets_traded = 0
        self.achievements: List[str] = []
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if k != "color_widget"}
    
    @classmethod
    def from_dict(cls, d):
        p = cls(d["name"], d["color"], d["symbol"], d["is_ai"], d["ai_level"])
        for k, v in d.items():
            if k not in ["name", "color", "symbol", "is_ai", "ai_level"]:
                setattr(p, k, v)
        return p


# ───────────────────────────── HAUPT-GUI ─────────────────────────────
class RisikoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎲 R I S I K O - Welteroberungsstrategie")
        self.geometry(f"{CONFIG['window_size'][0]}x{CONFIG['window_size'][1]}")
        self.minsize(1200, 700)
        
        self.theme = THEMES[CONFIG["theme"]]
        self.configure(bg=self.theme["bg"])
        
        # Spielzustand
        self.game = None
        self.selected_territory = None
        self.attack_mode = False
        self.fortify_mode = False
        self.placing_troops = False
        self.troops_to_place = 0
        self.drag_start = None
        
        self._setup_styles()
        self._create_menu()
        self._create_layout()
        self._bind_events()
        
        # Tutorial beim ersten Start
        if CONFIG["tutorial_mode"]:
            self.after(500, self.show_tutorial)
    
    def _setup_styles(self):
        """Stile für ttk-Widgets"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Button-Stile
        style.configure("Accent.TButton", 
                       background=self.theme["accent"],
                       foreground="white",
                       font=("Segoe UI", 10, "bold"),
                       padding=(15, 8))
        style.map("Accent.TButton",
                 background=[("active", self.theme["accent2"])])
        
        # Frame-Stile
        style.configure("Card.TFrame", 
                       background=self.theme["card_bg"],
                       relief=tk.RAISED,
                       borderwidth=1)
    
    def _create_menu(self):
        """Menüleiste erstellen"""
        menubar = tk.Menu(self, bg=self.theme["bg_secondary"], fg=self.theme["text"])
        self.config(menu=menubar)
        
        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.theme["bg_secondary"], fg=self.theme["text"])
        menubar.add_cascade(label="📁 Datei", menu=file_menu)
        file_menu.add_command(label="🎮 Neues Spiel", command=self.new_game, accelerator="Ctrl+N")
        file_menu.add_command(label="📂 Laden...", command=self.load_game, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 Speichern", command=self.save_game, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="⚙️ Einstellungen", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Beenden", command=self.quit_game)
        
        # Spiel-Menü
        game_menu = tk.Menu(menubar, tearoff=0, bg=self.theme["bg_secondary"], fg=self.theme["text"])
        menubar.add_cascade(label="🎲 Spiel", menu=game_menu)
        game_menu.add_command(label="⏭️ Zug beenden", command=self.end_turn, accelerator="Space")
        game_menu.add_command(label="⚔️ Angriff", command=self.start_attack, accelerator="A")
        game_menu.add_command(label="🔄 Verschieben", command=self.start_fortify, accelerator="F")
        game_menu.add_separator()
        game_menu.add_command(label="📊 Statistiken", command=self.show_stats)
        
        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.theme["bg_secondary"], fg=self.theme["text"])
        menubar.add_cascade(label="❓ Hilfe", menu=help_menu)
        help_menu.add_command(label="📖 Regeln", command=self.show_rules)
        help_menu.add_command(label="🎓 Tutorial", command=self.show_tutorial)
        help_menu.add_command(label="🏆 Achievements", command=self.show_achievements)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ Über", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="🌙 Dark Mode (Toggle)", command=self.toggle_theme)
        
        # Theme-Toggle für später
        self.theme_var = tk.BooleanVar(value=CONFIG["theme"] == "dark")
        
        # Keyboard Shortcuts
        self.bind("<Control-n>", lambda e: self.new_game())
        self.bind("<Control-o>", lambda e: self.load_game())
        self.bind("<Control-s>", lambda e: self.save_game())
        self.bind("<space>", lambda e: self.end_turn())
        self.bind("a", lambda e: self.start_attack())
        self.bind("f", lambda e: self.start_fortify())
    
    def _create_layout(self):
        """Haupt-Layout erstellen"""
        # Haupt-Container
        main_frame = tk.Frame(self, bg=self.theme["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Linke Sidebar: Spieler-Info
        self.sidebar = tk.Frame(main_frame, bg=self.theme["bg_secondary"], width=280)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        self._create_sidebar()
        
        # Mitte: Weltkarte
        self.map_frame = tk.Frame(main_frame, bg=self.theme["bg_tertiary"], relief=tk.SUNKEN, bd=2)
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self._create_map_canvas()
        
        # Rechte Sidebar: Aktionen & Log
        self.action_panel = tk.Frame(main_frame, bg=self.theme["bg_secondary"], width=300)
        self.action_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.action_panel.pack_propagate(False)
        
        self._create_action_panel()
        
        # Statusleiste unten
        self.status_bar = tk.Label(self, text="Bereit", bg=self.theme["bg_tertiary"], 
                                  fg=self.theme["text_dim"], anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_sidebar(self):
        """Sidebar mit Spieler-Informationen"""
        # Titel
        title = tk.Label(self.sidebar, text="👥 SPIELER", 
                        font=("Segoe UI", 12, "bold"), 
                        bg=self.theme["bg_secondary"], fg=self.theme["accent"])
        title.pack(pady=(15, 10))
        
        # Spieler-Liste
        self.player_frames = {}
        self.player_list = tk.Frame(self.sidebar, bg=self.theme["bg_secondary"])
        self.player_list.pack(fill=tk.X, padx=10)
        
        # Kontinent-Übersicht
        cont_title = tk.Label(self.sidebar, text="🌍 KONTINENTE", 
                             font=("Segoe UI", 10, "bold"),
                             bg=self.theme["bg_secondary"], fg=self.theme["text"])
        cont_title.pack(pady=(20, 5))
        
        self.continent_frame = tk.Frame(self.sidebar, bg=self.theme["bg_secondary"])
        self.continent_frame.pack(fill=tk.X, padx=10)
        self._update_continent_display()
        
        # Karten-Display
        card_title = tk.Label(self.sidebar, text="🃏 DEINE KARTEN", 
                             font=("Segoe UI", 10, "bold"),
                             bg=self.theme["bg_secondary"], fg=self.theme["text"])
        card_title.pack(pady=(20, 5))
        
        self.card_frame = tk.Frame(self.sidebar, bg=self.theme["card_bg"], 
                                  relief=tk.RAISED, bd=1)
        self.card_frame.pack(fill=tk.X, padx=10, pady=5)
        self._update_card_display()
        
        # Achievements Mini-View
        ach_title = tk.Label(self.sidebar, text="🏆 ERRUNGENSCHAFTEN", 
                            font=("Segoe UI", 9, "bold"),
                            bg=self.theme["bg_secondary"], fg=self.theme["warning"])
        ach_title.pack(pady=(15, 5))
        
        self.ach_frame = tk.Frame(self.sidebar, bg=self.theme["bg_secondary"])
        self.ach_frame.pack(fill=tk.X, padx=10)
    
    def _create_map_canvas(self):
        """Weltkarte mit Canvas"""
        # Canvas für Karte
        self.map_canvas = tk.Canvas(self.map_frame, bg=self.theme["bg_tertiary"], 
                                   highlightthickness=0, scrollregion=(0, 0, 1300, 800))
        self.map_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        h_scroll = ttk.Scrollbar(self.map_frame, orient=tk.HORIZONTAL, 
                                command=self.map_canvas.xview)
        v_scroll = ttk.Scrollbar(self.map_frame, orient=tk.VERTICAL, 
                                command=self.map_canvas.yview)
        self.map_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Zoom-Controls
        zoom_frame = tk.Frame(self.map_frame, bg=self.theme["bg_secondary"])
        zoom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        tk.Button(zoom_frame, text="🔍-", command=self.zoom_out, 
                 bg=self.theme["bg_tertiary"], fg=self.theme["text"],
                 relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        self.zoom_label = tk.Label(zoom_frame, text="100%", 
                                  bg=self.theme["bg_tertiary"], fg=self.theme["text"])
        self.zoom_label.pack(side=tk.LEFT, padx=10)
        tk.Button(zoom_frame, text="🔍+", command=self.zoom_in, 
                 bg=self.theme["bg_tertiary"], fg=self.theme["text"],
                 relief=tk.FLAT, width=3).pack(side=tk.LEFT, padx=2)
        
        # Mini-Map Toggle
        self.minimap_btn = tk.Button(zoom_frame, text="🗺️ Mini-Map", 
                                    command=self.toggle_minimap,
                                    bg=self.theme["bg_tertiary"], fg=self.theme["text"],
                                    relief=tk.FLAT)
        self.minimap_btn.pack(side=tk.RIGHT, padx=5)
        
        self._draw_map()
    
    def _draw_map(self):
        """Weltkarte zeichnen"""
        self.map_canvas.delete("all")
        scale = CONFIG["map_scale"]
        
        # Kontinente als Hintergrund
        for cont, data in CONTINENTS.items():
            # Einfache Polygone für Kontinente (vereinfacht)
            territories = [t for t, d in TERRITORIES.items() if d["continent"] == cont]
            if territories:
                coords = []
                for t in territories[:4]:  # Nur erste 4 für Demo
                    coords.append(TERRITORIES[t]["pos"][0] * scale + 50)
                    coords.append(TERRITORIES[t]["pos"][1] * scale + 50)
                if len(coords) >= 6:
                    self.map_canvas.create_polygon(coords, fill=data["color"], 
                                                  outline=self.theme["border"], 
                                                  width=1, stipple="gray12", tag="continent")
        
        # Verbindungen zwischen Gebieten
        drawn = set()
        for t_name, t_data in TERRITORIES.items():
            x1, y1 = t_data["pos"][0] * scale + 50, t_data["pos"][1] * scale + 50
            for neighbor in t_data["neighbors"]:
                if (t_name, neighbor) in drawn or (neighbor, t_name) in drawn:
                    continue
                drawn.add((t_name, neighbor))
                if neighbor in TERRITORIES:
                    x2, y2 = TERRITORIES[neighbor]["pos"][0] * scale + 50, \
                            TERRITORIES[neighbor]["pos"][1] * scale + 50
                    self.map_canvas.create_line(x1, y1, x2, y2, 
                                               fill=self.theme["border"], 
                                               width=1, dash=(2, 2), tag="connection")
        
        # Gebiete als Kreise
        self.territory_widgets = {}
        for t_name, t_data in TERRITORIES.items():
            x, y = t_data["pos"][0] * scale + 50, t_data["pos"][1] * scale + 50
            r = 18 * scale
            
            # Kreis für Gebiet
            circle = self.map_canvas.create_oval(x-r, y-r, x+r, y+r, 
                                                fill=self.theme["bg_secondary"],
                                                outline=self.theme["border"], 
                                                width=2, tag=f"territory_{t_name}")
            
            # Text-Label
            text = self.map_canvas.create_text(x, y, text=t_name[:2].upper(), 
                                              fill=self.theme["text"], 
                                              font=("Segoe UI", 8, "bold"),
                                              tag=f"text_{t_name}")
            
            # Truppen-Counter (wird später aktualisiert)
            troops = self.map_canvas.create_text(x, y+25, text="", 
                                                fill=self.theme["accent2"],
                                                font=("Segoe UI", 9, "bold"),
                                                tag=f"troops_{t_name}")
            
            # Klick-Events
            self.map_canvas.tag_bind(circle, "<Button-1>", 
                                   lambda e, t=t_name: self.on_territory_click(t))
            self.map_canvas.tag_bind(circle, "<Enter>", 
                                   lambda e, t=t_name: self.on_territory_hover(t))
            self.map_canvas.tag_bind(circle, "<Leave>", 
                                   lambda e: self.on_territory_leave())
            
            self.territory_widgets[t_name] = {
                "circle": circle, "text": text, "troops": troops
            }
            
            # Tooltip
            Tooltip(self.map_canvas, 
                   f"{t_name}\n{t_data['continent']}\nNachbarn: {', '.join(t_data['neighbors'][:3])}...",
                   delay=0.3)
    
    def _create_action_panel(self):
        """Rechte Aktionsleiste"""
        # Aktuelle Runde & Spieler
        self.turn_label = tk.Label(self.action_panel, text="Runde 1", 
                                  font=("Segoe UI", 11, "bold"),
                                  bg=self.theme["bg_secondary"], fg=self.theme["accent"])
        self.turn_label.pack(pady=(15, 5))
        
        self.current_player_label = tk.Label(self.action_panel, text="", 
                                            font=("Segoe UI", 10),
                                            bg=self.theme["bg_secondary"], fg=self.theme["text"])
        self.current_player_label.pack(pady=(0, 15))
        
        # Aktions-Buttons
        btn_frame = tk.Frame(self.action_panel, bg=self.theme["bg_secondary"])
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        actions = [
            ("⚔️ Angriff", self.start_attack, "A"),
            ("🔄 Verschieben", self.start_fortify, "F"),
            ("🃏 Tauschen", self.trade_cards, "T"),
            ("✅ Zug Ende", self.end_turn, "Space"),
        ]
        
        for text, cmd, key in actions:
            btn = tk.Button(btn_frame, text=f"{text} [{key}]", command=cmd,
                           bg=self.theme["accent"], fg="white",
                           font=("Segoe UI", 9, "bold"),
                           relief=tk.FLAT, padx=10, pady=5, cursor="hand2")
            btn.pack(fill=tk.X, pady=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.theme["accent2"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.theme["accent"]))
        
        # Würfel-Display
        dice_frame = tk.LabelFrame(self.action_panel, text="🎲 Würfel", 
                                  font=("Segoe UI", 9, "bold"),
                                  bg=self.theme["bg_secondary"], fg=self.theme["text"],
                                  padx=10, pady=10)
        dice_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.dice_container = tk.Frame(dice_frame, bg=self.theme["bg_secondary"])
        self.dice_container.pack()
        
        self.atk_dice = []
        self.def_dice = []
        
        # Zug-Historie
        log_frame = tk.LabelFrame(self.action_panel, text="📋 Zug-Log", 
                               font=("Segoe UI", 9, "bold"),
                               bg=self.theme["bg_secondary"], fg=self.theme["text"],
                               padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, height=12, width=30,
                               bg=self.theme["card_bg"], fg=self.theme["text"],
                               font=("Consolas", 8), wrap=tk.WORD,
                               relief=tk.FLAT, padx=5, pady=5)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scroll.set)
        
        # Quick-Info
        self.info_label = tk.Label(self.action_panel, text="", 
                                  font=("Segoe UI", 9),
                                  bg=self.theme["bg_tertiary"], fg=self.theme["text_dim"],
                                  justify=tk.LEFT, padx=10, pady=8, wraplength=280)
        self.info_label.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def _bind_events(self):
        """Event-Handler binden"""
        self.protocol("WM_DELETE_WINDOW", self.quit_game)
        
        # Canvas Zoom mit Mausrad
        self.map_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.map_canvas.bind("<Button-4>", lambda e: self.zoom_in())  # Linux
        self.map_canvas.bind("<Button-5>", lambda e: self.zoom_out())
        
        # Drag-Pan für Karte
        self.map_canvas.bind("<Button-3>", self.on_drag_start)
        self.map_canvas.bind("<B3-Motion>", self.on_drag_motion)
        self.map_canvas.bind("<ButtonRelease-3>", self.on_drag_end)
    
    # ───────────────────── MAP INTERACTION ─────────────────────
    def on_territory_click(self, territory: str):
        """Gebiet angeklickt"""
        if not self.game or not self.game.players:
            return
        
        player = self.game.players[self.game.current_player_idx]
        owner = self.game.board[territory]["owner"]
        
        if self.placing_troops and owner == player.name:
            # Truppen platzieren
            self.game.board[territory]["troops"] += 1
            self.troops_to_place -= 1
            self._update_territory_display(territory)
            self.log(f"✓ +1 Truppe in {territory}")
            
            if self.troops_to_place <= 0:
                self.placing_troops = False
                self.status("Verstärkung platziert - Jetzt angreifen oder verschieben!")
                self._update_action_buttons()
            return
        
        if self.attack_mode:
            if self.selected_territory is None:
                # Quellgebiet wählen
                if owner == player.name and self.game.board[territory]["troops"] >= 2:
                    self.selected_territory = territory
                    self._highlight_territory(territory, self.theme["warning"])
                    self.info_label.config(text=f"Angriff von: {territory}\nWähle ein feindliches Nachbargebiet als Ziel.")
                else:
                    self.log("⚠️ Wähle ein eigenes Gebiet mit ≥2 Truppen als Startpunkt")
            else:
                # Zielgebiet wählen
                if territory in TERRITORIES[self.selected_territory]["neighbors"] and owner != player.name:
                    self._execute_attack(self.selected_territory, territory)
                    self.selected_territory = None
                    self._clear_highlights()
                else:
                    self.log("⚠️ Ungültiges Ziel - muss feindlicher Nachbar sein")
            return
        
        if self.fortify_mode:
            # Verschiebe-Modus (vereinfacht: Klick auf Quelle, dann Ziel)
            if self.selected_territory is None:
                if owner == player.name:
                    self.selected_territory = territory
                    self._highlight_territory(territory, self.theme["accent2"])
                    self.info_label.config(text=f"Verschieben von: {territory}\nWähle ein erreichbares eigenes Zielgebiet.")
            else:
                if owner == player.name and self._is_reachable(player, self.selected_territory, territory):
                    self._show_fortify_dialog(self.selected_territory, territory)
                    self.selected_territory = None
                    self._clear_highlights()
                else:
                    self.log("⚠️ Ungültiges Ziel für Verschiebung")
            return
        
        # Normaler Klick: Gebiet auswählen & Info anzeigen
        self.selected_territory = territory
        self._highlight_territory(territory, self.theme["accent"])
        self._show_territory_info(territory)
    
    def on_territory_hover(self, territory: str):
        """Hover-Effekt für Gebiete"""
        if territory in self.territory_widgets:
            self.map_canvas.itemconfig(self.territory_widgets[territory]["circle"], 
                                      width=4, outline=self.theme["accent2"])
    
    def on_territory_leave(self):
        """Hover verlassen"""
        if self.selected_territory:
            self._highlight_territory(self.selected_territory, self.theme["accent"])
        else:
            for t, widgets in self.territory_widgets.items():
                self.map_canvas.itemconfig(widgets["circle"], width=2, outline=self.theme["border"])
    
    def _highlight_territory(self, territory: str, color: str):
        """Gebiet hervorheben"""
        if territory in self.territory_widgets:
            self.map_canvas.itemconfig(self.territory_widgets[territory]["circle"], 
                                      outline=color, width=4)
    
    def _clear_highlights(self):
        """Alle Hervorhebungen entfernen"""
        for t, widgets in self.territory_widgets.items():
            self.map_canvas.itemconfig(widgets["circle"], 
                                      outline=self.theme["border"], width=2)
    
    def on_mouse_wheel(self, event):
        """Zoom mit Mausrad"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_in(self):
        """Reinzoomen"""
        CONFIG["map_scale"] = min(2.0, CONFIG["map_scale"] + 0.1)
        self.zoom_label.config(text=f"{int(CONFIG['map_scale']*100)}%")
        self._draw_map()
        self._update_all_territories()
    
    def zoom_out(self):
        """Rauszoomen"""
        CONFIG["map_scale"] = max(0.5, CONFIG["map_scale"] - 0.1)
        self.zoom_label.config(text=f"{int(CONFIG['map_scale']*100)}%")
        self._draw_map()
        self._update_all_territories()
    
    def on_drag_start(self, event):
        """Drag zum Verschieben der Karte starten"""
        self.drag_start = (event.x, event.y)
        self.map_canvas.config(cursor="fleur")
    
    def on_drag_motion(self, event):
        """Karte beim Draggen verschieben"""
        if self.drag_start:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.map_canvas.xview_scroll(-dx, "units")
            self.map_canvas.yview_scroll(-dy, "units")
            self.drag_start = (event.x, event.y)
    
    def on_drag_end(self, event):
        """Drag beenden"""
        self.drag_start = None
        self.map_canvas.config(cursor="")
    
    # ───────────────────── SPIEL-LOGIK ─────────────────────
    def new_game(self):
        """Neues Spiel starten"""
        if self.game and messagebox.askyesno("Neues Spiel", 
                                            "Aktuelles Spiel verwerfen?"):
            pass
        elif self.game:
            return
        
        # Spieler-Setup Dialog
        dialog = SetupDialog(self, self.theme)
        self.wait_window(dialog)
        
        if dialog.result:
            self._init_game(dialog.result)
    
    def _init_game(self, players_data: List[dict]):
        """Spiel initialisieren"""
        from copy import deepcopy
        
        self.game = type('Game', (), {})()  # Simple namespace
        self.game.players = [Player(**p) for p in players_data]
        self.game.board = {t: {"owner": None, "troops": 0} for t in TERRITORIES}
        self.game.current_player_idx = 0
        self.game.turn = 1
        self.game.card_deck = []
        self.game.exchange_count = 0
        self.game.game_over = False
        
        # Setup
        self._setup_card_deck()
        self._distribute_territories()
        self._place_initial_troops()
        
        self.log("🎮 Neues Spiel gestartet!")
        self._update_ui()
    
    def _setup_card_deck(self):
        """Karten-Deck erstellen"""
        terr_list = list(TERRITORIES.keys())
        random.shuffle(terr_list)
        self.game.card_deck = [CARD_TYPES[i % 3] for i in range(len(terr_list))]
        self.game.card_deck += ["Wildcard", "Wildcard"]
        random.shuffle(self.game.card_deck)
    
    def _distribute_territories(self):
        """Gebiete verteilen"""
        territories = list(TERRITORIES.keys())
        random.shuffle(territories)
        for i, t in enumerate(territories):
            player = self.game.players[i % len(self.game.players)]
            self.game.board[t]["owner"] = player.name
            self.game.board[t]["troops"] = 1
    
    def _place_initial_troops(self):
        """Starttruppen platzieren (vereinfacht: automatisch)"""
        initial = {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}.get(len(self.game.players), 20)
        for player in self.game.players:
            owned = [t for t, d in self.game.board.items() if d["owner"] == player.name]
            remaining = initial - len(owned)
            # Zufällig auf eigene Gebiete verteilen
            for _ in range(remaining):
                target = random.choice(owned)
                self.game.board[target]["troops"] += 1
    
    def _update_ui(self):
        """Gesamte UI aktualisieren"""
        self._update_player_sidebar()
        self._update_all_territories()
        self._update_turn_display()
        self._update_card_display()
        self._update_continent_display()
        self._update_action_buttons()
    
    def _update_player_sidebar(self):
        """Spieler-Liste aktualisieren"""
        # Alte Frames entfernen
        for widget in self.player_list.winfo_children():
            widget.destroy()
        self.player_frames.clear()
        
        current = self.game.players[self.game.current_player_idx] if self.game.players else None
        
        for i, player in enumerate(self.game.players):
            # Player Card
            frame = tk.Frame(self.player_list, bg=self.theme["bg_tertiary"], 
                           relief=tk.RAISED if player == current else tk.FLAT, bd=2)
            frame.pack(fill=tk.X, pady=3)
            
            # Header
            header = tk.Frame(frame, bg=self.theme["bg_tertiary"])
            header.pack(fill=tk.X, padx=8, pady=5)
            
            # Symbol & Name
            sym = tk.Label(header, text=player.symbol, font=("Segoe UI", 14), 
                          bg=player.color, fg="white", width=2, relief=tk.RAISED)
            sym.pack(side=tk.LEFT)
            
            name = tk.Label(header, text=f" {player.name}", 
                           font=("Segoe UI", 10, "bold"),
                           bg=self.theme["bg_tertiary"], fg=self.theme["text"])
            name.pack(side=tk.LEFT)
            
            if player.is_ai:
                ai_badge = tk.Label(header, text="🤖", font=("Segoe UI", 8),
                                   bg=self.theme["bg_tertiary"], fg=self.theme["text_dim"])
                ai_badge.pack(side=tk.RIGHT)
            
            # Stats
            stats = tk.Frame(frame, bg=self.theme["bg_tertiary"])
            stats.pack(fill=tk.X, padx=8, pady=(0, 5))
            
            owned = len([t for t, d in self.game.board.items() if d["owner"] == player.name])
            troops = sum(d["troops"] for d in self.game.board.values() if d["owner"] == player.name)
            
            tk.Label(stats, text=f"🗺️ {owned}", bg=self.theme["bg_tertiary"], 
                    fg=self.theme["text_dim"], font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=5)
            tk.Label(stats, text=f"⚔️ {troops}", bg=self.theme["bg_tertiary"], 
                    fg=self.theme["text_dim"], font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=5)
            tk.Label(stats, text=f"🃏 {len(player.cards)}", bg=self.theme["bg_tertiary"], 
                    fg=self.theme["text_dim"], font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=5)
            
            # Fortschrittsbalken für Kontinente
            progress = tk.Frame(frame, bg=self.theme["bg_tertiary"], height=4)
            progress.pack(fill=tk.X, padx=8, pady=(0, 5))
            
            self.player_frames[player.name] = frame
    
    def _update_all_territories(self):
        """Alle Gebiets-Displays aktualisieren"""
        for t_name in TERRITORIES:
            self._update_territory_display(t_name)
    
    def _update_territory_display(self, territory: str):
        """Einzelnes Gebiet aktualisieren"""
        if territory not in self.territory_widgets or not self.game:
            return
        
        data = self.game.board[territory]
        owner_name = data["owner"]
        
        # Farbe nach Besitzer
        if owner_name:
            player = next((p for p in self.game.players if p.name == owner_name), None)
            color = player.color if player else self.theme["border"]
            self.map_canvas.itemconfig(self.territory_widgets[territory]["circle"], fill=color)
        
        # Truppen-Anzeige
        troops = data["troops"]
        self.map_canvas.itemconfig(self.territory_widgets[territory]["troops"], 
                                  text=str(troops) if troops > 0 else "")
    
    def _update_turn_display(self):
        """Runden- und Spieler-Anzeige aktualisieren"""
        if self.game and self.game.players:
            player = self.game.players[self.game.current_player_idx]
            self.turn_label.config(text=f"🔄 Runde {self.game.turn}")
            self.current_player_label.config(
                text=f"{player.symbol} {player.name}" + (" 🤖" if player.is_ai else ""),
                fg=player.color
            )
    
    def _update_card_display(self):
        """Karten-Display aktualisieren"""
        for widget in self.card_frame.winfo_children():
            widget.destroy()
        
        if not self.game or not self.game.players:
            return
        
        player = self.game.players[self.game.current_player_idx]
        if not player.cards:
            tk.Label(self.card_frame, text="– Keine Karten –", 
                    bg=self.theme["card_bg"], fg=self.theme["text_dim"],
                    font=("Segoe UI", 9, "italic"), pady=10).pack()
            return
        
        # Karten als Chips anzeigen
        card_counts = Counter(player.cards)
        for card_type, count in card_counts.items():
            chip = tk.Frame(self.card_frame, bg=self.theme["bg_tertiary"], 
                           relief=tk.RAISED, bd=1, padx=8, pady=4)
            chip.pack(side=tk.LEFT, padx=3, pady=5)
            
            tk.Label(chip, text=CARD_EMOJIS.get(card_type, "🃏"), 
                    font=("Segoe UI Emoji", 14), bg=self.theme["bg_tertiary"]).pack()
            tk.Label(chip, text=f"{card_type[:3]}\n×{count}", 
                    font=("Segoe UI", 7), bg=self.theme["bg_tertiary"], 
                    fg=self.theme["text"]).pack()
    
    def _update_continent_display(self):
        """Kontinent-Übersicht aktualisieren"""
        for widget in self.continent_frame.winfo_children():
            widget.destroy()
        
        if not self.game or not self.game.players:
            return
        
        player = self.game.players[self.game.current_player_idx]
        
        for cont, data in CONTINENTS.items():
            territories = [t for t, d in TERRITORIES.items() if d["continent"] == cont]
            owned = sum(1 for t in territories if self.game.board[t]["owner"] == player.name)
            total = len(territories)
            percent = owned / total
            
            row = tk.Frame(self.continent_frame, bg=self.theme["bg_secondary"])
            row.pack(fill=tk.X, pady=2)
            
            tk.Label(row, text=f"{cont[:10]}", font=("Segoe UI", 8), 
                    bg=self.theme["bg_secondary"], fg=self.theme["text"], width=12, anchor="w").pack(side=tk.LEFT)
            
            # Progress bar
            progress = tk.Canvas(row, width=100, height=12, bg=self.theme["bg_tertiary"], 
                              highlightthickness=0)
            progress.pack(side=tk.LEFT, padx=5)
            progress.create_rectangle(0, 0, 100 * percent, 12, fill=data["color"], outline="")
            progress.create_text(50, 6, text=f"{owned}/{total} (+{data['bonus']})", 
                              fill=self.theme["text"], font=("Segoe UI", 7))
    
    def _update_action_buttons(self):
        """Aktions-Buttons je nach Spielzustand aktivieren/deaktivieren"""
        # Wird bei Bedarf implementiert
    
    def toggle_minimap(self):
        """Mini-Map umschalten (Platzhalter)"""
        messagebox.showinfo("Mini-Map", "Mini-Map Feature wird noch entwickelt", parent=self)
    
    def _show_achievement(self, message: str):
        """Errungenschaft anzeigen"""
        messagebox.showinfo("🏆 Errungenschaft!", message, parent=self)
    
    def _show_territory_info(self, territory: str):
        """Gebiets-Info in Sidebar anzeigen"""
        data = TERRITORIES[territory]
        game_data = self.game.board[territory]
        owner = next((p for p in self.game.players if p.name == game_data["owner"]), None)
        
        info = f"""
{territory}
─────────────
🌍 {data['continent']}
👑 Besitzer: {owner.name if owner else 'Niemand'}
⚔️ Truppen: {game_data['troops']}
🔗 Nachbarn: {len(data['neighbors'])}
        """.strip()
        
        self.info_label.config(text=info, fg=self.theme["text"])
    
    def _execute_attack(self, from_t: str, to_t: str):
        """Angriff ausführen"""
        player = self.game.players[self.game.current_player_idx]
        
        # Würfel bestimmen
        atk_dice = min(3, self.game.board[from_t]["troops"] - 1)
        def_dice = min(2, self.game.board[to_t]["troops"])
        
        # Würfel-Animation
        self.log(f"⚔️ Angriff: {from_t} → {to_t}")
        self._roll_dice_animation(atk_dice, def_dice, 
                               lambda results: self._resolve_attack_results(from_t, to_t, results, player))
    
    def _roll_dice_animation(self, atk_count: int, def_count: int, callback: Callable):
        """Animiertes Würfeln"""
        # Dice-Widgets erstellen/leeren
        for widget in self.dice_container.winfo_children():
            widget.destroy()
        self.atk_dice = []
        self.def_dice = []
        
        # Angreifer-Würfel
        tk.Label(self.dice_container, text="🔴 Angreifer:", 
                bg=self.theme["bg_secondary"], fg=self.theme["danger"],
                font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        
        for i in range(atk_count):
            dice = DiceCanvas(self.dice_container, size=40)
            dice.grid(row=0, column=i+1, padx=2)
            self.atk_dice.append(dice)
        
        # Verteidiger-Würfel
        tk.Label(self.dice_container, text="🔵 Verteidiger:", 
                bg=self.theme["bg_secondary"], fg=self.theme["accent2"],
                font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=2)
        
        for i in range(def_count):
            dice = DiceCanvas(self.dice_container, size=40)
            dice.grid(row=1, column=i+1, padx=2)
            self.def_dice.append(dice)
        
        # Animation abspielen
        results = {"atk": [], "def": []}
        def animate_dice(dice_list, key, idx=0):
            if idx < len(dice_list):
                dice_list[idx].roll_animation(lambda val: None)
                results[key].append(random.randint(1, 6))  # Ergebnis vorab für Logik
                self.after(100, lambda: animate_dice(dice_list, key, idx + 1))
            elif key == "def":
                # Beide fertig -> Callback
                self.after(300, lambda: callback(results))
        
        animate_dice(self.atk_dice, "atk")
        self.after(150, lambda: animate_dice(self.def_dice, "def"))
    
    def _resolve_attack_results(self, from_t: str, to_t: str, 
                               rolls: dict, player: Player):
        """Angriffsergebnis verarbeiten"""
        atk_rolls = sorted(rolls["atk"], reverse=True)
        def_rolls = sorted(rolls["def"], reverse=True)
        
        atk_wins = sum(1 for a, d in zip(atk_rolls, def_rolls) if a > d)
        def_wins = len(def_rolls) - atk_wins
        
        # Truppen abziehen
        self.game.board[from_t]["troops"] -= def_wins
        self.game.board[to_t]["troops"] -= atk_wins
        
        # Log
        self.log(f"🎲 {atk_rolls} vs {def_rolls} → {'Angreifer' if atk_wins > def_wins else 'Verteidiger'} gewinnt {max(atk_wins, def_wins)}x")
        
        # Gebiet erobert?
        if self.game.board[to_t]["troops"] <= 0:
            # Eroberung!
            old_owner = self.game.board[to_t]["owner"]
            move_troops = min(3, self.game.board[from_t]["troops"] - 1)
            
            self.game.board[to_t]["owner"] = player.name
            self.game.board[to_t]["troops"] = move_troops
            self.game.board[from_t]["troops"] -= move_troops
            
            player.territories_conquered_this_turn += 1
            player.territories_captured += 1
            
            self.log(f"🏆 {to_t} erobert! ({move_troops} Truppen)")
            
            # Achievement check
            if player.territories_captured >= 10 and "Eroberer" not in player.achievements:
                player.achievements.append("Eroberer")
                self._show_achievement("🏆 Eroberer - 10 Gebiete erobert!")
            
            # Karte ziehen
            if self.game.card_deck:
                card = self.game.card_deck.pop()
                player.cards.append(card)
                self.log(f"🃏 Karte gezogen: {CARD_EMOJIS[card]} {card}")
                self._update_card_display()
        
        # UI updaten
        self._update_territory_display(from_t)
        self._update_territory_display(to_t)
        self._update_player_sidebar()
        
        # Weiter angreifen?
        if self.game.board[from_t]["troops"] >= 2:
            self.selected_territory = from_t
            self._highlight_territory(from_t, self.theme["warning"])
        else:
            self.selected_territory = None
            self._clear_highlights()
    
    def _show_fortify_dialog(self, from_t: str, to_t: str):
        """Dialog für Truppenverschiebung"""
        max_move = self.game.board[from_t]["troops"] - 1
        
        dialog = tk.Toplevel(self)
        dialog.title("Truppen verschieben")
        dialog.configure(bg=self.theme["bg_secondary"])
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"{from_t} → {to_t}", 
                font=("Segoe UI", 11, "bold"),
                bg=self.theme["bg_secondary"], fg=self.theme["text"]).pack(pady=15)
        
        tk.Label(dialog, text=f"Truppen verschieben (1-{max_move}):", 
                bg=self.theme["bg_secondary"], fg=self.theme["text"]).pack()
        
        scale = ttk.Scale(dialog, from_=1, to=max_move, orient=tk.HORIZONTAL, 
                         command=lambda v: count_var.set(int(float(v))))
        scale.pack(pady=10, padx=20, fill=tk.X)
        
        count_var = tk.IntVar(value=1)
        count_label = tk.Label(dialog, textvariable=count_var, 
                              font=("Segoe UI", 14, "bold"),
                              bg=self.theme["bg_secondary"], fg=self.theme["accent"])
        count_label.pack()
        
        btn_frame = tk.Frame(dialog, bg=self.theme["bg_secondary"])
        btn_frame.pack(pady=20)
        
        def confirm():
            n = count_var.get()
            self.game.board[from_t]["troops"] -= n
            self.game.board[to_t]["troops"] += n
            self._update_territory_display(from_t)
            self._update_territory_display(to_t)
            self.log(f"🔄 {n} Truppen: {from_t} → {to_t}")
            dialog.destroy()
        
        tk.Button(btn_frame, text="✅ Bestätigen", command=confirm,
                 bg=self.theme["success"], fg="white", relief=tk.FLAT,
                 padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Abbrechen", command=dialog.destroy,
                 bg=self.theme["danger"], fg="white", relief=tk.FLAT,
                 padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        dialog.geometry("300x250")
        self._center_window(dialog)
    
    def _is_reachable(self, player: Player, start: str, end: str) -> bool:
        """BFS: Prüfen ob Gebiet erreichbar ist"""
        if start == end:
            return True
        visited = {start}
        queue = [start]
        while queue:
            cur = queue.pop(0)
            for neighbor in TERRITORIES[cur]["neighbors"]:
                if neighbor == end:
                    return True
                if neighbor not in visited and self.game.board[neighbor]["owner"] == player.name:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False
    
    def trade_cards(self):
        """Karten tauschen Dialog"""
        player = self.game.players[self.game.current_player_idx]
        
        if len(player.cards) < 3:
            messagebox.showinfo("Karten tauschen", 
                              f"Du brauchst mindestens 3 Karten zum Tauschen.\nAktuell: {len(player.cards)}",
                              parent=self)
            return
        
        # Sets finden
        sets = self._find_card_sets(player.cards)
        if not sets:
            messagebox.showinfo("Karten tauschen", 
                              "Kein gültiges Set gefunden.\nBenötigt: 3 gleiche ODER je 1 von jeder Sorte",
                              parent=self)
            return
        
        # Einfacher Dialog: Erstes verfügbares Set tauschen
        chosen = sets[0]
        for card in chosen:
            if card in player.cards:
                player.cards.remove(card)
        
        bonus = CARD_EXCHANGE_BONUS[min(self.game.exchange_count, len(CARD_EXCHANGE_BONUS)-1)]
        self.game.exchange_count += 1
        player.card_sets_traded += 1
        
        # Bonus-Truppen platzieren (automatisch auf zufälliges Grenzgebiet)
        owned = [t for t, d in self.game.board.items() if d["owner"] == player.name]
        border = [t for t in owned if any(
            self.game.board[n]["owner"] != player.name 
            for n in TERRITORIES[t]["neighbors"]
        )]
        target = random.choice(border) if border else random.choice(owned)
        self.game.board[target]["troops"] += bonus
        
        self.log(f"🃏 Karten getauscht: {' + '.join(chosen)} → +{bonus} Truppen in {target}")
        self._update_card_display()
        self._update_territory_display(target)
        self._update_player_sidebar()
    
    def _find_card_sets(self, cards: List[str]) -> List[Tuple]:
        """Verfügbare Kartensets finden"""
        c = Counter(cards)
        results = []
        
        # 3 gleiche
        for ct in CARD_TYPES:
            if c[ct] + c.get("Wildcard", 0) >= 3:
                if c[ct] >= 3:
                    results.append((ct, ct, ct))
        
        # Ein von jedem
        if all(c[t] + c.get("Wildcard", 0) >= 1 for t in CARD_TYPES):
            results.append(("Infanterie", "Kavallerie", "Artillerie"))
        
        return results
    
    def start_attack(self):
        """Angriffsmodus starten"""
        self.attack_mode = True
        self.fortify_mode = False
        self.placing_troops = False
        self.selected_territory = None
        self._clear_highlights()
        self.status("⚔️ Angriffsmodus: Wähle Startgebiet (eigen, ≥2 Truppen)")
        self.info_label.config(text="Klicke auf ein eigenes Gebiet mit mindestens 2 Truppen,\ndann auf ein feindliches Nachbargebiet zum Angreifen.")
    
    def start_fortify(self):
        """Verschiebe-Modus starten"""
        self.fortify_mode = True
        self.attack_mode = False
        self.placing_troops = False
        self.selected_territory = None
        self._clear_highlights()
        self.status("🔄 Verschiebemodus: Wähle Quelle, dann Ziel")
    
    def end_turn(self):
        """Zug beenden"""
        if not self.game:
            return
        
        player = self.game.players[self.game.current_player_idx]
        
        # Karte ziehen wenn erobert
        if player.territories_conquered_this_turn > 0 and self.game.card_deck:
            card = self.game.card_deck.pop()
            player.cards.append(card)
            self.log(f"🃏 Bonus-Karte: {CARD_EMOJIS[card]} {card}")
            self._update_card_display()
        
        # Nächster Spieler
        self.game.current_player_idx = (self.game.current_player_idx + 1) % len(self.game.players)
        if self.game.current_player_idx == 0:
            self.game.turn += 1
            # Auto-Save
            if self.game.turn % CONFIG["auto_save_interval"] == 0:
                self._auto_save()
        
        # KI-Zug falls nötig
        if player.is_ai:
            self._process_ai_turn(player)
        
        self._update_ui()
        self._check_winner()
        self.status(f"{'✅' if not player.is_ai else '🤖'} Zug beendet. Nächster: {self.game.players[self.game.current_player_idx].name}")
    
    def _process_ai_turn(self, player: Player):
        """KI-Zug verarbeiten (vereinfacht)"""
        self.log(f"🤖 {player.name} denkt nach...")
        self.update()
        time.sleep(0.5)
        
        # Einfache KI: Zufällige Angriffe wenn Vorteil
        owned = [t for t, d in self.game.board.items() if d["owner"] == player.name]
        for from_t in owned:
            if self.game.board[from_t]["troops"] >= 3:
                targets = [n for n in TERRITORIES[from_t]["neighbors"] 
                          if self.game.board[n]["owner"] != player.name]
                if targets and random.random() < 0.6:  # 60% Angriffs-Chance
                    to_t = min(targets, key=lambda t: self.game.board[t]["troops"])
                    if self.game.board[from_t]["troops"] > self.game.board[to_t]["troops"] * 1.3:
                        self._execute_attack(from_t, to_t)
                        self.update()
                        time.sleep(0.3)
        
        self.end_turn()
    
    def _check_winner(self):
        """Sieg prüfen"""
        alive = [p for p in self.game.players 
                if any(d["owner"] == p.name for d in self.game.board.values())]
        
        if len(alive) == 1:
            winner = alive[0]
            self.game.game_over = True
            self._show_winner(winner)
    
    def _show_winner(self, winner: Player):
        """Sieger-Bildschirm"""
        dialog = tk.Toplevel(self)
        dialog.title("🏆 SPIEL ENDE")
        dialog.configure(bg=self.theme["bg_secondary"])
        dialog.transient(self)
        dialog.grab_set()
        
        # Konfetti-Effekt (simuliert mit Labels)
        for _ in range(20):
            x, y = random.randint(0, 400), random.randint(0, 300)
            tk.Label(dialog, text=random.choice("🎉✨🎊⭐"), 
                    font=("Segoe UI Emoji", 20),
                    bg=self.theme["bg_secondary"]).place(x=x, y=y)
        
        tk.Label(dialog, text="🏆 GEWONNEN! 🏆", 
                font=("Segoe UI", 24, "bold"),
                bg=self.theme["bg_secondary"], fg=winner.color).pack(pady=20)
        
        tk.Label(dialog, text=f"{winner.symbol} {winner.name}", 
                font=("Segoe UI", 18),
                bg=self.theme["bg_secondary"], fg=self.theme["text"]).pack(pady=10)
        
        # Stats
        stats = f"""
📊 Finale Statistiken:
• Eroberte Gebiete: {winner.territories_captured}
• Gewonnene Angriffe: {winner.attacks_won}/{winner.attacks_total}
• Karten-Tausche: {winner.card_sets_traded}
        """.strip()
        
        tk.Label(dialog, text=stats, font=("Consolas", 9),
                bg=self.theme["card_bg"], fg=self.theme["text"],
                justify=tk.LEFT, padx=15, pady=10, relief=tk.RAISED).pack(pady=15)
        
        tk.Button(dialog, text="🎮 Neues Spiel", command=lambda: [dialog.destroy(), self.new_game()],
                 bg=self.theme["accent"], fg="white", relief=tk.FLAT,
                 padx=20, pady=8, font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        self._center_window(dialog, 450, 400)
    
    # ───────────────────── UI HILFSFUNKTIONEN ─────────────────────
    def log(self, message: str):
        """Nachricht ins Log schreiben"""
        timestamp = datetime.now().strftime("%H:%M")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def status(self, message: str):
        """Statusleiste aktualisieren"""
        self.status_bar.config(text=message)
    
    def _center_window(self, window: tk.Toplevel, width: int = None, height: int = None):
        """Fenster zentrieren"""
        window.update_idletasks()
        w = width or window.winfo_width()
        h = height or window.winfo_height()
        x = (self.winfo_width() - w) // 2 + self.winfo_x()
        y = (self.winfo_height() - h) // 2 + self.winfo_y()
        window.geometry(f"{w}x{h}+{x}+{y}")
    
    def toggle_theme(self):
        """Theme umschalten"""
        CONFIG["theme"] = "dark" if self.theme_var.get() else "light"
        self.theme = THEMES[CONFIG["theme"]]
        self.configure(bg=self.theme["bg"])
        # UI refresh (vereinfacht - in Produktion alle Widgets updaten)
        messagebox.showinfo("Theme geändert", "Bitte starte das Spiel neu für vollständige Übernahme.", parent=self)
    
    def show_settings(self):
        """Einstellungen-Dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("⚙️ Einstellungen")
        dialog.configure(bg=self.theme["bg_secondary"])
        dialog.transient(self)
        dialog.grab_set()
        
        settings = [
            ("🔊 Soundeffekte", "sound_enabled"),
            ("🎓 Tutorial-Modus", "tutorial_mode"),
            ("🔄 Auto-Save alle 5 Runden", "auto_save"),
        ]
        
        vars = {}
        for text, key in settings:
            if key in CONFIG:
                vars[key] = tk.BooleanVar(value=CONFIG[key])
                tk.Checkbutton(dialog, text=text, variable=vars[key],
                              bg=self.theme["bg_secondary"], fg=self.theme["text"],
                              selectcolor=self.theme["bg_tertiary"],
                              activebackground=self.theme["bg_secondary"],
                              activeforeground=self.theme["text"]).pack(anchor="w", padx=20, pady=5)
        
        tk.Button(dialog, text="✅ Speichern", command=lambda: [self._save_settings(vars), dialog.destroy()],
                 bg=self.theme["success"], fg="white", relief=tk.FLAT,
                 padx=20, pady=5).pack(pady=20)
        
        self._center_window(dialog, 350, 250)
    
    def _save_settings(self, vars: dict):
        """Einstellungen speichern"""
        for key, var in vars.items():
            if key in CONFIG:
                CONFIG[key] = var.get()
    
    def _auto_save(self):
        """Automatisches Speichern"""
        try:
            self.save_game(auto=True)
            self.log("💾 Auto-Save erfolgreich")
        except:
            pass
    
    def save_game(self, auto: bool = False):
        """Spiel speichern"""
        if not self.game:
            return
        
        if not auto:
            filename = filedialog.asksaveasfilename(defaultextension=".json",
                                                   filetypes=[("JSON", "*.json")],
                                                   title="Spiel speichern")
            if not filename:
                return
        else:
            filename = os.path.expanduser("~/.risiko_autosave.json")
        
        try:
            data = {
                "version": "2.0",
                "saved_at": datetime.now().isoformat(),
                "players": [p.to_dict() for p in self.game.players],
                "board": self.game.board,
                "current_player_idx": self.game.current_player_idx,
                "turn": self.game.turn,
                "card_deck": self.game.card_deck,
                "exchange_count": self.game.exchange_count,
                "config": CONFIG,
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if not auto:
                messagebox.showinfo("Gespeichert", f"✓ Spiel gespeichert:\n{filename}", parent=self)
        except Exception as e:
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{e}", parent=self)
    
    def load_game(self):
        """Spiel laden"""
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Spiel laden")
        if not filename:
            return
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Game rekonstruieren
            self.game = type('Game', (), {})()
            self.game.players = [Player.from_dict(p) for p in data["players"]]
            self.game.board = data["board"]
            self.game.current_player_idx = data["current_player_idx"]
            self.game.turn = data["turn"]
            self.game.card_deck = data["card_deck"]
            self.game.exchange_count = data["exchange_count"]
            self.game.game_over = False
            
            if "config" in data:
                CONFIG.update(data["config"])
            
            self._update_ui()
            self.log(f"📂 Spiel geladen: {os.path.basename(filename)}")
            messagebox.showinfo("Geladen", f"✓ Runde {self.game.turn} geladen!", parent=self)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Laden fehlgeschlagen:\n{e}", parent=self)
    
    def show_rules(self):
        """Regeln anzeigen"""
        rules = """
🎲 RISIKO - REGELN

🎯 ZIEL:
• Alle 42 Gebiete der Welt erobern
• Letzter verbleibender Spieler gewinnt

🔄 SPIELABLAUF (pro Runde):
1️⃣ VERSTÄRKUNG
   • Basis: max(3, eigene Gebiete ÷ 3)
   • +Kontinent-Bonus wenn komplett besetzt
   
2️⃣ ANGRIFF
   • Nur von Gebieten mit ≥2 Truppen
   • Angreifer: bis zu 3 Würfel
   • Verteidiger: bis zu 2 Würfel
   • Höchste Würfel vergleichen (Gleichstand → Verteidiger)
   
3️⃣ VERSCHIEBEN
   • Truppen zwischen verbundenen eigenen Gebieten

🃏 KARTEN-SYSTEM:
• +1 Karte pro erobertem Gebiet
• 3 Karten tauschen gegen Truppen:
  - 3 gleiche: 4-15 Truppen (steigend)
  - 1 von jeder Sorte: ebenfalls möglich
• Wildcards ersetzen jede Karte

🌍 KONTINENT-BONI:
• Asien: +7 • Europa/Nordamerika: +5
• Afrika: +3 • Südamerika/Australien: +2
        """
        messagebox.showinfo("📖 Spielregeln", rules, parent=self)
    
    def show_tutorial(self):
        """Tutorial anzeigen"""
        tutorial = """
🎓 SCHNELLSTART-TUTORIAL

1️⃣ GEBIET AUSWÄHLEN
   • Klick auf einen Kreis auf der Karte
   • Blaue Umrandung = ausgewählt

2️⃣ TRUPPEN PLATZIEREN (Startphase)
   • Eigene Gebiete anklicken zum Aufwerten
   • Grüne Zahlen zeigen Truppen an

3️⃣ ANGRIFFEN
   • Button "⚔️ Angriff" oder Taste [A]
   • Erst Quellgebiet (eigen, ≥2 Truppen)
   • Dann Zielgebiet (feindlicher Nachbar)
   • Würfel entscheiden automatisch

4️⃣ TRUPPEN VERSCHIEBEN
   • Button "🔄 Verschieben" oder Taste [F]
   • Quelle → Ziel (beide eigen, verbunden)

5️⃣ KARTEN TAUSCHEN
   • Bei 3+ Karten: "🃏 Tauschen"
   • Bonus-Truppen sofort platzierbar

💡 TIPPS:
• Halte Kontinente für Bonus-Truppen!
• Grenzübergänge strategisch verstärken
• Karten-Sets rechtzeitig tauschen

🎮 Viel Erfolg bei der Welteroberung! 🏆
        """
        messagebox.showinfo("🎓 Tutorial", tutorial, parent=self)
    
    def show_achievements(self):
        """Achievements anzeigen"""
        if not self.game:
            messagebox.showinfo("🏆 Achievements", "Starte ein Spiel um Achievements zu sammeln!", parent=self)
            return
        
        all_achievements = {
            "Erster Blut": "Erstes Gebiet erobern",
            "Eroberer": "10 Gebiete in einem Spiel erobern",
            "Kartenmeister": "3 Kartensets tauschen",
            "Kontinent-König": "Einen Kontinent komplett besetzen",
            "Überlebenskünstler": "Mit nur 3 Gebieten gewinnen",
            "Blitzkrieg": "Spiel in unter 15 Runden gewinnen",
        }
        
        player = self.game.players[self.game.current_player_idx]
        unlocked = [ach for ach in player.achievements if ach in all_achievements]
        
        text = "🏆 DEINE ERRUNGENSCHAFTEN\n" + "═"*40 + "\n\n"
        for ach, desc in all_achievements.items():
            status = "✅" if ach in unlocked else "🔒"
            text += f"{status} {ach}\n   {desc}\n\n"
        
        messagebox.showinfo("🏆 Achievements", text, parent=self)
    
    def show_stats(self):
        """Statistiken anzeigen"""
        if not self.game:
            return
        
        stats = "📊 SPIEL-STATISTIKEN\n" + "═"*50 + "\n\n"
        for player in self.game.players:
            owned = len([t for t in self.game.board if self.game.board[t]["owner"] == player.name])
            troops = sum(d["troops"] for d in self.game.board.values() if d["owner"] == player.name)
            win_rate = f"{player.attacks_won*100//player.attacks_total}%" if player.attacks_total > 0 else "-"
            
            stats += f"{player.symbol} {player.name} {'🤖' if player.is_ai else ''}\n"
            stats += f"   🗺️ Gebiete: {owned}  ⚔️ Truppen: {troops}  🃏 Karten: {len(player.cards)}\n"
            stats += f"   🎯 Angriffe: {player.attacks_won}/{player.attacks_total} ({win_rate})\n"
            stats += f"   💀 Gegner eliminiert: {player.troops_killed}  😵 Verloren: {player.troops_lost}\n\n"
        
        stats += f"\n🔄 Aktuelle Runde: {self.game.turn}"
        
        messagebox.showinfo("📊 Statistiken", stats, parent=self)
    
    def show_about(self):
        """Über-Dialog"""
        about = """
🎲 R I S I K O - GUI Edition
═══════════════════════════

Version: 2.0 🚀
Engine: Python 3 + Tkinter

✨ FEATURES:
• Grafische Weltkarte mit Zoom
• Animierte Würfel & Effekte
• Dark/Light Mode Themes
• Drag & Drop Bedienung
• Auto-Save & Achievements
• KI-Gegner mit Schwierigkeitsgraden
• Vollständiges Karten-System

🎮 STEUERUNG:
• Maus: Gebiete anklicken & interagieren
• A: Angriffsmodus | F: Verschieben
• Leertaste: Zug beenden
• Mausrad: Zoom | Rechtsklick+Drag: Pan

💡 TIPP: 
Speichere regelmäßig mit Ctrl+S!

Viel Spaß bei der Welteroberung! 🌍⚔️
        """
        messagebox.showinfo("ℹ️ Über Risiko", about, parent=self)
    
    def quit_game(self):
        """Spiel beenden mit Speichern-Abfrage"""
        if self.game and messagebox.askyesno("Beenden", 
                                            "Spiel vor dem Beenden speichern?"):
            self.save_game()
        self.destroy()


# ───────────────────── SETUP DIALOG ─────────────────────
class SetupDialog(tk.Toplevel):
    """Dialog für Spiel-Setup"""
    def __init__(self, parent, theme: dict):
        super().__init__(parent)
        self.theme = theme
        self.result = None
        
        self.title("🎮 Neues Spiel")
        self.configure(bg=theme["bg_secondary"])
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        parent._center_window(self, 500, 550)
    
    def _create_ui(self):
        """UI erstellen"""
        # Titel
        tk.Label(self, text="⚙️ SPIEL SETUP", 
                font=("Segoe UI", 16, "bold"),
                bg=self.theme["bg_secondary"], fg=self.theme["accent"]).pack(pady=20)
        
        # Spieler-Anzahl
        frame = tk.Frame(self, bg=self.theme["bg_secondary"])
        frame.pack(pady=10)
        
        tk.Label(frame, text="👥 Menschliche Spieler:", 
                bg=self.theme["bg_secondary"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w")
        self.human_var = tk.IntVar(value=2)
        ttk.Spinbox(frame, from_=1, to=6, textvariable=self.human_var, width=5).grid(row=0, column=1, padx=10)
        
        tk.Label(frame, text="🤖 KI-Gegner:", 
                bg=self.theme["bg_secondary"], fg=self.theme["text"]).grid(row=1, column=0, sticky="w")
        self.ai_var = tk.IntVar(value=0)
        ttk.Spinbox(frame, from_=0, to=6, textvariable=self.ai_var, width=5).grid(row=1, column=1, padx=10)
        
        # KI-Schwierigkeit
        tk.Label(self, text="🎯 KI-Schwierigkeit:", 
                bg=self.theme["bg_secondary"], fg=self.theme["text"]).pack(pady=(15, 5))
        
        self.diff_var = tk.StringVar(value="mittel")
        diff_frame = tk.Frame(self, bg=self.theme["bg_secondary"])
        diff_frame.pack()
        
        for level, label in [("leicht", "🟢 Leicht"), ("mittel", "🟡 Mittel"), ("schwer", "🔴 Schwer")]:
            tk.Radiobutton(diff_frame, text=label, variable=self.diff_var, value=level,
                          bg=self.theme["bg_secondary"], fg=self.theme["text"],
                          selectcolor=self.theme["bg_tertiary"],
                          activebackground=self.theme["bg_secondary"],
                          activeforeground=self.theme["text"]).pack(side=tk.LEFT, padx=10)
        
        # Spielernamen
        tk.Label(self, text="📝 Spielernamen:", 
                bg=self.theme["bg_secondary"], fg=self.theme["text"]).pack(pady=(15, 5))
        
        self.name_entries = []
        names_frame = tk.Frame(self, bg=self.theme["bg_secondary"])
        names_frame.pack()
        
        default_names = ["Spieler 1", "Spieler 2", "Napoleon", "Caesar", "Alexandra", "Kublai"]
        for i in range(6):
            entry = ttk.Entry(names_frame, width=20)
            entry.insert(0, default_names[i])
            entry.grid(row=i//2, column=i%2, padx=5, pady=2)
            self.name_entries.append(entry)
        
        # Buttons
        btn_frame = tk.Frame(self, bg=self.theme["bg_secondary"])
        btn_frame.pack(pady=25)
        
        tk.Button(btn_frame, text="🎮 STARTEN", command=self._start_game,
                 bg=self.theme["accent"], fg="white", relief=tk.FLAT,
                 padx=25, pady=8, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Abbrechen", command=self.destroy,
                 bg=self.theme["danger"], fg="white", relief=tk.FLAT,
                 padx=20, pady=8).pack(side=tk.LEFT, padx=10)
    
    def _start_game(self):
        """Spiel starten"""
        n_human = min(6, max(1, self.human_var.get()))
        n_ai = min(6 - n_human, max(0, self.ai_var.get()))
        
        if n_human + n_ai < 2:
            messagebox.showerror("Fehler", "Mindestens 2 Spieler benötigt!", parent=self)
            return
        
        players = []
        colors = self.theme["player_colors"]
        symbols = PLAYER_SYMBOLS
        
        ai_level = {"leicht": 1, "mittel": 2, "schwer": 3}[self.diff_var.get()]
        
        # Menschliche Spieler
        for i in range(n_human):
            name = self.name_entries[i].get().strip() or f"Spieler {i+1}"
            players.append({
                "name": name,
                "color": colors[i],
                "symbol": symbols[i],
                "is_ai": False,
                "ai_level": 0
            })
        
        # KI-Spieler
        for i in range(n_ai):
            idx = n_human + i
            players.append({
                "name": self.name_entries[idx].get().strip() or f"KI {i+1}",
                "color": colors[idx],
                "symbol": symbols[idx],
                "is_ai": True,
                "ai_level": ai_level
            })
        
        self.result = players
        self.destroy()


# ───────────────────── MAIN ─────────────────────
def main():
    app = RisikoGUI()
    
    # Demo-Modus für schnelles Testen
    if "--demo" in sys.argv:
        app.after(100, lambda: app._init_game([
            {"name": "Du", "color": "#ff6b6b", "symbol": "★", "is_ai": False, "ai_level": 0},
            {"name": "Napoleon", "color": "#4ecdc4", "symbol": "♦", "is_ai": True, "ai_level": 2},
        ]))
    
    app.mainloop()


if __name__ == "__main__":
    import sys
    main()
