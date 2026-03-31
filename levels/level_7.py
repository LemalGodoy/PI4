import pygame
import sys
import math
import random

# ===================== INICIALIZAÇÃO =====================
pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fase 7 — ODS 7: Energia Limpa e Acessível")
clock = pygame.time.Clock()
FPS = 60

# ===================== CORES =====================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CAVE_BG = (18, 12, 22)
CAVE_WALL_1 = (40, 30, 35)
CAVE_WALL_2 = (55, 42, 48)
CAVE_ROCK = (70, 55, 60)

HOPE_BODY = (60, 180, 160)
HOPE_VISOR = (180, 240, 255)
HOPE_JETPACK = (80, 80, 100)

FLAME_ORANGE = (255, 160, 40)
FLAME_BLUE = (80, 160, 255)
FLAME_WHITE = (255, 240, 200)

SOLAR_ORB = (255, 220, 60)
SOLAR_GLOW = (255, 200, 40)

BULLET_COLOR = (120, 255, 180)
BULLET_GLOW = (60, 200, 120)

DRONE_COLOR = (130, 130, 140)
ZIGZAG_COLOR = (140, 70, 180)
DIVER_COLOR = (200, 50, 50)
TANK_COLOR = (180, 160, 60)
TANK_BULLET = (220, 180, 40)

CRYSTAL_COLORS = [(100, 200, 255), (180, 100, 255), (100, 255, 180), (255, 180, 100)]

HUD_BG = (0, 0, 0, 140)
ENERGY_BAR_BG = (30, 30, 40)
ENERGY_BAR_FILL = (255, 210, 50)
ENERGY_BAR_LOW = (255, 80, 60)
HEART_COLOR = (255, 60, 80)

VICTORY_COLOR = (100, 255, 160)
DEFEAT_COLOR = (255, 60, 60)

# ===================== FONTES =====================
font_large = pygame.font.SysFont('arial', 70, True)
font_medium = pygame.font.SysFont('arial', 40, True)
font_small = pygame.font.SysFont('arial', 26)
font_tiny = pygame.font.SysFont('arial', 20)

# ===================== PARTÍCULAS =====================
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=20, size=4, gravity=0.0, shrink=True):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.shrink = shrink

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        sz = max(1, int(self.size * ratio)) if self.shrink else self.size
        r = min(255, int(self.color[0] * ratio + 30 * (1 - ratio)))
        g = min(255, int(self.color[1] * ratio))
        b = min(255, int(self.color[2] * ratio))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), sz)


# ===================== HOPE (JOGADOR) =====================
class Hope:
    def __init__(self):
        self.width = 40
        self.height = 55
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 120
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 6
        self.lives = 3
        self.max_lives = 5
        self.hit_timer = 0  # invencibilidade

        # Energia solar
        self.energy = 100.0
        self.max_energy = 100.0
        self.energy_drain = 0.09  # por frame (~2.4%/s)
        self.jetpack_on = True

        # Tiro
        self.shoot_cooldown = 0
        self.shoot_rate = 10  # frames entre tiros

        # Animação
        self.anim_timer = 0
        self.flame_particles = []

    def update(self, keys):
        self.anim_timer += 1

        # Movimento horizontal
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        # Limites — paredes da caverna (margem ~80px cada lado)
        cave_margin = 80
        if self.x < cave_margin:
            self.x = cave_margin
        if self.x + self.width > WIDTH - cave_margin:
            self.x = WIDTH - cave_margin - self.width

        # Movimento vertical (leve, pra desviar)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * 0.6
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * 0.6

        # Limites verticais
        if self.y < HEIGHT * 0.15:
            self.y = HEIGHT * 0.15
        if self.y + self.height > HEIGHT - 30:
            self.y = HEIGHT - 30 - self.height

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Energia solar
        self.energy -= self.energy_drain
        if self.energy <= 0:
            self.energy = 0
            self.jetpack_on = False
            # Sem energia, Hope cai devagar
            self.y += 1.5
        else:
            self.jetpack_on = True

        # Tiro cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Invencibilidade
        if self.hit_timer > 0:
            self.hit_timer -= 1

        # Partículas da chama do jetpack
        if self.jetpack_on:
            for _ in range(2):
                fx = self.x + self.width // 2 + random.uniform(-8, 8)
                fy = self.y + self.height + random.uniform(0, 5)
                color = random.choice([FLAME_ORANGE, FLAME_BLUE, FLAME_WHITE])
                p = Particle(fx, fy, color,
                             vx=random.uniform(-1.5, 1.5),
                             vy=random.uniform(2, 5),
                             life=random.randint(8, 16),
                             size=random.randint(3, 6),
                             gravity=0.1)
                self.flame_particles.append(p)
        else:
            # Fumaça fraca quando sem energia
            if self.anim_timer % 4 == 0:
                fx = self.x + self.width // 2 + random.uniform(-5, 5)
                fy = self.y + self.height
                p = Particle(fx, fy, (80, 80, 80),
                             vx=random.uniform(-0.5, 0.5),
                             vy=random.uniform(1, 3),
                             life=10, size=3, gravity=0.05)
                self.flame_particles.append(p)

        # Atualizar partículas
        for p in self.flame_particles:
            p.update()
        self.flame_particles = [p for p in self.flame_particles if p.life > 0]

    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_rate
            bx = self.x + self.width // 2
            by = self.y - 5
            return Bullet(bx, by)
        return None

    def take_hit(self):
        if self.hit_timer > 0:
            return False
        self.lives -= 1
        self.hit_timer = 90  # 1.5s de invencibilidade
        return True

    def collect_energy(self, amount=25):
        self.energy = min(self.max_energy, self.energy + amount)

    def draw(self, surface):
        # Piscando quando invencível
        if self.hit_timer > 0 and (self.hit_timer // 5) % 2 == 0:
            return  # frame invisível

        # Partículas da chama (atrás)
        for p in self.flame_particles:
            p.draw(surface)

        x, y = int(self.x), int(self.y)

        # Corpo (traje espacial)
        pygame.draw.rect(surface, HOPE_BODY, (x + 5, y + 18, 30, 35), border_radius=4)

        # Cabeça/Capacete
        pygame.draw.ellipse(surface, HOPE_BODY, (x + 6, y, 28, 24))
        # Visor
        pygame.draw.ellipse(surface, HOPE_VISOR, (x + 10, y + 4, 20, 14))
        # Brilho no visor
        pygame.draw.ellipse(surface, (220, 250, 255), (x + 13, y + 6, 6, 4))

        # Jetpack nas costas
        pygame.draw.rect(surface, HOPE_JETPACK, (x + 2, y + 22, 8, 20), border_radius=2)
        pygame.draw.rect(surface, HOPE_JETPACK, (x + 30, y + 22, 8, 20), border_radius=2)

        # Braços
        pygame.draw.rect(surface, HOPE_BODY, (x, y + 22, 7, 16), border_radius=3)
        pygame.draw.rect(surface, HOPE_BODY, (x + 33, y + 22, 7, 16), border_radius=3)

        # Pernas
        pygame.draw.rect(surface, HOPE_BODY, (x + 10, y + 50, 9, 10), border_radius=2)
        pygame.draw.rect(surface, HOPE_BODY, (x + 22, y + 50, 9, 10), border_radius=2)

        # Indicação de energia solar — glow suave ao redor quando energia alta
        if self.energy > 50:
            glow_alpha = int((self.energy / 100) * 40)
            glow_surf = pygame.Surface((60, 75), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 220, 60, glow_alpha), (0, 0, 60, 75))
            surface.blit(glow_surf, (x - 10, y - 10))


# ===================== TIRO DE HOPE =====================
class Bullet:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = -12
        self.width = 6
        self.height = 18
        self.rect = pygame.Rect(int(x) - 3, int(y), self.width, self.height)
        self.alive = True
        self.trail = []

    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)
        self.rect.x = int(self.x) - 3
        if self.y < -20:
            self.alive = False
        # Trail
        self.trail.append((self.x, self.y + 10))
        if len(self.trail) > 6:
            self.trail.pop(0)

    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail)
            sz = max(1, int(3 * alpha))
            c = (int(BULLET_GLOW[0] * alpha), int(BULLET_GLOW[1] * alpha), int(BULLET_GLOW[2] * alpha))
            pygame.draw.circle(surface, c, (int(tx), int(ty)), sz)
        # Projétil principal
        pygame.draw.rect(surface, BULLET_COLOR, (int(self.x) - 3, int(self.y), 6, 18), border_radius=3)
        # Glow
        glow = pygame.Surface((16, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (120, 255, 180, 60), (0, 0, 16, 28))
        surface.blit(glow, (int(self.x) - 8, int(self.y) - 5))


# ===================== TIRO DOS UMANS =====================
class EnemyBullet:
    def __init__(self, x, y, speed=5):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.rect = pygame.Rect(int(x) - 4, int(y), 8, 12)
        self.alive = True

    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)
        self.rect.x = int(self.x) - 4
        if self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surface):
        pygame.draw.rect(surface, TANK_BULLET, (int(self.x) - 4, int(self.y), 8, 12), border_radius=2)
        glow = pygame.Surface((18, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (220, 180, 40, 50), (0, 0, 18, 22))
        surface.blit(glow, (int(self.x) - 9, int(self.y) - 5))


# ===================== ORBE SOLAR =====================
class SolarOrb:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x) - 15, int(y) - 15, 30, 30)
        self.alive = True
        self.timer = random.uniform(0, math.pi * 2)
        self.speed = 1.5  # desce devagar

    def update(self):
        self.y += self.speed
        self.timer += 0.08
        self.rect.x = int(self.x) - 15
        self.rect.y = int(self.y) - 15
        if self.y > HEIGHT + 30:
            self.alive = False

    def draw(self, surface):
        # Glow pulsante
        pulse = math.sin(self.timer) * 0.3 + 0.7
        glow_size = int(28 * pulse)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 60, int(50 * pulse)), (glow_size, glow_size), glow_size)
        surface.blit(glow, (int(self.x) - glow_size, int(self.y) - glow_size))

        # Orbe principal
        pygame.draw.circle(surface, SOLAR_ORB, (int(self.x), int(self.y)), 12)
        pygame.draw.circle(surface, (255, 250, 200), (int(self.x) - 3, int(self.y) - 3), 5)

        # Raios
        for angle_offset in range(0, 360, 45):
            angle = math.radians(angle_offset + self.timer * 30)
            rx = int(self.x + math.cos(angle) * 18 * pulse)
            ry = int(self.y + math.sin(angle) * 18 * pulse)
            pygame.draw.line(surface, (255, 240, 100), (int(self.x), int(self.y)), (rx, ry), 1)


# ===================== UMANS (INIMIGOS) =====================

class UmanDrone:
    """Tipo básico — desce reto"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 58
        self.height = 48
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 3.0
        self.hp = 1
        self.alive = True
        self.score = 10

    def update(self, hope):
        self.y += self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 40:
            self.alive = False
        return None  # sem tiro

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        # Corpo
        pygame.draw.rect(surface, DRONE_COLOR, (x, y + 10, 58, 28), border_radius=6)
        # Asas/Hélice
        wing_off = math.sin(pygame.time.get_ticks() * 0.015) * 6
        pygame.draw.line(surface, (180, 180, 190), (x - 8, y + 16 + wing_off), (x + 12, y + 16), 4)
        pygame.draw.line(surface, (180, 180, 190), (x + 66, y + 16 + wing_off), (x + 46, y + 16), 4)
        # Olho vermelho
        pygame.draw.circle(surface, (255, 50, 50), (x + 29, y + 22), 6)


class UmanZigzag:
    """Desce em S"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.base_x = float(x)
        self.width = 54
        self.height = 54
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 2.5
        self.hp = 1
        self.alive = True
        self.timer = random.uniform(0, math.pi * 2)
        self.amplitude = 100
        self.score = 15

    def update(self, hope):
        self.timer += 0.04
        self.y += self.speed
        self.x = self.base_x + math.sin(self.timer) * self.amplitude
        # Limitar nas paredes
        if self.x < 85:
            self.x = 85
        if self.x + self.width > WIDTH - 85:
            self.x = WIDTH - 85 - self.width
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 40:
            self.alive = False
        return None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        # Corpo triangular
        points = [(x + 27, y), (x, y + 54), (x + 54, y + 54)]
        pygame.draw.polygon(surface, ZIGZAG_COLOR, points)
        pygame.draw.polygon(surface, (180, 100, 220), points, 2)
        # Olhos
        pygame.draw.circle(surface, (255, 200, 255), (x + 18, y + 28), 6)
        pygame.draw.circle(surface, (255, 200, 255), (x + 36, y + 28), 6)
        pygame.draw.circle(surface, (60, 0, 80), (x + 18, y + 28), 3)
        pygame.draw.circle(surface, (60, 0, 80), (x + 36, y + 28), 3)


class UmanDiver:
    """Mergulha em direção a Hope"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 60
        self.height = 60
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 2.0
        self.dive_speed = 6.0
        self.hp = 2
        self.alive = True
        self.phase = "approach"  # approach -> aim -> dive
        self.aim_timer = 0
        self.vx = 0
        self.vy = 0
        self.score = 25

    def update(self, hope):
        if self.phase == "approach":
            self.y += self.speed
            if self.y > HEIGHT * 0.25:
                self.phase = "aim"
                self.aim_timer = 40

        elif self.phase == "aim":
            self.aim_timer -= 1
            # Tremor de mira
            self.x += random.uniform(-2, 2)
            if self.aim_timer <= 0:
                self.phase = "dive"
                # Calcular direção para Hope
                dx = (hope.x + hope.width / 2) - (self.x + self.width / 2)
                dy = (hope.y + hope.height / 2) - (self.y + self.height / 2)
                dist = max(1, math.sqrt(dx * dx + dy * dy))
                self.vx = (dx / dist) * self.dive_speed
                self.vy = (dy / dist) * self.dive_speed

        elif self.phase == "dive":
            self.x += self.vx
            self.y += self.vy

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 50 or self.x < -50 or self.x > WIDTH + 50:
            self.alive = False
        return None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        # Corpo aerodinâmico
        pygame.draw.ellipse(surface, DIVER_COLOR, (x, y, 60, 60))
        pygame.draw.ellipse(surface, (240, 80, 80), (x + 3, y + 3, 54, 54), 2)
        # Olhos furiosos
        pygame.draw.rect(surface, (255, 200, 200), (x + 15, y + 20, 12, 7))
        pygame.draw.rect(surface, (255, 200, 200), (x + 35, y + 20, 12, 7))
        pygame.draw.rect(surface, (80, 0, 0), (x + 18, y + 21, 6, 5))
        pygame.draw.rect(surface, (80, 0, 0), (x + 38, y + 21, 6, 5))
        # Indicador de mira
        if self.phase == "aim":
            pygame.draw.circle(surface, (255, 255, 0, 100), (x + 30, y + 30), 36, 2)


class UmanTank:
    """Blindado — lento, atira projéteis"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 66
        self.height = 66
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        self.speed = 1.5
        self.hp = 3
        self.alive = True
        self.shoot_timer = 0
        self.shoot_rate = 80  # frames
        self.score = 40

    def update(self, hope):
        self.y += self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.y > HEIGHT + 50:
            self.alive = False

        # Atirar
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_rate:
            self.shoot_timer = 0
            return EnemyBullet(self.x + self.width // 2, self.y + self.height)
        return None

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        # Corpo robusto
        pygame.draw.rect(surface, TANK_COLOR, (x + 6, y, 54, 66), border_radius=8)
        # Borda blindada
        pygame.draw.rect(surface, (200, 180, 80), (x + 6, y, 54, 66), 3, border_radius=8)
        # Placa frontal
        pygame.draw.rect(surface, (160, 140, 40), (x + 14, y + 8, 38, 16), border_radius=3)
        # Olho/Sensor
        pygame.draw.circle(surface, (255, 100, 100), (x + 33, y + 36), 9)
        pygame.draw.circle(surface, (255, 200, 200), (x + 33, y + 36), 5)
        # Canhão
        pygame.draw.rect(surface, (120, 100, 30), (x + 28, y + 56, 12, 14))


# ===================== ARMADILHAS (LEVEL DEVIL) =====================

class Stalactite:
    """Pedra que cai do teto sem aviso — Level Devil style"""
    def __init__(self, x):
        self.x = float(x)
        self.y = -60.0
        self.width = 28
        self.height = 55
        self.rect = pygame.Rect(int(x), int(self.y), self.width, self.height)
        self.speed = 0.0
        self.falling = False
        self.warning_timer = 30  # frames de aviso (sutil)
        self.alive = True

    def update(self):
        if self.warning_timer > 0:
            self.warning_timer -= 1
            # Treme antes de cair
            self.x += random.uniform(-2, 2)
            if self.warning_timer <= 0:
                self.falling = True
        
        if self.falling:
            self.speed += 0.5  # aceleração
            self.y += self.speed
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        if self.y > HEIGHT + 60:
            self.alive = False

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        # Forma de stalactite (triângulo pontudo)
        points = [(x + 14, y + 55), (x, y + 10), (x + 6, y), (x + 22, y), (x + 28, y + 10)]
        pygame.draw.polygon(surface, (90, 70, 65), points)
        pygame.draw.polygon(surface, (120, 95, 85), points, 2)
        # Brilho
        pygame.draw.line(surface, (140, 120, 110), (x + 10, y + 5), (x + 14, y + 35), 2)
        
        # Indicador de aviso (linha vermelha tênue no topo)
        if self.warning_timer > 0 and self.warning_timer < 20:
            alpha = int((20 - self.warning_timer) / 20 * 120)
            warn_surf = pygame.Surface((4, HEIGHT), pygame.SRCALPHA)
            warn_surf.fill((255, 50, 50, alpha))
            surface.blit(warn_surf, (x + 12, 0))


class FakeOrb:
    """Parece uma orbe solar mas EXPLODE e drena energia — pura maldade"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(x) - 15, int(y) - 15, 30, 30)
        self.alive = True
        self.timer = random.uniform(0, math.pi * 2)
        self.speed = 1.5
        self.exploded = False

    def update(self):
        if self.exploded:
            return
        self.y += self.speed
        self.timer += 0.08
        self.rect.x = int(self.x) - 15
        self.rect.y = int(self.y) - 15
        if self.y > HEIGHT + 30:
            self.alive = False

    def draw(self, surface):
        if self.exploded:
            return
        # Parece QUASE igual a uma orbe solar, mas com leve diferença
        pulse = math.sin(self.timer) * 0.3 + 0.7
        glow_size = int(28 * pulse)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 200, 60, int(50 * pulse)), (glow_size, glow_size), glow_size)
        surface.blit(glow, (int(self.x) - glow_size, int(self.y) - glow_size))

        # Orbe — cor levemente diferente (mais esverdeada, quase imperceptível)
        pygame.draw.circle(surface, (240, 220, 50), (int(self.x), int(self.y)), 12)
        pygame.draw.circle(surface, (255, 250, 180), (int(self.x) - 3, int(self.y) - 3), 5)

        # Raios (igual)
        for angle_offset in range(0, 360, 45):
            angle = math.radians(angle_offset + self.timer * 30)
            rx = int(self.x + math.cos(angle) * 18 * pulse)
            ry = int(self.y + math.sin(angle) * 18 * pulse)
            pygame.draw.line(surface, (255, 230, 90), (int(self.x), int(self.y)), (rx, ry), 1)


class GlitchText:
    """Texto de alerta do Glitch que aparece na tela"""
    def __init__(self, text, duration=90):
        self.text = text
        self.duration = duration
        self.max_duration = duration
        self.alive = True

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        ratio = self.duration / self.max_duration
        # Aparece com efeito glitch
        alpha = int(200 * ratio)
        
        # Renderizar com offset aleatório para efeito glitch
        ox = random.randint(-3, 3) if ratio > 0.3 else 0
        oy = random.randint(-2, 2) if ratio > 0.3 else 0
        
        text_surf = font_medium.render(self.text, True, (255, 50, 50))
        # Sombra/duplicata glitch
        shadow = font_medium.render(self.text, True, (0, 255, 255))
        
        cx = WIDTH // 2 - text_surf.get_width() // 2
        cy = HEIGHT // 2 - 50
        
        surface.blit(shadow, (cx + random.randint(-5, 5), cy + random.randint(-3, 3)))
        surface.blit(text_surf, (cx + ox, cy + oy))


class TrapSystem:
    """Sistema de armadilhas estilo Level Devil — surpresas em altitudes específicas"""
    def __init__(self):
        # Armadilhas programadas por altitude (em metros)
        # Cada trap é ativada UMA vez
        self.traps_triggered = set()
        self.active_stalactites = []
        self.active_fake_orbs = []
        self.glitch_texts = []
        
        # Estado de squeeze (paredes fechando)
        self.squeeze_active = False
        self.squeeze_timer = 0
        self.squeeze_amount = 0.0  # 0 = normal, 1 = máximo
        self.squeeze_target = 0.0
        
        # Inversão de controles
        self.invert_controls = False
        self.invert_timer = 0
        
        # Apagão
        self.blackout_active = False
        self.blackout_timer = 0
        self.blackout_alpha = 0

    def check_traps(self, altitude_m, hope, particles, shake):
        """Verifica e ativa armadilhas conforme altitude"""
        
        # ====== 40m — Primeira stalactite (susto inicial) ======
        if altitude_m >= 40 and 'stalk_60' not in self.traps_triggered:
            self.traps_triggered.add('stalk_60')
            # Cai exatamente onde Hope está!
            self.active_stalactites.append(Stalactite(hope.x + hope.width // 2 - 14))
            self.glitch_texts.append(GlitchText("CUIDADO!", 50))

        # ====== 75m — Fake orb ======
        if altitude_m >= 75 and 'fake_120' not in self.traps_triggered:
            self.traps_triggered.add('fake_120')
            self.active_fake_orbs.append(FakeOrb(WIDTH // 2, -20))

        # ====== 110m — 3 stalactites em sequência ======
        if altitude_m >= 110 and 'stalk_180' not in self.traps_triggered:
            self.traps_triggered.add('stalk_180')
            for i in range(3):
                s = Stalactite(random.randint(100, WIDTH - 130))
                s.warning_timer = 20 + i * 15  # em sequência
                self.active_stalactites.append(s)

        # ====== 140m — Paredes fechando! ======
        if altitude_m >= 140 and 'squeeze_220' not in self.traps_triggered:
            self.traps_triggered.add('squeeze_220')
            self.squeeze_active = True
            self.squeeze_timer = 240  # 4 segundos
            self.squeeze_target = 0.6
            self.glitch_texts.append(GlitchText("GLITCH: COMPRIMINDO...", 70))

        # ====== 175m — Inversão de controles ======
        if altitude_m >= 175 and 'invert_280' not in self.traps_triggered:
            self.traps_triggered.add('invert_280')
            self.invert_controls = True
            self.invert_timer = 240  # 4 segundos
            self.glitch_texts.append(GlitchText("CONTROLES INVERTIDOS!", 80))
            shake.trigger(15, 4)

        # ====== 210m — Chuva de stalactites ======
        if altitude_m >= 210 and 'stalk_330' not in self.traps_triggered:
            self.traps_triggered.add('stalk_330')
            for i in range(5):
                s = Stalactite(100 + i * 150)
                s.warning_timer = 10 + i * 8
                self.active_stalactites.append(s)
            self.glitch_texts.append(GlitchText("DESMORONAMENTO!", 60))

        # ====== 235m — Fake orb + apagão ======
        if altitude_m >= 235 and 'blackout_370' not in self.traps_triggered:
            self.traps_triggered.add('blackout_370')
            self.blackout_active = True
            self.blackout_timer = 150  # 2.5 segundos
            self.active_fake_orbs.append(FakeOrb(hope.x + 60, -20))
            self.glitch_texts.append(GlitchText("GLITCH: ESCURIDÃO", 60))

        # ====== 260m — Squeeze + stalactites combo ======
        if altitude_m >= 260 and 'combo_410' not in self.traps_triggered:
            self.traps_triggered.add('combo_410')
            self.squeeze_active = True
            self.squeeze_timer = 180
            self.squeeze_target = 0.5
            for i in range(3):
                s = Stalactite(200 + i * 200)
                s.warning_timer = 30 + i * 20
                self.active_stalactites.append(s)

        # ====== 280m — Inversão + stalactites finais ======
        if altitude_m >= 280 and 'final_460' not in self.traps_triggered:
            self.traps_triggered.add('final_460')
            self.invert_controls = True
            self.invert_timer = 180
            for i in range(4):
                s = Stalactite(hope.x + random.randint(-100, 100))
                s.warning_timer = 15 + i * 12
                self.active_stalactites.append(s)
            self.glitch_texts.append(GlitchText("GLITCH: CAOS TOTAL!", 90))
            shake.trigger(20, 6)

    def update(self, hope, particles, shake):
        """Atualiza todos os efeitos ativos"""
        
        # Stalactites
        for s in self.active_stalactites:
            s.update()
            # Colisão com Hope
            if s.falling and s.alive and hope.hit_timer <= 0 and s.rect.colliderect(hope.rect):
                if hope.take_hit():
                    shake.trigger(15, 8)
                    s.alive = False
                    for _ in range(12):
                        particles.append(Particle(
                            s.x + s.width // 2, s.y + s.height // 2,
                            (120, 100, 80),
                            vx=random.uniform(-5, 5),
                            vy=random.uniform(-3, 5),
                            life=20, size=5, gravity=0.2
                        ))
        self.active_stalactites = [s for s in self.active_stalactites if s.alive]

        # Fake orbs
        for fo in self.active_fake_orbs:
            fo.update()
            if not fo.exploded and fo.alive and fo.rect.colliderect(hope.rect):
                fo.exploded = True
                fo.alive = False
                # DRENA energia em vez de dar!
                hope.energy = max(0, hope.energy - 35)
                shake.trigger(20, 8)
                self.glitch_texts.append(GlitchText("HAHA! FALSA!", 50))
                # Explosão vermelha
                for _ in range(20):
                    particles.append(Particle(
                        fo.x, fo.y,
                        random.choice([(255, 50, 50), (255, 100, 0), (200, 0, 0)]),
                        vx=random.uniform(-7, 7),
                        vy=random.uniform(-7, 7),
                        life=25, size=6, gravity=0.1
                    ))
        self.active_fake_orbs = [fo for fo in self.active_fake_orbs if fo.alive]

        # Squeeze (paredes fechando)
        if self.squeeze_active:
            self.squeeze_timer -= 1
            if self.squeeze_timer > 60:
                # Fechando
                self.squeeze_amount += (self.squeeze_target - self.squeeze_amount) * 0.05
            else:
                # Abrindo de volta
                self.squeeze_amount *= 0.95
            
            if self.squeeze_timer <= 0:
                self.squeeze_active = False
                self.squeeze_amount = 0.0

        # Inversão de controles
        if self.invert_controls:
            self.invert_timer -= 1
            if self.invert_timer <= 0:
                self.invert_controls = False

        # Apagão
        if self.blackout_active:
            self.blackout_timer -= 1
            if self.blackout_timer > 120:
                self.blackout_alpha = min(200, self.blackout_alpha + 8)
            elif self.blackout_timer < 30:
                self.blackout_alpha = max(0, self.blackout_alpha - 8)
            if self.blackout_timer <= 0:
                self.blackout_active = False
                self.blackout_alpha = 0

        # Glitch texts
        for gt in self.glitch_texts:
            gt.update()
        self.glitch_texts = [gt for gt in self.glitch_texts if gt.alive]

    def get_squeeze_margin(self):
        """Retorna margem extra das paredes (usada para limitar Hope)"""
        return int(self.squeeze_amount * 120)  # até 120px extra de cada lado

    def draw(self, surface):
        # Stalactites
        for s in self.active_stalactites:
            s.draw(surface)

        # Fake orbs
        for fo in self.active_fake_orbs:
            fo.draw(surface)

        # Squeeze — paredes extras
        if self.squeeze_amount > 0.01:
            extra = self.get_squeeze_margin()
            # Parede esquerda extra
            squeeze_surf = pygame.Surface((extra, HEIGHT), pygame.SRCALPHA)
            squeeze_surf.fill((60, 45, 50, 200))
            surface.blit(squeeze_surf, (80, 0))
            # Parede direita extra
            surface.blit(squeeze_surf, (WIDTH - 80 - extra, 0))
            # Bordas com espinhos/rochas
            for i in range(0, HEIGHT, 40):
                pygame.draw.circle(surface, (80, 60, 55), (80 + extra, i + 20), 6)
                pygame.draw.circle(surface, (80, 60, 55), (WIDTH - 80 - extra, i + 20), 6)

        # Apagão
        if self.blackout_alpha > 0:
            dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, self.blackout_alpha))
            surface.blit(dark, (0, 0))

        # Glitch texts
        for gt in self.glitch_texts:
            gt.draw(surface)

        # Indicador de controle invertido
        if self.invert_controls:
            blink = (pygame.time.get_ticks() // 200) % 2 == 0
            if blink:
                inv_text = font_tiny.render("⚠ CONTROLES INVERTIDOS ⚠", True, (255, 80, 80))
                surface.blit(inv_text, (WIDTH // 2 - inv_text.get_width() // 2, HEIGHT - 40))


# ===================== CRISTAL DECORATIVO =====================
class Crystal:
    def __init__(self, x, y, side):
        self.x = x
        self.y = y  # posição relativa ao scroll  
        self.side = side  # 'left' ou 'right'
        self.color = random.choice(CRYSTAL_COLORS)
        self.size = random.randint(8, 18)
        self.glow_timer = random.uniform(0, math.pi * 2)

    def draw(self, surface, screen_y):
        sy = int(screen_y)
        if sy < -30 or sy > HEIGHT + 30:
            return
        self.glow_timer += 0.03
        pulse = math.sin(self.glow_timer) * 0.3 + 0.7

        # Glow
        glow_size = int(self.size * 1.8 * pulse)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, int(35 * pulse)), (glow_size, glow_size), glow_size)
        surface.blit(glow, (self.x - glow_size, sy - glow_size))

        # Cristal (losango)
        cx, cy = self.x, sy
        s = self.size
        points = [(cx, cy - s), (cx + s // 2, cy), (cx, cy + s // 2), (cx - s // 2, cy)]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, WHITE, points, 1)


# ===================== CENÁRIO DA CAVERNA =====================
class CaveBackground:
    def __init__(self):
        self.crystals = []
        self.speed_lines = []
        # Gerar cristais ao longo de toda a caverna (500m = 7500px internos)
        total_height = 8000
        for i in range(120):
            y = random.randint(0, total_height)
            side = random.choice(['left', 'right'])
            if side == 'left':
                x = random.randint(10, 70)
            else:
                x = random.randint(WIDTH - 70, WIDTH - 10)
            self.crystals.append(Crystal(x, y, side))

    def draw(self, surface, altitude_pixels, progress_ratio):
        # Cor de fundo escurece/clareia conforme sobe
        # Mais escuro embaixo, mais claro perto do topo
        r = int(18 + progress_ratio * 25)
        g = int(12 + progress_ratio * 20)
        b = int(22 + progress_ratio * 35)
        surface.fill((r, g, b))

        # Paredes da caverna — camada traseira (parallax lento)
        wall_offset_1 = altitude_pixels * 0.2
        for i in range(-1, HEIGHT // 60 + 2):
            y = i * 60 + (wall_offset_1 % 60)
            # Esquerda
            w = 65 + int(math.sin(y * 0.02 + 1) * 20)
            pygame.draw.rect(surface, CAVE_WALL_1, (0, y, w, 62))
            # Direita
            w2 = 65 + int(math.sin(y * 0.025 + 3) * 20)
            pygame.draw.rect(surface, CAVE_WALL_1, (WIDTH - w2, y, w2, 62))

        # Paredes — camada frontal (parallax rápido)
        wall_offset_2 = altitude_pixels * 0.5
        for i in range(-1, HEIGHT // 50 + 2):
            y = i * 50 + (wall_offset_2 % 50)
            # Esquerda
            w = 50 + int(math.sin(y * 0.03 + 2) * 18)
            pygame.draw.rect(surface, CAVE_WALL_2, (0, y, w, 52))
            # Rochas decorativas
            if i % 3 == 0:
                pygame.draw.circle(surface, CAVE_ROCK, (w - 5, int(y + 25)), 8)
            # Direita
            w2 = 50 + int(math.sin(y * 0.028 + 5) * 18)
            pygame.draw.rect(surface, CAVE_WALL_2, (WIDTH - w2, y, w2, 52))
            if i % 3 == 1:
                pygame.draw.circle(surface, CAVE_ROCK, (WIDTH - w2 + 5, int(y + 25)), 8)

        # Cristais
        for crystal in self.crystals:
            screen_y = crystal.y - altitude_pixels * 0.4
            # Loop para visibilidade contínua
            screen_y_mod = screen_y % 2000 - 200
            crystal.draw(surface, screen_y_mod)

        # Linhas de velocidade (estrias)
        if len(self.speed_lines) < 8:
            self.speed_lines.append({
                'x': random.randint(90, WIDTH - 90),
                'y': random.randint(-50, -10),
                'speed': random.uniform(8, 16),
                'length': random.randint(20, 60),
                'alpha': random.randint(30, 80)
            })

        for line in self.speed_lines:
            line['y'] += line['speed']
            a = min(255, line['alpha'])
            pygame.draw.line(surface, (200, 200, 220), 
                             (line['x'], int(line['y'])),
                             (line['x'], int(line['y'] + line['length'])), 1)

        self.speed_lines = [l for l in self.speed_lines if l['y'] < HEIGHT + 70]

        # Luz do topo nos últimos 30m (progress > 0.9)
        if progress_ratio > 0.9:
            light_intensity = (progress_ratio - 0.9) / 0.1  # 0 a 1
            light_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            # Gradiente de luz vindo de cima
            for ly in range(min(300, int(300 * light_intensity))):
                alpha = int((1 - ly / 300) * 60 * light_intensity)
                pygame.draw.rect(light_surf, (255, 250, 200, alpha), (0, ly, WIDTH, 2))
            surface.blit(light_surf, (0, 0))


# ===================== SCREEN SHAKE =====================
class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, duration=10, intensity=5):
        self.duration = duration
        self.intensity = intensity

    def update(self):
        if self.duration > 0:
            self.duration -= 1
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0


# ===================== WAVE SPAWNER =====================
class WaveSpawner:
    def __init__(self):
        self.timer = 0
        self.wave_num = 0
        self.cave_margin = 80

    def get_random_x(self):
        return random.randint(self.cave_margin + 10, WIDTH - self.cave_margin - 50)

    def update(self, altitude_m, enemies):
        self.timer += 1

        # Spawn baseado na altitude (progressão) — menos inimigos, maiores
        if altitude_m < 80:
            # Setor 1: Só drones, spawn lento
            if self.timer % 90 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 200 == 0:
                # Spawn de par
                x1 = self.get_random_x()
                enemies.append(UmanDrone(x1, -50))
                enemies.append(UmanDrone(x1 + 100, -80))

        elif altitude_m < 160:
            # Setor 2: Drones + Zigzags
            if self.timer % 75 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 120 == 0:
                enemies.append(UmanZigzag(self.get_random_x(), -55))
            if self.timer % 250 == 0:
                # Wave de 2 drones
                base_x = self.get_random_x()
                for i in range(2):
                    enemies.append(UmanDrone(base_x + i * 80, -50 - i * 40))

        elif altitude_m < 240:
            # Setor 3: + Mergulhadores
            if self.timer % 65 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 100 == 0:
                enemies.append(UmanZigzag(self.get_random_x(), -55))
            if self.timer % 150 == 0:
                enemies.append(UmanDiver(self.get_random_x(), -65))
            if self.timer % 220 == 0:
                # Wave mista
                enemies.append(UmanDrone(self.get_random_x(), -50))
                enemies.append(UmanZigzag(self.get_random_x(), -80))

        else:
            # Setor 4: TUDO + Blindados
            if self.timer % 55 == 0:
                enemies.append(UmanDrone(self.get_random_x(), -50))
            if self.timer % 90 == 0:
                enemies.append(UmanZigzag(self.get_random_x(), -55))
            if self.timer % 120 == 0:
                enemies.append(UmanDiver(self.get_random_x(), -65))
            if self.timer % 170 == 0:
                enemies.append(UmanTank(self.get_random_x(), -70))


# ===================== HUD =====================
def draw_hud(surface, hope, altitude_m):
    # Fundo semi-transparente do HUD
    hud_surf = pygame.Surface((WIDTH, 45), pygame.SRCALPHA)
    hud_surf.fill((0, 0, 0, 120))
    surface.blit(hud_surf, (0, 0))

    # Barra de energia solar
    bar_x, bar_y = 15, 12
    bar_w, bar_h = 180, 20

    pygame.draw.rect(surface, ENERGY_BAR_BG, (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), border_radius=4)
    fill_ratio = hope.energy / hope.max_energy
    fill_color = ENERGY_BAR_FILL if fill_ratio > 0.25 else ENERGY_BAR_LOW
    pygame.draw.rect(surface, fill_color, (bar_x, bar_y, int(bar_w * fill_ratio), bar_h), border_radius=3)

    # Ícone de sol
    pygame.draw.circle(surface, SOLAR_ORB, (bar_x + bar_w + 18, bar_y + 10), 8)
    energy_text = font_tiny.render(f"{int(hope.energy)}%", True, WHITE)
    surface.blit(energy_text, (bar_x + bar_w + 32, bar_y))

    # Altitude
    alt_text = font_small.render(f"{int(altitude_m)}m / 300m", True, WHITE)
    surface.blit(alt_text, (WIDTH // 2 - alt_text.get_width() // 2, 10))

    # Vidas (corações)
    for i in range(hope.lives):
        hx = WIDTH - 45 - i * 35
        hy = 12
        pygame.draw.circle(surface, HEART_COLOR, (hx, hy + 5), 7)
        pygame.draw.circle(surface, HEART_COLOR, (hx + 10, hy + 5), 7)
        pygame.draw.polygon(surface, HEART_COLOR, [(hx - 6, hy + 8), (hx + 5, hy + 20), (hx + 16, hy + 8)])


# ===================== TELAS =====================
def draw_victory_screen(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # Luz do topo
    for ly in range(HEIGHT):
        alpha = int((1 - ly / HEIGHT) * 50)
        pygame.draw.rect(overlay, (255, 250, 200, alpha), (0, ly, WIDTH, 2))
    surface.blit(overlay, (0, 0))

    title = font_large.render("HOPE ESCAPOU!", True, VICTORY_COLOR)
    sub = font_small.render("A energia solar iluminou o caminho.", True, (200, 255, 220))
    ods = font_small.render("ODS 7 — Energia Limpa e Acessível", True, SOLAR_ORB)
    restart = font_tiny.render("Pressione R para jogar novamente", True, WHITE)

    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 30))
    surface.blit(ods, (WIDTH // 2 - ods.get_width() // 2, HEIGHT // 2 + 20))
    surface.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 80))


def draw_defeat_screen(surface, altitude_m):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    title = font_large.render("HOPE CAIU...", True, DEFEAT_COLOR)
    sub = font_small.render(f"Altitude alcançada: {int(altitude_m)}m", True, WHITE)
    restart = font_tiny.render("Pressione R para tentar novamente", True, WHITE)

    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))
    surface.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 70))


def draw_start_screen(surface, anim_timer):
    surface.fill(CAVE_BG)

    # Paredes decorativas
    for i in range(HEIGHT // 50 + 1):
        y = i * 50
        w1 = 50 + int(math.sin(y * 0.03) * 15)
        w2 = 50 + int(math.sin(y * 0.025 + 3) * 15)
        pygame.draw.rect(surface, CAVE_WALL_2, (0, y, w1, 52))
        pygame.draw.rect(surface, CAVE_WALL_2, (WIDTH - w2, y, w2, 52))

    # Título
    pulse = math.sin(anim_timer * 0.05) * 0.15 + 1.0
    title = font_large.render("FASE 7", True, SOLAR_ORB)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    sub = font_medium.render("ODS 7 — Energia Limpa", True, HOPE_VISOR)
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 210))

    # Instruções
    instructions = [
        "← → ou A/D — Mover",
        "↑ ↓ ou W/S — Subir/Descer",
        "SPACE ou E — Atirar",
        "",
        "Colete orbes solares para recarregar o jetpack!",
        "Fuja da caverna subindo 300m!"
    ]
    for i, line in enumerate(instructions):
        color = (180, 220, 200) if line else WHITE
        text = font_tiny.render(line, True, color)
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 320 + i * 32))

    # Prompt
    blink = (anim_timer // 30) % 2 == 0
    if blink:
        start_text = font_small.render("Pressione ENTER para começar", True, WHITE)
        surface.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 560))

    # Hope desenhada na tela inicial
    hope_x = WIDTH // 2 - 20
    hope_y = 440 + int(math.sin(anim_timer * 0.04) * 8)
    pygame.draw.rect(surface, HOPE_BODY, (hope_x + 5, hope_y + 18, 30, 35), border_radius=4)
    pygame.draw.ellipse(surface, HOPE_BODY, (hope_x + 6, hope_y, 28, 24))
    pygame.draw.ellipse(surface, HOPE_VISOR, (hope_x + 10, hope_y + 4, 20, 14))

    # Chama animada
    for _ in range(3):
        fx = hope_x + 20 + random.randint(-6, 6)
        fy = hope_y + 55 + random.randint(0, 10)
        color = random.choice([FLAME_ORANGE, FLAME_BLUE])
        pygame.draw.circle(surface, color, (fx, fy), random.randint(3, 6))


# ===================== GAME LOOP =====================
def main():
    state = "START"  # START, PLAYING, VICTORY, DEFEAT
    anim_timer = 0

    # Variáveis do jogo (inicializadas no START → PLAYING)
    hope = None
    bullets = []
    enemies = []
    enemy_bullets = []
    orbs = []
    particles = []
    spawner = None
    cave_bg = None
    shake = None
    altitude_px = 0.0
    altitude_speed = 2.0  # pixels/frame base
    orb_timer = 0
    trap_system = None

    def start_game():
        nonlocal hope, bullets, enemies, enemy_bullets, orbs, particles
        nonlocal spawner, cave_bg, shake, altitude_px, orb_timer, trap_system
        hope = Hope()
        bullets = []
        enemies = []
        enemy_bullets = []
        orbs = []
        particles = []
        spawner = WaveSpawner()
        cave_bg = CaveBackground()
        shake = ScreenShake()
        trap_system = TrapSystem()
        altitude_px = 0.0
        orb_timer = 0

    running = True
    while running:
        # ---- EVENTOS ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "START":
                    if event.key == pygame.K_RETURN:
                        start_game()
                        state = "PLAYING"

                elif state == "PLAYING":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        b = hope.shoot()
                        if b:
                            bullets.append(b)

                elif state in ("VICTORY", "DEFEAT"):
                    if event.key == pygame.K_r:
                        start_game()
                        state = "PLAYING"

        anim_timer += 1

        # ---- START SCREEN ----
        if state == "START":
            draw_start_screen(screen, anim_timer)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ---- PLAYING ----
        if state == "PLAYING":
            keys = pygame.key.get_pressed()

            # Tiro contínuo segurando SPACE/E
            if keys[pygame.K_SPACE] or keys[pygame.K_e]:
                b = hope.shoot()
                if b:
                    bullets.append(b)

            # Aplicar inversão de controles (Level Devil!)
            if trap_system and trap_system.invert_controls:
                # Cria um mapeamento invertido
                class FakeKeys:
                    def __init__(self, real_keys):
                        self._real = real_keys
                    def __getitem__(self, key):
                        if key == pygame.K_LEFT:
                            return self._real[pygame.K_RIGHT]
                        elif key == pygame.K_RIGHT:
                            return self._real[pygame.K_LEFT]
                        elif key == pygame.K_UP or key == pygame.K_w:
                            return self._real[pygame.K_DOWN] or self._real[pygame.K_s]
                        elif key == pygame.K_DOWN or key == pygame.K_s:
                            return self._real[pygame.K_UP] or self._real[pygame.K_w]
                        elif key == pygame.K_a:
                            return self._real[pygame.K_d]
                        elif key == pygame.K_d:
                            return self._real[pygame.K_a]
                        return self._real[key]
                keys = FakeKeys(keys)

            hope.update(keys)

            # Aplicar squeeze nas margens da Hope
            if trap_system and trap_system.squeeze_amount > 0.01:
                extra_margin = trap_system.get_squeeze_margin()
                total_margin = 80 + extra_margin
                if hope.x < total_margin:
                    hope.x = total_margin
                if hope.x + hope.width > WIDTH - total_margin:
                    hope.x = WIDTH - total_margin - hope.width
                hope.rect.x = int(hope.x)

            # Progredir altitude
            altitude_px += altitude_speed
            altitude_m = altitude_px / 15.0  # 15px = 1m
            progress_ratio = min(1.0, altitude_m / 300.0)

            # Spawner
            spawner.update(altitude_m, enemies)

            # Orbe solar a cada ~4 segundos
            orb_timer += 1
            orb_interval = 190 if altitude_m < 200 else 200 if altitude_m < 400 else 260
            if orb_timer >= orb_interval:
                orb_timer = 0
                ox = random.randint(100, WIDTH - 100)
                orbs.append(SolarOrb(ox, -30))

            # Sistema de armadilhas Level Devil
            trap_system.check_traps(altitude_m, hope, particles, shake)
            trap_system.update(hope, particles, shake)

            # Atualizar balas
            for b in bullets:
                b.update()
            bullets = [b for b in bullets if b.alive]

            # Atualizar inimigos
            for e in enemies:
                result = e.update(hope)
                if result and isinstance(result, EnemyBullet):
                    enemy_bullets.append(result)
            enemies = [e for e in enemies if e.alive]

            # Atualizar balas inimigas
            for eb in enemy_bullets:
                eb.update()
            enemy_bullets = [eb for eb in enemy_bullets if eb.alive]

            # Atualizar orbes
            for orb in orbs:
                orb.update()
            orbs = [o for o in orbs if o.alive]

            # ---- COLISÕES ----

            # Balas de Hope → Inimigos
            for b in list(bullets):
                if not b.alive:
                    continue
                for e in enemies:
                    if not e.alive:
                        continue
                    if b.rect.colliderect(e.rect):
                        e.hp -= 1
                        b.alive = False
                        # Partículas de hit
                        for _ in range(6):
                            particles.append(Particle(
                                e.x + e.width // 2, e.y + e.height // 2,
                                (255, 200, 100),
                                vx=random.uniform(-4, 4),
                                vy=random.uniform(-4, 4),
                                life=15, size=4
                            ))
                        if e.hp <= 0:
                            e.alive = False
                            shake.trigger(6, 3)
                            # Explosão
                            for _ in range(15):
                                particles.append(Particle(
                                    e.x + e.width // 2, e.y + e.height // 2,
                                    random.choice([(255, 160, 40), (255, 100, 30), (255, 220, 80)]),
                                    vx=random.uniform(-6, 6),
                                    vy=random.uniform(-6, 6),
                                    life=random.randint(15, 30),
                                    size=random.randint(3, 7),
                                    gravity=0.15
                                ))
                        break

            # Inimigos → Hope
            for e in enemies:
                if e.alive and hope.hit_timer <= 0 and e.rect.colliderect(hope.rect):
                    if hope.take_hit():
                        shake.trigger(12, 6)
                        for _ in range(10):
                            particles.append(Particle(
                                hope.x + hope.width // 2, hope.y + hope.height // 2,
                                (255, 80, 80),
                                vx=random.uniform(-5, 5),
                                vy=random.uniform(-5, 5),
                                life=20, size=5
                            ))
                        if hope.lives <= 0:
                            state = "DEFEAT"

            # Balas inimigas → Hope
            for eb in list(enemy_bullets):
                if eb.alive and hope.hit_timer <= 0 and eb.rect.colliderect(hope.rect):
                    eb.alive = False
                    if hope.take_hit():
                        shake.trigger(10, 5)
                        if hope.lives <= 0:
                            state = "DEFEAT"

            # Orbes → Hope
            for orb in orbs:
                if orb.alive and orb.rect.colliderect(hope.rect):
                    orb.alive = False
                    hope.collect_energy(25)
                    # Partículas de coleta
                    for _ in range(12):
                        particles.append(Particle(
                            orb.x, orb.y,
                            (255, 230, 80),
                            vx=random.uniform(-5, 5),
                            vy=random.uniform(-5, 5),
                            life=20, size=4, gravity=-0.1
                        ))

            # Game over se cair muito (sem energia e saiu da tela)
            if hope.y + hope.height > HEIGHT + 10:
                state = "DEFEAT"

            # Vitória!
            if altitude_m >= 300:
                state = "VICTORY"

            # Checar se Hope morreu por armadilha
            if hope.lives <= 0:
                state = "DEFEAT"

            # Shake
            shake.update()

            # Partículas
            for p in particles:
                p.update()
            particles = [p for p in particles if p.life > 0]

        # ---- RENDERING ----
        render_surface = pygame.Surface((WIDTH, HEIGHT))

        if state in ("PLAYING", "VICTORY", "DEFEAT"):
            altitude_m = altitude_px / 15.0
            progress_ratio = min(1.0, altitude_m / 300.0)

            cave_bg.draw(render_surface, altitude_px, progress_ratio)

            # Orbes
            for orb in orbs:
                if orb.alive:
                    orb.draw(render_surface)

            # Balas inimigas
            for eb in enemy_bullets:
                if eb.alive:
                    eb.draw(render_surface)

            # Inimigos
            for e in enemies:
                if e.alive:
                    e.draw(render_surface)

            # Balas de Hope
            for b in bullets:
                if b.alive:
                    b.draw(render_surface)

            # Partículas
            for p in particles:
                p.draw(render_surface)

            # Armadilhas (Level Devil)
            if trap_system:
                trap_system.draw(render_surface)

            # Hope
            hope.draw(render_surface)

            # HUD
            draw_hud(render_surface, hope, altitude_m)

            # Telas de fim
            if state == "VICTORY":
                draw_victory_screen(render_surface)
            elif state == "DEFEAT":
                draw_defeat_screen(render_surface, altitude_m)

        # Aplicar shake
        if state in ("PLAYING",) and shake and shake.duration > 0:
            screen.fill(BLACK)
            screen.blit(render_surface, (shake.offset_x, shake.offset_y))
        else:
            screen.blit(render_surface, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
