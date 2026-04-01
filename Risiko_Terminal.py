#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          R I S I K O  -  Welteroberungsstrategie             ║
║          Eine Python-Umsetzung des Klassikers                ║
╚══════════════════════════════════════════════════════════════╝
Extras:
  • KI-Gegner mit 3 Schwierigkeitsstufen (Leicht / Mittel / Schwer)
  • Spielstand speichern & laden (JSON)
  • Farbige Terminal-Ausgabe
  • Kontinente-Boni
  • Karten-System (Tausch für Extra-Truppen)
  • Angriffsanimation
  • Statistiken am Spielende
"""

import json
import os
import random
import sys
import time
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ───────────────────────────── FARBEN ─────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"
    BG_RED = "\033[41m"
    BG_GREEN="\033[42m"

PLAYER_COLORS = [C.RED, C.BLUE, C.GREEN, C.MAGENTA, C.YELLOW, C.CYAN]
PLAYER_SYMBOLS = ["★", "♦", "▲", "●", "■", "♠"]

def colored(text, color):
    return f"{color}{text}{C.RESET}"

def bold(text):
    return f"{C.BOLD}{text}{C.RESET}"

# ───────────────────────────── KARTE ──────────────────────────────
TERRITORIES = {
    # Nordamerika
    "Alaska":             {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium", "Alberta", "Kamtschatka"]},
    "Nordwest-Territorium":{"continent": "Nordamerika", "neighbors": ["Alaska", "Alberta", "Ontario", "Grönland"]},
    "Grönland":           {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium", "Ontario", "Quebec", "Island"]},
    "Alberta":            {"continent": "Nordamerika", "neighbors": ["Alaska", "Nordwest-Territorium", "Ontario", "Weststaaten"]},
    "Ontario":            {"continent": "Nordamerika", "neighbors": ["Nordwest-Territorium", "Grönland", "Alberta", "Weststaaten", "Quebec", "Oststaaten"]},
    "Quebec":             {"continent": "Nordamerika", "neighbors": ["Ontario", "Grönland", "Oststaaten"]},
    "Weststaaten":        {"continent": "Nordamerika", "neighbors": ["Alberta", "Ontario", "Oststaaten", "Mittelamerika"]},
    "Oststaaten":         {"continent": "Nordamerika", "neighbors": ["Weststaaten", "Ontario", "Quebec", "Mittelamerika"]},
    "Mittelamerika":      {"continent": "Nordamerika", "neighbors": ["Weststaaten", "Oststaaten", "Venezuela"]},
    # Südamerika
    "Venezuela":          {"continent": "Südamerika", "neighbors": ["Mittelamerika", "Peru", "Brasilien"]},
    "Peru":               {"continent": "Südamerika", "neighbors": ["Venezuela", "Brasilien", "Argentinien"]},
    "Brasilien":          {"continent": "Südamerika", "neighbors": ["Venezuela", "Peru", "Argentinien", "Nordafrika"]},
    "Argentinien":        {"continent": "Südamerika", "neighbors": ["Peru", "Brasilien"]},
    # Europa
    "Island":             {"continent": "Europa", "neighbors": ["Grönland", "Großbritannien", "Skandinavien"]},
    "Großbritannien":     {"continent": "Europa", "neighbors": ["Island", "Skandinavien", "Nordeuropa", "Westeuropa"]},
    "Skandinavien":       {"continent": "Europa", "neighbors": ["Island", "Großbritannien", "Nordeuropa", "Ukraine"]},
    "Nordeuropa":         {"continent": "Europa", "neighbors": ["Großbritannien", "Skandinavien", "Westeuropa", "Mitteleuropa", "Ukraine"]},
    "Westeuropa":         {"continent": "Europa", "neighbors": ["Großbritannien", "Nordeuropa", "Mitteleuropa", "Nordafrika"]},
    "Mitteleuropa":       {"continent": "Europa", "neighbors": ["Nordeuropa", "Westeuropa", "Ukraine", "Südeuropa"]},
    "Ukraine":            {"continent": "Europa", "neighbors": ["Skandinavien", "Nordeuropa", "Mitteleuropa", "Südeuropa", "Ural", "Afghanistan", "Mittlerer Osten"]},
    "Südeuropa":          {"continent": "Europa", "neighbors": ["Westeuropa", "Mitteleuropa", "Ukraine", "Nordafrika", "Ägypten", "Mittlerer Osten"]},
    # Afrika
    "Nordafrika":         {"continent": "Afrika", "neighbors": ["Brasilien", "Westeuropa", "Südeuropa", "Ägypten", "Ostafrika", "Zentralafrika"]},
    "Ägypten":            {"continent": "Afrika", "neighbors": ["Nordafrika", "Südeuropa", "Mittlerer Osten", "Ostafrika"]},
    "Zentralafrika":      {"continent": "Afrika", "neighbors": ["Nordafrika", "Ostafrika", "Südafrika"]},
    "Ostafrika":          {"continent": "Afrika", "neighbors": ["Nordafrika", "Ägypten", "Zentralafrika", "Südafrika", "Madagaskar", "Mittlerer Osten"]},
    "Südafrika":          {"continent": "Afrika", "neighbors": ["Zentralafrika", "Ostafrika", "Madagaskar"]},
    "Madagaskar":         {"continent": "Afrika", "neighbors": ["Ostafrika", "Südafrika"]},
    # Asien
    "Ural":               {"continent": "Asien", "neighbors": ["Ukraine", "Sibirien", "Afghanistan", "China"]},
    "Sibirien":           {"continent": "Asien", "neighbors": ["Ural", "Jakutien", "Irkutsk", "Mongolei", "China"]},
    "Jakutien":           {"continent": "Asien", "neighbors": ["Sibirien", "Kamtschatka", "Irkutsk"]},
    "Kamtschatka":        {"continent": "Asien", "neighbors": ["Jakutien", "Irkutsk", "Mongolei", "Japan", "Alaska"]},
    "Irkutsk":            {"continent": "Asien", "neighbors": ["Sibirien", "Jakutien", "Kamtschatka", "Mongolei"]},
    "Mongolei":           {"continent": "Asien", "neighbors": ["Sibirien", "Kamtschatka", "Irkutsk", "China", "Japan"]},
    "Japan":              {"continent": "Asien", "neighbors": ["Kamtschatka", "Mongolei"]},
    "Afghanistan":        {"continent": "Asien", "neighbors": ["Ukraine", "Ural", "China", "Indien", "Mittlerer Osten"]},
    "China":              {"continent": "Asien", "neighbors": ["Ural", "Sibirien", "Mongolei", "Afghanistan", "Indien", "Siam"]},
    "Mittlerer Osten":    {"continent": "Asien", "neighbors": ["Ukraine", "Südeuropa", "Ägypten", "Ostafrika", "Afghanistan", "Indien"]},
    "Indien":             {"continent": "Asien", "neighbors": ["Mittlerer Osten", "Afghanistan", "China", "Siam"]},
    "Siam":               {"continent": "Asien", "neighbors": ["China", "Indien", "Indonesien"]},
    # Australien/Ozeanien
    "Indonesien":         {"continent": "Australien", "neighbors": ["Siam", "Neuguinea", "Westaustralien"]},
    "Neuguinea":          {"continent": "Australien", "neighbors": ["Indonesien", "Westaustralien", "Ostaustralien"]},
    "Westaustralien":     {"continent": "Australien", "neighbors": ["Indonesien", "Neuguinea", "Ostaustralien"]},
    "Ostaustralien":      {"continent": "Australien", "neighbors": ["Neuguinea", "Westaustralien"]},
}

CONTINENTS = {
    "Nordamerika": {"bonus": 5, "territories": [t for t, d in TERRITORIES.items() if d["continent"] == "Nordamerika"]},
    "Südamerika":  {"bonus": 2, "territories": [t for t, d in TERRITORIES.items() if d["continent"] == "Südamerika"]},
    "Europa":      {"bonus": 5, "territories": [t for t, d in TERRITORIES.items() if d["continent"] == "Europa"]},
    "Afrika":      {"bonus": 3, "territories": [t for t, d in TERRITORIES.items() if d["continent"] == "Afrika"]},
    "Asien":       {"bonus": 7, "territories": [t for t, d in TERRITORIES.items() if d["continent"] == "Asien"]},
    "Australien":  {"bonus": 2, "territories": [t for t, d in TERRITORIES.items() if d["continent"] == "Australien"]},
}

CARD_TYPES = ["Infanterie", "Kavallerie", "Artillerie"]
CARD_VALUES = {"Infanterie": 1, "Kavallerie": 5, "Artillerie": 10}
CARD_EXCHANGE_SETS = [
    ("Infanterie", "Infanterie", "Infanterie"),
    ("Kavallerie", "Kavallerie", "Kavallerie"),
    ("Artillerie", "Artillerie", "Artillerie"),
    ("Infanterie", "Kavallerie", "Artillerie"),
]
CARD_EXCHANGE_BONUS = [4, 6, 8, 10, 12, 15]  # Steigt nach 6 um 5

# ─────────────────────────── HILFSFUNKTIONEN ──────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(msg="Weiter mit ENTER..."):
    input(f"\n{colored(msg, C.GRAY)}")

def roll_dice(n: int) -> List[int]:
    return sorted([random.randint(1, 6) for _ in range(n)], reverse=True)

def print_banner():
    banner = f"""
{C.RED}{C.BOLD}
  ██████╗ ██╗███████╗██╗██╗  ██╗ ██████╗ 
  ██╔══██╗██║██╔════╝██║██║ ██╔╝██╔═══██╗
  ██████╔╝██║███████╗██║█████╔╝ ██║   ██║
  ██╔══██╗██║╚════██║██║██╔═██╗ ██║   ██║
  ██║  ██║██║███████║██║██║  ██╗╚██████╔╝
  ╚═╝  ╚═╝╚═╝╚══════╝╚═╝╚═╝  ╚═╝ ╚═════╝ 
{C.RESET}{C.YELLOW}          Welteroberungsstrategie{C.RESET}
"""
    print(banner)

def animate_battle(atk_rolls, def_rolls, atk_wins, def_wins):
    """Zeigt eine animierte Kampfszene."""
    print(f"\n  {C.BOLD}⚔  KAMPF  ⚔{C.RESET}")
    time.sleep(0.3)
    atk_str = "  ".join(
        colored(f"[{d}]", C.GREEN if i < atk_wins else C.RED)
        for i, d in enumerate(atk_rolls)
    )
    def_str = "  ".join(
        colored(f"[{d}]", C.GREEN if i < def_wins else C.RED)
        for i, d in enumerate(def_rolls)
    )
    print(f"  Angreifer: {atk_str}")
    print(f"  Verteidiger: {def_str}")
    time.sleep(0.4)

# ───────────────────────────── SPIELER ────────────────────────────
class Player:
    def __init__(self, name: str, color: str, symbol: str, is_ai: bool = False, ai_level: int = 1):
        self.name = name
        self.color = color
        self.symbol = symbol
        self.is_ai = is_ai
        self.ai_level = ai_level  # 1=Leicht, 2=Mittel, 3=Schwer
        self.cards: List[str] = []
        self.territories_conquered_this_turn = 0
        # Statistiken
        self.attacks_total = 0
        self.attacks_won = 0
        self.territories_captured = 0
        self.troops_lost = 0
        self.troops_killed = 0
        self.card_sets_traded = 0

    def colored_name(self):
        return colored(f"{self.symbol} {self.name}", self.color)

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "symbol": self.symbol,
            "is_ai": self.is_ai,
            "ai_level": self.ai_level,
            "cards": self.cards,
            "attacks_total": self.attacks_total,
            "attacks_won": self.attacks_won,
            "territories_captured": self.territories_captured,
            "troops_lost": self.troops_lost,
            "troops_killed": self.troops_killed,
            "card_sets_traded": self.card_sets_traded,
        }

    @classmethod
    def from_dict(cls, d):
        p = cls(d["name"], d["color"], d["symbol"], d["is_ai"], d["ai_level"])
        p.cards = d["cards"]
        p.attacks_total = d.get("attacks_total", 0)
        p.attacks_won = d.get("attacks_won", 0)
        p.territories_captured = d.get("territories_captured", 0)
        p.troops_lost = d.get("troops_lost", 0)
        p.troops_killed = d.get("troops_killed", 0)
        p.card_sets_traded = d.get("card_sets_traded", 0)
        return p

# ──────────────────────────── SPIELSTAND ──────────────────────────
SAVE_DIR = os.path.expanduser("~/.risiko_saves")

def ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)

def list_saves() -> List[str]:
    ensure_save_dir()
    return [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]

def save_game(game_state: dict, slot: str):
    ensure_save_dir()
    path = os.path.join(SAVE_DIR, f"{slot}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(game_state, f, ensure_ascii=False, indent=2)
    print(colored(f"✓ Gespeichert in: {path}", C.GREEN))

def load_game(slot: str) -> Optional[dict]:
    path = os.path.join(SAVE_DIR, f"{slot}.json")
    if not os.path.exists(path):
        print(colored(f"Datei nicht gefunden: {path}", C.RED))
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ───────────────────────────── SPIEL ──────────────────────────────
class RisikoGame:
    def __init__(self):
        self.players: List[Player] = []
        self.board: Dict[str, dict] = {}   # territory -> {owner, troops}
        self.current_player_idx = 0
        self.turn = 1
        self.card_deck: List[str] = []
        self.exchange_count = 0  # wie oft wurden Karten getauscht
        self.game_over = False
        self.winner: Optional[Player] = None

    # ── Initialisierung ──
    def setup_board(self):
        self.board = {t: {"owner": None, "troops": 0} for t in TERRITORIES}

    def setup_card_deck(self):
        terr_list = list(TERRITORIES.keys())
        random.shuffle(terr_list)
        self.card_deck = []
        for i, t in enumerate(terr_list):
            self.card_deck.append(CARD_TYPES[i % 3])
        # 2 Wildcards
        self.card_deck += ["Wildcard", "Wildcard"]
        random.shuffle(self.card_deck)

    def initial_troop_count(self) -> int:
        counts = {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}
        return counts.get(len(self.players), 20)

    def distribute_territories(self):
        """Verteilt Gebiete zufällig, dann platzieren Spieler ihre Truppen."""
        territories = list(TERRITORIES.keys())
        random.shuffle(territories)
        for i, t in enumerate(territories):
            player = self.players[i % len(self.players)]
            self.board[t]["owner"] = player.name
            self.board[t]["troops"] = 1

    def place_initial_troops(self):
        """Spieler platzieren ihre verbleibenden Starttruppen."""
        initial = self.initial_troop_count()
        n_territories = len(TERRITORIES) // len(self.players)
        remaining = {p.name: initial - n_territories for p in self.players}

        # Restliche Runden
        extra = len(TERRITORIES) % len(self.players)
        for i in range(extra):
            remaining[self.players[i].name] -= 1  # einer hat ein Gebiet mehr

        print(colored("\n═══ STARTTRUPPEN PLATZIEREN ═══", C.YELLOW))
        placing = True
        while placing:
            placing = False
            for player in self.players:
                while remaining[player.name] > 0:
                    placing = True
                    if player.is_ai:
                        self._ai_place_troop(player)
                        remaining[player.name] -= 1
                    else:
                        self._human_place_troop(player, remaining[player.name])
                        remaining[player.name] -= 1

    def _human_place_troop(self, player: Player, remaining: int):
        own = [t for t, d in self.board.items() if d["owner"] == player.name]
        print(f"\n{player.colored_name()} – Noch {colored(str(remaining), C.YELLOW)} Truppe(n) zu platzieren")
        self.print_player_territories(player)
        while True:
            t = input("Gebiet wählen: ").strip()
            # Abkürzungs-Matching
            matches = [x for x in own if t.lower() in x.lower()]
            if len(matches) == 1:
                self.board[matches[0]]["troops"] += 1
                print(colored(f"  +1 Truppe in {matches[0]} ({self.board[matches[0]]['troops']} gesamt)", C.GREEN))
                return
            elif len(matches) > 1:
                print(colored(f"  Mehrdeutig: {', '.join(matches)}", C.RED))
            else:
                print(colored("  Unbekannt oder nicht dein Gebiet.", C.RED))

    def _ai_place_troop(self, player: Player):
        """KI platziert Truppen – bevorzugt Grenzgebiete."""
        own = [t for t, d in self.board.items() if d["owner"] == player.name]
        # Grenzgebiete bevorzugen
        border = [t for t in own if any(
            self.board[n]["owner"] != player.name for n in TERRITORIES[t]["neighbors"]
        )]
        target = random.choice(border if border else own)
        self.board[target]["troops"] += 1

    # ── Hauptspiel ──
    def play(self):
        while not self.game_over:
            player = self.players[self.current_player_idx]
            if not self._player_alive(player):
                self._next_player()
                continue

            clear()
            print_banner()
            self.print_status_bar()
            print(f"\n{C.BOLD}{'─'*60}{C.RESET}")
            print(f"  Runde {colored(str(self.turn), C.YELLOW)} │ {player.colored_name()}'s Zug")
            print(f"{'─'*60}")

            if player.is_ai:
                time.sleep(0.5)
                self._ai_turn(player)
            else:
                self._human_turn(player)

            self._check_winner()
            self._next_player()

        self._show_end_screen()

    def _player_alive(self, player: Player) -> bool:
        return any(d["owner"] == player.name for d in self.board.values())

    def _next_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.turn += 1

    # ── Menschlicher Zug ──
    def _human_turn(self, player: Player):
        player.territories_conquered_this_turn = 0

        # 1) Truppen erhalten
        new_troops = self._calculate_reinforcements(player)
        print(f"\n  Du erhältst {colored(str(new_troops), C.GREEN)} Truppe(n).")
        self._maybe_trade_cards(player)
        new_troops = self._calculate_reinforcements(player)  # nach Tausch neu berechnen
        self._place_troops_human(player, new_troops)

        # 2) Angreifen
        print(f"\n{colored('═'*40, C.RED)}")
        print(colored("  ANGRIFFPHASE", C.RED + C.BOLD))
        while True:
            cmd = input("\n  [a]ngreifen  [w]eiter  [k]arte anzeigen  [s]peichern  [q]uit: ").strip().lower()
            if cmd == "a":
                self._attack_human(player)
            elif cmd in ("w", ""):
                break
            elif cmd == "k":
                self._show_cards(player)
            elif cmd == "s":
                self._save_prompt()
            elif cmd == "q":
                self._quit_prompt()

        # 3) Truppen verschieben
        print(f"\n{colored('═'*40, C.CYAN)}")
        print(colored("  VERSCHIEBENPHASE", C.CYAN + C.BOLD))
        cmd = input("\n  Truppen verschieben? [j/N]: ").strip().lower()
        if cmd == "j":
            self._fortify_human(player)

        # Karte ziehen falls Gebiet erobert
        if player.territories_conquered_this_turn > 0 and self.card_deck:
            card = self.card_deck.pop()
            player.cards.append(card)
            print(colored(f"\n  Du erhältst eine Karte: {card}!", C.YELLOW))

    # ── Truppenverstärkung ──
    def _calculate_reinforcements(self, player: Player) -> int:
        owned = [t for t, d in self.board.items() if d["owner"] == player.name]
        troops = max(3, len(owned) // 3)
        # Kontinent-Boni
        for cont, data in CONTINENTS.items():
            if all(self.board[t]["owner"] == player.name for t in data["territories"]):
                troops += data["bonus"]
        return troops

    def _place_troops_human(self, player: Player, n: int):
        own = [t for t, d in self.board.items() if d["owner"] == player.name]
        print(f"\n{colored('═'*40, C.GREEN)}")
        print(colored("  VERSTÄRKUNGSPHASE", C.GREEN + C.BOLD))
        print(f"  Platziere {colored(str(n), C.YELLOW)} Truppe(n) auf deinen Gebieten.")
        remaining = n
        while remaining > 0:
            print(f"\n  Noch {colored(str(remaining), C.YELLOW)} Truppe(n) verfügbar.")
            self.print_player_territories(player)
            raw = input("  Gebiet [Anzahl]: ").strip()
            # Format: "Alberta 3" oder nur "Alberta"
            parts = raw.split()
            count = 1
            if len(parts) >= 2 and parts[-1].isdigit():
                count = int(parts[-1])
                name_part = " ".join(parts[:-1])
            else:
                name_part = " ".join(parts)
            matches = [t for t in own if name_part.lower() in t.lower()]
            if len(matches) == 1:
                count = min(count, remaining)
                self.board[matches[0]]["troops"] += count
                remaining -= count
                print(colored(f"  +{count} in {matches[0]} ({self.board[matches[0]]['troops']} ges.)", C.GREEN))
            elif len(matches) > 1:
                print(colored(f"  Mehrdeutig: {', '.join(matches)}", C.RED))
            else:
                print(colored("  Unbekannt oder nicht dein Gebiet.", C.RED))

    # ── Karten ──
    def _show_cards(self, player: Player):
        if not player.cards:
            print(colored("  Du hast keine Karten.", C.GRAY))
            return
        from collections import Counter
        c = Counter(player.cards)
        print(colored(f"\n  Deine Karten: ", C.YELLOW) + ", ".join(
            f"{colored(str(v), C.WHITE)}x {k}" for k, v in c.items()
        ))

    def _maybe_trade_cards(self, player: Player):
        if len(player.cards) < 3:
            return
        self._show_cards(player)
        if len(player.cards) >= 5:
            print(colored("  Du hast 5+ Karten und MUSST tauschen!", C.RED))
            must = True
        else:
            must = False
            cmd = input("  Karten tauschen? [j/N]: ").strip().lower()
            if cmd != "j":
                return
        self._trade_cards(player, must)

    def _trade_cards(self, player: Player, must: bool = False):
        sets = self._find_card_sets(player.cards)
        if not sets:
            print(colored("  Kein gültiges Set möglich.", C.RED))
            return
        print("  Verfügbare Sets:")
        for i, s in enumerate(sets):
            troops = self._card_exchange_value()
            print(f"    [{i+1}] {' + '.join(s)} → {colored(str(troops), C.GREEN)} Truppen")
        while True:
            raw = input(f"  Set wählen [1-{len(sets)}]: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(sets):
                chosen = sets[int(raw)-1]
                break
            if not must and raw == "":
                return
        for card in chosen:
            if card in player.cards:
                player.cards.remove(card)
        bonus = self._card_exchange_value()
        self.exchange_count += 1
        player.card_sets_traded += 1
        print(colored(f"  Getauscht! Du erhältst {bonus} Bonustruppen.", C.GREEN))
        # Direkt auf ein Gebiet legen
        own = [t for t, d in self.board.items() if d["owner"] == player.name]
        self._place_troops_human(player, bonus)

    def _card_exchange_value(self) -> int:
        idx = min(self.exchange_count, len(CARD_EXCHANGE_BONUS)-1)
        return CARD_EXCHANGE_BONUS[idx]

    def _find_card_sets(self, cards: List[str]) -> List[Tuple]:
        from collections import Counter
        c = Counter(cards)
        results = []
        # Drei gleiche
        for ct in CARD_TYPES:
            if c[ct] + c.get("Wildcard", 0) >= 3:
                if c[ct] >= 3:
                    results.append((ct, ct, ct))
        # Ein von jedem
        types_have = [t for t in CARD_TYPES if c[t] >= 1]
        if len(types_have) >= 3:
            results.append(("Infanterie", "Kavallerie", "Artillerie"))
        return results

    # ── Angriff ──
    def _attack_human(self, player: Player):
        own_with_2plus = [t for t, d in self.board.items()
                          if d["owner"] == player.name and d["troops"] >= 2]
        if not own_with_2plus:
            print(colored("  Keine Gebiete mit genug Truppen.", C.RED))
            return
        self.print_player_territories(player)
        print(colored("\n  Von welchem Gebiet angreifen?", C.RED))
        from_t = self._input_territory(own_with_2plus, "  Von: ")
        if not from_t:
            return
        # Mögliche Ziele
        targets = [n for n in TERRITORIES[from_t]["neighbors"]
                   if self.board[n]["owner"] != player.name]
        if not targets:
            print(colored("  Keine feindlichen Nachbarn.", C.RED))
            return
        print(colored(f"\n  Ziele von {from_t}:", C.RED))
        for t in targets:
            owner = self.board[t]["owner"]
            p = self._get_player(owner)
            col = p.color if p else C.GRAY
            print(f"    {colored(t, col)} ({owner}) – {self.board[t]['troops']} Truppen")
        to_t = self._input_territory(targets, "  Ziel: ")
        if not to_t:
            return

        # Würfelanzahl
        max_atk = min(3, self.board[from_t]["troops"] - 1)
        print(f"  Wie viele Würfel? (1-{max_atk}, oder 'a' für alles bis Sieg)")
        raw = input("  Würfel: ").strip().lower()
        auto = raw == "a"
        if not auto:
            dice = int(raw) if raw.isdigit() and 1 <= int(raw) <= max_atk else 1
        else:
            dice = max_atk

        self._resolve_attack(player, from_t, to_t, dice, auto)

    def _resolve_attack(self, player: Player, from_t: str, to_t: str, atk_dice: int, auto: bool = False):
        while True:
            atk_troops = self.board[from_t]["troops"]
            def_troops = self.board[to_t]["troops"]
            if atk_troops < 2:
                break

            atk_dice = min(3, atk_troops - 1)
            def_dice = min(2, def_troops)

            atk_rolls = roll_dice(atk_dice)
            def_rolls = roll_dice(def_dice)

            # Vergleichen
            atk_wins = 0
            def_wins = 0
            for a, d in zip(atk_rolls, def_rolls):
                if a > d:
                    atk_wins += 1
                else:
                    def_wins += 1

            animate_battle(atk_rolls, def_rolls, atk_wins, def_wins)

            self.board[from_t]["troops"] -= def_wins
            self.board[to_t]["troops"] -= atk_wins
            player.troops_lost += def_wins
            player.troops_killed += atk_wins
            player.attacks_total += 1

            def_owner = self.board[to_t]["owner"]
            def_player = self._get_player(def_owner)
            if def_player:
                def_player.troops_lost += atk_wins

            if self.board[to_t]["troops"] <= 0:
                # Gebiet eingenommen
                move = min(atk_dice, self.board[from_t]["troops"] - 1)
                self.board[to_t]["owner"] = player.name
                self.board[to_t]["troops"] = move
                self.board[from_t]["troops"] -= move
                player.territories_conquered_this_turn += 1
                player.attacks_won += 1
                player.territories_captured += 1
                print(colored(f"\n  ✓ {to_t} eingenommen! ({move} Truppen verschoben)", C.GREEN))
                # Verteidiger noch am Leben?
                if def_player and not self._player_alive(def_player):
                    print(colored(f"\n  {def_player.colored_name()} wurde eliminiert!", C.RED))
                    # Karten übernehmen
                    player.cards += def_player.cards
                    def_player.cards = []
                break

            if not auto:
                break
            if self.board[from_t]["troops"] < 2:
                break

    def _fortify_human(self, player: Player):
        own = [t for t, d in self.board.items() if d["owner"] == player.name]
        print("\n  Truppen von → nach verschieben.")
        from_t = self._input_territory(
            [t for t in own if self.board[t]["troops"] >= 2], "  Von: ")
        if not from_t:
            return
        # Erreichbare eigene Gebiete (BFS)
        reachable = self._reachable(player, from_t)
        reachable.discard(from_t)
        if not reachable:
            print(colored("  Keine erreichbaren eigenen Gebiete.", C.RED))
            return
        to_t = self._input_territory(list(reachable), "  Nach: ")
        if not to_t:
            return
        max_move = self.board[from_t]["troops"] - 1
        print(f"  Wie viele Truppen verschieben? (1-{max_move})")
        raw = input("  Anzahl: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= max_move:
            n = int(raw)
            self.board[from_t]["troops"] -= n
            self.board[to_t]["troops"] += n
            print(colored(f"  {n} Truppen von {from_t} → {to_t}", C.CYAN))

    def _reachable(self, player: Player, start: str) -> set:
        visited = set()
        queue = [start]
        while queue:
            cur = queue.pop()
            if cur in visited:
                continue
            visited.add(cur)
            for n in TERRITORIES[cur]["neighbors"]:
                if self.board[n]["owner"] == player.name and n not in visited:
                    queue.append(n)
        return visited

    def _input_territory(self, valid: List[str], prompt: str) -> Optional[str]:
        if not valid:
            return None
        for v in sorted(valid):
            print(f"    {v} ({self.board[v]['troops']} Tr.)")
        raw = input(prompt).strip()
        if raw == "":
            return None
        matches = [t for t in valid if raw.lower() in t.lower()]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(colored(f"  Mehrdeutig: {', '.join(matches)}", C.RED))
            return None
        else:
            print(colored("  Unbekannt.", C.RED))
            return None

    # ── KI-Zug ──
    def _ai_turn(self, player: Player):
        print(f"\n  {player.colored_name()} denkt nach...")
        time.sleep(0.6)
        player.territories_conquered_this_turn = 0

        # Karten tauschen wenn möglich
        if len(player.cards) >= 3 and self._find_card_sets(player.cards):
            sets = self._find_card_sets(player.cards)
            chosen = sets[0]
            for card in chosen:
                if card in player.cards:
                    player.cards.remove(card)
            bonus = self._card_exchange_value()
            self.exchange_count += 1
            player.card_sets_traded += 1
            self._ai_place_troops(player, bonus)

        # Truppen erhalten und platzieren
        new_troops = self._calculate_reinforcements(player)
        print(f"  {player.colored_name()} erhält {colored(str(new_troops), C.GREEN)} Truppen.")
        self._ai_place_troops(player, new_troops)

        # Angreifen
        for _ in range(10 * player.ai_level):
            if not self._ai_attack(player):
                break

        # Verschieben
        self._ai_fortify(player)

        # Karte ziehen
        if player.territories_conquered_this_turn > 0 and self.card_deck:
            card = self.card_deck.pop()
            player.cards.append(card)

    def _ai_place_troops(self, player: Player, n: int):
        own = [t for t, d in self.board.items() if d["owner"] == player.name]
        # Starke KI: Grenzgebiete mit wenig Truppen bevorzugen
        for _ in range(n):
            border = sorted(
                [t for t in own if any(self.board[nb]["owner"] != player.name
                                       for nb in TERRITORIES[t]["neighbors"])],
                key=lambda t: self.board[t]["troops"]
            )
            target = border[0] if border else random.choice(own)
            self.board[target]["troops"] += 1

    def _ai_attack(self, player: Player) -> bool:
        own = [t for t, d in self.board.items()
               if d["owner"] == player.name and d["troops"] >= 2]
        random.shuffle(own)
        for from_t in own:
            targets = [n for n in TERRITORIES[from_t]["neighbors"]
                       if self.board[n]["owner"] != player.name]
            for to_t in targets:
                atk = self.board[from_t]["troops"]
                dfc = self.board[to_t]["troops"]
                # KI greift an wenn sie Vorteil hat (je nach Schwierigkeitsgrad)
                ratio = {1: 2.5, 2: 1.8, 3: 1.3}[player.ai_level]
                if atk > dfc * ratio:
                    self._resolve_attack(player, from_t, to_t,
                                         min(3, atk-1), auto=True)
                    return True
        return False

    def _ai_fortify(self, player: Player):
        own = [t for t, d in self.board.items() if d["owner"] == player.name]
        # Verschiebe Truppen von sicheren Gebieten zu Grenzgebieten
        interior = [t for t in own if all(
            self.board[n]["owner"] == player.name for n in TERRITORIES[t]["neighbors"]
        ) and self.board[t]["troops"] > 1]
        border = sorted(
            [t for t in own if any(self.board[n]["owner"] != player.name
                                   for n in TERRITORIES[t]["neighbors"])],
            key=lambda t: self.board[t]["troops"]
        )
        if interior and border:
            from_t = interior[0]
            to_t = border[0]
            reachable = self._reachable(player, from_t)
            if to_t in reachable:
                n = self.board[from_t]["troops"] - 1
                self.board[from_t]["troops"] = 1
                self.board[to_t]["troops"] += n

    # ── Sieg prüfen ──
    def _check_winner(self):
        alive = [p for p in self.players if self._player_alive(p)]
        if len(alive) == 1:
            self.game_over = True
            self.winner = alive[0]

    def _get_player(self, name: str) -> Optional[Player]:
        for p in self.players:
            if p.name == name:
                return p
        return None

    # ── Anzeige ──
    def print_status_bar(self):
        print(f"\n  {'Spieler':<20} {'Gebiete':>8} {'Truppen':>8} {'Karten':>7}")
        print(f"  {'─'*50}")
        for p in self.players:
            alive = self._player_alive(p)
            terr = len([t for t, d in self.board.items() if d["owner"] == p.name])
            troops = sum(d["troops"] for d in self.board.values() if d["owner"] == p.name)
            cards = len(p.cards)
            status = "" if alive else colored(" [eliminiert]", C.GRAY)
            print(f"  {p.colored_name():<35} {terr:>4}     {troops:>4}    {cards:>4}{status}")

    def print_player_territories(self, player: Player):
        own = {t: d for t, d in self.board.items() if d["owner"] == player.name}
        # Gruppiert nach Kontinent
        by_cont = defaultdict(list)
        for t in own:
            by_cont[TERRITORIES[t]["continent"]].append(t)
        print()
        for cont, terrs in sorted(by_cont.items()):
            bonus = CONTINENTS[cont]["bonus"]
            has_all = all(self.board[t]["owner"] == player.name
                          for t in CONTINENTS[cont]["territories"])
            cont_str = colored(f"[{cont}]", C.YELLOW if has_all else C.GRAY)
            print(f"  {cont_str} (Bonus: {bonus})")
            for t in sorted(terrs):
                troops = own[t]["troops"]
                bar = colored("█" * min(troops, 10), C.GREEN if troops >= 3 else C.RED)
                print(f"    {t:<28} {bar} {troops}")

    def print_world_map(self):
        """Einfache Textdarstellung der Kontinente."""
        print(colored("\n  ═══ WELTKARTE ═══", C.CYAN))
        for cont, data in CONTINENTS.items():
            print(f"\n  {colored(cont, C.YELLOW)} (Bonus: {data['bonus']})")
            for t in data["territories"]:
                owner = self.board[t]["owner"]
                p = self._get_player(owner) if owner else None
                col = p.color if p else C.GRAY
                sym = p.symbol if p else "?"
                troops = self.board[t]["troops"]
                print(f"    {colored(sym, col)} {t:<28} {troops} Tr.")

    # ── Speichern / Laden ──
    def to_dict(self) -> dict:
        return {
            "version": 2,
            "saved_at": datetime.now().isoformat(),
            "players": [p.to_dict() for p in self.players],
            "board": self.board,
            "current_player_idx": self.current_player_idx,
            "turn": self.turn,
            "card_deck": self.card_deck,
            "exchange_count": self.exchange_count,
        }

    def from_dict(self, d: dict):
        self.players = [Player.from_dict(p) for p in d["players"]]
        self.board = d["board"]
        self.current_player_idx = d["current_player_idx"]
        self.turn = d["turn"]
        self.card_deck = d["card_deck"]
        self.exchange_count = d["exchange_count"]

    def _save_prompt(self):
        slot = input("  Spielstand-Name (Enter = 'autosave'): ").strip() or "autosave"
        save_game(self.to_dict(), slot)

    def _quit_prompt(self):
        cmd = input("  Vorher speichern? [j/N]: ").strip().lower()
        if cmd == "j":
            self._save_prompt()
        sys.exit(0)

    # ── Endbildschirm ──
    def _show_end_screen(self):
        clear()
        print_banner()
        if self.winner:
            print(f"\n{C.BOLD}{'═'*60}{C.RESET}")
            print(f"\n  🏆  {self.winner.colored_name()} HAT GEWONNEN! 🏆")
            print(f"\n{'═'*60}")
        print(colored("\n  ═══ STATISTIKEN ═══", C.YELLOW))
        print(f"\n  {'Spieler':<20} {'Gebiet':>6} {'Angriff':>8} {'Gewon':>6} {'Get.':>6} {'Verlor':>7}")
        print(f"  {'─'*60}")
        for p in self.players:
            terr = len([t for t in self.board if self.board[t]["owner"] == p.name])
            win_rate = f"{100*p.attacks_won//p.attacks_total}%" if p.attacks_total > 0 else "–"
            print(f"  {p.colored_name():<35} {terr:>3}  {p.attacks_total:>5}   {win_rate:>6} {p.troops_killed:>5}  {p.troops_lost:>6}")
        pause("\nDrücke ENTER zum Beenden.")

# ──────────────────────────── HAUPTMENÜ ───────────────────────────
def main_menu():
    while True:
        clear()
        print_banner()
        print(f"  {bold('[1]')} Neues Spiel")
        print(f"  {bold('[2]')} Spiel laden")
        print(f"  {bold('[3]')} Regeln")
        print(f"  {bold('[0]')} Beenden")
        choice = input("\n  Wahl: ").strip()
        if choice == "1":
            game = setup_new_game()
            if game:
                game.play()
        elif choice == "2":
            game = load_existing_game()
            if game:
                game.play()
        elif choice == "3":
            show_rules()
        elif choice == "0":
            print(colored("\nAuf Wiedersehen!\n", C.CYAN))
            sys.exit(0)

def setup_new_game() -> Optional[RisikoGame]:
    clear()
    print_banner()
    print(colored("  ═══ NEUES SPIEL ═══\n", C.YELLOW))
    # Spieleranzahl
    while True:
        raw = input("  Anzahl Menschliche Spieler (1-6): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 6:
            n_human = int(raw)
            break
    n_ai = 0
    if n_human < 6:
        while True:
            raw = input(f"  Anzahl KI-Gegner (0-{6-n_human}): ").strip()
            if raw.isdigit() and 0 <= int(raw) <= 6 - n_human:
                n_ai = int(raw)
                break
    if n_human + n_ai < 2:
        print(colored("  Mindestens 2 Spieler nötig!", C.RED))
        pause()
        return None

    players = []
    color_idx = 0
    for i in range(n_human):
        name = input(f"  Name Spieler {i+1}: ").strip() or f"Spieler{i+1}"
        players.append(Player(name, PLAYER_COLORS[color_idx], PLAYER_SYMBOLS[color_idx]))
        color_idx += 1

    ai_level = 1
    if n_ai > 0:
        print("\n  KI-Schwierigkeitsgrad:")
        print("    [1] Leicht   [2] Mittel   [3] Schwer")
        raw = input("  Wahl [1]: ").strip()
        ai_level = int(raw) if raw in ("1","2","3") else 1

    ai_names = ["Napoleon", "Caesar", "Alexandra", "Kublai", "Bismarck", "Hanibal"]
    for i in range(n_ai):
        name = ai_names[i % len(ai_names)]
        players.append(Player(name, PLAYER_COLORS[color_idx], PLAYER_SYMBOLS[color_idx],
                               is_ai=True, ai_level=ai_level))
        color_idx += 1

    random.shuffle(players)
    game = RisikoGame()
    game.players = players
    game.setup_board()
    game.setup_card_deck()

    print(colored("\n  ═══ STARTREIHENFOLGE ═══", C.CYAN))
    for i, p in enumerate(players):
        ai_str = colored(f" (KI Stufe {p.ai_level})", C.GRAY) if p.is_ai else ""
        print(f"    {i+1}. {p.colored_name()}{ai_str}")

    print(colored("\n  ═══ GEBIETE WERDEN VERTEILT ═══", C.CYAN))
    game.distribute_territories()
    game.place_initial_troops()

    return game

def load_existing_game() -> Optional[RisikoGame]:
    saves = list_saves()
    if not saves:
        print(colored("\n  Keine gespeicherten Spiele gefunden.", C.RED))
        pause()
        return None
    print(colored("\n  ═══ GESPEICHERTE SPIELE ═══", C.YELLOW))
    for i, s in enumerate(saves):
        print(f"    [{i+1}] {s.replace('.json','')}")
    raw = input("\n  Wahl (Nr. oder Name): ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(saves):
        slot = saves[int(raw)-1].replace(".json","")
    else:
        slot = raw
    data = load_game(slot)
    if not data:
        pause()
        return None
    game = RisikoGame()
    game.from_dict(data)
    print(colored(f"\n  Spiel geladen! Runde {game.turn}", C.GREEN))
    pause()
    return game

def show_rules():
    clear()
    print_banner()
    rules = f"""
{colored("RISIKO – REGELN", C.YELLOW + C.BOLD)}

{bold("ZIEL:")} Alle Gebiete der Welt erobern.

{bold("SPIELABLAUF je Runde:")}
  1. {colored("Verstärkung", C.GREEN)}: Erhalte Truppen (max(3, Gebiete/3) + Kontinent-Boni).
  2. {colored("Angriff", C.RED)}: Greife benachbarte feindliche Gebiete an.
  3. {colored("Verschieben", C.CYAN)}: Bewege Truppen zwischen verbundenen eigenen Gebieten.

{bold("KAMPF:")}
  • Angreifer würfelt bis zu 3 Würfel (muss ≥2 Truppen haben).
  • Verteidiger würfelt bis zu 2 Würfel.
  • Höchste Würfel werden verglichen – bei Gleichstand gewinnt der Verteidiger.

{bold("KONTINENTE (Bonus pro Runde):")}
""" + "\n".join(
        f"  • {colored(c, C.YELLOW)}: +{d['bonus']} ({len(d['territories'])} Gebiete)"
        for c, d in CONTINENTS.items()
    ) + f"""

{bold("KARTEN:")}
  • Für jedes eroberte Gebiet ziehst du eine Karte.
  • 3 Karten können gegen Truppen getauscht werden:
    – 3 gleiche oder 1 von jeder Sorte.
  • Bonus steigt mit jedem Tausch.

{bold("EXTRAS:")}
  • KI-Gegner mit 3 Schwierigkeitsstufen
  • Automatischer Angriff bis Sieg ('a')
  • Spielstand jederzeit speichern
"""
    print(rules)
    pause()

# ───────────────────────────── MAIN ───────────────────────────────
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(colored("\n\nSpiel abgebrochen.", C.GRAY))
        sys.exit(0)
