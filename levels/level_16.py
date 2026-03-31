import pygame
import random
import math


class Level16Boss:
    def __init__(self):
        self.w = 1376
        self.h = 768
        self.player_start = (self.w // 2 - 20, self.h - 100)
        self.won = False

        self.boss_rect = pygame.Rect(self.w // 2 - 50, 100, 100, 100)
        self.boss_hp = 3
        self.boss_timer = 0

        self.fake_error = None
        self.downgrade = False
        self.inverted_colors = False
        self.projectiles = []

    def reset(self, w, h):
        self.w = w
        self.h = h
        self.player_start = (self.w // 2 - 20, self.h - 100)
        self.won = False
        self.boss_rect = pygame.Rect(self.w // 2 - 50, 100, 100, 100)
        self.boss_hp = 3
        self.boss_timer = 0
        self.fake_error = None
        self.downgrade = False
        self.inverted_colors = False
        self.projectiles = []

    def handle_movement(self, player, keys):
        left = pygame.K_a if not player.inverted_controls else pygame.K_d
        right = pygame.K_d if not player.inverted_controls else pygame.K_a
        up = pygame.K_w if not player.inverted_controls else pygame.K_s
        down = pygame.K_s if not player.inverted_controls else pygame.K_w
        left_a = pygame.K_LEFT if not player.inverted_controls else pygame.K_RIGHT
        right_a = pygame.K_RIGHT if not player.inverted_controls else pygame.K_LEFT
        up_a = pygame.K_UP if not player.inverted_controls else pygame.K_DOWN
        down_a = pygame.K_DOWN if not player.inverted_controls else pygame.K_UP

        dx, dy = 0, 0
        if keys[left] or keys[left_a]: dx = -player.speed
        if keys[right] or keys[right_a]: dx = player.speed
        if keys[up] or keys[up_a]: dy = -player.speed
        if keys[down] or keys[down_a]: dy = player.speed

        player.rect.x += dx
        player.rect.y += dy

        player.rect.x = max(0, min(player.rect.x, self.w - player.rect.width))
        player.rect.y = max(0, min(player.rect.y, self.h - player.rect.height))

    def update(self, player):
        if self.boss_hp <= 0:
            self.won = True
            player.inverted_controls = False
            self.inverted_colors = False
            self.downgrade = False
            return

        self.boss_timer += 1

        if self.boss_hp == 3:  # Fase 1: Fake Error Code
            if self.fake_error is None and self.boss_timer > 60:
                self.fake_error = pygame.Rect(self.w // 2 - 200, self.h // 2 - 100, 400, 150)

            if self.fake_error:
                if player.rect.colliderect(self.fake_error):
                    self.fake_error = None
                    self.boss_hp -= 1
                    self.boss_timer = 0

        elif self.boss_hp == 2:  # Fase 2: Resolution Downgrade
            self.downgrade = True
            self.boss_rect.x += 10 * (1 if (self.boss_timer // 30) % 2 == 0 else -1)
            self.boss_rect.x = max(0, min(self.boss_rect.x, self.w - 100))

            if player.rect.colliderect(self.boss_rect):
                self.downgrade = False
                self.boss_hp -= 1
                self.boss_timer = 0

        elif self.boss_hp == 1:  # Fase 3: Inverted Colors
            self.inverted_colors = True
            player.inverted_controls = True
            self.boss_rect.x = int(
                self.w // 2 - 50 + math.sin(self.boss_timer * 0.05) * (self.w // 2 - 100)
            )

            if self.boss_timer % 30 == 0:
                self.projectiles.append(
                    pygame.Rect(self.boss_rect.centerx - 10, self.boss_rect.bottom, 20, 20)
                )

            for p in self.projectiles[:]:
                p.y += 10
                if player.rect.colliderect(p):
                    player.rect.y += 50
                    self.projectiles.remove(p)
                elif p.y > self.h:
                    self.projectiles.remove(p)

            if player.rect.colliderect(self.boss_rect):
                self.boss_hp -= 1
                self.inverted_colors = False
                player.inverted_controls = False
                self.projectiles.clear()

    def draw(self, surface):
        surface.fill((15, 0, 15))  # Null.exe dark purple background

        font_b = pygame.font.Font(None, 40)

        if self.boss_hp > 0:
            # Glitch Boss
            pygame.draw.rect(surface, (150, 0, 255), self.boss_rect)
            for _ in range(8):
                gx = self.boss_rect.x + random.randint(-10, 100)
                gy = self.boss_rect.y + random.randint(-10, 100)
                pygame.draw.rect(surface, (255, 255, 255),
                                 (gx, gy, random.randint(10, 30), random.randint(2, 8)))

        if self.fake_error:
            pygame.draw.rect(surface, (200, 200, 200), self.fake_error)
            pygame.draw.rect(surface, (0, 0, 150),
                             (self.fake_error.x, self.fake_error.y,
                              self.fake_error.width, 30))
            err_title = pygame.font.Font(None, 24).render(
                "ERRO FATAL NO SISTEMA ODS", True, (255, 255, 255))
            surface.blit(err_title, (self.fake_error.x + 10, self.fake_error.y + 7))

            msg = font_b.render("DESTRUA ESTA JANELA!", True, (255, 0, 0))
            surface.blit(msg, (self.fake_error.centerx - msg.get_width() // 2,
                               self.fake_error.centery))

        for p in self.projectiles:
            pygame.draw.rect(surface, (255, 0, 0), p)

        if self.won:
            txt_win = pygame.font.Font(None, 60).render(
                "GLITCH DERROTADO! (ODS 16)", True, (0, 255, 0))
            surface.blit(txt_win, (self.w // 2 - txt_win.get_width() // 2,
                                   self.h // 2 - 30))
            sub_txt = font_b.render("A Paz e Justiça foram restauradas...", True, (255, 255, 255))
            surface.blit(sub_txt, (self.w // 2 - sub_txt.get_width() // 2,
                                   self.h // 2 + 30))
