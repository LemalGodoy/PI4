import pygame, sys, random, math, time
from entities import Player, PlayerBullet, Camera, SistemaVisual
from settings import *
from utils import load_scaled, draw_arrow_up, draw_key_hint

LARGURA_MAPA = 4000
CHAO_Y = 620

# ==========================================
# PARTÍCULAS (mesmo sistema da Fase 5)
# ==========================================
class Particle:
    __slots__ = ('x','y','vx','vy','color','life','max_life','size','grav')
    def __init__(self, x, y, color, vx=0, vy=0, life=25, size=3, grav=0):
        self.x, self.y = x, y
        self.color = color
        self.vx = vx + random.uniform(-0.8, 0.8)
        self.vy = vy + random.uniform(-0.8, 0.8)
        self.life = self.max_life = life
        self.size = size
        self.grav = grav

    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += self.grav
        self.life -= 1
        return self.life > 0

    def draw(self, surf, cam_x=0, cam_y=0):
        t = max(0.01, self.life / self.max_life)
        s = max(1, int(self.size * t))
        c = tuple(min(255, int(v * t)) for v in self.color)
        sx, sy = int(self.x - cam_x), int(self.y - cam_y)
        # Glow halo
        if s >= 2:
            gs = pygame.Surface((s*4, s*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*c, int(40 * t)), (s*2, s*2), s*2)
            surf.blit(gs, (sx - s*2, sy - s*2))
        pygame.draw.circle(surf, c, (sx, sy), s)

def spawn_hit_particles(particles, x, y, color, count=8):
    for _ in range(count):
        particles.append(Particle(x, y, color,
            random.uniform(-3, 3), random.uniform(-4, 1), random.randint(15, 30), random.randint(2, 4), 0.1))

CORES = {
    "idle": (255, 255, 255),
    "fundo": (0, 0, 0),
    "texto": (255, 255, 255),
    "chefe": (255, 255, 0),
    "instrucao": (200, 200, 200),
    "go": (255, 0, 0)
}

CENA_DESERTO = "deserto"
CENA_CASA = "casa"
CENA_DIALOGO = "dialogo"
CENA_BATALHA_FINAL = "batalha_final"
CENA_GAMEOVER = "gameover"
CENA_VITORIA = "vitoria"

class Game:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.get_surface()
        if self.tela is None:
            self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE)
        pygame.display.set_caption("Level 3 — ODS 6")
        self.clock = pygame.time.Clock()
        self.tela_jogo = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        self.load_assets()
        self.reset()
        self.visual = SistemaVisual(LARGURA_TELA, ALTURA_TELA)
        self.mouse_pos = (LARGURA_TELA // 2, ALTURA_TELA // 2)

    def load_assets(self):
        self.bg_mountains = load_scaled("assets/desert_mountains.png", ALTURA_TELA)
        self.bg_dunes = load_scaled("assets/desert_dunes.png", ALTURA_TELA)
        self.bg_ground = load_scaled("assets/desert_ground.png", ALTURA_TELA)
        self.img_chao = load_scaled("assets/chao_deserto.png", 160)
        self.w_chao = self.img_chao.get_width()
        self.img_coqueiro = load_scaled("assets/coqueiro.png", 200)
        self.img_casa1 = load_scaled("assets/casa1.png", 200)
        self.img_casa2 = load_scaled("assets/casa2.png", 280)
        self.img_aldeao1 = load_scaled("assets/aldeao1.png", 70)
        self.img_aldeao2 = load_scaled("assets/aldeao2.png", 70)
        self.img_chefe1 = load_scaled("assets/chefe1.png", 80)
        self.img_chefe2 = load_scaled("assets/chefe2.png", 75)
        self.img_chefe_dialogo = pygame.transform.flip(load_scaled("assets/chefe2.png", 900), True, False)
        self.img_chefe1_dialogo = pygame.transform.flip(load_scaled("assets/chefe1.png", 900), True, False)
        self.img_aldeao_dialogo1 = pygame.transform.flip(load_scaled("assets/aldeao1.png", 900), True, False)
        self.img_aldeao_dialogo2 = pygame.transform.flip(load_scaled("assets/aldeao2.png", 900), True, False)
        self.img_chao_casa = load_scaled("assets/chao_casa1.png", 160)
        self.w_chao_casa = self.img_chao_casa.get_width()
        self.img_chao_chefe = load_scaled("assets/chao_chefe.png", 160)
        self.w_chao_chefe = self.img_chao_chefe.get_width()
        self.img_alavanca = load_scaled("assets/alavanca.png", 50)
        self.img_hope = load_scaled("assets/hope.png", 900) 
        self.img_axe = load_scaled("assets/axe.png", 40)
        self.img_letter = load_scaled("assets/carta.png", 30)
        self.img_coco = load_scaled("assets/coco.png", 15)
        self.variacoes_cacto = []
        for h in [350, 450, 550]:
            img = load_scaled("assets/cacto.png", h)
            img_blur = pygame.transform.smoothscale(img, (img.get_width() // 4, img.get_height() // 4))
            self.variacoes_cacto.append(pygame.transform.smoothscale(img_blur, (img.get_width(), img.get_height())))
        self.cactos_fg = [(100, 420, 0), (1200, 370, 1), (2200, 320, 2)]
        self.fonts = {
            "ui": pygame.font.SysFont("Consolas", 20, bold=True),
            "dialogo": pygame.font.SysFont("Consolas", 16, bold=True),
            "instrucao": pygame.font.SysFont("Consolas", 12),
            "grande": pygame.font.SysFont("Consolas", 70, bold=True)
        }

    def reset(self):
        self.cena_atual = CENA_DESERTO
        self.largura_mapa_atual = LARGURA_MAPA
        self.pos_entrada_x = 0
        self.id_casa_atual = 0
        self.tipo_casa_proxima = None
        self.inventario = []
        self.machado_disponivel = True
        self.carta_disponivel = True
        self.lendo_carta = False
        self.npc_falando = None
        self.npc_falando_externo = False
        self.coqueiros_cortados = 0
        self.vila_reunida = False
        self.pos_ultimo_coqueiro = 0
        self.puzzle_alavancas = [{"x": 2000 + i*120, "ativo": False, "id": i+1} for i in range(5)]
        self.puzzle_sequencia = []
        self.puzzle_correto = [4, 3, 5, 1, 2]
        self.puzzle_vencido = False
        self.motivo_gameover = None
        self.boss_final_x = 3000
        self.boss_final_ativo = False
        self.boss_final_falando = False
        self.boss_final_concluido = False
        self.cocos_caindo = []
        self.projeteis = []
        self.projetil_velocidade = 600
        self.projetil_raio = 8
        self.projetil_cooldown = 0
        self.iris_raio = LARGURA_TELA
        self.iris_ativa = False
        self.iris_abrindo = False
        self.iris_velocidade = 800
        self.chefe_hp = 450
        self.chefe_hp_max = 450
        self.chefe_regen_timer = 0
        self.player_hp = 5
        self.player_invuln_timer = 0
        self.ataques_chefe = []
        self.chefe_ataque_timer = 0
        self.chefe_pos_y = CHAO_Y - 40
        self.laser_boss = {"ativo": False, "estado": "nenhum", "sx": 0, "sy": 0, "ex": 0, "ey": 0, "timer": 0}
        self.chefe_pos_x = LARGURA_TELA // 2
        self.chefe_vel_x = 300
        self.boss_particles = []
        self.boss_frame = 0
        self.player = Player(CHAO_Y=CHAO_Y)
        self.camera = Camera(LARGURA_TELA, self.largura_mapa_atual)
        self.dialogo_char_idx = 0
        self.dialogo_timer = 0
        self.dialogo_vel = 0.05
        self.chefe_aviso_externo = False
        self.start_time = time.time()

        self.txt_chefe = "Pare de mexer onde não é chamada!"
        self.plataformas_chefe = [
            pygame.Rect(500, CHAO_Y - 100, 150, 20),
            pygame.Rect(750, CHAO_Y - 200, 150, 20),
            pygame.Rect(1000, CHAO_Y - 100, 150, 20),
            pygame.Rect(1250, CHAO_Y - 200, 150, 20),
            pygame.Rect(1550, CHAO_Y - 120, 250, 20) 
        ]
        self.objetos_cenario = [
            [self.img_coqueiro, 250, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 700, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 1100, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 1500, 0, "coqueiro", True, 0, 0, 0],
            [self.img_coqueiro, 1900, 0, "coqueiro", True, 0, 0, 0],
            [self.img_casa1, 2300, 0, "casa1", True, 0, 0, 0],
            [self.img_aldeao1, 2380, 5, "aldeao", True, -80, 0, 0],
            [self.img_casa2, 2650, 15, "casa2", True, 0, 0, 0],
            [self.img_chefe1, 2810, 10, "chefe", True, 0, 0, 0],
            [self.img_casa1, 3100, 0, "casa1", True, 0, 0, 0],
            [self.img_aldeao2, 3180, 5, "aldeao", True, 80, 0, 0],
            [self.img_casa1, 3500, 0, "casa1", True, 0, 0, 0],
            [self.img_aldeao1, 3580, 5, "aldeao", True, 160, 0, 0]
        ]

    def handle_events(self):
        mostrar_prompt = False
        if self.cena_atual == CENA_DESERTO:
            for obj in self.objetos_cenario:
                img, cx, oy, tipo, ativo, offset, golpes, shake = obj
                if ativo and tipo in ("casa1", "casa2"):
                    porta_x = cx + img.get_width() // 2
                    if abs(self.player.rect.centerx - porta_x) < 40:
                        mostrar_prompt, self.tipo_casa_proxima = True, img
                        break
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return 'quit'
            elif e.type == pygame.MOUSEWHEEL:
                self.visual.handle_event(e)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11: pygame.display.toggle_fullscreen()
                elif e.key in (pygame.K_w, pygame.K_UP):
                    self.process_up_key(mostrar_prompt)
                elif e.key == pygame.K_e:
                    self.process_interaction_key()
                elif self.cena_atual == CENA_GAMEOVER:
                    return 'gameover'
                elif self.cena_atual == CENA_VITORIA:
                    return 'win'
        return mostrar_prompt

    def process_up_key(self, mostrar_prompt):
        if mostrar_prompt and self.cena_atual == CENA_DESERTO:
            porta_x = 0
            for obj in self.objetos_cenario:
                if obj[3] in ("casa1", "casa2") and abs(self.player.rect.centerx - (obj[1] + obj[0].get_width() // 2)) < 40:
                    porta_x = obj[1] + obj[0].get_width() // 2
                    break
            if self.tipo_casa_proxima == self.img_casa1:
                self.enter_house(porta_x)
            else:
                if self.vila_reunida:
                    self.enter_house(porta_x)
                else:
                    self.cena_atual, self.player.velX, self.dialogo_char_idx = CENA_DIALOGO, 0, 0
                    self.txt_chefe = "Pare de mexer onde não é chamada!"
                    self.lendo_carta = False
        elif self.cena_atual == CENA_DIALOGO:
            if self.dialogo_char_idx < len(self.txt_chefe):
                self.dialogo_char_idx = len(self.txt_chefe)
            else:
                self.advance_dialogue()
        else:
            self.player.jumpBuffer = 0.15

    def enter_house(self, porta_x):
        self.pos_entrada_x = self.player.pos_x
        self.cena_atual = CENA_CASA
        self.largura_mapa_atual = 800
        self.id_casa_atual = porta_x 
        self.player.pos_x = self.player.rect.x = 80
        self.player.velX = 0
        self.camera.largura_mapa, self.camera.x = self.largura_mapa_atual, 0
        es_casa_chefe = (porta_x == 2650 + self.img_casa2.get_width() // 2)
        if not es_casa_chefe:
            self.npc_casa_x = -120
            self.npc_entrou = False
            self.npc_casa_tipo = "aldeao1" if porta_x in (2300 + self.img_casa1.get_width() // 2, 3500 + self.img_casa1.get_width() // 2) else "aldeao2"

    def advance_dialogue(self):
        if self.lendo_carta:
            self.cena_atual = CENA_CASA
            self.lendo_carta = False
        elif self.boss_final_falando:
            self.cena_atual = CENA_CASA
            self.boss_final_concluido = True
            self.boss_final_falando = False
            self.iris_ativa = True 
        elif hasattr(self, "npc_falando") and self.npc_falando:
            if self.npc_falando_externo:
                self.cena_atual = CENA_DESERTO
                self.npc_falando = None
                self.npc_falando_externo = False
            else:
                self.cena_atual = CENA_CASA
                self.npc_falando = None
        elif self.chefe_aviso_externo:
            self.cena_atual = CENA_DESERTO
            self.chefe_aviso_externo = False
        else:
            self.motivo_gameover = "Talvez não tenha sido uma boa ideia entrar aí!"
            self.cena_atual = CENA_GAMEOVER

    def process_interaction_key(self):
        if self.cena_atual == CENA_CASA:
            es_casa_chefe = (self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2)
            if es_casa_chefe:
                for alav in self.puzzle_alavancas:
                    if abs(self.player.rect.centerx - alav["x"]) < 40 and not self.puzzle_vencido:
                        alav["ativo"] = not alav["ativo"]
                        if alav["id"] not in self.puzzle_sequencia:
                            self.puzzle_sequencia.append(alav["id"])
                            if len(self.puzzle_sequencia) == len(self.puzzle_correto):
                                if self.puzzle_sequencia == self.puzzle_correto:
                                    self.puzzle_vencido = True
                                else:
                                    self.puzzle_sequencia = []
                                    for a in self.puzzle_alavancas: a["ativo"] = False
                        break
            else:
                if hasattr(self, "npc_casa_x") and abs(self.player.rect.centerx - self.npc_casa_x) < 60:
                    self.cena_atual = CENA_DIALOGO
                    self.dialogo_char_idx = 0
                    if self.id_casa_atual == 2300 + self.img_casa1.get_width() // 2:
                        self.txt_chefe = "Ei, você! Viu os coqueiros lá fora? Pegue esse machado, talvez você consiga fazer algo..."
                        self.npc_falando = "aldeao1"
                    elif self.id_casa_atual == 3100 + self.img_casa1.get_width() // 2:
                        self.txt_chefe = "A água mal dá para sobreviver. Ah, essa carta? o chefe derrubou certo dia, mas não sabemos o que significa."
                        self.npc_falando = "aldeao2"
                    elif self.id_casa_atual == 3500 + self.img_casa1.get_width() // 2:
                        self.txt_chefe = "Desconfiamos do chefe. Nunca deixa ninguém entrar naquela casa... O que será que ele esconde lá?"
                        self.npc_falando = "aldeao1"
        elif self.cena_atual == CENA_DESERTO:
            npc_interagido = False
            for i, obj in enumerate(self.objetos_cenario):
                img, cx, oy, tipo, ativo, offset, golpes, shake = obj
                if ativo and tipo in ("aldeao", "chefe"):
                    dist = abs(self.player.rect.centerx - (cx + img.get_width() // 2))
                    if dist < 60:
                        npc_interagido = True
                        self.cena_atual = CENA_DIALOGO
                        self.dialogo_char_idx = 0
                        self.player.velX = 0
                        if tipo == "chefe":
                            self.txt_chefe = "O que foi, forasteira?"
                            self.npc_falando = None
                            self.npc_falando_externo = False
                            self.chefe_aviso_externo = True
                        elif tipo == "aldeao":
                            if cx == 2380 or (abs(cx - 2380) < 200 and i == 6):
                                self.txt_chefe = "Moça, por favor, nos ajude! Antes tínhamos água na cidade, mas do nada ela simplesmente... sumiu. Agora todos passamos sede."
                                self.npc_falando = "aldeao1"
                            elif cx == 3180 or (abs(cx - 3180) < 200 and i == 10):
                                self.txt_chefe = "Desde que o chefe assumiu a liderança, coisas estranhas começaram a acontecer. A água parou de chegar, e ele não deixa ninguém se aproximar da casa dele."
                                self.npc_falando = "aldeao2"
                            elif cx == 3580 or (abs(cx - 3580) < 200 and i == 12):
                                self.txt_chefe = "Ouvi dizer que o chefe esconde algo dentro daquela casa grande. Dizem que ele desviou a água para si mesmo! Alguém precisa investigar."
                                self.npc_falando = "aldeao1"
                            else:
                                self.txt_chefe = "Estamos sofrendo com a falta de água..."
                                self.npc_falando = "aldeao1"
                            self.npc_falando_externo = True
                            self.chefe_aviso_externo = False
                        break
            if not npc_interagido:
                for obj in self.objetos_cenario:
                    img, cx, oy, tipo, ativo, offset, golpes, shake = obj
                    if ativo and tipo == "coqueiro":
                        dist = abs(self.player.rect.centerx - (cx + img.get_width() // 2))
                        if dist < 60:
                            if "machado" in self.inventario:
                                obj[4] = False 
                                self.coqueiros_cortados += 1
                                self.pos_ultimo_coqueiro = cx + img.get_width() // 2
                                if self.coqueiros_cortados == 5:
                                    self.motivo_gameover = "Você desmatou todo o oásis! A vila faliu."
                                    self.cena_atual = CENA_GAMEOVER
                                elif self.coqueiros_cortados >= 3:
                                    self.vila_reunida = True
                            else:
                                obj[6] += 1
                                obj[7] = 0.3
                                if obj[6] >= 3:
                                    self.cocos_caindo.append({
                                        "x": cx + img.get_width() // 2 - self.img_coco.get_width() // 2,
                                        "y": CHAO_Y - img.get_height() + 60,
                                        "velY": 0
                                    })
                                    obj[6] = 0
                            break

    def fire_projectile(self):
        if self.cena_atual not in (CENA_DESERTO, CENA_CASA, CENA_BATALHA_FINAL) or getattr(self.player, 'shoot_cd_timer', 0) > 0:
            return
        teclas = pygame.key.get_pressed()
        dx, dy = 0, 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]: dy -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]: dy += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]: dx -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dx += 1
        if dx == 0 and dy == 0:
            dx = 1 if self.player.direcao == "direita" else -1
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1
        dx, dy = dx / dist, dy / dist
        px = self.player.rect.centerx + dx * 20
        py = self.player.rect.centery + dy * 20
        self.projeteis.append(PlayerBullet(px, py, dx, dy))
        self.player.shoot_cd_timer = getattr(self.player, 'SHOOT_CD', 10)
        self.player.is_shooting = True
        self.player.shoot_timer = 0.2
        self.player.shoot_anim_name = random.choice(["shoot1", "shoot2"])

    def update(self, dt):
        self.mouse_pos = pygame.mouse.get_pos()
        if self.cena_atual in (CENA_DESERTO, CENA_CASA, CENA_BATALHA_FINAL):
            plats = self.plataformas_chefe if (self.cena_atual == CENA_CASA and self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2) else None
            chao_at = True
            if plats and 400 < self.player.pos_x < 1800: chao_at = False 
            if plats: 
                self.largura_mapa_atual = 3500
                self.camera.largura_mapa = self.largura_mapa_atual
            teclas = pygame.key.get_pressed()
            mov = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
            self.player.update(dt, teclas, mov, CHAO_Y, self.largura_mapa_atual, plats, chao_at)
            self.camera.update(dt, self.player, mov)
            for coco in self.cocos_caindo[:]:
                coco["velY"] += 1600 * dt
                coco["y"] += coco["velY"] * dt
                rect_coco = pygame.Rect(coco["x"], coco["y"], self.img_coco.get_width(), self.img_coco.get_height())
                if rect_coco.colliderect(self.player.rect):
                    self.motivo_gameover = "Você levou uma cocada na cabeça!"
                    self.cena_atual = CENA_GAMEOVER
                    break
                if coco["y"] > CHAO_Y + 50:
                    self.cocos_caindo.remove(coco)
            if self.player.rect.y > ALTURA_TELA:
                self.motivo_gameover = "Você caiu no abismo sem fim..."
                self.cena_atual = CENA_GAMEOVER
            if teclas[pygame.K_f]:
                self.fire_projectile()
            if getattr(self.player, 'shoot_cd_timer', 0) > 0:
                self.player.shoot_cd_timer -= 1
                
            for proj in self.projeteis[:]:
                proj.update(max_x=self.largura_mapa_atual)
                if not proj.alive:
                    self.projeteis.remove(proj)
                    continue
                proj_rect = proj.rect()
                if self.cena_atual == CENA_DESERTO:
                    for obj in self.objetos_cenario:
                        img, cx, oy, tipo, ativo, offset, golpes, shake = obj
                        if ativo and tipo in ("aldeao", "chefe"):
                            npc_rect = pygame.Rect(cx, CHAO_Y - img.get_height() + oy, img.get_width(), img.get_height())
                            if proj_rect.colliderect(npc_rect):
                                self.motivo_gameover = "Você atacou um inocente! Que crueldade."
                                self.cena_atual = CENA_GAMEOVER
                                self.projeteis.clear()
                                break
                elif self.cena_atual == CENA_CASA:
                    es_casa_chefe = (self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2)
                    if es_casa_chefe and self.puzzle_vencido and not self.boss_final_concluido:
                        boss_rect = pygame.Rect(self.boss_final_x, CHAO_Y + 10 - self.img_chefe2.get_height(), self.img_chefe2.get_width(), self.img_chefe2.get_height())
                        if proj_rect.colliderect(boss_rect):
                            self.projeteis.remove(proj)
                            continue
                elif self.cena_atual == CENA_BATALHA_FINAL:
                    boss_rect = pygame.Rect(self.chefe_pos_x - self.img_chefe2.get_width()//2, self.chefe_pos_y - self.img_chefe2.get_height()//2, self.img_chefe2.get_width(), self.img_chefe2.get_height())
                    if proj_rect.colliderect(boss_rect):
                        self.chefe_hp -= 15
                        spawn_hit_particles(self.boss_particles, proj.x, proj.y, (0, 180, 255), 10)
                        self.projeteis.remove(proj)
                        if self.chefe_hp <= 0:
                            # Explosão de partículas na morte
                            for _ in range(40):
                                self.boss_particles.append(Particle(
                                    self.chefe_pos_x, self.chefe_pos_y,
                                    random.choice([(0, 150, 255), (100, 200, 255), (200, 230, 255)]),
                                    random.uniform(-5, 5), random.uniform(-6, 2),
                                    random.randint(30, 60), random.randint(3, 6), 0.12))
                            self.motivo_gameover = "VITÓRIA! Você derrotou o chefe da água e salvou o oásis!"
                            self.cena_atual = CENA_VITORIA
                        continue
            if self.cena_atual == CENA_BATALHA_FINAL:
                self.chefe_regen_timer += dt
                if self.chefe_regen_timer >= 1.0:
                    self.chefe_hp = min(self.chefe_hp_max, self.chefe_hp + 1)
                    self.chefe_regen_timer -= 1.0
                if self.laser_boss["ativo"]:
                    self.laser_boss["timer"] += dt
                    if self.laser_boss["estado"] == "aviso":
                        self.chefe_vel_x = 0
                        if self.laser_boss["timer"] > 1.0:
                            self.laser_boss["estado"] = "tiro"
                            self.laser_boss["timer"] = 0
                    elif self.laser_boss["estado"] == "tiro":
                        sx, sy = self.laser_boss["sx"], self.laser_boss["sy"]
                        ex, ey = self.laser_boss["ex"], self.laser_boss["ey"]
                        px, py = self.player.rect.centerx, self.player.rect.centery
                        v_x, v_y = px - sx, py - sy
                        d_x, d_y = ex - sx, ey - sy
                        dot = v_x * d_x + v_y * d_y
                        dist_line = 999
                        if dot >= 0:
                            num = abs((ex - sx) * (sy - py) - (sx - px) * (ey - sy))
                            den = math.hypot(ex - sx, ey - sy)
                            dist_line = num / den if den != 0 else 0
                        if self.player_invuln_timer <= 0 and dist_line < 40:
                            self.player_hp -= 1
                            self.player_invuln_timer = 1.0
                            spawn_hit_particles(self.boss_particles, self.player.rect.centerx, self.player.rect.centery, (255, 100, 100), 12)
                            if self.player_hp <= 0:
                                self.motivo_gameover = "Você foi desintegrado pelo ultra-jato!"
                                self.cena_atual = CENA_GAMEOVER
                        if self.laser_boss["timer"] > 0.5:
                            self.laser_boss["ativo"] = False
                            self.laser_boss["estado"] = "nenhum"
                            self.chefe_vel_x = 300 if random.random() > 0.5 else -300
                            self.chefe_ataque_timer = 1.5
                else:
                    self.chefe_pos_x += self.chefe_vel_x * dt
                    if self.chefe_pos_x < 100 or self.chefe_pos_x > LARGURA_TELA - 100:
                        self.chefe_vel_x *= -1
                        self.chefe_pos_x += self.chefe_vel_x * dt
                    self.chefe_ataque_timer -= dt
                    if self.chefe_ataque_timer <= 0:
                        if random.random() > 0.5:
                            self.laser_boss["ativo"] = True
                            self.laser_boss["estado"] = "aviso"
                            self.laser_boss["timer"] = 0
                            dx = self.player.rect.centerx - self.chefe_pos_x
                            dy = self.player.rect.centery - self.chefe_pos_y
                            dist = math.hypot(dx, dy)
                            if dist == 0: dist = 1
                            dx, dy = dx / dist, dy / dist
                            self.laser_boss["sx"] = self.chefe_pos_x
                            self.laser_boss["sy"] = self.chefe_pos_y
                            self.laser_boss["ex"] = self.chefe_pos_x + dx * 3000
                            self.laser_boss["ey"] = self.chefe_pos_y + dy * 3000
                        else:
                            dir_x = 1 if self.player.rect.centerx > self.chefe_pos_x else -1
                            self.ataques_chefe.append({"x": float(self.chefe_pos_x), "y": float(self.chefe_pos_y - 10), "dir": dir_x, "vel": 450})
                            self.chefe_ataque_timer = 1.0
                for atk in self.ataques_chefe[:]:
                    atk["x"] += atk["vel"] * atk["dir"] * dt
                    if atk["x"] < -100 or atk["x"] > LARGURA_TELA + 100:
                        self.ataques_chefe.remove(atk)
                        continue
                    rect_atk = pygame.Rect(atk["x"] - 15, atk["y"] - 15, 30, 30)
                    if self.player_invuln_timer <= 0 and rect_atk.colliderect(self.player.rect):
                        self.player_hp -= 1
                        self.player_invuln_timer = 1.0
                        spawn_hit_particles(self.boss_particles, atk["x"], atk["y"], (0, 180, 255), 10)
                        self.ataques_chefe.remove(atk)
                        if self.player_hp <= 0:
                            self.motivo_gameover = "Uma bolha d'água te derrubou!"
                            self.cena_atual = CENA_GAMEOVER
                            break
                boss_rect = pygame.Rect(self.chefe_pos_x - self.img_chefe2.get_width()//2, self.chefe_pos_y - self.img_chefe2.get_height()//2, self.img_chefe2.get_width(), self.img_chefe2.get_height())
                if self.player_invuln_timer <= 0 and self.player.rect.colliderect(boss_rect):
                    self.player_hp -= 1
                    self.player_invuln_timer = 1.0
                    spawn_hit_particles(self.boss_particles, self.player.rect.centerx, self.player.rect.centery, (255, 120, 80), 12)
                    if self.player_hp <= 0:
                        self.motivo_gameover = "O chefe te afogou num abraço gelado!"
                        self.cena_atual = CENA_GAMEOVER
                if self.player_invuln_timer > 0:
                    self.player_invuln_timer -= dt
                # Partículas ambientais do chefe (água girando ao redor)
                self.boss_frame += 1
                if self.boss_frame % 4 == 0:
                    bx = self.chefe_pos_x + random.randint(-25, 25)
                    by = self.chefe_pos_y + random.randint(-30, 20)
                    c = random.choice([(0, 120, 220), (40, 160, 255), (100, 200, 255), (180, 220, 255)])
                    self.boss_particles.append(Particle(bx, by, c, random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.3), 22, random.randint(2, 3), 0.02))
                # Atualizar partículas
                self.boss_particles = [p for p in self.boss_particles if p.update()]
            if self.puzzle_vencido and not self.boss_final_concluido:
                if self.boss_final_x > self.player.pos_x + 150:
                    self.boss_final_x -= 150 * dt
                elif not self.boss_final_falando:
                    self.boss_final_falando = True
                    self.cena_atual = CENA_DIALOGO
                    self.txt_chefe = "Você mexeu onde não devia, garota!"
                    self.dialogo_char_idx = 0
                self.lendo_carta = False
        elif self.cena_atual == CENA_DIALOGO:
            self.dialogo_timer += dt
            if self.dialogo_timer >= self.dialogo_vel and self.dialogo_char_idx < len(self.txt_chefe):
                self.dialogo_char_idx += 1
                self.dialogo_timer = 0
        if self.vila_reunida and self.cena_atual == CENA_DESERTO:
            for obj in self.objetos_cenario:
                if obj[3] in ("aldeao", "chefe"):
                    alvo = self.pos_ultimo_coqueiro + obj[5]
                    if abs(obj[1] - alvo) > 5:
                        obj[1] += 120 * dt * (1 if obj[1] < alvo else -1)
        for obj in self.objetos_cenario:
            if obj[7] > 0: obj[7] = max(0, obj[7] - dt)
        if self.cena_atual == CENA_CASA:
            if self.id_casa_atual == 2300 + self.img_casa1.get_width() // 2 and self.machado_disponivel:
                rect_axe = pygame.Rect(400, CHAO_Y - 40, 40, 40)
                if self.player.rect.colliderect(rect_axe):
                    self.inventario.append("machado")
                    self.machado_disponivel = False
            if self.id_casa_atual == 3100 + self.img_casa1.get_width() // 2 and self.carta_disponivel:
                rect_carta = pygame.Rect(400, CHAO_Y - 30, 40, 40)
                if self.player.rect.colliderect(rect_carta):
                    self.txt_chefe = "A carta diz... 4, 3, 5, 1, 2?! Manter pelo menos dois coqueiros sempre... Para quem são essas instruções?"
                    self.dialogo_char_idx = 0
                    self.cena_atual = CENA_DIALOGO
                    self.lendo_carta = True
                    self.carta_disponivel = False
            es_casa_chefe = (self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2)
            if not es_casa_chefe and hasattr(self, "npc_casa_x"):
                pode_entrar = False
                if self.id_casa_atual == 2300 + self.img_casa1.get_width() // 2:
                    pode_entrar = not self.machado_disponivel
                elif self.id_casa_atual == 3100 + self.img_casa1.get_width() // 2:
                    pode_entrar = not self.carta_disponivel
                else:
                    pode_entrar = True
                if pode_entrar and not getattr(self, "npc_entrou", True) and self.cena_atual == CENA_CASA:
                    if self.npc_casa_x < 30:
                        self.npc_casa_x += 100 * dt
                    else:
                        self.npc_entrou = True
                        self.cena_atual = CENA_DIALOGO
                        self.dialogo_char_idx = 0
                        self.npc_falando = self.npc_casa_tipo
                        if self.id_casa_atual == 2300 + self.img_casa1.get_width() // 2:
                            self.txt_chefe = "Os coqueiros? Ele plantou, mas não há água! Pegue esse machado, talvez você consiga fazer algo..."
                        elif self.id_casa_atual == 3100 + self.img_casa1.get_width() // 2:
                            self.txt_chefe = "A água mal dá para sobreviver. Ah, pegue essa carta, o chefe derrubou certo dia, mas não sabemos o que significa."
                        elif self.id_casa_atual == 3500 + self.img_casa1.get_width() // 2:
                            self.txt_chefe = "Desconfiamos dele. Nunca deixa ninguém entrar naquela casa... O que será que ele esconde lá?"
            if self.player.pos_x <= 0:
                self.exit_house()

    def exit_house(self):
        self.cena_atual, self.largura_mapa_atual = CENA_DESERTO, LARGURA_MAPA
        self.player.pos_x, self.player.rect.x = self.pos_entrada_x, int(self.pos_entrada_x)
        self.camera.largura_mapa = self.largura_mapa_atual
        self.camera.x = max(0, min(self.player.rect.centerx - self.camera.pos_tela, self.camera.largura_mapa - self.camera.largura_tela))

    def draw(self, mostrar_prompt):
        self.tela_jogo.fill(CORES["fundo"])
        npc_falando_v = getattr(self, "npc_falando", None)
        npc_externo = getattr(self, "npc_falando_externo", False)
        chefe_ext = getattr(self, "chefe_aviso_externo", False)
        dialogo_interno = (npc_falando_v and not npc_externo)
        dialogo_externo = (npc_falando_v and npc_externo) or chefe_ext
        em_casa = (self.cena_atual == CENA_CASA) or (self.cena_atual == CENA_DIALOGO and (self.boss_final_falando or self.lendo_carta or dialogo_interno))
        no_deserto = (self.cena_atual == CENA_DESERTO) or (self.cena_atual == CENA_DIALOGO and not self.boss_final_falando and not self.lendo_carta and not npc_falando_v and not chefe_ext) or (self.cena_atual == CENA_DIALOGO and dialogo_externo)
        na_batalha = (self.cena_atual == CENA_BATALHA_FINAL)
        if no_deserto:
            self.draw_desert()
        elif em_casa:
            self.draw_house()
        elif na_batalha:
            self.draw_batalha_final()
        self.draw_player()
        if em_casa:
            cam_x = self.camera.x - self.camera.offset_x
            pygame.draw.rect(self.tela_jogo, (0, 0, 0), (-2000 - cam_x, 0, 2000, ALTURA_TELA))
            pygame.draw.rect(self.tela_jogo, (0, 0, 0), (self.largura_mapa_atual - cam_x, 0, 2000, ALTURA_TELA))
        if no_deserto:
            self.draw_foreground_cacti()
        self.visual.render(self.tela_jogo, self.tela, self.mouse_pos)
        if mostrar_prompt: self.render_prompt()
        if self.cena_atual == CENA_DIALOGO: self.render_dialogue()
        elif self.cena_atual == CENA_GAMEOVER: self.render_gameover()
        elif self.cena_atual == CENA_VITORIA: self.render_vitoria()
        if self.cena_atual not in (CENA_GAMEOVER, CENA_VITORIA):
            from utils import draw_health_bar
            draw_health_bar(self.tela, self.player_hp, 5, 15, 15)

            elapsed = time.time() - self.start_time

            mins = int(elapsed) // 60
            secs = int(elapsed) % 60

            timer_txt = self.fonts["ui"].render(
                f"TEMPO {mins:02d}:{secs:02d}",
                False,
                (255, 170, 0)
            )

            self.tela.blit(timer_txt, (LARGURA_TELA - 190, 15))

            self.render_inventory()
        if self.iris_ativa or self.iris_abrindo: self.render_iris()
        pygame.display.flip()

    def draw_desert(self):
        for img, spd in [(self.bg_mountains, 0.2), (self.bg_dunes, 0.5), (self.bg_ground, 0.8)]:
            w, shift = img.get_width(), ((self.camera.x - self.camera.offset_x) * spd) % img.get_width()
            for x in range(int(-shift), LARGURA_TELA, w): self.tela_jogo.blit(img, (x, 0))
        for i in range(0, self.largura_mapa_atual, self.w_chao):
            if -self.w_chao < i - (self.camera.x - self.camera.offset_x) < LARGURA_TELA:
                self.tela_jogo.blit(self.img_chao, (i - (self.camera.x - self.camera.offset_x), CHAO_Y - 60))
        for obj in self.objetos_cenario:
            img, cx, oy, tipo, ativo, offset, golpes, shake = obj
            if ativo and -img.get_width() < cx - (self.camera.x - self.camera.offset_x) < LARGURA_TELA:
                img_draw = img
                if tipo in ("aldeao", "chefe"):
                    alvo_olhar = self.pos_ultimo_coqueiro if self.vila_reunida else self.player.rect.centerx
                    flip = alvo_olhar < cx + img.get_width() // 2
                    img_draw = pygame.transform.flip(img, flip, False)
                dx = random.randint(-4, 4) if shake > 0 else 0
                self.tela_jogo.blit(img_draw, (cx - (self.camera.x - self.camera.offset_x) + dx, CHAO_Y - img_draw.get_height() + oy))
                if tipo in ("casa1", "casa2") and abs(self.player.rect.centerx - (cx + img.get_width() // 2)) < 40:
                    draw_arrow_up(self.tela_jogo, (cx + img.get_width() // 2) - (self.camera.x - self.camera.offset_x), CHAO_Y - 80)
                if tipo == "coqueiro" and abs(self.player.rect.centerx - (cx + img.get_width() // 2)) < 60:
                    draw_key_hint(self.tela_jogo, (cx + img.get_width() // 2) - (self.camera.x - self.camera.offset_x), CHAO_Y - img.get_height() - 20, "E")
                if tipo in ("aldeao", "chefe") and abs(self.player.rect.centerx - (cx + img.get_width() // 2)) < 60:
                    draw_key_hint(self.tela_jogo, (cx + img.get_width() // 2) - (self.camera.x - self.camera.offset_x), CHAO_Y - img.get_height() + oy - 20, "E")
        for coco in self.cocos_caindo:
            self.tela_jogo.blit(self.img_coco, (coco["x"] - (self.camera.x - self.camera.offset_x), coco["y"]))
        cam = self.camera.x - self.camera.offset_x
        for proj in self.projeteis:
            proj.draw(self.tela_jogo, cam, 0)

    def draw_house(self):
        es_casa_chefe = (self.id_casa_atual == 2650 + self.img_casa2.get_width() // 2)
        img_chao_render = self.img_chao_chefe if es_casa_chefe else self.img_chao_casa
        w_chao_render = self.w_chao_chefe if es_casa_chefe else self.w_chao_casa
        for i in range(0, self.largura_mapa_atual, w_chao_render):
            desenhar_chao = False
            if not es_casa_chefe: desenhar_chao = True
            elif i < 400 or i > 1800: desenhar_chao = True
            if desenhar_chao: self.tela_jogo.blit(img_chao_render, (i - (self.camera.x - self.camera.offset_x), CHAO_Y - 60))
        if es_casa_chefe:
            for p in self.plataformas_chefe:
                for px in range(p.x, p.x + p.width, w_chao_render):
                    self.tela_jogo.blit(self.img_chao_chefe, (px - (self.camera.x - self.camera.offset_x), p.y), (0, 0, min(self.w_chao_chefe, p.x + p.width - px), p.height))
                pygame.draw.rect(self.tela_jogo, (200, 200, 200), (p.x - (self.camera.x - self.camera.offset_x), p.y, p.width, p.height), 2)
            for alav in self.puzzle_alavancas:
                img_alav = self.img_alavanca
                if alav["ativo"]: img_alav = pygame.transform.flip(self.img_alavanca, True, False)
                self.tela_jogo.blit(img_alav, (alav["x"] - (self.camera.x - self.camera.offset_x), CHAO_Y + 10 - img_alav.get_height()))
                if abs(self.player.rect.centerx - alav["x"]) < 40 and not self.puzzle_vencido:
                    draw_key_hint(self.tela_jogo, alav["x"] - (self.camera.x - self.camera.offset_x), CHAO_Y - 80, "E")
            if self.puzzle_vencido:
                img_f = pygame.transform.flip(self.img_chefe2, True, False)
                self.tela_jogo.blit(img_f, (self.boss_final_x - (self.camera.x - self.camera.offset_x), CHAO_Y + 10 - self.img_chefe2.get_height()))
        if self.id_casa_atual == 2300 + self.img_casa1.get_width() // 2 and self.machado_disponivel:
            self.tela_jogo.blit(self.img_axe, (400 - (self.camera.x - self.camera.offset_x), CHAO_Y - 40))
        if self.id_casa_atual == 3100 + self.img_casa1.get_width() // 2 and self.carta_disponivel:
            self.tela_jogo.blit(self.img_letter, (400 - (self.camera.x - self.camera.offset_x), CHAO_Y - 30))
        if not es_casa_chefe and hasattr(self, "npc_casa_x"):
            img_n = self.img_aldeao1 if self.npc_casa_tipo == "aldeao1" else self.img_aldeao2
            self.tela_jogo.blit(img_n, (self.npc_casa_x - (self.camera.x - self.camera.offset_x), CHAO_Y + 10 - img_n.get_height()))
            if getattr(self, "npc_entrou", False) and abs(self.player.rect.centerx - self.npc_casa_x) < 60:
                draw_key_hint(self.tela_jogo, self.npc_casa_x - (self.camera.x - self.camera.offset_x), CHAO_Y - 80, "E")
        cam = self.camera.x - self.camera.offset_x
        for proj in self.projeteis:
            proj.draw(self.tela_jogo, cam, 0)

    def draw_batalha_final(self):
        self.tela_jogo.fill((10, 30, 80))
        # Efeito de ondulação no fundo
        t = pygame.time.get_ticks() / 1000.0
        for wy in range(0, CHAO_Y, 6):
            alpha = int(8 + 4 * math.sin(t * 2 + wy * 0.05))
            wave_surf = pygame.Surface((LARGURA_TELA, 3), pygame.SRCALPHA)
            wave_surf.fill((40, 80, 180, alpha))
            self.tela_jogo.blit(wave_surf, (0, wy))
        pygame.draw.rect(self.tela_jogo, (20, 50, 100), (0, CHAO_Y, LARGURA_TELA, ALTURA_TELA - CHAO_Y))
        cam = self.camera.x - self.camera.offset_x
        # Bolhas d'água com glow
        for atk in self.ataques_chefe:
            sx, sy = int(atk["x"] - cam), int(atk["y"])
            # Glow externo
            gs = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(gs, (0, 100, 255, 40), (20, 20), 20)
            self.tela_jogo.blit(gs, (sx - 20, sy - 20))
            # Bolha principal
            pygame.draw.circle(self.tela_jogo, (0, 150, 255), (sx, sy), 15)
            pygame.draw.circle(self.tela_jogo, (100, 200, 255), (sx, sy), 10)
            pygame.draw.circle(self.tela_jogo, (200, 235, 255), (sx - 4, sy - 4), 4)
        if self.laser_boss["ativo"]:
            sx, sy = int(self.laser_boss["sx"] - cam), int(self.laser_boss["sy"])
            ex, ey = int(self.laser_boss["ex"] - cam), int(self.laser_boss["ey"])
            if self.laser_boss["estado"] == "aviso":
                r_val = int(abs(pygame.time.get_ticks() % 500 - 250) / 250.0 * 155 + 100)
                pygame.draw.line(self.tela_jogo, (r_val, 0, 0), (sx, sy), (ex, ey), 2)
            elif self.laser_boss["estado"] == "tiro":
                # Laser com brilho multicamada
                pygame.draw.line(self.tela_jogo, (0, 60, 180), (sx, sy), (ex, ey), 50)
                pygame.draw.line(self.tela_jogo, (0, 100, 255), (sx, sy), (ex, ey), 30)
                pygame.draw.line(self.tela_jogo, (100, 200, 255), (sx, sy), (ex, ey), 14)
                pygame.draw.line(self.tela_jogo, (220, 240, 255), (sx, sy), (ex, ey), 6)
                pygame.draw.line(self.tela_jogo, (255, 255, 255), (sx, sy), (ex, ey), 2)
        # Boss aura glow
        boss_sx = int(self.chefe_pos_x - cam)
        boss_sy = int(self.chefe_pos_y)
        aura = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = int(18 + 6 * math.sin(t * 4))
        pygame.draw.ellipse(aura, (0, 100, 255, pulse), aura.get_rect())
        self.tela_jogo.blit(aura, (boss_sx - 60, boss_sy - self.img_chefe2.get_height()//2 - 20))
        # Boss sprite
        img_c = self.img_chefe2
        if self.chefe_vel_x < 0: img_c = pygame.transform.flip(img_c, True, False)
        self.tela_jogo.blit(img_c, (self.chefe_pos_x - cam - img_c.get_width()//2, self.chefe_pos_y - img_c.get_height()//2))
        # Partículas
        for p in self.boss_particles:
            p.draw(self.tela_jogo, cam, 0)
        # Projéteis do jogador
        for proj in self.projeteis:
            proj.draw(self.tela_jogo, cam, 0)
        # HUD — Barra de HP do chefe (estilo premium)
        bar_w, bar_x, bar_y = 600, LARGURA_TELA // 2 - 300, 18
        # Fundo com borda arredondada
        pygame.draw.rect(self.tela_jogo, (20, 10, 40), (bar_x - 2, bar_y - 2, bar_w + 4, 24), border_radius=6)
        pct = max(0, self.chefe_hp / self.chefe_hp_max)
        # Gradiente visual na barra
        bar_fill = int(bar_w * pct)
        if bar_fill > 0:
            for bx_i in range(bar_fill):
                ratio = bx_i / max(1, bar_fill)
                r = int(0 + 50 * ratio)
                g = int(120 + 80 * ratio)
                b_c = int(200 + 55 * ratio)
                pygame.draw.line(self.tela_jogo, (r, g, b_c), (bar_x + bx_i, bar_y), (bar_x + bx_i, bar_y + 19))
        pygame.draw.rect(self.tela_jogo, (100, 180, 255), (bar_x - 2, bar_y - 2, bar_w + 4, 24), 2, border_radius=6)
        txt_boss = self.fonts["ui"].render("CHEFE DA ÁGUA", True, (255, 255, 255))
        self.tela_jogo.blit(txt_boss, (LARGURA_TELA//2 - txt_boss.get_width()//2, bar_y - 24))

    def draw_player(self):
        if self.player.current_animation:
            sprite = self.player.current_animation[self.player.frame_index]
            if self.player.direcao == "esquerda": sprite = pygame.transform.flip(sprite, True, False)
            offsetX = (sprite.get_width() - self.player.rect.width) // 2
            self.tela_jogo.blit(sprite, (self.player.rect.x - (self.camera.x - self.camera.offset_x) - offsetX, self.player.rect.y))
        else:
            pygame.draw.rect(self.tela_jogo, (255,255,255), (self.player.rect.x - (self.camera.x - self.camera.offset_x), self.player.rect.y, *self.player.rect.size))

    def draw_foreground_cacti(self):
        rect_j = pygame.Rect(self.player.rect.x - (self.camera.x - self.camera.offset_x), self.player.rect.y, *self.player.rect.size)
        for cx, cy, idx in self.cactos_fg:
            img_v = self.variacoes_cacto[idx]
            x = (cx - (self.camera.x - self.camera.offset_x) * 1.8) % 3200 - 600
            img_v.set_alpha(150 if pygame.Rect(x, cy, *img_v.get_size()).colliderect(rect_j) else 255)
            self.tela_jogo.blit(img_v, (x, cy))

    def render_prompt(self):
        txt = self.fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["texto"])
        smd = self.fonts["ui"].render("PRESSIONE 'W' OU '↑' PARA ENTRAR", False, CORES["fundo"])
        px, py = LARGURA_TELA // 2 - txt.get_width() // 2, ALTURA_TELA - 50
        self.tela.blit(smd, (px + 2, py + 2)); self.tela.blit(txt, (px, py))

    def render_dialogue(self):
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)); self.tela.blit(overlay, (0, 0))
        if self.lendo_carta:
            self.tela.blit(self.img_hope, (-80, ALTURA_TELA - int(self.img_hope.get_height() * 0.66)))
            self._render_carta_texto(self.txt_chefe[:self.dialogo_char_idx], LARGURA_TELA // 2 - 100, ALTURA_TELA // 2, LARGURA_TELA // 2 + 50)
        elif hasattr(self, "npc_falando") and self.npc_falando in ("aldeao1", "aldeao2"):
            img_npc = self.img_aldeao_dialogo1 if self.npc_falando == "aldeao1" else self.img_aldeao_dialogo2
            self.tela.blit(img_npc, (LARGURA_TELA - img_npc.get_width() + 50, ALTURA_TELA - int(img_npc.get_height() * 0.66)))
            pygame.draw.rect(self.tela, (0, 0, 0), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
            pygame.draw.rect(self.tela, (255, 255, 255), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
            self.tela.blit(self.fonts["ui"].render("ALDEÃO:", False, (0, 200, 0)), (70, ALTURA_TELA - 140))
            self._render_dialogo_texto(self.txt_chefe[:self.dialogo_char_idx], 70, ALTURA_TELA - 110, LARGURA_TELA - 180)
        elif getattr(self, "chefe_aviso_externo", False):
            self.tela.blit(self.img_chefe1_dialogo, (LARGURA_TELA - self.img_chefe1_dialogo.get_width() + 50, ALTURA_TELA - int(self.img_chefe1_dialogo.get_height() * 0.66)))
            pygame.draw.rect(self.tela, (0, 0, 0), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
            pygame.draw.rect(self.tela, (255, 255, 255), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
            self.tela.blit(self.fonts["ui"].render("CHEFE:", False, (200, 0, 0)), (70, ALTURA_TELA - 140))
            self._render_dialogo_texto(self.txt_chefe[:self.dialogo_char_idx], 70, ALTURA_TELA - 110, LARGURA_TELA - 180)
        else:
            self.tela.blit(self.img_chefe_dialogo, (LARGURA_TELA - self.img_chefe_dialogo.get_width() + 50, ALTURA_TELA - int(self.img_chefe_dialogo.get_height() * 0.66)))
            pygame.draw.rect(self.tela, (0, 0, 0), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100))
            pygame.draw.rect(self.tela, (255, 255, 255), (50, ALTURA_TELA - 150, LARGURA_TELA - 100, 100), 2)
            self.tela.blit(self.fonts["ui"].render("CHEFE:", False, (200, 0, 0)), (70, ALTURA_TELA - 140))
            self._render_dialogo_texto(self.txt_chefe[:self.dialogo_char_idx], 70, ALTURA_TELA - 110, LARGURA_TELA - 180)
        if self.dialogo_char_idx >= len(self.txt_chefe):
            inst = self.fonts["instrucao"].render("Pressione qualquer tecla para continuar...", False, (100, 100, 100))
            self.tela.blit(inst, (LARGURA_TELA - inst.get_width() - 70, ALTURA_TELA - 70))

    def render_gameover(self):
        self.tela.fill(CORES["fundo"])
        txt_go = self.fonts["grande"].render("GAME OVER", False, CORES["go"])
        self.tela.blit(txt_go, (LARGURA_TELA // 2 - txt_go.get_width() // 2, ALTURA_TELA // 2 - 120))
        if self.motivo_gameover:
            txt_motivo = self.fonts["ui"].render(self.motivo_gameover, False, (255, 200, 50))
            self.tela.blit(txt_motivo, (LARGURA_TELA // 2 - txt_motivo.get_width() // 2, ALTURA_TELA // 2 - 30))
        txt_r = self.fonts["ui"].render("Pressione qualquer tecla para reiniciar", False, CORES["texto"])
        self.tela.blit(txt_r, (LARGURA_TELA // 2 - txt_r.get_width() // 2, ALTURA_TELA // 2 + 50))

    def render_vitoria(self):
        self.tela.fill((10, 50, 20))
        txt_v = self.fonts["grande"].render("VITÓRIA!", False, (100, 255, 100))
        self.tela.blit(txt_v, (LARGURA_TELA // 2 - txt_v.get_width() // 2, ALTURA_TELA // 2 - 120))
        if self.motivo_gameover:
            txt_motivo = self.fonts["ui"].render(self.motivo_gameover, False, (255, 255, 255))
            self.tela.blit(txt_motivo, (LARGURA_TELA // 2 - txt_motivo.get_width() // 2, ALTURA_TELA // 2 - 30))
        txt_r = self.fonts["ui"].render("Pressione qualquer tecla para fechar!", False, CORES["texto"])
        self.tela.blit(txt_r, (LARGURA_TELA // 2 - txt_r.get_width() // 2, ALTURA_TELA // 2 + 50))

    def render_inventory(self):
        # Slot do machado posicionado abaixo da barra de HP (y=50 + 16 + gap)
        slot_x, slot_y = 15, 75
        overlay_inv = pygame.Surface((60, 60), pygame.SRCALPHA); overlay_inv.fill((0, 0, 0, 120)) 
        self.tela.blit(overlay_inv, (slot_x, slot_y))
        pygame.draw.rect(self.tela, (255, 255, 255, 180), (slot_x, slot_y, 60, 60), 2) 
        if "machado" in self.inventario:
            ax, ay = slot_x + (60 - self.img_axe.get_width()) // 2, slot_y + (60 - self.img_axe.get_height()) // 2
            self.tela.blit(self.img_axe, (ax, ay))

    def render_iris(self):
        dt = self.clock.get_time() / 1000.0
        if self.iris_ativa:
            self.iris_raio = max(0, self.iris_raio - self.iris_velocidade * dt)
            if self.iris_raio <= 0 and self.cena_atual == CENA_CASA:
                self.cena_atual, self.largura_mapa_atual, self.iris_abrindo, self.iris_ativa = CENA_BATALHA_FINAL, LARGURA_TELA, True, False
                self.player.pos_x = self.player.rect.x = 100
                self.camera.largura_mapa = LARGURA_TELA
                self.projeteis.clear()
        elif self.iris_abrindo:
            self.iris_raio += self.iris_velocidade * dt
            if self.iris_raio >= LARGURA_TELA: self.iris_abrindo = False
        px, py = self.player.rect.centerx - (self.camera.x - self.camera.offset_x), self.player.rect.centery
        s_iris = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA); s_iris.fill((0, 0, 0, 255))
        pygame.draw.circle(s_iris, (0, 0, 0, 0), (int(px), int(py)), int(self.iris_raio))
        self.tela.blit(s_iris, (0, 0))

    def _render_dialogo_texto(self, texto, x, y, max_width):
        palavras, linhas, linha_atual = texto.split(' '), [], ""
        for palavra in palavras:
            teste = linha_atual + (" " if linha_atual else "") + palavra
            if self.fonts["dialogo"].size(teste)[0] <= max_width: linha_atual = teste
            else:
                if linha_atual: linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual: linhas.append(linha_atual)
        for i, linha in enumerate(linhas[:3]): self.tela.blit(self.fonts["dialogo"].render(linha, False, (180, 180, 180)), (x, y + i * 22))

    def _render_carta_texto(self, texto, x, y, max_width):
        palavras, linhas, linha_atual = texto.split(' '), [], ""
        for palavra in palavras:
            teste = linha_atual + (" " if linha_atual else "") + palavra
            if self.fonts["ui"].size(teste)[0] <= max_width: linha_atual = teste
            else:
                if linha_atual: linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual: linhas.append(linha_atual)
        for i, linha in enumerate(linhas[:4]): self.tela.blit(self.fonts["ui"].render(linha, False, (255, 255, 255)), (x, y + i * 28))

    def draw_menu(self):
        """Tela de menu inicial com comandos. Só avança ao pressionar Enter."""
        waiting = True
        import math, time
        t_start = time.time()
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    waiting = False

            self.tela.fill((12, 12, 30))
            # Fundo com gradiente sutil
            for i in range(ALTURA_TELA):
                r = int(10 + i * 0.015)
                g = int(12 + i * 0.01)
                b = int(16 + i * 0.025)
                pygame.draw.line(self.tela, (r, g, b), (0, i), (LARGURA_TELA, i))

            # Overlay colorido
            BLUE_THEME = (50, 150, 255)
            ov = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            ov.fill((*BLUE_THEME, 12))
            self.tela.blit(ov, (0, 0))

            t = time.time() - t_start

            # Título
            title = self.fonts["grande"].render("FASE 3", True, BLUE_THEME)
            self.tela.blit(title, (LARGURA_TELA // 2 - title.get_width() // 2, 60))

            sub = self.fonts["ui"].render("A FOME, A SECA, A DESIGUALDADE E A CORRUPÇÃO (ODS 1, 6 e 10)", True, (180, 184, 200))
            self.tela.blit(sub, (LARGURA_TELA // 2 - sub.get_width() // 2, 120))

            # Caixa de comandos
            box_w, box_h = 460, 260
            box_x = LARGURA_TELA // 2 - box_w // 2
            box_y = 170
            pygame.draw.rect(self.tela, (20, 24, 35), (box_x, box_y, box_w, box_h), border_radius=8)
            pygame.draw.rect(self.tela, (*BLUE_THEME, 80), (box_x, box_y, box_w, box_h), 2, border_radius=8)

            # Título da caixa
            cmd_title = self.fonts["ui"].render("COMANDOS", True, (100, 200, 255))
            self.tela.blit(cmd_title, (LARGURA_TELA // 2 - cmd_title.get_width() // 2, box_y + 12))

            # Separador
            pygame.draw.line(self.tela, (60, 65, 80), (box_x + 20, box_y + 42), (box_x + box_w - 20, box_y + 42), 1)

            # Lista de comandos
            commands = [
                ("A / <", "Mover para esquerda"),
                ("D / >", "Mover para direita"),
                ("W / ^", "Pular / Entrar"),
                ("E", "Interagir com NPCs"),
                ("F", "Atirar"),
                ("ALT + F4", "Sair da fase"),
            ]
            cy = box_y + 55
            for key, desc in commands:
                kt = self.fonts["ui"].render(key, True, (0, 255, 255))
                self.tela.blit(kt, (box_x + 30, cy))
                pygame.draw.rect(self.tela, (50, 55, 70), (box_x + 200, cy + 2, 2, 14))
                dt_text = self.fonts["ui"].render(desc, True, (255, 255, 255))
                self.tela.blit(dt_text, (box_x + 215, cy))
                cy += 32

            # Objetivo
            obj_y = box_y + box_h + 20
            obj_box = pygame.Rect(box_x, obj_y, box_w, 50)
            from utils import draw_wrapped_objective
            draw_wrapped_objective(
                self.tela, obj_box,
                "OBJETIVO: Ajude a vila sem água potável e investigue as casas para derrotar o Chefe!",
                self.fonts["ui"], (15, 30, 40), (50, 200, 100, 80), (50, 200, 100)
            )

            # Botão Enter pulsante
            pulse = int((math.sin(t * 3) + 1) * 0.5 * 40 + 215)
            enter_text = self.fonts["ui"].render("Pressione ENTER para iniciar", True, (pulse, pulse, pulse))
            self.tela.blit(enter_text, (LARGURA_TELA // 2 - enter_text.get_width() // 2, ALTURA_TELA - 70))

            pygame.display.flip()
            self.clock.tick(30)

    def run(self):
        self.draw_menu()
        while True:
            dt = self.clock.tick(60) / 1000.0
            mostrar_prompt = self.handle_events()
            if mostrar_prompt == 'quit': return False
            if mostrar_prompt == 'win':
                from utils import show_end_screen
                show_end_screen(
                    self.tela, self.clock,
                    "FASE CONCLUIDA", "",
                    (34, 255, 136), "CONTINUAR",
                    stats=None,
                    lesson="Garantir a disponibilidade e gestão sustentável da água e saneamento para todos."
                )
                return True
            if mostrar_prompt == 'gameover':
                self.reset()
                continue
            self.update(dt)
            self.draw(mostrar_prompt)

if __name__ == "__main__":
    Game().run()

def run_level_3():
    import pygame
    orig_quit = pygame.quit
    pygame.quit = lambda: None
    try:
        won = Game().run()
        return bool(won)
    except SystemExit:
        return False
    except Exception as e:
        print(f"Erro ao executar Level 3: {e}")
        return False
    finally:
        pygame.quit = orig_quit
