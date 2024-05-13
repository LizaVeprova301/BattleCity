import pygame
import random
import button
from core.tools import make_graph_from_map, load_image, shortest_path

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WIDTH = 800
HEIGHT = 800
FPS = 30
GAME_OVER = "Game Over"
GAME_WIN = "You Win!"
GAME_CAPTION = "Battle City"
GAME_MENU_CAPTION = "Welcome to Battle-City"
FONT_NAME = 'freesansbold.ttf'
CENTER_SCREEN_POS = (400, 400)


# IN MAP OBJECTS RELATION
# |  0 - empty space  |  1 - unbreakable wall  |  2 - breakable wall
# |  3 - leaves  |  4 - water


class Bullet:
    def __init__(self, direction, x, y, tank, bullet_type):
        self.damage = 1 if bullet_type == 'simple' else 0.7
        self.tank = tank
        self.flag = True
        self.length = 7
        self.aim = direction
        self.alive = True
        self.x = x + (32 if self.aim == 'right' else -5 if self.aim == 'left' else 16)
        self.y = y + (16 if self.aim in ('right', 'left') else -5 if self.aim == 'up' else 32)
        self.rect = pygame.Rect(self.x, self.y, 8, 8)

    def move(self):
        if self.flag:
            if self.aim == 'right':
                self.x += 10
            if self.aim == 'left':
                self.x -= 10
            if self.aim == 'up':
                self.y -= 10
            if self.aim == 'down':
                self.y += 10
            if 0 > self.x or self.x >= WIDTH - 3 or 0 > self.y or \
                    self.y >= HEIGHT - 3:
                self.death()
                return
            for obj in tanks_obj_arr:
                if isinstance(obj, Map) and any([0 < terrain_grid[self.x // 16][
                    self.y // 16] < 3,
                                                 0 < terrain_grid[self.x // 16][
                                                     (self.y - 3) // 16] < 3,
                                                 0 < terrain_grid[self.x // 16][
                                                     (self.y + 3) // 16] < 3,
                                                 0 < terrain_grid[(self.x + 3) // 16][
                                                     self.y // 16] < 3,
                                                 0 < terrain_grid[(self.x - 3) // 16][
                                                     self.y // 16] < 3]):
                    for x in range(self.x - 3, self.x + 4):
                        for y in range(self.y - 3, self.y + 4):
                            if terrain_grid[x // 16][y // 16] == 2:
                                terrain_grid[x // 16][y // 16] = 0
                                if self.aim == 'left' or self.aim == 'right':
                                    if terrain_grid[x // 16][y // 16 + 1] == 2:
                                        terrain_grid[x // 16][y // 16 + 1] = 0
                                    if terrain_grid[x // 16][y // 16 - 1] == 2:
                                        terrain_grid[x // 16][y // 16 - 1] = 0
                                if self.aim == 'up' or self.aim == 'down':
                                    if terrain_grid[x // 16 + 1][y // 16] == 2:
                                        terrain_grid[x // 16 + 1][y // 16] = 0
                                    if terrain_grid[x // 16 - 1][y // 16] == 2:
                                        terrain_grid[x // 16 - 1][y // 16] = 0
                    self.death()
            self.rect = pygame.Rect(self.x, self.y, 8, 8)
            self.collider_bullet_checker()

    def draw(self):
        if self.flag and terrain_grid[self.x // 16][self.y // 16] != 3:
            pygame.draw.rect(screen, RED, (self.x - 3.5, self.y - 3.5, 7, 7))

    def death(self):
        self.flag = False
        self.alive = False
        try:
            del tanks_obj_arr[tanks_obj_arr.index(self)]
        except ValueError:
            pass

    def collider_bullet_checker(self):
        for obj in tanks_obj_arr:
            if obj is not self and (isinstance(obj, Tank) or isinstance(
                    obj, Base)) \
                    and pygame.Rect.colliderect(self.rect, obj.rect):
                if isinstance(obj, Base):
                    obj.death()
                else:
                    obj.death(1)
                self.death()


class Tank:
    def __init__(self, x, y, player=False, tank_type='simple', armored_type='simple'):
        self.x = x
        self.y = y
        self.tank_type = tank_type
        self.bullet_speed = 10
        self.bullet = armored_type
        self.health = 1
        self.reload = 60
        if player:
            self.speed = 3
            if self.tank_type == 'simple':
                self.texture = load_image("assets/tank1.png", (30, 30))
            if self.tank_type == 'high_health':
                self.texture = load_image("assets/tank4.png", (30, 30))
                self.health = 3
            if self.tank_type == 'fast_tank':
                self.texture = load_image("assets/tank2.png", (30, 30))
                self.speed = 5
            if self.tank_type == 'fast_bullet':
                self.bullet_speed = 20
                self.texture = load_image("assets/tank3.png", (30, 30))
        else:
            if self.tank_type == 'simple':
                self.texture = load_image("assets/enemy1.png", (30, 30))
                self.speed = 2
            if self.tank_type == 'high_health':
                self.texture = load_image("assets/enemy4.png", (30, 30))
                self.speed = 2
                self.health = 3
            if self.tank_type == 'fast_tank':
                self.texture = load_image("assets/enemy2.png", (30, 30))
                self.speed = 4
            if self.tank_type == 'fast_bullet':
                self.bullet_speed = 20
                self.texture = load_image("assets/enemy3.png", (30, 30))
                self.speed = 2

        self.color = BLUE
        self.is_player = player
        self.aim = 'right'
        self.delay = 0
        self.count = 0
        self.alive = True
        self.rect = pygame.Rect(self.x, self.y, 32, 32)

    def move(self):
        x_direction = []
        y_direction = []
        if self.color == BLUE:
            old_x, old_y = self.x, self.y
            if self.is_player:
                self.player_move(old_x, old_y)
            else:
                for obj in tanks_obj_arr:
                    if isinstance(obj, Tank) and obj.is_player:
                        path = shortest_path(graph,
                                             (self.x // 32, self.y // 32),
                                             (obj.x // 32, obj.y // 32))
                        path2 = shortest_path(graph, (
                            (self.x + 28) // 32, (self.y + 28) // 32),
                                              (obj.x // 32, obj.y // 32))
                        if self.delay == 0:
                            tanks_obj_arr.append(
                                Bullet(self.aim, self.x, self.y, self, 'simple'))
                            self.delay = 30
                        if self.delay > 0:
                            self.delay -= 1
                        if path != [] or path2 != []:
                            if len(path) != 0:
                                x_direction = (path[1 % len(path)][0] - self.x // 32,
                                               path[1 % len(path)][1] - self.y // 32)
                            if len(path2) != 0:
                                y_direction = (path2[1 % len(path2)][0] - (
                                        self.x + 28) // 32,
                                               path2[1 % len(path2)][1] - (
                                                       self.y + 28) // 32)
                            if len(path2) > len(path):
                                if y_direction[0] == 0:
                                    if y_direction[1] == 1:
                                        self.y += self.speed
                                        self.aim = 'down'
                                    else:
                                        self.y -= self.speed
                                        self.aim = 'up'
                                else:
                                    if y_direction[0] == 1:
                                        self.x += self.speed
                                        self.aim = 'right'
                                    else:
                                        self.x -= self.speed
                                        self.aim = 'left'
                            else:
                                if x_direction[0] == 0:
                                    if x_direction[1] == 1:
                                        self.y += self.speed
                                        self.aim = 'down'
                                    else:
                                        self.y -= self.speed
                                        self.aim = 'up'
                                else:
                                    if x_direction[0] == 1:
                                        self.x += self.speed
                                        self.aim = 'right'
                                    else:
                                        self.x -= self.speed
                                        self.aim = 'left'
                if 0 < terrain_grid[self.x // 16][self.y // 16] < 3 or \
                        terrain_grid[self.x // 16][self.y // 16] == 4:
                    self.x, self.y = old_x, old_y
            self.rect = pygame.Rect(self.x, self.y, 32, 32)
            self.collider_tank_checker(old_x, old_y)

    def collider_tank_checker(self, old_x, old_y):
        if self.x >= 800 - 31:
            self.x = old_x
        if self.y >= 800 - 31:
            self.y = old_y
        for obj in tanks_obj_arr:
            if obj is not self and isinstance(obj,
                                              Tank) and \
                    pygame.Rect.colliderect(self.rect, obj.rect):
                self.x, self.y = old_x, old_y
                self.rect.x, self.rect.y = self.x, self.y
            if obj is not self and isinstance(obj,
                                              Booster) and \
                    pygame.Rect.colliderect(self.rect, obj.rect) \
                    and self.is_player:
                if obj.booster_type == "speed":
                    self.speed = 6
                if obj.booster_type == "armor":
                    self.health = 5
                if obj.booster_type == "fast_reload":
                    self.reload = 10
                obj.collected()

    def player_move(self, old_x, old_y):
        if keys[pygame.K_SPACE] and self.delay == 0:
            tanks_obj_arr.append(Bullet(self.aim, self.x, self.y, self, self.bullet))
            if self.tank_type == 'fast_bullet':
                self.delay = 30
            else:
                self.delay = self.reload
        if self.delay > 0:
            self.delay -= 1
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.aim = 'right'
        elif keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.aim = 'left'
        elif keys[pygame.K_UP]:
            self.y -= self.speed
            self.aim = 'up'
        elif keys[pygame.K_DOWN]:
            self.y += self.speed
            self.aim = 'down'
        if any([(0 < terrain_grid[(self.x + i) // 16][(self.y + j) // 16] < 3 or
                 terrain_grid[(self.x + i) // 16][(self.y + j) // 16] == 4) for i in
                range(28) for j in range(28)]):
            self.x, self.y = old_x, old_y

    def draw(self):
        if self.aim == 'left':
            screen.blit(pygame.transform.rotate(self.texture, 90),
                        (self.x - 2, self.y - 2, 28, 28))
        elif self.aim == 'right':
            screen.blit(pygame.transform.rotate(self.texture, -90),
                        (self.x - 2, self.y - 2, 28, 28))
        elif self.aim == 'down':
            screen.blit(pygame.transform.rotate(self.texture, 180),
                        (self.x - 2, self.y - 2, 28, 28))
        else:
            screen.blit(self.texture, (self.x - 2, self.y - 2, 28, 28))

    def death(self, damage):
        self.health -= damage
        if self.health <= 0:
            del tanks_obj_arr[tanks_obj_arr.index(self)]
            self.alive = False
            self.color = RED
            if self.is_player:
                global is_over
                is_over = True


class Map:
    def __init__(self, road):
        self.road = road
        self.length = 16
        self.bench = load_image("assets/leafes.png", (16, 16))
        self.wall = load_image("assets/unbreakable_wall.png", (16, 16))
        self.break_wall = load_image("assets/break_wall2.png", (16, 16))
        self.water = load_image("assets/water.png", (16, 16))

    def move(self):
        pass

    def draw(self):
        for i in range(50):
            for j in range(50):
                if self.road[i][j] == 1:
                    screen.blit(self.wall, (i * 16, j * 16, 16, 16))
                if self.road[i][j] == 2:
                    screen.blit(self.break_wall, (i * 16, j * 16, 16, 16))
                if self.road[i][j] == 3:
                    screen.blit(self.bench, (i * 16, j * 16, 16, 16))
                if self.road[i][j] == 4:
                    screen.blit(self.water, (i * 16, j * 16, 16, 16))


class Booster:
    def __init__(self, booster_type):
        self.booster_type = booster_type
        self.texture = load_image(f'assets/{booster_type}.png', (16, 16))
        self.x, self.y = random.randint(0, WIDTH) // 16, random.randint(0, HEIGHT) // 16

        while terrain_grid[self.x][self.y] != 0:
            try:
                self.x, self.y = random.randint(0, WIDTH) // 16, \
                                 random.randint(0, HEIGHT) // 16
                if terrain_grid[self.x][self.y] != 0:
                    pass
            except IndexError:
                continue

        self.rect = pygame.Rect(self.x * 16, self.y * 16, 16, 16)

    def draw(self):
        screen.blit(self.texture, (self.x * 16, self.y * 16, 16, 16))

    def move(self):
        pass

    def collected(self):
        try:
            del tanks_obj_arr[tanks_obj_arr.index(self)]
        except ValueError:
            pass


class Base:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.texture = load_image('assets/base.png', (32, 32))
        self.rect = pygame.Rect(self.x, self.y, 32, 32)

    def move(self):
        pass

    def draw(self):
        screen.blit(self.texture, (self.x, self.y - 2, 32, 32))

    @classmethod
    def death(cls):
        global is_over
        is_over = True


def MenuScreen():
    global is_start, terrain_grid, is_menu
    screen.fill(BLACK)
    level1_button = button.Button(150, 150, pygame.image.load(
        "assets/level1.png").convert_alpha(), 0.5)
    level2_button = button.Button(350, 125, pygame.image.load(
        "assets/level2.png").convert_alpha(), 0.85)
    level3_button = button.Button(170, 450, pygame.image.load(
        "assets/level3.png").convert_alpha(), 0.4)
    level4_button = button.Button(470, 450, pygame.image.load(
        "assets/level4.png").convert_alpha(), 0.4)
    my_font = pygame.font.SysFont('Comic Sans MS', 50)
    text = my_font.render(GAME_MENU_CAPTION, True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, 50))
    screen.blit(text, text_rect)

    if level1_button.draw(screen):
        f = open("maps/map1.txt", encoding="UTF-8")
        for line in f.readlines():
            terrain_grid.append(list(map(int, line.split())))
        terrain_grid = [*zip(*terrain_grid)]
        for i in range(50):
            terrain_grid[i] = list(terrain_grid[i])
        init_game_map()
        is_start = False
        is_menu = False

    if level2_button.draw(screen):
        f = open("maps/map2.txt", encoding="UTF-8")
        for line in f.readlines():
            terrain_grid.append(list(map(int, line.split())))
        terrain_grid = [*zip(*terrain_grid)]
        for i in range(50):
            terrain_grid[i] = list(terrain_grid[i])
        init_game_map()
        is_start = False
        is_menu = False

    if level3_button.draw(screen):
        f = open("maps/map3.txt", encoding="UTF-8")
        for line in f.readlines():
            terrain_grid.append(list(map(int, line.split())))
        terrain_grid = [*zip(*terrain_grid)]
        for i in range(50):
            terrain_grid[i] = list(terrain_grid[i])
        init_game_map()
        is_start = False
        is_menu = False

    if level4_button.draw(screen):
        f = open("maps/map4.txt", encoding="UTF-8")
        for line in f.readlines():
            terrain_grid.append(list(map(int, line.split())))
        terrain_grid = [*zip(*terrain_grid)]
        for i in range(50):
            terrain_grid[i] = list(terrain_grid[i])
        init_game_map()
        is_start = False
        is_menu = False


def StartScreen():
    global is_start
    screen.fill(BLACK)
    start_button = button.Button(350, 350, pygame.image.load(
        "assets/start.png").convert_alpha(), 0.1)
    if start_button.draw(screen):
        is_start = False


def show_game_end_screen(result, color):
    screen.fill(BLACK)
    font = pygame.font.Font(FONT_NAME, 30)
    text_surface = font.render(result, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = CENTER_SCREEN_POS
    screen.blit(text_surface, text_rect)
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.quit()


def init_game_map():
    global tanks_obj_arr, graph
    game_map = Map(terrain_grid)
    base = Base(12 * 32, 23 * 32)

    player_tank = Tank(12 * 32, 21 * 32, True, tank_type='simple')

    boosters = [
        Booster("armor"),
        Booster("speed"),
        Booster("fast_reload"),
        Booster("speed")
    ]
    tanks_obj_arr = [player_tank, base] + boosters

    graph = make_graph_from_map(terrain_grid)

    for i in range(5):
        enemy_x, enemy_y = random.randint(0, 24), random.randint(0, 3)
        while (enemy_x, enemy_y) not in graph.keys():
            enemy_x, enemy_y = random.randint(0, 24), random.randint(0, 3)

        tanks_obj_arr.append(Tank(enemy_x * 32, enemy_y * 32, False, tank_type="simple"))

    tanks_obj_arr.append(game_map)


def get_enemy_count():
    count = 0
    for tank in tanks_obj_arr:
        if isinstance(tank, Tank) and not tank.is_player:
            count += 1
    return count


def game_loop():
    global tanks_obj_arr, keys
    running = True

    while running:
        if is_start:
            if is_menu:
                MenuScreen()
            else:
                StartScreen()
        else:
            if is_over:
                show_game_end_screen(GAME_OVER, RED)
            if get_enemy_count() == 0:
                show_game_end_screen(GAME_WIN, GREEN)
            else:
                for tank in tanks_obj_arr:
                    tank.move()
                screen.fill(BLACK)

                for tank in tanks_obj_arr:
                    tank.draw()

        pygame.display.update()
        clock.tick(FPS)

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_CAPTION)
clock = pygame.time.Clock()

is_over = False
is_start = True
is_menu = True
terrain_grid = []
tanks_obj_arr = []
keys = []
graph = []

game_loop()
pygame.quit()
