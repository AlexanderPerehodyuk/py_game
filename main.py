import os
import sys

import pygame

WIDTH = 500
HEIGHT = 500
FPS = 50


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

tile_width = tile_height = 50
player = None
clock = pygame.time.Clock()

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '1':
                Tile('forest', x, y)
            elif level[y][x] == 'e':
                Tile('empty', x, y)
                Tile('enemy', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)
        self.nap = "l"

    def update(self, *args, **kwargs):
        self.dx = 0
        self.dy = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if level[self.pos[0] - 1][self.pos[1]] != "#":
                        self.pos = (self.pos[0] - 1, self.pos[1])
                        if self.nap != 'l':
                            self.image = pygame.transform.flip(self.image, True, False)
                            self.nap = 'l'
                        self.dx = 1
            if event.key == pygame.K_RIGHT:
                if level[self.pos[0] + 1][self.pos[1]] != "#":
                        self.pos = (self.pos[0] + 1, self.pos[1])
                        if self.nap != 'r':
                            self.image = pygame.transform.flip(self.image, True, False)
                            self.nap = 'r'
                        self.dx = -1
            if event.key == pygame.K_UP:
                if level[self.pos[0]][self.pos[1] - 1] != "#":
                        self.pos = (self.pos[0], self.pos[1] - 1)
                        self.dy = 1
            if event.key == pygame.K_DOWN:
                if level[self.pos[0]][self.pos[1] + 1] != "#":
                        self.pos = (self.pos[0], self.pos[1] + 1)
                        self.dy = -1
            self.move()

    def move(self):
        camera.move(self.dx * tile_width, self.dy * tile_height)
        for sprite in tiles_group:
            camera.apply(sprite)


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


level = load_level('lvl1.txt')
player, level_x, level_y = generate_level(level)
camera = Camera()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    player.update()
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    screen.fill('black')
    all_sprites.draw(screen)
    tiles_group.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()
    pygame.display.flip()
    clock.tick(FPS)
