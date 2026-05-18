import pygame
import random

pygame.init()

WIDTH = 800
HEIGHT = 500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Defying Gravity')

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

class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, color, flip_key, lane_top, lane_bottom):
        pygame.sprite.Sprite.__init__(self)

        self.player_id = player_id
        self.flip_key = flip_key
        self.lane_top = lane_top
        self.lane_bottom = lane_bottom

        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.rect.x = 80
        self.rect.bottom = lane_bottom

        self.vel_y = 0
        self.gravity_dir = 1
        self.on_ground = True
        self.alive = True

    def flip_gravity(self):
        if self.on_ground:
            self.gravity_dir *= -1
            self.vel_y = 0
            self.on_ground = False

    def update(self, other_players):
        self.vel_y += 0.8 * self.gravity_dir
        self.rect.y += self.vel_y

        landed = False

        if self.rect.bottom >= self.lane_bottom:
            self.rect.bottom = self.lane_bottom
            self.vel_y = 0
            landed = True
        if self.rect.top <= self.lane_top:
            self.rect.top = self.lane_top
            self.vel_y = 0
            landed = True

        for other in other_players:
            if other is self or not other.alive:
                continue
            if self.rect.colliderect(other.rect):
                if self.vel_y > 0:
                    self.rect.bottom = other.rect.top
                elif self.vel_y < 0:
                    self.rect.top = other.rect.bottom
                self.vel_y = 0
                landed = True

        self.on_ground = landed

clock = pygame.time.Clock()
FPS = 30
font_big = pygame.font.SysFont(None, 72)
font_med = pygame.font.SysFont(None, 42)
font_small = pygame.font.SysFont(None, 28)

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
                    box_y = 200
                    if box_x <= mx <= box_x + 160 and box_y <= my <= box_y + 160:
                        num = i + 1
                        selecionando = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    num = 1
                    selecionando = False
                if event.key == pygame.K_2:
                    num = 2
                    selecionando = False
                if event.key == pygame.K_3:
                    num = 3
                    selecionando = False
                if event.key == pygame.K_4:
                    num = 4
                    selecionando = False

        window.fill((90, 40, 130))

        titulo = font_big.render('DEFYING GRAVITY', True, (255, 255, 255))
        window.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 60))

        sub = font_small.render('Escolha quantos jogadores', True, (230, 230, 230))
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 140))

        cores_box = [
            (200, 60, 60),
            (60, 120, 220),
            (60, 180, 90),
            (230, 180, 30),
        ]

        for i in range(4):
            box_x = 60 + i * 185
            box_y = 200
            pygame.draw.rect(window, cores_box[i], (box_x, box_y, 160, 160), border_radius=20)
            pygame.draw.rect(window, (255, 255, 255), (box_x, box_y, 160, 160), 4, border_radius=20)

            label = font_big.render(f'{i+1}P', True, (255, 255, 255))
            window.blit(label, (box_x + 80 - label.get_width() // 2, box_y + 50))

        rodape = font_small.render('Clique ou pressione 1, 2, 3 ou 4', True, (220, 220, 220))
        window.blit(rodape, (WIDTH // 2 - rodape.get_width() // 2, 420))

        pygame.display.update()

    return num

num_players = menu_selecao()

all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()

lane_height = HEIGHT // num_players
for i in range(num_players):
    lane_top = i * lane_height
    lane_bottom = (i + 1) * lane_height
    p = Player(i + 1, PLAYER_COLORS[i], PLAYER_KEYS[i], lane_top, lane_bottom)
    all_sprites.add(p)
    players.add(p)

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

    for player in players:
        player.update(players)

    window.fill((30, 30, 40))

    for i in range(1, num_players):
        y = i * lane_height
        pygame.draw.line(window, (200, 200, 200), (0, y), (WIDTH, y), 3)

    for sprite in all_sprites:
        window.blit(sprite.image, sprite.rect)

    pygame.display.update()

pygame.quit()