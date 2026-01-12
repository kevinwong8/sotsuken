import pygame
import sys

# ===== Initialize =====
pygame.init()

WIDTH, HEIGHT = 1280, 720
BOTTOM_BAR_HEIGHT = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kingyo Animation Example")
clock = pygame.time.Clock()

# ===== Load Images =====
kingyo_imgs = [
    pygame.image.load("assets/pictures/kingyo.png").convert_alpha(),
    pygame.image.load("assets/pictures/kingyo2.png").convert_alpha()
]

# Optional: scale images (recommended)
KINGYO_SIZE = (256, 256)
kingyo_imgs = [
    pygame.transform.scale(img, KINGYO_SIZE) for img in kingyo_imgs
]

# ===== Animation State =====
kingyo_index = 0
KINGYO_SWAP_TIME = 1000  # milliseconds (1 second)
last_kingyo_switch = pygame.time.get_ticks()

# ===== Main Loop =====
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ===== Update Animation =====
    current_time = pygame.time.get_ticks()
    if current_time - last_kingyo_switch >= KINGYO_SWAP_TIME:
        kingyo_index = (kingyo_index + 1) % len(kingyo_imgs)
        last_kingyo_switch = current_time

    # ===== Draw =====
    screen.fill((30, 30, 30))

    # Bottom UI bar (visual reference)
    pygame.draw.rect(
        screen,
        (50, 50, 50),
        (0, HEIGHT - BOTTOM_BAR_HEIGHT, WIDTH, BOTTOM_BAR_HEIGHT)
    )

    # Draw kingyo ABOVE bottom bar
    kingyo_pic = kingyo_imgs[kingyo_index]

    kingyo_x = 300
    kingyo_y = HEIGHT - BOTTOM_BAR_HEIGHT - kingyo_pic.get_height() + 25

    screen.blit(kingyo_pic, (kingyo_x, kingyo_y))

    pygame.display.flip()

# ===== Quit =====
pygame.quit()
sys.exit()
