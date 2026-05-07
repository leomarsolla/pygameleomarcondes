import pygame
import random
pygame.init()

WIDTH = 600
HEIGHT = 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Defying Gravity')

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 200, 100))
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.rect.y = HEIGHT - 40
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
            
game = True
clock = pygame.time.Clock()
FPS = 30

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

while game:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.flip_gravity()

    all_sprites.update()

    window.fill((30, 30, 30))
    all_sprites.draw(window)
    pygame.display.update()

pygame.quit()