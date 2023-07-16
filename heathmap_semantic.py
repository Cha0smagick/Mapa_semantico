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
NODE_COLOR = (200, 200, 200)
EDGE_COLOR = (100, 100, 100)
HIGHLIGHT_COLOR = (255, 0, 0)

# Clase para representar un nodo en el mapa conceptual
class Node:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.connections = []

    def add_connection(self, other):
        self.connections.append(other)

    def draw(self, screen):
        gfxdraw.filled_circle(screen, self.x, self.y, 50, NODE_COLOR)
        gfxdraw.aacircle(screen, self.x, self.y, 50, NODE_COLOR)
        font = pygame.font.Font(None, 20)
        text = font.render(self.text, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

    def draw_connections(self, screen):
        for other in self.connections:
            pygame.draw.line(screen, EDGE_COLOR, (self.x, self.y), (other.x, other.y), 2)

# Función para generar nodos aleatoriamente en la ventana, filtrando las palabras
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
    for i in range(num_nodes):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        node = Node(filtered_words[i], x, y)
        nodes.append(node)

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
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mapa Conceptual")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)

        # Generar nodos y dibujarlos en la pantalla
        nodes = generate_nodes(input("Ingrese el texto: "))
        for node in nodes:
            node.draw(screen)
            node.draw_connections(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
