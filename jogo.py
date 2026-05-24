import pygame
import random

pygame.init()

# configurações da tela
WIDTH = 800
HEIGHT = 500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Defying Gravity')

# cores e teclas de cada jogador
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

# constantes do jogo
SCROLL_SPEED = 8
LANE_LINES_LENGTH = 1200
PLAYER_SIZE = 40
NUM_LANES_VISUAL = 4
TEMPO_ATE_FINISH = 30000

# classe do jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, color, flip_key, lane_top, lane_bottom):
        pygame.sprite.Sprite.__init__(self)
        self.player_id = player_id
        self.flip_key = flip_key
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(color)
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.x = 150
        self.rect.bottom = lane_bottom
        self.vel_y = 0
        self.gravity_dir = 1 # 1 cai para baixo, -1 para cima
        self.on_ground = True
        self.alive = True
        self.venceu = False

    # inverte a gravidade quando aperta tecla
    def flip_gravity(self):
        if self.on_ground:
            self.gravity_dir *= -1
            self.vel_y = 0
            self.on_ground = False

    def update(self, other_players, blocks_group, spikes_group, scrolling):
        self.vel_y += 1.2 * self.gravity_dir
        self.rect.y += self.vel_y
        landed = False

        # limite das tela
        top_limit = 0
        bottom_limit = HEIGHT

        if self.rect.bottom >= bottom_limit:
            self.rect.bottom = bottom_limit
            self.vel_y = 0
            landed = True
        if self.rect.top <= top_limit:
            self.rect.top = top_limit
            self.vel_y = 0
            landed = True

        # colisão entre jogadores
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
        # detecta por qual lado colidiu com o bloco usando a menor sobreposição
        for block in pygame.sprite.spritecollide(self, blocks_group, False):
            overlap_left = self.rect.right - block.rect.left
            overlap_right = block.rect.right - self.rect.left
            overlap_top = self.rect.bottom - block.rect.top
            overlap_bottom = block.rect.bottom - self.rect.top
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_top:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                landed = True
            elif min_overlap == overlap_bottom:
                self.rect.top = block.rect.bottom
                self.vel_y = 0
                landed = True
            elif min_overlap == overlap_left:
                self.rect.right = block.rect.left
            elif min_overlap == overlap_right:
                self.rect.left = block.rect.right

        for spike in pygame.sprite.spritecollide(self, spikes_group, False):
            self.alive = False
            self.kill()
            return
        
        # morre se empurrado para fora da tela pela esquerda
        if scrolling and self.rect.right < 0:
            self.alive = False
            self.kill()
            return

        self.on_ground = landed


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
# plataforma que divide as faixas antes do jogo começar
class PlataformaInicial(pygame.sprite.Sprite):
    def __init__(self, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((WIDTH * 3, 8))
        self.image.fill((80, 80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = y

    def update(self):
        pass

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, pointing='up'):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # desenha triângulos para formar os espinhos
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


def chunk_spike_chao(start_x):
    return [('spike', start_x, HEIGHT - 25, 70, 25, 'up')], start_x + 220

def chunk_spike_teto(start_x):
    return [('spike', start_x, 0, 70, 25, 'down')], start_x + 220

def chunk_bloco_chao(start_x):
    altura = 70
    return [('block', start_x, HEIGHT - altura, 55, altura)], start_x + 220

def chunk_bloco_teto(start_x):
    altura = 70
    return [('block', start_x, 0, 55, altura)], start_x + 220

def chunk_dois_blocos(start_x):
    obs = [
        ('block', start_x, HEIGHT - 60, 50, 60),
        ('block', start_x + 230, 0, 50, 60),
    ]
    return obs, start_x + 430

def chunk_spike_duplo(start_x):
    obs = [
        ('spike', start_x, HEIGHT - 25, 50, 25, 'up'),
        ('spike', start_x + 180, 0, 50, 25, 'down'),
    ]
    return obs, start_x + 330

def chunk_zigzag(start_x):
    obs = [
        ('block', start_x, HEIGHT - 65, 60, 65),
        ('block', start_x + 200, 0, 60, 65),
        ('block', start_x + 400, HEIGHT - 65, 60, 65),
    ]
    return obs, start_x + 580

def chunk_spike_e_bloco(start_x):
    obs = [
        ('spike', start_x, HEIGHT - 25, 60, 25, 'up'),
        ('block', start_x + 220, 0, 55, 70),
    ]
    return obs, start_x + 400

def chunk_vazio(start_x):
    return [], start_x + 280

def chunk_plataforma_espinho(start_x):
    obs = [
        # plataforma longa com espinho no meio
        ('block', start_x, HEIGHT // 2 - 10, 800, 20),
        ('spike', start_x + 800, HEIGHT // 2 - 25, 80, 25, 'up'),
        ('block', start_x + 880, HEIGHT // 2 - 10, 800, 20),
        # espinhos no chão
        ('spike', start_x + 150, HEIGHT - 25, 60, 25, 'up'),
        ('spike', start_x + 600, HEIGHT - 25, 60, 25, 'up'),
        ('spike', start_x + 1100, HEIGHT - 25, 60, 25, 'up'),
        # espinhos no teto
        ('spike', start_x + 350, 0, 60, 25, 'down'),
        ('spike', start_x + 850, 0, 60, 25, 'down'),
        ('spike', start_x + 1300, 0, 60, 25, 'down'),
        # paredes na parte de cima
        ('block', start_x + 450, HEIGHT // 2 - 120, 40, 110),
        ('block', start_x + 1200, HEIGHT // 2 - 120, 40, 110),
        # paredes na parte de baixo
        ('block', start_x + 250, HEIGHT // 2 + 10, 40, 110),
        ('block', start_x + 950, HEIGHT // 2 + 10, 40, 110),
    ]
    return obs, start_x + 2000

def chunk_parede_espinhos(start_x):
    obs = [
        ('spike', start_x, HEIGHT // 2 - 120, 50, 25, 'down'),
        ('block', start_x, HEIGHT // 2 - 95, 50, 190),
        ('spike', start_x, HEIGHT // 2 + 95, 50, 25, 'up'),
    ]
    return obs, start_x + 280

def chunk_plataforma_meio(start_x):
    obs = [
        # plataforma longa no meio
        ('block', start_x, HEIGHT // 2 - 10, 2000, 20),
        # espinhos no chão
        ('spike', start_x + 100, HEIGHT - 25, 60, 25, 'up'),
        ('spike', start_x + 400, HEIGHT - 25, 60, 25, 'up'),
        ('spike', start_x + 800, HEIGHT - 25, 60, 25, 'up'),
        ('spike', start_x + 1200, HEIGHT - 25, 60, 25, 'up'),
        # espinhos no teto
        ('spike', start_x + 250, 0, 60, 25, 'down'),
        ('spike', start_x + 600, 0, 60, 25, 'down'),
        ('spike', start_x + 1000, 0, 60, 25, 'down'),
        ('spike', start_x + 1400, 0, 60, 25, 'down'),
        # paredes na parte de cima
        ('block', start_x + 300, HEIGHT // 2 - 120, 40, 110),
        ('block', start_x + 900, HEIGHT // 2 - 120, 40, 110),
        # paredes na parte de baixo
        ('block', start_x + 550, HEIGHT // 2 + 10, 40, 110),
        ('block', start_x + 1150, HEIGHT // 2 + 10, 40, 110),
    ]
    return obs, start_x + 2200


def chunk_parede_meio(start_x):
    obs = [
        ('block', start_x, HEIGHT // 2 - 95, 50, 190),
    ]
    return obs, start_x + 280

CHUNKS = [
    chunk_spike_chao,
    chunk_spike_teto,
    chunk_bloco_chao,
    chunk_bloco_teto,
    chunk_dois_blocos,
    chunk_spike_duplo,
    chunk_zigzag,
    chunk_spike_e_bloco,
    chunk_vazio,
    chunk_plataforma_espinho,
    chunk_parede_espinhos,
    chunk_plataforma_meio,
    chunk_parede_meio,
]


clock = pygame.time.Clock()
FPS = 30
font_big = pygame.font.SysFont(None, 72)
font_huge = pygame.font.SysFont(None, 180)
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
        cores_box = [(200, 60, 60), (60, 120, 220), (60, 180, 90), (230, 180, 30)]
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


def tela_fim(mensagem, cor):
    showing = True
    while showing:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                showing = False
            if event.type == pygame.KEYDOWN:
                showing = False
        window.fill((20, 20, 20))
        txt = font_huge.render(mensagem, True, cor)
        window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))
        sub = font_small.render('Pressione qualquer tecla para sair', True, (200, 200, 200))
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 100))
        pygame.display.update()


def spawnar_chunk(prox_x, blocks, spikes, all_sprites):
    chunk_func = random.choice(CHUNKS)
    obs_list, novo_x = chunk_func(prox_x)
    for o in obs_list:
        if o[0] == 'block':
            _, x, y, w, h = o
            cor = random.choice([(220, 100, 100), (100, 200, 150), (240, 180, 80)])
            b = Block(x, y, w, h, cor)
            blocks.add(b)
            all_sprites.add(b)
        elif o[0] == 'spike':
            _, x, y, w, h, direcao = o
            s = Spike(x, y, w, h, direcao)
            spikes.add(s)
            all_sprites.add(s)
    return novo_x


num_players = menu_selecao()

all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()

visual_lane_height = HEIGHT // NUM_LANES_VISUAL

posicoes_por_qnt = {
    1: [1],
    2: [0, 3],
    3: [0, 1, 3],
    4: [0, 1, 2, 3],
}
faixas_escolhidas = posicoes_por_qnt[num_players]

for i, faixa in enumerate(faixas_escolhidas):
    lane_top = faixa * visual_lane_height
    lane_bottom = (faixa + 1) * visual_lane_height
    p = Player(i + 1, PLAYER_COLORS[i], PLAYER_KEYS[i], lane_top, lane_bottom)
    all_sprites.add(p)
    players.add(p)
    
barrier_x = 220
barrier_active = True
countdown_start = pygame.time.get_ticks()
COUNTDOWN_DURATION = 3000
scrolling = False
bg_offset = 0
lane_lines_end = barrier_x + LANE_LINES_LENGTH

blocks = pygame.sprite.Group()
spikes = pygame.sprite.Group()
finish_group = pygame.sprite.Group()
prox_chunk_x = WIDTH + 200

plataformas_iniciais = pygame.sprite.Group()
for i in range(1, NUM_LANES_VISUAL):
    y = i * visual_lane_height
    plat = PlataformaInicial(y)
    plataformas_iniciais.add(plat)
    blocks.add(plat)

scroll_start_time = None
finish_spawned = False
vencedor = None

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
            plat.kill()

    for player in players:
        player.update(players, blocks, spikes, scrolling)
        if barrier_active and player.rect.right > barrier_x:
            player.rect.right = barrier_x

    if scrolling:
        blocks.update()
        spikes.update()
        finish_group.update()

        tempo_corrida = pygame.time.get_ticks() - scroll_start_time

        if not finish_spawned and tempo_corrida >= TEMPO_ATE_FINISH:
            finish_spawned = True
            fl = FinishLine(WIDTH + 100)
            finish_group.add(fl)

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
        lane_lines_end -= SCROLL_SPEED

        prox_chunk_x -= SCROLL_SPEED
        if prox_chunk_x <= WIDTH and not finish_spawned:
            prox_chunk_x = spawnar_chunk(WIDTH + 50, blocks, spikes, all_sprites)

    window.fill((255, 240, 150))
    for x in range(-40, WIDTH + 40, 40):
        pygame.draw.line(window, (240, 220, 130), (x - bg_offset, 0), (x - bg_offset, HEIGHT), 1)

    if barrier_active:
        pygame.draw.rect(window, (40, 40, 40), (barrier_x, 0, 12, HEIGHT))
        for stripe_y in range(0, HEIGHT, 30):
            pygame.draw.rect(window, (255, 220, 0), (barrier_x, stripe_y, 12, 15))

    for sprite in blocks:
        window.blit(sprite.image, sprite.rect)
    for sprite in spikes:
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
    tela_fim(f'{nome} VENCEU!', vencedor.color)
else:
    tela_fim('GAME OVER', (255, 60, 60))

pygame.quit()