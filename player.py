import pygame
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, group):
        pygame.sprite.Sprite.__init__(self)
        self.speedx = 0  #скорость перемещения. 0 - стоять на месте
        self.speedy = 0
        self.image_left = pygame.image.load("data/images/pudge_left.png")
        self.image_right = pygame.image.load("data/images/pudge_right.png")
        self.image = self.image_left
        self.rect = self.image_left.get_rect(center = (x, y))
        self.hitbox = pygame.Rect(x + 50, y + 40, 100, 80)
        self.hitbox.center = (x, y)
        
        self.add(group)
        self.hook = Hook(self)

    def move(self, left, right, up, down, center_rect, players, screen):

        if left:
            self.speedx = -MOVE_SPEED
            self.image = self.image_left
        if right:
            self.speedx = MOVE_SPEED
            self.image = self.image_right
        if up:
            self.speedy = -MOVE_SPEED

        if down:
            self.speedy = MOVE_SPEED

        if not(left or right) or (left and right):
            self.speedx = 0
        if not(up or down) or (up and down):
            self.speedy = 0

        self.hitbox.x += self.speedx
        self.hitbox.y += self.speedy

        self.collide(center_rect, players, screen)
        
        self.rect.center = self.hitbox.center

    def collide(self, center_rect, players, screen):
        if self.hitbox.x > (WIDTH - self.hitbox.width) or self.hitbox.x <= 0:
            self.hitbox.x -= self.speedx

        if self.hitbox.y >= (HEIGHT - self.hitbox.height) or self.hitbox.y <= 0:
            self.hitbox.y -= self.speedy

        if pygame.Rect.colliderect(self.hitbox, center_rect):
            self.hitbox.x -= self.speedx

        for collision in players:
            if collision != self and self.hitbox.colliderect(collision.hitbox):

                # Рассчитываем глубину проникновения
                dx_left = collision.hitbox.right - self.hitbox.left  # Слева
                dx_right = self.hitbox.right - collision.hitbox.left  # Справа
                dy_top = collision.hitbox.bottom - self.hitbox.top  # Сверху
                dy_bottom = self.hitbox.bottom - collision.hitbox.top  # Снизу

                # Определяем минимальное проникновение
                overlap_x = min(dx_left, dx_right)
                overlap_y = min(dy_top, dy_bottom)

                # Смещение по направлению меньшего проникновения
                if overlap_x < overlap_y:
                    # Горизонтальное столкновение
                    if dx_left < dx_right:  # Удар справа
                        self.hitbox.left = collision.hitbox.right
                    else:  # Удар слева
                        self.hitbox.right = collision.hitbox.left
                    self.speedx = 0
                else:
                    # Вертикальное столкновение
                    if dy_top < dy_bottom:  # Удар снизу
                        self.hitbox.top = collision.hitbox.bottom
                    else:  # Удар сверху
                        self.hitbox.bottom = collision.hitbox.top
                    self.speedy = 0

class Hook:
    def __init__(self, player):
        self.x = player.rect.x
        self.y = player.rect.y

        self.image = pygame.image.load('data/images/hook_right.png')