#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame
import os
import threading
import random
import queue
import sys

from datetime import datetime

import cv2
import numpy as np
from fer import FER

detector = FER()

cap = cv2.VideoCapture(0)

import sounddevice as sd

q = queue.Queue(maxsize=100)

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    rms = np.std(indata[::10, 0])
    if q.full():
        q.get()
    else:
        q.put(rms)
    # print(q.qsize(), rms)

pygame.init()

# Global Constants

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Chrome Dino Runner')

Ico = pygame.image.load('assets/DinoWallpaper.png')
pygame.display.set_icon(Ico)

RUNNING = [pygame.image.load(os.path.join('assets/Dino', 'DinoRun1.png'
           )), pygame.image.load(os.path.join('assets/Dino',
           'DinoRun2.png'))]
JUMPING = pygame.image.load(os.path.join('assets/Dino', 'DinoJump.png'))
DUCKING = [pygame.image.load(os.path.join('assets/Dino', 'DinoDuck1.png'
           )), pygame.image.load(os.path.join('assets/Dino',
           'DinoDuck2.png'))]

SMALL_CACTUS = [pygame.image.load(os.path.join('assets/Cactus',
                'SmallCactus1.png')),
                pygame.image.load(os.path.join('assets/Cactus',
                'SmallCactus2.png')),
                pygame.image.load(os.path.join('assets/Cactus',
                'SmallCactus3.png'))]
LARGE_CACTUS = [pygame.image.load(os.path.join('assets/Cactus',
                'LargeCactus1.png')),
                pygame.image.load(os.path.join('assets/Cactus',
                'LargeCactus2.png')),
                pygame.image.load(os.path.join('assets/Cactus',
                'LargeCactus3.png'))]

BIRD = [pygame.image.load(os.path.join('assets/Bird', 'Bird1.png')),
        pygame.image.load(os.path.join('assets/Bird', 'Bird2.png'))]

CLOUD = pygame.image.load(os.path.join('assets/Other', 'Cloud.png'))

BG = pygame.image.load(os.path.join('assets/Other', 'Track.png'))


class Dinosaur:

    X_POS = 80
    Y_POS = 310
    
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

        print(self.dino_rect)

    def update(self, customInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        # if userInput[pygame.K_UP] and not self.dino_jump:
        #     self.dino_duck = False
        #     self.dino_run = False
        #     self.dino_jump = True
        # elif userInput[pygame.K_DOWN] and not self.dino_jump:
        #     self.dino_duck = True
        #     self.dino_run = False
        #     self.dino_jump = False
        # elif not (self.dino_jump or userInput[pygame.K_DOWN]):
        #     self.dino_duck = False
        #     self.dino_run = True
        #     self.dino_jump = False

        if customInput['Up'] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif customInput['Down'] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or customInput['Down']):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:

    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        # self.x -= game_speed
        self.x -= modified_game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:

    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        # self.rect.x -= game_speed
        self.rect.x -= modified_game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):

    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):

    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    global modified_game_speed, smile_scores
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 10

    smile_scores = np.array([1.00] * 10)
    modified_game_speed = (2 - np.mean(smile_scores)) * game_speed
    volume = 0.0
    
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render('Points: ' + str(points) + ' Speed: ' + str(int(modified_game_speed)) + ' Volume: ' + f'{volume:4.2f}', True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (920, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        # x_pos_bg -= game_speed
        x_pos_bg -= modified_game_speed

    global q
    q = queue.Queue(maxsize=100)

    stream = sd.InputStream(
    device=1, channels=1,
    samplerate=16000, callback=audio_callback,
    blocksize=int(16000 / 100))
        
    with stream:

        start = datetime.now()

        while run:

            custom_input = {'Up': False, 'Down': False}

            buffer = [0.0]
            while q.qsize():
                buffer.append(q.get_nowait())
            volume = max(buffer)

            if volume > 0.1:
                custom_input['Up'] = True

            ret, frame = cap.read() # (720, 1280, 3)
            resampled_frame = np.array(frame[::5, ::5, :]) # (140, 256, 3) # 24 FPS
            emotions = detector.detect_emotions(resampled_frame)

            if len(emotions) > 0:
                emotion = emotions[0]
                emotion_d = emotion['emotions']
                smile_scores = np.append(smile_scores, emotion_d['happy'])[-10:]
                modified_game_speed = (2 - np.mean(smile_scores)) * game_speed
                custom_input['Down'] = True
            else:
                custom_input['Down'] = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            SCREEN.fill((255, 255, 255))
            userInput = pygame.key.get_pressed()

            player.draw(SCREEN)
            # player.update(userInput)
            player.update(custom_input)


            DICE = 5
            roll = random.randint(0, DICE)

            if (datetime.now() - start).total_seconds() > 15:
                if len(obstacles) == 0:
                    if roll == 0:
                        obstacles.append(SmallCactus(SMALL_CACTUS))
                    elif roll == -1:
                        obstacles.append(LargeCactus(LARGE_CACTUS))
                    elif roll == 2:
                        obstacles.append(Bird(BIRD))

            for obstacle in obstacles:
                obstacle.draw(SCREEN)
                obstacle.update()
                if player.dino_rect.colliderect(obstacle.rect):
                    pygame.time.delay(2000)
                    death_count += 1
                    menu(death_count)

            background()

            cloud.draw(SCREEN)
            cloud.update()

            score()

            clock.tick(30)
            pygame.display.update()


def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render('Press any Key to Start', True, (0, 0,
                               0))
        elif death_count > 0:
            text = font.render('Press any Key to Restart', True, (0, 0,
                               0))
            score = font.render('Your Score: ' + str(points), True, (0,
                                0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                                + 50)
            SCREEN.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT
                    // 2 - 140))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                main()


t1 = threading.Thread(target=menu(death_count=0), daemon=True)
t1.start()
