import pygame
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.speedx = 0  #скорость перемещения. 0 - стоять на месте
        self.speedy = 0
        self.startX = x # Начальаня позиция
        self.startY = y
        self.image = pygame.image.load("data/images/pudge_left.png")
        self.rect = self.image.get_rect(center = (x, y))
        
    def move(self, left, right, up, down, center_rect):

        if left:
            self.speedx = -MOVE_SPEED
            self.image = pygame.image.load("data/images/pudge_left.png")

        if right:
            self.speedx = MOVE_SPEED
            self.image = self.image = pygame.image.load("data/images/pudge_right.png")
        if up:
            self.speedy = -MOVE_SPEED

        if down:
            self.speedy = MOVE_SPEED

        if not(left or right) or (left and right):
            self.speedx = 0
        if not(up or down) or (up and down):
            self.speedy = 0

        self.rect.x += self.speedx  
        self.rect.y += self.speedy

        self.collide(center_rect)

    def collide(self, center_rect):
        if self.rect.x > (WIDTH - self.rect.width) or self.rect.x <= 0:
            self.rect.x -= self.speedx

        if self.rect.y >= (HEIGHT - self.rect.height) or self.rect.y <= 0:
            self.rect.y -= self.speedy

        if pygame.Rect.colliderect(self.rect, center_rect):
            self.rect.x -= self.speedx
           
        #for p in center_rect:
            #if pygame.sprite.collide_rect(self, p): # если есть пересечение платформы с игроком
            #    if self.rect.left > 0:                      # если движется вправо
            #        self.rect.right = p.rect.left # то не движется вправо
            #
            #    if self.rect.left < 0:                      # если движется влево
            #        self.rect.left = p.rect.right
            #pass

class Hook:
    def __init__(self, player):
        self.x = player.rect.x
        self.y = player.rect.y
        self.image = pygame.image.load('')