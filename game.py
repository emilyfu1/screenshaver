"""Some simple skeleton code for a pygame game/animation

This skeleton sets up a basic 800x600 window, an event loop, and a
redraw timer to redraw at 30 frames per second.
"""
from __future__ import division
import math
import sys
import random
import pygame

TIME_ALLOTTED = 45

SHRINK_RAZOR = pygame.USEREVENT + 2
STOPWATCH_TICK = pygame.USEREVENT + 3

class GameObject():
    def __init__(self, pos, img_path):
        self.pos = pos
        self.img = pygame.image.load(img_path)

        self.rect_width = self.img.get_rect().width
        self.rect_height = self.img.get_rect().height

    def draw_on(self, surface):
        surface.blit(self.img, tuple(self.pos))

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.rect_width, self.rect_height)
    
    def set_pos(self, pos):
        self.pos = pos

class Razor(GameObject):
    def __init__(self):
        super().__init__([0,0], "razor.png")
        self.rect_height = 20
        self.rect_width = self.rect_width//3

class Hair(GameObject):
    def __init__(self, pos=[0, 0]):
        super().__init__(pos, "hair.png")

class MyGame(object):
    START, PLAYING, GAMEOVER = 0, 1, 2
    def __init__(self):
        """Initialize a new game"""
        pygame.mixer.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()

        pygame.time.set_timer(SHRINK_RAZOR, 15000)
        pygame.time.set_timer(STOPWATCH_TICK, 1000)

        # set up a 640 x 480 window
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.Font('font.ttf', 25)

        # music
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.load('johncage433.mp3')
        pygame.mixer.music.play(-1)

        self.original_hair = Hair()

        # use a black background
        self.bg_color = 255, 229, 204

        self.clock = pygame.time.Clock()

        # Setup a timer to refresh the display FPS times per second
        self.FPS = 60
        self.REFRESH = pygame.USEREVENT+1
        pygame.time.set_timer(self.REFRESH, 1000//self.FPS)

        self.reset_game()
    
    def generate_hair(self):
        for hair in range(200): 
            self.hairs.append(Hair([random.randrange(self.width - self.original_hair.rect_width),random.randrange(self.height - self.original_hair.rect_height)]))

    def run(self):
        """Loop forever processing events"""
        shave = pygame.mixer.Sound('shave.wav')
        while True:
            for event in pygame.event.get():
                # player is asking to quit
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and self.state == self.START:
                    self.state = self.PLAYING
                elif event.type == SHRINK_RAZOR:
                    self.razor.img = pygame.transform.scale(
                        self.razor.img, (
                            int(self.razor.img.get_rect().width // 1.1),
                            int(self.razor.img.get_rect().height // 1.1)
                        )
                    )
                    self.razor.rect_width = self.razor.rect_width // 1.1
                    self.razor.rect_height = self.razor.rect_height // 1.1
                elif event.type == STOPWATCH_TICK and self.state == self.PLAYING:
                    if self.timer >= 0:
                        self.timer -= 1
                        if self.timer <= 0:
                            if len(self.hairs) > 0:
                                self.lives -= 1
                                self.timer = TIME_ALLOTTED
                                self.generate_hair()
                                if self.lives <= 0:
                                    self.state = self.GAMEOVER
                        if len(self.hairs) == 0:
                            self.timer = TIME_ALLOTTED
                            self.generate_hair()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.state == self.GAMEOVER:
                    self.reset_game()
                    continue
                else:
                    pass # an event type we don't handle
            if self.state == self.GAMEOVER:
                pygame.mouse.set_visible(True)
            
            if self.state == self.PLAYING:
                self.razor.pos = pygame.mouse.get_pos()
                pygame.mouse.set_visible(False)
                temp = []
                for hair in self.hairs:
                    if self.razor.rect().colliderect(hair.rect()):
                        shave.play()
                        self.points += 1
                    else:
                        temp.append(hair)
                self.hairs = temp
            self.draw()
            self.clock.tick(self.FPS)    

    def draw(self):
        """Update the display"""
        # everything we draw now is to a buffer that is not displayed

        black = (0,0,0)
        white = (255,255,255)
        points = self.font.render("points: {}".format(self.points), True, black)
        life = self.font.render("lives: {}".format(self.lives), True, black)
        timer = self.font.render("time remaining: {}".format(self.timer), True, black)

        if self.state == self.START:
            self.screen.fill(black)
            starttxt = self.font.render("screenshaver (inspired by simone giertz). click anywhere to start", True, white)
            startrect = starttxt.get_rect()
            startrect = startrect.move((self.width-startrect.width)//2, (self.height-startrect.height)//2)
            self.screen.blit(starttxt, startrect)
        elif self.state == self.PLAYING:
            self.screen.fill(self.bg_color)
            for hair in self.hairs:
                hair.draw_on(self.screen)
            self.razor.draw_on(self.screen)
            pointsrect = points.get_rect()
            pointsrect = pointsrect.move(self.width - pointsrect.width, 0)
            liferect = life.get_rect()
            liferect = liferect.move((self.width - liferect.width)//2, self.height - liferect.height)
            timerect = timer.get_rect()
            self.screen.blit(points, pointsrect)
            self.screen.blit(life, liferect)
            self.screen.blit(timer, timerect)
        elif self.state == self.GAMEOVER:
            self.screen.fill((black))
            endtxt = self.font.render("game over, you shaved {} hairs. click anywhere to return to start".format(self.points), True, white)
            endrect = endtxt.get_rect()
            endrect = endrect.move((self.width-endrect.width)//2, (self.height-endrect.height)//2)
            self.screen.blit(endtxt, endrect)

        # flip buffers so that everything we have drawn gets displayed
        pygame.display.flip()

    def reset_game(self):
        self.lives = 3
        self.points = 0
        self.timer = TIME_ALLOTTED
        self.razor = Razor()
        self.hairs = []
        self.generate_hair()
        self.state = self.START
        pass

MyGame().run()
pygame.quit()
sys.exit(0)