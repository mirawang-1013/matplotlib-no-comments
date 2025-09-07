



import copy

from functools import lru_cache

from weakref import WeakValueDictionary



import numpy as np



import matplotlib as mpl

from . import _api, _path

from .cbook import _to_unmasked_float_array, simple_linear_interpolation

from .bezier import BezierSegment





class Path:

    

    code_type = np.uint8



                

    STOP = code_type(0)                   

    MOVETO = code_type(1)                 

    LINETO = code_type(2)                 

    CURVE3 = code_type(3)                   

    CURVE4 = code_type(4)                   

    CLOSEPOLY = code_type(79)             



                                                                         

                    

    NUM_VERTICES_FOR_CODE = {STOP: 1,

                             MOVETO: 1,

                             LINETO: 1,

                             CURVE3: 2,

                             CURVE4: 3,

                             CLOSEPOLY: 1}



    def __init__(self, vertices, codes=None, _interpolation_steps=1,

                 closed=False, readonly=False):

        

        vertices = _to_unmasked_float_array(vertices)

        _api.check_shape((None, 2), vertices=vertices)



        if codes is not None and len(vertices):

            codes = np.asarray(codes, self.code_type)

            if codes.ndim != 1 or len(codes) != len(vertices):

                raise ValueError("'codes' must be a 1D list or array with the "

                                 "same length of 'vertices'. "

                                 f"Your vertices have shape {vertices.shape} "

                                 f"but your codes have shape {codes.shape}")

            if len(codes) and codes[0] != self.MOVETO:

                raise ValueError("The first element of 'code' must be equal "

                                 f"to 'MOVETO' ({self.MOVETO}).  "

                                 f"Your first code is {codes[0]}")

        elif closed and len(vertices):

            codes = np.empty(len(vertices), dtype=self.code_type)

            codes[0] = self.MOVETO

            codes[1:-1] = self.LINETO

            codes[-1] = self.CLOSEPOLY



        self._vertices = vertices

        self._codes = codes

        self._interpolation_steps = _interpolation_steps

        self._update_values()



        if readonly:

            self._vertices.flags.writeable = False

            if self._codes is not None:

                self._codes.flags.writeable = False

            self._readonly = True

        else:

            self._readonly = False



    @classmethod

    def _fast_from_codes_and_verts(cls, verts, codes, internals_from=None):

        

        pth = cls.__new__(cls)

        pth._vertices = _to_unmasked_float_array(verts)

        pth._codes = codes

        pth._readonly = False

        if internals_from is not None:

            pth._should_simplify = internals_from._should_simplify

            pth._simplify_threshold = internals_from._simplify_threshold

            pth._interpolation_steps = internals_from._interpolation_steps

        else:

            pth._should_simplify = True

            pth._simplify_threshold = mpl.rcParams['path.simplify_threshold']

            pth._interpolation_steps = 1

        return pth



    @classmethod

    def _create_closed(cls, vertices):

        

        v = _to_unmasked_float_array(vertices)

        return cls(np.concatenate([v, v[:1]]), closed=True)



    def _update_values(self):

        self._simplify_threshold = mpl.rcParams['path.simplify_threshold']

        self._should_simplify = (

            self._simplify_threshold > 0 and

            mpl.rcParams['path.simplify'] and

            len(self._vertices) >= 128 and

            (self._codes is None or np.all(self._codes <= Path.LINETO))

        )



    @property

    def vertices(self):

        

        return self._vertices



    @vertices.setter

    def vertices(self, vertices):

        if self._readonly:

            raise AttributeError("Can't set vertices on a readonly Path")

        self._vertices = vertices

        self._update_values()



    @property

    def codes(self):

        

        return self._codes



    @codes.setter

    def codes(self, codes):

        if self._readonly:

            raise AttributeError("Can't set codes on a readonly Path")

        self._codes = codes

        self._update_values()



    @property

    def simplify_threshold(self):

        

        return self._simplify_threshold



    @simplify_threshold.setter

    def simplify_threshold(self, threshold):

        self._simplify_threshold = threshold



    @property

    def should_simplify(self):

        

        return self._should_simplify



    @should_simplify.setter

    def should_simplify(self, should_simplify):

        self._should_simplify = should_simplify



    @property

    def readonly(self):

        

        return self._readonly



    def copy(self):

        

        return copy.copy(self)



    def __deepcopy__(self, memo):

        

                                                                               

        cls = type(self)

        memo[id(self)] = p = cls.__new__(cls)



        for k, v in self.__dict__.items():

            setattr(p, k, copy.deepcopy(v, memo))



        p._readonly = False

        return p



    def deepcopy(self, memo=None):

        

        return copy.deepcopy(self, memo)



    @classmethod

    def make_compound_path_from_polys(cls, XY):

        

                                                                             

                                                                           

                                                             

        numpolys, numsides, two = XY.shape

        if two != 2:

            raise ValueError("The third dimension of 'XY' must be 2")

        stride = numsides + 1

        nverts = numpolys * stride

        verts = np.zeros((nverts, 2))

        codes = np.full(nverts, cls.LINETO, dtype=cls.code_type)

        codes[0::stride] = cls.MOVETO

        codes[numsides::stride] = cls.CLOSEPOLY

        for i in range(numsides):

            verts[i::stride] = XY[:, i]

        return cls(verts, codes)



    @classmethod

    def make_compound_path(cls, *args):

        

        if not args:

            return Path(np.empty([0, 2], dtype=np.float32))

        vertices = np.concatenate([path.vertices for path in args])

        codes = np.empty(len(vertices), dtype=cls.code_type)

        i = 0

        for path in args:

            size = len(path.vertices)

            if path.codes is None:

                if size:

                    codes[i] = cls.MOVETO

                    codes[i+1:i+size] = cls.LINETO

            else:

                codes[i:i+size] = path.codes

            i += size

        not_stop_mask = codes != cls.STOP                                              

        return cls(vertices[not_stop_mask], codes[not_stop_mask])



    def __repr__(self):

        return f"Path({self.vertices!r}, {self.codes!r})"



    def __len__(self):

        return len(self.vertices)



    def iter_segments(self, transform=None, remove_nans=True, clip=None,

                      snap=False, stroke_width=1.0, simplify=None,

                      curves=True, sketch=None):

        

        if not len(self):

            return



        cleaned = self.cleaned(transform=transform,

                               remove_nans=remove_nans, clip=clip,

                               snap=snap, stroke_width=stroke_width,

                               simplify=simplify, curves=curves,

                               sketch=sketch)



                                                                 

        NUM_VERTICES_FOR_CODE = self.NUM_VERTICES_FOR_CODE

        STOP = self.STOP



        vertices = iter(cleaned.vertices)

        codes = iter(cleaned.codes)

        for curr_vertices, code in zip(vertices, codes):

            if code == STOP:

                break

            extra_vertices = NUM_VERTICES_FOR_CODE[code] - 1

            if extra_vertices:

                for i in range(extra_vertices):

                    next(codes)

                    curr_vertices = np.append(curr_vertices, next(vertices))

            yield curr_vertices, code



    def iter_bezier(self, **kwargs):

        

        first_vert = None

        prev_vert = None

        for verts, code in self.iter_segments(**kwargs):

            if first_vert is None:

                if code != Path.MOVETO:

                    raise ValueError("Malformed path, must start with MOVETO.")

            if code == Path.MOVETO:                            

                first_vert = verts

                yield BezierSegment(np.array([first_vert])), code

            elif code == Path.LINETO:            

                yield BezierSegment(np.array([prev_vert, verts])), code

            elif code == Path.CURVE3:

                yield BezierSegment(np.array([prev_vert, verts[:2],

                                              verts[2:]])), code

            elif code == Path.CURVE4:

                yield BezierSegment(np.array([prev_vert, verts[:2],

                                              verts[2:4], verts[4:]])), code

            elif code == Path.CLOSEPOLY:

                yield BezierSegment(np.array([prev_vert, first_vert])), code

            elif code == Path.STOP:

                return

            else:

                raise ValueError(f"Invalid Path.code_type: {code}")

            prev_vert = verts[-2:]



    def _iter_connected_components(self):

        

        if self.codes is None:

            yield self

        else:

            idxs = np.append((self.codes == Path.MOVETO).nonzero()[0], len(self.codes))

            for sl in map(slice, idxs, idxs[1:]):

                yield Path._fast_from_codes_and_verts(

                    self.vertices[sl], self.codes[sl], self)



    def cleaned(self, transform=None, remove_nans=False, clip=None,

                *, simplify=False, curves=False,

                stroke_width=1.0, snap=False, sketch=None):

        

        vertices, codes = _path.cleanup_path(

            self, transform, remove_nans, clip, snap, stroke_width, simplify,

            curves, sketch)

        pth = Path._fast_from_codes_and_verts(vertices, codes, self)

        if not simplify:

            pth._should_simplify = False

        return pth



    def transformed(self, transform):

        

        return Path(transform.transform(self.vertices), self.codes,

                    self._interpolation_steps)



    def contains_point(self, point, transform=None, radius=0.0):

        

        if transform is not None:

            transform = transform.frozen()

                                                                     

                                                                          

                                                                         

                 

        if transform and not transform.is_affine:

            self = transform.transform_path(self)

            transform = None

        return _path.point_in_path(point[0], point[1], radius, self, transform)



    def contains_points(self, points, transform=None, radius=0.0):

        

        if transform is not None:

            transform = transform.frozen()

        result = _path.points_in_path(points, radius, self, transform)

        return result.astype('bool')



    def contains_path(self, path, transform=None):

        

        if transform is not None:

            transform = transform.frozen()

        return _path.path_in_path(self, None, path, transform)



    def get_extents(self, transform=None, **kwargs):

        

        from .transforms import Bbox

        if transform is not None:

            self = transform.transform_path(self)

        if self.codes is None:

            xys = self.vertices

        elif len(np.intersect1d(self.codes, [Path.CURVE3, Path.CURVE4])) == 0:

                                                      

                                                               

                                            

                                                                   

            xys = self.vertices[np.isin(self.codes,

                                        [Path.MOVETO, Path.LINETO])]

        else:

            xys = []

            for curve, code in self.iter_bezier(**kwargs):

                                                                    

                _, dzeros = curve.axis_aligned_extrema()

                                              

                xys.append(curve([0, *dzeros, 1]))

            xys = np.concatenate(xys)

        if len(xys):

            return Bbox([xys.min(axis=0), xys.max(axis=0)])

        else:

            return Bbox.null()



    def intersects_path(self, other, filled=True):

        

        return _path.path_intersects_path(self, other, filled)



    def intersects_bbox(self, bbox, filled=True):

        

        return _path.path_intersects_rectangle(

            self, bbox.x0, bbox.y0, bbox.x1, bbox.y1, filled)



    def interpolated(self, steps):

        

        if steps == 1 or len(self) == 0:

            return self



        if self.codes is not None and self.MOVETO in self.codes[1:]:

            return self.make_compound_path(

                *(p.interpolated(steps) for p in self._iter_connected_components()))



        if self.codes is not None and self.CLOSEPOLY in self.codes and not np.all(

                self.vertices[self.codes == self.CLOSEPOLY] == self.vertices[0]):

            vertices = self.vertices.copy()

            vertices[self.codes == self.CLOSEPOLY] = vertices[0]

        else:

            vertices = self.vertices



        vertices = simple_linear_interpolation(vertices, steps)

        codes = self.codes

        if codes is not None:

            new_codes = np.full((len(codes) - 1) * steps + 1, Path.LINETO,

                                dtype=self.code_type)

            new_codes[0::steps] = codes

        else:

            new_codes = None

        return Path(vertices, new_codes)



    def to_polygons(self, transform=None, width=0, height=0, closed_only=True):

        

        if len(self.vertices) == 0:

            return []



        if transform is not None:

            transform = transform.frozen()



        if self.codes is None and (width == 0 or height == 0):

            vertices = self.vertices

            if closed_only:

                if len(vertices) < 3:

                    return []

                elif np.any(vertices[0] != vertices[-1]):

                    vertices = [*vertices, vertices[0]]



            if transform is None:

                return [vertices]

            else:

                return [transform.transform(vertices)]



                                                                   

                                         

        return _path.convert_path_to_polygons(

            self, transform, width, height, closed_only)



    _unit_rectangle = None



    @classmethod

    def unit_rectangle(cls):

        

        if cls._unit_rectangle is None:

            cls._unit_rectangle = cls([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]],

                                      closed=True, readonly=True)

        return cls._unit_rectangle



    _unit_regular_polygons = WeakValueDictionary()



    @classmethod

    def unit_regular_polygon(cls, numVertices):

        

        if numVertices <= 16:

            path = cls._unit_regular_polygons.get(numVertices)

        else:

            path = None

        if path is None:

            theta = ((2 * np.pi / numVertices) * np.arange(numVertices + 1)

                                                                               

                                   

                     + np.pi / 2)

            verts = np.column_stack((np.cos(theta), np.sin(theta)))

            path = cls(verts, closed=True, readonly=True)

            if numVertices <= 16:

                cls._unit_regular_polygons[numVertices] = path

        return path



    _unit_regular_stars = WeakValueDictionary()



    @classmethod

    def unit_regular_star(cls, numVertices, innerCircle=0.5):

        

        if numVertices <= 16:

            path = cls._unit_regular_stars.get((numVertices, innerCircle))

        else:

            path = None

        if path is None:

            ns2 = numVertices * 2

            theta = (2*np.pi/ns2 * np.arange(ns2 + 1))

                                                                      

                         

            theta += np.pi / 2.0

            r = np.ones(ns2 + 1)

            r[1::2] = innerCircle

            verts = (r * np.vstack((np.cos(theta), np.sin(theta)))).T

            path = cls(verts, closed=True, readonly=True)

            if numVertices <= 16:

                cls._unit_regular_stars[(numVertices, innerCircle)] = path

        return path



    @classmethod

    def unit_regular_asterisk(cls, numVertices):

        

        return cls.unit_regular_star(numVertices, 0.0)



    _unit_circle = None



    @classmethod

    def unit_circle(cls):

        

        if cls._unit_circle is None:

            cls._unit_circle = cls.circle(center=(0, 0), radius=1,

                                          readonly=True)

        return cls._unit_circle



    @classmethod

    def circle(cls, center=(0., 0.), radius=1., readonly=False):

        

        MAGIC = 0.2652031

        SQRTHALF = np.sqrt(0.5)

        MAGIC45 = SQRTHALF * MAGIC



        vertices = np.array([[0.0, -1.0],



                             [MAGIC, -1.0],

                             [SQRTHALF-MAGIC45, -SQRTHALF-MAGIC45],

                             [SQRTHALF, -SQRTHALF],



                             [SQRTHALF+MAGIC45, -SQRTHALF+MAGIC45],

                             [1.0, -MAGIC],

                             [1.0, 0.0],



                             [1.0, MAGIC],

                             [SQRTHALF+MAGIC45, SQRTHALF-MAGIC45],

                             [SQRTHALF, SQRTHALF],



                             [SQRTHALF-MAGIC45, SQRTHALF+MAGIC45],

                             [MAGIC, 1.0],

                             [0.0, 1.0],



                             [-MAGIC, 1.0],

                             [-SQRTHALF+MAGIC45, SQRTHALF+MAGIC45],

                             [-SQRTHALF, SQRTHALF],



                             [-SQRTHALF-MAGIC45, SQRTHALF-MAGIC45],

                             [-1.0, MAGIC],

                             [-1.0, 0.0],



                             [-1.0, -MAGIC],

                             [-SQRTHALF-MAGIC45, -SQRTHALF+MAGIC45],

                             [-SQRTHALF, -SQRTHALF],



                             [-SQRTHALF+MAGIC45, -SQRTHALF-MAGIC45],

                             [-MAGIC, -1.0],

                             [0.0, -1.0],



                             [0.0, -1.0]],

                            dtype=float)



        codes = [cls.CURVE4] * 26

        codes[0] = cls.MOVETO

        codes[-1] = cls.CLOSEPOLY

        return Path(vertices * radius + center, codes, readonly=readonly)



    _unit_circle_righthalf = None



    @classmethod

    def unit_circle_righthalf(cls):

        

        if cls._unit_circle_righthalf is None:

            MAGIC = 0.2652031

            SQRTHALF = np.sqrt(0.5)

            MAGIC45 = SQRTHALF * MAGIC



            vertices = np.array(

                [[0.0, -1.0],



                 [MAGIC, -1.0],

                 [SQRTHALF-MAGIC45, -SQRTHALF-MAGIC45],

                 [SQRTHALF, -SQRTHALF],



                 [SQRTHALF+MAGIC45, -SQRTHALF+MAGIC45],

                 [1.0, -MAGIC],

                 [1.0, 0.0],



                 [1.0, MAGIC],

                 [SQRTHALF+MAGIC45, SQRTHALF-MAGIC45],

                 [SQRTHALF, SQRTHALF],



                 [SQRTHALF-MAGIC45, SQRTHALF+MAGIC45],

                 [MAGIC, 1.0],

                 [0.0, 1.0],



                 [0.0, -1.0]],



                float)



            codes = np.full(14, cls.CURVE4, dtype=cls.code_type)

            codes[0] = cls.MOVETO

            codes[-1] = cls.CLOSEPOLY



            cls._unit_circle_righthalf = cls(vertices, codes, readonly=True)

        return cls._unit_circle_righthalf



    @classmethod

    def arc(cls, theta1, theta2, n=None, is_wedge=False):

        

        halfpi = np.pi * 0.5



        eta1 = theta1

        eta2 = theta2 - 360 * np.floor((theta2 - theta1) / 360)

                                                                              

                                                   

        if theta2 != theta1 and eta2 <= eta1:

            eta2 += 360

        eta1, eta2 = np.deg2rad([eta1, eta2])



                                          

        if n is None:

            n = int(2 ** np.ceil((eta2 - eta1) / halfpi))

        if n < 1:

            raise ValueError("n must be >= 1 or None")



        deta = (eta2 - eta1) / n

        t = np.tan(0.5 * deta)

        alpha = np.sin(deta) * (np.sqrt(4.0 + 3.0 * t * t) - 1) / 3.0



        steps = np.linspace(eta1, eta2, n + 1, True)

        cos_eta = np.cos(steps)

        sin_eta = np.sin(steps)



        xA = cos_eta[:-1]

        yA = sin_eta[:-1]

        xA_dot = -yA

        yA_dot = xA



        xB = cos_eta[1:]

        yB = sin_eta[1:]

        xB_dot = -yB

        yB_dot = xB



        if is_wedge:

            length = n * 3 + 4

            vertices = np.zeros((length, 2), float)

            codes = np.full(length, cls.CURVE4, dtype=cls.code_type)

            vertices[1] = [xA[0], yA[0]]

            codes[0:2] = [cls.MOVETO, cls.LINETO]

            codes[-2:] = [cls.LINETO, cls.CLOSEPOLY]

            vertex_offset = 2

            end = length - 2

        else:

            length = n * 3 + 1

            vertices = np.empty((length, 2), float)

            codes = np.full(length, cls.CURVE4, dtype=cls.code_type)

            vertices[0] = [xA[0], yA[0]]

            codes[0] = cls.MOVETO

            vertex_offset = 1

            end = length



        vertices[vertex_offset:end:3, 0] = xA + alpha * xA_dot

        vertices[vertex_offset:end:3, 1] = yA + alpha * yA_dot

        vertices[vertex_offset+1:end:3, 0] = xB - alpha * xB_dot

        vertices[vertex_offset+1:end:3, 1] = yB - alpha * yB_dot

        vertices[vertex_offset+2:end:3, 0] = xB

        vertices[vertex_offset+2:end:3, 1] = yB



        return cls(vertices, codes, readonly=True)



    @classmethod

    def wedge(cls, theta1, theta2, n=None):

        

        return cls.arc(theta1, theta2, n, True)



    @staticmethod

    @lru_cache(8)

    def hatch(hatchpattern, density=6):

        

        from matplotlib.hatch import get_path

        return (get_path(hatchpattern, density)

                if hatchpattern is not None else None)



    def clip_to_bbox(self, bbox, inside=True):

        

        verts = _path.clip_path_to_rect(self, bbox, inside)

        paths = [Path(poly) for poly in verts]

        return self.make_compound_path(*paths)





def get_path_collection_extents(

        master_transform, paths, transforms, offsets, offset_transform):

    

    from .transforms import Bbox

    if len(paths) == 0:

        raise ValueError("No paths provided")

    if len(offsets) == 0:

        raise ValueError("No offsets provided")

    extents, minpos = _path.get_path_collection_extents(

        master_transform, paths, np.atleast_3d(transforms),

        offsets, offset_transform)

    return Bbox.from_extents(*extents, minpos=minpos)

