



                                                                         

                                                                             

                                                                        



import functools

import itertools

import textwrap

import weakref

import math



import numpy as np

from numpy.linalg import inv



from matplotlib import _api

from matplotlib._path import affine_transform, count_bboxes_overlapping_bbox

from .path import Path



DEBUG = False





def _make_str_method(*args, **kwargs):

    

    indent = functools.partial(textwrap.indent, prefix=" " * 4)

    def strrepr(x): return repr(x) if isinstance(x, str) else str(x)

    return lambda self: (

        type(self).__name__ + "("

        + ",".join([*(indent("\n" + strrepr(getattr(self, arg)))

                      for arg in args),

                    *(indent("\n" + k + "=" + strrepr(getattr(self, arg)))

                      for k, arg in kwargs.items())])

        + ")")





class TransformNode:

    



                                                           

                                                                   

                         



                                                 

    _VALID, _INVALID_AFFINE_ONLY, _INVALID_FULL = range(3)



                                                                     

                                 

    is_affine = False



    pass_through = False

    """
    If pass_through is True, all ancestors will always be
    invalidated, even if 'self' is already invalid.
    """



    def __init__(self, shorthand_name=None):

        

        self._parents = {}

                                                     

        self._invalid = self._INVALID_FULL

        self._shorthand_name = shorthand_name or ''



    if DEBUG:

        def __str__(self):

                                                                            

            return self._shorthand_name or repr(self)



    def __getstate__(self):

                                                                       

        return {**self.__dict__,

                '_parents': {k: v() for k, v in self._parents.items()}}



    def __setstate__(self, data_dict):

        self.__dict__ = data_dict

                                                                            

                                                                  

                                                                       

        self._parents = {

            k: weakref.ref(v, lambda _, pop=self._parents.pop, k=k: pop(k))

            for k, v in self._parents.items() if v is not None}



    def __copy__(self):

        cls = type(self)

        other = cls.__new__(cls)

        other.__dict__.update(self.__dict__)

                                                                         

                                                                           

        other._parents = {}

                                                                              

                                

        for key, val in vars(self).items():

            if isinstance(val, TransformNode) and id(self) in val._parents:

                other.set_children(val)                              

        return other



    def invalidate(self):

        

        return self._invalidate_internal(

            level=self._INVALID_AFFINE_ONLY if self.is_affine else self._INVALID_FULL,

            invalidating_node=self)



    def _invalidate_internal(self, level, invalidating_node):

        

                                                                                    

                                            

        if level <= self._invalid and not self.pass_through:

            return

        self._invalid = level

        for parent in list(self._parents.values()):

            parent = parent()                                   

            if parent is not None:

                parent._invalidate_internal(level=level, invalidating_node=self)



    def set_children(self, *children):

        

                                                               

                                                                   

                          

        id_self = id(self)

        for child in children:

                                                                              

                                                                         

                                                                     

            ref = weakref.ref(

                self, lambda _, pop=child._parents.pop, k=id_self: pop(k))

            child._parents[id_self] = ref



    def frozen(self):

        

        return self





class BboxBase(TransformNode):

    



    is_affine = True



    if DEBUG:

        @staticmethod

        def _check(points):

            if isinstance(points, np.ma.MaskedArray):

                _api.warn_external("Bbox bounds are a masked array.")

            points = np.asarray(points)

            if any((points[1, :] - points[0, :]) == 0):

                _api.warn_external("Singular Bbox.")



    def frozen(self):

        return Bbox(self.get_points().copy())

    frozen.__doc__ = TransformNode.__doc__



    def __array__(self, *args, **kwargs):

        return self.get_points()



    @property

    def x0(self):

        

        return self.get_points()[0, 0]



    @property

    def y0(self):

        

        return self.get_points()[0, 1]



    @property

    def x1(self):

        

        return self.get_points()[1, 0]



    @property

    def y1(self):

        

        return self.get_points()[1, 1]



    @property

    def p0(self):

        

        return self.get_points()[0]



    @property

    def p1(self):

        

        return self.get_points()[1]



    @property

    def xmin(self):

        

        return np.min(self.get_points()[:, 0])



    @property

    def ymin(self):

        

        return np.min(self.get_points()[:, 1])



    @property

    def xmax(self):

        

        return np.max(self.get_points()[:, 0])



    @property

    def ymax(self):

        

        return np.max(self.get_points()[:, 1])



    @property

    def min(self):

        

        return np.min(self.get_points(), axis=0)



    @property

    def max(self):

        

        return np.max(self.get_points(), axis=0)



    @property

    def intervalx(self):

        

        return self.get_points()[:, 0]



    @property

    def intervaly(self):

        

        return self.get_points()[:, 1]



    @property

    def width(self):

        

        points = self.get_points()

        return points[1, 0] - points[0, 0]



    @property

    def height(self):

        

        points = self.get_points()

        return points[1, 1] - points[0, 1]



    @property

    def size(self):

        

        points = self.get_points()

        return points[1] - points[0]



    @property

    def bounds(self):

        

        (x0, y0), (x1, y1) = self.get_points()

        return (x0, y0, x1 - x0, y1 - y0)



    @property

    def extents(self):

        

        return self.get_points().flatten()                           



    def get_points(self):

        raise NotImplementedError



    def containsx(self, x):

        

        x0, x1 = self.intervalx

        return x0 <= x <= x1 or x0 >= x >= x1



    def containsy(self, y):

        

        y0, y1 = self.intervaly

        return y0 <= y <= y1 or y0 >= y >= y1



    def contains(self, x, y):

        

        return self.containsx(x) and self.containsy(y)



    def overlaps(self, other):

        

        ax1, ay1, ax2, ay2 = self.extents

        bx1, by1, bx2, by2 = other.extents

        if ax2 < ax1:

            ax2, ax1 = ax1, ax2

        if ay2 < ay1:

            ay2, ay1 = ay1, ay2

        if bx2 < bx1:

            bx2, bx1 = bx1, bx2

        if by2 < by1:

            by2, by1 = by1, by2

        return ax1 <= bx2 and bx1 <= ax2 and ay1 <= by2 and by1 <= ay2



    def fully_containsx(self, x):

        

        x0, x1 = self.intervalx

        return x0 < x < x1 or x0 > x > x1



    def fully_containsy(self, y):

        

        y0, y1 = self.intervaly

        return y0 < y < y1 or y0 > y > y1



    def fully_contains(self, x, y):

        

        return self.fully_containsx(x) and self.fully_containsy(y)



    def fully_overlaps(self, other):

        

        ax1, ay1, ax2, ay2 = self.extents

        bx1, by1, bx2, by2 = other.extents

        if ax2 < ax1:

            ax2, ax1 = ax1, ax2

        if ay2 < ay1:

            ay2, ay1 = ay1, ay2

        if bx2 < bx1:

            bx2, bx1 = bx1, bx2

        if by2 < by1:

            by2, by1 = by1, by2

        return ax1 < bx2 and bx1 < ax2 and ay1 < by2 and by1 < ay2



    def transformed(self, transform):

        

        pts = self.get_points()

        ll, ul, lr = transform.transform(np.array(

            [pts[0], [pts[0, 0], pts[1, 1]], [pts[1, 0], pts[0, 1]]]))

        return Bbox([ll, [lr[0], ul[1]]])



    coefs = {'C':  (0.5, 0.5),

             'SW': (0, 0),

             'S':  (0.5, 0),

             'SE': (1.0, 0),

             'E':  (1.0, 0.5),

             'NE': (1.0, 1.0),

             'N':  (0.5, 1.0),

             'NW': (0, 1.0),

             'W':  (0, 0.5)}



    def anchored(self, c, container):

        

        l, b, w, h = container.bounds

        L, B, W, H = self.bounds

        cx, cy = self.coefs[c] if isinstance(c, str) else c

        return Bbox(self._points +

                    [(l + cx * (w - W)) - L,

                     (b + cy * (h - H)) - B])



    def shrunk(self, mx, my):

        

        w, h = self.size

        return Bbox([self._points[0],

                     self._points[0] + [mx * w, my * h]])



    def shrunk_to_aspect(self, box_aspect, container=None, fig_aspect=1.0):

        

        if box_aspect <= 0 or fig_aspect <= 0:

            raise ValueError("'box_aspect' and 'fig_aspect' must be positive")

        if container is None:

            container = self

        w, h = container.size

        H = w * box_aspect / fig_aspect

        if H <= h:

            W = w

        else:

            W = h * fig_aspect / box_aspect

            H = h

        return Bbox([self._points[0],

                     self._points[0] + (W, H)])



    def splitx(self, *args):

        

        xf = [0, *args, 1]

        x0, y0, x1, y1 = self.extents

        w = x1 - x0

        return [Bbox([[x0 + xf0 * w, y0], [x0 + xf1 * w, y1]])

                for xf0, xf1 in itertools.pairwise(xf)]



    def splity(self, *args):

        

        yf = [0, *args, 1]

        x0, y0, x1, y1 = self.extents

        h = y1 - y0

        return [Bbox([[x0, y0 + yf0 * h], [x1, y0 + yf1 * h]])

                for yf0, yf1 in itertools.pairwise(yf)]



    def count_contains(self, vertices):

        

        if len(vertices) == 0:

            return 0

        vertices = np.asarray(vertices)

        with np.errstate(invalid='ignore'):

            return (((self.min < vertices) &

                     (vertices < self.max)).all(axis=1).sum())



    def count_overlaps(self, bboxes):

        

        return count_bboxes_overlapping_bbox(

            self, np.atleast_3d([np.array(x) for x in bboxes]))



    def expanded(self, sw, sh):

        

        width = self.width

        height = self.height

        deltaw = (sw * width - width) / 2.0

        deltah = (sh * height - height) / 2.0

        a = np.array([[-deltaw, -deltah], [deltaw, deltah]])

        return Bbox(self._points + a)



    def padded(self, w_pad, h_pad=None):

        

        points = self.get_points()

        if h_pad is None:

            h_pad = w_pad

        return Bbox(points + [[-w_pad, -h_pad], [w_pad, h_pad]])



    def translated(self, tx, ty):

        

        return Bbox(self._points + (tx, ty))



    def corners(self):

        

        (x0, y0), (x1, y1) = self.get_points()

        return np.array([[x0, y0], [x0, y1], [x1, y0], [x1, y1]])



    def rotated(self, radians):

        

        corners = self.corners()

        corners_rotated = Affine2D().rotate(radians).transform(corners)

        bbox = Bbox.unit()

        bbox.update_from_data_xy(corners_rotated, ignore=True)

        return bbox



    @staticmethod

    def union(bboxes):

        

        if not len(bboxes):

            raise ValueError("'bboxes' cannot be empty")

        x0 = np.min([bbox.xmin for bbox in bboxes])

        x1 = np.max([bbox.xmax for bbox in bboxes])

        y0 = np.min([bbox.ymin for bbox in bboxes])

        y1 = np.max([bbox.ymax for bbox in bboxes])

        return Bbox([[x0, y0], [x1, y1]])



    @staticmethod

    def intersection(bbox1, bbox2):

        

        x0 = np.maximum(bbox1.xmin, bbox2.xmin)

        x1 = np.minimum(bbox1.xmax, bbox2.xmax)

        y0 = np.maximum(bbox1.ymin, bbox2.ymin)

        y1 = np.minimum(bbox1.ymax, bbox2.ymax)

        return Bbox([[x0, y0], [x1, y1]]) if x0 <= x1 and y0 <= y1 else None





_default_minpos = np.array([np.inf, np.inf])





class Bbox(BboxBase):

    



    def __init__(self, points, **kwargs):

        

        super().__init__(**kwargs)

        points = np.asarray(points, float)

        if points.shape != (2, 2):

            raise ValueError('Bbox points must be of the form '

                             '"[[x0, y0], [x1, y1]]".')

        self._points = points

        self._minpos = _default_minpos.copy()

        self._ignore = True

                                                                 

                                                                  

                                     

        self._points_orig = self._points.copy()

    if DEBUG:

        ___init__ = __init__



        def __init__(self, points, **kwargs):

            self._check(points)

            self.___init__(points, **kwargs)



        def invalidate(self):

            self._check(self._points)

            super().invalidate()



    def frozen(self):

                             

        frozen_bbox = super().frozen()

        frozen_bbox._minpos = self.minpos.copy()

        return frozen_bbox



    @staticmethod

    def unit():

        

        return Bbox([[0, 0], [1, 1]])



    @staticmethod

    def null():

        

        return Bbox([[np.inf, np.inf], [-np.inf, -np.inf]])



    @staticmethod

    def from_bounds(x0, y0, width, height):

        

        return Bbox.from_extents(x0, y0, x0 + width, y0 + height)



    @staticmethod

    def from_extents(*args, minpos=None):

        

        bbox = Bbox(np.reshape(args, (2, 2)))

        if minpos is not None:

            bbox._minpos[:] = minpos

        return bbox



    def __format__(self, fmt):

        return (

            'Bbox(x0={0.x0:{1}}, y0={0.y0:{1}}, x1={0.x1:{1}}, y1={0.y1:{1}})'.

            format(self, fmt))



    def __str__(self):

        return format(self, '')



    def __repr__(self):

        return 'Bbox([[{0.x0}, {0.y0}], [{0.x1}, {0.y1}]])'.format(self)



    def ignore(self, value):

        

        self._ignore = value



    def update_from_path(self, path, ignore=None, updatex=True, updatey=True):

        

        if ignore is None:

            ignore = self._ignore



        if path.vertices.size == 0 or not (updatex or updatey):

            return



        if ignore:

            points = np.array([[np.inf, np.inf], [-np.inf, -np.inf]])

            minpos = np.array([np.inf, np.inf])

        else:

            points = self._points.copy()

            minpos = self._minpos.copy()



        valid_points = (np.isfinite(path.vertices[..., 0])

                        & np.isfinite(path.vertices[..., 1]))



        if updatex:

            x = path.vertices[..., 0][valid_points]

            points[0, 0] = min(points[0, 0], np.min(x, initial=np.inf))

            points[1, 0] = max(points[1, 0], np.max(x, initial=-np.inf))

            minpos[0] = min(minpos[0], np.min(x[x > 0], initial=np.inf))

        if updatey:

            y = path.vertices[..., 1][valid_points]

            points[0, 1] = min(points[0, 1], np.min(y, initial=np.inf))

            points[1, 1] = max(points[1, 1], np.max(y, initial=-np.inf))

            minpos[1] = min(minpos[1], np.min(y[y > 0], initial=np.inf))



        if np.any(points != self._points) or np.any(minpos != self._minpos):

            self.invalidate()

            if updatex:

                self._points[:, 0] = points[:, 0]

                self._minpos[0] = minpos[0]

            if updatey:

                self._points[:, 1] = points[:, 1]

                self._minpos[1] = minpos[1]



    def update_from_data_x(self, x, ignore=None):

        

        x = np.ravel(x)

                                                                             

                                                                             

        self.update_from_data_xy(np.array([x, x]).T, ignore=ignore, updatey=False)



    def update_from_data_y(self, y, ignore=None):

        

        y = np.ravel(y)

                                                                             

                                                                             

        self.update_from_data_xy(np.array([y, y]).T, ignore=ignore, updatex=False)



    def update_from_data_xy(self, xy, ignore=None, updatex=True, updatey=True):

        

        if len(xy) == 0:

            return



        path = Path(xy)

        self.update_from_path(path, ignore=ignore,

                              updatex=updatex, updatey=updatey)



    @BboxBase.x0.setter

    def x0(self, val):

        self._points[0, 0] = val

        self.invalidate()



    @BboxBase.y0.setter

    def y0(self, val):

        self._points[0, 1] = val

        self.invalidate()



    @BboxBase.x1.setter

    def x1(self, val):

        self._points[1, 0] = val

        self.invalidate()



    @BboxBase.y1.setter

    def y1(self, val):

        self._points[1, 1] = val

        self.invalidate()



    @BboxBase.p0.setter

    def p0(self, val):

        self._points[0] = val

        self.invalidate()



    @BboxBase.p1.setter

    def p1(self, val):

        self._points[1] = val

        self.invalidate()



    @BboxBase.intervalx.setter

    def intervalx(self, interval):

        self._points[:, 0] = interval

        self.invalidate()



    @BboxBase.intervaly.setter

    def intervaly(self, interval):

        self._points[:, 1] = interval

        self.invalidate()



    @BboxBase.bounds.setter

    def bounds(self, bounds):

        l, b, w, h = bounds

        points = np.array([[l, b], [l + w, b + h]], float)

        if np.any(self._points != points):

            self._points = points

            self.invalidate()



    @property

    def minpos(self):

        

        return self._minpos



    @minpos.setter

    def minpos(self, val):

        self._minpos[:] = val



    @property

    def minposx(self):

        

        return self._minpos[0]



    @minposx.setter

    def minposx(self, val):

        self._minpos[0] = val



    @property

    def minposy(self):

        

        return self._minpos[1]



    @minposy.setter

    def minposy(self, val):

        self._minpos[1] = val



    def get_points(self):

        

        self._invalid = 0

        return self._points



    def set_points(self, points):

        

        if np.any(self._points != points):

            self._points = points

            self.invalidate()



    def set(self, other):

        

        if np.any(self._points != other.get_points()):

            self._points = other.get_points()

            self.invalidate()



    def mutated(self):

        

        return self.mutatedx() or self.mutatedy()



    def mutatedx(self):

        

        return (self._points[0, 0] != self._points_orig[0, 0] or

                self._points[1, 0] != self._points_orig[1, 0])



    def mutatedy(self):

        

        return (self._points[0, 1] != self._points_orig[0, 1] or

                self._points[1, 1] != self._points_orig[1, 1])





class TransformedBbox(BboxBase):

    



    def __init__(self, bbox, transform, **kwargs):

        

        _api.check_isinstance(BboxBase, bbox=bbox)

        _api.check_isinstance(Transform, transform=transform)

        if transform.input_dims != 2 or transform.output_dims != 2:

            raise ValueError(

                "The input and output dimensions of 'transform' must be 2")



        super().__init__(**kwargs)

        self._bbox = bbox

        self._transform = transform

        self.set_children(bbox, transform)

        self._points = None



    __str__ = _make_str_method("_bbox", "_transform")



    def get_points(self):

                             

        if self._invalid:

            p = self._bbox.get_points()

                                                                     

                                                                      

                   

            points = self._transform.transform(

                [[p[0, 0], p[0, 1]],

                 [p[1, 0], p[0, 1]],

                 [p[0, 0], p[1, 1]],

                 [p[1, 0], p[1, 1]]])

            points = np.ma.filled(points, 0.0)



            xs = min(points[:, 0]), max(points[:, 0])

            if p[0, 0] > p[1, 0]:

                xs = xs[::-1]



            ys = min(points[:, 1]), max(points[:, 1])

            if p[0, 1] > p[1, 1]:

                ys = ys[::-1]



            self._points = np.array([

                [xs[0], ys[0]],

                [xs[1], ys[1]]

            ])



            self._invalid = 0

        return self._points



    if DEBUG:

        _get_points = get_points



        def get_points(self):

            points = self._get_points()

            self._check(points)

            return points



    def contains(self, x, y):

                              

        return self._bbox.contains(*self._transform.inverted().transform((x, y)))



    def fully_contains(self, x, y):

                              

        return self._bbox.fully_contains(*self._transform.inverted().transform((x, y)))





class LockableBbox(BboxBase):

    

    def __init__(self, bbox, x0=None, y0=None, x1=None, y1=None, **kwargs):

        

        _api.check_isinstance(BboxBase, bbox=bbox)

        super().__init__(**kwargs)

        self._bbox = bbox

        self.set_children(bbox)

        self._points = None

        fp = [x0, y0, x1, y1]

        mask = [val is None for val in fp]

        self._locked_points = np.ma.array(fp, float, mask=mask).reshape((2, 2))



    __str__ = _make_str_method("_bbox", "_locked_points")



    def get_points(self):

                             

        if self._invalid:

            points = self._bbox.get_points()

            self._points = np.where(self._locked_points.mask,

                                    points,

                                    self._locked_points)

            self._invalid = 0

        return self._points



    if DEBUG:

        _get_points = get_points



        def get_points(self):

            points = self._get_points()

            self._check(points)

            return points



    @property

    def locked_x0(self):

        

        if self._locked_points.mask[0, 0]:

            return None

        else:

            return self._locked_points[0, 0]



    @locked_x0.setter

    def locked_x0(self, x0):

        self._locked_points.mask[0, 0] = x0 is None

        self._locked_points.data[0, 0] = x0

        self.invalidate()



    @property

    def locked_y0(self):

        

        if self._locked_points.mask[0, 1]:

            return None

        else:

            return self._locked_points[0, 1]



    @locked_y0.setter

    def locked_y0(self, y0):

        self._locked_points.mask[0, 1] = y0 is None

        self._locked_points.data[0, 1] = y0

        self.invalidate()



    @property

    def locked_x1(self):

        

        if self._locked_points.mask[1, 0]:

            return None

        else:

            return self._locked_points[1, 0]



    @locked_x1.setter

    def locked_x1(self, x1):

        self._locked_points.mask[1, 0] = x1 is None

        self._locked_points.data[1, 0] = x1

        self.invalidate()



    @property

    def locked_y1(self):

        

        if self._locked_points.mask[1, 1]:

            return None

        else:

            return self._locked_points[1, 1]



    @locked_y1.setter

    def locked_y1(self, y1):

        self._locked_points.mask[1, 1] = y1 is None

        self._locked_points.data[1, 1] = y1

        self.invalidate()





class Transform(TransformNode):

    



    input_dims = None

    """
    The number of input dimensions of this transform.
    Must be overridden (with integers) in the subclass.
    """



    output_dims = None

    """
    The number of output dimensions of this transform.
    Must be overridden (with integers) in the subclass.
    """



    is_separable = False

    """True if this transform is separable in the x- and y- dimensions."""



    has_inverse = False

    """True if this transform has a corresponding inverse transform."""



    def __init_subclass__(cls):

                                                                               

                                                                              

                                                                               

                                                         

        if (sum("is_separable" in vars(parent) for parent in cls.__mro__) == 1

                and cls.input_dims == cls.output_dims == 1):

            cls.is_separable = True

                                                                               

                                                                              

                                   

        if (sum("has_inverse" in vars(parent) for parent in cls.__mro__) == 1

                and hasattr(cls, "inverted")

                and cls.inverted is not Transform.inverted):

            cls.has_inverse = True



    def __add__(self, other):

        

        return (composite_transform_factory(self, other)

                if isinstance(other, Transform) else

                NotImplemented)



                                                                        

                                                                         

                                         



    def _iter_break_from_left_to_right(self):

        

        yield IdentityTransform(), self



    @property

    def depth(self):

        

        return 1



    def contains_branch(self, other):

        

        if self.depth < other.depth:

            return False



                                                                     

        for _, sub_tree in self._iter_break_from_left_to_right():

            if sub_tree == other:

                return True

        return False



    def contains_branch_seperately(self, other_transform):

        

        if self.output_dims != 2:

            raise ValueError('contains_branch_seperately only supports '

                             'transforms with 2 output dimensions')

                                                                             

                                            

        return (self.contains_branch(other_transform), ) * 2



    def __sub__(self, other):

        

                                                                        

        if not isinstance(other, Transform):

            return NotImplemented

        for remainder, sub_tree in self._iter_break_from_left_to_right():

            if sub_tree == other:

                return remainder

        for remainder, sub_tree in other._iter_break_from_left_to_right():

            if sub_tree == self:

                if not remainder.has_inverse:

                    raise ValueError(

                        "The shortcut cannot be computed since 'other' "

                        "includes a non-invertible component")

                return remainder.inverted()

                                                                      

        if other.has_inverse:

            return self + other.inverted()

        else:

            raise ValueError('It is not possible to compute transA - transB '

                             'since transB cannot be inverted and there is no '

                             'shortcut possible.')



    def __array__(self, *args, **kwargs):

        

        return self.get_affine().get_matrix()



    def transform(self, values):

        

                                                                

                                            

        values = np.asanyarray(values)

        ndim = values.ndim

        values = values.reshape((-1, self.input_dims))



                              

        res = self.transform_affine(self.transform_non_affine(values))



                                                                   

        if ndim == 0:

            assert not np.ma.is_masked(res)                               

            return res[0, 0]

        if ndim == 1:

            return res.reshape(-1)

        elif ndim == 2:

            return res

        raise ValueError(

            "Input values must have shape (N, {dims}) or ({dims},)"

            .format(dims=self.input_dims))



    def transform_affine(self, values):

        

        return self.get_affine().transform(values)



    def transform_non_affine(self, values):

        

        return values



    def transform_bbox(self, bbox):

        

        return Bbox(self.transform(bbox.get_points()))



    def get_affine(self):

        

        return IdentityTransform()



    def get_matrix(self):

        

        return self.get_affine().get_matrix()



    def transform_point(self, point):

        

        if len(point) != self.input_dims:

            raise ValueError("The length of 'point' must be 'self.input_dims'")

        return self.transform(point)



    def transform_path(self, path):

        

        return self.transform_path_affine(self.transform_path_non_affine(path))



    def transform_path_affine(self, path):

        

        return self.get_affine().transform_path_affine(path)



    def transform_path_non_affine(self, path):

        

        x = self.transform_non_affine(path.vertices)

        return Path._fast_from_codes_and_verts(x, path.codes, path)



    def transform_angles(self, angles, pts, radians=False, pushoff=1e-5):

        

                    

        if self.input_dims != 2 or self.output_dims != 2:

            raise NotImplementedError('Only defined in 2D')

        angles = np.asarray(angles)

        pts = np.asarray(pts)

        _api.check_shape((None, 2), pts=pts)

        _api.check_shape((None,), angles=angles)

        if len(angles) != len(pts):

            raise ValueError("There must be as many 'angles' as 'pts'")

                                       

        if not radians:

            angles = np.deg2rad(angles)

                                    

        pts2 = pts + pushoff * np.column_stack([np.cos(angles),

                                                np.sin(angles)])

                                       

        tpts = self.transform(pts)

        tpts2 = self.transform(pts2)

                                      

        d = tpts2 - tpts

        a = np.arctan2(d[:, 1], d[:, 0])

                                            

        if not radians:

            a = np.rad2deg(a)

        return a



    def inverted(self):

        

        raise NotImplementedError()





class TransformWrapper(Transform):

    



    pass_through = True



    def __init__(self, child):

        

        _api.check_isinstance(Transform, child=child)

        super().__init__()

        self.set(child)



    def __eq__(self, other):

        return self._child.__eq__(other)



    __str__ = _make_str_method("_child")



    def frozen(self):

                             

        return self._child.frozen()



    def set(self, child):

        

        if hasattr(self, "_child"):                       

            self.invalidate()

            new_dims = (child.input_dims, child.output_dims)

            old_dims = (self._child.input_dims, self._child.output_dims)

            if new_dims != old_dims:

                raise ValueError(

                    f"The input and output dims of the new child {new_dims} "

                    f"do not match those of current child {old_dims}")

            self._child._parents.pop(id(self), None)



        self._child = child

        self.set_children(child)



        self.transform = child.transform

        self.transform_affine = child.transform_affine

        self.transform_non_affine = child.transform_non_affine

        self.transform_path = child.transform_path

        self.transform_path_affine = child.transform_path_affine

        self.transform_path_non_affine = child.transform_path_non_affine

        self.get_affine = child.get_affine

        self.inverted = child.inverted

        self.get_matrix = child.get_matrix

                                                                         

                                                                        

                                                               



        self._invalid = 0

        self.invalidate()

        self._invalid = 0



    input_dims = property(lambda self: self._child.input_dims)

    output_dims = property(lambda self: self._child.output_dims)

    is_affine = property(lambda self: self._child.is_affine)

    is_separable = property(lambda self: self._child.is_separable)

    has_inverse = property(lambda self: self._child.has_inverse)





class AffineBase(Transform):

    

    is_affine = True



    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._inverted = None



    def __array__(self, *args, **kwargs):

                                                                         

        return self.get_matrix()



    def __eq__(self, other):

        if getattr(other, "is_affine", False) and hasattr(other, "get_matrix"):

            return (self.get_matrix() == other.get_matrix()).all()

        return NotImplemented



    def transform(self, values):

                             

        return self.transform_affine(values)



    def transform_affine(self, values):

                             

        raise NotImplementedError('Affine subclasses should override this '

                                  'method.')



    def transform_non_affine(self, values):

                             

        return values



    def transform_path(self, path):

                             

        return self.transform_path_affine(path)



    def transform_path_affine(self, path):

                             

        return Path(self.transform_affine(path.vertices),

                    path.codes, path._interpolation_steps)



    def transform_path_non_affine(self, path):

                             

        return path



    def get_affine(self):

                             

        return self





class Affine2DBase(AffineBase):

    

    input_dims = 2

    output_dims = 2



    def frozen(self):

                             

        return Affine2D(self.get_matrix().copy())



    @property

    def is_separable(self):

        mtx = self.get_matrix()

        return mtx[0, 1] == mtx[1, 0] == 0.0



    def to_values(self):

        

        mtx = self.get_matrix()

        return tuple(mtx[:2].swapaxes(0, 1).flat)



    def transform_affine(self, values):

        mtx = self.get_matrix()

        if isinstance(values, np.ma.MaskedArray):

            tpoints = affine_transform(values.data, mtx)

            return np.ma.MaskedArray(tpoints, mask=np.ma.getmask(values))

        return affine_transform(values, mtx)



    if DEBUG:

        _transform_affine = transform_affine



        def transform_affine(self, values):

                                 

                                                                 

                                                                   

                                                          

            if not isinstance(values, np.ndarray):

                _api.warn_external(

                    f'A non-numpy array of type {type(values)} was passed in '

                    f'for transformation, which results in poor performance.')

            return self._transform_affine(values)



    def inverted(self):

                             

        if self._inverted is None or self._invalid:

            mtx = self.get_matrix()

            shorthand_name = None

            if self._shorthand_name:

                shorthand_name = '(%s)-1' % self._shorthand_name

            self._inverted = Affine2D(inv(mtx), shorthand_name=shorthand_name)

            self._invalid = 0

        return self._inverted





class Affine2D(Affine2DBase):

    



    def __init__(self, matrix=None, **kwargs):

        

        super().__init__(**kwargs)

        if matrix is None:

                                               

            matrix = IdentityTransform._mtx

        self._mtx = matrix.copy()

        self._invalid = 0



    _base_str = _make_str_method("_mtx")



    def __str__(self):

        return (self._base_str()

                if (self._mtx != np.diag(np.diag(self._mtx))).any()

                else f"Affine2D().scale({self._mtx[0, 0]}, {self._mtx[1, 1]})"

                if self._mtx[0, 0] != self._mtx[1, 1]

                else f"Affine2D().scale({self._mtx[0, 0]})")



    @staticmethod

    def from_values(a, b, c, d, e, f):

        

        return Affine2D(

            np.array([a, c, e, b, d, f, 0.0, 0.0, 1.0], float).reshape((3, 3)))



    def get_matrix(self):

        

        if self._invalid:

            self._inverted = None

            self._invalid = 0

        return self._mtx



    def set_matrix(self, mtx):

        

        self._mtx = mtx

        self.invalidate()



    def set(self, other):

        

        _api.check_isinstance(Affine2DBase, other=other)

        self._mtx = other.get_matrix()

        self.invalidate()



    def clear(self):

        

                                           

        self._mtx = IdentityTransform._mtx.copy()

        self.invalidate()

        return self



    def rotate(self, theta):

        

        a = math.cos(theta)

        b = math.sin(theta)

        mtx = self._mtx

                                                                      

        (xx, xy, x0), (yx, yy, y0), _ = mtx.tolist()

                                                  

        mtx[0, 0] = a * xx - b * yx

        mtx[0, 1] = a * xy - b * yy

        mtx[0, 2] = a * x0 - b * y0

        mtx[1, 0] = b * xx + a * yx

        mtx[1, 1] = b * xy + a * yy

        mtx[1, 2] = b * x0 + a * y0

        self.invalidate()

        return self



    def rotate_deg(self, degrees):

        

        return self.rotate(math.radians(degrees))



    def rotate_around(self, x, y, theta):

        

        return self.translate(-x, -y).rotate(theta).translate(x, y)



    def rotate_deg_around(self, x, y, degrees):

        

                                                               

        x, y = float(x), float(y)

        return self.translate(-x, -y).rotate_deg(degrees).translate(x, y)



    def translate(self, tx, ty):

        

        self._mtx[0, 2] += tx

        self._mtx[1, 2] += ty

        self.invalidate()

        return self



    def scale(self, sx, sy=None):

        

        if sy is None:

            sy = sx

                                                  

        self._mtx[0, 0] *= sx

        self._mtx[0, 1] *= sx

        self._mtx[0, 2] *= sx

        self._mtx[1, 0] *= sy

        self._mtx[1, 1] *= sy

        self._mtx[1, 2] *= sy

        self.invalidate()

        return self



    def skew(self, xShear, yShear):

        

        rx = math.tan(xShear)

        ry = math.tan(yShear)

        mtx = self._mtx

                                                                      

        (xx, xy, x0), (yx, yy, y0), _ = mtx.tolist()

                                                   

        mtx[0, 0] += rx * yx

        mtx[0, 1] += rx * yy

        mtx[0, 2] += rx * y0

        mtx[1, 0] += ry * xx

        mtx[1, 1] += ry * xy

        mtx[1, 2] += ry * x0

        self.invalidate()

        return self



    def skew_deg(self, xShear, yShear):

        

        return self.skew(math.radians(xShear), math.radians(yShear))





class IdentityTransform(Affine2DBase):

    

    _mtx = np.identity(3)



    def frozen(self):

                             

        return self



    __str__ = _make_str_method()



    def get_matrix(self):

                             

        return self._mtx



    def transform(self, values):

                             

        return np.asanyarray(values)



    def transform_affine(self, values):

                             

        return np.asanyarray(values)



    def transform_non_affine(self, values):

                             

        return np.asanyarray(values)



    def transform_path(self, path):

                             

        return path



    def transform_path_affine(self, path):

                             

        return path



    def transform_path_non_affine(self, path):

                             

        return path



    def get_affine(self):

                             

        return self



    def inverted(self):

                             

        return self





class _BlendedMixin:

    



    def __eq__(self, other):

        if isinstance(other, (BlendedAffine2D, BlendedGenericTransform)):

            return (self._x == other._x) and (self._y == other._y)

        elif self._x == self._y:

            return self._x == other

        else:

            return NotImplemented



    def contains_branch_seperately(self, transform):

        return (self._x.contains_branch(transform),

                self._y.contains_branch(transform))



    __str__ = _make_str_method("_x", "_y")





class BlendedGenericTransform(_BlendedMixin, Transform):

    

    input_dims = 2

    output_dims = 2

    is_separable = True

    pass_through = True



    def __init__(self, x_transform, y_transform, **kwargs):

        

        Transform.__init__(self, **kwargs)

        self._x = x_transform

        self._y = y_transform

        self.set_children(x_transform, y_transform)

        self._affine = None



    @property

    def depth(self):

        return max(self._x.depth, self._y.depth)



    def contains_branch(self, other):

                                                                       

                               

        return False



    is_affine = property(lambda self: self._x.is_affine and self._y.is_affine)

    has_inverse = property(

        lambda self: self._x.has_inverse and self._y.has_inverse)



    def frozen(self):

                             

        return blended_transform_factory(self._x.frozen(), self._y.frozen())



    def transform_non_affine(self, values):

                             

        if self._x.is_affine and self._y.is_affine:

            return values

        x = self._x

        y = self._y



        if x == y and x.input_dims == 2:

            return x.transform_non_affine(values)



        if x.input_dims == 2:

            x_points = x.transform_non_affine(values)[:, 0:1]

        else:

            x_points = x.transform_non_affine(values[:, 0])

            x_points = x_points.reshape((len(x_points), 1))



        if y.input_dims == 2:

            y_points = y.transform_non_affine(values)[:, 1:]

        else:

            y_points = y.transform_non_affine(values[:, 1])

            y_points = y_points.reshape((len(y_points), 1))



        if (isinstance(x_points, np.ma.MaskedArray) or

                isinstance(y_points, np.ma.MaskedArray)):

            return np.ma.concatenate((x_points, y_points), 1)

        else:

            return np.concatenate((x_points, y_points), 1)



    def inverted(self):

                             

        return BlendedGenericTransform(self._x.inverted(), self._y.inverted())



    def get_affine(self):

                             

        if self._invalid or self._affine is None:

            if self._x == self._y:

                self._affine = self._x.get_affine()

            else:

                x_mtx = self._x.get_affine().get_matrix()

                y_mtx = self._y.get_affine().get_matrix()

                                                                              

                                          

                mtx = np.array([x_mtx[0], y_mtx[1], [0.0, 0.0, 1.0]])

                self._affine = Affine2D(mtx)

            self._invalid = 0

        return self._affine





class BlendedAffine2D(_BlendedMixin, Affine2DBase):

    



    is_separable = True



    def __init__(self, x_transform, y_transform, **kwargs):

        

        is_affine = x_transform.is_affine and y_transform.is_affine

        is_separable = x_transform.is_separable and y_transform.is_separable

        is_correct = is_affine and is_separable

        if not is_correct:

            raise ValueError("Both *x_transform* and *y_transform* must be 2D "

                             "affine transforms")



        Transform.__init__(self, **kwargs)

        self._x = x_transform

        self._y = y_transform

        self.set_children(x_transform, y_transform)



        Affine2DBase.__init__(self)

        self._mtx = None



    def get_matrix(self):

                             

        if self._invalid:

            if self._x == self._y:

                self._mtx = self._x.get_matrix()

            else:

                x_mtx = self._x.get_matrix()

                y_mtx = self._y.get_matrix()

                                                                              

                                          

                self._mtx = np.array([x_mtx[0], y_mtx[1], [0.0, 0.0, 1.0]])

            self._inverted = None

            self._invalid = 0

        return self._mtx





def blended_transform_factory(x_transform, y_transform):

    

    if (isinstance(x_transform, Affine2DBase) and

            isinstance(y_transform, Affine2DBase)):

        return BlendedAffine2D(x_transform, y_transform)

    return BlendedGenericTransform(x_transform, y_transform)





class CompositeGenericTransform(Transform):

    

    pass_through = True



    def __init__(self, a, b, **kwargs):

        

        if a.output_dims != b.input_dims:

            raise ValueError("The output dimension of 'a' must be equal to "

                             "the input dimensions of 'b'")

        self.input_dims = a.input_dims

        self.output_dims = b.output_dims



        super().__init__(**kwargs)

        self._a = a

        self._b = b

        self.set_children(a, b)



    def frozen(self):

                             

        self._invalid = 0

        frozen = composite_transform_factory(

            self._a.frozen(), self._b.frozen())

        if not isinstance(frozen, CompositeGenericTransform):

            return frozen.frozen()

        return frozen



    def _invalidate_internal(self, level, invalidating_node):

                                                                                        

                                                                   

        if invalidating_node is self._a and not self._b.is_affine:

            level = Transform._INVALID_FULL

        super()._invalidate_internal(level, invalidating_node)



    def __eq__(self, other):

        if isinstance(other, (CompositeGenericTransform, CompositeAffine2D)):

            return self is other or (self._a == other._a

                                     and self._b == other._b)

        else:

            return False



    def _iter_break_from_left_to_right(self):

        for left, right in self._a._iter_break_from_left_to_right():

            yield left, right + self._b

        for left, right in self._b._iter_break_from_left_to_right():

            yield self._a + left, right



    def contains_branch_seperately(self, other_transform):

                             

        if self.output_dims != 2:

            raise ValueError('contains_branch_seperately only supports '

                             'transforms with 2 output dimensions')

        if self == other_transform:

            return (True, True)

        return self._b.contains_branch_seperately(other_transform)



    depth = property(lambda self: self._a.depth + self._b.depth)

    is_affine = property(lambda self: self._a.is_affine and self._b.is_affine)

    is_separable = property(

        lambda self: self._a.is_separable and self._b.is_separable)

    has_inverse = property(

        lambda self: self._a.has_inverse and self._b.has_inverse)



    __str__ = _make_str_method("_a", "_b")



    def transform_affine(self, values):

                             

        return self.get_affine().transform(values)



    def transform_non_affine(self, values):

                             

        if self._a.is_affine and self._b.is_affine:

            return values

        elif not self._a.is_affine and self._b.is_affine:

            return self._a.transform_non_affine(values)

        else:

            return self._b.transform_non_affine(self._a.transform(values))



    def transform_path_non_affine(self, path):

                             

        if self._a.is_affine and self._b.is_affine:

            return path

        elif not self._a.is_affine and self._b.is_affine:

            return self._a.transform_path_non_affine(path)

        else:

            return self._b.transform_path_non_affine(

                                    self._a.transform_path(path))



    def get_affine(self):

                             

        if not self._b.is_affine:

            return self._b.get_affine()

        else:

            return Affine2D(np.dot(self._b.get_affine().get_matrix(),

                                   self._a.get_affine().get_matrix()))



    def inverted(self):

                             

        return CompositeGenericTransform(

            self._b.inverted(), self._a.inverted())





class CompositeAffine2D(Affine2DBase):

    

    def __init__(self, a, b, **kwargs):

        

        if not a.is_affine or not b.is_affine:

            raise ValueError("'a' and 'b' must be affine transforms")

        if a.output_dims != b.input_dims:

            raise ValueError("The output dimension of 'a' must be equal to "

                             "the input dimensions of 'b'")

        self.input_dims = a.input_dims

        self.output_dims = b.output_dims



        super().__init__(**kwargs)

        self._a = a

        self._b = b

        self.set_children(a, b)

        self._mtx = None



    @property

    def depth(self):

        return self._a.depth + self._b.depth



    def _iter_break_from_left_to_right(self):

        for left, right in self._a._iter_break_from_left_to_right():

            yield left, right + self._b

        for left, right in self._b._iter_break_from_left_to_right():

            yield self._a + left, right



    __str__ = _make_str_method("_a", "_b")



    def get_matrix(self):

                             

        if self._invalid:

            self._mtx = np.dot(

                self._b.get_matrix(),

                self._a.get_matrix())

            self._inverted = None

            self._invalid = 0

        return self._mtx





def composite_transform_factory(a, b):

    

                                                                  

                                                                    

                                                                 

                                          

    if isinstance(a, IdentityTransform):

        return b

    elif isinstance(b, IdentityTransform):

        return a

    elif isinstance(a, Affine2D) and isinstance(b, Affine2D):

        return CompositeAffine2D(a, b)

    return CompositeGenericTransform(a, b)





class BboxTransform(Affine2DBase):

    



    is_separable = True



    def __init__(self, boxin, boxout, **kwargs):

        

        _api.check_isinstance(BboxBase, boxin=boxin, boxout=boxout)



        super().__init__(**kwargs)

        self._boxin = boxin

        self._boxout = boxout

        self.set_children(boxin, boxout)

        self._mtx = None

        self._inverted = None



    __str__ = _make_str_method("_boxin", "_boxout")



    def get_matrix(self):

                             

        if self._invalid:

            inl, inb, inw, inh = self._boxin.bounds

            outl, outb, outw, outh = self._boxout.bounds

            x_scale = outw / inw

            y_scale = outh / inh

            if DEBUG and (x_scale == 0 or y_scale == 0):

                raise ValueError(

                    "Transforming from or to a singular bounding box")

            self._mtx = np.array([[x_scale,     0.0, -inl*x_scale+outl],

                                  [    0.0, y_scale, -inb*y_scale+outb],

                                  [    0.0,     0.0,               1.0]],

                                 float)

            self._inverted = None

            self._invalid = 0

        return self._mtx





class BboxTransformTo(Affine2DBase):

    



    is_separable = True



    def __init__(self, boxout, **kwargs):

        

        _api.check_isinstance(BboxBase, boxout=boxout)



        super().__init__(**kwargs)

        self._boxout = boxout

        self.set_children(boxout)

        self._mtx = None

        self._inverted = None



    __str__ = _make_str_method("_boxout")



    def get_matrix(self):

                             

        if self._invalid:

            outl, outb, outw, outh = self._boxout.bounds

            if DEBUG and (outw == 0 or outh == 0):

                raise ValueError("Transforming to a singular bounding box.")

            self._mtx = np.array([[outw,  0.0, outl],

                                  [ 0.0, outh, outb],

                                  [ 0.0,  0.0,  1.0]],

                                 float)

            self._inverted = None

            self._invalid = 0

        return self._mtx





class BboxTransformFrom(Affine2DBase):

    

    is_separable = True



    def __init__(self, boxin, **kwargs):

        _api.check_isinstance(BboxBase, boxin=boxin)



        super().__init__(**kwargs)

        self._boxin = boxin

        self.set_children(boxin)

        self._mtx = None

        self._inverted = None



    __str__ = _make_str_method("_boxin")



    def get_matrix(self):

                             

        if self._invalid:

            inl, inb, inw, inh = self._boxin.bounds

            if DEBUG and (inw == 0 or inh == 0):

                raise ValueError("Transforming from a singular bounding box.")

            x_scale = 1.0 / inw

            y_scale = 1.0 / inh

            self._mtx = np.array([[x_scale,     0.0, -inl*x_scale],

                                  [    0.0, y_scale, -inb*y_scale],

                                  [    0.0,     0.0,          1.0]],

                                 float)

            self._inverted = None

            self._invalid = 0

        return self._mtx





class ScaledTranslation(Affine2DBase):

    

    def __init__(self, xt, yt, scale_trans, **kwargs):

        super().__init__(**kwargs)

        self._t = (xt, yt)

        self._scale_trans = scale_trans

        self.set_children(scale_trans)

        self._mtx = None

        self._inverted = None



    __str__ = _make_str_method("_t")



    def get_matrix(self):

                             

        if self._invalid:

                                               

            self._mtx = IdentityTransform._mtx.copy()

            self._mtx[:2, 2] = self._scale_trans.transform(self._t)

            self._invalid = 0

            self._inverted = None

        return self._mtx





class _ScaledRotation(Affine2DBase):

    

    def __init__(self, theta, trans_shift):

        super().__init__()

        self._theta = theta

        self._trans_shift = trans_shift

        self._mtx = None



    def get_matrix(self):

        if self._invalid:

            transformed_coords = self._trans_shift.transform([[self._theta, 0]])[0]

            adjusted_theta = transformed_coords[0]

            rotation = Affine2D().rotate(adjusted_theta)

            self._mtx = rotation.get_matrix()

        return self._mtx





class AffineDeltaTransform(Affine2DBase):

    



    pass_through = True



    def __init__(self, transform, **kwargs):

        super().__init__(**kwargs)

        self._base_transform = transform

        self.set_children(transform)



    __str__ = _make_str_method("_base_transform")



    def get_matrix(self):

        if self._invalid:

            self._mtx = self._base_transform.get_matrix().copy()

            self._mtx[:2, -1] = 0

        return self._mtx





class TransformedPath(TransformNode):

    

    def __init__(self, path, transform):

        

        _api.check_isinstance(Transform, transform=transform)

        super().__init__()

        self._path = path

        self._transform = transform

        self.set_children(transform)

        self._transformed_path = None

        self._transformed_points = None



    def _revalidate(self):

                                                                            

                       

        if (self._invalid == self._INVALID_FULL

                or self._transformed_path is None):

            self._transformed_path =
                self._transform.transform_path_non_affine(self._path)

            self._transformed_points =
                Path._fast_from_codes_and_verts(

                    self._transform.transform_non_affine(self._path.vertices),

                    None, self._path)

        self._invalid = 0



    def get_transformed_points_and_affine(self):

        

        self._revalidate()

        return self._transformed_points, self.get_affine()



    def get_transformed_path_and_affine(self):

        

        self._revalidate()

        return self._transformed_path, self.get_affine()



    def get_fully_transformed_path(self):

        

        self._revalidate()

        return self._transform.transform_path_affine(self._transformed_path)



    def get_affine(self):

        return self._transform.get_affine()





class TransformedPatchPath(TransformedPath):

    



    def __init__(self, patch):

        

                                            

        super().__init__(patch.get_path(), patch.get_transform())

        self._patch = patch



    def _revalidate(self):

        patch_path = self._patch.get_path()

                                                                           

                                   

        if patch_path != self._path:

            self._path = patch_path

            self._transformed_path = None

        super()._revalidate()





def nonsingular(vmin, vmax, expander=0.001, tiny=1e-15, increasing=True):

    



    if (not np.isfinite(vmin)) or (not np.isfinite(vmax)):

        return -expander, expander



    swapped = False

    if vmax < vmin:

        vmin, vmax = vmax, vmin

        swapped = True



                                                                           

                                                                              

    vmin, vmax = map(float, [vmin, vmax])



    maxabsvalue = max(abs(vmin), abs(vmax))

    if maxabsvalue < (1e6 / tiny) * np.finfo(float).tiny:

        vmin = -expander

        vmax = expander



    elif vmax - vmin <= maxabsvalue * tiny:

        if vmax == 0 and vmin == 0:

            vmin = -expander

            vmax = expander

        else:

            vmin -= expander*abs(vmin)

            vmax += expander*abs(vmax)



    if swapped and not increasing:

        vmin, vmax = vmax, vmin

    return vmin, vmax





def interval_contains(interval, val):

    

    a, b = interval

    if a > b:

        a, b = b, a

    return a <= val <= b





def _interval_contains_close(interval, val, rtol=1e-10):

    

    a, b = interval

    if a > b:

        a, b = b, a

    rtol = (b - a) * rtol

    return a - rtol <= val <= b + rtol





def interval_contains_open(interval, val):

    

    a, b = interval

    return a < val < b or a > val > b





def offset_copy(trans, fig=None, x=0.0, y=0.0, units='inches'):

    

    _api.check_in_list(['dots', 'points', 'inches'], units=units)

    if units == 'dots':

        return trans + Affine2D().translate(x, y)

    if fig is None:

        raise ValueError('For units of inches or points a fig kwarg is needed')

    if units == 'points':

        x /= 72.0

        y /= 72.0

                                

    return trans + ScaledTranslation(x, y, fig.dpi_scale_trans)

