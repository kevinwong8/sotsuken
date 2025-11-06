#list to do:
#timer dan tingkat kesusahan level
#review word yang ngga berhasil diketik
#ui dan character
import pygame, random, copy, string, nltk, json, time
pygame.init()

with open("assets/data/words.json", encoding="utf-8") as f:
    words = json.load(f)

print(words[0]["kanji"], words[0]["reading"], words[0]["meaning"])

#game initalization things
WIDTH = 1000
HEIGHT = 800
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


    def draw(self):
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
    for wrd in word_objects:
        if wrd.romaji == submit:
            points = wrd.speed * (6-int(wrd.nlevel))* 10 * (len(wrd.romaji) / 4)
            scor += int(points)
            word_objects.remove(wrd)
            
            whoosh.play()
    return scor

def generate_level():
    word_objs = []
    vertical_spacing = (HEIGHT - 150) // level

    # convert dictionary keys to list so we can randomly pick from them
    selected_levels = [str(5 - i) for i, chosen in enumerate(choices) if chosen]
    available_words = [w for w in words if w["level"] in selected_levels]

    # if not available_words:
    #     available_words = words

    for i in range(level):
        speed = level + 10
        y_pos = random.randint(10 + (i * vertical_spacing), (i + 1) * vertical_spacing)
        x_pos = random.randint(WIDTH, WIDTH )

        # pick a random Japanese word from dictionary
        word_data = random.choice(available_words)
        kanji = word_data["kanji"]
        kana = word_data["reading"]
        romaji = word_data["romaji"]
        meaning = word_data["meaning"]
        nlevel = word_data["level"]
        
        # show the kanji as the falling text
        new_word = Word(kanji, speed, y_pos, x_pos, kana, romaji, meaning, nlevel)
        word_objs.append(new_word)

    return word_objs


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

    # ⏱ Time-based difficulty increase
    elapsed_time = time.time() - start_time
    if elapsed_time >= interval and not paused:
        level += 1
        new_level = True
        start_time = time.time()  
        level_up_time = time.time()
        show_levelup = True

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

    if new_level and not paused:
        word_objects = generate_level()
        new_level = False
    else:
        for w in word_objects:
            w.draw()
            if not paused:
                w.update()
            if w.x_pos <-200:
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