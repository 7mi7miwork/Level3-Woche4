import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 10
PADDLE_SPEED = 6
BALL_SPEED = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")
clock = pygame.time.Clock()

# Paddle class
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

# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
        self.speed_x = BALL_SPEED
        self.speed_y = BALL_SPEED

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off top and bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y = -self.speed_y

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

    def reset(self):
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.speed_x = BALL_SPEED
        self.speed_y = BALL_SPEED

# Initialize game objects
player1 = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2)
player2 = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, is_cpu=True)
ball = Ball()

# Scores
score1 = 0
score2 = 0
font = pygame.font.Font(None, 74)

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key states
    keys = pygame.key.get_pressed()

    # Player 1 controls (W/S keys)
    if keys[pygame.K_w]:
        player1.move_up()
    if keys[pygame.K_s]:
        player1.move_down()

    # Update CPU opponent
    player2.update_cpu(ball)

    # Move ball
    ball.move()

    # Check paddle collisions
    if ball.rect.colliderect(player1.rect) or ball.rect.colliderect(player2.rect):
        ball.speed_x = -ball.speed_x

    # Check scoring
    if ball.rect.left <= 0:
        score2 += 1
        ball.reset()
    if ball.rect.right >= WIDTH:
        score1 += 1
        ball.reset()

    # Clear screen
    screen.fill(BLACK)

    # Draw game objects
    player1.draw()
    player2.draw()
    ball.draw()

    # Draw center line
    for i in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 2, i, 4, 20))

    # Draw scores
    score_text1 = font.render(str(score1), True, WHITE)
    score_text2 = font.render(str(score2), True, WHITE)
    screen.blit(score_text1, (WIDTH // 4, 50))
    screen.blit(score_text2, (WIDTH * 3 // 4 - 50, 50))

    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit game
pygame.quit()
sys.exit()