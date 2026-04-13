import pygame
from pygame.locals import *
import math
from OpenGL.GL import *
from OpenGL.GLU import *

from camera import Camera
from planet import Planet
from math_utils import unproject_mouse, ray_sphere_intersect, ray_plane_intersect

class SolarSystemApp:
    def __init__(self):
        pygame.init()
        self.display = (1024, 768)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        
        self.screen = pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Extended 3D Solar System (Multi-module refactored)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 16)
        self.title_font = pygame.font.SysFont("Consolas", 20, bold=True)
        
        # Execution states
        self.is_running = True
        self.show_orbits = True
        self.lighting_enabled = True
        self.orthographic_mode = False
        self.sim_speed = 1.0
        self.is_paused = False
        
        # User manipulation parameters
        self.selected_planet = None
        self.dragging_planet = None
        
        self.camera = Camera()
        
        self.setup_opengl()
        self.build_solar_system()
        
    def setup_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glClearColor(0.015, 0.015, 0.025, 1.0) 
        self.update_projection()
        
        # Illuminant mapping properties
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        
    def build_solar_system(self):
        self.sun = Planet("Sun", 3.0, 0, 0, 0.5, (1, 0.8, 0.1))
        mercury = Planet("Mercury", 0.4, 6.0, 4.0, 1.0, (0.7, 0.7, 0.7), self.sun)
        venus = Planet("Venus", 0.8, 9.0, 2.5, 0.8, (0.9, 0.7, 0.4), self.sun)
        earth = Planet("Earth", 1.0, 13.0, 1.5, 2.0, (0.2, 0.4, 0.9), self.sun)
        moon = Planet("Moon", 0.25, 2.0, 5.0, 3.0, (0.8, 0.8, 0.8), earth)
        mars = Planet("Mars", 0.6, 18.0, 1.2, 1.9, (0.9, 0.3, 0.1), self.sun)
        jupiter = Planet("Jupiter", 2.2, 26.0, 0.6, 4.0, (0.8, 0.6, 0.5), self.sun)
        saturn = Planet("Saturn", 1.8, 35.0, 0.4, 3.5, (0.9, 0.8, 0.4), self.sun)
        uranus = Planet("Uranus", 1.3, 44.0, 0.2, 2.5, (0.5, 0.8, 0.9), self.sun)
        neptune = Planet("Neptune", 1.2, 53.0, 0.1, 2.5, (0.2, 0.4, 0.9), self.sun)
        
        self.flattened_celestials = [self.sun, mercury, venus, earth, moon, mars, jupiter, saturn, uranus, neptune]
        for p in self.flattened_celestials:
            p.generate_texture()

    def update_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        if self.orthographic_mode:
            aspect = self.display[0]/self.display[1]
            scale = self.camera.distance / 1.5
            glOrtho(-scale*aspect, scale*aspect, -scale, scale, -200, 200)
        else:
            gluPerspective(45, (self.display[0]/self.display[1]), 0.1, 500.0)
            
        glMatrixMode(GL_MODELVIEW)
        
    def handle_planet_drag(self, mx, my):
        if not self.dragging_planet or not self.dragging_planet.parent:
            return
            
        ray_origin, ray_dir = unproject_mouse(mx, my)
        # Assuming orbital alignment natively sits on the world Y=0 XZ plane model
        intersect_pt = ray_plane_intersect(ray_origin, ray_dir, plane_y=0.0)
        
        if intersect_pt:
            # Map intersection distances onto positional hierarchy
            parent_pos = self.dragging_planet.parent.get_world_position()
            
            dx = intersect_pt[0] - parent_pos[0]
            dz = parent_pos[2] - intersect_pt[2] # Flip mapping aligned to our geometry rule built within get_world_position()
            
            # Snap orbital properties immediately matching exact absolute spatial mapping 
            new_distance = math.sqrt(dx**2 + dz**2)
            # Prevent pushing into collision threshold structure
            self.dragging_planet.orbit_distance = max(self.dragging_planet.parent.radius + self.dragging_planet.radius, new_distance)
            self.dragging_planet.current_orbit_angle = math.degrees(math.atan2(dz, dx))

    def pick_planet(self, mx, my):
        ray_origin, ray_dir = unproject_mouse(mx, my)
        closest, dist = None, float('inf')
        for p in self.flattened_celestials:
            pos = p.get_world_position()
            d = ray_sphere_intersect(ray_origin, ray_dir, pos, p.radius * 1.5)
            if d is not None and d < dist:
                dist = d
                closest = p
        return closest

    def run(self):
        mouse_down = False
        while self.is_running:
            dt = self.clock.tick(60) / 1000.0 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        mouse_down = True
                        picked = self.pick_planet(*event.pos)
                        if picked:
                            self.selected_planet = picked
                            if picked != self.sun and picked.parent:
                                self.dragging_planet = picked
                                # Immediately trigger snap physics
                                self.handle_planet_drag(*event.pos)
                        else:
                            # Releasing selection by clicking empty space
                            self.selected_planet = None
                    elif event.button == 4:
                        self.camera.distance = max(10, self.camera.distance - 4.0)
                        if self.orthographic_mode: self.update_projection()
                    elif event.button == 5:
                        self.camera.distance = min(200, self.camera.distance + 4.0)
                        if self.orthographic_mode: self.update_projection()
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False
                        self.dragging_planet = None
                        
                elif event.type == pygame.MOUSEMOTION:
                    if mouse_down:
                        if self.dragging_planet:
                            # Drag handling mapped strictly to XYZ intersect spatial grid
                            self.handle_planet_drag(*event.pos)
                        else:
                            # General Free-Cam rotation
                            self.camera.yaw += event.rel[0] * 0.5
                            self.camera.pitch -= event.rel[1] * 0.5
                            self.camera.pitch = max(-89, min(89, self.camera.pitch))

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_UP:
                        self.sim_speed += 0.5
                    elif event.key == pygame.K_DOWN:
                        self.sim_speed = max(0.0, self.sim_speed - 0.5)
                    elif event.key == pygame.K_o:
                        self.show_orbits = not self.show_orbits
                    elif event.key == pygame.K_l:
                        self.lighting_enabled = not self.lighting_enabled
                    elif event.key == pygame.K_p:
                        self.orthographic_mode = not self.orthographic_mode
                        self.update_projection()
                    elif event.key == pygame.K_TAB:
                        if not self.selected_planet:
                            self.selected_planet = self.flattened_celestials[0]
                        else:
                            idx = self.flattened_celestials.index(self.selected_planet)
                            self.selected_planet = self.flattened_celestials[(idx+1) % len(self.flattened_celestials)]
                    elif event.key == pygame.K_c:
                         self.selected_planet = None
            
            # --- Temporal Animation Scaling ---
            if not self.is_paused:
                for c in self.flattened_celestials:
                    # Skip angle iteration on dynamically locked bodies holding state
                    if c != self.dragging_planet:
                        c.current_orbit_angle += c.orbit_speed * self.sim_speed * dt * 10
                    c.current_rotation_angle += c.rotation_speed * self.sim_speed * dt * 20
                    
            if self.selected_planet:
                tpos = self.selected_planet.get_world_position()
                self.camera.target[0] += (tpos[0] - self.camera.target[0]) * 0.15
                self.camera.target[1] += (tpos[1] - self.camera.target[1]) * 0.15
                self.camera.target[2] += (tpos[2] - self.camera.target[2]) * 0.15
            else:
                self.camera.target[0] += (0 - self.camera.target[0]) * 0.1
                self.camera.target[1] += (0 - self.camera.target[1]) * 0.1
                self.camera.target[2] += (0 - self.camera.target[2]) * 0.1

            self.render()
            pygame.display.flip()
            
        pygame.quit()
        
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.camera.apply()
        
        glPushMatrix()
        glLoadIdentity()
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()
        
        self.sun.draw(self.show_orbits, self.lighting_enabled)
        self.render_ui()
        
    def render_ui(self):
        w, h = self.display
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.draw_text(15, 15, "Controls: Mouse Drag=Rotate Camera | Scroll=Zoom", (200, 200, 200))
        self.draw_text(15, 35, "Select: Click Planet or hit TAB. Drag planet directly to move it mapping orbit.", (200, 200, 200))
        self.draw_text(15, 55, "Toggles: [P]rojection | [L]ighting | [O]rbits | [SPACE] Pause | Up/Down=Speed", (200, 200, 200))
        
        self.draw_text(15, 90, f"Mode: {'Orthographic' if self.orthographic_mode else 'Perspective'}", (255, 230, 200))
        self.draw_text(15, 110, f"Speed: {self.sim_speed}x {'(PAUSED)' if self.is_paused else ''}", (255, 230, 200))
            
        # Draw Planet Information Detail HUD explicitly when targeted
        if self.selected_planet:
             panel_x = w - 300
             panel_y = h - 180
             
             # Subdued background box
             glColor4f(0.0, 0.0, 0.1, 0.6)
             glBegin(GL_QUADS)
             glVertex2f(panel_x - 10, panel_y - 10)
             glVertex2f(w - 10, panel_y - 10)
             glVertex2f(w - 10, h - 10)
             glVertex2f(panel_x - 10, h - 10)
             glEnd()
             
             p = self.selected_planet
             self.draw_text(panel_x, panel_y, f">> {p.name.upper()} <<", (100, 255, 150), is_title=True)
             self.draw_text(panel_x, panel_y + 30, f"- Core Radius:   {p.radius:.2f} kM", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 55, f"- Orbit Status:  {p.orbit_distance:.2f} AU", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 80, f"- Orbit Vel:     {p.orbit_speed:.2f} yr/s", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 105, f"- Rotation Vel:  {p.rotation_speed:.2f} d/s", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 130, f"- Sub-Bodies:    {len(p.moons)} moons", (200, 255, 220))

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        if self.lighting_enabled: glEnable(GL_LIGHTING)
            
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def draw_text(self, x, y, text, color=(255, 255, 255), is_title=False):
        font = self.title_font if is_title else self.font
        surface = font.render(text, True, color, (0, 0, 0, 0)) 
        text_data = pygame.image.tostring(surface, "RGBA", True)
        
        glRasterPos2d(x, y + surface.get_height())
        glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

if __name__ == "__main__":
    app = SolarSystemApp()
    app.run()