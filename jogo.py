import pygame
import random

pygame.init()

WIDTH = 600
HEIGHT = 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Defying Gravity')

PLAYER_COLORS = [
    (0, 200, 100),
    (70, 130, 255),
    (255, 80, 80),
    (255, 200, 0),
]

PLAYER_KEYS = [
    pygame.K_SPACE,
    pygame.K_w,
    pygame.K_o,
    pygame.K_UP,
]

KEY_NAMES = ['SPACE', 'W', 'O', '↑']

class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, color, flip_key):
        pygame.sprite.Sprite.__init__(self)

        self.player_id = player_id
        self.flip_key = flip_key

        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.rect.x = 80
        self.rect.y = 0  # posicionado depois, na hora de criar

        self.vel_y = 0
        self.gravity_dir = 1

    def flip_gravity(self):
        self.gravity_dir *= -1
        self.vel_y = 0

    def update(self):
        self.vel_y += 0.8 * self.gravity_dir
        self.rect.y += self.vel_y

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y = 0

clock = pygame.time.Clock()
FPS = 30
font = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 28)

# ===== LOBBY =====
ready = [False, False, False, False]
in_lobby = True

while in_lobby:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            for i, key in enumerate(PLAYER_KEYS):
                if event.key == key:
                    ready[i] = not ready[i]  # toggle: aperta de novo pra sair
            if event.key == pygame.K_RETURN and any(ready):
                in_lobby = False

    window.fill((30, 30, 30))

    title = font.render('DEFYING GRAVITY', True, (255, 255, 255))
    window.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    for i in range(4):
        label = f'P{i+1}  [{KEY_NAMES[i]}]'
        status = 'PRONTO!' if ready[i] else 'aperte para entrar'
        color = PLAYER_COLORS[i] if ready[i] else (120, 120, 120)

        text = font.render(label, True, color)
        sub = font_small.render(status, True, color)

        y = 110 + i * 65
        pygame.draw.rect(window, color if ready[i] else (60, 60, 60),
                         (WIDTH // 2 - 150, y - 5, 300, 50), border_radius=8)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, y + 26))

    if any(ready):
        enter_text = font_small.render('ENTER para começar', True, (200, 200, 200))
        window.blit(enter_text, (WIDTH // 2 - enter_text.get_width() // 2, 375))

    pygame.display.update()

# ===== CRIANDO OS PLAYERS QUE ENTRARAM =====
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()

active_players = [i for i in range(4) if ready[i]]
num_players = len(active_players)

for slot, i in enumerate(active_players):
    p = Player(i + 1, PLAYER_COLORS[i], PLAYER_KEYS[i])
    # distribui verticalmente só entre os que entraram
    p.rect.y = (HEIGHT // (num_players + 1)) * (slot + 1) - 20
    all_sprites.add(p)
    players.add(p)

# ===== GAME LOOP =====
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

    all_sprites.update()

    window.fill((30, 30, 30))
    all_sprites.draw(window)
    pygame.display.update()

pygame.quit()