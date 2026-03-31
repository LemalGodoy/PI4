"""
Cutscene animada 2D para o Level 1 — ODS 3: Saúde e Bem-Estar
Dá contexto narrativo à missão de Hope antes de iniciar a fase.
"""
import math
import random

import pygame


# ====================================================================== #
#  Cores temáticas ODS 3
# ====================================================================== #
ODS3_GREEN = (76, 159, 56)
ODS3_DARK = (25, 50, 25)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HEART_RED = (220, 50, 60)
CITY_BG = (15, 12, 20)
HOSPITAL_WHITE = (230, 240, 235)
CAPSULE_RED = (200, 60, 60)
CAPSULE_WHITE = (240, 240, 240)

# Duração de cada cena em frames (5 seg a 60 FPS)
SCENE_DURATION = 300
TYPEWRITER_SPEED = 3  # frames por caractere
DIALOGUE_ZONE_H = 150  # altura fixa da zona de diálogo no rodapé


class CutsceneODS3:
    """Cutscene animada antes do Level 1."""

    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.scene_h = screen_h - DIALOGUE_ZONE_H  # área da animação (acima)
        self.finished = False
        self.skipped = False

        # Fontes
        self.font_big = pygame.font.Font(None, 52)
        self.font_med = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.font_hint = pygame.font.Font(None, 20)

        # Estado
        self.scene_index = 0
        self.scene_timer = 0
        self.global_timer = 0

        # Typewriter
        self._type_chars = 0

        # Estrelas de fundo (geradas uma vez)
        self._stars = [(random.randint(0, screen_w),
                        random.randint(0, self.scene_h // 2),
                        random.randint(120, 255)) for _ in range(40)]

        # Prédios da cidade (gerados uma vez)
        self._buildings = []
        bx = 0
        rng = random.Random(99)
        while bx < screen_w + 100:
            bw = rng.randint(50, 120)
            bh = rng.randint(100, 280)
            self._buildings.append((bx, bw, bh))
            bx += bw + rng.randint(8, 30)

        # Posição do Hope (personagem animado)
        self._hope_x = -60.0
        self._hope_y = 0.0

        # Partículas decorativas
        self._particles = []

        # Definição das cenas
        self.scenes = [
            {
                "draw": self._draw_scene_city,
                "text": "Uma doença misteriosa se espalha pela cidade...",
                "sub": "Os hospitais estão lotados. As pessoas precisam de ajuda."
            },
            {
                "draw": self._draw_scene_hope_arrives,
                "text": "Hope é convocada para uma missão urgente.",
                "sub": "Apenas ela pode atravessar a zona contaminada."
            },
            {
                "draw": self._draw_scene_hospital,
                "text": "O hospital precisa de suprimentos para salvar vidas.",
                "sub": "Remédios, cápsulas e equipamentos devem ser levados a tempo."
            },
            {
                "draw": self._draw_scene_briefing,
                "text": "Atravesse as plataformas. Desvie das armadilhas.",
                "sub": "Chegue ao hospital. A saúde de todos depende de você!"
            },
            {
                "draw": self._draw_scene_title,
                "text": "",
                "sub": ""
            },
        ]

    # ================================================================== #
    #  EVENTS
    # ================================================================== #
    def handle_event(self, event):
        """Processa eventos de input da cutscene."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finished = True
                self.skipped = True
                return
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self._advance_scene()

    def _advance_scene(self):
        self.scene_index += 1
        self.scene_timer = 0
        self._type_chars = 0
        self._hope_x = -60.0
        if self.scene_index >= len(self.scenes):
            self.finished = True

    # ================================================================== #
    #  UPDATE
    # ================================================================== #
    def update(self):
        if self.finished:
            return

        self.scene_timer += 1
        self.global_timer += 1
        self._type_chars += 1

        # Auto-avança após duração
        if self.scene_timer >= SCENE_DURATION:
            self._advance_scene()

        # Partículas
        if self.global_timer % 8 == 0:
            px = random.randint(0, self.w)
            py = random.randint(0, self.h)
            self._particles.append({
                'x': float(px), 'y': float(py),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-1.5, -0.3),
                'life': random.randint(40, 90),
                'color': random.choice([ODS3_GREEN, HEART_RED, (255, 220, 60)])
            })

        for p in self._particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
        self._particles = [p for p in self._particles if p['life'] > 0]

    # ================================================================== #
    #  DRAW
    # ================================================================== #
    def draw(self, surface):
        if self.finished:
            return

        scene = self.scenes[self.scene_index]

        # Cena 5 (título) usa tela cheia
        is_title_scene = (self.scene_index == len(self.scenes) - 1)

        if is_title_scene:
            # ---- Tela cheia para o título FASE 1 ----
            scene["draw"](surface)

            # Partículas na tela toda
            for p in self._particles:
                sz = max(1, int(3 * (p['life'] / 90)))
                r = min(255, p['color'][0])
                g = min(255, p['color'][1])
                b = min(255, p['color'][2])
                pygame.draw.circle(surface, (r, g, b), (int(p['x']), int(p['y'])), sz)

            # Barra de progresso
            self._draw_progress_bar(surface)
        else:
            # ---- Zona da cena (parte superior) ----
            scene_surf = surface.subsurface((0, 0, self.w, self.scene_h))
            scene["draw"](scene_surf)

            # Partículas flutuantes (só na zona da cena)
            for p in self._particles:
                if int(p['y']) < self.scene_h:
                    sz = max(1, int(3 * (p['life'] / 90)))
                    r = min(255, p['color'][0])
                    g = min(255, p['color'][1])
                    b = min(255, p['color'][2])
                    pygame.draw.circle(scene_surf, (r, g, b), (int(p['x']), int(p['y'])), sz)

            # ---- Separador entre cena e diálogo ----
            pygame.draw.line(surface, ODS3_GREEN, (0, self.scene_h), (self.w, self.scene_h), 2)

            # ---- Zona de diálogo (parte inferior fixa) ----
            dlg_bg = pygame.Surface((self.w, DIALOGUE_ZONE_H), pygame.SRCALPHA)
            dlg_bg.fill((8, 12, 8, 240))
            surface.blit(dlg_bg, (0, self.scene_h))

            # Textos com typewriter
            if scene["text"]:
                self._draw_dialogue(surface, scene["text"], scene["sub"])

            # Hint no rodapé
            hint = self.font_hint.render("ENTER para avançar  |  ESC para pular", True, (140, 140, 140))
            surface.blit(hint, (self.w // 2 - hint.get_width() // 2, self.h - 22))

            # Barra de progresso das cenas (topo da tela)
            self._draw_progress_bar(surface)

    # ================================================================== #
    #  CENA 1 — Cidade Doente
    # ================================================================== #
    def _draw_scene_city(self, surface):
        sh = surface.get_height()  # altura da zona de cena
        # Céu escuro
        for y in range(sh):
            t = y / sh
            r = int(15 + t * 10)
            g = int(8 + t * 8)
            b = int(20 + t * 15)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Estrelas
        for sx, sy, brightness in self._stars:
            if sy < sh:
                pulse = brightness + int(30 * math.sin(self.global_timer * 0.03 + sx))
                pulse = max(60, min(255, pulse))
                pygame.draw.circle(surface, (pulse, pulse, pulse), (sx, sy), 1)

        # Prédios silhueta
        ground_y = sh - 60
        for bx, bw, bh in self._buildings:
            by = ground_y - bh
            # Prédio escuro
            pygame.draw.rect(surface, (25, 20, 30), (bx, by, bw, bh))
            # Janelas — alternando acesas/apagadas
            for wy in range(by + 10, ground_y - 10, 22):
                for wx in range(bx + 6, bx + bw - 6, 16):
                    lit = ((wx + wy + self.global_timer // 30) % 5) != 0
                    color = (60, 40, 30) if not lit else (200, 150, 60)
                    pygame.draw.rect(surface, color, (wx, wy, 8, 12))

        # Chão
        pygame.draw.rect(surface, (20, 18, 22), (0, ground_y, self.w, sh - ground_y))

        # Cruzes vermelhas piscando nos prédios (hospitais sobrecarregados)
        blink = (self.global_timer // 20) % 2 == 0
        for i, (bx, bw, bh) in enumerate(self._buildings):
            if i % 3 == 0:
                cx = bx + bw // 2
                cy = ground_y - bh - 15
                cross_color = HEART_RED if blink else (100, 30, 30)
                pygame.draw.rect(surface, cross_color, (cx - 2, cy - 7, 4, 14))
                pygame.draw.rect(surface, cross_color, (cx - 7, cy - 2, 14, 4))

        # Nuvem de "contaminação" (verde tóxico, sutil)
        for i in range(5):
            cloud_x = (self.global_timer * 0.3 + i * 200) % (self.w + 200) - 100
            cloud_y = ground_y - 40 + math.sin(self.global_timer * 0.01 + i * 2) * 15
            cloud_surf = pygame.Surface((160, 40), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surf, (50, 120, 50, 25), (0, 0, 160, 40))
            surface.blit(cloud_surf, (int(cloud_x), int(cloud_y)))

    # ================================================================== #
    #  CENA 2 — Hope Chega
    # ================================================================== #
    def _draw_scene_hope_arrives(self, surface):
        sh = surface.get_height()
        # Fundo: céu com aurora verde
        for y in range(sh):
            t = y / sh
            r = int(10 + t * 15)
            g = int(20 + t * 40)
            b = int(18 + t * 20)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Aurora borealis simplificada
        for i in range(3):
            ay = 80 + i * 40
            wave_x = math.sin(self.global_timer * 0.02 + i) * 80
            points = []
            for x in range(0, self.w + 20, 20):
                yy = ay + math.sin(x * 0.01 + self.global_timer * 0.03 + i) * 25
                points.append((x, int(yy)))
            if len(points) >= 2:
                aurora_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                alpha = 30 + i * 10
                for j in range(len(points) - 1):
                    pygame.draw.line(aurora_surf, (60, 180, 80, alpha),
                                     points[j], points[j + 1], 3)
                surface.blit(aurora_surf, (0, 0))

        # Chão / estrada
        ground_y = sh - 80
        pygame.draw.rect(surface, (30, 28, 25), (0, ground_y, self.w, sh - ground_y))
        # Estrada
        pygame.draw.rect(surface, (50, 48, 45), (0, ground_y + 30, self.w, 40))
        # Linha tracejada da estrada
        for dx in range(0, self.w, 40):
            pygame.draw.rect(surface, (120, 120, 80),
                             (dx + (self.global_timer % 40), ground_y + 47, 20, 6))

        # Hope caminhando
        self._hope_x += 1.5
        if self._hope_x > self.w // 2 - 20:
            self._hope_x = self.w // 2 - 20
        self._hope_y = ground_y + 30 - 60  # Em cima da estrada

        # Bobbing animation
        bob = math.sin(self.global_timer * 0.15) * 3
        self._draw_hope_sprite(surface, int(self._hope_x), int(self._hope_y + bob))

        # Trilha de passos atrás de Hope
        for i in range(5):
            step_x = int(self._hope_x) - 30 - i * 40
            if step_x > 0:
                step_alpha = max(0, 80 - i * 16)
                step_surf = pygame.Surface((12, 4), pygame.SRCALPHA)
                step_surf.fill((100, 100, 80, step_alpha))
                surface.blit(step_surf, (step_x, ground_y + 48))

    # ================================================================== #
    #  CENA 3 — Hospital à vista
    # ================================================================== #
    def _draw_scene_hospital(self, surface):
        sh = surface.get_height()
        # Fundo gradiente esperança
        for y in range(sh):
            t = y / sh
            r = int(15 + t * 25)
            g = int(25 + t * 55)
            b = int(20 + t * 25)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        ground_y = sh - 60

        # Hospital no fundo (grande, centralizado)
        hosp_w, hosp_h = 280, 220
        hosp_x = self.w // 2 - hosp_w // 2 + 80
        hosp_y = ground_y - hosp_h

        # Corpo principal
        pygame.draw.rect(surface, HOSPITAL_WHITE, (hosp_x, hosp_y, hosp_w, hosp_h))
        pygame.draw.rect(surface, (180, 200, 185), (hosp_x, hosp_y, hosp_w, hosp_h), 3)

        # Janelas
        for wy in range(hosp_y + 20, hosp_y + hosp_h - 20, 40):
            for wx in range(hosp_x + 20, hosp_x + hosp_w - 20, 45):
                light_on = ((wx + wy) % 3) != 0
                win_color = (200, 230, 200) if light_on else (140, 160, 145)
                pygame.draw.rect(surface, win_color, (wx, wy, 25, 25))
                pygame.draw.rect(surface, (150, 170, 155), (wx, wy, 25, 25), 1)

        # Cruz verde grande no topo
        cx = hosp_x + hosp_w // 2
        cy = hosp_y + 12
        pulse = math.sin(self.global_timer * 0.06) * 0.3 + 0.7
        g_val = int(159 * pulse + 60)
        cross_color = (int(76 * pulse), min(255, g_val), int(56 * pulse))
        pygame.draw.rect(surface, cross_color, (cx - 5, cy - 15, 10, 30))
        pygame.draw.rect(surface, cross_color, (cx - 15, cy - 5, 30, 10))

        # Glow da cruz
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        glow_alpha = int(40 * pulse)
        pygame.draw.circle(glow_surf, (76, 159, 56, glow_alpha), (30, 30), 30)
        surface.blit(glow_surf, (cx - 30, cy - 30))

        # Porta do hospital
        door_w, door_h = 50, 70
        door_x = hosp_x + hosp_w // 2 - door_w // 2
        door_y = hosp_y + hosp_h - door_h
        pygame.draw.rect(surface, ODS3_GREEN, (door_x, door_y, door_w, door_h))
        pygame.draw.rect(surface, (40, 100, 35), (door_x, door_y, door_w, door_h), 2)
        # Luz da porta
        light_surf = pygame.Surface((door_w, door_h), pygame.SRCALPHA)
        light_surf.fill((200, 255, 200, int(25 * pulse)))
        surface.blit(light_surf, (door_x, door_y))

        # Texto "HOSPITAL" acima da porta
        hosp_label = self.font_small.render("HOSPITAL", True, ODS3_GREEN)
        surface.blit(hosp_label, (hosp_x + hosp_w // 2 - hosp_label.get_width() // 2,
                                   hosp_y - 25))

        # Chão
        pygame.draw.rect(surface, (35, 40, 30), (0, ground_y, self.w, sh - ground_y))

        # Hope caminhando para o hospital
        self._hope_x += 1.2
        if self._hope_x > hosp_x - 100:
            self._hope_x = hosp_x - 100
        self._hope_y = ground_y - 60
        bob = math.sin(self.global_timer * 0.15) * 3
        self._draw_hope_sprite(surface, int(self._hope_x), int(self._hope_y + bob))

        # Seta indicando a porta
        arrow_y = door_y - 30 + math.sin(self.global_timer * 0.08) * 8
        points = [
            (hosp_x + hosp_w // 2, int(arrow_y + 15)),
            (hosp_x + hosp_w // 2 - 10, int(arrow_y)),
            (hosp_x + hosp_w // 2 + 10, int(arrow_y)),
        ]
        pygame.draw.polygon(surface, ODS3_GREEN, points)

    # ================================================================== #
    #  CENA 4 — Briefing da missão
    # ================================================================== #
    def _draw_scene_briefing(self, surface):
        sh = surface.get_height()
        surface.fill((12, 18, 12))

        # Painel central semi-transparente
        panel_w, panel_h = self.w - 120, sh - 40
        panel_x, panel_y = 60, 20
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((20, 40, 25, 200))
        surface.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(surface, ODS3_GREEN, (panel_x, panel_y, panel_w, panel_h), 2)

        # Título do briefing
        title = self.font_med.render("BRIEFING DA MISSÃO", True, ODS3_GREEN)
        surface.blit(title, (self.w // 2 - title.get_width() // 2, panel_y + 20))

        # Linha divisória
        pygame.draw.line(surface, ODS3_GREEN,
                         (panel_x + 30, panel_y + 60),
                         (panel_x + panel_w - 30, panel_y + 60), 1)

        # Itens do briefing com ícones
        items = [
            ("Plataformas de cápsula", CAPSULE_RED, "Pule entre os remédios para avançar"),
            ("Armadilhas troll", HEART_RED, "Seringas e blocos — cuidado com surpresas!"),
            ("Efeitos colaterais", (255, 200, 50), "Controles invertidos temporariamente"),
            ("Porta do hospital", ODS3_GREEN, "Chegue à porta final para vencer"),
        ]

        for i, (name, color, desc) in enumerate(items):
            iy = panel_y + 85 + i * 80
            show = self.scene_timer > 30 + i * 30  # Aparecem gradualmente

            if show:
                # Ícone (quadrado colorido)
                pygame.draw.rect(surface, color,
                                 (panel_x + 40, iy, 20, 20), border_radius=3)
                pygame.draw.rect(surface, WHITE,
                                 (panel_x + 40, iy, 20, 20), 1, border_radius=3)

                # Nome do item
                name_txt = self.font_small.render(name, True, WHITE)
                surface.blit(name_txt, (panel_x + 75, iy))

                # Descrição
                desc_txt = self.font_hint.render(desc, True, (170, 190, 170))
                surface.blit(desc_txt, (panel_x + 75, iy + 25))

                # Linha pó fade in
                line_alpha = min(255, (self.scene_timer - 30 - i * 30) * 6)
                if i < len(items) - 1:
                    line_surf = pygame.Surface((panel_w - 100, 1), pygame.SRCALPHA)
                    line_surf.fill((76, 159, 56, min(60, line_alpha)))
                    surface.blit(line_surf, (panel_x + 50, iy + 55))

        # Hope mini no canto inferior direito
        hope_x = panel_x + panel_w - 80
        hope_y = panel_y + panel_h - 90
        bob = math.sin(self.global_timer * 0.1) * 2
        self._draw_hope_sprite(surface, hope_x, int(hope_y + bob), scale=0.8)

    # ================================================================== #
    #  CENA 5 — Título com fade
    # ================================================================== #
    def _draw_scene_title(self, surface):
        sh = surface.get_height()
        # Fundo verde escuro
        for y in range(sh):
            t = y / sh
            r = int(10 + t * 20)
            g = int(20 + t * 50)
            b = int(12 + t * 18)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w, y))

        # Nome da fase (grande, pulsante)
        pulse = math.sin(self.global_timer * 0.05) * 0.2 + 1.0
        title = self.font_big.render("FASE 1", True, WHITE)
        surface.blit(title, (self.w // 2 - title.get_width() // 2, sh // 2 - 100))

        # Subtítulo ODS
        sub = self.font_med.render("ODS 3 — Saúde e Bem-Estar", True, ODS3_GREEN)
        surface.blit(sub, (self.w // 2 - sub.get_width() // 2, sh // 2 - 40))

        # Coração pixel art
        cx, cy = self.w // 2, sh // 2 + 20
        s = 3
        pygame.draw.rect(surface, HEART_RED, (cx - 3*s, cy - 2*s, 2*s, 2*s))
        pygame.draw.rect(surface, HEART_RED, (cx + 1*s, cy - 2*s, 2*s, 2*s))
        pygame.draw.rect(surface, HEART_RED, (cx - 4*s, cy, 8*s, 2*s))
        pygame.draw.rect(surface, HEART_RED, (cx - 3*s, cy + 2*s, 6*s, s))
        pygame.draw.rect(surface, HEART_RED, (cx - 2*s, cy + 3*s, 4*s, s))
        pygame.draw.rect(surface, HEART_RED, (cx - s, cy + 4*s, 2*s, s))

        # Mensagem motivacional
        msg = self.font_small.render('"A saúde de todos depende de você."', True, (180, 220, 180))
        surface.blit(msg, (self.w // 2 - msg.get_width() // 2, sh // 2 + 70))

        # Fade in/out
        if self.scene_timer < 40:
            fade_alpha = int(255 * (1 - self.scene_timer / 40))
            fade_surf = pygame.Surface((self.w, sh))
            fade_surf.fill(BLACK)
            fade_surf.set_alpha(fade_alpha)
            surface.blit(fade_surf, (0, 0))
        elif self.scene_timer > SCENE_DURATION - 60:
            fade_alpha = int(255 * ((self.scene_timer - (SCENE_DURATION - 60)) / 60))
            fade_surf = pygame.Surface((self.w, sh))
            fade_surf.fill(BLACK)
            fade_surf.set_alpha(min(255, fade_alpha))
            surface.blit(fade_surf, (0, 0))

    # ================================================================== #
    #  HOPE SPRITE (mesmo visual do Player — cavaleiro)
    # ================================================================== #
    def _draw_hope_sprite(self, surface, x, y, scale=1.0):
        """Desenha Hope usando o design original do Player (cavaleiro)."""
        s = scale

        def r(val):
            return int(val * s)

        # Sombra
        pygame.draw.ellipse(surface, (30, 30, 30),
                            (x, y + r(50), r(40), r(15)))

        # Corpo (armadura)
        pygame.draw.rect(surface, (120, 120, 120),
                         (x + r(8), y + r(20), r(24), r(25)))
        # Cinto
        pygame.draw.rect(surface, (80, 50, 30),
                         (x + r(8), y + r(40), r(24), r(5)))

        # Pernas com animação de caminhada
        leg_offset = int(math.sin(self.global_timer * 0.15) * 3 * s)
        pygame.draw.rect(surface, (60, 60, 60),
                         (x + r(10), y + r(45) + leg_offset, r(8), r(15)))
        pygame.draw.rect(surface, (60, 60, 60),
                         (x + r(22), y + r(45) - leg_offset, r(8), r(15)))

        # Botas
        pygame.draw.rect(surface, (40, 40, 40),
                         (x + r(8), y + r(55) + leg_offset, r(10), r(5)))
        pygame.draw.rect(surface, (40, 40, 40),
                         (x + r(22), y + r(55) - leg_offset, r(10), r(5)))

        # Braços
        arm_swing = int(math.sin(self.global_timer * 0.15) * 2 * s)
        pygame.draw.rect(surface, (100, 100, 100),
                         (x, y + r(22) - arm_swing, r(8), r(18)))
        pygame.draw.rect(surface, (100, 100, 100),
                         (x + r(32), y + r(22) + arm_swing, r(8), r(18)))

        # Capacete
        pygame.draw.rect(surface, (180, 180, 180),
                         (x + r(6), y + r(5), r(28), r(20)))
        # Visor
        pygame.draw.rect(surface, (30, 30, 30),
                         (x + r(12), y + r(10), r(16), r(6)))

        # Glow verde (brilho ODS)
        glow_surf = pygame.Surface((r(50), r(70)), pygame.SRCALPHA)
        glow_alpha = int(20 + 15 * math.sin(self.global_timer * 0.04))
        pygame.draw.ellipse(glow_surf, (76, 159, 56, glow_alpha),
                            (0, 0, r(50), r(70)))
        surface.blit(glow_surf, (x - r(5), y - r(5)))

    # ================================================================== #
    #  DIÁLOGO (typewriter + caixa estilizada)
    # ================================================================== #
    def _draw_dialogue(self, surface, text, sub_text):
        # Calcular caracteres visíveis (typewriter effect)
        chars_visible = min(len(text), self._type_chars // TYPEWRITER_SPEED)
        display_text = text[:chars_visible]

        # Sub texto aparece depois do principal
        sub_delay = len(text) * TYPEWRITER_SPEED + 20
        sub_chars = max(0, min(len(sub_text),
                               (self._type_chars - sub_delay) // TYPEWRITER_SPEED))
        display_sub = sub_text[:sub_chars]

        # Caixa de diálogo — posicionada na zona inferior fixa
        box_h = 90
        box_y = self.scene_h + 10
        box_x = 40
        box_w = self.w - 80

        # Fundo da caixa
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((10, 10, 10, 200))
        surface.blit(box_surf, (box_x, box_y))

        # Borda estilizada
        pygame.draw.rect(surface, ODS3_GREEN, (box_x, box_y, box_w, box_h), 2)
        # Cantos decorativos
        corner_size = 8
        for cx, cy in [(box_x, box_y), (box_x + box_w - corner_size, box_y),
                        (box_x, box_y + box_h - corner_size),
                        (box_x + box_w - corner_size, box_y + box_h - corner_size)]:
            pygame.draw.rect(surface, ODS3_GREEN, (cx, cy, corner_size, corner_size))

        # Nome do "speaker"
        speaker = self.font_hint.render("NARRADOR", True, ODS3_GREEN)
        speaker_bg = pygame.Surface((speaker.get_width() + 16, speaker.get_height() + 6),
                                     pygame.SRCALPHA)
        speaker_bg.fill((10, 10, 10, 230))
        surface.blit(speaker_bg, (box_x + 15, box_y - speaker.get_height() - 2))
        pygame.draw.rect(surface, ODS3_GREEN,
                         (box_x + 15, box_y - speaker.get_height() - 2,
                          speaker.get_width() + 16, speaker.get_height() + 6), 1)
        surface.blit(speaker, (box_x + 23, box_y - speaker.get_height() + 1))

        # Texto principal
        if display_text:
            txt_surf = self.font_med.render(display_text, True, WHITE)
            surface.blit(txt_surf, (box_x + 25, box_y + 20))

        # Subtexto
        if display_sub:
            sub_surf = self.font_small.render(display_sub, True, (180, 200, 180))
            surface.blit(sub_surf, (box_x + 25, box_y + 65))

        # Cursor piscante no final do texto
        if chars_visible < len(text):
            if (self.global_timer // 15) % 2 == 0:
                cursor_x = box_x + 25 + self.font_med.size(display_text)[0]
                pygame.draw.rect(surface, WHITE, (cursor_x + 2, box_y + 22, 2, 24))

    # ================================================================== #
    #  BARRA DE PROGRESSO
    # ================================================================== #
    def _draw_progress_bar(self, surface):
        total_scenes = len(self.scenes)
        bar_w = 200
        bar_h = 4
        bar_x = self.w // 2 - bar_w // 2
        bar_y = 15

        # Fundo
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))

        # Progresso
        progress = (self.scene_index + self.scene_timer / SCENE_DURATION) / total_scenes
        fill_w = int(bar_w * progress)
        pygame.draw.rect(surface, ODS3_GREEN, (bar_x, bar_y, fill_w, bar_h))

        # Pontos para cada cena
        for i in range(total_scenes):
            px = bar_x + int(bar_w * (i / total_scenes))
            filled = i <= self.scene_index
            color = ODS3_GREEN if filled else (80, 80, 80)
            pygame.draw.circle(surface, color, (px, bar_y + 2), 4)
            pygame.draw.circle(surface, WHITE, (px, bar_y + 2), 4, 1)
