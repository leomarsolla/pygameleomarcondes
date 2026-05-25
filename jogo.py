import pygame
import random
import math

pygame.init()

WIDTH = 800
HEIGHT = 500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Defying Gravity')
bg_menu_players = pygame.image.load('chicken_bg.png').convert()
bg_menu_mapa = pygame.image.load('maps_bg.png').convert()
bg_vitoria = pygame.image.load('podium_bg.png').convert()
bg_game_over = pygame.image.load('game_over_bg.png').convert()

PLAYER_COLORS = [
    (255, 80, 80),
    (70, 130, 255),
    (80, 220, 100),
    (255, 200, 0),
]

PLAYER_KEYS = [
    pygame.K_SPACE,
    pygame.K_w,
    pygame.K_o,
    pygame.K_UP,
]

KEY_NAMES = ['SPACE', 'W', 'O', 'UP']

SCROLL_SPEED = 8
PLAYER_SIZE = 60
NUM_LANES_VISUAL = 4
TEMPO_ATE_FINISH = 30000
LANE_LINES_LENGTH = 1500
PLAYER_BASE_X = 150
BOOST_DURATION = 30
BOOST_FORCA = 6
PLAYER_MAX_X = WIDTH - PLAYER_SIZE - 20

LANE_HEIGHT = HEIGHT // NUM_LANES_VISUAL
LANE_TOPS = [i * LANE_HEIGHT for i in range(NUM_LANES_VISUAL)]
LANE_BOTTOMS = [(i + 1) * LANE_HEIGHT for i in range(NUM_LANES_VISUAL)]

MAPA_CLASSICO = 0
MAPA_AEREO = 1
MAPA_CORREDOR = 2
MAPA_SERRAS = 3


class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, color, flip_key, lane_top, lane_bottom):
        pygame.sprite.Sprite.__init__(self)
        self.player_id = player_id
        self.flip_key = flip_key
        nomes_img = {
            (255, 80, 80): 'player_vermelho.png',
            (70, 130, 255): 'player_azul.png',
            (80, 220, 100): 'player_verde.png',
            (255, 200, 0): 'player_amarelo.png',
        }
        self.image = pygame.image.load(nomes_img[color]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))
        self.image_original = self.image.copy()
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.x = PLAYER_BASE_X
        self.rect.bottom = lane_bottom
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        self.vel_y = 0
        self.gravity_dir = 1
        self.tem_flip = True
        self.estava_tocando = True
        self.alive = True
        self.venceu = False
        self.boost_timer = 0

    def flip_gravity(self):
        if self.tem_flip:
            self.gravity_dir *= -1
            self.vel_y = 0
            self.tem_flip = False

    def ativar_boost(self):
        self.boost_timer = BOOST_DURATION

    def update(self, other_players, blocks_group, kills_group, buracos_group, scrolling):
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y

        if self.boost_timer > 0:
            self.rect.x += BOOST_FORCA
            self.boost_timer -= 1
            if self.rect.x > PLAYER_MAX_X:
                self.rect.x = PLAYER_MAX_X

        self.vel_y += 1.0 * self.gravity_dir
        if self.gravity_dir == -1:
            self.image = pygame.transform.flip(self.image_original, False, True)
        else:
            self.image = self.image_original.copy()
            
        self.rect.y += self.vel_y
        tocando_agora = False

        if self.rect.bottom < -PLAYER_SIZE * 2:
            self.alive = False
            self.kill()
            return
        if self.rect.top > HEIGHT + PLAYER_SIZE * 2:
            self.alive = False
            self.kill()
            return

        for other in other_players:
            if other is self or not other.alive:
                continue
            if self.rect.colliderect(other.rect):
                tocando_agora = True
                if self.vel_y > 0:
                    self.rect.bottom = other.rect.top
                elif self.vel_y < 0:
                    self.rect.top = other.rect.bottom
                self.vel_y = 0

        sobre_buraco_chao = False
        sobre_buraco_teto = False
        for b in buracos_group:
            if isinstance(b, BuracoChao):
                if self.rect.right > b.rect.left and self.rect.left < b.rect.right:
                    sobre_buraco_chao = True
            elif isinstance(b, BuracoTeto):
                if self.rect.right > b.rect.left and self.rect.left < b.rect.right:
                    sobre_buraco_teto = True

        for block in pygame.sprite.spritecollide(self, blocks_group, False):
            if isinstance(block, ChaoTetoFixo):
                if block.rect.y > HEIGHT // 2 and sobre_buraco_chao:
                    continue
                if block.rect.y < HEIGHT // 2 and sobre_buraco_teto:
                    continue

            tocando_agora = True

            overlap_left = self.rect.right - block.rect.left
            overlap_right = block.rect.right - self.rect.left
            overlap_top = self.rect.bottom - block.rect.top
            overlap_bottom = block.rect.bottom - self.rect.top

            if self.vel_y > 0 and self.prev_y + self.rect.height <= block.rect.top + abs(self.vel_y):
                self.rect.bottom = block.rect.top
                self.vel_y = 0
            elif self.vel_y < 0 and self.prev_y >= block.rect.bottom - abs(self.vel_y):
                self.rect.top = block.rect.bottom
                self.vel_y = 0
            else:
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                if min_overlap == overlap_top:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                elif min_overlap == overlap_bottom:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0
                elif min_overlap == overlap_left:
                    self.rect.right = block.rect.left
                elif min_overlap == overlap_right:
                    self.rect.left = block.rect.right

        for k in pygame.sprite.spritecollide(self, kills_group, False):
            if hasattr(k, 'ativo') and not k.ativo:
                continue
            self.alive = False
            self.kill()
            return

        if scrolling and self.rect.right < 0:
            self.alive = False
            self.kill()
            return

        if tocando_agora and not self.estava_tocando:
            self.tem_flip = True

        self.estava_tocando = tocando_agora


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(200, 100, 100)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, width, height), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < -200:
            self.kill()


class BlocoGrid(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        size = 40
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (170, 170, 180), (0, 0, size, size))
        pygame.draw.rect(self.image, (100, 100, 110), (0, 0, size, size), 3)
        pygame.draw.line(self.image, (100, 100, 110), (0, 0), (size, size), 2)
        pygame.draw.line(self.image, (100, 100, 110), (size, 0), (0, size), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < -200:
            self.kill()


class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, width, altura=14):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, altura))
        self.image.fill((120, 80, 40))
        pygame.draw.rect(self.image, (60, 40, 20), (0, 0, width, altura), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < -200:
            self.kill()


class PlataformaInicial(pygame.sprite.Sprite):
    def __init__(self, y, comprimento):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((comprimento, 8))
        self.image.fill((80, 80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = y - 4
        self.scrolling = False

    def update(self):
        if self.scrolling:
            self.rect.x -= SCROLL_SPEED
            if self.rect.right < 0:
                self.kill()


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, pointing='up'):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        num_spikes = max(1, width // 20)
        spike_w = width / num_spikes
        for i in range(num_spikes):
            if pointing == 'up':
                pts = [
                    (i * spike_w, height),
                    ((i + 0.5) * spike_w, 0),
                    ((i + 1) * spike_w, height),
                ]
            else:
                pts = [
                    (i * spike_w, 0),
                    ((i + 0.5) * spike_w, height),
                    ((i + 1) * spike_w, 0),
                ]
            pygame.draw.polygon(self.image, (220, 50, 50), pts)
            pygame.draw.polygon(self.image, (0, 0, 0), pts, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ativo = True

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()


class Serra(pygame.sprite.Sprite):
    def __init__(self, x, y, raio=22):
        pygame.sprite.Sprite.__init__(self)
        self.raio = raio
        size = raio * 2 + 4
        self.center = (size // 2, size // 2)
        self.angle = 0
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self._desenhar()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ativo = True

    def _desenhar(self):
        size = self.raio * 2 + 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = self.center
        pygame.draw.circle(self.image, (180, 180, 180), (cx, cy), self.raio)
        for i in range(8):
            ang = self.angle + i * (math.pi / 4)
            px = cx + math.cos(ang) * self.raio
            py = cy + math.sin(ang) * self.raio
            px2 = cx + math.cos(ang + 0.3) * (self.raio - 6)
            py2 = cy + math.sin(ang + 0.3) * (self.raio - 6)
            px3 = cx + math.cos(ang - 0.3) * (self.raio - 6)
            py3 = cy + math.sin(ang - 0.3) * (self.raio - 6)
            pygame.draw.polygon(self.image, (220, 220, 220), [(px, py), (px2, py2), (px3, py3)])
        pygame.draw.circle(self.image, (100, 100, 100), (cx, cy), self.raio // 3)
        pygame.draw.circle(self.image, (0, 0, 0), (cx, cy), self.raio, 2)

    def update(self):
        self.rect.x -= SCROLL_SPEED
        self.angle += 0.3
        self._desenhar()
        if self.rect.right < 0:
            self.kill()


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y_top, altura, pulsante=False):
        pygame.sprite.Sprite.__init__(self)
        self.altura = altura
        self.pulsante = pulsante
        self.timer = 0
        self.ativo = False if pulsante else True
        self.image = pygame.Surface((14, self.altura), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y_top
        self._desenhar()

    def _desenhar(self):
        self.image = pygame.Surface((14, self.altura), pygame.SRCALPHA)
        if self.ativo:
            pygame.draw.rect(self.image, (255, 0, 0, 80), (0, 0, 14, self.altura))
            pygame.draw.rect(self.image, (255, 50, 50, 200), (3, 0, 8, self.altura))
            pygame.draw.rect(self.image, (255, 200, 200), (5, 0, 4, self.altura))
        else:
            pygame.draw.rect(self.image, (120, 120, 120, 180), (5, 0, 4, self.altura))

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.pulsante:
            self.timer += 1
            if self.ativo and self.timer >= 30:
                self.timer = 0
                self.ativo = False
                self._desenhar()
            elif not self.ativo and self.timer >= 60:
                self.timer = 0
                self.ativo = True
                self._desenhar()
        if self.rect.right < 0:
            self.kill()


class BoostArrow(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        w, h = 50, 36
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pts = [
            (0, h * 0.3),
            (w * 0.55, h * 0.3),
            (w * 0.55, 0),
            (w, h * 0.5),
            (w * 0.55, h),
            (w * 0.55, h * 0.7),
            (0, h * 0.7),
        ]
        pygame.draw.polygon(self.image, (255, 220, 0), pts)
        pygame.draw.polygon(self.image, (200, 100, 0), pts, 3)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()


class FinishLine(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, HEIGHT))
        self.image.fill((255, 255, 255))
        for row in range(HEIGHT // 15):
            for col in range(2):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(self.image, (0, 0, 0), (col * 15, row * 15, 15, 15))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0

    def update(self):
        self.rect.x -= SCROLL_SPEED


class ChaoTetoFixo(pygame.sprite.Sprite):
    def __init__(self, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((WIDTH, 20))
        self.image.fill((100, 70, 40))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = y

    def update(self):
        pass


class BuracoChao(pygame.sprite.Sprite):
    def __init__(self, x, width, cor_fundo):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, 22))
        self.image.fill(cor_fundo)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT - 21

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < -200:
            self.kill()


class BuracoTeto(pygame.sprite.Sprite):
    def __init__(self, x, width, cor_fundo):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, 22))
        self.image.fill(cor_fundo)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -1

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < -200:
            self.kill()


def add_block(obs, x, y, w, h):
    obs.append(('block', x, y, w, h))

def add_grid(obs, x, y):
    obs.append(('grid', x, y))

def add_spike(obs, x, y, w, h, direcao):
    obs.append(('spike', x, y, w, h, direcao))

def add_plat(obs, x, y, w, altura=14):
    obs.append(('plat', x, y, w, altura))

def add_serra(obs, x, y):
    obs.append(('serra', x, y))

def add_laser(obs, x, y_top, altura, pulsante=False):
    obs.append(('laser', x, y_top, altura, pulsante))

def add_boost(obs, x, y):
    obs.append(('boost', x, y))

def add_buraco_chao(obs, x, w):
    obs.append(('buraco_chao', x, w))

def add_buraco_teto(obs, x, w):
    obs.append(('buraco_teto', x, w))


def chunk_classico_a(start_x):
    L = 780
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 8, 380, 16)
    add_spike(obs, start_x + 100, HEIGHT // 2 - 30, 80, 22, 'up')
    add_spike(obs, start_x + 280, HEIGHT // 2 + 8, 80, 22, 'down')
    add_block(obs, start_x + 540, HEIGHT - 80, 60, 60)
    add_boost(obs, start_x + 670, HEIGHT - 90)
    return obs, start_x + L

def chunk_classico_b(start_x):
    L = 760
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 80, 60, 60)
    add_spike(obs, start_x + 220, 20, 70, 22, 'down')
    add_plat(obs, start_x + 360, HEIGHT // 2 - 8, 280, 16)
    add_spike(obs, start_x + 440, HEIGHT // 2 - 30, 80, 22, 'up')
    add_spike(obs, start_x + 600, HEIGHT - 42, 80, 22, 'up')
    return obs, start_x + L

def chunk_classico_c(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 90, 55, 70)
    add_spike(obs, start_x + 160, HEIGHT - 42, 60, 22, 'up')
    add_block(obs, start_x + 280, 20, 55, 70)
    add_spike(obs, start_x + 380, 20, 60, 22, 'down')
    add_plat(obs, start_x + 500, HEIGHT // 2 + 30, 200, 16)
    add_boost(obs, start_x + 640, HEIGHT - 90)
    return obs, start_x + L

def chunk_classico_d(start_x):
    L = 760
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 50, 320, 16)
    add_spike(obs, start_x + 120, HEIGHT // 2 - 72, 80, 22, 'down')
    add_spike(obs, start_x + 230, HEIGHT - 42, 70, 22, 'up')
    add_block(obs, start_x + 460, HEIGHT - 70, 55, 50)
    add_spike(obs, start_x + 600, 20, 80, 22, 'down')
    return obs, start_x + L


def chunk_aereo_a(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 + 30, 480, 18)
    add_spike(obs, start_x + 200, HEIGHT // 2 + 8, 80, 22, 'up')
    add_buraco_teto(obs, start_x + 80, 260)
    add_buraco_chao(obs, start_x + 480, 260)
    add_boost(obs, start_x + 800, HEIGHT - 90)
    return obs, start_x + L

def chunk_aereo_b(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 80, HEIGHT // 2 - 8, 460, 22)
    add_spike(obs, start_x + 200, HEIGHT // 2 - 30, 80, 22, 'up')
    add_buraco_teto(obs, start_x + 580, 240)
    add_boost(obs, start_x + 800, HEIGHT - 90)
    return obs, start_x + L

def chunk_aereo_c(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 220, HEIGHT // 2 - 8, 420, 18)
    add_spike(obs, start_x + 280, HEIGHT // 2 + 14, 80, 22, 'down')
    add_buraco_chao(obs, start_x + 60, 260)
    add_buraco_teto(obs, start_x + 500, 240)
    add_boost(obs, start_x + 800, 40)
    return obs, start_x + L

def chunk_aereo_d(start_x):
    L = 900
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 50, 250, 18)
    add_plat(obs, start_x + 400, HEIGHT // 2 + 30, 280, 18)
    add_spike(obs, start_x + 500, HEIGHT // 2 + 8, 80, 22, 'up')
    add_buraco_teto(obs, start_x + 100, 240)
    add_buraco_chao(obs, start_x + 440, 280)
    return obs, start_x + L


def chunk_denso_a(start_x):
    L = 720
    obs = []
    for col in range(4):
        add_grid(obs, start_x + 80 + col * 80, HEIGHT - 130)
    for col in range(4):
        add_grid(obs, start_x + 120 + col * 80, 90)
    add_buraco_chao(obs, start_x + 440, 220)
    add_boost(obs, start_x + 580, HEIGHT // 2 - 18)
    return obs, start_x + L

def chunk_denso_b(start_x):
    L = 760
    obs = []
    for col in range(5):
        add_grid(obs, start_x + 60 + col * 80, HEIGHT // 2 - 60)
    for col in range(5):
        add_grid(obs, start_x + 100 + col * 80, HEIGHT // 2 + 20)
    add_buraco_teto(obs, start_x + 80, 220)
    return obs, start_x + L

def chunk_denso_c(start_x):
    L = 740
    obs = []
    for col in range(3):
        add_grid(obs, start_x + 80 + col * 50, HEIGHT - 90)
        add_grid(obs, start_x + 80 + col * 50, HEIGHT - 50)
    for col in range(3):
        add_grid(obs, start_x + 320 + col * 50, 50)
        add_grid(obs, start_x + 320 + col * 50, 90)
    add_buraco_chao(obs, start_x + 320, 220)
    add_plat(obs, start_x + 520, HEIGHT // 2 - 10, 180, 18)
    add_boost(obs, start_x + 640, HEIGHT // 2 - 50)
    return obs, start_x + L

def chunk_denso_d(start_x):
    L = 740
    obs = []
    for col in range(4):
        offset = (col % 2) * 40
        add_grid(obs, start_x + 80 + col * 75, HEIGHT - 100 + offset)
    for col in range(4):
        offset = (col % 2) * 40
        add_grid(obs, start_x + 100 + col * 75, 60 - offset)
    add_buraco_teto(obs, start_x + 440, 220)
    add_boost(obs, start_x + 620, HEIGHT - 90)
    return obs, start_x + L


def chunk_corredor_a(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, 20, 60, 110)
    add_block(obs, start_x + 60, HEIGHT - 130, 60, 110)
    add_buraco_chao(obs, start_x + 160, 220)
    add_block(obs, start_x + 400, 20, 60, 110)
    add_block(obs, start_x + 400, HEIGHT - 130, 60, 110)
    add_boost(obs, start_x + 570, HEIGHT // 2 - 18)
    return obs, start_x + L

def chunk_corredor_b(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, 20, 55, 130)
    add_buraco_chao(obs, start_x + 140, 220)
    add_block(obs, start_x + 380, HEIGHT - 150, 55, 130)
    add_buraco_teto(obs, start_x + 460, 220)
    return obs, start_x + L

def chunk_corredor_c(start_x):
    L = 720
    obs = []
    add_block(obs, start_x + 60, 20, 60, 120)
    add_block(obs, start_x + 60, HEIGHT - 140, 60, 120)
    add_plat(obs, start_x + 220, HEIGHT // 2 - 8, 250, 18)
    add_buraco_chao(obs, start_x + 180, 220)
    add_block(obs, start_x + 530, 20, 60, 120)
    add_block(obs, start_x + 530, HEIGHT - 140, 60, 120)
    return obs, start_x + L

def chunk_corredor_d(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 130, 60, 110)
    add_block(obs, start_x + 220, 20, 60, 110)
    add_buraco_chao(obs, start_x + 320, 220)
    add_block(obs, start_x + 580, HEIGHT - 130, 60, 110)
    add_boost(obs, start_x + 670, HEIGHT - 90)
    return obs, start_x + L


def chunk_serras_a(start_x):
    L = 760
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 80, 60, 60)
    add_serra(obs, start_x + 220, HEIGHT - 50)
    add_plat(obs, start_x + 340, HEIGHT // 2 - 8, 180, 18)
    add_buraco_chao(obs, start_x + 380, 220)
    add_block(obs, start_x + 620, 20, 60, 60)
    add_boost(obs, start_x + 700, HEIGHT - 90)
    return obs, start_x + L

def chunk_serras_b(start_x):
    L = 760
    obs = []
    add_serra(obs, start_x + 60, HEIGHT - 50)
    add_buraco_teto(obs, start_x + 180, 220)
    add_serra(obs, start_x + 460, 6)
    add_buraco_chao(obs, start_x + 540, 220)
    return obs, start_x + L

def chunk_serras_c(start_x):
    L = 760
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 90, 50, 70)
    add_serra(obs, start_x + 220, HEIGHT - 50)
    add_buraco_teto(obs, start_x + 320, 220)
    add_serra(obs, start_x + 580, 6)
    return obs, start_x + L

def chunk_serras_d(start_x):
    L = 760
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 + 30, 150, 14)
    add_serra(obs, start_x + 240, HEIGHT // 2 + 5)
    add_buraco_chao(obs, start_x + 360, 220)
    add_serra(obs, start_x + 580, 6)
    add_boost(obs, start_x + 680, 40)
    return obs, start_x + L


def chunk_lasers_a(start_x):
    L = 780
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 80, 60, 60)
    add_buraco_chao(obs, start_x + 180, 220)
    add_laser(obs, start_x + 440, HEIGHT // 2 - 60, 120, False)
    add_block(obs, start_x + 580, 20, 60, 60)
    add_plat(obs, start_x + 540, HEIGHT // 2 + 30, 130, 18)
    add_boost(obs, start_x + 690, HEIGHT - 90)
    return obs, start_x + L

def chunk_lasers_b(start_x):
    L = 760
    obs = []
    add_laser(obs, start_x + 120, 20, HEIGHT - 40, True)
    add_buraco_chao(obs, start_x + 240, 220)
    add_block(obs, start_x + 500, 20, 55, 70)
    add_laser(obs, start_x + 620, 20, HEIGHT - 40, True)
    return obs, start_x + L

def chunk_lasers_c(start_x):
    L = 780
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 70, 55, 50)
    add_laser(obs, start_x + 200, HEIGHT // 2 - 80, 160, False)
    add_buraco_teto(obs, start_x + 340, 220)
    add_plat(obs, start_x + 380, HEIGHT // 2 + 50, 130, 18)
    add_laser(obs, start_x + 590, HEIGHT // 2 - 80, 160, False)
    add_block(obs, start_x + 680, 20, 55, 60)
    return obs, start_x + L

def chunk_lasers_d(start_x):
    L = 780
    obs = []
    add_laser(obs, start_x + 100, 20, HEIGHT - 40, True)
    add_block(obs, start_x + 220, HEIGHT - 80, 55, 60)
    add_buraco_teto(obs, start_x + 340, 220)
    add_laser(obs, start_x + 600, 20, HEIGHT - 40, True)
    add_boost(obs, start_x + 670, HEIGHT - 90)
    return obs, start_x + L


def chunk_caos_a(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 8, 320, 18)
    add_serra(obs, start_x + 200, HEIGHT - 50)
    add_buraco_chao(obs, start_x + 280, 240)
    add_laser(obs, start_x + 540, HEIGHT // 2 - 60, 120, True)
    for col in range(3):
        add_grid(obs, start_x + 620 + col * 50, 100)
    add_boost(obs, start_x + 800, HEIGHT - 90)
    return obs, start_x + L

def chunk_caos_b(start_x):
    L = 900
    obs = []
    add_serra(obs, start_x + 60, 6)
    add_buraco_teto(obs, start_x + 140, 240)
    for col in range(3):
        add_grid(obs, start_x + 420 + col * 50, HEIGHT - 100)
    add_laser(obs, start_x + 600, HEIGHT // 2 - 70, 140, False)
    add_buraco_chao(obs, start_x + 700, 220)
    return obs, start_x + L

def chunk_caos_c(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 8, 400, 18)
    add_spike(obs, start_x + 100, HEIGHT // 2 - 30, 80, 22, 'up')
    add_spike(obs, start_x + 280, HEIGHT // 2 + 10, 80, 22, 'down')
    add_buraco_chao(obs, start_x + 500, 240)
    add_laser(obs, start_x + 580, 20, HEIGHT - 40, True)
    add_serra(obs, start_x + 740, HEIGHT - 50)
    add_boost(obs, start_x + 820, HEIGHT // 2 - 18)
    return obs, start_x + L

def chunk_caos_d(start_x):
    L = 920
    obs = []
    for col in range(2):
        add_grid(obs, start_x + 80 + col * 50, HEIGHT - 130)
    add_buraco_chao(obs, start_x + 220, 240)
    add_laser(obs, start_x + 480, 20, HEIGHT - 40, True)
    add_serra(obs, start_x + 620, HEIGHT - 50)
    add_buraco_teto(obs, start_x + 580, 240)
    return obs, start_x + L


SPIKE_H = 20

def chunk_inicial_alt_a(start_x):
    L = 380
    obs = []
    add_spike(obs, start_x + 80, LANE_BOTTOMS[0] - SPIKE_H, 50, SPIKE_H, 'up')
    add_spike(obs, start_x + 80, LANE_BOTTOMS[2] - SPIKE_H, 50, SPIKE_H, 'up')
    return obs, start_x + L

def chunk_inicial_alt_b(start_x):
    L = 380
    obs = []
    add_spike(obs, start_x + 80, LANE_TOPS[1], 50, SPIKE_H, 'down')
    add_spike(obs, start_x + 80, LANE_TOPS[3], 50, SPIKE_H, 'down')
    return obs, start_x + L

def chunk_inicial_alt_c(start_x):
    L = 380
    obs = []
    add_spike(obs, start_x + 80, LANE_BOTTOMS[1] - SPIKE_H, 50, SPIKE_H, 'up')
    add_spike(obs, start_x + 80, LANE_TOPS[2], 50, SPIKE_H, 'down')
    return obs, start_x + L

def chunk_inicial_vazio(start_x):
    L = 380
    obs = []
    return obs, start_x + L


CHUNKS_INICIAIS = [
    chunk_inicial_alt_a, chunk_inicial_alt_b,
    chunk_inicial_alt_c, chunk_inicial_vazio,
]


MAPAS_CONFIG = {
    MAPA_CLASSICO: {
        'nome': 'CLASSICO',
        'pool': [chunk_classico_a, chunk_classico_b, chunk_classico_c, chunk_classico_d],
        'cor_fundo': (255, 240, 150),
        'cor_linhas': (240, 220, 130),
        'bg': 'bg_classico.png',
        'chao': 'farm_ground_tile.png',
    },
    MAPA_AEREO: {
        'nome': 'AEREO',
        'pool': [chunk_aereo_a, chunk_aereo_b, chunk_aereo_c, chunk_aereo_d],
        'cor_fundo': (190, 220, 240),
        'cor_linhas': (170, 200, 220),
        'bg': 'bg_aereo.png',
        'chao': 'cloud_ground_tile.png',
    },
    MAPA_CORREDOR: {
        'nome': 'CORREDOR',
        'pool': [chunk_corredor_a, chunk_corredor_b, chunk_corredor_c, chunk_corredor_d],
        'cor_fundo': (250, 200, 180),
        'cor_linhas': (230, 180, 160),
        'bg': 'bg_corredor.png',
        'chao': 'backrooms_floor_tile.png',
    },
    MAPA_SERRAS: {
        'nome': 'SERRAS',
        'pool': [chunk_serras_a, chunk_serras_b, chunk_serras_c, chunk_serras_d],
        'cor_fundo': (200, 200, 220),
        'cor_linhas': (180, 180, 200),
        'bg': 'bg_serras.png',
        'chao': 'wooden_floor_tile.png',
    },
}


clock = pygame.time.Clock()
FPS = 30
font_big = pygame.font.SysFont(None, 72)
font_huge = pygame.font.SysFont(None, 180)
font_med = pygame.font.SysFont(None, 42)
font_small = pygame.font.SysFont(None, 28)
font_tiny = pygame.font.SysFont(None, 22)


def menu_selecao():
    selecionando = True
    num = None
    while selecionando:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(4):
                    box_x = 60 + i * 185
                    box_y = 320
                    if box_x <= mx <= box_x + 160 and box_y <= my <= box_y + 80:
                        num = i + 1
                        selecionando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: num = 1; selecionando = False
                if event.key == pygame.K_2: num = 2; selecionando = False
                if event.key == pygame.K_3: num = 3; selecionando = False
                if event.key == pygame.K_4: num = 4; selecionando = False

        window.blit(bg_menu_players, (0, 0))

        # overlay escuro no topo
        overlay = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        window.blit(overlay, (0, 0))

        titulo = font_big.render('DEFYING GRAVITY', True, (255, 220, 50))
        window.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 20))
        sub = font_small.render('Escolha quantos jogadores', True, (255, 255, 255))
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 90))

        cores_box = [(200, 60, 60), (60, 120, 220), (60, 180, 90), (230, 180, 30)]
        for i in range(4):
            box_x = 60 + i * 185
            box_y = 320
            pygame.draw.rect(window, cores_box[i], (box_x, box_y, 160, 80), border_radius=12)
            pygame.draw.rect(window, (255, 255, 255), (box_x, box_y, 160, 80), 3, border_radius=12)
            label = font_big.render(f'{i+1}P', True, (255, 255, 255))
            window.blit(label, (box_x + 80 - label.get_width() // 2, box_y + 18))

        rodape = font_small.render('Clique ou pressione 1, 2, 3 ou 4', True, (220, 220, 220))
        window.blit(rodape, (WIDTH // 2 - rodape.get_width() // 2, 430))
        pygame.display.update()
    return num


def menu_mapa():
    selecionando = True
    mapa = None
    cores_mapas = [
        (220, 180, 60), (90, 160, 220), (220, 120, 80), (130, 130, 180),
    ]
    nomes_mapas = ['CLASSICO', 'AEREO', 'CORREDOR', 'SERRAS']
    while selecionando:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(4):
                    col = i % 2
                    row = i // 2
                    box_x = 100 + col * 350
                    box_y = 160 + row * 160
                    if box_x <= mx <= box_x + 280 and box_y <= my <= box_y + 120:
                        mapa = i
                        selecionando = False
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_4:
                    mapa = event.key - pygame.K_1
                    selecionando = False

        window.blit(bg_menu_mapa, (0, 0))

        overlay = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        window.blit(overlay, (0, 0))

        titulo = font_big.render('ESCOLHA O MAPA', True, (255, 220, 50))
        window.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 15))
        sub = font_small.render('Clique ou pressione 1 a 4', True, (220, 220, 220))
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 75))

        for i in range(4):
            col = i % 2
            row = i // 2
            box_x = 100 + col * 350
            box_y = 160 + row * 160
            s = pygame.Surface((280, 120), pygame.SRCALPHA)
            s.fill((0, 0, 0, 120))
            window.blit(s, (box_x, box_y))
            pygame.draw.rect(window, cores_mapas[i], (box_x, box_y, 280, 120), 4, border_radius=12)
            num = font_big.render(str(i + 1), True, (255, 255, 255))
            window.blit(num, (box_x + 20, box_y + 20))
            nome = font_med.render(nomes_mapas[i], True, cores_mapas[i])
            window.blit(nome, (box_x + 140 - nome.get_width() // 2, box_y + 60))

        pygame.display.update()
    return mapa


def tela_fim(mensagem, cor, bg):
    showing = True
    resultado = None
    while showing:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                resultado = 'fechar'
                showing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # botão jogar novamente
                if 150 <= mx <= 370 and 380 <= my <= 450:
                    resultado = 'jogar'
                    showing = False
                # botão fechar
                if 430 <= mx <= 650 and 380 <= my <= 450:
                    resultado = 'fechar'
                    showing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    resultado = 'jogar'
                    showing = False
                if event.key == pygame.K_ESCAPE:
                    resultado = 'fechar'
                    showing = False

        window.blit(bg, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        window.blit(overlay, (0, 0))

        txt = font_huge.render(mensagem, True, cor)
        window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 150))

        # botão jogar novamente
        pygame.draw.rect(window, (60, 180, 60), (150, 380, 220, 70), border_radius=12)
        pygame.draw.rect(window, (255, 255, 255), (150, 380, 220, 70), 3, border_radius=12)
        label = font_med.render('JOGAR DNV', True, (255, 255, 255))
        window.blit(label, (260 - label.get_width() // 2, 403))

        # botão fechar
        pygame.draw.rect(window, (180, 60, 60), (430, 380, 220, 70), border_radius=12)
        pygame.draw.rect(window, (255, 255, 255), (430, 380, 220, 70), 3, border_radius=12)
        label2 = font_med.render('FECHAR', True, (255, 255, 255))
        window.blit(label2, (540 - label2.get_width() // 2, 403))

        pygame.display.update()
    return resultado


def spawnar_chunk(prox_x, blocks, spikes, serras, lasers, boosts, buracos, all_sprites, chunk_func, cor_fundo):
    obs_list, novo_x = chunk_func(prox_x)
    for o in obs_list:
        tipo = o[0]
        if tipo == 'block':
            _, x, y, w, h = o
            cor = random.choice([(180, 110, 80), (110, 160, 130), (200, 160, 90)])
            b = Block(x, y, w, h, cor)
            blocks.add(b)
            all_sprites.add(b)
        elif tipo == 'grid':
            _, x, y = o
            g = BlocoGrid(x, y)
            blocks.add(g)
            all_sprites.add(g)
        elif tipo == 'plat':
            _, x, y, w, altura = o
            p = Plataforma(x, y, w, altura)
            blocks.add(p)
            all_sprites.add(p)
        elif tipo == 'spike':
            _, x, y, w, h, direcao = o
            s = Spike(x, y, w, h, direcao)
            spikes.add(s)
            all_sprites.add(s)
        elif tipo == 'serra':
            _, x, y = o
            s = Serra(x, y)
            serras.add(s)
            all_sprites.add(s)
        elif tipo == 'laser':
            _, x, y_top, altura, pulsante = o
            l = Laser(x, y_top, altura, pulsante)
            lasers.add(l)
            all_sprites.add(l)
        elif tipo == 'boost':
            _, x, y = o
            b = BoostArrow(x, y)
            boosts.add(b)
            all_sprites.add(b)
        elif tipo == 'buraco_chao':
            _, x, w = o
            b = BuracoChao(x, w, cor_fundo)
            buracos.add(b)
            all_sprites.add(b)
        elif tipo == 'buraco_teto':
            _, x, w = o
            b = BuracoTeto(x, w, cor_fundo)
            buracos.add(b)
            all_sprites.add(b)
    return novo_x


num_players = menu_selecao()
mapa_escolhido = menu_mapa()
config = MAPAS_CONFIG[mapa_escolhido]
bg_image = pygame.image.load(config['bg']).convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
chao_img = pygame.image.load(config['chao']).convert_alpha()
teto_img = pygame.transform.flip(chao_img, False, True)
buraco_img = pygame.image.load('buraco.png').convert_alpha()
buraco_img = pygame.transform.scale(buraco_img, (220, 20))

all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()

posicoes_por_qnt = {
    1: [1],
    2: [0, 3],
    3: [0, 1, 3],
    4: [0, 1, 2, 3],
}
faixas_escolhidas = posicoes_por_qnt[num_players]

for i, faixa in enumerate(faixas_escolhidas):
    lane_top = LANE_TOPS[faixa]
    lane_bottom = LANE_BOTTOMS[faixa]
    p = Player(i + 1, PLAYER_COLORS[i], PLAYER_KEYS[i], lane_top, lane_bottom)
    all_sprites.add(p)
    players.add(p)

barrier_x = 220
barrier_active = True
countdown_start = pygame.time.get_ticks()
COUNTDOWN_DURATION = 3000
scrolling = False
bg_offset = 0

blocks = pygame.sprite.Group()
spikes = pygame.sprite.Group()
serras = pygame.sprite.Group()
lasers = pygame.sprite.Group()
boosts = pygame.sprite.Group()
buracos = pygame.sprite.Group()
finish_group = pygame.sprite.Group()

chao_fixo = ChaoTetoFixo(HEIGHT - 20)
blocks.add(chao_fixo)
teto_fixo = ChaoTetoFixo(0)
blocks.add(teto_fixo)

prox_chunk_x = WIDTH + 50

plataformas_iniciais = pygame.sprite.Group()
for i in range(1, NUM_LANES_VISUAL):
    y = i * LANE_HEIGHT
    plat = PlataformaInicial(y, LANE_LINES_LENGTH)
    plataformas_iniciais.add(plat)
    blocks.add(plat)

scroll_start_time = None
finish_spawned = False
vencedor = None
bg_x = 0

game = True

while game:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.KEYDOWN:
            for player in players:
                if event.key == player.flip_key:
                    player.flip_gravity()

    elapsed = pygame.time.get_ticks() - countdown_start
    if barrier_active and elapsed >= COUNTDOWN_DURATION:
        barrier_active = False
        scrolling = True
        scroll_start_time = pygame.time.get_ticks()
        for plat in plataformas_iniciais:
            plat.scrolling = True

    kills_group = pygame.sprite.Group()
    for s in spikes:
        kills_group.add(s)
    for s in serras:
        kills_group.add(s)
    for l in lasers:
        kills_group.add(l)

    for player in players:
        player.update(players, blocks, kills_group, buracos, scrolling)
        if barrier_active and player.rect.right > barrier_x:
            player.rect.right = barrier_x

        for boost in pygame.sprite.spritecollide(player, boosts, True):
            player.ativar_boost()

    if scrolling:
        blocks.update()
        spikes.update()
        serras.update()
        lasers.update()
        boosts.update()
        buracos.update()
        finish_group.update()

        tempo_corrida = pygame.time.get_ticks() - scroll_start_time

        if not finish_spawned and tempo_corrida >= TEMPO_ATE_FINISH:
            finish_spawned = True
            fl = FinishLine(WIDTH + 100)
            finish_group.add(fl)

            for b in list(blocks):
                if isinstance(b, (PlataformaInicial, ChaoTetoFixo)):
                    continue
                if b.rect.left > WIDTH:
                    b.kill()
            for s in list(spikes):
                if s.rect.left > WIDTH:
                    s.kill()
            for s in list(serras):
                if s.rect.left > WIDTH:
                    s.kill()
            for l in list(lasers):
                if l.rect.left > WIDTH:
                    l.kill()
            for b in list(boosts):
                if b.rect.left > WIDTH:
                    b.kill()
            for b in list(buracos):
                if b.rect.left > WIDTH:
                    b.kill()

        for player in players:
            for fl in finish_group:
                if player.rect.colliderect(fl.rect):
                    player.venceu = True
                    vencedor = player
                    game = False

        vivos = [p for p in players if p.alive]
        if num_players > 1 and len(vivos) == 1:
            vencedor = vivos[0]
            vencedor.venceu = True
            game = False
        elif len(vivos) == 0:
            game = False

    if scrolling:
        bg_offset = (bg_offset + SCROLL_SPEED) % 40
        bg_x -= SCROLL_SPEED
        if bg_x <= -WIDTH:
            bg_x += WIDTH
        if not finish_spawned:
            prox_chunk_x -= SCROLL_SPEED
            if prox_chunk_x <= WIDTH:
                plataforma_ainda_visivel = False
                for plat in plataformas_iniciais:
                    if plat.rect.right > WIDTH - 100:
                        plataforma_ainda_visivel = True
                        break
                if plataforma_ainda_visivel:
                    chunk_func = random.choice(CHUNKS_INICIAIS)
                else:
                    chunk_func = random.choice(config['pool'])
                prox_chunk_x = spawnar_chunk(WIDTH + 50, blocks, spikes, serras, lasers, boosts, buracos, all_sprites, chunk_func, config['cor_fundo'])

    window.blit(bg_image, (bg_x, 0))
    window.blit(bg_image, (bg_x + WIDTH, 0))

    if barrier_active:
        pygame.draw.rect(window, (40, 40, 40), (barrier_x, 0, 12, HEIGHT))
        for stripe_y in range(0, HEIGHT, 30):
            pygame.draw.rect(window, (255, 220, 0), (barrier_x, stripe_y, 12, 15))

    for sprite in blocks:
        if isinstance(sprite, ChaoTetoFixo):
            if sprite.rect.y == 0:
                window.blit(teto_img, (0, 0))
            else:
                window.blit(chao_img, (0, HEIGHT - 20))
            continue
        window.blit(sprite.image, sprite.rect)
    for sprite in buracos:
        if isinstance(sprite, BuracoChao):
            x = sprite.rect.x + sprite.rect.width // 2 - 110
            window.blit(buraco_img, (x, HEIGHT - 20))
        elif isinstance(sprite, BuracoTeto):
                x = sprite.rect.x + sprite.rect.width // 2 - 110
                window.blit(buraco_img, (x, 0))
    for sprite in boosts:
        window.blit(sprite.image, sprite.rect)
    for sprite in spikes:
        window.blit(sprite.image, sprite.rect)
    for sprite in lasers:
        window.blit(sprite.image, sprite.rect)
    for sprite in serras:
        window.blit(sprite.image, sprite.rect)
    for sprite in finish_group:
        window.blit(sprite.image, sprite.rect)
    for sprite in players:
        window.blit(sprite.image, sprite.rect)

    if barrier_active:
        secs_left = (COUNTDOWN_DURATION - elapsed) // 1000 + 1
        if secs_left > 0:
            num_text = font_huge.render(str(secs_left), True, (255, 60, 60))
            window.blit(num_text, (WIDTH // 2 - num_text.get_width() // 2, HEIGHT // 2 - num_text.get_height() // 2))
    elif elapsed < COUNTDOWN_DURATION + 800:
        go_text = font_huge.render('GO!', True, (60, 200, 60))
        window.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - go_text.get_height() // 2))

    pygame.display.update()

if vencedor is not None:
    nome_cores = {
        (255, 80, 80): 'VERMELHO',
        (70, 130, 255): 'AZUL',
        (80, 220, 100): 'VERDE',
        (255, 200, 0): 'AMARELO',
    }
    nome = nome_cores.get(vencedor.color, f'P{vencedor.player_id}')
    resultado = tela_fim(f'{nome} VENCEU!', vencedor.color, bg_vitoria)
else:
    resultado = tela_fim('GAME OVER', (255, 60, 60), bg_game_over)

if resultado == 'fechar':
    pygame.quit()