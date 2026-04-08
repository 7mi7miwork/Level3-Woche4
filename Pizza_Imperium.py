"""
╔══════════════════════════════════════════════════════════════════╗
║           PIZZERIA IMPERIUM - Das ultimative Tycoon Spiel        ║
║                                                                  ║
║  Features:                                                       ║
║  • 8 Level (Straßenstand bis Weltkonzern)                        ║
║  • 5 Schwierigkeitsgrade                                         ║
║  • 8 Power-Ups                                                   ║
║  • 6 Personal-Typen                                              ║
║  • 10 Pizzasorten                                                ║
║  • 30+ Achievements                                              ║
║  • Highscore-System                                              ║
║  • Speichern/Laden                                               ║
║  • Animationen & Partikeleffekte                                 ║
║  • Forschungs-Baum                                               ║
║  • Zufallsereignisse                                             ║
╚══════════════════════════════════════════════════════════════════╝

Steuerung:
  Maus: Klicken auf Buttons, Kunden, Zutaten
  Tastatur:
    SPACE  - Pause
    S      - Schnell speichern
    H      - Highscores
    A      - Achievements
    R      - Forschung
    ESC    - Menü / Zurück
    1-5    - Personal einsetzen (wenn ausgewählt)
"""

import pygame
import sys
import json
import os
import random
import math
import time
import datetime
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

# ═══════════════════════════════════════════════════════════════════
#  KONSTANTEN & KONFIGURATION
# ═══════════════════════════════════════════════════════════════════

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
SAVE_FILE = "pizzeria_save.json"
SCORES_FILE = "pizzeria_scores.json"
TITLE = "Pizzeria Imperium"

# ─── Farben ───────────────────────────────────────────────────────
C_BG         = (18,  18,  28)
C_PANEL      = (28,  28,  45)
C_PANEL2     = (38,  38,  60)
C_ACCENT     = (255, 100,  50)   # Orange-Rot
C_ACCENT2    = (255, 200,  50)   # Gold
C_GREEN      = ( 80, 220, 100)
C_RED        = (220,  70,  70)
C_BLUE       = ( 70, 150, 255)
C_PURPLE     = (180,  80, 255)
C_TEAL       = ( 50, 210, 180)
C_YELLOW     = (255, 230,  50)
C_WHITE      = (240, 240, 250)
C_GRAY       = (120, 120, 150)
C_DARKGRAY   = ( 60,  60,  90)
C_BLACK      = (  5,   5,  10)
C_GOLD       = (255, 200,  30)
C_SILVER     = (180, 190, 200)
C_BRONZE     = (180, 120,  50)

# Pizza-Farben
C_PIZZAS = {
    "Margherita":    (220, 160,  80),
    "Salami":        (180,  60,  60),
    "Funghi":        (140, 100,  60),
    "Tonno":         ( 80, 150, 200),
    "Hawaii":        (220, 180,  50),
    "Quattro":       (160, 100, 180),
    "Calzone":       (200, 140,  60),
    "Diavola":       (220,  50,  50),
    "Vegetariana":   ( 80, 180,  80),
    "Speciale":      (255, 150,  30),
}

# ─── Level-Definitionen ───────────────────────────────────────────
LEVELS = [
    {
        "id": 0, "name": "Straßenstand",
        "ziel_geld": 500,
        "max_kunden": 3, "max_personal": 1,
        "max_tische": 2, "ofen_slots": 1,
        "unlock_text": "Starte dein Imperium!",
        "hintergrund": (25, 20, 15),
        "beschreibung": "Dein erster kleiner Pizzastand am Straßenrand."
    },
    {
        "id": 1, "name": "Kiosk",
        "ziel_geld": 2000,
        "max_kunden": 5, "max_personal": 2,
        "max_tische": 4, "ofen_slots": 2,
        "unlock_text": "Du hast deinen ersten Kiosk!",
        "hintergrund": (20, 25, 20),
        "beschreibung": "Ein kleiner Kiosk mit etwas mehr Platz."
    },
    {
        "id": 2, "name": "Imbiss",
        "ziel_geld": 6000,
        "max_kunden": 8, "max_personal": 3,
        "max_tische": 6, "ofen_slots": 2,
        "unlock_text": "Willkommen im Imbiss-Geschäft!",
        "hintergrund": (20, 20, 28),
        "beschreibung": "Ein richtiger Imbiss mit Sitzplätzen."
    },
    {
        "id": 3, "name": "Pizzeria",
        "ziel_geld": 20000,
        "max_kunden": 12, "max_personal": 4,
        "max_tische": 10, "ofen_slots": 3,
        "unlock_text": "Eine echte Pizzeria! Fantastisch!",
        "hintergrund": (28, 20, 20),
        "beschreibung": "Deine eigene Pizzeria mit vollem Betrieb."
    },
    {
        "id": 4, "name": "Restaurant",
        "ziel_geld": 60000,
        "max_kunden": 18, "max_personal": 5,
        "max_tische": 15, "ofen_slots": 4,
        "unlock_text": "Ein echtes Restaurant — beeindruckend!",
        "hintergrund": (15, 25, 25),
        "beschreibung": "Ein elegantes Restaurant der Spitzenklasse."
    },
    {
        "id": 5, "name": "Kette",
        "ziel_geld": 200000,
        "max_kunden": 25, "max_personal": 7,
        "max_tische": 20, "ofen_slots": 5,
        "unlock_text": "Deine eigene Restaurantkette!",
        "hintergrund": (25, 15, 28),
        "beschreibung": "Mehrere Filialen unter deiner Führung."
    },
    {
        "id": 6, "name": "Imperium",
        "ziel_geld": 1000000,
        "max_kunden": 35, "max_personal": 9,
        "max_tische": 30, "ofen_slots": 7,
        "unlock_text": "Das Pizzeria-Imperium ist deins!",
        "hintergrund": (25, 25, 15),
        "beschreibung": "Ein weltweites Pizza-Imperium!"
    },
    {
        "id": 7, "name": "Weltkonzern",
        "ziel_geld": 5000000,
        "max_kunden": 50, "max_personal": 12,
        "max_tische": 50, "ofen_slots": 10,
        "unlock_text": "Du bist der Pizza-König der Welt!",
        "hintergrund": (20, 20, 20),
        "beschreibung": "Der größte Pizzakonzern aller Zeiten!"
    },
]

# ─── Schwierigkeitsgrade ──────────────────────────────────────────
SCHWIERIGKEITSGRADE = {
    "Kinderleicht": {
        "kunden_geduld_mult": 2.0,
        "preis_mult": 1.3,
        "kosten_mult": 0.7,
        "ereignis_chance": 0.001,
        "farbe": C_GREEN,
        "beschreibung": "Kunden sind sehr geduldig, hohe Einnahmen"
    },
    "Einfach": {
        "kunden_geduld_mult": 1.5,
        "preis_mult": 1.1,
        "kosten_mult": 0.85,
        "ereignis_chance": 0.003,
        "farbe": C_TEAL,
        "beschreibung": "Entspanntes Spieltempo"
    },
    "Normal": {
        "kunden_geduld_mult": 1.0,
        "preis_mult": 1.0,
        "kosten_mult": 1.0,
        "ereignis_chance": 0.005,
        "farbe": C_BLUE,
        "beschreibung": "Ausgewogene Herausforderung"
    },
    "Schwer": {
        "kunden_geduld_mult": 0.7,
        "preis_mult": 0.9,
        "kosten_mult": 1.2,
        "ereignis_chance": 0.008,
        "farbe": C_ACCENT,
        "beschreibung": "Kunden ungeduldig, höhere Kosten"
    },
    "Meister": {
        "kunden_geduld_mult": 0.4,
        "preis_mult": 0.8,
        "kosten_mult": 1.5,
        "ereignis_chance": 0.015,
        "farbe": C_RED,
        "beschreibung": "Nur für echte Profis!"
    },
}

# ─── Pizza-Definitionen ───────────────────────────────────────────
PIZZEN = {
    "Margherita":   {"preis": 8,  "zeit": 60,  "beliebt": 10, "zutaten": ["Teig", "Soße", "Käse"]},
    "Salami":       {"preis": 11, "zeit": 75,  "beliebt": 9,  "zutaten": ["Teig", "Soße", "Käse", "Salami"]},
    "Funghi":       {"preis": 10, "zeit": 70,  "beliebt": 7,  "zutaten": ["Teig", "Soße", "Käse", "Pilze"]},
    "Tonno":        {"preis": 12, "zeit": 80,  "beliebt": 6,  "zutaten": ["Teig", "Soße", "Käse", "Thunfisch"]},
    "Hawaii":       {"preis": 12, "zeit": 75,  "beliebt": 8,  "zutaten": ["Teig", "Soße", "Käse", "Schinken", "Ananas"]},
    "Quattro":      {"preis": 15, "zeit": 90,  "beliebt": 5,  "zutaten": ["Teig", "Soße", "4 Käsesorten"]},
    "Calzone":      {"preis": 14, "zeit": 100, "beliebt": 6,  "zutaten": ["Teig", "Soße", "Käse", "Schinken"]},
    "Diavola":      {"preis": 13, "zeit": 80,  "beliebt": 7,  "zutaten": ["Teig", "Soße", "Käse", "Peperoni"]},
    "Vegetariana":  {"preis": 11, "zeit": 70,  "beliebt": 6,  "zutaten": ["Teig", "Soße", "Käse", "Gemüse"]},
    "Speciale":     {"preis": 18, "zeit": 110, "beliebt": 4,  "zutaten": ["Teig", "Soße", "Käse", "Spezialbelag"]},
}

# ─── Personal-Typen ───────────────────────────────────────────────
PERSONAL_TYPEN = {
    "Lehrling": {
        "geschwindigkeit": 0.5, "fehler_rate": 0.2,
        "gehalt": 5, "farbe": C_GRAY,
        "beschreibung": "Langsam aber günstig"
    },
    "Koch": {
        "geschwindigkeit": 1.0, "fehler_rate": 0.08,
        "gehalt": 15, "farbe": C_WHITE,
        "beschreibung": "Solider Standardkoch"
    },
    "Chefkoch": {
        "geschwindigkeit": 1.5, "fehler_rate": 0.02,
        "gehalt": 30, "farbe": C_GOLD,
        "beschreibung": "Schnell und präzise"
    },
    "Kellner": {
        "geschwindigkeit": 1.2, "fehler_rate": 0.05,
        "gehalt": 12, "farbe": C_BLUE,
        "beschreibung": "Schneller Service"
    },
    "Manager": {
        "geschwindigkeit": 1.0, "fehler_rate": 0.0,
        "gehalt": 40, "farbe": C_PURPLE,
        "beschreibung": "Automatisiert Bestellungen"
    },
    "Superstar": {
        "geschwindigkeit": 2.0, "fehler_rate": 0.01,
        "gehalt": 80, "farbe": C_ACCENT,
        "beschreibung": "Der Beste der Besten"
    },
}

# ─── Power-Ups ────────────────────────────────────────────────────
POWERUPS = {
    "Turbobackofen": {
        "kosten": 200, "dauer": 300, "farbe": C_RED,
        "effekt": "backzeit_mult", "wert": 0.5,
        "icon": "🔥", "beschreibung": "Halbiert Backzeiten für 5 Min"
    },
    "Werbung": {
        "kosten": 150, "dauer": 600, "farbe": C_YELLOW,
        "effekt": "kunden_mult", "wert": 2.0,
        "icon": "📢", "beschreibung": "Verdoppelt Kundenzahl für 10 Min"
    },
    "Preisboost": {
        "kosten": 300, "dauer": 300, "farbe": C_GOLD,
        "effekt": "preis_mult", "wert": 1.5,
        "icon": "💰", "beschreibung": "+50% Preis für 5 Min"
    },
    "Geduldsengel": {
        "kosten": 100, "dauer": 240, "farbe": C_GREEN,
        "effekt": "geduld_mult", "wert": 2.0,
        "icon": "😇", "beschreibung": "Kunden warten 2x länger"
    },
    "Autopilot": {
        "kosten": 500, "dauer": 180, "farbe": C_BLUE,
        "effekt": "auto", "wert": 1.0,
        "icon": "🤖", "beschreibung": "Automatisch für 3 Min"
    },
    "Zutatenrabatt": {
        "kosten": 80, "dauer": 600, "farbe": C_TEAL,
        "effekt": "zutat_rabatt", "wert": 0.5,
        "icon": "🛒", "beschreibung": "50% Rabatt auf Zutaten"
    },
    "VIP-Abend": {
        "kosten": 400, "dauer": 120, "farbe": C_PURPLE,
        "effekt": "vip_mult", "wert": 3.0,
        "icon": "⭐", "beschreibung": "Alle Kunden zahlen 3x"
    },
    "Personalboost": {
        "kosten": 250, "dauer": 360, "farbe": C_ACCENT,
        "effekt": "personal_speed", "wert": 2.0,
        "icon": "💪", "beschreibung": "Personal 2x schneller"
    },
}

# ─── Zufallsereignisse ────────────────────────────────────────────
EREIGNISSE = [
    {"name": "Gesundheitsinspektion!", "typ": "negativ",
     "beschreibung": "Du musst €{wert} Geldstrafe zahlen.",
     "wert_range": (100, 500), "farbe": C_RED},
    {"name": "Kundenbewertung!", "typ": "positiv",
     "beschreibung": "Positive Presse! +{wert} Ansehen.",
     "wert_range": (50, 200), "farbe": C_GREEN},
    {"name": "Rohrbruch!", "typ": "negativ",
     "beschreibung": "Reparaturkosten €{wert}!",
     "wert_range": (200, 800), "farbe": C_RED},
    {"name": "Prominenter Besuch!", "typ": "positiv",
     "beschreibung": "Ein Star war da! +€{wert} Bonus!",
     "wert_range": (500, 2000), "farbe": C_GOLD},
    {"name": "Stromausfall!", "typ": "negativ",
     "beschreibung": "5 Minuten kein Betrieb! Verlust: €{wert}",
     "wert_range": (100, 400), "farbe": C_RED},
    {"name": "Lieferantenrabatt!", "typ": "positiv",
     "beschreibung": "30% Rabatt heute! Gespart: €{wert}",
     "wert_range": (50, 300), "farbe": C_GREEN},
    {"name": "Schlechtes Wetter!", "typ": "negativ",
     "beschreibung": "Weniger Kunden wegen Regen. -{wert} Umsatz.",
     "wert_range": (50, 200), "farbe": C_BLUE},
    {"name": "Stadtfest!", "typ": "positiv",
     "beschreibung": "Extraviel los! +€{wert} Bonus!",
     "wert_range": (300, 1000), "farbe": C_YELLOW},
    {"name": "Mitarbeiter krank!", "typ": "negativ",
     "beschreibung": "Personal fehlt heute. -{wert}% Effizienz.",
     "wert_range": (20, 40), "farbe": C_RED},
    {"name": "Zeitungsartikel!", "typ": "positiv",
     "beschreibung": "Tolle Kritik! Mehr Kunden kommen!",
     "wert_range": (100, 500), "farbe": C_GREEN},
]

# ─── Achievements ─────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id": "erste_pizza",    "name": "Erste Pizza!",         "beschreibung": "Backe deine erste Pizza",                "icon": "🍕", "xp": 10},
    {"id": "10_pizzen",      "name": "Pizzabäcker",          "beschreibung": "Backe 10 Pizzen",                        "icon": "👨‍🍳","xp": 25},
    {"id": "100_pizzen",     "name": "Pizza-Profi",          "beschreibung": "Backe 100 Pizzen",                       "icon": "🏆", "xp": 100},
    {"id": "1000_pizzen",    "name": "Pizza-Legende",        "beschreibung": "Backe 1000 Pizzen",                      "icon": "👑", "xp": 500},
    {"id": "erstes_level",   "name": "Aufsteiger",           "beschreibung": "Erreiche Level 1",                       "icon": "⬆️", "xp": 50},
    {"id": "level_5",        "name": "Restaurantbesitzer",   "beschreibung": "Erreiche Level 5",                       "icon": "🏪", "xp": 200},
    {"id": "level_7",        "name": "Weltkonzern",          "beschreibung": "Erreiche Level 7",                       "icon": "🌍", "xp": 1000},
    {"id": "1000_euro",      "name": "Tausender",            "beschreibung": "Verdiene €1.000",                        "icon": "💶", "xp": 50},
    {"id": "10000_euro",     "name": "Zehntausender",        "beschreibung": "Verdiene €10.000",                       "icon": "💰", "xp": 200},
    {"id": "100000_euro",    "name": "Millionär fast",       "beschreibung": "Verdiene €100.000",                      "icon": "🤑", "xp": 500},
    {"id": "1000000_euro",   "name": "Millionär!",           "beschreibung": "Verdiene €1.000.000",                    "icon": "💎", "xp": 2000},
    {"id": "kein_fehler",    "name": "Perfektionist",        "beschreibung": "10 Pizzen ohne Fehler",                  "icon": "✨", "xp": 75},
    {"id": "schnell",        "name": "Blitz-Koch",           "beschreibung": "Pizza in unter 30 Sekunden",             "icon": "⚡", "xp": 100},
    {"id": "5_personal",     "name": "Team-Chef",            "beschreibung": "Stelle 5 Mitarbeiter ein",               "icon": "👥", "xp": 150},
    {"id": "alle_pizzen",    "name": "Vollständige Karte",   "beschreibung": "Alle Pizzasorten freigeschaltet",         "icon": "📋", "xp": 300},
    {"id": "powerup_nutzen", "name": "Power-Spieler",        "beschreibung": "Benutze 5 Power-Ups",                    "icon": "⚡", "xp": 100},
    {"id": "ereignis_10",    "name": "Krisenmanager",        "beschreibung": "Überlebe 10 Zufallsereignisse",               "icon": "🎭", "xp": 200},
    {"id": "zufrieden",      "name": "Kundenflüsterer",      "beschreibung": "100 zufriedene Kunden",                  "icon": "😊", "xp": 150},
    {"id": "forschung_5",    "name": "Forscher",             "beschreibung": "5 Forschungen abschließen",              "icon": "🔬", "xp": 200},
    {"id": "spielzeit_1h",   "name": "Ausdauernd",           "beschreibung": "1 Stunde spielen",                       "icon": "⏰", "xp": 100},
    {"id": "nacht_schicht",  "name": "Nachtschicht",         "beschreibung": "Spiele nach 22 Uhr",                     "icon": "🌙", "xp": 50},
    {"id": "kein_personal",  "name": "Einzelkämpfer",        "beschreibung": "Level 2 ohne Personal",                  "icon": "🦸", "xp": 200},
    {"id": "combo_5",        "name": "Combo-König",          "beschreibung": "5er Bestellungs-Combo",                  "icon": "🔥", "xp": 150},
    {"id": "preisrekord",    "name": "Preisrekord",          "beschreibung": "€500 in einer Minute",                   "icon": "📈", "xp": 300},
    {"id": "vollhaus",       "name": "Vollhaus",             "beschreibung": "Alle Tische gleichzeitig besetzt",        "icon": "🎪", "xp": 200},
    {"id": "sparfuchs",      "name": "Sparfuchs",            "beschreibung": "Zutaten 50x mit Rabatt kaufen",          "icon": "🦊", "xp": 100},
    {"id": "erste_forschung","name": "Wissenschaftler",      "beschreibung": "Erste Forschung abschließen",            "icon": "🧪", "xp": 75},
    {"id": "vip_10",         "name": "VIP-Gastgeber",        "beschreibung": "10 VIP-Kunden bedienen",                 "icon": "🎩", "xp": 200},
    {"id": "streak_10",      "name": "Streak-Meister",       "beschreibung": "10 Tage hintereinander spielen",         "icon": "🔁", "xp": 500},
    {"id": "erste_krise",    "name": "Krisenprofi",          "beschreibung": "Dein erstes Ereignis überleben",         "icon": "💪", "xp": 25},
]

# ─── Forschungs-Baum ──────────────────────────────────────────────
FORSCHUNGEN = [
    {"id": "ofen1",        "name": "Schnellbackofen",    "kosten": 300,  "dauer": 30,  "voraus": [],
     "effekt": "backzeit_mult", "wert": 0.9,  "icon": "🔥", "beschreibung": "Backen 10% schneller"},
    {"id": "ofen2",        "name": "Turbobackofen",      "kosten": 800,  "dauer": 60,  "voraus": ["ofen1"],
     "effekt": "backzeit_mult", "wert": 0.8,  "icon": "🔥", "beschreibung": "Backen 20% schneller"},
    {"id": "ofen3",        "name": "Mega-Ofen",          "kosten": 2000, "dauer": 120, "voraus": ["ofen2"],
     "effekt": "backzeit_mult", "wert": 0.6,  "icon": "🔥", "beschreibung": "Backen 40% schneller"},
    {"id": "service1",     "name": "Freundlichkeit",     "kosten": 200,  "dauer": 20,  "voraus": [],
     "effekt": "geduld_mult",  "wert": 1.2,  "icon": "😊", "beschreibung": "Kunden 20% geduldiger"},
    {"id": "service2",     "name": "VIP-Service",        "kosten": 600,  "dauer": 45,  "voraus": ["service1"],
     "effekt": "geduld_mult",  "wert": 1.5,  "icon": "⭐", "beschreibung": "Kunden 50% geduldiger"},
    {"id": "marketing1",   "name": "Flyer",              "kosten": 150,  "dauer": 15,  "voraus": [],
     "effekt": "kunden_mult",  "wert": 1.1,  "icon": "📄", "beschreibung": "10% mehr Kunden"},
    {"id": "marketing2",   "name": "Social Media",       "kosten": 500,  "dauer": 40,  "voraus": ["marketing1"],
     "effekt": "kunden_mult",  "wert": 1.3,  "icon": "📱", "beschreibung": "30% mehr Kunden"},
    {"id": "marketing3",   "name": "TV-Werbung",         "kosten": 2000, "dauer": 90,  "voraus": ["marketing2"],
     "effekt": "kunden_mult",  "wert": 1.6,  "icon": "📺", "beschreibung": "60% mehr Kunden"},
    {"id": "preis1",       "name": "Qualitätszutaten",   "kosten": 400,  "dauer": 30,  "voraus": [],
     "effekt": "preis_mult",   "wert": 1.1,  "icon": "✨", "beschreibung": "10% höhere Preise"},
    {"id": "preis2",       "name": "Gourmet-Küche",      "kosten": 1200, "dauer": 80,  "voraus": ["preis1"],
     "effekt": "preis_mult",   "wert": 1.25, "icon": "👨‍🍳","beschreibung": "25% höhere Preise"},
    {"id": "auto1",        "name": "Kassensystem",       "kosten": 500,  "dauer": 35,  "voraus": [],
     "effekt": "auto_teil",    "wert": 1.0,  "icon": "🖥️", "beschreibung": "Kassen teilweise automatisch"},
    {"id": "auto2",        "name": "Roboter-Assistent",  "kosten": 3000, "dauer": 150, "voraus": ["auto1"],
     "effekt": "auto_voll",    "wert": 1.0,  "icon": "🤖", "beschreibung": "Voll automatisches System"},
]

# ═══════════════════════════════════════════════════════════════════
#  DATENKLASSEN
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Pizza:
    name: str
    fortschritt: float = 0.0
    fertig: bool = False
    verbrannt: bool = False
    bestellt_von: int = -1   # Kunden-ID
    backzeit: float = 0.0

@dataclass
class Kunde:
    id: int
    pizza_name: str
    geduld: float = 100.0
    max_geduld: float = 100.0
    bezahlt: bool = False
    vip: bool = False
    x: float = 0.0
    y: float = 0.0
    ziel_x: float = 0.0
    ziel_y: float = 0.0
    tisch_id: int = -1
    animation_timer: float = 0.0
    animation_phase: int = 0
    ungeduldig: bool = False
    emoji: str = "😊"

@dataclass
class Personal:
    id: int
    typ: str
    name: str
    task: str = "warten"   # warten, kochen, servieren
    task_timer: float = 0.0
    x: float = 0.0
    y: float = 0.0
    animation: float = 0.0
    erfahrung: int = 0
    erschoepft: bool = False

@dataclass
class Partikel:
    x: float
    y: float
    vx: float
    vy: float
    leben: float
    max_leben: float
    farbe: tuple
    groesse: float
    text: str = ""

@dataclass
class Benachrichtigung:
    text: str
    farbe: tuple
    timer: float = 3.0
    y_offset: float = 0.0

@dataclass
class ActivePowerup:
    name: str
    verbleibend: float
    gesamt: float

@dataclass
class ForschungsFortschritt:
    id: str
    verbleibend: float
    gesamt: float

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
        self.zufriedene_kunden: int = 0
        self.spielzeit: float = 0.0
        self.schwierigkeit: str = "Normal"
        self.achievements_erhalten: list = []
        self.forschungen_abgeschlossen: list = []
        self.freigeschaltete_pizzen: list = ["Margherita", "Salami"]
        self.powerups_benutzt: int = 0
        self.ereignisse_erlebt: int = 0
        self.vip_kunden_bedient: int = 0
        self.fehler_serie: int = 0
        self.perfekte_serie: int = 0
        self.combo: int = 0
        self.max_combo: int = 0
        self.xp: int = 0
        self.spieltage: list = []
        self.rabatt_kaeufe: int = 0
        self.minuten_umsatz: float = 0.0
        self.minuten_timer: float = 0.0
        self.max_minuten_umsatz: float = 0.0
        self.datum_gestartet: str = datetime.datetime.now().strftime("%Y-%m-%d")

    def zu_dict(self) -> dict:
        return {
            "geld": self.geld,
            "level": self.level,
            "gesamt_verdient": self.gesamt_verdient,
            "pizzen_gebacken": self.pizzen_gebacken,
            "kunden_bedient": self.kunden_bedient,
            "kunden_verloren": self.kunden_verloren,
            "zufriedene_kunden": self.zufriedene_kunden,
            "spielzeit": self.spielzeit,
            "schwierigkeit": self.schwierigkeit,
            "achievements_erhalten": self.achievements_erhalten,
            "forschungen_abgeschlossen": self.forschungen_abgeschlossen,
            "freigeschaltete_pizzen": self.freigeschaltete_pizzen,
            "powerups_benutzt": self.powerups_benutzt,
            "ereignisse_erlebt": self.ereignisse_erlebt,
            "vip_kunden_bedient": self.vip_kunden_bedient,
            "perfekte_serie": self.perfekte_serie,
            "combo": self.combo,
            "max_combo": self.max_combo,
            "xp": self.xp,
            "spieltage": self.spieltage,
            "rabatt_kaeufe": self.rabatt_kaeufe,
            "datum_gestartet": self.datum_gestartet,
        }

    def von_dict(self, d: dict):
        for k, v in d.items():
            if hasattr(self, k):
                setattr(self, k, v)

# ═══════════════════════════════════════════════════════════════════
#  HILFSFUNKTIONEN
# ═══════════════════════════════════════════════════════════════════

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def dist(ax, ay, bx, by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def fmt_geld(v: float) -> str:
    if v >= 1_000_000:
        return f"€{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"€{v/1_000:.1f}K"
    return f"€{v:.0f}"

def fmt_zeit(sek: float) -> str:
    m = int(sek) // 60
    s = int(sek) % 60
    return f"{m:02d}:{s:02d}"

def zeichne_rect_rund(surf, farbe, rect, radius=8, alpha=255):
    if alpha < 255:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*farbe, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, farbe, rect, border_radius=radius)

def zeichne_text(surf, text, x, y, font, farbe=C_WHITE, center=False, right=False):
    rendered = font.render(str(text), True, farbe)
    rx, ry = x, y
    if center:
        rx = x - rendered.get_width() // 2
    if right:
        rx = x - rendered.get_width()
    surf.blit(rendered, (rx, ry))
    return rendered.get_width()

def zeichne_balken(surf, x, y, w, h, wert, max_wert, farbe_voll, farbe_leer=C_DARKGRAY, border=True):
    anteil = clamp(wert / max_wert, 0, 1) if max_wert > 0 else 0
    pygame.draw.rect(surf, farbe_leer, (x, y, w, h), border_radius=4)
    if anteil > 0:
        pygame.draw.rect(surf, farbe_voll, (x, y, int(w * anteil), h), border_radius=4)
    if border:
        pygame.draw.rect(surf, C_DARKGRAY, (x, y, w, h), 1, border_radius=4)

# ═══════════════════════════════════════════════════════════════════
#  BUTTON-KLASSE
# ═══════════════════════════════════════════════════════════════════

class Button:
    def __init__(self, x, y, w, h, text, farbe=C_ACCENT, font=None,
                 icon="", aktiv=True, klein=False, tooltip=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.farbe = farbe
        self.font = font
        self.icon = icon
        self.aktiv = aktiv
        self.klein = klein
        self.tooltip = tooltip
        self.hover = False
        self.press_anim = 0.0
        self.glow = 0.0

    def update(self, dt):
        if self.hover:
            self.glow = min(1.0, self.glow + dt * 3)
        else:
            self.glow = max(0.0, self.glow - dt * 3)
        self.press_anim = max(0.0, self.press_anim - dt * 8)

    def zeichne(self, surf, font_normal, font_klein):
        font = self.font or (font_klein if self.klein else font_normal)
        farbe = self.farbe if self.aktiv else C_DARKGRAY
        glow_farbe = tuple(min(255, c + int(40 * self.glow)) for c in farbe)

        offset = int(self.press_anim * 3)
        r = pygame.Rect(self.rect.x, self.rect.y + offset,
                        self.rect.w, self.rect.h)

        zeichne_rect_rund(surf, glow_farbe, r, radius=8)
        if self.hover and self.aktiv:
            zeichne_rect_rund(surf, C_WHITE, r, radius=8)
            pygame.draw.rect(surf, C_WHITE, r, 2, border_radius=8)

        content = f"{self.icon} {self.text}" if self.icon else self.text
        txt_surf = font.render(content, True, C_WHITE if self.aktiv else C_GRAY)
        tx = r.centerx - txt_surf.get_width() // 2
        ty = r.centery - txt_surf.get_height() // 2
        surf.blit(txt_surf, (tx, ty))

    def check_hover(self, mpos):
        self.hover = self.rect.collidepoint(mpos)

    def clicked(self, mpos, button=1):
        if self.aktiv and self.rect.collidepoint(mpos):
            self.press_anim = 1.0
            return True
        return False

# ═══════════════════════════════════════════════════════════════════
#  PARTIKEL-SYSTEM
# ═══════════════════════════════════════════════════════════════════

class PartikelSystem:
    def __init__(self):
        self.partikel: list[Partikel] = []

    def add(self, x, y, farbe, anzahl=8, text="", geschwindigkeit=80):
        for _ in range(anzahl):
            winkel = random.uniform(0, math.tau)
            speed = random.uniform(20, geschwindigkeit)
            self.partikel.append(Partikel(
                x=x, y=y,
                vx=math.cos(winkel) * speed,
                vy=math.sin(winkel) * speed,
                leben=random.uniform(0.5, 1.5),
                max_leben=1.5,
                farbe=farbe,
                groesse=random.uniform(2, 6),
            ))
        if text:
            self.partikel.append(Partikel(
                x=x, y=y - 10,
                vx=random.uniform(-20, 20),
                vy=-60,
                leben=1.5,
                max_leben=1.5,
                farbe=farbe,
                groesse=0,
                text=text,
            ))

    def update(self, dt):
        lebend = []
        for p in self.partikel:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 40 * dt
            p.leben -= dt
            if p.leben > 0:
                lebend.append(p)
        self.partikel = lebend

    def zeichne(self, surf, font_klein):
        for p in self.partikel:
            alpha = p.leben / p.max_leben
            if p.text:
                surf_txt = font_klein.render(p.text, True,
                    tuple(int(c * alpha) for c in p.farbe))
                surf.blit(surf_txt, (int(p.x), int(p.y)))
            else:
                groesse = int(p.groesse * alpha)
                if groesse > 0:
                    farbe = tuple(int(c * alpha) for c in p.farbe)
                    pygame.draw.circle(surf, farbe, (int(p.x), int(p.y)), groesse)

# ═══════════════════════════════════════════════════════════════════
#  NAMEN-GENERATOR FÜR PERSONAL
# ═══════════════════════════════════════════════════════════════════

VORNAMEN = ["Mario", "Luigi", "Sofia", "Elena", "Marco", "Anna",
            "Luca", "Giulia", "Francesco", "Isabella", "Matteo",
            "Chiara", "Lorenzo", "Valentina", "Andrea", "Francesca",
            "Alessandro", "Martina", "Riccardo", "Alessia"]
NACHNAMEN = ["Rossi", "Ferrari", "Esposito", "Romano", "Colombo",
             "Ricci", "Marino", "Greco", "Bruno", "Gallo",
             "Conti", "De Luca", "Costa", "Giordano", "Mancini"]

def zufalls_name():
    return f"{random.choice(VORNAMEN)} {random.choice(NACHNAMEN)}"

# ═══════════════════════════════════════════════════════════════════
#  HAUPT-SPIEL
# ═══════════════════════════════════════════════════════════════════

class PizzeriaImperium:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_titel  = pygame.font.SysFont("arial", 42, bold=True)
        self.font_gross   = pygame.font.SysFont("arial", 28, bold=True)
        self.font_normal  = pygame.font.SysFont("arial", 20)
        self.font_klein   = pygame.font.SysFont("arial", 15)
        self.font_winzig  = pygame.font.SysFont("arial", 12)
        self.font_emoji   = pygame.font.SysFont("segoeui", 20)

        self.state = GameState()
        self.partikel = PartikelSystem()
        self.benachrichtigungen: list[Benachrichtigung] = []

        # Spielobjekte
        self.kunden: list[Kunde] = []
        self.personal: list[Personal] = []
        self.pizzen_im_ofen: list[Optional[Pizza]] = []
        self.fertige_pizzen: list[Pizza] = []
        self.active_powerups: list[ActivePowerup] = []
        self.aktive_forschung: Optional[ForschungsFortschritt] = None

        # Zähler
        self.naechste_kunden_id = 0
        self.naechstes_personal_id = 0
        self.kunden_timer = 0.0
        self.gehalt_timer = 0.0
        self.ereignis_timer = random.uniform(60, 120)

        # Multiplier (Forschung)
        self.mult_backzeit = 1.0
        self.mult_geduld = 1.0
        self.mult_kunden = 1.0
        self.mult_preis = 1.0
        self.auto_system = False

        # UI-Zustände
        self.screen_state = "menu"   # menu, schwierigkeit, spiel, pause, highscore,
                                     # achievement, forschung, game_over, level_up, ereignis
        self.ausgewaehlter_personal = -1
        self.ausgewaehlte_pizza = "Margherita"
        self.hover_tooltip = ""

        # Aktives Ereignis
        self.aktuelles_ereignis: Optional[dict] = None
        self.ereignis_timer2 = 0.0

        # Level-Up Animation
        self.level_up_timer = 0.0
        self.level_up_partikel_timer = 0.0

        # Hintergrund-Animation
        self.bg_anim = 0.0
        self.sterne = [(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H),
                        random.uniform(0.5, 2.0)) for _ in range(80)]

        # Menu Buttons
        self._init_menu_buttons()

        # Highscores laden
        self.highscores = self._lade_highscores()

        # Speicherstand prüfen
        self.speicherstand_vorhanden = os.path.exists(SAVE_FILE)

        # Combo-Anzeige
        self.combo_display_timer = 0.0

        # Tisch-Positionen
        self.tisch_positionen: list[tuple] = []

        # Nachrichten-Queue
        self.nachrichten_queue: list[tuple] = []

        # Statistik
        self.stats_minute_geld = 0.0
        self.stats_timer = 0.0

        # Power-Up Buttons
        self.powerup_btns: Dict[str, Button] = {}

        # Personal Menu
        self.personal_menu = None
        self.personal_btn = None

    def _init_menu_buttons(self):
        cx = SCREEN_W // 2
        self.btn_neues_spiel = Button(cx - 140, 300, 280, 55, "Neues Spiel", C_ACCENT)
        self.btn_weiterspielen = Button(cx - 140, 370, 280, 55, "Weiterspielen", C_GREEN)
        self.btn_highscores = Button(cx - 140, 440, 280, 55, "Highscores", C_BLUE)
        self.btn_beenden = Button(cx - 140, 510, 280, 55, "Beenden", C_RED)

        # Schwierigkeit
        self.btn_schwierig = {}
        for i, (name, daten) in enumerate(SCHWIERIGKEITSGRADE.items()):
            self.btn_schwierig[name] = Button(
                cx - 160, 200 + i * 80, 320, 60, name, daten["farbe"]
            )

        # Spiel-Buttons (Seitenleiste rechts)
        self.btn_pause     = Button(SCREEN_W - 115, 10, 105, 35, "Pause",   C_GRAY, klein=True)
        self.btn_speichern = Button(SCREEN_W - 230, 10, 105, 35, "Speichern",C_TEAL, klein=True)
        self.btn_menu_hs   = Button(SCREEN_W - 345, 10, 105, 35, "Scores",  C_BLUE, klein=True)
        self.btn_ach       = Button(SCREEN_W - 460, 10, 105, 35, "Trophäen",C_GOLD, klein=True)
        self.btn_forschung = Button(SCREEN_W - 575, 10, 105, 35, "Forschg", C_PURPLE, klein=True)

    def _init_powerup_buttons(self):
        """Initialisiert Power-Up Buttons für das Spiel-UI."""
        self.powerup_btns = {}
        for i, (name, daten) in enumerate(POWERUPS.items()):
            col = i % 4
            row = i // 4
            x = 205 + col * 190
            y = SCREEN_H - 108 + row * 35
            self.powerup_btns[name] = Button(
                x, y, 185, 28,
                f"{daten['icon']} {name}",
                daten["farbe"], klein=True,
                tooltip=daten["beschreibung"]
            )

    def _init_personal_ui(self):
        """Initialisiert Personal-UI-Elemente."""
        self.personal_btn = Button(
            SCREEN_W - 195, SCREEN_H // 2 + 30, 185, 35,
            "👤 Personal +", C_PURPLE, klein=True
        )
        self.personal_menu = PersonalMenu(self)

    def _init_spiel(self):
        """Setzt Spielobjekte zurück und bereitet ein neues Spiel vor."""
        level_data = LEVELS[self.state.level]
        self.pizzen_im_ofen = [None] * level_data["ofen_slots"]
        self.kunden = []
        self.personal = []
        self.fertige_pizzen = []
        self.active_powerups = []
        self.aktive_forschung = None
        self.naechste_kunden_id = 0
        self.naechstes_personal_id = 0
        self.kunden_timer = 5.0
        self.gehalt_timer = 30.0
        self.ereignis_timer = random.uniform(60, 120)
        self.combo_display_timer = 0.0

        # Multiplier zurücksetzen
        self.mult_backzeit = 1.0
        self.mult_geduld = 1.0
        self.mult_kunden = 1.0
        self.mult_preis = 1.0
        self.auto_system = False

        # Forschungs-Effekte erneut anwenden
        for fid in self.state.forschungen_abgeschlossen:
            self._forschung_anwenden(fid)

        # Tisch-Positionen berechnen
        self._berechne_tische()

        # Pizzen freischalten je nach Level
        self._pizzen_freischalten()

    def _pizzen_freischalten(self):
        alle = list(PIZZEN.keys())
        max_idx = min(2 + self.state.level * 1, len(alle))
        for p in alle[:max_idx]:
            if p not in self.state.freigeschaltete_pizzen:
                self.state.freigeschaltete_pizzen.append(p)
                self._benachrichtigung(f"🍕 Neue Pizza: {p}!", C_ACCENT)

    def _berechne_tische(self):
        self.tisch_positionen = []
        level_data = LEVELS[self.state.level]
        n = level_data["max_tische"]
        # Tische im mittleren Bereich des Spielfeldes
        spielfeld_x1 = 210
        spielfeld_x2 = SCREEN_W - 220
        spielfeld_y1 = 60
        spielfeld_y2 = SCREEN_H - 150
        breite = spielfeld_x2 - spielfeld_x1
        hoehe  = spielfeld_y2 - spielfeld_y1
        cols = max(1, int(math.sqrt(n * breite / hoehe)))
        rows = math.ceil(n / cols)
        for i in range(n):
            col = i % cols
            row = i // cols
            x = spielfeld_x1 + (col + 0.5) * (breite / cols)
            y = spielfeld_y1 + (row + 0.5) * (hoehe / rows)
            self.tisch_positionen.append((x, y))

    # ─── Spieler-Aktionen ─────────────────────────────────────────

    def pizza_in_ofen(self, slot: int):
        if slot >= len(self.pizzen_im_ofen):
            return
        if self.pizzen_im_ofen[slot] is not None:
            self._benachrichtigung("Ofen ist belegt!", C_RED)
            return
        if not self.state.freigeschaltete_pizzen:
            return
        if self.ausgewaehlte_pizza not in self.state.freigeschaltete_pizzen:
            self.ausgewaehlte_pizza = self.state.freigeschaltete_pizzen[0]

        # Zutatenkosten (günstiger mit Power-Up)
        zutat_rabatt = self._get_powerup_effekt("zutat_rabatt")
        kosten = 2 * zutat_rabatt
        if self.state.geld < kosten:
            self._benachrichtigung("Nicht genug Geld für Zutaten!", C_RED)
            return

        self.state.geld -= kosten
        p = Pizza(
            name=self.ausgewaehlte_pizza,
            backzeit=PIZZEN[self.ausgewaehlte_pizza]["zeit"] * self.mult_backzeit
        )
        self.pizzen_im_ofen[slot] = p
        self._benachrichtigung(f"🔥 {p.name} im Ofen!", C_ACCENT, kurz=True)

    def pizza_aus_ofen(self, slot: int):
        if slot >= len(self.pizzen_im_ofen):
            return
        pizza = self.pizzen_im_ofen[slot]
        if pizza is None:
            return
        if not pizza.fertig and not pizza.verbrannt:
            self._benachrichtigung("Pizza noch nicht fertig!", C_YELLOW)
            return

        if pizza.verbrannt:
            self._benachrichtigung("Verbrannte Pizza weggeworfen!", C_RED)
            self.partikel.add(SCREEN_W // 2, SCREEN_H // 2, C_RED, 15, "💨")
            self.pizzen_im_ofen[slot] = None
            self.state.fehler_serie += 1
            self.state.perfekte_serie = 0
            return

        self.pizzen_im_ofen[slot] = None
        self.fertige_pizzen.append(pizza)
        self.state.pizzen_gebacken += 1
        self.state.perfekte_serie += 1
        self._benachrichtigung(f"✅ {pizza.name} fertig!", C_GREEN, kurz=True)
        self.partikel.add(SCREEN_W // 2, 400, C_GREEN, 10)
        self._check_achievements()

    def pizza_servieren(self, pizza: Pizza, kunde: Kunde):
        """Servierfunktion — prüft ob Pizza zur Bestellung passt."""
        if pizza.name != kunde.pizza_name:
            # Falsche Pizza — negativer Effekt
            self._benachrichtigung(f"Falsche Pizza! Kunde wollte {kunde.pizza_name}!", C_RED)
            if pizza in self.fertige_pizzen:
                self.fertige_pizzen.remove(pizza)
            self.state.kunden_verloren += 1
            self.state.combo = 0
            return False

        # Korrekte Bestellung
        preis = PIZZEN[pizza.name]["preis"] * self.mult_preis
        preis *= self._get_powerup_effekt("preis_mult")
        if kunde.vip:
            preis *= self._get_powerup_effekt("vip_mult")
        schwierig = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]
        preis *= schwierig["preis_mult"]  # KORRIGIERT: Nur einmal anwenden

        # Trinkgeld je nach verbleibender Geduld
        geduld_bonus = (kunde.geduld / kunde.max_geduld) * 0.3
        endpreis = preis * (1 + geduld_bonus)
        if kunde.vip:
            endpreis *= 2.0

        self.state.geld += endpreis
        self.state.gesamt_verdient += endpreis
        self.state.kunden_bedient += 1
        self.state.zufriedene_kunden += 1
        self.state.minuten_umsatz += endpreis
        self.state.combo += 1
        if self.state.combo > self.state.max_combo:
            self.state.max_combo = self.state.combo

        if pizza in self.fertige_pizzen:
            self.fertige_pizzen.remove(pizza)
        if kunde in self.kunden:
            self.kunden.remove(kunde)
        if kunde.tisch_id >= 0:
            pass  # Tisch wird automatisch frei

        if kunde.vip:
            self.state.vip_kunden_bedient += 1
            self.partikel.add(kunde.x, kunde.y, C_GOLD, 20, f"⭐ {fmt_geld(endpreis)}")
        else:
            self.partikel.add(kunde.x, kunde.y, C_GREEN, 10, fmt_geld(endpreis))

        self._benachrichtigung(
            f"🎉 +{fmt_geld(endpreis)}" + (" VIP!" if kunde.vip else ""),
            C_GOLD if kunde.vip else C_GREEN
        )

        self._check_achievements()
        self._check_level_up()
        return True

    def personal_einstellen(self, typ: str):
        level_data = LEVELS[self.state.level]
        if len(self.personal) >= level_data["max_personal"]:
            self._benachrichtigung("Maximales Personal erreicht!", C_RED)
            return
        lohn_daten = PERSONAL_TYPEN[typ]
        einstellkosten = lohn_daten["gehalt"] * 5
        if self.state.geld < einstellkosten:
            self._benachrichtigung(f"Nicht genug Geld! Brauche {fmt_geld(einstellkosten)}", C_RED)
            return

        self.state.geld -= einstellkosten
        p = Personal(
            id=self.naechstes_personal_id,
            typ=typ,
            name=zufalls_name(),
            x=random.uniform(250, SCREEN_W - 250),
            y=random.uniform(100, SCREEN_H - 200),
        )
        self.naechstes_personal_id += 1
        self.personal.append(p)
        self._benachrichtigung(f"👤 {p.name} eingestellt ({typ})", C_BLUE)
        self._check_achievements()

    def powerup_aktivieren(self, name: str):
        daten = POWERUPS[name]
        if self.state.geld < daten["kosten"]:
            self._benachrichtigung("Nicht genug Geld!", C_RED)
            return

        # Prüfe ob schon aktiv
        for ap in self.active_powerups:
            if ap.name == name:
                self._benachrichtigung(f"{name} ist bereits aktiv!", C_YELLOW)
                return

        self.state.geld -= daten["kosten"]
        self.active_powerups.append(ActivePowerup(
            name=name,
            verbleibend=daten["dauer"],
            gesamt=daten["dauer"]
        ))
        self.state.powerups_benutzt += 1
        self._benachrichtigung(f"⚡ {name} aktiviert!", daten["farbe"])
        self.partikel.add(SCREEN_W // 2, SCREEN_H // 2, daten["farbe"], 20, name)
        self._check_achievements()

    def forschung_starten(self, fid: str):
        if self.aktive_forschung is not None:
            self._benachrichtigung("Bereits eine Forschung aktiv!", C_YELLOW)
            return
        f = next((x for x in FORSCHUNGEN if x["id"] == fid), None)
        if f is None:
            return
        if fid in self.state.forschungen_abgeschlossen:
            self._benachrichtigung("Bereits erforscht!", C_GRAY)
            return
        # Voraussetzungen prüfen
        for v in f["voraus"]:
            if v not in self.state.forschungen_abgeschlossen:
                self._benachrichtigung("Voraussetzung fehlt!", C_RED)
                return
        if self.state.geld < f["kosten"]:
            self._benachrichtigung(f"Brauche {fmt_geld(f['kosten'])}!", C_RED)
            return

        self.state.geld -= f["kosten"]
        self.aktive_forschung = ForschungsFortschritt(
            id=fid,
            verbleibend=f["dauer"],
            gesamt=f["dauer"]
        )
        self._benachrichtigung(f"🔬 Forschung gestartet: {f['name']}", C_PURPLE)

    # ─── Interne Hilfsmethoden ────────────────────────────────────

    def _get_powerup_effekt(self, effekt: str) -> float:
        for ap in self.active_powerups:
            daten = POWERUPS[ap.name]
            if daten["effekt"] == effekt:
                return daten["wert"]
        return 1.0

    def _forschung_anwenden(self, fid: str):
        f = next((x for x in FORSCHUNGEN if x["id"] == fid), None)
        if f is None:
            return
        eff = f["effekt"]
        val = f["wert"]
        if eff == "backzeit_mult":
            self.mult_backzeit *= val
        elif eff == "geduld_mult":
            self.mult_geduld *= val
        elif eff == "kunden_mult":
            self.mult_kunden *= val
        elif eff == "preis_mult":
            self.mult_preis *= val
        elif eff in ("auto_teil", "auto_voll"):
            self.auto_system = True

    def _benachrichtigung(self, text: str, farbe=C_WHITE, kurz=False):
        timer = 1.5 if kurz else 3.0
        # Alte verschieben
        for b in self.benachrichtigungen:
            b.y_offset -= 30
        self.benachrichtigungen.append(Benachrichtigung(text=text, farbe=farbe, timer=timer))
        if len(self.benachrichtigungen) > 8:
            self.benachrichtigungen.pop(0)

    def _check_achievements(self):
        unlocked = self.state.achievements_erhalten

        def check(aid, bedingung):
            if aid not in unlocked and bedingung:
                unlocked.append(aid)
                ach = next(a for a in ACHIEVEMENTS if a["id"] == aid)
                self.state.xp += ach["xp"]
                self._benachrichtigung(f"🏆 Achievement: {ach['name']}! +{ach['xp']}XP", C_GOLD)
                self.partikel.add(SCREEN_W // 2, 300, C_GOLD, 30, "🏆")

        check("erste_pizza",    self.state.pizzen_gebacken >= 1)
        check("10_pizzen",      self.state.pizzen_gebacken >= 10)
        check("100_pizzen",     self.state.pizzen_gebacken >= 100)
        check("1000_pizzen",    self.state.pizzen_gebacken >= 1000)
        check("erstes_level",   self.state.level >= 1)
        check("level_5",        self.state.level >= 5)
        check("level_7",        self.state.level >= 7)
        check("1000_euro",      self.state.gesamt_verdient >= 1000)
        check("10000_euro",     self.state.gesamt_verdient >= 10000)
        check("100000_euro",    self.state.gesamt_verdient >= 100000)
        check("1000000_euro",   self.state.gesamt_verdient >= 1000000)
        check("kein_fehler",    self.state.perfekte_serie >= 10)
        check("5_personal",     len(self.personal) >= 5)
        check("alle_pizzen",    len(self.state.freigeschaltete_pizzen) >= len(PIZZEN))
        check("powerup_nutzen", self.state.powerups_benutzt >= 5)
        check("ereignis_10",    self.state.ereignisse_erlebt >= 10)
        check("zufrieden",      self.state.zufriedene_kunden >= 100)
        check("vip_10",         self.state.vip_kunden_bedient >= 10)
        check("combo_5",        self.state.combo >= 5)
        check("spielzeit_1h",   self.state.spielzeit >= 3600)
        check("nacht_schicht",  datetime.datetime.now().hour >= 22)
        check("erste_krise",    self.state.ereignisse_erlebt >= 1)
        check("forschung_5",    len(self.state.forschungen_abgeschlossen) >= 5)
        check("erste_forschung",len(self.state.forschungen_abgeschlossen) >= 1)
        check("sparfuchs",      self.state.rabatt_kaeufe >= 50)
        check("preisrekord",    self.state.max_minuten_umsatz >= 500)

        # Vollhaus
        besetzt = sum(1 for k in self.kunden if k.tisch_id >= 0)
        level_data = LEVELS[self.state.level]
        check("vollhaus",       besetzt >= level_data["max_tische"])

    def _check_level_up(self):
        if self.state.level >= len(LEVELS) - 1:
            return
        ziel = LEVELS[self.state.level]["ziel_geld"]
        if self.state.gesamt_verdient >= ziel:
            self.state.level += 1
            self.screen_state = "level_up"
            self.level_up_timer = 4.0
            self._init_spiel()
            self._check_achievements()
            self._speichern()

    def _neuer_kunde(self):
        level_data = LEVELS[self.state.level]
        if len(self.kunden) >= level_data["max_kunden"]:
            return

        # VIP-Chance steigt mit Level
        vip = random.random() < (0.05 + self.state.level * 0.02)

        # Freien Tisch suchen
        belegte_tische = {k.tisch_id for k in self.kunden if k.tisch_id >= 0}
        freie_tische = [i for i in range(len(self.tisch_positionen)) if i not in belegte_tische]
        if not freie_tische:
            return

        tisch_id = random.choice(freie_tische)
        tx, ty = self.tisch_positionen[tisch_id]

        # Pizza-Bestellung (bevorzugt beliebte Pizzen)
        verfuegbar = self.state.freigeschaltete_pizzen
        gewichte = [PIZZEN[p]["beliebt"] for p in verfuegbar]
        pizza = random.choices(verfuegbar, weights=gewichte)[0]

        schwierig = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]
        geduld = 100.0 * schwierig["kunden_geduld_mult"] * self.mult_geduld
        geduld *= self._get_powerup_effekt("geduld_mult")

        emojis_normal = ["😊", "😄", "🙂", "😋", "🤤"]
        emojis_vip    = ["🤵", "👑", "💎", "⭐", "🎩"]
        emoji = random.choice(emojis_vip if vip else emojis_normal)

        kunde = Kunde(
            id=self.naechste_kunden_id,
            pizza_name=pizza,
            geduld=geduld,
            max_geduld=geduld,
            vip=vip,
            x=random.choice([-30, SCREEN_W + 30]),
            y=ty,
            ziel_x=tx,
            ziel_y=ty,
            tisch_id=tisch_id,
            emoji=emoji,
        )
        self.naechste_kunden_id += 1
        self.kunden.append(kunde)

    def _zufallsereignis(self):
        ereignis = random.choice(EREIGNISSE)
        wert = random.randint(*ereignis["wert_range"])
        self.state.ereignisse_erlebt += 1

        beschreibung = ereignis["beschreibung"].replace("{wert}", str(wert))
        self.aktuelles_ereignis = {
            "name": ereignis["name"],
            "beschreibung": beschreibung,
            "typ": ereignis["typ"],
            "wert": wert,
            "farbe": ereignis["farbe"],
        }
        self.ereignis_timer2 = 5.0

        if ereignis["typ"] == "negativ":
            self.state.geld = max(0, self.state.geld - wert)
            if self.state.geld <= 0:
                self.screen_state = "game_over"
        else:
            self.state.geld += wert
            self.state.gesamt_verdient += wert

        self.screen_state = "ereignis"
        self._check_achievements()

    def _auto_spielzug(self, dt):
        """Automatische Aktionen für Personal."""
        for mitarbeiter in self.personal:
            data = PERSONAL_TYPEN[mitarbeiter.typ]
            speed = data["geschwindigkeit"] * self._get_powerup_effekt("personal_speed")
            mitarbeiter.task_timer -= dt * speed

            if mitarbeiter.task_timer > 0:
                continue

            if mitarbeiter.typ == "Manager":
                # Manager bucht automatisch Pizzen
                for i, slot in enumerate(self.pizzen_im_ofen):
                    if slot is None and self.state.geld >= 2:
                        # Welche Pizza braucht ein wartender Kunde?
                        for k in self.kunden:
                            if any(fp.name == k.pizza_name for fp in self.fertige_pizzen):
                                continue
                            if k.pizza_name in self.state.freigeschaltete_pizzen:
                                kosten = 2 * self._get_powerup_effekt("zutat_rabatt")
                                self.state.geld -= kosten
                                p = Pizza(
                                    name=k.pizza_name,
                                    backzeit=PIZZEN[k.pizza_name]["zeit"] * self.mult_backzeit,
                                    bestellt_von=k.id
                                )
                                self.pizzen_im_ofen[i] = p
                                mitarbeiter.task_timer = 5.0
                                break

            elif mitarbeiter.typ in ("Koch", "Chefkoch", "Lehrling", "Superstar"):
                # Koch backt automatisch
                for i, slot in enumerate(self.pizzen_im_ofen):
                    if slot is not None and slot.fertig:
                        self.pizza_aus_ofen(i)
                        mitarbeiter.task_timer = 3.0 / speed
                        break
                    elif slot is None and self.kunden and self.state.geld >= 2:
                        # Passende Pizza für Kunden
                        for k in self.kunden:
                            if k.pizza_name in self.state.freigeschaltete_pizzen:
                                kosten = 2 * self._get_powerup_effekt("zutat_rabatt")
                                self.state.geld -= kosten
                                p = Pizza(
                                    name=k.pizza_name,
                                    backzeit=PIZZEN[k.pizza_name]["zeit"] * self.mult_backzeit,
                                    bestellt_von=k.id
                                )
                                self.pizzen_im_ofen[i] = p
                                mitarbeiter.task_timer = 8.0 / speed
                                break
                        break

            elif mitarbeiter.typ in ("Kellner",):
                # Kellner serviert automatisch
                for fp in list(self.fertige_pizzen):
                    for k in list(self.kunden):
                        if fp.name == k.pizza_name:
                            self.pizza_servieren(fp, k)
                            mitarbeiter.task_timer = 4.0 / speed
                            break
                    break

            if mitarbeiter.task_timer <= 0:
                mitarbeiter.task_timer = random.uniform(2, 5)

            # Animations-Update
            mitarbeiter.animation += dt * 2
            mitarbeiter.x += math.sin(mitarbeiter.animation) * 0.3
            mitarbeiter.y += math.cos(mitarbeiter.animation * 0.7) * 0.2

    # ─── Speichern / Laden ────────────────────────────────────────

    def _speichern(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state.zu_dict(), f, indent=2, ensure_ascii=False)
            self._benachrichtigung("💾 Gespeichert!", C_TEAL, kurz=True)
        except Exception as e:
            self._benachrichtigung(f"Speichern fehlgeschlagen: {e}", C_RED)

    def _laden(self):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state.von_dict(data)
            self._benachrichtigung("📂 Spielstand geladen!", C_TEAL)
            return True
        except Exception as e:
            self._benachrichtigung(f"Laden fehlgeschlagen: {e}", C_RED)
            return False

    def _lade_highscores(self) -> list:
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _speichere_highscore(self):
        entry = {
            "name": "Spieler",
            "geld": self.state.gesamt_verdient,
            "level": self.state.level,
            "pizzen": self.state.pizzen_gebacken,
            "schwierigkeit": self.state.schwierigkeit,
            "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.highscores.append(entry)
        self.highscores.sort(key=lambda x: x["geld"], reverse=True)
        self.highscores = self.highscores[:20]
        try:
            with open(SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.highscores, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════
    #  UPDATE-LOGIK
    # ═══════════════════════════════════════════════════════════════

    def update(self, dt: float):
        self.bg_anim += dt * 0.3
        self.partikel.update(dt)

        # Benachrichtigungen
        for b in list(self.benachrichtigungen):
            b.timer -= dt
            if b.timer <= 0:
                self.benachrichtigungen.remove(b)

        if self.screen_state == "spiel":
            self._update_spiel(dt)
        elif self.screen_state == "level_up":
            self.level_up_timer -= dt
            self.level_up_partikel_timer -= dt
            if self.level_up_partikel_timer <= 0:
                self.level_up_partikel_timer = 0.1
                for _ in range(5):
                    self.partikel.add(
                        random.randint(0, SCREEN_W),
                        random.randint(0, SCREEN_H),
                        random.choice([C_GOLD, C_ACCENT, C_GREEN, C_BLUE, C_PURPLE]),
                        anzahl=3
                    )
            if self.level_up_timer <= 0:
                self.screen_state = "spiel"
        elif self.screen_state == "ereignis":
            self.ereignis_timer2 -= dt
            if self.ereignis_timer2 <= 0:
                self.screen_state = "spiel"
                self.aktuelles_ereignis = None

    def _update_spiel(self, dt: float):
        self.state.spielzeit += dt

        # Minuten-Umsatz tracken
        if not hasattr(self.state, 'minuten_timer'):
            self.state.minuten_timer = 0
        self.state.minuten_timer += dt
        if self.state.minuten_timer >= 60:
            self.state.minuten_timer -= 60
            if self.state.minuten_umsatz > self.state.max_minuten_umsatz:
                self.state.max_minuten_umsatz = self.state.minuten_umsatz
            self.state.minuten_umsatz = 0

        # Statistik-Timer
        self.stats_timer += dt

        # Kunden spawnen
        schwierig = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]
        kunden_intervall = max(3.0, 12.0 / self.mult_kunden / self._get_powerup_effekt("kunden_mult"))
        # KORRIGIERT: Kein Zugriff auf nicht-existierenden Schlüssel 'kunden_mult'
        self.kunden_timer -= dt
        if self.kunden_timer <= 0:
            self._neuer_kunde()
            self.kunden_timer = kunden_intervall / max(0.1, self._get_powerup_effekt("kunden_mult"))
            if random.random() < 0.3:
                self._neuer_kunde()

        # Kunden updaten
        for k in list(self.kunden):
            # Bewegung zum Tisch
            dx = k.ziel_x - k.x
            dy = k.ziel_y - k.y
            d = math.sqrt(dx**2 + dy**2)
            if d > 2:
                speed = 120
                k.x += (dx / d) * speed * dt
                k.y += (dy / d) * speed * dt

            # Geduld abnehmen (nur wenn am Tisch)
            if d < 10:
                k.geduld -= dt * (8 / schwierig["kunden_geduld_mult"])
                k.geduld -= dt * (8 / self.mult_geduld)

            # Ungedulds-Emoji
            geduld_anteil = k.geduld / k.max_geduld
            if geduld_anteil < 0.3 and not k.ungeduldig:
                k.ungeduldig = True
                k.emoji = "😠"
            elif geduld_anteil < 0.6:
                k.emoji = "😕"

            # Kunde geht
            if k.geduld <= 0:
                self.kunden.remove(k)
                self.state.kunden_verloren += 1
                self.state.combo = 0
                self._benachrichtigung("😢 Kunde gegangen!", C_RED, kurz=True)
                self.partikel.add(k.x, k.y, C_RED, 5, "😠")

            # Animation
            k.animation_timer += dt

        # Pizzen im Ofen backen
        backzeit_mult = self.mult_backzeit * self._get_powerup_effekt("backzeit_mult")
        for pizza in self.pizzen_im_ofen:
            if pizza is None or pizza.fertig or pizza.verbrannt:
                continue
            pizza.fortschritt += dt * (1.0 / pizza.backzeit) * (1.0 / backzeit_mult)
            if pizza.fortschritt >= 1.0:
                pizza.fertig = True
                pizza.fortschritt = 1.0
                self._benachrichtigung(f"🍕 {pizza.name} fertig!", C_ACCENT, kurz=True)
            elif pizza.fortschritt >= 1.3:
                pizza.verbrannt = True
                pizza.fertig = False

        # Gehalt bezahlen
        self.gehalt_timer -= dt
        if self.gehalt_timer <= 0:
            self.gehalt_timer = 30.0
            gesamt_gehalt = 0
            schwierig_kosten = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]["kosten_mult"]
            for p in self.personal:
                gehalt = PERSONAL_TYPEN[p.typ]["gehalt"] * schwierig_kosten
                gesamt_gehalt += gehalt
            if gesamt_gehalt > 0:
                self.state.geld -= gesamt_gehalt
                self._benachrichtigung(f"💸 Gehalt: -{fmt_geld(gesamt_gehalt)}", C_GRAY, kurz=True)
                if self.state.geld < 0:
                    self.state.geld = 0
                    self.screen_state = "game_over"
                    self._speichere_highscore()

        # Power-Ups ablaufen lassen
        for ap in list(self.active_powerups):
            ap.verbleibend -= dt
            if ap.verbleibend <= 0:
                self.active_powerups.remove(ap)
                self._benachrichtigung(f"Power-Up {ap.name} abgelaufen", C_GRAY, kurz=True)

        # Forschung vorantreiben
        if self.aktive_forschung is not None:
            self.aktive_forschung.verbleibend -= dt
            if self.aktive_forschung.verbleibend <= 0:
                fid = self.aktive_forschung.id
                self.state.forschungen_abgeschlossen.append(fid)
                f = next(x for x in FORSCHUNGEN if x["id"] == fid)
                self._forschung_anwenden(fid)
                self._benachrichtigung(f"🔬 Forschung abgeschlossen: {f['name']}!", C_PURPLE)
                self.aktive_forschung = None
                self._check_achievements()

        # Zufallsereignis
        self.ereignis_timer -= dt
        if self.ereignis_timer <= 0:
            self.ereignis_timer = random.uniform(60, 180)
            chance = SCHWIERIGKEITSGRADE[self.state.schwierigkeit]["ereignis_chance"]
            if random.random() < chance * 100:
                self._zufallsereignis()

        # Auto-Spielzug (Personal)
        self._auto_spielzug(dt)

        # Combo Display
        if self.state.combo > 0:
            self.combo_display_timer = 2.0
        else:
            self.combo_display_timer = max(0, self.combo_display_timer - dt)

        # Achievements regelmäßig prüfen
        if int(self.state.spielzeit * 10) % 50 == 0:
            self._check_achievements()

    # ═══════════════════════════════════════════════════════════════
    #  ZEICHNEN
    # ═══════════════════════════════════════════════════════════════

    def draw(self):
        if self.screen_state == "menu":
            self._draw_menu()
        elif self.screen_state == "schwierigkeit":
            self._draw_schwierigkeit()
        elif self.screen_state in ("spiel", "pause"):
            self._draw_spiel()
            if self.screen_state == "pause":
                self._draw_pause_overlay()
        elif self.screen_state == "level_up":
            self._draw_spiel()
            self._draw_level_up()
        elif self.screen_state == "ereignis":
            self._draw_spiel()
            self._draw_ereignis()
        elif self.screen_state == "highscore":
            self._draw_highscores()
        elif self.screen_state == "achievement":
            self._draw_achievements()
        elif self.screen_state == "forschung":
            self._draw_forschung()
        elif self.screen_state == "game_over":
            self._draw_game_over()

        pygame.display.flip()

    def _draw_hintergrund(self):
        self.screen.fill(C_BG)
        # Sterne
        for (sx, sy, sz) in self.sterne:
            hell = int(100 + 60 * math.sin(self.bg_anim + sx * 0.05))
            groesse = max(1, int(sz * (0.8 + 0.2 * math.sin(self.bg_anim + sy * 0.03))))
            pygame.draw.circle(self.screen, (hell, hell, hell + 30), (sx, sy), groesse)

    def _draw_menu(self):
        self._draw_hintergrund()

        # Titel-Glow
        for i in range(3, 0, -1):
            surf = self.font_titel.render("🍕 PIZZERIA IMPERIUM 🍕", True,
                tuple(min(255, c + 30) for c in C_ACCENT))
            self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2 - i,
                                    150 - i))

        zeichne_text(self.screen, "🍕 PIZZERIA IMPERIUM 🍕",
                     SCREEN_W // 2, 150, self.font_titel, C_ACCENT, center=True)
        zeichne_text(self.screen, "Baue dein Pizza-Imperium!",
                     SCREEN_W // 2, 210, self.font_normal, C_GRAY, center=True)
        zeichne_text(self.screen, f"Version 1.0  •  {datetime.date.today()}",
                     SCREEN_W // 2, 240, self.font_klein, C_DARKGRAY, center=True)

        btns = [self.btn_neues_spiel, self.btn_highscores, self.btn_beenden]
        if self.speicherstand_vorhanden:
            btns.insert(1, self.btn_weiterspielen)
        for b in btns:
            b.zeichne(self.screen, self.font_normal, self.font_klein)

        # Footer
        zeichne_text(self.screen, "SPACE=Pause  S=Speichern  H=Highscores  A=Achievements  R=Forschung",
                     SCREEN_W // 2, SCREEN_H - 30, self.font_winzig, C_DARKGRAY, center=True)

        self.partikel.zeichne(self.screen, self.font_klein)

    def _draw_schwierigkeit(self):
        self._draw_hintergrund()
        zeichne_text(self.screen, "Schwierigkeitsgrad wählen",
                     SCREEN_W // 2, 120, self.font_gross, C_WHITE, center=True)
        zeichne_text(self.screen, "Wähle deinen Herausforderungslevel:",
                     SCREEN_W // 2, 160, self.font_normal, C_GRAY, center=True)

        for name, btn in self.btn_schwierig.items():
            btn.zeichne(self.screen, self.font_normal, self.font_klein)
            daten = SCHWIERIGKEITSGRADE[name]
            zeichne_text(self.screen, daten["beschreibung"],
                         btn.rect.right + 20, btn.rect.centery - 8,
                         self.font_klein, C_GRAY)

        zeichne_text(self.screen, "ESC = Zurück",
                     SCREEN_W // 2, SCREEN_H - 40, self.font_klein, C_GRAY, center=True)

    def _draw_spiel(self):
        level_data = LEVELS[self.state.level]
        bg = level_data["hintergrund"]
        self.screen.fill(bg)

        # Sterne
        for (sx, sy, sz) in self.sterne[:40]:
            hell = int(60 + 30 * math.sin(self.bg_anim + sx * 0.05))
            pygame.draw.circle(self.screen, (hell, hell, hell + 20), (sx, sy), max(1, int(sz)))

        # Hauptbereiche
        self._draw_linke_seitenleiste()
        self._draw_spielfeld()
        self._draw_rechte_seitenleiste()
        self._draw_top_leiste()
        self._draw_bottom_leiste()

        # Partikel
        self.partikel.zeichne(self.screen, self.font_klein)

        # Benachrichtigungen
        self._draw_benachrichtigungen()

        # Combo
        if self.combo_display_timer > 0 and self.state.combo >= 2:
            self._draw_combo()

        # Aktives Powerup-Leiste
        self._draw_powerup_leiste()

    def _draw_top_leiste(self):
        zeichne_rect_rund(self.screen, C_PANEL, (0, 0, SCREEN_W, 50), radius=0)

        # Geld
        zeichne_text(self.screen, fmt_geld(self.state.geld),
                     160, 15, self.font_gross, C_GOLD)
        zeichne_text(self.screen, "💰",  10, 15, self.font_normal)
        zeichne_text(self.screen, "Gesamt: " + fmt_geld(self.state.gesamt_verdient),
                     10, 35, self.font_winzig, C_GRAY)

        # Level + Ziel
        level_data = LEVELS[self.state.level]
        fortschritt = min(1.0, self.state.gesamt_verdient / level_data["ziel_geld"])
        zeichne_text(self.screen, f"Level {self.state.level}: {level_data['name']}",
                     SCREEN_W // 2, 8, self.font_normal, C_ACCENT, center=True)
        zeichne_balken(self.screen, SCREEN_W // 2 - 150, 30, 300, 12,
                       self.state.gesamt_verdient, level_data["ziel_geld"],
                       C_ACCENT, C_DARKGRAY)
        zeichne_text(self.screen,
                     f"Ziel: {fmt_geld(level_data['ziel_geld'])} ({fortschritt*100:.0f}%)",
                     SCREEN_W // 2, 32, self.font_winzig, C_WHITE, center=True)

        # Zeit + Buttons
        zeichne_text(self.screen, f"⏱ {fmt_zeit(self.state.spielzeit)}",
                     SCREEN_W - 620, 15, self.font_klein, C_GRAY)

        for btn in [self.btn_pause, self.btn_speichern, self.btn_menu_hs,
                    self.btn_ach, self.btn_forschung]:
            btn.zeichne(self.screen, self.font_normal, self.font_klein)

    def _draw_bottom_leiste(self):
        y = SCREEN_H - 110
        zeichne_rect_rund(self.screen, C_PANEL, (0, y, SCREEN_W, 110), radius=0)

        # Pizza-Auswahl
        zeichne_text(self.screen, "Pizza wählen:", 10, y + 5, self.font_klein, C_GRAY)
        pizza_x = 10
        for i, pname in enumerate(self.state.freigeschaltete_pizzen):
            farbe = C_PIZZAS.get(pname, C_ACCENT)
            ausgewaehlt = pname == self.ausgewaehlte_pizza
            pbreite = 90
            pr = pygame.Rect(pizza_x, y + 18, pbreite, 36)
            rand_farbe = C_WHITE if ausgewaehlt else farbe
            pygame.draw.rect(self.screen, farbe, pr, border_radius=6)
            if ausgewaehlt:
                pygame.draw.rect(self.screen, C_WHITE, pr, 2, border_radius=6)
            zeichne_text(self.screen, pname[:9], pr.centerx, pr.centery - 7,
                         self.font_winzig, C_WHITE, center=True)
            zeichne_text(self.screen, fmt_geld(PIZZEN[pname]["preis"]),
                         pr.centerx, pr.centery + 5,
                         self.font_winzig, C_GOLD, center=True)
            pizza_x += pbreite + 4
            if pizza_x > SCREEN_W - 100:
                break

        # Statistiken unten rechts
        stats = [
            f"🍕 Gebacken: {self.state.pizzen_gebacken}",
            f"😊 Bedient: {self.state.kunden_bedient}",
            f"😢 Verloren: {self.state.kunden_verloren}",
            f"⭐ XP: {self.state.xp}",
        ]
        for i, s in enumerate(stats):
            zeichne_text(self.screen, s,
                         SCREEN_W - 380 + i * 95, y + 8,
                         self.font_winzig, C_GRAY)

        # Schwierigkeit
        zeichne_text(self.screen,
                     f"Modus: {self.state.schwierigkeit}",
                     SCREEN_W - 200, y + 8, self.font_winzig,
                     SCHWIERIGKEITSGRADE[self.state.schwierigkeit]["farbe"])

        # Ofen-Slots Kurzinfo
        ofen_txt = f"Öfen: {sum(1 for o in self.pizzen_im_ofen if o is not None)}/{len(self.pizzen_im_ofen)}"
        zeichne_text(self.screen, ofen_txt, SCREEN_W - 120, y + 30, self.font_winzig, C_ACCENT)

    def _draw_linke_seitenleiste(self):
        """Linke Leiste: Öfen"""
        zeichne_rect_rund(self.screen, C_PANEL, (0, 50, 200, SCREEN_H - 160), radius=0)
        zeichne_text(self.screen, "🔥 Öfen", 100, 58, self.font_normal, C_ACCENT, center=True)

        for i, pizza in enumerate(self.pizzen_im_ofen):
            oy = 85 + i * 80
            ofen_rect = pygame.Rect(10, oy, 180, 70)

            if pizza is None:
                zeichne_rect_rund(self.screen, C_DARKGRAY, ofen_rect, radius=8)
                zeichne_text(self.screen, f"Ofen {i+1}: Leer",
                             100, oy + 12, self.font_klein, C_GRAY, center=True)
                zeichne_text(self.screen, "Klicken = Pizza rein",
                             100, oy + 32, self.font_winzig, C_DARKGRAY, center=True)
                zeichne_text(self.screen, "[LEERTASTE + Zahl]",
                             100, oy + 47, self.font_winzig, C_DARKGRAY, center=True)
            else:
                # Farbe nach Zustand
                if pizza.verbrannt:
                    farbe = C_RED
                    status = "VERBRANNT! Klicken"
                elif pizza.fertig:
                    farbe = C_GREEN
                    status = "Fertig! Klicken"
                else:
                    anteil = pizza.fortschritt
                    r = int(lerp(C_DARKGRAY[0], C_PIZZAS.get(pizza.name, C_ACCENT)[0], anteil))
                    g = int(lerp(C_DARKGRAY[1], C_PIZZAS.get(pizza.name, C_ACCENT)[1], anteil))
                    b = int(lerp(C_DARKGRAY[2], C_PIZZAS.get(pizza.name, C_ACCENT)[2], anteil))
                    farbe = (r, g, b)
                    status = f"{pizza.fortschritt*100:.0f}%"

                zeichne_rect_rund(self.screen, farbe, ofen_rect, radius=8)
                zeichne_text(self.screen, pizza.name,
                             100, oy + 5, self.font_klein, C_WHITE, center=True)

                if not pizza.fertig and not pizza.verbrannt:
                    zeichne_balken(self.screen, 15, oy + 25, 170, 10,
                                   pizza.fortschritt, 1.0, C_ACCENT2, C_DARKGRAY)

                zeichne_text(self.screen, status,
                             100, oy + 40, self.font_klein, C_WHITE, center=True)

                backzeit_verbleibend = max(0,
                    pizza.backzeit * (1 - pizza.fortschritt) * self.mult_backzeit)
                zeichne_text(self.screen, f"Noch: {backzeit_verbleibend:.0f}s",
                             100, oy + 55, self.font_winzig, C_GRAY, center=True)

    def _draw_rechte_seitenleiste(self):
        """Rechte Leiste: Kunden & Personal"""
        x0 = SCREEN_W - 200
        zeichne_rect_rund(self.screen, C_PANEL, (x0, 50, 200, SCREEN_H - 160), radius=0)

        # Kunden-Anzeige
        zeichne_text(self.screen, f"👥 Kunden ({len(self.kunden)})",
                     x0 + 100, 58, self.font_normal, C_BLUE, center=True)

        for i, k in enumerate(self.kunden[:6]):
            ky = 85 + i * 48
            kr = pygame.Rect(x0 + 5, ky, 190, 42)
            bg = (40, 40, 80) if k.vip else C_DARKGRAY
            zeichne_rect_rund(self.screen, bg, kr, radius=6)

            # Emoji + Name
            zeichne_text(self.screen, k.emoji, x0 + 10, ky + 5, self.font_normal)
            zeichne_text(self.screen, f"{k.pizza_name[:10]}",
                         x0 + 35, ky + 5, self.font_klein,
                         C_GOLD if k.vip else C_WHITE)
            if k.vip:
                zeichne_text(self.screen, "VIP", x0 + 155, ky + 5,
                             self.font_winzig, C_GOLD)

            # Gedulds-Balken
            farbe_geduld = (
                C_GREEN if k.geduld / k.max_geduld > 0.6 else
                C_YELLOW if k.geduld / k.max_geduld > 0.3 else
                C_RED
            )
            zeichne_balken(self.screen, x0 + 35, ky + 28, 155, 8,
                           k.geduld, k.max_geduld, farbe_geduld)

        if len(self.kunden) > 6:
            zeichne_text(self.screen, f"... +{len(self.kunden) - 6} weitere",
                         x0 + 100, 85 + 6 * 48 + 5, self.font_winzig, C_GRAY, center=True)

        # Personal-Anzeige
        personal_y = 85 + 6 * 48 + 30
        zeichne_text(self.screen, f"👤 Personal ({len(self.personal)})",
                     x0 + 100, personal_y, self.font_normal, C_PURPLE, center=True)

        for i, p in enumerate(self.personal[:4]):
            py = personal_y + 25 + i * 38
            pr = pygame.Rect(x0 + 5, py, 190, 32)
            zeichne_rect_rund(self.screen, C_PANEL2, pr, radius=6)
            typ_farbe = PERSONAL_TYPEN[p.typ]["farbe"]
            pygame.draw.rect(self.screen, typ_farbe, (x0 + 5, py, 4, 32))
            zeichne_text(self.screen, p.name[:14], x0 + 14, py + 4, self.font_winzig, C_WHITE)
            zeichne_text(self.screen, p.typ, x0 + 14, py + 16, self.font_winzig, typ_farbe)

        # Fertige Pizzen
        fertig_y = personal_y + 25 + len(self.personal) * 38 + 15
        if self.fertige_pizzen:
            zeichne_text(self.screen, "🍕 Fertige Pizzen:",
                         x0 + 100, fertig_y, self.font_klein, C_GREEN, center=True)
            for i, fp in enumerate(self.fertige_pizzen[:4]):
                py = fertig_y + 20 + i * 24
                zeichne_text(self.screen, f"• {fp.name}",
                             x0 + 10, py, self.font_winzig,
                             C_PIZZAS.get(fp.name, C_WHITE))

    def _draw_spielfeld(self):
        """Mittleres Spielfeld: Tische, Kunden"""
        x0, y0 = 200, 50
        breite = SCREEN_W - 400
        hoehe = SCREEN_H - 160

        # Spielfeld-Hintergrund
        zeichne_rect_rund(self.screen, (25, 25, 40), (x0, y0, breite, hoehe), radius=0)

        # Boden-Muster
        for gx in range(x0, x0 + breite, 60):
            pygame.draw.line(self.screen, (30, 30, 50), (gx, y0), (gx, y0 + hoehe))
        for gy in range(y0, y0 + hoehe, 60):
            pygame.draw.line(self.screen, (30, 30, 50), (x0, gy), (x0 + breite, gy))

        # Tische zeichnen
        for i, (tx, ty) in enumerate(self.tisch_positionen):
            # Prüfe ob belegt
            besetzt = any(k.tisch_id == i for k in self.kunden)
            farbe = C_PANEL2 if not besetzt else C_PANEL
            pygame.draw.circle(self.screen, farbe, (int(tx), int(ty)), 25)
            pygame.draw.circle(self.screen, C_DARKGRAY, (int(tx), int(ty)), 25, 2)
            zeichne_text(self.screen, str(i + 1),
                         int(tx), int(ty) - 7, self.font_klein, C_GRAY, center=True)

        # Kunden auf dem Spielfeld
        for k in self.kunden:
            self._draw_kunde_spielfeld(k)

        # Personal auf dem Spielfeld
        for p in self.personal:
            self._draw_personal_spielfeld(p)

        # Forschungs-Anzeige
        if self.aktive_forschung:
            f = next(x for x in FORSCHUNGEN if x["id"] == self.aktive_forschung.id)
            fortschritt = 1.0 - self.aktive_forschung.verbleibend / self.aktive_forschung.gesamt
            fx, fy = x0 + breite // 2, y0 + hoehe - 40
            zeichne_text(self.screen, f"🔬 {f['name']}",
                         fx, fy - 15, self.font_klein, C_PURPLE, center=True)
            zeichne_balken(self.screen, fx - 100, fy, 200, 10,
                           fortschritt, 1.0, C_PURPLE)

        # Level-Name im Spielfeld
        zeichne_text(self.screen, LEVELS[self.state.level]["beschreibung"],
                     x0 + breite // 2, y0 + 10, self.font_winzig, C_DARKGRAY, center=True)

    def _draw_kunde_spielfeld(self, k: Kunde):
        x, y = int(k.x), int(k.y)
        geduld_anteil = k.geduld / k.max_geduld

        # Schatten
        pygame.draw.ellipse(self.screen, (10, 10, 20), (x - 18, y + 16, 36, 10))

        # Körper
        farbe = C_GOLD if k.vip else (100, 150, 255)
        pygame.draw.circle(self.screen, farbe, (x, y), 16)
        pygame.draw.circle(self.screen, C_WHITE, (x, y), 16, 2)

        # Emoji
        emoji_surf = self.font_emoji.render(k.emoji, True, C_WHITE)
        self.screen.blit(emoji_surf, (x - emoji_surf.get_width() // 2,
                                      y - emoji_surf.get_height() // 2))

        # Gedulds-Balken über Kopf
        zeichne_balken(self.screen, x - 20, y - 28, 40, 6,
                       k.geduld, k.max_geduld,
                       C_GREEN if geduld_anteil > 0.5 else
                       C_YELLOW if geduld_anteil > 0.25 else C_RED)

        # Pizza-Bestellung über Kopf
        zeichne_text(self.screen, k.pizza_name[:8],
                     x, y - 38, self.font_winzig, C_WHITE, center=True)

        # VIP-Krone
        if k.vip:
            zeichne_text(self.screen, "👑", x - 8, y - 52, self.font_winzig)

    def _draw_personal_spielfeld(self, p: Personal):
        x, y = int(p.x), int(p.y)
        farbe = PERSONAL_TYPEN[p.typ]["farbe"]

        # Schatten
        pygame.draw.ellipse(self.screen, (10, 10, 20), (x - 15, y + 14, 30, 8))

        # Körper (Dreieck = Chef-Hut-Form)
        pygame.draw.circle(self.screen, farbe, (x, y), 14)
        pygame.draw.circle(self.screen, C_WHITE, (x, y), 14, 2)

        # Typ-Buchstabe
        buchstabe = p.typ[0]
        zeichne_text(self.screen, buchstabe, x, y - 7, self.font_klein, C_BLACK, center=True)

        # Name über Kopf
        zeichne_text(self.screen, p.name.split()[0],
                     x, y - 26, self.font_winzig, farbe, center=True)

    def _draw_benachrichtigungen(self):
        bx = SCREEN_W // 2
        by = SCREEN_H - 140
        for i, b in enumerate(reversed(self.benachrichtigungen[-5:])):
            alpha = min(1.0, b.timer)
            farbe = tuple(int(c * alpha) for c in b.farbe)
            zeichne_text(self.screen, b.text,
                         bx, by - i * 22 + b.y_offset,
                         self.font_klein, farbe, center=True)

    def _draw_combo(self):
        if self.state.combo < 2:
            return
        anim = abs(math.sin(pygame.time.get_ticks() / 200)) * 0.3 + 0.7
        farbe = tuple(int(c * anim) for c in C_GOLD)
        zeichne_text(self.screen, f"🔥 COMBO x{self.state.combo}!",
                     SCREEN_W // 2, 70, self.font_gross, farbe, center=True)

    def _draw_powerup_leiste(self):
        if not self.active_powerups:
            return
        py = SCREEN_H - 155
        px = SCREEN_W // 2 - len(self.active_powerups) * 80
        for ap in self.active_powerups:
            daten = POWERUPS[ap.name]
            pr = pygame.Rect(px, py, 150, 28)
            zeichne_rect_rund(self.screen, daten["farbe"], pr, radius=6, alpha=180)
            anteil = ap.verbleibend / ap.gesamt
            zeichne_balken(self.screen, px, py + 22, 150, 6, anteil, 1.0, daten["farbe"])
            zeichne_text(self.screen, f"{daten['icon']} {ap.name[:10]}",
                         px + 75, py + 5, self.font_winzig, C_WHITE, center=True)
            px += 160

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        zeichne_text(self.screen, "⏸ PAUSE", SCREEN_W // 2, SCREEN_H // 2 - 40,
                     self.font_titel, C_WHITE, center=True)
        zeichne_text(self.screen, "SPACE = Weiterspielen   ESC = Hauptmenü",
                     SCREEN_W // 2, SCREEN_H // 2 + 20, self.font_normal, C_GRAY, center=True)
        zeichne_text(self.screen, "S = Speichern",
                     SCREEN_W // 2, SCREEN_H // 2 + 55, self.font_normal, C_TEAL, center=True)

    def _draw_level_up(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        puls = abs(math.sin(pygame.time.get_ticks() / 300)) * 0.2 + 0.8
        level_data = LEVELS[self.state.level]

        zeichne_text(self.screen, "🎉 LEVEL UP! 🎉",
                     SCREEN_W // 2, SCREEN_H // 2 - 80,
                     self.font_titel,
                     tuple(int(c * puls) for c in C_GOLD),
                     center=True)
        zeichne_text(self.screen, f"Level {self.state.level}: {level_data['name']}",
                     SCREEN_W // 2, SCREEN_H // 2 - 20,
                     self.font_gross, C_WHITE, center=True)
        zeichne_text(self.screen, level_data["unlock_text"],
                     SCREEN_W // 2, SCREEN_H // 2 + 25,
                     self.font_normal, C_ACCENT, center=True)
        zeichne_text(self.screen, f"Neue max. Kunden: {level_data['max_kunden']}  "
                     f"Öfen: {level_data['ofen_slots']}",
                     SCREEN_W // 2, SCREEN_H // 2 + 65,
                     self.font_normal, C_GRAY, center=True)

    def _draw_ereignis(self):
        if not self.aktuelles_ereignis:
            return
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        e = self.aktuelles_ereignis
        box_w, box_h = 500, 200
        bx = (SCREEN_W - box_w) // 2
        by = (SCREEN_H - box_h) // 2

        zeichne_rect_rund(self.screen, C_PANEL, (bx, by, box_w, box_h), radius=12)
        pygame.draw.rect(self.screen, e["farbe"], (bx, by, box_w, box_h), 3, border_radius=12)

        zeichne_text(self.screen, "⚡ EREIGNIS!",
                     SCREEN_W // 2, by + 20, self.font_gross, e["farbe"], center=True)
        zeichne_text(self.screen, e["name"],
                     SCREEN_W // 2, by + 60, self.font_gross, C_WHITE, center=True)
        zeichne_text(self.screen, e["beschreibung"],
                     SCREEN_W // 2, by + 100, self.font_normal, C_GRAY, center=True)
        zeichne_text(self.screen, "Schließt automatisch...",
                     SCREEN_W // 2, by + 155, self.font_klein, C_DARKGRAY, center=True)
        zeichne_balken(self.screen, bx + 20, by + 180, box_w - 40, 8,
                       self.ereignis_timer2, 5.0, e["farbe"])

    def _draw_highscores(self):
        self._draw_hintergrund()
        zeichne_text(self.screen, "🏆 HIGHSCORES",
                     SCREEN_W // 2, 60, self.font_titel, C_GOLD, center=True)

        headers = ["#", "Verdient", "Level", "Pizzen", "Schwierigkeitsgr.", "Datum"]
        widths   = [40, 150, 80, 80, 160, 180]
        xs = [80]
        for w in widths[:-1]:
            xs.append(xs[-1] + w)

        for i, (h, x) in enumerate(zip(headers, xs)):
            zeichne_text(self.screen, h, x, 120, self.font_normal, C_GRAY)

        for i, hs in enumerate(self.highscores[:15]):
            y = 155 + i * 35
            farbe = C_GOLD if i == 0 else C_SILVER if i == 1 else C_BRONZE if i == 2 else C_WHITE
            if i % 2 == 0:
                zeichne_rect_rund(self.screen, C_PANEL, (75, y - 3, SCREEN_W - 150, 30), radius=4)

            werte = [
                str(i + 1),
                fmt_geld(hs.get("geld", 0)),
                str(hs.get("level", 0)),
                str(hs.get("pizzen", 0)),
                hs.get("schwierigkeit", "?"),
                hs.get("datum", "?"),
            ]
            for w, x in zip(werte, xs):
                zeichne_text(self.screen, w, x, y, self.font_normal, farbe)

        if not self.highscores:
            zeichne_text(self.screen, "Noch keine Scores vorhanden!",
                         SCREEN_W // 2, 300, self.font_gross, C_GRAY, center=True)

        zeichne_text(self.screen, "ESC = Zurück",
                     SCREEN_W // 2, SCREEN_H - 40, self.font_normal, C_GRAY, center=True)

    def _draw_achievements(self):
        self._draw_hintergrund()
        zeichne_text(self.screen, "🏆 ACHIEVEMENTS",
                     SCREEN_W // 2, 40, self.font_titel, C_GOLD, center=True)
        zeichne_text(self.screen,
                     f"Erhalten: {len(self.state.achievements_erhalten)}/{len(ACHIEVEMENTS)}  |  XP: {self.state.xp}",
                     SCREEN_W // 2, 90, self.font_normal, C_GRAY, center=True)

        cols = 3
        col_w = SCREEN_W // cols
        for i, ach in enumerate(ACHIEVEMENTS):
            col = i % cols
            row = i // cols
            x = col * col_w + 20
            y = 120 + row * 65

            erhalten = ach["id"] in self.state.achievements_erhalten
            bg = C_PANEL2 if erhalten else C_DARKGRAY
            alpha = 255 if erhalten else 120

            ar = pygame.Rect(x, y, col_w - 40, 55)
            zeichne_rect_rund(self.screen, bg, ar, radius=8)

            if erhalten:
                pygame.draw.rect(self.screen, C_GOLD, ar, 2, border_radius=8)

            zeichne_text(self.screen, ach["icon"] + " " + ach["name"],
                         x + 10, y + 7, self.font_klein,
                         C_GOLD if erhalten else C_GRAY)
            zeichne_text(self.screen, ach["beschreibung"],
                         x + 10, y + 26, self.font_winzig,
                         C_WHITE if erhalten else C_DARKGRAY)
            zeichne_text(self.screen, f"+{ach['xp']}XP",
                         ar.right - 40, y + 7, self.font_winzig,
                         C_ACCENT if erhalten else C_DARKGRAY)

        zeichne_text(self.screen, "ESC = Zurück",
                     SCREEN_W // 2, SCREEN_H - 30, self.font_klein, C_GRAY, center=True)

    def _draw_forschung(self):
        self._draw_hintergrund()
        zeichne_text(self.screen, "🔬 FORSCHUNGS-BAUM",
                     SCREEN_W // 2, 40, self.font_titel, C_PURPLE, center=True)

        if self.aktive_forschung:
            f = next(x for x in FORSCHUNGEN if x["id"] == self.aktive_forschung.id)
            fort = 1.0 - self.aktive_forschung.verbleibend / self.aktive_forschung.gesamt
            zeichne_text(self.screen, f"Aktiv: {f['name']} ({fort*100:.0f}%)",
                         SCREEN_W // 2, 90, self.font_normal, C_PURPLE, center=True)
            zeichne_balken(self.screen, SCREEN_W // 2 - 150, 115, 300, 12,
                           fort, 1.0, C_PURPLE)
        else:
            zeichne_text(self.screen, "Keine aktive Forschung — klicke eine an!",
                         SCREEN_W // 2, 90, self.font_normal, C_GRAY, center=True)

        cols = 3
        col_w = (SCREEN_W - 60) // cols
        for i, f in enumerate(FORSCHUNGEN):
            col = i % cols
            row = i // cols
            x = 30 + col * col_w
            y = 140 + row * 100

            abgeschlossen = f["id"] in self.state.forschungen_abgeschlossen
            aktiv = self.aktive_forschung and self.aktive_forschung.id == f["id"]

            # Voraussetzungen erfüllt?
            voraus_ok = all(v in self.state.forschungen_abgeschlossen for v in f["voraus"])
            verfuegbar = voraus_ok and not abgeschlossen and not aktiv

            if abgeschlossen:
                bg = (40, 80, 40)
                rand = C_GREEN
            elif aktiv:
                bg = (40, 40, 80)
                rand = C_PURPLE
            elif verfuegbar:
                bg = C_PANEL2
                rand = C_GRAY
            else:
                bg = (20, 20, 30)
                rand = (40, 40, 60)

            fr = pygame.Rect(x, y, col_w - 20, 85)
            zeichne_rect_rund(self.screen, bg, fr, radius=8)
            pygame.draw.rect(self.screen, rand, fr, 2, border_radius=8)

            zeichne_text(self.screen, f"{f['icon']} {f['name']}",
                         x + 10, y + 8, self.font_normal,
                         C_GREEN if abgeschlossen else C_WHITE if verfuegbar else C_GRAY)
            zeichne_text(self.screen, f["beschreibung"],
                         x + 10, y + 32, self.font_klein,
                         C_WHITE if verfuegbar else C_GRAY)
            zeichne_text(self.screen,
                         f"Kosten: {fmt_geld(f['kosten'])}  Zeit: {f['dauer']}s",
                         x + 10, y + 52, self.font_winzig,
                         C_ACCENT if verfuegbar else C_GRAY)

            if abgeschlossen:
                zeichne_text(self.screen, "✅ Abgeschlossen",
                             x + 10, y + 68, self.font_winzig, C_GREEN)
            elif aktiv:
                zeichne_text(self.screen, "⏳ In Arbeit...",
                             x + 10, y + 68, self.font_winzig, C_PURPLE)
            elif not voraus_ok:
                zeichne_text(self.screen, "🔒 Voraussetzung fehlt",
                             x + 10, y + 68, self.font_winzig, C_RED)

        zeichne_text(self.screen, "ESC = Zurück  |  Klicke Forschung = Starten",
                     SCREEN_W // 2, SCREEN_H - 30, self.font_klein, C_GRAY, center=True)

    def _draw_game_over(self):
        self._draw_hintergrund()
        self.partikel.zeichne(self.screen, self.font_klein)

        zeichne_text(self.screen, "💀 GAME OVER", SCREEN_W // 2, 120,
                     self.font_titel, C_RED, center=True)
        zeichne_text(self.screen, "Das Geld ist aufgebraucht!",
                     SCREEN_W // 2, 200, self.font_gross, C_GRAY, center=True)

        stats = [
            f"Verdient: {fmt_geld(self.state.gesamt_verdient)}",
            f"Pizzen gebacken: {self.state.pizzen_gebacken}",
            f"Kunden bedient: {self.state.kunden_bedient}",
            f"Erreichtes Level: {self.state.level} – {LEVELS[self.state.level]['name']}",
            f"Spielzeit: {fmt_zeit(self.state.spielzeit)}",
            f"XP: {self.state.xp}",
            f"Achievements: {len(self.state.achievements_erhalten)}/{len(ACHIEVEMENTS)}",
        ]
        for i, s in enumerate(stats):
            zeichne_text(self.screen, s, SCREEN_W // 2, 270 + i * 35,
                         self.font_normal, C_WHITE, center=True)

        zeichne_text(self.screen, "ENTER = Neues Spiel    ESC = Hauptmenü",
                     SCREEN_W // 2, SCREEN_H - 60, self.font_normal, C_GRAY, center=True)

    # ═══════════════════════════════════════════════════════════════
    #  EVENTS / EINGABE
    # ═══════════════════════════════════════════════════════════════

    def handle_events(self):
        mpos = pygame.mouse.get_pos()

        for btn in [self.btn_neues_spiel, self.btn_weiterspielen,
                    self.btn_highscores, self.btn_beenden,
                    self.btn_pause, self.btn_speichern, self.btn_menu_hs,
                    self.btn_ach, self.btn_forschung]:
            btn.check_hover(mpos)

        for btn in self.btn_schwierig.values():
            btn.check_hover(mpos)

        # Power-Up Buttons hover
        for btn in self.powerup_btns.values():
            btn.check_hover(mpos)
            btn.update(1/FPS)

        # Personal-Button hover
        if self.personal_btn:
            self.personal_btn.check_hover(mpos)
        if self.personal_menu:
            self.personal_menu.hover(mpos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.screen_state == "spiel":
                    self._speichern()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Linksklick
                    # Personal-Menü zuerst prüfen
                    if self.screen_state == "spiel" and self.personal_menu:
                        if self.personal_menu.click(mpos):
                            continue
                        if self.personal_btn and self.personal_btn.clicked(mpos):
                            self.personal_menu.toggle()
                            continue
                    self._handle_click(mpos, event.button)
                elif event.button == 3:  # Rechtsklick
                    if self.screen_state == "spiel" and self.personal_menu:
                        self.personal_menu.toggle()

        # Hover-Buttons updaten
        dt = 1 / FPS
        for btn in [self.btn_pause, self.btn_speichern, self.btn_menu_hs,
                    self.btn_ach, self.btn_forschung]:
            btn.update(dt)

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self._handle_escape()
        elif key == pygame.K_SPACE:
            if self.screen_state == "spiel":
                self.screen_state = "pause"
            elif self.screen_state == "pause":
                self.screen_state = "spiel"
        elif key == pygame.K_s:
            if self.screen_state in ("spiel", "pause"):
                self._speichern()
        elif key == pygame.K_h:
            if self.screen_state in ("spiel", "pause"):
                self.screen_state = "highscore"
        elif key == pygame.K_a:
            if self.screen_state in ("spiel", "pause"):
                self.screen_state = "achievement"
        elif key == pygame.K_r:
            if self.screen_state in ("spiel", "pause"):
                self.screen_state = "forschung"
        elif key == pygame.K_RETURN:
            if self.screen_state == "game_over":
                self._neues_spiel()
        elif key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
            # Schnell-Ofen-Slots
            slot = key - pygame.K_1
            if self.screen_state == "spiel":
                self.pizza_in_ofen(slot)

    def _handle_escape(self):
        if self.screen_state == "spiel":
            self.screen_state = "pause"
        elif self.screen_state == "pause":
            self._speichern()
            self.screen_state = "menu"
        elif self.screen_state in ("highscore", "achievement", "forschung"):
            self.screen_state = "spiel" if self._war_im_spiel else "menu"
        elif self.screen_state == "schwierigkeit":
            self.screen_state = "menu"
        elif self.screen_state == "game_over":
            self.screen_state = "menu"

    @property
    def _war_im_spiel(self):
        return self.state.spielzeit > 0

    def _handle_click(self, mpos, button):
        state = self.screen_state

        if state == "menu":
            self._click_menu(mpos)
        elif state == "schwierigkeit":
            self._click_schwierigkeit(mpos)
        elif state == "spiel":
            self._click_spiel(mpos)
        elif state == "highscore":
            if pygame.Rect(0, 0, SCREEN_W, SCREEN_H).collidepoint(mpos):
                self.screen_state = "menu" if not self._war_im_spiel else "spiel"
        elif state == "achievement":
            self.screen_state = "menu" if not self._war_im_spiel else "spiel"
        elif state == "forschung":
            self._click_forschung(mpos)
        elif state == "game_over":
            self._neues_spiel()

    def _click_menu(self, mpos):
        if self.btn_neues_spiel.clicked(mpos):
            self.screen_state = "schwierigkeit"
        elif self.btn_weiterspielen.clicked(mpos) and self.speicherstand_vorhanden:
            if self._laden():
                self._init_spiel()
                self.screen_state = "spiel"
        elif self.btn_highscores.clicked(mpos):
            self.screen_state = "highscore"
        elif self.btn_beenden.clicked(mpos):
            pygame.quit()
            sys.exit()

    def _click_schwierigkeit(self, mpos):
        for name, btn in self.btn_schwierig.items():
            if btn.clicked(mpos):
                self.state.schwierigkeit = name
                self._neues_spiel()

    def _neues_spiel(self):
        self.state.reset()
        self._init_spiel()
        self.screen_state = "spiel"
        self._benachrichtigung("🍕 Willkommen bei Pizzeria Imperium!", C_ACCENT)
        self._benachrichtigung("Klicke auf Öfen um Pizzen zu backen!", C_GRAY)
        self.speicherstand_vorhanden = os.path.exists(SAVE_FILE)

    def _click_spiel(self, mpos):
        mx, my = mpos

        # Top-Buttons
        if self.btn_pause.clicked(mpos):
            self.screen_state = "pause"
            return
        if self.btn_speichern.clicked(mpos):
            self._speichern()
            return
        if self.btn_menu_hs.clicked(mpos):
            self.screen_state = "highscore"
            return
        if self.btn_ach.clicked(mpos):
            self.screen_state = "achievement"
            return
        if self.btn_forschung.clicked(mpos):
            self.screen_state = "forschung"
            return

        # Power-Up Panel Klicks (untere Mitte)
        if SCREEN_H - 108 <= my <= SCREEN_H - 45:
            start_x = 205
            # Erste Reihe (4 Buttons)
            if SCREEN_H - 108 <= my <= SCREEN_H - 80:
                for i, (name, daten) in enumerate(list(POWERUPS.items())[:4]):
                    x = start_x + i * 190
                    r = pygame.Rect(x, SCREEN_H - 108, 185, 28)
                    if r.collidepoint(mpos):
                        self.powerup_aktivieren(name)
                        return
            # Zweite Reihe (4 Buttons)
            elif SCREEN_H - 73 <= my <= SCREEN_H - 45:
                for i, (name, daten) in enumerate(list(POWERUPS.items())[4:]):
                    x = start_x + i * 190
                    r = pygame.Rect(x, SCREEN_H - 73, 185, 28)
                    if r.collidepoint(mpos):
                        self.powerup_aktivieren(name)
                        return

        # Ofen-Klick (linke Seitenleiste)
        if mx < 200:
            for i in range(len(self.pizzen_im_ofen)):
                oy = 85 + i * 80
                if 10 <= mx <= 190 and oy <= my <= oy + 70:
                    if self.pizzen_im_ofen[i] is None:
                        self.pizza_in_ofen(i)
                    else:
                        self.pizza_aus_ofen(i)
                    return

        # Pizza-Auswahl (untere Leiste)
        if my > SCREEN_H - 110:
            pizza_x = 10
            for pname in self.state.freigeschaltete_pizzen:
                pr = pygame.Rect(pizza_x, SCREEN_H - 92, 90, 36)
                if pr.collidepoint(mpos):
                    self.ausgewaehlte_pizza = pname
                    return
                pizza_x += 94
                if pizza_x > SCREEN_W - 100:
                    break

        # Rechte Seitenleiste — Kunden-Klick (Servieren)
        if mx > SCREEN_W - 200:
            x0 = SCREEN_W - 200
            for i, k in enumerate(self.kunden[:6]):
                ky = 85 + i * 48
                kr = pygame.Rect(x0 + 5, ky, 190, 42)
                if kr.collidepoint(mpos):
                    # Passende fertige Pizza servieren
                    for fp in list(self.fertige_pizzen):
                        if fp.name == k.pizza_name:
                            self.pizza_servieren(fp, k)
                            return
                    # Falsche Pizza servieren (erste verfügbare)
                    if self.fertige_pizzen:
                        self.pizza_servieren(self.fertige_pizzen[0], k)
                    else:
                        self._benachrichtigung("Keine fertige Pizza verfügbar!", C_YELLOW)
                    return

        # Spielfeld — Kunden anklicken
        if 200 <= mx <= SCREEN_W - 200:
            for k in self.kunden:
                if dist(mx, my, k.x, k.y) < 20:
                    # Servieren wenn möglich
                    for fp in list(self.fertige_pizzen):
                        if fp.name == k.pizza_name:
                            self.pizza_servieren(fp, k)
                            return
                    if self.fertige_pizzen:
                        self.pizza_servieren(self.fertige_pizzen[0], k)
                    else:
                        self._benachrichtigung(f"Backe noch {k.pizza_name}!", C_YELLOW)
                    return

    def _click_forschung(self, mpos):
        mx, my = mpos
        if mx < 30 or mx > SCREEN_W - 30:
            self.screen_state = "spiel"
            return

        cols = 3
        col_w = (SCREEN_W - 60) // cols
        for i, f in enumerate(FORSCHUNGEN):
            col = i % cols
            row = i // cols
            x = 30 + col * col_w
            y = 140 + row * 100
            fr = pygame.Rect(x, y, col_w - 20, 85)
            if fr.collidepoint(mpos):
                self.forschung_starten(f["id"])
                return

        if my > SCREEN_H - 60:
            self.screen_state = "spiel"

    def _draw_powerup_panel(self):
        """Zeichnet Power-Up Buttons in der unteren Mitte."""
        y = SCREEN_H - 108
        start_x = 205
        for i, (name, daten) in enumerate(POWERUPS.items()):
            if i >= 4:
                break
            x = start_x + i * 190
            btn = self.powerup_btns[name]
            btn.rect = pygame.Rect(x, y, 185, 28)

            # Schon aktiv?
            aktiv = any(ap.name == name for ap in self.active_powerups)
            btn.farbe = C_DARKGRAY if aktiv else daten["farbe"]

            kann_kaufen = self.state.geld >= daten["kosten"]
            btn.aktiv = kann_kaufen and not aktiv

            btn.zeichne(self.screen, self.font_normal, self.font_winzig)

            # Kosten anzeigen
            zeichne_text(self.screen, fmt_geld(daten["kosten"]),
                         x + 93, y + 30, self.font_winzig,
                         C_GOLD if kann_kaufen else C_RED, center=True)

        # Zweite Reihe Power-Ups
        for i, (name, daten) in enumerate(list(POWERUPS.items())[4:]):
            x = start_x + i * 190
            btn = self.powerup_btns[name]
            btn.rect = pygame.Rect(x, y + 35, 185, 28)

            aktiv = any(ap.name == name for ap in self.active_powerups)
            btn.farbe = C_DARKGRAY if aktiv else daten["farbe"]
            kann_kaufen = self.state.geld >= daten["kosten"]
            btn.aktiv = kann_kaufen and not aktiv

            btn.zeichne(self.screen, self.font_normal, self.font_winzig)
            zeichne_text(self.screen, fmt_geld(daten["kosten"]),
                         x + 93, y + 65, self.font_winzig,
                         C_GOLD if kann_kaufen else C_RED, center=True)
        # KORRIGIERT: Kein pygame.display.flip() hier - wird in draw() aufgerufen

    # ═══════════════════════════════════════════════════════════════
    #  HAUPT-SCHLEIFE
    # ═══════════════════════════════════════════════════════════════

    def run(self):
        # Power-Up Panel im Spiel (separate Buttons, dynamisch erstellt)
        self._init_powerup_buttons()
        # Personal-UI initialisieren
        self._init_personal_ui()

        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Max 50ms Schritt

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


# ═══════════════════════════════════════════════════════════════════
#  PERSONAL-MENU KLASSE
# ═══════════════════════════════════════════════════════════════════

class PersonalMenu:
    """Popup-Menü zum Einstellen von Personal."""

    def __init__(self, game: PizzeriaImperium):
        self.game = game
        self.offen = False
        self.buttons: list[Button] = []
        self._rebuild()

    def _rebuild(self):
        self.buttons = []
        for i, (typ, daten) in enumerate(PERSONAL_TYPEN.items()):
            kosten = daten["gehalt"] * 5
            self.buttons.append(Button(
                SCREEN_W - 420, 300 + i * 55, 200, 45,
                f"{typ} (€{kosten:.0f})",
                daten["farbe"], klein=True
            ))

    def toggle(self):
        self.offen = not self.offen

    def draw(self, screen, font_klein, font_normal):
        if not self.offen:
            return
        x = SCREEN_W - 430
        y = 290
        h = len(PERSONAL_TYPEN) * 55 + 50

        zeichne_rect_rund(screen, C_PANEL, (x - 10, y - 10, 220, h), radius=10)
        pygame.draw.rect(screen, C_PURPLE, (x - 10, y - 10, 220, h), 2, border_radius=10)
        zeichne_text(screen, "Personal einstellen:", x, y - 2, font_klein, C_PURPLE)

        for btn in self.buttons:
            btn.zeichne(screen, font_normal, font_klein)

    def click(self, mpos) -> bool:
        if not self.offen:
            return False
        for i, (typ, daten) in enumerate(PERSONAL_TYPEN.items()):
            if self.buttons[i].clicked(mpos):
                self.game.personal_einstellen(typ)
                self.offen = False
                return True
        # Klick außerhalb schließt
        if not any(btn.rect.collidepoint(mpos) for btn in self.buttons):
            self.offen = False
        return False

    def hover(self, mpos):
        for btn in self.buttons:
            btn.check_hover(mpos)


# ═══════════════════════════════════════════════════════════════════
#  START-SCHIRM MIT ANIMATION
# ═══════════════════════════════════════════════════════════════════

def zeige_intro(screen, font_titel, font_normal, font_klein):
    """Kurzer Intro-Screen."""
    clock = pygame.time.Clock()
    timer = 3.0
    partikel = PartikelSystem()

    while timer > 0:
        dt = clock.tick(60) / 1000.0
        timer -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                timer = 0

        screen.fill(C_BLACK)

        # Pizza-Regen
        if random.random() < 0.3:
            partikel.add(
                random.randint(0, SCREEN_W),
                -10,
                random.choice(list(C_PIZZAS.values())),
                anzahl=1,
                geschwindigkeit=30
            )
            for p in partikel.partikel[-1:]:
                p.vy = 80
                p.vx = random.uniform(-20, 20)

        partikel.update(dt)
        partikel.zeichne(screen, font_klein)

        alpha = min(1.0, (3.0 - timer) * 2)
        farbe = tuple(int(c * alpha) for c in C_ACCENT)
        zeichne_text(screen, "🍕 PIZZERIA IMPERIUM 🍕",
                     SCREEN_W // 2, SCREEN_H // 2 - 40,
                     font_titel, farbe, center=True)
        zeichne_text(screen, "Ein Tycoon-Spiel von Pizza-Liebhabern",
                     SCREEN_W // 2, SCREEN_H // 2 + 30,
                     font_normal, tuple(int(c * alpha) for c in C_GRAY), center=True)
        zeichne_text(screen, "Drücke eine Taste...",
                     SCREEN_W // 2, SCREEN_H // 2 + 80,
                     font_klein, tuple(int(c * alpha * 0.6) for c in C_GRAY), center=True)

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════════
#  TUTORIAL
# ═══════════════════════════════════════════════════════════════════

TUTORIAL_SCHRITTE = [
    {
        "titel": "Willkommen! 🍕",
        "text": [
            "Du startest mit einem kleinen Pizzastand.",
            "Dein Ziel: Geld verdienen und aufsteigen!",
            "",
            "Wie es geht:",
            "1. Klicke auf einen Ofen → Pizza backen",
            "2. Warte bis sie fertig ist",
            "3. Klicke auf den Kunden → Pizza servieren",
            "4. Kassiere dein Geld! 💰",
        ]
    },
    {
        "titel": "Pizza-Auswahl 🍕",
        "text": [
            "Unten siehst du alle verfügbaren Pizzen.",
            "Klicke eine an um sie auszuwählen.",
            "",
            "Wichtig: Serviere Kunden NUR ihre",
            "bestellte Pizza — sonst verlierst du sie!",
            "",
            "Mit mehr Level schaltest du neue",
            "Pizzasorten frei!",
        ]
    },
    {
        "titel": "Power-Ups & Forschung ⚡",
        "text": [
            "Power-Ups: Temporäre Vorteile (unten Mitte)",
            "z.B. Turbobackofen, Werbung, VIP-Abend",
            "",
            "Forschung (R-Taste): Dauerhafte Verbesserungen",
            "z.B. schnellere Öfen, mehr Kunden",
            "",
            "Personal (Rechtsklick): Mitarbeiter einstellen",
            "die automatisch helfen!",
        ]
    },
]


def zeige_tutorial(screen, fonts):
    font_gross, font_normal, font_klein = fonts
    clock = pygame.time.Clock()
    schritt = 0

    btn_weiter = Button(SCREEN_W // 2 - 100, SCREEN_H - 80, 200, 45,
                        "Weiter →", C_ACCENT)
    btn_ueberspringen = Button(SCREEN_W - 150, SCREEN_H - 60, 130, 35,
                               "Überspringen", C_GRAY, klein=True)

    while schritt < len(TUTORIAL_SCHRITTE):
        dt = clock.tick(60) / 1000.0
        mpos = pygame.mouse.get_pos()
        btn_weiter.check_hover(mpos)
        btn_ueberspringen.check_hover(mpos)
        btn_weiter.update(dt)
        btn_ueberspringen.update(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_weiter.clicked(mpos):
                    schritt += 1
                elif btn_ueberspringen.clicked(mpos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
                    schritt += 1
                elif event.key == pygame.K_ESCAPE:
                    return

        screen.fill(C_BG)

        # Fortschritts-Punkte
        for i in range(len(TUTORIAL_SCHRITTE)):
            farbe = C_ACCENT if i == schritt else C_DARKGRAY
            pygame.draw.circle(screen, farbe,
                               (SCREEN_W // 2 - (len(TUTORIAL_SCHRITTE) - 1) * 15 + i * 30, 60), 8)

        if schritt < len(TUTORIAL_SCHRITTE):
            t = TUTORIAL_SCHRITTE[schritt]
            zeichne_text(screen, t["titel"], SCREEN_W // 2, 100,
                         font_gross, C_ACCENT, center=True)

            for i, zeile in enumerate(t["text"]):
                farbe = C_GRAY if zeile == "" else C_WHITE
                zeichne_text(screen, zeile, SCREEN_W // 2, 200 + i * 35,
                             font_normal, farbe, center=True)

        btn_weiter.zeichne(screen, font_normal, font_klein)
        btn_ueberspringen.zeichne(screen, font_normal, font_klein)

        zeichne_text(screen,
                     f"Schritt {min(schritt+1, len(TUTORIAL_SCHRITTE))}/{len(TUTORIAL_SCHRITTE)}",
                     20, SCREEN_H - 30, font_klein, C_GRAY)

        pygame.display.flip()


# ═══════════════════════════════════════════════════════════════════
#  EINSTELLUNGEN
# ═══════════════════════════════════════════════════════════════════

class Einstellungen:
    def __init__(self):
        self.musik_lautstaerke = 0.7
        self.effekte_lautstaerke = 1.0
        self.vollbild = False
        self.zeige_tutorial = True
        self.sprache = "Deutsch"

    def speichern(self):
        try:
            with open("einstellungen.json", "w") as f:
                json.dump(self.__dict__, f)
        except Exception:
            pass

    def laden(self):
        try:
            with open("einstellungen.json") as f:
                data = json.load(f)
                for k, v in data.items():
                    if hasattr(self, k):
                        setattr(self, k, v)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
#  STATISTIKEN-SCREEN
# ═══════════════════════════════════════════════════════════════════

def draw_statistiken(screen, state: GameState, fonts):
    font_gross, font_normal, font_klein = fonts
    screen.fill(C_BG)

    zeichne_text(screen, "📊 STATISTIKEN",
                 SCREEN_W // 2, 40, font_gross, C_ACCENT, center=True)

    stats = [
        ("Gesamt verdient", fmt_geld(state.gesamt_verdient), C_GOLD),
        ("Pizzen gebacken", str(state.pizzen_gebacken), C_ACCENT),
        ("Kunden bedient", str(state.kunden_bedient), C_GREEN),
        ("Kunden verloren", str(state.kunden_verloren), C_RED),
        ("VIP-Kunden", str(state.vip_kunden_bedient), C_PURPLE),
        ("Höchste Combo", f"x{state.max_combo}", C_YELLOW),
        ("Spielzeit", fmt_zeit(state.spielzeit), C_BLUE),
        ("Achievements", f"{len(state.achievements_erhalten)}/{len(ACHIEVEMENTS)}", C_GOLD),
        ("XP", str(state.xp), C_ACCENT),
        ("Level", f"{state.level} – {LEVELS[state.level]['name']}", C_WHITE),
        ("Power-Ups benutzt", str(state.powerups_benutzt), C_TEAL),
        ("Ereignisse erlebt", str(state.ereignisse_erlebt), C_GRAY),
    ]

    for i, (label, wert, farbe) in enumerate(stats):
        col = i % 2
        row = i // 2
        x = 150 + col * 500
        y = 100 + row * 45
        zeichne_text(screen, label + ":", x, y, font_normal, C_GRAY)
        zeichne_text(screen, wert, x + 280, y, font_normal, farbe)


# ═══════════════════════════════════════════════════════════════════
#  GRAFIK-EFFEKTE
# ═══════════════════════════════════════════════════════════════════

def draw_geld_animation(screen, betrag: float, x: int, y: int, font, anim_t: float):
    """Animiert einen Geldbetrag der aufsteigt und verblasst."""
    alpha = max(0, 1.0 - anim_t)
    dy = int(anim_t * 60)
    farbe = (int(C_GOLD[0] * alpha), int(C_GOLD[1] * alpha), int(C_GOLD[2] * alpha))
    zeichne_text(screen, f"+{fmt_geld(betrag)}", x, y - dy, font, farbe, center=True)


def draw_pizza_spinning(screen, cx: int, cy: int, radius: int, t: float, farbe):
    """Zeichnet eine sich drehende Pizza."""
    for i in range(8):
        winkel = t + i * math.pi / 4
        x1 = cx + int(math.cos(winkel) * radius * 0.3)
        y1 = cy + int(math.sin(winkel) * radius * 0.3)
        x2 = cx + int(math.cos(winkel) * radius)
        y2 = cy + int(math.sin(winkel) * radius)
        pygame.draw.line(screen, farbe, (x1, y1), (x2, y2), 2)
    pygame.draw.circle(screen, farbe, (cx, cy), radius, 3)
    pygame.draw.circle(screen, (farbe[0] // 2, farbe[1] // 2, farbe[2] // 2),
                       (cx, cy), radius // 2, 2)


# ═══════════════════════════════════════════════════════════════════
#  MINI-GAMES (Bonus-Feature)
# ═══════════════════════════════════════════════════════════════════

class PizzaWurf:
    """Mini-Game: Wirf Teig in die Luft! Erscheint als Bonus-Event."""

    def __init__(self, screen, fonts):
        self.screen = screen
        self.font_gross, self.font_normal, self.font_klein = fonts
        self.teig_y = SCREEN_H - 200
        self.teig_vy = 0
        self.teig_radius = 40
        self.punkte = 0
        self.versuche = 5
        self.anim = 0.0
        self.running = True
        self.clock = pygame.time.Clock()

    def run(self) -> int:
        btn = Button(SCREEN_W // 2 - 80, SCREEN_H - 100, 160, 45,
                     "Werfen! (SPACE)", C_ACCENT)

        while self.running and self.versuche > 0:
            dt = self.clock.tick(60) / 1000.0
            self.anim += dt

            mpos = pygame.mouse.get_pos()
            btn.check_hover(mpos)
            btn.update(dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._werfen()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn.clicked(mpos):
                        self._werfen()

            # Physik
            if self.teig_vy != 0:
                self.teig_y += self.teig_vy * dt
                self.teig_vy += 400 * dt  # Schwerkraft

                if self.teig_y >= SCREEN_H - 200:
                    self.teig_y = SCREEN_H - 200
                    self.teig_vy = 0
                    self.versuche -= 1

            self.screen.fill(C_BG)
            zeichne_text(self.screen, "🍕 MINI-GAME: Pizza-Wurf!",
                         SCREEN_W // 2, 40, self.font_gross, C_ACCENT, center=True)
            zeichne_text(self.screen, f"Punkte: {self.punkte}  |  Versuche: {self.versuche}",
                         SCREEN_W // 2, 90, self.font_normal, C_WHITE, center=True)

            # Teig
            draw_pizza_spinning(self.screen, SCREEN_W // 2, int(self.teig_y),
                                self.teig_radius, self.anim * 3,
                                C_PIZZAS["Margherita"])

            # Zielzone
            pygame.draw.rect(self.screen, (40, 80, 40),
                             (SCREEN_W // 2 - 30, SCREEN_H // 2 - 20, 60, 40), 2)
            zeichne_text(self.screen, "Ziel!",
                         SCREEN_W // 2, SCREEN_H // 2 - 10, self.font_klein, C_GREEN, center=True)

            btn.zeichne(self.screen, self.font_normal, self.font_klein)
            pygame.display.flip()

        return self.punkte * 50  # Bonus-Geld

    def _werfen(self):
        if self.teig_vy == 0:
            self.teig_vy = -600
            # Punkte wenn in Zielzone
            if abs(self.teig_y - SCREEN_H // 2) < 50:
                self.punkte += 1


# ═══════════════════════════════════════════════════════════════════
#  HAUPT-EINSTIEGSPUNKT
# ═══════════════════════════════════════════════════════════════════

def main():
    pygame.init()

    # Prüfe ob pygame.mixer verfügbar
    try:
        pygame.mixer.init()
        hat_mixer = True
    except Exception:
        hat_mixer = False

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)

    # Fonts laden
    font_titel  = pygame.font.SysFont("arial", 42, bold=True)
    font_gross  = pygame.font.SysFont("arial", 28, bold=True)
    font_normal = pygame.font.SysFont("arial", 20)
    font_klein  = pygame.font.SysFont("arial", 15)

    # Intro
    zeige_intro(screen, font_titel, font_normal, font_klein)

    # Spiel starten
    spiel = PizzeriaImperium()

    # Erster Start: Tutorial anzeigen
    einst = Einstellungen()
    einst.laden()
    if einst.zeige_tutorial and not os.path.exists(SAVE_FILE):
        zeige_tutorial(screen, (font_gross, font_normal, font_klein))
        einst.zeige_tutorial = False
        einst.speichern()

    spiel.run()


if __name__ == "__main__":
    main()