import pygame
import sys
import random
import math
import json

# ─── INIT ────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

CELL = 28
COLS, ROWS = 21, 21
W, H = COLS * CELL, ROWS * CELL + 80
FPS = 60

# ─── FARBEN ──────────────────────────────────────────────────────────────────
BLACK  = (0,   0,   0  )
YELLOW = (255, 220, 0  )
WHITE  = (255, 255, 255)
BLUE   = (33,  33,  222)
RED    = (255, 0,   0  )
PINK   = (255, 184, 255)
CYAN   = (0,   255, 255)
ORANGE = (255, 165, 0  )
GREEN  = (0,   200, 0  )
PURPLE = (180, 0,   255)
GRAY   = (120, 120, 120)
DKBLUE = (0,   0,   80 )
GOLD   = (255, 215, 0  )
LIME   = (0,   255, 128)
WALL_C = (33,  33,  180)

# ─── POWERUP-TYPEN ───────────────────────────────────────────────────────────
POWERUP_TYPES = {
    "speed":  {"color": LIME,   "symbol": "S", "duration": 8,  "desc": "SPEED BOOST"},
    "freeze": {"color": CYAN,   "symbol": "F", "duration": 6,  "desc": "FREEZE GHOSTS"},
    "magnet": {"color": GOLD,   "symbol": "M", "duration": 7,  "desc": "PELLET MAGNET"},
    "shield": {"color": WHITE,  "symbol": "X", "duration": 10, "desc": "SHIELD"},
    "double": {"color": ORANGE, "symbol": "2", "duration": 8,  "desc": "DOUBLE SCORE"},
    "life":   {"color": RED,    "symbol": "♥", "duration": 0,  "desc": "+1 LIFE"},
    "bomb":   {"color": GRAY,   "symbol": "B", "duration": 0,  "desc": "GHOST BOMB"},
}

# ─── GEISTER-TYPEN ───────────────────────────────────────────────────────────
GHOST_TYPES = [
    {"name": "Blinky", "color": RED,    "ai": "chase",   "speed_mul": 1.0},
    {"name": "Pinky",  "color": PINK,   "ai": "ambush",  "speed_mul": 0.95},
    {"name": "Inky",   "color": CYAN,   "ai": "random",  "speed_mul": 0.9},
    {"name": "Clyde",  "color": ORANGE, "ai": "scatter", "speed_mul": 0.85},
    {"name": "Shadow", "color": PURPLE, "ai": "chase",   "speed_mul": 1.1},
    {"name": "Speedy", "color": LIME,   "ai": "chase",   "speed_mul": 1.2},
]

# ─── LEVEL-MAPS (alle Zeilen exakt 21 Zeichen) ───────────────────────────────
LEVEL_MAPS = [
    # Level 1 – klassisch
    [
        "#####################",
        "#.........#.........#",
        "#.##.####.#.####.##.#",
        "#O##.####.#.####.##O#",
        "#.##.####.#.####.##.#",
        "#...................#",
        "#.##.#.#####.#.##..#",
        "#.##.#.#####.#.##..#",
        "#....#...#...#.....#",
        "#####.###.###.######",
        "#####.#     #.######",
        "#####.# ##=##.######",
        "#####.# #   #.######",
        "#####.#  G  #.######",
        "#####.# #####.######",
        "#####.#     #.######",
        "#####.#######.######",
        "#.........#.........#",
        "#.##.####.#.####.##.#",
        "#O..#...........#..O#",
        "#####################",
    ],
    # Level 2 – Labyrinth
    [
        "#####################",
        "#O.#.......#.......O#",
        "#.###.#####.#####.###",
        "#.....#.....#.....#.#",
        "#####.#.###.#.###.#.#",
        "#.....#.#...#...#.#.#",
        "#.#####.#.#####.#.###",
        "#.......#...#...#...#",
        "#.#####.###.#.###.#.#",
        "###...#.....#.....#.#",
        "###.#.#.##=##.#.###.#",
        "###.#.#.#   #.#.###.#",
        "###.#.# # G #.#.###.#",
        "###.#.# #####.#.###.#",
        "###.#.#       #.#####",
        "#...#.#########.#..O#",
        "#.###...........###.#",
        "#.#.###########.#.#.#",
        "#O..............#...#",
        "#.####.#####.####.###",
        "#####################",
    ],
    # Level 3 – offen
    [
        "#####################",
        "#O.................O#",
        "#.#######.#.#######.#",
        "#.#.......#.......#.#",
        "#.#.#####.#.#####.#.#",
        "#.#.#   #.#.#   #.#.#",
        "#.#.# G #.#.# G #.#.#",
        "#.#.#####.#.#####.#.#",
        "#.#.......#.......#.#",
        "#.#######.#.#######.#",
        "#...........#.......#",
        "#.#######.#.#######.#",
        "#.#.......#.......#.#",
        "#.#.####=###.#####.#.#",
        "#.#.#         #.#.##",
        "#.#.###########.#.#.#",
        "#.#.............#.#.#",
        "#.###############.#.#",
        "#O.................O#",
        "#................####",
        "#####################",
    ],
    # Level 4 – Spirale
    [
        "#####################",
        "#O.................O#",
        "#.###############.#.#",
        "#.#.............#.#.#",
        "#.#.###########.#.#.#",
        "#.#.#.........#.#.#.#",
        "#.#.#.#######.#.#.#.#",
        "#.#.#.#.....#.#.#.#.#",
        "#.#.#.# ##=##.#.#.#.#",
        "#.#.#.# #   #.#.#.#.#",
        "#.#.#.# # G #.#.#.#.#",
        "#.#.#.# #   #.#.#.#.#",
        "#.#.#.# #####.#.#.#.#",
        "#.#.#.#.......#.#.#.#",
        "#.#.#.#########.#.#.#",
        "#.#.#...........#.#.#",
        "#.#.#############.#.#",
        "#.#...............#.#",
        "#.#################.#",
        "#O.................O#",
        "#####################",
    ],
    # Level 5 – Kreuz
    [
        "#####################",
        "#O.....#.....#.....O#",
        "#.#####.#####.#####.#",
        "#.......#...#.......#",
        "#.#####.#.#.#.#####.#",
        "#.#...#...#...#...#.#",
        "#.#.###########.###.#",
        "#.#.#.........#.#...#",
        "#.#.#.#######.#.#.###",
        "#...#.# ##=##.#.#...#",
        "#####.# # G #.#.#####",
        "#...#.# #####.#.#...#",
        "#.#.#.#.......#.#.###",
        "#.#.#.#########.#.###",
        "#.#...#.........#...#",
        "#.#.###############.#",
        "#.#.#.............#.#",
        "#.....#.#.#.#.#.....#",
        "#.#####.#.#.#.#####.#",
        "#O.................O#",
        "#####################",
    ],
]


# ─── KLASSEN ─────────────────────────────────────────────────────────────────

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self._make_sounds()

    def _tone(self, freq, dur, vol=0.4):
        sr = 22050
        n  = int(sr * dur / 1000)
        import array as arr
        data = arr.array('h', [
            int(vol * 32767 * math.sin(2 * math.pi * freq * i / sr))
            for i in range(n)
        ])
        return pygame.sndarray.make_sound(data)

    def _make_sounds(self):
        try:
            self.sounds["eat"]   = self._tone(600,  30, 0.3)
            self.sounds["power"] = self._tone(300,  80, 0.5)
            self.sounds["ghost"] = self._tone(200, 120, 0.6)
            self.sounds["die"]   = self._tone(150, 300, 0.7)
            self.sounds["bonus"] = self._tone(900,  60, 0.4)
            self.sounds["level"] = self._tone(700, 200, 0.5)
        except Exception:
            pass

    def play(self, name):
        if name in self.sounds:
            try: self.sounds[name].play()
            except: pass


class Particle:
    def __init__(self, x, y, color, text=""):
        self.x, self.y = x, y
        self.color = color
        self.text  = text
        self.vy    = -2 - random.random() * 2
        self.vx    = random.uniform(-1, 1)
        self.life  = 40
        self.alpha = 255

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.1
        self.life -= 1
        self.alpha = int(255 * self.life / 40)

    def draw(self, surf, font):
        if self.text:
            s = font.render(self.text, True, self.color)
            s.set_alpha(self.alpha)
            surf.blit(s, (int(self.x), int(self.y)))
        else:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), 3)


class Map:
    def __init__(self, raw, level_num):
        self.level_num = level_num
        self.grid = []
        self.dots   = set()
        self.powers = set()
        self.special_powers = {}
        self.ghost_home = (10, 13)
        self.ghost_door = (10, 11)
        self._parse(raw)

    def _parse(self, raw):
        for r, row in enumerate(raw):
            # Zeilen auf exakt COLS Zeichen normieren
            row = row.ljust(COLS)[:COLS]
            line = []
            for c, ch in enumerate(row):
                if ch == '#':
                    line.append(1)
                elif ch == '.':
                    line.append(0)
                    self.dots.add((c, r))
                elif ch == 'O':
                    line.append(0)
                    self.powers.add((c, r))
                elif ch == '=':
                    line.append(2)   # Geister-Tür
                elif ch == 'G':
                    line.append(0)
                    self.ghost_home = (c, r)
                else:
                    line.append(0)
            self.grid.append(line)

        # Zufällige Extra-PowerUps platzieren
        empties = [
            (c, r)
            for r in range(len(self.grid))
            for c in range(len(self.grid[r]))
            if self.grid[r][c] == 0
            and (c, r) not in self.dots
            and (c, r) not in self.powers
        ]
        random.shuffle(empties)
        types = list(POWERUP_TYPES.keys())
        for pos in empties[:3 + self.level_num]:
            self.special_powers[pos] = random.choice(types)

    def walkable(self, c, r):
        # Tunnel-Wrap
        c = c % COLS
        if r < 0 or r >= ROWS:
            return False
        cell = self.grid[r][c]
        return cell == 0 or cell == 2   # BUG-FIX: Geister-Tür (=) als begehbar

    def walkable_pac(self, c, r):
        """Pac-Man darf NICHT durch die Geister-Tür."""
        c = c % COLS
        if r < 0 or r >= ROWS:
            return False
        return self.grid[r][c] == 0

    def draw(self, surf):
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                rx, ry = c * CELL, r * CELL
                if cell == 1:
                    pygame.draw.rect(surf, WALL_C,
                                     (rx+1, ry+1, CELL-2, CELL-2), border_radius=4)
                    pygame.draw.rect(surf, BLUE,
                                     (rx+1, ry+1, CELL-2, CELL-2), 2, border_radius=4)
                elif cell == 2:
                    pygame.draw.rect(surf, PINK,
                                     (rx+4, ry+CELL//2-2, CELL-8, 4))

        # Punkte
        for (c, r) in self.dots:
            cx, cy = c*CELL + CELL//2, r*CELL + CELL//2
            pygame.draw.circle(surf, WHITE, (cx, cy), 3)

        # Power-Pills
        t = pygame.time.get_ticks()
        pulse = int(abs(math.sin(t / 300)) * 4)
        for (c, r) in self.powers:
            cx, cy = c*CELL + CELL//2, r*CELL + CELL//2
            pygame.draw.circle(surf, GOLD,   (cx, cy), 7 + pulse)
            pygame.draw.circle(surf, YELLOW, (cx, cy), 5 + pulse)

        # Spezial-PowerUps
        fnt = pygame.font.SysFont("consolas", 12, bold=True)
        for (c, r), tp in self.special_powers.items():
            cx, cy = c*CELL + CELL//2, r*CELL + CELL//2
            col = POWERUP_TYPES[tp]["color"]
            sym = POWERUP_TYPES[tp]["symbol"]
            pygame.draw.circle(surf, col, (cx, cy), 8)
            txt = fnt.render(sym, True, BLACK)
            surf.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))


# ─── PAC-MAN ─────────────────────────────────────────────────────────────────
# BUG-FIX: Komplette Neuimplementierung der Bewegungslogik.
# Problem war: px/py wurden nie sauber auf CELL-Grenzen ausgerichtet,
# weshalb centered_x/y niemals True war und die Richtung nie wechseln konnte.

class PacMan:
    SPEED = 2   # Pixel pro Frame (Teiler von CELL=28 → 14 Frames pro Zelle)

    def __init__(self, x, y):
        self.cx, self.cy   = x, y
        self.px, self.py   = x * CELL, y * CELL
        self.dx, self.dy   = 0, 0
        self.next_dx, self.next_dy = 0, 0
        self.mouth     = 0
        self.mouth_dir = 1
        self.alive     = True
        self.effects   = {}
        self.flash     = 0

    def set_dir(self, dx, dy):
        self.next_dx = dx
        self.next_dy = dy

    def update(self, gmap):
        if not self.alive:
            return

        spd = self.SPEED * 2 if "speed" in self.effects else self.SPEED

        # Effekte herunterzählen
        self.effects = {k: v - 1 for k, v in self.effects.items() if v > 1}
        self.flash   = max(0, self.flash - 1)

        # Mund-Animation
        self.mouth += 5 * self.mouth_dir
        if self.mouth >= 40: self.mouth_dir = -1
        if self.mouth <= 0:  self.mouth_dir =  1

        # ── Schritt für Schritt bewegen ──────────────────────────────────
        # Bewege spd Pixel, prüfe bei jeder Gittergrenze ob Richtung wechselbar
        for _ in range(spd):
            self._step(gmap)

    def _step(self, gmap):
        """Bewegt Pac-Man genau 1 Pixel und wechselt Richtung an Gittergrenzen."""
        # Sind wir exakt auf einer Gittergrenze?
        on_x = (self.px % CELL) == 0
        on_y = (self.py % CELL) == 0

        if on_x and on_y:
            # Gitterposition aus Pixelposition berechnen
            self.cx = (self.px // CELL) % COLS
            self.cy =  self.py // CELL

            # Gewünschte neue Richtung testen
            nx = (self.cx + self.next_dx) % COLS
            ny =  self.cy + self.next_dy
            if gmap.walkable_pac(nx, ny):
                self.dx, self.dy = self.next_dx, self.next_dy

            # Aktuelle Richtung prüfen
            nx = (self.cx + self.dx) % COLS
            ny =  self.cy + self.dy
            if not gmap.walkable_pac(nx, ny):
                self.dx, self.dy = 0, 0

        # 1 Pixel in aktuelle Richtung bewegen
        new_px = self.px + self.dx
        new_py = self.py + self.dy

        # Tunnel-Wrap
        new_px = new_px % (COLS * CELL)

        self.px = new_px
        self.py = new_py

        # Gitterposition synchron halten
        self.cx = (self.px // CELL) % COLS
        self.cy =  self.py // CELL

    def draw(self, surf):
        cx = self.px + CELL // 2
        cy = self.py + CELL // 2
        r  = CELL // 2 - 2

        if self.flash > 0 and self.flash % 4 < 2:
            col = WHITE
        elif "shield" in self.effects:
            col = CYAN
        else:
            col = YELLOW

        if self.dx == 0 and self.dy == 0:
            pygame.draw.circle(surf, col, (cx, cy), r)
        else:
            angle = math.atan2(-self.dy, self.dx)
            deg   = math.degrees(angle)
            mo    = self.mouth
            start = math.radians(deg + mo / 2)
            end   = math.radians(deg - mo / 2)
            pts = [(cx, cy)]
            steps = max(1, (360 - mo) // 10)
            for i in range(steps + 1):
                a = start - i * (2 * math.pi - math.radians(mo)) / steps
                pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
            if len(pts) >= 3:
                pygame.draw.polygon(surf, col, pts)

        # Effekt-Indikatoren
        x_off = -r - 4
        for name, col_e in [("speed", LIME), ("shield", CYAN),
                             ("double", ORANGE), ("freeze", CYAN),
                             ("magnet", GOLD)]:
            if name in self.effects:
                pygame.draw.circle(surf, col_e, (cx + x_off, cy - r - 2), 3)
                x_off += 7


# ─── GHOST ───────────────────────────────────────────────────────────────────
# BUG-FIX: Geister hatten dieselben Pixelpositions-Probleme wie Pac-Man.
# Außerdem wurde speed falsch aus difficulty berechnet und nie korrekt gesetzt.

class Ghost:
    def __init__(self, gtype, home_x, home_y, difficulty):
        self.gtype    = gtype
        self.name     = gtype["name"]
        self.color    = gtype["color"]
        self.ai       = gtype["ai"]
        self.home_x   = home_x
        self.home_y   = home_y
        self.cx, self.cy = home_x, home_y
        self.px, self.py = home_x * CELL, home_y * CELL
        # Startrichtung: nach oben
        self.dx, self.dy = 0, -1
        self.difficulty  = difficulty
        # Basisgeschwindigkeit in Pixel/Frame
        self.base_speed  = max(1, round(difficulty * gtype["speed_mul"]))
        self.speed       = self.base_speed
        self.frightened  = 0
        self.eaten       = False
        self.scatter_x   = random.choice([0, COLS - 1])
        self.scatter_y   = random.choice([0, ROWS - 1])
        self.mode_timer  = 0
        self.mode        = "scatter"
        self.release_timer = random.randint(60, 180)
        self.released    = False

    def frighten(self, dur):
        if not self.eaten:
            self.frightened = dur
            # Richtung umkehren
            self.dx, self.dy = -self.dx, -self.dy

    def reset(self):
        self.cx, self.cy = self.home_x, self.home_y
        self.px, self.py = self.home_x * CELL, self.home_y * CELL
        self.dx, self.dy = 0, -1
        self.frightened  = 0
        self.eaten       = False
        self.released    = False
        self.release_timer = random.randint(60, 180)
        self.speed       = self.base_speed

    def _choose_dir(self, gmap, pac_cx, pac_cy, pac_dx, pac_dy):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rev  = (-self.dx, -self.dy)
        # Nicht rückwärts (außer es gibt keine andere Wahl)
        choices = [d for d in dirs if d != rev]

        if self.frightened:
            valid = [d for d in choices
                     if gmap.walkable((self.cx + d[0]) % COLS, self.cy + d[1])]
            return random.choice(valid) if valid else random.choice(dirs)

        # Ziel bestimmen
        if self.mode == "scatter":
            tx, ty = self.scatter_x, self.scatter_y
        elif self.ai == "chase":
            tx, ty = pac_cx, pac_cy
        elif self.ai == "ambush":
            tx = pac_cx + pac_dx * 4
            ty = pac_cy + pac_dy * 4
        elif self.ai == "random":
            valid = [d for d in choices
                     if gmap.walkable((self.cx + d[0]) % COLS, self.cy + d[1])]
            return random.choice(valid) if valid else random.choice(dirs)
        else:  # scatter-ai (Clyde)
            if abs(self.cx - pac_cx) + abs(self.cy - pac_cy) > 8:
                tx, ty = pac_cx, pac_cy
            else:
                tx, ty = self.scatter_x, self.scatter_y

        best, best_d = None, float('inf')
        for d in choices:
            nx = (self.cx + d[0]) % COLS
            ny =  self.cy + d[1]
            if gmap.walkable(nx, ny):
                dist = (nx - tx) ** 2 + (ny - ty) ** 2
                if dist < best_d:
                    best_d, best = dist, d

        if best:
            return best
        # Notfall: irgendeine gültige Richtung
        valid = [d for d in dirs
                 if gmap.walkable((self.cx + d[0]) % COLS, self.cy + d[1])]
        return random.choice(valid) if valid else (0, 0)

    def update(self, gmap, pac_cx, pac_cy, pac_dx, pac_dy, frozen):
        if frozen and not self.eaten:
            return

        # Release-Timer
        if not self.released:
            self.release_timer -= 1
            if self.release_timer <= 0:
                self.released = True
                door_x, door_y = gmap.ghost_door
                self.cx, self.cy = door_x, door_y
                self.px, self.py = door_x * CELL, door_y * CELL
                self.dx, self.dy = 0, -1
            return

        # Geschwindigkeit setzen
        if self.eaten:
            self.speed = 3
        elif self.frightened:
            self.speed = max(1, self.base_speed - 1)
        else:
            self.speed = self.base_speed

        if self.frightened > 0:
            self.frightened -= 1

        # Modus wechseln
        self.mode_timer += 1
        if   self.mode_timer < 300: self.mode = "scatter"
        elif self.mode_timer < 600: self.mode = "chase"
        elif self.mode_timer < 750: self.mode = "scatter"
        else:                        self.mode = "chase"
        if self.mode_timer > 800:
            self.mode_timer = 300

        # Bewegung: spd Pixel pro Frame
        for _ in range(self.speed):
            self._step(gmap, pac_cx, pac_cy, pac_dx, pac_dy)

        # Heimgekehrt nach "eaten"?
        if self.eaten and self.cx == self.home_x and self.cy == self.home_y:
            self.eaten      = False
            self.frightened = 0
            self.speed      = self.base_speed

    def _step(self, gmap, pac_cx, pac_cy, pac_dx, pac_dy):
        """1-Pixel-Schritt mit Richtungsentscheidung an Gittergrenzen."""
        on_x = (self.px % CELL) == 0
        on_y = (self.py % CELL) == 0

        if on_x and on_y:
            self.cx = (self.px // CELL) % COLS
            self.cy =  self.py // CELL

            # Neue Richtung wählen
            d = self._choose_dir(gmap, pac_cx, pac_cy, pac_dx, pac_dy)
            if d:
                self.dx, self.dy = d

        new_px = self.px + self.dx
        new_py = self.py + self.dy

        nc = (new_px // CELL) % COLS
        nr =  new_py // CELL

        if gmap.walkable(nc, nr):
            self.px = new_px % (COLS * CELL)
            self.py = new_py
        else:
            # An Wand: sofort neue Richtung suchen
            self.dx, self.dy = 0, 0

        self.cx = (self.px // CELL) % COLS
        self.cy =  self.py // CELL

    def draw(self, surf):
        if not self.released:
            return
        cx = self.px + CELL // 2
        cy = self.py + CELL // 2
        r  = CELL // 2 - 2

        if self.eaten:
            fnt = pygame.font.SysFont("consolas", 16)
            txt = fnt.render("^^", True, WHITE)
            surf.blit(txt, (cx - 8, cy - 8))
            return

        if self.frightened:
            t   = pygame.time.get_ticks()
            col = BLUE if self.frightened > 60 or (t // 200) % 2 == 0 else WHITE
        else:
            col = self.color

        # Körper (Halbkreis + Rechteck + Zacken)
        pygame.draw.ellipse(surf, col, (cx - r, cy - r, r * 2, r * 2))
        pygame.draw.rect(surf, col, (cx - r, cy, r * 2, r))

        # Unterer Rand gezackt
        steps = 4
        w_each = (r * 2) // steps
        for i in range(steps):
            bx = cx - r + i * w_each
            by = cy + r
            ty2 = cy + r // 2 if i % 2 == 0 else cy + r
            pygame.draw.polygon(surf, col, [
                (bx, cy),
                (bx + w_each, cy),
                (bx + w_each, ty2),
                (bx, by),
            ])

        # Augen
        ex  = cx - r // 3
        ey  = cy - r // 4
        er  = max(2, r // 4)
        pygame.draw.circle(surf, WHITE, (ex,          ey), er)
        pygame.draw.circle(surf, WHITE, (ex + r // 2, ey), er)
        if not self.frightened:
            pygame.draw.circle(surf, DKBLUE,
                               (ex + self.dx * 2,          ey + self.dy * 2), max(1, er // 2))
            pygame.draw.circle(surf, DKBLUE,
                               (ex + r // 2 + self.dx * 2, ey + self.dy * 2), max(1, er // 2))


# ─── HAUPTSPIEL ──────────────────────────────────────────────────────────────

class Game:
    DIFFICULTIES = {
        "Einfach":  {"ghost_count": 2, "ghost_speed": 1, "power_dur": 600, "extra_lives": 2},
        "Normal":   {"ghost_count": 3, "ghost_speed": 2, "power_dur": 400, "extra_lives": 1},
        "Schwer":   {"ghost_count": 4, "ghost_speed": 2, "power_dur": 250, "extra_lives": 0},
        "Wahnsinn": {"ghost_count": 5, "ghost_speed": 3, "power_dur": 150, "extra_lives": 0},
    }

    def __init__(self):
        self.screen  = pygame.display.set_mode((W, H))
        pygame.display.set_caption("PAC-MAN DELUXE")
        # BUG-FIX: self.clock war als Font initialisiert – korrigiert
        self.clock   = pygame.time.Clock()
        self.font_s  = pygame.font.SysFont("consolas", 14, bold=True)
        self.font_m  = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_l  = pygame.font.SysFont("consolas", 38, bold=True)
        self.font_xl = pygame.font.SysFont("consolas", 52, bold=True)
        self.snd     = SoundManager()
        self.state   = "menu"
        self.score   = 0
        self.hi_score = self._load_hi()
        self.lives   = 3
        self.level   = 0
        self.diff_name = "Normal"
        self.diff    = self.DIFFICULTIES[self.diff_name]
        self.particles  = []
        self.ghost_combo = 0
        self.total_dots  = 0
        self.freeze_timer = 0
        self.tick    = 0
        # Dummy-Objekte damit draw() vor start_game() nicht crasht
        self.map     = None
        self.pac     = None
        self.ghosts  = []

    # ── Highscore ────────────────────────────────────────────────────────
    def _load_hi(self):
        try:
            with open("pacman_hi.json") as f:
                return json.load(f).get("hi", 0)
        except:
            return 0

    def _save_hi(self):
        try:
            with open("pacman_hi.json", "w") as f:
                json.dump({"hi": self.hi_score}, f)
        except:
            pass

    # ── Level laden ──────────────────────────────────────────────────────
    def _load_level(self):
        idx = self.level % len(LEVEL_MAPS)
        raw = LEVEL_MAPS[idx]
        self.map = Map(raw, self.level)
        self.total_dots = len(self.map.dots) + len(self.map.powers)

        hx, hy = self.map.ghost_home
        # Pac-Man startet 3 Felder unterhalb des Geister-Hauses
        pac_y = min(hy + 3, ROWS - 2)
        self.pac = PacMan(hx, pac_y)

        spd      = self.diff["ghost_speed"]
        g_count  = min(self.diff["ghost_count"] + self.level // 2, len(GHOST_TYPES))
        types    = random.sample(GHOST_TYPES, g_count)
        self.ghosts = [
            Ghost(t, hx + random.randint(-1, 1), hy, spd)
            for t in types
        ]
        self.freeze_timer = 0
        self.ghost_combo  = 0

    # ── Spiel starten ────────────────────────────────────────────────────
    def start_game(self):
        self.score = 0
        self.lives = 3 + self.diff["extra_lives"]
        self.level = 0
        self.particles = []
        self._load_level()
        self.state = "playing"

    # ── Zeichnen ─────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BLACK)
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "diff":
            self._draw_diff()
        elif self.state in ("playing", "paused", "dead"):
            if self.map:
                self.map.draw(self.screen)
            if self.pac:
                self.pac.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self._draw_particles()
            self._draw_hud()
            if self.state == "paused":
                self._draw_overlay("PAUSE", YELLOW)
            if self.state == "dead":
                self._draw_overlay("VERLOREN!", RED)
        elif self.state == "win":
            if self.map:
                self.map.draw(self.screen)
            self._draw_overlay("LEVEL GESCHAFFT!", GREEN)
        elif self.state == "gameover":
            self._draw_gameover()
        pygame.display.flip()

    def _draw_menu(self):
        t = pygame.time.get_ticks() / 1000
        for i in range(15):
            x = int(W/2 + math.cos(t + i * 0.4) * 200)
            y = int(H/2 + math.sin(t * 0.7 + i * 0.5) * 120)
            col = [(255,220,0),(255,100,100),(100,200,255),(255,150,255)][i % 4]
            pygame.draw.circle(self.screen, col, (x, y), 6)

        title = self.font_xl.render("PAC-MAN", True, YELLOW)
        sub   = self.font_m.render("D E L U X E", True, GOLD)
        self.screen.blit(title, (W//2 - title.get_width()//2, 80))
        self.screen.blit(sub,   (W//2 - sub.get_width()//2,   150))

        opts = [
            ("ENTER  – Neues Spiel",    WHITE),
            ("D      – Schwierigkeit",  CYAN),
            ("ESC    – Beenden",        GRAY),
        ]
        for i, (txt, col) in enumerate(opts):
            s = self.font_m.render(txt, True, col)
            self.screen.blit(s, (W//2 - s.get_width()//2, 250 + i * 50))

        hi   = self.font_s.render(f"HIGHSCORE: {self.hi_score}", True, GOLD)
        diff = self.font_s.render(f"Schwierigkeit: {self.diff_name}", True, ORANGE)
        self.screen.blit(hi,   (W//2 - hi.get_width()//2,   H - 60))
        self.screen.blit(diff, (W//2 - diff.get_width()//2, H - 35))

    def _draw_diff(self):
        t = self.font_l.render("SCHWIERIGKEIT", True, YELLOW)
        self.screen.blit(t, (W//2 - t.get_width()//2, 60))
        names = list(self.DIFFICULTIES.keys())
        for i, name in enumerate(names):
            col  = GOLD if name == self.diff_name else WHITE
            d    = self.DIFFICULTIES[name]
            line = f"[{i+1}] {name:12s}  Geister:{d['ghost_count']}  Leben:+{d['extra_lives']}"
            s    = self.font_m.render(line, True, col)
            self.screen.blit(s, (W//2 - s.get_width()//2, 180 + i * 70))
        back = self.font_s.render("BACKSPACE – zurück", True, GRAY)
        self.screen.blit(back, (W//2 - back.get_width()//2, H - 50))

    def _draw_hud(self):
        y0 = ROWS * CELL + 4
        sc = self.font_m.render(f"SCORE {self.score}", True, YELLOW)
        self.screen.blit(sc, (10, y0))
        hi = self.font_s.render(f"HI {self.hi_score}", True, GOLD)
        self.screen.blit(hi, (W//2 - hi.get_width()//2, y0 + 4))
        for i in range(self.lives):
            pygame.draw.circle(self.screen, YELLOW, (W - 20 - i * 24, y0 + 12), 8)
        lv = self.font_s.render(f"LVL {self.level+1}  {self.diff_name}", True, CYAN)
        self.screen.blit(lv, (10, y0 + 28))

        # Aktive Effekte
        ex = W - 10
        for name, frames in self.pac.effects.items():
            info  = POWERUP_TYPES.get(name, {})
            col   = info.get("color", WHITE)
            desc  = info.get("desc", name.upper())
            dur_f = info.get("duration", 1) * FPS
            bar_w = int(50 * frames / max(1, dur_f))
            ex   -= 60
            pygame.draw.rect(self.screen, col, (ex, y0 + 28, bar_w, 8))
            t2 = self.font_s.render(desc[:4], True, col)
            self.screen.blit(t2, (ex, y0 + 16))

        # Fortschrittsbalken
        if self.map:
            eaten = self.total_dots - len(self.map.dots) - len(self.map.powers)
            pct   = eaten / max(1, self.total_dots)
            pygame.draw.rect(self.screen, GRAY,  (0, ROWS * CELL, W, 4))
            pygame.draw.rect(self.screen, GREEN, (0, ROWS * CELL, int(W * pct), 4))

    def _draw_overlay(self, text, color):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 140))
        self.screen.blit(s, (0, 0))
        t = self.font_l.render(text, True, color)
        self.screen.blit(t, (W//2 - t.get_width()//2, H//2 - 40))
        hint = self.font_m.render("ENTER – weiter  |  ESC – Menü", True, WHITE)
        self.screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 30))

    def _draw_gameover(self):
        t = self.font_xl.render("GAME OVER", True, RED)
        self.screen.blit(t, (W//2 - t.get_width()//2, 120))
        sc = self.font_l.render(f"Score: {self.score}", True, YELLOW)
        self.screen.blit(sc, (W//2 - sc.get_width()//2, 220))
        if self.score >= self.hi_score and self.score > 0:
            hi = self.font_m.render("NEUER HIGHSCORE!", True, GOLD)
            self.screen.blit(hi, (W//2 - hi.get_width()//2, 300))
        hint = self.font_m.render("ENTER – Menü  |  R – Neustart", True, WHITE)
        self.screen.blit(hint, (W//2 - hint.get_width()//2, 380))

    def _draw_particles(self):
        for p in self.particles:
            p.draw(self.screen, self.font_s)

    # ── Update ────────────────────────────────────────────────────────────
    def update(self):
        if self.state != "playing":
            return
        self.tick += 1

        frozen = self.freeze_timer > 0
        if frozen:
            self.freeze_timer -= 1

        if self.pac:
            self.pac.update(self.map)

        for g in self.ghosts:
            g.update(self.map,
                     self.pac.cx, self.pac.cy,
                     self.pac.dx, self.pac.dy,
                     frozen)

        self._check_dots()
        self._check_ghosts()
        self._check_win()
        self._update_particles()

    def _check_dots(self):
        if not self.pac or not self.map:
            return
        pos = (self.pac.cx, self.pac.cy)

        check = {pos}
        if "magnet" in self.pac.effects:
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    check.add(((pos[0] + dx) % COLS, pos[1] + dy))

        for p in list(check):
            if p in self.map.dots:
                self.map.dots.discard(p)
                pts = 20 if "double" in self.pac.effects else 10
                self.score += pts
                self.snd.play("eat")
                self._spawn_text(p[0]*CELL, p[1]*CELL, f"+{pts}", WHITE)

            if p in self.map.powers:
                self.map.powers.discard(p)
                dur = self.diff["power_dur"]
                for g in self.ghosts:
                    g.frighten(dur)
                self.ghost_combo = 0
                self.snd.play("power")
                pts = 100 if "double" in self.pac.effects else 50
                self.score += pts
                self._spawn_text(pos[0]*CELL, pos[1]*CELL, "POWER!", GOLD)

            if p in self.map.special_powers:
                tp = self.map.special_powers.pop(p)
                self._apply_powerup(tp)

    def _apply_powerup(self, tp):
        info = POWERUP_TYPES[tp]
        self.snd.play("bonus")
        self._spawn_text(self.pac.cx*CELL, self.pac.cy*CELL, info["desc"], info["color"])
        if tp == "life":
            self.lives += 1
        elif tp == "bomb":
            for g in self.ghosts:
                g.frighten(200)
                g.eaten = True
            self.score += 500
        elif tp == "freeze":
            self.freeze_timer = info["duration"] * FPS
        else:
            self.pac.effects[tp] = info["duration"] * FPS

    def _check_ghosts(self):
        if not self.pac:
            return
        for g in self.ghosts:
            if not g.released or g.eaten:
                continue
            if abs(g.px - self.pac.px) < CELL - 4 and abs(g.py - self.pac.py) < CELL - 4:
                if "shield" in self.pac.effects:
                    del self.pac.effects["shield"]
                    self.pac.flash = 40
                    g.frighten(200)
                    self._spawn_text(self.pac.cx*CELL, self.pac.cy*CELL, "SHIELD!", CYAN)
                elif g.frightened:
                    g.eaten = True
                    self.ghost_combo += 1
                    pts = 200 * (2 ** min(self.ghost_combo - 1, 6))
                    if "double" in self.pac.effects:
                        pts *= 2
                    self.score += pts
                    self.snd.play("ghost")
                    self._spawn_text(g.px, g.py, f"+{pts}", ORANGE)
                else:
                    self._die()
                    return

    def _die(self):
        self.snd.play("die")
        self.lives -= 1
        if self.lives <= 0:
            self.score = max(self.score, 0)
            if self.score > self.hi_score:
                self.hi_score = self.score
                self._save_hi()
            self.state = "gameover"
        else:
            self.state = "dead"

    def _check_win(self):
        if self.map and not self.map.dots and not self.map.powers:
            self.snd.play("level")
            self.score += 500 * (self.level + 1)
            self.level += 1
            self.state = "win"

    def _spawn_text(self, x, y, text, color):
        self.particles.append(Particle(x, y, color, text))

    def _update_particles(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    # ── Events ────────────────────────────────────────────────────────────
    def handle_event(self, ev):
        if ev.type == pygame.QUIT:
            self._save_hi()
            pygame.quit()
            sys.exit()

        if ev.type == pygame.KEYDOWN:
            k = ev.key

            if k == pygame.K_ESCAPE:
                if self.state in ("playing", "paused", "dead", "win", "gameover"):
                    self.state = "menu"
                elif self.state == "menu":
                    self._save_hi()
                    pygame.quit()
                    sys.exit()

            if self.state == "menu":
                if k == pygame.K_RETURN: self.start_game()
                if k == pygame.K_d:      self.state = "diff"

            elif self.state == "diff":
                names = list(self.DIFFICULTIES.keys())
                key_map = {
                    pygame.K_1: 0, pygame.K_2: 1,
                    pygame.K_3: 2, pygame.K_4: 3,
                }
                if k in key_map:
                    idx = key_map[k]
                    if idx < len(names):
                        self.diff_name = names[idx]
                        self.diff      = self.DIFFICULTIES[self.diff_name]
                if k == pygame.K_BACKSPACE:
                    self.state = "menu"

            elif self.state == "playing":
                if k in (pygame.K_LEFT,  pygame.K_a): self.pac.set_dir(-1,  0)
                if k in (pygame.K_RIGHT, pygame.K_d): self.pac.set_dir( 1,  0)
                if k in (pygame.K_UP,    pygame.K_w): self.pac.set_dir( 0, -1)
                if k in (pygame.K_DOWN,  pygame.K_s): self.pac.set_dir( 0,  1)
                if k in (pygame.K_p, pygame.K_PAUSE): self.state = "paused"

            elif self.state == "paused":
                if k in (pygame.K_p, pygame.K_RETURN): self.state = "playing"

            elif self.state == "dead":
                if k == pygame.K_RETURN:
                    self._load_level()
                    self.state = "playing"

            elif self.state == "win":
                if k == pygame.K_RETURN:
                    self._load_level()
                    self.state = "playing"

            elif self.state == "gameover":
                if k == pygame.K_RETURN: self.state = "menu"
                if k == pygame.K_r:      self.start_game()

    # ── Hauptschleife ────────────────────────────────────────────────────
    def run(self):
        while True:
            for ev in pygame.event.get():
                self.handle_event(ev)
            self.update()
            self.draw()
            self.clock.tick(FPS)   # BUG-FIX: war nie aufgerufen, da clock falsch war


# ─── START ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()
