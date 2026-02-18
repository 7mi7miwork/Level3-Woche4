"""
PING PONG SPIEL MIT KI-GEGNER UND UPGRADES - ERWEITERTE VERSION
================================================================
Neue Features:
- ✅ Farbwechsel-System (vollständig implementiert)
- ✅ Formwechsel-System (vollständig implementiert)
- ✅ Permanente Upgrades / Shop (zwischen Runden)
- ✅ Sound-Effekte (prozedural generiert mit pygame)
- ✅ Erweiterte Power-Ups (Shield, Ghost, Magnet)
- ✅ Statistiken & Achievements
- ✅ Verschiedene Spielmodi (Zeitlimit, Survival, Classic)
- ✅ Adaptive KI (lernt vom Spieler)

Steuerung:
- Spieler 1: W = Hoch, S = Runter
- Spieler 2 (2-Spieler): Pfeiltasten
- ESC = Zurück zum Menü
- Im Farbmenü: R/G/B/Y/P/O/C/W für Farben, 1/2/3 für Ziel
- Im Formenmenü: 1/2/3 für Form, P/B für Schläger/Ball
"""

import pygame
import random
import math
import sys
import json
import os
import array

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

# ── Konstanten ──────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1200
SCREEN_HEIGHT = 700
FPS           = 60

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
RED     = (255, 50,  50)
GREEN   = (50,  255, 50)
BLUE    = (50,  150, 255)
YELLOW  = (255, 255, 50)
PURPLE  = (200, 50,  200)
ORANGE  = (255, 165, 0)
CYAN    = (0,   255, 255)
PINK    = (255, 105, 180)
LIME    = (0,   255, 0)
DARK_BLUE = (0, 0,   100)
GRAY    = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
GOLD    = (255, 215, 0)
SILVER  = (192, 192, 192)
TEAL    = (0,   180, 180)

COLOR_OPTIONS = {
    'Weiß':   WHITE,
    'Rot':    RED,
    'Grün':   GREEN,
    'Blau':   BLUE,
    'Gelb':   YELLOW,
    'Lila':   PURPLE,
    'Orange': ORANGE,
    'Cyan':   CYAN,
    'Pink':   PINK,
}

SAVE_FILE = "pong_save.json"

# ── Sound-Generierung ────────────────────────────────────────────────────────
def generate_sound(frequency, duration_ms, volume=0.3, wave='sine'):
    """Generiert einen Ton prozedural ohne externe Audiodateien."""
    sample_rate = 44100
    n_samples   = int(sample_rate * duration_ms / 1000)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        if wave == 'sine':
            val = math.sin(2 * math.pi * frequency * t)
        elif wave == 'square':
            val = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
        elif wave == 'noise':
            val = random.uniform(-1, 1)
        else:
            val = math.sin(2 * math.pi * frequency * t)
        # Fade-out
        fade = 1.0 - (i / n_samples) ** 0.5
        buf[i] = int(val * volume * fade * 32767)
    sound = pygame.sndarray.make_sound(buf)
    return sound

class SoundManager:
    """Verwaltet alle Spielgeräusche."""
    def __init__(self):
        self.enabled = True
        self.volume  = 0.5
        self._sounds = {}
        self._build()

    def _build(self):
        self._sounds['hit']      = generate_sound(440, 80,  0.4, 'sine')
        self._sounds['wall']     = generate_sound(220, 60,  0.3, 'sine')
        self._sounds['score']    = generate_sound(150, 400, 0.5, 'square')
        self._sounds['powerup']  = generate_sound(880, 200, 0.4, 'sine')
        self._sounds['shield']   = generate_sound(660, 120, 0.35,'square')
        self._sounds['win']      = generate_sound(523, 600, 0.5, 'sine')
        self._sounds['achieve']  = generate_sound(1046,300, 0.5, 'sine')

    def play(self, name):
        if self.enabled and name in self._sounds:
            try:
                self._sounds[name].set_volume(self.volume)
                self._sounds[name].play()
            except Exception:
                pass

# ── Statistiken & Achievements ───────────────────────────────────────────────
ACHIEVEMENTS = {
    'first_win':    {'name': 'Erster Sieg',       'desc': 'Gewinne dein erstes Spiel',         'icon': '🏆'},
    'easy_beater':  {'name': 'Anfänger',           'desc': 'Besiege EINFACH-KI',                'icon': '⭐'},
    'medium_beater':{'name': 'Fortgeschrittener',  'desc': 'Besiege MITTEL-KI',                 'icon': '⭐⭐'},
    'hard_beater':  {'name': 'Experte',            'desc': 'Besiege SCHWER-KI',                 'icon': '⭐⭐⭐'},
    'impossible':   {'name': 'Legende',            'desc': 'Besiege UNMÖGLICH-KI',              'icon': '👑'},
    'powerup_100':  {'name': 'Power-Hungrig',      'desc': 'Sammle 100 Power-Ups',              'icon': '⚡'},
    'rally_20':     {'name': 'Ausdauer',           'desc': 'Schaffe einen Ballwechsel von 20+', 'icon': '🏓'},
    'shutout':      {'name': 'Shutout',            'desc': 'Gewinne ohne Gegenpunkt',           'icon': '🛡️'},
    'survivor':     {'name': 'Überlebenskünstler', 'desc': 'Überlebe 120s im Survival-Modus',   'icon': '💀'},
}

class Stats:
    def __init__(self):
        self.wins         = 0
        self.losses       = 0
        self.total_games  = 0
        self.powerups_col = 0
        self.max_rally    = 0
        self.coins        = 0
        self.unlocked     = set()
        self.load()

    def save(self):
        data = {
            'wins':         self.wins,
            'losses':       self.losses,
            'total_games':  self.total_games,
            'powerups_col': self.powerups_col,
            'max_rally':    self.max_rally,
            'coins':        self.coins,
            'unlocked':     list(self.unlocked),
        }
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            self.wins         = data.get('wins', 0)
            self.losses       = data.get('losses', 0)
            self.total_games  = data.get('total_games', 0)
            self.powerups_col = data.get('powerups_col', 0)
            self.max_rally    = data.get('max_rally', 0)
            self.coins        = data.get('coins', 0)
            self.unlocked     = set(data.get('unlocked', []))
        except Exception:
            pass

    def check_achievements(self, context):
        """Prüfe und schalte Achievements frei. Gibt Liste neuer frei."""
        new = []
        def unlock(key):
            if key not in self.unlocked:
                self.unlocked.add(key)
                new.append(key)

        if self.wins >= 1:
            unlock('first_win')
        if context.get('beat_easy'):
            unlock('easy_beater')
        if context.get('beat_medium'):
            unlock('medium_beater')
        if context.get('beat_hard'):
            unlock('hard_beater')
        if context.get('beat_impossible'):
            unlock('impossible')
        if self.powerups_col >= 100:
            unlock('powerup_100')
        if self.max_rally >= 20:
            unlock('rally_20')
        if context.get('shutout'):
            unlock('shutout')
        if context.get('survived_120'):
            unlock('survivor')
        self.save()
        return new

# ── Permanente Upgrades / Shop ────────────────────────────────────────────────
SHOP_ITEMS = [
    {'id': 'paddle_speed',  'name': 'Schläger-Speed +',   'desc': '+10% Schläger-Geschwindigkeit', 'cost': 30,  'max': 5},
    {'id': 'paddle_size',   'name': 'Schläger-Größe +',   'desc': '+10% Schläger-Größe',           'cost': 40,  'max': 5},
    {'id': 'ball_control',  'name': 'Ball-Kontrolle',      'desc': 'Schärfere Winkel beim Treffen', 'cost': 50,  'max': 3},
    {'id': 'powerup_magnet','name': 'Power-Up Magnet',     'desc': 'Power-Ups ziehen sich an',     'cost': 80,  'max': 1},
    {'id': 'shield_start',  'name': 'Start-Schild',        'desc': 'Starte jedes Spiel mit Schild','cost': 100, 'max': 1},
    {'id': 'coin_bonus',    'name': 'Münzbonus',           'desc': '+50% Münzen pro Spiel',        'cost': 120, 'max': 1},
]

class Shop:
    def __init__(self, stats):
        self.stats    = stats
        self.levels   = {item['id']: 0 for item in SHOP_ITEMS}
        self.load()

    def save(self):
        try:
            data = {}
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE) as f:
                    data = json.load(f)
            data['shop_levels'] = self.levels
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def load(self):
        if not os.path.exists(SAVE_FILE):
            return
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            self.levels = data.get('shop_levels', self.levels)
        except Exception:
            pass

    def can_buy(self, item_id):
        for item in SHOP_ITEMS:
            if item['id'] == item_id:
                return (self.stats.coins >= item['cost'] and
                        self.levels[item_id] < item['max'])
        return False

    def buy(self, item_id):
        for item in SHOP_ITEMS:
            if item['id'] == item_id and self.can_buy(item_id):
                self.stats.coins -= item['cost']
                self.levels[item_id] += 1
                self.save()
                self.stats.save()
                return True
        return False

    def get_paddle_speed_bonus(self):
        return 1.0 + self.levels['paddle_speed'] * 0.10

    def get_paddle_size_bonus(self):
        return 1.0 + self.levels['paddle_size'] * 0.10

    def has_shield_start(self):
        return self.levels['shield_start'] >= 1

    def has_magnet(self):
        return self.levels['powerup_magnet'] >= 1

    def coin_multiplier(self):
        return 1.5 if self.levels['coin_bonus'] >= 1 else 1.0

# ── Partikel ──────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x   = x
        self.y   = y
        self.color    = color
        self.size     = random.randint(2, 5)
        self.vx  = random.uniform(-3, 3)
        self.vy  = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        self.age = 0

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.2
        self.age += 1

    def draw(self, screen):
        if self.age < self.lifetime:
            size = max(1, self.size * (1 - self.age / self.lifetime))
            pygame.draw.circle(screen, self.color,
                               (int(self.x), int(self.y)), int(size))

    def is_alive(self):
        return self.age < self.lifetime

# ── Power-Up ──────────────────────────────────────────────────────────────────
class PowerUp:
    """
    Typen: speed_up, speed_down, size_up, size_down,
           multi_ball, shield, ghost, magnet
    """
    COLOR_MAP = {
        'speed_up':   RED,
        'speed_down': BLUE,
        'size_up':    GREEN,
        'size_down':  ORANGE,
        'multi_ball': PURPLE,
        'shield':     CYAN,
        'ghost':      (180, 180, 255),
        'magnet':     GOLD,
    }
    SYMBOLS = {
        'speed_up':   '>>',
        'speed_down': '<<',
        'size_up':    '+',
        'size_down':  '-',
        'multi_ball': 'x2',
        'shield':     'SH',
        'ghost':      'GH',
        'magnet':     'MG',
    }

    def __init__(self, x, y, power_type):
        self.x    = x
        self.y    = y
        self.width  = 30
        self.height = 30
        self.type   = power_type
        self.lifetime = 360
        self.age  = 0
        self.color = self.COLOR_MAP.get(power_type, WHITE)
        self.current_size = self.width
        self._font = pygame.font.Font(None, 18)

    def update(self):
        self.age += 1
        self.current_size = self.width + math.sin(self.age * 0.1) * 5

    def draw(self, screen):
        r = int(self.current_size)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)
        pygame.draw.circle(screen, WHITE,      (int(self.x), int(self.y)), max(1, r - 5))
        txt = self._font.render(self.SYMBOLS.get(self.type, '?'), True, self.color)
        screen.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))
        # Restzeit-Bogen
        frac = 1.0 - self.age / self.lifetime
        if frac > 0:
            pygame.draw.arc(screen, self.color,
                            pygame.Rect(self.x - r - 4, self.y - r - 4, (r+4)*2, (r+4)*2),
                            math.pi/2, math.pi/2 + frac * 2 * math.pi, 2)

    def is_expired(self):
        return self.age >= self.lifetime

    def collides_with(self, rect):
        pr = pygame.Rect(self.x - self.width/2, self.y - self.height/2,
                         self.width, self.height)
        return pr.colliderect(rect)

# ── Ball ──────────────────────────────────────────────────────────────────────
class Ball:
    def __init__(self, x, y):
        self.base_speed = 5
        self.reset_position(x, y)
        self.radius   = 10
        self.color    = WHITE
        self.shape    = 'circle'
        self.trail    = []
        self.speed_multiplier = 1.0
        self.size_multiplier  = 1.0
        self.ghost    = False      # Geistball: geht durch Wände
        self.ghost_timer = 0

    def reset_position(self, x, y):
        self.x = x
        self.y = y
        direction = random.choice([-1, 1])
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.speed_x = self.base_speed * direction
        self.speed_y = self.base_speed * math.sin(angle)

    def update(self):
        self.x += self.speed_x * self.speed_multiplier
        self.y += self.speed_y * self.speed_multiplier
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)

        if self.ghost_timer > 0:
            self.ghost_timer -= 1
            if self.ghost_timer == 0:
                self.ghost = False

        r = self.radius * self.size_multiplier
        if not self.ghost:
            if self.y - r <= 0:
                self.y = r
                self.speed_y *= -1
            elif self.y + r >= SCREEN_HEIGHT:
                self.y = SCREEN_HEIGHT - r
                self.speed_y *= -1
        else:
            # Ghost: Teleportiert durch Wände
            if self.y < 0:
                self.y = SCREEN_HEIGHT
            elif self.y > SCREEN_HEIGHT:
                self.y = 0

    def draw(self, screen):
        ghost_col = (self.color[0]//3, self.color[1]//3, self.color[2]//3)
        for i, pos in enumerate(self.trail):
            size = int(self.radius * self.size_multiplier * (i / max(len(self.trail), 1)))
            if size > 0:
                pygame.draw.circle(screen, ghost_col,
                                   (int(pos[0]), int(pos[1])), size)
        r = int(self.radius * self.size_multiplier)
        draw_color = (min(255, self.color[0]+80),
                      min(255, self.color[1]+80),
                      min(255, self.color[2]+80)) if self.ghost else self.color
        if self.shape == 'circle':
            pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y)), r)
        elif self.shape == 'square':
            pygame.draw.rect(screen, draw_color,
                             pygame.Rect(int(self.x - r), int(self.y - r), r*2, r*2))
        elif self.shape == 'triangle':
            pts = [(int(self.x), int(self.y - r)),
                   (int(self.x - r), int(self.y + r)),
                   (int(self.x + r), int(self.y + r))]
            pygame.draw.polygon(screen, draw_color, pts)

    def get_rect(self):
        r = int(self.radius * self.size_multiplier)
        return pygame.Rect(int(self.x - r), int(self.y - r), r*2, r*2)

    def reverse_x(self):
        self.speed_x *= -1

    def hit_paddle(self, paddle_y, paddle_height):
        rel = (paddle_y + paddle_height / 2) - self.y
        norm = rel / (paddle_height / 2)
        angle = norm * (math.pi / 3)
        speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        self.speed_x = speed * math.cos(angle) * (-1 if self.speed_x > 0 else 1)
        self.speed_y = speed * -math.sin(angle)
        self.speed_x *= 1.04
        self.speed_y *= 1.04
        # Maximalgeschwindigkeit begrenzen
        max_s = 18
        total = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if total > max_s:
            self.speed_x = self.speed_x / total * max_s
            self.speed_y = self.speed_y / total * max_s

# ── Schläger ──────────────────────────────────────────────────────────────────
class Paddle:
    def __init__(self, x, y, player_id, is_ai=False):
        self.x = x
        self.y = y
        self.width  = 15
        self.height = 100
        self.speed  = 7
        self.color  = WHITE
        self.player_id = player_id
        self.shape  = 'rectangle'
        self.speed_multiplier = 1.0
        self.size_multiplier  = 1.0
        self.moving_up   = False
        self.moving_down = False
        self.is_ai  = is_ai
        self.ai_difficulty   = 'medium'
        self.ai_reaction_delay = 0
        # Schild-Effekt
        self.shield_active = False
        self.shield_timer  = 0
        # Magnet-Effekt
        self.magnet_active = False
        self.magnet_timer  = 0
        # Adaptive KI
        self._player_hit_positions = []   # Y-Positionen der letzten Ballschläge
        self._bias_y = 0                  # Lernoffset

    def update(self, ball=None):
        if self.is_ai and ball:
            self.ai_move(ball)
        if self.moving_up:
            self.y -= self.speed * self.speed_multiplier
        if self.moving_down:
            self.y += self.speed * self.speed_multiplier
        if self.y < 0:
            self.y = 0
        elif self.y + self.height * self.size_multiplier > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.height * self.size_multiplier
        # Timers
        if self.shield_timer > 0:
            self.shield_timer -= 1
            self.shield_active = self.shield_timer > 0
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
            self.magnet_active = self.magnet_timer > 0

    def activate_shield(self, duration=300):
        self.shield_active = True
        self.shield_timer  = duration

    def activate_magnet(self, duration=300):
        self.magnet_active = True
        self.magnet_timer  = duration

    def record_player_hit(self, ball_y):
        """Adaptive KI: merkt sich wo Spieler trifft."""
        self._player_hit_positions.append(ball_y)
        if len(self._player_hit_positions) > 20:
            self._player_hit_positions.pop(0)
        # Mittelwert – KI versucht sich daran anzupassen
        avg = sum(self._player_hit_positions) / len(self._player_hit_positions)
        center = SCREEN_HEIGHT / 2
        self._bias_y = (avg - center) * 0.15  # sanfter Bias

    def ai_move(self, ball):
        if self.ai_difficulty == 'easy':
            react, err, pred = 0.4, 70, False
        elif self.ai_difficulty == 'medium':
            react, err, pred = 0.65, 35, False
        elif self.ai_difficulty == 'hard':
            react, err, pred = 0.88, 12, True
        else:
            react, err, pred = 1.0, 0, True

        self.ai_reaction_delay += 1
        delay_threshold = int(60 * (1 - react))
        if self.ai_reaction_delay < delay_threshold:
            return
        self.ai_reaction_delay = 0

        target_y = ball.y
        if pred and ball.speed_x > 0:
            dist = self.x - ball.x
            if ball.speed_x != 0:
                t = dist / (ball.speed_x * ball.speed_multiplier)
                target_y = ball.y + ball.speed_y * ball.speed_multiplier * t
                while target_y < 0 or target_y > SCREEN_HEIGHT:
                    if target_y < 0:
                        target_y = -target_y
                    elif target_y > SCREEN_HEIGHT:
                        target_y = 2 * SCREEN_HEIGHT - target_y

        # Adaptiver Offset (bei hard/impossible stärker berücksichtigt)
        if self.ai_difficulty in ('hard', 'impossible'):
            target_y += self._bias_y

        if err > 0:
            target_y += random.randint(-err, err)

        center = self.y + (self.height * self.size_multiplier) / 2
        dead = 12
        if target_y < center - dead:
            self.moving_up, self.moving_down = True, False
        elif target_y > center + dead:
            self.moving_up, self.moving_down = False, True
        else:
            self.moving_up, self.moving_down = False, False

    def set_difficulty(self, d):
        self.ai_difficulty = d

    def draw(self, screen):
        h = int(self.height * self.size_multiplier)
        if self.shape == 'rectangle':
            rect = pygame.Rect(int(self.x), int(self.y), self.width, h)
            pygame.draw.rect(screen, self.color, rect)
        elif self.shape == 'rounded':
            rect = pygame.Rect(int(self.x), int(self.y), self.width, h)
            pygame.draw.rect(screen, self.color, rect, border_radius=10)
        elif self.shape == 'diamond':
            pts = [
                (int(self.x + self.width/2), int(self.y)),
                (int(self.x + self.width),   int(self.y + h/2)),
                (int(self.x + self.width/2), int(self.y + h)),
                (int(self.x),                int(self.y + h/2)),
            ]
            pygame.draw.polygon(screen, self.color, pts)
        # Schild-Aura
        if self.shield_active:
            cx = int(self.x + self.width / 2)
            cy = int(self.y + h / 2)
            pygame.draw.circle(screen, CYAN,   (cx, cy), max(h//2+10, 30), 3)
            pygame.draw.circle(screen, (0,200,255,100), (cx, cy), max(h//2+14,34), 1)
        # Magnet-Aura
        if self.magnet_active:
            cx = int(self.x + self.width / 2)
            cy = int(self.y + h / 2)
            pygame.draw.circle(screen, GOLD, (cx, cy), max(h//2+10, 30), 2)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y),
                           self.width, int(self.height * self.size_multiplier))

# ── Hauptspiel ────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ping Pong – Erweiterte Edition")
        self.clock   = pygame.time.Clock()
        self.running = True

        # State-Machine
        self.state = 'menu'
        # menu | difficulty_select | playing | paused | game_over
        # settings_colors | settings_shapes | shop | stats | achievements
        # mode_select

        self.game_mode    = 'classic'   # classic | timelimit | survival
        self.ai_difficulty = 'medium'

        self.stats = Stats()
        self.shop  = Shop(self.stats)
        self.sound = SoundManager()

        self._init_paddles()
        self.balls = [Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)]
        self.score1 = 0
        self.score2 = 0
        self.winning_score = 5

        # Zeitlimit-Modus
        self.time_limit    = 60 * FPS   # 60 Sekunden
        self.time_remaining = self.time_limit

        # Survival-Modus
        self.survival_lives   = 3
        self.survival_elapsed = 0

        # Rallye-Zähler (für Achievement)
        self.current_rally = 0
        self.max_rally_session = 0

        # Neue Achievement-Notifikationen
        self.achievement_queue = []
        self.achievement_display_timer = 0
        self.achievement_display_item  = None

        # Partikel / Power-Ups
        self.particles  = []
        self.powerups   = []
        self.powerup_timer = 0
        self.powerup_spawn_interval = 280

        # Fonts
        self.font_large  = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small  = pygame.font.Font(None, 24)
        self.font_tiny   = pygame.font.Font(None, 20)

        self.bg_color = BLACK

        # Farbwechsel-Menü
        self._color_target  = 'p1'   # p1 | p2 | ball | bg
        self._color_keys = {
            pygame.K_r: 'Rot', pygame.K_g: 'Grün', pygame.K_b: 'Blau',
            pygame.K_y: 'Gelb', pygame.K_p: 'Lila', pygame.K_o: 'Orange',
            pygame.K_c: 'Cyan', pygame.K_w: 'Weiß', pygame.K_k: 'Schwarz',
        }
        self._color_extra = {'Schwarz': BLACK}

        # Formenmenü
        self._shape_target = 'paddle'  # paddle | ball
        self._paddle_shapes = ['rectangle', 'rounded', 'diamond']
        self._ball_shapes   = ['circle', 'square', 'triangle']

        # Shop-Cursor
        self._shop_cursor = 0

        # Stats-Seite
        self._stats_page = 0

        # Adaptive KI Daten
        self._session_hits = []

    def _init_paddles(self):
        self.paddle1 = Paddle(30, SCREEN_HEIGHT//2 - 50, 1, is_ai=False)
        self.paddle2 = Paddle(SCREEN_WIDTH - 45, SCREEN_HEIGHT//2 - 50, 2, is_ai=True)
        self.paddle2.set_difficulty(self.ai_difficulty)
        self._apply_shop_bonuses()

    def _apply_shop_bonuses(self):
        bonus_speed = self.shop.get_paddle_speed_bonus()
        bonus_size  = self.shop.get_paddle_size_bonus()
        self.paddle1.speed_multiplier = bonus_speed
        self.paddle1.size_multiplier  = bonus_size
        if self.shop.has_shield_start():
            self.paddle1.activate_shield(600)

    # ── Spawn ─────────────────────────────────────────────────────────────────
    def spawn_powerup(self):
        x = random.randint(SCREEN_WIDTH//3, 2*SCREEN_WIDTH//3)
        y = random.randint(100, SCREEN_HEIGHT - 100)
        all_types = ['speed_up', 'speed_down', 'size_up', 'size_down',
                     'multi_ball', 'shield', 'ghost', 'magnet']
        t = random.choice(all_types)
        self.powerups.append(PowerUp(x, y, t))

    def start_single_player(self):
        self.paddle2.is_ai = True
        self.paddle2.set_difficulty(self.ai_difficulty)
        diff_colors = {'easy': RED, 'medium': ORANGE,
                       'hard': PURPLE, 'impossible': PINK}
        self.paddle2.color = diff_colors.get(self.ai_difficulty, WHITE)
        self.reset_game()
        self.state = 'playing'

    # ── Power-Up Anwenden ─────────────────────────────────────────────────────
    def apply_powerup(self, powerup, paddle):
        if powerup.type == 'speed_up':
            paddle.speed_multiplier = min(2.5, paddle.speed_multiplier + 0.3)
        elif powerup.type == 'speed_down':
            paddle.speed_multiplier = max(0.4, paddle.speed_multiplier - 0.3)
        elif powerup.type == 'size_up':
            paddle.size_multiplier = min(2.5, paddle.size_multiplier + 0.3)
        elif powerup.type == 'size_down':
            paddle.size_multiplier = max(0.3, paddle.size_multiplier - 0.3)
        elif powerup.type == 'multi_ball':
            if len(self.balls) < 4:
                nb = Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                nb.color = random.choice([RED, GREEN, BLUE, YELLOW, ORANGE])
                nb.shape = self.balls[0].shape
                self.balls.append(nb)
        elif powerup.type == 'shield':
            paddle.activate_shield(400)
        elif powerup.type == 'ghost':
            for b in self.balls:
                b.ghost = True
                b.ghost_timer = 250
        elif powerup.type == 'magnet':
            paddle.activate_magnet(400)

    def _magnet_attract(self, paddle, powerups):
        """Magnet-Effekt: Power-Ups bewegen sich zum Schläger."""
        if not paddle.magnet_active:
            return
        cx = paddle.x + paddle.width / 2
        cy = paddle.y + (paddle.height * paddle.size_multiplier) / 2
        for pu in powerups:
            dx = cx - pu.x
            dy = cy - pu.y
            dist = math.sqrt(dx**2 + dy**2) or 1
            if dist < 250:
                pu.x += dx / dist * 3
                pu.y += dy / dist * 3

    # ── Partikel ──────────────────────────────────────────────────────────────
    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    # ── Events ────────────────────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stats.save()
                self.running = False

            if event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.paddle1.moving_up = False
                elif event.key == pygame.K_s:
                    self.paddle1.moving_down = False
                if not self.paddle2.is_ai:
                    if event.key == pygame.K_UP:
                        self.paddle2.moving_up = False
                    elif event.key == pygame.K_DOWN:
                        self.paddle2.moving_down = False

    def _handle_key(self, key):
        # ── Immer: Spieler-Bewegung ──
        if key == pygame.K_w:
            self.paddle1.moving_up = True
        elif key == pygame.K_s:
            self.paddle1.moving_down = True
        if not self.paddle2.is_ai:
            if key == pygame.K_UP:
                self.paddle2.moving_up = True
            elif key == pygame.K_DOWN:
                self.paddle2.moving_down = True

        # ── Menü ──
        if self.state == 'menu':
            if key == pygame.K_1:
                self.game_mode = 'single'
                self.state = 'difficulty_select'
            elif key == pygame.K_2:
                self.game_mode = 'two_player'
                self.paddle2.is_ai = False
                self.reset_game()
                self.state = 'playing'
            elif key == pygame.K_3:
                self.state = 'mode_select'
            elif key == pygame.K_4:
                self.state = 'settings_colors'
            elif key == pygame.K_5:
                self.state = 'settings_shapes'
            elif key == pygame.K_6:
                self._shop_cursor = 0
                self.state = 'shop'
            elif key == pygame.K_7:
                self._stats_page = 0
                self.state = 'stats'
            elif key == pygame.K_8:
                self.state = 'achievements'
            elif key == pygame.K_9:
                self.sound.enabled = not self.sound.enabled
            elif key == pygame.K_0:
                self.stats.save()
                self.running = False

        # ── Schwierigkeitswahl ──
        elif self.state == 'difficulty_select':
            diff_map = {pygame.K_1: 'easy', pygame.K_2: 'medium',
                        pygame.K_3: 'hard', pygame.K_4: 'impossible'}
            if key in diff_map:
                self.ai_difficulty = diff_map[key]
                self.start_single_player()
            elif key == pygame.K_ESCAPE:
                self.state = 'menu'

        # ── Moduswahl ──
        elif self.state == 'mode_select':
            if key == pygame.K_1:
                self.game_mode = 'classic'
                self.game_mode_display = 'classic'
            elif key == pygame.K_2:
                self.game_mode = 'timelimit'
            elif key == pygame.K_3:
                self.game_mode = 'survival'
            elif key == pygame.K_ESCAPE:
                self.state = 'menu'
            if key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.state = 'difficulty_select'

        # ── Spielend / Pause ──
        elif self.state in ('playing', 'paused'):
            if key == pygame.K_ESCAPE:
                self.stats.save()
                self.state = 'menu'
                self.reset_game()
            elif key == pygame.K_p:
                self.state = 'paused' if self.state == 'playing' else 'playing'

        # ── Game Over ──
        elif self.state == 'game_over':
            if key == pygame.K_ESCAPE:
                self.state = 'menu'
            elif key == pygame.K_r:
                self.start_single_player() if self.paddle2.is_ai else self._restart_two()

        # ── Farbeinstellungen ──
        elif self.state == 'settings_colors':
            if key == pygame.K_ESCAPE:
                self.state = 'menu'
            elif key == pygame.K_1:
                self._color_target = 'p1'
            elif key == pygame.K_2:
                self._color_target = 'p2'
            elif key == pygame.K_3:
                self._color_target = 'ball'
            elif key == pygame.K_4:
                self._color_target = 'bg'
            else:
                col_name = self._color_keys.get(key)
                if col_name:
                    col = {**COLOR_OPTIONS, **self._color_extra}.get(col_name)
                    if col:
                        if self._color_target == 'p1':
                            self.paddle1.color = col
                        elif self._color_target == 'p2':
                            self.paddle2.color = col
                        elif self._color_target == 'ball':
                            for b in self.balls:
                                b.color = col
                        elif self._color_target == 'bg':
                            self.bg_color = col

        # ── Formeneinstellungen ──
        elif self.state == 'settings_shapes':
            if key == pygame.K_ESCAPE:
                self.state = 'menu'
            elif key == pygame.K_p:
                self._shape_target = 'paddle'
            elif key == pygame.K_b:
                self._shape_target = 'ball'
            elif key == pygame.K_1:
                if self._shape_target == 'paddle':
                    self.paddle1.shape = 'rectangle'
                    self.paddle2.shape = 'rectangle'
                else:
                    for b in self.balls:
                        b.shape = 'circle'
            elif key == pygame.K_2:
                if self._shape_target == 'paddle':
                    self.paddle1.shape = 'rounded'
                    self.paddle2.shape = 'rounded'
                else:
                    for b in self.balls:
                        b.shape = 'square'
            elif key == pygame.K_3:
                if self._shape_target == 'paddle':
                    self.paddle1.shape = 'diamond'
                    self.paddle2.shape = 'diamond'
                else:
                    for b in self.balls:
                        b.shape = 'triangle'

        # ── Shop ──
        elif self.state == 'shop':
            if key == pygame.K_ESCAPE:
                self.state = 'menu'
            elif key == pygame.K_UP:
                self._shop_cursor = (self._shop_cursor - 1) % len(SHOP_ITEMS)
            elif key == pygame.K_DOWN:
                self._shop_cursor = (self._shop_cursor + 1) % len(SHOP_ITEMS)
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                item = SHOP_ITEMS[self._shop_cursor]
                if self.shop.buy(item['id']):
                    self.sound.play('powerup')
                    self.create_particles(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, GOLD, 25)

        # ── Statistiken / Achievements ──
        elif self.state in ('stats', 'achievements'):
            if key == pygame.K_ESCAPE:
                self.state = 'menu'

    def _restart_two(self):
        self.paddle2.is_ai = False
        self.reset_game()
        self.state = 'playing'

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self):
        # Achievement-Anzeige
        if self.achievement_display_timer > 0:
            self.achievement_display_timer -= 1
        elif self.achievement_queue:
            key = self.achievement_queue.pop(0)
            self.achievement_display_item  = key
            self.achievement_display_timer = 180
            self.sound.play('achieve')

        if self.state != 'playing':
            return

        # Survival: Zeit zählen
        if self.game_mode == 'survival':
            self.survival_elapsed += 1

        # Zeitlimit-Modus
        if self.game_mode == 'timelimit':
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self._end_game()
                return

        # Magnet-Effekte
        self._magnet_attract(self.paddle1, self.powerups)
        self._magnet_attract(self.paddle2, self.powerups)

        # Nächsten Ball für KI finden
        closest_ball = self.balls[0] if self.balls else None
        if self.paddle2.is_ai and len(self.balls) > 1:
            closest_ball = min(self.balls, key=lambda b: abs(b.x - self.paddle2.x))

        self.paddle1.update()
        self.paddle2.update(closest_ball)

        # Bälle
        to_remove = []
        for ball in self.balls:
            ball.update()

            # Schläger 1 Kollision
            if ball.speed_x < 0 and ball.get_rect().colliderect(self.paddle1.get_rect()):
                if self.paddle1.shield_active:
                    ball.speed_x = abs(ball.speed_x)  # Schild: immer zurück
                    self.sound.play('shield')
                else:
                    ball.hit_paddle(self.paddle1.y,
                                    self.paddle1.height * self.paddle1.size_multiplier)
                ball.x = self.paddle1.x + self.paddle1.width + ball.radius * ball.size_multiplier
                self.create_particles(ball.x, ball.y, self.paddle1.color, 12)
                self.sound.play('hit')
                self.current_rally += 1
                # Adaptive KI: Treffpunkt merken
                self.paddle2.record_player_hit(ball.y)

            # Schläger 2 Kollision
            if ball.speed_x > 0 and ball.get_rect().colliderect(self.paddle2.get_rect()):
                if self.paddle2.shield_active:
                    ball.speed_x = -abs(ball.speed_x)
                    self.sound.play('shield')
                else:
                    ball.hit_paddle(self.paddle2.y,
                                    self.paddle2.height * self.paddle2.size_multiplier)
                ball.x = self.paddle2.x - ball.radius * ball.size_multiplier
                self.create_particles(ball.x, ball.y, self.paddle2.color, 12)
                self.sound.play('hit')
                self.current_rally += 1

            # Ball raus
            if ball.x < 0:
                if self.game_mode == 'survival':
                    self.survival_lives -= 1
                    self.sound.play('score')
                    if self.survival_lives <= 0:
                        self._end_game()
                        return
                else:
                    self.score2 += 1
                    self.sound.play('score')
                self.max_rally_session = max(self.max_rally_session, self.current_rally)
                self.current_rally = 0
                to_remove.append(ball)
                self.create_particles(SCREEN_WIDTH//4, ball.y, RED, 25)
            elif ball.x > SCREEN_WIDTH:
                self.score1 += 1
                self.sound.play('score')
                coins_earned = int(1 * self.shop.coin_multiplier())
                self.stats.coins += coins_earned
                self.max_rally_session = max(self.max_rally_session, self.current_rally)
                self.current_rally = 0
                to_remove.append(ball)
                self.create_particles(3*SCREEN_WIDTH//4, ball.y, GREEN, 25)

        for b in to_remove:
            self.balls.remove(b)
        if not self.balls:
            nb = Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            nb.shape = self.balls[0].shape if self.balls else 'circle'
            self.balls = [nb]

        # Gewinner prüfen
        if self.game_mode == 'classic':
            if self.score1 >= self.winning_score or self.score2 >= self.winning_score:
                self._end_game()

        # Power-Ups spawnen
        self.powerup_timer += 1
        if self.powerup_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_timer = 0

        # Power-Ups verarbeiten
        pu_remove = []
        for pu in self.powerups:
            pu.update()
            if pu.collides_with(self.paddle1.get_rect()):
                self.apply_powerup(pu, self.paddle1)
                pu_remove.append(pu)
                self.stats.powerups_col += 1
                self.create_particles(pu.x, pu.y, pu.color, 18)
                self.sound.play('powerup')
            elif pu.collides_with(self.paddle2.get_rect()):
                self.apply_powerup(pu, self.paddle2)
                pu_remove.append(pu)
                self.create_particles(pu.x, pu.y, pu.color, 18)
                self.sound.play('powerup')
            else:
                for ball in self.balls:
                    if pu.collides_with(ball.get_rect()):
                        if pu.type == 'speed_up':
                            ball.speed_multiplier = min(2.0, ball.speed_multiplier + 0.2)
                        elif pu.type == 'speed_down':
                            ball.speed_multiplier = max(0.5, ball.speed_multiplier - 0.2)
                        pu_remove.append(pu)
                        self.create_particles(pu.x, pu.y, pu.color, 18)
                        self.sound.play('powerup')
                        break
            if pu.is_expired():
                pu_remove.append(pu)
        for pu in set(pu_remove):
            if pu in self.powerups:
                self.powerups.remove(pu)

        # Partikel
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update()

    def _end_game(self):
        self.state = 'game_over'
        # Statistiken aktualisieren
        p1_won = False
        if self.game_mode == 'survival':
            p1_won = self.survival_lives > 0 and self.survival_elapsed >= 120 * FPS
        elif self.game_mode == 'timelimit':
            p1_won = self.score1 >= self.score2
        else:
            p1_won = self.score1 > self.score2

        if p1_won:
            self.stats.wins += 1
            self.sound.play('win')
        else:
            self.stats.losses += 1
        self.stats.total_games += 1
        self.stats.max_rally = max(self.stats.max_rally, self.max_rally_session)

        ctx = {
            'beat_easy':      p1_won and self.ai_difficulty == 'easy',
            'beat_medium':    p1_won and self.ai_difficulty == 'medium',
            'beat_hard':      p1_won and self.ai_difficulty == 'hard',
            'beat_impossible':p1_won and self.ai_difficulty == 'impossible',
            'shutout':        p1_won and self.score2 == 0,
            'survived_120':   self.game_mode == 'survival' and self.survival_elapsed >= 120 * FPS,
        }
        new_ach = self.stats.check_achievements(ctx)
        self.achievement_queue.extend(new_ach)
        self.stats.save()

    # ── Zeichnen ──────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(self.bg_color)

        draw_map = {
            'menu':            self.draw_menu,
            'difficulty_select': self.draw_difficulty_select,
            'mode_select':     self.draw_mode_select,
            'playing':         self.draw_game,
            'paused':          self._draw_pause,
            'game_over':       self.draw_game_over,
            'settings_colors': self.draw_color_settings,
            'settings_shapes': self.draw_shape_settings,
            'shop':            self.draw_shop,
            'stats':           self.draw_stats,
            'achievements':    self.draw_achievements,
        }
        fn = draw_map.get(self.state)
        if fn:
            fn()

        # Achievement-Popup (immer oben)
        if self.achievement_display_timer > 0 and self.achievement_display_item:
            self._draw_achievement_popup(self.achievement_display_item)

        pygame.display.flip()

    def _box(self, x, y, w, h, color=DARK_GRAY, border=GRAY, radius=8):
        pygame.draw.rect(self.screen, color,  (x, y, w, h), border_radius=radius)
        pygame.draw.rect(self.screen, border, (x, y, w, h), 2, border_radius=radius)

    def _title(self, text, color=CYAN, y=70):
        t = self.font_large.render(text, True, color)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, y)))

    def _label(self, text, color=WHITE, y=0, x=None, size='small'):
        f = {'large': self.font_large, 'medium': self.font_medium,
             'small': self.font_small, 'tiny': self.font_tiny}[size]
        t = f.render(text, True, color)
        if x is None:
            self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, y)))
        else:
            self.screen.blit(t, (x, y))

    # ── Menüs ─────────────────────────────────────────────────────────────────
    def draw_menu(self):
        self._title("PING PONG", CYAN, 75)
        self._label("Erweiterte Edition", GRAY, 130, size='small')

        items = [
            ("1", "Einzelspieler (vs CPU)",      YELLOW),
            ("2", "Zwei Spieler (lokal)",         YELLOW),
            ("3", "Spielmodus wählen",            WHITE),
            ("4", "Farben Anpassen",              WHITE),
            ("5", "Formen Ändern",                WHITE),
            (f"6 [Münzen: {self.stats.coins}]", "Shop / Upgrades", GOLD),
            ("7", "Statistiken",                  SILVER),
            ("8", "Achievements",                 SILVER),
            (f"9 [{'AN' if self.sound.enabled else 'AUS'}]", "Sound", CYAN),
            ("0", "Beenden",                      RED),
        ]
        y = 185
        for key, label, color in items:
            self._label(f"[{key}]  {label}", color, y, size='small')
            y += 42

        # Münzen-Anzeige
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 60, 30), 14)
        self._label(f"{self.stats.coins}", GOLD, 22, SCREEN_WIDTH - 40, 'small')

    def draw_difficulty_select(self):
        self._title("Schwierigkeit Wählen", CYAN, 80)
        mode_names = {'classic': 'Classic', 'timelimit': 'Zeitlimit', 'survival': 'Survival'}
        self._label(f"Modus: {mode_names.get(self.game_mode, 'Classic')}",
                    GRAY, 130, size='small')
        entries = [
            ("1", "EINFACH",    RED,    "Langsame KI, macht viele Fehler"),
            ("2", "MITTEL",     ORANGE, "Normale KI, reagiert gut"),
            ("3", "SCHWER",     PURPLE, "Schnelle KI mit Ball-Vorhersage"),
            ("4", "UNMÖGLICH",  PINK,   "Perfekte KI + lernt von dir"),
        ]
        y = 210
        for key, name, col, desc in entries:
            self._box(SCREEN_WIDTH//2 - 310, y - 22, 620, 70, DARK_GRAY, col)
            self._label(f"[{key}]  {name}", col, y, size='medium')
            self._label(desc, GRAY, y + 30, size='tiny')
            y += 95
        self._label("ESC = Zurück", GRAY, 650, size='tiny')

    def draw_mode_select(self):
        self._title("Spielmodus", PURPLE, 80)
        modes = [
            ("1", "Classic",   WHITE,  "Erster auf 5 Punkte gewinnt"),
            ("2", "Zeitlimit", YELLOW, "60 Sekunden – wer mehr Punkte hat, gewinnt"),
            ("3", "Survival",  RED,    "3 Leben – überebe so lang wie möglich"),
        ]
        y = 220
        for key, name, col, desc in modes:
            self._box(SCREEN_WIDTH//2 - 320, y - 25, 640, 80, DARK_GRAY, col)
            self._label(f"[{key}]  {name}", col, y, size='medium')
            self._label(desc, GRAY, y + 33, size='tiny')
            y += 110
        self._label("ESC = Zurück", GRAY, 650, size='tiny')

    def draw_game(self):
        # Mittellinie
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, DARK_GRAY, (SCREEN_WIDTH//2 - 2, y, 4, 10))

        for p in self.particles:
            p.draw(self.screen)
        for pu in self.powerups:
            pu.draw(self.screen)

        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)
        for b in self.balls:
            b.draw(self.screen)

        # HUD Punkte
        if self.game_mode == 'timelimit':
            secs = self.time_remaining // FPS
            timer_col = RED if secs < 10 else WHITE
            t = self.font_large.render(f"{self.score1}  {secs}s  {self.score2}", True, timer_col)
        elif self.game_mode == 'survival':
            elapsed_s = self.survival_elapsed // FPS
            lives_str = "♥ " * self.survival_lives
            t = self.font_large.render(f"{lives_str}  {elapsed_s}s", True, RED)
        else:
            t = self.font_large.render(f"{self.score1}    {self.score2}", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, 45)))

        # Labels
        diff_map = {'easy':'EINFACH','medium':'MITTEL','hard':'SCHWER','impossible':'UNMÖGLICH'}
        if self.paddle2.is_ai:
            self._label("SPIELER", GREEN, 90, size='tiny')
            p2l = self.font_tiny.render(f"CPU ({diff_map[self.ai_difficulty]})", True, self.paddle2.color)
            self.screen.blit(p2l, p2l.get_rect(topright=(SCREEN_WIDTH - 10, 85)))

        # Upgrade-Info
        u1 = f"SPD:{self.paddle1.speed_multiplier:.1f}x  SZ:{self.paddle1.size_multiplier:.1f}x"
        self._label(u1, GREEN, 6, 5, 'tiny')
        u2 = f"SPD:{self.paddle2.speed_multiplier:.1f}x  SZ:{self.paddle2.size_multiplier:.1f}x"
        t2 = self.font_tiny.render(u2, True, GREEN)
        self.screen.blit(t2, t2.get_rect(topright=(SCREEN_WIDTH - 5, 6)))

        # Rally
        if self.current_rally >= 5:
            rc = YELLOW if self.current_rally < 15 else RED
            self._label(f"Rally: {self.current_rally}!", rc, SCREEN_HEIGHT - 25, size='tiny')

        # P – Pause Hinweis
        self._label("[P] Pause  [ESC] Menü", DARK_GRAY, SCREEN_HEIGHT - 8, size='tiny')

    def _draw_pause(self):
        self.draw_game()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        self._title("PAUSE", YELLOW, SCREEN_HEIGHT//2 - 40)
        self._label("[P] Weiter  |  [ESC] Menü", WHITE, SCREEN_HEIGHT//2 + 30, size='medium')

    def draw_game_over(self):
        if self.game_mode == 'survival':
            secs = self.survival_elapsed // FPS
            if self.survival_lives > 0:
                winner, wc = f"Überlebt! {secs}s", GREEN
            else:
                winner, wc = f"Game Over nach {secs}s", RED
        elif self.paddle2.is_ai:
            winner, wc = ("Du hast gewonnen! 🏆", GREEN) if self.score1 > self.score2 \
                         else ("CPU hat gewonnen! 🤖", RED)
        else:
            winner, wc = ("Spieler 1 gewinnt!", self.paddle1.color) if self.score1 > self.score2 \
                         else ("Spieler 2 gewinnt!", self.paddle2.color)

        self._title(winner, wc, SCREEN_HEIGHT//2 - 110)
        if self.paddle2.is_ai:
            diff_map = {'easy':'EINFACH','medium':'MITTEL','hard':'SCHWER','impossible':'UNMÖGLICH'}
            self._label(f"Schwierigkeit: {diff_map[self.ai_difficulty]}", GRAY,
                        SCREEN_HEIGHT//2 - 50, size='small')
        self._label(f"Endstand: {self.score1} – {self.score2}", WHITE,
                    SCREEN_HEIGHT//2 + 10, size='medium')
        self._label(f"Münzen verdient: +{int(max(self.score1,1)*self.shop.coin_multiplier())}",
                    GOLD, SCREEN_HEIGHT//2 + 55, size='small')
        self._label("[ESC] Hauptmenü   [R] Nochmal", GRAY,
                    SCREEN_HEIGHT//2 + 110, size='small')

    # ── Einstellungen ─────────────────────────────────────────────────────────
    def draw_color_settings(self):
        self._title("Farbanpassung", CYAN, 55)
        targets = [('1','Schläger 1', self.paddle1.color),
                   ('2','Schläger 2', self.paddle2.color),
                   ('3','Ball',       self.balls[0].color if self.balls else WHITE),
                   ('4','Hintergrund',self.bg_color)]
        y = 105
        for k, name, col in targets:
            active = (self._color_target == ['p1','p2','ball','bg'][int(k)-1])
            border = YELLOW if active else GRAY
            self._box(SCREEN_WIDTH//2 - 250, y - 12, 500, 34, DARK_GRAY, border)
            self._label(f"[{k}] {name}", YELLOW if active else WHITE, y, size='small')
            pygame.draw.rect(self.screen, col,
                             (SCREEN_WIDTH//2 + 150, y - 10, 60, 28))
            pygame.draw.rect(self.screen, WHITE,
                             (SCREEN_WIDTH//2 + 150, y - 10, 60, 28), 1)
            y += 52

        self._label("── Farbtasten ──", GRAY, y + 10, size='tiny')
        y += 32
        entries = [('R','Rot',RED),('G','Grün',GREEN),('B','Blau',BLUE),
                   ('Y','Gelb',YELLOW),('P','Lila',PURPLE),('O','Orange',ORANGE),
                   ('C','Cyan',CYAN),('W','Weiß',WHITE),('K','Schwarz',(30,30,30))]
        cols_per_row = 3
        for i, (k, name, col) in enumerate(entries):
            col_x = SCREEN_WIDTH//2 - 280 + (i % cols_per_row) * 200
            row_y = y + (i // cols_per_row) * 42
            pygame.draw.rect(self.screen, col, (col_x, row_y, 28, 28))
            self._label(f"[{k}] {name}", col if col != WHITE else GRAY,
                        row_y + 6, col_x + 36, 'tiny')

        # Vorschau-Paddel
        preview_y = SCREEN_HEIGHT - 110
        self._label("Vorschau:", GRAY, preview_y, size='tiny')
        pygame.draw.rect(self.screen, self.paddle1.color,
                         (SCREEN_WIDTH//2 - 120, preview_y+20, 15, 70))
        if self.balls:
            pygame.draw.circle(self.screen, self.balls[0].color,
                               (SCREEN_WIDTH//2, preview_y+55), 12)
        pygame.draw.rect(self.screen, self.paddle2.color,
                         (SCREEN_WIDTH//2 + 105, preview_y+20, 15, 70))
        self._label("ESC = Zurück", GRAY, SCREEN_HEIGHT - 15, size='tiny')

    def draw_shape_settings(self):
        self._title("Formen Ändern", PURPLE, 60)

        active_p = self._shape_target == 'paddle'
        self._label("[P] Schläger  |  [B] Ball",
                    WHITE, 120, size='medium')

        # Schläger-Formen
        self._box(60, 160, 500, 220, DARK_GRAY,
                  YELLOW if active_p else GRAY)
        self._label("Schläger-Formen:", YELLOW if active_p else GRAY, 175, size='small')
        shapes_p = [('1','Rectangle (Standard)'),('2','Rounded (Abgerundet)'),('3','Diamond (Diamant)')]
        for i, (k, name) in enumerate(shapes_p):
            cur = self.paddle1.shape == ['rectangle','rounded','diamond'][i]
            col = GREEN if cur else WHITE
            self._label(f"[{k}] {name}", col, 215 + i*52, size='small')

        # Ball-Formen
        self._box(640, 160, 500, 220, DARK_GRAY,
                  YELLOW if not active_p else GRAY)
        self._label("Ball-Formen:", YELLOW if not active_p else GRAY, 175, size='small')
        shapes_b = [('1','Circle (Kreis)'),('2','Square (Quadrat)'),('3','Triangle (Dreieck)')]
        cur_bshape = self.balls[0].shape if self.balls else 'circle'
        for i, (k, name) in enumerate(shapes_b):
            cur = cur_bshape == ['circle','square','triangle'][i]
            col = GREEN if cur else WHITE
            t = self.font_small.render(f"[{k}] {name}", True, col)
            self.screen.blit(t, t.get_rect(center=(890, 215 + i*52)))

        # Vorschau
        prev_y = 430
        self._label("Vorschau:", GRAY, prev_y, size='small')
        # Schläger
        p1c = self.paddle1
        pad_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, prev_y+30, 15, 80)
        if p1c.shape == 'rectangle':
            pygame.draw.rect(self.screen, self.paddle1.color, pad_rect)
        elif p1c.shape == 'rounded':
            pygame.draw.rect(self.screen, self.paddle1.color, pad_rect, border_radius=8)
        elif p1c.shape == 'diamond':
            pts = [(pad_rect.centerx, pad_rect.top),
                   (pad_rect.right, pad_rect.centery),
                   (pad_rect.centerx, pad_rect.bottom),
                   (pad_rect.left, pad_rect.centery)]
            pygame.draw.polygon(self.screen, self.paddle1.color, pts)
        # Ball
        bx, by = SCREEN_WIDTH//2, prev_y + 70
        bc = self.balls[0].color if self.balls else WHITE
        bs = cur_bshape
        r = 18
        if bs == 'circle':
            pygame.draw.circle(self.screen, bc, (bx, by), r)
        elif bs == 'square':
            pygame.draw.rect(self.screen, bc, (bx-r, by-r, r*2, r*2))
        elif bs == 'triangle':
            pygame.draw.polygon(self.screen, bc,
                                [(bx, by-r),(bx-r, by+r),(bx+r, by+r)])

        self._label("ESC = Zurück", GRAY, SCREEN_HEIGHT - 18, size='tiny')

    # ── Shop ─────────────────────────────────────────────────────────────────
    def draw_shop(self):
        self._title("Upgrade-Shop", GOLD, 55)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 60, 30), 14)
        self._label(f"{self.stats.coins} Münzen", GOLD, 22, SCREEN_WIDTH - 110, 'small')

        y = 115
        for i, item in enumerate(SHOP_ITEMS):
            selected = i == self._shop_cursor
            level    = self.shop.levels[item['id']]
            maxed    = level >= item['max']
            affordable = self.stats.coins >= item['cost']

            if selected:
                border = GOLD
            elif maxed:
                border = GREEN
            elif not affordable:
                border = GRAY
            else:
                border = WHITE

            self._box(80, y - 8, SCREEN_WIDTH - 160, 62, DARK_GRAY, border)

            # Name & Beschreibung
            col = GRAY if maxed else (WHITE if affordable else DARK_GRAY)
            self._label(item['name'], border if selected else col, y + 6, 100, 'small')
            self._label(item['desc'], GRAY, y + 34, 100, 'tiny')

            # Kosten / Level
            status = "MAX" if maxed else f"{item['cost']} 🪙"
            sc = GREEN if maxed else (GOLD if affordable else GRAY)
            ts = self.font_small.render(status, True, sc)
            self.screen.blit(ts, ts.get_rect(topright=(SCREEN_WIDTH - 100, y + 6)))

            # Level-Balken
            max_l = item['max']
            bar_w = 120
            bar_x = SCREEN_WIDTH - 240
            bar_y = y + 36
            pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_w, 10), border_radius=4)
            if max_l > 0:
                fill = int(bar_w * level / max_l)
                if fill > 0:
                    pygame.draw.rect(self.screen, GREEN,
                                     (bar_x, bar_y, fill, 10), border_radius=4)
            lv_t = self.font_tiny.render(f"Lv {level}/{max_l}", True, GRAY)
            self.screen.blit(lv_t, (bar_x + bar_w + 6, bar_y - 2))
            y += 76

        self._label("↑/↓ Navigieren   ENTER/SPACE Kaufen   ESC Zurück",
                    GRAY, SCREEN_HEIGHT - 18, size='tiny')

    # ── Statistiken ──────────────────────────────────────────────────────────
    def draw_stats(self):
        self._title("Statistiken", SILVER, 60)
        entries = [
            ("Siege",            str(self.stats.wins),         GREEN),
            ("Niederlagen",      str(self.stats.losses),       RED),
            ("Gesamt Spiele",    str(self.stats.total_games),  WHITE),
            ("Power-Ups gesammelt", str(self.stats.powerups_col), ORANGE),
            ("Bester Rally",     str(self.stats.max_rally),    YELLOW),
            ("Münzen gesamt",    str(self.stats.coins),        GOLD),
            ("Win-Rate", f"{(self.stats.wins/(max(1,self.stats.total_games))*100):.1f}%", CYAN),
        ]
        y = 140
        for label, value, col in entries:
            self._box(SCREEN_WIDTH//2 - 300, y - 8, 600, 44, DARK_GRAY, GRAY)
            self._label(label, GRAY, y + 6, SCREEN_WIDTH//2 - 280, 'small')
            vt = self.font_medium.render(value, True, col)
            self.screen.blit(vt, vt.get_rect(topright=(SCREEN_WIDTH//2 + 280, y + 4)))
            y += 56
        self._label("ESC = Zurück", GRAY, SCREEN_HEIGHT - 18, size='tiny')

    # ── Achievements ─────────────────────────────────────────────────────────
    def draw_achievements(self):
        self._title("Achievements", GOLD, 55)
        y = 130
        for key, ach in ACHIEVEMENTS.items():
            unlocked = key in self.stats.unlocked
            col    = GOLD if unlocked else DARK_GRAY
            border = GOLD if unlocked else GRAY
            self._box(80, y - 6, SCREEN_WIDTH - 160, 52, DARK_GRAY, border)
            icon_t = self.font_medium.render(ach['icon'], True, col)
            self.screen.blit(icon_t, (100, y + 5))
            name_col = WHITE if unlocked else GRAY
            self._label(ach['name'], name_col, y + 4,  150, 'small')
            self._label(ach['desc'], GRAY,     y + 28, 150, 'tiny')
            if unlocked:
                done = self.font_tiny.render("✓ Freigeschaltet", True, GREEN)
                self.screen.blit(done, done.get_rect(topright=(SCREEN_WIDTH - 90, y + 16)))
            y += 62
        count = len(self.stats.unlocked)
        total = len(ACHIEVEMENTS)
        self._label(f"{count}/{total} freigeschaltet", GOLD,
                    SCREEN_HEIGHT - 35, size='small')
        self._label("ESC = Zurück", GRAY, SCREEN_HEIGHT - 14, size='tiny')

    def _draw_achievement_popup(self, key):
        ach  = ACHIEVEMENTS.get(key)
        if not ach:
            return
        alpha = min(255, self.achievement_display_timer * 3)
        surf  = pygame.Surface((420, 70), pygame.SRCALPHA)
        surf.fill((20, 20, 20, min(220, alpha)))
        pygame.draw.rect(surf, GOLD, (0, 0, 420, 70), 2, border_radius=8)
        icon_t = self.font_medium.render(ach['icon'], True, GOLD)
        surf.blit(icon_t, (12, 18))
        n = self.font_small.render("Achievement: " + ach['name'], True, GOLD)
        surf.blit(n, (60, 10))
        d = self.font_tiny.render(ach['desc'], True, WHITE)
        surf.blit(d, (60, 38))
        self.screen.blit(surf, (SCREEN_WIDTH//2 - 210, 10))

    # ── Reset ─────────────────────────────────────────────────────────────────
    def reset_game(self):
        self.score1 = 0
        self.score2 = 0
        self.balls  = [Ball(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)]
        self.particles  = []
        self.powerups   = []
        self.powerup_timer = 0
        self.current_rally = 0
        self.max_rally_session = 0
        self.time_remaining = self.time_limit
        self.survival_lives   = 3
        self.survival_elapsed = 0
        self.paddle1.y = SCREEN_HEIGHT//2 - 50
        self.paddle2.y = SCREEN_HEIGHT//2 - 50
        self.paddle1.speed_multiplier = 1.0
        self.paddle2.speed_multiplier = 1.0
        self.paddle1.size_multiplier  = 1.0
        self.paddle2.size_multiplier  = 1.0
        self.paddle1.shield_active = False
        self.paddle2.shield_active = False
        self.paddle1.magnet_active = False
        self.paddle2.magnet_active = False
        self._apply_shop_bonuses()

    # ── Hauptschleife ─────────────────────────────────────────────────────────
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.stats.save()
        pygame.quit()
        sys.exit()

# ── Start ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()
