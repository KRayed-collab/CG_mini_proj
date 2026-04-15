import pygame
from OpenGL.GL import *
import random
import os

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

def load_image_texture(filename):
    """ Loads an image file and converts it into an OpenGL Texture Object """
    try:
        surface = pygame.image.load(filename)
        # Flip the image vertically since OpenGL expects the origin at the bottom-left
        surface = pygame.transform.flip(surface, False, True)
        return generate_opengl_texture(surface)
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return None
