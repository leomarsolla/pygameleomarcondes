import pygame
import math
from config import *


class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, color, flip_key, lane_top, lane_bottom):
        pygame.sprite.Sprite.__init__(self)
        self.player_id = player_id
        self.flip_key = flip_key
        nomes_img = {
            (255, 80, 80): 'vermelho',
            (70, 130, 255): 'azul',
            (80, 220, 100): 'verde',
            (255, 200, 0): 'amarelo',
        }
        cor_nome = nomes_img[color]
        self.frames = []
        for i in range(1, 4):
            f = pygame.image.load(f'assets/player_{cor_nome}_frame{i}.png').convert_alpha()
            f = pygame.transform.scale(f, (PLAYER_SIZE, PLAYER_SIZE))
            self.frames.append(f)
        self.frame_atual = 0
        self.frame_timer = 0
        self.image = self.frames[0]
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
        self.frame_timer += 1
        if self.frame_timer >= 8:
            self.frame_timer = 0
            self.frame_atual = (self.frame_atual + 1) % 3
            self.image_original = self.frames[self.frame_atual]
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
    def __init__(self, x, y, width, height, bloco_img=None):
        pygame.sprite.Sprite.__init__(self)
        if bloco_img:
            self.image = pygame.transform.scale(bloco_img, (width, height))
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((200, 100, 100))
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