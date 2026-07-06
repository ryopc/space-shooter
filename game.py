import pygame
import random
import sys

# 画面サイズの定義
WIDTH = 480
HEIGHT = 600
FPS = 60

# 色の定義 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (147, 112, 219)  # AI無双モード中の自機の色

# Pygameの初期化
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - AI Mode (ryopc)")
clock = pygame.time.Clock()

# -------------------------------------------------------------------
# クラスの定義 (自機・敵・弾)
# -------------------------------------------------------------------

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 8
        
        # 【追加】AI無双モードの状態フラグ
        self.ai_mode = False

    def update(self):
        # Zキーが押されたら、AI無双モードを起動（トグル切り替え）
        # ※押しっぱなし対策のため、メインループのイベントハンドラでも切り替えます
        
        if self.ai_mode:
            # -----------------------------------------------
            # 🤖 【AI無双モードの思考ロジック】
            # -----------------------------------------------
            self.image.fill(PURPLE)  # 無双中は紫に変身！
            
            # 画面上に敵がいるか確認
            if len(mobs) > 0:
                # 一番手前（画面の下側＝y座標が最大）にいる危険な敵をロックオン
                target_mob = max(mobs, key=lambda m: m.rect.y)
                
                # 敵の真下に移動するよう、x座標を合わせる
                if self.rect.centerx < target_mob.rect.centerx:
                    self.rect.x += self.speed_x
                elif self.rect.centerx > target_mob.rect.centerx:
                    self.rect.x -= self.speed_x
                    
            # AIは常に超高速で弾を自動連射（3フレームに1発）
            if random.random() < 0.3:
                self.shoot()
        else:
            # 🧑‍💻 【通常モード（手動操作）】
            self.image.fill(GREEN)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed_x
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed_x
            
        # 画面外制限
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(2, 5)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(2, 5)

        if random.random() < 0.01:
            self.shoot()

    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -12  # AI用に少し弾速をアップ

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 16))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.centerx = x
        self.speed_y = 6

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()

# -------------------------------------------------------------------
# ゲームのメイン処理
# -------------------------------------------------------------------

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

score = 0
font = pygame.font.SysFont(None, 36)

running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not player.ai_mode:  # 手動モードの時だけスペースで発射
                    player.shoot()
            # 【追加】zキー（小文字）が押されたら、AI無双モードをオン・オフ切り替え
            if event.key == pygame.K_z:
                player.ai_mode = not player.ai_mode

    all_sprites.update()

    # 衝突判定
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 10
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    hits_player = pygame.sprite.spritecollide(player, mobs, False)
    if hits_player:
        running = False

    hits_bullet = pygame.sprite.spritecollide(player, enemy_bullets, False)
    if hits_bullet:
        running = False

    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # 【追加】無双中の画面インジケーター表示
    if player.ai_mode:
        ai_text = font.render("AI AUTO MODE ACTIVE", True, PURPLE)
        screen.blit(ai_text, (WIDTH // 2 - 130, HEIGHT - 50))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
