import pygame, random, copy, string, nltk
pygame.init()

#nltk
from nltk.corpus import words
nltk.download('words', quiet=True)
wordlist = words.words()
len_indexes = []
length = 1
# wordlist sorting mechanism
wordlist.sort(key = len)

for i in range(len(wordlist)):
    if len(wordlist[i])> length:
        length+=1
        len_indexes.append(i)

len_indexes.append(len(wordlist))
# print(len_indexes)

#game initalization things
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH,HEIGHT])
pygame.display.set_caption('Typing Racer in Python')
surface = pygame.Surface((WIDTH, HEIGHT),pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60


#load  in assets like fonts and sound effects and music
fonts["header"] = pygame.font.Font('assets/fonts/square.ttf', 50)
pause_font= pygame.font.Font('assets/fonts/1up.ttf', 38)
fonts["banner"] = pygame.font.Font('assets/fonts/1up.ttf', 28)
font= pygame.font.Font('assets/fonts/AldotheApache.ttf', 48)

#sound effect
pygame.mixer.init()
pygame.mixer.music.load('assets/sound/music.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
sounds["click"] = pygame.mixer.Sound('assets/sound/sounds["click"].mp3')
whoosh = pygame.mixer.Sound('assets/sound/Swoosh.mp3')
wrong = pygame.mixer.Sound('assets/sound/Instrument Strum.mp3')

sounds["click"].set_volume(0.3)
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
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
new_level = True
# 2 letter - 8 letter choices as boolean options
choices = [False, True, False, False, False, False, False]

#highscore read in from text file
file = open('high.txt', 'r')
read = file.readlines()
high_score = int(read[0])
file.close()

class Word:
    def __init__(self, text, speed, y_pos, x_pos):
        self.text = text
        self.speed = speed
        self.y_pos = y_pos
        self.x_pos = x_pos

    def draw(self):
        color = 'black'
        screen.blit(font.render(self.text, True, color), (self.x_pos, self.y_pos))
        act_len = len(active_string)
        if active_string == self.text[:act_len]:
            screen.blit(font.render(active_string, True, 'green'), (self.x_pos, self.y_pos))

    def update(self):
        self.x_pos -= self.speed


       

class Button:
    def __init__(self, x_pos, y_pos, text, soundsclicked, surf):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.soundsclicked = soundsclicked
        self.surf = surf
    
    def draw(self):
        cir = pygame.draw.circle(self.surf, (45,89,135), (self.x_pos, self.y_pos), 35)
        if cir.collidepoint(pygame.mouse.get_pos()):
            butts = pygame.mouse.get_pressed()
            if butts[0]:
                pygame.draw.circle(self.surf, (190,35,35), (self.x_pos, self.y_pos), 35)
                self.soundsclicked = True
            else:
                pygame.draw.circle(self.surf, (190,89,135), (self.x_pos, self.y_pos), 35)

        pygame.draw.circle(self.surf, 'white', (self.x_pos, self.y_pos), 35, 3)
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
    screen.blit(fonts["header"].render(f'Level: {level}', True, 'white'), (10, HEIGHT-75))
    screen.blit(fonts["header"].render(f'"{active_string}"', True, 'white'), (270, HEIGHT-75))
    #pause button
    pause_btn = Button(748, HEIGHT-52, 'II', False, screen)
    pause_btn.draw()
    screen.blit(fonts["banner"].render(f'Score: {score}', True, 'black'), (250, 10))
    screen.blit(fonts["banner"].render(f'Best: {high_score}', True, 'black'), (550, 10))
    screen.blit(fonts["banner"].render(f'lives: {lives}', True, 'black'), (10, 10))
    return pause_btn.soundsclicked

def draw_pause():
    choice_commits = copy.deepcopy(choices)
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0,0,0,100), [100,100,600,300],0,5)
    pygame.draw.rect(surface, (0,0,0,200), [100,100,600,300],5,5)

    #define buttons for pause menu
    resume_btn = Button(160,200, '>', False, surface)
    resume_btn.draw()
    quit_btn = Button(410,200, 'X', False, surface)
    quit_btn.draw()
    #define text for pause menu
    surface.blit(fonts["header"].render('MENU', True, 'white'), (110,110))
    surface.blit(fonts["header"].render('PLAY!', True, 'white'), (210,175))
    surface.blit(fonts["header"].render('QUIT', True, 'white'), (450,175))
    surface.blit(fonts["header"].render('Active Letter Length: ', True, 'white'), (110,250))

    #define buttons for letter length selection
    for i in range(len(choices)):
        btn = Button(160+ (i*80),350, str(i+2), False, surface)
        btn.draw()
        if btn.soundsclicked:
            if choice_commits[i]:
                choice_commits[i] = False
            else:
                choice_commits[i] = True
        if choices[i] :
            pygame.draw.circle(surface, 'green',(160+ (i*80),350),35,5 )
    screen.blit(surface, (0,0))
    return resume_btn.soundsclicked, choice_commits, quit_btn.soundsclicked

def check_answer(scor):
    for wrd in word_objects:
        if wrd.text == submit:
            points = wrd.speed * len(wrd.text) * 10 * (len(wrd.text) / 4)
            scor += int(points)
            word_objects.remove(wrd)
            
            whoosh.play()
    return scor

def generate_level():
    word_objs = []
    include = []
    vertical_spacing = (HEIGHT - 150) // level
    if True not in choices:
        choices[0] = True
    for i in range(len(choices)):
        if choices[i]:
            include.append((len_indexes[i], len_indexes[i + 1]))
    for i in range(level):
        speed = random.randint(1, 3)
        y_pos = random.randint(10 + (i * vertical_spacing), (i + 1) * vertical_spacing)
        x_pos = random.randint(WIDTH, WIDTH + 1000)
        ind_sel = random.choice(include)
        index = random.randint(ind_sel[0], ind_sel[1])
        text = wordlist[index].lower()
        new_word = Word(text, speed, y_pos, x_pos)
        word_objs.append(new_word)
    return word_objs

def check_high_score():
    global high_score
    if score>high_score:
        high_score= score
        file = open('high.txt', 'w')
        file.write(str(int(high_score)))
        file.close()

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
                lives -= 1
    
    if len(word_objects)<=0 and not paused:
        level += 1
        new_level = True
    
    if submit != '':
        init = score
        score = check_answer(score)
        submit = ''
        if init == score:
            sounds["wrong"].play()
            pass 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            check_high_score()
            run = False
        
        if event.type == pygame.KEYDOWN:
            if not paused:
                if event.unicode.lower() in letters:
                    active_string += event.unicode.lower()
                    sounds["click"].play()
                if event.key == pygame.K_BACKSPACE and len(active_string)> 0:
                    active_string= active_string[:-1]
                    sounds["click"].play()
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

    if lives <=0:
        paused = True
        level = 1
        lives = 5
        word_objects = []
        new_level = True
        check_high_score()
        score = 0

    pygame.display.flip()

pygame.quit()