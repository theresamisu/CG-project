"""
modified basd on moderngl-window library: 
https://github.com/moderngl/moderngl-window/blob/master/examples/base.py

"""

import moderngl_window as mglw
from camera import WorldCoordinateCamera, CameraAxesWorldCenterCamera, CameraCoordinateCamera, Orbit4DCamera


class CameraWindow(mglw.WindowConfig):
    """
    base class for switching cameras and dealing with keyboard and mouse input
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(self.ctx)
        # rotation around camera cooridinate axes and world coord sys center
        self.MixCam = CameraAxesWorldCenterCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio) # 0
        # rotation around world coordinate system axes and world coord sys center
        self.WorldCam = WorldCoordinateCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio) # 1
        # real orbit controls (3 angles), around center of world coord sys
        self.OrbitCam = Orbit4DCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio) # 2
        # rotation around camera coordinate axes and camera coord sys center
        self.CamCam = CameraCoordinateCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio) # 3
        self.camera_enabled = True
        self.mouse_enabled = True
        self.mouseKey = 0
        # activate first camera
        self.camera = self.CamCam
        # trigger printing of controls
        self.key_event(self.wnd.keys.F1, self.wnd.keys.ACTION_PRESS, 0)
        
        # show coordinate system axes
        self.showAxes = False
        # render 3D cube
        self.render3D = False
        
    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)

        if action == keys.ACTION_PRESS:
            if key == keys.Z:
                self.showAxes = not self.showAxes
            if key == keys.H:
                self.render3D = not self.render3D
                self.MixCam.keyboard_3d = self.render3D
                self.WorldCam.keyboard_3d = self.render3D
                self.OrbitCam.keyboard_3d = self.render3D
                self.CamCam.keyboard_3d = self.render3D
                print("render")
            # choose camera (maybe give position and orientation of previously used camera when changing?)
            if key == keys.F1:
                print()
                print("Camera Coordinate Camera")
                print("rotation axes: \t\t camera coord sys")
                print("center of rotation: \t camera coord sys")
                print("rotations:\t left mouse xz, yz")
                print("rotations:\t right mouse xw, yw")
                print("rotations:\t scroll mouse zw")
                print("rotations:\t x,y keys xy")
                print()
                self.camera = self.CamCam
            if key == keys.F2:
                print()
                print("Pseudo Orbit/World Coordinate Camera:")
                print("rotation axes: \t\t world coord sys")
                print("center of rotation: \t world coord sys")
                print("rotations:\t left mouse xz, yz")
                print("rotations:\t right mouse xw, yw")
                print("rotations:\t scroll mouse zw")
                print("rotations:\t x,y keys xy")
                print()
                self.camera = self.WorldCam
            if key == keys.F3:
                print()
                print("Mix of World and Camera Coordinate system Camera")
                print("rotation axes: \t\t camera coord sys")
                print("center of rotation: \t world coord sys")
                print("rotations:\t left mouse xz, yz")
                print("rotations:\t right mouse xw, yw")
                print("rotations:\t scroll mouse zw")
                print("rotations:\t x,y keys xy")
                print()
                self.camera = self.MixCam
            if key == keys.F4:
                print()
                print("Orbit Control Camera")
                print("rotation: \t\t camera directions from angles")
                print("center of rotation: \t world coord sys")
                print("rotations:\t left mouse for yaw, pitch 3D Camera")
                print("rotations:\t right mouse + scroll for yaw, pitch, roll 4D Camera")
                print()
                self.camera = self.OrbitCam
        if key == keys.ESCAPE:
            self.ctx.release()
                
    # no mouse button clicked
    def mouse_position_event(self, x: int, y: int, dx: int, dy: int):
        if self.camera_enabled and self.mouse_enabled:
            self.camera.rot_state(-dx, -dy, 0, 0)
                
    # left mouse key clicked -> xz, yz planes
    # right mouse key clicked -> xw, yw planes
    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int):
        if self.camera_enabled and self.mouse_enabled:
            self.camera.rot_state(-dx, -dy, 0, self.mouseKey)
    
    # scrolling = rotate in zw plane
    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        self.camera.rot_state(0, 0, -y_offset, 3)
        
    def mouse_release_event(self, x: int, y: int, button: int):
        self.mouseKey = 0
            
    def mouse_press_event(self, x: int, y: int, button: int):
        self.mouseKey = button
        
    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)

