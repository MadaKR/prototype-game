import pygame
import pygame.gfxdraw
import math
import os

pygame.font.init()

# Used for hex code colors
def color(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def background(game, c):
    if type(c) == tuple:
        pygame.Surface.fill(game.screen_surface, c)
    else:
        pygame.Surface.fill(game.screen_surface, color(c))

def circle(game, x, y, size, color, strokeWidth = 0):
    if strokeWidth != 0:
        pygame.draw.circle(game.screen_surface, color, (x, y), size)
        pygame.draw.circle(game.screen_surface, (0, 0, 0), (x, y), size, strokeWidth)
    else:
        pygame.draw.circle(game.screen_surface, color, (x, y), size)

def rect(game, x, y, w, h, color):
    pygame.draw.rect(game.screen_surface, color, (x, y, w, h))

def image(game, image, x, y, w = None, h = None, smooth = True, angle = 0.0):
    if w != None and h != None:
        if smooth:
            image = pygame.transform.smoothscale(image, (w, h))
        else:
            image = pygame.transform.scale(image, (w, h))
    image = pygame.transform.rotate(image, angle)
    image_rect = image.get_rect(center = (x, y))
    game.screen_surface.blit(image, image_rect)

def loadAssets(game):
    for root, _, files in os.walk('assets'):  
        for filename in files:
            match filename.split('.')[1]:
                case 'wav':
                    game.sounds[filename.split('.')[0]] = pygame.mixer.Sound(os.path.join(root, filename))
                case 'png':
                    game.textures[filename.split('.')[0]] = pygame.image.load(os.path.join(root, filename)).convert_alpha()

class Button:
    def __init__(self, game: object, x, y, w, h, pressFunc, image, pressedImage = None, centered = False, isScalar = True):
        self.game = game # Game object reference

        # If true, then all dimensions are 0.0 to 1.0 as a fraction of the
        # respective window width or height (0.5 is center of the window)
        self.isScalar = isScalar
        # Keep raw scalar values for potential resizing later
        self.sPos = pygame.Vector2(x, y)
        self.sSize = pygame.Vector2(w, h)

        # Set pixel coordinates based on scalar values
        # or to raw pixel values if not using scalars.
        if self.isScalar:
            self.pos = pygame.Vector2(x * game.screen_width, y * game.screen_height)
            self.size = pygame.Vector2(w * game.screen_width, h * game.screen_height)
        else:
            self.pos = pygame.Vector2(x, y)
            self.size = pygame.Vector2(w, h)

        # pressFunc should be a lambda of the function to call when the button is pressed
        self.pressFunc = pressFunc
        # Determines if the x, y of the button is the center (true) or top left corner (false)
        self.centered = centered
        # Button texture
        self.image = self.game.textures[image]
        # Texture while the player is clicking the button
        self.pressedImage = self.game.textures[pressedImage]
        self.pressed = False
    
    def update(self):
        """Detects if the button is pressed."""
        if self.pressed and pygame.mouse.get_just_released()[0]:
            if self.isHovered():
                self.pressFunc()

        if self.isHovered() and pygame.mouse.get_just_pressed()[0]:
            self.pressed = True
        
        if not self.isHovered() and pygame.mouse.get_pressed()[0]:
            self.pressed = False

    def isHovered(self, pos = None):
        """Returns true if the mouse (or given coordinates) are within bounds of the button"""
        if pos == None:
            # If not checking a specific position, just use the mouse coordinates
            pos = pygame.Vector2(pygame.mouse.get_pos())
        if self.centered:
            # Draw 
            if (pos.x > self.pos.x + self.size.x / 2 or pos.x < self.pos.x - self.size.x / 2): return False
            if (pos.y > self.pos.y + self.size.y / 2 or pos.y < self.pos.y - self.size.y / 2): return False
        else:
            if (pos.x < self.pos.x or pos.x > self.pos.x + self.w): return False
            if (pos.y < self.pos.y or pos.y > self.pos.y + self.h): return False
        return True
    
    def draw(self):
        """Draws the button image"""
        if self.centered:
            if self.pressed:
                image(self.game, self.pressedImage, self.pos.x, self.pos.y, self.size.x, self.size.y, False)
            else:
                image(self.game, self.image, self.pos.x, self.pos.y, self.size.x, self.size.y, False)
        else:
            if self.pressed:
                image(self.game, self.pressedImage, self.pos.x + self.size.x / 2, self.pos.y + self.size.y / 2, self.size.x, self.size.y, False)
            else:
                image(self.game, self.image, self.pos.x + self.size.x / 2, self.pos.y + self.size.y / 2, self.size.x, self.size.y, False)

    def rescale(self):
        """Readjusts the button size based on the game window"""
        if self.isScalar:
            self.pos = pygame.Vector2(self.sPos.x * self.game.screen_width, self.sPos.y * self.game.screen_height)
            self.size = pygame.Vector2(self.sSize.x * self.game.screen_width, self.sSize.y * self.game.screen_height)
