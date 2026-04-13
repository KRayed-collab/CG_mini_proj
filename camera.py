import math
from OpenGL.GL import *
from OpenGL.GLU import *

class Camera:
    def __init__(self):
        self.distance = 50.0        # Active animated distance tracking
        self.target_distance = 50.0 # Goal interpolation distance
        self.pitch = 30.0           # Elevation angle
        self.yaw = 0.0              # Azimuth angle
        self.target = [0.0, 0.0, 0.0]

    def update(self):
        """ Evaluates smoothing interpolations. Designed to avoid abrupt camera visual jumps 
            when targeting bodies of varied sizes or vastly separated orbital distances. """
        # 1. Smooth interpolation applied to camera boom length setup
        self.distance += (self.target_distance - self.distance) * 0.08

    def apply(self):
        glLoadIdentity()
        
        # Calculate camera position based on spherical coordinates relative to target
        pitch_rad = math.radians(self.pitch)
        yaw_rad = math.radians(self.yaw)
        
        cam_x = self.target[0] + self.distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        cam_y = self.target[1] + self.distance * math.sin(pitch_rad)
        cam_z = self.target[2] + self.distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        
        # Orient the camera towards the target point
        gluLookAt(cam_x, cam_y, cam_z, 
                  self.target[0], self.target[1], self.target[2], 
                  0, 1, 0)
        
        return cam_x, cam_y, cam_z
