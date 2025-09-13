import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Font
font = pygame.font.SysFont(None, 36)

# Score
score = 0

# Level
level = 1
level_up_score = 50

# Load graphics
try:
    player_img = pygame.image.load("assets/player.png").convert_alpha()
    enemy_img = pygame.image.load("assets/enemy.png").convert_alpha()
    bullet_img = pygame.image.load("assets/bullet.png").convert_alpha()
    powerup_img = pygame.image.load("assets/powerup.png").convert_alpha()
    background = pygame.image.load("assets/background.png").convert()
except pygame.error as e:
    print("Could not load images. Make sure you have the 'assets' directory with all the images.")
    # Use colored surfaces as fallback
    player_img = pygame.Surface((50, 40))
    player_img.fill(BLUE)
    enemy_img = pygame.Surface((30, 30))
    enemy_img.fill(RED)
    bullet_img = pygame.Surface((5, 10))
    bullet_img.fill(WHITE)
    powerup_img = pygame.Surface((20, 20))
    powerup_img.fill(GREEN)
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(BLACK)


# Load sounds
try:
    shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
    explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
    powerup_sound = pygame.mixer.Sound("assets/powerup.wav")
except pygame.error as e:
    print("Could not load sounds. Make sure you have the 'assets' directory with all the sounds.")
    # Create dummy sound objects
    shoot_sound = pygame.mixer.Sound(buffer=b"")
    explosion_sound = pygame.mixer.Sound(buffer=b"")
    powerup_sound = pygame.mixer.Sound(buffer=b"")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = pygame.transform.scale(player_img, (50, 40))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
        self.speed = 5
        self.shield = False
        self.shield_timer = 0

    def update(self, pressed_keys):
        if self.shield and pygame.time.get_ticks() - self.shield_timer > 5000:
            self.shield = False
            self.image = pygame.transform.scale(player_img, (50, 40))

        if pressed_keys[pygame.K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.move_ip(self.speed, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super(Enemy, self).__init__()
        self.image = pygame.transform.scale(enemy_img, (30, 30))
        self.rect = self.image.get_rect(
            center=(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-100, -40),
            )
        )
        self.speed = random.randint(1 + level, 3 + level)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bullet, self).__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom < 0:
            self.kill()

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super(PowerUp, self).__init__()
        self.image = powerup_img
        self.rect = self.image.get_rect(
            center=(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-100, -40),
            )
        )
        self.speed = 2

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

def game_loop():
    global score, level, level_up_score
    # Reset game state
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    powerups.empty()

    player = Player()
    all_sprites.add(player)

    score = 0
    level = 1
    level_up_score = 50

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    shoot_sound.play()

        # Get pressed keys
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        # Level up
        if score >= level_up_score:
            level += 1
            level_up_score *= 2

        # Create new enemies
        if random.randint(1, 100) < 5 + level:
            enemy = Enemy(level)
            enemies.add(enemy)
            all_sprites.add(enemy)

        # Update enemies and bullets
        enemies.update()
        bullets.update()
        powerups.update()

        # Create new power-ups
        if random.randint(1, 1000) < 2:
            powerup = PowerUp()
            all_sprites.add(powerup)
            powerups.add(powerup)

        # Check for collisions
        # Check for collisions between player and power-ups
        collected_powerups = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in collected_powerups:
            player.shield = True
            player.shield_timer = pygame.time.get_ticks()
            player.image.fill(GREEN)
            powerup_sound.play()

        # Check for collisions between bullets and enemies
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            score += 10
            explosion_sound.play()

        # Check for collisions between player and enemies
        if not player.shield and pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            running = False
        elif player.shield:
            shield_hits = pygame.sprite.spritecollide(player, enemies, True)

        # Background
        screen.blit(background, (0, 0))

        # Draw all sprites
        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)

        # Draw the score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Update the display
        pygame.display.flip()

        # Frame rate
        pygame.time.Clock().tick(60)
    return "GAME_OVER"


def game_over_screen():
    screen.fill(BLACK)
    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press 'r' to restart or 'q' to quit", True, WHITE)

    screen.blit(game_over_text, (SCREEN_WIDTH / 2 - game_over_text.get_width() / 2, SCREEN_HEIGHT / 2 - 50))
    screen.blit(score_text, (SCREEN_WIDTH / 2 - score_text.get_width() / 2, SCREEN_HEIGHT / 2))
    screen.blit(restart_text, (SCREEN_WIDTH / 2 - restart_text.get_width() / 2, SCREEN_HEIGHT / 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    return "RESTART"
                elif event.key == pygame.K_q:
                    return "QUIT"

# Main game state manager
state = "RUNNING"
while state != "QUIT":
    if state == "RUNNING":
        result = game_loop()
        if result == "GAME_OVER":
            state = "GAME_OVER"
        elif result == "QUIT":
            state = "QUIT"
    elif state == "GAME_OVER":
        result = game_over_screen()
        if result == "RESTART":
            state = "RUNNING"
        elif result == "QUIT":
            state = "QUIT"

pygame.quit()
