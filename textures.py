import pygame
from OpenGL.GL import *
import random

def generate_opengl_texture(surface):
    """ Converts a Pygame Surface into an OpenGL Texture Object """
    w, h = surface.get_size()
    texture_data = pygame.image.tostring(surface, "RGB", True)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    return tex_id

def create_basic_texture(base_color, variance=30, width=128, height=128):
    """ Generate a basic procedural gas/band texture using Pygame surfaces. """
    surface = pygame.Surface((width, height))
    for y in range(height):
        # Create subtle horizontal bands resembling gas giants
        band_var = random.randint(-variance, variance)
        for x in range(width):
            # Also add tiny noise to each pixel
            noise = random.randint(-variance//2, variance//2)
            r = max(0, min(255, int(base_color[0] * 255) + band_var + noise))
            g = max(0, min(255, int(base_color[1] * 255) + band_var + noise))
            b = max(0, min(255, int(base_color[2] * 255) + band_var + noise))
            surface.set_at((x, y), (r, g, b))
    
    return generate_opengl_texture(surface)

def create_earth_texture(width=256, height=256):
    """
    Generate an intricate, pseudo-painted map of Earth.
    Simulates oceans, scattered landmasses, and polar ice caps.
    """
    surface = pygame.Surface((width, height))
    
    # 1. Base Layer: Deep ocean
    ocean_color = (15, 60, 140)
    surface.fill(ocean_color)
    
    # Lighter oceanic noise
    for x in range(width):
        for y in range(height):
            if random.random() < 0.1:
                col = (max(10, ocean_color[0]-10), min(255, ocean_color[1]+10), min(255, ocean_color[2]+20))
                surface.set_at((x, y), col)
                
    # 2. Continent Generators: Overlapping naturalistic circles
    land_clusters = random.randint(15, 25)
    for _ in range(land_clusters):
        cx = random.randint(0, width)
        # Avoid putting too much landmass directly at the extreme poles
        cy = random.randint(int(height*0.1), int(height*0.9)) 
        radius = random.randint(10, 40)
        
        # Color palettes for varied biomes (desert to forest)
        land_color = random.choice([
            (34, 139, 34),    # Forest green
            (85, 107, 47),    # Olive
            (145, 120, 60),   # Desert / arid
            (139, 69, 19),    # Mountainous / Brown
        ])
        
        # Build composite structure organically
        for _ in range(radius * 2):
            rad = random.randint(5, max(10, radius//2))
            pos_x = cx + random.randint(-radius, radius)
            pos_y = cy + random.randint(-radius, radius)
            
            pygame.draw.circle(surface, land_color, (pos_x, pos_y), rad)
            # Handle topological wrap-around so map connects smoothly on the sphere X seam
            if pos_x - rad < 0:
                pygame.draw.circle(surface, land_color, (pos_x + width, pos_y), rad)
            if pos_x + rad > width:
                pygame.draw.circle(surface, land_color, (pos_x - width, pos_y), rad)

    # 3. Apply Polar Ice Caps
    for x in range(width):
        for y in range(height):
            # South Pole maps to Y near bottom, North pole maps to Y near top
            if y < height * 0.12:
                # Jagged edge logic
                if y < height * 0.12 - random.randint(0, int(height*0.06)):
                    surface.set_at((x, y), (240, 240, 255))
            elif y > height * 0.88:
                if y > height * 0.88 + random.randint(0, int(height*0.06)):
                    surface.set_at((x, y), (240, 240, 255))
                    
    return generate_opengl_texture(surface)
