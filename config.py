import pygame

WIDTH = 800
HEIGHT = 500

# vermelho, azul, verde, amarelo
PLAYER_COLORS = [
    (255, 80, 80),
    (70, 130, 255),
    (80, 220, 100),
    (255, 200, 0),
]

# tecla de flip de cada player
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

# 30 segundos ate a linha de chegada
TEMPO_ATE_FINISH = 30000

# tamanho das linhas cinzas que dividem as raias no inicio
LANE_LINES_LENGTH = 1500

# x onde o player aparece
PLAYER_BASE_X = 150

# quanto tempo o boost dura (em frames)
BOOST_DURATION = 15

# velocidade do boost
BOOST_FORCA = 4

# limite da direita pro boost nao jogar o player pra fora
PLAYER_MAX_X = WIDTH - PLAYER_SIZE - 20

# divide a tela em 4 faixas horizontais
LANE_HEIGHT = HEIGHT // NUM_LANES_VISUAL
LANE_TOPS = [i * LANE_HEIGHT for i in range(NUM_LANES_VISUAL)]
LANE_BOTTOMS = [(i + 1) * LANE_HEIGHT for i in range(NUM_LANES_VISUAL)]

MAPA_CLASSICO = 0
MAPA_AEREO = 1
MAPA_CORREDOR = 2
MAPA_SERRAS = 3

SPIKE_H = 20

# em que raias os players nascem (depende de quantos jogadores)
posicoes_por_qnt = {
    1: [1],
    2: [0, 3],
    3: [0, 1, 3],
    4: [0, 1, 2, 3],
}