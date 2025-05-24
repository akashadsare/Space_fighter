import pygame
import random
import os
import sys
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Fighter")
clock = pygame.time.Clock()

# Asset loading functions
def load_image(name, scale=1):
    try:
        if name.startswith("Lasers/") or name.startswith("Enemies/") or name.startswith("Effects/") or name.startswith("Power-ups/") or name.startswith("UI/"):
            path = os.path.join("assets", "PNG", name)
        else:
            path = os.path.join("assets", "PNG", name)
        
        image = pygame.image.load(path).convert_alpha()
        if scale != 1:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except Exception as e:
        print(f"Error loading image: {name}, {e}")
        return pygame.Surface((50, 40))

def load_background(name):
    try:
        img = pygame.image.load(os.path.join("assets", "Backgrounds", name)).convert()
        # Scale background to match screen dimensions
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"Error loading background: {name}, {e}")
        return pygame.Surface((WIDTH, HEIGHT))

# Button class for menu
class Button:
    def __init__(self, x, y, width, height, text, color=(30, 30, 30), text_color=WHITE, border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.border_radius = border_radius
        self.hover_color = (min(color[0] + 20, 255), min(color[1] + 20, 255), min(color[2] + 20, 255))
        self.active_color = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))
        self.clicked = False
        self.active = False
        
    def draw(self):
        action = False
        # Get mouse position
        pos = pygame.mouse.get_pos()
        
        # Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
                pygame.draw.rect(screen, self.active_color, self.rect, 0, self.border_radius)
            else:
                pygame.draw.rect(screen, self.hover_color, self.rect, 0, self.border_radius)
        else:
            if self.active:
                pygame.draw.rect(screen, self.active_color, self.rect, 0, self.border_radius)
            else:
                pygame.draw.rect(screen, self.color, self.rect, 0, self.border_radius)
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
            
        # Draw subtle border
        pygame.draw.rect(screen, (200, 200, 200, 100), self.rect, 1, self.border_radius)
        
        # Draw text
        font = pygame.font.Font(None, 28)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        return action
        
    def set_active(self, active):
        self.active = active

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, color='blue'):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = load_image(f"playerShip1_{color}.png", 0.5)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8
        self.health = 100
        self.lives = 3
        self.shoot_delay = 250  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.hidden = False
        self.hide_timer = 0
        self.invulnerable = False
        self.invulnerable_timer = 0

    def update(self):
        # Check invulnerability
        if self.invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > 3000:  # 3 seconds
                self.invulnerable = False
        
        # Unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH // 2
            self.rect.bottom = HEIGHT - 10
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            
        if not self.hidden:
            # Movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += self.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.rect.y -= self.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.rect.y += self.speed

            # Keep player on screen
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT

    def shoot(self):
        if not self.hidden:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
                
    def hide(self):
        # Hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)
        
    def draw(self, surface):
        # Blinking effect when invulnerable
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
        surface.blit(self.image, self.rect)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, difficulty=1):
        pygame.sprite.Sprite.__init__(self)
        # Randomly choose enemy type
        enemy_types = ["Enemies/enemyRed1.png", "Enemies/enemyBlue2.png", "Enemies/enemyGreen3.png"]
        self.image = load_image(random.choice(enemy_types), 0.5)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -40)
        self.speedy = random.randrange(1, 3 + difficulty)
        self.speedx = random.randrange(-2, 2)
        self.can_shoot = random.random() < 0.3  # 30% chance enemy can shoot
        self.shoot_delay = random.randrange(1000, 3000)
        self.last_shot = pygame.time.get_ticks()
        self.difficulty = difficulty

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # Random shooting for enemies that can shoot
        if self.can_shoot:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot()
        
        # If enemy goes off screen, respawn
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)
            self.speedx = random.randrange(-2, 2)
            
    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("Lasers/laserBlue01.png", 0.5)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10  # Negative because moving up

    def update(self):
        self.rect.y += self.speedy
        # Kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()
            
# Enemy Bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("Lasers/laserRed01.png", 0.5)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 7  # Positive because moving down

    def update(self):
        self.rect.y += self.speedy
        # Kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill()
            
# Asteroid class
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Randomly choose asteroid type
        asteroid_types = [
            "Meteors/meteorBrown_big1.png",
            "Meteors/meteorBrown_med1.png", 
            "Meteors/meteorGrey_big2.png",
            "Meteors/meteorGrey_med2.png"
        ]
        self.image = load_image(random.choice(asteroid_types), 0.6)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        
        # Start from top of screen at random position
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        
        # Random speed and rotation
        self.speedy = random.randrange(3, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.original_image = self.image.copy()
        
    def update(self):
        # Rotate asteroid
        self.rot = (self.rot + self.rot_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rot)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Move asteroid
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # If asteroid goes off screen, respawn
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size="lg"):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.frame = 0
        self.frames = []
        for i in range(9):
            try:
                img = load_image(f"Effects/fire0{i}.png", 0.5)
                if size == "sm":
                    img = pygame.transform.scale(img, (32, 32))
                self.frames.append(img)
            except:
                print(f"Error loading explosion frame {i}")
        
        if len(self.frames) > 0:
            self.image = self.frames[0]
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # milliseconds

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame >= len(self.frames):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.frames[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Powerup class
class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'bolt'])
        if self.type == 'shield':
            self.image = load_image("Power-ups/powerupBlue_shield.png", 0.5)
        else:
            self.image = load_image("Power-ups/powerupBlue_bolt.png", 0.5)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        # Kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill()

# Background class for scrolling effect
class Background:
    def __init__(self):
        self.bg_options = {
            'purple': load_background("purple.png"),
            'blue': load_background("blue.png"),
            'black': load_background("black.png"),
            'darkPurple': load_background("darkPurple.png")
        }
        self.current_bg = 'darkPurple'
        self.bgimage = self.bg_options[self.current_bg]
        self.rectBGimg = self.bgimage.get_rect()
        self.bgY1 = 0
        self.bgX1 = 0
        self.bgY2 = -HEIGHT
        self.bgX2 = 0
        self.moving_speed = 2
        
    def change_background(self, bg_name):
        if bg_name in self.bg_options:
            self.current_bg = bg_name
            self.bgimage = self.bg_options[bg_name]
            self.rectBGimg = self.bgimage.get_rect()

    def update(self):
        self.bgY1 += self.moving_speed
        self.bgY2 += self.moving_speed
        if self.bgY1 >= HEIGHT:
            self.bgY1 = -HEIGHT
        if self.bgY2 >= HEIGHT:
            self.bgY2 = -HEIGHT

    def render(self):
        screen.blit(self.bgimage, (self.bgX1, self.bgY1))
        screen.blit(self.bgimage, (self.bgX2, self.bgY2))

# Game state management
class Game:
    def __init__(self):
        self.score = 0
        self.state = "menu"  # menu, start, playing, game_over
        self.difficulty = 1  # 1=easy, 2=medium, 3=hard
        self.ship_color = 'blue'  # Default ship color
        self.background_name = 'darkPurple'  # Default background
        
    def draw_text(self, text, size, x, y, color=WHITE):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        screen.blit(text_surface, text_rect)
        
    def show_menu(self):
        # Clear the screen first
        screen.fill(BLACK)
        background.render()
        
        # Adjust vertical spacing
        title_y = HEIGHT // 8
        play_y = HEIGHT // 4
        difficulty_y = HEIGHT // 2 - 80
        ship_y = HEIGHT // 2 + 40
        bg_y = HEIGHT // 2 + 160
        
        # Title with shadow effect
        self.draw_text("SPACE FIGHTER", 72, WIDTH // 2 + 3, title_y + 3, BLACK)
        self.draw_text("SPACE FIGHTER", 72, WIDTH // 2, title_y, YELLOW)
        
        # Play button
        play_button = Button(WIDTH//2 - 100, play_y, 200, 50, "PLAY", (50, 200, 50))
        
        # Difficulty section
        self.draw_text("DIFFICULTY", 36, WIDTH // 2, difficulty_y, YELLOW)
        easy_button = Button(WIDTH//2 - 250, difficulty_y + 40, 150, 40, "EASY", (0, 200, 0))
        medium_button = Button(WIDTH//2 - 75, difficulty_y + 40, 150, 40, "MEDIUM", (200, 200, 0))
        hard_button = Button(WIDTH//2 + 100, difficulty_y + 40, 150, 40, "HARD", (200, 0, 0))
        
        # Ship color section
        self.draw_text("SHIP COLOR", 36, WIDTH // 2, ship_y, YELLOW)
        blue_button = Button(WIDTH//2 - 250, ship_y + 40, 100, 40, "BLUE", (50, 50, 200))
        green_button = Button(WIDTH//2 - 125, ship_y + 40, 100, 40, "GREEN", (50, 200, 50))
        orange_button = Button(WIDTH//2, ship_y + 40, 100, 40, "ORANGE", (200, 100, 0))
        red_button = Button(WIDTH//2 + 125, ship_y + 40, 100, 40, "RED", (200, 50, 50))
        
        # Background section
        self.draw_text("BACKGROUND", 36, WIDTH // 2, bg_y, YELLOW)
        purple_bg_button = Button(WIDTH//2 - 325, bg_y + 40, 150, 40, "PURPLE", (100, 0, 100))
        blue_bg_button = Button(WIDTH//2 - 150, bg_y + 40, 150, 40, "BLUE BG", (0, 0, 100))
        black_bg_button = Button(WIDTH//2 + 25, bg_y + 40, 150, 40, "BLACK", (50, 50, 50))
        dark_purple_bg_button = Button(WIDTH//2 + 200, bg_y + 40, 150, 40, "DARK PURPLE", (50, 0, 50))

        # Draw buttons and check for clicks
        if play_button.draw():
            self.state = "start"
            
        if easy_button.draw():
            self.difficulty = 1
        if medium_button.draw():
            self.difficulty = 2
        if hard_button.draw():
            self.difficulty = 3
            
        if blue_button.draw():
            self.ship_color = 'blue'
        if green_button.draw():
            self.ship_color = 'green'
        if orange_button.draw():
            self.ship_color = 'orange'
        if red_button.draw():
            self.ship_color = 'red'
            
        # Background selection
        if purple_bg_button.draw():
            self.background_name = 'purple'
            background.change_background('purple')
        if blue_bg_button.draw():
            self.background_name = 'blue'
            background.change_background('blue')
        if black_bg_button.draw():
            self.background_name = 'black'
            background.change_background('black')
        if dark_purple_bg_button.draw():
            self.background_name = 'darkPurple'
            background.change_background('darkPurple')
            
        # Preview selected ship
        ship_img = load_image(f"playerShip1_{self.ship_color}.png", 0.5)
        ship_rect = ship_img.get_rect(center=(WIDTH//2, HEIGHT - 30))
        screen.blit(ship_img, ship_rect)
        
        pygame.display.flip()

    def show_start_screen(self):
        waiting = True
        while waiting:
            clock.tick(FPS)
            
            # Clear screen and draw background
            screen.fill(BLACK)
            background.render()
            
            # Title with animation effect
            title_size = 64 + int(10 * abs(math.sin(pygame.time.get_ticks() / 500)))
            self.draw_text("GET READY!", title_size, WIDTH // 2, HEIGHT // 4)
            
            # Instructions
            self.draw_text("Arrow keys or WASD to move", 28, WIDTH // 2, HEIGHT // 2 - 30)
            self.draw_text("Space to fire", 28, WIDTH // 2, HEIGHT // 2 + 10)
            self.draw_text("Collect powerups to upgrade your ship", 22, WIDTH // 2, HEIGHT // 2 + 50)
            
            # Animated prompt
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                self.draw_text("Press any key to begin", 30, WIDTH // 2, HEIGHT * 3 / 4, YELLOW)
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    waiting = False
                    self.state = "playing"
            
            # Update display
            pygame.display.flip()
            background.update()

    def show_game_over_screen(self):
        waiting = True
        while waiting:
            clock.tick(FPS)
            
            # Clear screen and draw background
            screen.fill(BLACK)
            background.render()
            
            # Game over text with shadow
            self.draw_text("GAME OVER", 72, WIDTH // 2 + 3, HEIGHT // 4 + 3, BLACK)
            self.draw_text("GAME OVER", 72, WIDTH // 2, HEIGHT // 4, RED)
            
            # Score
            self.draw_text(f"Final Score: {self.score}", 42, WIDTH // 2, HEIGHT // 2)
            
            # Options
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                self.draw_text("Press ENTER to play again", 30, WIDTH // 2, HEIGHT * 3 / 4 - 40, YELLOW)
                self.draw_text("Press ESC for main menu", 30, WIDTH // 2, HEIGHT * 3 / 4 + 10, YELLOW)
            else:
                self.draw_text("Press ENTER to play again", 30, WIDTH // 2, HEIGHT * 3 / 4 - 40)
                self.draw_text("Press ESC for main menu", 30, WIDTH // 2, HEIGHT * 3 / 4 + 10)
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        self.state = "playing"
                        return True  # Restart the game
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.state = "menu"
                        return False  # Go to menu
            
            # Update display
            pygame.display.flip()
            background.update()
            
        return False

# Load sounds
try:
    shoot_sound = pygame.mixer.Sound(os.path.join("assets", "Bonus", "sfx_laser1.ogg"))
    explosion_sound = pygame.mixer.Sound(os.path.join("assets", "Bonus", "sfx_twoTone.ogg"))
    shield_sound = pygame.mixer.Sound(os.path.join("assets", "Bonus", "sfx_shieldUp.ogg"))
    game_over_sound = pygame.mixer.Sound(os.path.join("assets", "Bonus", "sfx_lose.ogg"))
    
    # Set volume
    shoot_sound.set_volume(0.3)
    explosion_sound.set_volume(0.5)
    shield_sound.set_volume(0.5)
    game_over_sound.set_volume(0.7)
except Exception as e:
    print(f"Error loading sounds: {e}")

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Create game objects
background = Background()
game = Game()
player = None  # Will be created when game starts

# Main game loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input (events)
    for event in pygame.event.get():
        # Check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game.state == "playing" and player:
                player.shoot()
    
    # Update background
    background.update()
    
    # Process game states
    if game.state == "menu":
        game.show_menu()
        continue  # Skip the rest of the loop
        
    elif game.state == "start":
        # Reset game objects before showing start screen
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        
        # Show start screen
        game.show_start_screen()
        
        # Initialize player and game objects after start screen
        player = Player(game.ship_color)
        all_sprites.add(player)
        
        # Set background
        background.change_background(game.background_name)
        
        # Spawn initial enemies - more for higher difficulty
        for i in range(4 + game.difficulty * 2):
            enemy = Enemy(game.difficulty)
            all_sprites.add(enemy)
            enemies.add(enemy)
            
        # Spawn initial asteroids
        for i in range(3 + game.difficulty):
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroids.add(asteroid)
        
        game.score = 0
        player.health = 100
        player.lives = 3
        player.shoot_delay = 250

    elif game.state == "playing":
        # Update all sprites
        all_sprites.update()
        
        # Check for bullet-enemy collisions
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            game.score += 10 * game.difficulty
            # Create explosion
            expl = Explosion(hit.rect.center, "sm")
            all_sprites.add(expl)
            explosion_sound.play()
            
            # Random chance to spawn powerup - less likely on higher difficulty
            if random.random() > (0.9 + game.difficulty * 0.02):
                pow = Powerup(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
                
            # Spawn a new enemy
            enemy = Enemy(game.difficulty)
            all_sprites.add(enemy)
            enemies.add(enemy)
            
        # Check for bullet-asteroid collisions
        hits = pygame.sprite.groupcollide(bullets, asteroids, True, True)
        for hit in hits:
            game.score += 15 * game.difficulty
            # Create explosion
            expl = Explosion(hit.rect.center, "lg")
            all_sprites.add(expl)
            explosion_sound.play()
            
            # Spawn a new asteroid
            asteroid = Asteroid()
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        # Check for enemy-player collisions
        if player and not player.hidden and not player.invulnerable:
            hits = pygame.sprite.spritecollide(player, enemies, True)
            for hit in hits:
                player.health -= 20 + (game.difficulty * 5)
                expl = Explosion(hit.rect.center, "sm")
                all_sprites.add(expl)
                explosion_sound.play()
                
                if player.health <= 0:
                    player.lives -= 1
                    player.health = 100
                    player.hide()
                    if player.lives <= 0:
                        death_explosion = Explosion(player.rect.center)
                        all_sprites.add(death_explosion)
                        game_over_sound.play()
                        game.state = "game_over"
                        
                # Spawn a new enemy
                enemy = Enemy(game.difficulty)
                all_sprites.add(enemy)
                enemies.add(enemy)
                
            # Check for asteroid-player collisions
            hits = pygame.sprite.spritecollide(player, asteroids, True)
            for hit in hits:
                player.health -= 30 + (game.difficulty * 7)  # Asteroids do more damage
                expl = Explosion(hit.rect.center, "lg")
                all_sprites.add(expl)
                explosion_sound.play()
                
                if player.health <= 0:
                    player.lives -= 1
                    player.health = 100
                    player.hide()
                    if player.lives <= 0:
                        death_explosion = Explosion(player.rect.center)
                        all_sprites.add(death_explosion)
                        game_over_sound.play()
                        game.state = "game_over"
                        
                # Spawn a new asteroid
                asteroid = Asteroid()
                all_sprites.add(asteroid)
                asteroids.add(asteroid)
                
            # Check for enemy bullet-player collisions
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for hit in hits:
                player.health -= 10 + (game.difficulty * 3)
                expl = Explosion(hit.rect.center, "sm")
                all_sprites.add(expl)
                
                if player.health <= 0:
                    player.lives -= 1
                    player.health = 100
                    player.hide()
                    if player.lives <= 0:
                        death_explosion = Explosion(player.rect.center)
                        all_sprites.add(death_explosion)
                        game_over_sound.play()
                        game.state = "game_over"
                
        # Check for powerup-player collisions
        if player and not player.hidden:
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'shield':
                    player.health = 100
                    shield_sound.play()
                elif hit.type == 'bolt':
                    player.shoot_delay = max(50, player.shoot_delay - 50)
                    shield_sound.play()

        # Clear screen first
        screen.fill(BLACK)
        
        # Draw background
        background.render()
        
        # Draw all sprites except player
        for sprite in all_sprites:
            if sprite != player:
                screen.blit(sprite.image, sprite.rect)
        
        # Draw player with special handling
        if player and not player.hidden:
            player.draw(screen)

        # Draw UI
        game.draw_text(f"Score: {game.score}", 22, WIDTH // 2, 10)
        
        # Draw health bar
        health_width = 200
        health_height = 20
        fill_width = (player.health / 100) * health_width
        outline_rect = pygame.Rect(10, 10, health_width, health_height)
        fill_rect = pygame.Rect(10, 10, fill_width, health_height)
        pygame.draw.rect(screen, GREEN, fill_rect)
        pygame.draw.rect(screen, WHITE, outline_rect, 2)
        
        # Draw lives
        for i in range(player.lives):
            img = load_image("UI/playerLife1_blue.png", 0.5)
            img_rect = img.get_rect()
            img_rect.x = WIDTH - 30 * (i + 1)
            img_rect.y = 10
            screen.blit(img, img_rect)

    elif game.state == "game_over":
        if game.show_game_over_screen():
            # Reset game objects if returning to play
            all_sprites = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            enemy_bullets = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            asteroids = pygame.sprite.Group()
            player = Player(game.ship_color)
            all_sprites.add(player)
            
            # Spawn enemies
            for i in range(4 + game.difficulty * 2):
                enemy = Enemy(game.difficulty)
                all_sprites.add(enemy)
                enemies.add(enemy)
                
            # Spawn asteroids
            for i in range(3 + game.difficulty):
                asteroid = Asteroid()
                all_sprites.add(asteroid)
                asteroids.add(asteroid)

    # After drawing everything, flip the display
    pygame.display.flip()

pygame.quit()