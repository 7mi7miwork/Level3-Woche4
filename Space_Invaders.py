"""
Raumschiff-Test  –  nur Spieler, keine Gegner
Steuerung: ← → oder A D  |  ESC beenden
"""

import pygame, sys

pygame.init()

SW, SH = 800, 600
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Raumschiff Test")
clock  = pygame.time.Clock()
fnt    = pygame.font.SysFont("monospace", 18)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
CYAN  = (0, 220, 255)
GRAY  = (70, 70, 70)

# ── Spieler ───────────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    SPEED = 5

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        # Rumpf (Dreieck)
        pygame.draw.polygon(self.image, GREEN, [(20, 0), (0, 30), (40, 30)])
        # Kanone
        pygame.draw.rect(self.image, WHITE, (17, 0, 6, 16))
        self.rect = self.image.get_rect(centerx=SW // 2, bottom=SH - 20)

    def update(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += self.SPEED
        self.rect.clamp_ip(screen.get_rect())   # nicht aus dem Fenster fahren

# ── Projektil ─────────────────────────────────────────────────────────────────
class Bullet(pygame.sprite.Sprite):
    SPEED = 8

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 14))
        self.image.fill(CYAN)
        self.rect  = self.image.get_rect(centerx=x, bottom=y)

    def update(self):
        self.rect.y -= self.SPEED
        if self.rect.bottom < 0:
            self.kill()

# ── Hauptschleife ─────────────────────────────────────────────────────────────
player  = Player()
bullets = pygame.sprite.Group()
all_spr = pygame.sprite.Group(player)

while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.key == pygame.K_SPACE:
                if len(bullets) == 0:          # nur 1 Schuss gleichzeitig
                    b = Bullet(player.rect.centerx, player.rect.top)
                    bullets.add(b)
                    all_spr.add(b)

    keys = pygame.key.get_pressed()
    player.update(keys)
    bullets.update()

    screen.fill(BLACK)
    all_spr.draw(screen)

    # Debug-Info
    screen.blit(fnt.render(f"x={player.rect.x}  Schüsse={len(bullets)}", True, GRAY), (10, 10))
    screen.blit(fnt.render("← → Bewegen  |  SPACE Schießen  |  ESC Beenden", True, GRAY), (10, SH - 28))

    pygame.display.flip()
