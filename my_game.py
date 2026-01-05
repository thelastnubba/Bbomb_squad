import pygame
import sys
import random
pygame.init()
pygame.font.init()
pygame.mixer.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Evade The Squares")
FONT = pygame.font.Font(None, 36)
GAME_OVER_FONT = pygame.font.Font(None, 100)
MENU_FONT = pygame.font.Font(None, 100)
current_volume = 0.3
is_muted = False
try:
    music_file_path = "/Users/maxfrey/Downloads/08. Mantis Lords.mp3"
    pygame.mixer.music.load(music_file_path)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(current_volume)
except pygame.error:
    print("Warning: Background music file not found.")
def get_random_color():
    return (random.randrange(256), random.randrange(256), random.randrange(256))
try:
    background_image = pygame.image.load("/Users/maxfrey/Downloads/scaffold.png").convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error:
    background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_image.fill((30, 30, 30))
ENEMY_BASE_SPEED = 1
score = 0
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((45, 25))
        self.image.fill((158, 51, 51))
        self.rect = self.image.get_rect()
        self.reset_position()
        self.speed_y = ENEMY_BASE_SPEED + random.randrange(0, 4)
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.y > SCREEN_HEIGHT:
            global score
            score += 1
            self.reset_and_recolor()
            self.speed_y = ENEMY_BASE_SPEED + random.randrange(0, 4)
    def reset_and_recolor(self):
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.image.fill(get_random_color())
    def reset_position(self):
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 70))
        self.base_color = (247, 224, 146)
        self.dash_color = (100, 200, 255)
        self.image.fill(self.base_color)
        self.rect = self.image.get_rect()
        self.reset_pos()
        self.speed = 7
        self.dash_speed = 15
        self.dash_duration = 20
        self.dash_cooldown = 45
        self.dash_timer = 0
        self.cooldown_timer = 0
        self.dash_dir = [0, 0]
    def reset_pos(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.dash_timer = 0
        self.cooldown_timer = 0
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.cooldown_timer == 0:
            dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
            if dx != 0 or dy != 0:
                self.dash_timer = self.dash_duration
                self.cooldown_timer = self.dash_cooldown
                self.dash_dir = [dx, dy]
        if self.dash_timer > 0:
            self.rect.x += self.dash_dir[0] * self.dash_speed
            self.rect.y += self.dash_dir[1] * self.dash_speed
            self.dash_timer -= 1
            self.image.fill(self.dash_color)
        else:
            self.image.fill(self.base_color)
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
                self.rect.x -= self.speed
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < SCREEN_WIDTH:
                self.rect.x += self.speed
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
                self.rect.y -= self.speed
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < SCREEN_HEIGHT:
                self.rect.y += self.speed
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        self.rect.clamp_ip(screen.get_rect())
def reset_game():
    global score
    score = 0
    player.reset_pos()
    enemies.empty()
    all_sprites.empty()
    all_sprites.add(player)
    for i in range(30):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
player = Player()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
reset_game()
clock = pygame.time.Clock()
running = True
game_over = False
paused = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_p and not game_over:
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if pygame.K_1 <= event.key <= pygame.K_9:
                current_volume = (event.key - pygame.K_0) / 10.0
                is_muted = False
                pygame.mixer.music.set_volume(current_volume)
            elif event.key == pygame.K_0:
                current_volume = 1.0
                is_muted = False
                pygame.mixer.music.set_volume(current_volume)
            if event.key == pygame.K_m:
                is_muted = not is_muted
                pygame.mixer.music.set_volume(0 if is_muted else current_volume)
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                    game_over = False
                if event.key == pygame.K_q:
                    running = False
    if not game_over and not paused:
        all_sprites.update()
        if player.dash_timer == 0 and pygame.sprite.spritecollideany(player, enemies):
            game_over = True
    screen.blit(background_image, (0, 0))
    all_sprites.draw(screen)
    vol_display = 0 if is_muted else int(current_volume * 100)
    screen.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    if player.cooldown_timer == 0:
        dash_label = FONT.render("DASH READY", True, (0, 255, 150))
    else:
        dash_label = FONT.render("DASH COOLING...", True, (255, 100, 100))
    screen.blit(dash_label, (10, 70))
    if paused:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        p_text = MENU_FONT.render("PAUSED", True, (255, 255, 255))
        screen.blit(p_text, (SCREEN_WIDTH//2 - p_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        resume_text = FONT.render("Press 'P' to Resume", True, (200, 200, 200))
        screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        go_text = GAME_OVER_FONT.render("GAME OVER", True, (255, 50, 50))
        final_score = MENU_FONT.render(f"Final Score: {score}", True, (255, 255, 255))
        restart_text = MENU_FONT.render("Press 'R' to Restart or 'Q' to Quit", True, (0, 213, 255))
        screen.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, SCREEN_HEIGHT//2 - 120))
        screen.blit(final_score, (SCREEN_WIDTH//2 - final_score.get_width()//2, SCREEN_HEIGHT//2 - 20))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 80))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()