
import pygame
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

def inicializar_display(tamaño_bloque):
    """Carga fuente a utilizar para mostrar el puntaje y la imagen de la vida (corazón) y la ajusta al tamaño del mapa.
    Recibe el tamaño de cada bloque del mapa y retorna (fuente, icono adaptado)"""
    fuente = pygame.font.SysFont("freesansbold", 16) #la fuente que uso
    icono_vida = pygame.image.load(os.path.join(base_dir, "vida.png")).convert_alpha() #imagen de las vidas
    icono = pygame.transform.scale(icono_vida, (tamaño_bloque - 4, tamaño_bloque - 4))
    return fuente, icono

def dibujar_display(ventana, pacman, high_score, nivel, fuente, icono_vida, ancho, alto_mapa, alto_display):
    """Dibuja el panel con la info del juego. Muestra el puntaje actual y el mejor puntaje (actualizado), y los corazones
    correspondientes a las vidas restantes.
    Recibe: Ventana (donde se dibuja el display), Pacman (personaje, debe contener atributos puntaje y vidas), High_score (mejor puntaje),
    Fuente: fuente, Icono_vida (imagen), Ancho: ancho de ventana, Alto: altura del mapa, Alto_display: altura del panel
    """
    pygame.draw.rect(ventana, (0, 0, 0), (0, alto_mapa, ancho, alto_display))
    score = fuente.render(f"SCORE: {pacman.puntaje}", True, (224,33,138))
    ventana.blit(score,score.get_rect(center=(ancho//2, alto_mapa + alto_display//4)))

    best = fuente.render(f"BEST: {high_score}", True, (237,129,188))
    ventana.blit(best,best.get_rect(center=(ancho//2, alto_mapa + alto_display * 3//4)))

    nivel = fuente.render(f"NIVEL: {nivel}", True, (193,84,193))
    ventana.blit(nivel,nivel.get_rect(center=(ancho//4,alto_mapa + alto_display * 3//4)))

    for i in range(pacman.vidas):
        x = ancho - (pacman.vidas - i) * 20
        y = alto_mapa + alto_display // 2
        ventana.blit(icono_vida, (x, y))
