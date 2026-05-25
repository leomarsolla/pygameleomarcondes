import pygame

WIDTH = 800
HEIGHT = 500

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
BOOST_DURATION = 10
BOOST_FORCA = 2
PLAYER_MAX_X = WIDTH - PLAYER_SIZE - 20

LANE_HEIGHT = HEIGHT // NUM_LANES_VISUAL
LANE_TOPS = [i * LANE_HEIGHT for i in range(NUM_LANES_VISUAL)]
LANE_BOTTOMS = [(i + 1) * LANE_HEIGHT for i in range(NUM_LANES_VISUAL)]

MAPA_CLASSICO = 0
MAPA_AEREO = 1
MAPA_CORREDOR = 2
MAPA_SERRAS = 3

SPIKE_H = 20

posicoes_por_qnt = {
    1: [1],
    2: [0, 3],
    3: [0, 1, 3],
    4: [0, 1, 2, 3],
}