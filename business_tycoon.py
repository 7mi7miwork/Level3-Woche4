"""
╔══════════════════════════════════════════════════════════════╗
║    BUSINESS TYCOON PRO  —  by Michael (其米）                ║
║    pip install pygame  →  python business_tycoon.py          ║
║    NEU: Speichersystem (F5=Speichern, F9=Laden, F1=Slots)    ║
║         50+ Achievements mit Schwierigkeitsgraden            ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame, random, sys, math, json, os
from dataclasses import dataclass, field
from typing import List, Dict

# ─────────────────────────────────────────────────────
#  FARBEN
# ─────────────────────────────────────────────────────
BG      = (10,  14,  26)
PANEL   = (17,  24,  39)
PANEL2  = (31,  41,  55)
BORDER  = (55,  65,  81)
ACCENT  = (59, 130, 246)
GREEN   = (16, 185, 129)
RED     = (239, 68,  68)
YELLOW  = (245,158,  11)
CYAN    = (6,  182, 212)
GOLD    = (251,191,  36)
WHITE   = (240,240, 248)
MUTED   = (107,114, 128)
ORANGE  = (249,115,  22)
PURPLE  = (139, 92, 246)
PINK    = (236, 72, 153)
TEAL    = (20, 184, 166)

pygame.init()
W, H = 1280, 760
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Business Tycoon Pro — by Michael (其米）")
clock = pygame.time.Clock()

# ─────────────────────────────────────────────────────
#  SCHRIFTEN
# ─────────────────────────────────────────────────────
def _f(size, bold=False):
    for name in ["segoeui","arial","freesansbold" if bold else "freesans","sans"]:
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except:
            pass
    return pygame.font.Font(None, size)

F = {
    "xs":  _f(11), "sm": _f(13), "md": _f(15),
    "lg":  _f(17, True), "xl": _f(22, True), "title": _f(28, True),
}

# ─────────────────────────────────────────────────────
#  HILFSFUNKTIONEN
# ─────────────────────────────────────────────────────
def fmt(n: float) -> str:
    n = float(n)
    if abs(n) >= 1e9:  return f"{n/1e9:.2f} Mrd €"
    if abs(n) >= 1e6:  return f"{n/1e6:.2f} Mio €"
    if abs(n) >= 1e3:  return f"{n/1e3:.1f}k €"
    return f"{n:,.0f} €".replace(",",".")

def txt(surf, text, fkey, color, x, y, anchor="topleft", maxw=0):
    f = F[fkey]
    s = str(text)
    if maxw > 0:
        while f.size(s)[0] > maxw and len(s) > 1:
            s = s[:-1]
        if s != str(text): s += "…"
    surf_t = f.render(s, True, color)
    r = surf_t.get_rect(**{anchor: (x, y)})
    surf.blit(surf_t, r)
    return r

def box(surf, color, rect, r=6, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=r)

def line(surf, color, p1, p2):
    pygame.draw.line(surf, color, p1, p2)

def sparkline(surf, hist, x, y, w, h, col=None):
    if len(hist) < 2: return
    mn, mx2 = min(hist), max(hist)
    if mx2 == mn: mx2 = mn + 0.001
    pts = [(x + int(i/(len(hist)-1)*w),
            y + h - int((v-mn)/(mx2-mn)*h))
           for i, v in enumerate(hist)]
    c = col or (GREEN if hist[-1] >= hist[0] else RED)
    if len(pts) >= 2:
        pygame.draw.lines(surf, c, False, pts, 2)

def progress_bar(surf, x, y, w, h, frac, color):
    box(surf, PANEL2, (x,y,w,h), 3)
    fw = max(0, min(w, int(w*frac)))
    if fw > 0: box(surf, color, (x,y,fw,h), 3)

def dim_overlay(surf):
    s = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    s.fill((0,0,0,170))
    surf.blit(s,(0,0))

# ─────────────────────────────────────────────────────
#  SPEICHERSYSTEM
# ─────────────────────────────────────────────────────
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
os.makedirs(SAVE_DIR, exist_ok=True)
NUM_SLOTS = 6

def save_slot_path(slot: int) -> str:
    return os.path.join(SAVE_DIR, f"slot_{slot}.json")

def save_game(gs, slot: int) -> bool:
    """Speichert den Spielstand in einen Slot."""
    try:
        data = {
            "version": 2,
            "name": gs.name,
            "cash": gs.cash,
            "loan": gs.loan,
            "savings": gs.savings,
            "sav_rate": gs.sav_rate,
            "loan_rate": gs.loan_rate,
            "props": gs.props,
            "comps": gs.comps,
            "stocks": gs.stocks,
            "etf": gs.etf,
            "etf_price": gs.etf_price,
            "etf_hist": gs.etf_hist,
            "stock_data": {
                sid: {k: v for k, v in s.items()}
                for sid, s in gs.stock_data.items()
            },
            "month": gs.month,
            "year": gs.year,
            "phase": gs.phase,
            "phase_dur": gs.phase_dur,
            "base_rate": gs.base_rate,
            "inflation": gs.inflation,
            "gdp": gs.gdp,
            "unemp": gs.unemp,
            "sentiment": gs.sentiment,
            "reputation": gs.reputation,
            "tax_rate": gs.tax_rate,
            "achiev_done": list(gs.achiev_done),
            "log": gs.log[:40],
            "news": gs.news[:10],
            "nw_hist": gs.nw_hist,
            "cf_hist": gs.cf_hist,
            "_survived_dep": gs._survived_dep,
            "_crashed_once": getattr(gs, "_crashed_once", False),
            "_total_months": getattr(gs, "_total_months", 0),
            "_total_props_bought": getattr(gs, "_total_props_bought", 0),
            "_total_comps_bought": getattr(gs, "_total_comps_bought", 0),
            "_max_nw": getattr(gs, "_max_nw", 0),
            "_total_dividends": getattr(gs, "_total_dividends", 0),
            "_total_loan_repaid": getattr(gs, "_total_loan_repaid", 0),
            "_booms_survived": getattr(gs, "_booms_survived", 0),
            "_recessions_survived": getattr(gs, "_recessions_survived", 0),
            "_depressions_survived": getattr(gs, "_depressions_survived", 0),
            "_hyperinflations_survived": getattr(gs, "_hyperinflations_survived", 0),
            "_total_upgrades": getattr(gs, "_total_upgrades", 0),
            "_positive_cf_months": getattr(gs, "_positive_cf_months", 0),
            "_stock_trades": getattr(gs, "_stock_trades", 0),
            "_max_cash": getattr(gs, "_max_cash", 0),
            "_all_phases_seen": list(getattr(gs, "_all_phases_seen", set())),
            "_consecutive_profit_months": getattr(gs, "_consecutive_profit_months", 0),
            "_max_consecutive_profit": getattr(gs, "_max_consecutive_profit", 0),
        }
        with open(save_slot_path(slot), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Speicherfehler: {e}")
        return False

def load_game(slot: int):
    """Lädt einen Spielstand. Gibt GS-Objekt oder None zurück."""
    path = save_slot_path(slot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        gs = GS()
        gs.name       = data.get("name", "Investor")
        gs.cash       = data.get("cash", 50000.0)
        gs.loan       = data.get("loan", 0.0)
        gs.savings    = data.get("savings", 0.0)
        gs.sav_rate   = data.get("sav_rate", 0.0035)
        gs.loan_rate  = data.get("loan_rate", 0.006)
        gs.props      = data.get("props", [])
        gs.comps      = data.get("comps", [])
        gs.stocks     = data.get("stocks", {})
        gs.etf        = data.get("etf", 0.0)
        gs.etf_price  = data.get("etf_price", 100.0)
        gs.etf_hist   = data.get("etf_hist", [100.0])
        # Marktdaten wiederherstellen
        saved_sd = data.get("stock_data", {})
        for sid in gs.stock_data:
            if sid in saved_sd:
                gs.stock_data[sid].update(saved_sd[sid])
        gs.month      = data.get("month", 1)
        gs.year       = data.get("year", 2024)
        gs.phase      = data.get("phase", "STABLE")
        gs.phase_dur  = data.get("phase_dur", 8)
        gs.base_rate  = data.get("base_rate", 5.0)
        gs.inflation  = data.get("inflation", 0.002)
        gs.gdp        = data.get("gdp", 2.0)
        gs.unemp      = data.get("unemp", 5.0)
        gs.sentiment  = data.get("sentiment", 50.0)
        gs.reputation = data.get("reputation", 50)
        gs.tax_rate   = data.get("tax_rate", 0.25)
        gs.achiev_done= set(data.get("achiev_done", []))
        gs.log        = [tuple(x) for x in data.get("log", [])]
        gs.news       = data.get("news", [])
        gs.nw_hist    = data.get("nw_hist", [])
        gs.cf_hist    = data.get("cf_hist", [])
        gs._survived_dep = data.get("_survived_dep", False)
        gs._crashed_once = data.get("_crashed_once", False)
        gs._total_months = data.get("_total_months", 0)
        gs._total_props_bought = data.get("_total_props_bought", 0)
        gs._total_comps_bought = data.get("_total_comps_bought", 0)
        gs._max_nw = data.get("_max_nw", 0)
        gs._total_dividends = data.get("_total_dividends", 0)
        gs._total_loan_repaid = data.get("_total_loan_repaid", 0)
        gs._booms_survived = data.get("_booms_survived", 0)
        gs._recessions_survived = data.get("_recessions_survived", 0)
        gs._depressions_survived = data.get("_depressions_survived", 0)
        gs._hyperinflations_survived = data.get("_hyperinflations_survived", 0)
        gs._total_upgrades = data.get("_total_upgrades", 0)
        gs._positive_cf_months = data.get("_positive_cf_months", 0)
        gs._stock_trades = data.get("_stock_trades", 0)
        gs._max_cash = data.get("_max_cash", 0)
        gs._all_phases_seen = set(data.get("_all_phases_seen", []))
        gs._consecutive_profit_months = data.get("_consecutive_profit_months", 0)
        gs._max_consecutive_profit = data.get("_max_consecutive_profit", 0)
        return gs
    except Exception as e:
        print(f"Ladefehler: {e}")
        return None

def get_slot_info(slot: int) -> dict:
    """Gibt Infos über einen Speicherslot zurück."""
    path = save_slot_path(slot)
    if not os.path.exists(path):
        return {"empty": True}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        mtime = os.path.getmtime(path)
        import time
        return {
            "empty": False,
            "name": data.get("name", "?"),
            "year": data.get("year", 2024),
            "month": data.get("month", 1),
            "nw": data.get("nw_hist", [0])[-1] if data.get("nw_hist") else 0,
            "achievements": len(data.get("achiev_done", [])),
            "saved_at": time.strftime("%d.%m.%Y %H:%M", time.localtime(mtime)),
        }
    except:
        return {"empty": True}

def delete_slot(slot: int):
    path = save_slot_path(slot)
    if os.path.exists(path):
        os.remove(path)

# ─────────────────────────────────────────────────────
#  INPUT-BOX
# ─────────────────────────────────────────────────────
class InputBox:
    def __init__(self, x, y, w, h=34, hint="", numeric=True):
        self.rect  = pygame.Rect(x, y, w, h)
        self.hint  = hint
        self.text  = ""
        self.active= False
        self.numeric = numeric

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(ev.pos)
        if ev.type == pygame.KEYDOWN and self.active:
            if ev.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif ev.unicode.isprintable():
                ch = ev.unicode
                if self.numeric:
                    if ch.isdigit() or (ch=='.' and '.' not in self.text):
                        self.text += ch
                else:
                    self.text += ch

    def val(self):
        try: return float(self.text)
        except: return 0.0

    def draw(self, surf):
        col = ACCENT if self.active else BORDER
        box(surf, PANEL2, self.rect, 5)
        box(surf, col, self.rect, 5, 1)
        show = self.text if self.text else self.hint
        color = WHITE if self.text else MUTED
        txt(surf, show, "sm", color, self.rect.x+8, self.rect.centery, "midleft")

    def clear(self):
        self.text = ""

# ─────────────────────────────────────────────────────
#  BUTTON
# ─────────────────────────────────────────────────────
class Btn:
    def __init__(self, x, y, w, h, label, color=None, tc=WHITE, fkey="sm"):
        self.rect  = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color or ACCENT
        self.tc    = tc
        self.fkey  = fkey
        self.hover = False

    def draw(self, surf):
        c = tuple(min(255,v+25) for v in self.color) if self.hover else self.color
        box(surf, c, self.rect, 6)
        txt(surf, self.label, self.fkey, self.tc,
            self.rect.centerx, self.rect.centery, "center")

    def update(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def hit(self, ev):
        return (ev.type == pygame.MOUSEBUTTONDOWN
                and ev.button == 1
                and self.rect.collidepoint(ev.pos))

# ─────────────────────────────────────────────────────
#  SPIELZUSTAND-DATEN
# ─────────────────────────────────────────────────────
PROP_CATALOG = [
    ("flat",   "Kleine Wohnung",   "Wohnung",   75_000,    550,    90, 5),
    ("house",  "Einfamilienhaus",  "Haus",     240_000,  1_300,   270, 5),
    ("condo",  "Luxus-Penthouse",  "Penthouse",650_000,  4_000,   600, 5),
    ("office", "Bürogebäude",      "Büro",   1_200_000,  9_000, 1_400, 5),
    ("mall",   "Einkaufszentrum",  "Mall",   3_000_000, 25_000, 3_500, 5),
    ("hotel",  "Luxus-Hotel",      "Hotel",  5_000_000, 40_000, 6_000, 5),
]

COMP_CATALOG = [
    ("cafe",    "Café / Kiosk",       "Café",       15_000,      280,    40, 0.05, 8),
    ("craft",   "Handwerksbetrieb",   "Handwerk",   80_000,    1_100,   180, 0.05, 8),
    ("retail",  "Einzelhandel",        "Handel",    200_000,    2_500,   400, 0.08, 8),
    ("tech",    "Software-Startup",   "Software",  500_000,    7_000,   800, 0.12, 8),
    ("factory", "Fabrik",              "Fabrik",  1_500_000,   18_000, 2_800, 0.06, 8),
    ("media",   "Medienkonzern",       "Medien",  4_000_000,   50_000, 8_000, 0.10, 8),
    ("pharma",  "Pharmaunternehmen",   "Pharma",  8_000_000,  110_000,15_000, 0.14, 8),
    ("ibank",   "Investmentbank",      "Bank",   20_000_000,  300_000,40_000, 0.18, 8),
]

STOCK_CATALOG = [
    ("tg",   "TechGiant",    150.0, 0.13, 0.005, "Tech"),
    ("ac",   "AutoCorp",      85.0, 0.09, 0.018, "Auto"),
    ("ec",   "EnergyCo",     110.0, 0.07, 0.022, "Energie"),
    ("bg",   "BankGroup",     65.0, 0.11, 0.012, "Finanzen"),
    ("ph",   "PharmaHealth", 200.0, 0.10, 0.008, "Gesundheit"),
    ("re",   "RealEstCorp",   90.0, 0.08, 0.025, "Immobilien"),
    ("ai",   "AI-Ventures",  350.0, 0.25, 0.001, "Tech"),
    ("food", "FoodChain",     45.0, 0.06, 0.030, "Konsum"),
]

PHASES = {
    "BOOM":           {"label":"Boom",          "col":GREEN,  "stk":+.04, "rent":+.02, "profit":+.05},
    "STABLE":         {"label":"Stabil",        "col":CYAN,   "stk": .00, "rent": .00, "profit": .00},
    "RECESSION":      {"label":"Rezession",     "col":YELLOW, "stk":-.03, "rent":-.01, "profit":-.03},
    "DEPRESSION":     {"label":"Depression",    "col":RED,    "stk":-.08, "rent":-.03, "profit":-.08},
    "STAGFLATION":    {"label":"Stagflation",   "col":ORANGE, "stk":-.02, "rent":+.01, "profit":-.04},
    "HYPERINFLATION": {"label":"Hyperinflation","col":PINK,   "stk":+.01, "rent":+.06, "profit":-.06},
}

# ─────────────────────────────────────────────────────
#  ACHIEVEMENTS — 52 Stück, 5 Schwierigkeitsstufen
# ─────────────────────────────────────────────────────
# Schwierigkeit: "leicht" / "mittel" / "schwer" / "extrem" / "legendaer"
DIFF_COLORS = {
    "leicht":    GREEN,
    "mittel":    CYAN,
    "schwer":    YELLOW,
    "extrem":    ORANGE,
    "legendaer": GOLD,
}

ACHIEVEMENTS = [
    # ── VERMÖGEN ──────────────────────────────────────
    ("first_steps",    "Erste Schritte",        "leicht",
     "Erste Immobilie oder Firma gekauft",
     lambda g: len(g.props)+len(g.comps) >= 1),

    ("kiosk_owner",    "Kioskbesitzer",         "leicht",
     "Ein Café/Kiosk gegründet",
     lambda g: any(c["id"]=="cafe" for c in g.comps)),

    ("millionaire",    "Millionär",             "mittel",
     "Nettovermögen > 1 Mio €",
     lambda g: g.net_worth() >= 1_000_000),

    ("five_mio",       "5-Millionär",           "mittel",
     "Nettovermögen > 5 Mio €",
     lambda g: g.net_worth() >= 5_000_000),

    ("ten_mio",        "10-Millionär",          "schwer",
     "Nettovermögen > 10 Mio €",
     lambda g: g.net_worth() >= 10_000_000),

    ("fifty_mio",      "50-Millionär",          "extrem",
     "Nettovermögen > 50 Mio €",
     lambda g: g.net_worth() >= 50_000_000),

    ("legend_100",     "Legende",               "legendaer",
     "Nettovermögen > 100 Mio €",
     lambda g: g.net_worth() >= 100_000_000),

    ("billionaire",    "Milliardär",            "legendaer",
     "Nettovermögen > 1 Mrd €",
     lambda g: g.net_worth() >= 1_000_000_000),

    ("cash_king",      "Cash King",             "schwer",
     "Mehr als 5 Mio € Bargeld gleichzeitig",
     lambda g: g.cash >= 5_000_000),

    ("scrooge",        "Dagobert Duck",         "extrem",
     "Mehr als 50 Mio € Bargeld gleichzeitig",
     lambda g: g.cash >= 50_000_000),

    # ── IMMOBILIEN ────────────────────────────────────
    ("landlord",       "Vermieter",             "leicht",
     "3 oder mehr Immobilien besitzen",
     lambda g: len(g.props) >= 3),

    ("property_baron", "Immobilienmagnat",      "mittel",
     "6 oder mehr Immobilien besitzen",
     lambda g: len(g.props) >= 6),

    ("empire",         "Immobilienimperium",    "schwer",
     "10 oder mehr Immobilien besitzen",
     lambda g: len(g.props) >= 10),

    ("hotel_king",     "Hotelkönig",            "schwer",
     "Ein Luxus-Hotel besitzen",
     lambda g: any(p["id"]=="hotel" for p in g.props)),

    ("mall_lord",      "Mall-Lord",             "schwer",
     "Zwei Einkaufszentren besitzen",
     lambda g: sum(1 for p in g.props if p["id"]=="mall") >= 2),

    ("fullhouse",      "Vollvermieter",         "mittel",
     "Alle Immobilien vermietet (mind. 3)",
     lambda g: len(g.props)>=3 and all(not p["vacant"] for p in g.props)),

    ("premium_rent",   "Premium-Vermieter",     "mittel",
     "Luxusmieter in einer Immobilie",
     lambda g: any(p.get("tenant")==3 for p in g.props)),

    ("maxed_prop",     "Renovierungsmeister",   "schwer",
     "Eine Immobilie auf Max-Level bringen",
     lambda g: any(p["level"]>=p["lvl_max"] for p in g.props)),

    ("all_maxed",      "Perfektion",            "extrem",
     "Alle Immobilien auf Max-Level",
     lambda g: len(g.props)>=3 and all(p["level"]>=p["lvl_max"] for p in g.props)),

    ("passive_rent",   "Passiv-Einkommen",      "schwer",
     "Monatl. Mieteinnahmen > 100k €",
     lambda g: sum(p["rent"] for p in g.props if not p["vacant"]) >= 100_000),

    ("rent_mogul",     "Miet-Mogul",            "extrem",
     "Monatl. Mieteinnahmen > 1 Mio €",
     lambda g: sum(p["rent"] for p in g.props if not p["vacant"]) >= 1_000_000),

    ("multi_upgrades", "Fleißiger Renovierer",  "mittel",
     "Insgesamt 20 Upgrades durchgeführt",
     lambda g: getattr(g,"_total_upgrades",0) >= 20),

    # ── UNTERNEHMEN ───────────────────────────────────
    ("entrepreneur",   "Unternehmer",           "leicht",
     "Erste Firma gegründet",
     lambda g: len(g.comps) >= 1),

    ("tycoon",         "Tycoon",                "mittel",
     "5 oder mehr Unternehmen besitzen",
     lambda g: len(g.comps) >= 5),

    ("mogul",          "Mogul",                 "schwer",
     "10 oder mehr Unternehmen besitzen",
     lambda g: len(g.comps) >= 10),

    ("bank_owner",     "Bankier",               "legendaer",
     "Eine Investmentbank besitzen",
     lambda g: any(c["id"]=="ibank" for c in g.comps)),

    ("pharma_lord",    "Pharma-König",          "extrem",
     "Pharmaunternehmen auf Level 5+",
     lambda g: any(c["id"]=="pharma" and c["level"]>=5 for c in g.comps)),

    ("media_empire",   "Medienimperium",        "schwer",
     "Medienkonzern auf Max-Level",
     lambda g: any(c["id"]=="media" and c["level"]>=c["lvl_max"] for c in g.comps)),

    ("tech_unicorn",   "Tech-Unicorn",          "extrem",
     "Software-Startup auf Max-Level mit Wert > 10 Mio €",
     lambda g: any(c["id"]=="tech" and c["level"]>=c["lvl_max"] and c["val"]>=10_000_000 for c in g.comps)),

    ("comp_profit",    "Gewinnmaschine",        "schwer",
     "Monatl. Firmengewinn > 500k €",
     lambda g: sum(c["profit"] for c in g.comps) >= 500_000),

    ("mega_profit",    "Mega-Gewinnmaschine",   "legendaer",
     "Monatl. Firmengewinn > 5 Mio €",
     lambda g: sum(c["profit"] for c in g.comps) >= 5_000_000),

    # ── AKTIEN & FINANZEN ─────────────────────────────
    ("investor",       "Investor",              "leicht",
     "Aktien im Wert von 100k € besitzen",
     lambda g: g.stock_value() >= 100_000),

    ("stock_whale",    "Aktienwal",             "mittel",
     "Aktienportfolio > 1 Mio €",
     lambda g: g.stock_value() >= 1_000_000),

    ("wolf_of_wall",   "Wolf der Wallstreet",  "schwer",
     "Aktienportfolio > 10 Mio €",
     lambda g: g.stock_value() >= 10_000_000),

    ("etf_fan",        "ETF-Enthusiast",        "leicht",
     "Mehr als 100 ETF-Anteile besitzen",
     lambda g: g.etf >= 100),

    ("etf_master",     "ETF-Meister",           "schwer",
     "ETF-Portfolio > 5 Mio €",
     lambda g: g.etf * g.etf_price >= 5_000_000),

    ("diversify",      "Diversifikation",       "mittel",
     "In Immobilien, Firmen UND Aktien investiert",
     lambda g: len(g.props)>0 and len(g.comps)>0 and g.stock_value()>0),

    ("all_stocks",     "Volles Portfolio",      "schwer",
     "Alle 8 Aktien gleichzeitig besitzen",
     lambda g: all(g.stocks.get(sid,0)>0 for sid in ["tg","ac","ec","bg","ph","re","ai","food"])),

    ("dividend_king",  "Dividendenkönig",       "extrem",
     "Monatl. Dividenden > 50k €",
     lambda g: sum(qty*g.stock_data[sid]["price"]*g.stock_data[sid]["div"]/12
                   for sid,qty in g.stocks.items() if qty>0) >= 50_000),

    ("savings_master", "Sparmeister",           "mittel",
     "Mehr als 500k € auf Festgeld",
     lambda g: g.savings >= 500_000),

    ("debtfree",       "Schuldenfrei",          "mittel",
     "Alle Schulden getilgt (nach mind. einem Kredit)",
     lambda g: g.loan==0 and getattr(g,"_total_loan_repaid",0)>0),

    ("big_repay",      "Schuldenvernichter",    "schwer",
     "Insgesamt > 5 Mio € Schulden getilgt",
     lambda g: getattr(g,"_total_loan_repaid",0) >= 5_000_000),

    # ── WIRTSCHAFTLICHE KRISEN ────────────────────────
    ("recession_pro",  "Rezessions-Profi",      "mittel",
     "3 Rezessionen überlebt",
     lambda g: getattr(g,"_recessions_survived",0) >= 3),

    ("depression_slayer","Depressions-Killer", "schwer",
     "Eine Depression überlebt",
     lambda g: getattr(g,"_survived_dep",False)),

    ("crisis_king",    "Krisen-König",          "extrem",
     "Depression UND Hyperinflation überlebt",
     lambda g: getattr(g,"_survived_dep",False) and getattr(g,"_hyperinflations_survived",0)>=1),

    ("phase_collector","Phasen-Sammler",        "extrem",
     "Alle 6 Wirtschaftsphasen erlebt",
     lambda g: len(getattr(g,"_all_phases_seen",set())) >= 6),

    # ── RUHM & REPUTATION ─────────────────────────────
    ("famous",         "Berühmt",               "mittel",
     "Reputation > 80",
     lambda g: g.reputation >= 80),

    ("icon",           "Ikone",                 "schwer",
     "Reputation auf 100",
     lambda g: g.reputation >= 100),

    # ── ZEIT & AUSDAUER ───────────────────────────────
    ("survivor_1y",    "Jahres-Investor",       "leicht",
     "12 Monate gespielt",
     lambda g: getattr(g,"_total_months",0) >= 12),

    ("veteran_5y",     "Veteran",               "mittel",
     "60 Monate (5 Jahre) gespielt",
     lambda g: getattr(g,"_total_months",0) >= 60),

    ("decade",         "Dekade",                "schwer",
     "120 Monate (10 Jahre) gespielt",
     lambda g: getattr(g,"_total_months",0) >= 120),

    ("century",        "Jahrhundert-Investor",  "legendaer",
     "1200 Monate (100 Jahre) gespielt",
     lambda g: getattr(g,"_total_months",0) >= 1200),

    ("profit_streak",  "Gewinnsträhne",         "schwer",
     "24 Monate hintereinander positiver Cashflow",
     lambda g: getattr(g,"_max_consecutive_profit",0) >= 24),

    ("absolute_legend","ABSOLUTE LEGENDE",      "legendaer",
     "Alle anderen Achievements freigeschaltet!",
     lambda g: len(g.achiev_done) >= len(ACHIEVEMENTS)-1),
]


# ─────────────────────────────────────────────────────
#  SPIELZUSTAND
# ─────────────────────────────────────────────────────
class GS:
    """Gesamter Spielzustand."""
    def __init__(self):
        self.name      = "Investor"
        self.cash      = 50_000.0
        self.loan      = 0.0
        self.savings   = 0.0
        self.sav_rate  = 0.0035
        self.loan_rate = 0.006

        self.props : List[dict] = []
        self.comps : List[dict] = []
        self.stocks: Dict[str,float] = {}
        self.etf   : float = 0.0

        # Marktdaten
        self.stock_data = {
            sid: {"name":name,"price":price,"vol":vol,
                  "div":div,"sector":sector,"hist":[price]}
            for sid,name,price,vol,div,sector in STOCK_CATALOG
        }
        self.etf_price = 100.0
        self.etf_hist  = [100.0]

        # Zeit
        self.month = 1
        self.year  = 2024

        # Wirtschaft
        self.phase    = "STABLE"
        self.phase_dur= 8
        self.base_rate= 5.0
        self.inflation= 0.002
        self.gdp      = 2.0
        self.unemp    = 5.0
        self.sentiment= 50.0

        # Sonstiges
        self.reputation = 50
        self.tax_rate   = 0.25
        self.achiev_done= set()
        self.log  : List[tuple] = []
        self.news : List[str]   = []
        self.nw_hist  : List[float] = []
        self.cf_hist  : List[float] = []

        # Tracking-Flags für Achievements
        self._survived_dep           = False
        self._crashed_once           = False
        self._total_months           = 0
        self._total_props_bought     = 0
        self._total_comps_bought     = 0
        self._max_nw                 = 0.0
        self._total_dividends        = 0.0
        self._total_loan_repaid      = 0.0
        self._booms_survived         = 0
        self._recessions_survived    = 0
        self._depressions_survived   = 0
        self._hyperinflations_survived = 0
        self._total_upgrades         = 0
        self._positive_cf_months     = 0
        self._stock_trades           = 0
        self._max_cash               = 0.0
        self._all_phases_seen        = set()
        self._consecutive_profit_months = 0
        self._max_consecutive_profit    = 0

    # ── Berechnungen ──
    def net_worth(self):
        v = self.cash + self.savings
        for p in self.props: v += p["price"]
        for c in self.comps: v += c["val"]
        for sid, qty in self.stocks.items():
            v += qty * self.stock_data[sid]["price"]
        v += self.etf * self.etf_price
        v -= self.loan
        return v

    def stock_value(self):
        v = sum(qty * self.stock_data[sid]["price"]
                for sid, qty in self.stocks.items() if qty > 0)
        return v + self.etf * self.etf_price

    def monthly_income(self):
        i  = sum(p["rent"] for p in self.props if not p["vacant"])
        i += sum(c["profit"] for c in self.comps)
        i += sum(qty * self.stock_data[sid]["price"] * self.stock_data[sid]["div"] / 12
                 for sid, qty in self.stocks.items() if qty > 0)
        i += self.etf * self.etf_price * 0.002 / 12
        i += self.savings * self.sav_rate
        return i

    def monthly_expenses(self):
        e  = sum(p["maint"] for p in self.props)
        e += sum(c["maint"] for c in self.comps)
        e += self.loan * (self.loan_rate + self.base_rate/100/12)
        return e

    def add_log(self, msg, kind="info"):
        self.log.insert(0, (msg, kind))
        if len(self.log) > 80: self.log.pop()

    def add_news(self, msg):
        self.news.insert(0, msg)
        if len(self.news) > 20: self.news.pop()


# ─────────────────────────────────────────────────────
#  SPIELLOGIK (Monatstick)
# ─────────────────────────────────────────────────────
TENANT_TYPES = [
    ("Privat-Mieter",  0.00, 0.03, 12),
    ("Student",       -0.10, 0.10,  6),
    ("Firmenkunde",   +0.25, 0.05, 24),
    ("Luxusmieter",   +0.40, 0.04, 18),
    ("Sozialmieter",  -0.20, 0.01, 36),
]

def make_prop(catalog_row):
    tid, name, icon, price, rent, maint, lvl_max = catalog_row
    return {
        "id": tid, "name": name, "icon": icon,
        "price":     float(price),
        "base_rent": float(rent),
        "rent":      float(rent),
        "maint":     float(maint),
        "level": 1, "lvl_max": lvl_max,
        "vacant":  True,
        "listed":  False,
        "tenant":  None,
        "contract_left": 0,
        "rent_hist": [],
    }

def make_comp(catalog_row):
    tid, name, icon, price, profit, maint, risk, lvl_max = catalog_row
    return {"id":tid,"name":name,"icon":icon,
            "base_price":float(price),"val":float(price),
            "base_profit":float(profit),"profit":float(profit),
            "maint":float(maint),"risk":risk,
            "level":1,"lvl_max":lvl_max}

def tick(gs: GS):
    """Einen Monat vorwärtssimulieren."""
    gs.month += 1
    gs._total_months += 1
    if gs.month > 12:
        gs.month = 1
        gs.year += 1
        _year_end(gs)

    gs._all_phases_seen.add(gs.phase)
    _update_economy(gs)
    _update_markets(gs)

    ph = PHASES[gs.phase]
    income = 0.0
    expenses = 0.0

    # ── Immobilien ──
    for p in gs.props:
        if p["tenant"] is not None and p["contract_left"] > 0:
            p["contract_left"] -= 1
            if p["contract_left"] == 0:
                tname = TENANT_TYPES[p["tenant"]][0]
                gs.add_log(f"Mietvertrag abgelaufen: {p['name']} ({tname})", "warn")
                p["tenant"]  = None
                p["vacant"]  = True
                p["listed"]  = False

        if p["listed"] and p["vacant"]:
            chance = {"BOOM":0.55,"STABLE":0.40,"RECESSION":0.25,
                      "DEPRESSION":0.10,"STAGFLATION":0.20,"HYPERINFLATION":0.15}.get(gs.phase, 0.30)
            if random.random() < chance:
                weights = [4, 3, 2, 1, 2]
                ti = random.choices(range(len(TENANT_TYPES)), weights=weights)[0]
                tname, bonus, _, months = TENANT_TYPES[ti]
                p["tenant"]        = ti
                p["vacant"]        = False
                p["contract_left"] = months
                p["rent"]          = p["base_rent"] * (1 + bonus)
                gs.add_log(f"Neuer Mieter: {tname} in {p['name']} ({months} Monate)", "good")

        if not p["vacant"] and p["tenant"] is not None:
            dmg_risk = TENANT_TYPES[p["tenant"]][2]
            if random.random() < dmg_risk * 0.4:
                dmg = p["maint"] * (0.5 + random.random())
                expenses += dmg
                gs.add_log(f"Mieterschaden in {p['name']}: -{fmt(dmg)}", "bad")

        rent = p["rent"] * (1 + ph["rent"]) if not p["vacant"] else 0.0
        income   += rent
        expenses += p["maint"]
        p["rent_hist"].append(round(rent))
        if len(p["rent_hist"]) > 24: p["rent_hist"].pop(0)
        p["price"]     *= 1 + gs.inflation*0.7 + (0.004 if gs.phase=="BOOM" else -0.001)
        p["base_rent"] *= 1 + gs.inflation*0.35
        if not p["vacant"]:
            p["rent"] *= 1 + gs.inflation*0.35

    # ── Unternehmen ──
    rep_bonus = (gs.reputation - 50) / 2000.0
    for c in gs.comps:
        eff = c["base_profit"] * (1 + ph["profit"] + rep_bonus)
        c["profit"] = max(0.0, eff)
        if random.random() < c["risk"] * 0.35:
            dmg = c["profit"] * (0.15 + random.random()*0.25)
            expenses += dmg
            gs.add_log(f"Schadenfall bei {c['name']}: -{fmt(dmg)}", "bad")
        income   += c["profit"]
        expenses += c["maint"]
        c["val"]         *= 1 + gs.inflation*0.4
        c["base_profit"] *= 1 + gs.inflation*0.2

    # ── Kredit ──
    eff_rate = gs.loan_rate + gs.base_rate/100.0/12.0
    expenses += gs.loan * eff_rate

    # ── Tagesgeld ──
    income += gs.savings * gs.sav_rate

    # ── Aktiendividenden ──
    div_this_month = 0.0
    for sid, qty in gs.stocks.items():
        if qty > 0:
            s = gs.stock_data[sid]
            d = qty * s["price"] * s["div"] / 12.0
            div_this_month += d
            income += d
    gs._total_dividends += div_this_month

    # ── ETF-Dividenden ──
    income += gs.etf * gs.etf_price * 0.002 / 12.0

    # ── Zufallsereignisse ──
    _random_events(gs)

    # ── Steuer ──
    gross = income - expenses
    tax   = max(0.0, gross * gs.tax_rate)
    expenses += tax

    cf = income - expenses
    gs.cash += cf

    # Tracking
    if cf > 0:
        gs._consecutive_profit_months += 1
        gs._max_consecutive_profit = max(gs._max_consecutive_profit, gs._consecutive_profit_months)
    else:
        gs._consecutive_profit_months = 0

    gs._max_cash = max(gs._max_cash, gs.cash)
    gs._max_nw   = max(gs._max_nw, gs.net_worth())

    gs.cf_hist.append(cf)
    gs.nw_hist.append(gs.net_worth())
    if len(gs.cf_hist) > 24:  gs.cf_hist.pop(0)
    if len(gs.nw_hist) > 24:  gs.nw_hist.pop(0)

    gs.inflation = 0.001 + random.random()*0.004
    if gs.phase == "HYPERINFLATION": gs.inflation *= 4

    if gs.phase == "DEPRESSION" and gs.cash > 0:
        gs._survived_dep = True

    # ── Bankrott ──
    if gs.cash < -50_000 and gs.loan > gs.net_worth()*2:
        return "bankrott"
    return None


def _year_end(gs: GS):
    gs.add_news(f"Jahresabschluss {gs.year-1}: NV {fmt(gs.net_worth())}")
    if gs.net_worth() > 2_000_000:
        wt = (gs.net_worth() - 2_000_000) * 0.005
        gs.cash -= wt
        gs.add_log(f"Vermögenssteuer: -{fmt(wt)}", "bad")


def _update_economy(gs: GS):
    prev_phase = gs.phase
    gs.phase_dur -= 1
    if gs.phase_dur <= 0:
        r = random.random()
        if   r < 0.07: gs.phase, gs.phase_dur = "DEPRESSION",     random.randint(2,5)
        elif r < 0.22: gs.phase, gs.phase_dur = "RECESSION",      random.randint(3,7)
        elif r < 0.28: gs.phase, gs.phase_dur = "STAGFLATION",    random.randint(2,4)
        elif r < 0.30: gs.phase, gs.phase_dur = "HYPERINFLATION", random.randint(1,3)
        elif r < 0.65: gs.phase, gs.phase_dur = "STABLE",         random.randint(5,10)
        else:          gs.phase, gs.phase_dur = "BOOM",            random.randint(3,6)

        if gs.phase != prev_phase:
            # Phase-Tracking für Achievements
            if prev_phase == "BOOM":          gs._booms_survived += 1
            if prev_phase == "RECESSION":     gs._recessions_survived += 1
            if prev_phase == "DEPRESSION":    gs._depressions_survived += 1
            if prev_phase == "HYPERINFLATION":gs._hyperinflations_survived += 1

            label = PHASES[gs.phase]["label"]
            gs.add_news(f"Wirtschaftswechsel: {label}")
            kind = "good" if gs.phase=="BOOM" else ("bad" if "DEPRESS" in gs.phase else "warn")
            gs.add_log(f"Wirtschaft: {label}", kind)

    delta = {"BOOM":+.06,"STABLE":0,"RECESSION":-.1,
             "DEPRESSION":-.15,"STAGFLATION":0,"HYPERINFLATION":0}
    gs.base_rate = max(0, min(15, gs.base_rate + delta.get(gs.phase,0)))
    gs.loan_rate = 0.004 + gs.base_rate/100.0/12.0

    gs.gdp   += {"BOOM":.15,"STABLE":0,"RECESSION":-.2,"DEPRESSION":-.4,
                 "STAGFLATION":-.1,"HYPERINFLATION":-.15}.get(gs.phase,0)
    gs.unemp += {"BOOM":-.1,"STABLE":0,"RECESSION":.25,"DEPRESSION":.5,
                 "STAGFLATION":.1,"HYPERINFLATION":.1}.get(gs.phase,0)
    gs.gdp   = max(-15, min(12, gs.gdp))
    gs.unemp = max(1,   min(30, gs.unemp))
    gs.sentiment += (random.random()-.48)*8
    gs.sentiment  = max(0, min(100, gs.sentiment))


def _update_markets(gs: GS):
    ph   = PHASES[gs.phase]
    sent = (gs.sentiment-50)/5000.0
    sector_bonus = {
        "Tech":("BOOM",.015), "Energie":("STAGFLATION",.02),
        "Finanzen":("DEPRESSION",-.025), "Gesundheit":(None,.005), "Konsum":(None,.003)
    }
    for sid, s in gs.stock_data.items():
        se = 0.0
        for sec,(cond,val) in sector_bonus.items():
            if s["sector"]==sec and (cond is None or gs.phase==cond):
                se = val
        chg = (random.random()-.5)*2*s["vol"] + ph["stk"] + se + sent
        s["price"] = max(0.5, s["price"]*(1+chg))
        s["hist"].append(round(s["price"],2))
        if len(s["hist"]) > 40: s["hist"].pop(0)

    etf_chg = (random.random()-.48)*.045 + ph["stk"]*.5
    gs.etf_price = max(5, gs.etf_price*(1+etf_chg))
    gs.etf_hist.append(round(gs.etf_price,2))
    if len(gs.etf_hist) > 40: gs.etf_hist.pop(0)


def _random_events(gs: GS):
    events = [
        (0.025, lambda: _ev_fire(gs)),
        (0.020, lambda: _ev_vacancy(gs)),
        (0.015, lambda: _ev_lawsuit(gs)),
        (0.022, lambda: _ev_subsidy(gs)),
        (0.008, lambda: _ev_crash(gs)),
        (0.008, lambda: _ev_rally(gs)),
        (0.016, lambda: _ev_bad_press(gs)),
        (0.016, lambda: _ev_good_press(gs)),
        (0.010, lambda: _ev_tax_audit(gs)),
        (0.018, lambda: _ev_infra(gs)),
        (0.010, lambda: _ev_regulation(gs)),
    ]
    for prob, fn in events:
        if random.random() < prob:
            fn()

def _ev_fire(gs):
    if not gs.props: return
    p = random.choice(gs.props)
    dmg = p["price"]*0.06
    gs.cash -= dmg; p["price"] -= dmg
    gs.add_log(f"Feuer in {p['name']}! -{fmt(dmg)}", "bad")
    gs.add_news("Feuer in der Innenstadt — Immobilienschäden!")

def _ev_vacancy(gs):
    occupied = [p for p in gs.props if not p["vacant"]]
    if not occupied: return
    p = random.choice(occupied)
    tname = TENANT_TYPES[p["tenant"]][0] if p["tenant"] is not None else "Mieter"
    p["tenant"] = None; p["vacant"] = True; p["contract_left"] = 0
    gs.add_log(f"{tname} ausgezogen: {p['name']} jetzt leer", "bad")

def _ev_lawsuit(gs):
    if not gs.comps: return
    c = random.choice(gs.comps)
    pen = c["val"]*0.07
    gs.cash -= pen
    gs.add_log(f"Klage vs {c['name']}: -{fmt(pen)}", "bad")
    gs.add_news("Unternehmen verklagt — Strafzahlung fällig!")

def _ev_subsidy(gs):
    amt = 8_000 + random.random()*45_000
    gs.cash += amt
    gs.add_log(f"Staatliche Förderung: +{fmt(amt)}", "good")

def _ev_crash(gs):
    for s in gs.stock_data.values():
        s["price"] *= 0.80 + random.random()*0.10
    gs._crashed_once = True
    gs.add_log("Marktcrash! Alle Aktien stark gefallen.", "bad")
    gs.add_news("CRASH: Börsenpanik! Alle Kurse eingebrochen.")

def _ev_rally(gs):
    for s in gs.stock_data.values():
        s["price"] *= 1.10 + random.random()*0.10
    gs.add_log("Bullenmarkt! Aktien stark gestiegen.", "good")
    gs.add_news("Börsenrekord! Märkte feiern Allzeithoch.")

def _ev_bad_press(gs):
    gs.reputation = max(0, gs.reputation-10)
    gs.add_log("Schlechte Presse: Ruf -10", "bad")

def _ev_good_press(gs):
    gs.reputation = min(100, gs.reputation+8)
    gs.add_log("Positiver Artikel: Ruf +8", "good")

def _ev_tax_audit(gs):
    amt = gs.cash*0.04
    gs.cash -= amt
    gs.add_log(f"Sondersteuer-Prüfung: -{fmt(amt)}", "bad")

def _ev_infra(gs):
    if not gs.props: return
    p = random.choice(gs.props)
    p["price"] *= 1.10
    gs.add_log(f"Stadtentwicklung: {p['name']} +10%", "good")

def _ev_regulation(gs):
    for c in gs.comps:
        c["profit"]      *= 0.85
        c["base_profit"] *= 0.85
    gs.add_log("Neue Regulierung: Firmengewinne -15%", "bad")
    gs.add_news("Regierung beschließt neue Unternehmensauflagen.")


# ─────────────────────────────────────────────────────
#  NAME-SCREEN
# ─────────────────────────────────────────────────────
class NameScreen:
    def __init__(self):
        self.box     = InputBox(W//2-150, H//2+10, 300, 38, "Dein Name", numeric=False)
        self.btn     = Btn(W//2-70, H//2+62, 140, 38, "Spielen", GREEN, BG, "lg")
        self.load_btn= Btn(W//2-70, H//2+115, 140, 38, "Laden", ACCENT, WHITE, "sm")
        self.slot_btns = []
        self._show_slots = False
        self._slot_infos = []
        self._refresh_slots()

    def _refresh_slots(self):
        self._slot_infos = [get_slot_info(i) for i in range(NUM_SLOTS)]

    def handle(self, ev):
        self.box.handle(ev)
        if self.btn.hit(ev) or (ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN and not self._show_slots):
            return ("new", self.box.text.strip() or "Investor")
        if self.load_btn.hit(ev):
            self._show_slots = not self._show_slots
            self._refresh_slots()
        if self._show_slots and ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i in range(NUM_SLOTS):
                ry = H//2+160 + i*52
                r = pygame.Rect(W//2-250, ry, 500, 46)
                if r.collidepoint(ev.pos) and not self._slot_infos[i]["empty"]:
                    return ("load", i)
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self._show_slots = False
        return None

    def draw(self, surf):
        surf.fill(BG)
        txt(surf,"Business Tycoon Pro","title",GOLD, W//2,H//2-110,"center")
        txt(surf,"by Michael (其米）","md",MUTED, W//2,H//2-72,"center")
        txt(surf,"Wie heißt du?","lg",WHITE, W//2,H//2-20,"center")
        self.box.draw(surf)
        self.btn.update(pygame.mouse.get_pos())
        self.btn.draw(surf)
        self.load_btn.update(pygame.mouse.get_pos())
        self.load_btn.draw(surf)

        # Tastenkürzel-Hinweis
        txt(surf,"F5=Speichern  F9=Laden  F1=Slots","xs",MUTED,W//2,H-30,"center")

        if self._show_slots:
            txt(surf,"Spielstand laden — Slot wählen:","sm",CYAN,W//2,H//2+152,"center")
            for i, info in enumerate(self._slot_infos):
                ry = H//2+168 + i*52
                r  = pygame.Rect(W//2-250, ry, 500, 44)
                if info["empty"]:
                    box(surf, PANEL2, r, 6)
                    txt(surf,f"Slot {i+1}  —  Leer","sm",MUTED,r.centerx,r.centery,"center")
                else:
                    box(surf, PANEL, r, 6)
                    box(surf, ACCENT, r, 6, 1)
                    txt(surf,f"Slot {i+1}  {info['name']}","sm",WHITE,r.x+10,r.y+8)
                    txt(surf,f"{info['month']:02d}.{info['year']}  |  NV: {fmt(info['nw'])}  |  {info['achievements']} Erfolge  |  {info['saved_at']}",
                        "xs",MUTED,r.x+10,r.y+28)


# ─────────────────────────────────────────────────────
#  SPEICHER-MODAL
# ─────────────────────────────────────────────────────
class SaveModal:
    """Overlay zum Speichern/Laden — 6 Slots."""
    def __init__(self, gs: GS, mode="save"):
        self.gs   = gs
        self.mode = mode  # "save" oder "load"
        self.infos = [get_slot_info(i) for i in range(NUM_SLOTS)]
        self.result = None  # "saved", "loaded", "closed"
        self.loaded_gs = None
        self.msg = ""
        self.msg_timer = 0

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.result = "closed"
        if ev.type != pygame.MOUSEBUTTONDOWN or ev.button != 1:
            return
        mx, my = ev.pos
        mw, mh = 580, 440
        bx = (W-mw)//2; by = (H-mh)//2
        # Schließen
        if pygame.Rect(bx+mw-32,by+6,24,24).collidepoint(mx,my):
            self.result = "closed"
            return
        for i in range(NUM_SLOTS):
            ry = by+60 + i*58
            # Slot-Hauptbereich
            if pygame.Rect(bx+10, ry, mw-20, 50).collidepoint(mx,my):
                if self.mode == "save":
                    ok = save_game(self.gs, i)
                    if ok:
                        self.msg = f"✓ In Slot {i+1} gespeichert!"
                        self.msg_timer = 120
                        self.infos = [get_slot_info(j) for j in range(NUM_SLOTS)]
                elif self.mode == "load":
                    loaded = load_game(i)
                    if loaded:
                        self.loaded_gs = loaded
                        self.result = "loaded"
            # Löschen-Button (X) rechts — nur im Save-Modus für belegte Slots
            if self.mode == "save" and not self.infos[i]["empty"]:
                del_r = pygame.Rect(bx+mw-60, ry+12, 44, 28)
                if del_r.collidepoint(mx,my):
                    delete_slot(i)
                    self.infos = [get_slot_info(j) for j in range(NUM_SLOTS)]
                    self.msg = f"Slot {i+1} gelöscht"
                    self.msg_timer = 90

    def update(self):
        if self.msg_timer > 0:
            self.msg_timer -= 1

    def draw(self, surf):
        dim_overlay(surf)
        mw, mh = 580, 440
        bx = (W-mw)//2; by = (H-mh)//2
        box(surf, PANEL, (bx,by,mw,mh), 12)
        box(surf, ACCENT, (bx,by,mw,mh), 12, 1)
        title = "Spielstand speichern" if self.mode=="save" else "Spielstand laden"
        txt(surf, title, "lg", GOLD, bx+16, by+16)
        box(surf, RED, (bx+mw-32,by+6,24,24), 12)
        txt(surf, "X", "sm", WHITE, bx+mw-20, by+18, "center")

        for i, info in enumerate(self.infos):
            ry = by+60 + i*58
            if info["empty"]:
                box(surf, PANEL2, (bx+10,ry,mw-20,50), 7)
                box(surf, BORDER, (bx+10,ry,mw-20,50), 7, 1)
                txt(surf, f"Slot {i+1}  —  Leer", "sm", MUTED, bx+22, ry+16)
                if self.mode=="save":
                    box(surf, GREEN, (bx+mw-120,ry+12,100,28), 6)
                    txt(surf,"Hier speichern","xs",BG,bx+mw-70,ry+26,"center")
            else:
                box(surf, PANEL, (bx+10,ry,mw-20,50), 7)
                box(surf, CYAN if self.mode=="load" else ACCENT, (bx+10,ry,mw-20,50), 7, 1)
                txt(surf, f"Slot {i+1}  —  {info['name']}", "sm", WHITE, bx+22, ry+10)
                txt(surf,
                    f"{info['month']:02d}.{info['year']}  |  {fmt(info['nw'])}  |  {info['achievements']} Erfolge  |  {info['saved_at']}",
                    "xs", MUTED, bx+22, ry+30)
                if self.mode=="save":
                    box(surf, ACCENT, (bx+mw-170,ry+12,100,28), 6)
                    txt(surf,"Überschreiben","xs",WHITE,bx+mw-120,ry+26,"center")
                    box(surf, RED, (bx+mw-60,ry+12,44,28), 6)
                    txt(surf,"Löschen","xs",WHITE,bx+mw-38,ry+26,"center")
                else:
                    box(surf, GREEN, (bx+mw-120,ry+12,100,28), 6)
                    txt(surf,"Laden","sm",BG,bx+mw-70,ry+26,"center")

        # Meldung
        if self.msg_timer > 0:
            alpha = min(255, self.msg_timer * 3)
            msg_col = tuple(list(GREEN)+[alpha]) if "✓" in self.msg else tuple(list(YELLOW)+[alpha])
            txt(surf, self.msg, "md", GREEN if "✓" in self.msg else YELLOW,
                bx+mw//2, by+mh-24, "center")

        txt(surf, "ESC = Schließen  |  F5 = Schnellspeichern (Slot 0)", "xs", MUTED,
            bx+mw//2, by+mh-8, "center")


# ─────────────────────────────────────────────────────
#  HAUPTSPIEL
# ─────────────────────────────────────────────────────
TABS = ["Dashboard","Wirtschaft","Aktien","Erfolge","Log"]

class GameScreen:
    def __init__(self, gs: GS):
        self.gs        = gs
        self.tab       = 0
        self.speed     = 2000
        self.paused    = False
        self.last_tick = pygame.time.get_ticks()
        self.modal     = None
        self._save_modal = None
        self._news_x   = float(W)
        self._ach_popup= None
        self._inputs   = {}
        self._scroll   = 0
        self._save_feedback = ("", 0)  # (text, timer)
        self._ach_filter = "alle"  # "alle"/"leicht"/"mittel"/"schwer"/"extrem"/"legendaer"/"done"/"undone"

    def maybe_tick(self):
        if self.paused or self.modal or self._save_modal: return None
        now = pygame.time.get_ticks()
        if now - self.last_tick >= self.speed:
            self.last_tick = now
            result = tick(self.gs)
            self._check_achievements()
            if result == "bankrott":
                return "bankrott"
        return None

    def _check_achievements(self):
        gs = self.gs
        for aid, title, diff, desc, cond in ACHIEVEMENTS:
            if aid not in gs.achiev_done and cond(gs):
                gs.achiev_done.add(aid)
                gs.add_log(f"Erfolg ({diff.upper()}): {title}", "good")
                self._ach_popup = (title, desc, diff, pygame.time.get_ticks())

    def quicksave(self):
        ok = save_game(self.gs, 0)
        self._save_feedback = ("✓ Schnellgespeichert in Slot 1!" if ok else "✗ Speicherfehler!", 120)

    def open_save_modal(self):
        if not self.modal:
            self._save_modal = SaveModal(self.gs, "save")

    def open_load_modal(self):
        if not self.modal:
            self._save_modal = SaveModal(self.gs, "load")

    # ══ EVENTS ══
    def handle(self, ev):
        gs = self.gs
        for ib in self._inputs.values():
            ib.handle(ev)

        # Speicher-Modal hat Vorrang
        if self._save_modal:
            self._save_modal.handle(ev)
            if self._save_modal.result == "closed":
                self._save_modal = None
            elif self._save_modal.result == "loaded":
                new_gs = self._save_modal.loaded_gs
                self._save_modal = None
                return ("load", new_gs)
            return None

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self._close_modal()
            if ev.key == pygame.K_SPACE and not self.modal:
                self.paused = not self.paused
            if ev.key == pygame.K_F5:
                self.quicksave()
            if ev.key == pygame.K_F1:
                self.open_save_modal()
            if ev.key == pygame.K_F9:
                self.open_load_modal()

        if ev.type != pygame.MOUSEBUTTONDOWN or ev.button != 1:
            return None
        mx, my = ev.pos

        if self.modal:
            return self._handle_modal_click(mx, my)

        return self._handle_main_click(mx, my)

    def _handle_main_click(self, mx, my):
        gs = self.gs
        # Speed-Buttons
        for i, (ms, lbl) in enumerate([(2000,"1x"),(800,"3x"),(300,"10x")]):
            r = pygame.Rect(W-215+i*44, 9, 38, 26)
            if r.collidepoint(mx,my):
                self.speed = ms; return None
        # Pause
        if pygame.Rect(W-123,9,88,26).collidepoint(mx,my):
            self.paused = not self.paused; return None
        # Speichern-Button in Topbar
        if pygame.Rect(W-38,9,32,26).collidepoint(mx,my):
            self.open_save_modal(); return None

        # Tabs
        tx = 192
        for i, name in enumerate(TABS):
            tw = F["sm"].size(name)[0]+22
            if pygame.Rect(tx,46,tw,32).collidepoint(mx,my):
                self.tab = i; return None
            tx += tw+2

        # Sidebar
        sb_clicks = {
            "buy_prop": self._open_buy_prop, "sell_prop": self._open_sell_prop,
            "upg_prop": self._open_upg_prop, "rent_prop": self._open_rent_prop,
            "buy_comp": self._open_buy_comp, "sell_comp": self._open_sell_comp,
            "upg_comp": self._open_upg_comp,
            "loan":     self._open_loan,     "repay":     self._open_repay,
            "savings":  self._open_savings,  "buy_etf":   self._open_buy_etf,
        }
        for key, ry, rh in self._sidebar_rects():
            if pygame.Rect(4, ry, 182, rh).collidepoint(mx,my):
                if key in sb_clicks: sb_clicks[key]()
                return None

        # Achievement-Filter (im Erfolge-Tab)
        if self.tab == 3:
            self._handle_ach_filter_click(mx, my)

        if self.tab == 2:
            self._handle_stock_click(mx, my)

        return None

    # ── Achievement-Filter ──
    def _handle_ach_filter_click(self, mx, my):
        filters = ["alle","leicht","mittel","schwer","extrem","legendaer","done","undone"]
        labels  = ["Alle","Leicht","Mittel","Schwer","Extrem","Legendär","Erreicht","Offen"]
        bx = 192+10; by = 76+36; bw = 78; bh = 22; gap = 4
        for i,(f,l) in enumerate(zip(filters,labels)):
            r = pygame.Rect(bx+i*(bw+gap), by, bw, bh)
            if r.collidepoint(mx,my):
                self._ach_filter = f

    # ─────────────────────────────────────────────────
    #  MODAL ÖFFNEN
    # ─────────────────────────────────────────────────
    def _open_buy_prop(self):   self._inputs={}; self.modal={"type":"buy_prop"};  self._scroll=0
    def _open_sell_prop(self):  self._inputs={}; self.modal={"type":"sell_prop"}; self._scroll=0
    def _open_upg_prop(self):   self._inputs={}; self.modal={"type":"upg_prop"};  self._scroll=0
    def _open_rent_prop(self):  self._inputs={}; self.modal={"type":"rent_prop"}; self._scroll=0
    def _open_buy_comp(self):   self._inputs={}; self.modal={"type":"buy_comp"};  self._scroll=0
    def _open_sell_comp(self):  self._inputs={}; self.modal={"type":"sell_comp"}; self._scroll=0
    def _open_upg_comp(self):   self._inputs={}; self.modal={"type":"upg_comp"};  self._scroll=0

    def _open_loan(self):
        self._inputs={"amount":InputBox(0,0,220,34,"Betrag in €")}
        self.modal={"type":"loan"}

    def _open_repay(self):
        self._inputs={"amount":InputBox(0,0,220,34,"Betrag in €")}
        self.modal={"type":"repay"}

    def _open_savings(self):
        self._inputs={"amount":InputBox(0,0,220,34,"Betrag einzahlen")}
        self.modal={"type":"savings"}

    def _open_buy_stock(self, sid):
        self._inputs={"qty":InputBox(0,0,180,34,"Anzahl Aktien")}
        self.modal={"type":"buy_stock","sid":sid}

    def _open_sell_stock(self, sid):
        self._inputs={"qty":InputBox(0,0,180,34,"Anzahl verkaufen")}
        self.modal={"type":"sell_stock","sid":sid}

    def _open_buy_etf(self):
        self._inputs={"qty":InputBox(0,0,180,34,"Anzahl Anteile")}
        self.modal={"type":"buy_etf"}

    def _close_modal(self):
        self.modal=None; self._inputs={}

    # ─────────────────────────────────────────────────
    #  MODAL CLICK-HANDLER
    # ─────────────────────────────────────────────────
    def _handle_modal_click(self, mx, my):
        mt = self.modal.get("type","")
        mw, mh = 660, 520
        bx = (W-mw)//2; by = (H-mh)//2
        if pygame.Rect(bx+mw-32,by+6,24,24).collidepoint(mx,my):
            self._close_modal(); return None
        gs = self.gs

        if mt == "buy_prop":
            row_h=72; view_off=55
            view = pygame.Rect(bx, by+view_off, mw, mh-view_off-10)
            for i,row in enumerate(PROP_CATALOG):
                ry = by+view_off + i*row_h - self._scroll
                if ry+row_h<by+view_off or ry>by+mh-10: continue
                if pygame.Rect(bx+mw-110,ry+20,90,30).collidepoint(mx,my):
                    price=float(row[3])
                    if gs.cash>=price:
                        gs.cash-=price; gs.props.append(make_prop(row))
                        gs._total_props_bought+=1
                        gs.add_log(f"Immobilie gekauft: {row[1]} ({fmt(price)})", "good")
                        self._check_achievements()
                    self._close_modal(); return None

        elif mt == "sell_prop":
            row_h=64
            for i,p in enumerate(gs.props):
                ry=by+58+i*row_h-self._scroll
                if ry+row_h<by+50 or ry>by+mh-20: continue
                if pygame.Rect(bx+mw-110,ry+16,90,30).collidepoint(mx,my):
                    sv=p["price"]*0.94; gs.cash+=sv; gs.props.pop(i)
                    gs.add_log(f"Immobilie verkauft: {p['name']} +{fmt(sv)}", "info")
                    self._close_modal(); return None

        elif mt == "upg_prop":
            row_h=72
            for i,p in enumerate(gs.props):
                ry=by+58+i*row_h-self._scroll
                if ry+row_h<by+50 or ry>by+mh-20: continue
                cost=p["price"]*0.12; maxed=p["level"]>=p["lvl_max"]
                if not maxed and pygame.Rect(bx+mw-110,ry+20,90,30).collidepoint(mx,my):
                    if gs.cash>=cost:
                        gs.cash-=cost; p["level"]+=1
                        p["price"]*=1.08; p["base_rent"]*=1.15
                        p["rent"]*=1.15; p["maint"]*=1.06
                        gs._total_upgrades+=1
                        gs.add_log(f"Renoviert: {p['name']} Lvl {p['level']}", "good")
                        self._check_achievements()
                    self._close_modal(); return None

        elif mt == "rent_prop":
            row_h=100
            for i,p in enumerate(gs.props):
                ry=by+58+i*row_h-self._scroll
                if ry+row_h<by+50 or ry>by+mh-20: continue
                if p["vacant"] and not p["listed"]:
                    if pygame.Rect(bx+mw-120,ry+20,100,28).collidepoint(mx,my):
                        p["listed"]=True
                        gs.add_log(f"{p['name']} auf Mietmarkt angeboten","info")
                        self._close_modal(); return None
                elif not p["vacant"]:
                    if pygame.Rect(bx+mw-120,ry+20,100,28).collidepoint(mx,my):
                        tname=TENANT_TYPES[p["tenant"]][0] if p["tenant"] is not None else "Mieter"
                        p["tenant"]=None; p["vacant"]=True; p["listed"]=False; p["contract_left"]=0
                        penalty=p["rent"]*2; gs.cash-=penalty
                        gs.add_log(f"{tname} rausgekündigt: -{fmt(penalty)} Strafe","bad")
                        self._close_modal(); return None
                elif p["vacant"] and p["listed"]:
                    if pygame.Rect(bx+mw-120,ry+20,100,28).collidepoint(mx,my):
                        p["listed"]=False
                        gs.add_log(f"{p['name']} vom Mietmarkt genommen","info")
                        self._close_modal(); return None

        elif mt == "buy_comp":
            row_h=72
            for i,row in enumerate(COMP_CATALOG):
                ry=by+60+i*row_h-self._scroll
                if ry+row_h<by+55 or ry>by+mh-10: continue
                if pygame.Rect(bx+mw-110,ry+20,90,30).collidepoint(mx,my):
                    price=float(row[3])
                    if gs.cash>=price:
                        gs.cash-=price; gs.comps.append(make_comp(row))
                        gs._total_comps_bought+=1
                        gs.add_log(f"Firma gegründet: {row[1]} ({fmt(price)})", "good")
                        self._check_achievements()
                    self._close_modal(); return None

        elif mt == "sell_comp":
            row_h=64
            for i,c in enumerate(gs.comps):
                ry=by+58+i*row_h-self._scroll
                if ry+row_h<by+50 or ry>by+mh-20: continue
                if pygame.Rect(bx+mw-110,ry+16,90,30).collidepoint(mx,my):
                    sv=c["val"]*0.88; gs.cash+=sv; gs.comps.pop(i)
                    gs.add_log(f"Firma verkauft: {c['name']} +{fmt(sv)}","info")
                    self._close_modal(); return None

        elif mt == "upg_comp":
            row_h=72
            for i,c in enumerate(gs.comps):
                ry=by+58+i*row_h-self._scroll
                if ry+row_h<by+50 or ry>by+mh-20: continue
                cost=c["val"]*0.15; maxed=c["level"]>=c["lvl_max"]
                if not maxed and pygame.Rect(bx+mw-110,ry+20,90,30).collidepoint(mx,my):
                    if gs.cash>=cost:
                        gs.cash-=cost; c["level"]+=1
                        c["val"]*=1.12; c["base_profit"]*=1.22
                        c["profit"]=c["base_profit"]; c["maint"]*=1.08
                        gs._total_upgrades+=1
                        gs.add_log(f"Firma erweitert: {c['name']} Lvl {c['level']}","good")
                        self._check_achievements()
                    self._close_modal(); return None

        elif mt == "loan":
            self._inputs["amount"].rect = pygame.Rect(bx+30,by+128,220,34)
            if pygame.Rect(bx+260,by+128,120,34).collidepoint(mx,my):
                amt=self._inputs["amount"].val()
                max_l=max(0,gs.net_worth()*0.6-gs.loan)
                if 0<amt<=max_l:
                    gs.cash+=amt; gs.loan+=amt
                    gs.add_log(f"Kredit aufgenommen: +{fmt(amt)}","warn")
                self._close_modal(); return None

        elif mt == "repay":
            self._inputs["amount"].rect = pygame.Rect(bx+30,by+128,220,34)
            if pygame.Rect(bx+260,by+128,120,34).collidepoint(mx,my):
                amt=min(self._inputs["amount"].val(),gs.cash,gs.loan)
                if amt>0:
                    gs.cash-=amt; gs.loan=max(0,gs.loan-amt)
                    gs._total_loan_repaid+=amt
                    gs.add_log(f"Kredit getilgt: -{fmt(amt)}","good")
                    self._check_achievements()
                self._close_modal(); return None
            if pygame.Rect(bx+30,by+180,160,34).collidepoint(mx,my):
                amt=min(gs.cash,gs.loan)
                if amt>0:
                    gs.cash-=amt; gs.loan=max(0,gs.loan-amt)
                    gs._total_loan_repaid+=amt
                    gs.add_log(f"Alle Schulden getilgt: -{fmt(amt)}","good")
                    self._check_achievements()
                self._close_modal(); return None

        elif mt == "savings":
            self._inputs["amount"].rect = pygame.Rect(bx+30,by+128,220,34)
            if pygame.Rect(bx+260,by+128,120,34).collidepoint(mx,my):
                amt=self._inputs["amount"].val()
                if 0<amt<=gs.cash:
                    gs.cash-=amt; gs.savings+=amt
                    gs.add_log(f"Festgeld eingelegt: {fmt(amt)}","info")
                    self._check_achievements()
                self._close_modal(); return None
            if pygame.Rect(bx+30,by+180,160,34).collidepoint(mx,my):
                if gs.savings>0:
                    gs.cash+=gs.savings
                    gs.add_log(f"Festgeld ausgezahlt: {fmt(gs.savings)}","info")
                    gs.savings=0
                self._close_modal(); return None

        elif mt == "buy_stock":
            sid=self.modal["sid"]
            self._inputs["qty"].rect = pygame.Rect(bx+30,by+130,180,34)
            if pygame.Rect(bx+220,by+130,110,34).collidepoint(mx,my):
                qty=int(self._inputs["qty"].val())
                cost=qty*gs.stock_data[sid]["price"]
                if qty>0 and gs.cash>=cost:
                    gs.cash-=cost
                    gs.stocks[sid]=gs.stocks.get(sid,0.0)+qty
                    gs._stock_trades+=1
                    gs.add_log(f"Aktie gekauft: {qty}x {gs.stock_data[sid]['name']}","good")
                    self._check_achievements()
                self._close_modal(); return None

        elif mt == "sell_stock":
            sid=self.modal["sid"]
            self._inputs["qty"].rect = pygame.Rect(bx+30,by+130,180,34)
            if pygame.Rect(bx+220,by+130,110,34).collidepoint(mx,my):
                qty=int(self._inputs["qty"].val())
                owned=gs.stocks.get(sid,0.0)
                qty=min(qty,int(owned))
                if qty>0:
                    gs.cash+=qty*gs.stock_data[sid]["price"]
                    gs.stocks[sid]=owned-qty
                    gs._stock_trades+=1
                    gs.add_log(f"Aktie verkauft: {qty}x {gs.stock_data[sid]['name']}","info")
                self._close_modal(); return None
            if pygame.Rect(bx+30,by+180,160,34).collidepoint(mx,my):
                owned=gs.stocks.get(sid,0.0)
                if owned>0:
                    gs.cash+=owned*gs.stock_data[sid]["price"]
                    gs.stocks[sid]=0
                    gs._stock_trades+=1
                self._close_modal(); return None

        elif mt == "buy_etf":
            self._inputs["qty"].rect = pygame.Rect(bx+30,by+130,180,34)
            if pygame.Rect(bx+220,by+130,110,34).collidepoint(mx,my):
                qty=self._inputs["qty"].val()
                cost=qty*gs.etf_price
                if qty>0 and gs.cash>=cost:
                    gs.cash-=cost; gs.etf+=qty
                    gs.add_log(f"ETF gekauft: {qty:.1f} Anteile ({fmt(cost)})","good")
                    self._check_achievements()
                self._close_modal(); return None
            if pygame.Rect(bx+30,by+180,160,34).collidepoint(mx,my):
                if gs.etf>0:
                    gs.cash+=gs.etf*gs.etf_price
                    gs.add_log(f"Alle ETF-Anteile verkauft","info")
                    gs.etf=0
                self._close_modal(); return None

        return None

    def _handle_stock_click(self, mx, my):
        gs=self.gs; x=188; y=76; pad=10
        col_w=(W-x-pad*3)//2; row_h=62
        sids=list(gs.stock_data.keys())
        for i,sid in enumerate(sids):
            rx=x+pad+(i%2)*(col_w+pad)
            ry=y+18+(i//2)*row_h
            r=pygame.Rect(rx,ry,col_w,row_h-4)
            if r.collidepoint(mx,my):
                if mx<rx+col_w*0.65: self._open_buy_stock(sid)
                else: self._open_sell_stock(sid)
                return
        n_rows=(len(sids)//2)+(1 if len(sids)%2 else 0)
        ey=y+18+n_rows*row_h+8
        if pygame.Rect(x+pad,ey,W-x-pad*2,70).collidepoint(mx,my):
            self._open_buy_etf()

    def handle_scroll(self, ev):
        if ev.type == pygame.MOUSEWHEEL and self.modal:
            self._scroll = max(0, self._scroll - ev.y*30)

    # ══ ZEICHNEN ══════════════════════════════════════
    def draw(self):
        screen.fill(BG)
        self._draw_topbar()
        self._draw_sidebar()
        self._draw_tabs()
        self._draw_content()
        self._draw_newsbar()

        # Save-Modal über allem
        if self._save_modal:
            self._save_modal.update()
            self._save_modal.draw(screen)
        elif self.modal:
            dim_overlay(screen)
            self._draw_modal()

        if self._ach_popup:
            self._draw_ach_popup()

        # Save-Feedback
        if self._save_feedback[1] > 0:
            msg, timer = self._save_feedback
            self._save_feedback = (msg, timer-1)
            alpha = min(255, timer*3)
            col = GREEN if "✓" in msg else RED
            sf = F["md"].render(msg, True, col)
            screen.blit(sf, sf.get_rect(center=(W//2, H-40)))

    # ── TOPBAR ──
    def _draw_topbar(self):
        gs=self.gs
        box(screen,PANEL,(0,0,W,44)); line(screen,BORDER,(0,44),(W,44))
        txt(screen,"Business Tycoon Pro","lg",GOLD,10,22,"midleft")

        stats = [
            ("Bargeld",fmt(gs.cash),gs.cash>=0),
            ("Nettoverm.",fmt(gs.net_worth()),True),
            (f"{gs.month:02d}.{gs.year}","",True),
            ("Schulden",fmt(gs.loan),gs.loan==0),
            ("Ruf",str(int(gs.reputation)),gs.reputation>=50),
        ]
        x=220
        for label,val,good in stats:
            if not val:
                txt(screen,label,"sm",CYAN,x+50,22,"center"); x+=100; continue
            box(screen,PANEL2,(x,6,120,32),16)
            txt(screen,f"{label}:","xs",MUTED,x+8,22,"midleft")
            txt(screen,val,"sm",GREEN if good else RED,x+112,22,"midright")
            x+=128

        # Speed
        for i,(ms,lbl) in enumerate([(2000,"1x"),(800,"3x"),(300,"10x")]):
            r=pygame.Rect(W-215+i*44,9,38,26)
            c=ACCENT if self.speed==ms else PANEL2
            box(screen,c,r,6); box(screen,BORDER,r,6,1)
            txt(screen,lbl,"sm",WHITE,r.centerx,r.centery,"center")
        # Pause
        pr=pygame.Rect(W-123,9,88,26)
        box(screen,GREEN if not self.paused else YELLOW,pr,13)
        txt(screen,"Pause" if not self.paused else "Weiter","sm",BG,pr.centerx,pr.centery,"center")
        # Speichern-Icon
        sr=pygame.Rect(W-38,9,32,26)
        box(screen,PURPLE,sr,6)
        txt(screen,"💾","sm",WHITE,sr.centerx,sr.centery,"center")

    # ── SIDEBAR ──
    def _sidebar_rects(self):
        entries = [
            ("__sec_immo__","Immobilien"),
            ("buy_prop","  Immo kaufen"),("sell_prop","  Immo verkaufen"),
            ("upg_prop","  Renovieren"),("rent_prop","  Vermieten"),
            ("__sec_comp__","Unternehmen"),
            ("buy_comp","  Firma gründen"),("sell_comp","  Firma verkaufen"),
            ("upg_comp","  Firma erweitern"),
            ("__sec_fin__","Finanzen"),
            ("loan","  Kredit aufnehmen"),("repay","  Kredit tilgen"),
            ("savings","  Festgeld"),("buy_etf","  ETF kaufen"),
        ]
        y=52; rects=[]
        for key,label in entries:
            if key.startswith("__"): rects.append((key,y,18)); y+=20
            else: rects.append((key,y,28)); y+=30
        return rects

    def _draw_sidebar(self):
        gs=self.gs
        box(screen,PANEL,(0,44,188,H-44-20)); line(screen,BORDER,(188,44),(188,H-20))
        entries = [
            ("__sec_immo__","Immobilien"),
            ("buy_prop","  Immo kaufen"),("sell_prop","  Immo verkaufen"),
            ("upg_prop","  Renovieren"),("rent_prop","  Vermieten"),
            ("__sec_comp__","Unternehmen"),
            ("buy_comp","  Firma gründen"),("sell_comp","  Firma verkaufen"),
            ("upg_comp","  Firma erweitern"),
            ("__sec_fin__","Finanzen"),
            ("loan","  Kredit aufnehmen"),("repay","  Kredit tilgen"),
            ("savings","  Festgeld"),("buy_etf","  ETF kaufen"),
        ]
        for key,ry,rh in self._sidebar_rects():
            label=next(l for k,l in entries if k==key)
            if key.startswith("__"):
                txt(screen,label.upper(),"xs",MUTED,10,ry+2)
            else:
                hi=(key=="rent_prop" and any(p["vacant"] for p in gs.props))
                bg=(60,40,15) if hi else PANEL2
                box(screen,bg,(4,ry,182,rh),5)
                if hi: box(screen,YELLOW,(4,ry,182,rh),5,1)
                txt(screen,label,"sm",YELLOW if hi else WHITE,12,ry+rh//2,"midleft")
        # Speichern/Laden Hinweis ganz unten
        txt(screen,"F5=Speichern","xs",MUTED,10,H-64)
        txt(screen,"F9=Laden","xs",MUTED,10,H-52)
        txt(screen,"F1=Slots","xs",MUTED,10,H-40)
        txt(screen,f"Erfolge: {len(gs.achiev_done)}/{len(ACHIEVEMENTS)}","xs",GOLD,10,H-28)

    # ── TABS ──
    def _draw_tabs(self):
        box(screen,PANEL,(188,44,W-188,32)); line(screen,BORDER,(188,76),(W,76))
        tx=194
        for i,name in enumerate(TABS):
            tw=F["sm"].size(name)[0]+22
            active=self.tab==i
            if active:
                box(screen,ACCENT,(tx,74,tw,2),0)
                txt(screen,name,"sm",ACCENT,tx+tw//2,60,"center")
            else:
                txt(screen,name,"sm",MUTED,tx+tw//2,60,"center")
            tx+=tw+2

    # ── CONTENT ──
    def _draw_content(self):
        x,y,w,h=188,76,W-188,H-76-20
        {0:self._tab_dashboard,1:self._tab_economy,2:self._tab_stocks,
         3:self._tab_achievements,4:self._tab_log}.get(self.tab,self._tab_dashboard)(x,y,w,h)

    # ── TAB: DASHBOARD ──
    def _tab_dashboard(self,x,y,w,h):
        gs=self.gs; pad=10
        cw=(w-pad*4)//3; ch2=90
        tiles=[
            ("Bargeld",fmt(gs.cash),gs.cash>=0),
            ("Nettovermögen",fmt(gs.net_worth()),True),
            ("Immobilien",f"{len(gs.props)} Objekte",True),
            ("Unternehmen",f"{len(gs.comps)} Firmen",True),
            ("Monat. Einnahmen",fmt(gs.monthly_income()),True),
            ("Monat. Ausgaben",fmt(gs.monthly_expenses()),False),
        ]
        for i,(label,val,good) in enumerate(tiles):
            row,ci=divmod(i,3)
            tx2=x+pad+ci*(cw+pad); ty2=y+pad+row*(ch2+pad)
            box(screen,PANEL2,(tx2,ty2,cw,ch2),8)
            box(screen,BORDER,(tx2,ty2,cw,ch2),8,1)
            txt(screen,label,"xs",MUTED,tx2+10,ty2+12)
            txt(screen,val,"lg",GREEN if good else RED,tx2+10,ty2+42)

        cy3=y+pad+2*(ch2+pad)+8; ch3=h-2*(ch2+pad)-pad*3-8
        if gs.props:
            bar_h=28
            box(screen,PANEL2,(x+pad,cy3,w-pad*2,bar_h),6)
            box(screen,BORDER,(x+pad,cy3,w-pad*2,bar_h),6,1)
            txt(screen,"Immobilien:","xs",MUTED,x+pad+8,cy3+14,"midleft")
            px2=x+pad+90
            for p in gs.props:
                pw2=min(120,(w-pad*2-100)//len(gs.props)-4)
                if p["vacant"] and not p["listed"]: col2,status2=RED,"LEER"
                elif p["vacant"] and p["listed"]: col2,status2=YELLOW,"Suche..."
                else:
                    ti=p.get("tenant"); col2=GREEN
                    status2=TENANT_TYPES[ti][0][:8] if ti is not None else "Vermietet"
                box(screen,col2,(px2,cy3+4,pw2,20),4)
                txt(screen,p["name"][:7],"xs",BG,px2+4,cy3+14,"midleft")
                px2+=pw2+4
            cy3+=bar_h+6; ch3-=bar_h+6
        if ch3>60 and len(gs.nw_hist)>=2:
            box(screen,PANEL2,(x+pad,cy3,w-pad*2,ch3),8)
            box(screen,BORDER,(x+pad,cy3,w-pad*2,ch3),8,1)
            txt(screen,"Nettovermögen (24 Monate)","xs",MUTED,x+pad+10,cy3+8)
            sparkline(screen,gs.nw_hist,x+pad+10,cy3+24,w-pad*2-20,ch3-36,CYAN)
            if len(gs.cf_hist)>=2:
                bary=cy3+ch3-ch3//3-8; barh=ch3//3
                bw2=max(2,(w-pad*2-20)//max(1,len(gs.cf_hist)))
                mn2,mx2=min(gs.cf_hist),max(gs.cf_hist)
                rng=mx2-mn2 if mx2!=mn2 else 1
                for ii,cf in enumerate(gs.cf_hist):
                    bx2=x+pad+10+ii*bw2; norm=(cf-mn2)/rng
                    bh2=max(1,int(norm*barh)); c=GREEN if cf>=0 else RED
                    screen.fill(c,pygame.Rect(bx2,bary-int((cf/rng)*barh),bw2-1,max(1,abs(int((cf/rng)*barh)))))
                txt(screen,"Monatl. Cashflow","xs",MUTED,x+pad+10,bary-12)

    # ── TAB: WIRTSCHAFT ──
    def _tab_economy(self,x,y,w,h):
        gs=self.gs; ph=PHASES[gs.phase]; pad=12
        box(screen,PANEL2,(x+pad,y+pad,w-pad*2,72),8)
        pygame.draw.rect(screen,ph["col"],(x+pad,y+pad,5,72),border_radius=2)
        txt(screen,"Aktuelle Wirtschaftsphase","xs",MUTED,x+pad+14,y+pad+10)
        txt(screen,ph["label"],"xl",ph["col"],x+pad+14,y+pad+36)
        txt(screen,f"Noch ca. {gs.phase_dur} Monate","xs",MUTED,x+pad+14,y+pad+60)

        iy=y+pad+80
        indics=[
            ("Leitzins",f"{gs.base_rate:.2f}%",gs.base_rate<6),
            ("BIP-Wachstum",f"{gs.gdp:.1f}%",gs.gdp>0),
            ("Arbeitslosigkeit",f"{gs.unemp:.1f}%",gs.unemp<8),
            ("Marktstimmung",f"{int(gs.sentiment)}/100",gs.sentiment>50),
            ("Inflation",f"{gs.inflation*12*100:.1f}% pa",gs.inflation*12<0.03),
            ("Kreditrate",f"{gs.loan_rate*12*100:.2f}% pa",True),
        ]
        iw2=(w-pad*4)//3; ih2=58
        for i,(label,val,good) in enumerate(indics):
            row,ci=divmod(i,3)
            ix2=x+pad+ci*(iw2+pad); iy2=iy+row*(ih2+8)
            box(screen,PANEL2,(ix2,iy2,iw2,ih2),6); box(screen,BORDER,(ix2,iy2,iw2,ih2),6,1)
            txt(screen,label,"xs",MUTED,ix2+8,iy2+10)
            txt(screen,val,"md",GREEN if good else RED,ix2+8,iy2+32)

        py2=iy+2*(ih2+8)+16
        txt(screen,"Alle Wirtschaftsphasen","xs",MUTED,x+pad,py2-14)
        pw2=(w-pad*2-40)//6
        for i,(pname,pd) in enumerate(PHASES.items()):
            px2=x+pad+i*(pw2+8); active=gs.phase==pname
            seen=pname in gs._all_phases_seen
            bg=pd["col"] if active else (PANEL2 if not seen else (25,35,50))
            box(screen,bg,(px2,py2,pw2,40),6)
            box(screen,pd["col"],(px2,py2,pw2,40),6,2 if active else 1)
            c=BG if active else pd["col"]
            txt(screen,pd["label"][:8],"xs",c,px2+pw2//2,py2+20,"center")
            if seen and not active:
                txt(screen,"✓","xs",TEAL,px2+pw2//2,py2+34,"center")

        tips={"BOOM":"Aktien kaufen! Firmengewinne steigen.",
              "STABLE":"Stabile Phase — ideal für Schuldenabbau.",
              "RECESSION":"Vorsicht! ETFs sicherer als Einzelaktien.",
              "DEPRESSION":"Bargeld halten. Kein unnötiges Risiko!",
              "STAGFLATION":"Sachwerte (Immobilien) schützen vor Inflation.",
              "HYPERINFLATION":"Immobilien kaufen! Bargeld verliert rasant."}
        ty2=py2+52
        if ty2+36<y+h:
            tip=tips.get(gs.phase,"")
            box(screen,PANEL2,(x+pad,ty2,w-pad*2,34),6)
            box(screen,YELLOW,(x+pad,ty2,w-pad*2,34),6,1)
            txt(screen,f"Tipp: {tip}","sm",YELLOW,x+pad+10,ty2+17,"midleft",w-pad*2-20)

    # ── TAB: AKTIEN ──
    def _tab_stocks(self,x,y,w,h):
        gs=self.gs; pad=10; col_w=(w-pad*3)//2; row_h=62
        txt(screen,"Klick links: Kaufen  |  Klick rechts: Verkaufen","xs",MUTED,x+pad,y+4)
        sids=list(gs.stock_data.keys())
        for i,sid in enumerate(sids):
            s=gs.stock_data[sid]; rx=x+pad+(i%2)*(col_w+pad); ry=y+18+(i//2)*row_h
            qty=gs.stocks.get(sid,0)
            box(screen,PANEL2,(rx,ry,col_w,row_h-4),6)
            box(screen,BORDER,(rx,ry,col_w,row_h-4),6,1)
            pchg=(s["hist"][-1]/s["hist"][-2]-1)*100 if len(s["hist"])>=2 else 0
            txt(screen,s["name"],"sm",WHITE,rx+8,ry+10)
            txt(screen,fmt(s["price"]),"sm",CYAN,rx+8,ry+30)
            txt(screen,f"{pchg:+.1f}%","xs",GREEN if pchg>=0 else RED,rx+8,ry+48)
            txt(screen,f"Div: {s['div']*100:.1f}%","xs",MUTED,rx+col_w//2,ry+10)
            if qty>0:
                txt(screen,f"{qty:.0f} Stk = {fmt(qty*s['price'])}","xs",PURPLE,rx+col_w//2,ry+30)
            if len(s["hist"])>=2:
                sparkline(screen,s["hist"],rx+col_w-80,ry+4,72,50)

        n_rows=(len(sids)//2)+(1 if len(sids)%2 else 0)
        ey=y+18+n_rows*row_h+8
        if ey+70<y+h:
            ev2=gs.etf*gs.etf_price
            box(screen,PANEL2,(x+pad,ey,w-pad*2,68),8)
            box(screen,ACCENT,(x+pad,ey,w-pad*2,68),8,1)
            txt(screen,"Welt-ETF","lg",GOLD,x+pad+10,ey+12)
            txt(screen,fmt(gs.etf_price),"md",CYAN,x+pad+10,ey+36)
            txt(screen,"Div: 2.4% pa | Geringes Risiko","xs",MUTED,x+pad+10,ey+56)
            if gs.etf>0:
                txt(screen,f"{gs.etf:.1f} Anteile = {fmt(ev2)}","sm",PURPLE,x+pad+240,ey+32)
            if len(gs.etf_hist)>=2:
                sparkline(screen,gs.etf_hist,x+w-pad-120,ey+4,112,60)

    # ── TAB: ERFOLGE ──
    def _tab_achievements(self,x,y,w,h):
        gs=self.gs
        n=len(gs.achiev_done); total=len(ACHIEVEMENTS)
        pct=n/total if total else 0

        # Gesamtfortschritt
        txt(screen,f"Erfolge  {n}/{total}","lg",GOLD,x+12,y+8)
        progress_bar(screen,x+160,y+14,w-200,14,pct,GOLD)
        txt(screen,f"{int(pct*100)}%","xs",GOLD,x+w-30,y+14)

        # Filter-Buttons
        filters=["alle","leicht","mittel","schwer","extrem","legendaer","done","undone"]
        labels =["Alle","Leicht","Mittel","Schwer","Extrem","Legendär","Erreicht","Offen"]
        fx=x+10; fy=y+36; bw=78; bh=22; gap=3
        for i,(f,l) in enumerate(zip(filters,labels)):
            r=pygame.Rect(fx+i*(bw+gap),fy,bw,bh)
            active=self._ach_filter==f
            col=DIFF_COLORS.get(f,ACCENT) if not active else WHITE
            bg=DIFF_COLORS.get(f,(70,70,120)) if active else PANEL2
            box(screen,bg,r,5)
            if active: box(screen,WHITE,r,5,1)
            txt(screen,l,"xs",WHITE if active else MUTED,r.centerx,r.centery,"center")

        # Achievements filtern
        def passes(aid,title,diff,desc,cond):
            f=self._ach_filter
            earned=aid in gs.achiev_done
            if f=="alle": return True
            if f=="done": return earned
            if f=="undone": return not earned
            return f==diff

        filtered=[(aid,title,diff,desc,cond) for aid,title,diff,desc,cond in ACHIEVEMENTS if passes(aid,title,diff,desc,cond)]

        # Grid: 2 Spalten
        row_h=52; col=2
        cw2=(w-30)//col; start_y=y+66
        for i,(aid,title,diff,desc,cond) in enumerate(filtered):
            ci=i%col; ri=i//col
            ax=x+10+ci*(cw2+10); ay=start_y+ri*row_h
            if ay+row_h>y+h: break
            earned=aid in gs.achiev_done
            bg=(31,50,35) if earned else PANEL2
            box(screen,bg,(ax,ay,cw2,row_h-4),7)
            diff_col=DIFF_COLORS.get(diff,MUTED)
            bc=diff_col if earned else BORDER
            box(screen,bc,(ax,ay,cw2,row_h-4),7,1 if not earned else 2)
            # Schwierigkeits-Badge
            box(screen,diff_col,(ax+4,ay+4,50,14),3)
            txt(screen,diff[:6].upper(),"xs",BG if earned else WHITE,ax+29,ay+11,"center")
            icon="✓" if earned else "○"
            txt(screen,icon,"sm",GREEN if earned else MUTED,ax+60,ay+24,"midleft")
            txt(screen,title,"md" if earned else "sm",WHITE if earned else MUTED,ax+78,ay+12)
            txt(screen,desc,"xs",MUTED,ax+78,ay+30,maxw=cw2-90)

    # ── TAB: LOG ──
    def _tab_log(self,x,y,w,h):
        gs=self.gs
        txt(screen,"Aktivitätslog","lg",GOLD,x+12,y+10)
        row_h=24
        kind_col={"good":GREEN,"bad":RED,"warn":YELLOW,"info":CYAN}
        for i,(msg,kind) in enumerate(gs.log[:(h-40)//row_h]):
            ly=y+38+i*row_h; col=kind_col.get(kind,MUTED)
            pygame.draw.rect(screen,col,(x+10,ly+4,3,16))
            txt(screen,msg,"sm",WHITE,x+18,ly+12,"midleft",w-30)

    # ── NEWSBAR ──
    def _draw_newsbar(self):
        box(screen,PANEL,(0,H-20,W,20)); line(screen,BORDER,(0,H-20),(W,H-20))
        gs=self.gs
        news_str="  //  ".join(gs.news[:5]) if gs.news else "Willkommen!"
        self._news_x-=1.2
        if self._news_x<-F["sm"].size(news_str)[0]: self._news_x=float(W)
        txt(screen,news_str,"sm",MUTED,int(self._news_x),H-10,"midleft")

    # ── MODAL ZEICHNEN ──
    def _draw_modal(self):
        mt=self.modal.get("type","")
        mw,mh=660,520; bx=(W-mw)//2; by=(H-mh)//2
        box(screen,PANEL,(bx,by,mw,mh),12)
        box(screen,ACCENT,(bx,by,mw,mh),12,1)
        box(screen,RED,(bx+mw-32,by+6,24,24),12)
        txt(screen,"X","sm",WHITE,bx+mw-20,by+18,"center")
        if mt=="buy_prop":    self._draw_m_buy_prop(bx,by,mw,mh)
        elif mt=="sell_prop": self._draw_m_list_prop(bx,by,mw,mh,"Verkaufen","Verkaufen",RED)
        elif mt=="upg_prop":  self._draw_m_upg_prop(bx,by,mw,mh)
        elif mt=="rent_prop": self._draw_m_rent_prop(bx,by,mw,mh)
        elif mt=="buy_comp":  self._draw_m_buy_comp(bx,by,mw,mh)
        elif mt=="sell_comp": self._draw_m_list_comp(bx,by,mw,mh,"Verkaufen","Verkaufen",RED)
        elif mt=="upg_comp":  self._draw_m_upg_comp(bx,by,mw,mh)
        elif mt=="loan":      self._draw_m_loan(bx,by,mw,mh)
        elif mt=="repay":     self._draw_m_repay(bx,by,mw,mh)
        elif mt=="savings":   self._draw_m_savings(bx,by,mw,mh)
        elif mt in ("buy_stock","sell_stock"): self._draw_m_stock(bx,by,mw,mh)
        elif mt=="buy_etf":   self._draw_m_etf(bx,by,mw,mh)

    def _draw_m_buy_prop(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Immobilie kaufen","lg",GOLD,bx+16,by+16)
        txt(screen,f"Bargeld: {fmt(gs.cash)}","sm",CYAN,bx+16,by+42)
        row_h=72
        view=screen.subsurface(pygame.Rect(bx,by+55,mw,mh-65))
        for i,row in enumerate(PROP_CATALOG):
            tid,name,icon,price,rent,maint,lvl_max=row
            ry=i*row_h-self._scroll
            if ry+row_h<0 or ry>mh-65: continue
            can=gs.cash>=price
            box(view,PANEL2 if can else (25,28,38),(8,ry,mw-16,row_h-4),7)
            box(view,GREEN if can else BORDER,(8,ry,mw-16,row_h-4),7,1)
            txt(view,f"{icon}  {name}","md",WHITE if can else MUTED,18,ry+10)
            txt(view,f"Preis: {fmt(price)}","xs",MUTED,18,ry+32)
            txt(view,f"Miete: +{fmt(rent)}/Monat","xs",GREEN,220,ry+32)
            txt(view,f"Kosten: -{fmt(maint)}/Monat","xs",RED,400,ry+32)
            txt(view,f"Netto: {fmt(rent-maint)}/Monat","xs",CYAN,18,ry+50)
            box(view,ACCENT if can else BORDER,(mw-112,ry+20,90,30),6)
            txt(view,"Kaufen" if can else "Kein Geld","sm",WHITE,mw-67,ry+35,"center")

    def _draw_m_list_prop(self,bx,by,mw,mh,title,btn_label,btn_color):
        gs=self.gs
        txt(screen,f"Immobilie {title}","lg",GOLD,bx+16,by+16)
        if not gs.props: txt(screen,"Keine Immobilien vorhanden.","md",MUTED,bx+16,by+60); return
        row_h=64
        view=screen.subsurface(pygame.Rect(bx,by+50,mw,mh-60))
        for i,p in enumerate(gs.props):
            ry=i*row_h-self._scroll
            if ry+row_h<0 or ry>mh-60: continue
            sv=p["price"]*0.94
            box(view,PANEL2,(8,ry,mw-16,row_h-4),7); box(view,BORDER,(8,ry,mw-16,row_h-4),7,1)
            txt(view,f"{p['name']}  (Lvl {p['level']})","md",WHITE,18,ry+10)
            txt(view,f"Verkaufswert: {fmt(sv)}  |  Netto: {fmt(p['rent']-p['maint'])}/Monat","xs",MUTED,18,ry+34)
            txt(view,f"{'(Leerstand!)' if p.get('vacant') else ''}","xs",RED,18,ry+50)
            box(view,btn_color,(mw-112,ry+16,90,30),6)
            txt(view,btn_label,"sm",WHITE,mw-67,ry+31,"center")

    def _draw_m_upg_prop(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Immobilie renovieren","lg",GOLD,bx+16,by+16)
        txt(screen,"Kosten: 12% des Immowerts  |  +15% Miete, +8% Wert","xs",MUTED,bx+16,by+42)
        if not gs.props: txt(screen,"Keine Immobilien vorhanden.","md",MUTED,bx+16,by+70); return
        row_h=72
        view=screen.subsurface(pygame.Rect(bx,by+50,mw,mh-60))
        for i,p in enumerate(gs.props):
            ry=i*row_h-self._scroll
            if ry+row_h<0 or ry>mh-60: continue
            cost=p["price"]*0.12; maxed=p["level"]>=p["lvl_max"]
            can=gs.cash>=cost and not maxed
            box(view,PANEL2,(8,ry,mw-16,row_h-4),7); box(view,BORDER,(8,ry,mw-16,row_h-4),7,1)
            txt(view,f"{p['name']}","md",WHITE,18,ry+10)
            txt(view,f"Level {p['level']}/{p['lvl_max']}  |  Kosten: {fmt(cost)}","xs",MUTED,18,ry+32)
            progress_bar(view,18,ry+52,200,6,p["level"]/p["lvl_max"],ACCENT)
            if maxed:
                box(view,BORDER,(mw-112,ry+22,90,28),6); txt(view,"Max Level","xs",MUTED,mw-67,ry+36,"center")
            else:
                box(view,ACCENT if can else BORDER,(mw-112,ry+22,90,28),6)
                txt(view,"Renovieren" if can else "Kein Geld","xs",WHITE,mw-67,ry+36,"center")

    def _draw_m_rent_prop(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Vermietungs-Verwaltung","lg",GOLD,bx+16,by+16)
        txt(screen,"Biete leere Immobilien an. Mieter kommen automatisch je nach Wirtschaftslage.","xs",MUTED,bx+16,by+40)
        if not gs.props: txt(screen,"Keine Immobilien vorhanden.","md",MUTED,bx+16,by+80); return
        row_h=100
        view=screen.subsurface(pygame.Rect(bx,by+54,mw,mh-64))
        for i,p in enumerate(gs.props):
            ry=i*row_h-self._scroll
            if ry+row_h<0 or ry>mh-64: continue
            if p["vacant"] and not p["listed"]: bg,bc=(40,25,25),RED
            elif p["vacant"] and p["listed"]: bg,bc=(40,38,15),YELLOW
            else: bg,bc=(20,40,28),GREEN
            box(view,bg,(8,ry,mw-16,row_h-6),8); box(view,bc,(8,ry,mw-16,row_h-6),8,1)
            pygame.draw.rect(view,bc,(8,ry,5,row_h-6),border_radius=2)
            txt(view,f"{p['name']}  Lvl {p['level']}","lg",WHITE,22,ry+10)
            if p["vacant"] and not p["listed"]: status,sc="LEER",RED
            elif p["vacant"] and p["listed"]: status,sc="SUCHE MIETER...",YELLOW
            else:
                ti=p["tenant"]; tname=TENANT_TYPES[ti][0] if ti is not None else "Mieter"
                status,sc=f"VERMIETET: {tname}  ({p['contract_left']} Monate)",GREEN
            txt(view,status,"sm",sc,22,ry+34)
            if not p["vacant"]:
                txt(view,f"Miete: {fmt(p['rent'])}/Monat","xs",CYAN,22,ry+54)
                txt(view,f"Netto: {fmt(p['rent']-p['maint'])}/Monat","xs",GREEN,200,ry+54)
                if len(p["rent_hist"])>=2: sparkline(view,p["rent_hist"],22,ry+68,200,22,GREEN)
            else:
                txt(view,f"Basis-Miete: {fmt(p['base_rent'])}/Monat","xs",MUTED,22,ry+54)
                txt(view,f"Kosten: -{fmt(p['maint'])}/Monat","xs",RED,200,ry+54)
            if p["vacant"] and not p["listed"]:
                box(view,GREEN,(mw-128,ry+20,108,30),6); txt(view,"Anbieten","sm",BG,mw-74,ry+35,"center")
            elif p["vacant"] and p["listed"]:
                box(view,YELLOW,(mw-128,ry+20,108,30),6); txt(view,"Suche stoppen","xs",BG,mw-74,ry+35,"center")
            else:
                box(view,RED,(mw-128,ry+20,108,30),6); txt(view,"Kündigen (-2M)","xs",WHITE,mw-74,ry+35,"center")

    def _draw_m_buy_comp(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Unternehmen gründen","lg",GOLD,bx+16,by+16)
        txt(screen,f"Bargeld: {fmt(gs.cash)}","sm",CYAN,bx+16,by+42)
        row_h=72
        view=screen.subsurface(pygame.Rect(bx,by+55,mw,mh-65))
        for i,row in enumerate(COMP_CATALOG):
            tid,name,icon,price,profit,maint,risk,lvl_max=row
            ry=i*row_h-self._scroll
            if ry+row_h<0 or ry>mh-65: continue
            can=gs.cash>=price
            box(view,PANEL2 if can else (25,28,38),(8,ry,mw-16,row_h-4),7)
            box(view,GREEN if can else BORDER,(8,ry,mw-16,row_h-4),7,1)
            txt(view,f"{name}","md",WHITE if can else MUTED,18,ry+10)
            txt(view,f"Preis: {fmt(price)}","xs",MUTED,18,ry+32)
            txt(view,f"Gewinn: +{fmt(profit)}/Monat","xs",GREEN,220,ry+32)
            txt(view,f"Risiko: {risk*100:.0f}%","xs",YELLOW,400,ry+32)
            txt(view,f"Kosten: -{fmt(maint)}/Monat","xs",RED,18,ry+50)
            box(view,ACCENT if can else BORDER,(mw-112,ry+20,90,30),6)
            txt(view,"Gründen" if can else "Kein Geld","sm",WHITE,mw-67,ry+35,"center")

    def _draw_m_list_comp(self,bx,by,mw,mh,title,btn_label,btn_color):
        gs=self.gs
        txt(screen,f"Unternehmen {title}","lg",GOLD,bx+16,by+16)
        if not gs.comps: txt(screen,"Keine Unternehmen vorhanden.","md",MUTED,bx+16,by+60); return
        row_h=64
        view=screen.subsurface(pygame.Rect(bx,by+50,mw,mh-60))
        for i,c in enumerate(gs.comps):
            ry=i*row_h-self._scroll
            if ry+row_h<0 or ry>mh-60: continue
            sv=c["val"]*0.88
            box(view,PANEL2,(8,ry,mw-16,row_h-4),7); box(view,BORDER,(8,ry,mw-16,row_h-4),7,1)
            txt(view,f"{c['name']}  (Lvl {c['level']})","md",WHITE,18,ry+10)
            txt(view,f"Verkaufswert: {fmt(sv)}  |  Gewinn: {fmt(c['profit'])}/Monat","xs",MUTED,18,ry+34)
            box(view,btn_color,(mw-112,ry+16,90,30),6)
            txt(view,btn_label,"sm",WHITE,mw-67,ry+31,"center")

    def _draw_m_upg_comp(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Unternehmen erweitern","lg",GOLD,bx+16,by+16)
        txt(screen,"Kosten: 15% des Unternehmenswerts  |  +22% Gewinn, +12% Wert","xs",MUTED,bx+16,by+42)
        if not gs.comps: txt(screen,"Keine Unternehmen vorhanden.","md",MUTED,bx+16,by+70); return
        row_h=72
        view=screen.subsurface(pygame.Rect(bx,by+50,mw,mh-60))
        for i,c in enumerate(gs.comps):
            ry=i*row_h-self._scroll
            if ry+row_h<0 or ry>mh-60: continue
            cost=c["val"]*0.15; maxed=c["level"]>=c["lvl_max"]
            can=gs.cash>=cost and not maxed
            box(view,PANEL2,(8,ry,mw-16,row_h-4),7); box(view,BORDER,(8,ry,mw-16,row_h-4),7,1)
            txt(view,c["name"],"md",WHITE,18,ry+10)
            txt(view,f"Level {c['level']}/{c['lvl_max']}  |  Kosten: {fmt(cost)}  |  Gewinn: {fmt(c['profit'])}/Monat","xs",MUTED,18,ry+32)
            progress_bar(view,18,ry+52,200,6,c["level"]/c["lvl_max"],PURPLE)
            if maxed:
                box(view,BORDER,(mw-112,ry+22,90,28),6); txt(view,"Max Level","xs",MUTED,mw-67,ry+36,"center")
            else:
                box(view,ACCENT if can else BORDER,(mw-112,ry+22,90,28),6)
                txt(view,"Erweitern" if can else "Kein Geld","xs",WHITE,mw-67,ry+36,"center")

    def _draw_m_loan(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Kredit aufnehmen","lg",GOLD,bx+16,by+16)
        max_l=max(0,gs.net_worth()*0.6-gs.loan)
        rate=(gs.loan_rate+gs.base_rate/100/12)*12*100
        txt(screen,f"Aktuelle Schulden: {fmt(gs.loan)}","sm",RED,bx+16,by+50)
        txt(screen,f"Max. Kreditrahmen: {fmt(max_l)}","sm",CYAN,bx+16,by+74)
        txt(screen,f"Eff. Jahreszins: {rate:.2f}%","sm",YELLOW,bx+16,by+98)
        ib=self._inputs["amount"]; ib.rect=pygame.Rect(bx+30,by+128,220,34); ib.draw(screen)
        box(screen,ACCENT,(bx+260,by+128,120,34),7)
        txt(screen,"Aufnehmen","sm",WHITE,bx+320,by+145,"center")
        txt(screen,"Warnung: Hohe Schulden führen zu Bankrott!","xs",RED,bx+16,by+178)

    def _draw_m_repay(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Kredit tilgen","lg",GOLD,bx+16,by+16)
        txt(screen,f"Offene Schulden: {fmt(gs.loan)}","sm",RED,bx+16,by+50)
        txt(screen,f"Verfügbares Bargeld: {fmt(gs.cash)}","sm",CYAN,bx+16,by+74)
        ib=self._inputs["amount"]; ib.rect=pygame.Rect(bx+30,by+128,220,34); ib.draw(screen)
        box(screen,GREEN,(bx+260,by+128,120,34),7)
        txt(screen,"Tilgen","sm",WHITE,bx+320,by+145,"center")
        box(screen,YELLOW,(bx+30,by+180,160,34),7)
        txt(screen,"Alles tilgen","sm",BG,bx+110,by+197,"center")

    def _draw_m_savings(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Festgeld-Konto","lg",GOLD,bx+16,by+16)
        rate=gs.sav_rate*12*100
        txt(screen,f"Einlage: {fmt(gs.savings)}","sm",CYAN,bx+16,by+50)
        txt(screen,f"Zins: {rate:.2f}% pa = {fmt(gs.savings*gs.sav_rate)}/Monat","sm",GREEN,bx+16,by+74)
        txt(screen,f"Bargeld: {fmt(gs.cash)}","sm",MUTED,bx+16,by+98)
        ib=self._inputs["amount"]; ib.rect=pygame.Rect(bx+30,by+128,220,34); ib.draw(screen)
        box(screen,ACCENT,(bx+260,by+128,120,34),7)
        txt(screen,"Einzahlen","sm",WHITE,bx+320,by+145,"center")
        if gs.savings>0:
            box(screen,YELLOW,(bx+30,by+180,160,34),7)
            txt(screen,"Auszahlen","sm",BG,bx+110,by+197,"center")

    def _draw_m_stock(self,bx,by,mw,mh):
        gs=self.gs; mt=self.modal["type"]; sid=self.modal["sid"]
        s=gs.stock_data[sid]; qty_owned=gs.stocks.get(sid,0)
        label="Aktie kaufen" if mt=="buy_stock" else "Aktie verkaufen"
        txt(screen,label,"lg",GOLD,bx+16,by+16)
        txt(screen,f"{s['name']}  |  Kurs: {fmt(s['price'])}  |  Div: {s['div']*100:.1f}% pa","md",WHITE,bx+16,by+50)
        txt(screen,f"Im Besitz: {qty_owned:.0f} Stk = {fmt(qty_owned*s['price'])}","sm",CYAN,bx+16,by+76)
        txt(screen,f"Bargeld: {fmt(gs.cash)}","sm",MUTED,bx+16,by+100)
        ib=self._inputs["qty"]; ib.rect=pygame.Rect(bx+30,by+130,180,34); ib.draw(screen)
        bc=ACCENT if mt=="buy_stock" else RED
        box(screen,bc,(bx+220,by+130,110,34),7)
        txt(screen,"Kaufen" if mt=="buy_stock" else "Verkaufen","sm",WHITE,bx+275,by+147,"center")
        if mt=="sell_stock" and qty_owned>0:
            box(screen,YELLOW,(bx+30,by+180,160,34),7)
            txt(screen,"Alles verkaufen","sm",BG,bx+110,by+197,"center")
        if len(s["hist"])>=2:
            sparkline(screen,s["hist"],bx+30,by+240,mw-60,120)
            txt(screen,"Kursverlauf (letzte 40 Perioden)","xs",MUTED,bx+30,by+228)

    def _draw_m_etf(self,bx,by,mw,mh):
        gs=self.gs
        txt(screen,"Welt-ETF kaufen / verkaufen","lg",GOLD,bx+16,by+16)
        txt(screen,f"Kurs: {fmt(gs.etf_price)}  |  Im Besitz: {gs.etf:.1f} Anteile = {fmt(gs.etf*gs.etf_price)}","md",WHITE,bx+16,by+50)
        txt(screen,"Diversifiziert, geringes Risiko, Dividende: 2.4% pa","sm",GREEN,bx+16,by+76)
        txt(screen,f"Bargeld: {fmt(gs.cash)}","sm",MUTED,bx+16,by+100)
        ib=self._inputs["qty"]; ib.rect=pygame.Rect(bx+30,by+130,180,34); ib.draw(screen)
        box(screen,ACCENT,(bx+220,by+130,110,34),7)
        txt(screen,"Kaufen","sm",WHITE,bx+275,by+147,"center")
        if gs.etf>0:
            box(screen,RED,(bx+30,by+180,180,34),7)
            txt(screen,"Alle Anteile verkaufen","sm",WHITE,bx+120,by+197,"center")
        if len(gs.etf_hist)>=2:
            sparkline(screen,gs.etf_hist,bx+30,by+240,mw-60,100)

    # ── ACHIEVEMENT POPUP ──
    def _draw_ach_popup(self):
        title,desc,diff,t0=self._ach_popup
        elapsed=pygame.time.get_ticks()-t0
        if elapsed>4500: self._ach_popup=None; return
        alpha=255 if elapsed<3500 else int(255*(1-(elapsed-3500)/1000))
        pw,ph2=360,68; px,py2=W-pw-16,H-ph2-28
        diff_col=DIFF_COLORS.get(diff,GOLD)
        s=pygame.Surface((pw,ph2),pygame.SRCALPHA)
        r,g,b=diff_col
        s.fill((r//4,g//4,b//4,alpha))
        screen.blit(s,(px,py2))
        pygame.draw.rect(screen,diff_col,(px,py2,pw,ph2),2,border_radius=8)
        txt(screen,f"🏆 Erfolg ({diff.upper()}): {title}","sm",GOLD,px+10,py2+10)
        txt(screen,desc,"xs",MUTED,px+10,py2+34)
        # Fortschritt
        n=len(self.gs.achiev_done); tot=len(ACHIEVEMENTS)
        txt(screen,f"{n}/{tot} Erfolge","xs",diff_col,px+10,py2+52)
        progress_bar(screen,px+100,py2+52,pw-120,8,n/tot,diff_col)


# ─────────────────────────────────────────────────────
#  BANKROTT-SCREEN
# ─────────────────────────────────────────────────────
class BankruptScreen:
    def __init__(self, gs: GS):
        self.gs=gs
        self.btn=Btn(W//2-90,H//2+80,180,40,"Neu starten",GREEN,BG,"lg")

    def handle(self, ev):
        self.btn.update(pygame.mouse.get_pos())
        if self.btn.hit(ev): return "restart"
        return None

    def draw(self, surf):
        surf.fill(BG)
        txt(surf,"BANKROTT","title",RED,W//2,H//2-100,"center")
        txt(surf,"Du bist zahlungsunfähig!","lg",WHITE,W//2,H//2-50,"center")
        txt(surf,f"Nettovermögen: {fmt(self.gs.net_worth())}","md",MUTED,W//2,H//2-14,"center")
        txt(surf,f"Gespielte Monate: {self.gs._total_months}","md",MUTED,W//2,H//2+20,"center")
        txt(surf,f"Erreichte Erfolge: {len(self.gs.achiev_done)}/{len(ACHIEVEMENTS)}","md",GOLD,W//2,H//2+46,"center")
        self.btn.draw(surf)


# ─────────────────────────────────────────────────────
#  HAUPTSCHLEIFE
# ─────────────────────────────────────────────────────
def main():
    state="name"
    name_screen=NameScreen()
    game_screen=None
    bankr_screen=None
    gs=None

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                # Autosave beim Beenden
                if gs and game_screen:
                    save_game(gs, 0)
                pygame.quit(); sys.exit()
            if ev.type==pygame.VIDEORESIZE:
                global W,H
                W,H=ev.w,ev.h

            if state=="name":
                result=name_screen.handle(ev)
                if result:
                    action=result[0]
                    if action=="new":
                        gs=GS(); gs.name=result[1]
                        gs.add_log(f"Willkommen, {gs.name}! Startkapital: {fmt(gs.cash)}","info")
                        gs.add_news("Spielstart! Viel Erfolg beim Investieren.")
                        game_screen=GameScreen(gs); state="game"
                    elif action=="load":
                        slot=result[1]
                        loaded=load_game(slot)
                        if loaded:
                            gs=loaded
                            gs.add_log(f"Spielstand geladen (Slot {slot+1})","info")
                            game_screen=GameScreen(gs); state="game"

            elif state=="game":
                if ev.type==pygame.MOUSEWHEEL:
                    game_screen.handle_scroll(ev)
                else:
                    result=game_screen.handle(ev)
                    if result=="bankrott":
                        bankr_screen=BankruptScreen(gs); state="bankrott"
                    elif isinstance(result,tuple) and result[0]=="load":
                        gs=result[1]
                        gs.add_log("Spielstand geladen","info")
                        game_screen=GameScreen(gs)

            elif state=="bankrott":
                result=bankr_screen.handle(ev)
                if result=="restart":
                    state="name"; name_screen=NameScreen()

        if state=="name":
            name_screen.draw(screen)
        elif state=="game":
            result=game_screen.maybe_tick()
            if result=="bankrott":
                bankr_screen=BankruptScreen(gs); state="bankrott"
            else:
                game_screen.draw()
        elif state=="bankrott":
            bankr_screen.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__=="__main__":
    main()
