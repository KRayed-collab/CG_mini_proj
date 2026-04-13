import math
from OpenGL.GL import *
from OpenGL.GLU import *

def ray_sphere_intersect(ray_origin, ray_dir, sphere_center, radius):
    """ Algebraic quadratic solution to intersect rays (click) with bounding spheres. """
    oc = [ray_origin[0] - sphere_center[0], 
          ray_origin[1] - sphere_center[1], 
          ray_origin[2] - sphere_center[2]]
          
    a = ray_dir[0]**2 + ray_dir[1]**2 + ray_dir[2]**2
    b = 2.0 * (oc[0]*ray_dir[0] + oc[1]*ray_dir[1] + oc[2]*ray_dir[2])
    c = oc[0]**2 + oc[1]**2 + oc[2]**2 - radius**2
    
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None
    
    dist1 = (-b - math.sqrt(discriminant)) / (2.0*a)
    if dist1 > 0: return dist1
    return None

def ray_plane_intersect(ray_origin, ray_dir, plane_y=0.0):
    """
    Finds where a 3D ray intersects a horizontal plane (XZ plane).
    Used to drag planets dynamically into any 3D coordinate on their orbit plane.
    """
    if ray_dir[1] == 0:
        return None # Ray is parallel
        
    t = (plane_y - ray_origin[1]) / ray_dir[1]
    if t < 0:
        return None # Plane is behind camera
        
    return [
        ray_origin[0] + ray_dir[0] * t,
        plane_y,
        ray_origin[2] + ray_dir[2] * t
    ]

def unproject_mouse(mx, my):
    """ Calculate ray trajectory for screen coordinates to 3D World space """
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    
    opengl_y = viewport[3] - my # Flip Pygame Y Coordinate to OpenGL Y Axis
    
    if modelview is None or projection is None or viewport is None:
        return [0,0,0], [0,0,-1]
        
    p_near = gluUnProject(mx, opengl_y, 0.0, modelview, projection, viewport)
    p_far = gluUnProject(mx, opengl_y, 1.0, modelview, projection, viewport)
    
    ray_origin = p_near
    ray_dir = [p_far[0] - p_near[0], p_far[1] - p_near[1], p_far[2] - p_near[2]]
    
    length = math.sqrt(ray_dir[0]**2 + ray_dir[1]**2 + ray_dir[2]**2)
    if length > 0:
        ray_dir = [ray_dir[0]/length, ray_dir[1]/length, ray_dir[2]/length]
        
    return ray_origin, ray_dir
