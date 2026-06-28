###MODIFICACIONES A JUEGO:
#import inicializar
#cambio de colores fantasmas
#sumarle alto del display a la ventana
#guardar_highscore, leerlo y nivel 1 (292-306)
#si se acaban las bolitas se reinicia todo el mapa, se suma =+ al nivel

import pygame
from CLASES import Mapa, Pacman, Blinky, Pinky, Inky, Clyde, Greenky, Cookie
from INICIO import pantalla_selec_fantasmas, pantalla_asignar_esquinas, pantalla_inicio
from DISPLAY import inicializar_display, dibujar_display
import os 


base_dir = os.path.dirname(os.path.abspath(__file__))

pygame.init()

# Ventana chica: 28 * 20 = 560 px, 31 * 20 = 620 px.
TAMANO_BLOQUE = 20
FPS = 60

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
FUXIA = (255, 0, 255)
sonido_waka = pygame.mixer.Sound(os.path.join(base_dir, "pacman-waka-waka.mp3"))

mapa = Mapa(os.path.join(base_dir, "mapa.txt"))
cord_pacman, cords_ghost_house = mapa.posicion_pacman_gostHouse()  # (columna, fila)

alto_display = 40
ancho_ventana = len(mapa.mapa[0]) * TAMANO_BLOQUE 
alto_ventana = len(mapa.mapa) * TAMANO_BLOQUE + alto_display #le sumé el alto del display de vidas para que no se superpongan

ventana = pygame.display.set_mode((ancho_ventana, alto_ventana))
pygame.display.set_caption("PACMAN")
clock = pygame.time.Clock()

# No usamos el autorepeat de pygame. Lo controlamos nosotros con get_pressed()
# para que el movimiento al mantener una tecla sea regular y no dependa del teclado/SO.
pygame.key.set_repeat(0, 0)

pacman = Pacman(
    fila=cord_pacman[1],
    columna=cord_pacman[0],
    imagen_ruta=os.path.join(base_dir,"pacman_trucho.jpg"),
    velocidad=1,
    tamaño_bloque=TAMANO_BLOQUE,
    spritesheet_ruta=os.path.join(base_dir,"pacsprites.png"),
)

# El mapa ya no necesita guardar P/G: esas posiciones quedan libres.
mapa.mapa[cord_pacman[1]][cord_pacman[0]] = " "
for columna, fila in cords_ghost_house:
    mapa.mapa[fila][columna] = " "


TECLAS_DIRECCION = {
    pygame.K_RIGHT: (1, 0),
    pygame.K_LEFT: (-1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
}

# DEFINICION DE ESQUINAS (MODO SCATTER)

ESQUINA_SUP_IZQ = (0, -3)     
ESQUINA_SUP_DER = (27, -3)     
ESQUINA_INF_IZQ = (0, 34)      
ESQUINA_INF_DER = (27, 34)

# FANTASMAS 

blinky = Blinky (
    fila=cords_ghost_house[0][1],
    columna=cords_ghost_house[0][0],
    imagen_ruta='blinky.png',
    velocidad=1,
    nombre='blinky',
    color=(255, 0, 0),
    esquina_scatter = ESQUINA_INF_DER
    )

pinky = Pinky (
    fila=cords_ghost_house[0][1],
    columna=cords_ghost_house[0][0],
    imagen_ruta='pinky.png',
    velocidad=1,
    nombre='pinky',
    color=(255, 184, 255),
    esquina_scatter = ESQUINA_INF_IZQ
    )

inky = Inky (
    fila=cords_ghost_house[0][1],
    columna=cords_ghost_house[0][0],
    imagen_ruta='inky.png',
    velocidad=1,
    nombre='inky',
    color=(0, 255, 255),
    esquina_scatter = ESQUINA_SUP_DER
    )

clyde = Clyde(
    fila=cords_ghost_house[0][1],
    columna=cords_ghost_house[0][0],
    imagen_ruta='clyde.png',
    velocidad=1,
    nombre='clyde',
    color=(243,94,2),
    esquina_scatter = ESQUINA_SUP_IZQ
    )

greenky = Greenky (
    fila=cords_ghost_house[0][1],
    columna=cords_ghost_house[0][0],
    imagen_ruta='greenky.png',
    velocidad=1,
    nombre='greenky',
    color=(50, 205, 50),
    esquina_scatter = ESQUINA_SUP_IZQ

)

cookie = Cookie (
    fila=cords_ghost_house[0][1],
    columna=cords_ghost_house[0][0],
    imagen_ruta='cookie.png',
    velocidad=1,
    nombre='cookie',
    color=(151, 0, 254),
    esquina_scatter = ESQUINA_SUP_IZQ

)


fant_nombre_objeto = {
    "blinky": blinky,
    "inky": inky,
    "pinky": pinky,
    "clyde": clyde,
    "greenky": greenky,
    "cookie": cookie
}


# VELOCIDADES

def ms_por_tile(fraccion):
    ''' devuelve ms cada cuanto debe avanzar cada personaje del juego en un determinado estado'''
    return int(1000 / (fraccion * 7.5))
 
# ── Intervalos de movimiento (ms entre un paso y el siguiente) ──
MS_PACMAN_NORMAL   = ms_por_tile(0.80)   # ≈ 167 ms  (80 %)
MS_PACMAN_POWER    = ms_por_tile(0.90)   # ≈ 148 ms  (90 %)
MS_FANTASMA_NORMAL = ms_por_tile(0.75)   # ≈ 178 ms  (75 %)
MS_FANTASMA_TUNEL  = ms_por_tile(0.40)   # ≈ 333 ms  (40 %)
MS_FANTASMA_ASUST  = ms_por_tile(0.50)   # ≈ 267 ms  (50 %)
MS_FANTASMA_OJOS   = ms_por_tile(1.50)   # ≈  89 ms  (150 %)



def dibujar_mapa(ventana, mapa):
    for fila, linea in enumerate(mapa.mapa):
        for columna, valor in enumerate(linea):
            x = columna * TAMANO_BLOQUE
            y = fila * TAMANO_BLOQUE
            centro_x = x + TAMANO_BLOQUE // 2
            centro_y = y + TAMANO_BLOQUE // 2

            if valor == "X":
                bloque = pygame.Rect(x, y, TAMANO_BLOQUE, TAMANO_BLOQUE)
                pygame.draw.rect(ventana, FUXIA, bloque)
            elif valor == ".":
                pygame.draw.circle(ventana, BLANCO, (centro_x, centro_y), max(2, TAMANO_BLOQUE // 7))
            elif valor == "o":
                pygame.draw.circle(ventana, BLANCO, (centro_x, centro_y), max(4, TAMANO_BLOQUE // 4))
            elif valor == "-":
                puerta = pygame.Rect(x, y + TAMANO_BLOQUE // 3, TAMANO_BLOQUE, max(3, TAMANO_BLOQUE // 6))
                pygame.draw.rect(ventana, FUXIA, puerta)


def mover_y_comer(pacman, direccion, mapa):
    """Mueve una celda, si se puede, y luego come lo que haya en la celda."""
    if direccion is None or pacman.muerto:
        return
    se_movio = pacman.mover_pacman(direccion, mapa)
    if se_movio:
        sonido_waka.play(0)
        pacman.comer_pelotita(mapa)
        if pacman.comer_power_pellet(mapa):
            for f in fantasmas_elegidos:
                f.activar_asustado('asustado.png')


def direccion_mantenida(teclas, direccion_actual):
    """
    Devuelve la direccion que debe repetirse mientras hay teclas apretadas.
    Prioriza la ultima direccion elegida, para que mantener una tecla siga moviendo
    en esa direccion aunque haya otras teclas presionadas accidentalmente.
    """
    if direccion_actual == (1, 0) and teclas[pygame.K_RIGHT]:
        return (1, 0)
    if direccion_actual == (-1, 0) and teclas[pygame.K_LEFT]:
        return (-1, 0)
    if direccion_actual == (0, -1) and teclas[pygame.K_UP]:
        return (0, -1)
    if direccion_actual == (0, 1) and teclas[pygame.K_DOWN]:
        return (0, 1)

    # Si la ultima direccion ya no esta presionada, tomamos alguna flecha activa.
    if teclas[pygame.K_RIGHT]:
        return (1, 0)
    if teclas[pygame.K_LEFT]:
        return (-1, 0)
    if teclas[pygame.K_UP]:
        return (0, -1)
    if teclas[pygame.K_DOWN]:
        return (0, 1)

    return None

def salida_gohst_house (fantasmas_activos, pacman):
        puntos = [0,30,60,90]
        for i in range(4):
            if fantasmas_activos[i]==False and pacman.puntaje >= puntos[i]:
                fantasmas_activos[i] = True


def obtener_posicon_puerta ():
    for fila, linea in enumerate(mapa.mapa):
        for columna, valor in enumerate(linea):
            if valor == "-":
                pos_puerta = (columna, fila)
    return pos_puerta

fantasmas_disponibles = [blinky, pinky, inky, clyde, greenky, cookie]

if not pantalla_inicio(ventana, NEGRO, BLANCO, ancho_ventana, alto_ventana):
    pygame.quit()
    exit()

fantasmas_elegidos = pantalla_selec_fantasmas(
    fantasmas_disponibles, ventana, NEGRO, BLANCO, ancho_ventana, alto_ventana
)
if fantasmas_elegidos is None:
    pygame.quit()
    exit()

fantasmas_elegidos = pantalla_asignar_esquinas(
    fantasmas_elegidos, ventana, NEGRO, BLANCO, ancho_ventana, alto_ventana
)
for f in fantasmas_elegidos:
    print(f.nombre, f.esquina_scatter)
if fantasmas_elegidos is None:
    pygame.quit()
    exit()


def pantalla_gameover (ventana, clock):

    fuente = pygame.font.SysFont("freesansbold", 48)
    texto = fuente.render("GAME OVER", True, (255, 0, 0))
    texto_rect = texto.get_rect(center=(ancho_ventana // 2, alto_ventana // 2))
    
    inicio = pygame.time.get_ticks()
    while pygame.time.get_ticks() - inicio < 3000:
        ventana.fill(NEGRO)
        ventana.blit(texto, texto_rect)
        pygame.display.flip()
        clock.tick(FPS)
    
running = True
direccion_actual = None
ultimo_movimiento_pacman = 0


#fantasmas_elegidos = [clyde, inky, pinky, greenky] 
fantasmas_elegidos_strings = [f.nombre for f in fantasmas_elegidos]
fantasmas_activos = [True, False, False, False]
ultimo_mov_fant_ms = [0,0,0,0]

ciclo = [('scatter', 7), ('chase', 20), ('scatter', 7), ('chase', 20),('scatter', 5),('chase', 20),('scatter', 5),('chase', None)]
modo_general = 'scatter'
tiempo_en_fase = 0.0
indice_fase_actual = 0

fuente_display, icono_vida = inicializar_display(TAMANO_BLOQUE)

ruta_highscore = os.path.join(base_dir, "highscore.txt")
def leer_highscore():
    """Abre un archivo de texto highscore.txt en la misma carpeta que contiene un número.
    Lo lee cuando arranca el juego, si es la primera vez que juego se devuelve 0 con el 'except'."""
    try:
        with open(ruta_highscore, "r") as f: 
            return int(f.read().strip())
    except: 
        return 0

def guardar_highscore(puntaje):
    """Cuando termina el juego, abre el archivo y actualiza el puntaje"""
    with open(ruta_highscore, "w") as f:
        f.write(str(puntaje))

high_score = leer_highscore() #lee puntaje antes de arrancar
nivel = 1 #nivel antes de arrancar

while running:

    dt = clock.tick(FPS) / 1000
    ahora_ms = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key in TECLAS_DIRECCION and not pacman.muerto:
                direccion_actual = TECLAS_DIRECCION[event.key]

                # Primer movimiento inmediato cuando presionas la tecla.
                mover_y_comer(pacman, direccion_actual, mapa) #donde llamamos a mover_y_comer agregué la actualización de puntaje
                ultimo_movimiento_pacman = ahora_ms
                if pacman.puntaje > high_score: 
                    high_score = pacman.puntaje
                    guardar_highscore(high_score)


    if pacman.muerto:
        if pacman.actualizar_muerte(dt):
            pacman.vidas -= 1

            if pacman.vidas <= 0:
                if pacman.puntaje > high_score:
                    high_score = pacman.puntaje
                    guardar_highscore(high_score) #actualizar antes de morirse y game over
                pantalla_gameover(ventana, clock)

                running = False
                break 

            else:
                pacman.reiniciar_posicion()
                pacman.modo_power = False
                pacman.tiempo_power = 0.0

                for f in fantasmas_elegidos:
                    f.reiniciar_posicion()
                    f.estado_asustado = False
                    f.estado_ojos = False
                    f.cambiar_imagen(f.archivo_imagen)

                fantasmas_activos = [True, False, False, False]
                ultimo_movimiento_pacman = ahora_ms
                ultimo_mov_fant_ms = [0,0,0,0]
                if 'greenky' in fantasmas_elegidos_strings:
                    greenky.timer = 0.0
                    greenky.congelado = False
                    indice_fase_actual = 0
                    tiempo_en_fase = 0.0
                    modo_general = 'scatter'

    else:

        # Movimiento repetido mientras la tecla sigue mantenida.
        teclas = pygame.key.get_pressed()
        direccion = direccion_mantenida(teclas, direccion_actual)

        if direccion is not None:
            direccion_actual = direccion
            ms_pacman = MS_PACMAN_POWER if pacman.modo_power else MS_PACMAN_NORMAL
            if ahora_ms - ultimo_movimiento_pacman >= ms_pacman:
                mover_y_comer(pacman, direccion_actual, mapa) #donde llamamos a mover_y_comer agregué la actualización de puntaje
                ultimo_movimiento_pacman = ahora_ms
                if pacman.puntaje > high_score:
                    high_score = pacman.puntaje
                    guardar_highscore(high_score)
                if mapa.pasar_de_nivel():
                    nivel += 1
                    mapa = Mapa(os.path.join(base_dir, "mapa.txt"))
                    mapa.mapa[cord_pacman[1]][cord_pacman[0]] = " "
                    for columna, fila in cords_ghost_house:
                        mapa.mapa[fila][columna] = " "
                    pacman.reiniciar_posicion()
                    pacman.modo_power = False
                    pacman.tiempo_power = 0.0
                    for f in fantasmas_elegidos:
                        f.reiniciar_posicion()
                        f.estado_asustado = False
                        f.estado_ojos = False
                        f.cambiar_imagen(f.archivo_imagen)
                    fantasmas_activos = [True, False, False, False]
                    ultimo_movimiento_pacman = ahora_ms
                    ultimo_mov_fant_ms = [0,0,0,0]
                    indice_fase_actual = 0
                    tiempo_en_fase = 0.0
                    modo_general = 'scatter'

        # FANTASMAS 
        # actualizacion del ciclo asustado 

        if pacman.modo_power:
            pacman.tiempo_power -= dt
            if pacman.tiempo_power <= 0:
                # desactivar 
                pacman.modo_power = False 
                pacman.tiempo_power = 0.0
                for f in fantasmas_elegidos:
                    if f.estado_asustado == True:
                        f.estado_asustado = False 
                        f.cambiar_imagen(f.archivo_imagen)
        
        else:
            # actualizacion de ciclo scatter-chase
            duracion_fase = ciclo[indice_fase_actual][1]

            if duracion_fase != None:
                tiempo_en_fase += dt

                if tiempo_en_fase >= duracion_fase:
                    indice_fase_actual += 1
                    tiempo_en_fase = 0.0
                    modo_general = ciclo[indice_fase_actual][0]

                    # cambio de fase => cambio de direccion de fantasmas
                    for indice, activo in enumerate(fantasmas_activos):

                        if activo:
                            fantasma = fantasmas_elegidos[indice]
                            if fantasma.direccion_actual != None:
                                direccion = fantasma.direccion_actual
                                fantasma.direccion_actual = (-direccion[0], -direccion[1])
        

        # SALIDA DE GOHST HOUSE + MOVIMIENTO SCATTER/CHASE segun ciclo

        salida_gohst_house(fantasmas_activos, pacman)

        if 'greenky' in fantasmas_elegidos_strings:
            greenky.actualizar_timer(dt)

        # MOVIMIENTO FANTASMAS (SCATTER/CHASE)

        for indice, activo in enumerate(fantasmas_activos):
            fantasma = fantasmas_elegidos[indice]

            if fantasma.estado_ojos:
                MS = MS_FANTASMA_OJOS

            elif fantasma.estado_asustado:
                MS = MS_FANTASMA_ASUST
            else:
                MS = MS_FANTASMA_NORMAL
            
            if ahora_ms - ultimo_mov_fant_ms[indice] >= MS:

            # si debe salir de la casa
                if activo:

                    fil_col_fant = fantasma.posicion()

                    if fantasma.estado_ojos:
                        target = cords_ghost_house[0]
                        resultado = fantasma.movimiento_optimizado(target, mapa, ignorar_puerta=True)
                        if resultado:
                            direccion, futura_posicion = resultado
                            fantasma.mover_fantasma(futura_posicion[0], futura_posicion[1], direccion, mapa)
                    
                        if (fil_col_fant[1], fil_col_fant[0]) in cords_ghost_house:
                            fantasma.estado_ojos = False
                            fantasmas_activos[indice] = False
                            fantasma.cambiar_imagen(fantasma.archivo_imagen)

                    elif fantasma.estado_asustado:
                        fantasma.movimiento_aleatorio_asustado(mapa)

                    else:
                            target = None

                            # si esta dentro de la casa
                            if (fil_col_fant[1], fil_col_fant[0]) in cords_ghost_house: 
                                target = obtener_posicon_puerta() # target = puerta
                                ignorar_puerta = True # puerta abierta

                            # si salió de la casa

                            elif modo_general == 'scatter':
                                target = fantasma.esquina_scatter
                                ignorar_puerta = False # puerta cerrada 
                            
                            elif modo_general == 'chase':
                                if fantasma.nombre == 'blinky':
                                    target = blinky.obtener_target_chase((pacman.columna, pacman.fila))
                                
                                elif fantasma.nombre == 'pinky':
                                    target = pinky.obtener_target_chase((pacman.columna, pacman.fila), pacman.direccion_actual)
                                
                                elif fantasma.nombre == 'inky': 
                                    nom_fant_elegido = inky.obtener_nombre_fantasma(fantasmas_elegidos_strings)
                                    obj_fant_elegido = fant_nombre_objeto[nom_fant_elegido]
                                    target = inky.obtener_target_chase((pacman.columna,pacman.fila),pacman.direccion_actual,(obj_fant_elegido.columna, obj_fant_elegido.fila))

                                elif fantasma.nombre == 'clyde':
                                    target = clyde.obtener_target_chase((pacman.columna, pacman.fila))
                                
                                elif fantasma.nombre == 'cookie':
                                    target = cookie.obtener_target_chase((pacman.columna,pacman.fila))

                                elif fantasma.nombre == 'greenky':

                                    if greenky.congelado:

                                        ultimo_mov_fant_ms[indice] = ahora_ms

                                        continue 

                                    else:
                                        target = (pacman.columna, pacman.fila) 


                            # Movimeitno optimizado segun target (tanto para scatter/chase)

                            if fantasma.movimiento_optimizado(target, mapa, ignorar_puerta) != None:
                                direccion, futura_posicion = fantasma.movimiento_optimizado(target, mapa, ignorar_puerta)
                                fantasma.mover_fantasma(futura_posicion[0], futura_posicion[1], direccion, mapa)

                # si debe permanecer en la casa
                else:
                    fantasma.movimiento_aleatorio_asustado(mapa)

                ultimo_mov_fant_ms[indice] = ahora_ms

        # COLISIONES CON FANTASMAS 
        for indice, activo in enumerate(fantasmas_activos):

            if activo:

                fantasma = fantasmas_elegidos[indice]
                if fantasma.misma_posicion(pacman):
                    
                    if fantasma.estado_asustado:
                        pacman.comer_fantasmas(fantasma)

                    else:
                        pacman.iniciar_muerte()
                        break  # termina el ciclo for


# GAME OVER CHEQUEO 

    # DIBUJO

    ventana.fill(NEGRO)
    dibujar_mapa(ventana, mapa)

    for f in fantasmas_elegidos:
        ventana.blit (f.imagen, f.rect)
        
    ventana.blit(pacman.imagen, pacman.rect) 
    dibujar_display(ventana, pacman, high_score, nivel, fuente_display, icono_vida, ancho_ventana, 
    len(mapa.mapa) * TAMANO_BLOQUE, alto_display) #acá agregué al display de vidas

    pygame.display.set_caption(
        f"PACMAN | FPS: {clock.get_fps():.1f} | puntaje: {pacman.puntaje} | celda: {pacman.celda_actual()} | M = muerte"
    )
    pygame.display.flip()

pygame.quit()
