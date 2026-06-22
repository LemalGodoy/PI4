import pygame, sys, math, random, time
import os

from entities import Player as EnginePlayer

pygame.init()
W, H = 1280, 720
screen = pygame.display.get_surface()
if screen is None:
    try:
        screen = pygame.display.set_mode((W, H), pygame.RESIZABLE | pygame.SCALED)
    except pygame.error:
        screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Level 2 — ODS 9")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 22, bold=True)
font_t = pygame.font.SysFont("consolas", 18, bold=True)
font_e = pygame.font.SysFont("consolas", 22, bold=True)
font_big = pygame.font.SysFont("consolas", 48, bold=True)
font_med = pygame.font.SysFont("consolas", 24, bold=True)

BG = (15, 18, 25)
STEEL = (60, 65, 80)
STEEL_D = (40, 44, 55)
RUST = (139, 69, 19)
ORANGE = (255, 107, 44)
AMBER = (255, 170, 0)
RED = (255, 34, 68)
GREEN = (34, 255, 136)
CYAN = (0, 212, 255)
SMOKE_C = (50, 55, 65)
WHITE = (230, 234, 240)
DARK = (10, 12, 16)
PURPLE = (139, 0, 255)

GRAVITY = 0.6
LEVEL_W = 5000
CAM_X = 0

platforms = [
    (0, 670, 300, 50, 'solid'), (350, 620, 120, 20, 'break'), (520, 570, 150, 20, 'solid'),
    (720, 520, 100, 20, 'break'), (870, 470, 180, 20, 'solid'), (1100, 520, 80, 20, 'move_h'),
    (1250, 470, 150, 20, 'solid'), (1450, 420, 100, 20, 'break'), (1600, 470, 200, 20, 'solid'),
    (1850, 520, 80, 20, 'move_v'), (2000, 420, 150, 20, 'solid'), (2200, 470, 100, 20, 'break'),
    (2350, 420, 180, 20, 'solid'), (2580, 370, 100, 20, 'move_h'), (2750, 420, 150, 20, 'solid'),
    (2950, 470, 120, 20, 'break'), (3100, 420, 200, 20, 'solid'), (3350, 370, 80, 20, 'move_v'),
    (3500, 420, 150, 20, 'solid'), (3700, 470, 100, 20, 'break'), (3850, 420, 180, 20, 'solid'),
    (4050, 370, 120, 20, 'move_h'), (4250, 420, 200, 20, 'solid'), (4500, 470, 100, 20, 'break'),
    (4650, 420, 300, 50, 'solid'),
]

smoke_zones = [
    (400, 370, 200, 300), (1200, 320, 250, 350), (2100, 270, 300, 400),
    (3000, 320, 250, 350), (3900, 270, 200, 400),
]
chimneys_per_zone = [
    [(70, 200)],
    [(120, 300)],
    [(140, 260)],
    [(110, 350)],
    [(90, 380)],
]

machines = [
    (880, 120, 60, 350), (1650, 70, 60, 400), (2400, 70, 50, 350),
    (3150, 40, 60, 380), (4300, 70, 50, 350),
]

GOAL_X = 4770

# Filter collectibles: (x, y) positions in world (1 per chimney zone)
filter_items = [
    (250, 630), (1250, 430), (2100, 380),
    (3100, 380), (3850, 380),
]
# Track which chimneys have filters: chimney_filtered[zone_idx][chimney_idx]
chimney_filtered = [[False]*len(c) for c in chimneys_per_zone]

class SmokeParticle:
    def __init__(self, x, y):
        self.x = x + random.randint(-40, 40)
        self.y = y + random.randint(-20, 20)
        self.r = random.randint(6, 18)
        self.life = random.uniform(1.5, 3.0)
        self.max_life = self.life
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1.5, -0.3)
    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.life -= dt
        return self.life > 0
    def draw(self, surf, cx):
        a = max(0, int(80 * (self.life / self.max_life)))
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*SMOKE_C, a), (self.r, self.r), self.r)
        surf.blit(s, (self.x - cx - self.r, self.y - self.r))

class Player(EnginePlayer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 5
        self.toxicity = 0
        self.alive = True
        self.blink = 0
        self.filters = 0
        self.w, self.h = self.rect.width, self.rect.height

    def update_level2(self, keys, plats, dt, t):
        # 1. Movimento Horizontal das Teclas
        mov = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: mov -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: mov += 1
        
        # 2. Pulo Buffer
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jumpBuffer = 0.15

        # 3. Preparar retângulos para colisão padrão da engine
        plat_rects = []
        for p in plats:
            if p['active']:
                # Não tratamos breaking platform timer aqui, tratamos depois
                plat_rects.append(pygame.Rect(p['x'], p['y'], p['w'], p['h']))

        # 4. Chamar física nativa do EnginePlayer (inclui fase 5 / 1 movement)
        self.update_platform(dt, keys, mov, H + 200, LEVEL_W, plat_rects, chao_ativo=False)

        # 5. Adições customizadas da Fase 2: Plataformas Móveis (deslocamento) e Quebradiças
        for p in plats:
            if not p['active']: continue
            pr = pygame.Rect(p['x'], p['y'], p['w'], p['h'])
            
            # Se o player está em cima da plataforma
            if self.rect.bottom == pr.top and self.rect.right > pr.left and self.rect.left < pr.right:
                if p['type'] == 'move_h':
                    self.pos_x += math.cos(t * 1.5) * 1.5 * 80 * dt
                    self.rect.x = int(self.pos_x)
                if p['type'] == 'break':
                    if p['timer'] is None: p['timer'] = p['max_timer']

        if self.rect.y > 720 + 100: self.health = 0
        if self.health <= 0: self.alive = False
        self.blink = max(0, self.blink - 1)

    def draw_custom(self, surf, cx, t):
        if self.blink > 0 and self.frame_index % 4 < 2: return
        
        # Desenhar sprite do jogador padrão
        self.draw_at(surf, self.rect.x - cx, self.rect.y)
        
        # Desenhar máscara de toxicidade por cima se aplicável
        if self.toxicity > 10:
            mask_alpha = min(200, int(self.toxicity * 3))
            ms = pygame.Surface((16, 8), pygame.SRCALPHA)
            pygame.draw.rect(ms, (80, 90, 80, mask_alpha), (0, 0, 16, 8), border_radius=2)
            pygame.draw.rect(ms, (60, 70, 60, mask_alpha), (0, 0, 16, 8), 1, border_radius=2)
            pygame.draw.circle(ms, (50, 60, 50, mask_alpha), (4, 4), 3)
            pygame.draw.circle(ms, (50, 60, 50, mask_alpha), (12, 4), 3)
            
            # Ajuste da máscara dependendo para onde olha
            ox = self.rect.x - cx + (18 if self.facing == 'right' else 6)
            oy = self.rect.y + 16
            surf.blit(ms, (ox, oy))

def make_plats():
    result = []
    for x, y, w, h, t in platforms:
        p = {'x':x,'y':y,'w':w,'h':h,'type':t,'active':True,'orig_x':x,'orig_y':y,'timer':None,'max_timer':0.6,'shake':0}
        result.append(p)
    return result

def draw_bg(surf, cx):
    surf.fill(BG)
    for i in range(0, H, 2):
        r = int(15 + i*0.02)
        g = int(18 + i*0.01)
        b = int(25 + i*0.03)
        pygame.draw.rect(surf, (r,g,b), (0, i, W, 2))
    t = time.time()
    for i in range(30):
        bx = i * 250 - cx * 0.15
        bh = 150 + (i*37)%200
        by = H - bh
        if bx + 160 < 0 or bx > W: continue
        pygame.draw.rect(surf, (25,28,38), (bx, by, 80, bh))
        pygame.draw.rect(surf, (30,33,45), (bx+90, by+40, 60, bh-40))
        for wy in range(int(by)+10, H-20, 25):
            for wx in range(int(bx)+5, int(bx)+75, 18):
                glow = 40 + int(20*math.sin(t+i*2+wy*0.05))
                pygame.draw.rect(surf, (glow, max(0,glow-10), 10), (wx, wy, 8, 12))
    for i in range(15):
        sx = i * 350 + 50 - cx * 0.25
        if sx + 30 < 0 or sx > W: continue
        pygame.draw.rect(surf, (35,38,48), (sx, H-280, 20, 280))
        pygame.draw.rect(surf, (40,43,53), (sx-5, H-290, 30, 15))
    for i in range(25):
        px = i * 220 - cx * 0.35
        py = 350 + (i*43)%100
        if px + 200 < 0 or px > W: continue
        pygame.draw.line(surf, (50,54,65), (int(px), py), (int(px)+200, py), 4)
        pygame.draw.circle(surf, (60,64,75), (int(px), py), 8)
        pygame.draw.circle(surf, (60,64,75), (int(px)+200, py), 8)
    for i in range(-1, W//60 + 3):
        gx = i * 60 - (cx*0.8) % 60
        pygame.draw.polygon(surf, (40,15,10), [(gx, H), (gx+30, H-15), (gx+60, H)])

def draw_plat(surf, p, cx):
    if not p['active']: return
    x, y = p['x']-cx, p['y']
    if x > W+50 or x+p['w'] < -50: return
    shake = 0
    if p['type'] == 'break' and p['timer'] is not None and p['timer'] < 0.6:
        shake = random.randint(-2, 2)
    if p['type'] == 'solid':
        pygame.draw.rect(surf, STEEL, (x, y+shake, p['w'], p['h']))
        pygame.draw.rect(surf, (70,75,90), (x, y+shake, p['w'], 3))
        for bx in range(int(x)+8, int(x+p['w'])-8, 20):
            pygame.draw.circle(surf, (50,54,65), (bx, int(y)+10+shake), 2)
    elif p['type'] == 'break':
        if p['timer'] is not None:
            progress = 1.0 - (p['timer'] / p['max_timer'])
            alpha = max(30, int(255 * (1.0 - progress * 0.8)))
            shake = int(progress * 5)
            cr = int(120 + progress * 100)
            cg = int(80 - progress * 60)
            cb = int(40 - progress * 30)
        else:
            alpha = 255
            shake = 0
            cr, cg, cb = 120, 80, 40
        shk = random.randint(-shake, shake) if shake > 0 else 0
        ps = pygame.Surface((int(p['w']), int(p['h'])), pygame.SRCALPHA)
        pygame.draw.rect(ps, (cr, cg, cb, alpha), (0, 0, p['w'], p['h']))
        pygame.draw.rect(ps, (min(255,cr+20), min(255,cg+15), min(255,cb+10), alpha), (0, 0, p['w'], 3))
        if p['timer'] is not None:
            num_cracks = int(3 + progress * 5)
            for i in range(num_cracks):
                cx1 = random.randint(3, int(p['w'])-3)
                pygame.draw.line(ps, (80, 40, 20, alpha), (cx1, 0), (cx1+random.randint(-10,10), int(p['h'])), 1+int(progress*2))

        surf.blit(ps, (x, y + shk))
    elif p['type'] in ('move_h','move_v'):
        pygame.draw.rect(surf, CYAN[:3], (x, y, p['w'], p['h']))
        pygame.draw.rect(surf, (0,180,220), (x, y, p['w'], 3))
        if p['type'] == 'move_h':
            pygame.draw.polygon(surf, WHITE, [(x+5, y+10), (x+12, y+6), (x+12, y+14)])
            pygame.draw.polygon(surf, WHITE, [(x+p['w']-5, y+10), (x+p['w']-12, y+6), (x+p['w']-12, y+14)])

def get_crush_rect(m, t):
    """Get the crusher hitbox in world coordinates (no screen culling)."""
    x, y, w, h = m
    cycle = (math.sin(t * 5.0) + 1) / 2
    crush_y = y + int(cycle * (h - 30))
    return pygame.Rect(x - 8, crush_y, w + 16, 30)

def draw_machine(surf, m, cx, t):
    x, y, w, h = m
    sx = x - cx
    if sx > W+80 or sx+w < -80: return
    cycle = (math.sin(t * 5.0) + 1) / 2  # 0 to 1
    crush_y = y + int(cycle * (h - 30))
    pygame.draw.rect(surf, (50, 30, 30), (sx, y, w, h))
    pygame.draw.rect(surf, (70, 40, 35), (sx+2, y, w-4, h))
    pygame.draw.rect(surf, RED, (sx-8, crush_y, w+16, 30))
    pygame.draw.rect(surf, (200, 20, 40), (sx-8, crush_y, w+16, 5))
    for i in range(0, w+16, 10):
        pygame.draw.line(surf, AMBER, (sx-8+i, crush_y+25), (sx-8+i+5, crush_y+30), 2)

def draw_chimney(surf, cx, zone_x, chimney, t, filtered=False):
    off_x, ch_h = chimney
    cx_pos = zone_x + off_x - cx
    ch_w = 30
    ch_y = H - ch_h
    if cx_pos + ch_w < -50 or cx_pos > W + 50: return
    pygame.draw.rect(surf, (55, 50, 45), (cx_pos, ch_y, ch_w, ch_h))
    for by in range(int(ch_y) + 5, H, 20):
        pygame.draw.line(surf, (45, 40, 35), (int(cx_pos), by), (int(cx_pos) + ch_w, by), 1)
    pygame.draw.rect(surf, (70, 60, 50), (cx_pos - 4, ch_y - 6, ch_w + 8, 10))
    pygame.draw.rect(surf, (80, 70, 55), (cx_pos - 4, ch_y - 6, ch_w + 8, 3))
    if filtered:
        # Green filter cap on top
        pygame.draw.rect(surf, (30, 180, 60), (cx_pos - 6, ch_y - 14, ch_w + 12, 12), border_radius=3)
        pygame.draw.rect(surf, (40, 220, 80), (cx_pos - 6, ch_y - 14, ch_w + 12, 3), border_radius=3)
        # Grid lines on filter
        for gx in range(int(cx_pos) - 4, int(cx_pos) + ch_w + 4, 6):
            pygame.draw.line(surf, (20, 140, 40), (gx, int(ch_y)-13), (gx, int(ch_y)-4), 1)

    else:
        blink = int((math.sin(t * 4 + off_x) + 1) * 0.5 * 200 + 55)
        pygame.draw.circle(surf, (blink, 20, 20), (int(cx_pos + ch_w // 2), int(ch_y - 10)), 4)
        for i in range(3):
            wy = ch_y - 15 - i * 12
            wx = cx_pos + ch_w // 2 + math.sin(t * 2 + i * 1.5 + off_x) * 10
            wr = 8 + i * 5
            ws = pygame.Surface((wr*2, wr*2), pygame.SRCALPHA)
            pygame.draw.circle(ws, (*SMOKE_C, 60 - i * 15), (wr, wr), wr)
            surf.blit(ws, (int(wx) - wr, int(wy) - wr))
    if not filtered:
        et = font_e.render("E", True, GREEN)
        surf.blit(et, (cx_pos + 8, ch_y - 35))

def draw_filter_item(surf, fx, fy, cx, t):
    sx = fx - cx
    if sx < -30 or sx > W + 30: return
    bob = math.sin(t * 3) * 4
    gs = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(gs, (34, 255, 136, 70), (20, 20), 18)

    filter_x = int(sx) - 2
    filter_y = int(fy + bob)

    glow_x = filter_x + 10 - 20
    glow_y = filter_y + 7 - 20

    surf.blit(gs, (glow_x, glow_y))

    # Filter body
    pygame.draw.rect(surf, (40, 200, 80), (int(sx) - 2, int(fy + bob), 20, 14), border_radius=3)
    pygame.draw.rect(surf, (60, 240, 100), (int(sx) - 2, int(fy + bob), 20, 3), border_radius=3)
    # Grid
    for gx in range(int(sx), int(sx) + 16, 4):
        pygame.draw.line(surf, (30, 160, 60), (gx, int(fy+bob)+3), (gx, int(fy+bob)+12), 1)


def zone_active(zone_idx):
    return any(not f for f in chimney_filtered[zone_idx])

def draw_smoke_zone(surf, zone, zone_idx, cx, t):
    x, y, w, h = zone
    sx = x - cx
    if sx > W+100 or sx+w < -100: return
    for ci, chimney in enumerate(chimneys_per_zone[zone_idx]):
        draw_chimney(surf, cx, x, chimney, t, chimney_filtered[zone_idx][ci])
    if zone_active(zone_idx):
        active_count = sum(1 for f in chimney_filtered[zone_idx] if not f)
        total = len(chimney_filtered[zone_idx])
        ratio = active_count / total
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = int((35 + 20 * math.sin(t * 0.8 + zone_idx)) * ratio)
        s.fill((*SMOKE_C, alpha))
        surf.blit(s, (sx, y))
        pygame.draw.rect(surf, (*PURPLE, 60), (sx, y, w, 2))

def draw_goal(surf, cx, t):
    gx = GOAL_X - cx
    glow = int(40 + 30 * math.sin(t*3))
    pygame.draw.rect(surf, (0, glow+80, 0), (gx, 320, 60, 100))
    pygame.draw.rect(surf, GREEN, (gx, 320, 60, 100), 3)
    ay = 310 + int(math.sin(t*4)*8)
    pygame.draw.polygon(surf, GREEN, [(gx+30, ay), (gx+15, ay+15), (gx+45, ay+15)])
    txt = font_t.render("SAÍDA", True, GREEN)
    surf.blit(txt, (gx+10, 300))

def draw_hud(surf, player, elapsed, progress):
    from utils import draw_health_bar
    draw_health_bar(surf, player.health, 5, 10, 10)
    hb_x, hb_w = 10, 200
    
    tb_y = 10 + 22
    pygame.draw.rect(surf, (30,33,40), (hb_x, tb_y, hb_w, 10), border_radius=3)
    tw = max(0, int(hb_w * player.toxicity / 100))
    pygame.draw.rect(surf, PURPLE, (hb_x, tb_y, tw, 10), border_radius=3)
    txt = font.render(f"TOXICIDADE", True, (170, 68, 255))
    surf.blit(txt, (hb_x, tb_y + 12))

    mins = int(elapsed) // 60
    secs = int(elapsed) % 60
    ttxt = font.render(f"TEMPO {mins:02d}:{secs:02d}", True, AMBER)
    surf.blit(ttxt, (W - 180, 10))

    pb_x = W - 180
    pygame.draw.rect(surf, (30,33,40), (pb_x, 32, 160, 10), border_radius=3)
    pw = int(160 * progress)
    pygame.draw.rect(surf, CYAN, (pb_x, 32, pw, 10), border_radius=3)
    ptxt = font.render(f"PROGRESSO {int(progress*100)}%", True, CYAN)
    surf.blit(ptxt, (pb_x, 44))

    # Filter inventory
    fi_y = tb_y + 28
    pygame.draw.rect(surf, (30, 80, 40), (hb_x, fi_y, 20, 14), border_radius=2)
    pygame.draw.rect(surf, (50, 120, 60), (hb_x, fi_y, 20, 3), border_radius=2)
    ft = font.render(f"FILTROS x{player.filters}", True, GREEN)
    surf.blit(ft, (hb_x + 24, fi_y - 1))
    # Filtered chimneys count
    total_ch = sum(len(c) for c in chimneys_per_zone)
    done_ch = sum(sum(1 for f in zone if f) for zone in chimney_filtered)
    ct = font.render(f"CHAMINÉS {done_ch}/{total_ch}", True, (100, 200, 120))
    surf.blit(ct, (hb_x, fi_y + 16))


def game_loop():
    global CAM_X, chimney_filtered
    chimney_filtered = [[False]*len(c) for c in chimneys_per_zone]
    player = Player(50, 560)
    plats = make_plats()
    smoke_particles = []
    active_filters = [list(f) for f in filter_items]  # copies
    start_time = time.time()
    t = 0
    use_filter_pressed = False
    goal_warn_timer = 0

    while player.alive:
        dt = clock.tick(60) / 1000.0
        t += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return 'quit'
                if e.key in (pygame.K_e, pygame.K_LEFTBRACKET): use_filter_pressed = True

        keys = pygame.key.get_pressed()

        for p in plats:
            if p['type'] == 'move_h' and p['active']:
                p['x'] = p['orig_x'] + math.sin(t * 1.5) * 80
            elif p['type'] == 'move_v' and p['active']:
                p['y'] = p['orig_y'] + math.sin(t * 1.2) * 60
            if p['type'] == 'break' and p['timer'] is not None:
                p['timer'] -= dt
                if random.random() < 0.4:
                    debris_x = p['x'] + random.randint(0, int(p['w']))
                    debris_y = p['y'] + p['h']
                    smoke_particles.append(SmokeParticle(debris_x, debris_y))
                if p['timer'] <= 0:
                    p['active'] = False

        for p in plats:
            if p['active'] and p['type'] in ('move_h','move_v'):
                pr = pygame.Rect(p['x'], p['y']-2, p['w'], 4)
                if player.rect.colliderect(pr) and player.velY >= 0:
                    if p['type'] == 'move_h':
                        pass # horizontal moving handled in update_level2
                    elif p['type'] == 'move_v':
                        pass

        player.update_level2(keys, plats, dt, t)

        # Collect filters
        pr = player.rect
        for fi in active_filters[:]:
            fr = pygame.Rect(fi[0]-2, fi[1], 20, 14)
            if pr.colliderect(fr):
                player.filters += 1
                active_filters.remove(fi)

        # Use filter on chimney (press E)
        if use_filter_pressed and player.filters > 0:
            use_filter_pressed = False
            best_dist = 80
            best = None
            for zi, zone in enumerate(smoke_zones):
                for ci, chimney in enumerate(chimneys_per_zone[zi]):
                    if chimney_filtered[zi][ci]: continue
                    ch_x = zone[0] + chimney[0] + 15
                    ch_y_top = H - chimney[1]
                    dx = abs(player.rect.x + player.w // 2 - ch_x)
                    dy = abs(player.rect.y + player.h // 2 - ch_y_top)
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < best_dist:
                        best_dist = dist
                        best = (zi, ci)
            if best:
                chimney_filtered[best[0]][best[1]] = True
                player.filters -= 1
        else:
            use_filter_pressed = False

        target_cx = player.rect.x - W * 0.35
        CAM_X += (target_cx - CAM_X) * 0.08
        CAM_X = max(0, min(CAM_X, LEVEL_W - W))

        in_smoke = False
        for zi, zone in enumerate(smoke_zones):
            if not zone_active(zi): continue
            zr = pygame.Rect(zone[0], zone[1], zone[2], zone[3])
            if player.rect.colliderect(zr):
                active_ratio = sum(1 for f in chimney_filtered[zi] if not f) / len(chimney_filtered[zi])
                in_smoke = True
                player.health -= 0.6 * dt * active_ratio
                player.toxicity = min(100, player.toxicity + 18 * dt * active_ratio)
                player.blink = 3

        if not in_smoke:
            player.toxicity = max(0, player.toxicity - 5 * dt)

        for zi, zone in enumerate(smoke_zones):
            for ci, chimney in enumerate(chimneys_per_zone[zi]):
                if chimney_filtered[zi][ci]: continue
                if random.random() < 0.25:
                    ch_x = zone[0] + chimney[0] + 15
                    ch_top = H - chimney[1]
                    smoke_particles.append(SmokeParticle(ch_x, ch_top - 10))
        smoke_particles = [sp for sp in smoke_particles if sp.update(dt)]
        if len(smoke_particles) > 200:
            smoke_particles = smoke_particles[-200:]

        for m in machines:
            cr = get_crush_rect(m, t)
            if player.rect.colliderect(cr):
                player.health = 0
                player.alive = False

        progress = max(0, min(1, player.rect.x / GOAL_X))
        all_filtered = all(all(f for f in zone) for zone in chimney_filtered)
        if player.rect.x >= GOAL_X:
            if all_filtered:
                elapsed = time.time() - start_time
                return ('win', player.health, elapsed, progress)
            else:
                # Block exit — push player back and show warning
                player.rect.x = GOAL_X - 30
                player.pos_x = float(player.rect.x)
                goal_warn_timer = 180  # frames to show warning

        draw_bg(screen, CAM_X)

        for zi, zone in enumerate(smoke_zones):
            draw_smoke_zone(screen, zone, zi, CAM_X, t)

        for sp in smoke_particles:
            sp.draw(screen, CAM_X)

        for p in plats:
            draw_plat(screen, p, CAM_X)

        # Filter items
        for fi in active_filters:
            draw_filter_item(screen, fi[0], fi[1], CAM_X, t)

        for m in machines:
            draw_machine(screen, m, CAM_X, t)

        draw_goal(screen, CAM_X, t)

        player.draw_custom(screen, CAM_X, t)

        if in_smoke:
            dark_alpha = min(230, int(100 + player.toxicity * 1.3))
            radius = max(50, 180 - int(player.toxicity * 1.4))
            px, py = int(player.rect.x - CAM_X + player.w // 2), int(player.rect.y + player.h // 2)
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((15, 20, 25, dark_alpha))
            for r in range(radius, 0, -2):
                frac = r / radius
                hole_alpha = int(dark_alpha * (1 - frac * frac))
                pygame.draw.circle(ov, (15, 20, 25, hole_alpha), (px, py), r)
            pygame.draw.circle(ov, (0, 0, 0, 0), (px, py), max(10, radius // 4))
            screen.blit(ov, (0, 0))
            tint = pygame.Surface((W, H), pygame.SRCALPHA)
            tint.fill((0, 255, 50, int(player.toxicity * 0.3)))
            screen.blit(tint, (0, 0))

        if player.health < 2:
            vig = pygame.Surface((W, H), pygame.SRCALPHA)
            va = int((1 - player.health/2.0) * 100)

            screen.blit(vig, (0,0))

        elapsed = time.time() - start_time
        draw_hud(screen, player, elapsed, progress)

        # Warning when trying to exit without all filters
        if goal_warn_timer > 0:
            goal_warn_timer -= 1
            total_ch = sum(len(c) for c in chimneys_per_zone)
            done_ch = sum(sum(1 for f in zone if f) for zone in chimney_filtered)
            warn_alpha = min(255, goal_warn_timer * 3)
            ws = pygame.Surface((W, H), pygame.SRCALPHA)
            wr = pygame.Rect(W // 2 - 240, H // 2 - 40, 480, 80)
            pygame.draw.rect(ws, (40, 10, 10, warn_alpha), wr, border_radius=8)
            pygame.draw.rect(ws, (255, 34, 68, warn_alpha), wr, 2, border_radius=8)
            wt1 = font_med.render("SAÍDA BLOQUEADA!", True, RED)
            wt2 = font.render(f"Instale filtros em todas as chaminés ({done_ch}/{total_ch})", True, AMBER)
            ws.blit(wt1, (wr.centerx - wt1.get_width() // 2, wr.y + 12))
            ws.blit(wt2, (wr.centerx - wt2.get_width() // 2, wr.y + 48))
            screen.blit(ws, (0, 0))

        pygame.display.flip()

    elapsed = time.time() - start_time
    progress = max(0, min(1, player.rect.x / GOAL_X))
    return ('dead', player.health, elapsed, progress)

def draw_menu():
    """Tela de menu inicial com comandos. Só avança ao pressionar Enter."""
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                waiting = False

        screen.fill(DARK)
        # Fundo com gradiente sutil
        for i in range(H):
            r = int(10 + i * 0.015)
            g = int(12 + i * 0.01)
            b = int(16 + i * 0.025)
            pygame.draw.line(screen, (r, g, b), (0, i), (W, i))

        # Overlay colorido
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((*ORANGE[:3], 12))
        screen.blit(ov, (0, 0))

        t = time.time()

        # Título
        title = font_big.render("FASE 2", True, ORANGE)
        screen.blit(title, (W // 2 - title.get_width() // 2, 60))

        sub = font_med.render("A POLUIÇÃO NA CIDADE (ODS 9 e 13)", True, (180, 184, 200))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 120))

        # Caixa de comandos
        box_w, box_h = 460, 260
        box_x = W // 2 - box_w // 2
        box_y = 170
        pygame.draw.rect(screen, (20, 24, 35), (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, (*ORANGE, 80), (box_x, box_y, box_w, box_h), 2, border_radius=8)

        # Título da caixa
        cmd_title = font_med.render("COMANDOS", True, AMBER)
        screen.blit(cmd_title, (W // 2 - cmd_title.get_width() // 2, box_y + 12))

        # Separador
        pygame.draw.line(screen, (60, 65, 80), (box_x + 20, box_y + 42), (box_x + box_w - 20, box_y + 42), 1)

        # Lista de comandos
        commands = [
            ("A / <", "Mover para esquerda"),
            ("D / >", "Mover para direita"),
            ("W / ^", "Pular"),
            ("E", "Colocar filtro"),
            ("ALT + F4", "Sair da fase"),
        ]
        cy = box_y + 55
        for key, desc in commands:
            # Tecla
            kt = font_e.render(key, True, CYAN)
            screen.blit(kt, (box_x + 30, cy))
            # Separador
            pygame.draw.rect(screen, (50, 55, 70), (box_x + 200, cy + 2, 2, 14))
            # Descrição
            dt_text = font.render(desc, True, WHITE)
            screen.blit(dt_text, (box_x + 215, cy))
            cy += 32

        # Objetivo
        obj_y = box_y + box_h + 20
        obj_box = pygame.Rect(box_x, obj_y, box_w, 50)
        from utils import draw_wrapped_objective
        draw_wrapped_objective(
            screen, obj_box,
            "OBJETIVO: Colete filtros e instale nas chaminés para limpar a fumaça tóxica e alcançar a SAÍDA!",
            font, (15, 40, 25), (*GREEN[:3], 80), GREEN
        )

        # Botão Enter pulsante
        pulse = int((math.sin(t * 3) + 1) * 0.5 * 40 + 215)
        enter_text = font_med.render("Pressione ENTER para iniciar", True, (pulse, pulse, pulse))
        screen.blit(enter_text, (W // 2 - enter_text.get_width() // 2, H - 70))

        pygame.display.flip()
        clock.tick(30)

def main():
    draw_menu()
    won = False
    while True:
        result = game_loop()
        if result == 'quit':
            won = False
            break
        status, health, elapsed, progress = result
        mins = int(elapsed)//60
        secs = int(elapsed)%60

        from utils import show_end_screen
        if status == 'win':
            show_end_screen(
                screen, clock,
                "COMPLETO!", "Complexo superado!",
                GREEN, "CONTINUAR",
                stats={"Saúde Final": f"{int(health)}%", "Tempo": f"{mins:02d}:{secs:02d}"},
                lesson="Industrialização sustentável e inovação para um futuro melhor."
            )
            won = True
            break
        else:
            show_end_screen(
                screen, clock,
                "GAME OVER", "Contaminação letal",
                RED, "TENTAR DE NOVO",
                stats={"Progresso": f"{int(progress*100)}%", "Tempo": f"{mins:02d}:{secs:02d}"}
            )

    return won

if __name__ == "__main__":
    main()
    pygame.quit()

def run_level_2():
    import pygame
    orig_quit = pygame.quit
    pygame.quit = lambda: None
    try:
        won = main()
        return bool(won)
    except SystemExit:
        return False
    except Exception as e:
        print(f"Erro ao executar Level 2: {e}")
        return False
    finally:
        pygame.quit = orig_quit
