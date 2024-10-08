"""
main file to run

based on https://github.com/moderngl/moderngl-window/blob/master/examples/geometry_cube.py
"""

import numpy as np
from pyrr import matrix33

import moderngl
import moderngl_window

from cube import cube, hypercube
from utils import axes_coordinate_system, rotate
from base import CameraWindow


class CubeSimple(CameraWindow):
    title = "Cube"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = moderngl.LINES
        self.wnd.mouse_exclusivity = False
        self.cube = cube(size=(2, 2, 2), mode=self.mode)
        self.hypercube = hypercube(size = (2,2,2,2), mode=self.mode)
        self.hypercube2 = hypercube(size = (0.5,0.5,0.5,0.5), mode=self.mode)
        self.hypercube3 = hypercube(size = (0.5,0.5,0.5,0.5), mode=self.mode)
        self.axes4 = axes_coordinate_system(4, 2)
        
        self.prog4d = self.ctx.program(
            vertex_shader='''
                #version 450
                float PI = 3.141592653589793;
                in vec4 in_position;
                // in vec3 in_normal;
                
                uniform mat4 m_model_r; // model to world coordinates
                uniform vec4 m_model_t;
                uniform mat4 m_orientation4; // world to 3d camera coordinate transformation
                uniform vec4 m_position4; // world to 3d camera coordinate transformation
                uniform mat3 m_orientation3; // 3d to 2d camera
                uniform vec3 m_position3; // 3d to 2d camera
                uniform mat4 m_proj; // perspective projection
                
                out vec3 pos;
                out vec3 color;
                
                void main() {
                    float min = -abs(in_position.w);
                    float max = abs(in_position.w);
                    // 4d->3d
                    vec4 p_world = (transpose(m_model_r) * in_position) + m_model_t;
                    vec4 p_cam_or = (transpose(m_orientation4) * p_world);
                    
                    // depth coloring depending on w coordinate in camera coordinates
                    float c = (p_cam_or.w - min) / max;
                    color = vec3(1-c,c,0);
                    
                    vec4 p_cam = p_cam_or + m_position4;
                    
                    // perspective devide
                    float fov = tan(PI * 45 / 180);
                    p_cam.x /= p_cam.w * fov;
                    p_cam.y /= p_cam.w * fov;
                    p_cam.z /= p_cam.w * fov;
                    p_cam.w = 1;
                    
                    // 3d->2d
                    fov = tan(PI * 60 / 180);
                    p_cam.xyz = transpose(m_orientation3) * p_cam.xyz + m_position3; // to camera that projects from 3d to 2d
                    gl_Position = m_proj * p_cam; 
                    // vec4(p_cam.x * fov, p_cam.y * fov * (16.0/9.0), -p_cam.z + (1.0/99.0), -p_cam.z + 1.0); // 
                    
                    pos = p_cam.xyz;
                    vec4 unused = m_proj * vec4(1.0,1.0,1.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 fragColor;
                
                in vec3 pos;
                in vec3 color;
                
                void main() {
                    fragColor = vec4(color, 1.0); // vec4(0.1, 0.1, 0.1, 1.0);
                }
            ''',
        )
        # simple shader for axes of coordinate system
        self.axes4d = self.ctx.program(
            vertex_shader='''
                #version 450
                float PI = 3.141592653589793;
                in vec4 in_position;
                // in vec3 in_normal;
                
                uniform mat4 m_model_r; // model to world coordinates
                uniform vec4 m_model_t;
                uniform mat4 m_orientation4; // world to 3d camera coordinate transformation
                uniform vec4 m_position4; // world to 3d camera coordinate transformation
                uniform mat3 m_orientation3; // 3d to 2d camera
                uniform vec3 m_position3; // 3d to 2d camera
                uniform mat4 m_proj; // perspective projection
                
                out vec3 pos;
                out vec4 color;
                
                void main() {
                    float min = -abs(in_position.w);
                    float max = abs(in_position.w);
                    // 4d->3d
                    vec4 p_cam = (transpose(m_orientation4) * in_position) + m_position4;
                    // perspective devide
                    float fov = tan(PI * 45 / 180);
                    p_cam.x /= p_cam.w * fov;
                    p_cam.y /= p_cam.w * fov;
                    p_cam.z /= p_cam.w * fov;
                    p_cam.w = 1;
                    
                    // 3d->2d
                    fov = tan(PI * 60 / 180);
                    p_cam.xyz = transpose(m_orientation3) * p_cam.xyz + m_position3; // to camera that projects from 3d to 2d
                    gl_Position = m_proj * p_cam; 
                    
                    color = vec4(in_position.z+in_position.y+in_position.x, in_position.y+in_position.w+in_position.x, in_position.z+in_position.w+in_position.x, 0.5);
                    pos = p_cam.xyz;
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 fragColor;
                
                in vec3 pos;
                in vec4 color;
                
                void main() {
                    fragColor = color; // vec4(0.1, 0.1, 0.1, 1.0);
                }
            ''',
        )
        self.prog3d = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec3 in_position;
                
                uniform mat3 m_model_orient; // model to world coordinates
                uniform mat3 orientation; // world 2 camera coordinate rotation
                uniform vec3 position; // world 2 camera coordinate translation
                uniform mat4 m_proj; // perspective projection
                
                out vec3 pos;
                out vec3 normal;
                
                void main() {
                    mat3 m_view = transpose(orientation) * m_model_orient;
                    vec3 p = m_view * in_position + position;
                    float fov = tan(1.0471975511965976);
                    gl_Position =  m_proj * vec4(p, 1.0); 
                    pos = p.xyz;
                    
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 fragColor;
                uniform vec4 color;
                
                in vec3 pos;
                
                void main() {
                    fragColor = color; // vec4(0.1, 0.1, 0.1, 1.0);
                }
            ''',
        )
        self.prog3d['color'].value = 0.0, 0.0, 1.0, 1.0
        

    def render3d(self, time: float, frametime: float):
        rotation = matrix33.create_from_eulers((0.0, 0.0, 0.0), dtype='f4')
        modelview = rotation

        self.prog3d['m_proj'].write(self.camera.projection.matrix) # near, far, aspect, max, min in x and y dir
        self.prog3d['m_model_orient'].write(modelview) 
        
        orientation, position = self.camera.matrix
        #print(orientation, position)
        self.prog3d['orientation'].write(orientation) # position and orientation of camera, transforms from world to camera coordinates
        self.prog3d['position'].write(position) # position and orientation of camera, transforms from world to camera coordinates
        
        self.cube.render(self.prog3d, mode=self.mode)
        
    def render4d(self, time: float, frametime: float):
        # near, far, aspect, max, min in x and y dir for 3D camera, 4D projection with simple perspective devide
        self.prog4d['m_proj'].write(self.camera.projection.matrix) 
        # position and orientation of camera, transforms from world to camera coordinates
        orientation4, position4 = self.camera.matrix4d 
        self.prog4d['m_orientation4'].write(orientation4)
        self.prog4d['m_position4'].write(position4)
        # result of the perspective devide of the 4D camera is the world coordinate system of 3D camera
        orientation, position = self.camera.matrix
        self.prog4d['m_orientation3'].write(orientation)
        self.prog4d['m_position3'].write(position)
        
        # first cube in center
        rotation = rotate(np.array([0,0,0, 0,0,0]))
        translation = np.array([0.0, 0.0, 0.0, 0.0], dtype='f4')
        # rotate and move model in world coordinate system
        self.prog4d['m_model_r'].write(rotation) 
        self.prog4d['m_model_t'].write(translation)
        self.hypercube.render(self.prog4d, mode=self.mode)
        
        # second cube
        rotation = rotate(np.array([0,0,0, 0,0,0]))
        translation = np.array([-0.5, 1, 0.0, 0.0], dtype='f4')
        self.prog4d['m_model_r'].write(rotation)
        self.prog4d['m_model_t'].write(translation)
        self.hypercube2.render(self.prog4d, mode=self.mode)
        
        # third cube
        rotation = rotate(np.array([0,0,0, 0,0,0]))
        translation = np.array([0.5, 1, 0, 0], dtype='f4')
        self.prog4d['m_model_r'].write(rotation) 
        self.prog4d['m_model_t'].write(translation)
        self.hypercube3.render(self.prog4d, mode=self.mode)
        
        if self.showAxes:
            self.axes4d['m_proj'].write(self.camera.projection.matrix) 
            self.axes4d['m_orientation4'].write(orientation4)
            self.axes4d['m_position4'].write(position4)
            self.axes4d['m_orientation3'].write(orientation)
            self.axes4d['m_position3'].write(position)
            self.axes4.render(self.axes4d, mode=self.mode)
            
    def render(self, time: float, frametime: float):
        self.ctx.enable_only(moderngl.CULL_FACE | moderngl.DEPTH_TEST)
        self.ctx.clear(0.0, 0.0, 0.0) # make background white -> 1.0,1.0,1.0
        if self.render3D:
            self.render3d(time, frametime)
        else:
            self.render4d(time, frametime)


if __name__ == '__main__':
    moderngl_window.run_window_config(CubeSimple)