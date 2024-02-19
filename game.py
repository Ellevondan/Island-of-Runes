import pygame
import sys
from scripts.entities import PhysicsEntity
from scripts.utilites import load_image, load_images
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds

# Färger (Red, Green, Blue)
sky_blue = (14, 219 ,248)


pure_white = (255, 255, 255)
pure_black = (0, 0, 0)
pure_green = (0, 255, 0)
pure_red = (255, 0, 0)
pure_blue = (0, 0, 255)

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Island of Runes")
        
        self.screen = pygame.display.set_mode((1920, 1080))
        self.display = pygame.Surface((480, 270))
        
        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        original_background = load_image('background.png')
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player' : load_image('entities/player.png'),
            'background': pygame.transform.scale(original_background, (1920, 1080)),
            'clouds': load_images('clouds')
        }
        
        self.clouds = Clouds(self.assets['clouds'], count = 10)
        
        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self)
        
        self.scroll = [0, 0]
        
        
        
    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.clouds.update()
            self.clouds.render(self.display, offset = render_scroll)
            
            self.tilemap.render(self.display, offset = render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0)) 
            self.player.render(self.display, offset = render_scroll)
 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        self.player.velocity[1] = -3

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()
            
      
    