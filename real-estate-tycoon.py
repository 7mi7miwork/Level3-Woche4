"""
╔══════════════════════════════════════════════════════════════╗
║           BUSINESS TYCOON PRO  —  by Michael (其米）          ║
║          Wirtschaftssimulation mit pygame GUI                 ║
║                                                              ║
║  Installation:  pip install pygame                           ║
║  Starten:       python business_tycoon.py                    ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
import random
import math
import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ── Farben ──────────────────────────────────────────────────────
C = {
    "bg":      (10, 14, 26),
    "panel":   (17, 24, 39),
    "panel2":  (31, 41, 55),
    "border":  (55, 65, 81),
    "accent":  (59, 130, 246),
    "accent2": (139, 92, 246),
    "green":   (16, 185, 129),
    "red":     (239, 68, 68),
    "yellow":  (245, 158, 11),
    "cyan":    (6, 182, 212),
    "gold":    (251, 191, 36),
    "white":   (243, 244, 246),
    "muted":   (107, 114, 128),
    "orange":  (249, 115, 22),
    "pink":    (236, 72, 153),
}

pygame.init()
W, H = 1280, 780
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("💼 Business Tycoon Pro — by Michael (其米）")
clock = pygame.time.Clock()

# ── Schriften ─────────────────────────────────────────────────
def make_fonts():
    return {
        "tiny":  pygame.font.SysFont("segoeui", 11),
        "sm":    pygame.font.SysFont("segoeui", 13),
        "md":    pygame.font.SysFont("segoeui", 15),
        "lg":    pygame.font.SysFont("segoeui", 18, bold=True),
        "xl":    pygame.font.SysFont("segoeui", 24, bold=True),
        "title": pygame.font.SysFont("segoeui", 30, bold=True),
    }

fonts = make_fonts()


# ══════════════════════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════════
def fmt(n: float) -> str:
    if abs(n) >= 1e9: return f"{n/1e9:.2f} Mrd €"
    if abs(n) >= 1e6: return f"{n/1e6:.2f} Mio €"
    if abs(n) >= 1e3: return f"{n/1e3:.1f}k €"
    return f"{n:,.0f} €".replace(",", ".")

def draw_text(surf, text, font_key, color, x, y, anchor="topleft", max_width=0):
    f = fonts[font_key]
    if max_width and f.size(text)[0] > max_width:
        while f.size(text + "…")[0] > max_width and len(text) > 1:
            text = text[:-1]
        text += "…"
    s = f.render(text, True, color)
    r = s.get_rect(**{anchor: (x, y)})
    surf.blit(s, r)
    return r

def draw_rect(surf, color, rect, radius=6, alpha=None):
    if alpha:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_border(surf, color, rect, width=1, radius=6):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)

def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def spark_color(val, hist):
    if len(hist) < 2: return C["muted"]
    return C["green"] if hist[-1] >= hist[-2] else C["red"]

def draw_sparkline(surf, hist, x, y, w, h, color=None):
    if len(hist) < 2: return
    mn, mx = min(hist), max(hist)
    if mx == mn: mx = mn + 1
    pts = []
    for i, v in enumerate(hist):
        px = x + int(i / (len(hist)-1) * w)
        py = y + h - int((v - mn) / (mx - mn) * h)
        pts.append((px, py))
    if color is None:
        color = C["green"] if hist[-1] >= hist[0] else C["red"]
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, 2)

def draw_bar(surf, x, y, w, h, frac, color, bg=None):
    bg = bg or C["border"]
    draw_rect(surf, bg, (x, y, w, h), radius=3)
    fw = max(0, min(w, int(w * frac)))
    if fw > 0:
        draw_rect(surf, color, (x, y, fw, h), radius=3)


# ══════════════════════════════════════════════════════════════
#  DATEN-KLASSEN
# ══════════════════════════════════════════════════════════════
@dataclass
class Property:
    type_id: str
    name: str
    icon: str
    price: float
    rent: float
    maint: float
    level: int = 1
    lvl_max: int = 5
    vacant: bool = False

    @property
    def net_monthly(self):
        return (0 if self.vacant else self.rent) - self.maint

    def upgrade_cost(self):
        return self.price * 0.12

    def upgrade(self):
        if self.level < self.lvl_max:
            self.level += 1
            self.price  *= 1.08
            self.rent   *= 1.15
            self.maint  *= 1.06

    def sell_value(self):
        return self.price * 0.94


@dataclass
class Company:
    type_id: str
    name: str
    icon: str
    base_price: float
    base_profit: float
    maint: float
    risk: float
    level: int = 1
    lvl_max: int = 8

    def __post_init__(self):
        self.profit = self.base_profit
        self.valuation = self.base_price

    def upgrade_cost(self):
        return self.valuation * 0.15

    def upgrade(self):
        if self.level < self.lvl_max:
            self.level += 1
            self.valuation  *= 1.12
            self.base_profit *= 1.22
            self.profit = self.base_profit
            self.maint  *= 1.08

    def sell_value(self):
        return self.valuation * 0.88


@dataclass
class Stock:
    sid: str
    name: str
    icon: str
    price: float
    vol: float
    div: float       # Jahres-Dividendenrendite
    sector: str
    hist: List[float] = field(default_factory=list)
    bought_avg: float = 0.0


@dataclass
class Crypto:
    cid: str
    name: str
    icon: str
    price: float
    vol: float
    hist: List[float] = field(default_factory=list)
    bought_avg: float = 0.0


# ══════════════════════════════════════════════════════════════
#  SPIELZUSTAND
# ══════════════════════════════════════════════════════════════
class GameState:
    def __init__(self):
        self.name = "Investor"
        self.cash = 50_000.0
        self.loan = 0.0
        self.loan_rate = 0.006       # monatlich (variabel)
        self.savings = 0.0
        self.savings_rate = 0.004    # monatlich Festgeld

        self.properties: List[Property] = []
        self.companies:  List[Company] = []
        self.stock_qty:  Dict[str, float] = {}   # sid -> qty
        self.crypto_qty: Dict[str, float] = {}   # cid -> qty
        self.etf_shares: float = 0.0

        self.month = 1
        self.year  = 2024
        self.inflation = 0.002       # monatlich

        self.reputation = 50         # 0–100
        self.tax_rate   = 0.25
        self.achievements_earned = set()
        self.log: List[tuple] = []   # (text, type)
        self.news: List[str] = []
        self.net_worth_hist: List[float] = []
        self.cash_flow_hist: List[float] = []

        # Wirtschaft
        self.econ_phase    = "STABLE"
        self.econ_duration = 8
        self.interest_rate = 5.0     # Leitzins p.a. %
        self.gdp_growth    = 2.0
        self.unemployment  = 5.0
        self.market_sent   = 50.0    # 0–100

        # Markt-Objekte
        self.stocks: List[Stock] = [
            Stock("tg",   "TechGiant",    "💻", 150.0,  0.13, 0.005,  "Tech"),
            Stock("ac",   "AutoCorp",     "🚗",  85.0,  0.09, 0.018,  "Auto"),
            Stock("ec",   "EnergyCo",     "⚡", 110.0,  0.07, 0.022,  "Energy"),
            Stock("bg",   "BankGroup",    "🏦",  65.0,  0.11, 0.012,  "Finance"),
            Stock("ph",   "PharmaHealth", "💊", 200.0,  0.10, 0.008,  "Health"),
            Stock("re",   "RealEstCorp",  "🏘",  90.0,  0.08, 0.025,  "RE"),
            Stock("ai",   "AI-Ventures",  "🤖", 350.0,  0.25, 0.001,  "Tech"),
            Stock("food", "FoodChain",    "🍔",  45.0,  0.06, 0.030,  "Food"),
        ]
        self.etf_price = 100.0
        self.etf_hist:  List[float] = []

        self.cryptos: List[Crypto] = [
            Crypto("btc",  "Bitcoin",  "₿",  45000.0, 0.30),
            Crypto("eth",  "Ethereum", "Ξ",   2800.0, 0.28),
            Crypto("doge", "Dogecoin", "🐕",     0.12, 0.55),
            Crypto("sol",  "Solana",   "◎",    120.0, 0.38),
        ]

    # ── Berechnungen ──────────────────────────────────────────
    def net_worth(self):
        v = self.cash + self.savings
        for p in self.properties:  v += p.price
        for c in self.companies:   v += c.valuation
        for s in self.stocks:      v += self.stock_qty.get(s.sid, 0) * s.price
        v += self.etf_shares * self.etf_price
        for c in self.cryptos:     v += self.crypto_qty.get(c.cid, 0) * c.price
        v -= self.loan
        return v

    def stock_portfolio_value(self):
        v = sum(self.stock_qty.get(s.sid, 0) * s.price for s in self.stocks)
        return v + self.etf_shares * self.etf_price

    def crypto_portfolio_value(self):
        return sum(self.crypto_qty.get(c.cid, 0) * c.price for c in self.cryptos)

    def monthly_income(self):
        i = 0.0
        for p in self.properties:
            if not p.vacant: i += p.rent
        for c in self.companies: i += c.profit
        for s in self.stocks:    i += self.stock_qty.get(s.sid, 0) * s.price * (s.div / 12)
        i += self.etf_shares * self.etf_price * (0.002 / 12)
        i += self.savings * self.savings_rate
        return i

    def monthly_expenses(self):
        e = 0.0
        for p in self.properties: e += p.maint
        for c in self.companies:  e += c.maint
        e += self.loan * (self.loan_rate + self.interest_rate / 100 / 12)
        return e

    def add_log(self, text, kind="info"):
        self.log.insert(0, (text, kind))
        if len(self.log) > 60: self.log.pop()

    def add_news(self, text):
        self.news.insert(0, text)
        if len(self.news) > 20: self.news.pop()


# ══════════════════════════════════════════════════════════════
#  WIRTSCHAFTS-ENGINE
# ══════════════════════════════════════════════════════════════
PHASES = {
    "BOOM":          {"label": "Boom 🚀",          "color": C["green"],  "stock": +0.04, "rent": +0.02, "profit": +0.05},
    "STABLE":        {"label": "Stabil ➖",         "color": C["cyan"],   "stock":  0.00, "rent":  0.00, "profit":  0.00},
    "RECESSION":     {"label": "Rezession 📉",      "color": C["yellow"], "stock": -0.03, "rent": -0.01, "profit": -0.03},
    "DEPRESSION":    {"label": "Depression 🆘",     "color": C["red"],    "stock": -0.08, "rent": -0.03, "profit": -0.08},
    "STAGFLATION":   {"label": "Stagflation 🌪",    "color": C["orange"], "stock": -0.02, "rent": +0.01, "profit": -0.04},
    "HYPERINFLATION":{"label": "Hyperinflation 💥", "color": C["pink"],   "stock": +0.01, "rent": +0.06, "profit": -0.06},
}

PROP_CATALOG = [
    ("flat",   "Kleine Wohnung",    "🏢",   75_000,   550,    90, 5),
    ("house",  "Einfamilienhaus",   "🏠",  240_000,  1300,   270, 5),
    ("condo",  "Luxus-Penthouse",   "🌆",  650_000,  4000,   600, 5),
    ("office", "Bürogebäude",       "🏣", 1_200_000, 9000,  1400, 5),
    ("mall",   "Einkaufszentrum",   "🛍", 3_000_000,25000,  3500, 5),
    ("hotel",  "Luxus-Hotel",       "🏨", 5_000_000,40000,  6000, 5),
]

COMP_CATALOG = [
    ("cafe",    "Café / Kiosk",       "☕",    15_000,    280,    40, 0.05, 8),
    ("craft",   "Handwerksbetrieb",   "🔧",    80_000,   1100,   180, 0.05, 8),
    ("retail",  "Einzelhandel",        "🛒",   200_000,   2500,   400, 0.08, 8),
    ("tech",    "Software-Startup",   "💻",   500_000,   7000,   800, 0.12, 8),
    ("factory", "Fabrik",              "🏭", 1_500_000,  18000,  2800, 0.06, 8),
    ("media",   "Medienkonzern",       "📺", 4_000_000,  50000,  8000, 0.10, 8),
    ("pharma",  "Pharmaunternehmen",   "💊", 8_000_000, 110000, 15000, 0.14, 8),
    ("bank2",   "Investmentbank",      "🏦",20_000_000, 300000, 40000, 0.18, 8),
]

RANDOM_EVENTS = [
    # (Wahrscheinlichkeit pro Monat, Beschreibung, Effekt-Funktion)
    (0.025, "Feuer in Immobilie!",           "bad",
        lambda gs: _prop_damage(gs, 0.07, "Feuer-Schaden")),
    (0.020, "Mieter zahlt nicht!",           "bad",
        lambda gs: _rent_loss(gs)),
    (0.015, "Betriebsklage gegen Firma!",    "bad",
        lambda gs: _company_lawsuit(gs)),
    (0.020, "Staatliche Förderung!",         "good",
        lambda gs: _subsidy(gs)),
    (0.008, "Marktcrash! Alle Aktien -20%.", "bad",
        lambda gs: _market_crash(gs, 0.80)),
    (0.008, "Bullenmarkt! Aktien +15%.",     "good",
        lambda gs: _market_rally(gs, 1.15)),
    (0.015, "Schlechte Presse: Ruf -12.",    "bad",
        lambda gs: setattr(gs, "reputation", max(0, gs.reputation - 12))),
    (0.015, "Award: Ruf +10.",               "good",
        lambda gs: setattr(gs, "reputation", min(100, gs.reputation + 10))),
    (0.010, "Steuerprüfung: -5% Bargeld.",   "bad",
        lambda gs: _tax_audit(gs)),
    (0.015, "Infrastrukturprojekt: Immo +10% Wert.", "good",
        lambda gs: _infra_boost(gs)),
    (0.012, "Krypto-Mania! Kurse explodieren.", "good",
        lambda gs: _crypto_mania(gs)),
    (0.010, "Regulierung: Firmengewinn -15%.",  "bad",
        lambda gs: _regulation(gs)),
    (0.008, "Zinssenkung: Kreditrate sinkt.",    "good",
        lambda gs: setattr(gs, "interest_rate", max(0, gs.interest_rate - 0.5))),
    (0.008, "Zinserhöhung: Kreditrate steigt.",  "bad",
        lambda gs: setattr(gs, "interest_rate", min(15, gs.interest_rate + 0.5))),
]

def _prop_damage(gs, frac, label):
    if not gs.properties: return
    p = random.choice(gs.properties)
    dmg = p.price * frac
    gs.cash -= dmg
    p.price -= dmg
    gs.add_log(f"🔥 {p.name}: {label} -{fmt(dmg)}", "bad")
    gs.add_news(f"🔥 Feuer in der Stadt! Immobilienschäden verzeichnet.")

def _rent_loss(gs):
    if not gs.properties: return
    p = random.choice(gs.properties)
    p.vacant = True
    gs.add_log(f"🚫 {p.name}: Mieter ausgefallen!", "bad")

def _company_lawsuit(gs):
    if not gs.companies: return
    c = random.choice(gs.companies)
    pen = c.valuation * 0.08
    gs.cash -= pen
    gs.add_log(f"⚖️ Klage vs {c.name}: -{fmt(pen)}", "bad")

def _subsidy(gs):
    amt = 10_000 + random.random() * 50_000
    gs.cash += amt
    gs.add_log(f"🏅 Förderprogramm: +{fmt(amt)}", "good")

def _market_crash(gs, factor):
    for s in gs.stocks: s.price *= factor * (0.9 + random.random() * 0.2)
    gs.add_log("💥 Marktcrash! Aktienportfolio stark gefallen.", "bad")
    gs.add_news("📉 Schwarzer Dienstag: Börsen brechen ein!")

def _market_rally(gs, factor):
    for s in gs.stocks: s.price *= factor * (0.95 + random.random() * 0.1)
    gs.add_log("🚀 Bullenmarkt! Aktien gestiegen.", "good")
    gs.add_news("📈 Rekordhoch: Märkte feiern!")

def _tax_audit(gs):
    amt = gs.cash * 0.05
    gs.cash -= amt
    gs.add_log(f"📋 Sondersteuerprüfung: -{fmt(amt)}", "bad")

def _infra_boost(gs):
    if not gs.properties: return
    p = random.choice(gs.properties)
    p.price *= 1.10
    gs.add_log(f"🏗 Stadtentwicklung: {p.name} +10%", "good")

def _crypto_mania(gs):
    for c in gs.cryptos:
        if random.random() < 0.6:
            c.price *= 1.2 + random.random() * 0.8
    gs.add_log("₿ Krypto-Mania! Kurse explodieren.", "good")

def _regulation(gs):
    for c in gs.companies:
        c.profit *= 0.85
        c.base_profit *= 0.85
    gs.add_log("📜 Neue Regulierung: Unternehmensgewinne -15%", "bad")

# Erfolge
ACHIEVEMENTS = [
    ("first_step",     "🏁 Erste Schritte",     "Kaufe deine erste Immobilie oder Firma",       lambda gs: len(gs.properties)+len(gs.companies) >= 1),
    ("millionaire",    "💎 Millionär",           "Nettovermögen > 1 Mio €",                      lambda gs: gs.net_worth() >= 1_000_000),
    ("ten_million",    "👑 Zehnfach-Millionär",  "Nettovermögen > 10 Mio €",                     lambda gs: gs.net_worth() >= 10_000_000),
    ("hundred_m",      "🚀 Centurion",           "Nettovermögen > 100 Mio €",                    lambda gs: gs.net_worth() >= 100_000_000),
    ("debt_free",      "✅ Schuldenfrei",         "Tilge alle Schulden",                          lambda gs: gs.loan == 0 and len(gs.net_worth_hist) > 6),
    ("landlord",       "🏘 Vermieter",            "Besitze 3+ Immobilien",                        lambda gs: len(gs.properties) >= 3),
    ("mogul",          "🏭 Mogul",               "Besitze 5+ Unternehmen",                       lambda gs: len(gs.companies) >= 5),
    ("stock_whale",    "📈 Aktionär",            "Aktienportfolio > 500k €",                     lambda gs: gs.stock_portfolio_value() >= 500_000),
    ("crypto_bull",    "₿ Krypto-König",         "Krypto-Portfolio > 100k €",                    lambda gs: gs.crypto_portfolio_value() >= 100_000),
    ("diversified",    "🎯 Diversifiziert",      "In alle 4 Kategorien investiert",               lambda gs: len(gs.properties)>0 and len(gs.companies)>0 and gs.stock_portfolio_value()>0 and gs.crypto_portfolio_value()>0),
    ("reputation_100", "⭐ Legende",             "Reputation auf 100 gebracht",                  lambda gs: gs.reputation >= 100),
    ("big_spender",    "💸 Big Spender",         "Mehr als 1 Mio € in einem Kauf ausgegeben",    lambda gs: getattr(gs, '_big_spend', False)),
    ("survivor",       "💪 Krisenüberlebender",  "Eine Depression überlebt",                     lambda gs: getattr(gs, '_survived_depression', False)),
]


# ══════════════════════════════════════════════════════════════
#  UI KOMPONENTEN
# ══════════════════════════════════════════════════════════════
class Button:
    def __init__(self, x, y, w, h, text, color=None, text_color=None,
                 font="sm", radius=6, icon=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.icon = icon
        self.color = color or C["accent"]
        self.text_color = text_color or C["white"]
        self.font = font
        self.radius = radius
        self.hovered = False
        self.disabled = False

    def draw(self, surf):
        col = self.color
        if self.disabled:
            col = C["border"]
        elif self.hovered:
            col = tuple(min(255, c + 30) for c in self.color)
        draw_rect(surf, col, self.rect, self.radius)
        label = (self.icon + " " if self.icon else "") + self.text
        draw_text(surf, label, self.font, self.text_color,
                  self.rect.centerx, self.rect.centery, anchor="center")

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos) and not self.disabled

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos) and not self.disabled)


class ScrollList:
    """Scrollbares Panel für Listen."""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.scroll_y = 0
        self.content_h = 0
        self.surf = pygame.Surface((w, max(h, 1)), pygame.SRCALPHA)

    def begin(self):
        self.surf.fill((0, 0, 0, 0))
        self.content_h = 0
        return self.surf

    def end(self, target_surf):
        max_scroll = max(0, self.content_h - self.rect.h)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))
        target_surf.blit(self.surf, (self.rect.x, self.rect.y),
                         (0, self.scroll_y, self.rect.w, self.rect.h))
        # Scrollbar
        if max_scroll > 0:
            ratio = self.rect.h / self.content_h
            bar_h = max(20, int(self.rect.h * ratio))
            bar_y = int(self.scroll_y / max_scroll * (self.rect.h - bar_h))
            pygame.draw.rect(target_surf, C["border"],
                             (self.rect.right - 4, self.rect.y + bar_y, 3, bar_h), border_radius=2)

    def scroll(self, dy):
        self.scroll_y -= dy * 25


class InputBox:
    def __init__(self, x, y, w, h, placeholder="", numeric=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.numeric = numeric
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                ch = event.unicode
                if self.numeric:
                    if ch.isdigit() or (ch == '.' and '.' not in self.text):
                        self.text += ch
                else:
                    self.text += ch

    def value(self):
        try: return float(self.text)
        except: return 0.0

    def draw(self, surf):
        col = C["accent"] if self.active else C["border"]
        draw_rect(surf, C["panel2"], self.rect, 5)
        draw_border(surf, col, self.rect, 1, 5)
        txt = self.text if self.text else self.placeholder
        color = C["white"] if self.text else C["muted"]
        draw_text(surf, txt, "md", color,
                  self.rect.x + 8, self.rect.centery, anchor="midleft")


# ══════════════════════════════════════════════════════════════
#  HAUPT-SPIEL
# ══════════════════════════════════════════════════════════════
class Game:
    TAB_NAMES = ["📊 Dashboard", "🌍 Wirtschaft", "📈 Märkte",
                 "₿ Krypto", "🏆 Erfolge", "📜 Log"]

    def __init__(self):
        self.gs = GameState()
        self.running_game = True
        self.paused = False
        self.speed = 2000          # ms pro Monat
        self.speed_idx = 0
        self.last_tick = pygame.time.get_ticks()
        self.tab = 0
        self.modal = None          # aktives Modal
        self._anim_flash = {}      # stat -> timer für Farbblitzen
        self._news_x = W
        self._ach_popup = None     # (text, timer)
        self._modal_scroll = ScrollList(0, 0, 100, 100)

        # Startgeld aufstocken für bessere Spielbarkeit
        self.gs.name = self._ask_name()
        self.gs.add_log(f"Willkommen, {self.gs.name}! Kapital: {fmt(self.gs.cash)}", "info")
        self.gs.add_news("🎮 Business Tycoon Pro gestartet. Viel Erfolg!")

    def _ask_name(self):
        """Einfaches Name-Eingabe-Fenster vor dem Spiel."""
        box = InputBox(W//2 - 150, H//2, 300, 36, "Dein Name", numeric=False)
        done = False
        name = ""
        ok_btn = Button(W//2 - 60, H//2 + 55, 120, 34, "Starten", icon="▶")
        while not done:
            screen.fill(C["bg"])
            draw_text(screen, "💼 Business Tycoon Pro", "title", C["gold"], W//2, H//2 - 80, "center")
            draw_text(screen, "by Michael (其米）", "md", C["muted"], W//2, H//2 - 48, "center")
            draw_text(screen, "Wie heißt du?", "lg", C["white"], W//2, H//2 - 20, "center")
            box.draw(screen)
            ok_btn.draw(screen)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                box.handle_event(e)
                if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    name = box.text or "Investor"; done = True
                if ok_btn.clicked(e):
                    name = box.text or "Investor"; done = True
            ok_btn.update(pygame.mouse.get_pos())
        return name

    # ── Tick ──────────────────────────────────────────────────
    def maybe_tick(self):
        if self.paused: return
        now = pygame.time.get_ticks()
        if now - self.last_tick >= self.speed:
            self.last_tick = now
            self._advance_month()

    def _advance_month(self):
        gs = self.gs
        gs.month += 1
        if gs.month > 12:
            gs.month = 1
            gs.year += 1
            self._year_end()

        self._update_economy()
        self._update_markets()

        phase = PHASES[gs.econ_phase]
        income = 0.0; expenses = 0.0

        # Immobilien
        for p in gs.properties:
            # Leerstand-Erholung
            if p.vacant and random.random() < 0.3: p.vacant = False
            rent = p.rent * (1 + phase["rent"]) if not p.vacant else 0
            income   += rent
            expenses += p.maint
            p.price *= (1 + gs.inflation * 0.7 + (0.004 if gs.econ_phase == "BOOM" else -0.001))
            p.rent  *= (1 + gs.inflation * 0.35)

        # Unternehmen
        for c in gs.companies:
            rep_bonus = (gs.reputation - 50) / 2000
            eff_profit = c.base_profit * (1 + phase["profit"] + rep_bonus)
            c.profit = max(0, eff_profit)
            if random.random() < c.risk * 0.4:
                dmg = c.profit * (0.2 + random.random() * 0.3)
                expenses += dmg
                gs.add_log(f"⚠️ {c.name}: Betriebsschaden -{fmt(dmg)}", "bad")
            income   += c.profit
            expenses += c.maint
            c.valuation *= (1 + gs.inflation * 0.5)
            c.base_profit *= (1 + gs.inflation * 0.25)

        # Kreditkosten
        eff_rate = gs.loan_rate + gs.interest_rate / 100 / 12
        expenses += gs.loan * eff_rate

        # Tagesgeld
        income += gs.savings * gs.savings_rate

        # Aktiendividenden
        for s in gs.stocks:
            qty = gs.stock_qty.get(s.sid, 0)
            if qty > 0:
                income += qty * s.price * (s.div / 12)

        # ETF-Dividenden
        income += gs.etf_shares * gs.etf_price * (0.002 / 12)

        # Ethereum-Staking
        eth_qty = gs.crypto_qty.get("eth", 0)
        if eth_qty > 0:
            eth = next(c for c in gs.cryptos if c.cid == "eth")
            income += eth_qty * eth.price * 0.0005

        # Zufallsereignisse
        for prob, desc, kind, fn in RANDOM_EVENTS:
            if random.random() < prob:
                fn(gs)
                gs.add_log(f"📌 Ereignis: {desc}", kind)
                gs.add_news(f"{'⚠️' if kind=='bad' else '✅'} {desc}")

        # Steuer auf Nettogewinn
        gross = income - expenses
        tax = max(0, gross * gs.tax_rate)
        expenses += tax

        cf = income - expenses
        gs.cash += cf
        gs.cash_flow_hist.append(cf)
        if len(gs.cash_flow_hist) > 24: gs.cash_flow_hist.pop(0)
        gs.net_worth_hist.append(gs.net_worth())
        if len(gs.net_worth_hist) > 24: gs.net_worth_hist.pop(0)

        gs.inflation = 0.001 + random.random() * 0.004
        if gs.econ_phase == "HYPERINFLATION": gs.inflation *= 4

        # Depression überlebt
        if gs.econ_phase == "DEPRESSION" and gs.cash > 0:
            gs._survived_depression = True

        # Bankrott-Check
        if gs.cash < -100_000 and gs.loan > gs.net_worth() * 2:
            self._game_over()
            return

        self._check_achievements()

    def _year_end(self):
        gs = self.gs
        nw = gs.net_worth()
        gs.add_news(f"📅 Jahresabschluss {gs.year-1}: NV {fmt(nw)}")
        # Vermögenssteuer ab 2 Mio €
        if nw > 2_000_000:
            wt = (nw - 2_000_000) * 0.005
            gs.cash -= wt
            gs.add_log(f"💸 Vermögenssteuer: -{fmt(wt)}", "bad")

    def _update_economy(self):
        gs = self.gs
        gs.econ_duration -= 1
        if gs.econ_duration <= 0:
            prev = gs.econ_phase
            r = random.random()
            if   r < 0.07: gs.econ_phase, gs.econ_duration = "DEPRESSION",    random.randint(2, 5)
            elif r < 0.22: gs.econ_phase, gs.econ_duration = "RECESSION",     random.randint(3, 7)
            elif r < 0.28: gs.econ_phase, gs.econ_duration = "STAGFLATION",   random.randint(2, 4)
            elif r < 0.30: gs.econ_phase, gs.econ_duration = "HYPERINFLATION",random.randint(1, 3)
            elif r < 0.65: gs.econ_phase, gs.econ_duration = "STABLE",        random.randint(5,10)
            else:          gs.econ_phase, gs.econ_duration = "BOOM",           random.randint(3, 6)

            if prev != gs.econ_phase:
                label = PHASES[gs.econ_phase]["label"]
                gs.add_news(f"🌍 Wirtschaftswechsel → {label}")
                kind = "good" if gs.econ_phase == "BOOM" else ("bad" if "DEPRESSION" in gs.econ_phase else "warn")
                gs.add_log(f"Wirtschaft → {label}", kind)

        # Leitzins
        if gs.econ_phase == "BOOM":         gs.interest_rate = min(12, gs.interest_rate + 0.06)
        elif gs.econ_phase in ("RECESSION", "DEPRESSION"):
                                            gs.interest_rate = max(0, gs.interest_rate - 0.1)
        else:                               gs.interest_rate += (random.random()-0.5)*0.04
        gs.interest_rate = max(0, min(15, gs.interest_rate))

        gs.gdp_growth    += {"BOOM":+0.15,"STABLE":0,"RECESSION":-0.2,"DEPRESSION":-0.4,
                             "STAGFLATION":-0.1,"HYPERINFLATION":-0.2}.get(gs.econ_phase,0)
        gs.gdp_growth     = max(-15, min(12, gs.gdp_growth))
        gs.unemployment  += {"BOOM":-0.15,"STABLE":0,"RECESSION":+0.25,"DEPRESSION":+0.5,
                             "STAGFLATION":+0.1,"HYPERINFLATION":+0.1}.get(gs.econ_phase,0)
        gs.unemployment   = max(1, min(30, gs.unemployment))
        gs.market_sent   += (random.random()-0.48)*8
        gs.market_sent    = max(0, min(100, gs.market_sent))
        gs.loan_rate      = 0.004 + gs.interest_rate / 100 / 12

    def _update_markets(self):
        gs = self.gs
        phase = PHASES[gs.econ_phase]
        sent_mod = (gs.market_sent - 50) / 5000

        sector_extra = {
            "Tech":    0.015 if gs.econ_phase == "BOOM" else 0,
            "Energy":  0.020 if gs.econ_phase == "STAGFLATION" else 0,
            "Finance": -0.025 if gs.econ_phase in ("DEPRESSION","RECESSION") else 0,
            "Health":  0.005,  # defensiv
            "Food":    0.003,  # defensiv
        }
        for s in gs.stocks:
            se = sector_extra.get(s.sector, 0)
            chg = (random.random()-0.5)*2*s.vol + phase["stock"] + se + sent_mod
            s.price = max(0.5, s.price * (1 + chg))
            s.hist.append(round(s.price, 2))
            if len(s.hist) > 40: s.hist.pop(0)

        etf_chg = (random.random()-0.48)*0.045 + phase["stock"]*0.5
        gs.etf_price = max(5, gs.etf_price * (1 + etf_chg))
        gs.etf_hist.append(round(gs.etf_price, 2))
        if len(gs.etf_hist) > 40: gs.etf_hist.pop(0)

        crypto_boost = 0.04 if gs.econ_phase == "BOOM" else (-0.04 if gs.econ_phase == "DEPRESSION" else 0)
        for c in gs.cryptos:
            chg = (random.random()-0.5)*2*c.vol + crypto_boost
            c.price = max(0.00001, c.price*(1+chg))
            c.hist.append(round(c.price, 4))
            if len(c.hist) > 40: c.hist.pop(0)

    def _check_achievements(self):
        for aid, title, desc, cond in ACHIEVEMENTS:
            if aid not in self.gs.achievements_earned and cond(self.gs):
                self.gs.achievements_earned.add(aid)
                self.gs.add_log(f"🏆 Erfolg: {title}", "good")
                self._ach_popup = (f"🏆 {title}", desc, pygame.time.get_ticks())

    def _game_over(self):
        self.paused = True
        self.modal = {"type": "gameover"}

    # ══ ZEICHNEN ══════════════════════════════════════════════
    def draw(self):
        global W, H
        W, H = screen.get_size()
        screen.fill(C["bg"])
        self._draw_topbar()
        self._draw_sidebar()
        self._draw_center()
        self._draw_newsbar()
        if self.modal:
            self._draw_modal()
        if self._ach_popup:
            self._draw_ach_popup()
        pygame.display.flip()

    def _draw_topbar(self):
        gs = self.gs
        h = 46
        draw_rect(screen, C["panel"], (0, 0, W, h))
        pygame.draw.line(screen, C["border"], (0, h), (W, h))

        x = 10
        draw_text(screen, "💼 Business Tycoon Pro", "lg", C["gold"], x, h//2, "midleft")
        x += 220

        stats = [
            ("💰", "Bargeld",   fmt(gs.cash),      gs.cash >= 0),
            ("📈", "Nettoverm.", fmt(gs.net_worth()), True),
            (f"{gs.month:02d}.{gs.year}", "", "", True),
            ("🏦", "Schulden",  fmt(gs.loan),       gs.loan == 0),
            ("⭐", "Ruf",       str(int(gs.reputation)), gs.reputation >= 50),
        ]
        for icon, label, val, good in stats:
            if x + 130 > W - 200: break
            draw_rect(screen, C["panel2"], (x, 6, 120, 33), 16)
            draw_text(screen, f"{icon} {label}: ", "tiny", C["muted"], x+8, h//2, "midleft")
            col = C["green"] if good else C["red"]
            draw_text(screen, val, "sm", col, x+112, h//2, "midright")
            x += 128

        # Speed-Buttons
        for i, (label, ms) in enumerate([("1×", 2000), ("3×", 800), ("10×", 300)]):
            bx = W - 190 + i * 44
            active = self.speed == ms
            col = C["accent"] if active else C["panel2"]
            draw_rect(screen, col, (bx, 8, 38, 28), 6)
            draw_border(screen, C["border"] if not active else C["accent"], (bx, 8, 38, 28), 1, 6)
            draw_text(screen, label, "sm", C["white"], bx+19, 22, "center")

        # Pause-Button
        col = C["green"] if not self.paused else C["yellow"]
        draw_rect(screen, col, (W - 100, 8, 90, 28), 14)
        label = "⏸ Pause" if not self.paused else "▶ Weiter"
        draw_text(screen, label, "sm", C["bg"], W - 55, 22, "center")

    def _draw_sidebar(self):
        sx, sy, sw, sh = 0, 46, 190, H - 46 - 22
        draw_rect(screen, C["panel"], (sx, sy, sw, sh))
        pygame.draw.line(screen, C["border"], (sw, sy), (sw, H - 22))
        y = sy + 10
        sections = [
            ("ÜBERSICHT", [("📊 Dashboard", 0), ("🌍 Wirtschaft", 1)]),
            ("INVESTIEREN", [("🏠 Immobilien", "prop"), ("🏭 Unternehmen", "comp"),
                             ("📈 Märkte", 2), ("₿ Krypto", 3)]),
            ("FINANZEN", [("💳 Kredit", "loan"), ("💸 Tilgen", "repay"),
                          ("🏦 Festgeld", "savings")]),
            ("SONSTIGES", [("🏆 Erfolge", 4), ("📜 Log", 5)]),
        ]
        for sec_title, items in sections:
            draw_text(screen, sec_title, "tiny", C["muted"], sx+10, y)
            y += 16
            for label, action in items:
                active = (self.tab == action and isinstance(action, int))
                col = C["accent"] if active else C["panel2"]
                draw_rect(screen, col, (sx+5, y, sw-10, 28), 6)
                badge_txt = ""
                if action == "prop":
                    badge_txt = str(len(self.gs.properties))
                elif action == "comp":
                    badge_txt = str(len(self.gs.companies))
                draw_text(screen, label, "sm", C["white"] if active else C["muted"],
                          sx+12, y+14, "midleft")
                if badge_txt:
                    bw = fonts["tiny"].size(badge_txt)[0] + 10
                    draw_rect(screen, C["accent2"], (sx+sw-16-bw, y+6, bw, 16), 8)
                    draw_text(screen, badge_txt, "tiny", C["white"], sx+sw-16-bw//2, y+14, "center")
                y += 32
            y += 6

    def _draw_center(self):
        cx, cy, cw, ch = 190, 46, W - 190, H - 46 - 22
        # Tab-Leiste
        tab_h = 34
        draw_rect(screen, C["panel"], (cx, cy, cw, tab_h))
        pygame.draw.line(screen, C["border"], (cx, cy+tab_h), (cx+cw, cy+tab_h))
        tx = cx + 8
        for i, name in enumerate(self.TAB_NAMES):
            tw = fonts["sm"].size(name)[0] + 20
            active = self.tab == i
            if active:
                draw_rect(screen, C["accent"], (tx, cy+tab_h-3, tw, 3), 0)
                draw_text(screen, name, "sm", C["accent"], tx+tw//2, cy+tab_h//2, "center")
            else:
                draw_text(screen, name, "sm", C["muted"], tx+tw//2, cy+tab_h//2, "center")
            tx += tw + 4

        # Content
        content_y = cy + tab_h + 1
        content_h = ch - tab_h - 1
        {0: self._tab_dashboard,
         1: self._tab_economy,
         2: self._tab_markets,
         3: self._tab_crypto,
         4: self._tab_achievements,
         5: self._tab_log,
        }.get(self.tab, self._tab_dashboard)(cx, content_y, cw, content_h)

    # ── TAB: DASHBOARD ─────────────────────────────────────────
    def _tab_dashboard(self, x, y, w, h):
        gs = self.gs
        pad = 12
        card_w = (w - pad*3) // 3
        card_h = 100

        # Übersicht-Kacheln
        tiles = [
            ("💰 Bargeld",        fmt(gs.cash),              C["cyan"],    gs.cash >= 0),
            ("📈 Nettovermögen",  fmt(gs.net_worth()),        C["gold"],    True),
            ("🏠 Immobilien",     f"{len(gs.properties)} Obj.",C["green"],  True),
            ("🏭 Unternehmen",    f"{len(gs.companies)} Firmen",C["accent"],True),
            ("📊 Monat. Einnahmen",fmt(gs.monthly_income()),  C["green"],   True),
            ("📉 Monat. Ausgaben", fmt(gs.monthly_expenses()),C["red"],     False),
        ]
        for i, (label, val, col, _) in enumerate(tiles):
            row, col_i = divmod(i, 3)
            cx2 = x + pad + col_i*(card_w+pad)
            cy2 = y + pad + row*(card_h+pad)
            draw_rect(screen, C["panel2"], (cx2, cy2, card_w, card_h), 8)
            draw_border(screen, C["border"], (cx2, cy2, card_w, card_h), 1, 8)
            draw_text(screen, label, "tiny", C["muted"], cx2+10, cy2+12)
            draw_text(screen, val, "lg", col, cx2+10, cy2+38)

        # Nettovermögen-Chart
        cy_chart = y + pad + 2*(card_h+pad) + 8
        ch_chart = h - 2*(card_h+pad) - pad*3 - 30
        if ch_chart > 60:
            draw_rect(screen, C["panel2"], (x+pad, cy_chart, w-pad*2, ch_chart), 8)
            draw_border(screen, C["border"], (x+pad, cy_chart, w-pad*2, ch_chart), 1, 8)
            draw_text(screen, "📈 Nettovermögen-Verlauf (24 Monate)", "sm", C["muted"],
                      x+pad+10, cy_chart+8)
            if len(gs.net_worth_hist) >= 2:
                draw_sparkline(screen, gs.net_worth_hist,
                               x+pad+10, cy_chart+28,
                               w-pad*2-20, ch_chart-42)
            # Cash-Flow-Balken
            if len(gs.cash_flow_hist) >= 2:
                bw = max(2, (w-pad*2-20) // max(1, len(gs.cash_flow_hist)))
                mn2 = min(gs.cash_flow_hist)
                mx2 = max(gs.cash_flow_hist)
                rng = mx2-mn2 if mx2 != mn2 else 1
                bh_total = (ch_chart-42)//3
                by0 = cy_chart + ch_chart - 16 - bh_total
                zero_y = by0 + int((mx2/rng)*bh_total) if mx2 != mn2 else by0+bh_total//2
                for i, cf in enumerate(gs.cash_flow_hist):
                    bx2 = x+pad+10 + i*bw
                    norm = (cf - mn2) / rng
                    bh = max(1, int(norm*bh_total))
                    col2 = C["green"] if cf >= 0 else C["red"]
                    pygame.draw.rect(screen, col2, (bx2, zero_y-bh, bw-1, bh))
                draw_text(screen, "📊 Monatlicher Cashflow", "tiny", C["muted"], x+pad+10, by0-14)

    # ── TAB: WIRTSCHAFT ────────────────────────────────────────
    def _tab_economy(self, x, y, w, h):
        gs = self.gs
        pad = 12
        phase = PHASES[gs.econ_phase]

        # Phaseanzeige
        ph_w, ph_h = w-pad*2, 70
        draw_rect(screen, C["panel2"], (x+pad, y+pad, ph_w, ph_h), 8)
        draw_rect(screen, phase["color"], (x+pad, y+pad, 5, ph_h), 2)
        draw_text(screen, "Aktuelle Wirtschaftsphase", "tiny", C["muted"], x+pad+14, y+pad+10)
        draw_text(screen, phase["label"], "xl", phase["color"], x+pad+14, y+pad+34)
        draw_text(screen, f"Noch ca. {gs.econ_duration} Monate", "tiny", C["muted"],
                  x+pad+14, y+pad+58)

        # Indikatoren
        iy = y+pad+ph_h+pad
        indics = [
            ("🏦 Leitzins",         f"{gs.interest_rate:.2f}%",    gs.interest_rate < 5),
            ("📊 BIP-Wachstum",      f"{gs.gdp_growth:.1f}%",       gs.gdp_growth > 0),
            ("👷 Arbeitslosigkeit",  f"{gs.unemployment:.1f}%",     gs.unemployment < 8),
            ("🌡 Markt-Stimmung",    f"{int(gs.market_sent)}/100",  gs.market_sent > 50),
            ("💹 Inflation",         f"{gs.inflation*12*100:.1f}% p.a.", gs.inflation*12 < 0.03),
            ("💳 Kreditrate",        f"{(gs.loan_rate*12*100):.2f}% p.a.", True),
        ]
        iw = (w-pad*3)//3
        ih = 60
        for i, (label, val, good) in enumerate(indics):
            row, ci = divmod(i, 3)
            ix = x+pad + ci*(iw+pad)
            iy2 = iy + row*(ih+8)
            draw_rect(screen, C["panel2"], (ix, iy2, iw, ih), 6)
            draw_border(screen, C["border"], (ix, iy2, iw, ih), 1, 6)
            draw_text(screen, label, "tiny", C["muted"], ix+8, iy2+10)
            col = C["green"] if good else C["red"]
            draw_text(screen, val, "md", col, ix+8, iy2+32)

        # Phasen-Übersicht
        py2 = iy + 2*(ih+8) + 16
        draw_text(screen, "Wirtschaftsphasen", "sm", C["muted"], x+pad, py2)
        py2 += 22
        pw = (w-pad*2-40)//6
        for i, (pname, pd) in enumerate(PHASES.items()):
            px2 = x+pad + i*(pw+8)
            active = gs.econ_phase == pname
            col2 = pd["color"] if active else C["panel2"]
            draw_rect(screen, col2 if active else C["panel2"], (px2, py2, pw, 44), 6)
            draw_border(screen, pd["color"] if active else C["border"], (px2, py2, pw, 44), 2 if active else 1, 6)
            draw_text(screen, pd["label"][:6], "tiny",
                      pd["color"] if not active else C["bg"],
                      px2+pw//2, py2+22, "center")

        # Tipps
        ty = py2+56
        tips_map = {
            "BOOM":          "💡 Jetzt Aktien kaufen! Firmengewinne steigen. Immobilienwert steigt.",
            "STABLE":        "💡 Stabile Phase – ideal um Schulden zu tilgen und Reserven aufzubauen.",
            "RECESSION":     "💡 Vorsicht bei Neukäufen. ETFs sind defensiver als Einzelaktien.",
            "DEPRESSION":    "💡 Bargeld ist König. Reduziere Risiken, halte durch!",
            "STAGFLATION":   "💡 Sachwerte (Immobilien, Rohstoffe) schützen vor Inflation.",
            "HYPERINFLATION":"💡 Immobilien & Krypto können Schutz bieten. Cash verliert Wert!",
        }
        tip = tips_map.get(gs.econ_phase, "")
        if tip and ty + 40 < y+h:
            draw_rect(screen, C["panel2"], (x+pad, ty, w-pad*2, 40), 6)
            draw_border(screen, C["yellow"], (x+pad, ty, w-pad*2, 40), 1, 6)
            draw_text(screen, tip, "sm", C["yellow"], x+pad+10, ty+20, "midleft", w-pad*2-20)

    # ── TAB: MÄRKTE ────────────────────────────────────────────
    def _tab_markets(self, x, y, w, h):
        gs = self.gs
        pad = 10
        col_w = (w-pad*3)//2

        # Aktien
        draw_text(screen, "📈 Aktienmarkt", "md", C["gold"], x+pad, y+pad)
        sy = y+pad+22
        row_h = 52
        for i, s in enumerate(gs.stocks):
            sx2 = x+pad + (i%2)*(col_w+pad)
            sy2 = sy + (i//2)*row_h
            if sy2 + row_h > y+h: break
            qty = gs.stock_qty.get(s.sid, 0)
            draw_rect(screen, C["panel2"], (sx2, sy2, col_w, row_h-4), 6)
            draw_border(screen, C["border"], (sx2, sy2, col_w, row_h-4), 1, 6)
            # Sparkline
            if len(s.hist) >= 2:
                draw_sparkline(screen, s.hist, sx2+col_w-65, sy2+6, 58, 38,
                               C["green"] if s.hist[-1] >= s.hist[0] else C["red"])
            pchg = (s.hist[-1]/s.hist[-2]-1)*100 if len(s.hist)>=2 else 0
            pchg_col = C["green"] if pchg >= 0 else C["red"]
            draw_text(screen, f"{s.icon} {s.name}", "sm", C["white"], sx2+6, sy2+8)
            draw_text(screen, fmt(s.price).replace(" €","€"), "sm", C["cyan"], sx2+6, sy2+26)
            draw_text(screen, f"{pchg:+.1f}%", "tiny", pchg_col, sx2+6, sy2+40)
            draw_text(screen, f"Div: {s.div*100:.1f}%", "tiny", C["muted"], sx2+85, sy2+8)
            if qty > 0:
                draw_text(screen, f"{qty:.0f} Stk.", "tiny", C["accent"], sx2+85, sy2+26)
                draw_text(screen, fmt(qty*s.price).replace(" €","€"), "tiny", C["accent2"],
                          sx2+85, sy2+40)

        # ETF
        ey = sy + 4*row_h + 8
        if ey + 70 < y+h:
            draw_rect(screen, C["panel2"], (x+pad, ey, w-pad*2, 68), 6)
            draw_border(screen, C["accent"], (x+pad, ey, w-pad*2, 68), 1, 6)
            draw_text(screen, "🌍 Welt-ETF", "md", C["gold"], x+pad+10, ey+10)
            draw_text(screen, fmt(gs.etf_price), "lg", C["cyan"], x+pad+10, ey+32)
            draw_text(screen, "Div: 2.4% p.a. | Diversifiziert, geringes Risiko", "tiny", C["muted"],
                      x+pad+10, ey+52)
            if gs.etf_shares > 0:
                draw_text(screen, f"{gs.etf_shares:.1f} Anteile = {fmt(gs.etf_shares*gs.etf_price)}",
                          "sm", C["accent"], x+pad+220, ey+32)
            if len(gs.etf_hist) >= 2:
                draw_sparkline(screen, gs.etf_hist, x+w-pad-120, ey+6, 110, 56)

    # ── TAB: KRYPTO ────────────────────────────────────────────
    def _tab_crypto(self, x, y, w, h):
        gs = self.gs
        pad = 12
        draw_text(screen, "₿ Krypto-Markt  (Hochrisikoanlage!)", "md", C["gold"], x+pad, y+pad)
        draw_text(screen, "Extreme Volatilität – nur spekulieren, nicht investieren, was du nicht verlieren kannst.",
                  "tiny", C["red"], x+pad, y+pad+20)
        row_h = 90
        for i, c in enumerate(gs.cryptos):
            cy2 = y+pad+40 + i*row_h
            if cy2+row_h > y+h: break
            qty = gs.crypto_qty.get(c.cid, 0)
            draw_rect(screen, C["panel2"], (x+pad, cy2, w-pad*2, row_h-8), 8)
            draw_border(screen, C["border"], (x+pad, cy2, w-pad*2, row_h-8), 1, 8)
            if len(c.hist) >= 2:
                draw_sparkline(screen, c.hist, x+w-pad-130, cy2+8, 120, 70,
                               C["green"] if c.hist[-1]>=c.hist[0] else C["red"])
            pchg = (c.hist[-1]/c.hist[-2]-1)*100 if len(c.hist)>=2 else 0
            pchg_col = C["green"] if pchg >= 0 else C["red"]
            draw_text(screen, f"{c.icon} {c.name}", "lg", C["white"], x+pad+10, cy2+12)
            price_str = f"{c.price:,.2f} €" if c.price >= 1 else f"{c.price:.5f} €"
            draw_text(screen, price_str, "md", C["cyan"], x+pad+10, cy2+38)
            draw_text(screen, f"{pchg:+.1f}%", "sm", pchg_col, x+pad+10, cy2+58)
            draw_text(screen, f"Volatilität: {c.vol*100:.0f}%", "tiny", C["muted"], x+pad+160, cy2+38)
            if qty > 0:
                val = qty * c.price
                draw_text(screen, f"Bestand: {qty:.4f} = {fmt(val)}", "sm", C["accent"],
                          x+pad+160, cy2+58)

    # ── TAB: ERFOLGE ────────────────────────────────────────────
    def _tab_achievements(self, x, y, w, h):
        pad = 12
        draw_text(screen, f"🏆 Erfolge ({len(self.gs.achievements_earned)}/{len(ACHIEVEMENTS)})",
                  "lg", C["gold"], x+pad, y+pad)
        row_h = 56
        for i, (aid, title, desc, _) in enumerate(ACHIEVEMENTS):
            ay = y+pad+32 + i*row_h
            if ay+row_h > y+h: break
            earned = aid in self.gs.achievements_earned
            col = C["panel2"] if not earned else C["panel"]
            draw_rect(screen, col, (x+pad, ay, w-pad*2, row_h-6), 7)
            border_col = C["gold"] if earned else C["border"]
            draw_border(screen, border_col, (x+pad, ay, w-pad*2, row_h-6), 1, 7)
            icon = "✅" if earned else "🔒"
            draw_text(screen, icon, "lg", C["gold"] if earned else C["muted"], x+pad+12, ay+24, "midleft")
            draw_text(screen, title, "md" if earned else "sm",
                      C["white"] if earned else C["muted"], x+pad+44, ay+14)
            draw_text(screen, desc, "tiny", C["muted"], x+pad+44, ay+34)

    # ── TAB: LOG ─────────────────────────────────────────────
    def _tab_log(self, x, y, w, h):
        gs = self.gs
        pad = 10
        draw_text(screen, "📜 Aktivitätslog", "md", C["gold"], x+pad, y+pad)
        row_h = 26
        for i, (text, kind) in enumerate(gs.log[:((h-40)//row_h)]):
            ly = y+pad+28 + i*row_h
            col_map = {"good": C["green"], "bad": C["red"],
                       "warn": C["yellow"], "info": C["cyan"]}
            col = col_map.get(kind, C["muted"])
            pygame.draw.rect(screen, col, (x+pad, ly+4, 3, 18))
            draw_text(screen, text, "sm", C["white"], x+pad+10, ly+13, "midleft",
                      w-pad*2-10)

    # ── NEWSBAR ────────────────────────────────────────────────
    def _draw_newsbar(self):
        nb_h = 22
        draw_rect(screen, C["panel"], (0, H-nb_h, W, nb_h))
        pygame.draw.line(screen, C["border"], (0, H-nb_h), (W, H-nb_h))
        self._news_x -= 1.5
        gs = self.gs
        news_str = "  ·  ".join(gs.news[-5:]) if gs.news else "Kein Neuigkeiten."
        tw = fonts["sm"].size(news_str)[0]
        if self._news_x < -tw:
            self._news_x = W
        draw_text(screen, news_str, "sm", C["muted"], int(self._news_x), H-nb_h+11, "midleft")

    # ── MODAL ZEICHNEN ─────────────────────────────────────────
    def _draw_modal(self):
        m = self.modal
        # Dimm-Overlay
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0,0,0,170))
        screen.blit(s, (0,0))

        mw, mh = min(700, W-40), min(560, H-60)
        mx, my = (W-mw)//2, (H-mh)//2
        draw_rect(screen, C["panel"], (mx, my, mw, mh), 12)
        draw_border(screen, C["accent"], (mx, my, mw, mh), 1, 12)

        mt = m.get("type","")
        if   mt == "prop":    self._modal_prop(mx, my, mw, mh)
        elif mt == "comp":    self._modal_comp(mx, my, mw, mh)
        elif mt == "loan":    self._modal_loan(mx, my, mw, mh)
        elif mt == "repay":   self._modal_repay(mx, my, mw, mh)
        elif mt == "savings": self._modal_savings(mx, my, mw, mh)
        elif mt == "sell_prop": self._modal_sell_prop(mx, my, mw, mh)
        elif mt == "sell_comp": self._modal_sell_comp(mx, my, mw, mh)
        elif mt == "upg_prop":  self._modal_upg_prop(mx, my, mw, mh)
        elif mt == "upg_comp":  self._modal_upg_comp(mx, my, mw, mh)
        elif mt == "buy_stock":  self._modal_buy_stock(mx, my, mw, mh)
        elif mt == "sell_stock": self._modal_sell_stock(mx, my, mw, mh)
        elif mt == "buy_etf":    self._modal_buy_etf(mx, my, mw, mh)
        elif mt == "buy_crypto": self._modal_buy_crypto(mx, my, mw, mh)
        elif mt == "sell_crypto":self._modal_sell_crypto(mx, my, mw, mh)
        elif mt == "gameover":   self._modal_gameover(mx, my, mw, mh)

        # Schließen-Button
        close_r = pygame.Rect(mx+mw-34, my+6, 26, 26)
        draw_rect(screen, C["red"], close_r, 13)
        draw_text(screen, "✕", "sm", C["white"], close_r.centerx, close_r.centery, "center")
        if pygame.mouse.get_pressed()[0]:
            mp = pygame.mouse.get_pos()
            if close_r.collidepoint(mp):
                self.modal = None
                self.paused = False

    def _modal_prop(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "🏠 Immobilie kaufen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Bargeld: {fmt(gs.cash)}", "sm", C["cyan"], mx+16, my+42)
        pad = 16
        row_h = 68
        for i, (tid, name, icon, price, rent, maint, lvl) in enumerate(PROP_CATALOG):
            py = my+66 + i*row_h
            if py+row_h > my+mh-20: break
            can = gs.cash >= price
            col = C["panel2"] if can else C["panel"]
            draw_rect(screen, col, (mx+pad, py, mw-pad*2, row_h-6), 7)
            draw_border(screen, C["green"] if can else C["border"],
                        (mx+pad, py, mw-pad*2, row_h-6), 1, 7)
            draw_text(screen, f"{icon} {name}", "md", C["white"] if can else C["muted"],
                      mx+pad+10, py+12)
            draw_text(screen, f"Preis: {fmt(price)}", "tiny", C["muted"], mx+pad+10, py+34)
            draw_text(screen, f"Miete: +{fmt(rent)}/Monat", "tiny", C["green"], mx+pad+200, py+34)
            draw_text(screen, f"Kosten: -{fmt(maint)}/Monat", "tiny", C["red"], mx+pad+360, py+34)
            draw_text(screen, f"Netto: {fmt(rent-maint)}/Monat", "tiny",
                      C["cyan"], mx+pad+10, py+50)
            # Kaufen-Button
            bw = 80
            bx = mx+mw-pad-bw-10
            col2 = C["accent"] if can else C["border"]
            draw_rect(screen, col2, (bx, py+18, bw, 30), 6)
            draw_text(screen, "Kaufen" if can else "Kein $", "sm",
                      C["white"], bx+bw//2, py+33, "center")

    def _modal_comp(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "🏭 Unternehmen gründen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Bargeld: {fmt(gs.cash)}", "sm", C["cyan"], mx+16, my+42)
        pad = 16
        row_h = 68
        for i, (tid, name, icon, price, profit, maint, risk, lvl) in enumerate(COMP_CATALOG):
            py = my+66 + i*row_h
            if py+row_h > my+mh-20: break
            can = gs.cash >= price
            draw_rect(screen, C["panel2"] if can else C["panel"],
                      (mx+pad, py, mw-pad*2, row_h-6), 7)
            draw_border(screen, C["green"] if can else C["border"],
                        (mx+pad, py, mw-pad*2, row_h-6), 1, 7)
            draw_text(screen, f"{icon} {name}", "md", C["white"] if can else C["muted"],
                      mx+pad+10, py+12)
            draw_text(screen, f"Preis: {fmt(price)}", "tiny", C["muted"], mx+pad+10, py+34)
            draw_text(screen, f"Gewinn: +{fmt(profit)}/Monat", "tiny", C["green"], mx+pad+200, py+34)
            draw_text(screen, f"Risiko: {risk*100:.0f}%", "tiny", C["yellow"], mx+pad+360, py+34)
            draw_text(screen, f"Kosten: -{fmt(maint)}/Monat", "tiny", C["red"], mx+pad+10, py+50)
            bw = 80
            bx = mx+mw-pad-bw-10
            draw_rect(screen, C["accent"] if can else C["border"], (bx, py+18, bw, 30), 6)
            draw_text(screen, "Gründen" if can else "Kein $", "sm", C["white"], bx+bw//2, py+33, "center")

    def _modal_loan(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "💳 Kredit aufnehmen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Aktueller Schuldenstand: {fmt(gs.loan)}", "sm", C["red"], mx+16, my+46)
        rate = (gs.loan_rate + gs.interest_rate/100/12)*12*100
        draw_text(screen, f"Effektiver Jahreszins: {rate:.2f}%", "sm", C["yellow"], mx+16, my+68)
        max_loan = max(0, gs.net_worth()*0.6 - gs.loan)
        draw_text(screen, f"Max. Kreditrahmen: {fmt(max_loan)}", "sm", C["cyan"], mx+16, my+90)
        if hasattr(self, '_loan_input'):
            self._loan_input.rect.x = mx+16
            self._loan_input.rect.y = my+120
        else:
            self._loan_input = InputBox(mx+16, my+120, 280, 38, "Betrag in €")
        self._loan_input.draw(screen)
        bw=120
        draw_rect(screen, C["accent"], (mx+310, my+120, bw, 38), 7)
        draw_text(screen, "Kredit aufnehmen", "sm", C["white"], mx+310+bw//2, my+139, "center")
        draw_text(screen, "⚠️ Warnung: Hohe Schulden können zur Insolvenz führen!",
                  "tiny", C["red"], mx+16, my+176)

    def _modal_repay(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "💸 Kredit tilgen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Schulden: {fmt(gs.loan)}", "sm", C["red"], mx+16, my+46)
        draw_text(screen, f"Bargeld: {fmt(gs.cash)}", "sm", C["cyan"], mx+16, my+68)
        if not hasattr(self,'_repay_input') or self._repay_input.rect.x != mx+16:
            self._repay_input = InputBox(mx+16, my+110, 280, 38, "Betrag in €")
        self._repay_input.rect.x = mx+16; self._repay_input.rect.y = my+110
        self._repay_input.draw(screen)
        draw_rect(screen, C["green"], (mx+310, my+110, 120, 38), 7)
        draw_text(screen, "Tilgen", "sm", C["white"], mx+370, my+129, "center")
        draw_rect(screen, C["yellow"], (mx+16, my+160, 200, 34), 7)
        draw_text(screen, "Alles tilgen", "sm", C["bg"], mx+116, my+177, "center")

    def _modal_savings(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "🏦 Festgeld-Konto", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Einlage: {fmt(gs.savings)}", "sm", C["cyan"], mx+16, my+46)
        rate_pa = gs.savings_rate*12*100
        draw_text(screen, f"Zinsen: {rate_pa:.2f}% p.a. = {fmt(gs.savings*gs.savings_rate)}/Monat", "sm", C["green"], mx+16, my+68)
        draw_text(screen, f"Bargeld: {fmt(gs.cash)}", "sm", C["muted"], mx+16, my+90)
        if not hasattr(self,'_sav_input') or self._sav_input.rect.x != mx+16:
            self._sav_input = InputBox(mx+16, my+130, 280, 38, "Betrag einzahlen")
        self._sav_input.rect.x = mx+16; self._sav_input.rect.y = my+130
        self._sav_input.draw(screen)
        draw_rect(screen, C["accent"], (mx+310, my+130, 100, 38), 7)
        draw_text(screen, "Einzahlen", "sm", C["white"], mx+360, my+149, "center")
        if gs.savings > 0:
            draw_rect(screen, C["yellow"], (mx+16, my+184, 120, 34), 7)
            draw_text(screen, "Auszahlen", "sm", C["bg"], mx+76, my+201, "center")

    def _modal_sell_prop(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "💸 Immobilie verkaufen", "lg", C["gold"], mx+16, my+16)
        if not gs.properties:
            draw_text(screen, "Keine Immobilien vorhanden.", "md", C["muted"], mx+16, my+60)
            return
        row_h = 62
        for i, p in enumerate(gs.properties):
            py = my+54 + i*row_h
            if py+row_h > my+mh-10: break
            sv = p.sell_value()
            draw_rect(screen, C["panel2"], (mx+14, py, mw-28, row_h-6), 7)
            draw_text(screen, f"{p.icon} {p.name} (Lvl {p.level})", "md", C["white"], mx+24, py+10)
            draw_text(screen, f"Verkaufswert: {fmt(sv)}  (5% Maklergebühr)", "tiny", C["muted"], mx+24, py+34)
            draw_text(screen, f"Netto/Monat: {fmt(p.net_monthly)}", "tiny", C["cyan"], mx+24, py+48)
            draw_rect(screen, C["red"], (mx+mw-100, py+14, 72, 28), 6)
            draw_text(screen, "Verkaufen", "sm", C["white"], mx+mw-64, py+28, "center")

    def _modal_sell_comp(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "💸 Unternehmen verkaufen", "lg", C["gold"], mx+16, my+16)
        if not gs.companies:
            draw_text(screen, "Keine Unternehmen vorhanden.", "md", C["muted"], mx+16, my+60)
            return
        row_h = 62
        for i, c in enumerate(gs.companies):
            py = my+54 + i*row_h
            if py+row_h > my+mh-10: break
            sv = c.sell_value()
            draw_rect(screen, C["panel2"], (mx+14, py, mw-28, row_h-6), 7)
            draw_text(screen, f"{c.icon} {c.name} (Lvl {c.level})", "md", C["white"], mx+24, py+10)
            draw_text(screen, f"Verkaufswert: {fmt(sv)}", "tiny", C["muted"], mx+24, py+34)
            draw_text(screen, f"Gewinn/Monat: {fmt(c.profit)}", "tiny", C["green"], mx+24, py+48)
            draw_rect(screen, C["red"], (mx+mw-100, py+14, 72, 28), 6)
            draw_text(screen, "Verkaufen", "sm", C["white"], mx+mw-64, py+28, "center")

    def _modal_upg_prop(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "🔨 Immobilie renovieren", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, "Upgrade: +15% Miete, +8% Wert, +6% Kosten", "tiny", C["muted"], mx+16, my+44)
        if not gs.properties:
            draw_text(screen, "Keine Immobilien vorhanden.", "md", C["muted"], mx+16, my+70)
            return
        row_h = 68
        for i, p in enumerate(gs.properties):
            py = my+64 + i*row_h
            if py+row_h > my+mh-10: break
            cost = p.upgrade_cost()
            maxed = p.level >= p.lvl_max
            can = gs.cash >= cost and not maxed
            draw_rect(screen, C["panel2"], (mx+14, py, mw-28, row_h-6), 7)
            lvl_str = f"Lvl {p.level}/{p.lvl_max}"
            draw_text(screen, f"{p.icon} {p.name}  {lvl_str}", "md", C["white"], mx+24, py+10)
            draw_text(screen, f"Miete: {fmt(p.rent)}/Monat | Kosten: {fmt(cost)}", "tiny", C["muted"], mx+24, py+34)
            # Level-Bar
            draw_bar(screen, mx+24, py+50, 200, 8, p.level/p.lvl_max, C["accent"])
            if maxed:
                draw_rect(screen, C["border"], (mx+mw-110, py+16, 82, 28), 6)
                draw_text(screen, "Max Level", "tiny", C["muted"], mx+mw-69, py+30, "center")
            else:
                draw_rect(screen, C["accent"] if can else C["border"], (mx+mw-110, py+16, 82, 28), 6)
                draw_text(screen, f"Upg. {fmt(cost)}" if can else "Kein $", "tiny", C["white"], mx+mw-69, py+30, "center")

    def _modal_upg_comp(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "🚀 Unternehmen erweitern", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, "Upgrade: +22% Gewinn, +12% Bewertung, +8% Kosten", "tiny", C["muted"], mx+16, my+44)
        if not gs.companies:
            draw_text(screen, "Keine Unternehmen vorhanden.", "md", C["muted"], mx+16, my+70)
            return
        row_h = 68
        for i, c in enumerate(gs.companies):
            py = my+64 + i*row_h
            if py+row_h > my+mh-10: break
            cost = c.upgrade_cost()
            maxed = c.level >= c.lvl_max
            can = gs.cash >= cost and not maxed
            draw_rect(screen, C["panel2"], (mx+14, py, mw-28, row_h-6), 7)
            draw_text(screen, f"{c.icon} {c.name}  Lvl {c.level}/{c.lvl_max}", "md", C["white"], mx+24, py+10)
            draw_text(screen, f"Gewinn: {fmt(c.profit)}/Monat | Upg.-Kosten: {fmt(cost)}", "tiny", C["muted"], mx+24, py+34)
            draw_bar(screen, mx+24, py+50, 200, 8, c.level/c.lvl_max, C["accent2"])
            if maxed:
                draw_rect(screen, C["border"], (mx+mw-110, py+16, 82, 28), 6)
                draw_text(screen, "Max Level", "tiny", C["muted"], mx+mw-69, py+30, "center")
            else:
                draw_rect(screen, C["accent"] if can else C["border"], (mx+mw-110, py+16, 82, 28), 6)
                draw_text(screen, "Erweitern" if can else "Kein $", "tiny", C["white"], mx+mw-69, py+30, "center")

    def _modal_buy_stock(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "📈 Aktie kaufen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Bargeld: {fmt(gs.cash)}", "sm", C["cyan"], mx+16, my+44)
        idx = self.modal.get("idx", 0)
        s = gs.stocks[idx]
        draw_text(screen, f"{s.icon} {s.name}  |  {fmt(s.price)}/Aktie  |  Div: {s.div*100:.1f}%", "md", C["white"], mx+16, my+72)
        if not hasattr(self,'_stock_input') or self._stock_input.rect.x != mx+16:
            self._stock_input = InputBox(mx+16, my+116, 200, 38, "Anzahl Aktien")
        self._stock_input.rect.x = mx+16; self._stock_input.rect.y = my+116
        self._stock_input.draw(screen)
        qty_val = self._stock_input.value()
        total = qty_val * s.price
        draw_text(screen, f"Gesamt: {fmt(total)}", "sm", C["cyan"], mx+16, my+166)
        can = gs.cash >= total and qty_val > 0
        draw_rect(screen, C["accent"] if can else C["border"], (mx+230, my+116, 110, 38), 7)
        draw_text(screen, "Kaufen", "sm", C["white"], mx+285, my+135, "center")
        qty_owned = gs.stock_qty.get(s.sid, 0)
        if qty_owned > 0:
            draw_text(screen, f"Im Besitz: {qty_owned:.0f} Aktien = {fmt(qty_owned*s.price)}",
                      "sm", C["muted"], mx+16, my+200)
        if len(s.hist) >= 2:
            draw_sparkline(screen, s.hist, mx+16, my+230, mw-32, 80)

    def _modal_sell_stock(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "📉 Aktie verkaufen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Bargeld: {fmt(gs.cash)}", "sm", C["cyan"], mx+16, my+44)
        idx = self.modal.get("idx", 0)
        s = gs.stocks[idx]
        qty_owned = gs.stock_qty.get(s.sid, 0)
        draw_text(screen, f"{s.icon} {s.name}  |  Bestand: {qty_owned:.0f}", "md", C["white"], mx+16, my+72)
        if not hasattr(self,'_ssell_input') or self._ssell_input.rect.x != mx+16:
            self._ssell_input = InputBox(mx+16, my+116, 200, 38, "Anzahl verkaufen")
        self._ssell_input.rect.x = mx+16; self._ssell_input.rect.y = my+116
        self._ssell_input.draw(screen)
        qty_val = min(self._ssell_input.value(), qty_owned)
        total = qty_val * s.price
        draw_text(screen, f"Erlös: {fmt(total)}", "sm", C["green"], mx+16, my+166)
        draw_rect(screen, C["red"] if qty_val > 0 else C["border"], (mx+230, my+116, 110, 38), 7)
        draw_text(screen, "Verkaufen", "sm", C["white"], mx+285, my+135, "center")

    def _modal_buy_etf(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "🌍 Welt-ETF kaufen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, f"Kurs: {fmt(gs.etf_price)}  |  Anteile: {gs.etf_shares:.1f}  |  Wert: {fmt(gs.etf_shares*gs.etf_price)}",
                  "sm", C["cyan"], mx+16, my+46)
        draw_text(screen, "Diversifiziert, geringes Risiko, 2.4% Dividende p.a.", "tiny", C["green"], mx+16, my+68)
        if not hasattr(self,'_etf_input'):
            self._etf_input = InputBox(mx+16, my+100, 200, 38, "Anzahl Anteile")
        self._etf_input.rect.x = mx+16; self._etf_input.rect.y = my+100
        self._etf_input.draw(screen)
        qty = self._etf_input.value()
        draw_text(screen, f"Kosten: {fmt(qty*gs.etf_price)}", "sm", C["cyan"], mx+16, my+150)
        can = gs.cash >= qty*gs.etf_price and qty > 0
        draw_rect(screen, C["accent"] if can else C["border"], (mx+230, my+100, 100, 38), 7)
        draw_text(screen, "Kaufen", "sm", C["white"], mx+280, my+119, "center")
        if gs.etf_shares > 0:
            draw_rect(screen, C["red"], (mx+16, my+190, 130, 36), 7)
            draw_text(screen, "Alle verkaufen", "sm", C["white"], mx+81, my+208, "center")

    def _modal_buy_crypto(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "₿ Krypto kaufen", "lg", C["gold"], mx+16, my+16)
        draw_text(screen, "⚠️ Hochriskant! Kurs kann auf 0 fallen.", "tiny", C["red"], mx+16, my+44)
        idx = self.modal.get("idx", 0)
        c = gs.cryptos[idx]
        price_str = f"{c.price:,.4f} €"
        draw_text(screen, f"{c.icon} {c.name}  |  {price_str}", "md", C["white"], mx+16, my+70)
        if not hasattr(self,'_cry_input'):
            self._cry_input = InputBox(mx+16, my+110, 200, 38, "Menge (Dezimal ok)")
        self._cry_input.rect.x = mx+16; self._cry_input.rect.y = my+110
        self._cry_input.draw(screen)
        qty = self._cry_input.value()
        total = qty * c.price
        draw_text(screen, f"Kosten: {fmt(total)}", "sm", C["cyan"], mx+16, my+160)
        can = gs.cash >= total and qty > 0
        draw_rect(screen, C["accent"] if can else C["border"], (mx+230, my+110, 100, 38), 7)
        draw_text(screen, "Kaufen", "sm", C["white"], mx+280, my+129, "center")
        qty_owned = gs.crypto_qty.get(c.cid, 0)
        if qty_owned > 0:
            draw_text(screen, f"Bestand: {qty_owned:.4f} = {fmt(qty_owned*c.price)}", "sm", C["muted"], mx+16, my+200)

    def _modal_sell_crypto(self, mx, my, mw, mh):
        gs = self.gs
        draw_text(screen, "₿ Krypto verkaufen", "lg", C["gold"], mx+16, my+16)
        idx = self.modal.get("idx", 0)
        c = gs.cryptos[idx]
        qty_owned = gs.crypto_qty.get(c.cid, 0)
        draw_text(screen, f"{c.icon} {c.name}  |  Bestand: {qty_owned:.6f}", "md", C["white"], mx+16, my+50)
        if not hasattr(self,'_csell_input'):
            self._csell_input = InputBox(mx+16, my+100, 200, 38, "Menge verkaufen")
        self._csell_input.rect.x = mx+16; self._csell_input.rect.y = my+100
        self._csell_input.draw(screen)
        qty = min(self._csell_input.value(), qty_owned)
        draw_text(screen, f"Erlös: {fmt(qty*c.price)}", "sm", C["green"], mx+16, my+150)
        draw_rect(screen, C["red"] if qty > 0 else C["border"], (mx+230, my+100, 100, 38), 7)
        draw_text(screen, "Verkaufen", "sm", C["white"], mx+280, my+119, "center")
        if qty_owned > 0:
            draw_rect(screen, C["yellow"], (mx+16, my+180, 140, 36), 7)
            draw_text(screen, "Alles verkaufen", "sm", C["bg"], mx+86, my+198, "center")

    def _modal_gameover(self, mx, my, mw, mh):
        draw_text(screen, "💀 BANKROTT", "title", C["red"], mx+mw//2, my+80, "center")
        draw_text(screen, "Du bist zahlungsunfähig!", "lg", C["white"], mx+mw//2, my+130, "center")
        draw_text(screen, f"Endstand: {fmt(self.gs.net_worth())}", "md", C["muted"], mx+mw//2, my+165, "center")
        draw_text(screen, f"Monate gespielt: {(self.gs.year-2024)*12+self.gs.month}", "md", C["muted"], mx+mw//2, my+195, "center")
        draw_rect(screen, C["accent"], (mx+mw//2-80, my+240, 160, 44), 8)
        draw_text(screen, "Neu starten", "lg", C["white"], mx+mw//2, my+262, "center")

    def _draw_ach_popup(self):
        title, desc, t = self._ach_popup
        elapsed = pygame.time.get_ticks() - t
        if elapsed > 4000:
            self._ach_popup = None
            return
        alpha = 255
        if elapsed > 3000:
            alpha = int(255 * (1 - (elapsed-3000)/1000))
        pw, ph = 320, 60
        px, py = W - pw - 20, H - ph - 30
        s = pygame.Surface((pw, ph), pygame.SRCALPHA)
        s.fill((80, 40, 140, alpha))
        screen.blit(s, (px, py))
        pygame.draw.rect(screen, (139,92,246), (px, py, pw, ph), 1, border_radius=8)
        draw_text(screen, title, "md", C["gold"], px+12, py+14)
        draw_text(screen, desc, "tiny", C["muted"], px+12, py+38)

    # ══ EVENT HANDLER ═════════════════════════════════════════
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.VIDEORESIZE:
            pass  # handled by RESIZABLE flag
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_ESCAPE:
                self.modal = None
            elif event.key == pygame.K_F1: self.setSpeed(2000,0)
            elif event.key == pygame.K_F2: self.setSpeed(800,1)
            elif event.key == pygame.K_F3: self.setSpeed(300,2)
        
        if self.modal:
            self._handle_modal_input(event)
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my2 = event.pos
            self._handle_click(mx, my2)
        if event.type == pygame.MOUSEWHEEL:
            pass  # could add scrolling later

        # Input-Felder bei Modale
        for attr in ['_loan_input','_repay_input','_sav_input','_stock_input',
                     '_ssell_input','_etf_input','_cry_input','_csell_input']:
            if hasattr(self, attr):
                getattr(self, attr).handle_event(event)

        return True

    def _handle_click(self, mx, my2):
        # Topbar Speed-Buttons
        for i, ms in enumerate([2000, 800, 300]):
            bx = W - 190 + i*44
            if pygame.Rect(bx, 8, 38, 28).collidepoint(mx, my2):
                self.speed = ms
                self.speed_idx = i
                return
        # Pause
        if pygame.Rect(W-100, 8, 90, 28).collidepoint(mx, my2):
            self.paused = not self.paused
            return
        # Sidebar
        self._handle_sidebar_click(mx, my2)
        # Tabs
        tx = 190 + 8
        for i, name in enumerate(self.TAB_NAMES):
            tw = fonts["sm"].size(name)[0] + 20
            if pygame.Rect(tx, 46, tw, 34).collidepoint(mx, my2):
                self.tab = i
                return
            tx += tw + 4
        # Markets tab: buy/sell aktien
        if self.tab == 2:
            self._handle_markets_click(mx, my2)
        if self.tab == 3:
            self._handle_crypto_click(mx, my2)

    def _handle_sidebar_click(self, mx, my2):
        if mx > 190: return
        sections = [
            ("ÜBERSICHT", [("📊 Dashboard", 0), ("🌍 Wirtschaft", 1)]),
            ("INVESTIEREN", [("🏠 Immobilien", "prop"), ("🏭 Unternehmen", "comp"),
                             ("📈 Märkte", 2), ("₿ Krypto", 3)]),
            ("FINANZEN", [("💳 Kredit", "loan"), ("💸 Tilgen", "repay"),
                          ("🏦 Festgeld", "savings")]),
            ("SONSTIGES", [("🏆 Erfolge", 4), ("📜 Log", 5)]),
        ]
        y = 46+10
        for _, items in sections:
            y += 16
            for label, action in items:
                r = pygame.Rect(5, y, 180, 28)
                if r.collidepoint(mx, my2):
                    if isinstance(action, int):
                        self.tab = action
                    else:
                        self._open_action_modal(action)
                    return
                y += 32
            y += 6

    def _open_action_modal(self, action):
        self.paused = True
        if action == "prop":    self.modal = {"type":"prop"}
        elif action == "comp":  self.modal = {"type":"comp"}
        elif action == "loan":  self.modal = {"type":"loan"}
        elif action == "repay": self.modal = {"type":"repay"}
        elif action == "savings":self.modal = {"type":"savings"}

    def _handle_markets_click(self, mx, my2):
        """Klick auf Aktien in Märkte-Tab → Kauf/Verkauf Modal."""
        x, y = 190, 46+34+1
        pad, col_w = 10, (W-190-pad*3)//2
        row_h = 52
        sy = y + 22
        for i, s in enumerate(self.gs.stocks):
            sx2 = x+pad + (i%2)*(col_w+pad)
            sy2 = sy + (i//2)*row_h
            r = pygame.Rect(sx2, sy2, col_w, row_h-4)
            if r.collidepoint(mx, my2):
                # Rechts-Klick = Verkaufen, Links = Kaufen
                if mx > sx2 + col_w*0.7:
                    self.modal = {"type":"sell_stock","idx":i}
                else:
                    self.modal = {"type":"buy_stock","idx":i}
                self.paused = True
                return
        # ETF
        ey = sy + 4*row_h + 8
        if pygame.Rect(x+pad, ey, W-190-pad*2, 68).collidepoint(mx, my2):
            self.modal = {"type":"buy_etf"}
            self.paused = True

    def _handle_crypto_click(self, mx, my2):
        x, y = 190, 46+34+40+1
        pad = 12; row_h = 90
        for i, c in enumerate(self.gs.cryptos):
            cy2 = y + i*row_h
            r = pygame.Rect(x+pad, cy2, W-190-pad*2, row_h-8)
            if r.collidepoint(mx, my2):
                if mx > x + (W-190)*0.6:
                    self.modal = {"type":"sell_crypto","idx":i}
                else:
                    self.modal = {"type":"buy_crypto","idx":i}
                self.paused = True
                return

    def _handle_modal_input(self, event):
        m = self.modal
        if m is None: return
        mt = m.get("type","")

        # Input-Box Events weiterleiten
        for attr in ['_loan_input','_repay_input','_sav_input','_stock_input',
                     '_ssell_input','_etf_input','_cry_input','_csell_input']:
            if hasattr(self, attr):
                getattr(self, attr).handle_event(event)

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        mx, my2 = event.pos
        mw, mh = min(700, W-40), min(560, H-60)
        bx2, by2 = (W-mw)//2, (H-mh)//2

        if mt == "prop":   self._click_modal_prop(mx, my2, bx2, by2, mw, mh)
        elif mt == "comp": self._click_modal_comp(mx, my2, bx2, by2, mw, mh)
        elif mt == "loan": self._click_modal_loan(mx, my2, bx2, by2, mw)
        elif mt == "repay":self._click_modal_repay(mx, my2, bx2, by2, mw)
        elif mt == "savings":self._click_modal_savings(mx, my2, bx2, by2, mw)
        elif mt == "sell_prop": self._click_modal_sell_prop(mx, my2, bx2, by2, mw)
        elif mt == "sell_comp": self._click_modal_sell_comp(mx, my2, bx2, by2, mw)
        elif mt == "upg_prop":  self._click_modal_upg_prop(mx, my2, bx2, by2, mw)
        elif mt == "upg_comp":  self._click_modal_upg_comp(mx, my2, bx2, by2, mw)
        elif mt == "buy_stock": self._click_modal_buy_stock(mx, my2, bx2, by2, mw)
        elif mt == "sell_stock":self._click_modal_sell_stock(mx, my2, bx2, by2, mw)
        elif mt == "buy_etf":   self._click_modal_buy_etf(mx, my2, bx2, by2, mw)
        elif mt == "buy_crypto":self._click_modal_buy_crypto(mx, my2, bx2, by2, mw)
        elif mt == "sell_crypto":self._click_modal_sell_crypto(mx, my2, bx2, by2, mw)
        elif mt == "gameover":
            if pygame.Rect(bx2+mw//2-80, by2+240, 160, 44).collidepoint(mx, my2):
                self.__init__()  # Neustart

        # Schließen
        if pygame.Rect(bx2+mw-34, by2+6, 26, 26).collidepoint(mx, my2):
            self.modal = None
            self.paused = False

    def _buy_prop(self, idx):
        gs = self.gs
        tid, name, icon, price, rent, maint, lvl = PROP_CATALOG[idx]
        if gs.cash < price: return
        gs.cash -= price
        if price >= 1_000_000: gs._big_spend = True
        gs.properties.append(Property(tid, name, icon, float(price), float(rent), float(maint), lvl_max=lvl))
        gs.add_log(f"✅ {icon} {name} gekauft für {fmt(price)}", "good")
        gs.add_news(f"🏠 Neuer Immobilienkauf: {name}")
        self._check_achievements()
        self.modal = None; self.paused = False

    def _buy_comp(self, idx):
        gs = self.gs
        tid, name, icon, price, profit, maint, risk, lvl = COMP_CATALOG[idx]
        if gs.cash < price: return
        gs.cash -= price
        if price >= 1_000_000: gs._big_spend = True
        c = Company(tid, name, icon, float(price), float(profit), float(maint), risk, lvl_max=lvl)
        gs.companies.append(c)
        gs.add_log(f"✅ {icon} {name} gegründet für {fmt(price)}", "good")
        gs.add_news(f"🏭 Neue Firmengründung: {name}")
        self._check_achievements()
        self.modal = None; self.paused = False

    def _click_modal_prop(self, mx, my2, bx2, by2, mw, mh):
        row_h, pad = 68, 16
        for i in range(len(PROP_CATALOG)):
            py = by2+66 + i*row_h
            bw = 80; bxb = bx2+mw-pad-bw-10
            if pygame.Rect(bxb, py+18, bw, 30).collidepoint(mx, my2):
                self._buy_prop(i); return
        # Kontextbuttons
        for label, modal_type in [("Verkaufen", "sell_prop"), ("Renovieren", "upg_prop")]:
            pass  # handled via sidebar later

    def _click_modal_comp(self, mx, my2, bx2, by2, mw, mh):
        row_h, pad = 68, 16
        for i in range(len(COMP_CATALOG)):
            py = by2+66 + i*row_h
            bw = 80; bxb = bx2+mw-pad-bw-10
            if pygame.Rect(bxb, py+18, bw, 30).collidepoint(mx, my2):
                self._buy_comp(i); return

    def _click_modal_loan(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        if pygame.Rect(bx2+310, by2+120, 120, 38).collidepoint(mx, my2):
            amt = self._loan_input.value()
            max_l = max(0, gs.net_worth()*0.6 - gs.loan)
            if 0 < amt <= max_l:
                gs.cash += amt; gs.loan += amt
                gs.add_log(f"💳 Kredit aufgenommen: +{fmt(amt)}", "warn")
                self.modal = None; self.paused = False

    def _click_modal_repay(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        if pygame.Rect(bx2+310, by2+110, 120, 38).collidepoint(mx, my2):
            amt = min(self._repay_input.value(), gs.cash, gs.loan)
            if amt > 0:
                gs.cash -= amt; gs.loan = max(0, gs.loan - amt)
                gs.add_log(f"✅ Kredit getilgt: -{fmt(amt)}", "good")
                self.modal = None; self.paused = False
        if pygame.Rect(bx2+16, by2+160, 200, 34).collidepoint(mx, my2):
            amt = min(gs.cash, gs.loan)
            if amt > 0:
                gs.cash -= amt; gs.loan = max(0, gs.loan - amt)
                gs.add_log(f"✅ Alles getilgt: -{fmt(amt)}", "good")
                self.modal = None; self.paused = False

    def _click_modal_savings(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        if pygame.Rect(bx2+310, by2+130, 100, 38).collidepoint(mx, my2):
            amt = self._sav_input.value()
            if 0 < amt <= gs.cash:
                gs.cash -= amt; gs.savings += amt
                gs.add_log(f"🏦 Festgeld eingelegt: {fmt(amt)}", "info")
                self.modal = None; self.paused = False
        if gs.savings > 0 and pygame.Rect(bx2+16, by2+184, 120, 34).collidepoint(mx, my2):
            gs.cash += gs.savings
            gs.add_log(f"🏦 Festgeld ausgezahlt: {fmt(gs.savings)}", "info")
            gs.savings = 0
            self.modal = None; self.paused = False

    def _click_modal_sell_prop(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        row_h = 62
        for i, p in enumerate(gs.properties):
            py = by2+54 + i*row_h
            if pygame.Rect(bx2+mw-100, py+14, 72, 28).collidepoint(mx, my2):
                sv = p.sell_value()
                gs.cash += sv
                gs.properties.pop(i)
                gs.add_log(f"💸 {p.name} verkauft für {fmt(sv)}", "info")
                self.modal = None; self.paused = False; return

    def _click_modal_sell_comp(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        row_h = 62
        for i, c in enumerate(gs.companies):
            py = by2+54 + i*row_h
            if pygame.Rect(bx2+mw-100, py+14, 72, 28).collidepoint(mx, my2):
                sv = c.sell_value()
                gs.cash += sv
                gs.companies.pop(i)
                gs.add_log(f"💸 {c.name} verkauft für {fmt(sv)}", "info")
                self.modal = None; self.paused = False; return

    def _click_modal_upg_prop(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        row_h = 68
        for i, p in enumerate(gs.properties):
            py = by2+64 + i*row_h
            cost = p.upgrade_cost()
            if (not p.level >= p.lvl_max and
                    pygame.Rect(bx2+mw-110, py+16, 82, 28).collidepoint(mx, my2)):
                if gs.cash >= cost:
                    gs.cash -= cost
                    p.upgrade()
                    gs.add_log(f"🔨 {p.name} renoviert (Lvl {p.level})", "good")
                    self.modal = None; self.paused = False; return

    def _click_modal_upg_comp(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        row_h = 68
        for i, c in enumerate(gs.companies):
            py = by2+64 + i*row_h
            cost = c.upgrade_cost()
            if (not c.level >= c.lvl_max and
                    pygame.Rect(bx2+mw-110, py+16, 82, 28).collidepoint(mx, my2)):
                if gs.cash >= cost:
                    gs.cash -= cost
                    c.upgrade()
                    gs.add_log(f"🚀 {c.name} erweitert (Lvl {c.level})", "good")
                    self.modal = None; self.paused = False; return

    def _click_modal_buy_stock(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        if pygame.Rect(bx2+230, by2+116, 110, 38).collidepoint(mx, my2):
            idx = self.modal.get("idx",0)
            s = gs.stocks[idx]
            qty = int(self._stock_input.value())
            cost = qty * s.price
            if qty > 0 and gs.cash >= cost:
                gs.cash -= cost
                gs.stock_qty[s.sid] = gs.stock_qty.get(s.sid,0) + qty
                gs.add_log(f"📈 {qty}× {s.name} gekauft für {fmt(cost)}", "good")
                self._check_achievements()
                self.modal = None; self.paused = False

    def _click_modal_sell_stock(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        if pygame.Rect(bx2+230, by2+116, 110, 38).collidepoint(mx, my2):
            idx = self.modal.get("idx",0)
            s = gs.stocks[idx]
            qty_owned = gs.stock_qty.get(s.sid,0)
            qty = min(int(self._ssell_input.value()), int(qty_owned))
            if qty > 0:
                proceeds = qty * s.price
                gs.cash += proceeds
                gs.stock_qty[s.sid] = qty_owned - qty
                gs.add_log(f"📉 {qty}× {s.name} verkauft für {fmt(proceeds)}", "info")
                self.modal = None; self.paused = False

    def _click_modal_buy_etf(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        if pygame.Rect(bx2+230, by2+100, 100, 38).collidepoint(mx, my2):
            qty = self._etf_input.value()
            cost = qty * gs.etf_price
            if qty > 0 and gs.cash >= cost:
                gs.cash -= cost; gs.etf_shares += qty
                gs.add_log(f"🌍 {qty:.1f} ETF-Anteile gekauft für {fmt(cost)}", "good")
                self._check_achievements()
                self.modal = None; self.paused = False
        if gs.etf_shares > 0 and pygame.Rect(bx2+16, by2+190, 130, 36).collidepoint(mx, my2):
            proceeds = gs.etf_shares * gs.etf_price
            gs.cash += proceeds
            gs.add_log(f"🌍 Alle ETF-Anteile verkauft für {fmt(proceeds)}", "info")
            gs.etf_shares = 0
            self.modal = None; self.paused = False

    def _click_modal_buy_crypto(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        if pygame.Rect(bx2+230, by2+110, 100, 38).collidepoint(mx, my2):
            idx = self.modal.get("idx",0)
            c = gs.cryptos[idx]
            qty = self._cry_input.value()
            cost = qty * c.price
            if qty > 0 and gs.cash >= cost:
                gs.cash -= cost
                gs.crypto_qty[c.cid] = gs.crypto_qty.get(c.cid,0) + qty
                gs.add_log(f"₿ {qty:.4f}× {c.name} gekauft für {fmt(cost)}", "good")
                self._check_achievements()
                self.modal = None; self.paused = False

    def _click_modal_sell_crypto(self, mx, my2, bx2, by2, mw):
        gs = self.gs
        idx = self.modal.get("idx",0)
        c = gs.cryptos[idx]
        qty_owned = gs.crypto_qty.get(c.cid,0)
        if pygame.Rect(bx2+230, by2+100, 100, 38).collidepoint(mx, my2):
            qty = min(self._csell_input.value(), qty_owned)
            if qty > 0:
                proceeds = qty * c.price
                gs.cash += proceeds
                gs.crypto_qty[c.cid] = max(0, qty_owned - qty)
                gs.add_log(f"₿ {qty:.4f}× {c.name} verkauft für {fmt(proceeds)}", "info")
                self.modal = None; self.paused = False
        if qty_owned > 0 and pygame.Rect(bx2+16, by2+180, 140, 36).collidepoint(mx, my2):
            proceeds = qty_owned * c.price
            gs.cash += proceeds
            gs.crypto_qty[c.cid] = 0
            gs.add_log(f"₿ Alle {c.name} verkauft für {fmt(proceeds)}", "info")
            self.modal = None; self.paused = False

    # Kontextmenüs in Sidebar für sell/upgrade
    def open_modal(self, mtype):
        self.modal = {"type": mtype}
        self.paused = True

    def setSpeed(self, ms, idx):
        self.speed = ms
        self.speed_idx = idx

    # ══ HAUPT-LOOP ════════════════════════════════════════════
    def run(self):
        while True:
            for event in pygame.event.get():
                if not self.handle_event(event):
                    pygame.quit()
                    sys.exit()
            self.maybe_tick()
            self.draw()
            clock.tick(60)


if __name__ == "__main__":
    game = Game()
    # Extra Sidebar-Buttons für sell/upgrade über Klick im Dashboard
    # (implementiert über Sidebar-Erweiterung)
    
    # Füge weitere Sidebar-Buttons dynamisch hinzu via Tab-Ansicht
    game.TAB_NAMES = ["📊 Dashboard", "🌍 Wirtschaft", "📈 Märkte",
                      "₿ Krypto", "🏆 Erfolge", "📜 Log"]
    
    # Starte
    game.run()
