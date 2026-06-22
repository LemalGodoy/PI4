import pygame
import sys
import math
import random
import os
import settings

from settings import LARGURA_TELA, ALTURA_TELA
from entities import Player
from levels.level_1 import run_level_1
from levels.level_2 import run_level_2
from levels.level_3 import run_level_3
from levels.level_4 import run_level_4
from levels.level_5 import Level5Boss, run_level_5
from lobby import Lobby

# Configuração de diretório para PyInstaller
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Particula:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.tamanho = random.uniform(1, 3)
        self.cor = random.choice([
            (255, 255, 255), (220, 240, 255),
            (200, 220, 255), (255, 250, 200)
        ])

        # Cache da superfície da partícula para evitar recriação constante em runtime
        self.surf_base = pygame.Surface((int(self.tamanho * 2), int(self.tamanho * 2)), pygame.SRCALPHA)
        pygame.draw.circle(self.surf_base, self.cor, (int(self.tamanho), int(self.tamanho)), int(self.tamanho))
        
        self.reset(inicial=True)

    def reset(self, inicial=False):
        self.x = random.randint(0, self.largura) if inicial else self.largura + random.randint(5, 50)
        self.y = random.randint(0, self.altura)
        self.vel_x = random.uniform(-15, -40)
        self.vel_y = random.uniform(-8, 8)
        self.vida = random.uniform(3, 8)
        self.vida_max = self.vida
        self.alpha = random.randint(40, 120)

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.vida -= dt
        
        ratio = max(0.0, self.vida / self.vida_max)
        self.alpha = int(ratio * 120)
        
        if self.x < -10 or self.vida <= 0:
            self.reset()

    def draw(self, surf):
        if self.alpha > 5:
            # Copia a superfície em cache e apenas altera o canal alpha
            instancia_surf = self.surf_base.copy()
            instancia_surf.set_alpha(self.alpha)
            surf.blit(instancia_surf, (int(self.x), int(self.y)))


class BotaoMenu:
    def __init__(self, texto, x, y, largura, altura, cor_base, cor_hover, cor_texto=(255, 255, 255)):
        self.texto = texto
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.hover = False
        self.click_anim = 0.0

    def update(self, dt, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

        if self.click_anim > 0:
            self.click_anim = max(0.0, self.click_anim - dt * 6)

    def draw(self, surf, font):
        offset = 3 if self.click_anim > 0 else 0

        # Apenas a borda
        borda_rect = (
            self.rect.x,
            self.rect.y + offset,
            self.rect.width,
            self.rect.height
        )

        pygame.draw.rect(surf, (255, 255, 255), borda_rect, 3)

        # Glow leve no hover
        if self.hover:
            brilho = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            brilho.fill((255, 255, 255, 25))
            surf.blit(brilho, (self.rect.x, self.rect.y + offset))

        # Texto sem sombra
        txt = font.render(self.texto, False, self.cor_texto)

        txt_rect = txt.get_rect(
            center=(self.rect.centerx, self.rect.centery + offset)
        )

        surf.blit(txt, txt_rect)

    def clicado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.click_anim = 1.0
                return True

        return False

class TelaCreditos:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.ativa = False
        self.nomes = [
            "Daniel Silva Souza",
            "Franklin Pereira Santos Filho",
            "Giovanni Turetta",
            "Guilherme Gabriel Crispim",
            "Kauã Gianei de Matos",
            "Pedro Henrique Malpeli",
            "",
            "PyGameLoaderFx: kerodekroma",
        ]
        
        # Inicializa fontes internas
        self.font_titulo = pygame.font.SysFont("Consolas", 50, bold=True)
        self.font_nome = pygame.font.SysFont("Consolas", 26)
        self.font_dica = pygame.font.SysFont("Consolas", 18)

    def abrir(self): self.ativa = True
    def fechar(self): self.ativa = False

    def draw(self, surf):
        if not self.ativa:
            return
            
        surf.fill((0, 0, 0))
        
        titulo = self.font_titulo.render("CRÉDITOS", True, (200, 230, 255))
        surf.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, 120))
        
        y = 220
        for nome in self.nomes:
            if nome:
                txt = self.font_nome.render(nome, True, (255, 255, 255))
                surf.blit(txt, (self.largura // 2 - txt.get_width() // 2, y))
            y += 45
            
        dica = self.font_dica.render("Pressione ESC para voltar", True, (150, 150, 150))
        surf.blit(dica, (self.largura // 2 - dica.get_width() // 2, self.altura - 60))


class MenuPrincipal:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.get_surface()
        if self.tela is None:
            self.tela = pygame.display.set_mode(
                (LARGURA_TELA, ALTURA_TELA),
                pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED | pygame.RESIZABLE
            )
        pygame.display.set_caption("PROJETO 17 | Menu")
        self.clock = pygame.time.Clock()
        self.rodando = True
        
        # Variáveis de Estado e Tempo
        self.timer = 0.0
        self.frame_idx = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.18
        self.fade_alpha = 255
        self.fade_ativo = True
        
        self.historia_texto = [
            "EM UM MUNDO DEVASTADO PELO INFERNAL GLITCH,",
            "ONDE OS SOBREVIVENTES ESTÃO COMPLETAMENTE SEM",
            "ESPERANÇA, A VIAJANTE PLANETÁRIA HOPE ATERRISSA",
            "EM BUSCA DE RESTAURAÇÃO.", "", "",
            "O GLITCH AFETOU 9 DAS 17 ODS E AGORA ELA",
            "PRECISA DA SUA AJUDA PARA GUIA-LA EM SUA",
            "TRILHA PERIGOSA E DESCONHECIDA.", "", "",
            "QUEM É GLITCH?", "", "", "O QUE ELE QUER?", "", "",
            "O QUE SUA PRESENÇA SIMBOLIZA?"
        ]

        self.load_assets()
        self.setup_ui()
        self.setup_particles()

    def load_assets(self):
        sheet_full = pygame.image.load("assets/iddlefull.png").convert_alpha()
        
        # Extração de frames otimizada
        frame_h = sheet_full.get_height() // 5
        frame_w = sheet_full.get_width()
        self.char_height = int(ALTURA_TELA * 0.85)
        self.idle_frames_scaled = []
        
        for i in range(5):
            frame = sheet_full.subsurface(pygame.Rect(0, i * frame_h, frame_w, frame_h))
            aspect = frame.get_width() / frame.get_height()
            w = int(self.char_height * aspect)
            self.idle_frames_scaled.append(pygame.transform.scale(frame, (w, self.char_height)))

    def setup_ui(self):
        self.font_titulo = pygame.font.SysFont("Consolas", 62, bold=True)
        self.font_subtitulo = pygame.font.SysFont("Consolas", 22)
        self.font_botao = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_dica = pygame.font.SysFont("Consolas", 14)
        
        centro_y = ALTURA_TELA // 2 + 40
        self.btn_iniciar = BotaoMenu("INICIAR", 80, centro_y, 280, 60, (44, 62, 120), (70, 95, 170))
        self.btn_creditos = BotaoMenu("CRÉDITOS", 80, centro_y + 85, 280, 60, (70, 70, 70), (110, 110, 110))
        self.botoes = [self.btn_iniciar, self.btn_creditos]
        self.creditos = TelaCreditos(LARGURA_TELA, ALTURA_TELA)

    def setup_particles(self):
        self.particulas = [Particula(LARGURA_TELA, ALTURA_TELA) for _ in range(60)]

    def run(self):
        while self.rodando:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            self.handle_events()
            self.update(dt)
            self.render()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
                
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif evento.key == pygame.K_ESCAPE:
                    if self.creditos.ativa:
                        self.creditos.fechar()
                    else:
                        self.rodando = False
                        
            if not self.creditos.ativa:
                if self.btn_iniciar.clicado(evento):
                    self.iniciar_jogo()
                elif self.btn_creditos.clicado(evento):
                    self.creditos.abrir()

    def iniciar_jogo(self):
        flash = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        flash.fill((255, 255, 255))
        for alpha in range(0, 256, 8):
            flash.set_alpha(alpha)
            self.render()
            self.tela.blit(flash, (0, 0))
            pygame.display.flip()
            pygame.time.delay(15)
            
        self.exibir_historia()
        main()
        sys.exit()

    def exibir_historia(self):
        rodando_historia = True
        scroll_y = ALTURA_TELA
        font_historia = pygame.font.SysFont("Consolas", 32, bold=True)
        
        text_surfaces = [font_historia.render(line, True, (255, 255, 255)) for line in self.historia_texto]
        clock_historia = pygame.time.Clock()
        
        while rodando_historia:
            dt = clock_historia.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    rodando_historia = False
                    
            self.tela.fill((0, 0, 0))
            for p in self.particulas:
                p.draw(self.tela)
                
            y_atual = scroll_y
            for surf in text_surfaces:
                h_original = surf.get_height()
                w_original = surf.get_width()
                
                if -100 < y_atual < ALTURA_TELA + 100:
                    alpha = max(0, min(255, int(255 * (y_atual / (ALTURA_TELA * 0.8)))))
                    
                    for row in range(h_original):
                        row_y = y_atual + row
                        if 0 <= row_y < ALTURA_TELA:
                            p_fator = 0.2 + (row_y / ALTURA_TELA) * 0.8
                            slice_w = int(w_original * p_fator)
                            
                            if slice_w > 0:
                                slice_surf = surf.subsurface((0, row, w_original, 1))
                                scaled_slice = pygame.transform.scale(slice_surf, (slice_w, 1))
                                scaled_slice.set_alpha(alpha)
                                pos_x = LARGURA_TELA // 2 - slice_w // 2
                                self.tela.blit(scaled_slice, (pos_x, row_y))
                                
                y_atual += int(50 * (0.2 + (y_atual / ALTURA_TELA) * 0.8))
                
            scroll_y -= 45 * dt
            if y_atual < -50:
                rodando_historia = False
            pygame.display.flip()
            
        # Fade out suave ao terminar a história
        fade = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        fade.fill((0, 0, 0))
        for a in range(0, 256, 5):
            fade.set_alpha(a)
            self.tela.blit(fade, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)

    def update(self, dt):
        self.timer += dt
        self.anim_timer += dt
        
        if self.anim_timer >= self.anim_speed:
            self.anim_timer -= self.anim_speed
            self.frame_idx = (self.frame_idx + 1) % len(self.idle_frames_scaled)
            
        if not self.creditos.ativa:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.botoes:
                btn.update(dt, mouse_pos)
                
        for p in self.particulas:
            p.update(dt)
            
        if self.fade_ativo:
            self.fade_alpha = max(0, self.fade_alpha - int(200 * dt))
            if self.fade_alpha <= 0:
                self.fade_ativo = False

    def render(self):
        self.tela.fill((0, 0, 0))
        for p in self.particulas:
            p.draw(self.tela)
            
        # Posicionamento e efeitos do Personagem
        frame = self.idle_frames_scaled[self.frame_idx]
        bob_y = math.sin(self.timer * 1.5) * 4
        char_x = LARGURA_TELA - frame.get_width() - 20
        char_y = ALTURA_TELA - frame.get_height() + int(bob_y) + 10
        
        # Sombra sob o personagem
        sombra_w, sombra_h = int(frame.get_width() * 0.6), 20
        sombra_surf = pygame.Surface((sombra_w, sombra_h), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra_surf, (0, 0, 0, 60), (0, 0, sombra_w, sombra_h))
        self.tela.blit(sombra_surf, (char_x + frame.get_width() // 2 - sombra_w // 2, ALTURA_TELA - 30))
        
        # Glow pulsante do personagem
        glow_r = int(frame.get_width() * 0.5)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (150, 200, 255, int(40 * (0.7 + 0.3 * math.sin(self.timer * 2)))), (glow_r, glow_r), glow_r)
        self.tela.blit(glow_surf, (char_x + frame.get_width() // 2 - glow_r, char_y + frame.get_height() // 2 - glow_r))
        self.tela.blit(frame, (char_x, char_y))
        
        # Renderização do Título Principal
        titulo_y = 100
        titulo_sombra = self.font_titulo.render("PROJETO 17", True, (0, 0, 0))
        self.tela.blit(titulo_sombra, (84, titulo_y + 4))
        
        titulo_cor_val = int(200 + 55 * math.sin(self.timer * 1.2))
        titulo_txt = self.font_titulo.render("PROJETO 17", True, (titulo_cor_val, 230, 255))
        self.tela.blit(titulo_txt, (80, titulo_y))
        
        # Subtítulo
        sub_txt = self.font_subtitulo.render("As ODS precisam de sua ajuda!", True, (180, 200, 220))
        self.tela.blit(sub_txt, (84, titulo_y + titulo_txt.get_height() + 20))
        
        if not self.creditos.ativa:
            for btn in self.botoes:
                btn.draw(self.tela, self.font_botao)
            
            dica_alpha = int(100 + 50 * math.sin(self.timer * 2))
            dica_txt = self.font_dica.render("F11 — Tela Cheia  |  ESC — Sair", True, (180, 170, 150))
            dica_txt.set_alpha(dica_alpha)
            self.tela.blit(dica_txt, (LARGURA_TELA // 2 - dica_txt.get_width() // 2, ALTURA_TELA - 30))
            
        self.creditos.draw(self.tela)
        
        if self.fade_ativo:
            fade_surf = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            self.tela.blit(fade_surf, (0, 0))

def main():
    lobby = Lobby()
    player = Player(settings.WIDTH // 2 - 20, settings.HEIGHT // 2 - 90)
    level5 = Level5Boss()

    current_state = "LOBBY"
    current_ods = None
    lobby_pos = (player.rect.x, player.rect.y)

    # Dicionário mapeando os NOVOS IDs para suas respectivas funções e índices
    fases_mapeamento = {
        1: (run_level_1, 0),
        3: (run_level_3, 5),
        4: (run_level_4, 6),
        2: (run_level_2, 8),
        5: (run_level_5, 15)
    }
    

    while True:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    
                elif current_state == "LOBBY" and event.key in (pygame.K_e, pygame.K_RETURN):
                    door = lobby.get_interacting_door(player)
                    if door and lobby.is_unlocked(door.id):
                        current_ods = door
                        lobby_pos = (player.rect.x, player.rect.y)
                        
                        if door.id in fases_mapeamento:
                            funcao_level, _ = fases_mapeamento[door.id]
                            if funcao_level():
                                # Procura qual das 5 portas ativas tem o ID correspondente e muda a cor dela
                                for d in lobby.doors:
                                    if d.id == door.id:
                                        d.color = (0, 255, 0)
                                        break
                            player.set_position(*lobby_pos)
                            
                            # Reinicia as variáveis normais de retorno ao lobby.
                            current_state = "LOBBY"
                            current_ods = None
                        else:
                            current_state = f"LEVEL_{door.id}"

                elif current_state.startswith("LEVEL_") and event.key == pygame.K_ESCAPE:
                    if current_state == "LEVEL_5":
                        player.inverted_controls = False
                    else:
                        player.rect.y += 30
                    player.set_position(*lobby_pos)
                    current_state = "LOBBY"
                    current_ods = None

        # Updates e Renderização de Estados
        if current_state == "LOBBY":
            lobby.update(player, keys)
            lobby.draw(settings.screen, player)
        else:
            if current_ods:
                settings.screen.fill(current_ods.color)
                cx, cy = settings.WIDTH // 2, settings.HEIGHT // 2
                
                textos = [
                    (settings.title_font.render(f"Fase da ODS {current_ods.id}", True, (255, 255, 255)), -80),
                    (settings.title_font.render(current_ods.name, True, (255, 255, 255)), -30),
                    (settings.font.render("O código e a dinâmica dessa fase específica entrarão aqui.", True, (220, 220, 220)), 20),
                    (settings.font.render(">>> Pressione ESC para voltar ao Bazar <<<", True, (255, 255, 255)), 100)
                ]
                for surf_txt, offset_y in textos:
                    settings.screen.blit(surf_txt, (cx - surf_txt.get_width() // 2, cy + offset_y))

        pygame.display.flip()
        settings.clock.tick(60)

def play_loading_screen(screen):
    pygame.display.set_caption("a PyGame Project")
    try:
        from PIL import Image
        gif = Image.open("assets/pygame.gif")
    except Exception as e:
        print("Erro ao carregar gif:", e)
        return
    
    frames = []
    try:
        while True:
            frame_image = gif.convert("RGBA")
            str_format = frame_image.tobytes("raw", "RGBA")
            frames.append(pygame.image.fromstring(str_format, frame_image.size, "RGBA"))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    if not frames:
        return
        
    bg_color = frames[0].get_at((0, 0))
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    duration = 1500
    
    while True:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed >= duration:
            break
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
        frame_idx = min(int((elapsed / duration) * len(frames)), len(frames) - 1)
        screen.fill(bg_color)
        
        current_frame = frames[frame_idx]
        screen.blit(current_frame, ((screen.get_width() - current_frame.get_width()) // 2, (screen.get_height() - current_frame.get_height()) // 2))
        
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    play_loading_screen(settings.screen)
    menu = MenuPrincipal()
    menu.run()