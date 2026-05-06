import pygame
import random
pygame.init()

WIDTH = 600
HEIGHT = 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Jogo sem nome')

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 200, 100))
        self.rect = self.image.get_rect()
        self.rect.x = 80
        self.rect.y = HEIGHT - 40

    def update(self):
        pass

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

    window.fill((255, 0, 255))
    all_sprites.draw(window)
    pygame.display.update()

    window.fill((30, 30, 30))
    all_sprites.draw(window)
    pygame.display.update()

pygame.quit() 

