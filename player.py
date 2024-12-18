import pygame
from config import *
from time import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, group):
        super().__init__()
        self.speedx = 0  # скорость перемещения. 0 - стоять на месте
        self.speedy = 0
        self.image_left = pygame.image.load("data/images/pudge_left.png")
        self.image_right = pygame.image.load("data/images/pudge_right.png")
        self.image = self.image_left
        self.rect = self.image_left.get_rect(center = (x, y))
        self.hitbox = pygame.Rect(x + 50, y + 40, 100, 80)
        self.hitbox.center = (x, y)
        self.hook = Hook(self)
        self.add(group)
        
    def move(self, left, right, up, down, center_rect, players):

        # Speed changes
        

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

        if self.hook.active:
            self.speedx = 0
            self.speedy = 0

        self.rect.center = self.hitbox.center
        self.hitbox.x += self.speedx
        self.hitbox.y += self.speedy

        self.collide(center_rect, players)

    def collide(self, center_rect, players):
        if self.hitbox.x > (WIDTH - self.hitbox.width) or self.hitbox.x <= 0:
            self.hitbox.x -= self.speedx

        if self.hitbox.y >= (HEIGHT - self.hitbox.height) or self.hitbox.y <= 0:
            self.hitbox.y -= self.speedy

        if pygame.Rect.colliderect(self.hitbox, center_rect):
            self.hitbox.x -= self.speedx

        for collision in players:
            if collision != self and self.hitbox.colliderect(collision.hitbox):

                # Рассчитываем глубину столкновения
                dx_left = collision.hitbox.right - self.hitbox.left  # Слева
                dx_right = self.hitbox.right - collision.hitbox.left  # Справа
                dy_top = collision.hitbox.bottom - self.hitbox.top  # Сверху
                dy_bottom = self.hitbox.bottom - collision.hitbox.top  # Снизу

                # Определяем минимальное столкновение
                overlap_x = min(dx_left, dx_right)
                overlap_y = min(dy_top, dy_bottom)

                # Смещение по направлению меньшего столкновения
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

class Hook(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player =  player
        self.x = player.rect.x
        self.y = player.rect.y
        self.image = pygame.image.load('data/images/hook_right.png')
        self.rect = self.image.get_rect(center = (self.x, self.y))
        self.target_position = None
        self.active = False
        self.returning = False
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery

    def launch(self, target_pos):
        if not self.active and not self.returning:
            self.active = True
            self.target_position = target_pos
            
            hook_start = self.player.rect.center
            self.start_position = hook_start
            self.pos_x, self.pos_y = hook_start
            self.rect.center = hook_start
        
    def move(self, players):
        if self.active and self.target_position:
            # Calculate the direction vector
            target_x, target_y = self.target_position
            dx = target_x - self.pos_x
            dy = target_y - self.pos_y
            

            # Changing direction of hook image
            if dx < 0:
                self.image = pygame.image.load('data/images/hook_left.png')
            else:
                self.image = pygame.image.load('data/images/hook_right.png')

            # Normalize the direction vector
            traveled_distance = ((self.pos_x - self.start_position[0])**2 + 
                                 (self.pos_y - self.start_position[1])**2)**0.5
            
            distance = (dx**2 + dy**2)**0.5
            if distance == 0:
                self.rect.center = self.player.rect.center
                self.active = False
                self.returning = False
                return
            
            if (abs(dx) <= HOOK_SPEED and abs(dy) <= HOOK_SPEED) or traveled_distance >= HOOK_RADIUS or self.collide(players):
                self.rect.center = self.player.rect.center   # Snap to the exact position
                self.returning = True
                self.active = False
                return
            
            direction_x = dx / distance
            direction_y = dy / distance
            
            # Move the hook incrementally along the direction vector
            self.pos_x += direction_x * HOOK_SPEED
            self.pos_y += direction_y * HOOK_SPEED
            
            self.rect.center = (int(self.pos_x), int(self.pos_y))
            
        elif self.returning:
            self.move_backwards()
        self.collide(players)

    def move_backwards(self):
        # Calculate direction back to player
        dx = self.player.rect.centerx - self.pos_x
        dy = self.player.rect.centery - self.pos_y
        
        # Normalize direction vector
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 10:
            self.rect.center = self.player.rect.center
            self.active = False
            self.returning = False
            return
            
        if abs(dx) <= HOOK_SPEED and abs(dy) <= HOOK_SPEED:
            self.rect.center = self.player.rect.center  # Snap back to player
            self.returning = False
            self.active = False
            return

        direction_x = dx / distance
        direction_y = dy / distance

        # Move the hook incrementally
        self.pos_x += direction_x * (HOOK_SPEED * 3)
        self.pos_y += direction_y * (HOOK_SPEED * 3)
        
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def draw_chain(self, screen):
        if self.active or self.returning:
            pygame.draw.line(
                screen, 
                (200, 200, 200),  # Color: grey
                self.player.rect.center,  # Starting position (player's center)
                self.rect.center,  # Hook's position
                10  # Line thickness
            )
    
    def collide(self, players):
        for player in players:
            if self.rect.collidepoint(player.hitbox.center) and self.player != player:
                player.kill()  # Remove the collided player
                self.active = False  # Stop hook movement
                self.returning = True  # Start return movement
                return True  
        return False 
