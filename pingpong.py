import pygame
import sys

# Initialisieren von Pygame
pygame.init()

# Konstanten
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 10
PADDLE_SPEED = 6
BALL_SPEED = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Einrichten des Spielbildschirms
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Spiel")
clock = pygame.time.Clock()

# Paddle-Klasse
class Paddle:
    def __init__(self, x, y, is_cpu=False):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
        self.is_cpu = is_cpu

    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= self.speed

    def move_down(self):
        if self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def update_cpu(self, ball):
        if self.is_cpu:
            if ball.rect.centery < self.rect.centery - 10:
                self.move_up()
            elif ball.rect.centery > self.rect.centery + 10:
                self.move_down()

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
        
# Ball-Klasse
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE,BALL_SIZE)
        self.speed_x = BALL_SPEED
        self.speed_y = BALL_SPEED
        
    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Abprallen an den oberen und unteren Wänden
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y = -self.speed_y
        
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
        
    def reset(self):
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.speed_x = BALL_SPEED
        self.speed_y = BALL_SPEED
        
# Initialisieren von den Spielobjekten
player1 = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
player2 = Paddle(WIDTH - 40, HEIGHT // 2 - PADDLE_HEIGHT // 2, is_cpu=True)
ball = Ball()

# Spielstand
score1 = 0
score2 = 0
font = pygame.font.Font(None, 74)