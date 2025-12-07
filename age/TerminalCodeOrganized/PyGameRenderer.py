import pygame
from typing import Dict, Tuple
from Engine import SimpleEngine
from Generals import General
from Map import TILE_SIZE
from HtmlRapport import generate_snapshot_report

# Constantes d'affichage
SCREEN_W, SCREEN_H = 960, 640
FPS = 60
CAMERA_SPEED = 10.0

def clamp(v, a, b): 
    return max(a, min(b, v))

class PygameRenderer:
    def __init__(self, engine: SimpleEngine, generals: Dict[int, General]):
        if pygame is None:
            raise RuntimeError("Pygame not installed.")
        pygame.init()
        
        self.engine = engine
        self.generals = generals
        
        # Configuration de la fenêtre
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("MedievAIl - Projet Python")
        self.clock = pygame.time.Clock()
        
        # Caméra centrée au départ
        self.cam_x = max(0, engine.w//2 - (SCREEN_W // TILE_SIZE)//2)
        self.cam_y = max(0, engine.h//2 - (SCREEN_H // TILE_SIZE)//2)
        
        # État du jeu
        self.speed_multiplier = 1.0
        self.paused = False
        self.show_minimap = True

    def world_to_screen(self, wx, wy) -> Tuple[int,int]:
        """Convertit les coordonnées du monde (grille) en pixels écran."""
        sx = int((wx - self.cam_x) * TILE_SIZE)
        sy = int((wy - self.cam_y) * TILE_SIZE)
        return sx, sy

    def draw_game_over(self, winner_id):
        """Affiche l'écran de fin de partie par-dessus le jeu."""
        # Fond semi-transparent
        s = pygame.Surface((SCREEN_W, SCREEN_H))
        s.set_alpha(128)
        s.fill((0,0,0))
        self.screen.blit(s, (0,0))
        
        # Texte de victoire
        font = pygame.font.SysFont(None, 72)
        if winner_id == 0:
            txt = "EGALITE / TIMEOUT"
            color = (200, 200, 200)
        else:
            txt = f"VICTOIRE JOUEUR {winner_id} !"
            color = (255, 50, 50) if winner_id == 1 else (50, 50, 255)
            
        text_surf = font.render(txt, True, color)
        text_rect = text_surf.get_rect(center=(SCREEN_W/2, SCREEN_H/2))
        self.screen.blit(text_surf, text_rect)
        
        # Instructions
        font_small = pygame.font.SysFont(None, 36)
        help_surf = font_small.render("Appuyez sur ESC pour quitter", True, (255, 255, 255))
        help_rect = help_surf.get_rect(center=(SCREEN_W/2, SCREEN_H/2 + 60))
        self.screen.blit(help_surf, help_rect)

    def draw(self):
        """Dessine la carte, les unités et l'interface (HUD)."""
        # 1. DESSIN DE LA CARTE (Optimisé pour ne dessiner que ce qui est visible)
        cols = SCREEN_W // TILE_SIZE + 2
        rows = SCREEN_H // TILE_SIZE + 2
        
        for i in range(cols):
            for j in range(rows):
                tx = self.cam_x + i
                ty = self.cam_y + j
                
                # Couleur du sol (damier)
                if tx < 0 or ty < 0 or tx >= self.engine.w or ty >= self.engine.h:
                    color = (20, 20, 20) # Hors limites
                else:
                    color = (34, 139, 34) if (int(tx)+int(ty)) % 2 == 0 else (40, 120, 40)
                
                pygame.draw.rect(self.screen, color, 
                               (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE+1, TILE_SIZE+1))

        # 2. DESSIN DES UNITÉS
        for u in self.engine.units:
            # On ne dessine que les vivants
            if not u.alive: continue
            
            sx, sy = self.world_to_screen(u.x, u.y)
            
            # Optimisation : ne pas dessiner si hors écran
            if -TILE_SIZE < sx < SCREEN_W and -TILE_SIZE < sy < SCREEN_H:
                col = u.color
                r = int(TILE_SIZE * 0.4)
                
                # Corps de l'unité
                pygame.draw.circle(self.screen, col, (sx+TILE_SIZE//2, sy+TILE_SIZE//2), r)
                
                # Barre de vie
                hp_frac = clamp(u.hp / 55.0, 0.0, 1.0) # 55 est une base arbitraire pour l'échelle
                bar_w = int(TILE_SIZE * hp_frac)
                
                # Fond barre rouge, vie verte
                pygame.draw.rect(self.screen, (200,0,0), (sx, sy-6, TILE_SIZE, 4))
                pygame.draw.rect(self.screen, (0,255,0), (sx, sy-6, bar_w, 4))

        # 3. INTERFACE (HUD)
        font = pygame.font.SysFont(None, 24)
        status_txt = f"Tick: {self.engine.tick:.1f} | Units: {len(self.engine.units)} | Speed: x{self.speed_multiplier:.1f}"
        if self.paused: status_txt += " [PAUSE]"
        
        surf = font.render(status_txt, True, (255, 255, 255))
        # Fond noir sous le texte pour lisibilité
        bg_rect = surf.get_rect(topleft=(8,8))
        pygame.draw.rect(self.screen, (0,0,0, 180), bg_rect.inflate(10, 10)) 
        self.screen.blit(surf, (8,8))

        # 4. MINIMAP
        if self.show_minimap:
            mm_w, mm_h = 200, 200
            mm_surf = pygame.Surface((mm_w, mm_h))
            mm_surf.set_alpha(200)
            mm_surf.fill((30, 30, 30))
            
            scale_x = mm_w / self.engine.w
            scale_y = mm_h / self.engine.h
            
            for u in self.engine.units:
                if u.alive:
                    ux = int(u.x * scale_x)
                    uy = int(u.y * scale_y)
                    c = (255, 50, 50) if u.player == 1 else (50, 50, 255)
                    pygame.draw.rect(mm_surf, c, (ux, uy, 3, 3))
            
            # Cadre caméra sur minimap
            cam_rect_x = int(self.cam_x * scale_x)
            cam_rect_y = int(self.cam_y * scale_y)
            cam_rect_w = int((SCREEN_W/TILE_SIZE) * scale_x)
            cam_rect_h = int((SCREEN_H/TILE_SIZE) * scale_y)
            pygame.draw.rect(mm_surf, (255, 255, 255), (cam_rect_x, cam_rect_y, cam_rect_w, cam_rect_h), 1)

            self.screen.blit(mm_surf, (SCREEN_W - mm_w - 10, 10))

    def handle_input(self):
        """Gestion des déplacements continus (Caméra)."""
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time() / 1000.0
        
        # Gestion du Shift pour aller plus vite (x3)
        current_cam_speed = CAMERA_SPEED
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            current_cam_speed *= 3.0

        move = current_cam_speed * dt * (1 + self.speed_multiplier) # La caméra s'adapte aussi à la vitesse de jeu
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.cam_x -= move
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.cam_x += move
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.cam_y -= move
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.cam_y += move
        
        # On empêche la caméra de sortir de la carte
        self.cam_x = clamp(self.cam_x, 0, max(0, self.engine.w - SCREEN_W//TILE_SIZE))
        self.cam_y = clamp(self.cam_y, 0, max(0, self.engine.h - SCREEN_H//TILE_SIZE))

    def run(self):
        running = True
        game_over = False
        winner = 0

        while running:
            dt_real = self.clock.tick(FPS) / 1000.0
            
            # --- 1. GESTION DES EVENEMENTS (Touches uniques) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # ESC : Quitter
                    if event.key == pygame.K_ESCAPE: 
                        running = False
                    
                    # P : Pause
                    elif event.key == pygame.K_p: 
                        self.paused = not self.paused
                    
                    # TAB : Snapshot HTML + Pause (Requis PDF)
                    elif event.key == pygame.K_TAB:
                        self.paused = True
                        generate_snapshot_report(self.engine, self.generals)
                    
                    # M : Minimap
                    elif event.key == pygame.K_m: 
                        self.show_minimap = not self.show_minimap
                    
                    # Vitesse Jeu (+/-)
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS): 
                        self.speed_multiplier *= 2.0
                    elif event.key in (pygame.K_MINUS, pygame.K_6, pygame.K_KP_MINUS): 
                        self.speed_multiplier = max(0.125, self.speed_multiplier/2.0)
            
            # --- 2. GESTION DES ENTREES CONTINUES (Caméra) ---
            self.handle_input()

            # --- 3. LOGIQUE DU JEU ---
            if not self.paused and not game_over:
                # Simulation physique
                sim_dt = dt_real * self.speed_multiplier
                sim_dt = min(sim_dt, 0.5) # Cap pour éviter les sauts temporels
                self.engine.step(sim_dt, self.generals)
                
                # Vérification de Victoire
                p1 = self.engine.get_units_for_player(1)
                p2 = self.engine.get_units_for_player(2)
                
                if not p1 and not p2:
                    winner = 0 # Egalité (rare)
                    game_over = True
                elif not p2:
                    winner = 1
                    game_over = True
                elif not p1:
                    winner = 2
                    game_over = True

            # --- 4. DESSIN ---
            self.screen.fill((0,0,0))
            self.draw()
            
            if game_over:
                self.draw_game_over(winner)
            
            pygame.display.flip()

        pygame.quit()