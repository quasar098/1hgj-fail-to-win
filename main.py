try:
    from win32api import EnumDisplayDevices, EnumDisplaySettings
except:
    pass
from platform import platform
from tools import *
import pygame
from numpy import clip as clamp
from json import loads, dumps

pygame.init()

WIDTH, HEIGHT = 1280, 720
if "Windows" in platform():
    FRAMERATE = EnumDisplaySettings(EnumDisplayDevices().DeviceName, -1).DisplayFrequency
else:
    FRAMERATE = 60  # less than subpar way to do this probably
pygame.display.set_caption("you died!")
screen = pygame.display.set_mode([WIDTH, HEIGHT])
font = pygame.font.Font(get_path("Arialn.ttf"), 36)
clock = pygame.time.Clock()

# colors
BG_COL = pygame.Color(255, 255, 255)
PRIMARY_COL = pygame.Color(0, 178, 202)
SECONDARY_COL = pygame.Color(151, 250, 197)


class Player:
    def __init__(self, pos: tuple[float, float]):
        self.speed = 4
        self.x, self.y = pos
        self.image = get_texture(get_path("images", "player.png"))

    @property
    def hitbox(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def move(self) -> None:
        _ = pygame.key.get_pressed()
        self.x = clamp(self.x+(_[pygame.K_d]-_[pygame.K_a])*self.speed, 0, WIDTH-self.image.get_width())
        self.y = clamp(self.y+(_[pygame.K_s]-_[pygame.K_w])*self.speed, 0, WIDTH-self.image.get_height())

    @property
    def pos(self):
        return self.x, self.y

    def draw(self) -> None:
        screen.blit(self.image, self.pos)


class Goal:  # actually makes you lose
    def __init__(self, pos: tuple[float, float]):
        self.x, self.y = pos
        self.image = get_texture(get_path("images", "goal.png"))

    @property
    def hitbox(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    @property
    def pos(self):
        return self.x, self.y

    def draw(self) -> None:
        screen.blit(self.image, self.pos)


class Flame:  # how to win
    def __init__(self, pos: tuple[float, float]):
        self.x, self.y = pos
        self.image = get_texture(get_path("images", "flame.png"))

    @property
    def hitbox(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    @property
    def pos(self):
        return self.x, self.y

    def draw(self) -> None:
        screen.blit(self.image, self.pos)


def load_level(level_num: int):
    global goals, level, game_over, has_won
    goals = []
    game_over = False
    has_won = False
    if str(level_num) not in levels:
        level = 1
        level_num = 1
    for _ in levels[str(level_num)]["goals"]:
        goals.append(Goal(_))
    flame.x, flame.y = levels[str(level_num)]["flame"]
    player.x, player.y = levels[str(level_num)]["player"]


goals: list[Goal] = []
flame = Flame((WIDTH/2, HEIGHT/2))
player = Player((10, 10))

game_over = False
has_won = False
with open(get_path("levels.json")) as f:
    levels = loads(f.read())
level = 1
load_level(level)
debug = False

running = True
while running:
    screen.fill(BG_COL)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_over:
                    if not has_won:
                        running = False
                    else:
                        level += 1
                        load_level(level)
            if debug and not game_over:
                if event.button == 2:
                    flame.x, flame.y = pygame.mouse.get_pos()
                if event.button == 3:
                    goals.append(Goal(pygame.mouse.get_pos()))
                if event.button == 1:
                    player.x, player.y = pygame.mouse.get_pos()
        if debug:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    level += 1
                if event.key == pygame.K_LEFT:
                    level -= 1
                if event.key == pygame.K_c:
                    goals: list[Goal] = []
                    flame = Flame((WIDTH/2, HEIGHT/2))
                    player = Player((10, 10))
                if event.key == pygame.K_p:
                    levels[str(level)] = {}
                    levels[str(level)]["player"] = [int(player.x), int(player.y)]
                    levels[str(level)]["flame"] = [flame.x, flame.y]
                    levels[str(level)]["goals"] = [[goal.x, goal.y] for goal in goals]
                if event.key == pygame.K_g:
                    with open(get_path("levels.json"), 'w') as f:
                        f.write(dumps(levels))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                debug = not debug

    # code
    if not game_over:
        player.move()
        player.draw()
        for goal in goals:
            goal.draw()
            if player.hitbox.colliderect(goal.hitbox):
                game_over = True
                has_won = False
                break
        flame.draw()
        if player.hitbox.colliderect(flame.hitbox):
            game_over = True
            has_won = True
    else:
        if has_won:
            screen.blit(fetch_text(font, "you died!"), (20, 20))
            screen.blit(fetch_text(font, "you win"), (20, 90))
            screen.blit(fetch_text(font, "click again for next level"),  (300, 20))
        else:
            screen.blit(fetch_text(font, "you survived..."), (20, 20))
            screen.blit(fetch_text(font, "you lose"), (20, 90))
            screen.blit(fetch_text(font, "click to exit the game"),  (300, 20))
    if debug:
        screen.blit(fetch_text(font, f"current level: {level}"), (100, 100))
    pygame.display.flip()
    clock.tick(FRAMERATE)
pygame.quit()
