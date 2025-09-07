



import functools

import inspect

import math

from numbers import Number, Real

import textwrap

from types import SimpleNamespace

from collections import namedtuple

from matplotlib.transforms import Affine2D



import numpy as np



import matplotlib as mpl

from . import (_api, artist, cbook, colors, _docstring, hatch as mhatch,

               lines as mlines, transforms)

from .bezier import (

    NonIntersectingPathException, get_cos_sin, get_intersection,

    get_parallels, inside_circle, make_wedged_bezier2,

    split_bezier_intersecting_with_closedpath, split_path_inout)

from .path import Path

from ._enums import JoinStyle, CapStyle





@_docstring.interpd

@_api.define_aliases({

    "antialiased": ["aa"],

    "edgecolor": ["ec"],

    "facecolor": ["fc"],

    "linestyle": ["ls"],

    "linewidth": ["lw"],

})

class Patch(artist.Artist):

    

    zorder = 1



                                                   

                                 

    _edge_default = False



    def __init__(self, *,

                 edgecolor=None,

                 facecolor=None,

                 color=None,

                 linewidth=None,

                 linestyle=None,

                 antialiased=None,

                 hatch=None,

                 fill=True,

                 capstyle=None,

                 joinstyle=None,

                 hatchcolor=None,

                 **kwargs):

        

        super().__init__()



        if linestyle is None:

            linestyle = "solid"

        if capstyle is None:

            capstyle = CapStyle.butt

        if joinstyle is None:

            joinstyle = JoinStyle.miter



        self._hatch_linewidth = mpl.rcParams['hatch.linewidth']

        self._fill = bool(fill)                                 

        if color is not None:

            if edgecolor is not None or facecolor is not None:

                _api.warn_external(

                    "Setting the 'color' property will override "

                    "the edgecolor or facecolor properties.")

            self.set_color(color)

        else:

            self.set_edgecolor(edgecolor)

            self.set_hatchcolor(hatchcolor)

            self.set_facecolor(facecolor)



        self._linewidth = 0

        self._unscaled_dash_pattern = (0, None)                

        self._dash_pattern = (0, None)                                      



        self.set_linestyle(linestyle)

        self.set_linewidth(linewidth)

        self.set_antialiased(antialiased)

        self.set_hatch(hatch)

        self.set_capstyle(capstyle)

        self.set_joinstyle(joinstyle)



        if len(kwargs):

            self._internal_update(kwargs)



    def get_verts(self):

        

        trans = self.get_transform()

        path = self.get_path()

        polygons = path.to_polygons(trans)

        if len(polygons):

            return polygons[0]

        return []



    def _process_radius(self, radius):

        if radius is not None:

            return radius

        if isinstance(self._picker, Number):

            _radius = self._picker

        else:

            if self.get_edgecolor()[3] == 0:

                _radius = 0

            else:

                _radius = self.get_linewidth()

        return _radius



    def contains(self, mouseevent, radius=None):

        

        if self._different_canvas(mouseevent):

            return False, {}

        radius = self._process_radius(radius)

        codes = self.get_path().codes

        if codes is not None:

            vertices = self.get_path().vertices

                                                                        

                                                                           

            idxs, = np.where(codes == Path.MOVETO)

                                                  

            idxs = idxs[1:]

            subpaths = map(

                Path, np.split(vertices, idxs), np.split(codes, idxs))

        else:

            subpaths = [self.get_path()]

        inside = any(

            subpath.contains_point(

                (mouseevent.x, mouseevent.y), self.get_transform(), radius)

            for subpath in subpaths)

        return inside, {}



    def contains_point(self, point, radius=None):

        

        radius = self._process_radius(radius)

        return self.get_path().contains_point(point,

                                              self.get_transform(),

                                              radius)



    def contains_points(self, points, radius=None):

        

        radius = self._process_radius(radius)

        return self.get_path().contains_points(points,

                                               self.get_transform(),

                                               radius)



    def update_from(self, other):

                              

        super().update_from(other)

                                                                           

                                                         

        self._edgecolor = other._edgecolor

        self._facecolor = other._facecolor

        self._original_edgecolor = other._original_edgecolor

        self._original_facecolor = other._original_facecolor

        self._fill = other._fill

        self._hatch = other._hatch

        self._hatch_color = other._hatch_color

        self._original_hatchcolor = other._original_hatchcolor

        self._unscaled_dash_pattern = other._unscaled_dash_pattern

        self.set_linewidth(other._linewidth)                           

        self.set_transform(other.get_data_transform())

                                                                              

                                          

        self._transformSet = other.is_transform_set()



    def get_extents(self):

        

        return self.get_path().get_extents(self.get_transform())



    def get_transform(self):

        

        return self.get_patch_transform() + artist.Artist.get_transform(self)



    def get_data_transform(self):

        

        return artist.Artist.get_transform(self)



    def get_patch_transform(self):

        

        return transforms.IdentityTransform()



    def get_antialiased(self):

        

        return self._antialiased



    def get_edgecolor(self):

        

        return self._edgecolor



    def get_facecolor(self):

        

        return self._facecolor



    def get_hatchcolor(self):

        

        if self._hatch_color == 'edge':

            if self._edgecolor[3] == 0:                     

                return colors.to_rgba(mpl.rcParams['patch.edgecolor'])

            return self.get_edgecolor()

        return self._hatch_color



    def get_linewidth(self):

        

        return self._linewidth



    def get_linestyle(self):

        

        return self._linestyle



    def set_antialiased(self, aa):

        

        self._antialiased = mpl._val_or_rc(aa, 'patch.antialiased')

        self.stale = True



    def _set_edgecolor(self, color):

        if color is None:

            if (mpl.rcParams['patch.force_edgecolor'] or

                    not self._fill or self._edge_default):

                color = mpl.rcParams['patch.edgecolor']

            else:

                color = 'none'



        self._edgecolor = colors.to_rgba(color, self._alpha)

        self.stale = True



    def set_edgecolor(self, color):

        

        self._original_edgecolor = color

        self._set_edgecolor(color)



    def _set_facecolor(self, color):

        color = mpl._val_or_rc(color, 'patch.facecolor')

        alpha = self._alpha if self._fill else 0

        self._facecolor = colors.to_rgba(color, alpha)

        self.stale = True



    def set_facecolor(self, color):

        

        self._original_facecolor = color

        self._set_facecolor(color)



    def set_color(self, c):

        

        self.set_edgecolor(c)

        self.set_hatchcolor(c)

        self.set_facecolor(c)



    def _set_hatchcolor(self, color):

        color = mpl._val_or_rc(color, 'hatch.color')

        if cbook._str_equal(color, 'edge'):

            self._hatch_color = 'edge'

        else:

            self._hatch_color = colors.to_rgba(color, self._alpha)

        self.stale = True



    def set_hatchcolor(self, color):

        

        self._original_hatchcolor = color

        self._set_hatchcolor(color)



    def set_alpha(self, alpha):

                             

        super().set_alpha(alpha)

        self._set_facecolor(self._original_facecolor)

        self._set_edgecolor(self._original_edgecolor)

        self._set_hatchcolor(self._original_hatchcolor)

                               



    def set_linewidth(self, w):

        

        w = mpl._val_or_rc(w, 'patch.linewidth')

        w = float(w)

        self._linewidth = w

        self._dash_pattern = mlines._scale_dashes(*self._unscaled_dash_pattern, w)

        self.stale = True



    def set_linestyle(self, ls):

        

        if ls is None:

            ls = "solid"

        if ls in [' ', '', 'none']:

            ls = 'None'

        self._linestyle = ls

        self._unscaled_dash_pattern = mlines._get_dash_pattern(ls)

        self._dash_pattern = mlines._scale_dashes(

            *self._unscaled_dash_pattern, self._linewidth)

        self.stale = True



    def set_fill(self, b):

        

        self._fill = bool(b)

        self._set_facecolor(self._original_facecolor)

        self._set_edgecolor(self._original_edgecolor)

        self._set_hatchcolor(self._original_hatchcolor)

        self.stale = True



    def get_fill(self):

        

        return self._fill



                                                              

                                                             

                

    fill = property(get_fill, set_fill)



    @_docstring.interpd

    def set_capstyle(self, s):

        

        cs = CapStyle(s)

        self._capstyle = cs

        self.stale = True



    def get_capstyle(self):

        

        return self._capstyle.name



    @_docstring.interpd

    def set_joinstyle(self, s):

        

        js = JoinStyle(s)

        self._joinstyle = js

        self.stale = True



    def get_joinstyle(self):

        

        return self._joinstyle.name



    def set_hatch(self, hatch):

        

                                                     

        mhatch._validate_hatch_pattern(hatch)

        self._hatch = hatch

        self.stale = True



    def get_hatch(self):

        

        return self._hatch



    def set_hatch_linewidth(self, lw):

        

        self._hatch_linewidth = lw



    def get_hatch_linewidth(self):

        

        return self._hatch_linewidth



    def _draw_paths_with_artist_properties(

            self, renderer, draw_path_args_list):

        



        renderer.open_group('patch', self.get_gid())

        gc = renderer.new_gc()



        gc.set_foreground(self._edgecolor, isRGBA=True)



        lw = self._linewidth

        if self._edgecolor[3] == 0 or self._linestyle == 'None':

            lw = 0

        gc.set_linewidth(lw)

        gc.set_dashes(*self._dash_pattern)

        gc.set_capstyle(self._capstyle)

        gc.set_joinstyle(self._joinstyle)



        gc.set_antialiased(self._antialiased)

        self._set_gc_clip(gc)

        gc.set_url(self._url)

        gc.set_snap(self.get_snap())



        gc.set_alpha(self._alpha)



        if self._hatch:

            gc.set_hatch(self._hatch)

            gc.set_hatch_color(self.get_hatchcolor())

            gc.set_hatch_linewidth(self._hatch_linewidth)



        if self.get_sketch_params() is not None:

            gc.set_sketch_params(*self.get_sketch_params())



        if self.get_path_effects():

            from matplotlib.patheffects import PathEffectRenderer

            renderer = PathEffectRenderer(self.get_path_effects(), renderer)



        for draw_path_args in draw_path_args_list:

            renderer.draw_path(gc, *draw_path_args)



        gc.restore()

        renderer.close_group('patch')

        self.stale = False



    @artist.allow_rasterization

    def draw(self, renderer):

                             

        if not self.get_visible():

            return

        path = self.get_path()

        transform = self.get_transform()

        tpath = transform.transform_path_non_affine(path)

        affine = transform.get_affine()

        self._draw_paths_with_artist_properties(

            renderer,

            [(tpath, affine,

                                                                     

                                                                 

                                                  

              self._facecolor if self._facecolor[3] else None)])



    def get_path(self):

        

        raise NotImplementedError('Derived must override')



    def get_window_extent(self, renderer=None):

        return self.get_path().get_extents(self.get_transform())



    def _convert_xy_units(self, xy):

        

        x = self.convert_xunits(xy[0])

        y = self.convert_yunits(xy[1])

        return x, y





class Shadow(Patch):

    def __str__(self):

        return f"Shadow({self.patch})"



    @_docstring.interpd

    def __init__(self, patch, ox, oy, *, shade=0.7, **kwargs):

        

        super().__init__()

        self.patch = patch

        self._ox, self._oy = ox, oy

        self._shadow_transform = transforms.Affine2D()



        self.update_from(self.patch)

        if not 0 <= shade <= 1:

            raise ValueError("shade must be between 0 and 1.")

        color = (1 - shade) * np.asarray(colors.to_rgb(self.patch.get_facecolor()))

        self.update({'facecolor': color, 'edgecolor': color, 'alpha': 0.5,

                                                                              

                     'zorder': np.nextafter(self.patch.zorder, -np.inf),

                     **kwargs})



    def _update_transform(self, renderer):

        ox = renderer.points_to_pixels(self._ox)

        oy = renderer.points_to_pixels(self._oy)

        self._shadow_transform.clear().translate(ox, oy)



    def get_path(self):

        return self.patch.get_path()



    def get_patch_transform(self):

        return self.patch.get_patch_transform() + self._shadow_transform



    def draw(self, renderer):

        self._update_transform(renderer)

        super().draw(renderer)





class Rectangle(Patch):

    



    def __str__(self):

        pars = self._x0, self._y0, self._width, self._height, self.angle

        fmt = "Rectangle(xy=(%g, %g), width=%g, height=%g, angle=%g)"

        return fmt % pars



    @_docstring.interpd

    def __init__(self, xy, width, height, *,

                 angle=0.0, rotation_point='xy', **kwargs):

        

        super().__init__(**kwargs)

        self._x0 = xy[0]

        self._y0 = xy[1]

        self._width = width

        self._height = height

        self.angle = float(angle)

        self.rotation_point = rotation_point

                                                                    

                                                                        

                                                                            

                                                                         

                                                                       

                                  

        self._aspect_ratio_correction = 1.0

        self._convert_units()                        



    def get_path(self):

        

        return Path.unit_rectangle()



    def _convert_units(self):

        

        x0 = self.convert_xunits(self._x0)

        y0 = self.convert_yunits(self._y0)

        x1 = self.convert_xunits(self._x0 + self._width)

        y1 = self.convert_yunits(self._y0 + self._height)

        return x0, y0, x1, y1



    def get_patch_transform(self):

                                                                        

                                                                          

                                                                           

                                         

        bbox = self.get_bbox()

        if self.rotation_point == 'center':

            width, height = bbox.x1 - bbox.x0, bbox.y1 - bbox.y0

            rotation_point = bbox.x0 + width / 2., bbox.y0 + height / 2.

        elif self.rotation_point == 'xy':

            rotation_point = bbox.x0, bbox.y0

        else:

            rotation_point = self.rotation_point

        return transforms.BboxTransformTo(bbox)
                + transforms.Affine2D()
                .translate(-rotation_point[0], -rotation_point[1])
                .scale(1, self._aspect_ratio_correction)
                .rotate_deg(self.angle)
                .scale(1, 1 / self._aspect_ratio_correction)
                .translate(*rotation_point)



    @property

    def rotation_point(self):

        

        return self._rotation_point



    @rotation_point.setter

    def rotation_point(self, value):

        if value in ['center', 'xy'] or (

                isinstance(value, tuple) and len(value) == 2 and

                isinstance(value[0], Real) and isinstance(value[1], Real)

                ):

            self._rotation_point = value

        else:

            raise ValueError("`rotation_point` must be one of "

                             "{'xy', 'center', (number, number)}.")



    def get_x(self):

        

        return self._x0



    def get_y(self):

        

        return self._y0



    def get_xy(self):

        

        return self._x0, self._y0



    def get_corners(self):

        

        return self.get_patch_transform().transform(

            [(0, 0), (1, 0), (1, 1), (0, 1)])



    def get_center(self):

        

        return self.get_patch_transform().transform((0.5, 0.5))



    def get_width(self):

        

        return self._width



    def get_height(self):

        

        return self._height



    def get_angle(self):

        

        return self.angle



    def set_x(self, x):

        

        self._x0 = x

        self.stale = True



    def set_y(self, y):

        

        self._y0 = y

        self.stale = True



    def set_angle(self, angle):

        

        self.angle = angle

        self.stale = True



    def set_xy(self, xy):

        

        self._x0, self._y0 = xy

        self.stale = True



    def set_width(self, w):

        

        self._width = w

        self.stale = True



    def set_height(self, h):

        

        self._height = h

        self.stale = True



    def set_bounds(self, *args):

        

        if len(args) == 1:

            l, b, w, h = args[0]

        else:

            l, b, w, h = args

        self._x0 = l

        self._y0 = b

        self._width = w

        self._height = h

        self.stale = True



    def get_bbox(self):

        

        return transforms.Bbox.from_extents(*self._convert_units())



    xy = property(get_xy, set_xy)





class RegularPolygon(Patch):

    



    def __str__(self):

        s = "RegularPolygon((%g, %g), %d, radius=%g, orientation=%g)"

        return s % (self.xy[0], self.xy[1], self.numvertices, self.radius,

                    self.orientation)



    @_docstring.interpd

    def __init__(self, xy, numVertices, *,

                 radius=5, orientation=0, **kwargs):

        

        self.xy = xy

        self.numvertices = numVertices

        self.orientation = orientation

        self.radius = radius

        self._path = Path.unit_regular_polygon(numVertices)

        self._patch_transform = transforms.Affine2D()

        super().__init__(**kwargs)



    def get_path(self):

        return self._path



    def get_patch_transform(self):

        return self._patch_transform.clear()
            .scale(self.radius)
            .rotate(self.orientation)
            .translate(*self.xy)





class PathPatch(Patch):

    



    _edge_default = True



    def __str__(self):

        s = "PathPatch%d((%g, %g) ...)"

        return s % (len(self._path.vertices), *tuple(self._path.vertices[0]))



    @_docstring.interpd

    def __init__(self, path, **kwargs):

        

        super().__init__(**kwargs)

        self._path = path



    def get_path(self):

        return self._path



    def set_path(self, path):

        self._path = path





class StepPatch(PathPatch):

    



    _edge_default = False



    @_docstring.interpd

    def __init__(self, values, edges, *,

                 orientation='vertical', baseline=0, **kwargs):

        

        self.orientation = orientation

        self._edges = np.asarray(edges)

        self._values = np.asarray(values)

        self._baseline = np.asarray(baseline) if baseline is not None else None

        self._update_path()

        super().__init__(self._path, **kwargs)



    def _update_path(self):

        if np.isnan(np.sum(self._edges)):

            raise ValueError('Nan values in "edges" are disallowed')

        if self._edges.size - 1 != self._values.size:

            raise ValueError('Size mismatch between "values" and "edges". '

                             "Expected `len(values) + 1 == len(edges)`, but "

                             f"`len(values) = {self._values.size}` and "

                             f"`len(edges) = {self._edges.size}`.")

                                                                        

        verts, codes = [np.empty((0, 2))], [np.empty(0, dtype=Path.code_type)]



        _nan_mask = np.isnan(self._values)

        if self._baseline is not None:

            _nan_mask |= np.isnan(self._baseline)

        for idx0, idx1 in cbook.contiguous_regions(~_nan_mask):

            x = np.repeat(self._edges[idx0:idx1+1], 2)

            y = np.repeat(self._values[idx0:idx1], 2)

            if self._baseline is None:

                y = np.concatenate([y[:1], y, y[-1:]])

            elif self._baseline.ndim == 0:                         

                y = np.concatenate([[self._baseline], y, [self._baseline]])

            elif self._baseline.ndim == 1:                  

                base = np.repeat(self._baseline[idx0:idx1], 2)[::-1]

                x = np.concatenate([x, x[::-1]])

                y = np.concatenate([base[-1:], y, base[:1],

                                    base[:1], base, base[-1:]])

            else:               

                raise ValueError('Invalid `baseline` specified')

            if self.orientation == 'vertical':

                xy = np.column_stack([x, y])

            else:

                xy = np.column_stack([y, x])

            verts.append(xy)

            codes.append([Path.MOVETO] + [Path.LINETO]*(len(xy)-1))

        self._path = Path(np.concatenate(verts), np.concatenate(codes))



    def get_data(self):

        

        StairData = namedtuple('StairData', 'values edges baseline')

        return StairData(self._values, self._edges, self._baseline)



    def set_data(self, values=None, edges=None, baseline=None):

        

        if values is None and edges is None and baseline is None:

            raise ValueError("Must set *values*, *edges* or *baseline*.")

        if values is not None:

            self._values = np.asarray(values)

        if edges is not None:

            self._edges = np.asarray(edges)

        if baseline is not None:

            self._baseline = np.asarray(baseline)

        self._update_path()

        self.stale = True





class Polygon(Patch):

    



    def __str__(self):

        if len(self._path.vertices):

            s = "Polygon%d((%g, %g) ...)"

            return s % (len(self._path.vertices), *self._path.vertices[0])

        else:

            return "Polygon0()"



    @_docstring.interpd

    def __init__(self, xy, *, closed=True, **kwargs):

        

        super().__init__(**kwargs)

        self._closed = closed

        self.set_xy(xy)



    def get_path(self):

        

        return self._path



    def get_closed(self):

        

        return self._closed



    def set_closed(self, closed):

        

        if self._closed == bool(closed):

            return

        self._closed = bool(closed)

        self.set_xy(self.get_xy())

        self.stale = True



    def get_xy(self):

        

        return self._path.vertices



    def set_xy(self, xy):

        

        xy = np.asarray(xy)

        nverts, _ = xy.shape

        if self._closed:

                                                                              

                                                                            

                                                                           

                  

            if nverts == 1 or nverts > 1 and (xy[0] != xy[-1]).any():

                xy = np.concatenate([xy, [xy[0]]])

        else:

                                                                              

                                                                             

            if nverts > 2 and (xy[0] == xy[-1]).all():

                xy = xy[:-1]

        self._path = Path(xy, closed=self._closed)

        self.stale = True



    xy = property(get_xy, set_xy,

                  doc='The vertices of the path as a (N, 2) array.')





class Wedge(Patch):

    



    def __str__(self):

        pars = (self.center[0], self.center[1], self.r,

                self.theta1, self.theta2, self.width)

        fmt = "Wedge(center=(%g, %g), r=%g, theta1=%g, theta2=%g, width=%s)"

        return fmt % pars



    @_docstring.interpd

    def __init__(self, center, r, theta1, theta2, *, width=None, **kwargs):

        

        super().__init__(**kwargs)

        self.center = center

        self.r, self.width = r, width

        self.theta1, self.theta2 = theta1, theta2

        self._patch_transform = transforms.IdentityTransform()

        self._recompute_path()



    def _recompute_path(self):

                                                                            

        if abs((self.theta2 - self.theta1) - 360) <= 1e-12:

            theta1, theta2 = 0, 360

            connector = Path.MOVETO

        else:

            theta1, theta2 = self.theta1, self.theta2

            connector = Path.LINETO



                             

        arc = Path.arc(theta1, theta2)



        if self.width is not None:

                                                          

                                                          

            v1 = arc.vertices

            v2 = arc.vertices[::-1] * (self.r - self.width) / self.r

            v = np.concatenate([v1, v2, [(0, 0)]])

            c = [*arc.codes, connector, *arc.codes[1:], Path.CLOSEPOLY]

        else:

                                              

            v = np.concatenate([arc.vertices, [(0, 0), (0, 0)]])

            c = [*arc.codes, connector, Path.CLOSEPOLY]



                                                          

        self._path = Path(v * self.r + self.center, c)



    def set_center(self, center):

        self._path = None

        self.center = center

        self.stale = True



    def set_radius(self, radius):

        self._path = None

        self.r = radius

        self.stale = True



    def set_theta1(self, theta1):

        self._path = None

        self.theta1 = theta1

        self.stale = True



    def set_theta2(self, theta2):

        self._path = None

        self.theta2 = theta2

        self.stale = True



    def set_width(self, width):

        self._path = None

        self.width = width

        self.stale = True



    def get_path(self):

        if self._path is None:

            self._recompute_path()

        return self._path





                                                     

class Arrow(Patch):

    



    def __str__(self):

        return "Arrow()"



    _path = Path._create_closed([

        [0.0, 0.1], [0.0, -0.1], [0.8, -0.1], [0.8, -0.3], [1.0, 0.0],

        [0.8, 0.3], [0.8, 0.1]])



    @_docstring.interpd

    def __init__(self, x, y, dx, dy, *, width=1.0, **kwargs):

        

        super().__init__(**kwargs)

        self.set_data(x, y, dx, dy, width)



    def get_path(self):

        return self._path



    def get_patch_transform(self):

        return self._patch_transform



    def set_data(self, x=None, y=None, dx=None, dy=None, width=None):

        

        if x is not None:

            self._x = x

        if y is not None:

            self._y = y

        if dx is not None:

            self._dx = dx

        if dy is not None:

            self._dy = dy

        if width is not None:

            self._width = width

        self._patch_transform = (

            transforms.Affine2D()

            .scale(np.hypot(self._dx, self._dy), self._width)

            .rotate(np.arctan2(self._dy, self._dx))

            .translate(self._x, self._y)

            .frozen())





class FancyArrow(Polygon):

    



    _edge_default = True



    def __str__(self):

        return "FancyArrow()"



    @_docstring.interpd

    def __init__(self, x, y, dx, dy, *,

                 width=0.001, length_includes_head=False, head_width=None,

                 head_length=None, shape='full', overhang=0,

                 head_starts_at_zero=False, **kwargs):

        

        self._x = x

        self._y = y

        self._dx = dx

        self._dy = dy

        self._width = width

        self._length_includes_head = length_includes_head

        self._head_width = head_width

        self._head_length = head_length

        self._shape = shape

        self._overhang = overhang

        self._head_starts_at_zero = head_starts_at_zero

        self._make_verts()

        super().__init__(self.verts, closed=True, **kwargs)



    def set_data(self, *, x=None, y=None, dx=None, dy=None, width=None,

                 head_width=None, head_length=None):

        

        if x is not None:

            self._x = x

        if y is not None:

            self._y = y

        if dx is not None:

            self._dx = dx

        if dy is not None:

            self._dy = dy

        if width is not None:

            self._width = width

        if head_width is not None:

            self._head_width = head_width

        if head_length is not None:

            self._head_length = head_length

        self._make_verts()

        self.set_xy(self.verts)



    def _make_verts(self):

        if self._head_width is None:

            head_width = 3 * self._width

        else:

            head_width = self._head_width

        if self._head_length is None:

            head_length = 1.5 * head_width

        else:

            head_length = self._head_length



        distance = np.hypot(self._dx, self._dy)



        if self._length_includes_head:

            length = distance

        else:

            length = distance + head_length

        if np.size(length) == 0:

            self.verts = np.empty([0, 2])                            

        else:

                                                                

            hw, hl = head_width, head_length

            hs, lw = self._overhang, self._width

            left_half_arrow = np.array([

                [0.0, 0.0],                      

                [-hl, -hw / 2],                       

                [-hl * (1 - hs), -lw / 2],              

                [-length, -lw / 2],                      

                [-length, 0],

            ])

                                                                      

            if not self._length_includes_head:

                left_half_arrow += [head_length, 0]

                                                                      

            if self._head_starts_at_zero:

                left_half_arrow += [head_length / 2, 0]

                                                            

            if self._shape == 'left':

                coords = left_half_arrow

            else:

                right_half_arrow = left_half_arrow * [1, -1]

                if self._shape == 'right':

                    coords = right_half_arrow

                elif self._shape == 'full':

                                                                       

                                                                         

                                                       

                    coords = np.concatenate([left_half_arrow[:-1],

                                             right_half_arrow[-2::-1]])

                else:

                    raise ValueError(f"Got unknown shape: {self._shape!r}")

            if distance != 0:

                cx = self._dx / distance

                sx = self._dy / distance

            else:

                                              

                cx, sx = 0, 1

            M = [[cx, sx], [-sx, cx]]

            self.verts = np.dot(coords, M) + [

                self._x + self._dx,

                self._y + self._dy,

            ]





_docstring.interpd.register(

    FancyArrow="\n".join(

        (inspect.getdoc(FancyArrow.__init__) or "").splitlines()[2:]))





class CirclePolygon(RegularPolygon):

    



    def __str__(self):

        s = "CirclePolygon((%g, %g), radius=%g, resolution=%d)"

        return s % (self.xy[0], self.xy[1], self.radius, self.numvertices)



    @_docstring.interpd

    def __init__(self, xy, radius=5, *,

                 resolution=20,                          

                 ** kwargs):

        

        super().__init__(

            xy, resolution, radius=radius, orientation=0, **kwargs)





class Ellipse(Patch):

    



    def __str__(self):

        pars = (self._center[0], self._center[1],

                self.width, self.height, self.angle)

        fmt = "Ellipse(xy=(%s, %s), width=%s, height=%s, angle=%s)"

        return fmt % pars



    @_docstring.interpd

    def __init__(self, xy, width, height, *, angle=0, **kwargs):

        

        super().__init__(**kwargs)



        self._center = xy

        self._width, self._height = width, height

        self._angle = angle

        self._path = Path.unit_circle()

                                                                  

                                                                        

                                                                            

                                                                         

                                     

        self._aspect_ratio_correction = 1.0

                                                                        

        self._patch_transform = transforms.IdentityTransform()



    def _recompute_transform(self):

        

        center = (self.convert_xunits(self._center[0]),

                  self.convert_yunits(self._center[1]))

        width = self.convert_xunits(self._width)

        height = self.convert_yunits(self._height)

        self._patch_transform = transforms.Affine2D()
            .scale(width * 0.5, height * 0.5 * self._aspect_ratio_correction)
            .rotate_deg(self.angle)
            .scale(1, 1 / self._aspect_ratio_correction)
            .translate(*center)



    def get_path(self):

        

        return self._path



    def get_patch_transform(self):

        self._recompute_transform()

        return self._patch_transform



    def set_center(self, xy):

        

        self._center = xy

        self.stale = True



    def get_center(self):

        

        return self._center



    center = property(get_center, set_center)



    def set_width(self, width):

        

        self._width = width

        self.stale = True



    def get_width(self):

        

        return self._width



    width = property(get_width, set_width)



    def set_height(self, height):

        

        self._height = height

        self.stale = True



    def get_height(self):

        

        return self._height



    height = property(get_height, set_height)



    def set_angle(self, angle):

        

        self._angle = angle

        self.stale = True



    def get_angle(self):

        

        return self._angle



    angle = property(get_angle, set_angle)



    def get_corners(self):

        

        return self.get_patch_transform().transform(

            [(-1, -1), (1, -1), (1, 1), (-1, 1)])



    def get_vertices(self):

        

        if self.width < self.height:

            ret = self.get_patch_transform().transform([(0, 1), (0, -1)])

        else:

            ret = self.get_patch_transform().transform([(1, 0), (-1, 0)])

        return [tuple(x) for x in ret]



    def get_co_vertices(self):

        

        if self.width < self.height:

            ret = self.get_patch_transform().transform([(1, 0), (-1, 0)])

        else:

            ret = self.get_patch_transform().transform([(0, 1), (0, -1)])

        return [tuple(x) for x in ret]





class Annulus(Patch):

    



    @_docstring.interpd

    def __init__(self, xy, r, width, angle=0.0, **kwargs):

        

        super().__init__(**kwargs)



        self.set_radii(r)

        self.center = xy

        self.width = width

        self.angle = angle

        self._path = None



    def __str__(self):

        if self.a == self.b:

            r = self.a

        else:

            r = (self.a, self.b)



        return "Annulus(xy=(%s, %s), r=%s, width=%s, angle=%s)" %
                (*self.center, r, self.width, self.angle)



    def set_center(self, xy):

        

        self._center = xy

        self._path = None

        self.stale = True



    def get_center(self):

        

        return self._center



    center = property(get_center, set_center)



    def set_width(self, width):

        

        if width > min(self.a, self.b):

            raise ValueError(

                'Width of annulus must be less than or equal to semi-minor axis')



        self._width = width

        self._path = None

        self.stale = True



    def get_width(self):

        

        return self._width



    width = property(get_width, set_width)



    def set_angle(self, angle):

        

        self._angle = angle

        self._path = None

        self.stale = True



    def get_angle(self):

        

        return self._angle



    angle = property(get_angle, set_angle)



    def set_semimajor(self, a):

        

        self.a = float(a)

        self._path = None

        self.stale = True



    def set_semiminor(self, b):

        

        self.b = float(b)

        self._path = None

        self.stale = True



    def set_radii(self, r):

        

        if np.shape(r) == (2,):

            self.a, self.b = r

        elif np.shape(r) == ():

            self.a = self.b = float(r)

        else:

            raise ValueError("Parameter 'r' must be one or two floats.")



        self._path = None

        self.stale = True



    def get_radii(self):

        

        return self.a, self.b



    radii = property(get_radii, set_radii)



    def _transform_verts(self, verts, a, b):

        return transforms.Affine2D()
            .scale(*self._convert_xy_units((a, b)))
            .rotate_deg(self.angle)
            .translate(*self._convert_xy_units(self.center))
            .transform(verts)



    def _recompute_path(self):

                      

        arc = Path.arc(0, 360)



                                             

                                                      

        a, b, w = self.a, self.b, self.width

        v1 = self._transform_verts(arc.vertices, a, b)

        v2 = self._transform_verts(arc.vertices[::-1], a - w, b - w)

        v = np.vstack([v1, v2, v1[0, :], (0, 0)])

        c = np.hstack([arc.codes, Path.MOVETO,

                       arc.codes[1:], Path.MOVETO,

                       Path.CLOSEPOLY])

        self._path = Path(v, c)



    def get_path(self):

        if self._path is None:

            self._recompute_path()

        return self._path





class Circle(Ellipse):

    

    def __str__(self):

        pars = self.center[0], self.center[1], self.radius

        fmt = "Circle(xy=(%g, %g), radius=%g)"

        return fmt % pars



    @_docstring.interpd

    def __init__(self, xy, radius=5, **kwargs):

        

        super().__init__(xy, radius * 2, radius * 2, **kwargs)

        self.radius = radius



    def set_radius(self, radius):

        

        self.width = self.height = 2 * radius

        self.stale = True



    def get_radius(self):

        

        return self.width / 2.



    radius = property(get_radius, set_radius)





class Arc(Ellipse):

    



    def __str__(self):

        pars = (self.center[0], self.center[1], self.width,

                self.height, self.angle, self.theta1, self.theta2)

        fmt = ("Arc(xy=(%g, %g), width=%g, "

               "height=%g, angle=%g, theta1=%g, theta2=%g)")

        return fmt % pars



    @_docstring.interpd

    def __init__(self, xy, width, height, *,

                 angle=0.0, theta1=0.0, theta2=360.0, **kwargs):

        

        fill = kwargs.setdefault('fill', False)

        if fill:

            raise ValueError("Arc objects cannot be filled")



        super().__init__(xy, width, height, angle=angle, **kwargs)



        self.theta1 = theta1

        self.theta2 = theta2

        (self._theta1, self._theta2, self._stretched_width,

         self._stretched_height) = self._theta_stretch()

        self._path = Path.arc(self._theta1, self._theta2)



    @artist.allow_rasterization

    def draw(self, renderer):

        

        if not self.get_visible():

            return



        self._recompute_transform()



        self._update_path()

                                                       

                                                                    

                                                             

                                                                      

                                                            

                                                                   

                                 

        data_to_screen_trans = self.get_data_transform()

        pwidth, pheight = (

            data_to_screen_trans.transform((self._stretched_width,

                                            self._stretched_height)) -

            data_to_screen_trans.transform((0, 0)))

        inv_error = (1.0 / 1.89818e-6) * 0.5



        if pwidth < inv_error and pheight < inv_error:

            return Patch.draw(self, renderer)



        def line_circle_intersect(x0, y0, x1, y1):

            dx = x1 - x0

            dy = y1 - y0

            dr2 = dx * dx + dy * dy

            D = x0 * y1 - x1 * y0

            D2 = D * D

            discrim = dr2 - D2

            if discrim >= 0.0:

                sign_dy = np.copysign(1, dy)                  

                sqrt_discrim = np.sqrt(discrim)

                return np.array(

                    [[(D * dy + sign_dy * dx * sqrt_discrim) / dr2,

                      (-D * dx + abs(dy) * sqrt_discrim) / dr2],

                     [(D * dy - sign_dy * dx * sqrt_discrim) / dr2,

                      (-D * dx - abs(dy) * sqrt_discrim) / dr2]])

            else:

                return np.empty((0, 2))



        def segment_circle_intersect(x0, y0, x1, y1):

            epsilon = 1e-9

            if x1 < x0:

                x0e, x1e = x1, x0

            else:

                x0e, x1e = x0, x1

            if y1 < y0:

                y0e, y1e = y1, y0

            else:

                y0e, y1e = y0, y1

            xys = line_circle_intersect(x0, y0, x1, y1)

            xs, ys = xys.T

            return xys[

                (x0e - epsilon < xs) & (xs < x1e + epsilon)

                & (y0e - epsilon < ys) & (ys < y1e + epsilon)

            ]



                                                                           

                                                                            

                  

        box_path_transform = (

            transforms.BboxTransformTo((self.axes or self.get_figure(root=False)).bbox)

            - self.get_transform())

        box_path = Path.unit_rectangle().transformed(box_path_transform)



        thetas = set()

                                                              

        for p0, p1 in zip(box_path.vertices[:-1], box_path.vertices[1:]):

            xy = segment_circle_intersect(*p0, *p1)

            x, y = xy.T

                                                                     

                                         

            theta = (np.rad2deg(np.arctan2(y, x)) + 360) % 360

            thetas.update(

                theta[(self._theta1 < theta) & (theta < self._theta2)])

        thetas = sorted(thetas) + [self._theta2]

        last_theta = self._theta1

        theta1_rad = np.deg2rad(self._theta1)

        inside = box_path.contains_point(

            (np.cos(theta1_rad), np.sin(theta1_rad))

        )



                            

        path_original = self._path

        for theta in thetas:

            if inside:

                self._path = Path.arc(last_theta, theta, 8)

                Patch.draw(self, renderer)

                inside = False

            else:

                inside = True

            last_theta = theta



                               

        self._path = path_original



    def _update_path(self):

                                                                              

        stretched = self._theta_stretch()

        if any(a != b for a, b in zip(

                stretched, (self._theta1, self._theta2, self._stretched_width,

                            self._stretched_height))):

            (self._theta1, self._theta2, self._stretched_width,

             self._stretched_height) = stretched

            self._path = Path.arc(self._theta1, self._theta2)



    def _theta_stretch(self):

                                                                             

                                                            

        def theta_stretch(theta, scale):

            theta = np.deg2rad(theta)

            x = np.cos(theta)

            y = np.sin(theta)

            stheta = np.rad2deg(np.arctan2(scale * y, x))

                                                                  

            return (stheta + 360) % 360



        width = self.convert_xunits(self.width)

        height = self.convert_yunits(self.height)

        if (

                                                                       

            width != height

                                                 

             

                                                                   

                                                                     

                                                                       

                                                                          

            and not (self.theta1 != self.theta2 and

                     self.theta1 % 360 == self.theta2 % 360)

        ):

            theta1 = theta_stretch(self.theta1, width / height)

            theta2 = theta_stretch(self.theta2, width / height)

            return theta1, theta2, width, height

        return self.theta1, self.theta2, width, height





def bbox_artist(artist, renderer, props=None, fill=True):

    

    if props is None:

        props = {}

    props = props.copy()                                          

    pad = props.pop('pad', 4)

    pad = renderer.points_to_pixels(pad)

    bbox = artist.get_window_extent(renderer)

    r = Rectangle(

        xy=(bbox.x0 - pad / 2, bbox.y0 - pad / 2),

        width=bbox.width + pad, height=bbox.height + pad,

        fill=fill, transform=transforms.IdentityTransform(), clip_on=False)

    r.update(props)

    r.draw(renderer)





def draw_bbox(bbox, renderer, color='k', trans=None):

    

    r = Rectangle(xy=bbox.p0, width=bbox.width, height=bbox.height,

                  edgecolor=color, fill=False, clip_on=False)

    if trans is not None:

        r.set_transform(trans)

    r.draw(renderer)





class _Style:

    



    def __init_subclass__(cls):

                                                                          

                                                      

                              

                                     

                                

                                                        

                                          

                                                 

                                            

        _docstring.interpd.register(**{

            f"{cls.__name__}:table": cls.pprint_styles(),

            f"{cls.__name__}:table_and_accepts": (

                cls.pprint_styles()

                + "\n\n    .. ACCEPTS: ["

                + "|".join(map(" '{}' ".format, cls._style_list))

                + "]")

        })



    def __new__(cls, stylename, **kwargs):

        

                                                                               

                                          

        _list = stylename.replace(" ", "").split(",")

        _name = _list[0].lower()

        try:

            _cls = cls._style_list[_name]

        except KeyError as err:

            raise ValueError(f"Unknown style: {stylename!r}") from err

        try:

            _args_pair = [cs.split("=") for cs in _list[1:]]

            _args = {k: float(v) for k, v in _args_pair}

        except ValueError as err:

            raise ValueError(

                f"Incorrect style argument: {stylename!r}") from err

        return _cls(**{**_args, **kwargs})



    @classmethod

    def get_styles(cls):

        

        return cls._style_list



    @classmethod

    def pprint_styles(cls):

        

        table = [('Class', 'Name', 'Parameters'),

                 *[(cls.__name__,

                                                                              

                    f'``{name}``',

                                                               

                    str(inspect.signature(cls))[1:-1] or 'None')

                   for name, cls in cls._style_list.items()]]

                               

        col_len = [max(len(cell) for cell in column) for column in zip(*table)]

        table_formatstr = '  '.join('=' * cl for cl in col_len)

        rst_table = '\n'.join([

            '',

            table_formatstr,

            '  '.join(cell.ljust(cl) for cell, cl in zip(table[0], col_len)),

            table_formatstr,

            *['  '.join(cell.ljust(cl) for cell, cl in zip(row, col_len))

              for row in table[1:]],

            table_formatstr,

        ])

        return textwrap.indent(rst_table, prefix=' ' * 4)



    @classmethod

    @_api.deprecated(

        '3.10.0',

        message="This method is never used internally.",

        alternative="No replacement.  Please open an issue if you use this."

    )

    def register(cls, name, style):

        

        if not issubclass(style, cls._Base):

            raise ValueError(f"{style} must be a subclass of {cls._Base}")

        cls._style_list[name] = style





def _register_style(style_list, cls=None, *, name=None):

    

    if cls is None:

        return functools.partial(_register_style, style_list, name=name)

    style_list[name or cls.__name__.lower()] = cls

    return cls





@_docstring.interpd

class BoxStyle(_Style):

    



    _style_list = {}



    @_register_style(_style_list)

    class Square:

        



        def __init__(self, pad=0.3):

            

            self.pad = pad



        def __call__(self, x0, y0, width, height, mutation_size):

            pad = mutation_size * self.pad

                                                  

            width, height = width + 2 * pad, height + 2 * pad

                                        

            x0, y0 = x0 - pad, y0 - pad

            x1, y1 = x0 + width, y0 + height

            return Path._create_closed(

                [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])



    @_register_style(_style_list)

    class Circle:

        



        def __init__(self, pad=0.3):

            

            self.pad = pad



        def __call__(self, x0, y0, width, height, mutation_size):

            pad = mutation_size * self.pad

            width, height = width + 2 * pad, height + 2 * pad

                                        

            x0, y0 = x0 - pad, y0 - pad

            return Path.circle((x0 + width / 2, y0 + height / 2),

                                max(width, height) / 2)



    @_register_style(_style_list)

    class Ellipse:

        



        def __init__(self, pad=0.3):

            

            self.pad = pad



        def __call__(self, x0, y0, width, height, mutation_size):

            pad = mutation_size * self.pad

            width, height = width + 2 * pad, height + 2 * pad

                                        

            x0, y0 = x0 - pad, y0 - pad

            a = width / math.sqrt(2)

            b = height / math.sqrt(2)

            trans = Affine2D().scale(a, b).translate(x0 + width / 2,

                                                     y0 + height / 2)

            return trans.transform_path(Path.unit_circle())



    @_register_style(_style_list)

    class LArrow:

        



        def __init__(self, pad=0.3):

            

            self.pad = pad



        def __call__(self, x0, y0, width, height, mutation_size):

                     

            pad = mutation_size * self.pad

                                                  

            width, height = width + 2 * pad, height + 2 * pad

                                        

            x0, y0 = x0 - pad, y0 - pad,

            x1, y1 = x0 + width, y0 + height



            dx = (y1 - y0) / 2

            dxx = dx / 2

            x0 = x0 + pad / 1.4                      



            return Path._create_closed(

                [(x0 + dxx, y0), (x1, y0), (x1, y1), (x0 + dxx, y1),

                 (x0 + dxx, y1 + dxx), (x0 - dx, y0 + dx),

                 (x0 + dxx, y0 - dxx),         

                 (x0 + dxx, y0)])



    @_register_style(_style_list)

    class RArrow(LArrow):

        



        def __call__(self, x0, y0, width, height, mutation_size):

            p = BoxStyle.LArrow.__call__(

                self, x0, y0, width, height, mutation_size)

            p.vertices[:, 0] = 2 * x0 + width - p.vertices[:, 0]

            return p



    @_register_style(_style_list)

    class DArrow:

        

                                                                



        def __init__(self, pad=0.3):

            

            self.pad = pad



        def __call__(self, x0, y0, width, height, mutation_size):

                     

            pad = mutation_size * self.pad

                                                  

                                                                            

            height = height + 2 * pad

                                        

            x0, y0 = x0 - pad, y0 - pad

            x1, y1 = x0 + width, y0 + height



            dx = (y1 - y0) / 2

            dxx = dx / 2

            x0 = x0 + pad / 1.4                      



            return Path._create_closed([

                (x0 + dxx, y0), (x1, y0),               

                (x1, y0 - dxx), (x1 + dx + dxx, y0 + dx),

                (x1, y1 + dxx),               

                (x1, y1), (x0 + dxx, y1),               

                (x0 + dxx, y1 + dxx), (x0 - dx, y0 + dx),

                (x0 + dxx, y0 - dxx),              

                (x0 + dxx, y0)])



    @_register_style(_style_list)

    class Round:

        



        def __init__(self, pad=0.3, rounding_size=None):

            

            self.pad = pad

            self.rounding_size = rounding_size



        def __call__(self, x0, y0, width, height, mutation_size):



                     

            pad = mutation_size * self.pad



                                         

            if self.rounding_size:

                dr = mutation_size * self.rounding_size

            else:

                dr = pad



            width, height = width + 2 * pad, height + 2 * pad



            x0, y0 = x0 - pad, y0 - pad,

            x1, y1 = x0 + width, y0 + height



                                                                      

                                                                         

            cp = [(x0 + dr, y0),

                  (x1 - dr, y0),

                  (x1, y0), (x1, y0 + dr),

                  (x1, y1 - dr),

                  (x1, y1), (x1 - dr, y1),

                  (x0 + dr, y1),

                  (x0, y1), (x0, y1 - dr),

                  (x0, y0 + dr),

                  (x0, y0), (x0 + dr, y0),

                  (x0 + dr, y0)]



            com = [Path.MOVETO,

                   Path.LINETO,

                   Path.CURVE3, Path.CURVE3,

                   Path.LINETO,

                   Path.CURVE3, Path.CURVE3,

                   Path.LINETO,

                   Path.CURVE3, Path.CURVE3,

                   Path.LINETO,

                   Path.CURVE3, Path.CURVE3,

                   Path.CLOSEPOLY]



            return Path(cp, com)



    @_register_style(_style_list)

    class Round4:

        



        def __init__(self, pad=0.3, rounding_size=None):

            

            self.pad = pad

            self.rounding_size = rounding_size



        def __call__(self, x0, y0, width, height, mutation_size):



                     

            pad = mutation_size * self.pad



                                                             

            if self.rounding_size:

                dr = mutation_size * self.rounding_size

            else:

                dr = pad / 2.



            width = width + 2 * pad - 2 * dr

            height = height + 2 * pad - 2 * dr



            x0, y0 = x0 - pad + dr, y0 - pad + dr,

            x1, y1 = x0 + width, y0 + height



            cp = [(x0, y0),

                  (x0 + dr, y0 - dr), (x1 - dr, y0 - dr), (x1, y0),

                  (x1 + dr, y0 + dr), (x1 + dr, y1 - dr), (x1, y1),

                  (x1 - dr, y1 + dr), (x0 + dr, y1 + dr), (x0, y1),

                  (x0 - dr, y1 - dr), (x0 - dr, y0 + dr), (x0, y0),

                  (x0, y0)]



            com = [Path.MOVETO,

                   Path.CURVE4, Path.CURVE4, Path.CURVE4,

                   Path.CURVE4, Path.CURVE4, Path.CURVE4,

                   Path.CURVE4, Path.CURVE4, Path.CURVE4,

                   Path.CURVE4, Path.CURVE4, Path.CURVE4,

                   Path.CLOSEPOLY]



            return Path(cp, com)



    @_register_style(_style_list)

    class Sawtooth:

        



        def __init__(self, pad=0.3, tooth_size=None):

            

            self.pad = pad

            self.tooth_size = tooth_size



        def _get_sawtooth_vertices(self, x0, y0, width, height, mutation_size):



                     

            pad = mutation_size * self.pad



                              

            if self.tooth_size is None:

                tooth_size = self.pad * .5 * mutation_size

            else:

                tooth_size = self.tooth_size * mutation_size



            hsz = tooth_size / 2

            width = width + 2 * pad - tooth_size

            height = height + 2 * pad - tooth_size



                                                                   

                                                            

            dsx_n = round((width - tooth_size) / (tooth_size * 2)) * 2

            dsy_n = round((height - tooth_size) / (tooth_size * 2)) * 2



            x0, y0 = x0 - pad + hsz, y0 - pad + hsz

            x1, y1 = x0 + width, y0 + height



            xs = [

                x0, *np.linspace(x0 + hsz, x1 - hsz, 2 * dsx_n + 1),          

                *([x1, x1 + hsz, x1, x1 - hsz] * dsy_n)[:2*dsy_n+2],         

                x1, *np.linspace(x1 - hsz, x0 + hsz, 2 * dsx_n + 1),       

                *([x0, x0 - hsz, x0, x0 + hsz] * dsy_n)[:2*dsy_n+2],        

            ]

            ys = [

                *([y0, y0 - hsz, y0, y0 + hsz] * dsx_n)[:2*dsx_n+2],          

                y0, *np.linspace(y0 + hsz, y1 - hsz, 2 * dsy_n + 1),         

                *([y1, y1 + hsz, y1, y1 - hsz] * dsx_n)[:2*dsx_n+2],       

                y1, *np.linspace(y1 - hsz, y0 + hsz, 2 * dsy_n + 1),        

            ]



            return [*zip(xs, ys), (xs[0], ys[0])]



        def __call__(self, x0, y0, width, height, mutation_size):

            saw_vertices = self._get_sawtooth_vertices(x0, y0, width,

                                                       height, mutation_size)

            return Path(saw_vertices, closed=True)



    @_register_style(_style_list)

    class Roundtooth(Sawtooth):

        



        def __call__(self, x0, y0, width, height, mutation_size):

            saw_vertices = self._get_sawtooth_vertices(x0, y0,

                                                       width, height,

                                                       mutation_size)

                                                                              

            saw_vertices = np.concatenate([saw_vertices, [saw_vertices[0]]])

            codes = ([Path.MOVETO] +

                     [Path.CURVE3, Path.CURVE3] * ((len(saw_vertices)-1)//2) +

                     [Path.CLOSEPOLY])

            return Path(saw_vertices, codes)





@_docstring.interpd

class ConnectionStyle(_Style):

    



    _style_list = {}



    class _Base:

        

        def _in_patch(self, patch):

            

            return lambda xy: patch.contains(

                SimpleNamespace(x=xy[0], y=xy[1]))[0]



        def _clip(self, path, in_start, in_stop):

            

            if in_start:

                try:

                    _, path = split_path_inout(path, in_start)

                except ValueError:

                    pass

            if in_stop:

                try:

                    path, _ = split_path_inout(path, in_stop)

                except ValueError:

                    pass

            return path



        def __call__(self, posA, posB,

                     shrinkA=2., shrinkB=2., patchA=None, patchB=None):

            

            path = self.connect(posA, posB)

            path = self._clip(

                path,

                self._in_patch(patchA) if patchA else None,

                self._in_patch(patchB) if patchB else None,

            )

            path = self._clip(

                path,

                inside_circle(*path.vertices[0], shrinkA) if shrinkA else None,

                inside_circle(*path.vertices[-1], shrinkB) if shrinkB else None

            )

            return path



    @_register_style(_style_list)

    class Arc3(_Base):

        



        def __init__(self, rad=0.):

            

            self.rad = rad



        def connect(self, posA, posB):

            x1, y1 = posA

            x2, y2 = posB

            x12, y12 = (x1 + x2) / 2., (y1 + y2) / 2.

            dx, dy = x2 - x1, y2 - y1



            f = self.rad



            cx, cy = x12 + f * dy, y12 - f * dx



            vertices = [(x1, y1),

                        (cx, cy),

                        (x2, y2)]

            codes = [Path.MOVETO,

                     Path.CURVE3,

                     Path.CURVE3]



            return Path(vertices, codes)



    @_register_style(_style_list)

    class Angle3(_Base):

        



        def __init__(self, angleA=90, angleB=0):

            



            self.angleA = angleA

            self.angleB = angleB



        def connect(self, posA, posB):

            x1, y1 = posA

            x2, y2 = posB



            cosA = math.cos(math.radians(self.angleA))

            sinA = math.sin(math.radians(self.angleA))

            cosB = math.cos(math.radians(self.angleB))

            sinB = math.sin(math.radians(self.angleB))



            cx, cy = get_intersection(x1, y1, cosA, sinA,

                                      x2, y2, cosB, sinB)



            vertices = [(x1, y1), (cx, cy), (x2, y2)]

            codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]



            return Path(vertices, codes)



    @_register_style(_style_list)

    class Angle(_Base):

        



        def __init__(self, angleA=90, angleB=0, rad=0.):

            



            self.angleA = angleA

            self.angleB = angleB



            self.rad = rad



        def connect(self, posA, posB):

            x1, y1 = posA

            x2, y2 = posB



            cosA = math.cos(math.radians(self.angleA))

            sinA = math.sin(math.radians(self.angleA))

            cosB = math.cos(math.radians(self.angleB))

            sinB = math.sin(math.radians(self.angleB))



            cx, cy = get_intersection(x1, y1, cosA, sinA,

                                      x2, y2, cosB, sinB)



            vertices = [(x1, y1)]

            codes = [Path.MOVETO]



            if self.rad == 0.:

                vertices.append((cx, cy))

                codes.append(Path.LINETO)

            else:

                dx1, dy1 = x1 - cx, y1 - cy

                d1 = np.hypot(dx1, dy1)

                f1 = self.rad / d1

                dx2, dy2 = x2 - cx, y2 - cy

                d2 = np.hypot(dx2, dy2)

                f2 = self.rad / d2

                vertices.extend([(cx + dx1 * f1, cy + dy1 * f1),

                                 (cx, cy),

                                 (cx + dx2 * f2, cy + dy2 * f2)])

                codes.extend([Path.LINETO, Path.CURVE3, Path.CURVE3])



            vertices.append((x2, y2))

            codes.append(Path.LINETO)



            return Path(vertices, codes)



    @_register_style(_style_list)

    class Arc(_Base):

        



        def __init__(self, angleA=0, angleB=0, armA=None, armB=None, rad=0.):

            



            self.angleA = angleA

            self.angleB = angleB

            self.armA = armA

            self.armB = armB



            self.rad = rad



        def connect(self, posA, posB):

            x1, y1 = posA

            x2, y2 = posB



            vertices = [(x1, y1)]

            rounded = []

            codes = [Path.MOVETO]



            if self.armA:

                cosA = math.cos(math.radians(self.angleA))

                sinA = math.sin(math.radians(self.angleA))

                                

                d = self.armA - self.rad

                rounded.append((x1 + d * cosA, y1 + d * sinA))

                d = self.armA

                rounded.append((x1 + d * cosA, y1 + d * sinA))



            if self.armB:

                cosB = math.cos(math.radians(self.angleB))

                sinB = math.sin(math.radians(self.angleB))

                x_armB, y_armB = x2 + self.armB * cosB, y2 + self.armB * sinB



                if rounded:

                    xp, yp = rounded[-1]

                    dx, dy = x_armB - xp, y_armB - yp

                    dd = (dx * dx + dy * dy) ** .5



                    rounded.append((xp + self.rad * dx / dd,

                                    yp + self.rad * dy / dd))

                    vertices.extend(rounded)

                    codes.extend([Path.LINETO,

                                  Path.CURVE3,

                                  Path.CURVE3])

                else:

                    xp, yp = vertices[-1]

                    dx, dy = x_armB - xp, y_armB - yp

                    dd = (dx * dx + dy * dy) ** .5



                d = dd - self.rad

                rounded = [(xp + d * dx / dd, yp + d * dy / dd),

                           (x_armB, y_armB)]



            if rounded:

                xp, yp = rounded[-1]

                dx, dy = x2 - xp, y2 - yp

                dd = (dx * dx + dy * dy) ** .5



                rounded.append((xp + self.rad * dx / dd,

                                yp + self.rad * dy / dd))

                vertices.extend(rounded)

                codes.extend([Path.LINETO,

                              Path.CURVE3,

                              Path.CURVE3])



            vertices.append((x2, y2))

            codes.append(Path.LINETO)



            return Path(vertices, codes)



    @_register_style(_style_list)

    class Bar(_Base):

        



        def __init__(self, armA=0., armB=0., fraction=0.3, angle=None):

            

            self.armA = armA

            self.armB = armB

            self.fraction = fraction

            self.angle = angle



        def connect(self, posA, posB):

            x1, y1 = posA

            x20, y20 = x2, y2 = posB



            theta1 = math.atan2(y2 - y1, x2 - x1)

            dx, dy = x2 - x1, y2 - y1

            dd = (dx * dx + dy * dy) ** .5

            ddx, ddy = dx / dd, dy / dd



            armA, armB = self.armA, self.armB



            if self.angle is not None:

                theta0 = np.deg2rad(self.angle)

                dtheta = theta1 - theta0

                dl = dd * math.sin(dtheta)

                dL = dd * math.cos(dtheta)

                x2, y2 = x1 + dL * math.cos(theta0), y1 + dL * math.sin(theta0)

                armB = armB - dl



                        

                dx, dy = x2 - x1, y2 - y1

                dd2 = (dx * dx + dy * dy) ** .5

                ddx, ddy = dx / dd2, dy / dd2



            arm = max(armA, armB)

            f = self.fraction * dd + arm



            cx1, cy1 = x1 + f * ddy, y1 - f * ddx

            cx2, cy2 = x2 + f * ddy, y2 - f * ddx



            vertices = [(x1, y1),

                        (cx1, cy1),

                        (cx2, cy2),

                        (x20, y20)]

            codes = [Path.MOVETO,

                     Path.LINETO,

                     Path.LINETO,

                     Path.LINETO]



            return Path(vertices, codes)





def _point_along_a_line(x0, y0, x1, y1, d):

    

    dx, dy = x0 - x1, y0 - y1

    ff = d / (dx * dx + dy * dy) ** .5

    x2, y2 = x0 - ff * dx, y0 - ff * dy



    return x2, y2





@_docstring.interpd

class ArrowStyle(_Style):

    



    _style_list = {}



    class _Base:

        



                                                                       

                                                                       

                             



        @staticmethod

        def ensure_quadratic_bezier(path):

            

            segments = list(path.iter_segments())

            if (len(segments) != 2 or segments[0][1] != Path.MOVETO or

                    segments[1][1] != Path.CURVE3):

                raise ValueError(

                    "'path' is not a valid quadratic Bezier curve")

            return [*segments[0][0], *segments[1][0]]



        def transmute(self, path, mutation_size, linewidth):

            

            raise NotImplementedError('Derived must override')



        def __call__(self, path, mutation_size, linewidth,

                     aspect_ratio=1.):

            



            if aspect_ratio is not None:

                                                              

                vertices = path.vertices / [1, aspect_ratio]

                path_shrunk = Path(vertices, path.codes)

                                                             

                path_mutated, fillable = self.transmute(path_shrunk,

                                                        mutation_size,

                                                        linewidth)

                if np.iterable(fillable):

                                        

                    path_list = [Path(p.vertices * [1, aspect_ratio], p.codes)

                                 for p in path_mutated]

                    return path_list, fillable

                else:

                    return path_mutated, fillable

            else:

                return self.transmute(path, mutation_size, linewidth)



    class _Curve(_Base):

        



        arrow = "-"

        fillbegin = fillend = False                              



        def __init__(self, head_length=.4, head_width=.2, widthA=1., widthB=1.,

                     lengthA=0.2, lengthB=0.2, angleA=0, angleB=0, scaleA=None,

                     scaleB=None):

            



            self.head_length, self.head_width = head_length, head_width

            self.widthA, self.widthB = widthA, widthB

            self.lengthA, self.lengthB = lengthA, lengthB

            self.angleA, self.angleB = angleA, angleB

            self.scaleA, self.scaleB = scaleA, scaleB



            self._beginarrow_head = False

            self._beginarrow_bracket = False

            self._endarrow_head = False

            self._endarrow_bracket = False



            if "-" not in self.arrow:

                raise ValueError("arrow must have the '-' between "

                                 "the two heads")



            beginarrow, endarrow = self.arrow.split("-", 1)



            if beginarrow == "<":

                self._beginarrow_head = True

                self._beginarrow_bracket = False

            elif beginarrow == "<|":

                self._beginarrow_head = True

                self._beginarrow_bracket = False

                self.fillbegin = True

            elif beginarrow in ("]", "|"):

                self._beginarrow_head = False

                self._beginarrow_bracket = True



            if endarrow == ">":

                self._endarrow_head = True

                self._endarrow_bracket = False

            elif endarrow == "|>":

                self._endarrow_head = True

                self._endarrow_bracket = False

                self.fillend = True

            elif endarrow in ("[", "|"):

                self._endarrow_head = False

                self._endarrow_bracket = True



            super().__init__()



        def _get_arrow_wedge(self, x0, y0, x1, y1,

                             head_dist, cos_t, sin_t, linewidth):

            



                                         

            dx, dy = x0 - x1, y0 - y1



            cp_distance = np.hypot(dx, dy)



                                                          

                                                         

            pad_projected = (.5 * linewidth / sin_t)



                                          

            if cp_distance == 0:

                cp_distance = 1



                                          

            ddx = pad_projected * dx / cp_distance

            ddy = pad_projected * dy / cp_distance



                                    

            dx = dx / cp_distance * head_dist

            dy = dy / cp_distance * head_dist



            dx1, dy1 = cos_t * dx + sin_t * dy, -sin_t * dx + cos_t * dy

            dx2, dy2 = cos_t * dx - sin_t * dy, sin_t * dx + cos_t * dy



            vertices_arrow = [(x1 + ddx + dx1, y1 + ddy + dy1),

                              (x1 + ddx, y1 + ddy),

                              (x1 + ddx + dx2, y1 + ddy + dy2)]

            codes_arrow = [Path.MOVETO,

                           Path.LINETO,

                           Path.LINETO]



            return vertices_arrow, codes_arrow, ddx, ddy



        def _get_bracket(self, x0, y0,

                         x1, y1, width, length, angle):



            cos_t, sin_t = get_cos_sin(x1, y1, x0, y0)



                                         

            from matplotlib.bezier import get_normal_points

            x1, y1, x2, y2 = get_normal_points(x0, y0, cos_t, sin_t, width)



            dx, dy = length * cos_t, length * sin_t



            vertices_arrow = [(x1 + dx, y1 + dy),

                              (x1, y1),

                              (x2, y2),

                              (x2 + dx, y2 + dy)]

            codes_arrow = [Path.MOVETO,

                           Path.LINETO,

                           Path.LINETO,

                           Path.LINETO]



            if angle:

                trans = transforms.Affine2D().rotate_deg_around(x0, y0, angle)

                vertices_arrow = trans.transform(vertices_arrow)



            return vertices_arrow, codes_arrow



        def transmute(self, path, mutation_size, linewidth):

                                 

            if self._beginarrow_head or self._endarrow_head:

                head_length = self.head_length * mutation_size

                head_width = self.head_width * mutation_size

                head_dist = np.hypot(head_length, head_width)

                cos_t, sin_t = head_length / head_dist, head_width / head_dist



            scaleA = mutation_size if self.scaleA is None else self.scaleA

            scaleB = mutation_size if self.scaleB is None else self.scaleB



                         

            x0, y0 = path.vertices[0]

            x1, y1 = path.vertices[1]



                                                                              

            has_begin_arrow = self._beginarrow_head and (x0, y0) != (x1, y1)

            verticesA, codesA, ddxA, ddyA = (

                self._get_arrow_wedge(x1, y1, x0, y0,

                                      head_dist, cos_t, sin_t, linewidth)

                if has_begin_arrow

                else ([], [], 0, 0)

            )



                       

            x2, y2 = path.vertices[-2]

            x3, y3 = path.vertices[-1]



                                                                              

            has_end_arrow = self._endarrow_head and (x2, y2) != (x3, y3)

            verticesB, codesB, ddxB, ddyB = (

                self._get_arrow_wedge(x2, y2, x3, y3,

                                      head_dist, cos_t, sin_t, linewidth)

                if has_end_arrow

                else ([], [], 0, 0)

            )



                                                                            

                                          

            paths = [Path(np.concatenate([[(x0 + ddxA, y0 + ddyA)],

                                          path.vertices[1:-1],

                                          [(x3 + ddxB, y3 + ddyB)]]),

                          path.codes)]

            fills = [False]



            if has_begin_arrow:

                if self.fillbegin:

                    paths.append(

                        Path([*verticesA, (0, 0)], [*codesA, Path.CLOSEPOLY]))

                    fills.append(True)

                else:

                    paths.append(Path(verticesA, codesA))

                    fills.append(False)

            elif self._beginarrow_bracket:

                x0, y0 = path.vertices[0]

                x1, y1 = path.vertices[1]

                verticesA, codesA = self._get_bracket(x0, y0, x1, y1,

                                                      self.widthA * scaleA,

                                                      self.lengthA * scaleA,

                                                      self.angleA)



                paths.append(Path(verticesA, codesA))

                fills.append(False)



            if has_end_arrow:

                if self.fillend:

                    fills.append(True)

                    paths.append(

                        Path([*verticesB, (0, 0)], [*codesB, Path.CLOSEPOLY]))

                else:

                    fills.append(False)

                    paths.append(Path(verticesB, codesB))

            elif self._endarrow_bracket:

                x0, y0 = path.vertices[-1]

                x1, y1 = path.vertices[-2]

                verticesB, codesB = self._get_bracket(x0, y0, x1, y1,

                                                      self.widthB * scaleB,

                                                      self.lengthB * scaleB,

                                                      self.angleB)



                paths.append(Path(verticesB, codesB))

                fills.append(False)



            return paths, fills



    @_register_style(_style_list, name="-")

    class Curve(_Curve):

        



        def __init__(self):                                

                                                                              

                                                                            

            super().__init__(head_length=.2, head_width=.1)



    @_register_style(_style_list, name="<-")

    class CurveA(_Curve):

        

        arrow = "<-"



    @_register_style(_style_list, name="->")

    class CurveB(_Curve):

        

        arrow = "->"



    @_register_style(_style_list, name="<->")

    class CurveAB(_Curve):

        

        arrow = "<->"



    @_register_style(_style_list, name="<|-")

    class CurveFilledA(_Curve):

        

        arrow = "<|-"



    @_register_style(_style_list, name="-|>")

    class CurveFilledB(_Curve):

        

        arrow = "-|>"



    @_register_style(_style_list, name="<|-|>")

    class CurveFilledAB(_Curve):

        

        arrow = "<|-|>"



    @_register_style(_style_list, name="]-")

    class BracketA(_Curve):

        

        arrow = "]-"



        def __init__(self, widthA=1., lengthA=0.2, angleA=0):

            

            super().__init__(widthA=widthA, lengthA=lengthA, angleA=angleA)



    @_register_style(_style_list, name="-[")

    class BracketB(_Curve):

        

        arrow = "-["



        def __init__(self, widthB=1., lengthB=0.2, angleB=0):

            

            super().__init__(widthB=widthB, lengthB=lengthB, angleB=angleB)



    @_register_style(_style_list, name="]-[")

    class BracketAB(_Curve):

        

        arrow = "]-["



        def __init__(self,

                     widthA=1., lengthA=0.2, angleA=0,

                     widthB=1., lengthB=0.2, angleB=0):

            

            super().__init__(widthA=widthA, lengthA=lengthA, angleA=angleA,

                             widthB=widthB, lengthB=lengthB, angleB=angleB)



    @_register_style(_style_list, name="|-|")

    class BarAB(_Curve):

        

        arrow = "|-|"



        def __init__(self, widthA=1., angleA=0, widthB=1., angleB=0):

            

            super().__init__(widthA=widthA, lengthA=0, angleA=angleA,

                             widthB=widthB, lengthB=0, angleB=angleB)



    @_register_style(_style_list, name=']->')

    class BracketCurve(_Curve):

        

        arrow = "]->"



        def __init__(self, widthA=1., lengthA=0.2, angleA=None):

            

            super().__init__(widthA=widthA, lengthA=lengthA, angleA=angleA)



    @_register_style(_style_list, name='<-[')

    class CurveBracket(_Curve):

        

        arrow = "<-["



        def __init__(self, widthB=1., lengthB=0.2, angleB=None):

            

            super().__init__(widthB=widthB, lengthB=lengthB, angleB=angleB)



    @_register_style(_style_list)

    class Simple(_Base):

        



        def __init__(self, head_length=.5, head_width=.5, tail_width=.2):

            

            self.head_length, self.head_width, self.tail_width =
                head_length, head_width, tail_width

            super().__init__()



        def transmute(self, path, mutation_size, linewidth):

                                 

            x0, y0, x1, y1, x2, y2 = self.ensure_quadratic_bezier(path)



                                                    

            head_length = self.head_length * mutation_size

            in_f = inside_circle(x2, y2, head_length)

            arrow_path = [(x0, y0), (x1, y1), (x2, y2)]



            try:

                arrow_out, arrow_in =
                    split_bezier_intersecting_with_closedpath(arrow_path, in_f)

            except NonIntersectingPathException:

                                                                          

                       

                x0, y0 = _point_along_a_line(x2, y2, x1, y1, head_length)

                x1n, y1n = 0.5 * (x0 + x2), 0.5 * (y0 + y2)

                arrow_in = [(x0, y0), (x1n, y1n), (x2, y2)]

                arrow_out = None



                  

            head_width = self.head_width * mutation_size

            head_left, head_right = make_wedged_bezier2(arrow_in,

                                                        head_width / 2., wm=.5)



                  

            if arrow_out is not None:

                tail_width = self.tail_width * mutation_size

                tail_left, tail_right = get_parallels(arrow_out,

                                                      tail_width / 2.)



                patch_path = [(Path.MOVETO, tail_right[0]),

                              (Path.CURVE3, tail_right[1]),

                              (Path.CURVE3, tail_right[2]),

                              (Path.LINETO, head_right[0]),

                              (Path.CURVE3, head_right[1]),

                              (Path.CURVE3, head_right[2]),

                              (Path.CURVE3, head_left[1]),

                              (Path.CURVE3, head_left[0]),

                              (Path.LINETO, tail_left[2]),

                              (Path.CURVE3, tail_left[1]),

                              (Path.CURVE3, tail_left[0]),

                              (Path.LINETO, tail_right[0]),

                              (Path.CLOSEPOLY, tail_right[0]),

                              ]

            else:

                patch_path = [(Path.MOVETO, head_right[0]),

                              (Path.CURVE3, head_right[1]),

                              (Path.CURVE3, head_right[2]),

                              (Path.CURVE3, head_left[1]),

                              (Path.CURVE3, head_left[0]),

                              (Path.CLOSEPOLY, head_left[0]),

                              ]



            path = Path([p for c, p in patch_path], [c for c, p in patch_path])



            return path, True



    @_register_style(_style_list)

    class Fancy(_Base):

        



        def __init__(self, head_length=.4, head_width=.4, tail_width=.4):

            

            self.head_length, self.head_width, self.tail_width =
                head_length, head_width, tail_width

            super().__init__()



        def transmute(self, path, mutation_size, linewidth):

                                 

            x0, y0, x1, y1, x2, y2 = self.ensure_quadratic_bezier(path)



                                                    

            head_length = self.head_length * mutation_size

            arrow_path = [(x0, y0), (x1, y1), (x2, y2)]



                           

            in_f = inside_circle(x2, y2, head_length)

            try:

                path_out, path_in = split_bezier_intersecting_with_closedpath(

                    arrow_path, in_f)

            except NonIntersectingPathException:

                                                                          

                       

                x0, y0 = _point_along_a_line(x2, y2, x1, y1, head_length)

                x1n, y1n = 0.5 * (x0 + x2), 0.5 * (y0 + y2)

                arrow_path = [(x0, y0), (x1n, y1n), (x2, y2)]

                path_head = arrow_path

            else:

                path_head = path_in



                           

            in_f = inside_circle(x2, y2, head_length * .8)

            path_out, path_in = split_bezier_intersecting_with_closedpath(

                arrow_path, in_f)

            path_tail = path_out



                  

            head_width = self.head_width * mutation_size

            head_l, head_r = make_wedged_bezier2(path_head,

                                                 head_width / 2.,

                                                 wm=.6)



                  

            tail_width = self.tail_width * mutation_size

            tail_left, tail_right = make_wedged_bezier2(path_tail,

                                                        tail_width * .5,

                                                        w1=1., wm=0.6, w2=0.3)



                           

            in_f = inside_circle(x0, y0, tail_width * .3)

            path_in, path_out = split_bezier_intersecting_with_closedpath(

                arrow_path, in_f)

            tail_start = path_in[-1]



            head_right, head_left = head_r, head_l

            patch_path = [(Path.MOVETO, tail_start),

                          (Path.LINETO, tail_right[0]),

                          (Path.CURVE3, tail_right[1]),

                          (Path.CURVE3, tail_right[2]),

                          (Path.LINETO, head_right[0]),

                          (Path.CURVE3, head_right[1]),

                          (Path.CURVE3, head_right[2]),

                          (Path.CURVE3, head_left[1]),

                          (Path.CURVE3, head_left[0]),

                          (Path.LINETO, tail_left[2]),

                          (Path.CURVE3, tail_left[1]),

                          (Path.CURVE3, tail_left[0]),

                          (Path.LINETO, tail_start),

                          (Path.CLOSEPOLY, tail_start),

                          ]

            path = Path([p for c, p in patch_path], [c for c, p in patch_path])



            return path, True



    @_register_style(_style_list)

    class Wedge(_Base):

        



        def __init__(self, tail_width=.3, shrink_factor=0.5):

            

            self.tail_width = tail_width

            self.shrink_factor = shrink_factor

            super().__init__()



        def transmute(self, path, mutation_size, linewidth):

                                 

            x0, y0, x1, y1, x2, y2 = self.ensure_quadratic_bezier(path)



            arrow_path = [(x0, y0), (x1, y1), (x2, y2)]

            b_plus, b_minus = make_wedged_bezier2(

                                    arrow_path,

                                    self.tail_width * mutation_size / 2.,

                                    wm=self.shrink_factor)



            patch_path = [(Path.MOVETO, b_plus[0]),

                          (Path.CURVE3, b_plus[1]),

                          (Path.CURVE3, b_plus[2]),

                          (Path.LINETO, b_minus[2]),

                          (Path.CURVE3, b_minus[1]),

                          (Path.CURVE3, b_minus[0]),

                          (Path.CLOSEPOLY, b_minus[0]),

                          ]

            path = Path([p for c, p in patch_path], [c for c, p in patch_path])



            return path, True





class FancyBboxPatch(Patch):

    



    _edge_default = True



    def __str__(self):

        s = self.__class__.__name__ + "((%g, %g), width=%g, height=%g)"

        return s % (self._x, self._y, self._width, self._height)



    @_docstring.interpd

    def __init__(self, xy, width, height, boxstyle="round", *,

                 mutation_scale=1, mutation_aspect=1, **kwargs):

        



        super().__init__(**kwargs)

        self._x, self._y = xy

        self._width = width

        self._height = height

        self.set_boxstyle(boxstyle)

        self._mutation_scale = mutation_scale

        self._mutation_aspect = mutation_aspect

        self.stale = True



    @_docstring.interpd

    def set_boxstyle(self, boxstyle=None, **kwargs):

        

        if boxstyle is None:

            return BoxStyle.pprint_styles()

        self._bbox_transmuter = (

            BoxStyle(boxstyle, **kwargs)

            if isinstance(boxstyle, str) else boxstyle)

        self.stale = True



    def get_boxstyle(self):

        

        return self._bbox_transmuter



    def set_mutation_scale(self, scale):

        

        self._mutation_scale = scale

        self.stale = True



    def get_mutation_scale(self):

        

        return self._mutation_scale



    def set_mutation_aspect(self, aspect):

        

        self._mutation_aspect = aspect

        self.stale = True



    def get_mutation_aspect(self):

        

        return (self._mutation_aspect if self._mutation_aspect is not None

                else 1)               



    def get_path(self):

        

        boxstyle = self.get_boxstyle()

        m_aspect = self.get_mutation_aspect()

                                                                

        path = boxstyle(self._x, self._y / m_aspect,

                        self._width, self._height / m_aspect,

                        self.get_mutation_scale())

        return Path(path.vertices * [1, m_aspect], path.codes)                



                                                              



    def get_x(self):

        

        return self._x



    def get_y(self):

        

        return self._y



    def get_width(self):

        

        return self._width



    def get_height(self):

        

        return self._height



    def set_x(self, x):

        

        self._x = x

        self.stale = True



    def set_y(self, y):

        

        self._y = y

        self.stale = True



    def set_width(self, w):

        

        self._width = w

        self.stale = True



    def set_height(self, h):

        

        self._height = h

        self.stale = True



    def set_bounds(self, *args):

        

        if len(args) == 1:

            l, b, w, h = args[0]

        else:

            l, b, w, h = args

        self._x = l

        self._y = b

        self._width = w

        self._height = h

        self.stale = True



    def get_bbox(self):

        

        return transforms.Bbox.from_bounds(self._x, self._y,

                                           self._width, self._height)





class FancyArrowPatch(Patch):

    

    _edge_default = True



    def __str__(self):

        if self._posA_posB is not None:

            (x1, y1), (x2, y2) = self._posA_posB

            return f"{type(self).__name__}(({x1:g}, {y1:g})->({x2:g}, {y2:g}))"

        else:

            return f"{type(self).__name__}({self._path_original})"



    @_docstring.interpd

    def __init__(self, posA=None, posB=None, *,

                 path=None, arrowstyle="simple", connectionstyle="arc3",

                 patchA=None, patchB=None, shrinkA=2, shrinkB=2,

                 mutation_scale=1, mutation_aspect=1, **kwargs):

        

                                                                             

        kwargs.setdefault("joinstyle", JoinStyle.round)

        kwargs.setdefault("capstyle", CapStyle.round)



        super().__init__(**kwargs)



        if posA is not None and posB is not None and path is None:

            self._posA_posB = [posA, posB]



            if connectionstyle is None:

                connectionstyle = "arc3"

            self.set_connectionstyle(connectionstyle)



        elif posA is None and posB is None and path is not None:

            self._posA_posB = None

        else:

            raise ValueError("Either posA and posB, or path need to provided")



        self.patchA = patchA

        self.patchB = patchB

        self.shrinkA = shrinkA

        self.shrinkB = shrinkB



        self._path_original = path



        self.set_arrowstyle(arrowstyle)



        self._mutation_scale = mutation_scale

        self._mutation_aspect = mutation_aspect



        self._dpi_cor = 1.0



    def set_positions(self, posA, posB):

        

        if posA is not None:

            self._posA_posB[0] = posA

        if posB is not None:

            self._posA_posB[1] = posB

        self.stale = True



    def set_patchA(self, patchA):

        

        self.patchA = patchA

        self.stale = True



    def set_patchB(self, patchB):

        

        self.patchB = patchB

        self.stale = True



    @_docstring.interpd

    def set_connectionstyle(self, connectionstyle=None, **kwargs):

        

        if connectionstyle is None:

            return ConnectionStyle.pprint_styles()

        self._connector = (

            ConnectionStyle(connectionstyle, **kwargs)

            if isinstance(connectionstyle, str) else connectionstyle)

        self.stale = True



    def get_connectionstyle(self):

        

        return self._connector



    @_docstring.interpd

    def set_arrowstyle(self, arrowstyle=None, **kwargs):

        

        if arrowstyle is None:

            return ArrowStyle.pprint_styles()

        self._arrow_transmuter = (

            ArrowStyle(arrowstyle, **kwargs)

            if isinstance(arrowstyle, str) else arrowstyle)

        self.stale = True



    def get_arrowstyle(self):

        

        return self._arrow_transmuter



    def set_mutation_scale(self, scale):

        

        self._mutation_scale = scale

        self.stale = True



    def get_mutation_scale(self):

        

        return self._mutation_scale



    def set_mutation_aspect(self, aspect):

        

        self._mutation_aspect = aspect

        self.stale = True



    def get_mutation_aspect(self):

        

        return (self._mutation_aspect if self._mutation_aspect is not None

                else 1)               



    def get_path(self):

        

                                                                              

                           

        _path, fillable = self._get_path_in_displaycoord()

        if np.iterable(fillable):

            _path = Path.make_compound_path(*_path)

        return self.get_transform().inverted().transform_path(_path)



    def _get_path_in_displaycoord(self):

        

        dpi_cor = self._dpi_cor



        if self._posA_posB is not None:

            posA = self._convert_xy_units(self._posA_posB[0])

            posB = self._convert_xy_units(self._posA_posB[1])

            (posA, posB) = self.get_transform().transform((posA, posB))

            _path = self.get_connectionstyle()(posA, posB,

                                               patchA=self.patchA,

                                               patchB=self.patchB,

                                               shrinkA=self.shrinkA * dpi_cor,

                                               shrinkB=self.shrinkB * dpi_cor

                                               )

        else:

            _path = self.get_transform().transform_path(self._path_original)



        _path, fillable = self.get_arrowstyle()(

            _path,

            self.get_mutation_scale() * dpi_cor,

            self.get_linewidth() * dpi_cor,

            self.get_mutation_aspect())



        return _path, fillable



    def draw(self, renderer):

        if not self.get_visible():

            return



                                                                           

                                                                               

                                                                       

        self._dpi_cor = renderer.points_to_pixels(1.)

        path, fillable = self._get_path_in_displaycoord()



        if not np.iterable(fillable):

            path = [path]

            fillable = [fillable]



        affine = transforms.IdentityTransform()



        self._draw_paths_with_artist_properties(

            renderer,

            [(p, affine, self._facecolor if f and self._facecolor[3] else None)

             for p, f in zip(path, fillable)])





class ConnectionPatch(FancyArrowPatch):

    



    def __str__(self):

        return "ConnectionPatch((%g, %g), (%g, %g))" %
               (self.xy1[0], self.xy1[1], self.xy2[0], self.xy2[1])



    @_docstring.interpd

    def __init__(self, xyA, xyB, coordsA, coordsB=None, *,

                 axesA=None, axesB=None,

                 arrowstyle="-",

                 connectionstyle="arc3",

                 patchA=None,

                 patchB=None,

                 shrinkA=0.,

                 shrinkB=0.,

                 mutation_scale=10.,

                 mutation_aspect=None,

                 clip_on=False,

                 **kwargs):

        

        if coordsB is None:

            coordsB = coordsA

                                                                    

        self.xy1 = xyA

        self.xy2 = xyB

        self.coords1 = coordsA

        self.coords2 = coordsB



        self.axesA = axesA

        self.axesB = axesB



        super().__init__(posA=(0, 0), posB=(1, 1),

                         arrowstyle=arrowstyle,

                         connectionstyle=connectionstyle,

                         patchA=patchA, patchB=patchB,

                         shrinkA=shrinkA, shrinkB=shrinkB,

                         mutation_scale=mutation_scale,

                         mutation_aspect=mutation_aspect,

                         clip_on=clip_on,

                         **kwargs)

                                                                     

        self._annotation_clip = None



    def _get_xy(self, xy, s, axes=None):

        

        s0 = s                                     

        if axes is None:

            axes = self.axes



                                                      

        x = np.array(xy[0])

        y = np.array(xy[1])



        fig = self.get_figure(root=False)

        if s in ["figure points", "axes points"]:

            x = x * fig.dpi / 72

            y = y * fig.dpi / 72

            s = s.replace("points", "pixels")

        elif s == "figure fraction":

            s = fig.transFigure

        elif s == "subfigure fraction":

            s = fig.transSubfigure

        elif s == "axes fraction":

            s = axes.transAxes



        if s == 'data':

            trans = axes.transData

            x = cbook._to_unmasked_float_array(axes.xaxis.convert_units(x))

            y = cbook._to_unmasked_float_array(axes.yaxis.convert_units(y))

            return trans.transform((x, y))

        elif s == 'offset points':

            if self.xycoords == 'offset points':                     

                return self._get_xy(self.xy, 'data')

            return (

                self._get_xy(self.xy, self.xycoords)                        

                + xy * self.get_figure(root=True).dpi / 72)                    

        elif s == 'polar':

            theta, r = x, y

            x = r * np.cos(theta)

            y = r * np.sin(theta)

            trans = axes.transData

            return trans.transform((x, y))

        elif s == 'figure pixels':

                                                             

            bb = self.get_figure(root=False).figbbox

            x = bb.x0 + x if x >= 0 else bb.x1 + x

            y = bb.y0 + y if y >= 0 else bb.y1 + y

            return x, y

        elif s == 'subfigure pixels':

                                                             

            bb = self.get_figure(root=False).bbox

            x = bb.x0 + x if x >= 0 else bb.x1 + x

            y = bb.y0 + y if y >= 0 else bb.y1 + y

            return x, y

        elif s == 'axes pixels':

                                                           

            bb = axes.bbox

            x = bb.x0 + x if x >= 0 else bb.x1 + x

            y = bb.y0 + y if y >= 0 else bb.y1 + y

            return x, y

        elif isinstance(s, transforms.Transform):

            return s.transform(xy)

        else:

            raise ValueError(f"{s0} is not a valid coordinate transformation")



    def set_annotation_clip(self, b):

        

        self._annotation_clip = b

        self.stale = True



    def get_annotation_clip(self):

        

        return self._annotation_clip



    def _get_path_in_displaycoord(self):

        

        dpi_cor = self._dpi_cor

        posA = self._get_xy(self.xy1, self.coords1, self.axesA)

        posB = self._get_xy(self.xy2, self.coords2, self.axesB)

        path = self.get_connectionstyle()(

            posA, posB,

            patchA=self.patchA, patchB=self.patchB,

            shrinkA=self.shrinkA * dpi_cor, shrinkB=self.shrinkB * dpi_cor,

        )

        path, fillable = self.get_arrowstyle()(

            path,

            self.get_mutation_scale() * dpi_cor,

            self.get_linewidth() * dpi_cor,

            self.get_mutation_aspect()

        )

        return path, fillable



    def _check_xy(self, renderer):

        



        b = self.get_annotation_clip()



        if b or (b is None and self.coords1 == "data"):

            xy_pixel = self._get_xy(self.xy1, self.coords1, self.axesA)

            if self.axesA is None:

                axes = self.axes

            else:

                axes = self.axesA

            if not axes.contains_point(xy_pixel):

                return False



        if b or (b is None and self.coords2 == "data"):

            xy_pixel = self._get_xy(self.xy2, self.coords2, self.axesB)

            if self.axesB is None:

                axes = self.axes

            else:

                axes = self.axesB

            if not axes.contains_point(xy_pixel):

                return False



        return True



    def draw(self, renderer):

        if not self.get_visible() or not self._check_xy(renderer):

            return

        super().draw(renderer)

