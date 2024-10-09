# CG Project Navigating 4D space

Download the repository and open the website to see the detailed documentation.

4 Camera navigation systems are implemented. The first three move only the 4D camera while the forth rotates both. 
1. (on key F1) Camera that rotates completely in Camera Coordinate system
2. (F2) Camera that rotates completely in World Coordinate system
3. (F3) Camera that rotates around the axes of Camera Coordinate system but around the origin of the world coordinate system
4. (F4) Camera that uses orbit controls where the direction is retrieved from five angles 
(as opposed to rotating the axes of the camera coordinate system with rotation matrices)

#### general keys
* F1, F2, F3, F4 switch between cameras
* z - show world coordinate system axes
* h - switch between 3D and 4D scene
* p - switch between navigation of 3D and 4D camera but keep the scene
(this is cheating since we actually want to fix the 3D camera in the 4D scene)

### translation
* w,s - move in z-direction
* a,d - move in x-direction
* space,shift - move in y-direction
* q,e - move in w-direction (if 4D camera)

### rotations
Cameras can be rotated either by using the keys or the mouse:

#### 1. from keys
For all cameras except camera with orbit controls.
if 4D camera is activated (default):
* j,l - rotate in xz plane
* k,i - rotate in yz plane
* y,x - rotate in xy plane
* left, right = rotate in xw plane
* up, down = rotate in yw plane
* page up, page down = rotate in zw plane

if 3D camera is activated (either activated with "p" or by switching from 4D scene to 3D scene with "h"):
* left, right - rotate in xz plane
* up, down - rotate in yz plane
* page up, page down - rotate in xy plane


### 2. from mouse
All cameras can be rotated by using the mouse pad.
* mouse left key pressed - xz and yz planes
* mouse right key pressed - xw and yw planes (only 4D cam)
* mouse scroll - zw plane (only 4D cam)

for camera with orbit controls:
* mouse left key - yaw and pitch for 3D camera
* mouse right key - pitch and roll for 4D camera
* mouse scroll - yaw for 4D camera


### sources
the source code was developed based on example code from the moderngl-window library:

camera.py: [https://github.com/moderngl/moderngl-window/blob/master/moderngl_window/scene/camera.py](<https://github.com/moderngl/moderngl-window/blob/master/moderngl_window/scene/camera.py>)

main.py: [https://github.com/moderngl/moderngl-window/blob/master/examples/geometry_cube.py](<https://github.com/moderngl/moderngl-window/blob/master/examples/geometry_cube.py>)

cube.py: [https://github.com/moderngl/moderngl-window/blob/master/moderngl_window/geometry/cube.py](<https://github.com/moderngl/moderngl-window/blob/master/moderngl_window/geometry/cube.py>)

base.py: [https://github.com/moderngl/moderngl-window/blob/master/examples/base.py](<https://github.com/moderngl/moderngl-window/blob/master/examples/base.py>)
