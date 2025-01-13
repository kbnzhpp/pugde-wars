import pygame
from config import *
from time import *
import math

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
            
        # Сохраняем предыдущие координаты
        try:
            self.speed = 400 / fps
        except ZeroDivisionError:
            self.speed = 0

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
                self.hook.hit_player_id
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
                        self.hit_player_id = player.id_p  # Только сохраняем ID
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

class Button:
    def __init__(self, x, y, width, height, main_color, secondary_color, font, action=None, image=None, text=""):
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.main_color = main_color
        self.secondary_color = secondary_color
        self.font = font
        self.action = action
        self.image = image
        self.text = text
        self.hovered = False
        self.clicked = False
        
    def draw(self, surface):
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Change color based on state
        color = self.secondary_color if self.hovered else self.main_color
        
        # Draw button
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

        if self.text:
            text_surf = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

        if self.image:
            img_rect = self.image.get_rect(centery=self.rect.centery, right=self.rect.right - 10)
            surface.blit(self.image, img_rect)
        
    def click(self, event):
        # Check if mouse is over button and clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
                if self.action:
                    self.action()
                    return True
        return False

class Panel:
    def __init__(self):
        self.open = False
        self.buttons = []  # Store buttons for event handling

    def draw_section(self, surface, title, items, rect, selected_attr, font):
        """Updated draw_section using Button class"""
        pygame.draw.rect(surface, (220, 220, 220), rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1)

        title_text = font.render(title, True, (0, 0, 0))
        surface.blit(title_text, (rect.x + 10, rect.y + 10))

        button_height = 60
        buttons_in_section = []

        for i, (skin_name, skin_image) in enumerate(items.items()):
            # Wrap setattr in lambda to delay execution
            action = lambda s=skin_name: setattr(self, selected_attr, s)
            
            button = Button(
                x=rect.x + 10,
                y=rect.y + 40 + i * (button_height + 5),
                width=rect.width - 20,
                height=button_height,
                main_color=(255, 255, 255),
                secondary_color=(200, 200, 200),
                font=font,
                action=action,  # Pass the wrapped action
                image=pygame.transform.scale(skin_image, (50, 50)),
                text=skin_name
            )
            button.draw(surface)
            buttons_in_section.append(button)
            
        return buttons_in_section

class SkinPanel(Panel):
    def __init__(self, skins_pudge, skins_hook, font, inscription, panel_w, panel_h):
        super().__init__()
        self.items_pudge = skins_pudge
        self.items_hook = skins_hook
        self.selected_player_skin = 'default'
        self.selected_hook_skin = 'default'
        self.pudge_buttons = []
        self.hook_buttons = []
        self.name = inscription
        self.name_font = font
        self.panel_w = panel_w
        self.panel_h = panel_h

    def toggle_panel(self):
        """Changing panel state"""
        self.open = not self.open

    def draw_panel(self, surface):
        if not self.open:
            return

        panel_rect = pygame.Rect(WIDTH - 550, 50, self.panel_w, self.panel_h)
        pygame.draw.rect(surface, (200, 200, 200), panel_rect)
        pygame.draw.rect(surface, (0, 0, 0), panel_rect, 2)

        # Draw sections and store their buttons
        section_font = pygame.font.Font(None, 30)
        player_section = pygame.Rect(panel_rect.x + 10, panel_rect.y + 50, 250, 400)
        hook_section = pygame.Rect(panel_rect.x + 10 + 260, panel_rect.y + 50, 250, 400)
        title = self.name_font.render(self.name, True, (0, 0, 0))
        surface.blit(title, (panel_rect.x + 10, panel_rect.y + 10))

        self.pudge_buttons = self.draw_section(surface, "Игрок", self.items_pudge, player_section, "selected_player_skin", section_font)
        self.hook_buttons = self.draw_section(surface, "Хук", self.items_hook, hook_section, "selected_hook_skin", section_font)

    def handle_event(self, event):
        if self.open and event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.pudge_buttons + self.hook_buttons:
                if button.rect.collidepoint(event.pos):
                    button.click(event)
                    return True
        return False
