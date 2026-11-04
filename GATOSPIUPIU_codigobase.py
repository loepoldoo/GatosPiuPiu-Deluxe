# --- SHOOTER DE GATOS: GATOSPIUPIU DELUXE ---
import math
import random
import sys
import pygame

pygame.init()
pygame.font.init()

FONT_SMALL = pygame.font.SysFont('consolas', 12, bold=True)
FONT = pygame.font.SysFont('consolas', 16, bold=True)
FONT_BIG = pygame.font.SysFont('consolas', 36, bold=True)

# --- GATOS: (fuerza, agilidad, salto, vida) ---
GATOS = {
    'Gato naranja': (7, 8, 7, 100),
    'Gato negro': (4, 10, 9, 75),
    'Gato gordo': (9, 3, 4, 175),
    'Gato calvo': (5, 9, 6, 85),
    'Gato Siames': (6, 7, 10, 90),
}

# --- DICCIONARIO DE ARMAS DELUXE ---
armas_info = {
    'bigotito_pum': {
        'nombre': 'Bigotito Pum', 'tipo': 'Pistola', 'dano': 18,
        'cadencia': 260, 'velocidad_bala': 15, 'municion_max': 150, 'recarga_balas': 28
    },
    'subgatil': {
        'nombre': 'Subgatil', 'tipo': 'Subfusil', 'dano': 9,
        'cadencia': 95, 'velocidad_bala': 18, 'municion_max': 360, 'recarga_balas': 70
    },
    'miaufusil': {
        'nombre': 'Miaufusil', 'tipo': 'Asalto', 'dano': 17,
        'cadencia': 165, 'velocidad_bala': 17, 'municion_max': 240, 'recarga_balas': 44
    },
    'desnuca_ratones': {
        'nombre': 'Desnuca-ratones', 'tipo': 'Escopeta', 'dano': 13,
        'cadencia': 800, 'velocidad_bala': 14, 'municion_max': 56, 'recarga_balas': 12, 'b': 7, 'sp': 11, 'alcance': 600
    },
    'ronroneadora': {
        'nombre': 'Ronroneadora', 'tipo': 'Sniper', 'dano': 105,
        'cadencia': 1050, 'velocidad_bala': 28, 'municion_max': 34, 'recarga_balas': 7
    },
    'gatozooka': {
        'nombre': 'Gatozooka', 'tipo': 'Bazuca', 'dano': 160,
        'cadencia': 1200, 'velocidad_bala': 11, 'municion_max': 26, 'recarga_balas': 5, 'ex': 110
    },
    'ballesta': {
        'nombre': 'Ballesta Maullante', 'tipo': 'Ballesta', 'dano': 105,
        'cadencia': 620, 'velocidad_bala': 21, 'municion_max': 44, 'recarga_balas': 9
    },
    'laser': {
        'nombre': 'Láser Ronrón', 'tipo': 'Láser', 'dano': 7,
        'cadencia': 75, 'velocidad_bala': 30, 'municion_max': 450, 'recarga_balas': 100, 'alcance': 1000
    },
    'fuego': {
        'nombre': 'Lanzallamas Colita', 'tipo': 'Fuego', 'dano': 4.5,
        'cadencia': 42, 'velocidad_bala': 11, 'municion_max': 560, 'recarga_balas': 130, 'alcance': 260
    },
    'doble': {
        'nombre': 'Doble Miau', 'tipo': 'Dobles', 'dano': 10,
        'cadencia': 115, 'velocidad_bala': 19, 'municion_max': 190, 'recarga_balas': 36, 'b': 2, 'sp': 5
    },
}

# --- SISTEMA DE RAREZAS Y ELEMENTOS v3.0 ---
RR = [
    {'n': 'Común', 'c': (230, 230, 230), 'dm': 1.0, 'cs': 1.0, 'el': 0, 'w': 55, 'd': 'Sin bonificaciones'},
    {'n': 'Rara', 'c': (111, 183, 255), 'dm': 1.2, 'cs': 0.8, 'el': 0, 'w': 28, 'd': '+20% daño · -20% consumo'},
    {'n': 'Épica', 'c': (199, 125, 255), 'dm': 1.35, 'cs': 0.75, 'el': 1, 'w': 12, 'd': '+35% daño · Elemento fuego/hielo'},
    {'n': 'Legendaria', 'c': (255, 176, 46), 'dm': 1.6, 'cs': 0.5, 'el': 2, 'w': 5, 'd': '+60% daño · Rayo en cadena'}
]
ELC = {'fuego': (255, 122, 60), 'hielo': (143, 227, 255), 'rayo': (255, 225, 77)}
ELN = {'fuego': 'Quemadura', 'hielo': 'Ralentiza', 'rayo': 'Rayo en cadena'}

def roll_rar():
    r = random.uniform(0, 100)
    acum = 0
    for item in RR:
        acum += item['w']
        if r <= acum:
            e = pick_el(item['el'])
            res = dict(item)
            res['e'] = e
            res['d'] = item['d'] + (f' · {ELN[e]}' if e else '')
            return res
    return RR[0]

def pick_el(el_flag):
    if not el_flag:
        return None
    return random.choice(['fuego', 'hielo', 'rayo'])

# --- ENEMIGOS Y JEFES v3.0 ---
enemigos_info = {
    'raton': {'salud': 30, 'dano': 7, 'vel': 150, 'color': (150, 150, 150), 'recompensa': 10, 'r': 12, 'es_jefe': False},
    'perro': {'salud': 110, 'dano': 13, 'vel': 105, 'color': (139, 69, 19), 'recompensa': 25, 'r': 16, 'es_jefe': False},
    'bulldog': {'salud': 300, 'dano': 22, 'vel': 62, 'color': (80, 80, 80), 'recompensa': 60, 'r': 20, 'es_jefe': False},
    'erizo': {'salud': 75, 'dano': 9, 'vel': 85, 'color': (122, 75, 43), 'recompensa': 30, 'r': 15, 'es_jefe': False},
    'murci': {'salud': 22, 'dano': 6, 'vel': 190, 'color': (91, 58, 138), 'recompensa': 12, 'r': 11, 'es_jefe': False},
    'zorro': {'salud': 90, 'dano': 12, 'vel': 130, 'color': (255, 138, 42), 'recompensa': 35, 'r': 15, 'es_jefe': False},
    'buho': {'salud': 85, 'dano': 10, 'vel': 80, 'color': (138, 106, 74), 'recompensa': 40, 'r': 15, 'es_jefe': False},
    'escudero': {'salud': 170, 'dano': 15, 'vel': 88, 'color': (107, 115, 133), 'recompensa': 45, 'r': 18, 'es_jefe': False, 'escudo': 140},
    # JEFES
    'j_rata': {'salud': 1500, 'dano': 20, 'vel': 85, 'color': (200, 50, 50), 'recompensa': 400, 'r': 34, 'es_jefe': True},
    'j_perro': {'salud': 2600, 'dano': 28, 'vel': 100, 'color': (180, 40, 40), 'recompensa': 600, 'r': 40, 'es_jefe': True},
    'j_erizo': {'salud': 3800, 'dano': 24, 'vel': 55, 'color': (160, 60, 30), 'recompensa': 800, 'r': 44, 'es_jefe': True},
    'j_zorro': {'salud': 2200, 'dano': 26, 'vel': 120, 'color': (220, 90, 20), 'recompensa': 700, 'r': 36, 'es_jefe': True},
    'j_buho': {'salud': 3000, 'dano': 22, 'vel': 75, 'color': (100, 60, 160), 'recompensa': 900, 'r': 38, 'es_jefe': True},
    'j_reina': {'salud': 3400, 'dano': 26, 'vel': 140, 'color': (180, 30, 100), 'recompensa': 1000, 'r': 36, 'es_jefe': True},
}

SKILLS_DEF = [
    {'k': 'fue', 'n': 'Fuerza', 'e': 'F', 'd': 'Daño +6% por rango', 'c': (255, 154, 90)},
    {'k': 'agi', 'n': 'Agilidad', 'e': 'A', 'd': 'Velocidad +4% por rango', 'c': (111, 227, 255)},
    {'k': 'vit', 'n': 'Vitalidad', 'e': 'V', 'd': 'Vida máxima +15', 'c': (255, 143, 177)},
    {'k': 'pun', 'n': 'Puntería', 'e': 'P', 'd': 'Crítico +2%', 'c': (141, 255, 159)},
    {'k': 'cad', 'n': 'Cadencia', 'e': 'C', 'd': 'Cadencia +4%', 'c': (255, 216, 77)},
    {'k': 'reg', 'n': 'Regeneración', 'e': 'R', 'd': 'Regenera +0.35 HP/s', 'c': (125, 255, 216)},
    {'k': 'ima', 'n': 'Imán', 'e': 'I', 'd': 'Alcance imán +25', 'c': (213, 139, 255)},
    {'k': 'kat', 'n': 'Katana y Rodada', 'e': 'K', 'd': 'Katana +12% daño, recargas -5%', 'c': (201, 166, 255)},
]

dificultades = {
    'Normal': {'mult_hp': 1.35, 'mult_dano': 1.3, 'mult_vel': 1.18, 'bd': 1.15, 'bs': 1.05},
    'Difícil': {'mult_hp': 2.2, 'mult_dano': 1.9, 'mult_vel': 1.35, 'bd': 1.4, 'bs': 1.15},
    'Imposible': {'mult_hp': 3.6, 'mult_dano': 3.0, 'mult_vel': 1.55, 'bd': 1.8, 'bs': 1.28},
}
dificultad_actual = 'Normal'

SCREEN_WIDTH, SCREEN_HEIGHT = 960, 640
display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
DROP_VIDA_MS = 40000

# --- CLASES PRINCIPALES ---
class Player:
    def __init__(self, x, y, agilidad, vida, raza):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.vel_base = 150 + agilidad * 14
        self.vel = self.vel_base
        self.vida_max = vida
        self.vida = vida
        self.raza = raza

        self.monedas = 0
        self.inventario_armas = ['bigotito_pum']
        self.arma_index = 0
        self.municion = {'bigotito_pum': armas_info['bigotito_pum']['municion_max']}
        self.rareza_armas = {'bigotito_pum': RR[0]}

        self.mult_dano_permanente = 1.0
        self.prob_critico = 0.05
        self.mult_cadencia = 1.0

        self.nivel = 1
        self.xp = 0
        self.puntos_habilidad = 0
        self.sk = {s['k']: 0 for s in SKILLS_DEF}

        self.regeneracion = 0.0
        self.rango_iman = 150
        self.mejora_katana = 0
        self.factor_fiebre_ganancia = 1.0

        # Fiebre Felina Avanzada v3.0
        self.fiebre_barra = 0.0
        self.fiebre_activa_hasta = 0
        self.modo_fiebre = None

        # Power-ups y Granadas v3.0
        self.pu_escudo_hasta = 0
        self.pu_dano_hasta = 0
        self.pu_vel_hasta = 0
        self.pu_rafaga_hasta = 0
        self.pu_iman_hasta = 0

        self.cooldown_habilidad = 10000
        self.ultimo_uso_habilidad = -10000
        self.dano_hab_hasta = 0
        self.invuln_hab_hasta = 0
        self.vel_hab_hasta = 0
        self.invulnerable = False
        self.multiplicador_dano = 1.0

        self.cooldown_katana = 3200
        self.ultimo_uso_katana = -10000
        self.katana_activa_hasta = 0
        self.angulo_katana = 0

        self.cooldown_rodada = 1600
        self.ultimo_uso_rodada = -10000
        self.rodada_activa_hasta = 0
        self.dir_rodada = (1, 0)
        
        self.cooldown_granada = 14000
        self.ultimo_uso_granada = -10000

        self.dir_mov = (1, 0)

    def gain_xp(self, cantidad):
        self.xp += cantidad
        xp_necesaria = round(30 * (1.38 ** (self.nivel - 1)))
        while self.xp >= xp_necesaria:
            self.xp -= xp_necesaria
            self.nivel += 1
            self.puntos_habilidad += 1
            xp_necesaria = round(30 * (1.38 ** (self.nivel - 1)))

    def cd_habilidad_restante(self, t):
        return self.cooldown_habilidad - (t - self.ultimo_uso_habilidad)

    def cd_katana_restante(self, t):
        cd = self.cooldown_katana * max(0.5, 1 - 0.05 * self.mejora_katana)
        return cd - (t - self.ultimo_uso_katana)

    def cd_rodada_restante(self, t):
        cd = self.cooldown_rodada * max(0.5, 1 - 0.05 * self.mejora_katana)
        return cd - (t - self.ultimo_uso_rodada)

    def cd_granada_restante(self, t):
        return self.cooldown_granada - (t - self.ultimo_uso_granada)

    def usar_habilidad(self, t, enemigos_lista):
        if self.cd_habilidad_restante(t) > 0:
            return
        self.ultimo_uso_habilidad = t
        if self.raza == 'Gato naranja':
            self.dano_hab_hasta = t + 5000
        elif self.raza == 'Gato negro':
            self.invuln_hab_hasta = t + 3000
        elif self.raza == 'Gato gordo':
            for e in enemigos_lista:
                dx, dy = e.x - self.x, e.y - self.y
                dist = math.hypot(dx, dy)
                if dist < 200:
                    e.salud -= 100
                    if dist > 0:
                        e.x += (dx / dist) * 120
                        e.y += (dy / dist) * 120
        elif self.raza == 'Gato calvo':
            for e in enemigos_lista:
                if math.hypot(e.x - self.x, e.y - self.y) < 250:
                    e.aturdido_hasta = t + 3000
        elif self.raza == 'Gato Siames':
            self.vel_hab_hasta = t + 400

    def usar_katana(self, t, enemigos_lista, balas_enemigas, mw_x, mw_y):
        if self.cd_katana_restante(t) > 0:
            return
        self.ultimo_uso_katana = t
        self.katana_activa_hasta = t + 350
        self.angulo_katana = math.atan2(mw_y - self.y, mw_x - self.x)
        
        # Daño en área de la katana alrededor del jugador
        dano_katana = 70 * (1.0 + 0.12 * self.mejora_katana) * self.mult_dano_permanente
        for e in enemigos_lista:
            if math.hypot(e.x - self.x, e.y - self.y) < 65:
                e.salud -= dano_katana
                e.aturdido_hasta = t + 600

    def usar_rodada(self, t):
        if self.cd_rodada_restante(t) > 0:
            return
        self.ultimo_uso_rodada = t
        self.rodada_activa_hasta = t + 400
        self.dir_rodada = self.dir_mov if self.dir_mov != (0, 0) else (1, 0)

    def activar_fiebre(self, t):
        self.modo_fiebre = random.choice(['inst', 'onda', 'extra'])
        self.fiebre_activa_hasta = t + 8000
        self.fiebre_barra = 100.0

    def add_fiebre(self, cantidad, t):
        if t < self.fiebre_activa_hasta:
            return
        self.fiebre_barra = min(100.0, self.fiebre_barra + cantidad * self.factor_fiebre_ganancia)
        if self.fiebre_barra >= 100.0:
            self.activar_fiebre(t)

    def update_estados(self, t, dt):
        if self.regeneracion > 0 and self.vida < self.vida_max:
            self.vida = min(self.vida_max, self.vida + self.regeneracion * dt)

        en_fiebre = t < self.fiebre_activa_hasta
        if en_fiebre:
            if self.modo_fiebre == 'inst':
                self.ultimo_uso_habilidad = -10000
                self.ultimo_uso_rodada = -10000

        self.multiplicador_dano = 2.0 if (t < self.dano_hab_hasta or t < self.pu_dano_hasta or en_fiebre) else 1.0

        rodando = t < self.rodada_activa_hasta
        self.invulnerable = rodando or t < self.pu_escudo_hasta or t < self.invuln_hab_hasta

        if rodando:
            self.vel = self.vel_base * 2.6
        elif t < self.vel_hab_hasta:
            self.vel = self.vel_base * 3.5
        elif t < self.pu_vel_hasta:
            self.vel = self.vel_base * 1.4
        else:
            self.vel = self.vel_base

    def get_arma_actual(self):
        return self.inventario_armas[self.arma_index]

    def get_rect(self):
        return pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)

    def lanzar_granada(self, t, granadas_lista):
        if self.cd_granada_restante(t) > 0:
            return
        self.ultimo_uso_granada = t
        granadas_lista.append(Grenade(self.x, self.y, self.x + self.dir_mov[0] * 180, self.y + self.dir_mov[1] * 180))

    def draw(self, display, t):
        screen_x = SCREEN_WIDTH // 2
        screen_y = SCREEN_HEIGHT // 2
        rect = pygame.Rect(screen_x - self.width // 2, screen_y - self.height // 2, self.width, self.height)

        color = (255, 140, 0)
        if self.invulnerable:
            color = (100, 100, 255)
        elif self.multiplicador_dano > 1.0:
            color = (255, 50, 0)

        pygame.draw.rect(display, color, rect)

        if t < self.fiebre_activa_hasta:
            pygame.draw.circle(display, (255, 126, 182), (screen_x, screen_y), 42, 3)

        if t < self.katana_activa_hasta:
            pygame.draw.arc(display, (201, 166, 255), (screen_x - 40, screen_y - 40, 80, 80), -self.angulo_katana - 1.0, -self.angulo_katana + 1.0, 5)


class PlayerBullet:
    def __init__(self, x, y, angulo, dano, velocidad, es_critico=False, explosion=0, alcance=1500, elemento=0, el_tipo=None):
        self.x = x
        self.y = y
        self.dano = dano
        self.speed = velocidad
        self.radius = 5
        self.es_critico = es_critico
        self.explosion = explosion
        self.alcance = alcance
        self.elemento = elemento
        self.el_tipo = el_tipo
        self.recorrido = 0.0
        self.x_vel = math.cos(angulo) * velocidad
        self.y_vel = math.sin(angulo) * velocidad

    def avanzar(self, factor):
        self.x += self.x_vel * factor
        self.y += self.y_vel * factor
        self.recorrido += self.speed * factor

    def draw(self, display, scroll):
        color = (255, 215, 0) if self.es_critico else (255, 255, 255)
        if self.el_tipo == 'fuego':
            color = ELC['fuego']
        elif self.el_tipo == 'hielo':
            color = ELC['hielo']
        elif self.el_tipo == 'rayo':
            color = ELC['rayo']
        pygame.draw.circle(display, color, (int(self.x + scroll[0]), int(self.y + scroll[1])), self.radius)


class Enemy:
    def __init__(self, world_x, world_y, tipo_nombre, dif_config):
        datos = enemigos_info[tipo_nombre]
        self.tipo = tipo_nombre
        self.x = world_x
        self.y = world_y
        radio = datos.get('r', 15)
        self.width = radio * 2
        self.height = radio * 2
        self.salud_max = int(datos['salud'] * dif_config['mult_hp'])
        self.salud = self.salud_max
        self.dano = int(datos['dano'] * dif_config['mult_dano'])
        self.vel = datos['vel'] * dif_config['mult_vel']
        self.color = datos['color']
        self.recompensa = datos['recompensa']
        self.es_jefe = datos.get('es_jefe', False)
        
        self.tiene_escudo = 'escudo' in datos
        self.escudo_max = datos.get('escudo', 0) if self.tiene_escudo else 0
        self.escudo = self.escudo_max
        self.escudo_roto_hasta = 0

        self.aturdido_hasta = 0
        self.quemadura_hasta = 0
        self.lento_hasta = 0

    def update(self, player_x, player_y, dt, t):
        if t < self.aturdido_hasta:
            return
        if t < self.quemadura_hasta:
            self.salud -= 6 * dt
        
        vel_actual = self.vel * (0.5 if t < self.lento_hasta else 1.0)
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * vel_actual * dt
            self.y += (dy / dist) * vel_actual * dt

    def get_rect_world(self):
        return pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)

    def draw(self, display, scroll, t):
        rect = self.get_rect_world().move(int(scroll[0]), int(scroll[1]))
        color = (100, 200, 255) if t < self.aturdido_hasta else self.color
        if t < self.quemadura_hasta:
            color = (255, 100, 50)
        pygame.draw.rect(display, color, rect)

        if self.tiene_escudo and self.escudo > 0:
            pygame.draw.rect(display, (111, 183, 255), (rect.x, rect.y - 12, self.width, 4))

        porcentaje = min(1, max(0, self.salud / self.salud_max))
        pygame.draw.rect(display, (200, 0, 0), (rect.x, rect.y - 7, self.width, 4))
        pygame.draw.rect(display, (0, 255, 0), (rect.x, rect.y - 7, int(self.width * porcentaje), 4))


class Barrel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.salud = 45
        self.radius = 16
        self.fl = 0

    def get_rect_world(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def draw(self, display, scroll):
        rect = self.get_rect_world().move(int(scroll[0]), int(scroll[1]))
        color = (255, 255, 255) if self.fl > 0 else (217, 74, 58)
        pygame.draw.rect(display, color, rect, border_radius=4)
        pygame.draw.rect(display, (255, 215, 0), rect, 2, border_radius=4)


class Puddle:
    def __init__(self, x, y, r, tipo, color):
        self.x = x
        self.y = y
        self.r = r
        self.tipo = tipo
        self.color = color

    def draw(self, display, scroll):
        pos = (int(self.x + scroll[0]), int(self.y + scroll[1]))
        srf = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(srf, (*self.color, 120), (self.r, self.r), self.r)
        display.blit(srf, (pos[0] - self.r, pos[1] - self.r))


class Grenade:
    def __init__(self, x, y, tx, ty):
        self.x = x
        self.y = y
        self.tx = tx
        self.ty = ty
        self.t_creado = pygame.time.get_ticks()
        self.duracion = 1100

    def update(self, t):
        prog = min(1.0, (t - self.t_creado) / self.duracion)
        self.x = self.x + (self.tx - self.x) * prog
        self.y = self.y + (self.ty - self.y) * prog
        return prog >= 1.0

    def draw(self, display, scroll):
        pygame.draw.circle(display, (80, 80, 80), (int(self.x + scroll[0]), int(self.y + scroll[1])), 6)


class DropItem:
    def __init__(self, x, y, tipo, creado, valor=0, arma_key=None, powerup_type=None, rareza=None):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.valor = valor
        self.arma_key = arma_key
        self.powerup_type = powerup_type
        self.rareza = rareza
        self.radius = 8
        self.creado = creado

    def get_rect_world(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def draw(self, display, scroll):
        colors = {'moneda': (255, 215, 0), 'atun': (0, 200, 255), 'municion': (180, 100, 255), 'powerup': (255, 80, 80)}
        col = colors.get(self.tipo, (255, 255, 255))
        if self.rareza:
            col = self.rareza['c']
        pygame.draw.circle(display, col, (int(self.x + scroll[0]), int(self.y + scroll[1])), self.radius)


class WeaponDropBox:
    def __init__(self, x, y, costo=100):
        self.x = x
        self.y = y
        self.costo = costo
        self.width = 40
        self.height = 40

    def get_rect_world(self):
        return pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2), self.width, self.height)

    def draw(self, display, scroll):
        rect = self.get_rect_world().move(int(scroll[0]), int(scroll[1]))
        pygame.draw.rect(display, (139, 69, 19), rect, border_radius=6)
        pygame.draw.rect(display, (255, 215, 0), rect, 2, border_radius=6)
        txt = FONT.render(f'${self.costo} (E)', True, (255, 255, 255))
        display.blit(txt, (rect.x - 15, rect.y - 22))


# --- INTERFACES Y MENÚS ---
def dibujar_menu_habilidades(display, player):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((15, 6, 30))
    display.blit(overlay, (0, 0))

    txt_titulo = FONT_BIG.render('ÁRBOL DE HABILIDADES', True, (255, 176, 46))
    display.blit(txt_titulo, (SCREEN_WIDTH // 2 - txt_titulo.get_width() // 2, 30))

    txt_nv = FONT.render(f'Nivel {player.nivel} | XP: {player.xp} | Puntos: {player.puntos_habilidad}', True, (111, 227, 255))
    display.blit(txt_nv, (SCREEN_WIDTH // 2 - txt_nv.get_width() // 2, 80))

    for i, sk in enumerate(SKILLS_DEF):
        x, y = skill_card_pos(i)
        rango_actual = player.sk[sk['k']]
        costo_pts = 1 + (rango_actual // 2)

        rect_card = pygame.Rect(x, y, 410, 85)
        pygame.draw.rect(display, (58, 37, 64), rect_card, border_radius=10)
        pygame.draw.rect(display, sk['c'], rect_card, 2, border_radius=10)

        display.blit(FONT.render(f"{sk['e']} - {sk['n']} (Nv. {rango_actual}/8)", True, (255, 255, 255)), (x + 15, y + 10))
        display.blit(FONT_SMALL.render(sk['d'], True, (255, 233, 184)), (x + 15, y + 35))

        btn_rect = pygame.Rect(x + 290, y + 20, 100, 45)
        puedes = player.puntos_habilidad >= costo_pts and rango_actual < 8
        pygame.draw.rect(display, (125, 255, 154) if puedes else (100, 100, 100), btn_rect, border_radius=8)
        display.blit(FONT.render('MAX' if rango_actual >= 8 else f'+{costo_pts} Pt', True, (0, 0, 0)), (btn_rect.x + 15, btn_rect.y + 12))

    display.blit(FONT.render('Pulsa [TAB] o [ESC] para volver', True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 40))

def skill_card_pos(i):
    return 60 + (i % 2) * 430, 120 + (i // 2) * 100

def dibujar_game_over(display, oleada, player):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((20, 0, 0))
    display.blit(overlay, (0, 0))
    lineas = [
        (FONT_BIG, '¡HAS MUERTO!', (255, 60, 60)),
        (FONT, f'Llegaste a la oleada {oleada} con nivel {player.nivel}', (255, 255, 255)),
        (FONT, 'Pulsa [R] para reiniciar o [ESC] para salir', (255, 233, 184)),
    ]
    y = SCREEN_HEIGHT // 2 - 70
    for fuente, texto, color in lineas:
        surf = fuente.render(texto, True, color)
        display.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
        y += surf.get_height() + 14


# --- INICIALIZACIÓN Y ESTADOS ---
def nueva_partida():
    global gato_eleccion, player, player_bullets, balas_enemigas
    global enemigos_lista, drops_lista, boxes_lista, barriles_lista, charcos_lista, granadas_lista
    global ultimo_disparo, oleada, enemigos_por_spawnear
    global tiempo_siguiente_oleada, mensaje_oleada_timer
    global estado_juego, tiempo_juego

    gato_eleccion = random.choice(list(GATOS.keys()))
    _fuerza, agilidad, _salto, vida = GATOS[gato_eleccion]
    pygame.display.set_caption(f'GATOSPIUPIU DELUXE v3.0 - {gato_eleccion}')

    player = Player(400, 300, agilidad, vida, gato_eleccion)
    player_bullets = []
    balas_enemigas = []
    enemigos_lista = []
    drops_lista = []
    barriles_lista = [Barrel(300, 300), Barrel(500, 200)]
    charcos_lista = [Puddle(250, 250, 70, 'lodo', (90, 60, 30)), Puddle(650, 400, 70, 'hielo', (150, 220, 255))]
    granadas_lista = []
    boxes_lista = [WeaponDropBox(200, 200, costo=100)]

    ultimo_disparo = 0
    oleada = 1
    enemigos_por_spawnear = 5
    tiempo_siguiente_oleada = 0
    mensaje_oleada_timer = 0
    estado_juego = 'PLAY'
    tiempo_juego = 0.0

def procesar_muertes(t):
    for e in enemigos_lista[:]:
        if e.salud > 0:
            continue
        enemigos_lista.remove(e)
        player.gain_xp(e.recompensa)
        player.add_fiebre(15 if e.es_jefe else 5, t)
        drops_lista.append(DropItem(e.x, e.y, 'moneda', t, valor=e.recompensa))

        if random.random() < 0.2:
            drops_lista.append(DropItem(e.x, e.y, 'atun', t))
        if random.random() < 0.25:
            drops_lista.append(DropItem(e.x, e.y, 'municion', t, arma_key=random.choice(player.inventario_armas)))
        if random.random() < 0.1:
            drops_lista.append(DropItem(e.x, e.y, 'powerup', t, powerup_type=random.choice(['dano', 'vel', 'escudo', 'bomba'])))

def comprar_caja(box):
    player.monedas -= box.costo
    box.costo += 50
    opciones_armas = [k for k in armas_info if k not in player.inventario_armas]
    if opciones_armas and random.random() < 0.55:
        nueva_arma = random.choice(opciones_armas)
        rareza = roll_rar()
        player.inventario_armas.append(nueva_arma)
        player.municion[nueva_arma] = armas_info[nueva_arma]['municion_max']
        player.rareza_armas[nueva_arma] = rareza
        player.arma_index = len(player.inventario_armas) - 1
    else:
        mejora = random.choice(['dano', 'vel', 'vida', 'cad', 'crit', 'bal'])
        if mejora == 'dano': player.mult_dano_permanente += 0.15
        elif mejora == 'vel': player.vel_base *= 1.08
        elif mejora == 'vida':
            player.vida_max += 25
            player.vida += 25
        elif mejora == 'cad': player.mult_cadencia *= 1.08
        elif mejora == 'crit': player.prob_critico = min(0.6, player.prob_critico + 0.05)
        elif mejora == 'bal':
            for k_arm in player.inventario_armas:
                maximo = armas_info[k_arm]['municion_max']
                player.municion[k_arm] = min(maximo, player.municion[k_arm] + int(maximo * 0.5))

def comprar_habilidad(sk):
    rango = player.sk[sk['k']]
    costo_pts = 1 + (rango // 2)
    if player.puntos_habilidad < costo_pts or rango >= 8:
        return
    player.puntos_habilidad -= costo_pts
    player.sk[sk['k']] += 1
    k = sk['k']
    if k == 'fue': player.mult_dano_permanente += 0.06
    elif k == 'agi': player.vel_base *= 1.04
    elif k == 'vit':
        player.vida_max += 15
        player.vida += 15
    elif k == 'pun': player.prob_critico = min(0.6, player.prob_critico + 0.02)
    elif k == 'cad': player.mult_cadencia *= 1.04
    elif k == 'reg': player.regeneracion += 0.35
    elif k == 'ima': player.rango_iman += 25
    elif k == 'kat': player.mejora_katana += 1

def cd_txt(restante_ms):
    return 'LISTO' if restante_ms <= 0 else f'{math.ceil(restante_ms / 1000)}s'

nueva_partida()

# --- BUCLE DE JUEGO ---
while True:
    dt = min(clock.tick(60) / 1000.0, 0.05)
    if estado_juego == 'PLAY':
        tiempo_juego += dt * 1000
    tiempo_actual = int(tiempo_juego)

    display.fill((42, 26, 58))
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if estado_juego == 'MUERTO':
                if event.key == pygame.K_r:
                    nueva_partida()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                continue

            if event.key == pygame.K_TAB:
                estado_juego = 'SKILLS' if estado_juego == 'PLAY' else 'PLAY'
                continue

            if event.key == pygame.K_ESCAPE and estado_juego == 'SKILLS':
                estado_juego = 'PLAY'
                continue

            if estado_juego == 'PLAY':
                if event.key == pygame.K_SPACE:
                    player.usar_habilidad(tiempo_actual, enemigos_lista)
                if event.key == pygame.K_z:
                    mw_x = mouse_x - (SCREEN_WIDTH // 2 - player.x)
                    mw_y = mouse_y - (SCREEN_HEIGHT // 2 - player.y)
                    player.usar_katana(tiempo_actual, enemigos_lista, balas_enemigas, mw_x, mw_y)
                if event.key == pygame.K_q:
                    player.usar_rodada(tiempo_actual)
                if event.key == pygame.K_g:
                    player.lanzar_granada(tiempo_actual, granadas_lista)

                idx = None
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                elif event.key == pygame.K_0:
                    idx = 9
                if idx is not None and idx < len(player.inventario_armas):
                    player.arma_index = idx

                if event.key == pygame.K_e:
                    p_rect = player.get_rect()
                    for box in boxes_lista:
                        if p_rect.colliderect(box.get_rect_world().inflate(25, 25)) and player.monedas >= box.costo:
                            comprar_caja(box)
                            break

        if event.type == pygame.MOUSEWHEEL and estado_juego == 'PLAY':
            player.arma_index = (player.arma_index - event.y) % len(player.inventario_armas)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and estado_juego == 'SKILLS':
            for i, sk in enumerate(SKILLS_DEF):
                x, y = skill_card_pos(i)
                if pygame.Rect(x + 290, y + 20, 100, 45).collidepoint(event.pos):
                    comprar_habilidad(sk)

    if estado_juego == 'SKILLS':
        dibujar_menu_habilidades(display, player)
        pygame.display.update()
        continue

    if estado_juego == 'MUERTO':
        dibujar_game_over(display, oleada, player)
        pygame.display.update()
        continue

    # --- MOVIMIENTO ---
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_d]: dx += 1
    if keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_s]: dy += 1

    player.update_estados(tiempo_actual, dt)

    if dx != 0 or dy != 0:
        norm = math.hypot(dx, dy)
        player.dir_mov = (dx / norm, dy / norm)

    if tiempo_actual < player.rodada_activa_hasta:
        player.x += player.dir_rodada[0] * player.vel * dt
        player.y += player.dir_rodada[1] * player.vel * dt
    elif dx != 0 or dy != 0:
        player.x += player.dir_mov[0] * player.vel * dt
        player.y += player.dir_mov[1] * player.vel * dt

    display_scroll = [SCREEN_WIDTH // 2 - player.x, SCREEN_HEIGHT // 2 - player.y]

    # --- SPAWN DE OLEADAS ---
    if enemigos_por_spawnear > 0 and random.random() < 0.03:
        ang = random.uniform(0, math.pi * 2)
        dist = random.uniform(600, 800)
        px = player.x + math.cos(ang) * dist
        py = player.y + math.sin(ang) * dist

        if oleada % 5 == 0 and len(enemigos_lista) == 0:
            jefes = ['j_rata', 'j_perro', 'j_erizo', 'j_zorro', 'j_buho', 'j_reina']
            tipo_elegido = jefes[(oleada // 5 - 1) % len(jefes)]
        else:
            tipos = ['raton', 'escudero']
            if oleada >= 2: tipos.append('perro')
            if oleada >= 3: tipos.extend(['erizo', 'murci'])
            if oleada >= 4: tipos.append('bulldog')
            if oleada >= 5: tipos.append('zorro')
            if oleada >= 6: tipos.append('buho')
            tipo_elegido = random.choice(tipos)

        enemigos_lista.append(Enemy(px, py, tipo_elegido, dificultades[dificultad_actual]))
        enemigos_por_spawnear -= 1

    if enemigos_por_spawnear == 0 and len(enemigos_lista) == 0:
        if tiempo_siguiente_oleada == 0:
            tiempo_siguiente_oleada = tiempo_actual + 3000
        elif tiempo_actual >= tiempo_siguiente_oleada:
            oleada += 1
            enemigos_por_spawnear = 1 if oleada % 5 == 0 else 5 + oleada * 3
            tiempo_siguiente_oleada = 0
            mensaje_oleada_timer = tiempo_actual + 2000

    # --- DISPARO ---
    mouse_click = pygame.mouse.get_pressed()
    arma_key = player.get_arma_actual()
    arma = armas_info[arma_key]
    rareza_actual = player.rareza_armas.get(arma_key, RR[0])
    
    cadencia_efectiva = arma['cadencia'] / (player.mult_cadencia * (2.0 if tiempo_actual < player.pu_rafaga_hasta else 1.0))

    if mouse_click[0] and tiempo_actual - ultimo_disparo >= cadencia_efectiva and player.municion.get(arma_key, 0) > 0:
        if random.random() > rareza_actual['cs']:
            pass
        else:
            player.municion[arma_key] -= 1

        obj_x = mouse_x - display_scroll[0]
        obj_y = mouse_y - display_scroll[1]
        angulo_base = math.atan2(obj_y - player.y, obj_x - player.x)

        es_critico = random.random() < player.prob_critico
        dano_final = arma['dano'] * rareza_actual['dm'] * player.multiplicador_dano * player.mult_dano_permanente * (2.0 if es_critico else 1.0)
        spread = math.radians(arma.get('sp', 0))

        for _ in range(arma.get('b', 1)):
            player_bullets.append(
                PlayerBullet(
                    player.x, player.y,
                    angulo_base + random.uniform(-spread, spread),
                    dano_final,
                    arma['velocidad_bala'],
                    es_critico=es_critico,
                    explosion=arma.get('ex', 0),
                    alcance=arma.get('alcance', 1500),
                    elemento=rareza_actual['el'],
                    el_tipo=rareza_actual.get('e')
                )
            )
        ultimo_disparo = tiempo_actual

    # --- DIBUJO Y ACTUALIZACIÓN DEL MUNDO ---
    for charco in charcos_lista:
        charco.draw(display, display_scroll)

    for box in boxes_lista:
        box.draw(display, display_scroll)

    for bar in barriles_lista:
        bar.draw(display, display_scroll)

    p_rect = player.get_rect()
    for enemigo in enemigos_lista:
        enemigo.update(player.x, player.y, dt, tiempo_actual)
        enemigo.draw(display, display_scroll, tiempo_actual)

        if enemigo.salud > 0 and not player.invulnerable:
            if enemigo.get_rect_world().colliderect(p_rect):
                player.vida -= enemigo.dano * dt

    # --- PROYECTILES Y GRANADAS ---
    for g in granadas_lista[:]:
        if g.update(tiempo_actual):
            granadas_lista.remove(g)
            for e in enemigos_lista:
                if math.hypot(e.x - g.x, e.y - g.y) < 130:
                    e.salud -= 120
            for bar in barriles_lista:
                if math.hypot(bar.x - g.x, bar.y - g.y) < 130:
                    bar.salud = 0
        else:
            g.draw(display, display_scroll)

    for bullet in player_bullets[:]:
        pasos = int(bullet.speed * dt * 60 // 8) + 1
        impacto = False
        for _ in range(pasos):
            bullet.avanzar(dt * 60 / pasos)
            for bar in barriles_lista:
                if math.hypot(bullet.x - bar.x, bullet.y - bar.y) < bar.radius + bullet.radius:
                    bar.salud -= bullet.dano
                    if bar.salud <= 0 and bar in barriles_lista:
                        barriles_lista.remove(bar)
                        for e_exp in enemigos_lista:
                            if math.hypot(e_exp.x - bar.x, e_exp.y - bar.y) < 150:
                                e_exp.salud -= 150
                    impacto = True
                    break
            if impacto: break

            for enemigo in enemigos_lista:
                if enemigo.salud <= 0: continue
                if math.hypot(bullet.x - enemigo.x, bullet.y - enemigo.y) < enemigo.width / 2 + bullet.radius:
                    enemigo.salud -= bullet.dano
                    if bullet.el_tipo == 'fuego':
                        enemigo.quemadura_hasta = tiempo_actual + 3000
                    elif bullet.el_tipo == 'hielo':
                        enemigo.lento_hasta = tiempo_actual + 2000
                    elif bullet.el_tipo == 'rayo':
                        cadena = 2
                        for e_cad in enemigos_lista:
                            if e_cad is not enemigo and math.hypot(e_cad.x - enemigo.x, e_cad.y - enemigo.y) < 150 and cadena > 0:
                                e_cad.salud -= bullet.dano * 0.5
                                cadena -= 1

                    if bullet.explosion > 0:
                        for e_exp in enemigos_lista:
                            if e_exp is not enemigo and math.hypot(e_exp.x - enemigo.x, e_exp.y - enemigo.y) < bullet.explosion:
                                e_exp.salud -= bullet.dano * 0.8
                    impacto = True
                    break
            if impacto: break

        if impacto or bullet.recorrido > bullet.alcance:
            player_bullets.remove(bullet)
        else:
            bullet.draw(display, display_scroll)

    procesar_muertes(tiempo_actual)

    # --- RECOGIDA DE DROPS ---
    for drop in drops_lista[:]:
        if tiempo_actual - drop.creado > DROP_VIDA_MS:
            drops_lista.remove(drop)
            continue
        if math.hypot(drop.x - player.x, drop.y - player.y) < player.rango_iman:
            drop.x += (player.x - drop.x) * min(1.0, 6 * dt)
            drop.y += (player.y - player.y) * min(1.0, 6 * dt)

        drop.draw(display, display_scroll)
        if not drop.get_rect_world().colliderect(p_rect):
            continue

        if drop.tipo == 'moneda': player.monedas += drop.valor
        elif drop.tipo == 'atun': player.vida = min(player.vida_max, player.vida + 25)
        elif drop.tipo == 'municion' and drop.arma_key in player.municion:
            info = armas_info[drop.arma_key]
            player.municion[drop.arma_key] = min(info['municion_max'], player.municion[drop.arma_key] + info['recarga_balas'])
        elif drop.tipo == 'powerup':
            if drop.powerup_type == 'dano': player.pu_dano_hasta = tiempo_actual + 10000
            elif drop.powerup_type == 'vel': player.pu_vel_hasta = tiempo_actual + 10000
            elif drop.powerup_type == 'escudo': player.pu_escudo_hasta = tiempo_actual + 6000
            elif drop.powerup_type == 'bomba':
                for e in enemigos_lista: e.salud -= 150
                procesar_muertes(tiempo_actual)

        drops_lista.remove(drop)

    player.draw(display, tiempo_actual)

    if player.vida <= 0:
        estado_juego = 'MUERTO'

    # --- HUD ---
    pygame.draw.rect(display, (100, 0, 0), (20, 20, 200, 20))
    pygame.draw.rect(display, (255, 111, 156), (20, 20, int(200 * (max(0, player.vida) / player.vida_max)), 20))
    display.blit(FONT.render(f'HP: {int(player.vida)}/{player.vida_max}', True, (255, 255, 255)), (25, 22))

    pygame.draw.rect(display, (40, 20, 60), (20, 48, 200, 14))
    pygame.draw.rect(display, (255, 126, 182), (20, 48, int(200 * (player.fiebre_barra / 100.0)), 14))
    display.blit(FONT_SMALL.render('FIEBRE FELINA', True, (255, 255, 255)), (25, 48))

    txt_cooldowns = FONT_SMALL.render(f'[SPACE]: {cd_txt(player.cd_habilidad_restante(tiempo_actual))} | [Z] Katana: {cd_txt(player.cd_katana_restante(tiempo_actual))} | [Q] Rodada: {cd_txt(player.cd_rodada_restante(tiempo_actual))} | [G] Granada: {cd_txt(player.cd_granada_restante(tiempo_actual))}', True, (255, 255, 0))
    display.blit(txt_cooldowns, (20, 70))

    display.blit(FONT.render(f'Nv. {player.nivel} (XP: {player.xp}) | Pts: {player.puntos_habilidad} [TAB]', True, (111, 227, 255)), (20, 95))
    display.blit(FONT.render(f'Monedas: ${player.monedas}', True, (255, 215, 0)), (20, 120))
    display.blit(FONT.render(f'Oleada: {oleada} ({dificultad_actual})', True, (255, 255, 255)), (20, 145))

    balas_actuales = player.municion.get(arma_key, 0)
    col_arma = rareza_actual['c']
    display.blit(FONT.render(f'Arma [{player.arma_index + 1}]: {arma["nombre"]} ({rareza_actual["n"]}) | Balas: {balas_actuales}', True, col_arma), (20, 170))

    if tiempo_actual < mensaje_oleada_timer:
        txt_ol = FONT_BIG.render(f'¡OLEADA {oleada}!', True, (255, 50, 50))
        display.blit(txt_ol, (SCREEN_WIDTH // 2 - txt_ol.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

    pygame.display.update()