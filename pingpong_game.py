"""
PING PONG SPIEL MIT KI-GEGNER UND UPGRADES
===========================================

Ein vollständiges Ping-Pong-Spiel mit:
- Einzelspieler gegen CPU mit 4 Schwierigkeitsgraden
- Zwei-Spieler-Modus (lokal)
- Intelligente KI mit verschiedenen Verhaltensweisen
- Upgrade-System für Schläger und Ball
- Anpassbare Farben und Formen
- Power-Ups die zufällig erscheinen
- Partikel-Effekte
- Punktesystem mit Gewinner-Anzeige

Schwierigkeitsgrade:
- EINFACH: Langsame KI, macht viele Fehler
- MITTEL: Normale Geschwindigkeit, wenige Fehler
- SCHWER: Schnelle KI mit Ball-Vorhersage
- UNMÖGLICH: Perfekte KI ohne Fehler

Steuerung:
- Spieler 1: W = Hoch, S = Runter
- Spieler 2 (nur 2-Spieler): Pfeiltaste Hoch/Runter
- ESC = Zurück zum Menü
- Zahlen 1-6 = Menü-Navigation
"""

import pygame
import random
import math
import sys

# Pygame initialisieren
pygame.init()

# Konstanten für Bildschirmgröße
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# Farben (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
PURPLE = (200, 50, 200)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
LIME = (0, 255, 0)
DARK_BLUE = (0, 0, 100)
GRAY = (128, 128, 128)

# Farboptionen für die Anpassung
COLOR_OPTIONS = {
    'white': WHITE,
    'red': RED,
    'green': GREEN,
    'blue': BLUE,
    'yellow': YELLOW,
    'purple': PURPLE,
    'orange': ORANGE,
    'cyan': CYAN,
    'pink': PINK
}


class Particle:
    """
    Partikel-Klasse für visuelle Effekte
    Wird beim Treffen des Balls verwendet
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        self.age = 0
        
    def update(self):
        """Aktualisiere Position und Alter des Partikels"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Schwerkraft
        self.age += 1
        
    def draw(self, screen):
        """Zeichne Partikel mit Transparenz-Effekt"""
        if self.age < self.lifetime:
            alpha = int(255 * (1 - self.age / self.lifetime))
            size = max(1, self.size * (1 - self.age / self.lifetime))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(size))
            
    def is_alive(self):
        """Prüfe ob Partikel noch aktiv ist"""
        return self.age < self.lifetime


class PowerUp:
    """
    Power-Up Klasse für spezielle Effekte im Spiel
    Verschiedene Typen: Speed, Size, Multi-Ball, etc.
    """
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = power_type
        self.lifetime = 300  # Frames bis Power-Up verschwindet
        self.age = 0
        
        # Farbe basierend auf Typ
        self.color_map = {
            'speed_up': RED,
            'speed_down': BLUE,
            'size_up': GREEN,
            'size_down': ORANGE,
            'multi_ball': PURPLE
        }
        self.color = self.color_map.get(power_type, WHITE)
        
    def update(self):
        """Aktualisiere Power-Up (Pulsieren und Altern)"""
        self.age += 1
        # Pulsieren-Effekt
        pulse = math.sin(self.age * 0.1) * 5
        self.current_size = self.width + pulse
        
    def draw(self, screen):
        """Zeichne Power-Up mit Icon"""
        # Äußerer Kreis
        pygame.draw.circle(screen, self.color, 
                         (int(self.x), int(self.y)), 
                         int(self.current_size))
        # Innerer Kreis (weiß)
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x), int(self.y)), 
                         int(self.current_size - 5))
        
        # Typ-Symbol
        font = pygame.font.Font(None, 20)
        symbols = {
            'speed_up': '>>',
            'speed_down': '<<',
            'size_up': '+',
            'size_down': '-',
            'multi_ball': 'x2'
        }
        text = font.render(symbols.get(self.type, '?'), True, self.color)
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)
        
    def is_expired(self):
        """Prüfe ob Power-Up abgelaufen ist"""
        return self.age >= self.lifetime
        
    def collides_with(self, rect):
        """Prüfe Kollision mit Rechteck (Ball oder Schläger)"""
        power_rect = pygame.Rect(self.x - self.width/2, 
                                 self.y - self.height/2,
                                 self.width, self.height)
        return power_rect.colliderect(rect)


class Ball:
    """
    Ball-Klasse für das Spiel
    Enthält Position, Geschwindigkeit, Form und Kollisionslogik
    """
    def __init__(self, x, y):
        self.base_speed = 5
        self.reset_position(x, y)
        self.speed_x = self.base_speed
        self.speed_y = self.base_speed
        self.radius = 10
        self.color = WHITE
        self.shape = 'circle'  # circle, square, triangle
        self.trail = []  # Schweif-Effekt
        
        # Upgrade-Eigenschaften
        self.speed_multiplier = 1.0
        self.size_multiplier = 1.0
        
    def reset_position(self, x, y):
        """Setze Ball auf Startposition zurück"""
        self.x = x
        self.y = y
        direction = random.choice([-1, 1])
        angle = random.uniform(-math.pi/4, math.pi/4)
        self.speed_x = self.base_speed * direction
        self.speed_y = self.base_speed * math.sin(angle)
        
    def update(self):
        """Aktualisiere Ballposition"""
        self.x += self.speed_x * self.speed_multiplier
        self.y += self.speed_y * self.speed_multiplier
        
        # Schweif hinzufügen
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Kollision mit oberer und unterer Wand
        if self.y - self.radius * self.size_multiplier <= 0:
            self.y = self.radius * self.size_multiplier
            self.speed_y *= -1
        elif self.y + self.radius * self.size_multiplier >= SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius * self.size_multiplier
            self.speed_y *= -1
            
    def draw(self, screen):
        """Zeichne Ball mit Schweif und gewählter Form"""
        # Schweif zeichnen
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = int(self.radius * self.size_multiplier * (i / len(self.trail)))
            if size > 0:
                pygame.draw.circle(screen, 
                                 (self.color[0]//2, self.color[1]//2, self.color[2]//2), 
                                 (int(pos[0]), int(pos[1])), 
                                 size)
        
        # Ball zeichnen
        current_radius = int(self.radius * self.size_multiplier)
        
        if self.shape == 'circle':
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), current_radius)
        elif self.shape == 'square':
            rect = pygame.Rect(int(self.x - current_radius), 
                             int(self.y - current_radius),
                             current_radius * 2, current_radius * 2)
            pygame.draw.rect(screen, self.color, rect)
        elif self.shape == 'triangle':
            points = [
                (int(self.x), int(self.y - current_radius)),
                (int(self.x - current_radius), int(self.y + current_radius)),
                (int(self.x + current_radius), int(self.y + current_radius))
            ]
            pygame.draw.polygon(screen, self.color, points)
            
    def get_rect(self):
        """Gibt Rechteck für Kollisionserkennung zurück"""
        r = int(self.radius * self.size_multiplier)
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)
    
    def reverse_x(self):
        """Kehre horizontale Richtung um"""
        self.speed_x *= -1
        
    def hit_paddle(self, paddle_y, paddle_height):
        """
        Berechne neue Ballrichtung basierend auf Treffpunkt am Schläger
        Je weiter vom Zentrum, desto steiler der Winkel
        """
        relative_intersect_y = (paddle_y + paddle_height/2) - self.y
        normalized_intersect = relative_intersect_y / (paddle_height/2)
        bounce_angle = normalized_intersect * (math.pi/3)  # Max 60 Grad
        
        speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        self.speed_x = speed * math.cos(bounce_angle) * (-1 if self.speed_x > 0 else 1)
        self.speed_y = speed * -math.sin(bounce_angle)
        
        # Geschwindigkeit leicht erhöhen für Dynamik
        self.speed_x *= 1.05
        self.speed_y *= 1.05


class Paddle:
    """
    Schläger-Klasse für die Spieler
    Enthält Position, Größe, Bewegung und Upgrade-Eigenschaften
    """
    def __init__(self, x, y, player_id, is_ai=False):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 100
        self.speed = 7
        self.color = WHITE
        self.player_id = player_id
        self.shape = 'rectangle'  # rectangle, rounded, diamond
        
        # Upgrade-Eigenschaften
        self.speed_multiplier = 1.0
        self.size_multiplier = 1.0
        
        # Bewegungssteuerung
        self.moving_up = False
        self.moving_down = False
        
        # AI-Eigenschaften
        self.is_ai = is_ai
        self.ai_difficulty = 'medium'  # easy, medium, hard, impossible
        self.ai_reaction_delay = 0
        self.ai_error_margin = 0
        
    def update(self, ball=None):
        """Aktualisiere Schlägerposition basierend auf Eingabe oder AI"""
        # AI-Steuerung
        if self.is_ai and ball:
            self.ai_move(ball)
        
        # Normale Bewegung
        if self.moving_up:
            self.y -= self.speed * self.speed_multiplier
        if self.moving_down:
            self.y += self.speed * self.speed_multiplier
            
        # Begrenzung auf Spielfeld
        if self.y < 0:
            self.y = 0
        elif self.y + self.height * self.size_multiplier > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.height * self.size_multiplier
    
    def ai_move(self, ball):
        """
        KI-Bewegungslogik basierend auf Schwierigkeitsgrad
        - Easy: Langsam, viele Fehler
        - Medium: Normale Geschwindigkeit, wenige Fehler
        - Hard: Schnell, kaum Fehler
        - Impossible: Perfekt, keine Fehler
        """
        # Schwierigkeitsgrad-Einstellungen
        if self.ai_difficulty == 'easy':
            reaction_speed = 0.5
            error_margin = 60
            prediction_enabled = False
        elif self.ai_difficulty == 'medium':
            reaction_speed = 0.7
            error_margin = 30
            prediction_enabled = False
        elif self.ai_difficulty == 'hard':
            reaction_speed = 0.9
            error_margin = 10
            prediction_enabled = True
        else:  # impossible
            reaction_speed = 1.0
            error_margin = 0
            prediction_enabled = True
        
        # Verzögerung für Reaktionszeit
        self.ai_reaction_delay += 1
        if self.ai_reaction_delay < (60 - 60 * reaction_speed):
            return
        self.ai_reaction_delay = 0
        
        # Vorhersage wo der Ball sein wird (nur bei hard/impossible)
        target_y = ball.y
        if prediction_enabled and ball.speed_x > 0:
            # Berechne wo der Ball sein wird wenn er den Schläger erreicht
            distance_x = self.x - ball.x
            if ball.speed_x != 0:
                time_to_reach = distance_x / ball.speed_x
                target_y = ball.y + (ball.speed_y * time_to_reach)
                
                # Berücksichtige Wandkollisionen
                while target_y < 0 or target_y > SCREEN_HEIGHT:
                    if target_y < 0:
                        target_y = -target_y
                    elif target_y > SCREEN_HEIGHT:
                        target_y = 2 * SCREEN_HEIGHT - target_y
        
        # Füge Fehlermarge hinzu (AI macht Fehler)
        target_y += random.randint(-error_margin, error_margin)
        
        # Ziel: Mitte des Schlägers soll zum Ball
        paddle_center = self.y + (self.height * self.size_multiplier) / 2
        
        # Bewegung zum Ziel
        dead_zone = 15  # Bereich in dem AI nicht reagiert
        if target_y < paddle_center - dead_zone:
            self.moving_up = True
            self.moving_down = False
        elif target_y > paddle_center + dead_zone:
            self.moving_up = False
            self.moving_down = True
        else:
            self.moving_up = False
            self.moving_down = False
    
    def set_difficulty(self, difficulty):
        """Setze AI-Schwierigkeitsgrad"""
        self.ai_difficulty = difficulty
            
    def draw(self, screen):
        """Zeichne Schläger mit gewählter Form"""
        current_height = int(self.height * self.size_multiplier)
        
        if self.shape == 'rectangle':
            rect = pygame.Rect(int(self.x), int(self.y), 
                             self.width, current_height)
            pygame.draw.rect(screen, self.color, rect)
        elif self.shape == 'rounded':
            rect = pygame.Rect(int(self.x), int(self.y), 
                             self.width, current_height)
            pygame.draw.rect(screen, self.color, rect, border_radius=10)
        elif self.shape == 'diamond':
            points = [
                (int(self.x + self.width/2), int(self.y)),
                (int(self.x + self.width), int(self.y + current_height/2)),
                (int(self.x + self.width/2), int(self.y + current_height)),
                (int(self.x), int(self.y + current_height/2))
            ]
            pygame.draw.polygon(screen, self.color, points)
            
    def get_rect(self):
        """Gibt Rechteck für Kollisionserkennung zurück"""
        return pygame.Rect(int(self.x), int(self.y), 
                          self.width, 
                          int(self.height * self.size_multiplier))


class Game:
    """
    Haupt-Spielklasse
    Verwaltet Spiellogik, Kollisionen, Punkte und Upgrades
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ping Pong - Mit KI-Gegner!")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'  # menu, playing, paused, game_over, difficulty_select
        
        # Spielmodus
        self.game_mode = 'single'  # single oder two_player
        self.ai_difficulty = 'medium'  # easy, medium, hard, impossible
        
        # Spielobjekte
        self.paddle1 = Paddle(30, SCREEN_HEIGHT//2 - 50, 1, is_ai=False)
        self.paddle2 = Paddle(SCREEN_WIDTH - 45, SCREEN_HEIGHT//2 - 50, 2, is_ai=True)
        self.paddle2.set_difficulty(self.ai_difficulty)
        self.balls = [Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)]
        
        # Spielstand
        self.score1 = 0
        self.score2 = 0
        self.winning_score = 5
        
        # Effekte
        self.particles = []
        self.powerups = []
        self.powerup_timer = 0
        self.powerup_spawn_interval = 300  # Frames zwischen Power-Ups
        
        # Schriftarten
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Hintergrund
        self.bg_color = BLACK
        
    def spawn_powerup(self):
        """Erzeuge zufälliges Power-Up in der Mitte des Spielfelds"""
        x = random.randint(SCREEN_WIDTH//3, 2*SCREEN_WIDTH//3)
        y = random.randint(100, SCREEN_HEIGHT - 100)
        power_type = random.choice(['speed_up', 'speed_down', 
                                   'size_up', 'size_down', 'multi_ball'])
        self.powerups.append(PowerUp(x, y, power_type))
    
    def start_single_player(self):
        """Starte Einzelspieler-Spiel mit gewählter Schwierigkeit"""
        self.paddle2.is_ai = True
        self.paddle2.set_difficulty(self.ai_difficulty)
        self.paddle2.color = RED if self.ai_difficulty == 'easy' else ORANGE if self.ai_difficulty == 'medium' else PURPLE if self.ai_difficulty == 'hard' else PINK
        self.reset_game()
        self.state = 'playing'
        
    def apply_powerup(self, powerup, paddle):
        """
        Wende Power-Up-Effekt auf Schläger oder Ball an
        Verschiedene Upgrade-Typen haben verschiedene Effekte
        """
        if powerup.type == 'speed_up':
            paddle.speed_multiplier = min(2.0, paddle.speed_multiplier + 0.3)
        elif powerup.type == 'speed_down':
            paddle.speed_multiplier = max(0.5, paddle.speed_multiplier - 0.3)
        elif powerup.type == 'size_up':
            paddle.size_multiplier = min(2.0, paddle.size_multiplier + 0.3)
        elif powerup.type == 'size_down':
            paddle.size_multiplier = max(0.5, paddle.size_multiplier - 0.3)
        elif powerup.type == 'multi_ball':
            # Erstelle zusätzlichen Ball
            if len(self.balls) < 3:
                new_ball = Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                new_ball.color = random.choice([RED, GREEN, BLUE, YELLOW])
                self.balls.append(new_ball)
                
    def create_particles(self, x, y, color, count=10):
        """Erstelle Partikel-Effekt an Position"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
            
    def handle_events(self):
        """Verarbeite Tastatur- und Maus-Ereignisse"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                # Menü-Steuerung
                if self.state == 'menu':
                    if event.key == pygame.K_1:
                        self.game_mode = 'single'
                        self.state = 'difficulty_select'
                    elif event.key == pygame.K_2:
                        self.game_mode = 'two_player'
                        self.paddle2.is_ai = False
                        self.reset_game()
                        self.state = 'playing'
                    elif event.key == pygame.K_3:
                        self.state = 'settings_colors'
                    elif event.key == pygame.K_4:
                        self.state = 'settings_shapes'
                    elif event.key == pygame.K_5:
                        self.state = 'settings_upgrades'
                    elif event.key == pygame.K_6:
                        self.running = False
                
                # Schwierigkeitsauswahl
                elif self.state == 'difficulty_select':
                    if event.key == pygame.K_1:
                        self.ai_difficulty = 'easy'
                        self.start_single_player()
                    elif event.key == pygame.K_2:
                        self.ai_difficulty = 'medium'
                        self.start_single_player()
                    elif event.key == pygame.K_3:
                        self.ai_difficulty = 'hard'
                        self.start_single_player()
                    elif event.key == pygame.K_4:
                        self.ai_difficulty = 'impossible'
                        self.start_single_player()
                        
                # Zurück zum Menü
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'menu'
                    self.reset_game()
                    
                # Spieler 1 Steuerung (W/S) - immer aktiv
                if event.key == pygame.K_w:
                    self.paddle1.moving_up = True
                elif event.key == pygame.K_s:
                    self.paddle1.moving_down = True
                    
                # Spieler 2 Steuerung (Pfeiltasten) - nur im 2-Spieler-Modus
                if not self.paddle2.is_ai:
                    if event.key == pygame.K_UP:
                        self.paddle2.moving_up = True
                    elif event.key == pygame.K_DOWN:
                        self.paddle2.moving_down = True
                    
            if event.type == pygame.KEYUP:
                # Spieler 1
                if event.key == pygame.K_w:
                    self.paddle1.moving_up = False
                elif event.key == pygame.K_s:
                    self.paddle1.moving_down = False
                    
                # Spieler 2 (nur wenn kein AI)
                if not self.paddle2.is_ai:
                    if event.key == pygame.K_UP:
                        self.paddle2.moving_up = False
                    elif event.key == pygame.K_DOWN:
                        self.paddle2.moving_down = False
                    
    def update(self):
        """Aktualisiere Spiellogik"""
        if self.state != 'playing':
            return
        
        # Finde nächsten Ball für AI
        closest_ball = self.balls[0] if self.balls else None
        if self.paddle2.is_ai and len(self.balls) > 1:
            # Finde Ball der am nächsten zum AI-Schläger ist
            min_dist = float('inf')
            for ball in self.balls:
                dist = abs(ball.x - self.paddle2.x)
                if dist < min_dist:
                    min_dist = dist
                    closest_ball = ball
            
        # Schläger aktualisieren
        self.paddle1.update()
        self.paddle2.update(closest_ball)  # Ball für AI übergeben
        
        # Bälle aktualisieren
        balls_to_remove = []
        for ball in self.balls:
            ball.update()
            
            # Kollision mit Schläger 1 (Links)
            if (ball.speed_x < 0 and 
                ball.get_rect().colliderect(self.paddle1.get_rect())):
                ball.hit_paddle(self.paddle1.y, 
                              self.paddle1.height * self.paddle1.size_multiplier)
                ball.x = self.paddle1.x + self.paddle1.width + ball.radius * ball.size_multiplier
                self.create_particles(ball.x, ball.y, self.paddle1.color, 15)
                
            # Kollision mit Schläger 2 (Rechts)
            if (ball.speed_x > 0 and 
                ball.get_rect().colliderect(self.paddle2.get_rect())):
                ball.hit_paddle(self.paddle2.y, 
                              self.paddle2.height * self.paddle2.size_multiplier)
                ball.x = self.paddle2.x - ball.radius * ball.size_multiplier
                self.create_particles(ball.x, ball.y, self.paddle2.color, 15)
                
            # Ball aus dem Spielfeld (Punkt)
            if ball.x < 0:
                self.score2 += 1
                balls_to_remove.append(ball)
                self.create_particles(ball.x, ball.y, RED, 30)
            elif ball.x > SCREEN_WIDTH:
                self.score1 += 1
                balls_to_remove.append(ball)
                self.create_particles(ball.x, ball.y, RED, 30)
                
        # Entferne Bälle die aus dem Feld sind
        for ball in balls_to_remove:
            self.balls.remove(ball)
            
        # Wenn alle Bälle weg sind, neuen Ball erstellen
        if len(self.balls) == 0:
            self.balls.append(Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
        # Prüfe Gewinner
        if self.score1 >= self.winning_score or self.score2 >= self.winning_score:
            self.state = 'game_over'
            
        # Power-Up System
        self.powerup_timer += 1
        if self.powerup_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_timer = 0
            
        # Power-Ups aktualisieren
        powerups_to_remove = []
        for powerup in self.powerups:
            powerup.update()
            
            # Kollision mit Schlägern
            if powerup.collides_with(self.paddle1.get_rect()):
                self.apply_powerup(powerup, self.paddle1)
                powerups_to_remove.append(powerup)
                self.create_particles(powerup.x, powerup.y, powerup.color, 20)
            elif powerup.collides_with(self.paddle2.get_rect()):
                self.apply_powerup(powerup, self.paddle2)
                powerups_to_remove.append(powerup)
                self.create_particles(powerup.x, powerup.y, powerup.color, 20)
                
            # Kollision mit Bällen
            for ball in self.balls:
                if powerup.collides_with(ball.get_rect()):
                    # Power-Up auf Ball anwenden
                    if powerup.type == 'speed_up':
                        ball.speed_multiplier = min(2.0, ball.speed_multiplier + 0.2)
                    elif powerup.type == 'speed_down':
                        ball.speed_multiplier = max(0.5, ball.speed_multiplier - 0.2)
                    powerups_to_remove.append(powerup)
                    self.create_particles(powerup.x, powerup.y, powerup.color, 20)
                    break
                    
            if powerup.is_expired():
                powerups_to_remove.append(powerup)
                
        for powerup in powerups_to_remove:
            if powerup in self.powerups:
                self.powerups.remove(powerup)
                
        # Partikel aktualisieren
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
            
    def draw(self):
        """Zeichne alles auf dem Bildschirm"""
        self.screen.fill(self.bg_color)
        
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'difficulty_select':
            self.draw_difficulty_select()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'game_over':
            self.draw_game_over()
        elif self.state == 'settings_colors':
            self.draw_color_settings()
        elif self.state == 'settings_shapes':
            self.draw_shape_settings()
        elif self.state == 'settings_upgrades':
            self.draw_upgrade_settings()
            
        pygame.display.flip()
        
    def draw_menu(self):
        """Zeichne Hauptmenü"""
        # Titel
        title = self.font_large.render("PING PONG", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Untertitel
        subtitle = self.font_small.render("Mit KI-Gegner & verschiedenen Schwierigkeiten!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menü-Optionen
        menu_items = [
            "1 - Einzelspieler (vs CPU)",
            "2 - Zwei Spieler (lokal)",
            "3 - Farben Anpassen",
            "4 - Formen Ändern",
            "5 - Upgrade-Info",
            "6 - Beenden"
        ]
        
        y_start = 250
        for i, item in enumerate(menu_items):
            color = YELLOW if i < 2 else WHITE  # Hervorheben der Spielmodi
            text = self.font_medium.render(item, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_start + i * 60))
            self.screen.blit(text, text_rect)
            
        # Steuerung
        controls = [
            "Steuerung:",
            "Spieler 1: W / S",
            "Spieler 2 (nur 2-Spieler): Pfeiltasten",
            "ESC = Zurück zum Menü"
        ]
        y_start = 620
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_start + i * 20))
            self.screen.blit(text, text_rect)
    
    def draw_difficulty_select(self):
        """Zeichne Schwierigkeitsauswahl-Bildschirm"""
        # Titel
        title = self.font_large.render("Schwierigkeit Wählen", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Schwierigkeitsgrade
        difficulties = [
            ("1 - EINFACH", RED, "Langsame KI, macht viele Fehler"),
            ("2 - MITTEL", ORANGE, "Normale KI, macht wenige Fehler"),
            ("3 - SCHWER", PURPLE, "Schnelle KI mit Vorhersage"),
            ("4 - UNMÖGLICH", PINK, "Perfekte KI ohne Fehler!")
        ]
        
        y_start = 220
        for i, (title_text, color, desc) in enumerate(difficulties):
            # Titel
            text = self.font_medium.render(title_text, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_start + i * 100))
            self.screen.blit(text, text_rect)
            
            # Beschreibung
            desc_text = self.font_small.render(desc, True, GRAY)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, y_start + i * 100 + 30))
            self.screen.blit(desc_text, desc_rect)
        
        # Info
        info = self.font_small.render("ESC = Zurück zum Menü", True, WHITE)
        info_rect = info.get_rect(center=(SCREEN_WIDTH//2, 650))
        self.screen.blit(info, info_rect)
            
    def draw_game(self):
        """Zeichne Spielfeld"""
        # Mittellinie
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, GRAY, 
                           (SCREEN_WIDTH//2 - 2, y, 4, 10))
        
        # Partikel zeichnen
        for particle in self.particles:
            particle.draw(self.screen)
            
        # Power-Ups zeichnen
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        # Schläger zeichnen
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)
        
        # Bälle zeichnen
        for ball in self.balls:
            ball.draw(self.screen)
            
        # Punktestand
        score_text = self.font_large.render(f"{self.score1}   {self.score2}", 
                                           True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(score_text, score_rect)
        
        # Spieler-Labels
        if self.paddle2.is_ai:
            diff_map = {
                'easy': 'EINFACH',
                'medium': 'MITTEL',
                'hard': 'SCHWER',
                'impossible': 'UNMÖGLICH'
            }
            p1_label = self.font_small.render("SPIELER", True, GREEN)
            p2_label = self.font_small.render(f"CPU ({diff_map[self.ai_difficulty]})", True, self.paddle2.color)
            self.screen.blit(p1_label, (50, 100))
            p2_rect = p2_label.get_rect(topright=(SCREEN_WIDTH - 50, 100))
            self.screen.blit(p2_label, p2_rect)
        
        # Upgrade-Anzeige für Spieler 1
        upgrade_text = self.font_small.render(
            f"P1 Speed: {self.paddle1.speed_multiplier:.1f}x  Size: {self.paddle1.size_multiplier:.1f}x", 
            True, GREEN)
        self.screen.blit(upgrade_text, (10, 10))
        
        # Upgrade-Anzeige für Spieler 2 (nur wenn nicht unmöglich)
        if not self.paddle2.is_ai or self.ai_difficulty != 'impossible':
            upgrade_text = self.font_small.render(
                f"P2 Speed: {self.paddle2.speed_multiplier:.1f}x  Size: {self.paddle2.size_multiplier:.1f}x", 
                True, GREEN)
            upgrade_rect = upgrade_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
            self.screen.blit(upgrade_text, upgrade_rect)
        
    def draw_game_over(self):
        """Zeichne Game Over Bildschirm"""
        # Gewinner
        if self.paddle2.is_ai:
            winner = "Du hast gewonnen!" if self.score1 > self.score2 else "CPU hat gewonnen!"
            winner_color = GREEN if self.score1 > self.score2 else RED
        else:
            winner = "Spieler 1 Gewinnt!" if self.score1 > self.score2 else "Spieler 2 Gewinnt!"
            winner_color = self.paddle1.color if self.score1 > self.score2 else self.paddle2.color
        
        winner_text = self.font_large.render(winner, True, winner_color)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(winner_text, winner_rect)
        
        # Schwierigkeitsgrad anzeigen (nur im Einzelspieler)
        if self.paddle2.is_ai:
            diff_map = {
                'easy': 'EINFACH',
                'medium': 'MITTEL',
                'hard': 'SCHWER',
                'impossible': 'UNMÖGLICH'
            }
            diff_text = self.font_medium.render(
                f"Schwierigkeit: {diff_map[self.ai_difficulty]}", True, GRAY)
            diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(diff_text, diff_rect)
        
        # Endstand
        score_text = self.font_medium.render(
            f"Endstand: {self.score1} - {self.score2}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Anweisung
        instruction = self.font_small.render("Drücke ESC für Hauptmenü", True, GRAY)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        self.screen.blit(instruction, instruction_rect)
        
    def draw_color_settings(self):
        """Zeichne Farbanpassungs-Menü"""
        title = self.font_large.render("Farbanpassung", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Info-Text
        info = [
            "In diesem Menü könntest du Farben ändern.",
            "Bereich für Implementierung:",
            "- Paddle 1 Farbe",
            "- Paddle 2 Farbe",
            "- Ball Farbe(n)",
            "- Hintergrund Farbe",
            "",
            "Beispiel: Tastendruck 'R' = Rot, 'B' = Blau, etc.",
            "",
            "Drücke ESC um zurückzukehren"
        ]
        
        y = 180
        for line in info:
            text = self.font_small.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 40
            
    def draw_shape_settings(self):
        """Zeichne Formanpassungs-Menü"""
        title = self.font_large.render("Formen Ändern", True, PURPLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Verfügbare Formen zeigen
        info = [
            "Verfügbare Paddle-Formen:",
            "- Rectangle (Standard)",
            "- Rounded (Abgerundet)",
            "- Diamond (Diamant)",
            "",
            "Verfügbare Ball-Formen:",
            "- Circle (Kreis)",
            "- Square (Quadrat)",
            "- Triangle (Dreieck)",
            "",
            "Implementiere hier Tastenbefehle zum Ändern!",
            "",
            "Drücke ESC um zurückzukehren"
        ]
        
        y = 180
        for line in info:
            text = self.font_small.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 35
            
    def draw_upgrade_settings(self):
        """Zeichne Upgrade-Informationen"""
        title = self.font_large.render("Upgrade System", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 60))
        self.screen.blit(title, title_rect)
        
        info = [
            "Power-Up Typen:",
            "",
            ">> SPEED UP (Rot): Erhöht Schläger-Geschwindigkeit",
            "<< SPEED DOWN (Blau): Verringert Schläger-Geschwindigkeit",
            "+ SIZE UP (Grün): Vergrößert Schläger",
            "- SIZE DOWN (Orange): Verkleinert Schläger",
            "x2 MULTI BALL (Lila): Erstellt zusätzlichen Ball",
            "",
            "Power-Ups erscheinen automatisch im Spiel.",
            "Sammle sie mit deinem Schläger ein!",
            "",
            "UPGRADE-BEREICHE FÜR ERWEITERUNGEN:",
            "- Permanente Upgrades zwischen Runden",
            "- Upgrade-Shop mit Punkten",
            "- Spezielle Fähigkeiten/Skills",
            "- Level-System",
            "",
            "Drücke ESC um zurückzukehren"
        ]
        
        y = 140
        for line in info:
            if line.startswith(">>") or line.startswith("<<") or line.startswith("+") or line.startswith("-") or line.startswith("x2"):
                color = RED if ">>" in line else BLUE if "<<" in line else GREEN if "+" in line else ORANGE if "-" in line else PURPLE
            else:
                color = WHITE
            text = self.font_small.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 28
            
    def reset_game(self):
        """Setze Spiel zurück"""
        self.score1 = 0
        self.score2 = 0
        self.balls = [Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)]
        self.particles = []
        self.powerups = []
        self.powerup_timer = 0
        
        # Schläger zurücksetzen
        self.paddle1.y = SCREEN_HEIGHT//2 - 50
        self.paddle2.y = SCREEN_HEIGHT//2 - 50
        self.paddle1.speed_multiplier = 1.0
        self.paddle2.speed_multiplier = 1.0
        self.paddle1.size_multiplier = 1.0
        self.paddle2.size_multiplier = 1.0
        
    def run(self):
        """Haupt-Spielschleife"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


# ========================================
# HAUPTPROGRAMM - ERWEITERUNGSBEREICHE
# ========================================

"""
BEREICHE FÜR UPGRADES UND ERWEITERUNGEN:

✅ KI-GEGNER (IMPLEMENTIERT):
   - 4 verschiedene Schwierigkeitsgrade funktionieren
   - Easy: Langsam mit Fehlern
   - Medium: Normale Geschwindigkeit 
   - Hard: Schnell mit Vorhersage
   - Impossible: Perfekt ohne Fehler

1. KI-VERBESSERUNGEN:
   - Füge adaptive KI hinzu die vom Spieler lernt
   - Implementiere verschiedene KI-Persönlichkeiten (aggressiv, defensiv)
   - Füge KI-Taunts/Kommentare hinzu

2. PERMANENTE UPGRADES:
   - Implementiere ein System wo Spieler zwischen Runden Upgrades kaufen können
   - Füge eine Währung hinzu (z.B. Münzen pro gewonnenen Punkt)
   - Erstelle einen Upgrade-Shop mit verschiedenen permanenten Verbesserungen

3. FARBWECHSEL-SYSTEM:
   - Erweitere draw_color_settings() mit echter Funktionalität
   - Füge Tastenbefehle hinzu (z.B. R, G, B für Farben)
   - Speichere Farbeinstellungen zwischen Spielen

4. FORMWECHSEL-SYSTEM:
   - Erweitere draw_shape_settings() mit Tastenbefehlen
   - Erlaube Spielern ihre Paddle-Formen zu wählen
   - Füge Kollisionsanpassungen für verschiedene Formen hinzu

5. ERWEITERTE POWER-UPS:
   - Füge neue Power-Up-Typen hinzu (z.B. Shield, Ghost-Mode, Magnet)
   - Implementiere Power-Up-Kombinationen
   - Füge visuelle Effekte für aktive Power-Ups hinzu

6. LEVEL-SYSTEM:
   - Füge ein Erfahrungssystem hinzu
   - Erstelle Level mit unterschiedlichen Herausforderungen
   - Schalte neue Features mit Levels frei

7. SOUND-EFFEKTE:
   - Füge pygame.mixer für Sound hinzu
   - Implementiere Sounds für Kollisionen, Power-Ups, Punkte
   - Füge Hintergrundmusik hinzu
   - CPU-spezifische Sounds basierend auf Schwierigkeit

8. SPIEL-MODI:
   - Implementiere verschiedene Spielmodi (Zeitlimit, Survival, etc.)
   - Füge Team-Modus hinzu (2v2 mit 2 CPUs)
   - Erstelle Turnier-Modus gegen mehrere CPU-Gegner

9. STATISTIKEN:
   - Speichere Spielerstatistiken (Siege, längste Serie, etc.)
   - Zeige Statistiken im Menü
   - Füge Achievements hinzu
   - Tracking für Siege gegen verschiedene KI-Schwierigkeiten

10. MULTIPLAYER:
    - Implementiere Online-Multiplayer (mit Socket)
    - Füge Lobby-System hinzu
    - Erstelle Rangliste
    - Ermögliche Zuschauer-Modus
"""


if __name__ == "__main__":
    # Spiel erstellen und starten
    game = Game()
    game.run()
