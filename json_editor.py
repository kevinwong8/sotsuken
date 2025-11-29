
import pygame
import spritesheet

pygame.init()

# Window
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Sprite Test')

# Load the 3-frame horizontal sprite sheet we created
sprite_sheet_image = pygame.image.load('assets/pictures/yakitori.png').convert_alpha()
sprite_sheet = spritesheet.SpriteSheet(sprite_sheet_image)

# Colors
BG = (50, 50, 50)

# Animation setup
animation_list = []
animation_steps = 3  # we have 3 frames
frame_w, frame_h = 1024, 1024  # each frame size in the generated sheet
scale = 0.5  # scale down to fit window; adjust as needed
animation_cooldown = 200  # milliseconds per frame
last_update = pygame.time.get_ticks()
frame = 0

# Build frames (index 0..2)
for i in range(animation_steps):
    # get_image(index, frame_w, frame_h, scale, colorkey)
    # if your get_image expects 'black' string, use it; otherwise use a tuple like (0,0,0)
    animation_list.append(sprite_sheet.get_image(i, frame_w, frame_h, scale, 'black'))

run = True
while run:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Update
    current_time = pygame.time.get_ticks()
    if (current_time - last_update) >= animation_cooldown:
        frame = (frame + 1) % len(animation_list)
        last_update = current_time

    # Draw
    screen.fill(BG)
    # Center it a bit
    img = animation_list[frame]
    img_rect = img.get_rect()
    screen.blit(img, ((SCREEN_WIDTH - img_rect.width) // 2, (SCREEN_HEIGHT - img_rect.height) // 2))

    pygame.display.update()

pygame.quit()
