import os
import sys
import random
import pygame

WIDTH = 500
HEIGHT = 500
FPS = 144

def terminate():
    pygame.quit()
    sys.exit()

def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print("Файл с изображением", fullname, "не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


pygame.init()
size = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
screen.fill('black')
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'forest': load_image('les.png'),
    'enemy': load_image('enemy.png')
}
player_image = load_image('protohero.png')
enemy_image = load_image('enemy.png')

tile_width = tile_height = 50
player = None
enemies = []
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
let_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
font = pygame.font.SysFont("Arial", 18)


def generate_level(level):
    new_player, x, y = None, None, None
    enemies = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', y, x)
            elif level[y][x] == '#':
                Tile('wall', y, x)
            elif level[y][x] == '1':
                Tile('forest', y, x)
            elif level[y][x] == '@':
                Tile('empty', y, x)
                new_player = Player(y, x)
    if len(level) > 12:
        for _ in range(5):
            rint_y = random.randint(6, len(level) - 6)
            rint_x = random.randint(6, len(level[rint_y]) - 6)
            if level[rint_y][rint_x] != "@" and level[rint_y][rint_x] != "#":
                e = Enemy(rint_y, rint_x)
                enemies.append(e)
    return new_player, enemies, y, x


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_y, pos_x):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.score = 0
        self.health = 100
        self.chance_of_critical = 3.0
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_y, pos_x)
        self.nap = "l"

    def update(self):
        if self.health <= 0:
            player_group.remove(self)
            self.kill()
        self.dx = 0
        self.dy = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if level[self.pos[0] + 1][self.pos[1]] != "#":
                    self.pos = (self.pos[0] + 1, self.pos[1])
                    if self.nap != 'l':
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.nap = 'l'
                    self.dx = -1
            if event.key == pygame.K_RIGHT:
                if level[self.pos[0] - 1][self.pos[1]] != "#":
                    self.pos = (self.pos[0] - 1, self.pos[1])
                    if self.nap != 'r':
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.nap = 'r'
                    self.dx = 1
            if event.key == pygame.K_UP:
                if level[self.pos[0]][self.pos[1] + 1] != "#":
                    self.pos = (self.pos[0], self.pos[1] - 1)
                    self.dy = -1
            if event.key == pygame.K_DOWN:
                if level[self.pos[0]][self.pos[1] - 1] != "#":
                    self.pos = (self.pos[0], self.pos[1] - 1)
                    self.dy = 1
            self.move()

    def move(self):
        camera.move(self.dx * tile_width, self.dy * tile_height)
        for sprite in player_group:
            camera.apply(sprite)

    def attack(self):
        for e in enemies:
            if self.rect.colliderect(e.rect):
                if random.randint(1, 100) <= 5:
                    given_damage = 0
                    print("was block")
                    print(given_damage, self.chance_of_critical, self.health)
                    self.score += 5
                else:
                    if random.uniform(1.0, 10) <= self.chance_of_critical:
                        if random.uniform(1.0, 10) <= self.chance_of_critical:
                            given_damage = (self.health * 0.1) * 2.5
                            self.health *= 2
                            self.chance_of_critical -= 1
                            print("was crit and + health")
                            self.score += 3
                        else:
                            given_damage = (self.health * 0.1) * 2
                            if random.getrandbits(1):
                                self.chance_of_critical += 0.2
                            else:
                                self.chance_of_critical -= 0.2
                            print("was crit")
                            self.score += 2
                    else:
                        self.chance_of_critical += (self.chance_of_critical * 0.13)
                        given_damage = (self.health * 0.1)
                        print("no crit")
                        self.score += 1
                    print(given_damage, self.chance_of_critical, self.health)
                    if self.chance_of_critical >= 5:
                        self.chance_of_critical -= 3
                        self.health += 19
                print(self.health, e.health)
                e.take_damage(given_damage)

    def take_damage(self, given_damage):
        self.health -= given_damage
        self.score -= 1
        self.update()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_y, pos_x):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.nap = 'l'
        self.health = 100
        self.rect = self.image.get_rect().move(
            tile_width * pos_y, tile_height * pos_x)
        self.position = (pos_y, pos_x)
        self.dx = self.dy = 0
        self.can_move = 0

    def update(self):
        if self.health <= 0:
            self.kill()
            enemies.remove(self)
        if self.can_move == 1:
            if self.position != player.pos:
                if player.pos[0] < self.position[0]:
                    if level[self.position[0] - 1][self.position[1]] != "#":
                        self.position = (self.position[0] - 1, self.position[1])
                        if self.nap != 'l':
                            self.image = pygame.transform.flip(self.image, True, False)
                            self.nap = 'l'
                        self.dx = -1
                elif player.pos[0] > self.position[0]:
                    if level[self.position[0] + 1][self.position[1]] != "#":
                        self.position = (self.position[0] + 1, self.position[1])
                        if self.nap != 'r':
                            self.image = pygame.transform.flip(self.image, True, False)
                            self.nap = 'r'
                        self.dx = 1
                elif player.pos[1] < self.position[1]:
                    if level[self.position[0]][self.position[1] - 1] != "#":
                        self.position = (self.position[0], self.position[1] - 1)
                        self.dy = -1
                elif player.pos[1] > self.position[1]:
                    if level[self.position[0]][self.position[1] + 1] != "#":
                        self.position = (self.position[0], self.position[1] + 1)
                        self.dy = 1
            self.move()
        else:
            self.can_move = 0
        if self.rect.colliderect(player.rect):
            pygame.time.delay(1000)
            player.take_damage(e.attack())

    def move(self):
        camera.move(self.dx * tile_width, self.dy * tile_height)
        for sprite in tiles_group:
            camera.apply(sprite)

    def attack(self):
        if random.randint(1, 10) <= 2:
            given_damage = self.health * 0.1 * 2
        else:
            given_damage = self.health * 0.1
        print("enemy health", self.health)
        return given_damage

    def take_damage(self, given_damage):
        self.health -= given_damage
        self.can_move = 0
        self.update()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)

    def move(self, x, y):
        self.dx = x
        self.dy = y


class AnimatedAttack(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text


level = load_level('lvl1.txt')
player, enemies, level_y, level_x = generate_level(level)
camera = Camera()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            player.update()
            for e in enemies:
                e.update()
                clock.tick(FPS // 10)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player.attack()
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    screen.fill('black')
    all_sprites.draw(screen)
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    player_group.draw(screen)
    screen.blit(update_fps(), (10, 0))
    pygame.display.flip()
    clock.tick(FPS)