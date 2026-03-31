import pygame


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
