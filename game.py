import pygame
import sys
import random
from scripts.entities import PhysicsEntity, Player
from scripts.utilites import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle

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

        self.menu_active = True  # Om sann: Visar menyn

        original_background = load_image('background.png')
        meny_background = load_image('meny_background.png')

        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player' : load_image('entities/player.png'),
            'background': pygame.transform.scale(original_background, (1920, 1080)),
            'meny_background': pygame.transform.scale(meny_background,(480, 270)),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump'), img_dur=6),
            'player/slide': Animation(load_images('entities/player/slide'), img_dur=6),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=6),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=10, loop=False)
        }
        
        
        self.setup_menu()
    
    def init_game(self):
        pygame.init()
        pygame.display.set_caption("Island of Runes")
        
        self.screen = pygame.display.set_mode((1920, 1080))
        self.display = pygame.Surface((480, 270))
        
        self.clock = pygame.time.Clock()
        
        self.menu_active = True 
        self.setup_menu()
        
        self.movement = [False, False]
        
        self.menu_active = False

        self.clouds = Clouds(self.assets['clouds'], count = 10)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self)
        self.tilemap.load('map.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13)) # Offsets spawn locationen för löven så dom ej spawnar i top-left hörnet
        
        self.particles = []
        self.scroll = [0, 0]
        self.dead = 0
        
    def setup_menu(self):
        self.menu_font = pygame.font.Font('data/fonts/NorseBold-2Kge.ttf', 24) # Byter fonten i main-menyn
        self.menu_options = ["Start", "Options", "Exit"]
        self.selected_option = 0   
        
         # Load and scale the logo image
        self.logo = pygame.transform.scale(load_image('logo.png'), (150, 150))
        
    def handle_menu_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.selected_option == 0:
                        self.menu_active = False 
                        self.init_game()
                    elif self.selected_option == 1:
                        pass  # Lägg till kod för options här     
                    elif self.selected_option == 2:
                            pygame.quit()
                            sys.exit()

                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)

    # Ritar start menyn
    def draw_menu(self):
        self.display.fill((140, 140, 140)) 
        
        self.display.blit(self.assets['meny_background'], (0, 0))
        
        # Ritar logon
        logo_rect = self.logo.get_rect(center=(self.display.get_width() / 2, 75))
        self.display.blit(self.logo, logo_rect)
        
        option_spacing = 25  # Ändra tomrummet 

        for i, option in enumerate(self.menu_options):
            color = pure_red if i == self.selected_option else pure_white
            
            text_surface = self.menu_font.render(option, True, color)
            text_width, text_height = text_surface.get_size()
            
            text_rect = text_surface.get_rect(center=(self.display.get_width() / 2, 175 + i * option_spacing))
            text_rect.height = text_height + 10
            
            # Adjust the width to ensure the full text is visible
            text_rect.width = text_width + 20  # Adjust the padding as needed
        
            self.display.blit(text_surface, text_rect)

        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
        pygame.display.update()
        self.clock.tick(60)

    def run(self):
        while True:
            if self.menu_active:
                self.handle_menu_input()
                self.draw_menu()
            else:
                self.run_game()

    def run_game(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height: # 49999 är delay för spawnraten, utan den hade löv spawnat varje tick
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() *rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame = random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display, offset = render_scroll)
            
            self.tilemap.render(self.display, offset = render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0)) 
            self.player.render(self.display, offset = render_scroll)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if kill:
                    self.particles.remove(particle)
            
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
                        self.player.jump()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()

      
    