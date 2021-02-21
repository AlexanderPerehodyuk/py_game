import os
import sys
import random
import pygame

WIDTH = 1000
HEIGHT = 1000
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
enemy = None
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
bonus_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
font = pygame.font.SysFont("Arial", 18)
font_b = pygame.font.SysFont("Arial", 26)


def generate_level(level):
    new_player, x, y = None, None, None
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
    return new_player, y, x


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
        self.y, self.x = self.pos = (pos_y, pos_x)
        self.bonus_to_damage = 0
        self.count_kill = 0
        self.hp_bonus = 0
        self.took_damage = 0
        self.gave_damage = 0
        self.messange = ""
        self.nap = "l"

    def update(self):
        if self.health <= 0:
            player_group.remove(self)
            self.kill()
        self.dx = 0
        self.dy = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if level[self.pos[0] - 1][self.pos[1]] != "#":
                    self.pos = (self.pos[0] - 1, self.pos[1])
                    if self.nap != 'l':
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.nap = 'l'
                    self.dx = 1
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if level[self.pos[0] + 1][self.pos[1]] != "#":
                    self.pos = (self.pos[0] + 1, self.pos[1])
                    if self.nap != 'r':
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.nap = 'r'
                    self.dx = -1
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                if level[self.pos[0]][self.pos[1] - 1] != "#":
                    self.pos = (self.pos[0], self.pos[1] - 1)
                    self.dy = 1
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if level[self.pos[0]][self.pos[1] + 1] != "#":
                    self.pos = (self.pos[0], self.pos[1] + 1)
                    self.dy = -1
            self.y, self.x = self.pos
            self.move()

    def move(self):
        self.rect = self.image.get_rect().move(
            tile_width * self.y + 15, tile_height * self.x + 5)
        for sprite in tiles_group:
            camera.apply(sprite)

    def attack(self):
        if random.uniform(1.0, 10) <= self.chance_of_critical:
            if random.uniform(1.0, 10) <= self.chance_of_critical:
                given_damage = (self.health * 0.1) * 2.5 + self.bonus_to_damage
                self.health *= 2
                self.chance_of_critical -= 1
                self.messange = "critical hit and heal " + str(round(given_damage))
                self.score += 3
            else:
                given_damage = (self.health * 0.1) * 2 + self.bonus_to_damage
                if random.getrandbits(1):
                    self.chance_of_critical += 0.2
                else:
                    self.chance_of_critical -= 0.2
                self.messange = "critical hit " + str(round(given_damage))
                self.score += 2
        else:
            self.chance_of_critical += (self.chance_of_critical * 0.13)
            given_damage = (self.health * 0.1) + self.bonus_to_damage
            self.messange = "simple hit " + str(round(given_damage))
            self.score += 1
        print(given_damage, self.chance_of_critical, self.health)
        if self.chance_of_critical >= 5:
            self.chance_of_critical -= 3
            self.health += 19
            self.messange = "heal, chance of critical heat (in %) " + str(round(self.chance_of_critical * 10))
        enemy.take_damage(given_damage)
        self.gave_damage += given_damage

    def take_damage(self, given_damage):
        if random.randint(1, 100) <= 5:
            print("was block")
            self.score += 5
        else:
            self.health -= given_damage
            self.score -= 1
        self.update()
        self.took_damage += given_damage


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_y, pos_x):
        super().__init__(enemy_group, tiles_group, all_sprites)
        self.image = enemy_image
        self.nap = 'l'
        if player.score <= 100:
            p = random.uniform(0, 1.2)
        elif player.score <= 1000:
            p = random.uniform(0.5, 1.4)
        elif player.score >= 1001:
            p = random.uniform(1, 2)
        self.health = player.health * p
        print("health in time of spawn", self.health, p)
        self.rect = self.image.get_rect().move(
            tile_width * pos_y, tile_height * pos_x)
        self.y, self.x = self.position = (pos_y, pos_x)
        self.bonus_to_damage = 0
        print(self.position)
        self.dx = self.dy = 0

    def update(self):
        if self.health <= 0:
            self.kill()
            player.count_kill += 1
            player.score += 15
            return
        if player.pos != self.position:
            if player.x < self.x:
                if level[self.y][self.x - 1] != "#":
                    if self.nap != 'l':
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.nap = 'l'
                    self.x -= 1
            elif player.x < self.x:
                if level[self.y][self.x + 1] != "#":
                    if self.nap != 'r':
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.nap = 'r'
                    self.x += 1
            if player.y > self.y:
                if level[self.y + 1][self.x] != "#":
                    self.y += 1
            if player.y < self.y:
                self.y -= 1
        self.position = self.y, self.x
        self.move()
        clock.tick(10)

    def move(self):
        self.rect = self.image.get_rect().move(
            tile_width * self.y, tile_height * self.x)
        for sprite in all_sprites:
            camera.apply(sprite)

    def attack(self):
        if random.randint(1, 10) <= 2:
            given_damage = self.health * 0.1 * 2 + self.bonus_to_damage
        else:
            given_damage = self.health * 0.11 + self.bonus_to_damage
        print("enemy health", self.health)
        return given_damage

    def take_damage(self, given_damage):
        if random.randint(1, 100) <= 3:
            pass
        else:
            self.health -= given_damage
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


class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bonus_group, tiles_group, all_sprites)
        self.r_b = random.getrandbits(1)
        b_image = ["bonus_to_damage.png", "bonus_to_hp.png"]
        self.image = load_image(b_image[self.r_b])
        self.rect = self.image.get_rect().move(
            tile_width * y, tile_height * x)
        self.y, self.x = self.pos = y, x


def spawn_enemy():
    while True:
        rint_y = random.randint(1, len(level) - 1)
        rint_x = random.randint(1, len(level[rint_y]) - 1)
        if level[rint_y][rint_x] != "#":
            enemy = Enemy(rint_y, rint_x)
            return enemy


def spawn_bonus():
    while True:
        rint_y = random.randint(1, len(level) - 1)
        rint_x = random.randint(1, len(level[rint_y]) - 1)
        if level[rint_x][rint_y] == "." and enemy.position != (rint_y, rint_x):
            bonus = Bonus(rint_y, rint_x)
            return bonus


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text


def update_hp():
    hp = str(round(player.health))
    hp_text = font.render("HP - " + hp, 1, pygame.Color("red"))
    return hp_text


def update_damage():
    damage_text = font.render(player.messange, 1, pygame.Color("white"))
    return damage_text


def update_score():
    score = str(player.score)
    score_text = font.render("Score - " + score, 1, pygame.Color("white"))
    return score_text


def enemy_hp():
    hp = str(round(enemy.health))
    score_text = font.render("Enemy hp - " + hp, 1, pygame.Color("white"))
    return score_text


def update_bonus():
    bonus_text = font_b.render(bonus_messange, 1, pygame.Color("Red"))
    return bonus_text


level = load_level('lvl1.txt')
player, level_y, level_x = generate_level(level)
camera = Camera()
running = True
enemy = spawn_enemy()
bonus = None
bonus_end = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            player.update()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if player.rect.colliderect(enemy.rect):
                player.attack()
                player.take_damage(enemy.attack())
    if player.health <= 0:
        break
    bonus_group.draw(screen)
    if bonus != None:
        if bonus.rect.colliderect(player.rect):
            if bonus.r_b == 1:
                player.health += 100
                player.hp_bonus += 100
                bonus_messange = "You picked up the health bonus"
            else:
                if player.health < 1000:
                    player.bonus_to_damage += 10
                else:
                    player.bonus_to_damage += 100
                bonus_messange = "You picked up the damage bonus"
            bonus_end = pygame.time.get_ticks() + 5000
            player.score += 20
            bonus.kill()
            bonus = None
        elif bonus.rect.colliderect(enemy.rect):
            if bonus.r_b == 1:
                enemy.health += 100
                bonus_messange = "Enemy picked up the health bonus"
            else:
                if enemy.health < 1000:
                    enemy.bonus_to_damage += 10
                else:
                    enemy.bonus_to_damage += 100
                bonus_messange = "Enemy picked up the damage bonus"
            bonus_end = pygame.time.get_ticks() + 5000
            bonus.kill()
            bonus = None
    else:
        bonus = spawn_bonus()
    if enemy:
        if enemy.health <= 0:
            bonus.kill()
            enemy = spawn_enemy()
            bonus = spawn_bonus()
    else:
        enemy = spawn_enemy()
    enemy.update()
    screen.fill('black')
    all_sprites.draw(screen)
    bonus_group.draw(screen)
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    player_group.draw(screen)
    if pygame.time.get_ticks() < bonus_end:
        screen.blit(update_bonus(), (300, 400))
    screen.blit(update_fps(), (0, 0))
    screen.blit(update_hp(), (0, 20))
    screen.blit(enemy_hp(), (0, 35))
    screen.blit(update_score(), (0, 55))
    screen.blit(update_damage(), (0, 75))
    pygame.display.flip()
    clock.tick(FPS)
running = True
rip_image = load_image("death.jpg")
while running and player.health <= 0:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(rip_image, rip_image.get_rect())
    screen.blit(pygame.font.Font(None, 60).render("You died", 1, "black"), (400, 200))
    screen.blit(pygame.font.Font(None, 46).render("Your score " + str(player.score), 1, "black"), (300, 300))
    screen.blit(pygame.font.Font(None, 36).render("Your damage bonus was " + str(player.bonus_to_damage), 1, "black"),
                (300, 350))
    screen.blit(pygame.font.Font(None, 36).render("Your health bonus was " + str(player.hp_bonus), 1, "black"),
                (300, 400))
    screen.blit(pygame.font.Font(None, 36).render("Your gave  " + str(round(player.gave_damage)) + " damage",
                                                  1, "black"), (300, 450))
    screen.blit(pygame.font.Font(None, 36).render("Your killed  " + str(round(player.count_kill)) + " enemy", 1,
                                                  "black"), (300, 500))
    screen.blit(pygame.font.Font(None, 36).render("Your took  " + str(round(player.took_damage)) + " damage", 1,
                                                  "black"), (300, 550))
    pygame.display.flip()
    clock.tick(FPS)
