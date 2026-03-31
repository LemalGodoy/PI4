"""
Level 1 — ODS 3: Saúde e Bem-Estar  (estilo Level Devil / Troll)

Fase horizontalmente longa (~3600 px) com câmera scrolling, dividida em 3 seções:
  • SEÇÃO A (0–1200)   — Tutorial troll: plataformas de cápsula + primeiros sustos.
  • SEÇÃO B (1200–2400) — Escalada: plataformas escorregadias, efeito colateral, spikes.
  • SEÇÃO C (2400–3600) — Clímax: porta fake de hospital, plataformas piscam, porta real.

SEM checkpoints — morte reinicia a fase inteira.
Tema: hospitalar / saúde — fundo parallax com profundidade (cidade + hospital).
Triggers troll inspirados em Level Devil, todos possíveis de superar.
"""
from __future__ import annotations

import math
import random

import pygame

from engine.camera import Camera
from engine.entities import Platform, Trap, Trigger


# ====================================================================== #
#  Constantes do mundo
# ====================================================================== #
WORLD_W = 3600
WORLD_H = 768
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
    """Fase 1 — ODS 3: Saúde e Bem-Estar — Level Devil troll."""

    def __init__(self):
        self.player_start = PLAYER_START
        self.world_w = WORLD_W
        self.world_h = WORLD_H

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
            Platform(30,  520, 260, 35, ODS3_GREEN),          # 0  — chão inicial (grande, seguro)
            Platform(330, 470, 160, 30, CAPSULE_WHITE),       # 1  — cápsula branca
            Platform(530, 420, 150, 30, CAPSULE_RED),         # 2  — cápsula vermelha (vai sumir!)
            Platform(720, 480, 200, 35, ODS3_GREEN),          # 3  — descanso seguro
            Platform(960, 420, 170, 30, CAPSULE_WHITE),       # 4  — subida suave
            Platform(1120, 520, 130, 30, ODS3_GREEN),         # 5  — degrau de transição

            # ===== SEÇÃO B (1200 – 2400) — "Farmácia" ===== #
            Platform(1250, 480, 200, 35, ODS3_GREEN),         # 6  — entrada seção B
            Platform(1440, 410, 160, 30, CAPSULE_WHITE),      # 7  — plataforma que escorrega
            Platform(1640, 350, 150, 30, ODS3_GREEN_LIGHT),   # 8  — plataforma MÓVEL
            Platform(1830, 430, 180, 30, CAPSULE_RED),        # 9  — spike sobe (injeção)
            Platform(2020, 370, 170, 30, CAPSULE_WHITE),      # 10 — ponte após spike
            Platform(2200, 470, 160, 35, ODS3_GREEN),         # 11 — descanso antes seção C

            # ===== SEÇÃO C (2400 – 3600) — "Hospital / Cura" ===== #
            Platform(2380, 510, 220, 35, ODS3_GREEN),         # 12 — entrada seção C
            Platform(2600, 430, 160, 30, CAPSULE_WHITE),      # 13 — pisca
            Platform(2780, 360, 150, 30, ODS3_GREEN_LIGHT),   # 14 — pisca
            Platform(2960, 450, 200, 35, ODS3_GREEN),         # 15 — plataforma porta fake
            Platform(3180, 400, 170, 30, CAPSULE_WHITE),      # 16 — penúltima
            Platform(3380, 480, 180, 35, ODS3_GREEN),         # 17 — plataforma da PORTA FINAL
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
        self.ceiling_block = Trap(530, -200, 100, 80, "block", (80, 80, 80))
        self.ceiling_block.active = True

        # --------------------------------------------------------------- #
        #  PORTAS
        # --------------------------------------------------------------- #
        # Porta fake (engana o jogador na seção C)
        self.door_fake = pygame.Rect(3020, 350, 60, 100)
        # Porta real (aparece depois do trigger da fake)
        self.door_real = pygame.Rect(0, 0, 0, 0)
        # PORTA FINAL — sempre visível no final da fase
        self.door_final = pygame.Rect(3420, 380, 60, 100)

        # --------------------------------------------------------------- #
        #  TRIGGERS — callbacks inteligentes (Level Devil style)
        # --------------------------------------------------------------- #
        self.triggers = []

        # ---- SEÇÃO A ------------------------------------------------- #
        # T0 — Ao chegar perto da plat 2: teto começa a descer com pré-aviso
        def _trig_teto():
            self.t_teto_active = True
            self._start_shake(2, 45)  # plat 2 treme = aviso

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
            self._blink_timer = 150  # 2.5 seg piscando

        # T6 — Porta fake "foge" + plat some + porta real aparece embaixo
        def _trig_porta_fuga():
            if self._fake_door_triggered:
                return
            self._fake_door_triggered = True
            self.door_fake.y = 9999  # some
            self.platforms[15].active = False
            # Plataforma de emergência + porta real com coração
            self.platforms.append(Platform(2920, 620, 280, 30, ODS3_GREEN))
            self.door_real = pygame.Rect(3020, 520, 60, 100)

        # T7 — "Ambulância" — plataforma da porta real se move
        def _trig_ambulance():
            if len(self.platforms) > 18:
                self._ambulance_active = True
                self._ambulance_plat = self.platforms[18]  # plat de emergência
                self._ambulance_origin_x = self._ambulance_plat.rect.x

        # --------------------------------------------------------------- #
        #  Montar lista de triggers
        # --------------------------------------------------------------- #
        self.triggers = [
            # Seção A
            Trigger(460, 0, 20, WORLD_H, _trig_teto),              # T0
            Trigger(660, 0, 20, WORLD_H, _trig_plat2_vanish),      # T1

            # Seção B
            Trigger(1400, 0, 20, WORLD_H, _trig_slide),            # T2
            Trigger(1780, 0, 20, WORLD_H, _trig_injection),        # T3
            Trigger(1960, 0, 20, WORLD_H, _trig_side_effect),      # T4

            # Seção C
            Trigger(2550, 0, 20, WORLD_H, _trig_blink),            # T5
            Trigger(2930, 0, 20, WORLD_H, _trig_porta_fuga),       # T6
            Trigger(2980, 0, 20, WORLD_H, _trig_ambulance),        # T7
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
    #  MOVEMENT — lógica de movimento e colisão
    # ================================================================== #
    def handle_movement(self, player, keys) -> None:
        # Direções (respeita inversão por efeito colateral)
        left_keys = (pygame.K_a, pygame.K_LEFT)
        right_keys = (pygame.K_d, pygame.K_RIGHT)

        if player.inverted_controls:
            left_keys, right_keys = right_keys, left_keys

        dx = 0
        for k in left_keys:
            if keys[k]:
                dx = -player.speed
        for k in right_keys:
            if keys[k]:
                dx = player.speed

        # Movimento horizontal + colisão
        player.rect.x += dx
        for p in self.platforms:
            if p.active and player.rect.colliderect(p.rect):
                if dx > 0:
                    player.rect.right = p.rect.left
                elif dx < 0:
                    player.rect.left = p.rect.right

        # Limite esquerdo
        if player.rect.left < 0:
            player.rect.left = 0

        # Pulo
        jump_keys = (pygame.K_UP, pygame.K_w, pygame.K_SPACE)
        if any(keys[k] for k in jump_keys) and self.is_grounded:
            self.dy = JUMP_FORCE
            self.is_grounded = False

        # Gravidade
        self.dy += GRAVITY
        if self.dy > MAX_FALL:
            self.dy = MAX_FALL

        player.rect.y += int(self.dy)

        # Colisão vertical
        self.is_grounded = False
        for p in self.platforms:
            if p.active and player.rect.colliderect(p.rect):
                if self.dy > 0:
                    player.rect.bottom = p.rect.top
                    self.dy = 0
                    self.is_grounded = True
                elif self.dy < 0:
                    player.rect.top = p.rect.bottom
                    self.dy = 0

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
        if self.t_teto_active and self.ceiling_block.rect.bottom < 450:
            self.ceiling_block.rect.y += 12
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
        vp_w = self.camera.vp_w if self.camera else 1376
        vp_h = self.camera.vp_h if self.camera else 768
        player.inverted_controls = False
        self.reset(vp_w, vp_h, player)

    # ================================================================== #
    #  DRAW
    # ================================================================== #
    def draw(self, surface, camera: Camera | None = None) -> None:
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
        font = pygame.font.Font(None, 24)
        if self.door_fake.top < WORLD_H:
            dr = cam.apply(self.door_fake) if cam else self.door_fake
            self._draw_hospital_door(surface, dr, fake=True)
            txt = font.render("SAIDA", True, WHITE)
            surface.blit(txt, (dr.centerx - txt.get_width() // 2, dr.top - 22))

        # ----- Porta Real (coração brilhante — aparece após trigger) ----- #
        if self.door_real.width > 0:
            dr = cam.apply(self.door_real) if cam else self.door_real
            self._draw_hospital_door(surface, dr, fake=False)
            txt2 = font.render("SAIDA REAL", True, ODS3_GREEN)
            surface.blit(txt2, (dr.centerx - txt2.get_width() // 2, dr.top - 22))

        # ----- PORTA FINAL (sempre visível, com efeito pulsante) ----- #
        if self.door_final.width > 0:
            dr = cam.apply(self.door_final) if cam else self.door_final
            self._draw_final_door(surface, dr)

        # ----- HUD ----- #
        self._draw_hud(surface)

        # ----- Vitória ----- #
        if self.won:
            vp_w = surface.get_width()
            vp_h = surface.get_height()
            # Overlay escuro
            overlay = pygame.Surface((vp_w, vp_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))

            font_win = pygame.font.Font(None, 72)
            txt_win = font_win.render("Fase Concluida!", True, ODS3_GREEN_LIGHT)
            surface.blit(txt_win, (vp_w // 2 - txt_win.get_width() // 2, vp_h // 2 - 50))

            sub = pygame.font.Font(None, 30)
            txt_sub = sub.render("ODS 3 -- Saude e Bem-Estar", True, WHITE)
            surface.blit(txt_sub, (vp_w // 2 - txt_sub.get_width() // 2, vp_h // 2 + 20))

            txt_back = sub.render("Voltando ao Bazar...", True, (200, 200, 200))
            surface.blit(txt_back, (vp_w // 2 - txt_back.get_width() // 2, vp_h // 2 + 60))

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

        # Texto "SAUDE" na porta
        font_door = pygame.font.Font(None, 18)
        txt_saude = font_door.render("SAUDE", True, ODS3_GREEN_DARK)
        surface.blit(txt_saude, (x + w // 2 - txt_saude.get_width() // 2, y + h * 2 // 3))

        # Maçaneta dourada
        pygame.draw.circle(surface, (255, 215, 0), (x + w - 10, y + h // 2), 6)
        pygame.draw.circle(surface, (200, 170, 0), (x + w - 10, y + h // 2), 6, 2)

        # Label acima da porta
        font_label = pygame.font.Font(None, 26)

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
    def _draw_hud(self, surface: pygame.Surface) -> None:
        vp_w = surface.get_width()
        font_hud = pygame.font.Font(None, 22)
        font_title = pygame.font.Font(None, 18)

        # Título ODS 3
        title_txt = font_title.render("ODS 3 -- Saude e Bem-Estar", True, ODS3_GREEN_LIGHT)
        surface.blit(title_txt, (vp_w // 2 - title_txt.get_width() // 2, 8))

        # Indicador de seção baseado na posição do jogador
        if self.camera:
            cam_x = self.camera.offset_x
            if cam_x < 1200:
                sec_name = "Consulta Medica"
            elif cam_x < 2400:
                sec_name = "Farmacia"
            else:
                sec_name = "Hospital — Cura"
        else:
            sec_name = "Consulta Medica"
        sec_txt = font_hud.render(sec_name, True, (200, 220, 200))
        surface.blit(sec_txt, (10, 10))

        # Coração de vida (decorativo)
        _draw_pixel_heart(surface, vp_w - 30, 20, 8, HEART_RED)

        # Dica: sem checkpoints
        hint_font = pygame.font.Font(None, 16)
        hint_txt = hint_font.render("Sem checkpoints — cuidado!", True, (180, 140, 140))
        surface.blit(hint_txt, (vp_w - hint_txt.get_width() - 10, 38))

        # Aviso de efeito colateral
        if self._side_effect_text_timer > 0:
            # Pisca o aviso
            if (self._side_effect_text_timer // 8) % 2 == 0:
                warn_font = pygame.font.Font(None, 36)
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
                blink_font = pygame.font.Font(None, 28)
                blink_txt = blink_font.render("INSTABILIDADE DETECTADA!", True, (255, 100, 100))
                bx = vp_w // 2 - blink_txt.get_width() // 2
                surface.blit(blink_txt, (bx, 70))


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
