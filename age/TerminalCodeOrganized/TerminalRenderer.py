from typing import Dict
from dataclasses import dataclass, field
from Map import MAP_W, MAP_H
from Units import Unit
from Generals import General
from typing import List, Dict
import time
from Engine import SimpleEngine
from GameState import GameStateManager
from DebugInfo import DebugInfoGenerator
try:
    import curses
    from curses import wrapper
except Exception:
    curses = None
import os
os.environ.setdefault('ESCDELAY', '25')

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
        
        # Game state management
        self.state_manager = GameStateManager()
        self.debug_generator = DebugInfoGenerator()

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
        view_w = max(10, w-2)
        view_h = max(6, h-6)

        # draw grid background (simple dots)
        for yy in range(view_h):
            row = []
            for xx in range(view_w):
                row.append('')
            stdscr.addstr(1+yy, 1, ''.join(row))

        # draw units
        for u in self.engine.units:
            ux = int(u.x) - int(self.cam_x)
            uy = int(u.y) - int(self.cam_y)
            if 0 <= ux < view_w and 0 <= uy < view_h:
                ch = self.unit_char(u)
                if u.player == 1:
                    attr = curses.A_BOLD
                else:
                    attr = curses.A_DIM
                # highlight selected
                selected = False
                if self.engine.get_units_for_player(1):
                    my_units = self.engine.get_units_for_player(1)
                    if 0 <= self.selected_idx < len(my_units) and my_units[self.selected_idx].id == u.id:
                        attr |= curses.A_REVERSE
                        selected = True
                try:
                    stdscr.addch(1+uy, 1+ux, ch, attr)
                except curses.error:
                    pass
                # draw tiny hp above if selected
                if selected:
                    hp_text = f"{int(u.hp)}/{int(55)}"
                    try:
                        stdscr.addstr(0, 1, hp_text)
                    except curses.error:
                        pass

        # HUD
        txt = f"Tick: {self.engine.tick:.2f} Units: {len(self.engine.units)} Speed x{self.speed_multiplier:.2f} {'PAUSED' if self.paused else ''}"
        try:
            stdscr.addstr(view_h+2, 1, txt)
            stdscr.addstr(view_h+3, 1, "ZQSD/Arrows:Move Shift+Move:Fast Tab:Debug P:Pause +/-:Speed F9:Switch F11:Save F12:Load")
            stdscr.addstr(view_h+4, 1, "t:Target r:Reset esc:Quit")
        except curses.error:
            pass
        stdscr.refresh()

    def handle_input(self, stdscr, dt):
        ch = stdscr.getch()
        if ch == -1:
            return True
        
        # Check for Shift modifier (not directly available in curses, so use fast scroll with capital letters)
        fast_scroll = 3.0
        
        # esc - Quit
        if ch == 27:
            return False
        
        # P or Space - Pause
        if ch in (ord('p'), ord('P'), ord(' ')):
            self.paused = not self.paused
        
        # +/= - Increase speed
        if ch in (ord('+'), ord('=')):
            self.speed_multiplier = min(self.speed_multiplier * 2.0, 16.0)
        
        # - - Decrease speed
        if ch in (ord('-'), ord('_')):
            self.speed_multiplier = max(self.speed_multiplier / 2.0, 0.125)
        
        # Tab - Debug info (now generates HTML)
        if ch == 9:  # Tab key
            try:
                filepath = self.debug_generator.generate_html(self.engine, self.generals)
                # Can't easily show message in curses, will show in console
            except Exception as e:
                pass
        
        # T - Target nearest enemy (for selected unit)
        if ch in (ord('t'), ord('T')):
            my_units = self.engine.get_units_for_player(1)
            if my_units and self.selected_idx < len(my_units):
                su = my_units[self.selected_idx]
                enemies = [e for e in self.engine.units if e.player != 1 and e.alive]
                if enemies:
                    nearest = min(enemies, key=lambda e: su.distance_to(e))
                    su.target_id = nearest.id
        
        # R - Reset
        if ch in (ord('r'), ord('R')):
            return 'reset'
        
        # F9 - Switch to PyGame view
        if ch == curses.KEY_F9:
            return 'switch_pygame'
        
        # F11 - Quick Save
        if ch == curses.KEY_F11:
            try:
                if self.state_manager.quick_save(self.engine, self.generals):
                    pass  # Saved successfully
            except Exception as e:
                pass
        
        # F12 - Quick Load
        if ch == curses.KEY_F12:
            try:
                state = self.state_manager.quick_load()
                if state:
                    self.state_manager.restore_engine(state, self.engine)
                    self.generals = self.state_manager.restore_generals(state)
            except Exception as e:
                pass
        
        # Camera panning - ZQSD + Arrow keys
        # Capital letters for fast scroll
        move_speed = camera_speed * dt
        
        if ch in (curses.KEY_LEFT, ord('a'), ord('A'), ord('q'), ord('Q')):
            speed = move_speed * (fast_scroll if ch == ord('A') or ch == ord('Q') else 1.0)
            self.cam_x = clamp(self.cam_x - speed, 0, max(0, self.engine.w - 1))
        
        if ch in (curses.KEY_RIGHT, ord('d'), ord('D')):
            speed = move_speed * (fast_scroll if ch == ord('D') else 1.0)
            self.cam_x = clamp(self.cam_x + speed, 0, max(0, self.engine.w - 1))
        
        if ch in (curses.KEY_UP, ord('w'), ord('W'), ord('z'), ord('Z')):
            speed = move_speed * (fast_scroll if ch in (ord('W'), ord('Z')) else 1.0)
            self.cam_y = clamp(self.cam_y - speed, 0, max(0, self.engine.h - 1))
        
        if ch in (curses.KEY_DOWN, ord('s'), ord('S')):
            speed = move_speed * (fast_scroll if ch == ord('S') else 1.0)
            self.cam_y = clamp(self.cam_y + speed, 0, max(0, self.engine.h - 1))
        
        return True

    def run_curses(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)
        running = True
        last = time.time()
        while running:
            now = time.time()
            dt = now - last
            last = now
            inp = self.handle_input(stdscr, dt)
            if inp == 'reset':
                return 'reset'
            if inp == 'switch_pygame':
                return 'switch_pygame'
            if inp is False:
                break
            if not self.paused:
                sim_dt = dt * self.speed_multiplier
                sim_dt = min(sim_dt, 0.5)
                self.engine.step(sim_dt, self.generals)
            self.draw(stdscr)
        return 'quit'

    def run(self):
        return wrapper(self.run_curses)

