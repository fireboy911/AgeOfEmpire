from typing import Dict
from dataclasses import dataclass, field
from Map import MAP_W, MAP_H
from Units import Unit
from Generals import General
from typing import List, Dict
import time
from Engine import SimpleEngine 
from HtmlRapport import generate_snapshot_report
try:
    import curses
    from curses import wrapper
except Exception:
    curses = None

def clamp(v, a, b): return max(a, min(b, v))
FPS = 20
camera_speed = 10.0
class TerminalRenderer:
    def __init__(self, engine: SimpleEngine, generals: Dict[int, General]):
        if curses is None:
            raise RuntimeError("curses not available on this system")
        self.engine = engine
        self.generals = generals
        self.cam_x = max(0, engine.w//2 - 20)
        self.cam_y = max(0, engine.h//2 - 10)
        self.speed_multiplier = 1.0
        self.paused = False
        self.selected_idx = 0
        self.last_time = time.time()

    def unit_char(self, u: Unit) -> str:
        if u.unit_type.lower().startswith('pik'):
            return 'P'
        if u.unit_type.lower().startswith('cross'):
            return 'C'
        if u.unit_type.lower().startswith('knight'):
            return 'K'
        if u.unit_type.lower().startswith('monk'):
            return 'M'
        return '?'

    def draw(self, stdscr):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Sécurité : Si la fenêtre est trop petite, on ne dessine rien pour éviter le crash
        if h < 10 or w < 20:
            try:
                stdscr.addstr(0, 0, "Fenetre trop petite!")
            except:
                pass
            return

        view_w = max(10, w-2)
        view_h = max(6, h-6)

        # 1. DESSIN DU BACKGROUNG (GRILLE)
        # Utilisation de try/except pour éviter le crash si on touche le bord droit
        for yy in range(view_h):
            # Note: Dans votre code précédent, row.append('') ajoutait du vide.
            # Mettons un point '.' pour voir la grille, ou un espace ' ' pour nettoyer.
            row_str = '.' * (view_w - 1) 
            try:
                # On vérifie qu'on ne dépasse pas la hauteur
                if 1 + yy < h - 1: 
                    stdscr.addstr(1+yy, 1, row_str)
            except curses.error:
                pass

        # 2. DESSIN DES UNITÉS
        for u in self.engine.units:
            ux = int(u.x) - int(self.cam_x)
            uy = int(u.y) - int(self.cam_y)
            
            # Vérification stricte des bornes avant de dessiner
            if 0 <= ux < view_w-1 and 0 <= uy < view_h-1:
                ch = self.unit_char(u)
                attr = curses.A_BOLD if u.player == 1 else curses.A_DIM
                
                # Gestion de la sélection
                selected = False
                p1_units = self.engine.get_units_for_player(1)
                if p1_units:
                    # Sécurité index
                    if self.selected_idx >= len(p1_units):
                        self.selected_idx = 0
                    if p1_units[self.selected_idx].id == u.id:
                        attr |= curses.A_REVERSE
                        selected = True
                
                try:
                    # On dessine l'unité (sécurisé)
                    if 1+uy < h-1 and 1+ux < w-1:
                        stdscr.addch(1+uy, 1+ux, ch, attr)
                except curses.error:
                    pass

                # Affichage PV si sélectionné
                if selected:
                    hp_text = f"{int(u.hp)}"
                    try:
                        if 1+ux+len(hp_text) < w-1:
                            stdscr.addstr(1+uy, 1+ux+1, hp_text, curses.A_NORMAL)
                    except curses.error:
                        pass

        # 3. HUD (INTERFACE)
        txt = f"Tick: {self.engine.tick:.0f} Units: {len(self.engine.units)} Speed x{self.speed_multiplier:.1f} {'[PAUSE]' if self.paused else ''}"
        try:
            # On écrit en bas de l'écran, mais pas sur la toute dernière ligne
            if view_h + 2 < h - 1:
                stdscr.addstr(view_h+2, 1, txt[:w-2]) # On coupe si trop long
                stdscr.addstr(view_h+3, 1, "WASD:Cam Tab:Select T:Target P:Pause"[:w-2])
        except curses.error:
            pass
            
        stdscr.refresh()

    # Ajoutez l'import en haut du fichier
   

    # ... dans la classe TerminalRenderer ...

    def handle_input(self, stdscr, dt):
        ch = stdscr.getch()
        if ch == -1: return True

        # Q : Quitter
        if ch in (ord('q'), ord('Q')): return False
        
        # R : Reset
        if ch in (ord('r'), ord('R')): return 'reset'

        # P : Pause
        if ch in (ord('p'), ord('P'), ord(' ')):
            self.paused = not self.paused

        # TAB (Code ASCII 9) : Snapshot HTML + Pause
        if ch == 9: 
            self.paused = True # Le PDF demande de mettre en pause
            generate_snapshot_report(self.engine, self.generals)

        # +/- : Vitesse du jeu
        if ch in (ord('+'), ord('=')): self.speed_multiplier *= 2.0
        if ch in (ord('-'), ord('_')): self.speed_multiplier = max(0.125, self.speed_multiplier/2.0)

        # DEPLACEMENT CAMERA (Scrolling)
        # Shift est géré par les majuscules ('a' vs 'A')
        # Vitesse normale
        move = camera_speed * dt
        # Vitesse rapide (Shift maintenu -> Majuscule)
        fast_move = move * 3.0 

        if ch == ord('a'): self.cam_x -= move
        if ch == ord('A'): self.cam_x -= fast_move # Shift+A
        
        if ch == ord('d'): self.cam_x += move
        if ch == ord('D'): self.cam_x += fast_move # Shift+D
        
        if ch == ord('w'): self.cam_y -= move
        if ch == ord('W'): self.cam_y -= fast_move # Shift+W
        
        if ch == ord('s'): self.cam_y += move
        if ch == ord('S'): self.cam_y += fast_move # Shift+S
        
        # Gestion Flèches (Curses ne détecte pas toujours Shift+Flèche facilement, 
        # on garde vitesse normale pour les flèches simples)
        if ch == curses.KEY_LEFT: self.cam_x -= move
        if ch == curses.KEY_RIGHT: self.cam_x += move
        if ch == curses.KEY_UP: self.cam_y -= move
        if ch == curses.KEY_DOWN: self.cam_y += move

        # Clamp
        self.cam_x = clamp(self.cam_x, 0, max(0, self.engine.w - 1))
        self.cam_y = clamp(self.cam_y, 0, max(0, self.engine.h - 1))

        return True

    def run_curses(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)
        running = True
        last = time.time()
        
        # Variables pour la fin de partie
        game_over = False
        winner = 0

        while running:
            now = time.time()
            dt = now - last
            last = now
            
            inp = self.handle_input(stdscr, dt)
            if inp == 'reset': return 'reset'
            if inp is False: break
            
            # --- LOGIQUE DE JEU ---
            if not self.paused and not game_over:
                sim_dt = dt * self.speed_multiplier
                sim_dt = min(sim_dt, 0.5)
                self.engine.step(sim_dt, self.generals)
                
                # VERIFICATION VICTOIRE
                p1 = self.engine.get_units_for_player(1)
                p2 = self.engine.get_units_for_player(2)
                
                if not p1 and not p2:
                    winner = 0 # Egalité
                    game_over = True
                elif not p2:
                    winner = 1
                    game_over = True
                elif not p1:
                    winner = 2
                    game_over = True

            # --- DESSIN ---
            self.draw(stdscr)
            
            # Affichage du message de fin par dessus
            if game_over:
                h, w = stdscr.getmaxyx()
                msg = f" VICTOIRE JOUEUR {winner} ! (Appuyez sur Q) "
                try:
                    # On centre le message
                    stdscr.addstr(h//2, max(0, w//2 - len(msg)//2), msg, curses.A_REVERSE | curses.A_BOLD)
                except:
                    pass

        return 'quit'

    def run(self):

        return wrapper(self.run_curses)
