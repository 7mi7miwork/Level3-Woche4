"""
EVOLUTION CLICKER - Ein umfangreiches Idle-Clicker-Spiel
=========================================================

Ein vollständiges Idle-Clicker-Spiel mit:
- 6 Evolutionsstufen (Steinzeit → Zukunft)
- 30+ verschiedene Gebäude und Upgrades
- Prestige-System mit Multiplikatoren
- Achievements und Statistiken
- Auto-Clicker und Boost-System
- Speichern/Laden Funktion
- Partikel-Effekte und Animationen
- Offline-Fortschritt

Evolutionsstufen:
1. STEINZEIT: Sammle Steine und Holz
2. ANTIKE: Baue Dörfer und Farmen
3. MITTELALTER: Errichte Burgen und Gilden
4. INDUSTRIAL: Fabriken und Maschinen
5. MODERN: Computer und Technologie
6. ZUKUNFT: KI und Raumfahrt

Steuerung:
- Linksklick auf Hauptressource = +1 Ressource
- Klick auf Gebäude = Kaufen
- Klick auf Upgrade = Aktivieren
- ESC = Hauptmenü
- S = Speichern
- L = Laden
- P = Prestige (wenn verfügbar)
"""

import pygame
import random
import math
import json
import os
import time
from datetime import datetime, timedelta

# Pygame initialisieren
pygame.init()

# Konstanten
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 200)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)


class Particle:
    """Partikel für visuelle Effekte"""
    def __init__(self, x, y, color, text=None):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, -2)
        self.lifetime = random.randint(30, 60)
        self.age = 0
        self.text = text
        self.size = random.randint(3, 6)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Schwerkraft
        self.age += 1
        
    def draw(self, screen, font):
        if self.age < self.lifetime:
            alpha_factor = 1 - (self.age / self.lifetime)
            if self.text:
                text_surf = font.render(self.text, True, self.color)
                text_surf.set_alpha(int(255 * alpha_factor))
                screen.blit(text_surf, (int(self.x), int(self.y)))
            else:
                size = max(1, int(self.size * alpha_factor))
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
                
    def is_alive(self):
        return self.age < self.lifetime


class Building:
    """Gebäude-Klasse für passive Ressourcenproduktion"""
    def __init__(self, name, base_cost, base_production, icon, era, description):
        self.name = name
        self.base_cost = base_cost
        self.base_production = base_production
        self.count = 0
        self.icon = icon
        self.era = era
        self.description = description
        self.unlocked = (era == 0)  # Steinzeit-Gebäude sind freigeschaltet
        
    def get_cost(self):
        """Berechne aktuellen Preis basierend auf Anzahl (steigt exponentiell)"""
        return int(self.base_cost * (1.15 ** self.count))
    
    def get_production(self):
        """Berechne aktuelle Produktion pro Sekunde"""
        return self.base_production * self.count
    
    def purchase(self, resources):
        """Kaufe ein Gebäude"""
        cost = self.get_cost()
        if resources >= cost:
            self.count += 1
            return cost
        return 0
    
    def get_info(self):
        """Informationstext für Tooltip"""
        return (f"{self.name}\n"
                f"Besitz: {self.count}\n"
                f"Kosten: {format_number(self.get_cost())}\n"
                f"Produktion: {format_number(self.base_production)}/s\n"
                f"Gesamt: {format_number(self.get_production())}/s\n"
                f"{self.description}")


class Upgrade:
    """Upgrade-Klasse für Multiplikatoren und Boni"""
    def __init__(self, name, cost, multiplier, upgrade_type, era, description, icon="⬆"):
        self.name = name
        self.cost = cost
        self.multiplier = multiplier
        self.upgrade_type = upgrade_type  # 'click', 'production', 'building'
        self.era = era
        self.description = description
        self.icon = icon
        self.purchased = False
        self.unlocked = (era == 0)
        
    def purchase(self):
        """Kaufe Upgrade"""
        self.purchased = True
        
    def get_info(self):
        """Informationstext"""
        return (f"{self.name}\n"
                f"Kosten: {format_number(self.cost)}\n"
                f"Effekt: x{self.multiplier}\n"
                f"{self.description}")


class Achievement:
    """Achievement-System"""
    def __init__(self, name, description, requirement_type, requirement_value, reward):
        self.name = name
        self.description = description
        self.requirement_type = requirement_type  # 'resources', 'clicks', 'buildings', etc.
        self.requirement_value = requirement_value
        self.reward = reward  # Prestige-Punkte
        self.unlocked = False
        
    def check(self, game_state):
        """Prüfe ob Achievement erfüllt ist"""
        if self.unlocked:
            return False
            
        if self.requirement_type == 'resources':
            return game_state['total_earned'] >= self.requirement_value
        elif self.requirement_type == 'clicks':
            return game_state['total_clicks'] >= self.requirement_value
        elif self.requirement_type == 'buildings':
            return game_state['total_buildings'] >= self.requirement_value
        elif self.requirement_type == 'era':
            return game_state['current_era'] >= self.requirement_value
        return False


def format_number(num):
    """Formatiere große Zahlen lesbar"""
    if num < 1000:
        return str(int(num))
    elif num < 1000000:
        return f"{num/1000:.1f}K"
    elif num < 1000000000:
        return f"{num/1000000:.1f}M"
    elif num < 1000000000000:
        return f"{num/1000000000:.1f}B"
    elif num < 1000000000000000:
        return f"{num/1000000000000:.1f}T"
    else:
        return f"{num/1000000000000000:.1f}Q"


class Button:
    """UI Button Klasse"""
    def __init__(self, x, y, width, height, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, screen, font):
        # Hover-Effekt
        color = self.color
        if self.hovered:
            color = tuple(min(255, c + 30) for c in self.color)
            
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)


class Game:
    """Haupt-Spielklasse"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Evolution Clicker - Von der Steinzeit zur Zukunft!")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'  # menu, playing, achievements, stats, prestige
        
        # Schriftarten
        self.font_huge = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Spielstand
        self.resources = 0
        self.total_earned = 0
        self.total_clicks = 0
        self.click_power = 1
        self.production_per_second = 0
        self.current_era = 0
        self.prestige_points = 0
        self.prestige_multiplier = 1.0
        
        # Zeit-Tracking
        self.last_save_time = time.time()
        self.session_start = time.time()
        
        # Eras
        self.eras = [
            {"name": "STEINZEIT", "color": BROWN, "threshold": 0, "icon": "🪨"},
            {"name": "ANTIKE", "color": GOLD, "threshold": 1000, "icon": "🏛️"},
            {"name": "MITTELALTER", "color": DARK_BLUE, "threshold": 50000, "icon": "🏰"},
            {"name": "INDUSTRIAL", "color": GRAY, "threshold": 1000000, "icon": "🏭"},
            {"name": "MODERN", "color": BLUE, "threshold": 50000000, "icon": "💻"},
            {"name": "ZUKUNFT", "color": PURPLE, "threshold": 1000000000, "icon": "🚀"}
        ]
        
        # Gebäude initialisieren
        self.buildings = self.initialize_buildings()
        
        # Upgrades initialisieren
        self.upgrades = self.initialize_upgrades()
        
        # Achievements initialisieren
        self.achievements = self.initialize_achievements()
        
        # UI-Elemente
        self.particles = []
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Klickbarer Bereich für Hauptressource
        self.click_area = pygame.Rect(100, 150, 300, 300)
        self.click_animation = 0
        
        # Auto-Clicker
        self.auto_clicker_active = False
        self.auto_click_timer = 0
        self.auto_click_interval = 60  # Frames zwischen Auto-Clicks
        
        # Boost-System
        self.boost_active = False
        self.boost_timer = 0
        self.boost_duration = 600  # 10 Sekunden bei 60 FPS
        self.boost_multiplier = 5
        
        # Statistiken
        self.stats = {
            'total_time_played': 0,
            'total_buildings_purchased': 0,
            'total_upgrades_purchased': 0,
            'highest_resources': 0,
            'prestiges': 0
        }
        
    def initialize_buildings(self):
        """Erstelle alle Gebäude für jede Era"""
        buildings = []
        
        # STEINZEIT (Era 0)
        buildings.append(Building("Steinsammler", 10, 0.1, "🪨", 0, 
                                 "Sammelt automatisch Steine"))
        buildings.append(Building("Holzfäller", 50, 0.5, "🪵", 0, 
                                 "Fällt Bäume für Ressourcen"))
        buildings.append(Building("Jäger", 200, 2, "🏹", 0, 
                                 "Jagt wilde Tiere"))
        buildings.append(Building("Lagerfeuer", 800, 8, "🔥", 0, 
                                 "Wärmt und motiviert"))
        buildings.append(Building("Höhle", 3000, 30, "⛰️", 0, 
                                 "Sichere Unterkunft"))
        
        # ANTIKE (Era 1)
        buildings.append(Building("Farm", 10000, 100, "🌾", 1, 
                                 "Produziert Nahrung"))
        buildings.append(Building("Dorf", 40000, 400, "🏘️", 1, 
                                 "Bringt neue Arbeiter"))
        buildings.append(Building("Tempel", 150000, 1500, "⛩️", 1, 
                                 "Göttlicher Segen"))
        buildings.append(Building("Marktplatz", 500000, 5000, "🏪", 1, 
                                 "Handelt mit anderen"))
        buildings.append(Building("Bibliothek", 2000000, 20000, "📚", 1, 
                                 "Sammelt Wissen"))
        
        # MITTELALTER (Era 2)
        buildings.append(Building("Burg", 10000000, 100000, "🏰", 2, 
                                 "Verteidigt dein Reich"))
        buildings.append(Building("Gilde", 40000000, 400000, "⚔️", 2, 
                                 "Organisiert Handwerker"))
        buildings.append(Building("Kathedrale", 150000000, 1500000, "⛪", 2, 
                                 "Monumentales Bauwerk"))
        buildings.append(Building("Hafen", 600000000, 6000000, "⚓", 2, 
                                 "Ermöglicht Seehandel"))
        buildings.append(Building("Universität", 2500000000, 25000000, "🎓", 2, 
                                 "Bildet Gelehrte aus"))
        
        # INDUSTRIAL (Era 3)
        buildings.append(Building("Fabrik", 10000000000, 100000000, "🏭", 3, 
                                 "Massenproduktion"))
        buildings.append(Building("Kraftwerk", 50000000000, 500000000, "⚡", 3, 
                                 "Erzeugt Energie"))
        buildings.append(Building("Eisenbahn", 200000000000, 2000000000, "🚂", 3, 
                                 "Transportiert Güter"))
        buildings.append(Building("Bank", 1000000000000, 10000000000, "🏦", 3, 
                                 "Verwaltet Reichtum"))
        buildings.append(Building("Labor", 5000000000000, 50000000000, "🔬", 3, 
                                 "Forscht neue Technologien"))
        
        # MODERN (Era 4)
        buildings.append(Building("Rechenzentrum", 25000000000000, 250000000000, "💻", 4, 
                                 "Verarbeitet Daten"))
        buildings.append(Building("Startup", 100000000000000, 1000000000000, "📱", 4, 
                                 "Innovative Technologie"))
        buildings.append(Building("Forschungsinstitut", 500000000000000, 5000000000000, "🧬", 4, 
                                 "Fortgeschrittene Wissenschaft"))
        buildings.append(Building("Wolkenkratzer", 2000000000000000, 20000000000000, "🏢", 4, 
                                 "Symbol des Fortschritts"))
        buildings.append(Building("Kernreaktor", 10000000000000000, 100000000000000, "☢️", 4, 
                                 "Unbegrenzte Energie"))
        
        # ZUKUNFT (Era 5)
        buildings.append(Building("KI-System", 50000000000000000, 500000000000000, "🤖", 5, 
                                 "Künstliche Intelligenz"))
        buildings.append(Building("Raumstation", 250000000000000000, 2500000000000000, "🛸", 5, 
                                 "Orbitale Plattform"))
        buildings.append(Building("Terraformer", 1000000000000000000, 10000000000000000, "🌍", 5, 
                                 "Formt Planeten um"))
        buildings.append(Building("Zeitmaschine", 5000000000000000000, 50000000000000000, "⏰", 5, 
                                 "Manipuliert Zeit"))
        buildings.append(Building("Universumsportal", 25000000000000000000, 250000000000000000, "🌌", 5, 
                                 "Zugang zu neuen Dimensionen"))
        
        return buildings
    
    def initialize_upgrades(self):
        """Erstelle alle Upgrades"""
        upgrades = []
        
        # STEINZEIT Upgrades
        upgrades.append(Upgrade("Steinwerkzeuge", 100, 2, 'click', 0, 
                               "Verdoppelt Click-Power", "🔨"))
        upgrades.append(Upgrade("Feuerstein", 500, 2, 'production', 0, 
                               "Verdoppelt Steinzeit-Produktion", "✨"))
        upgrades.append(Upgrade("Stammesführer", 2000, 3, 'click', 0, 
                               "Verdreifacht Click-Power", "👑"))
        
        # ANTIKE Upgrades
        upgrades.append(Upgrade("Bronze-Werkzeuge", 50000, 2, 'production', 1, 
                               "Verdoppelt Antike-Produktion", "🔧"))
        upgrades.append(Upgrade("Schrift", 200000, 2, 'click', 1, 
                               "Verdoppelt Click-Power", "📜"))
        upgrades.append(Upgrade("Bewässerung", 800000, 3, 'production', 1, 
                               "Verdreifacht Farm-Produktion", "💧"))
        
        # MITTELALTER Upgrades
        upgrades.append(Upgrade("Stahl", 50000000, 2, 'production', 2, 
                               "Verdoppelt Mittelalter-Produktion", "⚔️"))
        upgrades.append(Upgrade("Gotische Architektur", 200000000, 3, 'click', 2, 
                               "Verdreifacht Click-Power", "🏰"))
        upgrades.append(Upgrade("Handelswege", 1000000000, 2, 'production', 2, 
                               "Verdoppelt Hafen-Produktion", "🗺️"))
        
        # INDUSTRIAL Upgrades
        upgrades.append(Upgrade("Dampfmaschine", 50000000000, 2, 'production', 3, 
                               "Verdoppelt Industrial-Produktion", "⚙️"))
        upgrades.append(Upgrade("Elektrizität", 500000000000, 3, 'click', 3, 
                               "Verdreifacht Click-Power", "⚡"))
        upgrades.append(Upgrade("Fließband", 2500000000000, 4, 'production', 3, 
                               "Vervierfacht Fabrik-Produktion", "🏭"))
        
        # MODERN Upgrades
        upgrades.append(Upgrade("Internet", 100000000000000, 2, 'production', 4, 
                               "Verdoppelt Modern-Produktion", "🌐"))
        upgrades.append(Upgrade("Quantencomputer", 1000000000000000, 5, 'click', 4, 
                               "Verfünffacht Click-Power", "💻"))
        upgrades.append(Upgrade("Cloud Computing", 10000000000000000, 3, 'production', 4, 
                               "Verdreifacht Rechenzentrum-Produktion", "☁️"))
        
        # ZUKUNFT Upgrades
        upgrades.append(Upgrade("Künstliche Intelligenz", 500000000000000000, 10, 'click', 5, 
                               "Verzehnfacht Click-Power", "🤖"))
        upgrades.append(Upgrade("Nanobots", 5000000000000000000, 5, 'production', 5, 
                               "Verfünffacht Zukunft-Produktion", "🔬"))
        upgrades.append(Upgrade("Antimaterie", 50000000000000000000, 10, 'production', 5, 
                               "Verzehnfacht alle Produktion", "💫"))
        
        return upgrades
    
    def initialize_achievements(self):
        """Erstelle Achievements"""
        achievements = []
        
        achievements.append(Achievement("Erster Klick", "Klicke zum ersten Mal", 
                                       'clicks', 1, 1))
        achievements.append(Achievement("Fleißiger Klicker", "Klicke 100 Mal", 
                                       'clicks', 100, 5))
        achievements.append(Achievement("Klick-Meister", "Klicke 1000 Mal", 
                                       'clicks', 1000, 10))
        achievements.append(Achievement("Klick-Legende", "Klicke 10000 Mal", 
                                       'clicks', 10000, 25))
        
        achievements.append(Achievement("Erste Ressourcen", "Sammle 100 Ressourcen", 
                                       'resources', 100, 1))
        achievements.append(Achievement("Wohlhabend", "Sammle 100K Ressourcen", 
                                       'resources', 100000, 10))
        achievements.append(Achievement("Reich", "Sammle 100M Ressourcen", 
                                       'resources', 100000000, 25))
        achievements.append(Achievement("Unbegrenzt Reich", "Sammle 100B Ressourcen", 
                                       'resources', 100000000000, 50))
        
        achievements.append(Achievement("Erste Immobilie", "Kaufe 10 Gebäude", 
                                       'buildings', 10, 5))
        achievements.append(Achievement("Immobilien-Mogul", "Kaufe 100 Gebäude", 
                                       'buildings', 100, 15))
        achievements.append(Achievement("Baumeister", "Kaufe 500 Gebäude", 
                                       'buildings', 500, 30))
        
        achievements.append(Achievement("Zeitreisender", "Erreiche die Antike", 
                                       'era', 1, 10))
        achievements.append(Achievement("Mittelalterlicher Herrscher", "Erreiche das Mittelalter", 
                                       'era', 2, 20))
        achievements.append(Achievement("Industrieller Titan", "Erreiche die Industrielle Revolution", 
                                       'era', 3, 30))
        achievements.append(Achievement("Moderner Visionär", "Erreiche die Moderne", 
                                       'era', 4, 40))
        achievements.append(Achievement("Zukunfts-Pionier", "Erreiche die Zukunft", 
                                       'era', 5, 50))
        
        return achievements
    
    def update_era(self):
        """Prüfe und aktualisiere die aktuelle Era"""
        old_era = self.current_era
        for i, era in enumerate(self.eras):
            if self.total_earned >= era['threshold']:
                self.current_era = i
        
        # Schalte Gebäude und Upgrades für neue Era frei
        if self.current_era > old_era:
            for building in self.buildings:
                if building.era <= self.current_era:
                    building.unlocked = True
            for upgrade in self.upgrades:
                if upgrade.era <= self.current_era:
                    upgrade.unlocked = True
            
            # Erstelle Partikel für Era-Wechsel
            self.create_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 
                                 self.eras[self.current_era]['color'], 
                                 f"Neue Era: {self.eras[self.current_era]['name']}!", 50)
    
    def calculate_click_power(self):
        """Berechne aktuelle Click-Power mit Upgrades"""
        power = 1
        for upgrade in self.upgrades:
            if upgrade.purchased and upgrade.upgrade_type == 'click':
                power *= upgrade.multiplier
        power *= self.prestige_multiplier
        if self.boost_active:
            power *= self.boost_multiplier
        return int(power)
    
    def calculate_production(self):
        """Berechne Produktion pro Sekunde"""
        production = 0
        for building in self.buildings:
            base_prod = building.get_production()
            
            # Wende Gebäude-spezifische Upgrades an
            for upgrade in self.upgrades:
                if upgrade.purchased and upgrade.upgrade_type == 'production':
                    # Upgrade gilt für Gebäude derselben Era oder alle
                    if upgrade.era == building.era or upgrade.name == "Antimaterie":
                        base_prod *= upgrade.multiplier
            
            production += base_prod
        
        production *= self.prestige_multiplier
        if self.boost_active:
            production *= self.boost_multiplier
        return production
    
    def click_resource(self):
        """Hauptressource klicken"""
        power = self.calculate_click_power()
        self.resources += power
        self.total_earned += power
        self.total_clicks += 1
        self.click_animation = 10
        
        # Partikel-Effekt
        self.create_particles(self.click_area.centerx, self.click_area.centery, 
                             self.eras[self.current_era]['color'], 
                             f"+{format_number(power)}", 5)
        
        # Update Statistik
        if self.resources > self.stats['highest_resources']:
            self.stats['highest_resources'] = self.resources
    
    def create_particles(self, x, y, color, text=None, count=10):
        """Erstelle Partikel-Effekte"""
        for _ in range(count):
            if text and _ == 0:
                self.particles.append(Particle(x, y, color, text))
            else:
                self.particles.append(Particle(x, y, color))
    
    def buy_building(self, building):
        """Kaufe ein Gebäude"""
        cost = building.purchase(self.resources)
        if cost > 0:
            self.resources -= cost
            self.stats['total_buildings_purchased'] += 1
            self.create_particles(600, 300, GREEN, f"{building.icon} +1", 5)
    
    def buy_upgrade(self, upgrade):
        """Kaufe ein Upgrade"""
        if not upgrade.purchased and self.resources >= upgrade.cost:
            self.resources -= upgrade.cost
            upgrade.purchase()
            self.stats['total_upgrades_purchased'] += 1
            self.create_particles(600, 300, GOLD, f"{upgrade.icon} Upgrade!", 10)
    
    def activate_boost(self):
        """Aktiviere temporären Boost"""
        if not self.boost_active and self.prestige_points >= 1:
            self.prestige_points -= 1
            self.boost_active = True
            self.boost_timer = self.boost_duration
            self.create_particles(SCREEN_WIDTH//2, 100, GOLD, "BOOST x5!", 20)
    
    def do_prestige(self):
        """Führe Prestige durch (Neustart mit Bonus)"""
        if self.total_earned < 1000000:  # Mindestens 1M für ersten Prestige
            return
        
        # Berechne Prestige-Punkte basierend auf gesamt verdienten Ressourcen
        new_points = int(math.sqrt(self.total_earned / 1000000))
        
        if new_points > 0:
            # Speichere Statistiken
            self.stats['prestiges'] += 1
            
            # Reset
            self.resources = 0
            self.total_earned = 0
            self.current_era = 0
            
            # Reset Gebäude
            for building in self.buildings:
                building.count = 0
                building.unlocked = (building.era == 0)
            
            # Reset Upgrades
            for upgrade in self.upgrades:
                upgrade.purchased = False
                upgrade.unlocked = (upgrade.era == 0)
            
            # Füge Prestige-Punkte hinzu
            self.prestige_points += new_points
            self.prestige_multiplier = 1.0 + (self.prestige_points * 0.1)
            
            self.create_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PURPLE, 
                                 f"+{new_points} Prestige!", 30)
            self.state = 'playing'
    
    def check_achievements(self):
        """Prüfe alle Achievements"""
        game_state = {
            'total_earned': self.total_earned,
            'total_clicks': self.total_clicks,
            'total_buildings': sum(b.count for b in self.buildings),
            'current_era': self.current_era
        }
        
        for achievement in self.achievements:
            if achievement.check(game_state) and not achievement.unlocked:
                achievement.unlocked = True
                self.prestige_points += achievement.reward
                self.create_particles(SCREEN_WIDTH//2, 200, GOLD, 
                                     f"Achievement: {achievement.name}!", 20)
    
    def save_game(self):
        """Speichere Spielstand"""
        save_data = {
            'resources': self.resources,
            'total_earned': self.total_earned,
            'total_clicks': self.total_clicks,
            'current_era': self.current_era,
            'prestige_points': self.prestige_points,
            'prestige_multiplier': self.prestige_multiplier,
            'buildings': [(b.count, b.unlocked) for b in self.buildings],
            'upgrades': [(u.purchased, u.unlocked) for u in self.upgrades],
            'achievements': [a.unlocked for a in self.achievements],
            'stats': self.stats,
            'last_save_time': time.time()
        }
        
        with open('evolution_clicker_save.json', 'w') as f:
            json.dump(save_data, f)
        
        self.create_particles(SCREEN_WIDTH//2, 50, GREEN, "Spiel gespeichert!", 10)
    
    def load_game(self):
        """Lade Spielstand"""
        try:
            if not os.path.exists('evolution_clicker_save.json'):
                return False
                
            with open('evolution_clicker_save.json', 'r') as f:
                save_data = json.load(f)
            
            self.resources = save_data['resources']
            self.total_earned = save_data['total_earned']
            self.total_clicks = save_data['total_clicks']
            self.current_era = save_data['current_era']
            self.prestige_points = save_data['prestige_points']
            self.prestige_multiplier = save_data['prestige_multiplier']
            
            for i, (count, unlocked) in enumerate(save_data['buildings']):
                self.buildings[i].count = count
                self.buildings[i].unlocked = unlocked
            
            for i, (purchased, unlocked) in enumerate(save_data['upgrades']):
                self.upgrades[i].purchased = purchased
                self.upgrades[i].unlocked = unlocked
            
            for i, unlocked in enumerate(save_data['achievements']):
                self.achievements[i].unlocked = unlocked
            
            self.stats = save_data['stats']
            
            # Berechne Offline-Fortschritt
            time_passed = time.time() - save_data['last_save_time']
            offline_production = self.calculate_production() * time_passed
            if offline_production > 0:
                self.resources += offline_production
                self.total_earned += offline_production
                self.create_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, GREEN, 
                                     f"Offline-Produktion: {format_number(offline_production)}", 20)
            
            self.create_particles(SCREEN_WIDTH//2, 50, BLUE, "Spiel geladen!", 10)
            return True
            
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return False
    
    def handle_events(self):
        """Verarbeite Events"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'playing':
                        self.state = 'menu'
                    elif self.state in ['achievements', 'stats', 'prestige']:
                        self.state = 'playing'
                
                elif event.key == pygame.K_s:
                    self.save_game()
                
                elif event.key == pygame.K_l:
                    self.load_game()
                
                elif event.key == pygame.K_p:
                    if self.total_earned >= 1000000:
                        self.state = 'prestige'
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Linksklick
                    if self.state == 'menu':
                        self.handle_menu_click(mouse_pos)
                    elif self.state == 'playing':
                        self.handle_game_click(mouse_pos)
                    elif self.state == 'prestige':
                        self.handle_prestige_click(mouse_pos)
            
            if event.type == pygame.MOUSEWHEEL:
                if self.state == 'playing':
                    self.scroll_offset = max(0, min(self.max_scroll, 
                                                    self.scroll_offset - event.y * 30))
    
    def handle_menu_click(self, pos):
        """Behandle Menü-Klicks"""
        # Start Button
        if pygame.Rect(SCREEN_WIDTH//2 - 150, 300, 300, 60).collidepoint(pos):
            self.state = 'playing'
        # Load Button
        elif pygame.Rect(SCREEN_WIDTH//2 - 150, 380, 300, 60).collidepoint(pos):
            if self.load_game():
                self.state = 'playing'
        # Achievements Button
        elif pygame.Rect(SCREEN_WIDTH//2 - 150, 460, 300, 60).collidepoint(pos):
            self.state = 'achievements'
        # Quit Button
        elif pygame.Rect(SCREEN_WIDTH//2 - 150, 540, 300, 60).collidepoint(pos):
            self.running = False
    
    def handle_game_click(self, pos):
        """Behandle Spiel-Klicks"""
        # Haupt-Klickbereich
        if self.click_area.collidepoint(pos):
            self.click_resource()
        
        # Gebäude kaufen (Rechte Seite)
        building_start_y = 150 - self.scroll_offset
        for i, building in enumerate(self.buildings):
            if not building.unlocked:
                continue
            
            building_rect = pygame.Rect(900, building_start_y + i * 70, 450, 60)
            if building_rect.collidepoint(pos):
                self.buy_building(building)
        
        # Upgrades kaufen (Unten)
        upgrade_x = 50
        upgrade_y = SCREEN_HEIGHT - 120
        for i, upgrade in enumerate(self.upgrades):
            if not upgrade.unlocked or upgrade.purchased:
                continue
            
            upgrade_rect = pygame.Rect(upgrade_x + (i % 10) * 120, upgrade_y, 110, 110)
            if upgrade_rect.collidepoint(pos):
                self.buy_upgrade(upgrade)
        
        # UI Buttons
        # Achievement Button
        if pygame.Rect(10, 10, 120, 40).collidepoint(pos):
            self.state = 'achievements'
        # Stats Button
        if pygame.Rect(140, 10, 120, 40).collidepoint(pos):
            self.state = 'stats'
        # Boost Button
        if pygame.Rect(270, 10, 120, 40).collidepoint(pos):
            self.activate_boost()
    
    def handle_prestige_click(self, pos):
        """Behandle Prestige-Klicks"""
        # Prestige bestätigen
        if pygame.Rect(SCREEN_WIDTH//2 - 100, 400, 200, 60).collidepoint(pos):
            self.do_prestige()
        # Abbrechen
        elif pygame.Rect(SCREEN_WIDTH//2 - 100, 480, 200, 60).collidepoint(pos):
            self.state = 'playing'
    
    def update(self):
        """Update-Logik"""
        if self.state != 'playing':
            # Partikel auch in anderen States updaten
            self.particles = [p for p in self.particles if p.is_alive()]
            for p in self.particles:
                p.update()
            return
        
        # Produktion pro Frame (60 FPS = 1 Sekunde)
        self.production_per_second = self.calculate_production()
        production_per_frame = self.production_per_second / FPS
        
        if production_per_frame > 0:
            self.resources += production_per_frame
            self.total_earned += production_per_frame
        
        # Update Statistik
        if self.resources > self.stats['highest_resources']:
            self.stats['highest_resources'] = self.resources
        
        self.stats['total_time_played'] += 1 / FPS
        
        # Era updaten
        self.update_era()
        
        # Achievements prüfen
        self.check_achievements()
        
        # Partikel updaten
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update()
        
        # Click-Animation
        if self.click_animation > 0:
            self.click_animation -= 1
        
        # Auto-Clicker
        if self.auto_clicker_active:
            self.auto_click_timer += 1
            if self.auto_click_timer >= self.auto_click_interval:
                self.click_resource()
                self.auto_click_timer = 0
        
        # Boost-Timer
        if self.boost_active:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.boost_active = False
        
        # Auto-Save alle 60 Sekunden
        if time.time() - self.last_save_time > 60:
            self.save_game()
            self.last_save_time = time.time()
    
    def draw(self):
        """Zeichne alles"""
        self.screen.fill(BLACK)
        
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'achievements':
            self.draw_achievements()
        elif self.state == 'stats':
            self.draw_stats()
        elif self.state == 'prestige':
            self.draw_prestige()
        
        # Partikel immer zeichnen
        for p in self.particles:
            p.draw(self.screen, self.font_medium)
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Zeichne Hauptmenü"""
        # Titel
        title = self.font_huge.render("EVOLUTION CLICKER", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Von der Steinzeit zur Zukunft", True, CYAN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Buttons
        buttons = [
            ("NEUES SPIEL", 300, GREEN),
            ("LADEN", 380, BLUE),
            ("ACHIEVEMENTS", 460, GOLD),
            ("BEENDEN", 540, RED)
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        for text, y, color in buttons:
            rect = pygame.Rect(SCREEN_WIDTH//2 - 150, y, 300, 60)
            hover = rect.collidepoint(mouse_pos)
            
            draw_color = tuple(min(255, c + 30) for c in color) if hover else color
            pygame.draw.rect(self.screen, draw_color, rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, rect, 3, border_radius=10)
            
            text_surf = self.font_medium.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
        
        # Anleitung
        controls = [
            "Steuerung:",
            "LINKSKLICK = Ressourcen sammeln",
            "S = Speichern | L = Laden",
            "P = Prestige (wenn verfügbar)",
            "ESC = Menü"
        ]
        
        y = 650
        for line in controls:
            text = self.font_small.render(line, True, GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 25
    
    def draw_game(self):
        """Zeichne Spielbildschirm"""
        era_color = self.eras[self.current_era]['color']
        
        # Obere Leiste
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, 60))
        
        # Buttons
        btn_y = 10
        pygame.draw.rect(self.screen, BLUE, (10, btn_y, 120, 40), border_radius=5)
        pygame.draw.rect(self.screen, WHITE, (10, btn_y, 120, 40), 2, border_radius=5)
        text = self.font_small.render("Achievements", True, WHITE)
        self.screen.blit(text, (20, btn_y + 10))
        
        pygame.draw.rect(self.screen, GREEN, (140, btn_y, 120, 40), border_radius=5)
        pygame.draw.rect(self.screen, WHITE, (140, btn_y, 120, 40), 2, border_radius=5)
        text = self.font_small.render("Statistiken", True, WHITE)
        self.screen.blit(text, (150, btn_y + 10))
        
        boost_color = GOLD if self.boost_active else GRAY
        pygame.draw.rect(self.screen, boost_color, (270, btn_y, 120, 40), border_radius=5)
        pygame.draw.rect(self.screen, WHITE, (270, btn_y, 120, 40), 2, border_radius=5)
        boost_text = f"Boost ({self.prestige_points}P)"
        if self.boost_active:
            boost_text = f"AKTIV {self.boost_timer//60}s"
        text = self.font_small.render(boost_text, True, WHITE)
        self.screen.blit(text, (280, btn_y + 10))
        
        # Ressourcen-Anzeige
        res_text = self.font_large.render(format_number(self.resources), True, GOLD)
        res_rect = res_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        self.screen.blit(res_text, res_rect)
        
        # Era-Anzeige
        era_text = self.font_medium.render(
            f"{self.eras[self.current_era]['icon']} {self.eras[self.current_era]['name']}", 
            True, era_color)
        era_rect = era_text.get_rect(topright=(SCREEN_WIDTH - 20, 15))
        self.screen.blit(era_text, era_rect)
        
        # Linke Seite - Klickbereich
        pygame.draw.rect(self.screen, DARK_GRAY, (50, 80, 400, 600), border_radius=10)
        pygame.draw.rect(self.screen, era_color, (50, 80, 400, 600), 3, border_radius=10)
        
        # Era-Name groß
        era_name = self.font_large.render(self.eras[self.current_era]['name'], True, era_color)
        era_name_rect = era_name.get_rect(center=(250, 120))
        self.screen.blit(era_name, era_name_rect)
        
        # Klickbarer Bereich
        scale = 1.0 + (self.click_animation / 100)
        icon_size = int(150 * scale)
        icon_text = self.font_huge.render(self.eras[self.current_era]['icon'], True, era_color)
        icon_rect = icon_text.get_rect(center=self.click_area.center)
        
        # Glow-Effekt bei Klick
        if self.click_animation > 0:
            glow_surf = pygame.Surface((icon_size + 50, icon_size + 50), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*era_color, 100), 
                             (icon_size//2 + 25, icon_size//2 + 25), icon_size//2 + 25)
            self.screen.blit(glow_surf, 
                           (self.click_area.centerx - icon_size//2 - 25, 
                            self.click_area.centery - icon_size//2 - 25))
        
        self.screen.blit(icon_text, icon_rect)
        
        # Stats unter dem Icon
        stats_y = 400
        click_pow = self.calculate_click_power()
        stats = [
            f"Click-Power: {format_number(click_pow)}",
            f"Pro Sekunde: {format_number(self.production_per_second)}",
            f"Gesamt verdient: {format_number(self.total_earned)}",
            f"Prestige: x{self.prestige_multiplier:.1f}",
            f"Prestige-Punkte: {self.prestige_points}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.font_small.render(stat, True, WHITE)
            text_rect = text.get_rect(center=(250, stats_y + i * 30))
            self.screen.blit(text, text_rect)
        
        # Rechte Seite - Gebäude
        pygame.draw.rect(self.screen, DARK_GRAY, (480, 80, 880, 470), border_radius=10)
        pygame.draw.rect(self.screen, era_color, (480, 80, 880, 470), 3, border_radius=10)
        
        # Gebäude-Titel
        buildings_title = self.font_medium.render("GEBÄUDE", True, GOLD)
        self.screen.blit(buildings_title, (700, 90))
        
        # Scrollbare Gebäude-Liste
        building_start_y = 150
        visible_buildings = 0
        mouse_pos = pygame.mouse.get_pos()
        
        for i, building in enumerate(self.buildings):
            if not building.unlocked:
                continue
            
            y = building_start_y + visible_buildings * 70 - self.scroll_offset
            
            # Nur zeichnen wenn sichtbar
            if y < 80 or y > 520:
                visible_buildings += 1
                continue
            
            rect = pygame.Rect(500, y, 820, 60)
            can_afford = self.resources >= building.get_cost()
            
            # Hover-Effekt
            hover = rect.collidepoint(mouse_pos)
            
            # Hintergrund
            bg_color = DARK_GREEN if can_afford else DARK_BLUE
            if hover:
                bg_color = tuple(min(255, c + 30) for c in bg_color)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(self.screen, WHITE if can_afford else GRAY, rect, 2, border_radius=5)
            
            # Icon
            icon_text = self.font_large.render(building.icon, True, WHITE)
            self.screen.blit(icon_text, (510, y + 10))
            
            # Name und Anzahl
            name_text = self.font_medium.render(f"{building.name} ({building.count})", True, WHITE)
            self.screen.blit(name_text, (560, y + 5))
            
            # Kosten und Produktion
            cost_text = self.font_small.render(f"Kosten: {format_number(building.get_cost())}", 
                                              True, GOLD if can_afford else GRAY)
            prod_text = self.font_small.render(f"+{format_number(building.base_production)}/s", 
                                              True, GREEN)
            self.screen.blit(cost_text, (560, y + 35))
            self.screen.blit(prod_text, (750, y + 35))
            
            # Gesamt-Produktion
            if building.count > 0:
                total_text = self.font_small.render(
                    f"Gesamt: {format_number(building.get_production())}/s", 
                    True, CYAN)
                total_rect = total_text.get_rect(right=1310, centery=y + 30)
                self.screen.blit(total_text, total_rect)
            
            visible_buildings += 1
        
        # Berechne max scroll
        self.max_scroll = max(0, visible_buildings * 70 - 370)
        
        # Upgrade-Bereich
        pygame.draw.rect(self.screen, DARK_GRAY, (50, SCREEN_HEIGHT - 140, 
                                                   SCREEN_WIDTH - 100, 130), border_radius=10)
        pygame.draw.rect(self.screen, PURPLE, (50, SCREEN_HEIGHT - 140, 
                                                SCREEN_WIDTH - 100, 130), 3, border_radius=10)
        
        # Upgrades-Titel
        upgrades_title = self.font_medium.render("UPGRADES", True, PURPLE)
        self.screen.blit(upgrades_title, (60, SCREEN_HEIGHT - 135))
        
        # Upgrades zeichnen
        upgrade_x = 60
        upgrade_y = SCREEN_HEIGHT - 120
        drawn_upgrades = 0
        
        for upgrade in self.upgrades:
            if not upgrade.unlocked or upgrade.purchased:
                continue
            
            if drawn_upgrades >= 10:  # Max 10 Upgrades anzeigen
                break
            
            x = upgrade_x + drawn_upgrades * 120
            rect = pygame.Rect(x, upgrade_y, 110, 90)
            can_afford = self.resources >= upgrade.cost
            
            hover = rect.collidepoint(mouse_pos)
            
            # Hintergrund
            bg_color = DARK_GREEN if can_afford else DARK_BLUE
            if hover:
                bg_color = tuple(min(255, c + 30) for c in bg_color)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(self.screen, GOLD if can_afford else GRAY, rect, 3, border_radius=5)
            
            # Icon
            icon_text = self.font_large.render(upgrade.icon, True, WHITE)
            icon_rect = icon_text.get_rect(center=(x + 55, upgrade_y + 25))
            self.screen.blit(icon_text, icon_rect)
            
            # Multiplikator
            mult_text = self.font_small.render(f"x{upgrade.multiplier}", True, YELLOW)
            mult_rect = mult_text.get_rect(center=(x + 55, upgrade_y + 55))
            self.screen.blit(mult_text, mult_rect)
            
            # Kosten
            cost_text = self.font_tiny.render(format_number(upgrade.cost), True, GOLD if can_afford else GRAY)
            cost_rect = cost_text.get_rect(center=(x + 55, upgrade_y + 75))
            self.screen.blit(cost_text, cost_rect)
            
            drawn_upgrades += 1
        
        # Prestige-Hinweis
        if self.total_earned >= 1000000:
            prestige_available = int(math.sqrt(self.total_earned / 1000000))
            prestige_text = self.font_medium.render(
                f"Prestige verfügbar! Drücke P (+{prestige_available} Punkte)", 
                True, PURPLE)
            prestige_rect = prestige_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 160))
            
            # Pulsierender Hintergrund
            pulse = int(abs(math.sin(time.time() * 3) * 30))
            pulse_color = tuple(min(255, c + pulse) for c in PURPLE)
            pulse_rect = prestige_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, pulse_color, pulse_rect, border_radius=5)
            
            self.screen.blit(prestige_text, prestige_rect)
    
    def draw_achievements(self):
        """Zeichne Achievement-Bildschirm"""
        # Hintergrund
        pygame.draw.rect(self.screen, DARK_GRAY, (100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100), 
                        border_radius=10)
        pygame.draw.rect(self.screen, GOLD, (100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100), 
                        3, border_radius=10)
        
        # Titel
        title = self.font_large.render("ACHIEVEMENTS", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Zähler
        unlocked_count = sum(1 for a in self.achievements if a.unlocked)
        counter = self.font_medium.render(f"{unlocked_count} / {len(self.achievements)} freigeschaltet", 
                                         True, WHITE)
        counter_rect = counter.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(counter, counter_rect)
        
        # Achievements
        y = 200
        x_left = 150
        x_right = SCREEN_WIDTH//2 + 50
        
        for i, achievement in enumerate(self.achievements):
            x = x_left if i % 2 == 0 else x_right
            if i % 2 == 0 and i > 0:
                y += 120
            
            if y > SCREEN_HEIGHT - 150:
                break
            
            # Achievement Box
            rect = pygame.Rect(x, y, 500, 100)
            color = GOLD if achievement.unlocked else DARK_BLUE
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, WHITE if achievement.unlocked else GRAY, rect, 2, border_radius=5)
            
            # Icon
            icon = "✅" if achievement.unlocked else "🔒"
            icon_text = self.font_large.render(icon, True, WHITE)
            self.screen.blit(icon_text, (x + 10, y + 25))
            
            # Name
            name_text = self.font_medium.render(achievement.name, True, WHITE)
            self.screen.blit(name_text, (x + 70, y + 10))
            
            # Beschreibung
            desc_text = self.font_small.render(achievement.description, True, LIGHT_GRAY)
            self.screen.blit(desc_text, (x + 70, y + 45))
            
            # Belohnung
            reward_text = self.font_small.render(f"+{achievement.reward} Prestige", True, PURPLE)
            reward_rect = reward_text.get_rect(right=x + 490, bottom=y + 90)
            self.screen.blit(reward_text, reward_rect)
        
        # Zurück-Hinweis
        back_text = self.font_medium.render("Drücke ESC zum Zurückkehren", True, GRAY)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)
    
    def draw_stats(self):
        """Zeichne Statistik-Bildschirm"""
        # Hintergrund
        pygame.draw.rect(self.screen, DARK_GRAY, (200, 100, SCREEN_WIDTH - 400, SCREEN_HEIGHT - 200), 
                        border_radius=10)
        pygame.draw.rect(self.screen, CYAN, (200, 100, SCREEN_WIDTH - 400, SCREEN_HEIGHT - 200), 
                        3, border_radius=10)
        
        # Titel
        title = self.font_large.render("STATISTIKEN", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Statistiken
        hours = int(self.stats['total_time_played'] // 3600)
        minutes = int((self.stats['total_time_played'] % 3600) // 60)
        
        stats_list = [
            ("Gesamt verdient", format_number(self.total_earned)),
            ("Höchste Ressourcen", format_number(self.stats['highest_resources'])),
            ("Gesamt Klicks", format_number(self.total_clicks)),
            ("Gebäude gekauft", str(self.stats['total_buildings_purchased'])),
            ("Upgrades gekauft", str(self.stats['total_upgrades_purchased'])),
            ("Prestige durchgeführt", str(self.stats['prestiges'])),
            ("Spielzeit", f"{hours}h {minutes}m"),
            ("Aktuelle Era", self.eras[self.current_era]['name']),
            ("Prestige-Multiplikator", f"x{self.prestige_multiplier:.1f}"),
            ("Prestige-Punkte", str(self.prestige_points))
        ]
        
        y = 230
        for label, value in stats_list:
            # Label
            label_text = self.font_medium.render(label + ":", True, WHITE)
            self.screen.blit(label_text, (250, y))
            
            # Wert
            value_text = self.font_medium.render(str(value), True, GOLD)
            value_rect = value_text.get_rect(right=SCREEN_WIDTH - 250, y=y)
            self.screen.blit(value_text, value_rect)
            
            y += 45
        
        # Zurück-Hinweis
        back_text = self.font_medium.render("Drücke ESC zum Zurückkehren", True, GRAY)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 130))
        self.screen.blit(back_text, back_rect)
    
    def draw_prestige(self):
        """Zeichne Prestige-Bildschirm"""
        # Hintergrund
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Box
        pygame.draw.rect(self.screen, DARK_GRAY, (300, 200, SCREEN_WIDTH - 600, 400), 
                        border_radius=10)
        pygame.draw.rect(self.screen, PURPLE, (300, 200, SCREEN_WIDTH - 600, 400), 
                        5, border_radius=10)
        
        # Titel
        title = self.font_large.render("PRESTIGE", True, PURPLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(title, title_rect)
        
        # Info
        new_points = int(math.sqrt(self.total_earned / 1000000))
        
        info_lines = [
            "Prestige startet das Spiel neu, aber du erhältst:",
            f"+{new_points} Prestige-Punkte",
            f"Neuer Multiplikator: x{1.0 + ((self.prestige_points + new_points) * 0.1):.1f}",
            "",
            "Alle Gebäude und Upgrades werden zurückgesetzt!",
            "Achievements und Statistiken bleiben erhalten."
        ]
        
        y = 320
        for line in info_lines:
            color = GOLD if "+" in line or "x" in line else WHITE
            text = self.font_medium.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 40
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Bestätigen
        confirm_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 500, 180, 60)
        hover_confirm = confirm_rect.collidepoint(mouse_pos)
        color = tuple(min(255, c + 30) for c in GREEN) if hover_confirm else GREEN
        
        pygame.draw.rect(self.screen, color, confirm_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, confirm_rect, 3, border_radius=5)
        
        confirm_text = self.font_medium.render("PRESTIGE!", True, WHITE)
        confirm_text_rect = confirm_text.get_rect(center=confirm_rect.center)
        self.screen.blit(confirm_text, confirm_text_rect)
        
        # Abbrechen
        cancel_rect = pygame.Rect(SCREEN_WIDTH//2 + 20, 500, 180, 60)
        hover_cancel = cancel_rect.collidepoint(mouse_pos)
        color = tuple(min(255, c + 30) for c in RED) if hover_cancel else RED
        
        pygame.draw.rect(self.screen, color, cancel_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, cancel_rect, 3, border_radius=5)
        
        cancel_text = self.font_medium.render("Abbrechen", True, WHITE)
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        self.screen.blit(cancel_text, cancel_text_rect)
    
    def run(self):
        """Haupt-Spielschleife"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Auto-Save beim Beenden
        if self.state == 'playing':
            self.save_game()
        
        pygame.quit()


# Spiel starten
if __name__ == "__main__":
    game = Game()
    game.run()