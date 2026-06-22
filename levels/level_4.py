import math
import pygame
import random
import sys
from entities import Player as SpritePlayer

# === CONSTANTS.PY ===
# Screen
WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Level 4 — ODS 7"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (12, 12, 30)
CAVE_DARK = (20, 18, 35)
CAVE_WALL = (45, 40, 60)
CAVE_ACCENT = (65, 55, 80)

# Player colors
HOPE_BODY = (0, 160, 160)
HOPE_HELMET = (0, 220, 220)
HOPE_VISOR = (100, 255, 255)
HOPE_SKIN = (210, 180, 140)
JETPACK_GRAY = (80, 80, 100)

# Solar / Energy colors
SOLAR_GOLD = (255, 215, 0)
SOLAR_ORANGE = (255, 165, 0)
SOLAR_BRIGHT = (255, 255, 100)
ENERGY_CYAN = (0, 230, 255)
ENERGY_BEAM = (150, 255, 255)

# Enemy colors
UMAN_DARK = (60, 20, 80)
UMAN_RED = (200, 30, 30)
UMAN_TOXIC = (100, 255, 50)
UMAN_PURPLE = (120, 40, 160)
UMAN_ELITE = (180, 0, 0)
BOSS_COLOR = (100, 0, 130)
BOSS_ACCENT = (200, 0, 50)

# Trap colors
TRAP_WARNING = (255, 50, 50)
TOXIC_GREEN = (50, 200, 30)
FAKE_ORB = (200, 200, 0)

# Destroyed world
RUIN_GRAY = (60, 55, 50)
RUIN_ORANGE = (180, 80, 20)
SKY_DARK = (30, 20, 40)
FIRE_COLOR = (255, 100, 20)

# Game settings
PLAYER_SPEED = 5
PLAYER_MAX_HP = 5
PLAYER_MAX_ENERGY = 100
ENERGY_DRAIN_RATE = 0.08
ENERGY_ORB_VALUE = 30
SHOOT_COOLDOWN = 10
BULLET_SPEED = 8
INVINCIBLE_FRAMES = 60

# Enemy settings
ENEMY_CONFIGS = {
    "drone": {
        "hp": 1, "speed": 2, "score": 100,
        "shoot_rate": 90, "size": (24, 24),
        "color": UMAN_DARK, "accent": UMAN_RED
    },
    "bomber": {
        "hp": 2, "speed": 1.5, "score": 200,
        "shoot_rate": 120, "size": (32, 28),
        "color": UMAN_PURPLE, "accent": UMAN_TOXIC
    },
    "elite": {
        "hp": 3, "speed": 3.5, "score": 350,
        "shoot_rate": 45, "size": (28, 28),
        "color": UMAN_ELITE, "accent": (255, 100, 0)
    }
}

BOSS_HP = 60
BOSS_SIZE = (90, 70)
BOSS_SPEED = 2

# Wave definitions: list of (enemy_type, count, delay_between_spawns)
WAVES = [
    # Wave 1 - easy
    [("drone", 5, 55), ("bomber", 1, 80)],
    # Wave 2 - medium
    [("drone", 4, 45), ("bomber", 2, 60), ("elite", 1, 80)],
    # Wave 3 - hard
    [("drone", 4, 35), ("bomber", 3, 50), ("elite", 3, 55)],
    # Wave 4 - BOSS
    [("boss", 1, 0)],
]

# Max solar orbs on screen at once
MAX_SOLAR_ORBS = 3

# Trap types
TRAP_INVERSION = "inversion"
TRAP_FALLING = "falling"
TRAP_FAKE_ORB = "fake_orb"
TRAP_TOXIC_ZONE = "toxic_zone"
TRAP_SCREEN_GLITCH = "glitch"

# Cutscene
FONT_NAME = None  # Use default pygame font
CUTSCENE_SPEED = 2  # text chars per frame

# === PARTICLES.PY ===
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=30, size=3, gravity=0, shrink=True, glow=False):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.shrink = shrink
        self.glow = glow

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = self.life / self.max_life
        cur_size = max(1, int(self.size * alpha)) if self.shrink else self.size
        r = min(255, int(self.color[0] * alpha + 50 * (1 - alpha)))
        g = min(255, int(self.color[1] * alpha))
        b = min(255, int(self.color[2] * alpha))
        if self.glow and cur_size > 2:
            glow_surf = pygame.Surface((cur_size * 4, cur_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (r, g, b, int(40 * alpha)), (cur_size * 2, cur_size * 2), cur_size * 2)
            surface.blit(glow_surf, (int(self.x - cur_size * 2), int(self.y - cur_size * 2)))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), cur_size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add(self, particle):
        self.particles.append(particle)

    def emit_burst(self, x, y, color, count=10, speed=3, life=20, size=3, gravity=0, glow=False):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(0.5, speed)
            self.particles.append(Particle(
                x, y, color,
                vx=math.cos(angle) * spd,
                vy=math.sin(angle) * spd,
                life=random.randint(life // 2, life),
                size=random.randint(max(1, size - 1), size + 1),
                gravity=gravity, glow=glow
            ))

    def emit_jetpack(self, x, y, energy_pct):
        if energy_pct > 0.5:
            color = (255, 200, 50)
        elif energy_pct > 0.2:
            color = (255, 140, 30)
        else:
            color = (255, 60, 20)
        for _ in range(3):
            self.particles.append(Particle(
                x + random.randint(-4, 4), y,
                color,
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(1, 3),
                life=random.randint(8, 18),
                size=random.randint(2, 4),
                glow=True
            ))

    def emit_trail(self, x, y, color, count=2):
        for _ in range(count):
            self.particles.append(Particle(
                x + random.randint(-2, 2), y + random.randint(-2, 2),
                color,
                vx=random.uniform(-0.3, 0.3),
                vy=random.uniform(-0.3, 0.3),
                life=random.randint(5, 12),
                size=random.randint(1, 2)
            ))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# === PLAYER.PY ===
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.w = 80
        self.h = 80
        self.hp = PLAYER_MAX_HP
        self.energy = PLAYER_MAX_ENERGY
        self.speed = PLAYER_SPEED
        self.shoot_timer = 0
        self.invincible = 0
        self.inverted = False
        self.score = 0
        self.flash_timer = 0

        self.animations = {
            "idle": [],
            "flyup": [],
            "flyrl": []
        }
        
        # Load idle and flyup (single frame scaled to 80x80)
        try:
            img = pygame.image.load("assets/flyup.png").convert_alpha()
            img = pygame.transform.scale(img, (80, 80))
            self.animations["idle"].append(img)
            self.animations["flyup"].append(img)
        except Exception:
            surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            self.animations["idle"] = [surf]
            self.animations["flyup"] = [surf]
            
        # Load flyrl (single frame scaled to 80x80)
        try:
            img = pygame.image.load("assets/flyrl.png").convert_alpha()
            img = pygame.transform.scale(img, (80, 80))
            self.animations["flyrl"].append(img)
        except Exception:
            self.animations["flyrl"] = [pygame.Surface((80, 80), pygame.SRCALPHA)]

        self.current_anim = "idle"
        self.frame_index = 0
        self.anim_timer = 0
        self.facing_right = True

    def update(self, keys, particles):
        # Movement with potential inversion
        dx, dy = 0, 0
        mult = -1 if self.inverted else 1

        moving_x = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed * mult
            self.facing_right = False if mult == 1 else True
            moving_x = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed * mult
            self.facing_right = True if mult == 1 else False
            moving_x = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed * mult
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed * mult

        if dy < 0:
            self.current_anim = "flyup"
        elif moving_x:
            self.current_anim = "flyrl"
        else:
            self.current_anim = "idle"

        self.anim_timer += 1
        if self.anim_timer >= 6:
            self.frame_index += 1
            self.anim_timer = 0

        self.x = max(self.w // 2, min(WIDTH - self.w // 2, self.x + dx))
        self.y = max(self.h // 2, min(HEIGHT - self.h // 2, self.y + dy))

        # Energy drain
        self.energy = max(0, self.energy - ENERGY_DRAIN_RATE)

        # Shoot cooldown
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Invincibility frames
        if self.invincible > 0:
            self.invincible -= 1

        if self.flash_timer > 0:
            self.flash_timer -= 1

        # Jetpack particles
        if self.energy > 0:
            particles.emit_jetpack(self.x, self.y + self.h // 2, self.energy / PLAYER_MAX_ENERGY)

    def shoot(self):
        if self.shoot_timer <= 0 and self.energy > 2:
            self.shoot_timer = SHOOT_COOLDOWN
            self.energy -= 0.8
            return Bullet(self.x, self.y - self.h // 2)
        return None

    def take_damage(self, amount=1):
        if self.invincible <= 0:
            self.hp -= amount
            self.invincible = INVINCIBLE_FRAMES
            self.flash_timer = 15
            return True
        return False

    def collect_energy(self, amount):
        self.energy = min(PLAYER_MAX_ENERGY, self.energy + amount)

    def get_rect(self):
        return pygame.Rect(self.x - 40, self.y - 20, 80, 40)

    def draw(self, surface):
        if self.invincible > 0 and self.invincible % 6 < 3:
            return

        frames = self.animations.get(self.current_anim)
        if not frames:
            frames = self.animations["idle"]
        frame = frames[self.frame_index % len(frames)]
        
        if self.facing_right and self.current_anim == "flyrl":
            frame = pygame.transform.flip(frame, True, False)

        # Glow based on energy
        energy_pct = self.energy / PLAYER_MAX_ENERGY
        if energy_pct > 0.3:
            glow = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
            alpha = int(30 * energy_pct)
            pygame.draw.ellipse(glow, (*SOLAR_GOLD, alpha), (0, 0, self.w + 20, self.h + 20))
            surface.blit(glow, (self.x - self.w // 2 - 10, self.y - self.h // 2 - 10))

        if self.flash_timer > 0:
            flash_surf = frame.copy()
            flash_surf.fill((255, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(flash_surf, (self.x - self.w // 2, self.y - self.h // 2))
        else:
            surface.blit(frame, (self.x - self.w // 2, self.y - self.h // 2))


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.w = 4
        self.h = 12
        self.alive = True

    def update(self, particles):
        self.y -= self.speed
        if self.y < -10:
            self.alive = False
        particles.emit_trail(self.x, self.y + 6, ENERGY_CYAN, 1)

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        # Beam glow
        glow = pygame.Surface((16, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*ENERGY_CYAN, 40), (0, 0, 16, 20))
        surface.blit(glow, (self.x - 8, self.y - 10))
        pygame.draw.rect(surface, ENERGY_BEAM, (self.x - 2, self.y - 6, 4, 12))
        pygame.draw.rect(surface, WHITE, (self.x - 1, self.y - 5, 2, 10))


class EnemyBullet:
    def __init__(self, x, y, vx=0, vy=3, toxic=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = 6 if toxic else 4
        self.alive = True
        self.toxic = toxic
        self.color = UMAN_TOXIC if toxic else UMAN_RED

    def update(self, particles):
        self.x += self.vx
        self.y += self.vy
        if self.y > HEIGHT + 10 or self.y < -10 or self.x < -10 or self.x > WIDTH + 10:
            self.alive = False
        if self.toxic and random.random() < 0.3:
            particles.emit_trail(self.x, self.y, UMAN_TOXIC, 1)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        if self.toxic:
            pygame.draw.circle(surface, (150, 255, 100), (int(self.x), int(self.y)), self.size - 2)

# === ENEMIES.PY ===
class Enemy:
    def __init__(self, etype, x, y):
        cfg = ENEMY_CONFIGS[etype]
        self.etype = etype
        self.x = x
        self.y = y
        self.w, self.h = cfg["size"]
        self.hp = cfg["hp"]
        self.max_hp = cfg["hp"]
        self.speed = cfg["speed"]
        self.score = cfg["score"]
        self.shoot_rate = cfg["shoot_rate"]
        self.shoot_timer = random.randint(30, self.shoot_rate)
        self.color = cfg["color"]
        self.accent = cfg["accent"]
        self.alive = True
        self.move_timer = 0
        self.move_pattern = random.choice(["straight", "sine", "zigzag"])
        self.start_x = x
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, player_x, player_y):
        self.move_timer += 1
        bullets = []

        if self.etype == "drone":
            if self.move_pattern == "sine":
                self.x = self.start_x + math.sin(self.move_timer * 0.03 + self.phase) * 80
            self.y += self.speed

        elif self.etype == "bomber":
            self.x = self.start_x + math.sin(self.move_timer * 0.02 + self.phase) * 120
            self.y += self.speed * 0.7
            if self.shoot_timer <= 0:
                self.shoot_timer = self.shoot_rate
                # Drop toxic bombs
                bullets.append(EnemyBullet(self.x, self.y + self.h // 2, 0, 2.5, toxic=True))

        elif self.etype == "elite":
            # Aggressive: track player X
            if self.x < player_x - 10:
                self.x += self.speed * 0.6
            elif self.x > player_x + 10:
                self.x -= self.speed * 0.6
            self.y += self.speed * 0.4
            if self.shoot_timer <= 0:
                self.shoot_timer = self.shoot_rate
                angle = math.atan2(player_y - self.y, player_x - self.x)
                spd = 4
                bullets.append(EnemyBullet(
                    self.x, self.y + self.h // 2,
                    math.cos(angle) * spd, math.sin(angle) * spd
                ))

        # Generic shooting for drones
        if self.etype == "drone":
            if self.shoot_timer <= 0:
                self.shoot_timer = self.shoot_rate
                bullets.append(EnemyBullet(self.x, self.y + self.h // 2, 0, 3))

        self.shoot_timer -= 1

        if self.y > HEIGHT + 50:
            self.alive = False

        return bullets

    def take_damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        hw, hh = self.w // 2, self.h // 2

        if self.etype == "drone":
            # Hexagonal drone
            points = []
            for i in range(6):
                angle = math.pi / 6 + i * math.pi / 3
                points.append((cx + int(hw * math.cos(angle)), cy + int(hh * math.sin(angle))))
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, self.accent, points, 2)
            # Eyes
            pygame.draw.circle(surface, self.accent, (cx - 4, cy - 2), 3)
            pygame.draw.circle(surface, self.accent, (cx + 4, cy - 2), 3)

        elif self.etype == "bomber":
            # Bulky bomber
            pygame.draw.rect(surface, self.color, (cx - hw, cy - hh, self.w, self.h), border_radius=4)
            pygame.draw.rect(surface, self.accent, (cx - hw + 2, cy - hh + 2, self.w - 4, self.h - 4), 2, border_radius=3)
            # Toxic container
            pygame.draw.rect(surface, UMAN_TOXIC, (cx - 5, cy + 4, 10, 8))
            pygame.draw.rect(surface, (50, 150, 30), (cx - 5, cy + 4, 10, 8), 1)
            # Eyes
            pygame.draw.circle(surface, self.accent, (cx - 6, cy - 5), 3)
            pygame.draw.circle(surface, self.accent, (cx + 6, cy - 5), 3)

        elif self.etype == "elite":
            # Sleek elite
            points = [
                (cx, cy - hh),
                (cx + hw, cy + hh // 2),
                (cx + hw - 4, cy + hh),
                (cx - hw + 4, cy + hh),
                (cx - hw, cy + hh // 2),
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, self.accent, points, 2)
            # Core
            pygame.draw.circle(surface, self.accent, (cx, cy), 5)
            pygame.draw.circle(surface, (255, 200, 50), (cx, cy), 3)

        # HP bar for enemies with more than 1 hp
        if self.max_hp > 1:
            bar_w = self.w
            bar_h = 3
            pct = self.hp / self.max_hp
            pygame.draw.rect(surface, (80, 0, 0), (cx - bar_w // 2, cy - hh - 6, bar_w, bar_h))
            pygame.draw.rect(surface, UMAN_RED, (cx - bar_w // 2, cy - hh - 6, int(bar_w * pct), bar_h))


class Boss:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = -80
        self.w, self.h = BOSS_SIZE
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.speed = BOSS_SPEED
        self.alive = True
        self.phase = 0  # 0=enter, 1=fight1, 2=fight2, 3=fight3
        self.timer = 0
        self.shoot_timer = 0
        self.dir = 1
        self.entered = False
        self.score = 2000
        self.flash = 0

    def update(self, player_x, player_y):
        self.timer += 1
        bullets = []

        if not self.entered:
            self.y += 1.5
            if self.y >= 80:
                self.y = 80
                self.entered = True
                self.phase = 1
            return bullets

        # Determine phase based on HP
        hp_pct = self.hp / self.max_hp
        if hp_pct > 0.66:
            self.phase = 1
        elif hp_pct > 0.33:
            self.phase = 2
        else:
            self.phase = 3

        # Movement
        move_speed = self.speed + (3 - self.phase) * 0.5
        self.x += self.dir * move_speed
        if self.x > WIDTH - 80:
            self.dir = -1
        elif self.x < 80:
            self.dir = 1

        # Slight vertical bobbing
        self.y = 80 + math.sin(self.timer * 0.02) * 15

        # Attacks based on phase
        self.shoot_timer -= 1
        if self.phase == 1 and self.shoot_timer <= 0:
            self.shoot_timer = 40
            bullets.append(EnemyBullet(self.x - 20, self.y + 30, -1, 3, toxic=True))
            bullets.append(EnemyBullet(self.x + 20, self.y + 30, 1, 3, toxic=True))
            bullets.append(EnemyBullet(self.x, self.y + 35, 0, 4, toxic=False))

        elif self.phase == 2 and self.shoot_timer <= 0:
            self.shoot_timer = 25
            for i in range(-2, 3):
                angle = math.pi / 2 + i * 0.3
                bullets.append(EnemyBullet(
                    self.x, self.y + 35,
                    math.cos(angle) * 3, math.sin(angle) * 3, toxic=True
                ))

        elif self.phase == 3 and self.shoot_timer <= 0:
            self.shoot_timer = 15
            angle = math.atan2(player_y - self.y, player_x - self.x)
            for offset in [-0.2, 0, 0.2]:
                a = angle + offset
                bullets.append(EnemyBullet(
                    self.x, self.y + 35,
                    math.cos(a) * 4.5, math.sin(a) * 4.5, toxic=True
                ))

        if self.flash > 0:
            self.flash -= 1

        return bullets

    def take_damage(self, amount=1):
        self.hp -= amount
        self.flash = 8
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        hw, hh = self.w // 2, self.h // 2

        # Main body
        body_color = (255, 150, 150) if self.flash > 0 else BOSS_COLOR
        # Large menacing shape
        points = [
            (cx - hw, cy - hh // 2),
            (cx - hw + 15, cy - hh),
            (cx + hw - 15, cy - hh),
            (cx + hw, cy - hh // 2),
            (cx + hw - 5, cy + hh),
            (cx + 15, cy + hh + 5),
            (cx - 15, cy + hh + 5),
            (cx - hw + 5, cy + hh),
        ]
        pygame.draw.polygon(surface, body_color, points)
        pygame.draw.polygon(surface, BOSS_ACCENT, points, 3)

        # Central eye
        eye_size = 12 + int(math.sin(self.timer * 0.1) * 3)
        pygame.draw.circle(surface, (30, 0, 0), (cx, cy), eye_size + 2)
        pygame.draw.circle(surface, BOSS_ACCENT, (cx, cy), eye_size)
        pygame.draw.circle(surface, (255, 255, 100), (cx, cy), eye_size // 2)

        # Side thrusters
        for sx in [-1, 1]:
            tx = cx + sx * (hw - 8)
            pygame.draw.rect(surface, UMAN_DARK, (tx - 5, cy + hh - 10, 10, 15))
            # Thruster glow
            glow = pygame.Surface((14, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (200, 50, 255, 80), (0, 0, 14, 10))
            surface.blit(glow, (tx - 7, cy + hh + 3))

        # Phase indicator lines
        for i in range(self.phase):
            pygame.draw.line(surface, BOSS_ACCENT, (cx - 25 + i * 25, cy - hh + 5), (cx - 15 + i * 25, cy - hh + 5), 3)

        # HP bar
        bar_w = self.w + 20
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = cy - hh - 18
        pct = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (40, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        if pct > 0.66:
            bar_color = BOSS_ACCENT
        elif pct > 0.33:
            bar_color = SOLAR_ORANGE
        else:
            bar_color = (255, 50, 50)
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=3)
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

# === TRAPS.PY ===
class SolarOrb:
    def __init__(self, x=None, y=None):
        self.x = x or random.randint(50, WIDTH - 50)
        self.y = y or random.randint(-200, -30)
        self.radius = 10
        self.speed = 1.2
        self.alive = True
        self.timer = 0
        self.value = ENERGY_ORB_VALUE

    def update(self):
        self.y += self.speed
        self.timer += 1
        if self.y > HEIGHT + 20:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pulse = math.sin(self.timer * 0.1) * 3
        r = int(self.radius + pulse)
        # Outer glow
        glow = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*SOLAR_GOLD, 30), (r * 3, r * 3), r * 3)
        pygame.draw.circle(glow, (*SOLAR_ORANGE, 50), (r * 3, r * 3), r * 2)
        surface.blit(glow, (int(self.x - r * 3), int(self.y - r * 3)))
        # Core
        pygame.draw.circle(surface, SOLAR_GOLD, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, SOLAR_BRIGHT, (int(self.x), int(self.y)), r // 2)
        # Rays
        for i in range(6):
            angle = self.timer * 0.05 + i * math.pi / 3
            ex = int(self.x + math.cos(angle) * (r + 5))
            ey = int(self.y + math.sin(angle) * (r + 5))
            pygame.draw.line(surface, SOLAR_GOLD, (int(self.x), int(self.y)), (ex, ey), 1)

class HealthOrb:
    def __init__(self, x=None, y=None):
        self.x = x or random.randint(50, WIDTH - 50)
        self.y = y or random.randint(-200, -30)
        self.radius = 12
        self.speed = 1.0
        self.alive = True
        self.timer = 0
        self.heal_amount = 1

    def update(self):
        self.y += self.speed
        self.timer += 1
        if self.y > HEIGHT + 20:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        glow_size = self.radius + int(math.sin(self.timer * 0.1) * 3)
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (50, 255, 50, 100), (glow_size, glow_size), glow_size)
        surface.blit(glow, (self.x - glow_size, self.y - glow_size))
        
        pygame.draw.circle(surface, (30, 255, 30), (int(self.x), int(self.y)), self.radius - 2)
        pygame.draw.circle(surface, (150, 255, 150), (int(self.x) - 2, int(self.y) - 2), 3)


class FallingDebris:
    """Rocks/stalactites that fall rapidly from above"""
    def __init__(self):
        self.x = random.randint(30, WIDTH - 30)
        self.y = -40
        self.w = random.randint(12, 25)
        self.h = random.randint(25, 50)
        self.speed = random.uniform(5, 9)
        self.alive = True
        self.warned = False
        self.warn_timer = 45  # frames of warning before falling
        self.falling = False
        self.color = CAVE_WALL

    def update(self):
        if not self.falling:
            self.warn_timer -= 1
            if self.warn_timer <= 0:
                self.falling = True
            return
        self.y += self.speed
        if self.y > HEIGHT + 60:
            self.alive = False

    def get_rect(self):
        if not self.falling:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surface):
        if not self.falling:
            # Warning indicator
            alpha = int(abs(math.sin(self.warn_timer * 0.2)) * 200)
            warn_surf = pygame.Surface((self.w + 20, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(warn_surf, (255, 50, 50, min(40, alpha // 3)), (0, 0, self.w + 20, HEIGHT))
            surface.blit(warn_surf, (self.x - self.w // 2 - 10, 0))
            # Arrow at top
            arrow_y = 10 + int(math.sin(self.warn_timer * 0.3) * 5)
            pygame.draw.polygon(surface, TRAP_WARNING, [
                (self.x, arrow_y + 15),
                (self.x - 8, arrow_y),
                (self.x + 8, arrow_y)
            ])
        else:
            # Stalactite shape
            points = [
                (self.x - self.w // 2, self.y - self.h // 2),
                (self.x + self.w // 2, self.y - self.h // 2),
                (self.x + self.w // 3, self.y + self.h // 2 - 5),
                (self.x, self.y + self.h // 2),
                (self.x - self.w // 3, self.y + self.h // 2 - 5),
            ]
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, CAVE_ACCENT, points, 2)


class FakeOrb:
    """Looks like a solar orb but explodes on contact"""
    def __init__(self):
        self.x = random.randint(60, WIDTH - 60)
        self.y = random.randint(-150, -30)
        self.radius = 10
        self.speed = 1.0
        self.alive = True
        self.timer = 0
        self.exploded = False

    def update(self):
        self.y += self.speed
        self.timer += 1
        if self.y > HEIGHT + 20:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pulse = math.sin(self.timer * 0.1) * 3
        r = int(self.radius + pulse)
        # Looks similar to solar orb but slightly different hue
        glow = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*FAKE_ORB, 25), (r * 3, r * 3), r * 3)
        surface.blit(glow, (int(self.x - r * 3), int(self.y - r * 3)))
        pygame.draw.circle(surface, FAKE_ORB, (int(self.x), int(self.y)), r)
        # Subtle skull-like pattern (two dots and line) - hard to notice
        pygame.draw.circle(surface, (180, 180, 0), (int(self.x) - 2, int(self.y) - 2), 1)
        pygame.draw.circle(surface, (180, 180, 0), (int(self.x) + 2, int(self.y) - 2), 1)


class ToxicZone:
    """Area that damages the player if they stay in it"""
    def __init__(self, x=None, y_target=None):
        self.x = x or random.randint(100, WIDTH - 100)
        self.y = y_target or random.randint(150, HEIGHT - 150)
        self.radius = random.randint(50, 90)
        self.alive = True
        self.timer = 0
        self.duration = 300  # 5 seconds
        self.alpha_dir = 1
        self.alpha = 0

    def update(self):
        self.timer += 1
        self.alpha += self.alpha_dir * 2
        if self.alpha >= 80:
            self.alpha_dir = -1
        elif self.alpha <= 30:
            self.alpha_dir = 1
        if self.timer > self.duration:
            self.alive = False

    def contains(self, rect):
        cx = rect.centerx
        cy = rect.centery
        dist = math.sqrt((cx - self.x) ** 2 + (cy - self.y) ** 2)
        return dist < self.radius

    def draw(self, surface):
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*UMAN_TOXIC, int(self.alpha)), (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (*TOXIC_GREEN, int(self.alpha * 0.6)), (self.radius, self.radius), self.radius, 2)
        surface.blit(s, (self.x - self.radius, self.y - self.radius))
        # Hazard symbol
        if self.timer % 40 < 20:
            font = pygame.font.Font(None, 20)
            txt = font.render("☠", True, UMAN_TOXIC)
            surface.blit(txt, (self.x - txt.get_width() // 2, self.y - txt.get_height() // 2))


class TrapManager:
    """Manages Level Devil style traps"""
    def __init__(self):
        self.debris_list = []
        self.fake_orbs = []
        self.toxic_zones = []
        self.inversion_active = False
        self.inversion_timer = 0
        self.inversion_duration = 0
        self.glitch_active = False
        self.glitch_timer = 0
        self.glitch_duration = 0
        self.spawn_timers = {
            "debris": 0,
            "fake_orb": 0,
            "toxic": 0,
            "inversion": 0,
            "glitch": 0
        }
        self.wave_difficulty = 0  # increases with waves
        self.warning_text = ""
        self.warning_timer = 0

    def set_difficulty(self, wave_num):
        self.wave_difficulty = wave_num

    def show_warning(self, text):
        self.warning_text = text
        self.warning_timer = 90

    def update(self, player):
        # Update timers
        for k in self.spawn_timers:
            if self.spawn_timers[k] > 0:
                self.spawn_timers[k] -= 1

        if self.warning_timer > 0:
            self.warning_timer -= 1

        # Spawn traps based on difficulty
        if self.wave_difficulty >= 1 and self.spawn_timers["debris"] <= 0:
            interval = max(30, 90 - self.wave_difficulty * 10)
            if random.random() < 0.02 + self.wave_difficulty * 0.008:
                count = min(4, 1 + self.wave_difficulty // 2)
                for _ in range(count):
                    self.debris_list.append(FallingDebris())
                self.spawn_timers["debris"] = interval

        if self.wave_difficulty >= 2 and self.spawn_timers["fake_orb"] <= 0:
            if random.random() < 0.005 + self.wave_difficulty * 0.003:
                self.fake_orbs.append(FakeOrb())
                self.spawn_timers["fake_orb"] = 180

        if self.wave_difficulty >= 3 and self.spawn_timers["toxic"] <= 0:
            if random.random() < 0.003 + self.wave_difficulty * 0.002:
                self.toxic_zones.append(ToxicZone())
                self.spawn_timers["toxic"] = 300

        if self.wave_difficulty >= 2 and self.spawn_timers["inversion"] <= 0:
            if random.random() < 0.001 + self.wave_difficulty * 0.001:
                self.inversion_active = True
                self.inversion_duration = 120 + self.wave_difficulty * 30
                self.inversion_timer = self.inversion_duration
                self.spawn_timers["inversion"] = 600
                self.show_warning("CONTROLES INVERTIDOS!")

        if self.wave_difficulty >= 4 and self.spawn_timers["glitch"] <= 0:
            if random.random() < 0.002:
                self.glitch_active = True
                self.glitch_duration = 90
                self.glitch_timer = self.glitch_duration
                self.spawn_timers["glitch"] = 500
                self.show_warning("INTERFERÊNCIA DE GLITCH!")

        # Update inversion
        if self.inversion_active:
            self.inversion_timer -= 1
            player.inverted = True
            if self.inversion_timer <= 0:
                self.inversion_active = False
                player.inverted = False

        # Update glitch
        if self.glitch_active:
            self.glitch_timer -= 1
            if self.glitch_timer <= 0:
                self.glitch_active = False

        # Update debris
        for d in self.debris_list:
            d.update()
        self.debris_list = [d for d in self.debris_list if d.alive]

        # Update fake orbs
        for fo in self.fake_orbs:
            fo.update()
        self.fake_orbs = [fo for fo in self.fake_orbs if fo.alive]

        # Update toxic zones
        for tz in self.toxic_zones:
            tz.update()
        self.toxic_zones = [tz for tz in self.toxic_zones if tz.alive]

        # Check collisions with player
        damage_dealt = False
        p_rect = player.get_rect()

        for d in self.debris_list:
            if d.falling and d.get_rect().colliderect(p_rect):
                if player.take_damage():
                    damage_dealt = True
                d.alive = False

        for fo in self.fake_orbs:
            if fo.get_rect().colliderect(p_rect):
                if player.take_damage(2):
                    damage_dealt = True
                fo.alive = False
                fo.exploded = True

        for tz in self.toxic_zones:
            if tz.contains(p_rect) and random.random() < 0.02:
                player.energy = max(0, player.energy - 3)

        return damage_dealt

    def draw(self, surface):
        for tz in self.toxic_zones:
            tz.draw(surface)
        for d in self.debris_list:
            d.draw(surface)
        for fo in self.fake_orbs:
            fo.draw(surface)

        # Inversion warning overlay
        if self.inversion_active:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(abs(math.sin(self.inversion_timer * 0.1)) * 25)
            overlay.fill((255, 0, 100, alpha))
            surface.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 28)
            remaining = max(0, self.inversion_timer // 60)
            txt = font.render(f"CONTROLES INVERTIDOS! {remaining + 1}s", True, TRAP_WARNING)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 50))

        # Glitch effect
        if self.glitch_active:
            for _ in range(5):
                y = random.randint(0, HEIGHT)
                h = random.randint(2, 8)
                offset = random.randint(-15, 15)
                strip = surface.subsurface(pygame.Rect(0, max(0, y), WIDTH, min(h, HEIGHT - y))).copy()
                surface.blit(strip, (offset, y))

        # Warning text
        if self.warning_timer > 0:
            font = pygame.font.Font(None, 42)
            alpha = min(255, self.warning_timer * 5)
            txt = font.render(self.warning_text, True, TRAP_WARNING)
            txt.set_alpha(alpha)
            y = HEIGHT // 2 - 80 + int(math.sin(self.warning_timer * 0.15) * 5)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))

# === CUTSCENES.PY ===
class CutsceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.Font(None, 52)
        self.font_med = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.scene_index = 0
        self.timer = 0
        self.char_index = 0
        self.finished = False
        self.skip_held = 0
        self.sprite_player = SpritePlayer(0, 0)
        self.sprite_player.set_animation("idle")
        # Carregar sprites de aldeões e cientista
        npc_size = (60, 60)
        cientista_size = (80, 80)
        try:
            self.aldeao3_img = pygame.transform.flip(
                pygame.transform.scale(
                    pygame.image.load("assets/aldeao3.png").convert_alpha(), npc_size),
                True, False)
        except Exception:
            self.aldeao3_img = None
        try:
            self.aldeao4_img = pygame.transform.flip(
                pygame.transform.scale(
                    pygame.image.load("assets/aldeao4.png").convert_alpha(), npc_size),
                True, False)
        except Exception:
            self.aldeao4_img = None
        try:
            self.cientista_img = pygame.transform.flip(
                pygame.transform.scale(
                    pygame.image.load("assets/cientista.png").convert_alpha(), cientista_size),
                True, False)
        except Exception:
            self.cientista_img = None

    def reset(self, scene_type="intro"):
        self.scene_index = 0
        self.timer = 0
        self.char_index = 0
        self.finished = False
        self.skip_held = 0
        self.scene_type = scene_type

    def _draw_cave_bg(self, brightness=0):
        self.screen.fill((12 + brightness, 12 + brightness, 30 + brightness))
        ground_y = HEIGHT - 180  # chão elevado acima do diálogo
        # Cave walls
        for i in range(0, WIDTH, 40):
            h = 60 + int(math.sin(i * 0.05) * 30)
            color = (40 + brightness, 35 + brightness, 55 + brightness)
            pygame.draw.rect(self.screen, color, (i, 0, 38, h))
            pygame.draw.rect(self.screen, color, (i, ground_y - h + 20, 38, h + (HEIGHT - ground_y)))
        # Stalactites
        for i in range(50, WIDTH, 120):
            pts = [(i, 0), (i + 15, 50 + int(math.sin(i) * 20)), (i + 30, 0)]
            pygame.draw.polygon(self.screen, (55 + brightness, 50 + brightness, 70 + brightness), pts)

    def _draw_sunbeam(self, cx, width, intensity):
        beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(width, 0, -3):
            alpha = int((intensity / 255) * (20 - i * 0.3))
            alpha = max(0, min(80, alpha))
            pygame.draw.polygon(beam, (255, 255, 180, alpha), [
                (cx - i, 0), (cx + i, 0),
                (cx + i + 40, HEIGHT), (cx - i - 40, HEIGHT)
            ])
        self.screen.blit(beam, (0, 0))

    def _draw_prisoners(self, count=5):
        for i in range(count):
            total_w = (count - 1) * 70
            px = (WIDTH - total_w) // 2 + i * 70
            py = HEIGHT - 260 + 40
            # Alternar entre aldeao3 e aldeao4
            img = self.aldeao3_img if i % 2 == 0 else self.aldeao4_img
            if img:
                self.screen.blit(img, (px - img.get_width() // 2, py - img.get_height() // 2))
            else:
                # Fallback geométrico
                pygame.draw.rect(self.screen, (120, 100, 80), (px - 5, py, 10, 20))
                pygame.draw.circle(self.screen, (180, 150, 110), (px, py - 5), 6)

    def _draw_hope(self, x, y, has_jetpack=False):
        if has_jetpack:
            if not hasattr(self, 'flyup_img'):
                try:
                    self.flyup_img = pygame.transform.scale(pygame.image.load("assets/flyup.png").convert_alpha(), (80, 80))
                except Exception:
                    self.flyup_img = None
            if self.flyup_img:
                offsetX = self.flyup_img.get_width() // 2
                offsetY = self.flyup_img.get_height() // 2
                self.screen.blit(self.flyup_img, (x - offsetX, y - offsetY + 15))
                return

        if self.sprite_player.current_animation:
            sprite = self.sprite_player.current_animation[self.sprite_player.frame_index % len(self.sprite_player.current_animation)]
            offsetX = sprite.get_width() // 2
            offsetY = sprite.get_height() // 2
            self.screen.blit(sprite, (x - offsetX, y - offsetY + 15))

    def _draw_scientist(self, x, y):
        if self.cientista_img:
            self.screen.blit(self.cientista_img, (x - self.cientista_img.get_width() // 2, y - self.cientista_img.get_height() // 2))
        else:
            # Fallback geométrico
            pygame.draw.rect(self.screen, (200, 200, 210), (x - 8, y - 6, 16, 24))
            pygame.draw.circle(self.screen, (190, 160, 130), (x, y - 12), 7)

    def _draw_umans_flying(self, count=3):
        for i in range(count):
            ux = 150 + i * 200 + int(math.sin(self.timer * 0.03 + i) * 30)
            uy = 80 + int(math.cos(self.timer * 0.02 + i * 2) * 20)
            # UMAN body
            pts = [(ux, uy - 12), (ux + 14, uy + 6), (ux - 14, uy + 6)]
            pygame.draw.polygon(self.screen, UMAN_DARK, pts)
            pygame.draw.polygon(self.screen, UMAN_RED, pts, 2)
            pygame.draw.circle(self.screen, UMAN_RED, (ux - 3, uy - 3), 2)
            pygame.draw.circle(self.screen, UMAN_RED, (ux + 3, uy - 3), 2)

    def _draw_text_box(self, text, y_pos=None):

        # ==========================================================
        # POSIÇÃO
        # ==========================================================
        if y_pos is None:
            y_pos = HEIGHT - 140

        box_w = WIDTH - 90
        box_h = 125

        box_x = 45
        box_y = y_pos

        # ==========================================================
        # FUNDO
        # ==========================================================
        dialog = pygame.Surface(
            (box_w, box_h),
            pygame.SRCALPHA
        )

        dialog.fill((0, 0, 0, 235))

        self.screen.blit(dialog, (box_x, box_y))

        # ==========================================================
        # BORDA
        # ==========================================================
        pygame.draw.rect(
            self.screen,
            (145, 145, 145),
            (box_x, box_y, box_w, box_h),
            1
        )

        # ==========================================================
        # FONTES
        # ==========================================================
        speaker_font = pygame.font.SysFont(
            "Consolas",
            14,
            bold=True
        )

        text_font = pygame.font.SysFont(
            "Consolas",
            17
        )

        hint_font = pygame.font.SysFont(
            "Consolas",
            11
        )

        # ==========================================================
        # POSICIONAMENTO
        # ==========================================================
        speaker_y = box_y + 8
        line_y = box_y + 23
        text_y = box_y + 38

        # ==========================================================
        # NARRADOR
        # ==========================================================
        speaker = speaker_font.render(
            "NARRADOR",
            True,
            (225, 225, 225)
        )

        self.screen.blit(
            speaker,
            (box_x + 18, speaker_y)
        )

        # ==========================================================
        # LINHA
        # ==========================================================
        pygame.draw.line(
            self.screen,
            (70, 70, 70),
            (box_x + 18, line_y),
            (box_x + box_w - 18, line_y),
            1
        )

        # ==========================================================
        # WRAP FIXO (CORREÇÃO DO BUG)
        # ==========================================================
        full_lines = self._wrap_text(
            text,
            text_font,
            box_w - 60
        )

        visible_chars = self.char_index

        rendered_chars = 0

        for i, line in enumerate(full_lines):

            remaining = visible_chars - rendered_chars

            if remaining <= 0:
                break

            visible_line = line[:remaining]

            txt_surf = text_font.render(
                visible_line,
                True,
                (245, 245, 245)
            )

            self.screen.blit(
                txt_surf,
                (
                    box_x + 18,
                    text_y + i * 22
                )
            )

            rendered_chars += len(line)

        # ==========================================================
        # TYPEWRITER
        # ==========================================================
        if self.timer % CUTSCENE_SPEED == 0:

            if self.char_index < len(text):
                self.char_index += 1

        # ==========================================================
        # CURSOR
        # ==========================================================
        if self.char_index < len(text):

            if (self.timer // 20) % 2 == 0:

                current_line = ""

                rendered = 0

                for line in full_lines:

                    if rendered + len(line) >= self.char_index:
                        current_line = line[
                            :self.char_index - rendered
                        ]
                        break

                    rendered += len(line)

                cursor_x = (
                    box_x
                    + 18
                    + text_font.size(current_line)[0]
                )

                current_line_index = 0
                rendered = 0

                for idx, line in enumerate(full_lines):

                    if rendered + len(line) >= self.char_index:
                        current_line_index = idx
                        break

                    rendered += len(line)

                cursor_y = (
                    text_y
                    + current_line_index * 22
                )

                pygame.draw.rect(
                    self.screen,
                    (220, 220, 220),
                    (
                        cursor_x + 2,
                        cursor_y + 2,
                        2,
                        14
                    )
                )

        # ==========================================================
        # HINT
        # ==========================================================
        if self.timer > 60:

            hint = hint_font.render(
                "[ ENTER ] avançar",
                True,
                (90, 90, 90)
            )

            self.screen.blit(
                hint,
                (
                    box_x + box_w - hint.get_width() - 18,
                    box_y + box_h - 18
                )
            )

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current = ""
        for w in words:
            test = current + (" " if current else "") + w
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines if lines else [""]

    def _draw_destroyed_world(self):
        ground_y = HEIGHT - 180  # chão elevado acima do diálogo
        # Dark apocalyptic sky
        for y in range(HEIGHT):
            pct = y / HEIGHT
            r = int(30 + pct * 40)
            g = int(15 + pct * 20)
            b = int(25 + pct * 15)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        # Ruined buildings
        buildings = [(100, 200), (200, 280), (350, 180), (480, 260), (600, 220), (700, 190)]
        for bx, bh in buildings:
            bh_scaled = min(bh, ground_y - 30)
            by = ground_y - bh_scaled
            bw = 60
            pygame.draw.rect(self.screen, RUIN_GRAY, (bx, by, bw, bh_scaled))
            # Broken top
            for i in range(0, bw, 8):
                rh = random.Random(bx + i).randint(5, 25)
                pygame.draw.rect(self.screen, (70, 65, 60), (bx + i, by - rh, 6, rh))
            # Windows (some broken/lit)
            for wy in range(by + 15, ground_y - 10, 25):
                for wx in range(bx + 8, bx + bw - 8, 15):
                    if random.Random(wx + wy + bx).random() < 0.3:
                        pygame.draw.rect(self.screen, FIRE_COLOR, (wx, wy, 8, 10))
                    else:
                        pygame.draw.rect(self.screen, (40, 35, 30), (wx, wy, 8, 10))
        # Fires
        for fx in [150, 380, 550, 680]:
            fy = ground_y - 10
            for _ in range(5):
                fsize = random.Random(fx + self.timer // 10).randint(3, 8)
                fo = random.Random(fx + self.timer // 5 + _).randint(-10, 10)
                color = random.Random(fx + _).choice([FIRE_COLOR, SOLAR_ORANGE, (255, 50, 20)])
                pygame.draw.circle(self.screen, color, (fx + fo, fy - random.Random(fx + self.timer // 8 + _).randint(0, 20)), fsize)
        # Ground
        pygame.draw.rect(self.screen, (45, 40, 35), (0, ground_y, WIDTH, HEIGHT - ground_y))
        # Smoke/haze
        haze = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        haze.fill((40, 30, 20, 30))
        self.screen.blit(haze, (0, 0))

    def update_intro(self, events):
        self.timer += 1
        self.sprite_player.atualizar_animacao(1/60.0)
        enter_pressed = False
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                enter_pressed = True

        scenes = [
            # Scene 0: Cave with prisoners
            {
                "draw": lambda: (
                    self._draw_cave_bg(0),
                    self._draw_sunbeam(WIDTH // 2, 60, 100 + math.sin(self.timer * 0.03) * 30),
                    self._draw_prisoners(),
                    self._draw_text_box(
                        "Ao libertar os moradores, Hope descobre que eles estavam mantidos sob um enorme "
                        "buraco no teto da caverna, por onde a luz do Sol penetrava. Era tambem o local onde "
                        "os U.M.A.N.S arremessavam dejetos poluentes sobre os prisioneiros."
                    )
                )
            },
            # Scene 1: UMANs throwing waste
            {
                "draw": lambda: (
                    self._draw_cave_bg(5),
                    self._draw_sunbeam(WIDTH // 2, 80, 130),
                    self._draw_umans_flying(),
                    self._draw_prisoners(),
                    self._draw_hope(180, HEIGHT - 250),
                    self._draw_text_box(
                        "Os U.M.A.N.S, capangas de Glitch, voavam acima do buraco e lancavam residuos "
                        "toxicos para intensificar o sofrimento dos prisioneiros. Hope observa a cena "
                        "com determinacao."
                    )
                )
            },
            # Scene 2: Scientist approaches
            {
                "draw": lambda: (
                    self._draw_cave_bg(10),
                    self._draw_sunbeam(WIDTH // 2, 60, 120),
                    self._draw_hope(WIDTH // 2 - 35, HEIGHT - 250),
                    self._draw_scientist(WIDTH // 2 + 35, HEIGHT - 230),
                    self._draw_text_box(
                        "Um cientista da vila se aproxima e revela uma invencao criada em segredo: uma "
                        "mochila jetpack equipada com uma placa solar, capaz de transformar a energia do "
                        "Sol em propulsao."
                    )
                )
            },
            # Scene 3: Hope gets jetpack
            {
                "draw": lambda: (
                    self._draw_cave_bg(20),
                    self._draw_sunbeam(WIDTH // 2, 100, 180 + math.sin(self.timer * 0.05) * 40),
                    self._draw_hope(WIDTH // 2, HEIGHT - 250 - min(self.timer * 0.5, 80), has_jetpack=True),
                    self._jetpack_particles(),
                    self._draw_text_box(
                        "Hope veste o equipamento e sente a forca da energia limpa impulsiona-lo para "
                        "cima! Com habilidade, ela vai enfrentar os U.M.A.N.S e trazer esperanca de volta!"
                    )
                )
            },
            # Scene 4: Title card
            {
                "draw": lambda: self._draw_title_card()
            },
        ]

        if self.scene_index < len(scenes):
            scenes[self.scene_index]["draw"]()
            # Check for scene advance
            scene_texts_len = [200, 190, 190, 180, 0]
            min_time = 60
            text_done = self.char_index >= scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
            if enter_pressed and (text_done or self.timer > min_time):
                self.scene_index += 1
                self.timer = 0
                self.char_index = 0
            elif enter_pressed and not text_done:
                self.char_index = scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
        else:
            self.finished = True

    def _jetpack_particles(self):
        cx = WIDTH // 2
        cy = HEIGHT - 250 - min(self.timer * 0.5, 80) + 18
        for i in range(3):
            fx = cx + random.randint(-6, 6)
            fy = cy + random.randint(0, 8)
            color = random.choice([SOLAR_GOLD, SOLAR_ORANGE, (255, 100, 30)])
            size = random.randint(2, 5)
            pygame.draw.circle(self.screen, color, (int(fx), int(fy)), size)

    def _draw_title_card(self):
        # Gradient background
        for y in range(HEIGHT):
            pct = y / HEIGHT
            r = int(10 + pct * 20)
            g = int(5 + pct * 10)
            b = int(40 + pct * 30)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        # Sun
        sun_y = HEIGHT // 3
        sun_r = 60 + int(math.sin(self.timer * 0.03) * 5)
        glow = pygame.Surface((sun_r * 6, sun_r * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 200, 50, 20), (sun_r * 3, sun_r * 3), sun_r * 3)
        pygame.draw.circle(glow, (255, 200, 50, 40), (sun_r * 3, sun_r * 3), sun_r * 2)
        self.screen.blit(glow, (WIDTH // 2 - sun_r * 3, sun_y - sun_r * 3))
        pygame.draw.circle(self.screen, SOLAR_GOLD, (WIDTH // 2, sun_y), sun_r)
        pygame.draw.circle(self.screen, SOLAR_BRIGHT, (WIDTH // 2, sun_y), sun_r - 15)
        # Rays
        for i in range(12):
            angle = self.timer * 0.02 + i * math.pi / 6
            ex = WIDTH // 2 + int(math.cos(angle) * (sun_r + 30))
            ey = sun_y + int(math.sin(angle) * (sun_r + 30))
            pygame.draw.line(self.screen, SOLAR_GOLD, (WIDTH // 2, sun_y), (ex, ey), 2)
        # Title
        alpha = min(255, self.timer * 4)
        title1 = self.font_big.render("FASE 4", True, WHITE)
        title2 = self.font_med.render("ENERGIA LIMPA E ACESSÍVEL", True, SOLAR_GOLD)
        title1.set_alpha(alpha)
        title2.set_alpha(alpha)
        self.screen.blit(title1, (WIDTH // 2 - title1.get_width() // 2, sun_y + sun_r + 40))
        self.screen.blit(title2, (WIDTH // 2 - title2.get_width() // 2, sun_y + sun_r + 85))
        # Controls hint
        if self.timer > 90:
            hint = self.font_small.render("WASD/Setas: Mover  |  F: Atirar  |  ENTER: Começar", True, (150, 150, 180))
            hint.set_alpha(int(abs(math.sin(self.timer * 0.04)) * 200))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))
        if self.timer > 60:
            enter_hint = self.font_med.render("[ENTER]", True, ENERGY_CYAN)
            enter_hint.set_alpha(int(abs(math.sin(self.timer * 0.06)) * 255))
            self.screen.blit(enter_hint, (WIDTH // 2 - enter_hint.get_width() // 2, HEIGHT - 100))

    def update_outro(self, events):
        self.timer += 1
        self.sprite_player.atualizar_animacao(1/60.0)
        enter_pressed = False
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                enter_pressed = True

        scenes = [
            # Scene 0: Hope exits cave
            {
                "draw": lambda: (
                    self._draw_cave_bg(30),
                    self._draw_sunbeam(WIDTH // 2, 120, 220),
                    self._draw_hope(WIDTH // 2, HEIGHT // 2 - min(self.timer * 0.8, HEIGHT // 2 - 30), has_jetpack=True),
                    self._jetpack_outro_particles(),
                    self._draw_text_box(
                        "Apos derrotar os U.M.A.N.S, Hope sobe pelo buraco da caverna impulsionada "
                        "pela forca da energia solar. A luz do sol a guia para a superficie..."
                    )
                )
            },
            # Scene 1: Destroyed world
            {
                "draw": lambda: (
                    self._draw_destroyed_world(),
                    self._draw_hope(WIDTH // 2 - 100, HEIGHT - 230, has_jetpack=True),
                    self._draw_text_box(
                        "Ao sair da caverna, Hope ve a extensao do impacto que os poluidores "
                        "causaram na regiao. Mas a operacao toxica finalmente chegou ao fim."
                    )
                )
            },
            # Scene 2: Hope's victory
            {
                "draw": lambda: (
                    self._draw_destroyed_world(),
                    self._draw_hope(WIDTH // 2, HEIGHT - 230, has_jetpack=True),
                    self._draw_text_box(
                        "Gracas a energia solar, Hope desmantelou a fortaleza dos U.M.A.N.S! "
                        "Ela devolveu a esperanca de um futuro com energia limpa e acessivel "
                        "para todos os sobreviventes!",
                        HEIGHT - 140
                    )
                )
            }
        ]

        if self.scene_index < len(scenes):
            scenes[self.scene_index]["draw"]()
            scene_texts_len = [170, 160, 180]
            min_time = 60
            text_done = self.char_index >= scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
            if enter_pressed and (text_done or self.timer > min_time):
                self.scene_index += 1
                self.timer = 0
                self.char_index = 0
            elif enter_pressed and not text_done:
                self.char_index = scene_texts_len[min(self.scene_index, len(scene_texts_len) - 1)]
        else:
            self.finished = True

    def _jetpack_outro_particles(self):
        cx = WIDTH // 2
        cy = HEIGHT // 2 - min(self.timer * 0.8, HEIGHT // 2 - 30) + 18
        for i in range(4):
            fx = cx + random.randint(-6, 6)
            fy = cy + random.randint(2, 12)
            color = random.choice([SOLAR_GOLD, SOLAR_ORANGE])
            pygame.draw.circle(self.screen, color, (int(fx), int(fy)), random.randint(2, 5))

    def _draw_victory_screen(self):
        self.screen.fill((5, 5, 15))
        # Stars
        for i in range(50):
            sx = random.Random(i * 7).randint(0, WIDTH)
            sy = random.Random(i * 13).randint(0, HEIGHT)
            bright = int(abs(math.sin(self.timer * 0.02 + i)) * 200) + 55
            pygame.draw.circle(self.screen, (bright, bright, bright), (sx, sy), 1)
        # Hope silhouette flying
        hx = WIDTH // 2 + int(math.sin(self.timer * 0.02) * 30)
        hy = HEIGHT // 2 - 50
        self._draw_hope(hx, hy, has_jetpack=True)
        # Glow behind Hope
        glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*SOLAR_GOLD, 30), (40, 40), 40)
        self.screen.blit(glow, (hx - 40, hy - 40))
        # Text
        alpha = min(255, self.timer * 3)
        t1 = self.font_big.render("U.M.A.N.S DERROTADOS!", True, SOLAR_GOLD)
        t1.set_alpha(alpha)
        self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 + 60))
        t2 = self.font_small.render("Hope trouxe energia limpa e acessivel para todos!", True, (180, 200, 180))
        t2.set_alpha(alpha)
        self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 110))
        if self.timer > 120:
            hint = self.font_small.render("[ENTER para encerrar]", True, (120, 120, 150))
            hint.set_alpha(int(abs(math.sin(self.timer * 0.05)) * 200))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

# === FASE_7.PY ===
class Background:
    def __init__(self):
        self.scroll = 0
        self.brightness = 0  # increases as waves progress
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(40)]

    def set_brightness(self, wave_num, total_waves):
        self.brightness = int((wave_num / total_waves) * 60)

    def update(self):
        self.scroll += 0.5

    def draw(self, surface):
        b = self.brightness
        # Sky gradient
        for y in range(HEIGHT):
            pct = y / HEIGHT
            r = min(255, int(12 + b * 0.5 + pct * (15 + b * 0.3)))
            g = min(255, int(8 + b * 0.3 + pct * (10 + b * 0.2)))
            bl = min(255, int(30 + b + pct * (20 + b * 0.4)))
            pygame.draw.line(surface, (r, g, bl), (0, y), (WIDTH, y))

        # Stars (fade as brightness increases)
        star_alpha = max(0, 200 - b * 3)
        if star_alpha > 0:
            for sx, sy in self.stars:
                ty = (sy + int(self.scroll * 0.3)) % HEIGHT
                pygame.draw.circle(surface, (star_alpha, star_alpha, star_alpha), (sx, ty), 1)

        # Cave walls on sides
        wall_w = 40 + int(math.sin(self.scroll * 0.01) * 10)
        wall_color = (35 + b // 3, 30 + b // 3, 50 + b // 3)
        for y in range(0, HEIGHT, 20):
            offset = int(math.sin((y + self.scroll) * 0.03) * 15)
            lw = wall_w + offset
            rw = wall_w - offset + 5
            pygame.draw.rect(surface, wall_color, (0, y, lw, 22))
            pygame.draw.rect(surface, wall_color, (WIDTH - rw, y, rw, 22))
            # Texture
            pygame.draw.line(surface, (50 + b // 2, 45 + b // 2, 65 + b // 2),
                             (lw - 3, y), (lw - 3, y + 20), 1)
            pygame.draw.line(surface, (50 + b // 2, 45 + b // 2, 65 + b // 2),
                             (WIDTH - rw + 3, y), (WIDTH - rw + 3, y + 20), 1)

        # Sun at top (gets bigger/brighter with waves)
        if b > 10:
            sun_r = int(b * 0.8)
            sun_alpha = min(120, b * 2)
            glow = pygame.Surface((sun_r * 6, sun_r * 4), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 220, 100, sun_alpha // 3), (0, 0, sun_r * 6, sun_r * 4))
            surface.blit(glow, (WIDTH // 2 - sun_r * 3, -sun_r * 2))
            pygame.draw.circle(surface, (255, 230, 120, min(200, sun_alpha)),
                               (WIDTH // 2, 0), sun_r)


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.font_big = pygame.font.Font(None, 40)
        self.wave_text = ""
        self.wave_text_timer = 0

    def show_wave_text(self, text):
        self.wave_text = text
        self.wave_text_timer = 180

    def draw(self, surface, player, wave_num, total_waves):
        # HP bar
        from utils import draw_health_bar
        draw_health_bar(surface, player.hp, PLAYER_MAX_HP, 15, 15)

        # Energy bar
        bx, bar_w, bar_h = 15, 160, 16
        en_pct = player.energy / PLAYER_MAX_ENERGY
        ey = 15 + bar_h + 6
        pygame.draw.rect(surface, (40, 30, 0), (bx, ey, bar_w, bar_h), border_radius=4)
        en_color = SOLAR_GOLD if en_pct > 0.3 else SOLAR_ORANGE if en_pct > 0.1 else (200, 50, 20)
        pygame.draw.rect(surface, en_color, (bx, ey, int(bar_w * en_pct), bar_h), border_radius=4)
        pygame.draw.rect(surface, SOLAR_GOLD, (bx, ey, bar_w, bar_h), 2, border_radius=4)
        en_txt = self.font_small.render(f"ENERGIA {int(player.energy)}%", True, WHITE)
        surface.blit(en_txt, (bx + 5, ey + 1))

        # Score
        score_txt = self.font.render(f"Pontos: {player.score}", True, WHITE)
        surface.blit(score_txt, (WIDTH - score_txt.get_width() - 15, 15))

        # Wave indicator
        wave_txt = self.font_small.render(f"Onda {wave_num}/{total_waves}", True, (180, 180, 200))
        surface.blit(wave_txt, (WIDTH - wave_txt.get_width() - 15, 42))

        # Wave announcement text
        if self.wave_text_timer > 0:
            self.wave_text_timer -= 1
            alpha = min(255, self.wave_text_timer * 3)
            txt = self.font_big.render(self.wave_text, True, SOLAR_GOLD)
            txt.set_alpha(alpha)
            y = HEIGHT // 2 - 120 + int(math.sin(self.wave_text_timer * 0.05) * 3)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))


class Game:
    STATE_INTRO = 0
    STATE_PLAYING = 1
    STATE_GAME_OVER = 2
    STATE_VICTORY = 3
    STATE_OUTRO = 4
    STATE_PAUSED = 5

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            try:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
            except pygame.error:
                self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.state = self.STATE_INTRO

        self.player = Player()
        self.particles = ParticleSystem()
        self.background = Background()
        self.hud = HUD()
        self.trap_manager = TrapManager()
        self.cutscene = CutsceneManager(self.screen)
        self.cutscene.reset("intro")

        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.boss = None
        self.solar_orbs = []
        self.health_orbs = []

        self.current_wave = 0
        self.wave_queue = []  # enemies to spawn
        self.spawn_timer = 0
        self.wave_clear = False
        self.wave_transition_timer = 0
        self.total_waves = len(WAVES)

        self.shake_timer = 0
        self.shake_intensity = 0
        self.game_over_timer = 0

        self.wave_texts = [
            "Os U.M.A.N.S te avistaram!",
            "Reforços inimigos chegando!",
            "Ataque máximo! Resistam!",
            "COMANDANTE U.M.A.N.S DETECTADO!"
        ]

    def screen_shake(self, intensity=8, duration=15):
        self.shake_timer = duration
        self.shake_intensity = intensity

    def start_wave(self, wave_idx):
        if wave_idx >= len(WAVES):
            return
        self.current_wave = wave_idx
        self.wave_queue = []
        self.background.set_brightness(wave_idx, self.total_waves)
        self.trap_manager.set_difficulty(wave_idx)

        wave_data = WAVES[wave_idx]
        for etype, count, delay in wave_data:
            if etype == "boss":
                self.boss = Boss()
            else:
                for i in range(count):
                    self.wave_queue.append((etype, delay * i + random.randint(0, 30)))

        # Sort by spawn time
        self.wave_queue.sort(key=lambda x: x[1])
        self.spawn_timer = 0

        if wave_idx < len(self.wave_texts):
            self.hud.show_wave_text(self.wave_texts[wave_idx])

    def spawn_enemies(self):
        to_remove = []
        for i, (etype, delay) in enumerate(self.wave_queue):
            if self.spawn_timer >= delay:
                x = random.randint(80, WIDTH - 80)
                self.enemies.append(Enemy(etype, x, -30))
                to_remove.append(i)
        for i in reversed(to_remove):
            self.wave_queue.pop(i)
        self.spawn_timer += 1

    def check_wave_clear(self):
        if self.boss is not None:
            return not self.boss.alive
        return len(self.wave_queue) == 0 and len(self.enemies) == 0

    def update_playing(self, events, keys):
        # Maintain exactly MAX_SOLAR_ORBS on screen
        while len(self.solar_orbs) < MAX_SOLAR_ORBS:
            # Space them apart: find positions far from existing orbs
            attempts = 0
            while attempts < 10:
                new_x = random.randint(80, WIDTH - 80)
                new_y = random.randint(-300, -50)
                too_close = False
                for existing in self.solar_orbs:
                    if abs(existing.x - new_x) < 150 and abs(existing.y - new_y) < 200:
                        too_close = True
                        break
                if not too_close:
                    break
                attempts += 1
            self.solar_orbs.append(SolarOrb(new_x, new_y))

        # Spawn wave enemies
        self.spawn_enemies()

        # Player update
        self.player.update(keys, self.particles)

        # Low energy penalty
        if self.player.energy <= 0:
            self.player.y = min(HEIGHT - 30, self.player.y + 1.5)
            if random.random() < 0.03:
                self.player.take_damage()

        # Shooting
        if keys[pygame.K_f]:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.append(bullet)

        # Update bullets
        for b in self.bullets:
            b.update(self.particles)
        self.bullets = [b for b in self.bullets if b.alive]

        # Update enemy bullets
        for eb in self.enemy_bullets:
            eb.update(self.particles)
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]

        # Update enemies
        for e in self.enemies:
            new_bullets = e.update(self.player.x, self.player.y)
            self.enemy_bullets.extend(new_bullets)
        self.enemies = [e for e in self.enemies if e.alive]

        # Update boss
        if self.boss and self.boss.alive:
            new_bullets = self.boss.update(self.player.x, self.player.y)
            self.enemy_bullets.extend(new_bullets)

        # Update solar orbs
        for orb in self.solar_orbs:
            orb.update()
        self.solar_orbs = [o for o in self.solar_orbs if o.alive]
        
        if random.random() < 0.005 and len(self.health_orbs) < 2:
            self.health_orbs.append(HealthOrb())
            
        for orb in self.health_orbs:
            orb.update()
        self.health_orbs = [o for o in self.health_orbs if o.alive]

        # Update traps
        self.trap_manager.update(self.player)

        # Update particles
        self.particles.update()

        # Update background
        self.background.update()

        # --- Collisions ---
        p_rect = self.player.get_rect()

        # Player bullets vs enemies
        for b in self.bullets:
            b_rect = b.get_rect()
            for e in self.enemies:
                if b_rect.colliderect(e.get_rect()):
                    b.alive = False
                    if e.take_damage(amount=2):
                        self.player.score += e.score
                        self.particles.emit_burst(e.x, e.y, UMAN_RED, 15, 4, 25, 4, glow=True)
                        self.screen_shake(4, 8)
                    else:
                        self.particles.emit_burst(e.x, e.y, WHITE, 5, 2, 10, 2)
                    break
            # Bullets vs boss
            if self.boss and self.boss.alive:
                if b_rect.colliderect(self.boss.get_rect()):
                    b.alive = False
                    if self.boss.take_damage(amount=2):
                        self.player.score += self.boss.score
                        self.particles.emit_burst(self.boss.x, self.boss.y, BOSS_ACCENT, 40, 6, 40, 5, glow=True)
                        self.screen_shake(15, 30)
                    else:
                        self.particles.emit_burst(self.boss.x, self.boss.y, WHITE, 3, 2, 8, 2)

        # Enemy bullets vs player
        for eb in self.enemy_bullets:
            if eb.get_rect().colliderect(p_rect):
                if self.player.take_damage():
                    self.particles.emit_burst(self.player.x, self.player.y, (255, 100, 100), 12, 3, 15, 3)
                    self.screen_shake(6, 12)
                eb.alive = False

        # Enemies touching player
        for e in self.enemies:
            if e.get_rect().colliderect(p_rect):
                if self.player.take_damage():
                    self.particles.emit_burst(self.player.x, self.player.y, (255, 100, 100), 10, 3, 15, 3)
                    self.screen_shake(5, 10)

        # Solar orbs collection
        for orb in self.solar_orbs:
            if orb.get_rect().colliderect(p_rect):
                self.player.collect_energy(orb.value)
                self.particles.emit_burst(orb.x, orb.y, SOLAR_GOLD, 10, 3, 15, 3, glow=True)
                orb.alive = False
                
        # Health orbs collection
        for orb in self.health_orbs:
            if orb.get_rect().colliderect(p_rect):
                self.player.hp = min(PLAYER_MAX_HP, self.player.hp + orb.heal_amount)
                self.particles.emit_burst(orb.x, orb.y, (50, 255, 50), 10, 3, 15, 3, glow=True)
                orb.alive = False

        # Check player death
        if self.player.hp <= 0:
            self.state = self.STATE_GAME_OVER
            self.game_over_timer = 0

        # Check wave clear
        if self.check_wave_clear():
            if not self.wave_clear:
                self.wave_clear = True
                self.wave_transition_timer = 120
                if self.boss and not self.boss.alive:
                    self.boss = None
            else:
                self.wave_transition_timer -= 1
                if self.wave_transition_timer <= 0:
                    next_wave = self.current_wave + 1
                    if next_wave >= len(WAVES):
                        self.state = self.STATE_OUTRO
                        self.cutscene.reset("outro")
                    else:
                        self.wave_clear = False
                        self.start_wave(next_wave)

        # Shake
        if self.shake_timer > 0:
            self.shake_timer -= 1

    def draw_playing(self):
        render_surface = pygame.Surface((WIDTH, HEIGHT))

        self.background.draw(render_surface)
        self.trap_manager.draw(render_surface)

        for orb in self.solar_orbs:
            orb.draw(render_surface)
        for orb in self.health_orbs:
            orb.draw(render_surface)
        for b in self.bullets:
            b.draw(render_surface)
        for eb in self.enemy_bullets:
            eb.draw(render_surface)
        for e in self.enemies:
            e.draw(render_surface)
        if self.boss and self.boss.alive:
            self.boss.draw(render_surface)

        self.player.draw(render_surface)
        self.particles.draw(render_surface)
        self.hud.draw(render_surface, self.player, self.current_wave + 1, self.total_waves)

        # Apply screen shake
        offset_x, offset_y = 0, 0
        if self.shake_timer > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        self.screen.fill(BLACK)
        self.screen.blit(render_surface, (offset_x, offset_y))

    def draw_game_over(self):
        self.game_over_timer += 1
        self.screen.fill(BLACK)

        # Red vignette
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for r in range(300, 0, -5):
            alpha = max(0, 60 - r // 6)
            pygame.draw.circle(vignette, (100, 0, 0, alpha), (WIDTH // 2, HEIGHT // 2), r)
        self.screen.blit(vignette, (0, 0))

        font_big = pygame.font.Font(None, 64)
        font_med = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)

        alpha = min(255, self.game_over_timer * 4)

        txt = font_big.render("GAME OVER", True, (200, 30, 30))
        txt.set_alpha(alpha)
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 3))

        score_txt = font_med.render(f"Pontuação: {self.player.score}", True, WHITE)
        score_txt.set_alpha(alpha)
        self.screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 3 + 70))

        wave_txt = font_med.render(f"Onda alcançada: {self.current_wave + 1}/{self.total_waves}", True, (180, 180, 200))
        wave_txt.set_alpha(alpha)
        self.screen.blit(wave_txt, (WIDTH // 2 - wave_txt.get_width() // 2, HEIGHT // 3 + 105))

        if self.game_over_timer > 90:
            hint = font_small.render("[ENTER] Tentar novamente  |  [ESC] Sair", True, (150, 150, 150))
            hint.set_alpha(int(abs(math.sin(self.game_over_timer * 0.04)) * 255))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))

    def reset_game(self):
        self.player = Player()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.boss = None
        self.solar_orbs.clear()
        self.health_orbs.clear()
        self.particles = ParticleSystem()
        self.trap_manager = TrapManager()
        self.wave_clear = False
        self.wave_transition_timer = 0
        self.background = Background()
        self.state = self.STATE_PLAYING
        self.start_wave(0)

    def draw_menu(self):
        """Tela de menu inicial com comandos."""
        waiting = True
        import math, time
        t_start = time.time()
        
        font_grande = pygame.font.Font(None, 64)
        font_ui = pygame.font.SysFont("Consolas", 20)
        
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    waiting = False

            self.screen.fill((12, 12, 30))
            # Fundo com gradiente sutil
            for i in range(HEIGHT):
                r = int(15 + i * 0.02)
                g = int(12 + i * 0.015)
                b = int(10 + i * 0.01)
                pygame.draw.line(self.screen, (r, g, b), (0, i), (WIDTH, i))

            # Overlay colorido
            YELLOW_THEME = (255, 200, 50)
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((*YELLOW_THEME, 12))
            self.screen.blit(ov, (0, 0))

            t = time.time() - t_start

            # Título
            title = font_grande.render("FASE 4", True, YELLOW_THEME)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

            sub = font_ui.render("UMA ENERGIA LIMPA QUE OS FAZ VOAR (ODS 7)", True, (200, 190, 180))
            self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 120))

            # Caixa de comandos
            box_w, box_h = 460, 260
            box_x = WIDTH // 2 - box_w // 2
            box_y = 170
            pygame.draw.rect(self.screen, (25, 22, 20), (box_x, box_y, box_w, box_h), border_radius=8)
            pygame.draw.rect(self.screen, (*YELLOW_THEME, 80), (box_x, box_y, box_w, box_h), 2, border_radius=8)

            # Título da caixa
            cmd_title = font_ui.render("COMANDOS", True, (255, 220, 100))
            self.screen.blit(cmd_title, (WIDTH // 2 - cmd_title.get_width() // 2, box_y + 12))

            # Separador
            pygame.draw.line(self.screen, (80, 70, 60), (box_x + 20, box_y + 42), (box_x + box_w - 20, box_y + 42), 1)

            # Lista de comandos
            commands = [
                ("A / <", "Mover para esquerda"),
                ("D / >", "Mover para direita"),
                ("W / ^", "Voar"),
                ("S / v", "Descer"),
                ("F", "Atirar"),
                ("ALT + F4", "Sair da fase"),
            ]
            cy = box_y + 55
            for key, desc in commands:
                kt = font_ui.render(key, True, (255, 255, 150))
                self.screen.blit(kt, (box_x + 30, cy))
                pygame.draw.rect(self.screen, (70, 65, 50), (box_x + 200, cy + 2, 2, 14))
                dt_text = font_ui.render(desc, True, (255, 255, 255))
                self.screen.blit(dt_text, (box_x + 215, cy))
                cy += 32

            # Objetivo
            obj_y = box_y + box_h + 20
            obj_box = pygame.Rect(box_x, obj_y, box_w, 50)
            from utils import draw_wrapped_objective
            draw_wrapped_objective(
                self.screen, obj_box,
                "OBJETIVO: Sobreviva às ondas inimigas e derrote o Chefe usando Energia Limpa!",
                font_ui, (40, 30, 15), (255, 150, 50, 80), (255, 180, 80)
            )

            # Botão Enter pulsante
            pulse = int((math.sin(t * 3) + 1) * 0.5 * 40 + 215)
            enter_text = font_ui.render("Pressione ENTER para iniciar", True, (pulse, pulse, pulse))
            self.screen.blit(enter_text, (WIDTH // 2 - enter_text.get_width() // 2, HEIGHT - 70))

            pygame.display.flip()
            self.clock.tick(30)

    def run(self):
        self.draw_menu()
        running = True
        while running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            for e in events:
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    elif e.key == pygame.K_ESCAPE:
                        if self.state == self.STATE_PLAYING:
                            self.state = self.STATE_PAUSED
                        elif self.state == self.STATE_PAUSED:
                            self.state = self.STATE_PLAYING
                        elif self.state in (self.STATE_GAME_OVER, self.STATE_OUTRO):
                            running = False

            if self.state == self.STATE_INTRO:
                self.cutscene.update_intro(events)
                if self.cutscene.finished:
                    self.state = self.STATE_PLAYING
                    self.start_wave(0)

            elif self.state == self.STATE_PLAYING:
                self.update_playing(events, keys)
                self.draw_playing()

            elif self.state == self.STATE_GAME_OVER:
                return 'gameover'

            elif self.state == self.STATE_OUTRO:
                self.cutscene.update_outro(events)
                if self.cutscene.finished:
                    return 'win'

            elif self.state == self.STATE_PAUSED:
                # Dim screen
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                self.screen.blit(overlay, (0, 0))
                font = pygame.font.Font(None, 52)
                txt = font.render("PAUSADO", True, WHITE)
                self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
                hint = pygame.font.Font(None, 26).render("[ESC] Continuar", True, (180, 180, 180))
                self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 30))

            pygame.display.flip()
            self.clock.tick(FPS)

        return 'quit'

if __name__ == "__main__":
    run_level_4()

def run_level_4():
    import pygame
    orig_quit = pygame.quit
    pygame.quit = lambda: None
    try:
        while True:
            game = Game()
            status = game.run()
            if status == 'quit':
                return False
            elif status == 'win':
                from utils import show_end_screen
                show_end_screen(
                    pygame.display.get_surface(), pygame.time.Clock(),
                    "COMPLETO!", "Umans resgatado e pedras limpas!",
                    (34, 255, 136), "CONTINUAR",
                    stats={"Pontuação": f"{game.player.score}"},
                    lesson="Energia limpa e acessível é essencial para salvar ecossistemas e a humanidade."
                )
                return True
            elif status == 'gameover':
                from utils import show_end_screen
                show_end_screen(
                    pygame.display.get_surface(), pygame.time.Clock(),
                    "GAME OVER", "A caverna colapsou...",
                    (255, 34, 68), "TENTAR DE NOVO",
                    stats={"Pontuação": f"{game.player.score}", "Onda": f"{game.current_wave + 1}/{game.total_waves}"}
                )
                continue
            else:
                return False
    except SystemExit:
        return False
    except Exception as e:
        print(f"Erro ao executar Level 4: {e}")
        return False
    finally:
        pygame.quit = orig_quit