import pygame
import os
import settings
from entities import Door
from renderer import draw_placeholder_background


class Lobby:
    """Cena do Bazar / Lobby com apenas as 5 ODS ativas (Sem rastros de 17 posições)"""

    def __init__(self):
        self.doors = []
        
        # Cria apenas as 5 portas baseadas estritamente no dicionário do settings
        for id_ods, (posicao, raio) in settings.ODS_HITBOXES.items():
            cx, cy = posicao
            
            # Cria o Rect limitador baseado no raio da parcela para colisão física do jogador
            hitbox_rect = pygame.Rect(cx - raio, cy - raio, raio * 2, raio * 2)
            
            nome_ods = settings.ODS_NAMES[id_ods]
            cor_ods = settings.ODS_COLORS[id_ods]
            
            nova_porta = Door(hitbox_rect, id_ods, nome_ods, cor_ods)
            nova_porta.radius = raio
            nova_porta.center_pos = posicao
            
            self.doors.append(nova_porta)

        # Carrega as imagens de névoa (nev4 = mais névoa, nev1 = menos névoa)
        # nev4: 0 fases concluídas, nev3: 1 fase, nev2: 2 fases, nev1: 3 fases, nenhuma: 4+ fases
        self.fog_images = {}
        for i in range(1, 5):
            fog_path = os.path.join(settings.ASSETS_DIR, f"nev{i}.png")
            if not os.path.exists(fog_path):
                fog_path = os.path.join(settings.SCRIPT_DIR, "assets", f"nev{i}.png")
            try:
                raw = pygame.image.load(fog_path).convert_alpha()
                self.fog_images[i] = pygame.transform.scale(raw, (settings.WIDTH, settings.HEIGHT))
            except Exception as e:
                print(f"Aviso: Não foi possível carregar nev{i}.png: {e}")
                self.fog_images[i] = None

        # Carrega a imagem do carimbo para fases concluídas
        carimbo_path = os.path.join(settings.ASSETS_DIR, "carimbo.png")
        if not os.path.exists(carimbo_path):
            carimbo_path = os.path.join(settings.SCRIPT_DIR, "assets", "carimbo.png")
        try:
            raw_carimbo = pygame.image.load(carimbo_path).convert_alpha()
            self.img_carimbo = pygame.transform.scale(raw_carimbo, (200, 200))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar carimbo.png: {e}")
            self.img_carimbo = None

    def is_unlocked(self, door_id):
        if door_id == 1:
            return True
        for i in range(1, door_id):
            door = next((d for d in self.doors if d.id == i), None)
            if not door or door.color != (0, 255, 0):
                return False
        return True

    def _contar_fases_concluidas(self):
        """Conta quantas portas/fases foram concluídas (cor verde)"""
        return sum(1 for d in self.doors if d.color == (0, 255, 0))

    def _get_fog_image(self):
        """Retorna a imagem de névoa adequada ao progresso atual, ou None se todas as fases foram zeradas"""
        concluidas = self._contar_fases_concluidas()
        # 0 concluídas → nev4, 1 → nev3, 2 → nev2, 3 → nev1, 4+ → sem névoa
        if concluidas >= 4:
            return None
        nev_index = 4 - concluidas  # 0→4, 1→3, 2→2, 3→1
        return self.fog_images.get(nev_index)

    def update(self, player, keys):
        """Atualiza o estado do lobby"""
        player.move(keys)

    def get_interacting_door(self, player):
        """Retorna a porta com a qual o jogador está interagindo, ou None"""
        for d in self.doors:
            if player.rect.colliderect(d.rect):
                return d
        return None

    def draw(self, surface, player):
        """Renderiza o lobby completo sem nenhuma geometria visível nas hitboxes"""
        # Câmera segue o jogador
        camera_x = player.rect.centerx - settings.WIDTH // 2
        camera_y = player.rect.centery - settings.HEIGHT // 2
        camera_x = max(0, min(camera_x, settings.WORLD_WIDTH - settings.WIDTH))
        camera_y = max(0, min(camera_y, settings.WORLD_HEIGHT - settings.HEIGHT))

        # 1. Background
        bg_x = (0 - camera_x) if camera_x > 0 else 0
        bg_y = (0 - camera_y) if camera_y > 0 else 0
        if settings.bg_image:
            surface.blit(settings.bg_image, (bg_x, bg_y))
        else:
            draw_placeholder_background(surface, camera_x, camera_y)
            warn_text = settings.font.render(
                'Salve a imagem como "background.jpg" na pasta do jogo para ver a arte real!',
                True, (255, 255, 255))
            pygame.draw.rect(surface, (0, 0, 0),
                             (settings.WIDTH // 2 - warn_text.get_width() // 2 - 10, 20,
                              warn_text.get_width() + 20, 30))
            surface.blit(warn_text,
                         (settings.WIDTH // 2 - warn_text.get_width() // 2, 25))

        # 2. Overlay de névoa (bloqueia visão das fases não desbloqueadas)
        fog_img = self._get_fog_image()
        if fog_img:
            surface.blit(fog_img, (bg_x, bg_y))

        # 3. Interações das ODS (Apenas texto, sem círculos ou bordas)
        for d in self.doors:
            screen_cx = d.center_pos[0] - camera_x
            screen_cy = d.center_pos[1] - camera_y

            if player.rect.colliderect(d.rect):
                unlocked = self.is_unlocked(d.id)
                # Tooltip descritivo da ODS ativa
                name_text = settings.door_font.render(d.name, True, (255, 255, 255))
                if not unlocked:
                    name_text.set_alpha(128)  # 50% opacity
                
                bg_rect = pygame.Rect(
                    int(screen_cx - name_text.get_width() // 2 - 10),
                    int(screen_cy - d.radius - 80),
                    int(name_text.get_width() + 20),
                    int(name_text.get_height() + 10)
                )
                
                # Cor do fundo com opacidade se bloqueado
                bg_color = (30, 30, 30)
                border_color = d.color
                
                if not unlocked:
                    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(bg_surf, (30, 30, 30, 128), bg_surf.get_rect(), border_radius=5)
                    pygame.draw.rect(bg_surf, (*d.color[:3], 128), bg_surf.get_rect(), 2, border_radius=5)
                    surface.blit(bg_surf, (bg_rect.x, bg_rect.y))
                else:
                    pygame.draw.rect(surface, bg_color, bg_rect, border_radius=5)
                    pygame.draw.rect(surface, border_color, bg_rect, 2, border_radius=5)
                    
                surface.blit(name_text, (bg_rect.x + 10, bg_rect.y + 5))

                # Prompt de interação "[E] Entrar" ou "[Bloqueado]"
                hint_str = "[E] Entrar" if unlocked else "[Bloqueado]"
                hint_text = settings.font.render(hint_str, True, (0, 0, 0))
                if not unlocked:
                    hint_text.set_alpha(128)
                    
                hint_bg = pygame.Rect(
                    bg_rect.centerx - hint_text.get_width() // 2 - 5,
                    bg_rect.bottom + 5,
                    hint_text.get_width() + 10,
                    hint_text.get_height() + 4)
                    
                if not unlocked:
                    hint_bg_surf = pygame.Surface((hint_bg.width, hint_bg.height), pygame.SRCALPHA)
                    pygame.draw.rect(hint_bg_surf, (255, 255, 255, 128), hint_bg_surf.get_rect(), border_radius=3)
                    surface.blit(hint_bg_surf, (hint_bg.x, hint_bg.y))
                else:
                    pygame.draw.rect(surface, (255, 255, 255), hint_bg, border_radius=3)
                    
                surface.blit(hint_text, (hint_bg.x + 5, hint_bg.y + 2))

            # Se a ODS foi concluída, mostra a imagem carimbo.png sobre a hitbox da porta
            if d.color == (0, 255, 0):
                if hasattr(self, 'img_carimbo') and self.img_carimbo:
                    surface.blit(self.img_carimbo, (screen_cx - self.img_carimbo.get_width() // 2,
                                             screen_cy - self.img_carimbo.get_height() // 2))
                else:
                    font_win_ods = pygame.font.Font(None, 60)
                    text_done = font_win_ods.render(str(d.id), True, (0, 255, 0))
                    surface.blit(text_done, (screen_cx - text_done.get_width() // 2,
                                             screen_cy - text_done.get_height() // 2))

        # 4. Desenha o jogador
        player.draw_at(surface, player.rect.x - camera_x, player.rect.y - camera_y)