import pygame
import random
pygame.init()

# ----- Gera tela principal
window = pygame.display.set_mode((600, 400))
pygame.display.set_caption('Jogo sem nome')

# ----- Inicia estruturas de dados
game = True

# ===== Loop principal =====
while game:
    # ----- Trata eventos
    for event in pygame.event.get():
        # ----- Verifica consequências
        if event.type == pygame.KEYUP:
            game = False

    # ----- Gera saídas
    window.fill((255, 0, 255))  # Preenche com a cor branca

    # ----- Atualiza estado do jogo
    pygame.display.update()  # Mostra o novo frame para o jogador

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados

