#list to do:

import pygame, random, copy, string, nltk, json, time
pygame.init()

def load_selected_words(level_choices):
    loaded_words = []
    level_map = {
        0: "N5",
        1: "N4",
        2: "N3",
        3: "N2",
        4: "N1"
    }

    for i, chosen in enumerate(level_choices):
        if chosen:
            filename = f"assets/data/{level_map[i]}.json"
            try:
                with open(filename, encoding="utf-8") as f:
                    level_words = json.load(f)
                    for w in level_words:
                        w["level"] = level_map[i][-1]  # "5" for N5, etc.
                    loaded_words.extend(level_words)
            except FileNotFoundError:
                print(f"⚠️ File not found: {filename}")

    return loaded_words

#game initalization things
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH,HEIGHT])
pygame.display.set_caption('Typing Racer in Python')
surface = pygame.Surface((WIDTH, HEIGHT),pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60


#load  in assets like fonts and sound effects and music
header_font = pygame.font.Font('assets/fonts/Bold.ttf', 50)
pause_font= pygame.font.Font('assets/fonts/Bold.ttf', 38)
banner_font = pygame.font.Font('assets/fonts/Bold.ttf', 28)
font= pygame.font.Font('assets/fonts/Bold.ttf', 48)
kusukusuame = pygame.font.Font('assets/fonts/kusukusuame.otf', 25)
romaji_font= pygame.font.Font('assets/fonts/Square.ttf', 25)
notosans = pygame.font.Font('assets/fonts/notosans.ttf', 25)
#sound effect
pygame.mixer.init()
pygame.mixer.music.load('assets/sound/natsunoyoru.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
click = pygame.mixer.Sound('assets/sound/click.mp3')
whoosh = pygame.mixer.Sound('assets/sound/Swoosh.mp3')
wrong = pygame.mixer.Sound('assets/sound/Instrument Strum.mp3')

click.set_volume(0.3)
whoosh.set_volume(0.3)
wrong.set_volume(0.3)

#game variables
level = 1
active_string = ""
score = 0
lives = 5
paused = True
submit = ''
word_objects = []
new_level = True
letters = ['a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'あ']
level_up_time = 0
show_levelup = False
missed_words = []
WORDS_PER_LEVEL = 10      # number of correct words needed to level up
words_typed = 0           # counter for correct words typed
max_active_words = 1      # how many words can appear at once
spawn_interval = 3       # seconds between new words
last_spawn_time = time.time()

# N5-N1 Level
choices = [False, True, False, False, False]

#highscore read in from text file
file = open('high.txt', 'r')
read = file.readlines()
high_score = int(read[0])
file.close()

class Word:
    def __init__(self, kanji, speed, y_pos, x_pos, kana, romaji, meaning, nlevel):
        self.kanji = kanji
        self.speed = speed
        self.y_pos = y_pos
        self.x_pos = x_pos
        self.kana = kana
        self.romaji = romaji
        self.meaning = meaning
        self.nlevel = nlevel
        self.spawn_time = time.time()  # for animation



    def draw(self):
        elapsed = time.time() - self.spawn_time
        slide_distance = max(0, 100 - elapsed * 200)  # slide 100px from right
        x_draw = self.x_pos + slide_distance
        color = 'black'
        screen.blit(font.render(self.kanji, True, color), (self.x_pos, self.y_pos))
        act_len = len(active_string)
        if active_string == self.romaji[:act_len] and active_string != '':
            screen.blit(romaji_font.render(active_string, True, 'maroon'), (self.x_pos, self.y_pos+60))
            screen.blit(font.render(self.kanji, True, 'green'), (self.x_pos, self.y_pos))

    def update(self):
        self.x_pos -= self.speed



class Button:
    def __init__(self, x_pos, y_pos, text, clicked, surf, radius=35):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.clicked = clicked
        self.surf = surf
        self.radius = radius
    
    def draw(self):
        cir = pygame.draw.circle(self.surf, (45,89,135), (self.x_pos, self.y_pos), self.radius)
        if cir.collidepoint(pygame.mouse.get_pos()):
            butts = pygame.mouse.get_pressed()
            if butts[0]:
                pygame.draw.circle(self.surf, (190,35,35), (self.x_pos, self.y_pos), self.radius)
                self.clicked = True
            else:
                pygame.draw.circle(self.surf, (190,89,135), (self.x_pos, self.y_pos), self.radius)

        pygame.draw.circle(self.surf, 'white', (self.x_pos, self.y_pos), self.radius, 3)
        self.surf.blit(pause_font.render(self.text, True, 'white'), (self.x_pos-15, self.y_pos-25))

def draw_screen():
    #screen outlines for background shapes and title bar areas

    pygame.draw.rect(screen, (32,42,68), [0, HEIGHT-100, WIDTH, 100], 0)
    pygame.draw.rect(screen,'white', [0,0,WIDTH, HEIGHT],5)
    pygame.draw.line(screen,'white', (250, HEIGHT-100), (250,HEIGHT),2)
    pygame.draw.line(screen,'white', (700, HEIGHT-100), (700,HEIGHT),2)
    pygame.draw.line(screen,'white', (0, HEIGHT-100), (WIDTH,HEIGHT-100),2)
    pygame.draw.rect(screen,'black', [0,0,WIDTH, HEIGHT],2)

    #text for showing the current level, player's current input, high score, schore, lives and pause
    screen.blit(header_font.render(f'レベル: {level}', True, 'white'), (10, HEIGHT-85))
    screen.blit(header_font.render(f'"{active_string}"', True, 'white'), (270, HEIGHT-75))
    #pause button
    pause_btn = Button(748, HEIGHT-52, 'II', False, screen)
    pause_btn.draw()
    screen.blit(banner_font.render(f'点数: {score}', True, 'black'), (250, 10))
    screen.blit(banner_font.render(f'最高点: {high_score}', True, 'black'), (550, 10))
    screen.blit(banner_font.render(f'命: {lives}', True, 'black'), (10, 10))
    return pause_btn.clicked

def draw_pause():
    choice_commits = copy.deepcopy(choices)
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0,0,0,100), [100,100,600,350],0,5)
    pygame.draw.rect(surface, (0,0,0,200), [100,100,600,350],5,5)

    #define buttons for pause menu
    resume_btn = Button(160,210, '>', False, surface)
    resume_btn.draw()
    quit_btn = Button(410,210, 'X', False, surface)
    quit_btn.draw()
    #define text for pause menu
    surface.blit(header_font.render('メニュー', True, 'white'), (110,110))
    surface.blit(header_font.render('PLAY!', True, 'white'), (210,175))
    surface.blit(header_font.render('QUIT', True, 'white'), (450,175))
    surface.blit(header_font.render('レベルを選んでください ', True, 'white'), (110,250))

    #define buttons for letter length selection
    for i in range(len(choices)):
        btn = Button(190+ (i*100),380, "N"+ str(5-i), False, surface,45)
        btn.draw()
        if btn.clicked:
            if choice_commits[i]:
                choice_commits[i] = False
            else:
                choice_commits[i] = True
        if choices[i] :
            pygame.draw.circle(surface, 'green',(190+ (i*100),380),45,5 )
    screen.blit(surface, (0,0))
    return resume_btn.clicked, choice_commits, quit_btn.clicked

def draw_result():
    global missed_words, score, high_score

    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0, 0, 0, 180), [100, 80, 800, 600], 0, 20)
    pygame.draw.rect(surface, (255, 255, 255), [100, 80, 800, 600], 5, 20)

    # Titles
    title = header_font.render("ゲームオーバー", True, 'white')
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    score_text = banner_font.render(f"スコア: {score}", True, 'white')
    high_text = banner_font.render(f"最高点: {high_score}", True, 'white')
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 170))
    surface.blit(high_text, (WIDTH//2 - high_text.get_width()//2, 210))

    # Missed words section
    surface.blit(banner_font.render("打てなかった言葉:", True, 'white'), (150, 260))
    y = 300
    for i, word in enumerate(missed_words[-6:]):  # show last 6 missed words
        entry = f"{i+1}. {word['kanji']} ({word['reading']}) - {word['meaning']}"
        surface.blit(notosans.render(entry, True, 'white'), (160, y))
        y += 40

    # Buttons
    play_btn = Button(WIDTH//2 - 100, 620, '>', False, surface)
    quit_btn = Button(WIDTH//2 + 100, 620, 'X', False, surface)
    play_btn.draw()
    quit_btn.draw()

    # Labels
    surface.blit(notosans.render("PLAY AGAIN", True, 'white'), (WIDTH//2 - 160, 540))
    surface.blit(notosans.render("QUIT", True, 'white'), (WIDTH//2 + 50, 540))

    screen.blit(surface, (0, 0))
    return play_btn.clicked, quit_btn.clicked

def check_answer(scor):
    global words_typed, level, new_level, show_levelup, level_up_time, max_active_words, spawn_interval

    for wrd in word_objects:
        if wrd.romaji == submit:
            points = wrd.speed * (6 - int(wrd.nlevel)) * 10 * (len(wrd.romaji) / 4)
            scor += int(points)
            word_objects.remove(wrd)
            whoosh.play()
            words_typed += 1

            # Level up only every 10 correct words
            if words_typed % WORDS_PER_LEVEL == 0 and level < 10:
                level += 1
                new_level = True
                level_up_time = time.time()
                show_levelup = True
                spawn_interval = max(0.8, spawn_interval - 0.2)
                if max_active_words < 5:
                    max_active_words += 1
    return scor



def generate_word():
    if not words:
        print("⚠️ No words loaded, defaulting to N5.json")
        with open("assets/data/N5.json", encoding="utf-8") as f:
            fallback = json.load(f)
        word_data = random.choice(fallback)
    else:
        word_data = random.choice(words)

    kanji = word_data["kanji"]
    kana = word_data["reading"]
    romaji = word_data["romaji"]
    meaning = word_data["meaning"]
    nlevel = word_data.get("level", "5")

    y_pos = random.randint(80, HEIGHT - 200)
    base_speed = 2.0 + (level - 1) * 0.4
    speed = random.uniform(base_speed - 0.3, base_speed + 0.5)
    x_pos = WIDTH + random.randint(0, 100)

    return Word(kanji, speed, y_pos, x_pos, kana, romaji, meaning, nlevel)




def check_high_score():
    global high_score
    if score>high_score:
        high_score= score
        file = open('high.txt', 'w')
        file.write(str(int(high_score)))
        file.close()

start_time = time.time()
interval = 30  # 1 minute per hardness increase
run = True
while run:
    screen.fill('gray')
    timer.tick(fps)



    #draw background screen stuff and statuses and get pause button status
    pause_btn = draw_screen()
    if paused:
        resume_butt, changes, quit_butt = draw_pause()
        if resume_butt:
            paused = False
            start_time = time.time()  # reset timer when resuming
        if quit_butt:
            check_high_score()
            run = False

    # spawn new word periodically if under max_active_words
    if not paused and len(word_objects) < max_active_words:
        if time.time() - last_spawn_time > spawn_interval:
            word_objects.append(generate_word())
            last_spawn_time = time.time()

    # update and draw words
    for w in word_objects:
        w.draw()
        if not paused:
            w.update()
        if w.x_pos < -200:
            word_objects.remove(w)
            missed_words.append({
                "kanji": w.kanji,
                "reading": w.kana,
                "meaning": w.meaning
            })
            lives -= 1

    
    
    if len(word_objects)<=0 and not paused:
        
        new_level = True
    
    if submit != '':
        init = score
        score = check_answer(score)
        submit = ''
        if init == score:
            wrong.play()
            pass 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            check_high_score()
            run = False
        
        if event.type == pygame.KEYDOWN:
            if not paused:
                if event.unicode.lower() in letters:
                    active_string += event.unicode.lower()
                    click.play()
                if event.key == pygame.K_BACKSPACE and len(active_string)> 0:
                    active_string= active_string[:-1]
                    click.play()
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    submit = active_string
                    active_string = ''
            
            if event.key == pygame.K_ESCAPE:
                if paused:
                    paused = False
                else:
                    paused = True


        if event.type == pygame.MOUSEBUTTONUP and paused:
            if event.button == 1:
                choices = changes
                words = load_selected_words(choices)
                print(f"{len(words)} words loaded from selected levels.")
    if pause_btn:
        paused = True

    if lives <= 0:
        check_high_score()
        game_over = True
        while game_over:
            screen.fill('gray')
            play_again, quit_game = draw_result()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    game_over = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if play_again:
                        missed_words.clear()
                        level = 1
                        lives = 5
                        score = 0
                        word_objects = []
                        new_level = True
                        paused = True  # go back to pause/start menu
                        game_over = False
                    if quit_game:
                        run = False
                        game_over = False


    if show_levelup:
        elapsed = time.time() - level_up_time
        if elapsed < 2:  # show for 2 seconds
            alpha = max(0, 255 - int((elapsed / 2) * 255))  # fade out
            msg_surface = header_font.render(f'レベルアップ！', True, (255, 255, 255))
            msg_surface.set_alpha(alpha)
            screen.blit(msg_surface, (WIDTH//2 - 150, HEIGHT//2 - 50))
        else:
            show_levelup = False
    pygame.display.flip()

pygame.quit()