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
PURPLE = (147, 112, 219)

# Pygameの初期化
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Friendly Mode (ryopc)")
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
        
        # プレイヤーのステータス（人間に優しい設計）
        self.hp = 100         # 最大HP
        self.shoot_delay = 15 # 連射の速さ（15フレームごと）
        self.last_shot = pygame.time.get_ticks()
        self.hidden = False
        self.invulnerable = False
        self.invulnerable_timer = 0

    def update(self):
        # 無敵時間のカウントダウン処理
        if self.invulnerable and pygame.time.get_ticks() - self.invulnerable_timer > 1000:
            self.invulnerable = False

        if self.ai_mode:
            # 🤖 AI無双モード（前回の回避AIロジック）
            self.image.fill(PURPLE)
            danger_bullets = [b for b in enemy_bullets if abs(b.rect.centerx - self.rect.centerx) < 100 and b.rect.bottom < self.rect.top]
            
            if danger_bullets:
                closest_bullet = min(danger_bullets, key=lambda b: self.rect.top - b.rect.bottom)
                if closest_bullet.rect.centerx >= self.rect.centerx:
                    self.rect.x -= self.speed_x
                else:
                    self.rect.x += self.speed_x
            else:
                if len(mobs) > 0:
                    target_mob = max(mobs, key=lambda m: m.rect.y)
                    if self.rect.centerx < target_mob.rect.centerx:
                        self.rect.x += self.speed_x
                    elif self.rect.centerx > target_mob.rect.centerx:
                        self.rect.x -= self.speed_x
            
            if random.random() < 0.3:
                self.shoot()
        else:
            # 🧑‍💻 手動操作モード（無敵中は黄色に点滅）
            if self.invulnerable:
                self.image.fill(YELLOW)
            else:
                self.image.fill(GREEN)
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed_x
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed_x
            # 【追加】スペースキー長押しで自動連射できるように優しく変更
            if keys[pygame.K_SPACE]:
                self.shoot()
            
        # 画面外制限
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        now = pygame.time.get_ticks()
        # 連射タイマーのチェック（手動時は長押し対応、AIは制限なしで無双）
        if self.ai_mode or now - self.last_shot > self.shoot_delay * 16:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

    # 【追加】ダメージを受けたときの優しさ処理
    def hit(self, damage):
        if not self.invulnerable:
            self.hp -= damage
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            if self.hp <= 0:
                self.hp = 0
                return True # ゲームオーバー
        return False

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(2, 4) # 人間に優しく最高速度を少し低下

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(2, 4)

        if random.random() < 0.008: # 弾の頻度も少しだけ優しく
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
        self.speed_y = -12

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
        self.speed_y = 5 # 弾速も少しだけ優しく

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()

# 【追加】HPバーを描画する便利な関数
def draw_hp_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, outline_rect)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 1)

# -------------------------------------------------------------------
# ゲームのメイン処理
# -------------------------------------------------------------------

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

player = Player()
player.ai_mode = False # 最初は必ず手動
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
            if event.key == pygame.K_z:
                player.ai_mode = not player.ai_mode

    all_sprites.update()

    # 自機の弾と敵の衝突判定
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 10
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    # 自機と敵の本体衝突判定（即死せず、HPを35減らす）
    hits_player = pygame.sprite.spritecollide(player, mobs, True)
    for hit in hits_player:
        if player.hit(35):
            running = False
        # 当たった敵は消えるので、新しい敵を補充
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    # 自機と敵の弾の衝突判定（即死せず、HPを20減らす）
    hits_bullet = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for hit in hits_bullet:
        if player.hit(20):
            running = False

    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # 画面UIの表示（スコアとHPバー）
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    draw_hp_bar(screen, WIDTH - 120, 15, player.hp)
    
    # 無双中の画面インジケーター表示
    if player.ai_mode:
        ai_text = font.render("AI AUTO MODE ACTIVE", True, PURPLE)
        screen.blit(ai_text, (WIDTH // 2 - 130, HEIGHT - 50))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
