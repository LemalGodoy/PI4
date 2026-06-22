"""
Camera — Sistema de câmera com scroll suave (lerp) para fases scrolláveis.

Uso:
    camera = Camera(world_w, world_h, viewport_w, viewport_h)
    camera.update(player.rect)              # a cada frame
    screen_pos = camera.apply(entity.rect)  # para desenhar
"""
from __future__ import annotations

import pygame


class Camera:
    """Câmera 2D com interpolação linear para acompanhar o jogador suavemente."""

    __slots__ = ("world_w", "world_h", "vp_w", "vp_h", "offset_x", "offset_y", "lerp_speed")

    def __init__(self, world_w: int, world_h: int, viewport_w: int, viewport_h: int,
                 lerp_speed: float = 0.08):
        self.world_w = world_w
        self.world_h = world_h
        self.vp_w = viewport_w
        self.vp_h = viewport_h
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.lerp_speed = lerp_speed

    # ------------------------------------------------------------------ #
    #  Core
    # ------------------------------------------------------------------ #

    def update(self, target_rect: pygame.Rect) -> None:
        """Atualiza o offset para centralizar no *target_rect* com suavidade."""
        # Posição desejada — centro do alvo no centro da viewport
        desired_x = target_rect.centerx - self.vp_w // 2
        desired_y = target_rect.centery - self.vp_h // 2

        # Interpolação linear para scroll orgânico
        self.offset_x += (desired_x - self.offset_x) * self.lerp_speed
        self.offset_y += (desired_y - self.offset_y) * self.lerp_speed

        # Clamp — nunca mostrar fora do mundo
        self.offset_x = max(0.0, min(self.offset_x, self.world_w - self.vp_w))
        self.offset_y = max(0.0, min(self.offset_y, self.world_h - self.vp_h))

    def snap(self, target_rect: pygame.Rect) -> None:
        """Posiciona a câmera **instantaneamente** no alvo (sem lerp). Útil em resets."""
        self.offset_x = float(target_rect.centerx - self.vp_w // 2)
        self.offset_y = float(target_rect.centery - self.vp_h // 2)
        self.offset_x = max(0.0, min(self.offset_x, self.world_w - self.vp_w))
        self.offset_y = max(0.0, min(self.offset_y, self.world_h - self.vp_h))

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Retorna uma cópia de *rect* deslocada para coordenadas de tela."""
        return rect.move(-int(self.offset_x), -int(self.offset_y))

    def apply_pos(self, x: float, y: float) -> tuple[int, int]:
        """Converte uma posição de mundo para posição de tela."""
        return int(x - self.offset_x), int(y - self.offset_y)

    @property
    def rect(self) -> pygame.Rect:
        """Retorna o retângulo visível no mundo (útil para culling)."""
        return pygame.Rect(int(self.offset_x), int(self.offset_y), self.vp_w, self.vp_h)
