import pygame, math, random, time
from camera import Camera
from entities import Platform, Trap, Trigger, Player

WORLD_W = 8200
WORLD_H = 720

ODS3_GREEN = (76, 159, 56)
ODS3_GREEN_DARK = (45, 100, 35)
ODS3_GREEN_LIGHT = (130, 200, 110)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

HEART_RED = (220, 50, 60)

CAPSULE_RED = (200, 60, 60)
CAPSULE_WHITE = (240, 240, 240)

HOSPITAL_TILE = (220, 235, 225)

PLAYER_START = (60, 400)

FINAL_DOOR_X = 6360

def _draw_pixel_heart(surface, cx, cy, s, color):
    pygame.draw.rect(surface, color, (cx - 3*s, cy - 2*s, 2*s, 2*s))
    pygame.draw.rect(surface, color, (cx + 1*s, cy - 2*s, 2*s, 2*s))
    pygame.draw.rect(surface, color, (cx - 4*s, cy, 8*s, 2*s))
    pygame.draw.rect(surface, color, (cx - 3*s, cy + 2*s, 6*s, s))
    pygame.draw.rect(surface, color, (cx - 2*s, cy + 3*s, 4*s, s))
    pygame.draw.rect(surface, color, (cx - s, cy + 4*s, 2*s, s))

# ======================================================================
#  CUTSCENE
# ======================================================================

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
        self.font_big = pygame.font.SysFont("Consolas", 52, bold=True)
        self.font_med = pygame.font.SysFont("Consolas", 36)
        self.font_small = pygame.font.SysFont("Consolas", 26)
        self.font_hint = pygame.font.SysFont("Consolas", 20)
        self.font_door = pygame.font.SysFont("Consolas", 18)
        self.font_label = pygame.font.SysFont("Consolas", 26)

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

        # Player (para sprite animado)
        self.hope_player = Player(0, 0)
        self.hope_player.set_animation("run")

        # Definição das cenas
        self.scenes = [
            {
                "draw": self._draw_scene_city,
                "text": "Uma doença misteriosa se espalha pela cidade... Os hospitais estão lotados. As pessoas precisam de ajuda.",
                "sub": "",
            },
            {
                "draw": self._draw_scene_hope_arrives,
                "text": "Hope é convocada para uma missão urgente. Apenas ela pode atravessar a zona contaminada.",
                "sub": "",
            },
            {
                "draw": self._draw_scene_hospital,
                "text": "O hospital precisa de suprimentos para salvar vidas. Remédios, cápsulas e equipamentos devem ser levados a tempo.",
                "sub": "",
            },
            {
                "draw": self._draw_scene_briefing,
                "text": "Atravesse as plataformas. Desvie das armadilhas. Chegue ao hospital. A saúde de todos depende de você!",
                "sub": "",
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
        self.hope_player.atualizar_animacao(1/60.0)

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

        # Sem bobbing
        self._draw_hope_sprite(surface, int(self._hope_x), int(self._hope_y))

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
        self._draw_hope_sprite(surface, int(self._hope_x), int(self._hope_y))

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
        self._draw_hope_sprite(surface, hope_x, int(hope_y), scale=0.8)

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
        sub = self.font_med.render("RECURSOS SUSTENTÁVEIS E BEM-ESTAR (ODS 2 e 3)", True, ODS3_GREEN)
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
        msg = self.font_small.render('"Leve os recursos para o hospital!"', True, (180, 220, 180))
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

        if self.hope_player.current_animation:
            sprite = self.hope_player.current_animation[self.hope_player.frame_index % len(self.hope_player.current_animation)]
            if scale != 1.0:
                sprite = pygame.transform.scale(sprite, (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
            
            offsetX = (sprite.get_width() - r(40)) // 2
            surface.blit(sprite, (x - offsetX, y - r(10)))


    def _draw_dialogue(self, surface, text, sub_text):

        # ==========================================================
        # TEXTO COMPLETO
        # ==========================================================
        full_text = text

        if sub_text:
            full_text += " " + sub_text

        # ==========================================================
        # POSIÇÃO
        # ==========================================================
        box_w = self.w - 90
        box_h = 125

        box_x = 45
        box_y = self.h - 140

        # ==========================================================
        # FUNDO
        # ==========================================================
        dialog = pygame.Surface(
            (box_w, box_h),
            pygame.SRCALPHA
        )

        dialog.fill((0, 0, 0, 235))

        surface.blit(dialog, (box_x, box_y))

        # ==========================================================
        # BORDA
        # ==========================================================
        pygame.draw.rect(
            surface,
            (145, 145, 145),
            (box_x, box_y, box_w, box_h),
            1
        )

        # ==========================================================
        # FONTES
        # ==========================================================
        speaker_font = pygame.font.SysFont(
            "Consolas",
            14,
            bold=True
        )

        text_font = pygame.font.SysFont(
            "Consolas",
            17
        )

        hint_font = pygame.font.SysFont(
            "Consolas",
            11
        )

        # ==========================================================
        # POSICIONAMENTO
        # ==========================================================
        speaker_y = box_y + 8
        line_y = box_y + 23
        text_y = box_y + 38

        # ==========================================================
        # NARRADOR
        # ==========================================================
        speaker = speaker_font.render(
            "NARRADOR",
            True,
            (225, 225, 225)
        )

        surface.blit(
            speaker,
            (box_x + 18, speaker_y)
        )

        # ==========================================================
        # LINHA
        # ==========================================================
        pygame.draw.line(
            surface,
            (70, 70, 70),
            (box_x + 18, line_y),
            (box_x + box_w - 18, line_y),
            1
        )

        # ==========================================================
        # WRAP FIXO (SEM BUG)
        # ==========================================================
        full_lines = self._wrap_text(
            full_text,
            text_font,
            box_w - 60
        )

        visible_chars = min(
            len(full_text),
            self._type_chars // TYPEWRITER_SPEED
        )

        rendered_chars = 0

        # ==========================================================
        # TEXTO
        # ==========================================================
        for i, line in enumerate(full_lines):

            remaining = visible_chars - rendered_chars

            if remaining <= 0:
                break

            visible_line = line[:remaining]

            txt_surf = text_font.render(
                visible_line,
                True,
                (245, 245, 245)
            )

            surface.blit(
                txt_surf,
                (
                    box_x + 18,
                    text_y + i * 22
                )
            )

            rendered_chars += len(line)

        # ==========================================================
        # TYPEWRITER
        # ==========================================================
        if self._type_chars < len(full_text) * TYPEWRITER_SPEED:

            self._type_chars += 1

        # ==========================================================
        # CURSOR
        # ==========================================================
        if visible_chars < len(full_text):

            if (self.global_timer // 20) % 2 == 0:

                current_line = ""

                rendered = 0

                for line in full_lines:

                    if rendered + len(line) >= visible_chars:

                        current_line = line[
                            :visible_chars - rendered
                        ]

                        break

                    rendered += len(line)

                current_line_index = 0
                rendered = 0

                for idx, line in enumerate(full_lines):

                    if rendered + len(line) >= visible_chars:

                        current_line_index = idx
                        break

                    rendered += len(line)

                cursor_x = (
                    box_x
                    + 18
                    + text_font.size(current_line)[0]
                )

                cursor_y = (
                    text_y
                    + current_line_index * 22
                )

                pygame.draw.rect(
                    surface,
                    (220, 220, 220),
                    (
                        cursor_x + 2,
                        cursor_y + 2,
                        2,
                        14
                    )
                )

        # ==========================================================
        # HINT
        # ==========================================================
        if visible_chars >= len(full_text):

            hint = hint_font.render(
                "[ ENTER ] avançar",
                True,
                (90, 90, 90)
            )

            surface.blit(
                hint,
                (
                    box_x + box_w - hint.get_width() - 18,
                    box_y + box_h - 18
                )
            )

    def _wrap_text(self, text, font, max_width):
        """Quebra texto manualmente sem usar o Pygame textwrap."""
        lines = []
        words = text.split(' ')
        current_line = ''

        for word in words:

            if not current_line:
                current_line = word
            else:
                test_line = current_line + ' ' + word

                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

        lines.append(current_line)
        return lines

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


# ======================================================================
#  LEVEL
# ======================================================================

# ====================================================================== #
#  Constantes do mundo
# ====================================================================== #
WORLD_H = 720
GRAVITY = 0.8
MAX_FALL = 12
JUMP_FORCE = -14

# Cor oficial ODS 3
ODS3_GREEN = (76, 159, 56)
ODS3_GREEN_DARK = (45, 100, 35)
ODS3_GREEN_LIGHT = (130, 200, 110)
WHITE = (255, 255, 255)
HOSPITAL_TILE = (220, 235, 225)
CAPSULE_RED = (200, 60, 60)
CAPSULE_WHITE = (240, 240, 240)
HEART_RED = (220, 50, 60)

# Ponto de início (sem checkpoints — sempre começa aqui)
PLAYER_START = (60, 400)


class Level1Troll:

    
    def __init__(self):
        self.player_start = PLAYER_START
        self.world_w = WORLD_W
        self.world_h = WORLD_H

        # Timer interno
        self._tick = 0
        self.start_time = time.time()

        # Física
        self.dy = 0
        self.is_grounded = False
        self.won = False

        # Entidades
        self.platforms: list[Platform] = []
        self.traps: list[Trap] = []
        self.triggers: list[Trigger] = []

        # Portas
        self.door_fake = pygame.Rect(0, 0, 0, 0)
        self.door_real = pygame.Rect(0, 0, 0, 0)
        self.door_final = pygame.Rect(0, 0, 0, 0)

        # Armadilhas contínuas
        self.ceiling_block = Trap(0, -200, 60, 100, "block")
        self.t_teto_active = False

        # Plataforma móvel
        self._moving_plat: Platform | None = None
        self._moving_origin_x = 0
        self._moving_range = 0
        self._moving_speed = 0.0

        # Plataforma escorregadia (slide)
        self._sliding_plat: Platform | None = None
        self._sliding_active = False
        self._sliding_speed = 3

        # Shake em plataformas (pré-aviso visual)
        self._shake_targets: dict[int, int] = {}

        # Efeito colateral (controles invertidos temporário)
        self._side_effect_timer = 0
        self._side_effect_text_timer = 0

        # Plataformas piscando
        self._blink_active = False
        self._blink_timer = 0
        self._blink_indices: list[int] = []

        # Ambulância (plataforma real move rápido)
        self._ambulance_active = False
        self._ambulance_plat: Platform | None = None
        self._ambulance_origin_x = 0

        # Porta fake já fugiu?
        self._fake_door_triggered = False

        # Câmera
        self.camera: Camera | None = None

        # Timer interno
        self._tick = 0

        # Estrelas do background (geradas uma vez)
        self._bg_stars: list[tuple[int, int, int]] = []
        self._bg_buildings: list[tuple[int, int, int, int, tuple]] = []
        self._bg_trees: list[tuple[int, int]] = []
        self._bg_generated = False

        # Animação da porta final (pulso de brilho)
        self._door_pulse = 0.0

    # ================================================================== #
    #  GERAR BACKGROUND estático (uma vez)
    # ================================================================== #
    def _generate_bg_elements(self) -> None:
        if self._bg_generated:
            return
        self._bg_generated = True

        rng = random.Random(42)  # seed fixa para consistência

        # Estrelas/partículas no céu
        for _ in range(60):
            x = rng.randint(0, WORLD_W)
            y = rng.randint(0, WORLD_H // 3)
            brightness = rng.randint(150, 255)
            self._bg_stars.append((x, y, brightness))

        # Prédios hospitalares na silhueta (camada média)
        bx = 0
        while bx < WORLD_W + 200:
            bw = rng.randint(60, 140)
            bh = rng.randint(120, 300)
            by = WORLD_H - bh - rng.randint(30, 80)
            color_variant = rng.randint(-15, 15)
            base = (55 + color_variant, 90 + color_variant, 55 + color_variant)
            self._bg_buildings.append((bx, by, bw, bh, base))
            bx += bw + rng.randint(20, 80)

        # Árvores (saúde/natureza)
        for _ in range(20):
            tx = rng.randint(0, WORLD_W)
            ty = WORLD_H - rng.randint(60, 150)
            self._bg_trees.append((tx, ty))

    # ================================================================== #
    #  RESET — reconstrói todo o nível
    # ================================================================== #
    def reset(self, vp_w: int, vp_h: int, player) -> None:
        self.dy = 0
        self.is_grounded = False
        self.won = False
        self._tick = 0
        self.t_teto_active = False
        self._shake_targets.clear()
        self._side_effect_timer = 0
        self._side_effect_text_timer = 0
        self._blink_active = False
        self._blink_timer = 0
        self._sliding_active = False
        self._ambulance_active = False
        self._fake_door_triggered = False
        self._door_pulse = 0.0

        # Câmera
        self.camera = Camera(WORLD_W, WORLD_H, vp_w, vp_h, lerp_speed=0.10)

        # Gerar cenário de fundo
        self._generate_bg_elements()

        # --------------------------------------------------------------- #
        #  PLATAFORMAS — blocos ao longo do mundo (compacto, ~3600px)
        #  Gaps máximos: ~140px horizontal, ~100px vertical ascendente
        # --------------------------------------------------------------- #
        self.platforms = [
            # ===== SEÇÃO A (0 – 1200) — "Consulta Médica" ===== #
# ===== SEÇÃO A (0 – 1800) — "Consulta Médica" ===== #
            Platform(30,   520, 260, 35, ODS3_GREEN),         # 0  — chão inicial (grande, seguro)
            Platform(500,  470, 160, 30, CAPSULE_WHITE),      # 1  — cápsula branca
            Platform(900,  400, 150, 30, CAPSULE_RED),        # 2  — cápsula vermelha (vai sumir!)
            Platform(1320, 500, 200, 35, ODS3_GREEN),         # 3  — descanso seguro
            Platform(1760, 390, 170, 30, CAPSULE_WHITE),      # 4  — subida suave
            Platform(2140, 520, 130, 30, ODS3_GREEN),         # 5  — degrau de transição

            # ===== SEÇÃO B (2200 – 4200) — "Farmácia" ===== #
            Platform(2450, 480, 200, 35, ODS3_GREEN),         # 6  — entrada seção B
            Platform(2880, 390, 160, 30, CAPSULE_WHITE),      # 7  — plataforma que escorrega
            Platform(2900, 320, 150, 30, ODS3_GREEN_LIGHT),   # 8  — plataforma MÓVEL
            Platform(3280, 430, 180, 30, CAPSULE_RED),        # 9  — spike sobe (injeção)
            Platform(3600, 340, 170, 30, CAPSULE_WHITE),      # 10 — ponte após spike
            Platform(3900, 500, 160, 35, ODS3_GREEN),         # 11 — descanso antes seção C

            # ===== SEÇÃO C (4800 – 7000) — "Hospital / Cura" ===== #
            Platform(4300, 520, 220, 35, ODS3_GREEN),         # 12 — entrada seção C
            Platform(4700, 500, 160, 30, CAPSULE_WHITE),      # 13 — pisca
            Platform(5100, 470, 150, 30, CAPSULE_WHITE),      # 14 — pisca
            Platform(5400, 430, 170, 30, ODS3_GREEN_LIGHT),   # móvel
            Platform(5640, 470, 200, 35, ODS3_GREEN),         # fake        # 16 — plataforma fake
            Platform(5900, 400, 170, 30, CAPSULE_WHITE),      # 17 — penúltima
            Platform(6300, 470, 180, 35, ODS3_GREEN),         # 18 — plataforma final       # 17 — plataforma da PORTA FINAL
        ]

        # Plataforma móvel — referência ao index 8
        self._moving_plat = self.platforms[8]
        self._moving_origin_x = self._moving_plat.rect.x
        self._moving_range = 100
        self._moving_speed = 0.03

        # Plataforma escorregadia — index 7
        self._sliding_plat = self.platforms[7]
        self._sliding_active = False

        # Blink indices (seção C)
        self._blink_indices = [13, 14]

        # --------------------------------------------------------------- #
        #  TRAPS estáticos
        # --------------------------------------------------------------- #
        self.traps = []
        # Teto que cai (seção A) — bloco hospitalar
        self.ceiling_block = Trap(530, -180, 100, 80, "block", (80, 80, 80))
        self.ceiling_block.active = True

        # --------------------------------------------------------------- #
        #  PORTAS
        # --------------------------------------------------------------- #
        # Porta fake (engana o jogador na seção C)
        self.door_fake = pygame.Rect(5710, 370, 60, 100)
        # Porta real (aparece depois do trigger da fake)
        self.door_real = pygame.Rect(0, 0, 0, 0)
        # PORTA FINAL — sempre visível no final da fase
        self.door_final = pygame.Rect(6360, 370, 60, 100)

        # --------------------------------------------------------------- #
        #  TRIGGERS — callbacks inteligentes (Level Devil style)
        # --------------------------------------------------------------- #
        self.triggers = []

        # ---- SEÇÃO A ------------------------------------------------- #
        # T0 — Ao chegar perto da plat 2: teto começa a descer com pré-aviso
        def _trig_teto():
            self.t_teto_active = True

        # T1 — Plat 2 some (cápsula vermelha "expira") — com delay
        def _trig_plat2_vanish():
            self._start_shake(2, 40)  # treme antes de sumir
            # O sumir é controlado no update via shake

        # ---- SEÇÃO B ------------------------------------------------- #
        # T2 — Plat 7 escorrega para a direita quando jogador chega perto
        def _trig_slide():
            self._sliding_active = True
            self._start_shake(7, 20)  # aviso rápido

        # T3 — "Injeção" — spikes sobem do chão sob plat 9
        def _trig_injection():
            spike = Trap(
                self.platforms[9].rect.x + 10,
                self.platforms[9].rect.bottom,
                160, 25, "spike", HEART_RED
            )
            self.traps.append(spike)
            self._start_shake(9, 35)  # aviso antes do spike

        # T4 — "Efeito Colateral" — controles invertem por 120 frames (2 seg)
        def _trig_side_effect():
            player.inverted_controls = True
            self._side_effect_timer = 120
            self._side_effect_text_timer = 120

        # ---- SEÇÃO C ------------------------------------------------- #
        # T5 — Plataformas piscam (aviso visual)
        def _trig_blink():
            self._blink_active = True
            self._blink_timer = 120

        # T6 — Porta fake "foge" + plat some + porta real aparece embaixo
        def _trig_porta_fuga():
            if self._fake_door_triggered:
                return

            self._fake_door_triggered = True

            # some com a porta fake
            self.door_fake.y = 99999

            # some com a plataforma fake
            self.platforms[16].active = False

        # --------------------------------------------------------------- #
        #  Montar lista de triggers
        # --------------------------------------------------------------- #
        self.triggers = [
            # Seção A
            Trigger(460, 0, 20, WORLD_H, _trig_teto),              # T0
            Trigger(850, 0, 20, WORLD_H, _trig_plat2_vanish),      # T1

            # Seção B
            Trigger(1400, 0, 20, WORLD_H, _trig_slide),            # T2
            Trigger(1780, 0, 20, WORLD_H, _trig_injection),        # T3
            Trigger(1960, 0, 20, WORLD_H, _trig_side_effect),      # T4

            # Seção C
            Trigger(4580, 0, 20, WORLD_H, _trig_blink),
            Trigger(5620, 0, 20, WORLD_H, _trig_porta_fuga),       # T6
        ]

        # Posicionar jogador e câmera
        player.rect.x, player.rect.y = PLAYER_START
        self.camera.snap(player.rect)

    # ================================================================== #
    #  SHAKE helper
    # ================================================================== #
    def _start_shake(self, plat_index: int, duration: int) -> None:
        self._shake_targets[plat_index] = duration

    def _process_shakes(self) -> None:
        finished = []
        for idx, remaining in self._shake_targets.items():
            if remaining <= 0:
                finished.append(idx)
                continue
            self._shake_targets[idx] = remaining - 1
        for idx in finished:
            del self._shake_targets[idx]
            # Plat 2: some ao terminar o shake (trigger T1)
            if idx == 2 and not self.platforms[2].active:
                pass  # já desativada
            elif idx == 2:
                self.platforms[2].active = False

    # ================================================================== #
    #  MOVEMENT — lógica de movimento e colisão (Integrada da Fase 5)
    # ================================================================== #
    def handle_movement(self, player, keys) -> None:
        # Direções (respeita inversão por efeito colateral)
        left_keys = (pygame.K_a, pygame.K_LEFT)
        right_keys = (pygame.K_d, pygame.K_RIGHT)

        if player.inverted_controls:
            left_keys, right_keys = right_keys, left_keys

        mov = 0
        if any(keys[k] for k in left_keys):
            mov -= 1
        if any(keys[k] for k in right_keys):
            mov += 1

        jump_keys = (pygame.K_UP, pygame.K_w, pygame.K_SPACE)
        if any(keys[k] for k in jump_keys):
            player.jumpBuffer = 0.15

        # Pega rects de todas as plataformas ativas
        plats = [p.rect for p in self.platforms if p.active]
        
        # Chama a mesma física da Fase 5 (chao_ativo=False pois não há um chão global embaixo)
        player.update_platform(1.0 / 60.0, keys, mov, WORLD_H + 500, WORLD_W, plats, chao_ativo=False)

    # ================================================================== #
    #  UPDATE
    # ================================================================== #
    def update(self, player) -> None:
        if self.won:
            return

        self._tick += 1
        self._door_pulse += 0.05
        dead = False

        # Morte por queda
        if player.rect.top > WORLD_H + 50:
            dead = True

        # Triggers
        for tr in self.triggers:
            tr.check(player)

        # Teto caindo (seção A)
        if self.t_teto_active and self.ceiling_block.rect.bottom < 470:
            self.ceiling_block.rect.y += 10
        if self.t_teto_active and self.ceiling_block.check_collision(player):
            dead = True

        # Plataforma móvel (seção B — index 8)
        if self._moving_plat and self._moving_plat.active:
            self._moving_plat.rect.x = int(
                self._moving_origin_x
                + math.sin(self._tick * self._moving_speed) * self._moving_range
            )

        # Plataforma escorregadia (seção B — index 7)
        if self._sliding_active and self._sliding_plat and self._sliding_plat.active:
            self._sliding_plat.rect.x += self._sliding_speed
            # Para depois de um certo ponto
            if self._sliding_plat.rect.x > 1700:
                self._sliding_plat.active = False

        # Efeito colateral timer
        if self._side_effect_timer > 0:
            self._side_effect_timer -= 1
            if self._side_effect_timer <= 0:
                player.inverted_controls = False

        if self._side_effect_text_timer > 0:
            self._side_effect_text_timer -= 1

        # Plataformas piscando (seção C)
        if self._blink_active and self._blink_timer > 0:
            self._blink_timer -= 1
            # Pisca a cada 15 frames
            show = (self._blink_timer // 15) % 2 == 0
            for bi in self._blink_indices:
                if bi < len(self.platforms):
                    self.platforms[bi].active = show
            if self._blink_timer <= 0:
                # Restaura todas no final
                for bi in self._blink_indices:
                    if bi < len(self.platforms):
                        self.platforms[bi].active = True
                self._blink_active = False

        # Ambulância — plataforma se move rápido
        if self._ambulance_active and self._ambulance_plat and self._ambulance_plat.active:
            self._ambulance_plat.rect.x = int(
                self._ambulance_origin_x
                + math.sin(self._tick * 0.04) * 80
            )
            # Atualiza posição da porta real junto
            if self.door_real.width > 0:
                self.door_real.x = self._ambulance_plat.rect.x + 100

        # Shake visual
        self._process_shakes()

        # Traps convencionais
        for trap in self.traps:
            if trap.check_collision(player):
                dead = True

        # --- VITÓRIA --- #
        # Porta REAL (aparece após trigger da porta fake)
        if self.door_real.width > 0 and player.rect.colliderect(self.door_real):
            self.won = True
            player.inverted_controls = False

        # Porta FINAL (sempre presente no final da fase)
        if self.door_final.width > 0 and player.rect.colliderect(self.door_final):
            self.won = True
            player.inverted_controls = False

        # Câmera
        if self.camera:
            self.camera.update(player.rect)

        # Morte → REINICIA DO INÍCIO (sem checkpoints)
        if dead:
            self._respawn(player)

    # ================================================================== #
    #  RESPAWN — sempre volta ao início (sem checkpoints)
    # ================================================================== #
    def _respawn(self, player) -> None:
        vp_w = self.camera.vp_w if self.camera else 1280
        vp_h = self.camera.vp_h if self.camera else 720
        player.inverted_controls = False
        self.reset(vp_w, vp_h, player)
        player.set_position(*self.player_start)

    # ================================================================== #
    #  DRAW
    # ================================================================== #
    def draw(self, surface, player=None, camera=None) -> None:
        cam = camera or self.camera

        # ----- Background ODS 3 com profundidade ----- #
        self._draw_background(surface, cam)

        # ----- Chão hospitalar ----- #
        self._draw_floor(surface, cam)

        # ----- Plataformas (estilo cápsula de remédio) ----- #
        visible = cam.rect if cam else pygame.Rect(0, 0, surface.get_width(), surface.get_height())

        for idx, p in enumerate(self.platforms):
            if not p.active:
                continue
            if not p.rect.colliderect(visible):
                continue

            draw_rect = cam.apply(p.rect) if cam else p.rect

            # Shake offset
            shake_off = 0
            if idx in self._shake_targets:
                shake_off = random.randint(-3, 3)

            shaken_rect = draw_rect.move(shake_off, 0)
            self._draw_capsule_platform(surface, shaken_rect, p.color)

        # ----- Traps ----- #
        for t in self.traps:
            if t.active and t.rect.colliderect(visible):
                tr = cam.apply(t.rect) if cam else t.rect
                self._draw_syringe_spike(surface, tr, t.color)

        # Ceiling block
        if self.ceiling_block.active and self.t_teto_active:
            cb = cam.apply(self.ceiling_block.rect) if cam else self.ceiling_block.rect
            self._draw_falling_block(surface, cb)

        # ----- Porta Fake (porta de hospital) ----- #
        font = pygame.font.SysFont("Consolas", 24)
        if self.door_fake.top < WORLD_H:
            dr = cam.apply(self.door_fake) if cam else self.door_fake
            self._draw_hospital_door(surface, dr, fake=True)
            txt = font.render("SAIDA", True, WHITE)
            surface.blit(txt, (dr.centerx - txt.get_width() // 2, dr.top - 22))

        # ----- PORTA FINAL (sempre visível, com efeito pulsante) ----- #
        if self.door_final.width > 0:
            dr = cam.apply(self.door_final) if cam else self.door_final
            self._draw_final_door(surface, dr)

        # ----- HUD ----- #
        self._draw_hud(surface, player)

        # ----- Vitória ----- #
        if self.won:
            vp_w = surface.get_width()
            vp_h = surface.get_height()
            # Overlay escuro
            overlay = pygame.Surface((vp_w, vp_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))

            font_win = pygame.font.SysFont("Consolas", 52, bold=True)
            txt_win = font_win.render("Fase Concluida!", True, ODS3_GREEN_LIGHT)
            surface.blit(txt_win, (vp_w // 2 - txt_win.get_width() // 2, vp_h // 2 - 50))


    # ================================================================== #
    #  Background — Parallax ODS 3 com profundidade
    # ================================================================== #
    def _draw_background(self, surface: pygame.Surface, cam: Camera | None) -> None:
        vp_w = surface.get_width()
        vp_h = surface.get_height()
        offset_x = int(cam.offset_x) if cam else 0

        # --- Céu gradiente (escuro no topo → verde claro embaixo) --- #
        for y in range(vp_h):
            t = y / vp_h
            r = int(15 + t * 30)
            g = int(30 + t * 60)
            b = int(25 + t * 25)
            pygame.draw.line(surface, (r, g, b), (0, y), (vp_w, y))

        # --- Estrelas / partículas (camada mais distante) --- #
        parallax_far = offset_x * 0.1
        for sx, sy, brightness in self._bg_stars:
            screen_x = int(sx - parallax_far) % (vp_w + 100) - 50
            alpha_pulse = brightness + int(20 * math.sin(self._tick * 0.02 + sx))
            alpha_pulse = max(100, min(255, alpha_pulse))
            color = (alpha_pulse, alpha_pulse, alpha_pulse)
            pygame.draw.circle(surface, color, (screen_x, sy), 1)

        # --- Prédios hospitalares (camada média — parallax 0.3) --- #
        parallax_mid = offset_x * 0.3
        for bx, by, bw, bh, base_color in self._bg_buildings:
            screen_bx = int(bx - parallax_mid)
            if screen_bx + bw < -50 or screen_bx > vp_w + 50:
                continue

            # Corpo do prédio
            r = max(0, min(255, base_color[0]))
            g = max(0, min(255, base_color[1]))
            b = max(0, min(255, base_color[2]))
            pygame.draw.rect(surface, (r, g, b),
                             (screen_bx, by, bw, bh))

            # Janelas iluminadas (amarelas/verdes)
            win_cols = max(1, bw // 20)
            win_rows = max(1, bh // 30)
            for wr in range(win_rows):
                for wc in range(win_cols):
                    wx = screen_bx + 6 + wc * 20
                    wy = by + 8 + wr * 30
                    # Algumas janelas acesas, outras apagadas
                    lit = ((bx + wc * 7 + wr * 13) % 3) != 0
                    if lit:
                        win_color = (200, 220, 140) if (wc + wr) % 2 == 0 else (140, 200, 160)
                    else:
                        win_color = (35, 55, 35)
                    pygame.draw.rect(surface, win_color, (wx, wy, 10, 14))

            # Cruz hospitalar no topo de alguns prédios
            if bh > 200 and bw > 80:
                cx = screen_bx + bw // 2
                cy = by + 15
                cross_color = ODS3_GREEN_LIGHT
                pygame.draw.rect(surface, cross_color, (cx - 3, cy - 8, 6, 16))
                pygame.draw.rect(surface, cross_color, (cx - 8, cy - 3, 16, 6))

        # --- Árvores silhueta (camada próxima — parallax 0.5) --- #
        parallax_near = offset_x * 0.5
        for tx, ty in self._bg_trees:
            screen_tx = int(tx - parallax_near) % (vp_w + 200) - 100
            # Tronco
            pygame.draw.rect(surface, (40, 65, 35), (screen_tx - 3, ty, 6, 30))
            # Copa (círculo verde)
            pygame.draw.circle(surface, (35, 75, 30), (screen_tx, ty - 5), 18)
            pygame.draw.circle(surface, (40, 85, 35), (screen_tx - 8, ty + 2), 12)
            pygame.draw.circle(surface, (40, 85, 35), (screen_tx + 8, ty + 2), 12)

        # --- Colinas no horizonte (parallax 0.2) --- #
        parallax_hills = offset_x * 0.2
        hill_points = []
        for hx in range(-50, vp_w + 100, 30):
            world_hx = hx + parallax_hills
            hy = vp_h - 100 + int(40 * math.sin(world_hx * 0.005))
            hill_points.append((hx, hy))
        hill_points.append((vp_w + 100, vp_h))
        hill_points.append((-50, vp_h))
        if len(hill_points) >= 3:
            pygame.draw.polygon(surface, (30, 55, 28), hill_points)

    # ================================================================== #
    #  Chão hospitalar (azulejos)
    # ================================================================== #
    def _draw_floor(self, surface: pygame.Surface, cam: Camera | None) -> None:
        vp_w = surface.get_width()
        vp_h = surface.get_height()
        offset_x = int(cam.offset_x) if cam else 0

        # Faixa de chão na base (linha de azulejos)
        floor_y = vp_h - 25
        floor_h = 25

        # Padrão xadrez de azulejo
        tile_size = 25
        start_x = -(offset_x % tile_size)
        for tx in range(int(start_x), vp_w + tile_size, tile_size):
            tile_col = int((tx + offset_x) / tile_size) % 2
            color = HOSPITAL_TILE if tile_col == 0 else (195, 215, 200)
            pygame.draw.rect(surface, color, (tx, floor_y, tile_size, floor_h))
            pygame.draw.rect(surface, (180, 200, 185), (tx, floor_y, tile_size, floor_h), 1)

    # ================================================================== #
    #  Plataforma estilo cápsula de remédio
    # ================================================================== #
    @staticmethod
    def _draw_capsule_platform(surface: pygame.Surface, rect: pygame.Rect,
                                color: tuple) -> None:
        x, y, w, h = rect
        half_w = w // 2

        # Metade esquerda
        pygame.draw.rect(surface, color, (x, y, half_w, h))
        # Metade direita (cor mais clara)
        lighter = tuple(min(255, c + 40) for c in color)
        pygame.draw.rect(surface, lighter, (x + half_w, y, w - half_w, h))

        # Bordas arredondadas simuladas (cantos)
        radius = min(h // 2, 8)
        pygame.draw.circle(surface, color, (x + radius, y + h // 2), radius)
        pygame.draw.circle(surface, lighter, (x + w - radius, y + h // 2), radius)

        # Contorno
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)

        # Linha divisória central
        pygame.draw.line(surface, (0, 0, 0), (x + half_w, y), (x + half_w, y + h), 1)

        # Brilho sutil
        pygame.draw.line(surface, (255, 255, 255, 80),
                         (x + 4, y + 3), (x + half_w - 4, y + 3), 1)

    # ================================================================== #
    #  Spike estilo seringa
    # ================================================================== #
    @staticmethod
    def _draw_syringe_spike(surface: pygame.Surface, rect: pygame.Rect,
                             color: tuple) -> None:
        x, y, w, h = rect
        # Base (retângulo)
        pygame.draw.rect(surface, (180, 180, 200), (x, y + h // 3, w, h * 2 // 3))
        # Pontas de agulha (triângulos)
        num_needles = max(1, w // 25)
        needle_w = w / num_needles
        for i in range(num_needles):
            nx = x + i * needle_w
            points = [
                (nx, y + h // 3),
                (nx + needle_w / 2, y),
                (nx + needle_w, y + h // 3),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 1)
        # Contorno da base
        pygame.draw.rect(surface, (0, 0, 0), (x, y + h // 3, w, h * 2 // 3), 1)

    # ================================================================== #
    #  Bloco que cai
    # ================================================================== #
    @staticmethod
    def _draw_falling_block(surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, (80, 80, 80), rect)
        # Cruz vermelha (perigo)
        cx, cy = rect.centerx, rect.centery
        pygame.draw.rect(surface, HEART_RED, (cx - 4, cy - 12, 8, 24))
        pygame.draw.rect(surface, HEART_RED, (cx - 12, cy - 4, 24, 8))
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)

    # ================================================================== #
    #  Porta de hospital (fake / real)
    # ================================================================== #
    @staticmethod
    def _draw_hospital_door(surface: pygame.Surface, rect: pygame.Rect,
                             fake: bool = True) -> None:
        x, y, w, h = rect
        if fake:
            # Porta verde de hospital
            pygame.draw.rect(surface, ODS3_GREEN, rect)
            pygame.draw.rect(surface, ODS3_GREEN_DARK, rect, 4)
            # Cruz branca
            cx, cy = x + w // 2, y + h // 3
            pygame.draw.rect(surface, WHITE, (cx - 4, cy - 10, 8, 20))
            pygame.draw.rect(surface, WHITE, (cx - 10, cy - 4, 20, 8))
            # Maçaneta
            pygame.draw.circle(surface, (200, 200, 50), (x + w - 10, y + h // 2), 5)
        else:
            # Porta real — branca brilhante com coração
            pygame.draw.rect(surface, WHITE, rect)
            pygame.draw.rect(surface, ODS3_GREEN, rect, 5)
            # Coração pixel art
            cx, cy = x + w // 2, y + h // 3
            _draw_pixel_heart(surface, cx, cy, 10, HEART_RED)
            # Brilho
            glow = pygame.Surface((w + 16, h + 16), pygame.SRCALPHA)
            glow.fill((76, 159, 56, 30))
            surface.blit(glow, (x - 8, y - 8))
            # Maçaneta
            pygame.draw.circle(surface, ODS3_GREEN, (x + w - 10, y + h // 2), 5)

    # ================================================================== #
    #  PORTA FINAL — porta grande e brilhante com animação pulsante
    # ================================================================== #
    def _draw_final_door(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        x, y, w, h = rect

        # Brilho pulsante ao redor da porta
        pulse = abs(math.sin(self._door_pulse))
        glow_size = int(8 + pulse * 6)
        glow_alpha = int(20 + pulse * 30)

        # Glow externo (verde ODS 3)
        glow_surf = pygame.Surface((w + glow_size * 2, h + glow_size * 2), pygame.SRCALPHA)
        glow_surf.fill((76, 159, 56, glow_alpha))
        surface.blit(glow_surf, (x - glow_size, y - glow_size))

        # Corpo da porta — branco brilhante
        pygame.draw.rect(surface, WHITE, rect)

        # Borda verde grossa
        pygame.draw.rect(surface, ODS3_GREEN, rect, 5)

        # Borda interna dourada
        inner = pygame.Rect(x + 6, y + 6, w - 12, h - 12)
        pygame.draw.rect(surface, (255, 215, 0), inner, 2)

        # Coração grande pixel art no centro
        cx, cy = x + w // 2, y + h // 3
        _draw_pixel_heart(surface, cx, cy, 14, HEART_RED)

        # Maçaneta dourada
        pygame.draw.circle(surface, (255, 215, 0), (x + w - 10, y + h // 2), 6)
        pygame.draw.circle(surface, (200, 170, 0), (x + w - 10, y + h // 2), 6, 2)

        # Label acima da porta
        font_label = pygame.font.SysFont("Consolas", 26)

        # Cor pulsante para o label
        label_r = int(130 + pulse * 125)
        label_g = int(200 + pulse * 55)
        label_b = int(110 + pulse * 50)
        label_color = (min(255, label_r), min(255, label_g), min(255, label_b))

        lbl = font_label.render("PORTA FINAL", True, label_color)
        # Fundo semi-transparente para o label
        lbl_bg = pygame.Surface((lbl.get_width() + 12, lbl.get_height() + 6), pygame.SRCALPHA)
        lbl_bg.fill((0, 0, 0, 100))
        surface.blit(lbl_bg, (x + w // 2 - lbl.get_width() // 2 - 6, y - 30))
        surface.blit(lbl, (x + w // 2 - lbl.get_width() // 2, y - 27))

    # ================================================================== #
    #  HUD — ODS 3 temática
    # ================================================================== #
    def _draw_hud(self, surface: pygame.Surface, player=None) -> None:
        vp_w = surface.get_width()
        font_hud = pygame.font.SysFont("Consolas", 22)
        font_title = pygame.font.SysFont("Consolas", 18)

        # Health bar
        if player:
            from utils import draw_health_bar
            from entities import Player
            draw_health_bar(surface, player.hp, Player.PLAYER_MAX_HP)

        # Aviso de efeito colateral
        if self._side_effect_text_timer > 0:
            # Pisca o aviso
            if (self._side_effect_text_timer // 8) % 2 == 0:
                warn_font = pygame.font.SysFont("Consolas", 36)
                warn_txt = warn_font.render("EFEITO COLATERAL!", True, (255, 200, 50))
                wx = vp_w // 2 - warn_txt.get_width() // 2
                # Fundo semi-transparente
                bg = pygame.Surface((warn_txt.get_width() + 20, 36), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 140))
                surface.blit(bg, (wx - 10, 35))
                surface.blit(warn_txt, (wx, 38))

        # Aviso de plataformas piscando
        if self._blink_active:
            if (self._blink_timer // 10) % 2 == 0:
                warn_font = pygame.font.SysFont("Consolas", 36)
                warn_txt = warn_font.render("INSTABILIDADE DETECTADA!", True, (255, 200, 50))
                wx = vp_w // 2 - warn_txt.get_width() // 2
                # Fundo semi-transparente
                bg = pygame.Surface((warn_txt.get_width() + 20, 36), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 140))
                surface.blit(bg, (wx - 10, 35))
                surface.blit(warn_txt, (wx, 38))

        # TIMER
        elapsed = time.time() - self.start_time

        mins = int(elapsed) // 60
        secs = int(elapsed) % 60

        font_timer = pygame.font.SysFont("Consolas", 18, bold=True)

        timer_txt = font_timer.render(
            f"TEMPO {mins:02d}:{secs:02d}",
            True,
            (255, 170, 0)
        )

        surface.blit(timer_txt, (vp_w - 190, 10))


        # PROGRESSO
        progress = max(
            0,
            min(1, player.rect.x / FINAL_DOOR_X)
        )

        pb_x = vp_w - 190
        pb_y = 35
        pb_w = 170
        pb_h = 10

        pygame.draw.rect(
            surface,
            (30, 33, 40),
            (pb_x, pb_y, pb_w, pb_h),
            border_radius=3
        )

        fill_w = int(pb_w * progress)

        pygame.draw.rect(
            surface,
            (0, 212, 255),
            (pb_x, pb_y, fill_w, pb_h),
            border_radius=3
        )

        prog_txt = font_timer.render(
            f"PROGRESSO {int(progress * 100)}%",
            True,
            (0, 212, 255)
        )

        surface.blit(prog_txt, (pb_x, pb_y + 12))


# ====================================================================== #
#  Funções auxiliares de pixel art
# ====================================================================== #
def _draw_pixel_heart(surface: pygame.Surface, cx: int, cy: int,
                       size: int, color: tuple) -> None:
    """Desenha um coração pixel art centralizado em (cx, cy)."""
    s = max(1, size // 5)
    # Linha superior (dois bumps)
    pygame.draw.rect(surface, color, (cx - 3 * s, cy - 2 * s, 2 * s, 2 * s))
    pygame.draw.rect(surface, color, (cx + 1 * s, cy - 2 * s, 2 * s, 2 * s))
    # Linha do meio
    pygame.draw.rect(surface, color, (cx - 4 * s, cy, 8 * s, 2 * s))
    # Base triangular
    pygame.draw.rect(surface, color, (cx - 3 * s, cy + 2 * s, 6 * s, s))
    pygame.draw.rect(surface, color, (cx - 2 * s, cy + 3 * s, 4 * s, s))
    pygame.draw.rect(surface, color, (cx - s, cy + 4 * s, 2 * s, s))

def draw_menu(screen):
    """Tela de menu inicial com comandos."""
    waiting = True
    import math, time
    t_start = time.time()
    
    font_grande = pygame.font.SysFont("Consolas", 48, bold=True)
    font_ui = pygame.font.SysFont("Consolas", 20)
    WIDTH, HEIGHT = screen.get_size()
    
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                waiting = False

        screen.fill((12, 12, 30))
        # Fundo com gradiente sutil
        for i in range(HEIGHT):
            r = int(12 + i * 0.01)
            g = int(20 + i * 0.02)
            b = int(12 + i * 0.01)
            pygame.draw.line(screen, (r, g, b), (0, i), (WIDTH, i))

        # Overlay colorido
        GREEN_THEME = (76, 180, 80)
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((*GREEN_THEME, 12))
        screen.blit(ov, (0, 0))

        t = time.time() - t_start

        # Título
        title = font_grande.render("FASE 1", True, GREEN_THEME)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        sub = font_ui.render("RECURSOS SUSTENTÁVEIS E BEM-ESTAR (ODS 2 e 3)", True, (180, 200, 180))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 120))

        # Caixa de comandos
        box_w, box_h = 460, 260
        box_x = WIDTH // 2 - box_w // 2
        box_y = 170
        pygame.draw.rect(screen, (20, 30, 22), (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, (*GREEN_THEME, 80), (box_x, box_y, box_w, box_h), 2, border_radius=8)

        # Título da caixa
        cmd_title = font_ui.render("COMANDOS", True, (150, 255, 150))
        screen.blit(cmd_title, (WIDTH // 2 - cmd_title.get_width() // 2, box_y + 12))

        # Separador
        pygame.draw.line(screen, (60, 90, 60), (box_x + 20, box_y + 42), (box_x + box_w - 20, box_y + 42), 1)

        # Lista de comandos
        commands = [
            ("A / <", "Mover para esquerda"),
            ("D / >", "Mover para direita"),
            ("W / ^", "Pular"),
            ("ALT + F4", "Sair da fase"),
        ]
        cy = box_y + 55
        for key, desc in commands:
            kt = font_ui.render(key, True, (100, 255, 100))
            screen.blit(kt, (box_x + 30, cy))
            pygame.draw.rect(screen, (50, 80, 50), (box_x + 200, cy + 2, 2, 14))
            dt_text = font_ui.render(desc, True, (255, 255, 255))
            screen.blit(dt_text, (box_x + 215, cy))
            cy += 32

        # Objetivo
        obj_y = box_y + box_h + 20
        obj_box = pygame.Rect(box_x, obj_y, box_w, 50)
        from utils import draw_wrapped_objective
        draw_wrapped_objective(
            screen, obj_box,
            "OBJETIVO: Atravesse as armadilhas para chegar ao hospital antes que seja tarde!",
            font_ui, (15, 40, 20), (100, 255, 100, 80), (100, 255, 100)
        )

        # Botão Enter pulsante
        pulse = int((math.sin(t * 3) + 1) * 0.5 * 40 + 215)
        enter_text = font_ui.render("Pressione ENTER para iniciar", True, (pulse, pulse, pulse))
        screen.blit(enter_text, (WIDTH // 2 - enter_text.get_width() // 2, HEIGHT - 70))

        pygame.display.flip()
        pygame.time.Clock().tick(30)

# ==========================================
# GAME LOOP STANDALONE
# ==========================================
def main():
    import sys
    from entities import Player
    # CutsceneODS3 já está definida neste arquivo (não importar de arquivo externo)

    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.get_surface()
    if screen is None:
        try:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
        except pygame.error:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Level 1")

    draw_menu(screen)

    clock = pygame.time.Clock()
    player = Player(WIDTH // 2 - 20, HEIGHT // 2 - 30)

    # Estados
    state = "CUTSCENE"
    cutscene = CutsceneODS3(WIDTH, HEIGHT)
    level1 = Level1Troll()

    won = False
    running = True
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if state == "CUTSCENE" and cutscene:
                cutscene.handle_event(event)

        if state == "CUTSCENE":
            if cutscene:
                cutscene.update()
                cutscene.draw(screen)
                if cutscene.finished:
                    cutscene = None
                    state = "LEVEL_1"
                    level1.reset(WIDTH, HEIGHT, player)
                    level1.start_time = time.time()
                    player.set_position(*level1.player_start)

        elif state == "LEVEL_1":
            if not level1.won:
                level1.handle_movement(player, keys)
            level1.update(player)
            level1.draw(screen, player)

            if not level1.won:
                if level1.camera:
                    screen_rect = level1.camera.apply(player.rect)
                    player.draw_at(screen, screen_rect.x, screen_rect.y)
                else:
                    player.draw(screen)
            else:
                pygame.display.flip()
                pygame.time.wait(2000)
                from utils import show_end_screen
                show_end_screen(
                    screen, clock,
                    "SAÚDE ATINGIDA!", "Acesso de recursos garantido ao hospital.",
                    (34, 255, 136), "CONTINUAR",
                    stats=None,
                    lesson="Investir na saúde pública reduz mortalidade e promove qualidade de vida."
                )
                won = True
                running = False

        pygame.display.flip()

    return won

if __name__ == "__main__":
    main()
    pygame.quit()

def run_level_1():
    """Executa o Level 1 e retorna True se o jogador venceu."""
    try:
        won = main()
        return bool(won)
    except Exception as e:
        print(f"Erro ao executar Level 1: {e}")
        import traceback
        traceback.print_exc()
        return False
