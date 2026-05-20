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

SCROLL_SPEED = 8
LANE_LINES_LENGTH = 1200

class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, color, flip_key, lane_top, lane_bottom):
        pygame.sprite.Sprite.__init__(self)

        self.player_id = player_id
        self.flip_key = flip_key
        self.lane_top = lane_top
        self.lane_bottom = lane_bottom
        self.locked_lane = True

        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.rect.x = 150
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

    def update(self, other_players, blocks_group):
        self.vel_y += 1.2 * self.gravity_dir
        self.rect.y += self.vel_y

        landed = False

        if self.locked_lane:
            top_limit = self.lane_top
            bottom_limit = self.lane_bottom
        else:
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

        for block in pygame.sprite.spritecollide(self, blocks_group, False):
            if self.rect.right > block.rect.left and self.rect.left < block.rect.left:
                self.rect.right = block.rect.left
            elif self.rect.bottom > block.rect.top and self.rect.top < block.rect.top:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                landed = True
            elif self.rect.top < block.rect.bottom and self.rect.bottom > block.rect.bottom:
                self.rect.top = block.rect.bottom
                self.vel_y = 0
                landed = True

        if self.rect.left < 0:
            self.alive = False
            self.kill()

        self.on_ground = landed

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill((80, 80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()

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


barrier_x = 220
barrier_active = True
countdown_start = pygame.time.get_ticks()
COUNTDOWN_DURATION = 3000
scrolling = False
bg_offset = 0
lane_lines_end = barrier_x + LANE_LINES_LENGTH

game = True

blocks = pygame.sprite.Group()
BLOCK_INTERVAL = 1500
last_block_time = pygame.time.get_ticks()

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

    for player in players:
        player.update(players, blocks)
        if barrier_active and player.rect.right > barrier_x:
            player.rect.right = barrier_x

    if scrolling:
        bg_offset = (bg_offset + SCROLL_SPEED) % 40
        lane_lines_end -= SCROLL_SPEED
    
        for player in players:
            if player.locked_lane and lane_lines_end <= player.rect.right:
                player.locked_lane = False

        now = pygame.time.get_ticks()
        if now - last_block_time > BLOCK_INTERVAL:
            last_block_time = now
            bw = random.randint(30, 80)  
            bh = random.randint(40, 120)
            by = random.randint(0, HEIGHT - bh) 
            b = Block(WIDTH, by, bw, bh)
            blocks.add(b)
            all_sprites.add(b)

    window.fill((255, 240, 150))

    for x in range(-40, WIDTH + 40, 40):
        pygame.draw.line(window, (240, 220, 130), (x - bg_offset, 0), (x - bg_offset, HEIGHT), 1)

    if lane_lines_end > 0:
        for i in range(1, num_players):
            y = i * lane_height
            pygame.draw.line(window, (80, 80, 80), (0, y), (lane_lines_end, y), 4)

    if barrier_active:
        pygame.draw.rect(window, (40, 40, 40), (barrier_x, 0, 12, HEIGHT))
        for stripe_y in range(0, HEIGHT, 30):
            pygame.draw.rect(window, (255, 220, 0), (barrier_x, stripe_y, 12, 15))

    if barrier_active:
        secs_left = (COUNTDOWN_DURATION - elapsed) // 1000 + 1
        if secs_left > 0:
            num_text = font_huge.render(str(secs_left), True, (255, 60, 60))
            window.blit(num_text, (WIDTH // 2 - num_text.get_width() // 2, HEIGHT // 2 - num_text.get_height() // 2))
    elif elapsed < COUNTDOWN_DURATION + 800:
        go_text = font_huge.render('GO!', True, (60, 200, 60))
        window.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - go_text.get_height() // 2))

    blocks.update()
    for sprite in blocks:
        window.blit(sprite.image, sprite.rect)

    for sprite in players:
        window.blit(sprite.image, sprite.rect)

    pygame.display.update()

pygame.quit()