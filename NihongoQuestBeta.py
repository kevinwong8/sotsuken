# Typing Racer in Python
# ------------------------------------------------------------
# Features:
# - Multiple JLPT levels (N5–N1)
# - Pause / Resume system
# - Level-up every 10 correct words
# - Tracks high score & missed words
# - Uses Pygame for all rendering
# ------------------------------------------------------------

import pygame, random, copy, json, time
pygame.init()

# ============================================================
#  Utility Functions
# ============================================================

def load_selected_words(level_choices):
    """Load vocabulary lists based on selected JLPT levels."""
    loaded_words = []
    level_map = {0: "N5", 1: "N4", 2: "N3", 3: "N2", 4: "N1"}

    for i, chosen in enumerate(level_choices):
        if chosen:
            filename = f"assets/data/{level_map[i]}.json"
            try:
                with open(filename, encoding="utf-8") as f:
                    data = json.load(f)
                    for w in data:
                        w["level"] = level_map[i][-1]  # add level metadata (e.g. "5" for N5)
                    loaded_words.extend(data)
            except FileNotFoundError:
                print(f"⚠️ Missing file: {filename}")

    return loaded_words

# ============================================================
#  Pygame Initialization
# ============================================================

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

# Maintain 5:3 ratio
ASPECT_RATIO = 5 / 3
max_width, max_height = int(screen_width * 0.8), int(screen_height * 0.8)

if max_width / max_height > ASPECT_RATIO:
    WIDTH, HEIGHT = int(max_height * ASPECT_RATIO), max_height
else:
    WIDTH, HEIGHT = max_width, int(max_width / ASPECT_RATIO)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Typing Racer in Python')
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
FPS = 60

# ============================================================
#  Load Fonts & Sounds
# ============================================================

header_font = pygame.font.Font('assets/fonts/RocknRollOne-Regular.ttf', 50)
pause_font = pygame.font.Font('assets/fonts/notosans.ttf', 38)
banner_font = pygame.font.Font('assets/fonts/notosans.ttf', 28)
font = pygame.font.Font('assets/fonts/RocknRollOne-Regular.ttf', 48)
romaji_font = pygame.font.Font('assets/fonts/Square.ttf', 25)
notosans = pygame.font.Font('assets/fonts/notosans.ttf', 25)

pygame.mixer.init()
pygame.mixer.music.load('assets/sound/natsunoyoru.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

click = pygame.mixer.Sound('assets/sound/click.mp3')
success = pygame.mixer.Sound('assets/sound/success.mp3')
wrong = pygame.mixer.Sound('assets/sound/Instrument Strum.mp3')

click.set_volume(0.3)
success.set_volume(0.6)
wrong.set_volume(0.3)

# ============================================================
#  Global Variables
# ============================================================

level = 1
active_string = ""
score = 0
lives = 5
paused = True
submit = ''
word_objects = []
new_level = True
letters = list('abcdefghijklmnopqrstuvwxyz')
level_up_time = 0
show_levelup = False
missed_words = []
WORDS_PER_LEVEL = 10
words_typed = 0
max_active_words = 1
spawn_interval = 3
last_spawn_time = time.time()

# Default Level Choices (N5 active)
choices = [True, False, False, False, False]
words = load_selected_words(choices)
print(f"{len(words)} words loaded (default N5).")

# Load high score
with open('high.txt', 'r') as f:
    high_score = int(f.readline().strip())

# ============================================================
#  Classes
# ============================================================

class Word:
    """Represents a falling Japanese word."""
    def __init__(self, kanji, speed, y_pos, x_pos, kana, romaji, meaning, nlevel):
        self.kanji = kanji
        self.kana = kana
        self.romaji = romaji
        self.meaning = meaning
        self.nlevel = nlevel
        self.speed = speed
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.spawn_time = time.time()

    def draw(self):
        """Render the word and highlight correct partial input."""
        elapsed = time.time() - self.spawn_time
        slide_distance = max(0, 100 - elapsed * 200)
        x_draw = self.x_pos + slide_distance

        color = 'black'
        screen.blit(font.render(self.kanji, True, color), (x_draw, self.y_pos))

        # Highlight typed romaji
        act_len = len(active_string)
        if active_string == self.romaji[:act_len] and active_string:
            screen.blit(romaji_font.render(active_string, True, 'maroon'), (x_draw, self.y_pos + 60))
            screen.blit(font.render(self.kanji, True, 'green'), (x_draw, self.y_pos))

    def update(self):
        """Move word leftward each frame."""
        self.x_pos -= self.speed


class Button:
    """Circular button component."""
    def __init__(self, x, y, text, clicked, surf, radius=35):
        self.x = x
        self.y = y
        self.text = text
        self.clicked = clicked
        self.surf = surf
        self.radius = radius

    def draw(self):
        """Draw button and handle click states."""
        circle = pygame.draw.circle(self.surf, (45, 89, 135), (self.x, self.y), self.radius)
        mouse_pos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        if circle.collidepoint(mouse_pos):
            color = (190, 35, 35) if pressed[0] else (190, 89, 135)
            pygame.draw.circle(self.surf, color, (self.x, self.y), self.radius)
            if pressed[0]:
                self.clicked = True

        pygame.draw.circle(self.surf, 'white', (self.x, self.y), self.radius, 3)
        self.surf.blit(pause_font.render(self.text, True, 'white'), (self.x - 15, self.y - 25))

# ============================================================
#  Drawing Functions
# ============================================================

def draw_screen():
    """Draws main UI (bottom bar, score, lives, etc.)."""
    pygame.draw.rect(screen, (32, 42, 68), [0, HEIGHT - 100, WIDTH, 100])
    pygame.draw.rect(screen, 'white', [0, 0, WIDTH, HEIGHT], 5)

    # Lines and dividers
    pygame.draw.line(screen, 'white', (250, HEIGHT - 100), (250, HEIGHT))
    pygame.draw.line(screen, 'white', (700, HEIGHT - 100), (700, HEIGHT))
    pygame.draw.line(screen, 'white', (0, HEIGHT - 100), (WIDTH, HEIGHT - 100))
    pygame.draw.rect(screen, 'black', [0, 0, WIDTH, HEIGHT], 2)

    # Status Text
    screen.blit(header_font.render(f'レベル: {level}', True, 'white'), (10, HEIGHT - 85))
    screen.blit(header_font.render(f'"{active_string}"', True, 'white'), (270, HEIGHT - 75))

    # Pause button
    pause_btn = Button(748, HEIGHT - 52, 'II', False, screen)
    pause_btn.draw()

    screen.blit(banner_font.render(f'点数: {score}', True, 'black'), (250, 10))
    screen.blit(banner_font.render(f'最高点: {high_score}', True, 'black'), (550, 10))
    screen.blit(banner_font.render(f'命: {lives}', True, 'black'), (10, 10))

    return pause_btn.clicked


def draw_pause():
    """Draws a Matsuri-themed pause menu, centered and flexible."""
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Semi-transparent night overlay
    pygame.draw.rect(surface, (0, 0, 0, 160), (0, 0, WIDTH, HEIGHT))

    # Dynamic dimensions for menu box
    box_w, box_h = WIDTH * 0.6, HEIGHT * 0.55
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2

    # Wooden-style menu board
    pygame.draw.rect(surface, (80, 40, 20, 230), [box_x, box_y, box_w, box_h], border_radius=20)
    pygame.draw.rect(surface, (200, 50, 50), [box_x, box_y, box_w, box_h], 8, border_radius=20)

    # Title
    title = header_font.render("⛩ メニュー ⛩", True, (255, 220, 180))
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, box_y + 30))

    # Buttons (lantern-style)
    resume_btn = Button(WIDTH // 2 - 150, box_y + box_h * 0.4, '▶', False, surface)
    quit_btn   = Button(WIDTH // 2 + 150, box_y + box_h * 0.4, '✖', False, surface)
    resume_btn.draw()
    quit_btn.draw()

    # Labels
    play_label = notosans.render("再開 (Resume)", True, (255, 230, 200))
    quit_label = notosans.render("やめる (Quit)", True, (255, 230, 200))
    surface.blit(play_label, (WIDTH // 2 - 220, box_y + box_h * 0.55))
    surface.blit(quit_label, (WIDTH // 2 + 70, box_y + box_h * 0.55))

    # Level selector section
    surface.blit(header_font.render("レベルを選んでください:", True, (255, 220, 180)),
                 (WIDTH // 2 - 200, box_y + box_h * 0.68))

    temp_choices = copy.deepcopy(choices)
    spacing = 100
    base_x = WIDTH // 2 - ((len(choices) - 1) * spacing) // 2
    for i in range(len(choices)):
        btn_x = base_x + i * spacing
        btn = Button(btn_x, int(box_y + box_h * 0.85), f"N{5 - i}", False, surface, 45)
        btn.draw()
        if btn.clicked:
            temp_choices[i] = not temp_choices[i]
        if choices[i]:
            pygame.draw.circle(surface, (255, 100, 100), (btn_x, int(box_y + box_h * 0.85)), 45, 5)

    screen.blit(surface, (0, 0))
    return resume_btn.clicked, temp_choices, quit_btn.clicked



def draw_result():
    """Draws Matsuri-themed result (game-over) screen, centered and flexible."""
    global missed_words, score, high_score

    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0, 0, 0, 180), [0, 0, WIDTH, HEIGHT])

    # Centered box
    box_w, box_h = WIDTH * 0.7, HEIGHT * 0.7
    box_x, box_y = (WIDTH - box_w) // 2, (HEIGHT - box_h) // 2

    # Wooden-style background
    pygame.draw.rect(surface, (90, 45, 25, 240), [box_x, box_y, box_w, box_h], border_radius=25)
    pygame.draw.rect(surface, (255, 80, 80), [box_x, box_y, box_w, box_h], 8, border_radius=25)

    # Header
    title = header_font.render("🎆 ゲームオーバー 🎆", True, (255, 220, 180))
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, box_y + 40))

    # Scores
    surface.blit(banner_font.render(f"スコア: {score}", True, (255, 240, 210)),
                 (WIDTH // 2 - 80, box_y + 120))
    surface.blit(banner_font.render(f"最高点: {high_score}", True, (255, 240, 210)),
                 (WIDTH // 2 - 100, box_y + 160))

    # Missed words section
    y = box_y + 220
    surface.blit(banner_font.render("打てなかった言葉:", True, (255, 220, 200)), (box_x + 60, y))
    y += 40
    for i, word in enumerate(missed_words[-6:]):
        entry = f"{i+1}. {word['kanji']} ({word['reading']}) - {word['meaning']}"
        surface.blit(notosans.render(entry, True, (255, 230, 230)), (box_x + 70, y))
        y += 35

    # Buttons
    play_btn = Button(WIDTH // 2 - 120, int(box_y + box_h - 80), '▶', False, surface)
    quit_btn = Button(WIDTH // 2 + 120, int(box_y + box_h - 80), '✖', False, surface)
    play_btn.draw()
    quit_btn.draw()

    surface.blit(notosans.render("もう一度 (Play Again)", True, (255, 240, 210)),
                 (WIDTH // 2 - 250, int(box_y + box_h - 150)))
    surface.blit(notosans.render("やめる (Quit)", True, (255, 240, 210)),
                 (WIDTH // 2 + 40, int(box_y + box_h - 150)))

    screen.blit(surface, (0, 0))
    return play_btn.clicked, quit_btn.clicked


# ============================================================
#  Game Logic Functions
# ============================================================

def check_answer(current_score):
    """Check typed word, update score and handle level-ups."""
    global words_typed, level, new_level, show_levelup, level_up_time, max_active_words, spawn_interval

    for wrd in word_objects[:]:
        if wrd.romaji == submit:
            points = wrd.speed * (6 - int(wrd.nlevel)) * 10 * (len(wrd.romaji) / 4)
            current_score += int(points)
            word_objects.remove(wrd)
            success.play()
            words_typed += 1

            # Level-up after every 10 correct words
            if words_typed % WORDS_PER_LEVEL == 0 and level < 10:
                level += 1
                new_level = True
                show_levelup = True
                level_up_time = time.time()
                spawn_interval = max(0.8, spawn_interval - 0.2)
                if max_active_words < 5:
                    max_active_words += 1
    return current_score


def generate_word():
    """Randomly select a word from the loaded list and return a Word object."""
    global words

    if not words:
        with open("assets/data/N5.json", encoding="utf-8") as f:
            words = json.load(f)
            print("⚠️ Defaulted to N5.json")

    data = random.choice(words)
    y = random.randint(80, HEIGHT - 200)
    speed = random.uniform(2.0 + (level - 1) * 0.4 - 0.3, 2.0 + (level - 1) * 0.4 + 0.5)
    x = WIDTH + random.randint(0, 100)
    return Word(data["kanji"], speed, y, x, data["reading"], data["romaji"], data["meaning"], data.get("level", "5"))


def check_high_score():
    """Save new high score if beaten."""
    global high_score
    if score > high_score:
        high_score = score
        with open('high.txt', 'w') as f:
            f.write(str(high_score))

# ============================================================
#  Main Game Loop
# ============================================================

run = True
while run:
    screen.fill('gray')
    timer.tick(FPS)

    pause_btn = draw_screen()

    # ----- Pause Menu -----
    if paused:
        resume, new_choices, quit_game = draw_pause()
        if resume:
            paused = False
            start_time = time.time()
        if quit_game:
            check_high_score()
            run = False

    # ----- Word Spawning -----
    if not paused and len(word_objects) < max_active_words:
        if time.time() - last_spawn_time > spawn_interval:
            word_objects.append(generate_word())
            last_spawn_time = time.time()

    # ----- Word Updates -----
    for w in word_objects[:]:
        w.draw()
        if not paused:
            w.update()
        if w.x_pos < -200:
            word_objects.remove(w)
            missed_words.append({"kanji": w.kanji, "reading": w.kana, "meaning": w.meaning})
            lives -= 1

    # ----- Input Checking -----
    if submit:
        old_score = score
        score = check_answer(score)
        submit = ''
        if old_score == score:
            wrong.play()

    # ----- Events -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            check_high_score()
            run = False

        if event.type == pygame.KEYDOWN:
            if not paused:
                if event.unicode.lower() in letters:
                    active_string += event.unicode.lower()
                    click.play()
                elif event.key == pygame.K_BACKSPACE:
                    active_string = active_string[:-1]
                    click.play()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    submit = active_string
                    active_string = ''
            if event.key == pygame.K_ESCAPE:
                paused = not paused

        if event.type == pygame.MOUSEBUTTONUP and paused and event.button == 1:
            choices = new_choices
            words = load_selected_words(choices)
            print(f"{len(words)} words loaded from selected levels.")

    if pause_btn:
        paused = True

    # ----- Game Over -----
    if lives <= 0:
        check_high_score()
        game_over = True
        while game_over:
            screen.fill('gray')
            play_again, quit_now = draw_result()
            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    run, game_over = False, False
                elif e.type == pygame.MOUSEBUTTONUP:
                    if play_again:
                        missed_words.clear()
                        level, lives, score = 1, 5, 0
                        word_objects.clear()
                        paused, game_over = True, False
                    elif quit_now:
                        run, game_over = False, False

    # ----- Level-Up Message -----
    if show_levelup:
        elapsed = time.time() - level_up_time
        if elapsed < 2:
            alpha = max(0, 255 - int((elapsed / 2) * 255))
            msg = header_font.render('レベルアップ！', True, (255, 255, 255))
            msg.set_alpha(alpha)
            screen.blit(msg, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
        else:
            show_levelup = False

    pygame.display.flip()

pygame.quit()
