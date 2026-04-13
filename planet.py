from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
from textures import create_basic_texture, create_earth_texture

class Planet:
    def __init__(self, name, radius, orbit_distance, orbit_speed, rotation_speed, color, parent=None, description=None):
        self.name = name
        self.radius = radius
        self.orbit_distance = orbit_distance
        self.orbit_speed = orbit_speed
        self.rotation_speed = rotation_speed
        self.color = color
        self.parent = parent
        self.moons = []
        
        # Default fallback string if no educational string injected
        self.description = description if description else ["Data missing..."]
        
        self.current_orbit_angle = random.uniform(0, 360)
        self.current_rotation_angle = 0.0
        
        self.texture_id = None
        self.quad = gluNewQuadric()
        gluQuadricTexture(self.quad, GL_TRUE)
        gluQuadricNormals(self.quad, GLU_SMOOTH)
        
        if self.parent:
            self.parent.add_moon(self)
        
    def add_moon(self, moon):
        self.moons.append(moon)
        
    def generate_texture(self):
        if self.name.lower() == "earth":
            self.texture_id = create_earth_texture()
        elif self.name.lower() == "sun":
             self.texture_id = create_basic_texture(self.color, variance=5)
        else:
             self.texture_id = create_basic_texture(self.color)
        
    def get_world_position(self):
        """ Calculate absolute rendering context coordinate mappings. """
        if self.parent is None:
            return (0.0, 0.0, 0.0) 
            
        parent_pos = self.parent.get_world_position()
        rad = math.radians(self.current_orbit_angle)
        
        # Geometrical placement aligned to Y-Axis hierarchical stack
        x = parent_pos[0] + self.orbit_distance * math.cos(rad)
        z = parent_pos[2] - self.orbit_distance * math.sin(rad)
        return (x, 0, z)

    def draw_orbit_path(self, active_selection=None):
        """ Render orbital route loops mapping raster structures """
        if self.orbit_distance == 0: return
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        # Extensively highlight specific tracks when object acts as current target
        is_selected = (self == active_selection)
        
        if is_selected:
            glLineWidth(3.5) # Emphasize target orbital geometry 
            glColor3f(1.0, 0.9, 0.4) # Bright golden trail
        else:
            glLineWidth(1.0)
            if self.name.lower() == "earth":
                 glColor3f(0.2, 0.35, 0.6)
            else:
                 glColor3f(0.2, 0.2, 0.2)
             
        glBegin(GL_LINE_LOOP)
        segments = 64
        for i in range(segments):
            theta = 2.0 * math.pi * float(i) / float(segments)
            x = self.orbit_distance * math.cos(theta)
            z = -self.orbit_distance * math.sin(theta)
            glVertex3f(x, 0, z)
        glEnd()
        
        glLineWidth(1.0) # Restorations

    def draw(self, show_orbits, lighting_enabled, active_selection=None):
        glPushMatrix()
        
        ambient = [self.color[0]*0.2, self.color[1]*0.2, self.color[2]*0.2, 1.0]
        diffuse = [self.color[0], self.color[1], self.color[2], 1.0]
        specular = [0.1, 0.1, 0.1, 1.0]
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT, GL_SHININESS, 10.0)
        
        if show_orbits and self.parent is not None:
             self.draw_orbit_path(active_selection)

        if lighting_enabled: glEnable(GL_LIGHTING)
        
        # 1. Transformational Depth offseting (Composite positioning)
        glRotatef(self.current_orbit_angle, 0, 1, 0)
        glTranslatef(self.orbit_distance, 0, 0)
        
        glPushMatrix()
        
        # 2. Frame-bound orientation
        glRotatef(self.current_rotation_angle, 0, 1, 0)
        
        if not lighting_enabled:
            glColor3fv(self.color)
        else:
            glColor4f(1, 1, 1, 1) # Disengage solid vector mapping
            
        if self.texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        else:
            glDisable(GL_TEXTURE_2D)
            
        # Orient spherical mesh alignments
        glRotatef(-90, 1, 0, 0)
        
        if self.name.lower() == "sun":
            # Override for the Sun acting as the primary illuminant
            emissive = [1.0, 1.0, 0.8, 1.0]
            if lighting_enabled: glMaterialfv(GL_FRONT, GL_EMISSION, emissive)
            gluSphere(self.quad, self.radius, 32, 32)
            no_emission = [0.0, 0.0, 0.0, 1.0] # Reset
            if lighting_enabled: glMaterialfv(GL_FRONT, GL_EMISSION, no_emission)
        else:
            gluSphere(self.quad, self.radius, 32, 32)
        
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)
        
        # Pass recursive drawing elements into inner body matrixes propagating Context target
        for moon in self.moons:
            moon.draw(show_orbits, lighting_enabled, active_selection)
            
        glPopMatrix()
