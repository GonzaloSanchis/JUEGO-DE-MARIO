"""
=============================================================================
CLON SUPER MARIO BROS (NIVEL 1-1) EN PYTHON CON PYGAME
=============================================================================

REQUISITOS E INSTALACIÓN:
    1. Asegúrate de tener Python 3 instalado.
    2. Instala la librería pygame mediante tu terminal con:
           pip install pygame

CÓMO EJECUTAR EL JUEGO:
    python mario.py
    (o bien: py mario.py)

CONTROLES:
    - 'A': Mover a la izquierda.
    - 'D': Mover a la derecha.
    - 'S': Agacharse.
    - 'W': Mirar hacia arriba.
    - BARRA ESPACIADORA: Saltar.
    - 'R': Reiniciar la partida tras Game Over o Victoria.
    - ESC: Salir del juego.

CARACTERÍSTICAS IMPLEMENTADAS:
    - Física con gravedad, inercia, aceleración y fricción.
    - Bloques de suelo, tuberías de diferentes alturas y ladrillos rompibles.
    - Bloques de interrogación (?) con animación de salto de moneda y contador.
    - Enemigos (Goombas) que patrullan, rebotan con tuberías/bloques y mueren
      aplastados al caerles encima (o te derrotan al tocarte de lado).
    - Cámara lateral con desplazamiento (Side-scrolling dinámico que avanza con Mario).
    - Poste de bandera final al final del nivel 1-1 que activa la victoria.
=============================================================================
"""

import sys
import pygame

# ---------------------------------------------------------------------------
# CONSTANTES DE PANTALLA Y FÍSICA
# ---------------------------------------------------------------------------
ANCHO_VENTANA = 800
ALTO_VENTANA = 480
FPS = 60
TAMANO_TILE = 32  # Tamaño base de cada bloque/tile en píxeles

# Constantes de movimiento y gravedad
GRAVEDAD = 0.75
VELOCIDAD_MAX_X = 5.0
ACELERACION_X = 0.5
FRICCION = 0.82
IMPULSO_SALTO = -13.5
REBOTE_ENEMIGO = -9.0

# ---------------------------------------------------------------------------
# PALETA DE COLORES (ESTILO RETRO NES)
# ---------------------------------------------------------------------------
COLOR_CIELO = (92, 148, 252)
COLOR_SUELO = (200, 76, 12)
COLOR_SUELO_TOPO = (0, 168, 0)
COLOR_LADRILLO = (180, 60, 20)
COLOR_LADRILLO_BORDE = (120, 30, 0)
COLOR_BLOQUE_Q = (252, 152, 56)
COLOR_BLOQUE_Q_USADO = (140, 100, 60)
COLOR_TUBERIA = (0, 168, 0)
COLOR_TUBERIA_OSCURO = (0, 120, 0)
COLOR_MARIO_ROJO = (228, 0, 88)
COLOR_MARIO_AZUL = (0, 64, 216)
COLOR_MARIO_PIEL = (252, 152, 56)
COLOR_GOOMBA_CUERPO = (156, 76, 28)
COLOR_MONEDA = (252, 216, 0)
COLOR_BLANCO = (255, 255, 255)
COLOR_BANDERA = (0, 200, 0)
COLOR_ASTA = (220, 220, 220)


# ---------------------------------------------------------------------------
# GENERADORES DE SPRITES PROCEDURALES (Fáciles de reemplazar por imágenes)
# ---------------------------------------------------------------------------
def crear_sprite_mario():
    surf = pygame.Surface((24, 32), pygame.SRCALPHA)
    # Gorra y camisa roja
    surf.fill(COLOR_MARIO_ROJO, (4, 0, 16, 8))
    # Cara piel
    surf.fill(COLOR_MARIO_PIEL, (4, 8, 16, 8))
    # Bigote/ojo
    surf.fill((0, 0, 0), (14, 10, 4, 3))
    # Overol azul
    surf.fill(COLOR_MARIO_AZUL, (4, 16, 16, 10))
    # Botón dorado
    surf.fill((255, 255, 0), (6, 18, 2, 2))
    # Zapatos marrones
    surf.fill((100, 50, 0), (2, 26, 8, 6))
    surf.fill((100, 50, 0), (14, 26, 8, 6))
    return surf


def crear_sprite_goomba():
    surf = pygame.Surface((28, 28), pygame.SRCALPHA)
    # Cabeza en forma de seta
    pygame.draw.circle(surf, COLOR_GOOMBA_CUERPO, (14, 12), 12)
    # Tallo/cuerpo inferior
    surf.fill((230, 190, 150), (6, 14, 16, 10))
    # Ojos y cejas
    surf.fill((0, 0, 0), (7, 10, 3, 5))
    surf.fill((0, 0, 0), (18, 10, 3, 5))
    surf.fill((255, 255, 255), (7, 12, 3, 3))
    surf.fill((255, 255, 255), (18, 12, 3, 3))
    # Pies negros
    surf.fill((20, 20, 20), (2, 22, 10, 6))
    surf.fill((20, 20, 20), (16, 22, 10, 6))
    return surf


def crear_sprite_goomba_aplastado():
    surf = pygame.Surface((28, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, COLOR_GOOMBA_CUERPO, (0, 0, 28, 12))
    surf.fill((0, 0, 0), (6, 4, 16, 3))
    return surf


# ---------------------------------------------------------------------------
# CLASES DE ENTIDADES Y BLOQUES
# ---------------------------------------------------------------------------
class BloqueSuelo(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto):
        super().__init__()
        self.rect = pygame.Rect(x, y, ancho, alto)

    def draw(self, surface, offset_x):
        r = self.rect.move(-offset_x, 0)
        # Fondo tierra
        pygame.draw.rect(surface, COLOR_SUELO, r)
        # Borde superior con hierba
        pygame.draw.rect(surface, COLOR_SUELO_TOPO, (r.x, r.y, r.width, 6))
        # Patrón de bloques
        for cx in range(0, r.width, TAMANO_TILE):
            pygame.draw.line(surface, (140, 50, 10), (r.x + cx, r.y), (r.x + cx, r.bottom), 1)


class Tuberia(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, alto):
        super().__init__()
        self.rect = pygame.Rect(x, y, ancho, alto)

    def draw(self, surface, offset_x):
        r = self.rect.move(-offset_x, 0)
        # Cuerpo
        pygame.draw.rect(surface, COLOR_TUBERIA, r)
        pygame.draw.rect(surface, COLOR_TUBERIA_OSCURO, (r.right - 8, r.y, 8, r.height))
        # Cabeza de la tubería
        cabeza = pygame.Rect(r.x - 4, r.y, r.width + 8, 16)
        pygame.draw.rect(surface, COLOR_TUBERIA, cabeza)
        pygame.draw.rect(surface, (0, 60, 0), cabeza, 2)


class Ladrillo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TAMANO_TILE, TAMANO_TILE)

    def draw(self, surface, offset_x):
        r = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surface, COLOR_LADRILLO, r)
        pygame.draw.rect(surface, COLOR_LADRILLO_BORDE, r, 2)
        # Detalle de líneas de ladrillo
        pygame.draw.line(surface, COLOR_LADRILLO_BORDE, (r.x, r.centery), (r.right, r.centery), 2)
        pygame.draw.line(surface, COLOR_LADRILLO_BORDE, (r.centerx, r.y), (r.centerx, r.centery), 2)


class BloquePregunta(pygame.sprite.Sprite):
    def __init__(self, x, y, tiene_moneda=True):
        super().__init__()
        self.rect = pygame.Rect(x, y, TAMANO_TILE, TAMANO_TILE)
        self.tiene_moneda = tiene_moneda
        self.activado = False
        self.anim_rebote = 0

    def golpear(self, nivel):
        if not self.activado:
            self.activado = True
            self.anim_rebote = -6
            if self.tiene_moneda:
                nivel.monedas += 1
                nivel.puntuacion += 200
                nivel.particulas.append(EfectoMoneda(self.rect.centerx, self.rect.y))

    def update(self):
        if self.anim_rebote < 0:
            self.anim_rebote += 1

    def draw(self, surface, offset_x, fuente):
        r = self.rect.move(-offset_x, self.anim_rebote)
        if not self.activado:
            pygame.draw.rect(surface, COLOR_BLOQUE_Q, r)
            pygame.draw.rect(surface, (180, 90, 0), r, 2)
            # Dibujar signo de interrogación '?'
            txt = fuente.render("?", True, COLOR_BLANCO)
            txt_rect = txt.get_rect(center=r.center)
            surface.blit(txt, txt_rect)
        else:
            pygame.draw.rect(surface, COLOR_BLOQUE_Q_USADO, r)
            pygame.draw.rect(surface, (80, 60, 40), r, 2)


class EfectoMoneda:
    """Animación visual de la moneda que sale del bloque '?'."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -8.0
        self.gravedad = 0.5
        self.vida = 25

    def update(self):
        self.y += self.vy
        self.vy += self.gravedad
        self.vida -= 1

    def draw(self, surface, offset_x):
        r = pygame.Rect(self.x - offset_x - 6, self.y, 12, 16)
        pygame.draw.ellipse(surface, COLOR_MONEDA, r)
        pygame.draw.ellipse(surface, (255, 255, 200), (r.x + 2, r.y + 2, 4, 12))


class ParticulaLadrillo:
    """Pedazos de ladrillo cuando Mario los rompe al golpear."""
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVEDAD

    def draw(self, surface, offset_x):
        pygame.draw.rect(surface, COLOR_LADRILLO, (self.x - offset_x, self.y, 8, 8))


# ---------------------------------------------------------------------------
# CLASE ENEMIGO (GOOMBA)
# ---------------------------------------------------------------------------
class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 28, 28)
        self.vx = -1.2
        self.vy = 0.0
        self.vivo = True
        self.tiempo_muerto = 0
        self.sprite_vivo = crear_sprite_goomba()
        self.sprite_aplastado = crear_sprite_goomba_aplastado()

    def aplastar(self):
        self.vivo = False
        self.tiempo_muerto = 20
        self.rect.height = 12
        self.rect.y += 16

    def update(self, obstaculos):
        if not self.vivo:
            self.tiempo_muerto -= 1
            return

        # Movimiento horizontal y colisiones
        self.rect.x += int(self.vx)
        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                if self.vx > 0:
                    self.rect.right = obs.rect.left
                    self.vx = -self.vx
                elif self.vx < 0:
                    self.rect.left = obs.rect.right
                    self.vx = -self.vx

        # Gravedad y colisión vertical
        self.vy += GRAVEDAD
        if self.vy > 10:
            self.vy = 10
        self.rect.y += int(self.vy)

        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                if self.vy > 0:
                    self.rect.bottom = obs.rect.top
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = obs.rect.bottom
                    self.vy = 0

    def draw(self, surface, offset_x):
        r = self.rect.move(-offset_x, 0)
        if self.vivo:
            surface.blit(self.sprite_vivo, r)
        else:
            surface.blit(self.sprite_aplastado, r)


# ---------------------------------------------------------------------------
# CLASE MARIO (JUGADOR)
# ---------------------------------------------------------------------------
class Mario(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 24, 32)
        self.vx = 0.0
        self.vy = 0.0
        self.en_suelo = False
        self.mirando_derecha = True
        self.agachado = False
        self.muerto = False
        self.sprite_base = crear_sprite_mario()

    def update(self, teclas, nivel):
        if self.muerto:
            self.vy += GRAVEDAD
            self.rect.y += int(self.vy)
            return

        # --- CONTROLES DE MOVIMIENTO ('A' / 'D') ---
        mov_x = 0
        if teclas[pygame.K_d]:
            mov_x += 1
            self.mirando_derecha = True
        if teclas[pygame.K_a]:
            mov_x -= 1
            self.mirando_derecha = False

        # 'S' para agacharse
        self.agachado = teclas[pygame.K_s] and self.en_suelo

        # Aceleración horizontal e inercia
        if mov_x != 0 and not self.agachado:
            self.vx += mov_x * ACELERACION_X
            if abs(self.vx) > VELOCIDAD_MAX_X:
                self.vx = VELOCIDAD_MAX_X if self.vx > 0 else -VELOCIDAD_MAX_X
        else:
            self.vx *= FRICCION
            if abs(self.vx) < 0.1:
                self.vx = 0.0

        # --- APLICAR MOVIMIENTO HORIZONTAL Y COLISIONES ---
        self.rect.x += int(self.vx)
        obstaculos = nivel.obtener_solidos()

        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                if self.vx > 0:
                    self.rect.right = obs.rect.left
                    self.vx = 0
                elif self.vx < 0:
                    self.rect.left = obs.rect.right
                    self.vx = 0

        # No permitir retroceder más allá del margen izquierdo de la cámara
        if self.rect.left < nivel.camara_x:
            self.rect.left = nivel.camara_x
            self.vx = 0

        # --- GRAVEDAD Y SALTO ---
        self.vy += GRAVEDAD
        if self.vy > 12:
            self.vy = 12

        # --- APLICAR MOVIMIENTO VERTICAL Y COLISIONES ---
        self.rect.y += int(self.vy)
        self.en_suelo = False

        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                if self.vy > 0:  # Aterrizar sobre bloque
                    self.rect.bottom = obs.rect.top
                    self.vy = 0
                    self.en_suelo = True
                elif self.vy < 0:  # Golpear cabeza con techo
                    self.rect.top = obs.rect.bottom
                    self.vy = 0

                    # Interacción con bloques rompibles y cajas '?'
                    if isinstance(obs, BloquePregunta):
                        obs.golpear(nivel)
                    elif isinstance(obs, Ladrillo):
                        nivel.romper_ladrillo(obs)

        # Caída al vacío (muerte)
        if self.rect.top > ALTO_VENTANA + 50:
            self.morir()

    def saltar(self):
        """Ejecuta el salto si Mario está en el suelo."""
        if self.en_suelo and not self.muerto:
            self.vy = IMPULSO_SALTO
            self.en_suelo = False

    def morir(self):
        if not self.muerto:
            self.muerto = True
            self.vy = -12.0  # Animación clásica de salto al morir

    def draw(self, surface, offset_x):
        r = self.rect.move(-offset_x, 0)
        sprite = self.sprite_base

        if not self.mirando_derecha:
            sprite = pygame.transform.flip(sprite, True, False)

        if self.agachado:
            # Escala comprimida para simular agachado
            sprite = pygame.transform.scale(sprite, (24, 20))
            surface.blit(sprite, (r.x, r.y + 12))
        else:
            surface.blit(sprite, r)


# ---------------------------------------------------------------------------
# GESTIÓN DEL NIVEL 1-1 (MAPA, SIDE-SCROLLING, ENEMIGOS)
# ---------------------------------------------------------------------------
class Nivel:
    def __init__(self):
        self.camara_x = 0
        self.monedas = 0
        self.puntuacion = 0
        self.particulas = []
        self.ladrillo_particulas = []
        self.victoria = False
        self.mario = Mario(80, 300)

        # Colección de elementos del mapa
        self.suelos = []
        self.tuberias = []
        self.ladrillos = []
        self.bloques_q = []
        self.goombas = []

        self.construir_mundo()

    def construir_mundo(self):
        """Construye la réplica del trazado inicial del nivel 1-1."""
        y_suelo = ALTO_VENTANA - (TAMANO_TILE * 2)

        # Suelos principales con huecos clásicos del nivel 1-1
        self.suelos.append(BloqueSuelo(0, y_suelo, 2150, TAMANO_TILE * 2))
        self.suelos.append(BloqueSuelo(2220, y_suelo, 450, TAMANO_TILE * 2))  # Hueco 1
        self.suelos.append(BloqueSuelo(2740, y_suelo, 2000, TAMANO_TILE * 2)) # Hueco 2

        # Tuberías verdes
        self.tuberias.append(Tuberia(520, y_suelo - 48, 48, 48))
        self.tuberias.append(Tuberia(750, y_suelo - 72, 48, 72))
        self.tuberias.append(Tuberia(1000, y_suelo - 96, 48, 96))
        self.tuberias.append(Tuberia(1350, y_suelo - 96, 48, 96))
        self.tuberias.append(Tuberia(2400, y_suelo - 64, 48, 64))

        # Formación clásica de bloques: [?] [Ladrillo] [?] [Ladrillo] [?]
        y_fila1 = y_suelo - 120
        self.bloques_q.append(BloquePregunta(320, y_fila1))
        self.ladrillos.append(Ladrillo(352, y_fila1))
        self.bloques_q.append(BloquePregunta(384, y_fila1))
        self.ladrillos.append(Ladrillo(416, y_fila1))
        self.bloques_q.append(BloquePregunta(448, y_fila1))

        # Bloque '?' solitario elevado
        self.bloques_q.append(BloquePregunta(384, y_fila1 - 80))

        # Grupo de ladrillos más adelante
        for i in range(5):
            self.ladrillos.append(Ladrillo(1200 + i * TAMANO_TILE, y_fila1))

        # Bloque de interrogación con moneda entre tuberías
        self.bloques_q.append(BloquePregunta(1450, y_fila1))
        self.bloques_q.append(BloquePregunta(1700, y_fila1))

        # Enemigos Goombas colocados en puntos clave
        pos_goombas = [650, 880, 1150, 1250, 1550, 1800, 2050]
        for gx in pos_goombas:
            self.goombas.append(Goomba(gx, y_suelo - 28))

        # Asta de Bandera (Final del nivel)
        self.pos_bandera_x = 3400
        self.bandera_y = y_suelo - 240

    def obtener_solidos(self):
        """Retorna todos los objetos sólidos que causan colisión."""
        return self.suelos + self.tuberias + self.ladrillos + self.bloques_q

    def romper_ladrillo(self, ladrillo):
        """Elimina el ladrillo y genera partículas de escombros."""
        if ladrillo in self.ladrillos:
            self.ladrillos.remove(ladrillo)
            self.puntuacion += 50
            # Generar 4 partículas expulsadas en arco
            centro_x, centro_y = ladrillo.rect.centerx, ladrillo.rect.centery
            self.ladrillo_particulas.extend([
                ParticulaLadrillo(centro_x, centro_y, -3, -8),
                ParticulaLadrillo(centro_x, centro_y, 3, -8),
                ParticulaLadrillo(centro_x, centro_y, -2, -5),
                ParticulaLadrillo(centro_x, centro_y, 2, -5),
            ])

    def update(self, teclas):
        # Actualizar a Mario
        self.mario.update(teclas, self)

        # Actualizar bloques interactivos
        for b in self.bloques_q:
            b.update()

        # Actualizar partículas
        for p in self.particulas[:]:
            p.update()
            if p.vida <= 0:
                self.particulas.remove(p)

        for lp in self.ladrillo_particulas[:]:
            lp.update()
            if lp.y > ALTO_VENTANA:
                self.ladrillo_particulas.remove(lp)

        solidos = self.obtener_solidos()

        # Actualizar Goombas y procesar colisiones con Mario
        for g in self.goombas[:]:
            # Solo actualizar si está cerca de la pantalla visible
            if abs(g.rect.x - self.mario.rect.x) < 900:
                g.update(solidos)

            if not g.vivo and g.tiempo_muerto <= 0:
                self.goombas.remove(g)
                continue

            # Colisión Mario <-> Goomba
            if g.vivo and not self.mario.muerto and self.mario.rect.colliderect(g.rect):
                # Si Mario cae sobre el Goomba (aplastamiento)
                if self.mario.vy > 0 and self.mario.rect.bottom <= g.rect.top + 14:
                    g.aplastar()
                    self.mario.vy = REBOTE_ENEMIGO  # Rebote satisfactorio
                    self.puntuacion += 100
                else:
                    # Choque lateral: Mario muere
                    self.mario.morir()

        # Condición de Victoria (tocar el poste de la bandera)
        if not self.victoria and self.mario.rect.x >= self.pos_bandera_x:
            self.victoria = True
            self.puntuacion += 1000

        # --- SIDE-SCROLLING (Cámara que sigue a Mario hacia adelante) ---
        margen_derecho = self.camara_x + (ANCHO_VENTANA * 0.45)
        if self.mario.rect.x > margen_derecho:
            self.camara_x = int(self.mario.rect.x - (ANCHO_VENTANA * 0.45))


# ---------------------------------------------------------------------------
# BUCLE PRINCIPAL DE JUEGO
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Super Mario Bros - Nivel 1-1")
    reloj = pygame.time.Clock()

    fuente_retro = pygame.font.SysFont("Courier", 18, bold=True)
    fuente_grande = pygame.font.SysFont("Arial", 36, bold=True)
    fuente_signo = pygame.font.SysFont("Arial", 22, bold=True)

    nivel = Nivel()
    corriendo = True

    while corriendo:
        teclas = pygame.key.get_pressed()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False

                elif evento.key == pygame.K_SPACE:
                    # Barra espaciadora para salto
                    nivel.mario.saltar()

                elif evento.key == pygame.K_r:
                    # Reiniciar en caso de Game Over o Victoria
                    if nivel.mario.muerto or nivel.victoria:
                        nivel = Nivel()

        # Actualizar física y lógica
        nivel.update(teclas)

        # -------------------------------------------------------------------
        # RENDERIZADO
        # -------------------------------------------------------------------
        pantalla.fill(COLOR_CIELO)
        cam = nivel.camara_x

        # Nubes de adorno de fondo
        for nx in range(100, 4000, 450):
            r_nube = pygame.Rect(nx - int(cam * 0.5), 70, 70, 24)
            pygame.draw.ellipse(pantalla, (255, 255, 255), r_nube)
            pygame.draw.ellipse(pantalla, (255, 255, 255), (r_nube.x + 15, r_nube.y - 10, 40, 26))

        # Dibujar suelos
        for s in nivel.suelos:
            s.draw(pantalla, cam)

        # Dibujar tuberías
        for t in nivel.tuberias:
            t.draw(pantalla, cam)

        # Dibujar bloques y ladrillos
        for l in nivel.ladrillos:
            l.draw(pantalla, cam)

        for b in nivel.bloques_q:
            b.draw(pantalla, cam, fuente_signo)

        # Dibujar asta y bandera final
        asta_rect = pygame.Rect(nivel.pos_bandera_x - cam, nivel.bandera_y, 8, 240)
        pygame.draw.rect(pantalla, COLOR_ASTA, asta_rect)
        bandera_rect = pygame.Rect(nivel.pos_bandera_x - cam - 32, nivel.bandera_y + 10, 32, 24)
        pygame.draw.polygon(pantalla, COLOR_BANDERA, [
            (bandera_rect.right, bandera_rect.top),
            (bandera_rect.left, bandera_rect.centery),
            (bandera_rect.right, bandera_rect.bottom)
        ])

        # Dibujar partículas de moneda y ladrillo
        for p in nivel.particulas:
            p.draw(pantalla, cam)
        for lp in nivel.ladrillo_particulas:
            lp.draw(pantalla, cam)

        # Dibujar Goombas
        for g in nivel.goombas:
            g.draw(pantalla, cam)

        # Dibujar a Mario
        nivel.mario.draw(pantalla, cam)

        # --- INTERFAZ HUD SUPERIOR (Puntuación, Monedas, Nivel) ---
        hud_txt = (
            f"MARIO       MONEDAS       MUNDO       TIEMPO\n"
            f"{nivel.puntuacion:06d}        x{nivel.monedas:02d}          1-1          400"
        )
        lineas = hud_txt.split("\n")
        pantalla.blit(fuente_retro.render(lineas[0], True, COLOR_BLANCO), (30, 16))
        pantalla.blit(fuente_retro.render(lineas[1], True, (252, 216, 0)), (30, 36))

        # Pantalla de GAME OVER
        if nivel.mario.muerto:
            t_go = fuente_grande.render("GAME OVER", True, (240, 40, 40))
            t_rect = t_go.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 20))
            pantalla.blit(t_go, t_rect)

            t_sub = fuente_retro.render("Presiona 'R' para volver a intentar", True, COLOR_BLANCO)
            t_sub_rect = t_sub.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 30))
            pantalla.blit(t_sub, t_sub_rect)

        # Pantalla de VICTORIA
        elif nivel.victoria:
            t_win = fuente_grande.render("¡NIVEL 1-1 COMPLETADO!", True, (255, 215, 0))
            t_rect = t_win.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 20))
            pantalla.blit(t_win, t_rect)

            t_sub = fuente_retro.render("Presiona 'R' para jugar de nuevo", True, COLOR_BLANCO)
            t_sub_rect = t_sub.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 30))
            pantalla.blit(t_sub, t_sub_rect)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

