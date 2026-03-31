import pygame
import settings
from engine.entities import Door
from engine.renderer import draw_placeholder_background


class Lobby:
    """Cena do Bazar / Lobby com as 17 barracas ODS"""

    def __init__(self):
        self.doors = []
        for i in range(17):
            x, y = settings.ODS_POS[i]
            self.doors.append(Door(
                pygame.Rect(x - settings.DOOR_W // 2, y - settings.DOOR_H // 2,
                            settings.DOOR_W, settings.DOOR_H),
                i + 1,
                settings.ODS_NAMES[i],
                settings.ODS_COLORS[i]
            ))

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
        """Renderiza o lobby completo"""
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

        # 2. Portas / Barracas ODS
        for d in self.doors:
            screen_rect = d.rect.move(0 - camera_x, 0 - camera_y)

            if player.rect.colliderect(d.rect):
                # Highlight ao se aproximar
                s = pygame.Surface((settings.DOOR_W, settings.DOOR_H), pygame.SRCALPHA)
                s.fill((*d.color, 80))
                surface.blit(s, (screen_rect.x, screen_rect.y))
                pygame.draw.rect(surface, (255, 255, 255), screen_rect, 3, border_radius=10)

                # Tooltip com o nome da ODS
                name_text = settings.door_font.render(d.name, True, (255, 255, 255))
                bg_rect = pygame.Rect(
                    int(screen_rect.centerx - name_text.get_width() // 2 - 10),
                    int(screen_rect.top - 45),
                    int(name_text.get_width() + 20),
                    int(name_text.get_height() + 10)
                )
                pygame.draw.rect(surface, (30, 30, 30), bg_rect, border_radius=5)
                pygame.draw.rect(surface, d.color, bg_rect, 2, border_radius=5)
                surface.blit(name_text, (bg_rect.x + 10, bg_rect.y + 5))

                # Dica de botão
                hint_text = settings.font.render("[E] Entrar", True, (0, 0, 0))
                hint_bg = pygame.Rect(
                    bg_rect.centerx - hint_text.get_width() // 2 - 5,
                    bg_rect.bottom + 5,
                    hint_text.get_width() + 10,
                    hint_text.get_height() + 4)
                pygame.draw.rect(surface, (255, 255, 255), hint_bg, border_radius=3)
                surface.blit(hint_text, (hint_bg.x + 5, hint_bg.y + 2))

            elif not settings.bg_image:
                # Porta visível sem background (modo guia)
                pygame.draw.rect(surface, d.color, screen_rect, border_radius=10)
                pygame.draw.rect(surface, (255, 255, 255), screen_rect, 2, border_radius=10)
                text = settings.door_font.render(str(d.id), True, (255, 255, 255))
                surface.blit(text, (screen_rect.centerx - text.get_width() // 2,
                                    screen_rect.centery - text.get_height() // 2))

            # ODS completada: número verde
            if d.color == (0, 255, 0):
                font_win_ods = pygame.font.Font(None, 60)
                text_done = font_win_ods.render(str(d.id), True, (0, 255, 0))
                surface.blit(text_done, (screen_rect.centerx - text_done.get_width() // 2,
                                         screen_rect.centery - text_done.get_height() // 2))

        # 3. Jogador (ajustado pela câmera)
        player.draw_at(surface, player.rect.x - camera_x, player.rect.y - camera_y)
