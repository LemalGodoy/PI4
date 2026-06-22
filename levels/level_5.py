import pygame
import random
import sys
import math
import os
from entities import Player, PlayerBullet

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60
GROUND_Y = HEIGHT - 60

# Física
GRAVITY = 0.55
JUMP_SPEED = -10.5
PLAYER_SPEED = 4.2
DASH_SPEED = 11
DASH_FRAMES = 8
DASH_CD = 50
SHOOT_CD = 10
BULLET_SPEED = 9
PLAYER_MAX_HP = 5
INV_FRAMES = 60

# Boss
BOSS_MAX_HP = 300
BOSS_ATK_CD = [60, 45, 30]
BOSS_BULLET_SPD = 4

# Cores
C_BG_TOP = (12, 8, 30)
C_BG_BOT = (35, 15, 65)
C_GROUND = (50, 35, 85)
C_GROUND_LINE = (80, 55, 130)
C_HOPE = (50, 160, 255)
C_HOPE_DARK = (35, 120, 200)
C_GOLD = (255, 215, 60)
C_GLITCH = (200, 45, 65)
C_GLITCH_DARK = (140, 25, 45)
C_WHITE = (255, 255, 255)
C_HP_GREEN = (80, 220, 100)
C_HP_RED = (220, 60, 60)
C_HP_BG = (40, 20, 60)

screen = pygame.display.get_surface()
if screen is None:
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    except pygame.error:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Level 5 — ODS 16")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Consolas", 52, bold=True)
font_med = pygame.font.SysFont("Consolas", 28, bold=True)
font_sm = pygame.font.SysFont("Consolas", 18)


_levels_dir = os.path.dirname(os.path.abspath(__file__))

_script_dir = os.path.dirname(_levels_dir)

_bg_path = os.path.join(
    _script_dir,
    'assets',
    'cidadela_ref.jpg'
)

print("Tentando carregar:", _bg_path)

try:
    BG_IMG_RAW = pygame.image.load(_bg_path).convert()
    BG_IMG = pygame.transform.scale(BG_IMG_RAW, (WIDTH, HEIGHT))

    BG_IMG_FIGHT = BG_IMG.copy()

    _dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    _dark_overlay.fill((0, 0, 0, 90))

    BG_IMG_FIGHT.blit(_dark_overlay, (0, 0))

    BG_LOADED = True

    print("Imagem carregada com sucesso!")

except Exception as e:

    print("ERRO AO CARREGAR FUNDO:")
    print(e)

    BG_IMG = None
    BG_IMG_FIGHT = None
    BG_LOADED = False

# ==========================================
# UTILIDADES
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

    def draw(self, surf):
        t = max(0.01, self.life / self.max_life)
        s = max(1, int(self.size * t))
        c = tuple(min(255, int(v * t)) for v in self.color)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), s)

class ScreenShake:
    def __init__(self):
        self.amount = 0; self.duration = 0
    def trigger(self, amount, duration):
        self.amount = amount; self.duration = duration
    def get_offset(self):
        if self.duration > 0:
            self.duration -= 1
            return random.randint(-self.amount, self.amount), random.randint(-self.amount, self.amount)
        return 0, 0

shake = ScreenShake()
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT - 80),
          random.uniform(0.3, 1.0), random.uniform(0.02, 0.06)) for _ in range(80)]

def draw_background(surf, frame):
    if BG_LOADED:
        surf.blit(BG_IMG_FIGHT, (0, 0))
        # Subtle twinkling stars overlay on dark sky areas
        for sx, sy, bright, speed in stars:
            if sy < GROUND_Y - 20:
                a = (math.sin(frame * speed + sx) + 1) / 2
                v = int(80 * bright * a)
                if v > 20:
                    pygame.draw.circle(surf, (v, v, int(v * 0.8)), (sx, sy), 1)
    else:
        # Fallback procedural background
        for y in range(0, HEIGHT - 60, 4):
            t = y / (HEIGHT - 60)
            r = int(C_BG_TOP[0] + (C_BG_BOT[0] - C_BG_TOP[0]) * t)
            g = int(C_BG_TOP[1] + (C_BG_BOT[1] - C_BG_TOP[1]) * t)
            b = int(C_BG_TOP[2] + (C_BG_BOT[2] - C_BG_TOP[2]) * t)
            pygame.draw.rect(surf, (r, g, b), (0, y, WIDTH, 4))
        for sx, sy, bright, speed in stars:
            a = (math.sin(frame * speed + sx) + 1) / 2
            v = int(180 * bright * a)
            pygame.draw.circle(surf, (v, v, int(v * 0.8)), (sx, sy), 1 + int(bright > 0.7))
    # Ground platform overlay — marble with golden edge
    pygame.draw.rect(surf, (200, 195, 210), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(surf, (180, 175, 195), (0, GROUND_Y + 3, WIDTH, HEIGHT - GROUND_Y - 3))
    # Greek key pattern on ground
    for i in range(0, WIDTH, 32):
        pygame.draw.rect(surf, (160, 155, 175), (i, GROUND_Y + 8, 16, 4))
        pygame.draw.rect(surf, (160, 155, 175), (i + 16, GROUND_Y + 14, 16, 4))
        pygame.draw.rect(surf, (160, 155, 175), (i, GROUND_Y + 12, 4, 6))
        pygame.draw.rect(surf, (160, 155, 175), (i + 28, GROUND_Y + 4, 4, 14))
    # Golden top edge
    pygame.draw.line(surf, C_GOLD, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
    pygame.draw.line(surf, (180, 150, 40), (0, GROUND_Y + 1), (WIDTH, GROUND_Y + 1), 1)

def draw_hud(surf, player_hp, boss_hp, boss_phase, boss_alive):
    # Player HP — barra padronizada
    from utils import draw_health_bar
    draw_health_bar(surf, player_hp, PLAYER_MAX_HP, 15, 15)
    # Boss HP bar
    if boss_alive:
        bx, by, bw, bh = WIDTH // 2 - 180, 18, 360, 16
        pygame.draw.rect(surf, C_HP_BG, (bx - 2, by - 2, bw + 4, bh + 4), border_radius=4)
        ratio = max(0, boss_hp / BOSS_MAX_HP)
        bar_color = C_GLITCH if boss_phase < 3 else (180, 30, 200)
        pygame.draw.rect(surf, bar_color, (bx, by, int(bw * ratio), bh), border_radius=3)
        pygame.draw.rect(surf, (200, 180, 220), (bx - 2, by - 2, bw + 4, bh + 4), 2, border_radius=4)
        name = font_sm.render(f"NUVEM DE GLITCH  —  FASE {boss_phase}", True, C_WHITE)
        surf.blit(name, (bx + bw // 2 - name.get_width() // 2, by - 18))

def spawn_hit_particles(particles, x, y, color, count=8):
    for _ in range(count):
        particles.append(Particle(x, y, color,
            random.uniform(-3, 3), random.uniform(-4, 1), random.randint(15, 30), random.randint(2, 4), 0.1))

# ==========================================
# ==========================================
# JOGADOR — HOPE (Classes unificadas em entities.py)
# ==========================================

# ==========================================
# BOSS — NUVEM DE GLITCH
# ==========================================
class BossProj:
    def __init__(self, x, y, vx, vy, color=C_GLITCH, size=6):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.color, self.size = color, size
        self.alive = True
    def update(self):
        self.x += self.vx; self.y += self.vy
        if self.x < -40 or self.x > WIDTH + 40 or self.y < -40 or self.y > HEIGHT + 40: self.alive = False
    def rect(self): return pygame.Rect(int(self.x) - self.size, int(self.y) - self.size, self.size * 2, self.size * 2)
    def draw(self, surf):
        x, y, s = int(self.x), int(self.y), self.size
        gs = pygame.Surface((s * 4, s * 4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self.color, 35), (s * 2, s * 2), s * 2)
        surf.blit(gs, (x - s * 2, y - s * 2))
        pygame.draw.circle(surf, self.color, (x, y), s)
        pygame.draw.circle(surf, (255, 200, 200), (x, y), max(1, s // 2))

class Boss:
    def __init__(self):
        self.reset()

    def reset(self):
        self.w, self.h = 250, 200
        self.x = float(WIDTH - 280); self.y = float(GROUND_Y - self.h - 10)
        self.home_x, self.home_y = self.x, self.y
        self.hp = BOSS_MAX_HP; self.phase = 1
        self.bob = 0.0; self.atk_timer = 0
        self.cur_atk = None; self.atk_frame = 0
        self.hit_flash = 0; self.inv = 0
        self.alive = True; self.frame = 0
        self.phase_trans = 0
        self._p2 = False; self._p3 = False
        self.phase_just_changed = False

    def _get_phase(self):
        r = self.hp / BOSS_MAX_HP
        return 3 if r <= 0.3 else (2 if r <= 0.6 else 1)

    def update(self, player, projs, particles):
        if not self.alive: return
        self.frame += 1; self.bob += 0.04
        np = self._get_phase()
        if np == 2 and not self._p2:
            self._p2 = True; self.phase = 2; self.phase_trans = 100; self.cur_atk = None
            self.phase_just_changed = True
        elif np == 3 and not self._p3:
            self._p3 = True; self.phase = 3; self.phase_trans = 100; self.cur_atk = None
            self.phase_just_changed = True
        if self.phase_trans > 0: self.phase_trans -= 1; return

        ty = self.home_y + math.sin(self.bob) * 28
        self.y += (ty - self.y) * 0.05
        self.x += (self.home_x - self.x) * 0.03

        if self.cur_atk is None:
            self.atk_timer += 1
            if self.atk_timer >= BOSS_ATK_CD[self.phase - 1]:
                atks = ['spread']
                if self.phase >= 2: atks += ['spiral']
                if self.phase >= 3: atks += ['wave', 'spiral']
                self.cur_atk = random.choice(atks); self.atk_frame = 0; self.atk_timer = 0
        else:
            self._do_attack(player, projs, particles)
        if self.hit_flash > 0: self.hit_flash -= 1
        if self.inv > 0: self.inv -= 1

    def _do_attack(self, player, projs, particles):
        self.atk_frame += 1
        cx, cy = self.x + self.w // 2, self.y + self.h // 2
        px, py = player.x + player.w // 2, player.y + player.h // 2

        if self.cur_atk == 'spread' and self.atk_frame == 18:
            a0 = math.atan2(py - cy, px - cx)
            n = 3 + self.phase; sp = 0.28
            for i in range(n):
                a = a0 + (i - n // 2) * sp
                s = BOSS_BULLET_SPD + self.phase * 0.4
                projs.append(BossProj(cx, cy, math.cos(a) * s, math.sin(a) * s))
            shake.trigger(3, 8); self.cur_atk = None


        elif self.cur_atk == 'spiral':
            if self.atk_frame <= 24 and self.atk_frame % 3 == 0:
                a = self.atk_frame * 0.6 + self.bob
                for i in range(2):
                    aa = a + i * math.pi
                    projs.append(BossProj(cx, cy, math.cos(aa) * 3.5, math.sin(aa) * 3.5, (170, 50, 190), 5))
            if self.atk_frame > 24: self.cur_atk = None

        elif self.cur_atk == 'wave' and self.atk_frame == 20:
            wy = GROUND_Y - 25
            for i in range(12):
                projs.append(BossProj(WIDTH + 10 - i * 55, wy, -5.5, 0, (255, 70, 70), 8))
            shake.trigger(4, 10); self.cur_atk = None

    def take_damage(self, dmg=6):
        if self.inv > 0: return False
        self.hp = max(0, self.hp - dmg); self.hit_flash = 6; self.inv = 5
        if self.hp <= 0: self.alive = False
        return True

    def rect(self): return pygame.Rect(int(self.x) + 10, int(self.y) + 10, self.w - 20, self.h - 20)

    def draw(self, surf):
        if not self.alive: return
        x, y, w, h = int(self.x), int(self.y), self.w, self.h
        cx, cy = x + w // 2, y + h // 2
        cc = C_WHITE if self.hit_flash > 0 else ((170, 30, 190) if self.phase == 3 else
              (C_GLITCH if self.phase <= 2 else C_GLITCH))
        dc = tuple(max(0, v - 40) for v in cc)
        # Aura
        as_ = 28 + self.phase * 12
        asf = pygame.Surface((w + as_ * 2, h + as_ * 2), pygame.SRCALPHA)
        ac = (200, 40, 60) if self.phase < 3 else (160, 30, 180)
        pygame.draw.ellipse(asf, (*ac, 18 + self.phase * 4), asf.get_rect())
        surf.blit(asf, (x - as_, y - as_))
        # Cloud circles — scaled up for larger body
        p = math.sin(self.frame * 0.08) * 6
        j = 3 if self.phase >= 2 else 0
        circles = [(cx, cy, 55 + p), (cx - 50, cy - 18, 40 + p * .7), (cx + 50, cy - 18, 40 + p * .7),
                   (cx - 34, cy + 26, 35 + p * .5), (cx + 34, cy + 26, 35 + p * .5), (cx, cy - 40, 30),
                   (cx - 60, cy + 5, 28 + p * .3), (cx + 60, cy + 5, 28 + p * .3)]
        for ccx, ccy, r in circles:
            jx, jy = random.randint(-j, j), random.randint(-j, j)
            pygame.draw.circle(surf, cc, (ccx + jx, ccy + jy), int(r))
        for ccx, ccy, r in circles[:4]:
            pygame.draw.circle(surf, dc, (ccx, ccy), int(r * .55))
        # Eyes — larger
        ep = math.sin(self.frame * 0.08) * 3
        es = 14 + int(ep)
        ey = cy - 5
        for ox in (-28, 28):
            pygame.draw.circle(surf, (255, 235, 190), (cx + ox, ey), es)
            pygame.draw.circle(surf, (50, 0, 0), (cx + ox, ey), es // 2 + 2)
            pygame.draw.circle(surf, (255, 200, 200), (cx + ox + 3, ey - 3), 3)
        if self.phase >= 2:
            pygame.draw.line(surf, (60, 0, 0), (cx - 44, ey - 18), (cx - 14, ey - 12), 4)
            pygame.draw.line(surf, (60, 0, 0), (cx + 44, ey - 18), (cx + 14, ey - 12), 4)
        # Mouth — larger
        if self.cur_atk and self.atk_frame < 20:
            pygame.draw.circle(surf, (50, 0, 0), (cx, cy + 28), 15 + self.phase * 2)
        else:
            pygame.draw.arc(surf, (50, 0, 0), (cx - 20, cy + 14, 40, 24), math.pi, 2 * math.pi, 3)
        # Phase transition flash
        if self.phase_trans > 50:
            fs = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fs.fill((255, 50, 50, min(120, (self.phase_trans - 50) * 6)))
            surf.blit(fs, (0, 0))

# ==========================================
# LEVEL DEVIL TRIGGERS
# ==========================================
class FloorTrap:
    """A section of ground that warns (flashes), then crumbles into a pit."""
    def __init__(self, x, width):
        self.x = x
        self.width = width
        self.state = 'warn'   # warn → open → closing → done
        self.timer = 0
        self.warn_dur = 45    # frames of warning flash
        self.open_dur = 120   # frames pit stays open
        self.close_dur = 25
        self.alive = True

    def update(self):
        self.timer += 1
        if self.state == 'warn' and self.timer >= self.warn_dur:
            self.state = 'open'; self.timer = 0
        elif self.state == 'open' and self.timer >= self.open_dur:
            self.state = 'closing'; self.timer = 0
        elif self.state == 'closing' and self.timer >= self.close_dur:
            self.alive = False

    def is_pit_active(self):
        return self.state == 'open'

    def player_falls(self, player):
        """Check if player is standing over the open pit."""
        if not self.is_pit_active(): return False
        px_center = player.x + player.w / 2
        return (player.on_ground and
                self.x <= px_center <= self.x + self.width)

    def draw(self, surf):
        if self.state == 'warn':
            # Flashing gold warning on the ground
            alpha = int((math.sin(self.timer * 0.3) + 1) * 60 + 40)
            ws = pygame.Surface((self.width, 60), pygame.SRCALPHA)
            pygame.draw.rect(ws, (255, 200, 40, alpha), (0, 0, self.width, 60))
            # Exclamation marks
            if self.timer % 20 < 14:
                warn_txt = font_sm.render("! !", True, (255, 80, 40))
                surf.blit(warn_txt, (self.x + self.width // 2 - warn_txt.get_width() // 2, GROUND_Y - 25))
            surf.blit(ws, (self.x, GROUND_Y))
        elif self.state == 'open':
            # Dark pit
            pygame.draw.rect(surf, (8, 5, 15), (self.x, GROUND_Y, self.width, 60))
            # Danger edges
            pygame.draw.line(surf, (120, 40, 40), (self.x, GROUND_Y), (self.x, GROUND_Y + 60), 2)
            pygame.draw.line(surf, (120, 40, 40), (self.x + self.width, GROUND_Y),
                           (self.x + self.width, GROUND_Y + 60), 2)
            # Faint red glow from pit
            gs = pygame.Surface((self.width, 30), pygame.SRCALPHA)
            pygame.draw.rect(gs, (180, 30, 30, 20), gs.get_rect())
            surf.blit(gs, (self.x, GROUND_Y + 30))
        elif self.state == 'closing':
            # Ground reforming
            progress = self.timer / self.close_dur
            filled_w = int(self.width * progress)
            pygame.draw.rect(surf, C_GROUND, (self.x, GROUND_Y, filled_w, 60))
            remaining = self.width - filled_w
            if remaining > 0:
                pygame.draw.rect(surf, (8, 5, 15), (self.x + filled_w, GROUND_Y, remaining, 60))


class CeilingSpike:
    """A spike that drops from the ceiling with a red warning line."""
    def __init__(self, x):
        self.x = x
        self.y = -20.0
        self.target_y = GROUND_Y - 8
        self.width = 16
        self.height = 24
        self.state = 'warn'  # warn → drop → stuck → done
        self.timer = 0
        self.warn_dur = 25
        self.stuck_dur = 40
        self.speed = 0.0
        self.alive = True

    def update(self):
        self.timer += 1
        if self.state == 'warn' and self.timer >= self.warn_dur:
            self.state = 'drop'; self.timer = 0; self.speed = 2.0
        elif self.state == 'drop':
            self.speed = min(self.speed + 0.8, 14)
            self.y += self.speed
            if self.y >= self.target_y:
                self.y = self.target_y; self.state = 'stuck'; self.timer = 0
        elif self.state == 'stuck' and self.timer >= self.stuck_dur:
            self.alive = False

    def get_rect(self):
        if self.state == 'drop' or self.state == 'stuck':
            return pygame.Rect(int(self.x) - self.width // 2, int(self.y), self.width, self.height)
        return pygame.Rect(0, 0, 0, 0)  # no collision during warn

    def draw(self, surf):
        if self.state == 'warn':
            # Red vertical warning line
            alpha = int((math.sin(self.timer * 0.4) + 1) * 50 + 30)
            line_surf = pygame.Surface((4, HEIGHT), pygame.SRCALPHA)
            line_surf.fill((255, 50, 50, alpha))
            surf.blit(line_surf, (self.x - 2, 0))
            # Small triangle at top
            if self.timer % 16 < 10:
                pygame.draw.polygon(surf, (255, 80, 60), [
                    (self.x, 0), (self.x - 8, 15), (self.x + 8, 15)])
        else:
            # Spike body
            color = (160, 50, 60) if self.state == 'drop' else (120, 40, 50)
            pygame.draw.polygon(surf, color, [
                (self.x, int(self.y) + self.height),
                (self.x - self.width // 2, int(self.y)),
                (self.x + self.width // 2, int(self.y)),
            ])
            # Metallic highlight
            pygame.draw.line(surf, (200, 100, 110),
                           (self.x, int(self.y) + self.height),
                           (self.x - 2, int(self.y) + 4), 1)

class HealthOrb:
    """Golden health pickup that heals 1 HP."""
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.alive = True
        self.frame = 0
        self.bob_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.frame += 1
        self.y += math.sin(self.frame * 0.06 + self.bob_offset) * 0.3

    def get_rect(self):
        return pygame.Rect(int(self.x) - 12, int(self.y) - 12, 24, 24)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        pulse = math.sin(self.frame * 0.1) * 3
        # Outer glow
        gs = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(gs, (255, 215, 60, 30), (20, 20), int(18 + pulse))
        surf.blit(gs, (x - 20, y - 20))
        # Core
        pygame.draw.circle(surf, C_GOLD, (x, y), int(9 + pulse * 0.5))
        pygame.draw.circle(surf, (255, 240, 150), (x, y), int(5 + pulse * 0.3))
        # Cross/plus symbol
        pygame.draw.rect(surf, (255, 255, 220), (x - 1, y - 5, 3, 10))
        pygame.draw.rect(surf, (255, 255, 220), (x - 5, y - 1, 10, 3))
        # Sparkle particles
        if self.frame % 12 == 0:
            sx = x + random.randint(-8, 8)
            sy = y + random.randint(-8, 8)
            pygame.draw.circle(surf, (255, 255, 200), (sx, sy), 1)

class DisappearingPlatform:
    """A floating platform that appears, stays solid for a while, then crumbles away."""
    def __init__(self, x, y, width=90):
        self.x = x
        self.y = y
        self.width = width
        self.height = 12
        self.state = 'appearing'  # appearing → solid → warn → crumble → gone
        self.timer = 0
        self.appear_dur = 30     # fade-in frames
        self.solid_dur = 180     # frames it stays solid
        self.warn_dur = 60       # flashing warning before crumble
        self.crumble_dur = 20    # crumble animation
        self.alive = True
        self.alpha = 0
        self.chunks = []  # for crumble particles

    def update(self):
        self.timer += 1
        if self.state == 'appearing':
            self.alpha = min(255, int(255 * self.timer / self.appear_dur))
            if self.timer >= self.appear_dur:
                self.state = 'solid'; self.timer = 0; self.alpha = 255
        elif self.state == 'solid' and self.timer >= self.solid_dur:
            self.state = 'warn'; self.timer = 0
        elif self.state == 'warn' and self.timer >= self.warn_dur:
            self.state = 'crumble'; self.timer = 0
            # Generate crumble chunks
            for i in range(0, self.width, 8):
                self.chunks.append([self.x + i, self.y, random.uniform(-1, 1), random.uniform(0, 2)])
        elif self.state == 'crumble':
            for c in self.chunks:
                c[0] += c[2]; c[1] += c[3]; c[3] += 0.3
            if self.timer >= self.crumble_dur:
                self.alive = False

    def is_solid(self):
        return self.state in ('solid', 'warn')

    def get_rect(self):
        if self.is_solid():
            return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        return pygame.Rect(0, 0, 0, 0)

    def check_player_land(self, player):
        """Check if player should land on this platform (falling down onto it)."""
        if not self.is_solid(): return False
        if player.vy < 0: return False  # going up, don't snap
        px = player.x + player.w / 2
        player_bottom = player.y + player.h
        # Player center must be within platform width
        if not (self.x <= px <= self.x + self.width): return False
        # Player feet must be near the platform top
        if self.y - 8 <= player_bottom <= self.y + self.height + 4:
            return True
        return False

    def draw(self, surf):
        if self.state == 'crumble':
            for c in self.chunks:
                alpha = max(0, 200 - self.timer * 10)
                cs = pygame.Surface((8, self.height), pygame.SRCALPHA)
                pygame.draw.rect(cs, (180, 170, 200, alpha), (0, 0, 8, self.height), border_radius=2)
                surf.blit(cs, (int(c[0]), int(c[1])))
            return
        if not self.alive: return
        x, y, w, h = int(self.x), int(self.y), self.width, self.height
        ps = pygame.Surface((w, h + 6), pygame.SRCALPHA)
        if self.state == 'warn':
            # Flashing red/gold warning
            flash = int((math.sin(self.timer * 0.5) + 1) * 80 + 80)
            color = (flash, min(255, flash // 2 + 40), 40, min(255, self.alpha))
            pygame.draw.rect(ps, color, (0, 0, w, h), border_radius=4)
            # Exclamation
            if self.timer % 12 < 8:
                warn_txt = font_sm.render("!", True, (255, 80, 40))
                surf.blit(warn_txt, (x + w // 2 - warn_txt.get_width() // 2, y - 18))
        else:
            # Normal marble platform
            pygame.draw.rect(ps, (200, 195, 215, self.alpha), (0, 0, w, h), border_radius=4)
            pygame.draw.rect(ps, (170, 165, 185, self.alpha), (2, 3, w - 4, h - 3), border_radius=3)
            # Gold edge on top
            pygame.draw.line(ps, (255, 215, 60, self.alpha), (2, 1), (w - 2, 1), 2)
        surf.blit(ps, (x, y))
        # Subtle glow underneath
        gs = pygame.Surface((w + 10, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(gs, (100, 80, 180, min(40, self.alpha // 4)), gs.get_rect())
        surf.blit(gs, (x - 5, y + h))

# ==========================================
CUTSCENE_SLIDES = [
    {
        'title': 'FASE FINAL',
        'subtitle': 'ODS 16 — Paz, Justiça e Instituições Eficazes',
        'text': '',
    },
    {
        'title': '',
        'subtitle': '',
        'text': 'Hope chega ao epicentro da civilização, a Cidadela da Verdade, '
                'uma metrópole utópica flutuante que remete à estética de Asgard, '
                'com arquitetura em mármore branco e detalhes em ouro.',
    },
    {
        'title': '',
        'subtitle': '',
        'text': 'No entanto, a realidade está sendo ativamente "deletada" pelo Glitch, '
                'que se manifesta como uma nuvem massiva de desinformação vermelha '
                'que distorce a geometria do cenário.',
    },
    {
        'title': '',
        'subtitle': '',
        'text': 'A revelação narrativa atinge seu ponto crítico: o Glitch não é um '
                'vírus externo, mas a personificação das falhas morais e sistêmicas '
                'da humanidade.',
    },
    {
        'title': '',
        'subtitle': '',
        'text': 'O objetivo não é o combate físico, mas a estabilização institucional. '
                'Hope deve navegar pelo caos, provando que a justiça e a transparência '
                'podem restaurar a ordem sobre o erro sistêmico.',
    },
]

font_cutscene = pygame.font.SysFont("Consolas", 16, bold=True)
font_cutscene_sm = pygame.font.SysFont("Consolas", 12)
font_nome = pygame.font.SysFont("Consolas", 20, bold=True)

def wrap_text(text, font, max_width):
    """Break text into lines that fit within max_width."""
    words = text.split(' ')
    lines = []
    current = ''
    for w in words:
        test = current + (' ' if current else '') + w
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current: lines.append(current)
            current = w
    if current: lines.append(current)
    return lines

def draw_cutscene_bg(surf, frame, slide_idx):
    """Draw the Cidadela da Verdade backdrop using the loaded image."""
    if BG_LOADED:
        surf.blit(BG_IMG, (0, 0))
    else:
        # Fallback gradient
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(8 + 20 * t)
            g = int(6 + 10 * t)
            b = int(35 + 30 * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Subtle vignette overlay for cinematic feel
    vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(80):
        alpha = int(i * 1.2)
        pygame.draw.rect(vig, (0, 0, 0, alpha), (0, i, WIDTH, 1))
        pygame.draw.rect(vig, (0, 0, 0, alpha), (0, HEIGHT - i, WIDTH, 1))
    surf.blit(vig, (0, 0))

    # Glitch distortion effect on later slides
    if slide_idx >= 2:
        intensity = min(50, (slide_idx - 1) * 18)
        for _ in range(intensity):
            gx = random.randint(0, WIDTH - 60)
            gy = random.randint(0, HEIGHT)
            gw = random.randint(20, 100)
            gh = random.randint(1, 4)
            gc = (200, 40, 50, random.randint(20, 60))
            gs = pygame.Surface((gw, gh), pygame.SRCALPHA)
            gs.fill(gc)
            surf.blit(gs, (gx, gy))
        # Horizontal scanline shift effect
        if slide_idx >= 3:
            for _ in range(3):
                sy = random.randint(0, HEIGHT - 8)
                sh = random.randint(2, 6)
                shift = random.randint(-8, 8)
                strip = surf.subsurface((0, sy, WIDTH, sh)).copy()
                surf.blit(strip, (shift, sy))

def draw_cutscene(surf, slide_idx, frame, chars_shown):

    draw_cutscene_bg(surf, frame, slide_idx)

    slide = CUTSCENE_SLIDES[slide_idx]

    # overlay escuro
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surf.blit(overlay, (0, 0))

    # ==========================================
    # CAIXA DE DIÁLOGO ESTILO ALDEÕES
    # ==========================================
    if slide['text']:

        box_x = 50
        box_y = HEIGHT - 150
        box_w = WIDTH - 100
        box_h = 100

        # caixa preta
        pygame.draw.rect(
            surf,
            (0, 0, 0),
            (box_x, box_y, box_w, box_h)
        )

        # borda branca
        pygame.draw.rect(
            surf,
            (255, 255, 255),
            (box_x, box_y, box_w, box_h),
            2
        )

        # nome
        nome = font_nome.render(
            "NARRADOR:",
            False,
            (0, 200, 0)
        )

        surf.blit(nome, (box_x + 20, box_y + 10))

        # texto visível (typewriter)
        visible_text = slide['text'][:chars_shown]

        palavras = visible_text.split(' ')
        linhas = []
        linha_atual = ""

        for palavra in palavras:

            teste = linha_atual + (" " if linha_atual else "") + palavra

            if font_cutscene.size(teste)[0] <= box_w - 40:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra

        if linha_atual:
            linhas.append(linha_atual)

        # desenhar linhas
        for i, linha in enumerate(linhas[:3]):

            rendered = font_cutscene.render(
                linha,
                False,
                (180, 180, 180)
            )

            surf.blit(
                rendered,
                (
                    box_x + 20,
                    box_y + 40 + i * 22
                )
            )

    # ==========================================
    # ENTER PARA CONTINUAR
    # ==========================================
    full_len = len(slide['text']) if slide['text'] else 0

    if chars_shown >= full_len:

        inst = font_cutscene_sm.render(
            "Pressione ENTER para continuar...",
            False,
            (100, 100, 100)
        )

        surf.blit(
            inst,
            (
                WIDTH - inst.get_width() - 70,
                HEIGHT - 70
            )
        )

# ==========================================
# GAME LOOP
# ==========================================
def main():
    state = 'title'  # title, cutscene, fight, victory, gameover
    player = Player()
    player.reset_boss_fight(GROUND_Y)
    boss = Boss()
    p_bullets = []
    b_projs = []
    particles = []
    frame = 0
    victory_timer = 0

    # Cutscene state
    cut_slide = 0
    cut_chars = 0
    cut_char_speed = 1  # characters per frame
    cut_ready = False   # True when typewriter finished current slide

    # Level Devil traps + health orbs + platforms
    floor_traps = []
    ceil_spikes = []
    health_orbs = []
    platforms = []
    next_trap_time = 180     # first trap spawns after ~3 sec
    next_orb_time = 400      # first orb spawns after ~6.5 sec
    next_plat_time = 120     # first platform spawns after ~2 sec

    def reset_game():
        nonlocal p_bullets, b_projs, particles, frame, state, victory_timer
        nonlocal floor_traps, ceil_spikes, health_orbs, platforms
        nonlocal next_trap_time, next_orb_time, next_plat_time
        player.reset_boss_fight(GROUND_Y); boss.reset()
        p_bullets.clear(); b_projs.clear(); particles.clear()
        floor_traps.clear(); ceil_spikes.clear(); health_orbs.clear()
        platforms.clear()
        next_trap_time = 300; next_orb_time = 500; next_plat_time = 120
        frame = 0; state = 'fight'; victory_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        frame += 1

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: running = False
            if ev.type == pygame.KEYDOWN:
                if state == 'title' and ev.key == pygame.K_RETURN:
                    state = 'cutscene'; cut_slide = 0; cut_chars = 0; cut_ready = False
                if state == 'cutscene' and ev.key == pygame.K_RETURN:
                    slide = CUTSCENE_SLIDES[cut_slide]
                    full_len = len(slide['text']) if slide['text'] else 0
                    if cut_chars < full_len:
                        cut_chars = full_len  # skip typewriter
                    else:
                        cut_slide += 1
                        cut_chars = 0
                        cut_ready = False
                        if cut_slide >= len(CUTSCENE_SLIDES):
                            reset_game()
                if state == 'victory' and victory_timer > 60:
                    running = False
                elif state == 'gameover' and gameover_timer > 60:
                    state = 'title'

        # ---- RENDER BACKGROUND ----
        render_surf = pygame.Surface((WIDTH, HEIGHT))
        draw_background(render_surf, frame)

        if state == 'cutscene':
            # Update typewriter
            if cut_slide < len(CUTSCENE_SLIDES):
                slide = CUTSCENE_SLIDES[cut_slide]
                full_len = len(slide['text']) if slide['text'] else 0
                if cut_chars < full_len:
                    cut_chars = min(cut_chars + cut_char_speed, full_len)
                render_surf = pygame.Surface((WIDTH, HEIGHT))
                draw_cutscene(render_surf, cut_slide, frame, cut_chars)

        elif state == 'title':
            import math
            import time
            t = time.time()

            render_surf.fill((12, 12, 30))
            for i in range(HEIGHT):
                r = int(15 + i * 0.01)
                g = int(10 + i * 0.015)
                b = int(25 + i * 0.02)
                pygame.draw.line(render_surf, (r, g, b), (0, i), (WIDTH, i))

            RED_THEME = (255, 60, 60)
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((*RED_THEME, 12))
            render_surf.blit(ov, (0, 0))

            title = font_big.render("FASE 5", True, RED_THEME)
            render_surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

            sub = font_sm.render("A VERDADE, A PAZ E A JUSTIÇA (ODS 16)", True, (200, 180, 190))
            render_surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 120))

            box_w, box_h = 460, 260
            box_x = WIDTH // 2 - box_w // 2
            box_y = 170
            pygame.draw.rect(render_surf, (30, 20, 25), (box_x, box_y, box_w, box_h), border_radius=8)
            pygame.draw.rect(render_surf, (*RED_THEME, 80), (box_x, box_y, box_w, box_h), 2, border_radius=8)

            cmd_title = font_sm.render("COMANDOS", True, (255, 100, 100))
            render_surf.blit(cmd_title, (WIDTH // 2 - cmd_title.get_width() // 2, box_y + 12))

            pygame.draw.line(render_surf, (80, 50, 60), (box_x + 20, box_y + 42), (box_x + box_w - 20, box_y + 42), 1)

            commands = [
                ("A / <", "Mover para esquerda"),
                ("D / >", "Mover para direita"),
                ("W / ^", "Pular"),
                ("ESPAÇO", "Dash"),
                ("F", "Atirar"),
            ]
            cy = box_y + 55
            for key, desc in commands:
                kt = font_sm.render(key, True, (255, 150, 150))
                render_surf.blit(kt, (box_x + 30, cy))
                pygame.draw.rect(render_surf, (70, 40, 50), (box_x + 200, cy + 2, 2, 14))
                dt_text = font_sm.render(desc, True, (255, 255, 255))
                render_surf.blit(dt_text, (box_x + 215, cy))
                cy += 38

            obj_y = box_y + box_h + 20
            obj_box = pygame.Rect(box_x, obj_y, box_w, 50)
            from utils import draw_wrapped_objective
            draw_wrapped_objective(
                render_surf, obj_box,
                "OBJETIVO: Derrote a Nuvem de Glitch esquivando dos projéteis e atirando energia reparadora!",
                font_sm, (40, 15, 20), (255, 80, 80, 80), (255, 100, 100)
            )

            pulse = int((math.sin(t * 3) + 1) * 0.5 * 40 + 215)
            enter_text = font_sm.render("Pressione ENTER para iniciar", True, (pulse, pulse, pulse))
            render_surf.blit(enter_text, (WIDTH // 2 - enter_text.get_width() // 2, HEIGHT - 70))
        
        elif state == 'fight':
            # Update
            keys = pygame.key.get_pressed()
            player.update_boss_fight(keys, p_bullets, GROUND_Y, WIDTH, platforms)

            boss.update(player, b_projs, particles)

            # === PHASE TRANSITION HEAL ===
            if boss.phase_just_changed:
                boss.phase_just_changed = False
                if player.hp < PLAYER_MAX_HP:
                    player.hp = min(PLAYER_MAX_HP, player.hp + 2)
                    spawn_hit_particles(particles, player.x + player.w // 2,
                                       player.y + player.h // 2, C_GOLD, 15)

            # === LEVEL DEVIL TRAPS ===
            # Spawn floor traps (phase 1: rare, phase 2+: more frequent)
            if frame >= next_trap_time and boss.alive:
                # Floor trap — avoid spawning right under player
                tw = random.randint(80, 130)
                tx = random.randint(50, WIDTH - tw - 50)
                # Push away from player position
                if abs(tx + tw / 2 - player.x - player.w / 2) < 100:
                    tx = (tx + 200) % (WIDTH - tw - 50)
                floor_traps.append(FloorTrap(tx, tw))
                # Next trap timer — easier in phase 1
                base_cd = {1: 200, 2: 150, 3: 100}
                next_trap_time = frame + base_cd.get(boss.phase, 300) + random.randint(-40, 60)

            # Spawn health orbs periodically
            if frame >= next_orb_time and boss.alive:
                ox = random.randint(80, WIDTH - 200)
                oy = random.randint(GROUND_Y - 180, GROUND_Y - 60)
                health_orbs.append(HealthOrb(ox, oy))
                next_orb_time = frame + random.randint(400, 600)

            # Spawn disappearing platforms
            if frame >= next_plat_time and boss.alive:
                pw = random.randint(70, 120)
                px = random.randint(50, WIDTH - pw - 50)
                py = random.randint(GROUND_Y - 200, GROUND_Y - 80)
                platforms.append(DisappearingPlatform(px, py, pw))
                base_plat_cd = {1: 250, 2: 180, 3: 140}
                next_plat_time = frame + base_plat_cd.get(boss.phase, 200) + random.randint(-30, 50)

            # Update traps
            for ft in floor_traps:
                ft.update()
                if ft.player_falls(player):
                    # Instant death when falling into pit
                    player.hp = 0
                    spawn_hit_particles(particles, player.x + player.w // 2,
                                       GROUND_Y, (200, 50, 40), 20)
                    shake.trigger(6, 12)
            floor_traps = [ft for ft in floor_traps if ft.alive]

            # Update platforms
            for plat in platforms: plat.update()
            platforms = [plat for plat in platforms if plat.alive]

            # Health orb pickup
            for orb in health_orbs:
                orb.update()
                if orb.get_rect().colliderect(player.rect):
                    if player.hp < PLAYER_MAX_HP:
                        player.hp += 1
                        spawn_hit_particles(particles, orb.x, orb.y, C_GOLD, 12)
                    orb.alive = False
            health_orbs = [orb for orb in health_orbs if orb.alive]

            # Player bullets vs Boss
            for b in p_bullets:
                b.update()
                if b.alive and boss.alive and b.rect().colliderect(boss.rect()):
                    if boss.take_damage():
                        spawn_hit_particles(particles, b.x, b.y, (255, 120, 80))
                        shake.trigger(2, 5)
                    b.alive = False
            p_bullets = [b for b in p_bullets if b.alive]

            # Boss projs vs Player
            for p in b_projs:
                p.update()
                if p.alive and p.rect().colliderect(player.rect):
                    if player.take_hit():
                        spawn_hit_particles(particles, player.x + player.w // 2, player.y + player.h // 2, C_HOPE, 12)
                        shake.trigger(5, 10)
                    p.alive = False
            b_projs = [p for p in b_projs if p.alive]

            # Particles
            particles = [p for p in particles if p.update()]

            # Boss ambient particles
            if boss.alive and frame % 6 == 0:
                bx = boss.x + random.randint(10, boss.w - 10)
                by = boss.y + random.randint(10, boss.h - 10)
                c = random.choice([(200, 60, 80), (160, 40, 60), (180, 50, 180)])
                particles.append(Particle(bx, by, c, random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.3), 20, 2))

            # State check
            if boss.hp <= 0 and state != 'victory':
                return 'win'
            if player.hp <= 0 and state != 'gameover':
                return 'gameover'

            # Draw entities
            for plat in platforms: plat.draw(render_surf)
            for ft in floor_traps: ft.draw(render_surf)
            for orb in health_orbs: orb.draw(render_surf)
            for p in particles: p.draw(render_surf)
            for b in p_bullets: b.draw(render_surf)
            for p in b_projs: p.draw(render_surf)
            boss.draw(render_surf)
            player.draw(render_surf)
            draw_hud(render_surf, player.hp, boss.hp, boss.phase, boss.alive)

            # Phase transition text
            if boss.phase_trans > 0:
                txt = font_big.render(f"— FASE {boss.phase} —", True, C_GOLD)
                render_surf.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))

        elif state == 'victory':
            victory_timer += 1
            player.draw(render_surf)
            for p in particles: p.draw(render_surf)
            particles = [p for p in particles if p.update()]
            if victory_timer % 4 == 0:
                particles.append(Particle(random.randint(200, 700), random.randint(100, 400),
                    random.choice([C_GOLD, C_HOPE, C_WHITE]), random.uniform(-2, 2), random.uniform(-3, 0), 40, 4, 0.05))
            ko = font_big.render("VITÓRIA!", True, C_GOLD)
            sub = font_med.render("Pressione qualquer tecla para voltar ao lobby", True, C_WHITE)
            render_surf.blit(ko, (WIDTH // 2 - ko.get_width() // 2, 200))
            if victory_timer > 60:
                render_surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 300))

        elif state == 'gameover':
            gameover_timer += 1
            
            # 1. Mantém o Boss e os Projéteis desenhados ao fundo congelados
            boss.draw(render_surf)
            for p in b_projs: 
                p.draw(render_surf)
            
            # 2. Cortina preta semitransparente por cima da ação (Exatamente como o overlay do Level 3)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Escurece o fundo mantendo o jogo visível por trás
            render_surf.blit(overlay, (0, 0))

            # 3. Texto principal "GAME OVER" gigante em Vermelho Puro (CORES["go"] ou (255, 0, 0))
            go = font_big.render("GAME OVER", True, (255, 0, 0))
            render_surf.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 120))

            # 4. Linha única com o Motivo da derrota centralizado (Exatamente igual ao seu motivo_gameover)
            # Usa cor amarela/ouro para destacar o alerta do erro do sistema
            txt_motivo = font_sm.render("A infraestrutura cibernética colapsou!", True, (255, 200, 50))
            render_surf.blit(txt_motivo, (WIDTH // 2 - txt_motivo.get_width() // 2, HEIGHT // 2 - 30))

            # 5. Texto de reiniciar surgindo após 60 frames com a oscilação por Seno (Pulsante do Level 3)
            if gameover_timer > 60:
                # Modulação usando o próprio gameover_timer para fazer o texto clarear e apagar suavemente
                pulse = int((math.sin(gameover_timer * 0.08) + 1) * 35)
                # Cria o tom cinza-claro/branco que pulsa de forma sutil
                cor_pulse = (min(255, 180 + pulse), min(255, 180 + pulse), min(255, 180 + pulse))
                
                sub = font_med.render("Pressione qualquer tecla para tentar de novo", True, cor_pulse)
                render_surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 50))

        # Apply screen shake
        ox, oy = shake.get_offset()
        screen.fill((0, 0, 0))
        screen.blit(render_surf, (ox, oy))
        pygame.display.flip()
        
    return state == 'victory'

class Level5Boss:
    def __init__(self):
        self.w = 1280
        self.h = 720
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

def run_level_5():
    import pygame
    orig_quit = pygame.quit
    pygame.quit = lambda: None
    try:
        while True:
            status = main()
            if status == 'quit' or status is False:
                return False
            elif status == 'win':
                from utils import show_end_screen
                show_end_screen(
                    pygame.display.get_surface(), pygame.time.Clock(),
                    "VITÓRIA!", "Paz e Justiça restauradas!",
                    (34, 255, 136), "CONTINUAR",
                    stats=None,
                    lesson="Instituições fortes e justiça são a base para o desenvolvimento sustentável."
                )
                return True
            elif status == 'gameover':
                from utils import show_end_screen
                show_end_screen(
                    pygame.display.get_surface(), pygame.time.Clock(),
                    "GAME OVER", "A infraestrutura cibernética colapsou!",
                    (255, 34, 68), "TENTAR DE NOVO",
                    stats=None
                )
                continue
            else:
                return False
    except SystemExit:
        return False
    except Exception as e:
        print(f"Erro ao executar Level 5: {e}")
        return False
    finally:
        pygame.quit = orig_quit