import pygame
from pygame import gfxdraw
import random
from itertools import combinations, product
import nltk
from nltk.corpus import wordnet

# Dimensiones de la ventana
WIDTH = 800
HEIGHT = 600

# Colores
BACKGROUND_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
EDGE_COLOR = (100, 100, 100)
MIN_RADIUS = 20
MAX_RADIUS = 50
NODE_PADDING = 5
NODE_MARGIN = 10

# Función para escalar un valor dentro de un rango a otro rango
def scale_value(value, min_value, max_value, new_min_value, new_max_value):
    normalized_value = (value - min_value) / (max_value - min_value)
    scaled_value = new_min_value + (new_max_value - new_min_value) * normalized_value
    return int(scaled_value)

# Clase para representar un nodo en el mapa conceptual
class Node:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.connections = []
        self.count = 0

    def add_connection(self, other):
        self.connections.append(other)

    def increment_count(self):
        self.count += 1

    def draw(self, screen, max_count, screen_width, screen_height):
        # Escalar las coordenadas del nodo según el tamaño de la ventana
        scaled_x = scale_value(self.x, 0, WIDTH, 0, screen_width)
        scaled_y = scale_value(self.y, 0, HEIGHT, 0, screen_height)

        # Escalar el radio del círculo según el recuento de ocurrencias y el tamaño de la ventana
        min_radius = MIN_RADIUS * min(screen_width, screen_height) / max(WIDTH, HEIGHT)
        max_radius = MAX_RADIUS * min(screen_width, screen_height) / max(WIDTH, HEIGHT)
        radius = scale_value(self.count, 0, max_count, min_radius, max_radius)

        # Escalar el tamaño de la fuente según el tamaño de la ventana
        font_size = int(radius * 0.6)

        # Escalar el color del círculo según el recuento de ocurrencias
        color_value = scale_value(self.count, 0, max_count, 0, 255)
        color = (255 - color_value, color_value, 0)

        gfxdraw.filled_circle(screen, scaled_x, scaled_y, radius, color)
        gfxdraw.aacircle(screen, scaled_x, scaled_y, radius, color)

        font = pygame.font.Font(None, font_size)
        text = font.render(f"{self.text} ({self.count})", True, TEXT_COLOR)
        text_rect = text.get_rect(center=(scaled_x, scaled_y))
        screen.blit(text, text_rect)

    def draw_connections(self, screen, screen_width, screen_height):
        for other in self.connections:
            pygame.draw.line(screen, EDGE_COLOR, (scale_value(self.x, 0, WIDTH, 0, screen_width),
                                                  scale_value(self.y, 0, HEIGHT, 0, screen_height)),
                             (scale_value(other.x, 0, WIDTH, 0, screen_width),
                              scale_value(other.y, 0, HEIGHT, 0, screen_height)), 2)

# Función para generar nodos organizados en la ventana, filtrando las palabras
def generate_nodes(text):
    stopwords = ["a", "ante", "bajo", "con", "contra", "de", "desde", "en", "entre", "hacia",
                 "hasta", "para", "por", "según", "sin", "sobre", "tras", "durante", "mediante",
                 "versus", "vía", "y", "o", "u", "pero", "aunque", "si", "porque", "para", "como",
                 "que", "qué", "quien", "cómo", "cuando", "donde", "cual", "cuál", "cuanto", "cuánto",
                 "estas", "tiene", "siendo"]

    words = text.split()
    filtered_words = [word for word in words if len(word) >= 4 and word.lower() not in stopwords and not word.endswith("ando") and not word.endswith("iendo")]

    num_nodes = len(filtered_words)
    nodes = []
    max_horizontal_nodes = int((WIDTH - 2 * NODE_MARGIN) / (MAX_RADIUS * 2 + NODE_PADDING))
    max_vertical_nodes = int((HEIGHT - 2 * NODE_MARGIN) / (MAX_RADIUS * 2 + NODE_PADDING))
    num_rows = min(max_vertical_nodes, int(num_nodes / max_horizontal_nodes))
    num_columns = min(max_horizontal_nodes, num_nodes)

    x_start = NODE_MARGIN + MAX_RADIUS
    y_start = NODE_MARGIN + MAX_RADIUS

    for i in range(num_nodes):
        row = i // max_horizontal_nodes
        column = i % max_horizontal_nodes
        x = x_start + column * (MAX_RADIUS * 2 + NODE_PADDING)
        y = y_start + row * (MAX_RADIUS * 2 + NODE_PADDING)
        node_text = filtered_words[i]
        node = Node(node_text, x, y)
        nodes.append(node)
        node.increment_count()

    # Conectar nodos según su relevancia semántica
    for node1, node2 in combinations(nodes, 2):
        if node1.text != node2.text:
            synsets1 = wordnet.synsets(node1.text)
            synsets2 = wordnet.synsets(node2.text)
            if synsets1 and synsets2:
                max_similarity = max((s1.path_similarity(s2) or 0) for s1, s2 in product(synsets1, synsets2))
                if max_similarity > 0.5:
                    node1.add_connection(node2)
                    node2.add_connection(node1)

    return nodes

# Función principal
def main():
    # Descargar el recurso de WordNet si no está disponible
    nltk.download('wordnet')

    pygame.init()
    screen_width = pygame.display.Info().current_w
    screen_height = pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Mapa Conceptual")
    clock = pygame.time.Clock()

    x_offset = 0
    y_offset = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_MIDDLE:
                    y_offset += event.rel[1]  # Desplazarse hacia arriba y hacia abajo con el botón central del mouse

        screen.fill(BACKGROUND_COLOR)

        # Generar nodos y dibujarlos en la pantalla con los desplazamientos
        nodes = generate_nodes(input("Ingrese el texto: "))
        max_count = max(node.count for node in nodes)

        # Calcular los límites de los nodos
        min_x = min(node.x for node in nodes)
        max_x = max(node.x for node in nodes)
        min_y = min(node.y for node in nodes)
        max_y = max(node.y for node in nodes)

        # Ajustar los desplazamientos según los límites de los nodos y las dimensiones de la pantalla
        x_offset = max(-min_x + NODE_MARGIN + MAX_RADIUS, min(WIDTH - max_x - MAX_RADIUS - NODE_MARGIN, x_offset))
        y_offset = max(-min_y + NODE_MARGIN + MAX_RADIUS, min(HEIGHT - max_y - MAX_RADIUS - NODE_MARGIN, y_offset))

        for node in nodes:
            node.x += x_offset
            node.y += y_offset
            node.draw(screen, max_count, screen_width, screen_height)
            node.draw_connections(screen, screen_width, screen_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
