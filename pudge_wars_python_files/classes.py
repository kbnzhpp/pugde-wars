import pygame
from config import *
from time import *
from font_change import *

class Button:
    def __init__(self, x, y, width, height, main_color, secondary_color, font, action=None, image=None, text="", text_color=(0, 0, 0), volume=False):
        self.rect = pygame.rect.Rect(x, y, width, height)
        self.main_color = main_color
        self.secondary_color = secondary_color
        self.font = font
        self.action = action
        self.image = image
        self.text = text
        self.hovered = False
        self.active = True
        self.volume = volume
        self.text_color = text_color

    def draw(self, surface):
        # Get current mouse position
        if self.active:
            mouse_pos = pygame.mouse.get_pos()
            self.hovered = self.rect.collidepoint(mouse_pos)

            # Change color based on state
            color = self.secondary_color if self.hovered else self.main_color

            # Draw button
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

            if self.text:
                if self.volume:
                    text_surf = textOutline(self.font, self.text, self.text_color, (80, 80, 80))
                    text_rect = text_surf.get_rect(center=self.rect.center)
                    surface.blit(text_surf, text_rect)
                else:
                    text_surf = self.font.render(self.text, True, self.text_color)
                    text_rect = text_surf.get_rect(center=self.rect.center)
                    surface.blit(text_surf, text_rect)

            if self.image:
                img_rect = self.image.get_rect(centery=self.rect.centery, right=self.rect.right - 10)
                surface.blit(self.image, img_rect)

    def require_click(func):
        def wrapper(self, event, *args, **kwargs):
            # Проверка события: нажатие мыши и курсор над кнопкой
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(pygame.mouse.get_pos())
                and self.active
                and self.action
            ):
                return func(self, *args, **kwargs)  # Возвращаем результат действия
            return None  # Если клик не произошёл, возвращаем None
        return wrapper


    @require_click
    def click(self, *args, **kwargs):
        return self.action(*args, **kwargs)

class Panel:
    def __init__(self):
        self.open = False
        self.buttons = []  # Store buttons for event handling

    def toggle_panel(self):
        """Changing panel state"""
        self.open = not self.open

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
        self.panel_rect = pygame.Rect(WIDTH / 2 - 225, 50, self.panel_w, self.panel_h)

        self.button_close = Button(
            x=WIDTH - 65,
            y=self.panel_rect.y + 10,
            width=35,
            height=35,
            main_color=(255, 255, 255),
            secondary_color=(200, 200, 200),
            font=pygame.font.Font(None, 40),
            action=self.toggle_panel,  # Pass the wrapped action
            image=None,
            text='x',
            text_color=(0, 0, 0),
            volume=False
        )

    def draw_panel(self, surface):
        if not self.open:
            return

        pygame.draw.rect(surface, (200, 200, 200), self.panel_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.panel_rect, 2)

        # Draw sections and store their buttons
        section_font = pygame.font.Font(None, 30)
        player_section = pygame.Rect(self.panel_rect.x + 10, self.panel_rect.y + 50, 250, 450)
        hook_section = pygame.Rect(self.panel_rect.x + 10 + 260, self.panel_rect.y + 50, 250, 450)
        title = self.name_font.render(self.name, True, (0, 0, 0))
        surface.blit(title, (self.panel_rect.x + 10, self.panel_rect.y + 10))

        self.pudge_buttons = self.draw_section(surface, "Игрок", self.items_pudge, player_section, "selected_player_skin", section_font)
        self.hook_buttons = self.draw_section(surface, "Хук", self.items_hook, hook_section, "selected_hook_skin", section_font)

        self.buttons.extend(self.pudge_buttons)
        self.buttons.extend(self.hook_buttons)
        

    def handle_event(self, event):
        if self.open and event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    button.click(event)
                    return True
        return False
