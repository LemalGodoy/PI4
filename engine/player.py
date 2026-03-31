import pygame
import settings


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.speed = 8
        self.inverted_controls = False

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        # Impede de sair dos limites do mundo
        self.rect.x = max(0, min(self.rect.x, settings.WORLD_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, settings.WORLD_HEIGHT - self.rect.height))

    def draw(self, surface):
        self.draw_at(surface, self.rect.x, self.rect.y)

    def draw_at(self, surface, x, y):
        """Desenha o jogador na posição (x, y) da surface, sem alterar self.rect."""
        w, h = self.rect.width, self.rect.height

        # Sombra
        pygame.draw.ellipse(surface, (30, 30, 30), (x, y + h - 10, w, 15))

        # Corpo (cavaleiro pixel art)
        pygame.draw.rect(surface, (120, 120, 120), (x + 8, y + 20, 24, 25))
        # Cinto
        pygame.draw.rect(surface, (80, 50, 30), (x + 8, y + 40, 24, 5))
        # Pernas
        pygame.draw.rect(surface, (60, 60, 60), (x + 10, y + 45, 8, 15))
        pygame.draw.rect(surface, (60, 60, 60), (x + 22, y + 45, 8, 15))
        # Botas
        pygame.draw.rect(surface, (40, 40, 40), (x + 8, y + 55, 10, 5))
        pygame.draw.rect(surface, (40, 40, 40), (x + 22, y + 55, 10, 5))
        # Braços
        pygame.draw.rect(surface, (100, 100, 100), (x, y + 22, 8, 18))
        pygame.draw.rect(surface, (100, 100, 100), (x + 32, y + 22, 8, 18))
        # Capacete
        pygame.draw.rect(surface, (180, 180, 180), (x + 6, y + 5, 28, 20))
        # Visor do capacete
        pygame.draw.rect(surface, (30, 30, 30), (x + 12, y + 10, 16, 6))
