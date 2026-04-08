"""
╔══════════════════════════════════════════════════════════════════╗
║           PIZZERIA IMPERIUM - Das ultimative Tycoon Spiel        ║
╚══════════════════════════════════════════════════════════════════╝
Steuerung:
  Maus:   Alles klickbar
  SPACE   Pause
  S       Speichern
  ESC     Menü / Zurück
"""

import pygame
import sys
import json
import os
import random
import math
import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict

# ═══════════════════════════════════════════════════════════════════
#  KONSTANTEN
# ═══════════════════════════════════════════════════════════════════
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
SAVE_FILE  = "pizzeria_save.json"
SCORES_FILE= "pizzeria_scores.json"
TITLE      = "Pizzeria Imperium"

C_BG       = (18,  18,  28)
C_PANEL    = (28,  28,  45)
C_PANEL2   = (38,  38,  60)
C_ACCENT   = (255, 100,  50)
C_ACCENT2  = (255, 200,  50)
C_GREEN    = ( 80, 220, 100)
C_RED      = (220,  70,  70)
C_BLUE     = ( 70, 150, 255)
C_PURPLE   = (180,  80, 255)
C_TEAL     = ( 50, 210, 180)
C_YELLOW   = (255, 230,  50)
C_WHITE    = (240, 240, 250)
C_GRAY     = (120, 120, 150)
C_DARKGRAY = ( 50,  50,  80)
C_BLACK    = (  5,   5,  10)
C_GOLD     = (255, 200,  30)
C_SILVER   = (180, 190, 200)
C_BRONZE   = (180, 120,  50)
C_ORANGE   = (255, 140,  30)

# ─── Pizza-Definitionen ───────────────────────────────────────────
ALLE_PIZZEN = {
    "Margherita":  {"preis": 8,  "backzeit": 12, "kosten": 2, "beliebt": 10, "freischalten": 0,    "farbe": (220,160, 80)},
    "Salami":      {"preis": 11, "backzeit": 15, "kosten": 3, "beliebt":  9, "freischalten": 0,    "farbe": (180, 60, 60)},
    "Funghi":      {"preis": 10, "backzeit": 14, "kosten": 3, "beliebt":  7, "freischalten": 200,  "farbe": (140,100, 60)},
    "Tonno":       {"preis": 12, "backzeit": 16, "kosten": 3, "beliebt":  6, "freischalten": 400,  "farbe": ( 80,150,200)},
    "Hawaii":      {"preis": 12, "backzeit": 15, "kosten": 4, "beliebt":  8, "freischalten": 600,  "farbe": (220,180, 50)},
    "Quattro":     {"preis": 15, "backzeit": 18, "kosten": 5, "beliebt":  5, "freischalten": 1200, "farbe": (160,100,180)},
    "Calzone":     {"preis": 14, "backzeit": 20, "kosten": 5, "beliebt":  6, "freischalten": 1500, "farbe": (200,140, 60)},
    "Diavola":     {"preis": 13, "backzeit": 16, "kosten": 4, "beliebt":  7, "freischalten": 800,  "farbe": (220, 50, 50)},
    "Vegetariana": {"preis": 11, "backzeit": 14, "kosten": 3, "beliebt":  6, "freischalten": 1000, "farbe": ( 80,180, 80)},
    "Speciale":    {"preis": 18, "backzeit": 22, "kosten": 6, "beliebt":  4, "freischalten": 2500, "farbe": (255,150, 30)},
}

# ─── Personal-Typen ───────────────────────────────────────────────
PERSONAL_TYPEN = {
    "Lehrling": {
        "geschwindigkeit": 0.6, "fehler_rate": 0.15,
        "gehalt_pro_30s": 3,  "einstellkosten": 20,
        "farbe": C_GRAY,  "aufgaben": ["backen"],
        "beschreibung": "Backt Pizzen, langsam aber günstig",
    },
    "Koch": {
        "geschwindigkeit": 1.0, "fehler_rate": 0.05,
        "gehalt_pro_30s": 8,  "einstellkosten": 60,
        "farbe": C_WHITE, "aufgaben": ["backen"],
        "beschreibung": "Backt Pizzen zuverlässig",
    },
    "Chefkoch": {
        "geschwindigkeit": 1.6, "fehler_rate": 0.01,
        "gehalt_pro_30s": 18, "einstellkosten": 150,
        "farbe": C_GOLD,  "aufgaben": ["backen"],
        "beschreibung": "Backt sehr schnell & präzise",
    },
    "Kellner": {
        "geschwindigkeit": 1.3, "fehler_rate": 0.02,
        "gehalt_pro_30s": 7,  "einstellkosten": 50,
        "farbe": C_BLUE,  "aufgaben": ["servieren"],
        "beschreibung": "Serviert fertige Pizzen automatisch",
    },
    "Manager": {
        "geschwindigkeit": 1.0, "fehler_rate": 0.0,
        "gehalt_pro_30s": 22, "einstellkosten": 200,
        "farbe": C_PURPLE,"aufgaben": ["backen", "servieren"],
        "beschreibung": "Backt UND serviert automatisch",
    },
}

# ─── Ofen-Upgrades ────────────────────────────────────────────────
OFEN_KAUFEN_KOSTEN = [0, 150, 300, 600, 1200, 2000, 3500, 5000, 8000, 10000]

# ─── Schwierigkeitsgrade ──────────────────────────────────────────
SCHWIERIGKEITSGRADE = {
    "Einfach": {"geduld_mult": 1.8, "preis_mult": 1.2, "kosten_mult": 0.8, "farbe": C_GREEN},
    "Normal":  {"geduld_mult": 1.0, "preis_mult": 1.0, "kosten_mult": 1.0, "farbe": C_BLUE},
    "Schwer":  {"geduld_mult": 0.6, "preis_mult": 0.9, "kosten_mult": 1.3, "farbe": C_RED},
}

# ─── Level ────────────────────────────────────────────────────────
LEVELS = [
    {"id":0,"name":"Straßenstand","ziel":500,   "max_kunden":3,  "max_personal":2},
    {"id":1,"name":"Kiosk",       "ziel":2000,  "max_kunden":5,  "max_personal":3},
    {"id":2,"name":"Imbiss",      "ziel":6000,  "max_kunden":8,  "max_personal":4},
    {"id":3,"name":"Pizzeria",    "ziel":20000, "max_kunden":12, "max_personal":6},
    {"id":4,"name":"Restaurant",  "ziel":60000, "max_kunden":18, "max_personal":8},
    {"id":5,"name":"Kette",       "ziel":200000,"max_kunden":25, "max_personal":10},
    {"id":6,"name":"Imperium",    "ziel":999999999,"max_kunden":40,"max_personal":15},
]

# ─── Achievements ─────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id":"erste_pizza",  "name":"Erste Pizza!",    "desc":"Backe deine erste Pizza",        "icon":"P", "xp":10,  "cond": lambda s: s.pizzen_gebacken>=1},
    {"id":"p10",          "name":"Pizzabäcker",     "desc":"Backe 10 Pizzen",                "icon":"P", "xp":25,  "cond": lambda s: s.pizzen_gebacken>=10},
    {"id":"p100",         "name":"Pizza-Profi",     "desc":"Backe 100 Pizzen",               "icon":"T", "xp":100, "cond": lambda s: s.pizzen_gebacken>=100},
    {"id":"e1000",        "name":"Tausender",       "desc":"Verdiene €1.000",                "icon":"E", "xp":50,  "cond": lambda s: s.gesamt_verdient>=1000},
    {"id":"e10000",       "name":"Zehntausender",   "desc":"Verdiene €10.000",               "icon":"E", "xp":200, "cond": lambda s: s.gesamt_verdient>=10000},
    {"id":"lv1",          "name":"Aufsteiger",      "desc":"Erreiche Level 1",               "icon":"L", "xp":50,  "cond": lambda s: s.level>=1},
    {"id":"lv3",          "name":"Restaurantchef",  "desc":"Erreiche Level 3",               "icon":"L", "xp":150, "cond": lambda s: s.level>=3},
    {"id":"personal5",    "name":"Team-Chef",       "desc":"Habe 5 Mitarbeiter gleichzeitig","icon":"M", "xp":150, "cond": lambda s: s.max_personal_gleichzeitig>=5},
    {"id":"allpizza",     "name":"Volle Karte",     "desc":"Schalte alle Pizzen frei",       "icon":"K", "xp":300, "cond": lambda s: len(s.freigeschaltete_pizzen)>=len(ALLE_PIZZEN)},
    {"id":"combo5",       "name":"Combo-König",     "desc":"5er Combo",                      "icon":"C", "xp":100, "cond": lambda s: s.max_combo>=5},
]

ZUFALLSEREIGNISSE = [
    {"name":"Gesundheitsinspektion!", "typ":"negativ","desc":"Geldstrafe: -€{w}",        "range":(80,300), "farbe":C_RED},
    {"name":"Prominenter Besuch!",    "typ":"positiv","desc":"Bonus: +€{w}",              "range":(200,800),"farbe":C_GOLD},
    {"name":"Rohrbruch!",             "typ":"negativ","desc":"Reparatur: -€{w}",          "range":(100,400),"farbe":C_RED},
    {"name":"Stadtfest!",             "typ":"positiv","desc":"Viele Kunden! +€{w}",       "range":(100,500),"farbe":C_YELLOW},
    {"name":"Schlechtes Wetter!",     "typ":"negativ","desc":"Weniger Kunden: -€{w}",     "range":(50,150), "farbe":C_BLUE},
    {"name":"Lieferantenrabatt!",     "typ":"positiv","desc":"Gespart: +€{w}",            "range":(50,200), "farbe":C_GREEN},
]

# ═══════════════════════════════════════════════════════════════════
#  DATENKLASSEN
# ═══════════════════════════════════════════════════════════════════
@dataclass
class Pizza:
    name: str
    fortschritt: float = 0.0   # 0..1
    fertig: bool = False
    verbrannt: bool = False

@dataclass
class Kunde:
    id: int
    pizza_name: str
    geduld: float = 100.0
    max_geduld: float = 100.0
    vip: bool = False
    x: float = 0.0
    y: float = 0.0
    ziel_x: float = 0.0
    ziel_y: float = 0.0
    tisch_id: int = -1
    emoji: str = ":-)"
    bedient: bool = False

@dataclass
class Mitarbeiter:
    id: int
    typ: str
    name: str
    aktion_timer: float = 0.0   # Countdown bis nächste Auto-Aktion
    x: float = 0.0
    y: float = 0.0

@dataclass
class Benachrichtigung:
    text: str
    farbe: tuple
    timer: float = 2.5

@dataclass
class Partikel:
    x: float; y: float
    vx: float; vy: float
    leben: float; max_leben: float
    farbe: tuple; groesse: float
    text: str = ""

# ═══════════════════════════════════════════════════════════════════
#  SPIELZUSTAND
# ═══════════════════════════════════════════════════════════════════
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.geld: float = 100.0
        self.level: int = 0
        self.gesamt_verdient: float = 0.0
        self.pizzen_gebacken: int = 0
        self.kunden_bedient: int = 0
        self.kunden_verloren: int = 0
        self.spielzeit: float = 0.0
        self.schwierigkeit: str = "Normal"
        self.achievements: list = []
        self.xp: int = 0
        self.combo: int = 0
        self.max_combo: int = 0
        self.freigeschaltete_pizzen: list = ["Margherita", "Salami"]
        self.anzahl_oefen: int = 2         # Startet mit 2 Öfen
        self.max_personal_gleichzeitig: int = 0

    def save(self):
        return {k: v for k, v in self.__dict__.items()
                if not callable(v)}

    def load(self, d):
        for k, v in d.items():
            if hasattr(self, k):
                setattr(self, k, v)

# ═══════════════════════════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ═══════════════════════════════════════════════════════════════════
def fmt(v):
    if v >= 1_000_000: return f"€{v/1_000_000:.1f}M"
    if v >= 1_000:     return f"€{v/1_000:.1f}K"
    return f"€{v:.0f}"

def fmt_zeit(s):
    return f"{int(s)//60:02d}:{int(s)%60:02d}"

def clamp(v, lo, hi): return max(lo, min(hi, v))
def dist(ax,ay,bx,by): return math.sqrt((ax-bx)**2+(ay-by)**2)
def lerp(a,b,t): return a+(b-a)*t

def draw_rect_r(surf, farbe, rect, r=8, alpha=255):
    if alpha < 255:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*farbe, alpha), (0,0,rect[2],rect[3]), border_radius=r)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, farbe, rect, border_radius=r)

def draw_text(surf, text, x, y, font, farbe=C_WHITE, center=False, right=False):
    s = font.render(str(text), True, farbe)
    rx = x - s.get_width()//2 if center else (x - s.get_width() if right else x)
    surf.blit(s, (rx, y))
    return s.get_width()

def draw_bar(surf, x, y, w, h, val, maxv, fg, bg=C_DARKGRAY):
    a = clamp(val/maxv, 0, 1) if maxv else 0
    pygame.draw.rect(surf, bg, (x,y,w,h), border_radius=3)
    if a > 0:
        pygame.draw.rect(surf, fg, (x,y,int(w*a),h), border_radius=3)

VORNAMEN  = ["Mario","Luigi","Sofia","Elena","Marco","Anna","Luca","Giulia","Matteo","Chiara"]
NACHNAMEN = ["Rossi","Ferrari","Esposito","Romano","Colombo","Ricci","Marino","Greco"]
def rand_name(): return f"{random.choice(VORNAMEN)} {random.choice(NACHNAMEN)}"

# ═══════════════════════════════════════════════════════════════════
#  BUTTON
# ═══════════════════════════════════════════════════════════════════
class Btn:
    def __init__(self, x, y, w, h, text, farbe=C_ACCENT, aktiv=True, tooltip=""):
        self.rect = pygame.Rect(x,y,w,h)
        self.text = text
        self.farbe = farbe
        self.aktiv = aktiv
        self.tooltip = tooltip
        self._hover = False

    def check(self, mpos): self._hover = self.rect.collidepoint(mpos)

    def draw(self, surf, font):
        f = self.farbe if self.aktiv else C_DARKGRAY
        if self._hover and self.aktiv:
            f = tuple(min(255, c+40) for c in f)
        draw_rect_r(surf, f, self.rect)
        s = font.render(self.text, True, C_WHITE if self.aktiv else C_GRAY)
        surf.blit(s, (self.rect.centerx - s.get_width()//2,
                      self.rect.centery - s.get_height()//2))

    def clicked(self, mpos):
        return self.aktiv and self.rect.collidepoint(mpos)

# ═══════════════════════════════════════════════════════════════════
#  PARTIKEL-SYSTEM
# ═══════════════════════════════════════════════════════════════════
class Partikel_Sys:
    def __init__(self): self.ps: list = []

    def add(self, x, y, farbe, n=8, text=""):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            sp = random.uniform(20, 80)
            self.ps.append(Partikel(x,y,math.cos(a)*sp,math.sin(a)*sp,
                                    random.uniform(0.6,1.5),1.5,farbe,random.uniform(2,5)))
        if text:
            self.ps.append(Partikel(x,y-10,random.uniform(-15,15),-55,1.5,1.5,farbe,0,text))

    def update(self, dt):
        self.ps = [p for p in self.ps if p.leben > 0]
        for p in self.ps:
            p.x+=p.vx*dt; p.y+=p.vy*dt; p.vy+=35*dt; p.leben-=dt

    def draw(self, surf, font):
        for p in self.ps:
            a = max(0.0, min(1.0, p.leben/p.max_leben))
            if p.text:
                fc = tuple(max(0, min(255, int(c*a))) for c in p.farbe)
                surf.blit(font.render(p.text,True,fc),(int(p.x),int(p.y)))
            else:
                g = int(p.groesse*a)
                if g>0:
                    fc = tuple(max(0, min(255, int(c*a))) for c in p.farbe)
                    pygame.draw.circle(surf, fc,(int(p.x),int(p.y)),g)

# ═══════════════════════════════════════════════════════════════════
#  HAUPT-SPIEL
# ═══════════════════════════════════════════════════════════════════
class Spiel:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.fT = pygame.font.SysFont("arial", 38, bold=True)
        self.fG = pygame.font.SysFont("arial", 26, bold=True)
        self.fN = pygame.font.SysFont("arial", 19)
        self.fK = pygame.font.SysFont("arial", 14)
        self.fW = pygame.font.SysFont("arial", 12)

        self.state = GameState()
        self.partikel = Partikel_Sys()
        self.notes: list = []

        # Spielobjekte
        self.oefen: list = []           # list[Optional[Pizza]]
        self.fertige_pizzen: list = []   # list[Pizza]
        self.kunden: list = []
        self.mitarbeiter: list = []

        # Timer
        self.kunden_timer = 5.0
        self.gehalt_timer = 30.0
        self.ereignis_timer = random.uniform(90, 180)
        self._naechste_kid = 0
        self._naechste_mid = 0

        # Multiplier (Forschung/Boni)
        self.mult_backzeit = 1.0
        self.mult_geduld   = 1.0
        self.mult_preis    = 1.0

        # Tischpositionen
        self.tische: list = []

        # UI-State
        self.screen_state = "menu"     # menu / schwierigkeit / spiel / pause / shop / game_over
        self.selected_pizza = "Margherita"
        self.bg_t = 0.0
        self.sterne = [(random.randint(0,SCREEN_W),random.randint(0,SCREEN_H),random.uniform(0.5,2)) for _ in range(80)]

        # Aktives Ereignis
        self.ereignis_popup = None
        self.ereignis_popup_t = 0.0

        # Level-Up
        self.levelup_timer = 0.0

        # Shop-Tab: "personal" / "oefen" / "pizzen"
        self.shop_tab = "personal"

        # Highscores
        self.highscores = self._lade_hs()
        self.save_exists = os.path.exists(SAVE_FILE)

        self._build_menu_btns()

    # ─── SETUP ────────────────────────────────────────────────────
    def _build_menu_btns(self):
        cx = SCREEN_W//2
        self.btn_neu    = Btn(cx-130, 280, 260, 52, "Neues Spiel", C_ACCENT)
        self.btn_weiter = Btn(cx-130, 345, 260, 52, "Weiterspielen", C_GREEN)
        self.btn_hs     = Btn(cx-130, 410, 260, 52, "Highscores", C_BLUE)
        self.btn_exit   = Btn(cx-130, 475, 260, 52, "Beenden", C_RED)
        self.btn_diff   = {
            n: Btn(cx-140, 200+i*80, 280, 58, n, SCHWIERIGKEITSGRADE[n]["farbe"])
            for i,n in enumerate(SCHWIERIGKEITSGRADE)
        }
        # Spiel-Leiste oben rechts
        self.btn_shop  = Btn(SCREEN_W-340, 8, 100, 34, "Shop", C_ORANGE, tooltip="Personal, Öfen, Pizzen kaufen")
        self.btn_pause = Btn(SCREEN_W-230, 8, 100, 34, "Pause", C_GRAY)
        self.btn_save  = Btn(SCREEN_W-120, 8, 110, 34, "Speichern", C_TEAL)

    def _init_spiel(self):
        """Spielfeld vorbereiten / zurücksetzen."""
        n = self.state.anzahl_oefen
        self.oefen = [None]*n
        self.fertige_pizzen = []
        self.kunden = []
        self.mitarbeiter = []
        self.kunden_timer = 5.0
        self.gehalt_timer = 30.0
        self.ereignis_timer = random.uniform(90, 180)
        self._naechste_kid = 0
        self._naechste_mid = 0
        self.mult_backzeit = 1.0
        self.mult_geduld   = 1.0
        self.mult_preis    = 1.0
        self._calc_tische()

    def _sync_oefen(self):
        """Ofenliste an aktuelle Anzahl anpassen (ohne vorhandene zu löschen)."""
        n = self.state.anzahl_oefen
        while len(self.oefen) < n:
            self.oefen.append(None)
        while len(self.oefen) > n:
            # Letzten leeren Slot entfernen
            for i in range(len(self.oefen)-1, -1, -1):
                if self.oefen[i] is None:
                    self.oefen.pop(i)
                    break
            else:
                break

    def _calc_tische(self):
        self.tische = []
        n = LEVELS[self.state.level]["max_kunden"]
        x0, y0 = 210, 60
        breite, hoehe = SCREEN_W-420, SCREEN_H-170
        cols = max(1, int(math.sqrt(n*(breite/hoehe))))
        rows = math.ceil(n/cols)
        for i in range(n):
            c, r = i%cols, i//cols
            self.tische.append((x0+(c+0.5)*(breite/cols), y0+(r+0.5)*(hoehe/rows)))

    # ─── NOTEN ────────────────────────────────────────────────────
    def note(self, text, farbe=C_WHITE, kurz=False):
        for n in self.notes: n.timer = min(n.timer, 1.5)
        self.notes.append(Benachrichtigung(text, farbe, 1.8 if kurz else 3.0))
        if len(self.notes) > 6: self.notes.pop(0)

    # ─── SPIELLOGIK ───────────────────────────────────────────────
    def pizza_in_ofen(self, slot):
        if slot >= len(self.oefen): return
        if self.oefen[slot] is not None:
            self.note("Ofen belegt!", C_YELLOW, kurz=True); return
        if self.selected_pizza not in self.state.freigeschaltete_pizzen:
            self.selected_pizza = self.state.freigeschaltete_pizzen[0]
        kosten = ALLE_PIZZEN[self.selected_pizza]["kosten"]
        if self.state.geld < kosten:
            self.note(f"Nicht genug Geld! (brauche {fmt(kosten)})", C_RED); return
        self.state.geld -= kosten
        self.oefen[slot] = Pizza(name=self.selected_pizza)
        self.note(f"Ofen {slot+1}: {self.selected_pizza}", C_ACCENT, kurz=True)

    def pizza_aus_ofen(self, slot):
        if slot >= len(self.oefen): return
        p = self.oefen[slot]
        if p is None: return
        if p.verbrannt:
            self.oefen[slot] = None
            self.note("Verbrannte Pizza weggeworfen!", C_RED); return
        if not p.fertig:
            self.note("Noch nicht fertig!", C_YELLOW, kurz=True); return
        self.oefen[slot] = None
        self.fertige_pizzen.append(p)
        self.state.pizzen_gebacken += 1
        self.note(f"{p.name} fertig!", C_GREEN, kurz=True)
        self.partikel.add(120, 300+slot*90, C_GREEN, 8)
        self._check_achievements()

    def servieren(self, fp: Pizza, k: Kunde):
        if fp.name != k.pizza_name:
            self.note(f"Falsche Pizza! Wollte {k.pizza_name}!", C_RED)
            if fp in self.fertige_pizzen: self.fertige_pizzen.remove(fp)
            self._kunde_verloren(k); return False

        sch = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]
        preis = ALLE_PIZZEN[fp.name]["preis"] * self.mult_preis * sch["preis_mult"]
        trinkgeld = preis * (k.geduld/k.max_geduld) * 0.25
        if k.vip: preis *= 1.8
        endpreis = preis + trinkgeld

        self.state.geld += endpreis
        self.state.gesamt_verdient += endpreis
        self.state.kunden_bedient += 1
        self.state.combo += 1
        if self.state.combo > self.state.max_combo:
            self.state.max_combo = self.state.combo

        if fp in self.fertige_pizzen: self.fertige_pizzen.remove(fp)
        if k in self.kunden: self.kunden.remove(k)

        self.partikel.add(k.x, k.y, C_GOLD, 12, fmt(endpreis))
        self.note(f"+{fmt(endpreis)}" + (" VIP!" if k.vip else ""), C_GOLD if k.vip else C_GREEN)
        self._check_achievements()
        self._check_levelup()
        return True

    def _kunde_verloren(self, k: Kunde):
        self.state.kunden_verloren += 1
        self.state.combo = 0
        if k in self.kunden: self.kunden.remove(k)
        self.partikel.add(k.x, k.y, C_RED, 5)

    def _neuer_kunde(self):
        lv = LEVELS[self.state.level]
        if len(self.kunden) >= lv["max_kunden"]: return
        freie = [i for i,_ in enumerate(self.tische) if not any(k.tisch_id==i for k in self.kunden)]
        if not freie: return
        tid = random.choice(freie)
        tx, ty = self.tische[tid]
        vip = random.random() < 0.07
        pizzen = self.state.freigeschaltete_pizzen
        gew = [ALLE_PIZZEN[p]["beliebt"] for p in pizzen]
        pname = random.choices(pizzen, weights=gew)[0]
        sch = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]
        geduld = 120.0 * sch["geduld_mult"] * self.mult_geduld
        k = Kunde(
            id=self._naechste_kid, pizza_name=pname,
            geduld=geduld, max_geduld=geduld, vip=vip,
            x=float(random.choice([-40, SCREEN_W+40])), y=ty,
            ziel_x=tx, ziel_y=ty, tisch_id=tid,
            emoji="V" if vip else "S",
        )
        self._naechste_kid += 1
        self.kunden.append(k)

    def mitarbeiter_einstellen(self, typ: str):
        lv = LEVELS[self.state.level]
        if len(self.mitarbeiter) >= lv["max_personal"]:
            self.note("Max. Personal erreicht!", C_RED); return
        d = PERSONAL_TYPEN[typ]
        if self.state.geld < d["einstellkosten"]:
            self.note(f"Brauche {fmt(d['einstellkosten'])}!", C_RED); return
        self.state.geld -= d["einstellkosten"]
        m = Mitarbeiter(
            id=self._naechste_mid, typ=typ, name=rand_name(),
            aktion_timer=random.uniform(2, 5),
            x=float(random.randint(250, SCREEN_W-250)),
            y=float(random.randint(100, SCREEN_H-200)),
        )
        self._naechste_mid += 1
        self.mitarbeiter.append(m)
        cnt = len(self.mitarbeiter)
        if cnt > self.state.max_personal_gleichzeitig:
            self.state.max_personal_gleichzeitig = cnt
        self.note(f"{m.name} eingestellt ({typ})", C_BLUE)
        self._check_achievements()

    def mitarbeiter_entlassen(self, mid: int):
        self.mitarbeiter = [m for m in self.mitarbeiter if m.id != mid]
        self.note("Mitarbeiter entlassen.", C_GRAY)

    def ofen_kaufen(self):
        n = self.state.anzahl_oefen
        if n >= len(OFEN_KAUFEN_KOSTEN)-1:
            self.note("Max. Öfen erreicht!", C_RED); return
        kosten = OFEN_KAUFEN_KOSTEN[n]
        if self.state.geld < kosten:
            self.note(f"Brauche {fmt(kosten)}!", C_RED); return
        self.state.geld -= kosten
        self.state.anzahl_oefen += 1
        self._sync_oefen()
        self.note(f"Neuer Ofen! Jetzt {self.state.anzahl_oefen} Öfen.", C_ORANGE)

    def pizza_freischalten(self, name: str):
        d = ALLE_PIZZEN[name]
        preis = d["freischalten"]
        if name in self.state.freigeschaltete_pizzen:
            self.note("Bereits freigeschaltet!", C_GRAY); return
        if self.state.geld < preis:
            self.note(f"Brauche {fmt(preis)}!", C_RED); return
        self.state.geld -= preis
        self.state.freigeschaltete_pizzen.append(name)
        self.note(f"Pizza freigeschaltet: {name}!", C_ACCENT)
        self._check_achievements()

    # ─── AUTO-MITARBEITER ─────────────────────────────────────────
    def _auto_mitarbeiter(self, dt: float):
        """Jeder Mitarbeiter führt seine Aufgaben automatisch aus."""
        for m in self.mitarbeiter:
            d = PERSONAL_TYPEN[m.typ]
            m.aktion_timer -= dt * d["geschwindigkeit"]
            if m.aktion_timer > 0:
                continue
            m.aktion_timer = random.uniform(2.5, 5.0) / d["geschwindigkeit"]

            aufgaben = d["aufgaben"]

            # --- BACKEN ---
            if "backen" in aufgaben:
                # Fertige Pizzen aus Ofen nehmen
                for i, op in enumerate(self.oefen):
                    if op and op.fertig and not op.verbrannt:
                        self.oefen[i] = None
                        self.fertige_pizzen.append(op)
                        self.state.pizzen_gebacken += 1
                        self.partikel.add(m.x, m.y, C_GREEN, 5)
                        self.note(f"{m.name}: {op.name} fertig!", C_GREEN, kurz=True)
                        self._check_achievements()
                        break

                # Leere Öfen befüllen (passend zu wartenden Kunden)
                for i, op in enumerate(self.oefen):
                    if op is None and self.kunden:
                        # Welche Pizza brauchen wartende Kunden?
                        benoetigt = set()
                        for k in self.kunden:
                            benoetigt.add(k.pizza_name)
                        # Schon in Arbeit?
                        in_arbeit = {o.name for o in self.oefen if o}
                        fertig_namen = {fp.name for fp in self.fertige_pizzen}
                        fehlende = [p for p in benoetigt if p not in fertig_namen and p in self.state.freigeschaltete_pizzen]
                        if not fehlende:
                            fehlende = list(benoetigt & set(self.state.freigeschaltete_pizzen))
                        if fehlende:
                            pname = random.choice(fehlende)
                            kosten = ALLE_PIZZEN[pname]["kosten"]
                            if self.state.geld >= kosten:
                                self.state.geld -= kosten
                                self.oefen[i] = Pizza(name=pname)
                                break

            # --- SERVIEREN ---
            if "servieren" in aufgaben:
                for fp in list(self.fertige_pizzen):
                    for k in list(self.kunden):
                        if fp.name == k.pizza_name:
                            self.servieren(fp, k)
                            return  # Eine Aktion pro Durchgang

    # ─── UPDATE ───────────────────────────────────────────────────
    def update(self, dt: float):
        self.bg_t += dt * 0.25
        self.partikel.update(dt)
        self.notes = [n for n in self.notes if n.timer > 0]
        for n in self.notes: n.timer -= dt

        if self.screen_state == "spiel":
            self._update_spiel(dt)
        elif self.screen_state == "levelup":
            self.levelup_timer -= dt
            if self.levelup_timer <= 0:
                self.screen_state = "spiel"
            self._partikel_regen(dt)
        elif self.screen_state == "ereignis":
            self.ereignis_popup_t -= dt
            if self.ereignis_popup_t <= 0:
                self.screen_state = "spiel"
                self.ereignis_popup = None

    def _partikel_regen(self, dt):
        if random.random() < dt * 15:
            self.partikel.add(random.randint(0,SCREEN_W), random.randint(0,SCREEN_H),
                              random.choice([C_GOLD,C_ACCENT,C_GREEN,C_BLUE,C_PURPLE]), n=3)

    def _update_spiel(self, dt: float):
        self.state.spielzeit += dt

        # Kunden spawnen
        self.kunden_timer -= dt
        if self.kunden_timer <= 0:
            self._neuer_kunde()
            if random.random() < 0.3: self._neuer_kunde()
            self.kunden_timer = max(2.5, 10.0 / max(1, self.state.level+1))

        # Kunden bewegen + Geduld
        sch = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]
        for k in list(self.kunden):
            dx, dy = k.ziel_x-k.x, k.ziel_y-k.y
            d = math.sqrt(dx*dx+dy*dy)
            if d > 2:
                sp = 110
                k.x += (dx/d)*sp*dt; k.y += (dy/d)*sp*dt
            else:
                verlust = (7.0 / sch["geduld_mult"] / self.mult_geduld) * dt
                k.geduld -= verlust
            if k.geduld <= 0:
                self.note("Kunde weg!", C_RED, kurz=True)
                self._kunde_verloren(k)

        # Pizzen backen
        for p in self.oefen:
            if p is None or p.fertig or p.verbrannt: continue
            bt = ALLE_PIZZEN[p.name]["backzeit"] * self.mult_backzeit
            p.fortschritt += dt / bt
            if p.fortschritt >= 1.2:
                p.verbrannt = True; p.fertig = False
            elif p.fortschritt >= 1.0:
                p.fertig = True

        # Gehalt
        self.gehalt_timer -= dt
        if self.gehalt_timer <= 0:
            self.gehalt_timer = 30.0
            gesamt = sum(PERSONAL_TYPEN[m.typ]["gehalt_pro_30s"] * sch["kosten_mult"]
                         for m in self.mitarbeiter)
            if gesamt > 0:
                self.state.geld -= gesamt
                self.note(f"Gehalt: -{fmt(gesamt)}", C_GRAY, kurz=True)
                if self.state.geld < 0:
                    self.state.geld = 0
                    self._game_over()

        # Zufallsereignis
        self.ereignis_timer -= dt
        if self.ereignis_timer <= 0:
            self.ereignis_timer = random.uniform(90, 200)
            if random.random() < 0.4:
                self._zufallsereignis()

        # Auto-Mitarbeiter
        self._auto_mitarbeiter(dt)

    def _check_achievements(self):
        for ach in ACHIEVEMENTS:
            if ach["id"] not in self.state.achievements:
                try:
                    if ach["cond"](self.state):
                        self.state.achievements.append(ach["id"])
                        self.state.xp += ach["xp"]
                        self.note(f"Achievement: {ach['name']}! +{ach['xp']}XP", C_GOLD)
                        self.partikel.add(SCREEN_W//2, 300, C_GOLD, 20)
                except: pass

    def _check_levelup(self):
        if self.state.level >= len(LEVELS)-1: return
        if self.state.gesamt_verdient >= LEVELS[self.state.level]["ziel"]:
            self.state.level += 1
            self.screen_state = "levelup"
            self.levelup_timer = 3.5
            self._calc_tische()
            self._speichern()
            self.note(f"LEVEL UP! {LEVELS[self.state.level]['name']}", C_GOLD)
            self._check_achievements()

    def _game_over(self):
        self.screen_state = "game_over"
        self._hs_eintrag()

    def _zufallsereignis(self):
        e = random.choice(ZUFALLSEREIGNISSE)
        w = random.randint(*e["range"])
        sch = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]
        if e["typ"] == "negativ":
            verlust = w * sch["kosten_mult"]
            self.state.geld = max(0, self.state.geld - verlust)
            desc = e["desc"].replace("{w}", fmt(verlust))
        else:
            gewinn = w * sch["preis_mult"]
            self.state.geld += gewinn
            self.state.gesamt_verdient += gewinn
            desc = e["desc"].replace("{w}", fmt(gewinn))
        self.ereignis_popup = {"name": e["name"], "desc": desc, "farbe": e["farbe"]}
        self.ereignis_popup_t = 4.0
        self.screen_state = "ereignis"

    # ─── SPEICHERN / LADEN ────────────────────────────────────────
    def _speichern(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state.save(), f, indent=2)
            self.note("Gespeichert!", C_TEAL, kurz=True)
        except Exception as e:
            self.note(f"Fehler: {e}", C_RED)

    def _laden(self):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                self.state.load(json.load(f))
            return True
        except: return False

    def _lade_hs(self):
        try:
            with open(SCORES_FILE, "r") as f: return json.load(f)
        except: return []

    def _hs_eintrag(self):
        self.highscores.append({
            "verdient": self.state.gesamt_verdient,
            "level": self.state.level,
            "pizzen": self.state.pizzen_gebacken,
            "diff": self.state.schwierigkeit,
            "datum": datetime.datetime.now().strftime("%d.%m.%y %H:%M"),
        })
        self.highscores.sort(key=lambda x: x["verdient"], reverse=True)
        self.highscores = self.highscores[:20]
        try:
            with open(SCORES_FILE, "w") as f: json.dump(self.highscores, f)
        except: pass

    # ═══════════════════════════════════════════════════════════════
    #  ZEICHNEN
    # ═══════════════════════════════════════════════════════════════
    def draw(self):
        s = self.screen_state
        if s == "menu":          self._d_menu()
        elif s == "schwierigkeit": self._d_schwierigkeit()
        elif s in ("spiel","shop","pause","levelup","ereignis"): self._d_spiel_basis()
        elif s == "highscore":   self._d_highscores()
        elif s == "game_over":   self._d_gameover()
        pygame.display.flip()

    def _d_sterne(self):
        for sx,sy,sz in self.sterne:
            h = int(80 + 50*math.sin(self.bg_t+sx*0.04))
            pygame.draw.circle(self.screen,(h,h,h+25),(sx,sy),max(1,int(sz)))

    def _d_menu(self):
        self.screen.fill(C_BG); self._d_sterne()
        draw_text(self.screen,"PIZZERIA IMPERIUM",SCREEN_W//2,130,self.fT,C_ACCENT,center=True)
        draw_text(self.screen,"Baue dein Pizza-Imperium!",SCREEN_W//2,185,self.fN,C_GRAY,center=True)
        btns = [self.btn_neu, self.btn_hs, self.btn_exit]
        if self.save_exists: btns.insert(1, self.btn_weiter)
        for b in btns: b.draw(self.screen, self.fN)
        self.partikel.draw(self.screen, self.fK)

    def _d_schwierigkeit(self):
        self.screen.fill(C_BG); self._d_sterne()
        draw_text(self.screen,"Schwierigkeit wählen",SCREEN_W//2,120,self.fG,C_WHITE,center=True)
        for n,b in self.btn_diff.items():
            b.draw(self.screen, self.fN)
            draw_text(self.screen, SCHWIERIGKEITSGRADE[n]["farbe"] and
                      {"Einfach":"Geduldige Kunden, gute Einnahmen",
                       "Normal": "Ausgewogen",
                       "Schwer": "Ungeduldige Kunden, höhere Kosten"}[n],
                      b.rect.right+15, b.rect.centery-8, self.fK, C_GRAY)
        draw_text(self.screen,"ESC = Zurück",SCREEN_W//2,SCREEN_H-35,self.fK,C_GRAY,center=True)

    def _d_spiel_basis(self):
        lv = LEVELS[self.state.level]
        self.screen.fill((22,20,35))
        for sx,sy,sz in self.sterne[:30]:
            h=int(50+25*math.sin(self.bg_t+sx*0.04))
            pygame.draw.circle(self.screen,(h,h,h+15),(sx,sy),max(1,int(sz)))

        self._d_top_leiste()
        self._d_oefen_leiste()
        self._d_spielfeld()
        self._d_rechts_leiste()
        self._d_bottom_leiste()
        self.partikel.draw(self.screen, self.fK)
        self._d_notizen()

        if self.screen_state == "pause":    self._d_pause_overlay()
        elif self.screen_state == "shop":   self._d_shop()
        elif self.screen_state == "levelup": self._d_levelup()
        elif self.screen_state == "ereignis": self._d_ereignis()

    def _d_top_leiste(self):
        draw_rect_r(self.screen, C_PANEL, (0,0,SCREEN_W,50), r=0)
        # Geld
        draw_text(self.screen,"€", 10, 8, self.fG, C_GOLD)
        draw_text(self.screen, fmt(self.state.geld), 30, 8, self.fG, C_GOLD)
        draw_text(self.screen, f"Gesamt: {fmt(self.state.gesamt_verdient)}", 10, 33, self.fW, C_GRAY)
        # Level + Fortschritt
        lv = LEVELS[self.state.level]
        prog = min(1.0, self.state.gesamt_verdient / lv["ziel"])
        draw_text(self.screen, f"Lv{self.state.level} {lv['name']}", SCREEN_W//2, 5, self.fN, C_ACCENT, center=True)
        draw_bar(self.screen, SCREEN_W//2-140, 26, 280, 12, self.state.gesamt_verdient, lv["ziel"], C_ACCENT)
        draw_text(self.screen, f"Ziel: {fmt(lv['ziel'])} ({prog*100:.0f}%)",
                  SCREEN_W//2, 28, self.fW, C_WHITE, center=True)
        # Zeit + XP
        draw_text(self.screen, f"Zeit: {fmt_zeit(self.state.spielzeit)}", SCREEN_W-500, 8, self.fW, C_GRAY)
        draw_text(self.screen, f"XP: {self.state.xp}", SCREEN_W-500, 25, self.fW, C_ACCENT)
        # Buttons
        self.btn_shop.draw(self.screen, self.fK)
        self.btn_pause.draw(self.screen, self.fK)
        self.btn_save.draw(self.screen, self.fK)

    def _d_oefen_leiste(self):
        """Linke Leiste: alle Öfen."""
        draw_rect_r(self.screen, C_PANEL, (0,50,205,SCREEN_H-160), r=0)
        draw_text(self.screen,"Öfen",103,56,self.fN,C_ACCENT,center=True)
        draw_text(self.screen,f"({self.state.anzahl_oefen}x)",160,56,self.fW,C_GRAY)

        slot_h = min(85, (SCREEN_H-230) // max(1,len(self.oefen)))
        for i, p in enumerate(self.oefen):
            oy = 82 + i*slot_h
            r = pygame.Rect(8, oy, 188, slot_h-4)
            if p is None:
                draw_rect_r(self.screen, C_DARKGRAY, r, r=6)
                draw_text(self.screen, f"Ofen {i+1}: leer", 103, oy+5, self.fK, C_GRAY, center=True)
                draw_text(self.screen, "Klick = Pizza rein", 103, oy+20, self.fW, (70,70,100), center=True)
                if slot_h > 45:
                    draw_text(self.screen,"[Taste 1-9]",103,oy+33,self.fW,(50,50,80),center=True)
            else:
                if p.verbrannt:
                    fc = C_RED; status = "VERBRANNT!"
                elif p.fertig:
                    fc = C_GREEN; status = "FERTIG - Klick!"
                else:
                    pf = ALLE_PIZZEN[p.name]["farbe"]
                    fc = tuple(int(lerp(60,c,p.fortschritt)) for c in pf)
                    status = f"{p.fortschritt*100:.0f}%"
                draw_rect_r(self.screen, fc, r, r=6)
                draw_text(self.screen, p.name, 103, oy+3, self.fK, C_WHITE, center=True)
                if not p.fertig and not p.verbrannt:
                    draw_bar(self.screen, 12, oy+slot_h-22, 182, 8, p.fortschritt, 1.0, C_ACCENT2)
                draw_text(self.screen, status, 103, oy+slot_h-36, self.fW, C_WHITE, center=True)

    def _d_spielfeld(self):
        x0, y0, bw, bh = 205, 50, SCREEN_W-415, SCREEN_H-160
        draw_rect_r(self.screen, (22,22,38), (x0,y0,bw,bh), r=0)
        for gx in range(x0,x0+bw,55):
            pygame.draw.line(self.screen,(28,28,48),(gx,y0),(gx,y0+bh))
        for gy in range(y0,y0+bh,55):
            pygame.draw.line(self.screen,(28,28,48),(x0,gy),(x0+bw,gy))

        # Tische
        for i,(tx,ty) in enumerate(self.tische):
            besetzt = any(k.tisch_id==i for k in self.kunden)
            fc = (50,50,85) if besetzt else (35,35,60)
            pygame.draw.circle(self.screen, fc,(int(tx),int(ty)),22)
            pygame.draw.circle(self.screen,(60,60,100),(int(tx),int(ty)),22,1)
            draw_text(self.screen,str(i+1),int(tx),int(ty)-8,self.fW,C_GRAY,center=True)

        # Kunden
        for k in self.kunden: self._d_kunde(k)
        # Mitarbeiter
        for m in self.mitarbeiter: self._d_mitarbeiter(m)

        # Level-Beschreibung
        lv = LEVELS[self.state.level]
        draw_text(self.screen, lv["name"], x0+bw//2, y0+8, self.fW, (50,50,80), center=True)

        # Combo
        if self.state.combo >= 3:
            a = abs(math.sin(pygame.time.get_ticks()/200))*0.3+0.7
            draw_text(self.screen,f"COMBO x{self.state.combo}!",
                      x0+bw//2, y0+30, self.fG,
                      tuple(int(c*a) for c in C_GOLD), center=True)

    def _d_kunde(self, k: Kunde):
        x,y = int(k.x),int(k.y)
        ga = k.geduld/k.max_geduld
        # Schatten
        pygame.draw.ellipse(self.screen,(15,15,25),(x-17,y+14,34,9))
        # Körper
        fc = C_GOLD if k.vip else (80,130,230)
        if ga < 0.3: fc = C_RED
        elif ga < 0.6: fc = C_YELLOW
        pygame.draw.circle(self.screen,fc,(x,y),15)
        pygame.draw.circle(self.screen,C_WHITE,(x,y),15,2)
        # Buchstabe
        draw_text(self.screen,"V" if k.vip else "K",x,y-8,self.fW,C_WHITE,center=True)
        # Geduldsbalken
        draw_bar(self.screen,x-20,y-28,40,5,k.geduld,k.max_geduld,
                 C_GREEN if ga>0.5 else C_YELLOW if ga>0.25 else C_RED)
        # Bestellzettel
        draw_text(self.screen,k.pizza_name[:7],x,y-38,self.fW,C_WHITE,center=True)
        if k.vip:
            draw_text(self.screen,"VIP",x-8,y-52,self.fW,C_GOLD)

    def _d_mitarbeiter(self, m: Mitarbeiter):
        x,y = int(m.x),int(m.y)
        fc = PERSONAL_TYPEN[m.typ]["farbe"]
        pygame.draw.ellipse(self.screen,(15,15,25),(x-14,y+12,28,8))
        pygame.draw.circle(self.screen,fc,(x,y),13)
        pygame.draw.circle(self.screen,C_WHITE,(x,y),13,1)
        draw_text(self.screen,m.typ[0],x,y-7,self.fW,C_BLACK,center=True)
        draw_text(self.screen,m.name.split()[0],x,y-24,self.fW,fc,center=True)

    def _d_rechts_leiste(self):
        x0 = SCREEN_W-210
        draw_rect_r(self.screen, C_PANEL, (x0,50,210,SCREEN_H-160), r=0)

        # Kunden
        draw_text(self.screen,f"Kunden ({len(self.kunden)})",x0+105,56,self.fN,C_BLUE,center=True)
        for i,k in enumerate(self.kunden[:5]):
            ky = 82+i*52
            kr = pygame.Rect(x0+5,ky,200,46)
            draw_rect_r(self.screen,(40,40,75) if k.vip else C_DARKGRAY, kr, r=5)
            ga = k.geduld/k.max_geduld
            gc = C_GREEN if ga>0.5 else C_YELLOW if ga>0.25 else C_RED
            draw_text(self.screen,("★" if k.vip else " ")+k.pizza_name[:12],x0+10,ky+4,self.fK,C_GOLD if k.vip else C_WHITE)
            draw_bar(self.screen,x0+8,ky+32,195,7,k.geduld,k.max_geduld,gc)
            draw_text(self.screen,f"Klicken = servieren",x0+8,ky+20,self.fW,(80,80,120))
        if len(self.kunden)>5:
            draw_text(self.screen,f"+{len(self.kunden)-5} weitere",x0+105,82+5*52+5,self.fW,C_GRAY,center=True)

        sep_y = 82+5*52+22
        pygame.draw.line(self.screen,C_DARKGRAY,(x0+5,sep_y),(x0+205,sep_y))

        # Fertige Pizzen
        draw_text(self.screen,f"Fertig ({len(self.fertige_pizzen)})",x0+105,sep_y+5,self.fK,C_GREEN,center=True)
        for i,fp in enumerate(self.fertige_pizzen[:4]):
            py = sep_y+24+i*22
            fc = ALLE_PIZZEN[fp.name]["farbe"]
            pygame.draw.rect(self.screen,fc,(x0+8,py,8,16),border_radius=2)
            draw_text(self.screen,fp.name,x0+22,py+2,self.fW,C_WHITE)

        sep2_y = sep_y+24+4*22+5
        pygame.draw.line(self.screen,C_DARKGRAY,(x0+5,sep2_y),(x0+205,sep2_y))

        # Mitarbeiter
        draw_text(self.screen,f"Personal ({len(self.mitarbeiter)})",x0+105,sep2_y+5,self.fK,C_PURPLE,center=True)
        for i,m in enumerate(self.mitarbeiter):
            py = sep2_y+24+i*22
            if py > SCREEN_H-180: break
            fc = PERSONAL_TYPEN[m.typ]["farbe"]
            draw_text(self.screen,m.name[:12],x0+8,py,self.fW,C_WHITE)
            draw_text(self.screen,m.typ,x0+115,py,self.fW,fc)

    def _d_bottom_leiste(self):
        y0 = SCREEN_H-110
        draw_rect_r(self.screen, C_PANEL, (0,y0,SCREEN_W,110), r=0)

        # Pizza-Auswahl
        draw_text(self.screen,"Auswahl:",8,y0+5,self.fW,C_GRAY)
        px = 8
        for pname in self.state.freigeschaltete_pizzen:
            pw = 88
            pr = pygame.Rect(px, y0+20, pw, 38)
            pf = ALLE_PIZZEN[pname]["farbe"]
            sel = pname == self.selected_pizza
            draw_rect_r(self.screen, pf, pr, r=5)
            if sel:
                pygame.draw.rect(self.screen,C_WHITE,pr,2,border_radius=5)
            draw_text(self.screen,pname[:8],px+44,y0+23,self.fW,C_WHITE,center=True)
            draw_text(self.screen,fmt(ALLE_PIZZEN[pname]["preis"]),px+44,y0+35,self.fW,C_GOLD,center=True)
            px += 92
            if px > SCREEN_W-200: break

        # Statistiken rechts unten
        stats = [
            f"Gebacken: {self.state.pizzen_gebacken}",
            f"Bedient: {self.state.kunden_bedient}",
            f"Verloren: {self.state.kunden_verloren}",
            f"Combo max: x{self.state.max_combo}",
        ]
        for i,s in enumerate(stats):
            draw_text(self.screen,s,SCREEN_W-390+i*97,y0+8,self.fW,C_GRAY)
        draw_text(self.screen,f"Modus: {self.state.schwierigkeit}",
                  SCREEN_W-15,y0+8,self.fW,
                  SCHWIERIGKEITSGRADE[self.state.schwierigkeit]["farbe"],right=True)

        # Hilfe
        draw_text(self.screen,"Öfen: klicken | Kunden: klicken | Shop: oben rechts",
                  SCREEN_W//2,y0+62,self.fW,(70,70,100),center=True)
        draw_text(self.screen,"Taste 1-9: Ofen befüllen | SPACE: Pause | S: Speichern",
                  SCREEN_W//2,y0+78,self.fW,(60,60,90),center=True)

    def _d_notizen(self):
        cx = SCREEN_W//2
        by = SCREEN_H-125
        for i,n in enumerate(reversed(self.notes[-5:])):
            a = max(0.0, min(1.0, n.timer))
            fc = tuple(max(0, min(255, int(c*a))) for c in n.farbe)
            draw_text(self.screen, n.text, cx, by-i*22, self.fK, fc, center=True)

    def _d_pause_overlay(self):
        s = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        s.fill((0,0,0,160)); self.screen.blit(s,(0,0))
        draw_text(self.screen,"PAUSE",SCREEN_W//2,SCREEN_H//2-40,self.fT,C_WHITE,center=True)
        draw_text(self.screen,"SPACE = Weiterspielen   ESC = Hauptmenü",
                  SCREEN_W//2,SCREEN_H//2+20,self.fN,C_GRAY,center=True)

    def _d_levelup(self):
        s = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        s.fill((0,0,0,130)); self.screen.blit(s,(0,0))
        p = abs(math.sin(pygame.time.get_ticks()/280))*0.3+0.7
        lv = LEVELS[self.state.level]
        draw_text(self.screen,"LEVEL UP!",SCREEN_W//2,SCREEN_H//2-70,self.fT,
                  tuple(int(c*p) for c in C_GOLD),center=True)
        draw_text(self.screen,f"Level {self.state.level}: {lv['name']}",
                  SCREEN_W//2,SCREEN_H//2+5,self.fG,C_WHITE,center=True)
        draw_text(self.screen,f"Max Kunden: {lv['max_kunden']}  Max Personal: {lv['max_personal']}",
                  SCREEN_W//2,SCREEN_H//2+50,self.fN,C_GRAY,center=True)
        self.partikel.draw(self.screen,self.fK)

    def _d_ereignis(self):
        if not self.ereignis_popup: return
        s = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        s.fill((0,0,0,150)); self.screen.blit(s,(0,0))
        e = self.ereignis_popup
        bw,bh = 480,180; bx=(SCREEN_W-bw)//2; by=(SCREEN_H-bh)//2
        draw_rect_r(self.screen,C_PANEL,(bx,by,bw,bh),r=12)
        pygame.draw.rect(self.screen,e["farbe"],(bx,by,bw,bh),3,border_radius=12)
        draw_text(self.screen,"EREIGNIS!",SCREEN_W//2,by+18,self.fG,e["farbe"],center=True)
        draw_text(self.screen,e["name"],SCREEN_W//2,by+55,self.fG,C_WHITE,center=True)
        draw_text(self.screen,e["desc"],SCREEN_W//2,by+100,self.fN,C_GRAY,center=True)
        draw_bar(self.screen,bx+20,by+155,bw-40,8,self.ereignis_popup_t,4.0,e["farbe"])

    def _d_shop(self):
        """Shop-Overlay: Personal / Öfen / Pizzen."""
        s = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        s.fill((0,0,0,170)); self.screen.blit(s,(0,0))

        sw, sh = 800, 560
        sx = (SCREEN_W-sw)//2; sy = (SCREEN_H-sh)//2
        draw_rect_r(self.screen,C_PANEL,(sx,sy,sw,sh),r=12)
        pygame.draw.rect(self.screen,C_ACCENT,(sx,sy,sw,sh),2,border_radius=12)

        draw_text(self.screen,"SHOP",sx+sw//2,sy+12,self.fG,C_ACCENT,center=True)
        draw_text(self.screen,f"Geld: {fmt(self.state.geld)}",sx+sw-15,sy+12,self.fN,C_GOLD,right=True)
        draw_text(self.screen,"ESC / Klick außen = Schließen",sx+sw//2,sy+sh-18,self.fW,C_GRAY,center=True)

        # Tabs
        tabs = [("personal","Personal"),("oefen","Öfen"),("pizzen","Pizzen")]
        for i,(tid,tn) in enumerate(tabs):
            tx = sx+30+i*175; ty = sy+45
            fc = C_ACCENT if self.shop_tab==tid else C_DARKGRAY
            draw_rect_r(self.screen,fc,(tx,ty,160,36),r=6)
            draw_text(self.screen,tn,tx+80,ty+9,self.fN,C_WHITE,center=True)

        content_y = sy+92

        if self.shop_tab == "personal":
            lv = LEVELS[self.state.level]
            draw_text(self.screen,
                      f"Max. Personal für dieses Level: {lv['max_personal']}  |  Aktuell: {len(self.mitarbeiter)}",
                      sx+20, content_y, self.fK, C_GRAY)
            draw_text(self.screen,"Gehalt wird alle 30 Sekunden abgezogen.",sx+20,content_y+18,self.fW,C_GRAY)

            for i,(typ,d) in enumerate(PERSONAL_TYPEN.items()):
                row_y = content_y + 45 + i*72
                rr = pygame.Rect(sx+20, row_y, sw-40, 65)
                draw_rect_r(self.screen, C_PANEL2, rr, r=8)
                # Farb-Streifen
                pygame.draw.rect(self.screen, d["farbe"], (sx+20,row_y,5,65), border_radius=8)
                draw_text(self.screen, typ, sx+35, row_y+6, self.fN, d["farbe"])
                draw_text(self.screen, d["beschreibung"], sx+35, row_y+27, self.fK, C_GRAY)
                draw_text(self.screen, f"Gehalt: {fmt(d['gehalt_pro_30s'])}/30s",
                          sx+35, row_y+43, self.fW, C_GRAY)
                # Einstellkosten + Button
                kann = self.state.geld >= d["einstellkosten"] and len(self.mitarbeiter)<lv["max_personal"]
                bc = C_GREEN if kann else C_DARKGRAY
                draw_rect_r(self.screen, bc, (sx+sw-180, row_y+12, 155, 38), r=6)
                draw_text(self.screen, f"Einstellen {fmt(d['einstellkosten'])}",
                          sx+sw-103, row_y+22, self.fK, C_WHITE, center=True)
                draw_text(self.screen, f"Geschw. {d['geschwindigkeit']}x | Aufg: {', '.join(d['aufgaben'])}",
                          sx+250, row_y+6, self.fW, C_GRAY)

            # Mitarbeiter-Liste + Entlassen
            if self.mitarbeiter:
                my = content_y + 45 + len(PERSONAL_TYPEN)*72 + 10
                if my < sy+sh-60:
                    draw_text(self.screen,"Aktuelle Mitarbeiter:",sx+20,my,self.fK,C_GRAY)
                    for j,m in enumerate(self.mitarbeiter):
                        if my+22+j*22 > sy+sh-40: break
                        fc = PERSONAL_TYPEN[m.typ]["farbe"]
                        draw_text(self.screen,f"{m.name} ({m.typ})",sx+20,my+22+j*22,self.fW,fc)
                        # Entlassen-Button
                        draw_rect_r(self.screen,C_RED,(sx+sw-100,my+18+j*22,80,18),r=4)
                        draw_text(self.screen,"Entlassen",sx+sw-60,my+20+j*22,self.fW,C_WHITE,center=True)

        elif self.shop_tab == "oefen":
            n = self.state.anzahl_oefen
            draw_text(self.screen, f"Aktuelle Öfen: {n}", sx+20, content_y, self.fN, C_ORANGE)
            draw_text(self.screen,"Mehr Öfen = mehr Pizzen gleichzeitig backen.",sx+20,content_y+28,self.fK,C_GRAY)

            for i in range(1, min(len(OFEN_KAUFEN_KOSTEN), 10)):
                ry = content_y + 60 + (i-1)*55
                if ry > sy+sh-60: break
                kosten = OFEN_KAUFEN_KOSTEN[i]
                bereits = i < n
                rr = pygame.Rect(sx+20, ry, sw-40, 48)
                bg = (30,60,30) if bereits else C_PANEL2
                draw_rect_r(self.screen, bg, rr, r=6)
                draw_text(self.screen, f"Ofen {i+1}", sx+35, ry+7, self.fN,
                          C_GREEN if bereits else C_WHITE)
                draw_text(self.screen, f"Slot {i+1} freischalten",sx+120,ry+7,self.fK,C_GRAY)
                if bereits:
                    draw_text(self.screen,"✓ Besitz",sx+sw-120,ry+14,self.fN,C_GREEN,center=True)
                else:
                    kann = self.state.geld >= kosten and i == n
                    ist_naechster = i == n
                    bc = C_ORANGE if (kann and ist_naechster) else C_DARKGRAY
                    draw_rect_r(self.screen, bc, (sx+sw-170,ry+7,145,34),r=6)
                    lbl = f"Kaufen {fmt(kosten)}" if ist_naechster else "Erst vorherige"
                    draw_text(self.screen,lbl,sx+sw-97,ry+16,self.fK,C_WHITE,center=True)

        elif self.shop_tab == "pizzen":
            draw_text(self.screen,"Schalte neue Pizzasorten frei:",sx+20,content_y,self.fN,C_ACCENT)
            draw_text(self.screen,"Freigeschaltete Pizzen können von dir und deinen Mitarbeitern gebacken werden.",
                      sx+20,content_y+26,self.fK,C_GRAY)
            items = list(ALLE_PIZZEN.items())
            cols = 2
            for i,(pname,pd) in enumerate(items):
                col = i%cols; row = i//cols
                px2 = sx+20+col*(sw//2-15)
                py2 = content_y+55+row*68
                if py2 > sy+sh-55: break
                bereits = pname in self.state.freigeschaltete_pizzen
                rr = pygame.Rect(px2,py2,sw//2-25,60)
                bg = (25,50,25) if bereits else C_PANEL2
                draw_rect_r(self.screen, bg, rr, r=6)
                pf = pd["farbe"]
                pygame.draw.rect(self.screen,pf,(px2,py2,5,60),border_radius=6)
                draw_text(self.screen,pname,px2+14,py2+5,self.fN,C_WHITE)
                draw_text(self.screen,f"Preis: {fmt(pd['preis'])} | Backzeit: {pd['backzeit']}s",
                          px2+14,py2+26,self.fW,C_GRAY)
                draw_text(self.screen,f"Kosten/Backen: {fmt(pd['kosten'])}",
                          px2+14,py2+40,self.fW,C_GRAY)
                if bereits:
                    draw_text(self.screen,"freigeschaltet",px2+(sw//2-30)-5,py2+20,self.fK,C_GREEN,right=True)
                elif pd["freischalten"] == 0:
                    draw_text(self.screen,"gratis",px2+(sw//2-30)-5,py2+20,self.fK,C_TEAL,right=True)
                else:
                    kann = self.state.geld >= pd["freischalten"]
                    bc = C_ACCENT if kann else C_DARKGRAY
                    draw_rect_r(self.screen,bc,(px2+(sw//2-145),py2+12,130,34),r=6)
                    draw_text(self.screen,f"Freischalten {fmt(pd['freischalten'])}",
                              px2+(sw//2-80),py2+22,self.fW,C_WHITE,center=True)

    def _d_highscores(self):
        self.screen.fill(C_BG); self._d_sterne()
        draw_text(self.screen,"HIGHSCORES",SCREEN_W//2,50,self.fT,C_GOLD,center=True)
        headers=["#","Verdient","Level","Pizzen","Modus","Datum"]
        xs=[60,180,360,460,560,700]
        for h,x in zip(headers,xs): draw_text(self.screen,h,x,110,self.fN,C_GRAY)
        for i,hs in enumerate(self.highscores[:15]):
            y=145+i*34
            fc=C_GOLD if i==0 else C_SILVER if i==1 else C_BRONZE if i==2 else C_WHITE
            if i%2==0: draw_rect_r(self.screen,C_PANEL,(55,y-3,SCREEN_W-110,28),r=4)
            for v,x in zip([str(i+1),fmt(hs.get("verdient",0)),str(hs.get("level",0)),
                             str(hs.get("pizzen",0)),hs.get("diff","?"),hs.get("datum","?")],xs):
                draw_text(self.screen,v,x,y,self.fN,fc)
        if not self.highscores:
            draw_text(self.screen,"Noch keine Scores!",SCREEN_W//2,300,self.fG,C_GRAY,center=True)
        draw_text(self.screen,"ESC = Zurück",SCREEN_W//2,SCREEN_H-35,self.fN,C_GRAY,center=True)

    def _d_gameover(self):
        self.screen.fill(C_BG); self._d_sterne()
        draw_text(self.screen,"GAME OVER",SCREEN_W//2,100,self.fT,C_RED,center=True)
        draw_text(self.screen,"Kein Geld mehr!",SCREEN_W//2,175,self.fG,C_GRAY,center=True)
        stats=[
            f"Verdient: {fmt(self.state.gesamt_verdient)}",
            f"Level: {self.state.level} – {LEVELS[self.state.level]['name']}",
            f"Pizzen: {self.state.pizzen_gebacken}",
            f"Kunden bedient: {self.state.kunden_bedient}",
            f"Spielzeit: {fmt_zeit(self.state.spielzeit)}",
            f"XP: {self.state.xp}",
        ]
        for i,s in enumerate(stats):
            draw_text(self.screen,s,SCREEN_W//2,230+i*38,self.fN,C_WHITE,center=True)
        draw_text(self.screen,"ENTER = Neues Spiel    ESC = Hauptmenü",
                  SCREEN_W//2,SCREEN_H-55,self.fN,C_GRAY,center=True)
        self.partikel.draw(self.screen,self.fK)

    # ═══════════════════════════════════════════════════════════════
    #  EVENTS
    # ═══════════════════════════════════════════════════════════════
    def handle_events(self):
        mpos = pygame.mouse.get_pos()
        for b in [self.btn_neu,self.btn_weiter,self.btn_hs,self.btn_exit,
                  self.btn_shop,self.btn_pause,self.btn_save]:
            b.check(mpos)
        for b in self.btn_diff.values(): b.check(mpos)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if self.screen_state == "spiel": self._speichern()
                pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN:
                self._key(ev.key)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self._click(mpos)

    def _key(self, key):
        st = self.screen_state
        if key == pygame.K_ESCAPE:
            if st in ("shop",): self.screen_state = "spiel"
            elif st == "spiel": self.screen_state = "pause"
            elif st == "pause":
                self._speichern(); self.screen_state = "menu"
            elif st in ("highscore","achievement"):
                self.screen_state = "menu"
            elif st == "schwierigkeit": self.screen_state = "menu"
            elif st == "game_over": self.screen_state = "menu"
            elif st == "levelup": self.screen_state = "spiel"
            elif st == "ereignis":
                self.screen_state = "spiel"; self.ereignis_popup = None
        elif key == pygame.K_SPACE:
            if st == "spiel": self.screen_state = "pause"
            elif st == "pause": self.screen_state = "spiel"
        elif key == pygame.K_s:
            if st in ("spiel","pause"): self._speichern()
        elif key == pygame.K_RETURN:
            if st == "game_over": self._neues_spiel()
        # Tasten 1-9: Ofen befüllen
        elif key in range(pygame.K_1, pygame.K_9+1):
            if st == "spiel":
                slot = key - pygame.K_1
                if slot < len(self.oefen):
                    if self.oefen[slot] is None:
                        self.pizza_in_ofen(slot)
                    else:
                        self.pizza_aus_ofen(slot)

    def _click(self, mpos):
        st = self.screen_state
        mx, my = mpos

        if st == "menu":        self._click_menu(mpos)
        elif st == "schwierigkeit": self._click_diff(mpos)
        elif st == "spiel":     self._click_spiel(mpos)
        elif st == "shop":      self._click_shop(mpos)
        elif st == "highscore":
            self.screen_state = "menu"
        elif st == "game_over":
            self._neues_spiel()
        elif st == "pause":
            if not pygame.Rect(0,0,SCREEN_W,SCREEN_H).collidepoint(mpos): return
        elif st in ("levelup","ereignis"):
            self.screen_state = "spiel"
            self.ereignis_popup = None

    def _click_menu(self, mpos):
        if self.btn_neu.clicked(mpos):
            self.screen_state = "schwierigkeit"
        elif self.btn_weiter.clicked(mpos) and self.save_exists:
            if self._laden():
                self._init_spiel(); self.screen_state = "spiel"
        elif self.btn_hs.clicked(mpos):
            self.screen_state = "highscore"
        elif self.btn_exit.clicked(mpos):
            pygame.quit(); sys.exit()

    def _click_diff(self, mpos):
        for name, btn in self.btn_diff.items():
            if btn.clicked(mpos):
                self.state.schwierigkeit = name
                self._neues_spiel()

    def _neues_spiel(self):
        self.state.reset()
        self._init_spiel()
        self.screen_state = "spiel"
        self.save_exists = os.path.exists(SAVE_FILE)
        self.note("Willkommen bei Pizzeria Imperium!", C_ACCENT)
        self.note("Klick auf Öfen = Pizza backen. Shop = oben rechts.", C_GRAY)

    def _click_spiel(self, mpos):
        mx, my = mpos

        # Top-Buttons
        if self.btn_shop.clicked(mpos):  self.screen_state = "shop"; return
        if self.btn_pause.clicked(mpos): self.screen_state = "pause"; return
        if self.btn_save.clicked(mpos):  self._speichern(); return

        # Ofen-Klick (linke Leiste)
        if mx < 205:
            slot_h = min(85, (SCREEN_H-230) // max(1,len(self.oefen)))
            for i in range(len(self.oefen)):
                oy = 82 + i*slot_h
                if 8 <= mx <= 197 and oy <= my <= oy+slot_h-4:
                    if self.oefen[i] is None:
                        self.pizza_in_ofen(i)
                    else:
                        self.pizza_aus_ofen(i)
                    return

        # Pizza-Auswahl (untere Leiste)
        if my > SCREEN_H-110:
            px = 8
            for pname in self.state.freigeschaltete_pizzen:
                pr = pygame.Rect(px, SCREEN_H-90, 88, 38)
                if pr.collidepoint(mpos):
                    self.selected_pizza = pname; return
                px += 92
                if px > SCREEN_W-200: break

        # Rechte Leiste: Kunden servieren
        if mx > SCREEN_W-210:
            x0 = SCREEN_W-210
            for i,k in enumerate(self.kunden[:5]):
                ky = 82+i*52
                kr = pygame.Rect(x0+5,ky,200,46)
                if kr.collidepoint(mpos):
                    # Passende Pizza suchen
                    for fp in list(self.fertige_pizzen):
                        if fp.name == k.pizza_name:
                            self.servieren(fp, k); return
                    if self.fertige_pizzen:
                        self.servieren(self.fertige_pizzen[0], k)
                    else:
                        self.note(f"Backe erst {k.pizza_name}!", C_YELLOW)
                    return

        # Spielfeld: Kunden direkt anklicken
        if 205 <= mx <= SCREEN_W-210:
            for k in self.kunden:
                if dist(mx, my, k.x, k.y) < 22:
                    for fp in list(self.fertige_pizzen):
                        if fp.name == k.pizza_name:
                            self.servieren(fp, k); return
                    if self.fertige_pizzen:
                        self.servieren(self.fertige_pizzen[0], k)
                    else:
                        self.note(f"Backe erst {k.pizza_name}!", C_YELLOW)
                    return

    def _click_shop(self, mpos):
        mx, my = mpos
        sw, sh = 800, 560
        sx = (SCREEN_W-sw)//2; sy = (SCREEN_H-sh)//2

        # Klick außerhalb = schließen
        if not pygame.Rect(sx,sy,sw,sh).collidepoint(mpos):
            self.screen_state = "spiel"; return

        # Tabs
        tabs = ["personal","oefen","pizzen"]
        for i,tid in enumerate(tabs):
            tr = pygame.Rect(sx+30+i*175, sy+45, 160, 36)
            if tr.collidepoint(mpos):
                self.shop_tab = tid; return

        content_y = sy+92

        if self.shop_tab == "personal":
            lv = LEVELS[self.state.level]
            for i,(typ,d) in enumerate(PERSONAL_TYPEN.items()):
                row_y = content_y + 45 + i*72
                br = pygame.Rect(sx+sw-180, row_y+12, 155, 38)
                if br.collidepoint(mpos):
                    self.mitarbeiter_einstellen(typ); return
            # Entlassen
            if self.mitarbeiter:
                my2 = content_y + 45 + len(PERSONAL_TYPEN)*72 + 10
                for j,m in enumerate(self.mitarbeiter):
                    er = pygame.Rect(sx+sw-100, my2+18+j*22, 80, 18)
                    if er.collidepoint(mpos):
                        self.mitarbeiter_entlassen(m.id); return

        elif self.shop_tab == "oefen":
            n = self.state.anzahl_oefen
            for i in range(1, min(len(OFEN_KAUFEN_KOSTEN), 10)):
                ry = content_y + 60 + (i-1)*55
                if ry > sy+sh-60: break
                if i == n:  # Nächsten kaufbaren Slot
                    br = pygame.Rect(sx+sw-170, ry+7, 145, 34)
                    if br.collidepoint(mpos):
                        self.ofen_kaufen(); return

        elif self.shop_tab == "pizzen":
            items = list(ALLE_PIZZEN.items())
            cols = 2
            for i,(pname,pd) in enumerate(items):
                col = i%cols; row = i//cols
                px2 = sx+20+col*(sw//2-15)
                py2 = content_y+55+row*68
                if py2 > sy+sh-55: break
                if pname not in self.state.freigeschaltete_pizzen:
                    br = pygame.Rect(px2+(sw//2-145),py2+12,130,34)
                    if br.collidepoint(mpos):
                        self.pizza_freischalten(pname); return

    # ═══════════════════════════════════════════════════════════════
    #  HAUPT-SCHLEIFE
    # ═══════════════════════════════════════════════════════════════
    def run(self):
        while True:
            dt = min(self.clock.tick(FPS)/1000.0, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()


# ═══════════════════════════════════════════════════════════════════
#  EINSTIEG
# ═══════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    try: pygame.mixer.init()
    except: pass
    Spiel().run()

if __name__ == "__main__":
    main()