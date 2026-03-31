import pygame
import os

# Inicializa o Pygame
pygame.init()

# Configurações da Tela (valores padrão, podem mudar com o background)
WIDTH, HEIGHT = 1376, 768
WORLD_WIDTH, WORLD_HEIGHT = 1376, 768

# Cria a tela inicial (necessária antes de carregar imagens)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bazar dos Objetivos Globais - Menu ODS")
clock = pygame.time.Clock()

# Fontes
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 40)
door_font = pygame.font.Font(None, 36)

# Dimensões das portas/barracas
DOOR_W, DOOR_H = 80, 80

# Nomes das 17 ODS
ODS_NAMES = [
    "1. Erradicação da Pobreza",
    "2. Fome Zero e Agric. Sustentável",
    "3. Saúde e Bem-Estar",
    "4. Educação de Qualidade",
    "5. Igualdade de Gênero",
    "6. Água Potável e Saneamento",
    "7. Energia Limpa e Acessível",
    "8. Trabalho Decente e Crescimento",
    "9. Indústria, Inovação e Infra.",
    "10. Redução das Desigualdades",
    "11. Cidades Sustentáveis",
    "12. Consumo e Produção Responsáveis",
    "13. Ação Contra a Mudança do Clima",
    "14. Vida na Água",
    "15. Vida Terrestre",
    "16. Paz, Justiça e Instituições",
    "17. Parcerias e Meios de Implem."
]

# Cores oficiais das ODS
ODS_COLORS = [
    (229, 36, 59), (221, 166, 58), (76, 159, 56), (197, 25, 45),
    (255, 58, 33), (38, 189, 226), (252, 195, 11), (162, 25, 66),
    (253, 105, 37), (221, 19, 103), (253, 157, 36), (191, 139, 46),
    (63, 126, 68), (10, 151, 217), (86, 192, 43), (0, 104, 157),
    (25, 72, 106)
]

# Posições dos stands/portas na imagem 1376x768
ODS_POS = [
    (250, 100),   # 1
    (390, 100),   # 2
    (510, 100),   # 3
    (630, 100),   # 4
    (800, 100),   # 5
    (920, 180),   # 6
    (920, 280),   # 7
    (930, 380),   # 8
    (920, 470),   # 9
    (740, 470),   # 10
    (450, 470),   # 11
    (600, 470),   # 12
    (290, 470),   # 13
    (150, 470),   # 14
    (100, 400),   # 15
    (100, 300),   # 16
    (100, 180)    # 17
]

# ========================================== #
# Carregamento de Assets
# ========================================== #

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
                bg_image = pygame.image.load(path).convert_alpha()
                WORLD_WIDTH, WORLD_HEIGHT = bg_image.get_rect().size
                WIDTH, HEIGHT = WORLD_WIDTH, WORLD_HEIGHT
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
