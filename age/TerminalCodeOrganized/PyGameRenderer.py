import pygame
from typing import Dict, Tuple
from Engine import SimpleEngine
from Generals import General
from Units import Unit
from Map import TILE_SIZE, MAP_W, MAP_H
import os
import math
SCREEN_W, SCREEN_H = 960, 640
FPS = 60
camera_speed = 10.0

def clamp(v, a, b): return max(a, min(b, v))
class PygameRenderer:
    def __init__(self, engine: SimpleEngine, generals: Dict[int, General]):
        if pygame is None:
            raise RuntimeError("Pygame not installed.")
        pygame.init()
        self.engine = engine
        self.generals = generals
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("MedievAIl prototype")
        self.clock = pygame.time.Clock()
        self.cam_x = max(0, engine.w//2 - (SCREEN_W // TILE_SIZE)//2)
        self.cam_y = max(0, engine.h//2 - (SCREEN_H // TILE_SIZE)//2)
        self.speed_multiplier = 1.0
        self.paused = False
        self.show_minimap = True
        
        # Load textures
        self.load_textures()

    def load_textures(self):
        """Load all terrain and unit textures"""
        assets_path = os.path.join(os.path.dirname(__file__), 'assets')
        
        # Load terrain textures
        self.terrain_textures = []
        try:
            grass1 = pygame.image.load(os.path.join(assets_path, 'terrain', 'grass1.png'))
            grass2 = pygame.image.load(os.path.join(assets_path, 'terrain', 'grass2.png'))
            self.terrain_textures = [
                pygame.transform.scale(grass1, (TILE_SIZE, TILE_SIZE)),
                pygame.transform.scale(grass2, (TILE_SIZE, TILE_SIZE))
            ]
        except Exception as e:
            print(f"Warning: Could not load terrain textures: {e}")
            self.terrain_textures = None
        
        # Load unit textures: {(unit_type, player, direction): surface}
        self.unit_textures = {}
        unit_types = ['Pikeman', 'Crossbowman', 'Knight', 'Long_Swordman']
        colors = {1: 'red', 2: 'blue'}
        directions = ['up', 'down', 'left', 'right']
        
        for unit_type in unit_types:
            for player, color in colors.items():
                for direction in directions:
                    try:
                        path = os.path.join(assets_path, 'units', unit_type, color, f'{direction}.png')
                        img = pygame.image.load(path)
                        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                        self.unit_textures[(unit_type, player, direction)] = img
                    except Exception as e:
                        print(f"Warning: Could not load {unit_type}/{color}/{direction}: {e}")
        
        # Also handle Monk (if images exist)
        for player, color in colors.items():
            for direction in directions:
                try:
                    path = os.path.join(assets_path, 'units', 'Monk', color, f'{direction}.png')
                    if os.path.exists(path):
                        img = pygame.image.load(path)
                        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                        self.unit_textures[('Monk', player, direction)] = img
                except:
                    pass

    def get_unit_direction(self, unit: Unit) -> str:
        """Determine which direction the unit is facing based on target or last movement"""
        if not hasattr(unit, 'last_x'):
            unit.last_x = unit.x
            unit.last_y = unit.y
        
        # Calculate direction based on target
        target = None
        if unit.target_id and unit.target_id in self.engine.units_by_id:
            target = self.engine.units_by_id[unit.target_id]
        
        if target:
            dx = target.x - unit.x
            dy = target.y - unit.y
        else:
            dx = unit.x - unit.last_x
            dy = unit.y - unit.last_y
        
        # Store current position for next frame
        unit.last_x = unit.x
        unit.last_y = unit.y
        
        # Determine direction based on angle
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'

    def world_to_screen(self, wx, wy) -> Tuple[int,int]:
        sx = int((wx - self.cam_x) * TILE_SIZE)
        sy = int((wy - self.cam_y) * TILE_SIZE)
        return sx, sy

    def draw(self):
        cols = SCREEN_W // TILE_SIZE + 2
        rows = SCREEN_H // TILE_SIZE + 2
        
        # Draw terrain
        for i in range(cols):
            for j in range(rows):
                tx = self.cam_x + i
                ty = self.cam_y + j
                
                if tx < 0 or ty < 0 or tx >= self.engine.w or ty >= self.engine.h:
                    # Out of bounds - draw grey
                    color = (50,50,50)
                    pygame.draw.rect(self.screen, color, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE+1, TILE_SIZE+1))
                elif self.terrain_textures:
                    # Use only grass1 texture for all tiles
                    self.screen.blit(self.terrain_textures[0], (i*TILE_SIZE, j*TILE_SIZE))
                else:
                    # Fallback to colored rectangles
                    color = (34,139,34) if (int(tx)+int(ty))%2==0 else (40,120,40)
                    pygame.draw.rect(self.screen, color, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE+1, TILE_SIZE+1))
        
        # Draw units
        for u in self.engine.units:
            sx, sy = self.world_to_screen(u.x, u.y)
            
            # Get unit type (normalize name)
            unit_type = u.unit_type
            if unit_type.lower().startswith('pik'):
                unit_type = 'Pikeman'
            elif unit_type.lower().startswith('cross'):
                unit_type = 'Crossbowman'
            elif unit_type.lower().startswith('knight'):
                unit_type = 'Knight'
            elif unit_type.lower().startswith('monk'):
                unit_type = 'Monk'
            
            # Get direction
            direction = self.get_unit_direction(u)
            
            # Try to use texture, fallback to circle
            texture_key = (unit_type, u.player, direction)
            if texture_key in self.unit_textures:
                self.screen.blit(self.unit_textures[texture_key], (sx, sy))
            else:
                # Fallback to colored circle
                col = u.color
                r = int(TILE_SIZE*0.4)
                pygame.draw.circle(self.screen, col, (sx+TILE_SIZE//2, sy+TILE_SIZE//2), r)
            
            # Draw HP bar
            hp_frac = clamp(u.hp / 55.0, 0.0, 1.0)
            bar_w = int(TILE_SIZE * hp_frac)
            pygame.draw.rect(self.screen, (0,0,0), (sx, sy-6, TILE_SIZE, 4))
            pygame.draw.rect(self.screen, (0,255,0), (sx, sy-6, bar_w, 4))
        
        # Draw HUD
        font = pygame.font.SysFont(None, 20)
        txt = f"Tick: {self.engine.tick:.2f}  Units: {len(self.engine.units)}  Speed x{self.speed_multiplier:.1f}"
        surf = font.render(txt, True, (255,255,255))
        self.screen.blit(surf, (8,8))
        if self.show_minimap:
            mm_w, mm_h = 200,200
            mm_surf = pygame.Surface((mm_w, mm_h))
            mm_surf.fill((20,20,20))
            scale_x = mm_w / self.engine.w
            scale_y = mm_h / self.engine.h
            for u in self.engine.units:
                ux = int(u.x*scale_x)
                uy = int(u.y*scale_y)
                c = (255,50,50) if u.player==1 else (50,50,255)
                mm_surf.fill(c, (ux, uy, 2,2))
            self.screen.blit(mm_surf, (SCREEN_W - mm_w - 8, 8))
        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time()/1000.0
        move_speed = camera_speed * dt * (1 + self.speed_multiplier)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.cam_x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.cam_x += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.cam_y -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.cam_y += move_speed
        self.cam_x = clamp(self.cam_x, 0, max(0, self.engine.w - SCREEN_W//TILE_SIZE))
        self.cam_y = clamp(self.cam_y, 0, max(0, self.engine.h - SCREEN_H//TILE_SIZE))

    def run(self):
        running = True
        while running:
            dt_real = self.clock.tick(FPS)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    elif event.key == pygame.K_p: self.paused = not self.paused
                    elif event.key == pygame.K_m: self.show_minimap = not self.show_minimap
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS): self.speed_multiplier *= 2.0
                    elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE): self.speed_multiplier = max(0.125, self.speed_multiplier/2.0)
            self.handle_input()
            if not self.paused:
                sim_dt = dt_real * self.speed_multiplier
                sim_dt = min(sim_dt, 0.5)
                self.engine.step(sim_dt, self.generals)
            self.screen.fill((0,0,0))
            self.draw()
        pygame.quit()