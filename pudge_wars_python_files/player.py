import pygame
from config import *
from time import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, group, team, skin, skin_hook):
        super().__init__(group)
        self.skin = skin
        self.direction = 'right'
        self.image = pygame.image.load(f"data/images/pudge_{self.skin}_{self.direction}.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.rect.Rect(self.rect.x, self.rect.y - self.rect.height / 2, 132, 80)
        self._id = None  # Приватное поле для ID
        self.team = team
        self.alive = True
        self.hook = Hook(self, skin_hook)
        self.speed = MOVE_SPEED
        self.spawn_x = x  # Сохраняем начальную позицию
        self.spawn_y = y
        self.respawn_timer = 0
        self.just_respawned = False  # Флаг для защиты только что возродившегося игрока
        self.group = group  # Сохраняем ссылку на группу
        self.last_hit_by = None  # Добавляем отслеживание последнего урона
        self.shield_timer = 0

    @property
    def id_p(self):
        return self._id

    @id_p.setter
    def id_p(self, value):
        self._id = value   

    def set_id(self, player_id):
        """Устанавливает ID игрока"""
        self._id = player_id

    def check_collisions(self, center_rect, players, axis='x'):
        """Проверяет коллизии с центральной областью и другими игроками"""
        if self.hitbox.colliderect(center_rect):
            return True
            
        #for player in players:
        #    if player != self and player.alive and self.hitbox.colliderect(player.hitbox):
        #        return True
        return False

    def move(self, left, right, up, down, center_rect, players, fps):
        if self.hook.active:
            return

        prev_x = self.rect.x
        prev_y = self.rect.y
        prev_hitbox_x = self.hitbox.x
        prev_hitbox_y = self.hitbox.y

        if left:
            self.hitbox.x -= self.speed
            self.direction = 'left'
        if right:
            self.hitbox.x += self.speed
            self.direction = 'right'
            
        # Проверяем коллизии по X
        if self.check_collisions(center_rect, players, 'x'):
            self.rect.x = prev_x
            self.hitbox.x = prev_hitbox_x
                
        # Обновляем координаты по Y
        if up:
            self.hitbox.y -= self.speed
        if down:
            self.hitbox.y += self.speed

        # Проверяем коллизии по Y
        if self.check_collisions(center_rect, players, 'y'):
            self.rect.y = prev_y
            self.hitbox.y = prev_hitbox_y
        
        # Ограничиваем движение в пределах экрана
        self.hitbox.x = max(0, min(self.hitbox.x, WIDTH - self.hitbox.width))
        self.hitbox.y = max(40, min(self.hitbox.y, HEIGHT - self.hitbox.height))

        self.rect.center = self.hitbox.center

    def kill(self):
        """Убивает игрока и запускает таймер респавна"""
        if self.just_respawned:
            return
        self.alive = False
        if self.respawn_timer == 0:
            self.respawn_timer = pygame.time.get_ticks()
        if self.shield_timer == 0:
            self.shield_timer = pygame.time.get_ticks()
        self.hook.active = False
        self.hook.returning = False
        self.hook.rect.center = self.rect.center

    def update(self):
        """Обновляет состояние игрока"""
        current_time = pygame.time.get_ticks()
        self.image = pygame.image.load(f'data/images/pudge_{self.skin}_{self.direction}.png')

        if not self.alive and self.respawn_timer > 0:
            time_passed = current_time - self.respawn_timer
            
            if time_passed >= 2500:  # 1.5 секунды
                self.hook.hit_player_id = None
                self.alive = True
                self.respawn_timer = 0
                self.rect.center = (self.spawn_x, self.spawn_y)
                self.hitbox.center = (self.spawn_x, self.spawn_y)  

class Hook(pygame.sprite.Sprite):
    def __init__(self, player, skin):
        super().__init__()
        self.player = player
        self.direction = 'right'
        self.skin = skin
        self.image = pygame.image.load(f'data/images/hook_{self.skin}_{self.direction}.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        self.target_position = None
        self.active = False
        self.returning = False
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery
        self.hit_player_id = None  # ID игрока, в которого попали\
        self.cooldown = 0
        self.timer = 0

    def launch(self, target_pos):
        if not self.active and not self.returning and self.player.alive and self.cooldown == 0:
            self.active = True
            self.target_position = target_pos
            self.start_position = self.player.rect.center
            self.pos_x, self.pos_y = self.start_position
            self.rect.center = self.start_position
            self.cooldown = pygame.time.get_ticks()
    
    def update(self):
        current_time = pygame.time.get_ticks()

        self.timer = current_time - self.cooldown
        if self.timer >= HOOK_COOLDOWN:
            self.cooldown = 0

        if self.active and self.target_position and self.player.alive:
            # Вычисляем вектор направления

            dx = self.target_position[0] - self.pos_x
            dy = self.target_position[1] - self.pos_y
            
            # Поворачиваем изображение хука
            if dx < 0:
                self.direction = 'left'
            else:
                self.direction = 'right'

            self.image = pygame.image.load(f'data/images/hook_{self.skin}_{self.direction}.png')
            # Нормализуем вектор
            distance = (dx**2 + dy**2)**0.5
            traveled_distance = ((self.pos_x - self.start_position[0])**2 + 
                               (self.pos_y - self.start_position[1])**2)**0.5
            
            # Проверяем условия возврата
            if distance < HOOK_SPEED or traveled_distance >= HOOK_RADIUS:
                self.returning = True
                self.active = False
                return
            
            # Двигаем хук
            direction_x = dx / distance
            direction_y = dy / distance
            self.pos_x += direction_x * HOOK_SPEED
            self.pos_y += direction_y * HOOK_SPEED
            self.rect.center = (int(self.pos_x), int(self.pos_y))
            
            # Проверяем попадание в других игроков
            for player in self.player.group:
                if player != self.player and player.alive and player.team != self.player.team:
                    if self.rect.colliderect(player.hitbox):
                        self.hit_player_id = player.id_p
                        self.returning = True
                        self.active = False
                        return
            
        elif self.returning:
            # Возвращаем хук к игроку
            dx = self.player.rect.centerx - self.pos_x
            dy = self.player.rect.centery - self.pos_y
            
            distance = (dx**2 + dy**2)**0.5
            if distance < 30:  # Если хук достаточно близко к игроку
                self.rect.center = self.player.rect.center
                self.returning = False
                return
                
            # Двигаем хук обратно
            direction_x = dx / distance
            direction_y = dy / distance
            self.pos_x += direction_x * (HOOK_SPEED * 3)
            self.pos_y += direction_y * (HOOK_SPEED * 3)
            self.rect.center = (int(self.pos_x), int(self.pos_y))
        
    def draw_chain(self, screen):
        if self.active or self.returning:
            pygame.draw.line(
                screen,
                (200, 200, 200),  # Серый цвет
                self.player.rect.center,
                self.rect.center,
                8  # Толщина линии
            )
