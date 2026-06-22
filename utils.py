# utils.py - Funções auxiliares de carregamento e desenho

import pygame

def load_scaled(path, tgt_h):
    """Carrega uma imagem e a redimensiona mantendo a proporção."""
    img = pygame.image.load(path).convert_alpha()
    aspect_ratio = img.get_width() / img.get_height()
    return pygame.transform.scale(img, (int(tgt_h * aspect_ratio), tgt_h))

def draw_arrow_up(surf, x, y):
    """Desenha uma seta indicadora para cima."""
    points = [(x, y), (x-12, y+12), (x-6, y+12), (x-6, y+25), (x+6, y+25), (x+6, y+12), (x+12, y+12)]
    pygame.draw.polygon(surf, (255, 255, 255), points)
    pygame.draw.polygon(surf, (0, 0, 0), points, 2)

def draw_key_hint(surf, x, y, key_txt):
    """Desenha uma dica de tecla (ex: [E])."""
    f = pygame.font.SysFont("Consolas", 20, bold=True)
    txt = f.render(f"{key_txt}", False, (255, 255, 255))
    size = max(txt.get_width(), txt.get_height()) + 10
    bg_r = pygame.Rect(x - size//2, y + txt.get_height()//2 - size//2, size, size)
    
    # Criar fundo semitransparente
    s = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    
    surf.blit(s, (bg_r.x, bg_r.y))
    surf.blit(txt, (x - txt.get_width()//2, y))

def show_end_screen(screen, clock, title, subtitle, color, btn_text, stats=None, lesson=None):
    """Exibe uma tela de finalização ou falha padronizada para as fases."""
    import sys
    import pygame
    
    W, H = screen.get_width(), screen.get_height()
    font_big = pygame.font.SysFont("consolas", 48, bold=True)
    font_med = pygame.font.SysFont("consolas", 24, bold=True)
    font = pygame.font.SysFont("consolas", 16, bold=True)
    
    DARK = (10, 12, 16)
    AMBER = (255, 170, 0)
    GREEN = (34, 255, 136)
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                return
                    
        screen.fill(DARK)
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((*color[:3], 20))
        screen.blit(ov, (0,0))

        t1 = font_big.render(title, True, color)
        screen.blit(t1, (W//2 - t1.get_width()//2, 120))
        t2 = font_med.render(subtitle, True, (180,184,200))
        screen.blit(t2, (W//2 - t2.get_width()//2, 190))

        if stats:
            sy = 240
            for k, v in stats.items():
                st = font.render(f"{k}: {v}", True, AMBER)
                screen.blit(st, (W//2 - st.get_width()//2, sy))
                sy += 25

        if lesson:
            lr = pygame.Rect(W//2-280, 310, 560, 90)
            pygame.draw.rect(screen, (0, 40, 20), lr, border_radius=4)
            pygame.draw.rect(screen, (*GREEN, 100), lr, 1, border_radius=4)
            
            words = lesson.split(' ')
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] < lr.width - 20:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
                
            for i, l in enumerate(lines):
                lt = font.render(l, True, GREEN)
                screen.blit(lt, (lr.x+10, lr.y+10+i*22))

        import math
        t = pygame.time.get_ticks()
        pulse = int((math.sin(t * 0.005) + 1) * 0.5 * 100 + 155)
        prompt = f"Pressione qualquer tecla para {btn_text.lower()}..."
        pt = font_med.render(prompt, True, (pulse, pulse, pulse))
        screen.blit(pt, (W//2 - pt.get_width()//2, 450))

        pygame.display.flip()
        clock.tick(30)

def draw_wrapped_objective(screen, box_rect, text, font, bg_color, border_color, text_color):
    """Desenha uma caixa de objetivo com quebra de linha inteligente para não vazar a caixa."""
    import pygame
    # Desenha o fundo da caixa
    pygame.draw.rect(screen, bg_color, box_rect, border_radius=6)
    pygame.draw.rect(screen, border_color, box_rect, 1, border_radius=6)
    
    # Processa a quebra de texto
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        # margem de 30px no total (15 de cada lado)
        if font.size(test_line)[0] < box_rect.width - 30:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
        
    # Ajusta altura da caixa se necessário
    line_height = font.size("Tg")[1] + 2
    total_text_height = len(lines) * line_height
    
    # Redesenha a caixa se o texto for maior que o box original
    if total_text_height > box_rect.height - 16:
        box_rect.height = total_text_height + 16
        pygame.draw.rect(screen, bg_color, box_rect, border_radius=6)
        pygame.draw.rect(screen, border_color, box_rect, 1, border_radius=6)
        
    for i, line in enumerate(lines):
        line_surf = font.render(line, True, text_color)
        screen.blit(line_surf, (box_rect.x + 15, box_rect.y + 8 + i * line_height))

def draw_health_bar(surface, hp, max_hp, bx=15, by=15):
    """Desenha a barra de vida padronizada em todas as fases."""
    import pygame
    font_small = pygame.font.Font(None, 22)
    hp_pct = max(0.0, min(1.0, hp / max_hp))
    bar_w, bar_h = 160, 16
    pygame.draw.rect(surface, (40, 0, 0), (bx, by, bar_w, bar_h), border_radius=4)
    if hp_pct > 0.5:
        hp_color = (50, 200, 80)
    elif hp_pct > 0.25:
        hp_color = (220, 180, 30)
    else:
        hp_color = (220, 50, 30)
    pygame.draw.rect(surface, hp_color, (bx, by, int(bar_w * hp_pct), bar_h), border_radius=4)
    pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 2, border_radius=4)
    hp_txt = font_small.render(f"HP {int(hp)}/{max_hp}", True, (255, 255, 255))
    surface.blit(hp_txt, (bx + 5, by + 1))
