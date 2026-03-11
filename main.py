import pygame

from utils import *
from entities import *

# ---------------------------------------------------------------------------------------------------- #

class Camera:
    def __init__(self, game):
        self.game = game
        self.pos = pygame.Vector2(0, 0)
        self.followSpeed = 0.01
        self.angle = game.player.angle
        self.update()
    
    def update(self):
        self.offset = pygame.Vector2(-(self.game.screen_width / 2), -(self.game.screen_height / 2))
        followOffset = self.pos - self.game.player.pos
        self.pos = self.pos - followOffset * self.followSpeed * self.game.dt

        #angleOffset = self.angle - self.game.player.angle
        #self.angle -= angleOffset * self.followSpeed * self.game.dt
        self.angle = self.game.player.angle

    def worldToScreen(self, pos):
        """Converts a world-space coordinate vector to screen-space coordinates."""
        rel = pos - self.pos          # world -> camera space
        rel = rel.rotate(-self.angle) # rotate around camera
        return rel - self.offset      # camera -> screen

# ---------------------------------------------------------------------------------------------------- #
# Main game object

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)

        # Game window
        self.fullscreen = False
        self.screen_width = 1280
        self.screen_height = 720
        self.screen_surface = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Prototype")
        
        # Game assets
        self.textures = {}
        self.sounds = {}
        loadAssets(self) # Populate game asset properties from \assets directory

        # States
        self.running = True
        self.state = menuState(self)
        self.dt = 1 # deltaTime

        # Player object
        self.player = Player(self, 0, 0)
        # Camera object
        self.camera = Camera(self)

    def changeState(self, newState):
        self.sounds['click1'].play()
        self.state = newState(self)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            # Time
            self.dt = clock.tick()

            # Handle window events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.scancode == 68:
                        self.toggleFullscreen()
                        continue
                if event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen_width = event.w
                    self.screen_height = event.h
                    self.screen_surface = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                    if hasattr(self.state, 'uiElements'):
                        for element in self.state.uiElements:
                            element.rescale()

            # Game loop
            self.state.update(events)
            self.state.draw()
            pygame.display.flip()
            #print(clock.get_fps())

    def toggleFullscreen(self):
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            self.screen_width = pygame.display.get_desktop_sizes()[0][0]
            self.screen_height = pygame.display.get_desktop_sizes()[0][1]
            self.screen_surface = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE | pygame.FULLSCREEN)
        else:
            self.screen_width = 1280
            self.screen_height = 720
            self.screen_surface = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

        if hasattr(self.state, 'uiElements'):
            for element in self.state.uiElements:
                element.rescale()

# ---------------------------------------------------------------------------------------------------- #
# Game state classes

class gameState:
    def __init__(self, game):
        self.game = game

        self.level = Level1(game)

    def getInput(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.changeState(menuState)
        return

    def update(self, events):
        self.getInput(events)
        self.level.update()
        self.game.camera.update()
        self.game.player.update()

    def draw(self):
        background(self.game, color('#013501'))
        self.level.draw()
        self.game.player.draw()

class menuState:
    def __init__(self, game):
        self.game = game
        self.uiElements = [
            Button(self.game, 0.5, 0.8, 0.15, 0.05, lambda: self.game.changeState(gameState), "play_button", "play_button_pressed", True)
        ]

    def getInput(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 or event.button == 5:
                    self.game.sounds['scroll'].play()

    def update(self, events):
        self.getInput(events)

        for element in self.uiElements:
            element.update()

    def draw(self):
        image(self.game, self.game.textures['menu_background'], self.game.screen_width / 2, self.game.screen_height / 2, self.game.screen_width, self.game.screen_height)

        for element in self.uiElements:
            element.draw()

# ---------------------------------------------------------------------------------------------------- #
# Level classes

class Level1:
    def __init__(self, game):
        self.game = game
        self.parallaxBackground = ParallaxEntity(self.game, 0, 0, 'space', 0.7)
        self.floor = Decoration(self.game, 0, 0, 'track1')

    def update(self):
        return
    
    def draw(self):
        self.parallaxBackground.draw()
        self.floor.draw()

# ---------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    game = Game()
    game.run()