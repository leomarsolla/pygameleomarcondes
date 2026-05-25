from config import *
from classes import *


# So juntam os obstaculos numa lista, pra nao precisar repetir o append no codigo
def add_block(obs, x, y, w, h):
    obs.append(('block', x, y, w, h))

def add_grid(obs, x, y):
    obs.append(('grid', x, y))

def add_spike(obs, x, y, w, h, direcao):
    obs.append(('spike', x, y, w, h, direcao))

def add_plat(obs, x, y, w, altura=14):
    obs.append(('plat', x, y, w, altura))

def add_serra(obs, x, y):
    obs.append(('serra', x, y))

def add_laser(obs, x, y_top, altura, pulsante=False):
    obs.append(('laser', x, y_top, altura, pulsante))

def add_boost(obs, x, y):
    obs.append(('boost', x, y))

def add_buraco_chao(obs, x, w):
    obs.append(('buraco_chao', x, w))

def add_buraco_teto(obs, x, w):
    obs.append(('buraco_teto', x, w))


# Cada chunk eh um pedaco do mapa. L eh o tamanho dele.

# mapa classico---plataforma no meio com espinho em cima e embaixo, bloco e boost
def chunk_classico_a(start_x):
    L = 780
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 8, 380, 16)
    add_spike(obs, start_x + 100, HEIGHT // 2 - 30, 80, 22, 'up')
    add_spike(obs, start_x + 280, HEIGHT // 2 + 8, 80, 22, 'down')
    add_block(obs, start_x + 540, HEIGHT - 80, 60, 60)
    add_boost(obs, start_x + 670, HEIGHT - 90)
    return obs, start_x + L

def chunk_classico_b(start_x):
    L = 760
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 80, 60, 60)
    add_spike(obs, start_x + 220, 20, 70, 22, 'down')
    add_plat(obs, start_x + 360, HEIGHT // 2 - 8, 280, 16)
    add_spike(obs, start_x + 440, HEIGHT // 2 - 30, 80, 22, 'up')
    add_spike(obs, start_x + 600, HEIGHT - 42, 80, 22, 'up')
    return obs, start_x + L

def chunk_classico_c(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 90, 55, 70)
    add_spike(obs, start_x + 160, HEIGHT - 42, 60, 22, 'up')
    add_block(obs, start_x + 280, 20, 55, 70)
    add_spike(obs, start_x + 380, 20, 60, 22, 'down')
    add_plat(obs, start_x + 500, HEIGHT // 2 + 30, 200, 16)
    add_boost(obs, start_x + 640, HEIGHT - 90)
    return obs, start_x + L

def chunk_classico_d(start_x):
    L = 760
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 50, 320, 16)
    add_spike(obs, start_x + 120, HEIGHT // 2 - 72, 80, 22, 'down')
    add_spike(obs, start_x + 230, HEIGHT - 42, 70, 22, 'up')
    add_block(obs, start_x + 460, HEIGHT - 70, 55, 50)
    add_spike(obs, start_x + 600, 20, 80, 22, 'down')
    return obs, start_x + L


# usa buracos pra forcar a virar a gravidade
def chunk_aereo_a(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 + 30, 480, 18)
    add_spike(obs, start_x + 200, HEIGHT // 2 + 8, 80, 22, 'up')
    add_buraco_teto(obs, start_x + 80, 260)
    add_buraco_chao(obs, start_x + 480, 260)
    add_boost(obs, start_x + 800, HEIGHT - 90)
    return obs, start_x + L

def chunk_aereo_b(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 80, HEIGHT // 2 - 8, 460, 22)
    add_spike(obs, start_x + 200, HEIGHT // 2 - 30, 80, 22, 'up')
    add_buraco_teto(obs, start_x + 580, 240)
    add_boost(obs, start_x + 800, HEIGHT - 90)
    return obs, start_x + L

def chunk_aereo_c(start_x):
    L = 880
    obs = []
    add_plat(obs, start_x + 220, HEIGHT // 2 - 8, 420, 18)
    add_spike(obs, start_x + 280, HEIGHT // 2 + 14, 80, 22, 'down')
    add_buraco_chao(obs, start_x + 60, 260)
    add_buraco_teto(obs, start_x + 500, 240)
    add_boost(obs, start_x + 800, 40)
    return obs, start_x + L

def chunk_aereo_d(start_x):
    L = 900
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 - 50, 250, 18)
    add_plat(obs, start_x + 400, HEIGHT // 2 + 30, 280, 18)
    add_spike(obs, start_x + 500, HEIGHT // 2 + 8, 80, 22, 'up')
    add_buraco_teto(obs, start_x + 100, 240)
    add_buraco_chao(obs, start_x + 440, 280)
    return obs, start_x + L


#  paredes no chao e no teto formando um corredor central pra passar
def chunk_corredor_a(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, 20, 60, 110)
    add_block(obs, start_x + 60, HEIGHT - 130, 60, 110)
    add_buraco_chao(obs, start_x + 160, 220)
    add_block(obs, start_x + 400, 20, 60, 110)
    add_block(obs, start_x + 400, HEIGHT - 130, 60, 110)
    add_boost(obs, start_x + 570, HEIGHT // 2 - 18)
    return obs, start_x + L

def chunk_corredor_b(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, 20, 55, 130)
    add_buraco_chao(obs, start_x + 140, 220)
    add_block(obs, start_x + 380, HEIGHT - 150, 55, 130)
    add_buraco_teto(obs, start_x + 460, 220)
    return obs, start_x + L

def chunk_corredor_c(start_x):
    L = 720
    obs = []
    add_block(obs, start_x + 60, 20, 60, 120)
    add_block(obs, start_x + 60, HEIGHT - 140, 60, 120)
    add_plat(obs, start_x + 220, HEIGHT // 2 - 8, 250, 18)
    add_buraco_chao(obs, start_x + 180, 220)
    add_block(obs, start_x + 530, 20, 60, 120)
    add_block(obs, start_x + 530, HEIGHT - 140, 60, 120)
    return obs, start_x + L

def chunk_corredor_d(start_x):
    L = 740
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 130, 60, 110)
    add_block(obs, start_x + 220, 20, 60, 110)
    add_buraco_chao(obs, start_x + 320, 220)
    add_block(obs, start_x + 580, HEIGHT - 130, 60, 110)
    add_boost(obs, start_x + 670, HEIGHT - 90)
    return obs, start_x + L


# serras girando matam no chao e no teto
def chunk_serras_a(start_x):
    L = 760
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 80, 60, 60)
    add_serra(obs, start_x + 220, HEIGHT - 50)
    add_plat(obs, start_x + 340, HEIGHT // 2 - 8, 180, 18)
    add_buraco_chao(obs, start_x + 380, 220)
    add_block(obs, start_x + 620, 20, 60, 60)
    add_boost(obs, start_x + 700, HEIGHT - 90)
    return obs, start_x + L

def chunk_serras_b(start_x):
    L = 760
    obs = []
    add_serra(obs, start_x + 60, HEIGHT - 50)
    add_buraco_teto(obs, start_x + 180, 220)
    add_serra(obs, start_x + 460, 6)
    add_buraco_chao(obs, start_x + 540, 220)
    return obs, start_x + L

def chunk_serras_c(start_x):
    L = 760
    obs = []
    add_block(obs, start_x + 60, HEIGHT - 90, 50, 70)
    add_serra(obs, start_x + 220, HEIGHT - 50)
    add_buraco_teto(obs, start_x + 320, 220)
    add_serra(obs, start_x + 580, 6)
    return obs, start_x + L

def chunk_serras_d(start_x):
    L = 760
    obs = []
    add_plat(obs, start_x + 60, HEIGHT // 2 + 30, 150, 14)
    add_serra(obs, start_x + 240, HEIGHT // 2 + 5)
    add_buraco_chao(obs, start_x + 360, 220)
    add_serra(obs, start_x + 580, 6)
    add_boost(obs, start_x + 680, 40)
    return obs, start_x + L


# chunks do comeco, mais faceis, pra dar tempo do player se posicionar
def chunk_inicial_alt_a(start_x):
    L = 380
    obs = []
    add_spike(obs, start_x + 80, LANE_BOTTOMS[0] - SPIKE_H, 50, SPIKE_H, 'up')
    add_spike(obs, start_x + 80, LANE_BOTTOMS[2] - SPIKE_H, 50, SPIKE_H, 'up')
    return obs, start_x + L

def chunk_inicial_alt_b(start_x):
    L = 380
    obs = []
    add_spike(obs, start_x + 80, LANE_TOPS[1], 50, SPIKE_H, 'down')
    add_spike(obs, start_x + 80, LANE_TOPS[3], 50, SPIKE_H, 'down')
    return obs, start_x + L

def chunk_inicial_alt_c(start_x):
    L = 380
    obs = []
    add_spike(obs, start_x + 80, LANE_BOTTOMS[1] - SPIKE_H, 50, SPIKE_H, 'up')
    add_spike(obs, start_x + 80, LANE_TOPS[2], 50, SPIKE_H, 'down')
    return obs, start_x + L

def chunk_inicial_vazio(start_x):
    return [], start_x + 380


CHUNKS_INICIAIS = [
    chunk_inicial_alt_a, chunk_inicial_alt_b,
    chunk_inicial_alt_c, chunk_inicial_vazio,
]

# config de cada mapa: chunks que ele usa, cor de fundo e as imagens
MAPAS_CONFIG = {
    MAPA_CLASSICO: {
        'nome': 'CLASSICO',
        'pool': [chunk_classico_a, chunk_classico_b, chunk_classico_c, chunk_classico_d],
        'cor_fundo': (255, 240, 150),
        'bg': 'assets/bg_classico.png',
        'chao': 'assets/farm_ground_tile.png',
        'bloco': 'assets/cerca.png',
    },
    MAPA_AEREO: {
        'nome': 'AEREO',
        'pool': [chunk_aereo_a, chunk_aereo_b, chunk_aereo_c, chunk_aereo_d],
        'cor_fundo': (190, 220, 240),
        'bg': 'assets/bg_aereo.png',
        'chao': 'assets/cloud_ground_tile.png',
        'bloco': 'assets/nuvem.png',
    },
    MAPA_CORREDOR: {
        'nome': 'CORREDOR',
        'pool': [chunk_corredor_a, chunk_corredor_b, chunk_corredor_c, chunk_corredor_d],
        'cor_fundo': (250, 200, 180),
        'bg': 'assets/bg_corredor.png',
        'chao': 'assets/backrooms_floor_tile.png',
        'bloco': 'assets/wall.png',
    },
    MAPA_SERRAS: {
        'nome': 'SERRAS',
        'pool': [chunk_serras_a, chunk_serras_b, chunk_serras_c, chunk_serras_d],
        'cor_fundo': (200, 200, 220),
        'bg': 'assets/bg_serras.png',
        'chao': 'assets/wooden_floor_tile.png',
        'bloco': 'assets/wood.png',
    },
}