import pygame
import os
import random


pygame.init()#start up pygame
pygame.mixer.init()

JUMP_SOUND = pygame.mixer.Sound(
    os.path.join('onkey_start','Assets','tracks','jump.wav')
)
DIE_SOUND = pygame.mixer.Sound(
    os.path.join("onkey_start", "Assets", "tracks", "die.wav")
)

FONT = pygame.font.Font(
    os.path.join("onkey_start", "Assets",'fonts', "PixelOperator-Bold.ttf"),
    30
)

SCORE_FONT = pygame.font.Font(
    os.path.join("onkey_start", "Assets", 'fonts',"PixelOperator-Bold.ttf"),
    23
)

#constants
SCREEN_WIDTH=720
SCREEN_HEIGHT=400
WINDOW_BG='#464858'
HORIZON_VEL=4
FPS=70

WINDOW=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))#the screen
pygame.display.set_caption('(m)onkey')

HORIZON = pygame.image.load(os.path.join('onkey_start','Assets','sprites','Horizon.png'))
HORIZON_y=SCREEN_HEIGHT//2 + SCREEN_HEIGHT//6
tint = pygame.Surface(HORIZON.get_size(), pygame.SRCALPHA)
tint.fill('#0F3040')   # Any RGBA color
HORIZON.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

clock=pygame.time.Clock()#refresh rate of the screen

#global
offset_x=0
left_foot = True
offset_y =0
####character

PLAY_WIDTH=75
PLAY_HEIGHT=75

PLAY_JUMP = pygame.transform.scale(pygame.image.load(os.path.join('onkey_start','Assets','jump.png')),
                                   (PLAY_WIDTH,PLAY_HEIGHT))
PLAY_STANDING =pygame.transform.scale(pygame.image.load(os.path.join('onkey_start','Assets','stand.png')),
                                      (PLAY_WIDTH,PLAY_HEIGHT))

PLAY_LEFT=pygame.transform.scale(pygame.image.load(os.path.join('onkey_start','Assets','left.png')),
                                 (PLAY_WIDTH,PLAY_HEIGHT))
PLAY_RIGHT=pygame.transform.scale(pygame.image.load(os.path.join('onkey_start','Assets','right.png')),
                                 (PLAY_WIDTH,PLAY_HEIGHT))
PLAY_y=HORIZON_y - PLAY_HEIGHT + PLAY_HEIGHT//4
PLAY_x=PLAY_WIDTH + PLAY_WIDTH//4                                  
#define event
SWITCH_FOOT = pygame.USEREVENT + 1


pygame.time.set_timer(SWITCH_FOOT,125)#higher number slower 

CACTUS = pygame.image.load(os.path.join('onkey_start','Assets',
                                        'plant.png')).convert_alpha()
CACTUS_WIDTH = 50

obstacle_offset_x = 0

def draw_window(play,game_over,dino,obstacles,score,high_score):
    global left_foot

    horizon_tiles=2
    horizon_width = HORIZON.get_width()

    WINDOW.fill(WINDOW_BG)

    for i in range(horizon_tiles):
        WINDOW.blit(HORIZON,(horizon_width * i + offset_x,HORIZON_y))

    for obstacle in obstacles:
        cactus_image = pygame.transform.scale(
            CACTUS,(obstacle.width, obstacle.height)).convert_alpha()

        WINDOW.blit(cactus_image,(obstacle.x,obstacle.y))

    if play:
        if left_foot:
            WINDOW.blit(PLAY_LEFT,(dino.x,dino.y))
        else:
            WINDOW.blit(PLAY_RIGHT,(dino.x,dino.y))

    else:
        if game_over:
            WINDOW.blit(PLAY_JUMP, (dino.x, dino.y))
        else:
            WINDOW.blit(PLAY_STANDING, (dino.x, dino.y))

    if not play:
        if game_over:
            text = FONT.render('GAME OVER - Press E to play again',True,(255, 255, 255))

        else:
            text = FONT.render('Press E to start',True,(255, 255, 255))

        text_rect = text.get_rect(center=(SCREEN_WIDTH//2,50))
        WINDOW.blit(text,text_rect)

        high_score_text = SCORE_FONT.render(
            f"High: {int(high_score)}",
            True,(255, 255, 255))
        WINDOW.blit(high_score_text,(20,50))

    score_text = SCORE_FONT.render(f'Score : {int(score)}',True,(255, 255, 255))
    WINDOW.blit(score_text,(20,20))

    pygame.display.update()

def generate_cacti(starting_point=0):
    cacti=[]
    num_cactus = random.choices(
        [1,2,3],
        weights=[60,30,10]
    )[0]
    
    for i in range(num_cactus):
        cactus_height = random.randint(50,80)
        cactus_y_pos = HORIZON_y - cactus_height + cactus_height//4
        gap = random.randint(450,700)
        cactus_x_pos = starting_point + SCREEN_WIDTH + gap + i*150

        cacti.append(pygame.Rect(
            cactus_x_pos,cactus_y_pos,CACTUS_WIDTH,cactus_height))
    return cacti

def game_loop():
    #main code for the game
    global left_foot,offset_y,offset_x
    gravity = 0
    jumping = False

    cacti = generate_cacti()

    game_running = True
    play= False
    game_over = False
    score = 0
    high_score = 0
    

    dino = pygame.Rect(PLAY_x,PLAY_y,PLAY_WIDTH,PLAY_HEIGHT)

    while game_running:
        clock.tick(FPS)
    
        #poll for events
        
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                game_running = False

            if event.type == SWITCH_FOOT:
                left_foot = not left_foot

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    
                if not play and not game_over:
                    play=True

                elif play and not jumping:
                    gravity = -18
                    jumping = True

                    JUMP_SOUND.play()

                elif game_over:
                    play = False
                    game_over = False

                    score=0

                    gravity = 0
                    jumping = False

                    dino.x = PLAY_x
                    dino.y = PLAY_y

                    offset_x = 0
                    left_foot = True

                    cacti = generate_cacti()

        if play:
            gravity +=1
            dino.y += gravity
            score += 0.1
            if score > high_score:
                high_score = score
            if dino.y >= PLAY_y:
                dino.y = PLAY_y
                gravity = 0
                jumping = False
            for obstacle in cacti:
                obstacle.x -= HORIZON_VEL
            
                
            for obstacle in cacti:
                hitbox = obstacle.inflate(-25,-15)

                pygame.draw.rect(WINDOW,(255,0,0),hitbox,2)
                if dino.colliderect(hitbox):
                    DIE_SOUND.play()
                    play = False
                    game_over = True
                    
            cacti = [obstacle for obstacle in cacti if obstacle.right > 0]
                
            if len(cacti) == 0:
                cacti = generate_cacti()

            offset_x -= HORIZON_VEL
            
            if abs(offset_x) > HORIZON.get_width():
                offset_x = 0
            
            #dont think about it
        draw_window(play,game_over,dino=dino,obstacles=cacti,score=score,high_score=high_score)
    pygame.quit()

if __name__ == '__main__':#tells to only run when file is executed
    game_loop()

