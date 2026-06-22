# settings.py - Configurações GLOBAIS do Motor do Jogo

import pygame
import os
import sys

# Inicializa o Pygame
pygame.init()

# Resolução lógica interna do jogo (lobby e fases)
# Toda a renderização é feita nesta resolução — o pygame.SCALED
# escala automaticamente para o tamanho real da janela.
LARGURA_TELA = 1280
ALTURA_TELA = 720

# Configurações da Tela
WIDTH, HEIGHT = 1280, 720
WORLD_WIDTH, WORLD_HEIGHT = 1280, 720

# Cria a tela inicial com RESIZABLE + SCALED se ela ainda não existir
screen = pygame.display.get_surface()
if screen is None:
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    except pygame.error:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Objetivos Globais")
clock = pygame.time.Clock()

# Fontes
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 40)
door_font = pygame.font.Font(None, 36)

# ========================================================================= #
# Mapeamento de Fases Ativas e Hitboxes (Baseado nas 5 Parcelas da Imagem)
# ========================================================================= #

# Mantemos apenas as 5 ODS que possuem arquivos e lógicas implementadas no main
ODS_NAMES = {
    1: "1. Vitalidade",             # Parcela Favela / Urbana
    2: "2. A poluição já é visivel...",    # Parcela Caverna / Laboratório
    3: "3. Situações Desiguais: Sede e Fome!",       # Parcela Indústria / Poluição
    4: "4. Energia!",       # Parcela Sertão / Seca
    5: "5. A verdade!"     # Parcela Central / Templo Celestial
}

# Cores oficiais correspondentes das 5 ODS ativas
ODS_COLORS = {
    1: (229, 36, 59),
    2: (253, 105, 37),
    3: (38, 189, 226),
    4: (252, 195, 11),
    5: (0, 104, 157)
}

# Configurações de colisão circular personalizadas para cada grande região (1280x720)
# Formato: id_ods: ((centro_x, centro_y), raio_de_colisao)
ODS_HITBOXES = {
    1: ((325, 230),  100),  # Superior Esquerda
    2: ((950, 230),  100),  # Inferior Direita 
    3: ((238, 510),  100),  # Superior Direita
    4: ((1012, 510), 100),  # Inferior Esquerda    
    5: ((640, 635),  100)   # Inferior Central
}

# ========================================== #
# Carregamento de Assets
# ========================================== #

if getattr(sys, 'frozen', False):
    # PyInstaller extrai para _MEIPASS em onefile ou aponta para _internal em onedir
    SCRIPT_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
    
    if not os.path.exists(ASSETS_DIR):
        ASSETS_DIR = os.path.join(os.path.dirname(sys.executable), "_internal", "assets")
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

bg_image = None
img_transicao_1 = None

try:
    # Fundo do Lobby — busca em assets/ e depois na raiz
    for filename in ["background.jpg", "background.png", "BACKGROUND.JPG", "backgroud.png"]:
        for search_dir in [ASSETS_DIR, SCRIPT_DIR]:
            path = os.path.join(search_dir, filename)
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                # Escala o background para a resolução lógica interna
                bg_image = pygame.transform.scale(raw, (WIDTH, HEIGHT))
                WORLD_WIDTH, WORLD_HEIGHT = WIDTH, HEIGHT
                break
        if bg_image:
            break

    # Imagem de transição ODS 1
    for trans_name in ["ods1.jpg", "ods1.png", "transicao1.jpg", "transicao1.png"]:
        for search_dir in [ASSETS_DIR, SCRIPT_DIR]:
            tr_path = os.path.join(search_dir, trans_name)
            if os.path.exists(tr_path):
                img_transicao_1 = pygame.image.load(tr_path).convert_alpha()
                img_transicao_1 = pygame.transform.scale(img_transicao_1, (WIDTH, HEIGHT))
                break
        if img_transicao_1:
            break

except Exception as e:
    print(f"Aviso: Não foi possível carregar as imagens: {e}")