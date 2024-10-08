"""
modified based on moderngl-window library: https://github.com/moderngl/moderngl-window/blob/master/moderngl_window/geometry/cube.py

"""

import numpy

from moderngl_window.opengl.vao import VAO
from moderngl_window.geometry import AttributeNames
import moderngl


def cube(
    size=(1.0, 1.0, 1.0),
    center=(0.0, 0.0, 0.0),
    normals=False,
    uvs=False,
    name=None,
    attr_names=AttributeNames,
    mode=moderngl.TRIANGLES
) -> VAO:
    """Creates a cube VAO with normals and texture coordinates

    Keyword Args:
        width (float): Width of the cube
        height (float): Height of the cube
        depth (float): Depth of the cube
        center: center of the cube as a 3-component tuple
        normals: (bool) Include normals
        uvs: (bool) include uv coordinates
        name (str): Optional name for the VAO
        attr_names (AttributeNames): Attribute names
        mode: triangles/lines
    Returns:
        A :py:class:`moderngl_window.opengl.vao.VAO` instance
    """
    width, height, depth = size
    width, height, depth = width / 2.0, height / 2.0, depth / 2.0
    
    if mode == moderngl.TRIANGLES:
        # fmt: off
        pos = numpy.array([
            center[0] + width, center[1] - height, center[2] + depth,
            center[0] + width, center[1] + height, center[2] + depth,
            center[0] - width, center[1] - height, center[2] + depth,
            center[0] + width, center[1] + height, center[2] + depth, 
            center[0] - width, center[1] + height, center[2] + depth,
            center[0] - width, center[1] - height, center[2] + depth,
            center[0] + width, center[1] - height, center[2] - depth,
            center[0] + width, center[1] + height, center[2] - depth,
            center[0] + width, center[1] - height, center[2] + depth,
            center[0] + width, center[1] + height, center[2] - depth,
            center[0] + width, center[1] + height, center[2] + depth,
            center[0] + width, center[1] - height, center[2] + depth,
            center[0] + width, center[1] - height, center[2] - depth,
            center[0] + width, center[1] - height, center[2] + depth,
            center[0] - width, center[1] - height, center[2] + depth,
            center[0] + width, center[1] - height, center[2] - depth,
            center[0] - width, center[1] - height, center[2] + depth,
            center[0] - width, center[1] - height, center[2] - depth,
            center[0] - width, center[1] - height, center[2] + depth,
            center[0] - width, center[1] + height, center[2] + depth,
            center[0] - width, center[1] + height, center[2] - depth,
            center[0] - width, center[1] - height, center[2] + depth,
            center[0] - width, center[1] + height, center[2] - depth,
            center[0] - width, center[1] - height, center[2] - depth,
            center[0] + width, center[1] + height, center[2] - depth,
            center[0] + width, center[1] - height, center[2] - depth,
            center[0] - width, center[1] - height, center[2] - depth,
            center[0] + width, center[1] + height, center[2] - depth,
            center[0] - width, center[1] - height, center[2] - depth,
            center[0] - width, center[1] + height, center[2] - depth,
            center[0] + width, center[1] + height, center[2] - depth,
            center[0] - width, center[1] + height, center[2] - depth,
            center[0] + width, center[1] + height, center[2] + depth,
            center[0] - width, center[1] + height, center[2] - depth,
            center[0] - width, center[1] + height, center[2] + depth,
            center[0] + width, center[1] + height, center[2] + depth,
        ], dtype=numpy.float32)
    
        if normals:
            normal_data = numpy.array([
                -0, 0, 1,
                -0, 0, 1,
                -0, 0, 1,
                0, 0, 1,
                0, 0, 1,
                0, 0, 1,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
            ], dtype=numpy.float32)
    
        if uvs:
            uvs_data = numpy.array([
                1, 0,
                1, 1,
                0, 0,
                1, 1,
                0, 1,
                0, 0,
                1, 0,
                1, 1,
                0, 0,
                1, 1,
                0, 1,
                0, 0,
                1, 1,
                0, 1,
                0, 0,
                1, 1,
                0, 0,
                1, 0,
                0, 1,
                0, 0,
                1, 0,
                0, 1,
                1, 0,
                1, 1,
                1, 0,
                1, 1,
                0, 1,
                1, 0,
                0, 1,
                0, 0,
                1, 1,
                0, 1,
                1, 0,
                0, 1,
                0, 0,
                1, 0
            ], dtype=numpy.float32)
        # fmt: on
    else:
        pos = numpy.array([ center[0] + width, center[1] + height, center[2] + depth,
                      center[0] - width, center[1] + height, center[2] + depth,
                      center[0] + width, center[1] + height, center[2] + depth,
                      center[0] + width, center[1] - height, center[2] + depth,
                      center[0] + width, center[1] + height, center[2] + depth,
                      center[0] + width, center[1] + height, center[2] - depth,
                      center[0] - width, center[1] + height, center[2] + depth,
                      center[0] - width, center[1] - height, center[2] + depth,
                      center[0] - width, center[1] + height, center[2] + depth,
                      center[0] - width, center[1] + height, center[2] - depth,
                      center[0] + width, center[1] - height, center[2] + depth,
                      center[0] - width, center[1] - height, center[2] + depth,
                      center[0] + width, center[1] - height, center[2] + depth,
                      center[0] + width, center[1] - height, center[2] - depth,
                      center[0] + width, center[1] + height, center[2] - depth,
                      center[0] + width, center[1] - height, center[2] - depth,
                      center[0] + width, center[1] + height, center[2] - depth,
                      center[0] - width, center[1] + height, center[2] - depth,
                      center[0] + width, center[1] - height, center[2] - depth,
                      center[0] - width, center[1] - height, center[2] - depth,
                      center[0] - width, center[1] + height, center[2] - depth,
                      center[0] - width, center[1] - height, center[2] - depth,
                      center[0] - width, center[1] - height, center[2] + depth,
                      center[0] - width, center[1] - height, center[2] - depth,
        ], dtype=numpy.float32)
        normals = False
    vao = VAO(name or "geometry:cube")

    # Add buffers
    vao.buffer(pos, "3f", [attr_names.POSITION])
    if normals:
        vao.buffer(normal_data, "3f", [attr_names.NORMAL])
    if uvs:
        vao.buffer(uvs_data, "2f", [attr_names.TEXCOORD_0])

    return vao

def hypercube(
    size=(1.0, 1.0, 1.0, 1.0),
    center=(0.0, 0.0, 0.0, 0.0),
    normals=False,
    uvs=False,
    name=None,
    attr_names=AttributeNames,
    mode=moderngl.TRIANGLES
) -> VAO:
    """Creates a cube VAO with normals and texture coordinates

    Keyword Args:
        width (float): Width of the cube
        height (float): Height of the cube
        depth (float): Depth of the cube
        center: center of the cube as a 3-component tuple
        normals: (bool) Include normals
        uvs: (bool) include uv coordinates
        name (str): Optional name for the VAO
        attr_names (AttributeNames): Attribute names
        mode: triangles/lines
    Returns:
        A :py:class:`moderngl_window.opengl.vao.VAO` instance
    """
    width, height, depth, fourth = size
    width, height, depth, fourth = width / 2.0, height / 2.0, depth / 2.0, fourth / 2.0
    
    if mode == moderngl.TRIANGLES:
        # fmt: off
        pos = numpy.array([
            center[0] + width, center[1] - height, center[2] + depth, 0.0,
            center[0] + width, center[1] + height, center[2] + depth, 0.0,
            center[0] - width, center[1] - height, center[2] + depth, 0.0,
            center[0] + width, center[1] + height, center[2] + depth, 0.0,
            center[0] - width, center[1] + height, center[2] + depth, 0.0,
            center[0] - width, center[1] - height, center[2] + depth, 0.0,
            center[0] + width, center[1] - height, center[2] - depth, 0.0,
            center[0] + width, center[1] + height, center[2] - depth, 0.0,
            center[0] + width, center[1] - height, center[2] + depth, 0.0,
            center[0] + width, center[1] + height, center[2] - depth, 0.0,
            center[0] + width, center[1] + height, center[2] + depth, 0.0,
            center[0] + width, center[1] - height, center[2] + depth, 0.0,
            center[0] + width, center[1] - height, center[2] - depth, 0.0,
            center[0] + width, center[1] - height, center[2] + depth, 0.0,
            center[0] - width, center[1] - height, center[2] + depth, 0.0,
            center[0] + width, center[1] - height, center[2] - depth, 0.0,
            center[0] - width, center[1] - height, center[2] + depth, 0.0,
            center[0] - width, center[1] - height, center[2] - depth, 0.0,
            center[0] - width, center[1] - height, center[2] + depth, 0.0,
            center[0] - width, center[1] + height, center[2] + depth, 0.0,
            center[0] - width, center[1] + height, center[2] - depth, 0.0,
            center[0] - width, center[1] - height, center[2] + depth, 0.0,
            center[0] - width, center[1] + height, center[2] - depth, 0.0,
            center[0] - width, center[1] - height, center[2] - depth, 0.0,
            center[0] + width, center[1] + height, center[2] - depth, 0.0,
            center[0] + width, center[1] - height, center[2] - depth, 0.0,
            center[0] - width, center[1] - height, center[2] - depth, 0.0,
            center[0] + width, center[1] + height, center[2] - depth, 0.0,
            center[0] - width, center[1] - height, center[2] - depth, 0.0,
            center[0] - width, center[1] + height, center[2] - depth, 0.0,
            center[0] + width, center[1] + height, center[2] - depth, 0.0,
            center[0] - width, center[1] + height, center[2] - depth, 0.0,
            center[0] + width, center[1] + height, center[2] + depth, 0.0,
            center[0] - width, center[1] + height, center[2] - depth, 0.0,
            center[0] - width, center[1] + height, center[2] + depth, 0.0,
            center[0] + width, center[1] + height, center[2] + depth, 0.0,
        ], dtype=numpy.float32)
    
        if normals:
            normal_data = numpy.array([
                -0, 0, 1,
                -0, 0, 1,
                -0, 0, 1,
                0, 0, 1,
                0, 0, 1,
                0, 0, 1,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                -1, -0, 0,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
            ], dtype=numpy.float32)
    
        if uvs:
            uvs_data = numpy.array([
                1, 0,
                1, 1,
                0, 0,
                1, 1,
                0, 1,
                0, 0,
                1, 0,
                1, 1,
                0, 0,
                1, 1,
                0, 1,
                0, 0,
                1, 1,
                0, 1,
                0, 0,
                1, 1,
                0, 0,
                1, 0,
                0, 1,
                0, 0,
                1, 0,
                0, 1,
                1, 0,
                1, 1,
                1, 0,
                1, 1,
                0, 1,
                1, 0,
                0, 1,
                0, 0,
                1, 1,
                0, 1,
                1, 0,
                0, 1,
                0, 0,
                1, 0
            ], dtype=numpy.float32)
        # fmt: on
    else:
        pos = numpy.array([ 
                      center[0] + width, center[1] + height, center[2] + depth, center[3] + fourth,
                       center[0] - width, center[1] + height, center[2] + depth, center[3] + fourth,
                      center[0] + width, center[1] + height, center[2] + depth, center[3] + fourth,
                       center[0] + width, center[1] - height, center[2] + depth, center[3] + fourth,
                      center[0] + width, center[1] + height, center[2] + depth, center[3] + fourth,
                       center[0] + width, center[1] + height, center[2] - depth, center[3] + fourth,
                      center[0] - width, center[1] + height, center[2] + depth, center[3] + fourth,
                       center[0] - width, center[1] - height, center[2] + depth, center[3] + fourth,
                      center[0] - width, center[1] + height, center[2] + depth, center[3] + fourth,
                       center[0] - width, center[1] + height, center[2] - depth, center[3] + fourth,
                      center[0] + width, center[1] - height, center[2] + depth, center[3] + fourth,
                       center[0] - width, center[1] - height, center[2] + depth, center[3] + fourth,
                      center[0] + width, center[1] - height, center[2] + depth, center[3] + fourth,
                       center[0] + width, center[1] - height, center[2] - depth, center[3] + fourth,
                      center[0] + width, center[1] + height, center[2] - depth, center[3] + fourth,
                       center[0] + width, center[1] - height, center[2] - depth, center[3] + fourth,
                      center[0] + width, center[1] + height, center[2] - depth, center[3] + fourth,
                       center[0] - width, center[1] + height, center[2] - depth, center[3] + fourth,
                      center[0] + width, center[1] - height, center[2] - depth, center[3] + fourth,
                       center[0] - width, center[1] - height, center[2] - depth, center[3] + fourth,
                      center[0] - width, center[1] + height, center[2] - depth, center[3] + fourth,
                       center[0] - width, center[1] - height, center[2] - depth, center[3] + fourth,
                      center[0] - width, center[1] - height, center[2] + depth, center[3] + fourth,
                       center[0] - width, center[1] - height, center[2] - depth, center[3] + fourth,
                      
                      center[0] + width, center[1] + height, center[2] + depth, center[3] - fourth,
                       center[0] - width, center[1] + height, center[2] + depth, center[3] - fourth,
                      center[0] + width, center[1] + height, center[2] + depth, center[3] - fourth,
                       center[0] + width, center[1] - height, center[2] + depth, center[3] - fourth,
                      center[0] + width, center[1] + height, center[2] + depth, center[3] - fourth,
                       center[0] + width, center[1] + height, center[2] - depth, center[3] - fourth,
                      center[0] - width, center[1] + height, center[2] + depth, center[3] - fourth,
                       center[0] - width, center[1] - height, center[2] + depth, center[3] - fourth,
                      center[0] - width, center[1] + height, center[2] + depth, center[3] - fourth,
                       center[0] - width, center[1] + height, center[2] - depth, center[3] - fourth,
                      center[0] + width, center[1] - height, center[2] + depth, center[3] - fourth,
                       center[0] - width, center[1] - height, center[2] + depth, center[3] - fourth,
                      center[0] + width, center[1] - height, center[2] + depth, center[3] - fourth,
                       center[0] + width, center[1] - height, center[2] - depth, center[3] - fourth,
                      center[0] + width, center[1] + height, center[2] - depth, center[3] - fourth,
                       center[0] + width, center[1] - height, center[2] - depth, center[3] - fourth,
                      center[0] + width, center[1] + height, center[2] - depth, center[3] - fourth,
                       center[0] - width, center[1] + height, center[2] - depth, center[3] - fourth,
                      center[0] + width, center[1] - height, center[2] - depth, center[3] - fourth,
                       center[0] - width, center[1] - height, center[2] - depth, center[3] - fourth,
                      center[0] - width, center[1] + height, center[2] - depth, center[3] - fourth,
                       center[0] - width, center[1] - height, center[2] - depth, center[3] - fourth,
                      center[0] - width, center[1] - height, center[2] + depth, center[3] - fourth,
                       center[0] - width, center[1] - height, center[2] - depth, center[3] - fourth,
                      
                      center[0] + width, center[1] + height, center[2] + depth, center[3] - fourth,
                       center[0] + width, center[1] + height, center[2] + depth, center[3] + fourth,
                      center[0] - width, center[1] + height, center[2] + depth, center[3] - fourth,
                       center[0] - width, center[1] + height, center[2] + depth, center[3] + fourth,
                      center[0] + width, center[1] - height, center[2] + depth, center[3] - fourth,
                       center[0] + width, center[1] - height, center[2] + depth, center[3] + fourth,
                      center[0] + width, center[1] + height, center[2] - depth, center[3] - fourth,
                       center[0] + width, center[1] + height, center[2] - depth, center[3] + fourth,
                      
                        center[0] - width, center[1] + height, center[2] - depth, center[3] - fourth,
                       center[0] - width, center[1] + height, center[2] - depth, center[3] + fourth,
                      center[0] + width, center[1] - height, center[2] - depth, center[3] - fourth,
                       center[0] + width, center[1] - height, center[2] - depth, center[3] + fourth,
                      center[0] - width, center[1] - height, center[2] + depth, center[3] - fourth,
                       center[0] - width, center[1] - height, center[2] + depth, center[3] + fourth,
                      center[0] - width, center[1] - height, center[2] - depth, center[3] - fourth,
                       center[0] - width, center[1] - height, center[2] - depth, center[3] + fourth,
        ], dtype=numpy.float32)
        normals = False
    vao = VAO(name or "geometry:hypercube")

    # Add buffers
    vao.buffer(pos, "4f", [attr_names.POSITION])
    if normals:
        vao.buffer(normal_data, "3f", [attr_names.NORMAL])
    if uvs:
        vao.buffer(uvs_data, "2f", [attr_names.TEXCOORD_0])

    return vao
