"""
based on an example 3D camera from the moderngl-window library:
https://github.com/moderngl/moderngl-window/blob/master/moderngl_window/scene/camera.py

"""

import time
from math import cos, radians, sin

import numpy as np
from pyrr import Vector3, vector, vector3, Vector4, Matrix44
from utils import cross, rotate_plane

from moderngl_window.opengl.projection import Projection3D
from moderngl_window.context.base.keys import BaseKeys

# Direction Definitions
RIGHT = 1
LEFT = 2
FORWARD = 3
BACKWARD = 4
UP = 5
DOWN = 6
IN = 7
OUT = 8
RED = 9
GREEN = 10
BLUE = 11
ORANGE = 12
YELLOW = 13
VIOLET = 14


# Movement Definitions
STILL = 0
POSITIVE = 1
NEGATIVE = 2


class Camera:
    """Simple camera class containing projection.

    .. code:: python

        # create a camera
        camera = Camera(fov=60.0, aspect_ratio=1.0, near=1.0, far=100.0)

        # Get the current camera matrix as numpy array
        print(camera.matrix)

        # Get projection matrix as numpy array
        print(camera.projection.matrix)
    """

    def __init__(self, keys: BaseKeys, fov=45.0, aspect_ratio=1.0, near=1.0, far=100.0):
        """Initialize camera using a specific projection

        Keyword Args:
            fov (float): Field of view
            aspect_ratio (float): Aspect ratio
            near (float): Near plane
            far (float): Far plane
        """
        # position and orientation of 3D camera
        self.position = Vector3([0.0, 0.0, 2.0])
        self.up = Vector3([0.0, 1.0, 0.0])
        self.right = Vector3([1.0, 0.0, 0.0])
        self.dir = Vector3([0.0, 0.0, 1.0])
        self.orientation = np.array([self.right, self.up, self.dir], dtype="f4")
        
        # if true move 3d camera, else 4d camera
        # usually set to false bc 3D camera is supposed to be fixed
        self.keyboard_3d = False
        # if true rotation around camera coordinate system axes, else world coordinate sys axes)
        self.cameraCoordinates = True
        # if true rotate around center of camera coordinate system, else of world coordinate system
        self.cameraCenter = True
        
        # position and orientation of 4D camera
        self.position4 = Vector4([0.0, 0.0, 0.0, -3.0])
        self.dir4 = Vector4([0.0, 0.0, 0.0, 1.0]) # w
        self.up4 = Vector4([0.0, 1.0, 0.0, 0.0]) # y
        self.right4 = Vector4([0.0, 0.0, 1.0, 0.0]) # z
        self.in4 = Vector4([1.0, 0.0, 0.0, 0.0]) # x
        self.orientation4 = np.array([self.in4, self.up4, self.right4, self.dir4], dtype="f4")
        
        # Yaw and Pitch (rotation in 3d with mouse)
        self._yaw3D = 90.0
        self._pitch3D = 90.0

        # yaw and pitch in 4D, for orbit controls in 4D
        self._yaw = 90.0
        self._pitch = 90.0
        # + roll for 4D mouse control (scrolling)
        self._roll = 90.0

        # World up vector of 3D world
        self._up = Vector3([0.0, 1.0, 0.0])
        # 4D world up and right vector
        self._up4 = Vector4([0.0, 1.0, 0.0, 0.0]) # y
        self._right4 = Vector4([0.0, 0.0, 1.0, 0.0]) # z

        # Projection for 3D->2D of 3D camera
        self._projection = Projection3D(aspect_ratio, fov, near, far)
        
        # NAVIGATION ATTRIBUTES:
        # 2 keys for each direction 
        # (direction = rotation in plane in POSITIVE/NEGATIVE dir (changing orientation), 
        # or translation in POSITIVE/NEGATIVE dir. (changing position)))
        # "still" if none of the 2 keys is pressed.
        # position:
        self._xdir = STILL
        self._zdir = STILL
        self._ydir = STILL
        self._wdir = STILL
        # rotation:
        self._xwrot = STILL
        self._ywrot = STILL
        self._zwrot = STILL
        self._xyrot4 = STILL
        self._yzrot4 = STILL
        self._xzrot4 = STILL
        # for the 3D camera if used:
        self._xzrot = STILL
        self._yzrot = STILL
        self._xyrot = STILL

        self._last_time = 0
        self._last_rot_time = 0
        
        # Velocity in axis units per second
        self._velocity = 3.0
        self._mouse_sensitivity = 0.5

        # For using keys to navigate:
        self.keys = keys

    @property
    def projection(self):
        """
        :py:class:`~moderngl_window.opengl.projection.Projection3D`: The 3D projection
        projection matrix for 3D camera (3D->2D perspective projection)
        """
        return self._projection

    """
    @property
    def matrix(self) -> np.ndarray:
        np.ndarray: The current view matrix for the camera
        overwritten for each specific camera navigation system
        self._update_yaw_and_pitch()
        return self._gl_look_at(self.position, self.position + self.dir, self._up)
    
    @property
    def matrix4d(self) -> np.ndarray:
        np.ndarray: The current view matrix for the camera
        overwritten for each specific camera navigation system
        
        self._update_yaw_and_pitch_4d()
        return self._gl_look_at4d(self.position4, self.position4 + self.dir4, self._up4, self._right4)
    """
    def _update_yaw_and_pitch_3d(self) -> None:
        """
        Updates the 3D camera direction based on the current yaw and pitch.
        direction corresponds to z-axis of camera coordinate system, 
        = axis along which is projected.
        used only for orbit camera
        Orientation matrix of camera is updated based on dir and global up vector self._up in "matrix()"
        """
        front = Vector3([0.0, 0.0, 0.0])
        front.x = sin(radians(self._pitch3D)) * cos(radians(self._yaw3D))
        front.y = cos(radians(self._pitch3D))
        front.z = sin(radians(self._pitch3D)) * sin(radians(self._yaw3D))
        self.dir = vector.normalise(front)
    
    def update_orientation3D(self, d_xz, d_yz, d_xy = 0):
        """
        rotates camera orientation (dir, right, up vectors) around each axis by the
        given delta angles
        """
        xy_rot = rotate_plane(radians(d_xy), np.array([1,1,0,0]))
        xz_rot = rotate_plane(radians(d_xz), np.array([1,0,1,0]))
        yz_rot = rotate_plane(radians(d_yz), np.array([0,1,1,0]))
        
        rot_matrix = np.dot(xz_rot, yz_rot)
        rot_matrix = np.dot(rot_matrix, xy_rot)[:3,:3]
        
        
        # rotate around camera coordinates system axes
        if self.cameraCoordinates:
            self.dir = np.dot(rot_matrix, np.array([0, 0, 1])) #np.array([0, 0, 1, 0]))[:3] #z
            self.dir = np.dot(np.linalg.inv(self.orientation), self.dir)
            
            self.right = np.dot(rot_matrix, np.array([1, 0, 0])) #np.array([0, 0, 1, 0]))[:3] #z
            self.right = np.dot(np.linalg.inv(self.orientation), self.right) #np.array([0, 0, 1, 0]))[:3] #z
            
            self.up = np.dot(rot_matrix, np.array([0, 1, 0]))
            self.up = np.dot(np.linalg.inv(self.orientation), self.up)
            
            self.orientation = np.array([self.right, self.up, self.dir], dtype="f4")
        # rotate around world coordinates system axes
        else:
            self.dir = np.dot(rot_matrix, self.dir) #z
            self.right = np.dot(rot_matrix, self.right) #x
            self.up = np.dot(rot_matrix, self.up) #y
            self.orientation = np.array([self.right, self.up, self.dir], dtype="f4")
        
    
    def update_orientation4D(self, d_xz, d_yz, d_xw, d_yw, d_zw, d_xy = 0):
        """
        receives delta of angle in each rotation plane and updates
        the orientation and coordinate system axes of camera accordingly
        """
        xy_rot = rotate_plane(radians(d_xy), np.array([1,1,0,0]))
        yz_rot = rotate_plane(radians(d_yz), np.array([0,1,1,0]))
        xz_rot = rotate_plane(radians(d_xz), np.array([1,0,1,0]))
        xw_rot = rotate_plane(radians(d_xw), np.array([1,0,0,1]))
        yw_rot = rotate_plane(radians(d_yw), np.array([0,1,0,1]))
        zw_rot = rotate_plane(radians(d_zw), np.array([0,0,1,1]))
        
        rot_matrix = np.dot(xz_rot, yz_rot)
        rot_matrix = np.dot(rot_matrix, xy_rot)
        rot_matrix = np.dot(rot_matrix, xw_rot)
        rot_matrix = np.dot(rot_matrix, yw_rot)
        rot_matrix = np.dot(rot_matrix, zw_rot)
        
        # rotate around axes of camera coordinate system
        if self.cameraCoordinates:
            self.dir4 = np.dot(rot_matrix, np.array([0, 0, 0, 1])) #w
            self.dir4 = np.dot(np.linalg.inv(self.orientation4), self.dir4)
        
            self.right4 = np.dot(rot_matrix, np.array([0, 0, 1, 0])) #z
            self.right4 = np.dot(np.linalg.inv(self.orientation4), self.right4)
            
            self.up4 = np.dot(rot_matrix, np.array([0, 1, 0, 0])) #y
            self.up4 = np.dot(np.linalg.inv(self.orientation4), self.up4)
            
            self.in4 = np.dot(rot_matrix, np.array([1, 0, 0, 0])) #x
            self.in4 = np.dot(np.linalg.inv(self.orientation4), self.in4)
            
            self.orientation4 = np.dot(rot_matrix, self.orientation4)
            #self.orientation4 = np.array([self.in4, self.up4, self.right4, self.dir4], dtype="f4")
        # rotate around axes of world coordinate system    
        else:
            self.dir4 = np.dot(rot_matrix, self.dir4) #w
            self.right4 = np.dot(rot_matrix, self.right4) #z
            self.up4 = np.dot(rot_matrix, self.up4) #y
            self.in4 = np.dot(rot_matrix, self.in4) #x
            self.orientation4 = np.dot(self.orientation4, rot_matrix)
            #self.orientation4 = np.array([self.in4, self.up4, self.right4, self.dir4], dtype="f4")
        
    def _update_yaw_and_pitch_4d(self) -> None:
        """
        Updates the camera direction based on the current yaw [0,2pi], pitch[0,pi] and roll[0,pi]
        -> orbit controls
        in 4D w-axis = axis of projection
        camera orientation can then be calculated with the look at method
        """
        front = np.array([0.0, 0.0, 0.0, 0.0])
        front[0] = sin(radians(self._pitch)) * sin(radians(self._roll)) * cos(radians(self._yaw))
        front[1] = sin(radians(self._roll)) * cos(radians(self._pitch)) # up
        front[2] = cos(radians(self._roll)) # right
        front[3] = sin(radians(self._pitch)) * sin(radians(self._roll)) * sin(radians(self._yaw))
        self.dir4 = vector.normalise(front)
        
    def _gl_look_at(self, pos, target, up) -> (np.ndarray, np.ndarray):
        """The standard lookAt method.
        returns orientation and position ready to pass to shader

        Args:
            pos: current position
            target: target position to look at
            up: direction up
        Returns:
            np.ndarray: orientation (3x3)
            np.ndarray: position (3)
        """
        z = vector.normalise(target - pos) # dir
        x = vector.normalise(vector3.cross(vector.normalise(up), z)) # orthogonal to dir and up
        y = vector.normalise(vector3.cross(z, x)) # camera up
        
        orientation = np.zeros((3,3), dtype="f4")
        orientation[0][0] = x[0]  # -- X
        orientation[0][1] = x[1]
        orientation[0][2] = x[2]
        orientation[1][0] = y[0]  # -- Y
        orientation[1][1] = y[1]
        orientation[1][2] = y[2]
        orientation[2][0] = z[0]  # -- Z
        orientation[2][1] = z[1]
        orientation[2][2] = z[2]
        
        position = -np.array(pos, dtype="f4")
        
        return orientation, position
    
    def _gl_look_at4d(self, pos, target, up, right) -> np.ndarray:
        """The standard lookAt method extended for 4D.
        returns camera orientation and position ready to pass to shader

        Args:
            pos: current position
            target: target position to look at (pos + dir)
            up: direction up (world y axis)
            right: fixed direction that points to the "right" (world z axis)
        Returns:
            np.ndarray: orientation (4x4)
            np.ndarray: position (4)
        """
        
        w = vector.normalize(target - pos) # front/dir
        x = vector.normalize(cross(vector.normalize(up), vector.normalize(right), w)) # in
        y = vector.normalize(cross(vector.normalize(right), x, w)) # up
        z = vector.normalize(cross(w, x, y)) # right
        
        orientation = Matrix44.identity(dtype="f4")
        orientation[0][0] = x[0]  # -- X
        orientation[0][1] = x[1]
        orientation[0][2] = x[2]
        orientation[0][3] = x[3]
        orientation[1][0] = y[0]  # -- Y
        orientation[1][1] = y[1]
        orientation[1][2] = y[2]
        orientation[1][3] = y[3]
        orientation[2][0] = z[0]  # -- Z
        orientation[2][1] = z[1]
        orientation[2][2] = z[2]
        orientation[2][3] = z[3]
        orientation[3][0] = w[0]  # -- W
        orientation[3][1] = w[1]
        orientation[3][2] = w[2]
        orientation[3][3] = w[3]
        
        # 
        position = -np.array(pos, dtype="f4")
        return orientation, position

    def key_input(self, key, action, modifiers) -> None:
        """Process key inputs and move camera

        Args:
            key: The key
            action: key action release/press
            modifiers: key modifier states such as ctrl or shift
        """
        # Right
        if key == self.keys.D:
            if action == self.keys.ACTION_PRESS:
                self.move_right(True)
            elif action == self.keys.ACTION_RELEASE:
                self.move_right(False)
        # Left
        elif key == self.keys.A:
            if action == self.keys.ACTION_PRESS:
                self.move_left(True)
            elif action == self.keys.ACTION_RELEASE:
                self.move_left(False)
        # Forward
        elif key == self.keys.W:
            if action == self.keys.ACTION_PRESS:
                self.move_forward(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_forward(False)
        # Backwards
        elif key == self.keys.S:
            if action == self.keys.ACTION_PRESS:
                self.move_backward(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_backward(False)

        # Down
        elif key == 65505: #shift
            if action == self.keys.ACTION_PRESS:
                self.move_down(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_down(False)
        # Up
        elif key == self.keys.SPACE:
            if action == self.keys.ACTION_PRESS:
                self.move_up(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_up(False)
                
        # IN
        elif key == self.keys.Q:
            if action == self.keys.ACTION_PRESS:
                self.move_in(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_in(False)
        # OUT
        elif key == self.keys.E:
            if action == self.keys.ACTION_PRESS:
                self.move_out(True)
            if action == self.keys.ACTION_RELEASE:
                self.move_out(False)
        
        
        # rotation depending on which camera is activated (3D/4D)
        # rotate xw(4D)/xz(3D) 
        elif key == self.keys.LEFT:
            if action == self.keys.ACTION_PRESS:
                self.rotate_left(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_left(False)
        elif key == self.keys.RIGHT:
            if action == self.keys.ACTION_PRESS:
                self.rotate_right(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_right(False)
        
        # rotate yw(4D)/yz(3D)
        elif key == self.keys.UP:
            if action == self.keys.ACTION_PRESS:
                self.rotate_up(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_up(False)
        elif key == self.keys.DOWN:
            if action == self.keys.ACTION_PRESS:
                self.rotate_down(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_down(False)
                
        # rotate zw(4D)/xy(3D)
        elif key == self.keys.PAGE_UP:
            if action == self.keys.ACTION_PRESS:
                self.rotate_in(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_in(False)
        elif key == self.keys.PAGE_DOWN:
            if action == self.keys.ACTION_PRESS:
                self.rotate_out(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_out(False)
                
                
        # rotate xz(4D)
        elif key == self.keys.J:
            if action == self.keys.ACTION_PRESS:
                self.rotate_red(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_red(False)
        elif key == self.keys.L:
            if action == self.keys.ACTION_PRESS:
                self.rotate_green(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_green(False)
                
        # rotate yz(4D)
        elif key == self.keys.I:
            if action == self.keys.ACTION_PRESS:
                self.rotate_orange(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_orange(False)
        elif key == self.keys.K:
            if action == self.keys.ACTION_PRESS:
                self.rotate_blue(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_blue(False)
                
        # rotate xy(4D)
        elif key == self.keys.X:
            if action == self.keys.ACTION_PRESS:
                self.rotate_yellow(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_yellow(False)
        elif key == self.keys.Y:
            if action == self.keys.ACTION_PRESS:
                self.rotate_violet(True)
            if action == self.keys.ACTION_RELEASE:
                self.rotate_violet(False)
        
        elif action == self.keys.ACTION_PRESS and key == self.keys.P:
            self.keyboard_3d = not self.keyboard_3d
            print("camera 3d:", self.keyboard_3d)
        
        # reset angles, orientation & position
        elif key == self.keys.R and action == self.keys.ACTION_PRESS:
            print("reset all")
            self._yaw3D = 90.0
            self._pitch3D = 90.0
            self._yaw = 90.0
            self._pitch = 90.0
            self._roll = 90.0
            self.in4 = np.array([1,0,0,0])
            self.up4 = np.array([0,1,0,0])
            self.right4 = np.array([0,0,1,0])
            self.dir4 = np.array([0,0,0,1])
            self.position4 = Vector4([0.0, 0.0, 0.0, -3.0])
            self.orientation4 = np.array([self.in4, self.up4, self.right4, self.dir4], dtype="f4")
        
            self.dir = np.array([0,0,1])
            self.right = np.array([1,0,0])
            self.up = np.array([0,1,0])
            self.position = Vector3([0.0, 0.0, 2.0])
            self.orientation = np.array([self.right, self.up, self.dir], dtype="f4")
        # reproduce the same position to make video for documentation
        if key == self.keys.V and action == self.keys.ACTION_PRESS:
            cc = self.cameraCoordinates
            self.cameraCoordinates = True
            self.update_orientation4D(-20, 0, 0, 0, 0)
            self.update_orientation4D(0, 25, 0, 0, 0)
            self.cameraCoordinates = cc
            
    def move_left(self, activate) -> None:
        """The camera should be continiously moving to the left.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(LEFT, activate)

    def move_right(self, activate) -> None:
        """The camera should be continiously moving to the right.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(RIGHT, activate)

    def move_forward(self, activate) -> None:
        """The camera should be continiously moving forward.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(FORWARD, activate)

    def move_backward(self, activate) -> None:
        """The camera should be continiously moving backwards.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(BACKWARD, activate)

    def move_up(self, activate) -> None:
        """The camera should be continiously moving up.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(UP, activate)

    def move_down(self, activate):
        """The camera should be continiously moving down.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(DOWN, activate)
    
    # for fourth dimension in/out
    def move_in(self, activate):
        """The camera should be continiously moving inwards.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(IN, activate)
        
    def move_out(self, activate):
        """The camera should be continiously moving outwards.

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.move_state(OUT, activate)        
    
    def rotate_left(self, activate) -> None: # <-
        """camera rotation either in xw (4d scene) or xz (3d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(LEFT, activate)

    def rotate_right(self, activate) -> None: # ->
        """camera rotation either in xw (4d scene) or xz (3d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(RIGHT, activate)
    
    def rotate_up(self, activate) -> None: # arrow up
        """camera rotation either in yw (4d scene) or yz (3d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(UP, activate)

    def rotate_down(self, activate) -> None: # arrowdown
        """camera rotation either in yw (4d scene) or yz (3d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(DOWN, activate)
    
    def rotate_in(self, activate) -> None: # pagedown
        """camera rotation either in zw (4d scene) or xy (3d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(IN, activate)

    def rotate_out(self, activate) -> None: # pageup
        """camera rotation either in zw (4d scene) or xy (3d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(OUT, activate)
        
    def rotate_red(self, activate) -> None: # l
        """camera rotation in xz (4d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(RED, activate)
        
    def rotate_green(self, activate) -> None: # j
        """camera rotation in xz (4d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(GREEN, activate)
        
    def rotate_blue(self, activate) -> None: # k
        """camera rotation in yz (4d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(BLUE, activate)
        
    def rotate_orange(self, activate) -> None: # i
        """camera rotation in yz (4d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(ORANGE, activate)

    def rotate_yellow(self, activate) -> None: # x
        """camera rotation in xy (4d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(YELLOW, activate) 
    
    def rotate_violet(self, activate) -> None: # y
        """camera rotation in xy (4d scene)

        Args:
            activate (bool): Activate or deactivate this state
        """
        self.rot_state_from_keys(VIOLET, activate)
    
        
    def move_state(self, direction, activate) -> None:
        """Set the camera position move state.

        Args:
            direction: What direction to update
            activate: Start or stop moving in the direction
        """
        if direction == RIGHT:
            self._xdir = POSITIVE if activate else STILL
        elif direction == LEFT:
            self._xdir = NEGATIVE if activate else STILL
            
        elif direction == FORWARD:
            self._zdir = NEGATIVE if activate else STILL
        elif direction == BACKWARD:
            self._zdir = POSITIVE if activate else STILL
            
        elif direction == UP:
            self._ydir = POSITIVE if activate else STILL
        elif direction == DOWN:
            self._ydir = NEGATIVE if activate else STILL
        
        elif direction == IN:
            self._wdir = POSITIVE  if activate else STILL
        elif direction == OUT:
            self._wdir = NEGATIVE if activate else STILL

    def rot_state_from_keys(self, direction, activate) -> None:
        """Set the camera orientation change state.

        Args:
            direction: What direction (rotation plane) to update
            activate: Start or stop rotating in the plane
        """
        # 4D camera is activated (4D scene is rendered)
        if not self.keyboard_3d:
            if direction == RIGHT:
                print("rotate xw 4D")
                self._xwrot = POSITIVE if activate else STILL
            elif direction == LEFT:
                print("rotate xw 4D")
                self._xwrot = NEGATIVE if activate else STILL
                
            if direction == UP:
                print("rotate yw 4D")
                self._ywrot = POSITIVE if activate else STILL
            elif direction == DOWN:
                print("rotate yw 4D")
                self._ywrot = NEGATIVE if activate else STILL
                
            if direction == IN:
                self._zwrot = POSITIVE if activate else STILL
                print("rotate zw 4D")
            elif direction == OUT:
                self._zwrot = NEGATIVE if activate else STILL
                print("rotate zw 4D")
            
            # for camera in 3D space
            if direction == RED: # j, xz
                self._xzrot4 = POSITIVE if activate else STILL
                print("rotate xz 4D")
            elif direction == GREEN: # l
                self._xzrot4 = NEGATIVE if activate else STILL
                print("rotate xz 4D")
                
            if direction == BLUE: # k, yz
                self._yzrot4 = POSITIVE if activate else STILL
                print("rotate yz 4D")
            elif direction == ORANGE: # i
                self._yzrot4 = NEGATIVE if activate else STILL
                print("rotate yz 4D")
            
            if direction == YELLOW: # x, xy-plane
                self._xyrot4 = POSITIVE if activate else STILL
                print("rotate xy 4D")
            elif direction == VIOLET: # y, xy-plane
                self._xyrot4 = NEGATIVE if activate else STILL
                print("rotate xy 4D")
                
        # 3D camera is activated (3D scene is rendered)
        else:
            if direction == RIGHT:
                self._xzrot = POSITIVE if activate else STILL
                print("rotate xz 3D")
            elif direction == LEFT:
                self._xzrot = NEGATIVE if activate else STILL
                print("rotate xz 3D")
                
            if direction == UP:
                self._yzrot = POSITIVE if activate else STILL
                print("rotate yz 3D")
            elif direction == DOWN:
                self._yzrot = NEGATIVE if activate else STILL
                print("rotate yz 3D")
                
            if direction == IN:
                self._xyrot = POSITIVE if activate else STILL
                print("rotate xy 3D")
            elif direction == OUT:
                self._xyrot = NEGATIVE if activate else STILL
                print("rotate xy 3D")
    
    def update_position_from_keys3D(self):
        """
        change the position by moving in the 3 direction by using the keyboard
        movement can be along the axes of the camera coordinate system or on an orbit around the 
        world coordinate system origin ("pseudo orbit control" bc up-direction not considered)
        """
        # Use separate time in camera so we can move it when the demo is paused
        now = time.time()
        # If the camera has been inactive for a while, a large time delta
        # can suddenly move the camera far away from the scene
        t = max(now - self._last_time, 0)
        self._last_time = now
        velocity = 20
        
        if self.keyboard_3d:
            # only when rotating around center of camera coordinate system
            if self.cameraCenter:
                self.position = Vector3(np.dot(self.orientation, self.position))
            # X Movement
            if self._xdir == POSITIVE:
                self.position.x += velocity * t
            elif self._xdir == NEGATIVE:
                self.position.x -= velocity * t
        
            # Z Movement
            if self._zdir == POSITIVE:
                self.position.z += velocity * t
            elif self._zdir == NEGATIVE:
                self.position.z -= velocity * t
        
            # Y Movement
            if self._ydir == POSITIVE:
                self.position.y += velocity * t
            elif self._ydir == NEGATIVE:
                self.position.y -= velocity * t
                
            # only when rotating around center of camera coord. sys.
            if self.cameraCenter:
                self.position = Vector3(np.dot(np.linalg.inv(self.orientation), self.position))
        
    
    def update_orientation_from_keys3D(self):
        """
        change the orientation by rotating in the 3 planes by using the keyboard
        """
        diff = 1.0
        _xz = 0
        _yz = 0
        _xy = 0
        # XZ Rotation
        if self._xzrot == POSITIVE:
            _xz = -diff
        elif self._xzrot == NEGATIVE:
            _xz = diff
        
        # XZ Rotation
        if self._yzrot == POSITIVE:
            _yz = diff
        elif self._yzrot == NEGATIVE:
            _yz = -diff
            
        # XY Rotation
        if self._xyrot == POSITIVE:
            _xy += -diff
        elif self._xyrot == NEGATIVE:
            _xy += diff
            
        if self.keyboard_3d:
            self.update_orientation3D(_xz, _yz, _xy)
    
    def update_position_from_keys4D(self):
        """
        change the position by moving in the 4 directions by using the keyboard
        movement can be along the axes of the camera coordinate system or on an orbit around the 
        world coordinate system origin ("pseudo orbit control" bc up-direction not considered)
        """
        # Use separate time in camera so we can move it when the demo is paused
        now = time.time()
        # If the camera has been inactive for a while, a large time delta
        # can suddenly move the camera far away from the scene
        t = max(now - self._last_time, 0)
        self._last_time = now
        
        velocity = 20
        
        if not self.keyboard_3d:
            # for rotating around axes of camera coordinate system
            if self.cameraCenter:
                self.position4 = Vector4(np.dot(self.orientation4, self.position4))
            
            # X Movement
            if self._xdir == POSITIVE:
                self.position4.x += velocity * t
            elif self._xdir == NEGATIVE:
                self.position4.x -= velocity * t
        
            # Z Movement
            if self._zdir == POSITIVE:
                self.position4.z += velocity * t
            elif self._zdir == NEGATIVE:
                self.position4.z -= velocity * t
        
            # Y Movement
            if self._ydir == POSITIVE:
                self.position4.y += velocity * t
            elif self._ydir == NEGATIVE:
                self.position4.y -= velocity * t
            
            # W Movement
            if self._wdir == POSITIVE:
                self.position4.w += velocity * t
            elif self._wdir == NEGATIVE:
                self.position4.w -= velocity * t
            
            # for rotating around axes of camera coordinate system
            if self.cameraCenter:
                self.position4 = Vector4(np.dot(np.linalg.inv(self.orientation4), self.position4))
            
    
    def update_orientation_from_keys4D(self):
        """
        change the orientation by rotating in the 6 planes by using the keyboard
        """
        diff = 1.0
        _xz, _yz, _xw, _yw, _zw, _xy = (0,0,0,0,0,0)
        
        # XW Rotation
        if self._xwrot == POSITIVE:
            _xw = -diff
        elif self._xwrot == NEGATIVE:
            _xw = diff
        
        # YW Rotation
        if self._ywrot == POSITIVE:
            _yw = -diff
        elif self._ywrot == NEGATIVE:
            _yw = diff
            
        # ZW Rotation
        if self._zwrot == POSITIVE:
            _zw = -diff
        elif self._zwrot == NEGATIVE:
            _zw = diff
        
        # XZ Rotation
        if self._xzrot4 == POSITIVE:
            _xz = -diff
        elif self._xzrot4 == NEGATIVE:
            _xz = diff
            
        # YZ Rotation
        if self._yzrot4 == POSITIVE:
            _yz = diff
        elif self._yzrot4 == NEGATIVE:
            _yz = -diff
        
        # XY Rotation
        if self._xyrot4 == POSITIVE:
            _xy = diff
        elif self._xyrot4 == NEGATIVE:
            _xy = -diff
            
        if not self.keyboard_3d:
            self.update_orientation4D(_xz, _yz, _xw, _yw, _zw, _xy)

    """
    camera specific functions that might depend on the navigation system
    """
    
    # the same for all cameras except orbit controls
    def rot_state(self, dx: int, dy: int, dz: int, mouseKey: int, cam_3d = False) -> None:
        """Update the rotation of the camera from mouse movement

        This is done by passing in the relative
        mouse movement change on x and y (delta x, delta y)
        and scrollong movement change (delta z)

        Args:
            dx: Relative mouse position change on x
            dy: Relative mouse position change on y
            dz: Relative scrolling position change
            mouseKey: 1 = left mouse key, 2 = right mouse key, 3 = scrolling
        """
        now = time.time()
        delta = now - self._last_rot_time
        self._last_rot_time = now

        # Greatly decrease the chance of camera popping.
        # This can happen when the mouse enters and leaves the window
        # or when getting focus again.
        if delta > 0.1 and max(abs(dx), abs(dy)) > 2:
            return

        dx *= self._mouse_sensitivity
        dy *= self._mouse_sensitivity
        
        d_xz, d_yz, d_xw, d_yw, d_zw = (0, 0, 0, 0, 0)
        if mouseKey == 1: # left mouse key is clicked -> rotate xz, yz
            d_xz = -dx
            d_yz = -dy
        elif mouseKey == 2: # right key -> rotate xw, yw
            d_xw = dx
            d_yw = -dy
        elif mouseKey == 3: # scrolling
            d_zw = dz*3
            
        # orientation updated by rotation matrices of delta angles
        if not self.keyboard_3d:
            self.update_orientation4D(d_xz, d_yz, d_xw, d_yw, d_zw)
        else:
            self.update_orientation3D(d_xz, d_yz)
            
    
    @property
    def matrix(self):
        """
        updates orientation and position of 3D camera (if activated) based on key input
        and returns orientation matrix and position vector that are put to shader.
        input from the mouse is already in self.orientation at this point
        """
        # update position of camera 
        self.update_position_from_keys3D()
            
        # option of using keys to change orientation in addition to mouse
        self.update_orientation_from_keys3D()    

        if not self.cameraCenter:
            # rotate around center of world coordinates
            pos = -np.array(self.position, dtype = "f4") 
        else:
            # rotate around center of camera coordinates
            pos = np.array(-np.dot(self.orientation, self.position), dtype="f4") 
        return self.orientation, pos

        
    @property
    def matrix4d(self):
        """
        updates orientation and position of camera based on key input
        and returns orientation matrix and position vector that are put to shader.
        input from the mouse is already in self.orientation4 at this point
        """
        # update position of camera
        self.update_position_from_keys4D()
        
        # allowing rotating from keys
        self.update_orientation_from_keys4D()
        
        if not self.cameraCenter:  
            pos = -np.array(self.position4, dtype="f4")
        else:
            pos = np.array(-np.dot(self.orientation4, self.position4), dtype="f4")
        return self.orientation4, pos


## Cameras ##

class CameraCoordinateCamera(Camera):
    """
    4D Camera rotates around the coordinate system axes of the camera coordinate system
    3D Camera fixed
    use mouse+left key to rotate in xw and yw planes
    use mouse+right key to rotate in xz and yz planes
    use scrolling to rotate zw plane
    use x,y keys to rotate xy-plane
    move 4D cam in kamera coord. with ws (3d zoom), ad, shift-space, qe (4d zoom)
    """
    
    def __init__(self, keys: BaseKeys, fov=90.0, aspect_ratio=1.0, near=1.0, far=100.0):
        # For using keys to navigate:
        self.keys = keys
        super().__init__(keys=keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)
        self.cameraCoordinates = True
        self.cameraCenter = True
    
    
class WorldCoordinateCamera(Camera):
    """
    4D Camera rotates around axes of 4D world coordinate system
    3D camera fixed
    use mouse+left key to rotate in xw and yw planes
    use mouse+right key to rotate in xz and yz planes
    use scrolling to rotate zw plane
    move 4D cam in kamera coord. with ws (3d zoom), ad, shift-space, qe (4d zoom)
    """
    def __init__(self, keys: BaseKeys, fov=90.0, aspect_ratio=1.0, near=1.0, far=100.0):
        # For using keys to navigate:
        self.keys = keys
        super().__init__(keys=keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)
        
        self.cameraCoordinates = False
        self.cameraCenter = False


class CameraAxesWorldCenterCamera(Camera):
    """
    4D Camera rotates around axes of 4D camera coordinate system but center of world coordinates
    3D camera fixed
    use mouse+right mouse key to rotate in xw and yw planes
    use mouse+left mouse key to rotate in xz and yz planes
    use scrolling to rotate zw plane
    move 4D cam in kamera coord. with ws, ad, shift-space, qe (4d zoom)
    """
    def __init__(self, keys: BaseKeys, fov=90.0, aspect_ratio=1.0, near=1.0, far=100.0):
        # For using keys to navigate:
        super().__init__(keys=keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)
        self.cameraCoordinates = True
        self.cameraCenter = False
    
class Orbit4DCamera(Camera):
    """
    orbit controls for 4D cam using mouse only for rotation
    direction in which camera points (self.dir4) is calculated from 3 angles
    yaw [0,pi], pitch [0,pi], roll [0,2*pi]
    orientation from camera calculated from world up- and right-direction with look at function
    """
    def __init__(self, keys: BaseKeys, fov=90.0, aspect_ratio=1.0, near=1.0, far=100.0):
        # For using keys to navigate:
        self.keys = keys
        super().__init__(keys=keys, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)
        # rotate around center of world cooridinates
        self.cameraCenter = False
        # self.cameraCoordinates not relevant here bc no rotation around axes but looking direction from angles instead 
        
    # different rot_state method because direction directly from angles and not from multiplication with rotation matrices
    def rot_state(self, dx: int, dy: int, dz: int, mouseKey: int) -> None:
        """Update the rotation of the camera.

        This is done by passing in the relative
        mouse movement change on x and y (delta x, delta y).

        Args:
            dx: Relative mouse position change on x
            dy: Relative mouse position change on y
            dz: Relative scrolling position change
            mouseKey: 1 = left mouse key, 2 = right mouse key, 3 = scrolling
        """
        now = time.time()
        delta = now - self._last_rot_time
        self._last_rot_time = now

        # Greatly decrease the chance of camera popping.
        # This can happen when the mouse enters and leaves the window
        # or when getting focus again.
        if delta > 0.1 and max(abs(dx), abs(dy)) > 2:
            return

        dx *= self._mouse_sensitivity
        dy *= self._mouse_sensitivity
        
        # if 3D camera is used, the yaw (0,360) is not on scroll but on mouse
        if self.keyboard_3d:
            self._yaw3D -= dx # (0,360) -> x,z plane
            self._pitch3D += dy # (0,180) -> y-axis
        else:
            # left mouse key -> 3D camera
            if mouseKey == 1:
                self._yaw3D -= dx # (0,360) -> x,z plane
                self._pitch3D += dy # (0,180) -> y-axis
            # right mouse key -> 4D camera
            elif mouseKey == 2:
                self._roll -= dx # (0,180) -> z-axis
                self._pitch += dy # (0,180) -> y-axis
            # scroll
            self._yaw += dz*3 # (0,360) -> x,w plane
        
        if self._pitch > 179:
            self._pitch = 179
        if self._pitch < 1:
            self._pitch = 1
        if self._roll > 179: 
            self._roll = 179
        if self._roll < 1:
            self._roll = 1
        if self._yaw > 360:
            self._yaw = 360
        if self._yaw < 0:
            self._yaw = 0
            
        if self._yaw3D > 360:
            self._yaw3D = 360
        if self._yaw3D < 0:
            self._yaw3D = 0
        if self._pitch3D > 179:
            self._pitch3D = 179
        if self._pitch3D < 1:
            self._pitch3D = 1
        
        self._update_yaw_and_pitch_3d()
        self._update_yaw_and_pitch_4d()
        
    @property
    def matrix(self):
        """np.ndarray: The current view matrix for the camera"""
        
        self.update_position_from_keys3D()
        
        # use look at function to calculate orientation for orbit control
        self.orientation, pos = self._gl_look_at(self.position, self.position + self.dir, self.up)
        return self.orientation, pos
    
    @property
    def matrix4d(self):
        """np.ndarray: The current view matrix for the camera"""
        self.update_position_from_keys4D()
        
        self.orientation4, pos = self._gl_look_at4d(self.position4, self.position4 + self.dir4, self._up4, self._right4)
        return self.orientation4, pos
        
