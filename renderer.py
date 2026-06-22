import pygame
import random
import settings


def draw_placeholder_background(surface, camera_x, camera_y):
    """Fundo padrão caso a imagem de background não esteja na pasta"""
    surface.fill((117, 92, 72))

    border_x = 0 if camera_x > 0 else (0 - camera_x)
    border_y = 0 if camera_y > 0 else (0 - camera_y)
    pygame.draw.rect(surface, (66, 49, 39),
                     (border_x, border_y, settings.WORLD_WIDTH, settings.WORLD_HEIGHT), 20)

    path_points = [
        (80, 220), (360, 240), (480, 300), (480, 500),
        (450, 700), (650, 920), (80, 920)
    ]
    adjusted_path = [(p[0] - camera_x, p[1] - camera_y) for p in path_points]
    pygame.draw.polygon(surface, (148, 122, 102), adjusted_path)

    plat_rect = pygame.Rect(
        settings.WIDTH // 2 - 45 - camera_x,
        settings.HEIGHT // 2 - 30 - camera_y,
        90, 50
    )
    pygame.draw.rect(surface, (150, 120, 100), plat_rect)
    pygame.draw.rect(surface, (100, 70, 50), plat_rect, 3)


def background_fundo(surface):
    """Fundo corrompido / Glitchy para fases estilo Level Devil"""
    surface.fill((30, 15, 40))
    for _ in range(15):
        gx = random.randint(0, surface.get_width())
        gy = random.randint(0, surface.get_height())
        gw = random.randint(50, 300)
        gh = random.randint(2, 10)
        color = random.choice([
            (255, 0, 50), (0, 255, 100), (50, 50, 255), (20, 10, 30)
        ])
        pygame.draw.rect(surface, color, (gx, gy, gw, gh))


def draw_transition_screen(surface):
    """Tela de transição para a ODS 1 (imagem abandonada + glitch)"""
    if settings.img_transicao_1:
        surface.blit(settings.img_transicao_1, (0, 0))
    else:
        surface.fill((20, 10, 15))
        font_warn = pygame.font.Font(None, 40)
        t_title = font_warn.render("FALTA IMAGEM DE TRANSIÇÃO", True, (255, 100, 100))
        t_sub1 = font_warn.render('Salve a foto como "ods1.jpg" ou "ods1.png"', True, (200, 200, 200))
        t_sub2 = font_warn.render("na MESMA PASTA do seu jogo para ela aparecer aqui!", True, (200, 200, 200))

        cx, cy = surface.get_width() // 2, surface.get_height() // 2
        surface.blit(t_title, (cx - t_title.get_width() // 2, cy - 60))
        surface.blit(t_sub1, (cx - t_sub1.get_width() // 2, cy + 10))
        surface.blit(t_sub2, (cx - t_sub2.get_width() // 2, cy + 50))

    # Efeitos sutis de glitch por cima
    for _ in range(8):
        gx = random.randint(0, surface.get_width())
        gy = random.randint(0, surface.get_height())
        color = random.choice([(255, 0, 50), (50, 255, 50), (50, 50, 255), (0, 0, 0)])
        s = pygame.Surface((random.randint(20, 100), random.randint(5, 15)), pygame.SRCALPHA)
        s.fill((*color, 128))
        surface.blit(s, (gx, gy))
