#CAMBIOS:
#cambié mapa por self en: def pasar_de_nivel(self)

import pygame
import random
import math
import os
_base = os.path.dirname(os.path.abspath(__file__))

base_dir = os.path.dirname(os.path.abspath(__file__))

# ---------------- SPRITES / ANIMACIONES ----------------

def _pixel_es_pacman(color):
    """Detecta los pixeles amarillos/naranjas del spritesheet y descarta fondo/texto."""
    r, g, b, a = color
    return a > 0 and r > 140 and 70 <= g <= 210 and b < 90


def cortar_sprite_pacman(sheet, rect, tamaño_final):
    """
    Recorta un frame del spritesheet y deja transparente todo lo que no sea Pacman.
    Esto es importante porque el spritesheet tiene fondo negro/gris opaco.
    """
    x, y, ancho, alto = rect
    recorte = sheet.subsurface(pygame.Rect(x, y, ancho, alto)).copy().convert_alpha()

    for py in range(recorte.get_height()):
        for px in range(recorte.get_width()):
            if not _pixel_es_pacman(recorte.get_at((px, py))):
                recorte.set_at((px, py), (0, 0, 0, 0))

    return pygame.transform.scale(recorte, (tamaño_final, tamaño_final))


def cargar_animaciones_pacman(ruta_spritesheet, tamaño_final):
    """
    Carga la animacion normal de Pacman.
    Del spritesheet usamos solo los frames de Pacman hacia la derecha y generamos
    izquierda/arriba/abajo con flip/rotaciones.
    """
    sheet = pygame.image.load(ruta_spritesheet).convert_alpha()

    cerrado = cortar_sprite_pacman(sheet, (0, 0, 16, 16), tamaño_final)
    medio_abierto = cortar_sprite_pacman(sheet, (17, 0, 16, 16), tamaño_final)
    abierto = cortar_sprite_pacman(sheet, (34, 0, 16, 16), tamaño_final)

    derecha = [cerrado, medio_abierto, abierto, medio_abierto]
    izquierda = [pygame.transform.flip(frame, True, False) for frame in derecha]
    arriba = [pygame.transform.rotate(frame, 90) for frame in derecha]
    abajo = [pygame.transform.rotate(frame, -90) for frame in derecha]

    return {
        (1, 0): derecha,
        (-1, 0): izquierda,
        (0, -1): arriba,
        (0, 1): abajo,
    }


def cargar_animacion_muerte(ruta_spritesheet, tamaño_final):
    """Carga los frames pequeños de muerte ubicados en la segunda fila del spritesheet."""
    sheet = pygame.image.load(ruta_spritesheet).convert_alpha()

    # Los frames de muerte estan en la fila y=19/20 aprox., separados cada 17 px.
    xs = [0, 17, 34, 51, 68, 85, 102, 119, 136]
    frames = [cortar_sprite_pacman(sheet, (x, 19, 16, 16), tamaño_final) for x in xs]
    return frames


class Mapa:
    def __init__(self, file, ancho=28, alto=31):
        self.file = file
        self.ancho = ancho
        self.alto = alto
        self.mapa = self.generar_mapa()

    def generar_mapa(self):
        with open(self.file, mode="r", encoding="utf-8") as file:
            lineas = [linea.rstrip("\n") for linea in file.readlines()]

        lineas_final = []
        for linea in lineas:
            if len(linea) < self.ancho:
                linea += "X" * (self.ancho - len(linea))
            elif len(linea) > self.ancho:
                linea = linea[: self.ancho]
            lineas_final.append(list(linea))

        if len(lineas_final) < self.alto:
            for _ in range(self.alto - len(lineas_final)):
                lineas_final.append(list("X" * self.ancho))
        elif len(lineas_final) > self.alto:
            lineas_final = lineas_final[: self.alto]

        caracteres_validos = " X.GPTo-"
        cantidad_pacman = 0
        existe_ghost_house = False
        existe_puerta = False
        existe_comida = False

        for fila in lineas_final:
            for caracter in fila:
                if caracter not in caracteres_validos:
                    raise ValueError(f"Caracter invalido en el mapa: {caracter!r}")
                if caracter == "P":
                    cantidad_pacman += 1
                elif caracter == "G":
                    existe_ghost_house = True
                elif caracter == "-":
                    existe_puerta = True
                elif caracter in ".o":
                    existe_comida = True

        if cantidad_pacman == 0:
            raise ValueError("Posicion inicial de Pacman no definida")
        if cantidad_pacman > 1:
            raise ValueError("Mas de una posicion inicial de Pacman definida")
        if not existe_ghost_house:
            raise ValueError("Posicion inicial de Ghost House no definida")
        if not existe_puerta:
            raise ValueError("No hay puerta de Ghost House definida en el mapa")
        if not existe_comida:
            raise ValueError("No hay comida definida en el mapa")

        return lineas_final

    def posicion_pacman_gostHouse(self):
        """Devuelve posicion de Pacman como (columna, fila) y lista de posiciones G."""
        cord_pacman = None
        cords_ghost_house = []

        for fila, linea in enumerate(self.mapa):
            for columna, valor in enumerate(linea):
                if valor == "P":
                    cord_pacman = (columna, fila)
                elif valor == "G":
                    cords_ghost_house.append((columna, fila))

        return cord_pacman, cords_ghost_house
    
    def pasar_de_nivel(self):
        for fila in self.mapa:
            for columna in fila:
                if columna == "." or columna == "o":
                    return False
        return True

    def posicion_valida(self, fila, columna):
        return 0 <= fila < len(self.mapa) and 0 <= columna < len(self.mapa[0])

    def celda_bloqueada(self, fila, columna, ignorar_puerta=False):
        """True si la celda no existe, o si es pared/puerta."""
        if not self.posicion_valida(fila, columna):
            return True
        if ignorar_puerta:
            return self.mapa[fila][columna] == "X"
        return self.mapa[fila][columna] in ('X', '-')

    def celda_libre(self, fila, columna, ignorar_puerta=False):
        return not self.celda_bloqueada(fila, columna, ignorar_puerta)

    def posicion_libre(self, fila, columna, direccion=None): # agregar ignorar puerta
        """Compatibilidad con versiones anteriores."""
        return self.celda_libre(int(fila), int(columna))


class Personaje:
    def __init__(self, fila, columna, imagen_ruta, velocidad=1, tamaño_bloque=20):
        # En esta version la posicion logica SIEMPRE es una celda entera.
        self.fila = int(fila)
        self.columna = int(columna)
        self.fila_inicial = int(fila)
        self.columna_inicial = int(columna)
        self.velocidad = velocidad
        self.tamaño_bloque = tamaño_bloque
        self.direccion_actual = None

        self.imagen_org = pygame.image.load(os.path.join(_base, imagen_ruta)).convert_alpha()
        # La imagen es un poco menor que la celda. Visualmente no pisa paredes.
        self.margen = max(2, tamaño_bloque // 10)
        tamaño_imagen = tamaño_bloque - 2 * self.margen
        self.imagen = pygame.transform.scale(self.imagen_org, (tamaño_imagen, tamaño_imagen))
        self.rect = self.imagen.get_rect()
        self._actualizar_rect_desde_celda()

    def _actualizar_rect_desde_celda(self):
        self.rect.x = self.columna * self.tamaño_bloque + self.margen
        self.rect.y = self.fila * self.tamaño_bloque + self.margen

    def calcular_nueva_posicion(self, direccion, dt=None):
        if direccion is None:
            return self.fila, self.columna
        nueva_fila = self.fila + direccion[1]
        nueva_columna = self.columna + direccion[0]
        return nueva_fila, nueva_columna

    def mover_a_celda(self, fila, columna):
        self.fila = int(fila)
        self.columna = int(columna)
        self._actualizar_rect_desde_celda()

    def misma_posicion(self, otro):
        return self.fila == otro.fila and self.columna == otro.columna

    def posicion(self):
        return self.fila, self.columna

    def celda_actual(self):
        return self.fila, self.columna

    def reiniciar_posicion(self):
        self.fila = self.fila_inicial
        self.columna = self.columna_inicial
        self.direccion_actual = None
        self._actualizar_rect_desde_celda()

    def aplicar_tunel(self, mapa):
        if mapa.mapa[self.fila][self.columna] == "T":
            if self.columna == 0:
                self.columna = len(mapa.mapa[0]) - 1
            elif self.columna == len(mapa.mapa[0]) - 1:
                self.columna = 0
            self._actualizar_rect_desde_celda()

class Pacman(Personaje):
    def __init__(
        self,
        fila,
        columna,
        imagen_ruta="pacman_trucho.jpg",
        velocidad=1,
        tamaño_bloque=20,
        spritesheet_ruta="pacsprites.png",
    ):
        super().__init__(fila, columna, imagen_ruta, velocidad, tamaño_bloque)
        self.puntaje = 0
        self.modo_power = False
        self.vidas = 3
        self.tiempo_power = 0.0
        self.vida_extra_otorgada = False
        self.multiplicador = 1

        self.frame_actual = 0
        self.tiempo_muerte = 0.0
        self.frame_muerte = 0
        self.muerto = False
        self.muerte_terminada = False

        # Sprites: si falla la carga, queda la imagen vieja como fallback.
        self.sonido_muerte = pygame.mixer.Sound(os.path.join(base_dir,"pacman-dies.mp3"))
        self.animaciones = None
        self.animacion_muerte = []
        try:
            tamaño_imagen = tamaño_bloque - 2 * self.margen
            self.animaciones = cargar_animaciones_pacman(spritesheet_ruta, tamaño_imagen)
            self.animacion_muerte = cargar_animacion_muerte(spritesheet_ruta, tamaño_imagen)
            self.direccion_actual = (1, 0)
            self.imagen = self.animaciones[self.direccion_actual][0]
            self.rect = self.imagen.get_rect()
            self._actualizar_rect_desde_celda()
        except (pygame.error, FileNotFoundError):
            self.animaciones = None
            self.animacion_muerte = []

    def _actualizar_sprite_movimiento(self):
        if self.animaciones is None or self.direccion_actual is None:
            return
        frames = self.animaciones[self.direccion_actual]
        self.frame_actual = (self.frame_actual + 1) % len(frames)
        self.imagen = frames[self.frame_actual]

    def iniciar_muerte(self):
        """Activa la animacion de muerte. Mientras corre, Pacman no se mueve."""
        if self.muerto:
            return
        self.muerto = True
        self.muerte_terminada = False
        self.tiempo_muerte = 0.0
        self.frame_muerte = 0
        if self.animacion_muerte:
            self.imagen = self.animacion_muerte[0]
        self.sonido_muerte.play()

    def actualizar_muerte(self, dt):
        """
        Avanza la animacion de muerte.
        Devuelve True cuando termina, para que el juego pueda reiniciar la posicion.
        """
        if not self.muerto:
            return False
        if not self.animacion_muerte:
            self.muerto = False
            return True

        self.tiempo_muerte += dt
        if self.tiempo_muerte >= 0.10:
            self.tiempo_muerte = 0.0
            self.frame_muerte += 1

            if self.frame_muerte >= len(self.animacion_muerte):
                self.muerto = False
                self.muerte_terminada = True
                return True

            self.imagen = self.animacion_muerte[self.frame_muerte]

        return False

    def reiniciar_posicion(self):
        super().reiniciar_posicion()
        self.muerto = False
        self.muerte_terminada = False
        self.frame_muerte = 0
        self.tiempo_muerte = 0.0
        self.direccion_actual = (1, 0)
        self.frame_actual = 0
        if self.animaciones is not None:
            self.imagen = self.animaciones[self.direccion_actual][0]
            self.rect = self.imagen.get_rect()
            self._actualizar_rect_desde_celda()

    def puede_mover(self, direccion, mapa, ignorar_puerta=False):
        if direccion is None:
            return False
        fila_destino = self.fila + direccion[1]
        columna_destino = self.columna + direccion[0]
        return mapa.celda_libre(fila_destino, columna_destino, ignorar_puerta)

    def mover_pacman(self, direccion, mapa, dt=None, tamaño_bloque=None):
        """
        Movimiento por grilla: avanza exactamente una celda cada vez.
        Si la tecla queda mantenida, juego.py llama repetidamente a esta funcion.
        """
        if self.muerto:
            return False
        if not self.puede_mover(direccion, mapa):
            return False

        self.fila += direccion[1]
        self.columna += direccion[0]
        self.aplicar_tunel(mapa)
        self.direccion_actual = direccion
        self._actualizar_sprite_movimiento()
        self._actualizar_rect_desde_celda()
        return True

    def comer_pelotita(self, variable_mapa):
        fila, columna = self.celda_actual()
        if variable_mapa.mapa[fila][columna] == ".":
            variable_mapa.mapa[fila][columna] = " "
            self.puntaje += 10

    def comer_power_pellet(self, variable_mapa):
        fila, columna = self.celda_actual()
        if variable_mapa.mapa[fila][columna] == "o":
            variable_mapa.mapa[fila][columna] = " "
            self.puntaje += 50
            self.modo_power = True
            self.tiempo_power = 6.0
            return True 
        return False

    def actualizar_tiempo_power(self, dt):
        if self.modo_power:
            self.tiempo_power -= dt
            if self.tiempo_power <= 0:
                self.modo_power = False
                self.tiempo_power = 0.0
        return self.modo_power

    def comer_fantasmas(self, fantasma):
        self.puntaje += 200 * self.multiplicador 
        self.multiplicador += 1
        fantasma.estado_asustado = False
        fantasma.estado_ojos = True 
        fantasma.cambiar_imagen('ojos.png')

    def dar_vida_extra(self):
        if self.puntaje >= 10000 and not self.vida_extra_otorgada:
            self.vidas += 1
            self.vida_extra_otorgada = True


class Fantasma(Personaje):
    def __init__(self, fila, columna, imagen_ruta, velocidad, nombre, color, esquina_scatter: tuple, tamaño_bloque=20):
        super().__init__(fila, columna, imagen_ruta, velocidad, tamaño_bloque)
        self.nombre = nombre
        self.color = color
        self.modo = "SCATTER"
        self.esquina_scatter = esquina_scatter
        self.estado_asustado = False
        self.archivo_imagen = imagen_ruta 
        self.estado_ojos = False

    def mover_fantasma(self, futura_columna, futura_fila, direccion, mapa):
        self.mover_a_celda(futura_fila, futura_columna)
        self.aplicar_tunel(mapa)
        self.direccion_actual = direccion

    def celdas_posibles_movimiento(self, mapa, ignorar_puerta=False):
        if self.direccion_actual is None:
            self.direccion_actual = (0, -1)

        direcciones = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        direcciones_validas = {}

        for direc in direcciones:
            # Evita volver directamente hacia atras.
            if self.direccion_actual[0] + direc[0] == 0 and self.direccion_actual[1] + direc[1] == 0:
                continue

            nueva_fila, nueva_columna = self.calcular_nueva_posicion(direc)
            if mapa.celda_libre(nueva_fila, nueva_columna, ignorar_puerta):
                direcciones_validas[direc] = (nueva_columna, nueva_fila)

        return direcciones_validas

    def movimiento_aleatorio_asustado(self, mapa, ignorar_puerta=False):
        direc_pos_validas = self.celdas_posibles_movimiento(mapa, ignorar_puerta)
        if not direc_pos_validas:
            return
        direccion_elegida = random.choice(list(direc_pos_validas))
        columna, fila = direc_pos_validas[direccion_elegida]
        self.mover_fantasma(columna, fila, direccion_elegida, mapa)

    def activar_asustado(self, nueva_imagen):
        if self.direccion_actual is not None:
            self.direccion_actual = (-self.direccion_actual[0], -self.direccion_actual[1])
        self.imagen_org = pygame.image.load(os.path.join(_base, nueva_imagen)).convert_alpha()
        tamaño_imagen = self.tamaño_bloque - 2 * self.margen
        self.imagen = pygame.transform.scale(self.imagen_org, (tamaño_imagen, tamaño_imagen))
        self.estado_asustado = True

    def cambiar_imagen (self, imagen):
        self.imagen_org = pygame.image.load(os.path.join(_base, imagen)).convert_alpha()
        tamaño_imagen = self.tamaño_bloque - 2 * self.margen
        self.imagen = pygame.transform.scale(self.imagen_org, (tamaño_imagen, tamaño_imagen))


    def movimiento_optimizado(self, target: tuple, mapa, ignorar_puerta=False):
       
        if target == None:
            return None
        
        direcciones_prioridad = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        direcciones_validas = self.celdas_posibles_movimiento(mapa, ignorar_puerta)
        if not direcciones_validas:
            return None

        distancia_minima = float("inf")
        celdas_optimas = {}

        for direccion, posicion in direcciones_validas.items():
            distancia = ((target[0] - posicion[0]) ** 2 + (target[1] - posicion[1]) ** 2) ** 0.5
            if distancia < distancia_minima:
                distancia_minima = distancia
                celdas_optimas = {direccion: posicion}
            elif distancia == distancia_minima:
                celdas_optimas[direccion] = posicion

        for direccion in direcciones_prioridad:
            if direccion in celdas_optimas:
                return direccion, celdas_optimas[direccion]
        return None




class Blinky(Fantasma):
    def obtener_target_chase(self, pos_pacman):
        return pos_pacman


class Pinky(Fantasma):
    def obtener_target_chase(self, pos_pacman, dir_pacman):
        if dir_pacman == (0, -1):
            fila_target = pos_pacman[1] + dir_pacman[1] * 4
            columna_target = pos_pacman[0] - 4
        else:
            fila_target = pos_pacman[1] + dir_pacman[1] * 4
            columna_target = pos_pacman[0] + dir_pacman[0] * 4
        return columna_target, fila_target

class Inky(Fantasma):
    def obtener_nombre_fantasma(self, fantasmas: list):

        if "blinky" in fantasmas:
            return "blinky"
        fantasmas_copia = fantasmas.copy()
        if "inky" in fantasmas_copia:
            fantasmas_copia.remove("inky")
        if fantasmas_copia:
            return random.choice(fantasmas_copia)
        return None

    def obtener_target_chase(self, pos_pacman: tuple, dir_pacman, pos_fantasma_elegido: tuple):
        if dir_pacman == (0, -1):
            fila_pacman2 = pos_pacman[1] + dir_pacman[1] * 2
            columna_pacman2 = pos_pacman[0] - 2
        else:
            fila_pacman2 = pos_pacman[1] + dir_pacman[1] * 2
            columna_pacman2 = pos_pacman[0] + dir_pacman[0] * 2

        desplazamiento_x = (pos_fantasma_elegido[0] - columna_pacman2) * -1
        desplazamiento_y = (pos_fantasma_elegido[1] - fila_pacman2) * -1
        target_x = columna_pacman2 + desplazamiento_x
        target_y = fila_pacman2 + desplazamiento_y
        return target_x, target_y
    
class Clyde (Fantasma): 
    def obtener_target_chase(self, pos_pacman:tuple):
        distancia_pivote = 8
        fila, columna = self.posicion()
        pos_clyde = (columna, fila)

        distancia = math.sqrt((pos_pacman[0] - pos_clyde[0]) ** 2 + (pos_pacman[1] - pos_clyde[1]) ** 2)

        if distancia >= distancia_pivote:
            return pos_pacman
        else:
            return self.esquina_scatter

class Cookie(Fantasma):
    def obtener_target_chase(self, pos_pacman):        #a distancia menor que 5, no tiene miedo y avanza hacia pacman
        dif_columna = abs(self.columna - pos_pacman[0])
        dif_fila = abs(self.fila - pos_pacman[1])
        distancia = dif_columna + dif_fila

        if distancia <= 5:
            return pos_pacman
        else:
            return self.esquina_scatter
     
        
class Greenky(Fantasma):

    TIEMPO_QUIETO = 2.0      # segundos quieto
    TIEMPO_PERSIGUE = 4.0    # segundos persiguiendo

    def __init__(self, fila, columna, imagen_ruta, velocidad, nombre, color, esquina_scatter):
        super().__init__(fila, columna, imagen_ruta, velocidad, nombre, color, esquina_scatter)
        self.timer = 0.0
        self.congelado = False

    def actualizar_timer(self, dt):
        """Llamar una vez por frame en el loop principal."""
        self.timer += dt
        ciclo = self.TIEMPO_QUIETO + self.TIEMPO_PERSIGUE
        if self.timer >= ciclo:
            self.timer = 0.0  # reinicia el ciclo

        self.congelado = self.timer < self.TIEMPO_QUIETO
        