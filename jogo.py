import pygame
import random
from config import *
from classes import *
from chunks import *

pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Defying Gravity')

# Imagens de fundo das telas 
bg_menu_players = pygame.image.load('assets/chicken_bg.png').convert()
bg_menu_mapa = pygame.image.load('assets/maps_bg.png').convert()
bg_vitoria = pygame.image.load('assets/podium_bg.png').convert()
bg_game_over = pygame.image.load('assets/game_over_bg.png').convert()

clock = pygame.time.Clock()
FPS = 30
font_big = pygame.font.SysFont(None, 72)
font_huge = pygame.font.SysFont(None, 180)
font_med = pygame.font.SysFont(None, 42)
font_small = pygame.font.SysFont(None, 28)
font_tiny = pygame.font.SysFont(None, 22)


# Tela inicial (1 a 4 playerss)
def menu_selecao():
    selecionando = True
    num = None

    # Musica do menu- loop infinito (-1)
    pygame.mixer.music.load('assets/menu.mpeg')
    pygame.mixer.music.play(-1)

    while selecionando:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Detecta clique do mouse em cada um dos 4 botoes
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(4):
                    box_x = 60 + i * 185
                    box_y = 320
                    if box_x <= mx <= box_x + 160 and box_y <= my <= box_y + 80:
                        num = i + 1
                        selecionando = False

            # Atalhos pelo teclado (1, 2, 3, 4)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: num = 1; selecionando = False
                if event.key == pygame.K_2: num = 2; selecionando = False
                if event.key == pygame.K_3: num = 3; selecionando = False
                if event.key == pygame.K_4: num = 4; selecionando = False

        window.blit(bg_menu_players, (0, 0))

        # Camada preta semi-transparente em cima do bg pra destacar o texto
        overlay = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        window.blit(overlay, (0, 0))

        titulo = font_big.render('DEFYING GRAVITY', True, (255, 220, 50))
        window.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 20))
        sub = font_small.render('Escolha quantos jogadores', True, (255, 255, 255))
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 90))

        # Desenha os 4 botoes de quantidade de jogadores em cores diferentes
        cores_box = [(200, 60, 60), (60, 120, 220), (60, 180, 90), (230, 180, 30)]
        for i in range(4):
            box_x = 60 + i * 185
            box_y = 320
            pygame.draw.rect(window, cores_box[i], (box_x, box_y, 160, 80), border_radius=12)
            pygame.draw.rect(window, (255, 255, 255), (box_x, box_y, 160, 80), 3, border_radius=12)
            label = font_big.render(f'{i+1}P', True, (255, 255, 255))
            window.blit(label, (box_x + 80 - label.get_width() // 2, box_y + 18))

        rodape = font_small.render('Clique ou pressione 1, 2, 3 ou 4', True, (220, 220, 220))
        window.blit(rodape, (WIDTH // 2 - rodape.get_width() // 2, 430))
        pygame.display.update()
    return num


# Tela onde o jogador escolhe qual mapa quer jogar
def menu_mapa():
    selecionando = True
    mapa = None
    cores_mapas = [(220, 180, 60), (90, 160, 220), (220, 120, 80), (130, 130, 180)]
    nomes_mapas = ['CLASSICO', 'AEREO', 'CORREDOR', 'SERRAS']

    while selecionando:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Os botoes ficam em uma grade 2x2 (2 colunas, 2 linhas)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(4):
                    col = i % 2
                    row = i // 2
                    box_x = 100 + col * 350
                    box_y = 160 + row * 160
                    if box_x <= mx <= box_x + 280 and box_y <= my <= box_y + 120:
                        mapa = i
                        selecionando = False
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_4:
                    mapa = event.key - pygame.K_1
                    selecionando = False

        window.blit(bg_menu_mapa, (0, 0))
        overlay = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        window.blit(overlay, (0, 0))
        titulo = font_big.render('ESCOLHA O MAPA', True, (255, 220, 50))
        window.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 15))
        sub = font_small.render('Clique ou pressione 1 a 4', True, (220, 220, 220))
        window.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 75))
        for i in range(4):
            col = i % 2
            row = i // 2
            box_x = 100 + col * 350
            box_y = 160 + row * 160
            s = pygame.Surface((280, 120), pygame.SRCALPHA)
            s.fill((0, 0, 0, 120))
            window.blit(s, (box_x, box_y))
            pygame.draw.rect(window, cores_mapas[i], (box_x, box_y, 280, 120), 4, border_radius=12)
            num = font_big.render(str(i + 1), True, (255, 255, 255))
            window.blit(num, (box_x + 20, box_y + 20))
            nome = font_med.render(nomes_mapas[i], True, cores_mapas[i])
            window.blit(nome, (box_x + 140 - nome.get_width() // 2, box_y + 60))
        pygame.display.update()
    return mapa


# Tela final - jogar dnv ou pra parar
def tela_fim(mensagem, cor, bg):
    showing = True
    resultado = None
    while showing:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                resultado = 'fechar'
                showing = False

            # Verifica se o clique foi no botao JOGAR DNV (verde) ou FECHAR (vermelho)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if 150 <= mx <= 370 and 380 <= my <= 450:
                    resultado = 'jogar'
                    showing = False
                if 430 <= mx <= 650 and 380 <= my <= 450:
                    resultado = 'fechar'
                    showing = False

            # Atalhos: Enter para jogar de novo, Esc para fechar
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    resultado = 'jogar'
                    showing = False
                if event.key == pygame.K_ESCAPE:
                    resultado = 'fechar'
                    showing = False

        window.blit(bg, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        window.blit(overlay, (0, 0))
        txt = font_big.render(mensagem, True, cor)
        window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 150))
        pygame.draw.rect(window, (60, 180, 60), (150, 380, 220, 70), border_radius=12)
        pygame.draw.rect(window, (255, 255, 255), (150, 380, 220, 70), 3, border_radius=12)
        label = font_med.render('JOGAR DNV', True, (255, 255, 255))
        window.blit(label, (260 - label.get_width() // 2, 403))
        pygame.draw.rect(window, (180, 60, 60), (430, 380, 220, 70), border_radius=12)
        pygame.draw.rect(window, (255, 255, 255), (430, 380, 220, 70), 3, border_radius=12)
        label2 = font_med.render('FECHAR', True, (255, 255, 255))
        window.blit(label2, (540 - label2.get_width() // 2, 403))
        pygame.display.update()
    return resultado


# Pega a lista de obstaculos que um chunk descreve e cria os sprites de verdade
# Bloco vira a sua classe
def spawnar_chunk(prox_x, blocks, spikes, serras, lasers, boosts, buracos, all_sprites, chunk_func, cor_fundo, bloco_img):
    obs_list, novo_x = chunk_func(prox_x)
    for o in obs_list:
        tipo = o[0]
        if tipo == 'block':
            _, x, y, w, h = o
            b = Block(x, y, w, h, bloco_img)
            blocks.add(b); all_sprites.add(b)
        elif tipo == 'grid':
            _, x, y = o
            g = BlocoGrid(x, y)
            blocks.add(g); all_sprites.add(g)
        elif tipo == 'plat':
            _, x, y, w, altura = o
            p = Plataforma(x, y, w, altura)
            blocks.add(p); all_sprites.add(p)
        elif tipo == 'spike':
            _, x, y, w, h, direcao = o
            s = Spike(x, y, w, h, direcao)
            spikes.add(s); all_sprites.add(s)
        elif tipo == 'serra':
            _, x, y = o
            s = Serra(x, y)
            serras.add(s); all_sprites.add(s)
        elif tipo == 'laser':
            _, x, y_top, altura, pulsante = o
            l = Laser(x, y_top, altura, pulsante)
            lasers.add(l); all_sprites.add(l)
        elif tipo == 'boost':
            _, x, y = o
            b = BoostArrow(x, y)
            boosts.add(b); all_sprites.add(b)
        elif tipo == 'buraco_chao':
            _, x, w = o
            b = BuracoChao(x, w, cor_fundo)
            buracos.add(b); all_sprites.add(b)
        elif tipo == 'buraco_teto':
            _, x, w = o
            b = BuracoTeto(x, w, cor_fundo)
            buracos.add(b); all_sprites.add(b)
    return novo_x


# Funcao principal que roda uma partida do jogo
def jogar(num_players, mapa_escolhido):
    config = MAPAS_CONFIG[mapa_escolhido]

    # Carrega as imagens visuais dos mapas
    bg_image = pygame.image.load(config['bg']).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    chao_img = pygame.image.load(config['chao']).convert_alpha()
    teto_img = pygame.transform.flip(chao_img, False, True)
    buraco_img = pygame.image.load('assets/buraco.png').convert_alpha()
    buraco_img = pygame.transform.scale(buraco_img, (220, 20))
    bloco_img = pygame.image.load(config['bloco']).convert_alpha()

    # musica dos maapas
    musicas = {
        MAPA_CLASSICO: 'assets/fazenda.mpeg',
        MAPA_AEREO: 'assets/aereo.mpeg',
        MAPA_CORREDOR: 'assets/backrooms.mpeg',
        MAPA_SERRAS: 'assets/serra.mpeg',
    }
    pygame.mixer.music.load(musicas[mapa_escolhido])
    pygame.mixer.music.play(-1)

    all_sprites = pygame.sprite.Group()
    players = pygame.sprite.Group()

    # raias certas pros jogadores
    faixas_escolhidas = posicoes_por_qnt[num_players]
    for i, faixa in enumerate(faixas_escolhidas):
        lane_top = LANE_TOPS[faixa]
        lane_bottom = LANE_BOTTOMS[faixa]
        p = Player(i + 1, PLAYER_COLORS[i], PLAYER_KEYS[i], lane_top, lane_bottom)
        all_sprites.add(p); players.add(p)

    # barreira q impede os players antes do comeco (GO)
    barrier_x = 220
    barrier_active = True
    countdown_start = pygame.time.get_ticks()
    COUNTDOWN_DURATION = 3000

    scrolling = False
    bg_offset = 0

    # Cada tipo de obstaculo tem seu proprio grupo pra facilitar colisoes
    blocks = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    serras = pygame.sprite.Group()
    lasers = pygame.sprite.Group()
    boosts = pygame.sprite.Group()
    buracos = pygame.sprite.Group()
    finish_group = pygame.sprite.Group()

    # Chao e teto ficam fixos pra n ter uns buraquinhos
    chao_fixo = ChaoTetoFixo(HEIGHT - 20)
    blocks.add(chao_fixo)
    teto_fixo = ChaoTetoFixo(0)
    blocks.add(teto_fixo)
    prox_chunk_x = WIDTH + 50

    # linhas divisorias
    plataformas_iniciais = pygame.sprite.Group()
    for i in range(1, NUM_LANES_VISUAL):
        y = i * LANE_HEIGHT
        plat = PlataformaInicial(y, LANE_LINES_LENGTH)
        plataformas_iniciais.add(plat); blocks.add(plat)

    scroll_start_time = None
    finish_spawned = False
    vencedor = None
    bg_x = 0
    game = True

    # Loop principal do jogo
    while game:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # tecla de cada playerrs
            if event.type == pygame.KEYDOWN:
                for player in players:
                    if event.key == player.flip_key:
                        player.flip_gravity()

        # contdown acaba libera a barreira e o mapa vai pra esquerda
        elapsed = pygame.time.get_ticks() - countdown_start
        if barrier_active and elapsed >= COUNTDOWN_DURATION:
            barrier_active = False
            scrolling = True
            scroll_start_time = pygame.time.get_ticks()
            for plat in plataformas_iniciais:
                plat.scrolling = True

        # Junta tudo que pode matar o player em um unico grupo
        kills_group = pygame.sprite.Group()
        for s in spikes: kills_group.add(s)
        for s in serras: kills_group.add(s)
        for l in lasers: kills_group.add(l)

        for player in players:
            player.update(players, blocks, kills_group, buracos, scrolling)

            # Trava o player na barreira durante o countdown
            if barrier_active and player.rect.right > barrier_x:
                player.rect.right = barrier_x

            # Se o player encostou no boost, ele recebe o efeito e o boost some
            for boost in pygame.sprite.spritecollide(player, boosts, True):
                player.ativar_boost()

        if scrolling:
            blocks.update(); spikes.update(); serras.update()
            lasers.update(); boosts.update(); buracos.update()
            finish_group.update()

            tempo_corrida = pygame.time.get_ticks() - scroll_start_time

            # Depois de 30s, spawna a linha de chegada e limpa obstaculos 
            if not finish_spawned and tempo_corrida >= TEMPO_ATE_FINISH:
                finish_spawned = True
                fl = FinishLine(WIDTH + 100)
                finish_group.add(fl)
                for b in list(blocks):
                    if isinstance(b, (PlataformaInicial, ChaoTetoFixo)): continue
                    if b.rect.left > WIDTH: b.kill()
                for s in list(spikes):
                    if s.rect.left > WIDTH: s.kill()
                for s in list(serras):
                    if s.rect.left > WIDTH: s.kill()
                for l in list(lasers):
                    if l.rect.left > WIDTH: l.kill()
                for b in list(boosts):
                    if b.rect.left > WIDTH: b.kill()
                for b in list(buracos):
                    if b.rect.left > WIDTH: b.kill()

            # Quem cruzar a linha de chegada primeiro vence
            for player in players:
                for fl in finish_group:
                    if player.rect.colliderect(fl.rect):
                        player.venceu = True
                        vencedor = player
                        game = False

            # ultimo q sobreviver vence
            vivos = [p for p in players if p.alive]
            if num_players > 1 and len(vivos) == 1:
                vencedor = vivos[0]; vencedor.venceu = True; game = False
            elif len(vivos) == 0:
                game = False

        if scrolling:
            # bg_x faz a imagem de fundo rolar continuamente em loop
            bg_offset = (bg_offset + SCROLL_SPEED) % 40
            bg_x -= SCROLL_SPEED
            if bg_x <= -WIDTH:
                bg_x += WIDTH

            # Spawna novo chunk quando o anterior chega na tela
            # Enquanto as plataformas iniciais estao visiveis, usa chunks faceis
            if not finish_spawned:
                prox_chunk_x -= SCROLL_SPEED
                if prox_chunk_x <= WIDTH:
                    plataforma_ainda_visivel = any(plat.rect.right > WIDTH - 100 for plat in plataformas_iniciais)
                    chunk_func = random.choice(CHUNKS_INICIAIS) if plataforma_ainda_visivel else random.choice(config['pool'])
                    prox_chunk_x = spawnar_chunk(WIDTH + 50, blocks, spikes, serras, lasers, boosts, buracos, all_sprites, chunk_func, config['cor_fundo'], bloco_img)

        # Desenha o fundo duas vezes lado a lado pra dar a ilusao de scroll infinito
        window.blit(bg_image, (bg_x, 0))
        window.blit(bg_image, (bg_x + WIDTH, 0))

        # Barreira amarela e preta do countdown
        if barrier_active:
            pygame.draw.rect(window, (40, 40, 40), (barrier_x, 0, 12, HEIGHT))
            for stripe_y in range(0, HEIGHT, 30):
                pygame.draw.rect(window, (255, 220, 0), (barrier_x, stripe_y, 12, 15))

        # Desenha os blocos usando a textura 
        for sprite in blocks:
            if isinstance(sprite, ChaoTetoFixo):
                if sprite.rect.y == 0:
                    window.blit(teto_img, (0, 0))
                else:
                    window.blit(chao_img, (0, HEIGHT - 20))
                continue
            window.blit(sprite.image, sprite.rect)

        # Os buracos do chao e do teto
        for sprite in buracos:
            if isinstance(sprite, BuracoChao):
                x = sprite.rect.x + sprite.rect.width // 2 - 110
                window.blit(buraco_img, (x, HEIGHT - 20))
            elif isinstance(sprite, BuracoTeto):
                x = sprite.rect.x + sprite.rect.width // 2 - 110
                window.blit(buraco_img, (x, 0))

        for sprite in boosts: window.blit(sprite.image, sprite.rect)
        for sprite in spikes: window.blit(sprite.image, sprite.rect)
        for sprite in lasers: window.blit(sprite.image, sprite.rect)
        for sprite in serras: window.blit(sprite.image, sprite.rect)
        for sprite in finish_group: window.blit(sprite.image, sprite.rect)
        for sprite in players: window.blit(sprite.image, sprite.rect)

        # Numeros 3, 2, 1 do countdown e o GO! depois
        if barrier_active:
            secs_left = (COUNTDOWN_DURATION - elapsed) // 1000 + 1
            if secs_left > 0:
                num_text = font_huge.render(str(secs_left), True, (255, 60, 60))
                window.blit(num_text, (WIDTH // 2 - num_text.get_width() // 2, HEIGHT // 2 - num_text.get_height() // 2))
        elif elapsed < COUNTDOWN_DURATION + 800:
            go_text = font_huge.render('GO!', True, (60, 200, 60))
            window.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - go_text.get_height() // 2))

        pygame.display.update()

    return vencedor


# Converte a cor RGB do player vencedor pro nome em portugues que vai aparecer na tela
nome_cores = {
    (255, 80, 80): 'VERMELHO',
    (70, 130, 255): 'AZUL',
    (80, 220, 100): 'VERDE',
    (255, 200, 0): 'AMARELO',
}

# Loop principal do programa: roda o jogo varias vezes ate clicar em FECHAR
rodando = True
while rodando:
    num_players = menu_selecao()
    mapa_escolhido = menu_mapa()
    vencedor = jogar(num_players, mapa_escolhido)

    if vencedor is not None:
        nome = nome_cores.get(vencedor.color, f'P{vencedor.player_id}')
        resultado = tela_fim(f'{nome} VENCEU!', vencedor.color, bg_vitoria)
    else:
        resultado = tela_fim('GAME OVER', (255, 60, 60), bg_game_over)

    if resultado == 'fechar':
        rodando = False

pygame.quit()