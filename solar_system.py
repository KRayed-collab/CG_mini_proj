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
        self.font = pygame.font.SysFont("Consolas", 15)
        self.title_font = pygame.font.SysFont("Consolas", 19, bold=True)
        
        # Execution states
        self.is_running = True
        self.show_orbits = True
        self.lighting_enabled = True
        self.orthographic_mode = False
        self.sim_speed = 1.0
        self.is_paused = False
        self.invert_controls = False # Option to invert Mouse Dragging behaviors
        
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
        # Spatially extending the distance spreads dramatically to avoid orbital line congestion natively.
        # Rich 4-line descriptors baked comprehensively into each model's instantiation.
        self.sun = Planet("Sun", 3.0, 0, 0, 0.5, (1, 0.8, 0.1), description=[
            "Center of the Solar System.", 
            "Contains roughly 99.8% of the system's mass.", 
            "Generates energy via thermonuclear fusion.", 
            "Surface temperature is an intense 5,500 Celsius."
        ])
        
        mercury = Planet("Mercury", 0.4, 12.0, 4.0, 1.0, (0.7, 0.7, 0.7), self.sun, description=[
            "Closest planet to the Sun.", 
            "Lacks an atmosphere to retain any heat.", 
            "Features a densely cratered, rocky surface.", 
            "Orbital period lasts only 88 Earth days."
        ])
        
        venus = Planet("Venus", 0.8, 18.0, 2.5, 0.8, (0.9, 0.7, 0.4), self.sun, description=[
            "Second planet from the Sun.", 
            "Possesses a thick, toxic atmosphere consisting of CO2.", 
            "Hottest planet inherently due to a runaway greenhouse effect.", 
            "Strangely rotates backwards compared to other planets."
        ])
        
        earth = Planet("Earth", 1.0, 26.0, 1.5, 2.0, (0.2, 0.4, 0.9), self.sun, description=[
            "Third planet from the Sun.", 
            "The only known planetary body actively holding life.", 
            "Liquid water oceans blanket roughly 71% of its surface.", 
            "Breathable atmosphere is rich in nitrogen and oxygen."
        ])
        
        # Adding Moon natively
        moon = Planet("Moon", 0.25, 2.0, 5.0, 3.0, (0.8, 0.8, 0.8), earth, description=[
            "Earth's solely natural satellite.", 
            "Gravitational pull effectively regulates Earth's tides.", 
            "Surface is eternally covered in ancient meteor craters.", 
            "Synchronous rotation locks one face permanently to Earth."
        ])
        
        mars = Planet("Mars", 0.6, 35.0, 1.2, 1.9, (0.9, 0.3, 0.1), self.sun, description=[
            "Fourth planet, traditionally known as the 'Red Planet'.", 
            "Operates as a dusty, terribly cold desert world.", 
            "Home to Olympus Mons, the largest volcano in the system.", 
            "Thin atmospheric remnants imply past massive liquid lakes."
        ])
        
        jupiter = Planet("Jupiter", 2.2, 55.0, 0.6, 4.0, (0.8, 0.6, 0.5), self.sun, description=[
            "Fifth planet, classified as the largest gas giant.", 
            "Hosts the Great Red Spot—a storm raging for centuries.", 
            "Entirely lacks a solid planetary surface.", 
            "Boasts a massive, incredibly complex system of 90+ moons."
        ])
        
        # Jupiter's Galilean Moons precisely spaced and articulated
        io = Planet("Io", 0.2, 3.0, 6.0, 5.0, (0.9, 0.8, 0.2), jupiter, description=["Innermost Galilean moon.", "Most volcanically active body recognized in the system.", "Surface constantly repainted from massive magma features.", "Locked in a perpetual gravitational tug-of-war."])
        europa = Planet("Europa", 0.18, 4.0, 4.0, 4.0, (0.8, 0.9, 0.9), jupiter, description=["Second Galilean moon.", "Incredibly smooth icy surface covers a vast subsurface ocean.", "A prime planetary candidate for hosting extraterrestrial life.", "Surface displays beautiful tectonic-like fracturing."])
        ganymede = Planet("Ganymede", 0.3, 5.5, 3.0, 3.0, (0.6, 0.6, 0.6), jupiter, description=["The largest categorized moon in the solar system.", "Actually volumetrically bigger than the planet Mercury.", "Distinctively generates its own independent magnetic field.", "Features mixing dark ancient regions alongside bright young ones."])
        callisto = Planet("Callisto", 0.25, 7.0, 2.0, 2.0, (0.5, 0.5, 0.5), jupiter, description=["Outermost Galilean moon belonging to Jupiter.", "Arguably the most heavily cratered object sitting in the system.", "Considered a geologically inactive, cold dead world.", "Contains extreme natural radiation shielding organically."])
        
        saturn = Planet("Saturn", 1.8, 75.0, 0.4, 3.5, (0.9, 0.8, 0.4), self.sun, description=[
            "Sixth planet, revered as the ringed jewel.", 
            "Possesses an exceptionally prominent icy ring subsystem.", 
            "Composed mostly of raw hydrogen and helium gas.", 
            "Functions as the least dense planet overall natively."
        ])
        
        # Saturn's dominant moon
        titan = Planet("Titan", 0.3, 4.0, 4.0, 4.0, (0.8, 0.7, 0.3), saturn, description=[
            "Saturn's largest independent satellite.", 
            "The sole moon confirmed holding a dense, completely opaque atmosphere.", 
            "Uniquely features stable liquid methane lakes on its surface.", 
            "Atmosphere is comprised overwhelmingly of thick nitrogen."
        ])
        
        uranus = Planet("Uranus", 1.3, 95.0, 0.2, 2.5, (0.5, 0.8, 0.9), self.sun, description=[
            "Seventh planet, commonly designated as an ice giant.", 
            "Strangely rotates directly on its structural side (98 degree tilt).", 
            "Harbors an extremely cold baseline planetary atmosphere.", 
            "Surrounded by thin, remarkably faint dark orbital rings."
        ])
        
        neptune = Planet("Neptune", 1.2, 110.0, 0.1, 2.5, (0.2, 0.4, 0.9), self.sun, description=[
            "Eighth planet, representing the farthest major body out.", 
            "Operates as a dark, cold world whipped natively by supersonic winds.", 
            "Vivid blue coloration stems directly from atmospheric methane gas.", 
            "Takes an immense 165 years to definitively orbit the Sun."
        ])
        
        # Explicit context-locking separations fulfilling requirement
        self.major_planets = [self.sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune]
        
        self.flattened_celestials = []
        for p in self.major_planets:
            self.flattened_celestials.append(p)
            for m in p.moons:
                self.flattened_celestials.append(m)
                
        # Kick off programmatic textures securely
        for p in self.flattened_celestials:
            p.generate_texture()

    def update_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        if self.orthographic_mode:
            aspect = self.display[0]/self.display[1]
            scale = self.camera.target_distance / 1.5
            glOrtho(-scale*aspect, scale*aspect, -scale, scale, -200, 200)
        else:
            gluPerspective(45, (self.display[0]/self.display[1]), 0.1, 500.0)
            
        glMatrixMode(GL_MODELVIEW)
        
    def handle_planet_drag(self, mx, my):
        if not self.dragging_planet or not self.dragging_planet.parent:
            return
            
        ray_origin, ray_dir = unproject_mouse(mx, my)
        intersect_pt = ray_plane_intersect(ray_origin, ray_dir, plane_y=0.0)
        
        if intersect_pt:
            parent_pos = self.dragging_planet.parent.get_world_position()
            
            dx = intersect_pt[0] - parent_pos[0]
            dz = parent_pos[2] - intersect_pt[2] 
            
            new_distance = math.sqrt(dx**2 + dz**2)
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
            
            self.camera.update() # Proc evaluation easing models continually
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        mouse_down = True
                        picked = self.pick_planet(*event.pos)
                        if picked:
                            self.selected_planet = picked
                            # Map focal sizing naturally resolving UX requirement
                            self.camera.target_distance = max(15, picked.radius * 9)
                            
                            if picked != self.sun and picked.parent:
                                self.dragging_planet = picked
                                self.handle_planet_drag(*event.pos)
                        else:
                            self.selected_planet = None
                    elif event.button == 4:
                        self.camera.target_distance = max(5.0, self.camera.target_distance - 4.0)
                        if self.orthographic_mode: self.update_projection()
                    elif event.button == 5:
                        self.camera.target_distance = min(200.0, self.camera.target_distance + 4.0)
                        if self.orthographic_mode: self.update_projection()
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False
                        self.dragging_planet = None
                        
                elif event.type == pygame.MOUSEMOTION:
                    if mouse_down:
                        if self.dragging_planet:
                            self.handle_planet_drag(*event.pos)
                        else:
                            # Apply configurable inversion parameter strictly to view-pitch scaling
                            inv = -1 if self.invert_controls else 1
                            self.camera.yaw += event.rel[0] * 0.5 * inv
                            self.camera.pitch -= event.rel[1] * 0.5 * inv
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
                    elif event.key == pygame.K_i:
                        self.invert_controls = not self.invert_controls
                    elif event.key == pygame.K_TAB:
                        # Iterate EXCLUSIVELY on standard explicit planets avoiding moon congestion
                        if not self.selected_planet or self.selected_planet not in self.major_planets:
                            self.selected_planet = self.major_planets[0]
                            self.camera.target_distance = max(15, self.selected_planet.radius * 9)
                        else:
                            idx = self.major_planets.index(self.selected_planet)
                            self.selected_planet = self.major_planets[(idx+1) % len(self.major_planets)]
                            self.camera.target_distance = max(15, self.selected_planet.radius * 9)
                    elif event.key == pygame.K_m:
                        # Secondary cycling exclusively to swap through moons of the contextual target
                        if self.selected_planet and self.selected_planet.parent in self.major_planets:
                            siblings = self.selected_planet.parent.moons
                            idx = siblings.index(self.selected_planet)
                            self.selected_planet = siblings[(idx+1) % len(siblings)]
                            self.camera.target_distance = max(15, self.selected_planet.radius * 9)
                        elif self.selected_planet and len(self.selected_planet.moons) > 0:
                            # Contextual root holds moons; drop down into children
                            self.selected_planet = self.selected_planet.moons[0]
                            self.camera.target_distance = max(15, self.selected_planet.radius * 9)
                    elif event.key == pygame.K_c:
                         self.selected_planet = None
            
            if not self.is_paused:
                for c in self.flattened_celestials:
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
        
        # Injects the active context target deeper into the pipeline allowing unique highlighting configurations mapped explicitly
        self.sun.draw(self.show_orbits, self.lighting_enabled, active_selection=self.selected_planet)
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
        self.draw_text(15, 35, "Select: Click Body | [TAB] Cycle Planets | [M] Cycle Moons", (200, 200, 200))
        self.draw_text(15, 55, "Toggles: [P]rojection | [L]ighting | [O]rbits | [SPACE] Pause", (200, 200, 200))
        
        self.draw_text(15, 90, f"Mode: {'Orthographic' if self.orthographic_mode else 'Perspective'}", (255, 230, 200))
        self.draw_text(15, 110, f"Speed: {self.sim_speed}x {'(PAUSED)' if self.is_paused else ''}", (255, 230, 200))
        self.draw_text(15, 130, f"Controls [I]: {'Inverted' if self.invert_controls else 'Standard'}", (255, 230, 200))
            
        # Draw explicit, highly detailed Planet Information Panel
        if self.selected_planet:
             # Widened bounds adapting formatting naturally around heavier descriptive texts mapped to parameters
             panel_w_offset = 380
             panel_h_offset = 240
             panel_x = w - panel_w_offset
             panel_y = h - panel_h_offset
             
             glColor4f(0.0, 0.0, 0.1, 0.75) # Darker, readable opacity boundary box mapping
             glBegin(GL_QUADS)
             glVertex2f(panel_x - 15, panel_y - 15)
             glVertex2f(w - 10, panel_y - 15)
             glVertex2f(w - 10, h - 10)
             glVertex2f(panel_x - 15, h - 10)
             glEnd()
             
             p = self.selected_planet
             self.draw_text(panel_x, panel_y, f">> {p.name.upper()} <<", (100, 255, 150), is_title=True)
             
             # Statistical properties mapped visually vertically across column bounds
             self.draw_text(panel_x, panel_y + 30, f"Core Radius:  {p.radius:.2f} kM", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 48, f"Orbit Status: {p.orbit_distance:.2f} AU", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 66, f"Orbit Vel:    {p.orbit_speed:.2f} yr/s", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 84, f"Rotation Vel: {p.rotation_speed:.2f} d/s", (200, 255, 220))
             self.draw_text(panel_x, panel_y + 102, f"Sub-Bodies:   {len(p.moons)} known satellites", (200, 255, 220))

             # Educational Descriptions injection rendering 
             self.draw_text(panel_x, panel_y + 130, f"--- Profile Data ---", (150, 180, 255))
             p_desc_y = panel_y + 150
             for line in p.description:
                 self.draw_text(panel_x, p_desc_y, f"• {line}", (220, 230, 255)) 
                 p_desc_y += 18

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