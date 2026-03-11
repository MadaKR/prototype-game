import pygame
import cmath
from utils import *

class Entity:
    def __init__(self, game, x, y, texture = None, centered = True):
        self.game = game
        self.pos = pygame.Vector2(x, y)
        self.texture = texture
        self.size = 50
        self.angle = 0
        self.centered = centered

    def update(self):
        return
    
    def draw(self):
        screenPos = self.game.camera.worldToScreen(self.pos)
        if self.texture:
            image(self.game, self.game.textures[self.texture], screenPos.x, screenPos.y, self.size, self.size, True, -self.game.camera.angle)

class Decoration(Entity):
    """Static parts of a level with no collision."""
    def __init__(self, game, x, y, texture: str):
        super().__init__(game, x, y, texture)

    def draw(self):
        screenPos = self.game.camera.worldToScreen(self.pos)
        if self.texture:
            self.size = pygame.Vector2(self.game.textures[self.texture].get_size())
            image(self.game, self.game.textures[self.texture], screenPos.x, screenPos.y, None, None, True, self.game.camera.angle)

class ParallaxEntity(Entity):
    """
    Parallaxed textures that show 'underneath' the level

    Args:
        parallaxAmt (float): 0 = 'Closer', 1 = 'Farther'
    """
    def __init__(self, game, x, y, texture: str, parallaxAmt: float):
        super().__init__(game, x, y, texture)
        self.parallaxAmt = parallaxAmt
    
    def draw(self):
        screenPos = self.game.camera.worldToScreen(self.pos.lerp(self.game.camera.pos, self.parallaxAmt))
        if self.texture:
            self.size = pygame.Vector2(self.game.textures[self.texture].get_size())
        else:
            return
        tilesX = math.ceil(((self.game.screen_width / self.size.x) + 1) / 2)
        offsetX = math.ceil((1 - self.parallaxAmt) * self.game.camera.pos.x / self.size.x)
        tilesY = math.ceil(((self.game.screen_height / self.size.y) + 1) / 2)
        offsetY = math.ceil((1 - self.parallaxAmt) * self.game.camera.pos.y / self.size.y)
        for x in range(-tilesX + offsetX, tilesX + offsetX):
            for y in range(-tilesY + offsetY, tilesY + offsetY):
                image(self.game, self.game.textures[self.texture], 
                      screenPos.x + x * self.size.x,
                      screenPos.y + y * self.size.y,
                      self.size.x, self.size.y)

class Player(Entity):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)

        # Position/movement properties
        self.vel = pygame.Vector2(0, 0)
        self.angle = 0
        self.turnSpeed = 0.2
        self.accelValue = 0.0005
        self.friction = 0.07

        # Rendering properties
        self.texture = 'player'
        self.size = 50

    def update(self):
        self.pos += self.vel * self.game.dt

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.angle += self.turnSpeed * self.game.dt
        if keys[pygame.K_a]:
            self.angle -= self.turnSpeed * self.game.dt

        forward = pygame.Vector2(0, -1).rotate(-self.angle)
        perpendicular = pygame.Vector2(-forward.y, forward.x)
        frictionMag = self.vel.dot(perpendicular) * self.friction
        frictionVec = -self.friction * perpendicular * frictionMag
        self.vel += frictionVec * self.game.dt

        if keys[pygame.K_w]:
            self.vel += forward * self.accelValue * self.game.dt
        if keys[pygame.K_s]:
            self.vel -= forward * self.accelValue * self.game.dt