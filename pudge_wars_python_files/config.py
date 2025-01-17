import pygame

WIDTH = 1920
HEIGHT = 1080
MOVE_SPEED = 5
WIN_CONDITION = 50
HOOK_RADIUS = 1200
HOOK_SPEED = 19
HOOK_COOLDOWN = 4000
skins_pudge = {
    'default' : pygame.image.load('data/images/pudge_default_right.png'),
    'pig' : pygame.image.load('data/images/pudge_pig_right.png'),
    'steve' : pygame.image.load('data/images/pudge_steve_right.png'),
    'roblox' : pygame.image.load('data/images/pudge_roblox_right.png'),
    'jett' : pygame.image.load('data/images/pudge_jett_right.png'),
}   
skins_hook = {
    'default' : pygame.image.load('data/images/hook_default_right.png'), 
    'chesters' : pygame.image.load('data/images/hook_chesters_right.png'),
    'float' : pygame.image.load('data/images/hook_float_right.png'),
    'dragclaw' : pygame.image.load('data/images/hook_dragclaw_right.png'),
    'valorant' : pygame.image.load('data/images/hook_valorant_right.png'),
}