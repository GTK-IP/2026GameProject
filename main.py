import pygame
import random
import sys
import json
import os

pygame.init()

# =========================
# 설정
# =========================
WIDTH = 800
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meteor Assault")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
YELLOW = (255, 220, 0)
BLUE = (80, 180, 255)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont("malgungothic", 30)
BIG_FONT = pygame.font.SysFont("malgungothic", 60)

SAVE_FILE = "highscore.json"


# =========================
# 최고 점수 저장
# =========================

def load_highscore():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                return data["highscore"]
        except:
            return 0
    return 0


def save_highscore(score):
    with open(SAVE_FILE, "w") as f:
        json.dump({"highscore": score}, f)


highscore = load_highscore()


# =========================
# 별 배경
# =========================

stars = []

for _ in range(100):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])


def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[2])

        star[1] += star[2]

        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0


# =========================
# 플레이어
# =========================

class Player:
    def __init__(self):
        self.width = 60
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 80
        self.speed = 7
        self.hp = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        self.x = max(0, min(WIDTH - self.width, self.x))

    def draw(self):
        body = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]

        pygame.draw.polygon(screen, BLUE, body)

        pygame.draw.rect(
            screen,
            WHITE,
            (self.x + 22, self.y + 12, 16, 18)
        )

    def rect(self):
        return pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )


# =========================
# 미사일
# =========================

class Bullet:
    def __init__(self, x, y):
        self.rect_obj = pygame.Rect(x, y, 6, 15)
        self.speed = 10

    def update(self):
        self.rect_obj.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, YELLOW, self.rect_obj)


# =========================
# 운석
# =========================

class Meteor:
    def __init__(self, speed_bonus):
        size = random.randint(30, 70)

        self.rect_obj = pygame.Rect(
            random.randint(0, WIDTH - size),
            -size,
            size,
            size
        )

        self.speed = random.uniform(3, 6) + speed_bonus
        self.size = size

    def update(self):
        self.rect_obj.y += self.speed

    def draw(self):
        pygame.draw.circle(
            screen,
            (150, 150, 150),
            self.rect_obj.center,
            self.size // 2
        )

        pygame.draw.circle(
            screen,
            (100, 100, 100),
            self.rect_obj.center,
            self.size // 3
        )


# =========================
# 텍스트 출력
# =========================

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


# =========================
# 시작화면
# =========================

def show_title():
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        screen.fill(BLACK)
        draw_stars()

        title = BIG_FONT.render("METEOR ASSAULT", True, WHITE)
        screen.blit(title, (140, 180))

        draw_text("SPACE : 게임 시작", FONT, GREEN, 280, 300)
        draw_text("← → 또는 A D : 이동", FONT, WHITE, 250, 350)
        draw_text("SPACE : 발사", FONT, WHITE, 310, 390)
        draw_text(f"최고점수 : {highscore}", FONT, YELLOW, 280, 450)

        pygame.display.flip()


# =========================
# 게임오버
# =========================

def game_over(score):
    global highscore

    if score > highscore:
        highscore = score
        save_highscore(highscore)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    return

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)

        title = BIG_FONT.render("GAME OVER", True, RED)
        screen.blit(title, (220, 180))

        draw_text(
            f"최종 점수 : {score}",
            FONT,
            WHITE,
            280,
            300
        )

        draw_text(
            f"최고 점수 : {highscore}",
            FONT,
            YELLOW,
            260,
            350
        )

        draw_text(
            "R : 다시 시작",
            FONT,
            GREEN,
            300,
            420
        )

        draw_text(
            "ESC : 종료",
            FONT,
            WHITE,
            320,
            460
        )

        pygame.display.flip()


# =========================
# 메인 게임
# =========================

def game():

    player = Player()

    bullets = []
    meteors = []

    score = 0

    meteor_timer = 0
    shoot_delay = 0

    paused = False

    while True:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:
                    paused = not paused

                if not paused:
                    if event.key == pygame.K_SPACE:
                        if shoot_delay <= 0:
                            bullets.append(
                                Bullet(
                                    player.x + player.width // 2,
                                    player.y
                                )
                            )
                            shoot_delay = 10

        if paused:
            draw_text("PAUSE", BIG_FONT, YELLOW, 290, 250)
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        player.move(keys)

        if shoot_delay > 0:
            shoot_delay -= 1

        speed_bonus = score // 200

        meteor_timer += 1

        if meteor_timer > 25:
            meteors.append(Meteor(speed_bonus))
            meteor_timer = 0

        # 미사일 업데이트
        for bullet in bullets[:]:
            bullet.update()

            if bullet.rect_obj.bottom < 0:
                bullets.remove(bullet)

        # 운석 업데이트
        for meteor in meteors[:]:

            meteor.update()

            if meteor.rect_obj.top > HEIGHT:
                score += 2
                meteors.remove(meteor)

            elif meteor.rect_obj.colliderect(
                    player.rect()):

                player.hp -= 1
                meteors.remove(meteor)

                if player.hp <= 0:
                    return score

        # 충돌 처리
        for bullet in bullets[:]:

            for meteor in meteors[:]:

                if bullet.rect_obj.colliderect(
                        meteor.rect_obj):

                    score += 10

                    if bullet in bullets:
                        bullets.remove(bullet)

                    if meteor in meteors:
                        meteors.remove(meteor)

                    break

        # 화면 그리기
        screen.fill(BLACK)

        draw_stars()

        player.draw()

        for bullet in bullets:
            bullet.draw()

        for meteor in meteors:
            meteor.draw()

        draw_text(
            f"점수 : {score}",
            FONT,
            WHITE,
            20,
            20
        )

        draw_text(
            f"최고점수 : {highscore}",
            FONT,
            YELLOW,
            20,
            60
        )

        # 체력 표시
        for i in range(player.hp):
            pygame.draw.rect(
                screen,
                RED,
                (650 + i * 40, 20, 30, 30)
            )

        pygame.display.flip()


# =========================
# 실행
# =========================

show_title()

while True:
    final_score = game()
    game_over(final_score)