"""
some useful functions like 4D pendant to 3D cross product, rotation matrices
and function for rendering coordinate system axes

"""
import numpy as np
from moderngl_window.opengl.vao import VAO
from moderngl_window.geometry import AttributeNames


def cross(A, B, C):
    """Returns vector that is orthogonal to three given 4-dimensional vectors
    according to http://hollasch.github.io/ray4/Four-Space_Visualization_of_4D_Objects.html#chapter2
    """
    u = (B[0] * C[1]) - (B[1] * C[0])
    v = (B[0] * C[2]) - (B[2] * C[0])
    w = (B[0] * C[3]) - (B[3] * C[0])
    x = (B[1] * C[2]) - (B[2] * C[1])
    y = (B[1] * C[3]) - (B[3] * C[1])
    z = (B[2] * C[3]) - (B[3] * C[2])
    return np.array([ (A[1] * z) - (A[2] * y) + (A[3] * x),
                     -(A[0] * z) + (A[2] * w) - (A[3] * v),
                      (A[0] * y) - (A[1] * x) + (A[3] * u),
                      (A[0] * x) + (A[1] * v) - (A[2] * u)])
    
def rotate_plane(angle: float, plane: np.array):
    """
    plane [x,y,z,w], two 1's
    eg [1,0,1,0] x,z plane
    returns rotation matrix in this plane with given angle 
    """
    s = np.sin(angle)
    c = np.cos(angle)
    
    # x y plane
    if plane[0] == 1 and plane[1] == 1:
        return np.array([[c, -s, 0, 0],
                         [s, c, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype='f4')
    # x z plane
    if plane[0] == 1 and plane[2] == 1:
        return np.array([[c, 0, s, 0],
                         [0, 1, 0, 0],
                         [-s, 0, c, 0],
                         [0, 0, 0, 1]], dtype='f4')
    # x w plane
    if plane[0] == 1 and plane[3] == 1:
        return np.array([[c, 0, 0, s],
                         [0, 1, 0, 0],
                         [0, 0, 1, 0],
                         [-s, 0, 0, c]], dtype='f4')
    # y z plane
    if plane[1] == 1 and plane[2] == 1:
        return np.array([[1, 0, 0, 0],
                         [0, c, -s, 0],
                         [0, s, c, 0],
                         [0, 0, 0, 1]], dtype='f4')
    # y w plane
    if plane[1] == 1 and plane[3] == 1:
        return np.array([[1, 0, 0, 0],
                         [0, c, 0, s],
                         [0, 0, 1, 0],
                         [0, -s, 0, c]], dtype='f4')
    # z w plane
    if plane[2] == 1 and plane[3] == 1:
        return np.array([[1, 0, 0, 0],
                         [0, 1, 0, 0],
                         [0, 0, c, -s],
                         [0, 0, s, c]], dtype='f4')
    
def rotate(angles: np.array):
    """
    rotate around given angles (6) in planes
    xy, xz, yz, xw, yw, zw
    return rotation matrix
    """
    rot = rotate_plane(angles[0], np.array([1,1,0,0])) # xy plane
    rot = np.dot(rot, rotate_plane(angles[1], np.array([1,0,1,0]))) # xz plane
    rot = np.dot(rot, rotate_plane(angles[2], np.array([0,1,1,0]))) # yz plane
    
    rot = np.dot(rot, rotate_plane(angles[3], np.array([1,0,0,1]))) # xw plane
    rot = np.dot(rot, rotate_plane(angles[4], np.array([0,1,0,1]))) # yw plane
    rot = np.dot(rot, rotate_plane(angles[5], np.array([0,0,1,1]))) # zw plane
    return rot
    
def axes_coordinate_system(dim, leng):
    vao = VAO("geometry:axes")
    # Add buffers
    if dim == 4:
        pos = np.array([0, 0, 0, 0, 
                         leng, 0, 0, 0,
                        0, 0, 0, 0,
                         0, leng, 0, 0,
                        0, 0, 0, 0,
                         0, 0, leng, 0,
                        0, 0, 0, 0,
                         0, 0, 0, leng,
                        ], dtype=np.float32)
        vao.buffer(pos, "4f", [AttributeNames.POSITION])
        return vao
    else: #3
        pos = np.array([0, 0, 0, 
                         leng, 0, 0,
                        0, 0, 0,
                         0, leng, 0,
                        0, 0, 0,
                         0, 0, leng
                        ], dtype=np.float32)
        vao.buffer(pos, "3f", [AttributeNames.POSITION])
        return vao