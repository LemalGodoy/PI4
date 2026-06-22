import pygame
import random
import os
import settings


class Player:
    """Jogador unificado para Lobby e fases de plataforma.
    Prioriza a estrutura de assets da classe Jogador antiga, mas 
    mantém a robustez e interfaces do antigo Player.
    """
    SPRITE_FILES = {
        "idle": "assets/iddle.png",
        "run": "assets/run.png",
        "jump_prep": "assets/jump.png",
        "jump_up": "assets/jump.png",
        "jump_apex": "assets/jump.png",
        "jump_fall": "assets/jump.png",
        "jump_land": "assets/jump.png",
        "fall": "assets/jump.png",
        "fall_land": "assets/jump.png",
        "shoot1": "assets/shoot1.png",
        "shoot2": "assets/shoot2.png",
        "shootjump": "assets/shootjump.png",
        "shootrun": "assets/shootrun.png"
    }
    FRAME_SIZE = (80, 80)
    
    # Constants from level_5
    DASH_SPEED = 11
    DASH_FRAMES = 8
    DASH_CD = 50
    SHOOT_CD = 10
    BULLET_SPEED = 9
    PLAYER_MAX_HP = 5
    INV_FRAMES = 60

    
    def __init__(self, x=None, y=None, CHAO_Y=None):
        if x is None and CHAO_Y is not None:
            # Compatibilidade com a inicialização antiga da classe Jogador
            x = 100
            y = CHAO_Y - 80 + 10
        elif x is None:
            x, y = 0, 0
            
        self.rect = pygame.Rect(x, y, 40, 80)
        self.pos_x, self.pos_y = float(self.rect.x), float(self.rect.y)
        self.speed = 8
        self.inverted_controls = False

        # Movimento / física
        self.velX = 0.0
        self.velY = 0.0
        self.velocidadeMax = 400
        self.aceleracao = 1000
        self.desaceleracao = 1400
        self.forcaPulo = -820
        self.gravidade = 1600
        self.gravidadeQueda = 2000
        self.noChao = True
        self.jumpBuffer = 0
        self.direcao = "direita"

        # Compat: facing para outras partes
        self.facing = "right"

        # Animações
        self.estado = "idle"
        self.frame_index = 0
        self.frame_timer = 0
        self.anim_speed = 0.15
        self.run_anim_speed = 0.06
        self.animations = {}
        self.current_animation = []
        self._anim_nome = ""

        # Sistema de pulo simplificado
        self.fase_pulo = None
        self.pulo_anterior_em_chao = True
        self.landing_frame_counter = 0

        # Sistema de tiro
        self.is_shooting = False
        self.shoot_timer = 0
        self.shoot_duration = 0.2
        self.shoot_anim_name = ""
        self.shoot_from_run = False

        # Compat: frames legados
        self.frames = []
        self.is_moving = False
        self.ANIM_SPEED = self.anim_speed

        # Atributos de level 5 boss fight
        self.hp = self.PLAYER_MAX_HP
        self.inv = 0
        self.dash_t = 0
        self.dash_cd_timer = 0
        self.dash_dir = 1
        self.shoot_cd_timer = 0

        self.load_all_animations()
        self.set_animation("idle")

    # Propriedades de compatibilidade com level 5
    @property
    def x(self): return self.pos_x
    @x.setter
    def x(self, val): self.pos_x = float(val); self.rect.x = int(val)
    @property
    def y(self): return self.pos_y
    @y.setter
    def y(self, val): self.pos_y = float(val); self.rect.y = int(val)
    @property
    def w(self): return self.rect.width
    @w.setter
    def w(self, val): self.rect.width = int(val)
    @property
    def h(self): return self.rect.height
    @h.setter
    def h(self, val): self.rect.height = int(val)
    @property
    def vx(self): return self.velX
    @vx.setter
    def vx(self, val): self.velX = float(val)
    @property
    def vy(self): return self.velY
    @vy.setter
    def vy(self, val): self.velY = float(val)
    @property
    def on_ground(self): return self.noChao
    @on_ground.setter
    def on_ground(self, val): self.noChao = bool(val)

    def reset_boss_fight(self, ground_y):
        self.set_position(120.0, float(ground_y - 80))
        self.hp = self.PLAYER_MAX_HP
        self.inv = 0
        self.dash_t = 0
        self.dash_cd_timer = 0
        self.shoot_cd_timer = 0
        self.is_shooting = False
        self.fase_pulo = None
        self.noChao = False
        self.facing = "right"
        self.direcao = "direita"

    def take_hit(self):
        if self.inv > 0 or self.dash_t > 0: return False
        self.hp -= 1
        self.inv = self.INV_FRAMES
        return True

    def update_boss_fight(self, keys, bullets, chao_y, largura_mapa, platforms=None):
        # Movimentação e pulo idênticos à fase 2 (update_platform)
        dt = 1.0 / 60.0
        self.frame_timer += dt
        
        mov = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: mov = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: mov = 1
        
        # Gerenciamento do Dash
        if self.dash_t > 0:
            self.velX = self.DASH_SPEED * self.dash_dir * 60
            self.dash_t -= 1
        else:
            if mov:
                self.direcao = "direita" if mov > 0 else "esquerda"
                self.facing = "right" if mov > 0 else "left"
                acel = self.desaceleracao if mov * self.velX < 0 else self.aceleracao
                self.velX = max(-self.velocidadeMax, min(self.velocidadeMax, self.velX + mov * acel * dt))
            else:
                self.velX = max(0, abs(self.velX) - self.desaceleracao * dt) * (1 if self.velX > 0 else -1)
                
            if keys[pygame.K_SPACE] and self.dash_cd_timer <= 0:
                self.dash_dir = 1 if self.facing == "right" else -1
                self.dash_t = self.DASH_FRAMES
                self.dash_cd_timer = self.DASH_CD
                
            if keys[pygame.K_f] and self.shoot_cd_timer <= 0:
                self.is_shooting = True
                self.shoot_timer = 0.2
                self.shoot_anim_name = random.choice(["shoot1", "shoot2"])
                
                aim_x, aim_y = 0, 0
                if keys[pygame.K_a] or keys[pygame.K_LEFT]: aim_x = -1
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]: aim_x = 1
                if keys[pygame.K_w] or keys[pygame.K_UP]: aim_y = -1
                if keys[pygame.K_s] or keys[pygame.K_DOWN]: aim_y = 1
                if aim_x == 0 and aim_y == 0:
                    aim_x = 1 if self.facing == "right" else -1
                    
                import math
                length = math.sqrt(aim_x * aim_x + aim_y * aim_y)
                if length > 0: aim_x /= length; aim_y /= length
                
                bx = self.pos_x + self.rect.width / 2
                by = self.pos_y + self.rect.height / 2
                bullets.append(PlayerBullet(bx, by, aim_x, aim_y))
                self.shoot_cd_timer = self.SHOOT_CD

        self.pos_x += self.velX * dt
        self.rect.x = int(self.pos_x)
        
        if self.pos_x < 0:
            self.pos_x, self.rect.x, self.velX = 0, 0, 0
        elif self.pos_x > largura_mapa - self.rect.width:
            self.pos_x = largura_mapa - self.rect.width
            self.rect.x = int(self.pos_x)
            self.velX = 0

        # Lógica de Pulo
        self.jumpBuffer = max(0, self.jumpBuffer - dt)
        if (keys[pygame.K_w] or keys[pygame.K_UP]):
            if self.noChao:
                self.velY = self.forcaPulo
                self.noChao = False
                self.jumpBuffer = 0
            else:
                self.jumpBuffer = 0.15

        # Gravidade da fase 2
        self.velY += (self.gravidade if self.velY < 0 else self.gravidadeQueda) * dt
        self.pos_y += self.velY * dt
        self.rect.y = int(self.pos_y)
        self.noChao = False
        
        # Colisão com o chão
        if self.rect.bottom >= chao_y + 10:
            self.rect.bottom = chao_y + 10
            self.velY = 0
            self.noChao = True
            self.pos_y = float(self.rect.y)
            
        # Colisão com plataformas da Boss Fight
        if platforms:
            for plat in platforms:
                if plat.check_player_land(self):
                    self.y = plat.y - self.h
                    self.velY = 0
                    self.noChao = True
                    self.pos_y = float(self.rect.y)
                    break
            
        # Pulo de fato
        if self.jumpBuffer > 0 and self.noChao:
            self.velY = self.forcaPulo
            self.noChao = False
            self.jumpBuffer = 0
        elif not (keys[pygame.K_w] or keys[pygame.K_UP]) and self.velY < 0:
            self.velY *= 0.7

        if self.dash_cd_timer > 0: self.dash_cd_timer -= 1
        if self.shoot_cd_timer > 0: self.shoot_cd_timer -= 1
        if self.inv > 0: self.inv -= 1

        if self.is_shooting:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.is_shooting = False

        self.fase_pulo = self.calcular_fase_pulo()
        self.estado = self.determinar_estado_animacao()
        if self._anim_nome != self.estado:
            if self.estado not in self.animations:
                self.set_animation("idle")
            else:
                self.set_animation(self.estado)
        self.atualizar_animacao(dt)

        
    def set_position(self, x, y):
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.velX = 0.0
        self.velY = 0.0
        self.jumpBuffer = 0
        self.is_shooting = False
        self.fase_pulo = None
        self.noChao = False

    def load_all_animations(self):
        for estado, filename in self.SPRITE_FILES.items():
            sprite_path = filename
            # Fallbacks para manter a robustez do antigo Player
            if not os.path.exists(sprite_path):
                for search_dir in [getattr(settings, "ASSETS_DIR", ""), getattr(settings, "SCRIPT_DIR", "")]:
                    if search_dir:
                        candidate = os.path.join(search_dir, os.path.basename(filename))
                        if os.path.exists(candidate):
                            sprite_path = candidate
                            break

            try:
                folha = pygame.image.load(sprite_path).convert_alpha()
            except Exception:
                try:
                    folha = pygame.image.load(sprite_path)
                except Exception:
                    folha = None
                    
            frames = []
            if folha:
                frame_w, frame_h = self.FRAME_SIZE
                num_frames = folha.get_width() // frame_w
                for i in range(num_frames):
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(folha, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    frames.append(frame)
            self.animations[estado] = frames

    def set_animation(self, estado):
        self._anim_nome = estado
        self.current_animation = self.animations.get(estado, [])
        if self.current_animation:
            self.frame_index = self.frame_index % len(self.current_animation)
            self.rect.height = self.current_animation[0].get_height()
        self.frames = self.current_animation

    def calcular_fase_pulo(self):
        if self.noChao:
            if not self.pulo_anterior_em_chao:
                self.landing_frame_counter = 1
            self.pulo_anterior_em_chao = True
            return None

        self.pulo_anterior_em_chao = False
        if self.velY < -300:
            return "up"
        elif -300 <= self.velY < 300:
            return "apex"
        else:
            return "fall"

    def iniciar_animacao_tiro(self):
        if self.noChao:
            if abs(self.velX) < 5:
                self.is_shooting = True
                self.shoot_timer = self.shoot_duration
                self.shoot_anim_name = random.choice(["shoot1", "shoot2"])
                self.shoot_from_run = False
            else:
                self.is_shooting = True
                self.shoot_timer = self.shoot_duration
                self.shoot_anim_name = "shootrun"
                self.shoot_from_run = True
        else:
            self.is_shooting = True
            self.shoot_timer = self.shoot_duration
            self.shoot_anim_name = "shootjump"
            self.shoot_from_run = False

    def determinar_estado_animacao(self):
        if self.is_shooting:
            return self.shoot_anim_name
        if self.landing_frame_counter > 0:
            self.landing_frame_counter -= 1
            return "jump_land" if self.jumpBuffer > 0 else "fall_land"
        if self.noChao:
            return "run" if abs(self.velX) > 5 else "idle"
        
        if self.fase_pulo == "up":
            return "jump_up"
        elif self.fase_pulo == "apex":
            return "jump_apex"
        elif self.fase_pulo == "fall":
            return "jump_fall" if self.jumpBuffer > 0 else "fall"
        return "idle"

    def atualizar_animacao(self, dt):
        if not self.current_animation:
            return
        if self.estado.startswith("jump_") or self.estado in ["fall", "fall_land"]:
            phase_map = {
                "jump_prep": 0, "jump_up": 1, "jump_apex": 2,
                "jump_fall": 3, "fall": 3, "jump_land": 4, "fall_land": 4
            }
            if self.estado in phase_map:
                self.frame_index = min(phase_map[self.estado], len(self.current_animation) - 1)
        else:
            self.frame_timer += dt
            if self.is_shooting and not getattr(self, 'shoot_from_run', False):
                anim_speed = self.shoot_duration / max(1, len(self.current_animation))
            else:
                anim_speed = self.run_anim_speed if self.estado in ["run", "shootrun"] else self.anim_speed
            
            if self.frame_timer >= anim_speed:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.current_animation)

    def move(self, keys):
        """Movimento top-down (lobby)."""
        old_x, old_y = self.rect.x, self.rect.y

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direcao = "esquerda"
            self.facing = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direcao = "direita"
            self.facing = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        self.rect.x = max(0, min(self.rect.x, settings.WORLD_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, settings.WORLD_HEIGHT - self.rect.height))

        self.pos_x, self.pos_y = float(self.rect.x), float(self.rect.y)
        self.is_moving = (self.rect.x != old_x or self.rect.y != old_y)
        self.velX = self.speed if self.is_moving else 0.0

        self.noChao = True
        self.fase_pulo = None

        if self.is_shooting:
            self.shoot_timer -= 1.0 / 60.0
            if self.shoot_timer <= 0:
                self.is_shooting = False

        self.estado = self.determinar_estado_animacao()
        if self._anim_nome != self.estado:
            if self.estado not in self.animations:
                self.set_animation("idle")
            else:
                self.set_animation(self.estado)
        self.atualizar_animacao(1.0 / 60.0)

    def update(self, dt, teclas, mov, CHAO_Y, LARGURA_MAPA, plataformas=None, chao_ativo=True):
        """Alias mantido por compatibilidade com a antiga classe Jogador."""
        self.update_platform(dt, teclas, mov, CHAO_Y, LARGURA_MAPA, plataformas, chao_ativo)

    def update_platform(self, dt, teclas, mov, CHAO_Y, LARGURA_MAPA, plataformas=None, chao_ativo=True):
        if self.is_shooting:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.is_shooting = False

        self.jumpBuffer = max(0, self.jumpBuffer - dt)
        if mov:
            self.direcao = "direita" if mov > 0 else "esquerda"
            self.facing = "right" if mov > 0 else "left"
            acel = self.desaceleracao if mov * self.velX < 0 else self.aceleracao
            self.velX = max(-self.velocidadeMax, min(self.velocidadeMax, self.velX + mov * acel * dt))
        else:
            self.velX = max(0, abs(self.velX) - self.desaceleracao * dt) * (1 if self.velX > 0 else -1)

        self.pos_x += self.velX * dt
        self.rect.x = int(self.pos_x)

        if plataformas:
            for p in plataformas:
                if self.rect.colliderect(p):
                    if self.rect.bottom > p.top + 10:
                        if self.velX > 0:
                            self.rect.right = p.left
                        elif self.velX < 0:
                            self.rect.left = p.right
                        self.pos_x = float(self.rect.x)
                        self.velX = 0

        if self.pos_x < 0:
            self.pos_x, self.rect.x, self.velX = 0, 0, 0
        elif self.pos_x > LARGURA_MAPA - self.rect.width:
            self.pos_x = LARGURA_MAPA - self.rect.width
            self.rect.x = int(self.pos_x)
            self.velX = 0

        self.velY += (self.gravidade if self.velY < 0 else self.gravidadeQueda) * dt
        self.pos_y += self.velY * dt
        self.rect.y = int(self.pos_y)
        self.noChao = False

        if chao_ativo and self.rect.bottom >= CHAO_Y + 10:
            self.rect.bottom = CHAO_Y + 10
            self.velY = 0
            self.noChao = True
            self.pos_y = float(self.rect.y)

        if plataformas:
            for p in plataformas:
                if self.rect.colliderect(p) or (self.velY >= 0 and self.rect.move(0, 1).colliderect(p)):
                    if self.velY >= 0 and self.rect.bottom - self.velY * dt <= p.top + 10:
                        self.rect.bottom = p.top
                        self.velY = 0
                        self.noChao = True
                        self.pos_y = float(self.rect.y)
                        break
                    elif self.velY < 0 and self.rect.top - self.velY * dt >= p.bottom - 10:
                        if self.rect.colliderect(p):
                            self.rect.top = p.bottom
                            self.velY = 0
                            self.pos_y = float(self.rect.y)
                            break

        if self.jumpBuffer > 0 and self.noChao:
            self.velY = self.forcaPulo
            self.noChao = False
            self.jumpBuffer = 0
        elif not (teclas[pygame.K_w] or teclas[pygame.K_UP]) and self.velY < 0:
            self.velY *= 0.7

        self.fase_pulo = self.calcular_fase_pulo()
        self.estado = self.determinar_estado_animacao()

        if self._anim_nome != self.estado:
            if self.estado not in self.animations:
                self.set_animation("idle")
            else:
                self.set_animation(self.estado)

        self.atualizar_animacao(dt)

    def draw(self, surface):
        self.draw_at(surface, self.rect.x, self.rect.y)

    def draw_at(self, surface, x, y):
        # Piscar por invencibilidade
        if getattr(self, 'inv', 0) > 0 and int(self.frame_timer * 60) % 4 < 2: return

        # Glow e Dash Trail (boss fight)
        w, h = 80, 80 # Tamanho visual base do sprite
        offsetX = (w - self.rect.width) // 2
        sprite_x, sprite_y = x - offsetX, y - (h - self.rect.height) // 2

        if getattr(self, 'dash_t', 0) > 0:
            for i in range(1, 4):
                ts = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(ts, (50, 160, 255, max(0, 70 - i * 22)), (0, 0, w, h), border_radius=5)
                surface.blit(ts, (sprite_x - getattr(self, 'dash_dir', 1) * i * 14, sprite_y))
                
        # Glow
        if hasattr(self, 'hp'):  # Indica que está na boss fight
            gs = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (50, 150, 255, 22), gs.get_rect())
            surface.blit(gs, (sprite_x - 12, sprite_y - 12))

        if self.current_animation:
            sprite = self.current_animation[self.frame_index % len(self.current_animation)]
            if self.direcao == "esquerda" or self.facing == "left":
                sprite = pygame.transform.flip(sprite, True, False)
            offsetX = (sprite.get_width() - self.rect.width) // 2
            surface.blit(sprite, (x - offsetX, y))
        else:
            pygame.draw.rect(surface, (120, 120, 120), (x + 8, y + 20, 24, 25))
            pygame.draw.rect(surface, (80, 50, 30), (x + 8, y + 40, 24, 5))
            pygame.draw.rect(surface, (60, 60, 60), (x + 10, y + 45, 8, 15))
            pygame.draw.rect(surface, (60, 60, 60), (x + 22, y + 45, 8, 15))
            pygame.draw.rect(surface, (40, 40, 40), (x + 8, y + 55, 10, 5))
            pygame.draw.rect(surface, (40, 40, 40), (x + 22, y + 55, 10, 5))
            pygame.draw.rect(surface, (100, 100, 100), (x, y + 22, 8, 18))
            pygame.draw.rect(surface, (100, 100, 100), (x + 32, y + 22, 8, 18))
            pygame.draw.rect(surface, (180, 180, 180), (x + 6, y + 5, 28, 20))
            pygame.draw.rect(surface, (30, 30, 30), (x + 12, y + 10, 16, 6))

class PlayerBullet:
    def __init__(self, x, y, dx, dy):
        self.x, self.y = float(x), float(y)
        self.dx, self.dy = dx, dy
        self.alive = True
    def update(self, max_x=5000, max_y=5000):
        self.x += 9 * self.dx  # BULLET_SPEED
        self.y += 9 * self.dy
        if self.x < -20 or self.x > max_x + 20 or self.y < -20 or self.y > max_y + 20:
            self.alive = False
    def rect(self): return pygame.Rect(int(self.x) - 6, int(self.y) - 6, 12, 12)
    def draw(self, surf, cam_x=0, cam_y=0):
        x, y = int(self.x - cam_x), int(self.y - cam_y)
        gs = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(gs, (80, 200, 255, 50), (10, 10), 10)
        surf.blit(gs, (x - 10, y - 10))
        pygame.draw.circle(surf, (140, 220, 255), (x, y), 5)
        pygame.draw.circle(surf, (255, 255, 255), (x, y), 3)


class Camera:
    def __init__(self, largura_tela, largura_mapa):
        self.x = 0.0
        self.offset_x = 0
        self.largura_tela, self.largura_mapa = largura_tela, largura_mapa
        self.pos_tela = largura_tela / 2

    def update(self, dt, jogador, mov):
        # Se o mapa for menor que a tela (ex: casas de 800px em tela de 1280px)
        if self.largura_mapa < self.largura_tela:
            self.offset_x = (self.largura_tela - self.largura_mapa) // 2
            self.x = 0
            return
        
        self.offset_x = 0
        alvo_pos = self.largura_tela * (0.4 if mov > 0 else 0.6 if mov < 0 else 0.45 if jogador.direcao == "direita" else 0.55)
        self.pos_tela += (alvo_pos - self.pos_tela) * 2.0 * dt
        alvoCamera = jogador.rect.centerx - self.pos_tela
        vel = min(0.5 + abs(alvoCamera - self.x) / 80.0 * 4.5, 8.0)
        self.x = max(0, min(self.x + (alvoCamera - self.x) * vel * dt, self.largura_mapa - self.largura_tela))

class SistemaVisual:
    def __init__(self, largura, altura, zoom_max=3.0):
        self.nivel = 1.0
        self.max = zoom_max
        self.largura, self.altura = largura, altura
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.nivel = max(1.0, min(self.max, self.nivel + (0.1 if event.y > 0 else -0.1)))

    def render(self, surface_jogo, tela_display, mouse_pos):
        if self.nivel == 1.0:
            tela_display.blit(surface_jogo, (0, 0))
            return
            
        nw, nh = int(self.largura * self.nivel), int(self.altura * self.nivel)
        scaled = pygame.transform.smoothscale(surface_jogo, (nw, nh))
        
        px, py = mouse_pos[0] / self.largura, mouse_pos[1] / self.altura
        ox = max(-nw + self.largura, min(0, int(mouse_pos[0] - nw * px)))
        oy = max(-nh + self.altura, min(0, int(mouse_pos[1] - nh * py)))
        
        tela_display.fill((0, 0, 0))
        tela_display.blit(scaled, (ox, oy))

    def get_mouse_tela(self, mouse_pos):
        if self.nivel == 1.0:
            return mouse_pos
        nw, nh = int(self.largura * self.nivel), int(self.altura * self.nivel)
        px, py = mouse_pos[0] / self.largura, mouse_pos[1] / self.altura
        ox = max(-nw + self.largura, min(0, int(mouse_pos[0] - nw * px)))
        oy = max(-nh + self.altura, min(0, int(mouse_pos[1] - nh * py)))
        
        tela_x = (mouse_pos[0] - ox) / self.nivel
        tela_y = (mouse_pos[1] - oy) / self.nivel
        return (tela_x, tela_y)


class Platform:
    """Uma Plataforma Mestra com status Active para armadilhas fáceis"""
    def __init__(self, x, y, w, h, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.active = True

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)


class Trap:
    """Qualquer armadilha fatal ou esmagadora"""
    def __init__(self, x, y, w, h, trap_type="spike", color=(200, 50, 50)):
        self.rect = pygame.Rect(x, y, w, h)
        self.trap_type = trap_type
        self.color = color
        self.active = True

    def check_collision(self, player):
        return self.active and player.rect.colliderect(self.rect)

    def draw(self, surface):
        if not self.active:
            return

        if self.trap_type == "spike":
            pygame.draw.polygon(surface, self.color, [
                (self.rect.left, self.rect.bottom),
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.bottom)
            ])
        elif self.trap_type == "block":
            pygame.draw.rect(surface, (80, 80, 80), self.rect)
            pygame.draw.rect(surface, (255, 0, 0),
                             (self.rect.x + 10, self.rect.bottom - 20,
                              self.rect.w - 20, 10))


class Trigger:
    """O Coração das Trollagens Invisíveis"""
    def __init__(self, x, y, w, h, callback_action, trigger_once=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.action = callback_action
        self.trigger_once = trigger_once
        self.has_triggered = False

    def check(self, player):
        if not self.has_triggered and player.rect.colliderect(self.rect):
            self.action()
            if self.trigger_once:
                self.has_triggered = True


class Door:
    """Porta/Barraca do Bazar ODS"""
    def __init__(self, rect, door_id, name, color):
        self.rect = rect
        self.id = door_id
        self.name = name
        self.color = color
