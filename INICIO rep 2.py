import pygame
import os

def pantalla_inicio(ventana, NEGRO, BLANCO, ancho, alto):
    """Pantalla que muestra 'PAC-MAN', solo cuando el jugador presione ENTER se termina la función y se avanza. 
    Finaliza si el jugador cierra la ventana. Retorna un bool"""

    pygame.mixer.music.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pacman-song.mp3'))
    pygame.mixer.music.play(-1)


    fuente_titulo = pygame.font.SysFont("freesansbold", 64, bold=True)
    fuente_sub = pygame.font.SysFont("freesansbold", 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.mixer.music.stop()
                    return True
        ventana.fill(NEGRO)
        titulo = fuente_titulo.render("PAC-MAN", True, (255,255,0))
        sub = fuente_sub.render("Presioná ENTER para continuar", True, BLANCO)
        ventana.blit(titulo,titulo.get_rect(center=(ancho//2, alto//3)))
        ventana.blit(sub, sub.get_rect(center=(ancho//2, alto//2)))
        pygame.display.flip()

def pantalla_selec_fantasmas(fantasmas_disponibles,ventana,NEGRO,BLANCO,ancho,alto):
    """Permite que jugador seleccione 4 fantasmas de una lista de 6. Los navega con las flechas arriba y abajo y los selecciona
    presionando ENTER. Con la tecla ESPACIO se confirma la selección solo cuando hay 4 fantasmas."""
    fuente = pygame.font.SysFont("freesansbold", 28)
    fuente_titulo = pygame.font.SysFont("freesansbold", 40,bold=True)
    pygame.mixer.music.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pacman-intermission.mp3'))
    pygame.mixer.music.play(-1)

    cursor = 0
    seleccion = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cursor = (cursor + 1)%len(fantasmas_disponibles)
                elif event.key == pygame.K_UP:
                    cursor = (cursor-1)%len(fantasmas_disponibles)
                elif event.key == pygame.K_RETURN:
                    fantasma = fantasmas_disponibles[cursor]
                    if fantasma in seleccion:
                        seleccion.remove(fantasma)
                    elif len(seleccion) <4:
                        seleccion.append(fantasma)
                elif event.key == pygame.K_SPACE:
                    if len(seleccion)==4:
                        return seleccion
        ventana.fill(NEGRO)

        titulo = fuente_titulo.render('Elegí 4 fantasmas', True, (255,255,0))
        ventana.blit(titulo,titulo.get_rect(center=(ancho//2,60)))
        for i, f in enumerate(fantasmas_disponibles):
            if f in seleccion:
                color = f.color
            elif i == cursor:
                color = (200,200,200)
            else:
                color = BLANCO

            prefijo = "✓ " if f in seleccion else "  "
            texto = fuente.render(f"{prefijo}{f.nombre.capitalize()}", True, color)
            ventana.blit(texto, texto.get_rect(center=(ancho//2, 150 + i * 50)))

        if len(seleccion) ==4:
            inst = fuente.render("ESPACIO para confirmar", True, (255,255,0))
        else:
            inst = fuente.render(f"Seleccionados: {len(seleccion)}/4", True, (150,150,150))
        ventana.blit(inst, inst.get_rect(center=(ancho//2, alto - 60)))

        pygame.display.flip()

def pantalla_asignar_esquinas(fantasmas_elegidos, ventana, NEGRO, BLANCO, ancho, alto):
    """Pantalla donde jugador asigna esquina scatter a cada uno de los 4 fantasmas. Navega las opciones con teclas arriba y abajo
    y las selecciona con enter"""
    ESQUINAS = {
        "Superior izquierda": (0, -3),
        "Superior derecha":   (27, -3),
        "Inferior izquierda": (0, 34),
        "Inferior derecha":   (27, 34),
    }
    nombres_esquinas = list(ESQUINAS.keys())
    
    fuente = pygame.font.SysFont("freesansbold", 26)
    fuente_titulo = pygame.font.SysFont("freesansbold", 26, bold=True)
    
    cursor_fant = 0   
    cursor_esq = 0    
    asignaciones = {} 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    cursor_esq = (cursor_esq + 1) % 4
                elif event.key == pygame.K_UP:
                    cursor_esq = (cursor_esq - 1) % 4
                elif event.key == pygame.K_RETURN:
                    nombre_esq = nombres_esquinas[cursor_esq]

                    if nombre_esq not in asignaciones.values():
                        asignaciones[fantasmas_elegidos[cursor_fant].nombre] = nombre_esq
                        cursor_fant += 1
                        cursor_esq = 0
                        if cursor_fant == 4:
                            for f in fantasmas_elegidos:
                                f.esquina_scatter = ESQUINAS[asignaciones[f.nombre]]
                            pygame.mixer.music.stop()
                            return fantasmas_elegidos

        ventana.fill(NEGRO)

        titulo = fuente_titulo.render("Asigná una esquina a cada fantasma", True, (255, 255, 0))
        ventana.blit(titulo, titulo.get_rect(center=(ancho//2, 50)))

        f_actual = fantasmas_elegidos[cursor_fant]
        texto_fant = fuente.render(f"Fantasma: {f_actual.nombre.capitalize()}", True, f_actual.color)
        ventana.blit(texto_fant, texto_fant.get_rect(center=(ancho//2, 120)))

        esquinas_usadas = list(asignaciones.values())
        for i, nombre_esq in enumerate(nombres_esquinas):
            if nombre_esq in esquinas_usadas:
                color = (80, 80, 80) 
            elif i == cursor_esq:
                color = (255, 255, 0) 
            else:
                color = BLANCO
            texto_esq = fuente.render(nombre_esq, True, color)
            ventana.blit(texto_esq, texto_esq.get_rect(center=(ancho//2, 200 + i * 55)))

        for j, f in enumerate(fantasmas_elegidos[:cursor_fant]):
            resumen = fuente.render(f"✓ {f.nombre.capitalize()} → {asignaciones[f.nombre]}", True, f.color)
            ventana.blit(resumen, (30, 420 + j * 35))

        pygame.display.flip()