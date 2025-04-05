import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
import numpy as np
from PIL import Image
import io
import time

class BinGraphics:
    def __init__(self):
        pygame.init()
        self.WIDTH = 400
        self.HEIGHT = 500
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Enhanced colors with shading
        self.BG_COLOR = (240, 240, 240)
        self.BIN_COLOR = (180, 180, 180)
        self.BIN_HIGHLIGHT = (220, 220, 220)
        self.BIN_SHADOW = (140, 140, 140)
        self.RED_BIN = (220, 160, 160)
        self.RED_BIN_HIGHLIGHT = (255, 200, 200)
        self.RED_BIN_SHADOW = (180, 120, 120)
        self.GREEN_BIN = (160, 220, 160)
        self.GREEN_BIN_HIGHLIGHT = (200, 255, 200)
        self.GREEN_BIN_SHADOW = (120, 180, 120)
        
        # Enhanced bin dimensions with perspective
        self.bin_rect = pygame.Rect(50, 150, 300, 300)
        self.bin_depth = 40  # 3D depth effect
        self.divider = (self.bin_rect.centerx, self.bin_rect.top, 2, self.bin_rect.height)
        
        # Add lid properties
        self.lid_angle = 0
        self.lid_rect = pygame.Rect(self.bin_rect.left, self.bin_rect.top - 20, self.bin_rect.width, 20)
        self.lid_color = (160, 160, 160)
        self.lid_highlight = (200, 200, 200)

    def draw_bin(self, biomedical_level, general_level):
        self.surface.fill(self.BG_COLOR)
        
        # Warning light with glow effect
        if biomedical_level >= 90 or general_level >= 90:
            for radius in range(20, 5, -5):
                alpha = 100 - (radius * 4)
                s = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 0, 0, alpha), (15, 15), radius)
                self.surface.blit(s, (self.WIDTH - 45, 15))
            pygame.draw.circle(self.surface, (255, 0, 0), (self.WIDTH - 30, 30), 10)
        
        # Draw 3D bin base with perspective
        points = [
            (self.bin_rect.left + self.bin_depth, self.bin_rect.bottom - self.bin_depth),
            (self.bin_rect.right + self.bin_depth, self.bin_rect.bottom - self.bin_depth),
            (self.bin_rect.right, self.bin_rect.bottom),
            (self.bin_rect.left, self.bin_rect.bottom)
        ]
        pygame.draw.polygon(self.surface, self.BIN_SHADOW, points)
        
        # Draw right side perspective
        points = [
            (self.bin_rect.right, self.bin_rect.top),
            (self.bin_rect.right + self.bin_depth, self.bin_rect.top - self.bin_depth),
            (self.bin_rect.right + self.bin_depth, self.bin_rect.bottom - self.bin_depth),
            (self.bin_rect.right, self.bin_rect.bottom)
        ]
        pygame.draw.polygon(self.surface, self.BIN_HIGHLIGHT, points)
        
        # Draw main compartments with 3D effect
        left_comp = pygame.Rect(self.bin_rect.left, self.bin_rect.top,
                              self.bin_rect.width//2 - 2, self.bin_rect.height)
        right_comp = pygame.Rect(self.bin_rect.centerx + 2, self.bin_rect.top,
                               self.bin_rect.width//2 - 2, self.bin_rect.height)
        
        # Draw compartments with shading
        pygame.draw.rect(self.surface, self.RED_BIN_SHADOW, left_comp)
        pygame.draw.rect(self.surface, self.GREEN_BIN_SHADOW, right_comp)
        
        # Add highlights to bin edges
        pygame.draw.line(self.surface, self.RED_BIN_HIGHLIGHT, 
                        (left_comp.left, left_comp.top),
                        (left_comp.right, left_comp.top), 3)
        pygame.draw.line(self.surface, self.GREEN_BIN_HIGHLIGHT,
                        (right_comp.left, right_comp.top),
                        (right_comp.right, right_comp.top), 3)
        
        # Draw sensor area with metallic effect
        sensor = pygame.Rect(self.WIDTH//2 - 50, 100, 100, 20)
        pygame.draw.rect(self.surface, (120, 120, 120), sensor, border_radius=5)
        pygame.draw.rect(self.surface, (160, 160, 160), sensor, border_radius=5, width=2)
        
        # Draw waste levels with gradient effect
        bio_height = int(biomedical_level * left_comp.height / 100)
        gen_height = int(general_level * right_comp.height / 100)
        
        if bio_height > 0:
            for i in range(bio_height):
                alpha = 255 - (i // 2)
                color = (min(255, 200 + i//3), max(0, 100 - i//2), max(0, 100 - i//2))
                pygame.draw.rect(self.surface, color,
                               (left_comp.left + 5,
                                left_comp.bottom - i - 1,
                                left_comp.width - 10,
                                1))
        
        if gen_height > 0:
            for i in range(gen_height):
                alpha = 255 - (i // 2)
                color = (max(0, 100 - i//2), min(255, 200 + i//3), max(0, 100 - i//2))
                pygame.draw.rect(self.surface, color,
                               (right_comp.left + 5,
                                right_comp.bottom - i - 1,
                                right_comp.width - 10,
                                1))
        
        # Draw the lid with perspective and rotation
        if self.lid_angle > 0:
            # Calculate lid points with rotation
            lid_height = int(self.lid_rect.height * abs(np.cos(np.radians(self.lid_angle))))
            lid_offset = int(self.lid_rect.height * np.sin(np.radians(self.lid_angle)))
            
            if self.lid_angle <= 90:
                points = [
                    (self.lid_rect.left, self.lid_rect.top),
                    (self.lid_rect.right, self.lid_rect.top),
                    (self.lid_rect.right, self.lid_rect.top + lid_height),
                    (self.lid_rect.left, self.lid_rect.top + lid_height)
                ]
                # Add shading based on angle
                lid_shade = int(160 + (self.lid_angle / 90) * 40)
                pygame.draw.polygon(self.surface, (lid_shade, lid_shade, lid_shade), points)
        else:
            # Draw normal lid
            pygame.draw.rect(self.surface, self.lid_color, self.lid_rect)
            pygame.draw.line(self.surface, self.lid_highlight, 
                           (self.lid_rect.left, self.lid_rect.top),
                           (self.lid_rect.right, self.lid_rect.top), 3)

    def animate_waste_drop(self, waste_type, biomedical_level, general_level, frames=30):
        final_x = self.WIDTH // 4 if waste_type == "biomedical" else 3 * self.WIDTH // 4
        waste_x = self.WIDTH // 2  # Start in center
        
        # Phase 1: Drop onto lid (8 frames)
        for frame in range(8):
            self.surface.fill(self.BG_COLOR)
            y = 50 + (frame * 8)  # Faster drop
            self.draw_bin(biomedical_level, general_level)
            
            # Draw falling waste
            color = (255, 0, 0) if waste_type == "biomedical" else (0, 255, 0)
            pygame.draw.circle(self.surface, color, (waste_x, y), 10)
            yield self.surface_to_image()
            time.sleep(0.01)  # Faster animation
        
        # Phase 2: Lid animation (8 frames)
        for frame in range(8):
            self.lid_angle = frame * 11.25  # Rotate up to 90 degrees
            self.surface.fill(self.BG_COLOR)
            self.draw_bin(biomedical_level, general_level)
            
            # Calculate waste position during lid opening
            if frame < 4:
                waste_y = self.lid_rect.top
            else:
                waste_y = self.lid_rect.top + ((frame - 4) * 30)
                waste_x = waste_x + (final_x - waste_x) * ((frame - 4) / 4)
            
            pygame.draw.circle(self.surface, color, (waste_x, waste_y), 10)
            yield self.surface_to_image()
            time.sleep(0.01)
        
        # Phase 3: Close lid (5 frames)
        for frame in range(5):
            self.lid_angle = max(0, 90 - (frame * 18))
            self.surface.fill(self.BG_COLOR)
            self.draw_bin(biomedical_level, general_level)
            yield self.surface_to_image()
            time.sleep(0.01)
        
        # Reset lid
        self.lid_angle = 0

    def surface_to_image(self):
        return Image.frombytes('RGB', self.surface.get_size(),
                             pygame.image.tostring(self.surface, 'RGB'))
