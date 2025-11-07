# -------------------------
# Pygame renderer (optional)
# -------------------------

from battletest3 import *
from functions import *
from classes import *

import argparse
import random
import math
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

import pygame


# ---------- CONFIG ----------
TILE_SIZE = 24         # pixels per tile in GUI
SCREEN_W, SCREEN_H = 960, 640
MAP_W, MAP_H = 120, 120
FPS = 60
camera_speed = 8.0     # tiles per second
# ---------------------------

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

    def world_to_screen(self, wx, wy) -> Tuple[int,int]:
        sx = int((wx - self.cam_x) * TILE_SIZE)
        sy = int((wy - self.cam_y) * TILE_SIZE)
        return sx, sy

    def draw(self):
        cols = SCREEN_W // TILE_SIZE + 2
        rows = SCREEN_H // TILE_SIZE + 2
        for i in range(cols):
            for j in range(rows):
                tx = self.cam_x + i
                ty = self.cam_y + j
                if tx < 0 or ty < 0 or tx >= self.engine.w or ty >= self.engine.h:
                    color = (50,50,50)
                else:
                    color = (34,139,34) if (int(tx)+int(ty))%2==0 else (40,120,40)
                pygame.draw.rect(self.screen, color, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE+1, TILE_SIZE+1))
        for u in self.engine.units:
            sx, sy = self.world_to_screen(u.x, u.y)
            col = u.color
            r = int(TILE_SIZE*0.4)
            pygame.draw.circle(self.screen, col, (sx+TILE_SIZE//2, sy+TILE_SIZE//2), r)
            hp_frac = clamp(u.hp / 55.0, 0.0, 1.0)
            bar_w = int(TILE_SIZE * hp_frac)
            pygame.draw.rect(self.screen, (0,0,0), (sx, sy-6, TILE_SIZE, 4))
            pygame.draw.rect(self.screen, (0,255,0), (sx, sy-6, bar_w, 4))
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
