                                                   

                                                       

                                                        



"""
Module containing 3D artist code and functions to convert 2D
artists into 3D versions which can be added to an Axes3D.
"""



import math



import numpy as np



from contextlib import contextmanager



from matplotlib import (

    _api, artist, cbook, colors as mcolors, lines, text as mtext,

    path as mpath, rcParams)

from matplotlib.collections import (

    Collection, LineCollection, PolyCollection, PatchCollection, PathCollection)

from matplotlib.patches import Patch

from . import proj3d





def _norm_angle(a):

    

    a = (a + 360) % 360

    if a > 180:

        a = a - 360

    return a





def _norm_text_angle(a):

    

    a = (a + 180) % 180

    if a > 90:

        a = a - 180

    return a





def get_dir_vector(zdir):

    

    if zdir == 'x':

        return np.array((1, 0, 0))

    elif zdir == 'y':

        return np.array((0, 1, 0))

    elif zdir == 'z':

        return np.array((0, 0, 1))

    elif zdir is None:

        return np.array((0, 0, 0))

    elif np.iterable(zdir) and len(zdir) == 3:

        return np.array(zdir)

    else:

        raise ValueError("'x', 'y', 'z', None or vector of length 3 expected")





def _viewlim_mask(xs, ys, zs, axes):

    

    mask = np.logical_or.reduce((xs < axes.xy_viewLim.xmin,

                                 xs > axes.xy_viewLim.xmax,

                                 ys < axes.xy_viewLim.ymin,

                                 ys > axes.xy_viewLim.ymax,

                                 zs < axes.zz_viewLim.xmin,

                                 zs > axes.zz_viewLim.xmax))

    return mask





class Text3D(mtext.Text):

    



    def __init__(self, x=0, y=0, z=0, text='', zdir='z', axlim_clip=False,

                 **kwargs):

        mtext.Text.__init__(self, x, y, text, **kwargs)

        self.set_3d_properties(z, zdir, axlim_clip)



    def get_position_3d(self):

        

        return self._x, self._y, self._z



    def set_position_3d(self, xyz, zdir=None):

        

        super().set_position(xyz[:2])

        self.set_z(xyz[2])

        if zdir is not None:

            self._dir_vec = get_dir_vector(zdir)



    def set_z(self, z):

        

        self._z = z

        self.stale = True



    def set_3d_properties(self, z=0, zdir='z', axlim_clip=False):

        

        self._z = z

        self._dir_vec = get_dir_vector(zdir)

        self._axlim_clip = axlim_clip

        self.stale = True



    @artist.allow_rasterization

    def draw(self, renderer):

        if self._axlim_clip:

            mask = _viewlim_mask(self._x, self._y, self._z, self.axes)

            pos3d = np.ma.array([self._x, self._y, self._z],

                                mask=mask, dtype=float).filled(np.nan)

        else:

            pos3d = np.array([self._x, self._y, self._z], dtype=float)



        proj = proj3d._proj_trans_points([pos3d, pos3d + self._dir_vec], self.axes.M)

        dx = proj[0][1] - proj[0][0]

        dy = proj[1][1] - proj[1][0]

        angle = math.degrees(math.atan2(dy, dx))

        with cbook._setattr_cm(self, _x=proj[0][0], _y=proj[1][0],

                               _rotation=_norm_text_angle(angle)):

            mtext.Text.draw(self, renderer)

        self.stale = False



    def get_tightbbox(self, renderer=None):

                                                                     

                                                                       

        return None





def text_2d_to_3d(obj, z=0, zdir='z', axlim_clip=False):

    

    obj.__class__ = Text3D

    obj.set_3d_properties(z, zdir, axlim_clip)





class Line3D(lines.Line2D):

    



    def __init__(self, xs, ys, zs, *args, axlim_clip=False, **kwargs):

        

        super().__init__([], [], *args, **kwargs)

        self.set_data_3d(xs, ys, zs)

        self._axlim_clip = axlim_clip



    def set_3d_properties(self, zs=0, zdir='z', axlim_clip=False):

        

        xs = self.get_xdata()

        ys = self.get_ydata()

        zs = cbook._to_unmasked_float_array(zs).ravel()

        zs = np.broadcast_to(zs, len(xs))

        self._verts3d = juggle_axes(xs, ys, zs, zdir)

        self._axlim_clip = axlim_clip

        self.stale = True



    def set_data_3d(self, *args):

        

        if len(args) == 1:

            args = args[0]

        for name, xyz in zip('xyz', args):

            if not np.iterable(xyz):

                raise RuntimeError(f'{name} must be a sequence')

        self._verts3d = args

        self.stale = True



    def get_data_3d(self):

        

        return self._verts3d



    @artist.allow_rasterization

    def draw(self, renderer):

        if self._axlim_clip:

            mask = np.broadcast_to(

                _viewlim_mask(*self._verts3d, self.axes),

                (len(self._verts3d), *self._verts3d[0].shape)

            )

            xs3d, ys3d, zs3d = np.ma.array(self._verts3d,

                                           dtype=float, mask=mask).filled(np.nan)

        else:

            xs3d, ys3d, zs3d = self._verts3d

        xs, ys, zs, tis = proj3d._proj_transform_clip(xs3d, ys3d, zs3d,

                                                      self.axes.M,

                                                      self.axes._focal_length)

        self.set_data(xs, ys)

        super().draw(renderer)

        self.stale = False





def line_2d_to_3d(line, zs=0, zdir='z', axlim_clip=False):

    



    line.__class__ = Line3D

    line.set_3d_properties(zs, zdir, axlim_clip)





def _path_to_3d_segment(path, zs=0, zdir='z'):

    



    zs = np.broadcast_to(zs, len(path))

    pathsegs = path.iter_segments(simplify=False, curves=False)

    seg = [(x, y, z) for (((x, y), code), z) in zip(pathsegs, zs)]

    seg3d = [juggle_axes(x, y, z, zdir) for (x, y, z) in seg]

    return seg3d





def _paths_to_3d_segments(paths, zs=0, zdir='z'):

    



    if not np.iterable(zs):

        zs = np.broadcast_to(zs, len(paths))

    else:

        if len(zs) != len(paths):

            raise ValueError('Number of z-coordinates does not match paths.')



    segs = [_path_to_3d_segment(path, pathz, zdir)

            for path, pathz in zip(paths, zs)]

    return segs





def _path_to_3d_segment_with_codes(path, zs=0, zdir='z'):

    



    zs = np.broadcast_to(zs, len(path))

    pathsegs = path.iter_segments(simplify=False, curves=False)

    seg_codes = [((x, y, z), code) for ((x, y), code), z in zip(pathsegs, zs)]

    if seg_codes:

        seg, codes = zip(*seg_codes)

        seg3d = [juggle_axes(x, y, z, zdir) for (x, y, z) in seg]

    else:

        seg3d = []

        codes = []

    return seg3d, list(codes)





def _paths_to_3d_segments_with_codes(paths, zs=0, zdir='z'):

    



    zs = np.broadcast_to(zs, len(paths))

    segments_codes = [_path_to_3d_segment_with_codes(path, pathz, zdir)

                      for path, pathz in zip(paths, zs)]

    if segments_codes:

        segments, codes = zip(*segments_codes)

    else:

        segments, codes = [], []

    return list(segments), list(codes)





class Collection3D(Collection):

    



    def do_3d_projection(self):

        

        vs_list = [vs for vs, _ in self._3dverts_codes]

        if self._axlim_clip:

            vs_list = [np.ma.array(vs, mask=np.broadcast_to(

                       _viewlim_mask(*vs.T, self.axes), vs.shape))

                       for vs in vs_list]

        xyzs_list = [proj3d.proj_transform(*vs.T, self.axes.M) for vs in vs_list]

        self._paths = [mpath.Path(np.ma.column_stack([xs, ys]), cs)

                       for (xs, ys, _), (_, cs) in zip(xyzs_list, self._3dverts_codes)]

        zs = np.concatenate([zs for _, _, zs in xyzs_list])

        return zs.min() if len(zs) else 1e9





def collection_2d_to_3d(col, zs=0, zdir='z', axlim_clip=False):

    

    zs = np.broadcast_to(zs, len(col.get_paths()))

    col._3dverts_codes = [

        (np.column_stack(juggle_axes(

            *np.column_stack([p.vertices, np.broadcast_to(z, len(p.vertices))]).T,

            zdir)),

         p.codes)

        for p, z in zip(col.get_paths(), zs)]

    col.__class__ = cbook._make_class_factory(Collection3D, "{}3D")(type(col))

    col._axlim_clip = axlim_clip





class Line3DCollection(LineCollection):

    

    def __init__(self, lines, axlim_clip=False, **kwargs):

        super().__init__(lines, **kwargs)

        self._axlim_clip = axlim_clip

        """
        Parameters
        ----------
        lines : list of (N, 3) array-like
            A sequence ``[line0, line1, ...]`` where each line is a (N, 3)-shape
            array-like containing points:: line0 = [(x0, y0, z0), (x1, y1, z1), ...]
            Each line can contain a different number of points.
        linewidths : float or list of float, default: :rc:`lines.linewidth`
            The width of each line in points.
        colors : :mpltype:`color` or list of color, default: :rc:`lines.color`
            A sequence of RGBA tuples (e.g., arbitrary color strings, etc, not
            allowed).
        antialiaseds : bool or list of bool, default: :rc:`lines.antialiased`
            Whether to use antialiasing for each line.
        facecolors : :mpltype:`color` or list of :mpltype:`color`, default: 'none'
            When setting *facecolors*, each line is interpreted as a boundary
            for an area, implicitly closing the path from the last point to the
            first point. The enclosed area is filled with *facecolor*.
            In order to manually specify what should count as the "interior" of
            each line, please use `.PathCollection` instead, where the
            "interior" can be specified by appropriate usage of
            `~.path.Path.CLOSEPOLY`.
        **kwargs : Forwarded to `.Collection`.
        """



    def set_sort_zpos(self, val):

        

        self._sort_zpos = val

        self.stale = True



    def set_segments(self, segments):

        

        self._segments3d = segments

        super().set_segments([])



    def do_3d_projection(self):

        

        segments = np.asanyarray(self._segments3d)



        mask = False

        if np.ma.isMA(segments):

            mask = segments.mask



        if self._axlim_clip:

            viewlim_mask = _viewlim_mask(segments[..., 0],

                                         segments[..., 1],

                                         segments[..., 2],

                                         self.axes)

            if np.any(viewlim_mask):

                                      

                viewlim_mask = np.broadcast_to(viewlim_mask[..., np.newaxis],

                                               (*viewlim_mask.shape, 3))

                mask = mask | viewlim_mask

        xyzs = np.ma.array(proj3d._proj_transform_vectors(segments, self.axes.M),

                           mask=mask)

        segments_2d = xyzs[..., 0:2]

        LineCollection.set_segments(self, segments_2d)



               

        if len(xyzs) > 0:

            minz = min(xyzs[..., 2].min(), 1e9)

        else:

            minz = np.nan

        return minz





def line_collection_2d_to_3d(col, zs=0, zdir='z', axlim_clip=False):

    

    segments3d = _paths_to_3d_segments(col.get_paths(), zs, zdir)

    col.__class__ = Line3DCollection

    col.set_segments(segments3d)

    col._axlim_clip = axlim_clip





class Patch3D(Patch):

    



    def __init__(self, *args, zs=(), zdir='z', axlim_clip=False, **kwargs):

        

        super().__init__(*args, **kwargs)

        self.set_3d_properties(zs, zdir, axlim_clip)



    def set_3d_properties(self, verts, zs=0, zdir='z', axlim_clip=False):

        

        zs = np.broadcast_to(zs, len(verts))

        self._segment3d = [juggle_axes(x, y, z, zdir)

                           for ((x, y), z) in zip(verts, zs)]

        self._axlim_clip = axlim_clip



    def get_path(self):

                             

                                                                

        if not hasattr(self, '_path2d'):

            self.axes.M = self.axes.get_proj()

            self.do_3d_projection()

        return self._path2d



    def do_3d_projection(self):

        s = self._segment3d

        if self._axlim_clip:

            mask = _viewlim_mask(*zip(*s), self.axes)

            xs, ys, zs = np.ma.array(zip(*s),

                                     dtype=float, mask=mask).filled(np.nan)

        else:

            xs, ys, zs = zip(*s)

        vxs, vys, vzs, vis = proj3d._proj_transform_clip(xs, ys, zs,

                                                         self.axes.M,

                                                         self.axes._focal_length)

        self._path2d = mpath.Path(np.ma.column_stack([vxs, vys]))

        return min(vzs)





class PathPatch3D(Patch3D):

    



    def __init__(self, path, *, zs=(), zdir='z', axlim_clip=False, **kwargs):

        

                               

        Patch.__init__(self, **kwargs)

        self.set_3d_properties(path, zs, zdir, axlim_clip)



    def set_3d_properties(self, path, zs=0, zdir='z', axlim_clip=False):

        

        Patch3D.set_3d_properties(self, path.vertices, zs=zs, zdir=zdir,

                                  axlim_clip=axlim_clip)

        self._code3d = path.codes



    def do_3d_projection(self):

        s = self._segment3d

        if self._axlim_clip:

            mask = _viewlim_mask(*zip(*s), self.axes)

            xs, ys, zs = np.ma.array(zip(*s),

                                     dtype=float, mask=mask).filled(np.nan)

        else:

            xs, ys, zs = zip(*s)

        vxs, vys, vzs, vis = proj3d._proj_transform_clip(xs, ys, zs,

                                                         self.axes.M,

                                                         self.axes._focal_length)

        self._path2d = mpath.Path(np.ma.column_stack([vxs, vys]), self._code3d)

        return min(vzs)





def _get_patch_verts(patch):

    

    trans = patch.get_patch_transform()

    path = patch.get_path()

    polygons = path.to_polygons(trans)

    return polygons[0] if len(polygons) else np.array([])





def patch_2d_to_3d(patch, z=0, zdir='z', axlim_clip=False):

    

    verts = _get_patch_verts(patch)

    patch.__class__ = Patch3D

    patch.set_3d_properties(verts, z, zdir, axlim_clip)





def pathpatch_2d_to_3d(pathpatch, z=0, zdir='z'):

    

    path = pathpatch.get_path()

    trans = pathpatch.get_patch_transform()



    mpath = trans.transform_path(path)

    pathpatch.__class__ = PathPatch3D

    pathpatch.set_3d_properties(mpath, z, zdir)





class Patch3DCollection(PatchCollection):

    



    def __init__(

        self,

        *args,

        zs=0,

        zdir="z",

        depthshade=None,

        depthshade_minalpha=None,

        axlim_clip=False,

        **kwargs

    ):

        

        if depthshade is None:

            depthshade = rcParams['axes3d.depthshade']

        if depthshade_minalpha is None:

            depthshade_minalpha = rcParams['axes3d.depthshade_minalpha']

        self._depthshade = depthshade

        self._depthshade_minalpha = depthshade_minalpha

        super().__init__(*args, **kwargs)

        self.set_3d_properties(zs, zdir, axlim_clip)



    def get_depthshade(self):

        return self._depthshade



    def set_depthshade(

        self,

        depthshade,

        depthshade_minalpha=None,

    ):

        

        if depthshade_minalpha is None:

            depthshade_minalpha = rcParams['axes3d.depthshade_minalpha']

        self._depthshade = depthshade

        self._depthshade_minalpha = depthshade_minalpha

        self.stale = True



    def set_sort_zpos(self, val):

        

        self._sort_zpos = val

        self.stale = True



    def set_3d_properties(self, zs, zdir, axlim_clip=False):

        

                                                                    

                                                              

        self.update_scalarmappable()

        offsets = self.get_offsets()

        if len(offsets) > 0:

            xs, ys = offsets.T

        else:

            xs = []

            ys = []

        self._offsets3d = juggle_axes(xs, ys, np.atleast_1d(zs), zdir)

        self._z_markers_idx = slice(-1)

        self._vzs = None

        self._axlim_clip = axlim_clip

        self.stale = True



    def do_3d_projection(self):

        if self._axlim_clip:

            mask = _viewlim_mask(*self._offsets3d, self.axes)

            xs, ys, zs = np.ma.array(self._offsets3d, mask=mask)

        else:

            xs, ys, zs = self._offsets3d

        vxs, vys, vzs, vis = proj3d._proj_transform_clip(xs, ys, zs,

                                                         self.axes.M,

                                                         self.axes._focal_length)

        self._vzs = vzs

        if np.ma.isMA(vxs):

            super().set_offsets(np.ma.column_stack([vxs, vys]))

        else:

            super().set_offsets(np.column_stack([vxs, vys]))



        if vzs.size > 0:

            return min(vzs)

        else:

            return np.nan



    def _maybe_depth_shade_and_sort_colors(self, color_array):

        color_array = (

            _zalpha(

                color_array,

                self._vzs,

                min_alpha=self._depthshade_minalpha,

            )

            if self._vzs is not None and self._depthshade

            else color_array

        )

        if len(color_array) > 1:

            color_array = color_array[self._z_markers_idx]

        return mcolors.to_rgba_array(color_array, self._alpha)



    def get_facecolor(self):

        return self._maybe_depth_shade_and_sort_colors(super().get_facecolor())



    def get_edgecolor(self):

                                                                               

                                                                           

                                                             

        if cbook._str_equal(self._edgecolors, 'face'):

            return self.get_facecolor()

        return self._maybe_depth_shade_and_sort_colors(super().get_edgecolor())





def _get_data_scale(X, Y, Z):

    

                                                                            

                  

    if not np.ma.count(X):

        return 0



                                                                      

                                                                         

                                         

    ptp_x = X.max() - X.min()

    ptp_y = Y.max() - Y.min()

    ptp_z = Z.max() - Z.min()

    return np.sqrt(ptp_x ** 2 + ptp_y ** 2 + ptp_z ** 2)





class Path3DCollection(PathCollection):

    



    def __init__(

        self,

        *args,

        zs=0,

        zdir="z",

        depthshade=None,

        depthshade_minalpha=None,

        axlim_clip=False,

        **kwargs

    ):

        

        if depthshade is None:

            depthshade = rcParams['axes3d.depthshade']

        if depthshade_minalpha is None:

            depthshade_minalpha = rcParams['axes3d.depthshade_minalpha']

        self._depthshade = depthshade

        self._depthshade_minalpha = depthshade_minalpha

        self._in_draw = False

        super().__init__(*args, **kwargs)

        self.set_3d_properties(zs, zdir, axlim_clip)

        self._offset_zordered = None



    def draw(self, renderer):

        with self._use_zordered_offset():

            with cbook._setattr_cm(self, _in_draw=True):

                super().draw(renderer)



    def set_sort_zpos(self, val):

        

        self._sort_zpos = val

        self.stale = True



    def set_3d_properties(self, zs, zdir, axlim_clip=False):

        

                                                                    

                                                              

        self.update_scalarmappable()

        offsets = self.get_offsets()

        if len(offsets) > 0:

            xs, ys = offsets.T

        else:

            xs = []

            ys = []

        self._zdir = zdir

        self._offsets3d = juggle_axes(xs, ys, np.atleast_1d(zs), zdir)

                                                                          

                                                                          

                                             

         

                                                                              

                                                                      

                                                                              

                                                   

         

                                                                 

        self._sizes3d = self._sizes

        self._linewidths3d = np.array(self._linewidths)

        xs, ys, zs = self._offsets3d



                                                

                                                                           

                                                                  

        self._z_markers_idx = slice(-1)

        self._vzs = None



        self._axlim_clip = axlim_clip

        self.stale = True



    def set_sizes(self, sizes, dpi=72.0):

        super().set_sizes(sizes, dpi)

        if not self._in_draw:

            self._sizes3d = sizes



    def set_linewidth(self, lw):

        super().set_linewidth(lw)

        if not self._in_draw:

            self._linewidths3d = np.array(self._linewidths)



    def get_depthshade(self):

        return self._depthshade



    def set_depthshade(

        self,

        depthshade,

        depthshade_minalpha=None,

    ):

        

        if depthshade_minalpha is None:

            depthshade_minalpha = rcParams['axes3d.depthshade_minalpha']

        self._depthshade = depthshade

        self._depthshade_minalpha = depthshade_minalpha

        self.stale = True



    def do_3d_projection(self):

        mask = False

        for xyz in self._offsets3d:

            if np.ma.isMA(xyz):

                mask = mask | xyz.mask

        if self._axlim_clip:

            mask = mask | _viewlim_mask(*self._offsets3d, self.axes)

            mask = np.broadcast_to(mask,

                                   (len(self._offsets3d), *self._offsets3d[0].shape))

            xyzs = np.ma.array(self._offsets3d, mask=mask)

        else:

            xyzs = self._offsets3d

        vxs, vys, vzs, vis = proj3d._proj_transform_clip(*xyzs,

                                                         self.axes.M,

                                                         self.axes._focal_length)

        self._data_scale = _get_data_scale(vxs, vys, vzs)

                                                

                                                                           

                                                                  

        z_markers_idx = self._z_markers_idx = np.ma.argsort(vzs)[::-1]

        self._vzs = vzs



                                                                             

                                 

                                                           

                                                                         



        if len(self._sizes3d) > 1:

            self._sizes = self._sizes3d[z_markers_idx]



        if len(self._linewidths3d) > 1:

            self._linewidths = self._linewidths3d[z_markers_idx]



        PathCollection.set_offsets(self, np.ma.column_stack((vxs, vys)))



                        

        vzs = vzs[z_markers_idx]

        vxs = vxs[z_markers_idx]

        vys = vys[z_markers_idx]



                                                  

        self._offset_zordered = np.ma.column_stack((vxs, vys))



        return np.min(vzs) if vzs.size else np.nan



    @contextmanager

    def _use_zordered_offset(self):

        if self._offset_zordered is None:

                        

            yield

        else:

                                               

            old_offset = self._offsets

            super().set_offsets(self._offset_zordered)

            try:

                yield

            finally:

                self._offsets = old_offset



    def _maybe_depth_shade_and_sort_colors(self, color_array):

                                                                         

                                     

        if self._vzs is not None and self._depthshade:

            color_array = _zalpha(

                color_array,

                self._vzs,

                min_alpha=self._depthshade_minalpha,

                _data_scale=self._data_scale,

            )



                                                                       

                                          

        if len(color_array) > 1:

            color_array = color_array[self._z_markers_idx]



        return mcolors.to_rgba_array(color_array)



    def get_facecolor(self):

        return self._maybe_depth_shade_and_sort_colors(super().get_facecolor())



    def get_edgecolor(self):

                                                                               

                                                                           

                                                             

        if cbook._str_equal(self._edgecolors, 'face'):

            return self.get_facecolor()

        return self._maybe_depth_shade_and_sort_colors(super().get_edgecolor())





def patch_collection_2d_to_3d(

    col,

    zs=0,

    zdir="z",

    depthshade=None,

    axlim_clip=False,

    *args,

    depthshade_minalpha=None,

):

    

    if isinstance(col, PathCollection):

        col.__class__ = Path3DCollection

        col._offset_zordered = None

    elif isinstance(col, PatchCollection):

        col.__class__ = Patch3DCollection

    if depthshade is None:

        depthshade = rcParams['axes3d.depthshade']

    if depthshade_minalpha is None:

        depthshade_minalpha = rcParams['axes3d.depthshade_minalpha']

    col._depthshade = depthshade

    col._depthshade_minalpha = depthshade_minalpha

    col._in_draw = False

    col.set_3d_properties(zs, zdir, axlim_clip)





class Poly3DCollection(PolyCollection):

    



    def __init__(self, verts, *args, zsort='average', shade=False,

                 lightsource=None, axlim_clip=False, **kwargs):

        

        if shade:

            normals = _generate_normals(verts)

            facecolors = kwargs.get('facecolors', None)

            if facecolors is not None:

                kwargs['facecolors'] = _shade_colors(

                    facecolors, normals, lightsource

                )



            edgecolors = kwargs.get('edgecolors', None)

            if edgecolors is not None:

                kwargs['edgecolors'] = _shade_colors(

                    edgecolors, normals, lightsource

                )

            if facecolors is None and edgecolors is None:

                raise ValueError(

                    "You must provide facecolors, edgecolors, or both for "

                    "shade to work.")

        super().__init__(verts, *args, **kwargs)

        if isinstance(verts, np.ndarray):

            if verts.ndim != 3:

                raise ValueError('verts must be a list of (N, 3) array-like')

        else:

            if any(len(np.shape(vert)) != 2 for vert in verts):

                raise ValueError('verts must be a list of (N, 3) array-like')

        self.set_zsort(zsort)

        self._codes3d = None

        self._axlim_clip = axlim_clip



    _zsort_functions = {

        'average': np.average,

        'min': np.min,

        'max': np.max,

    }



    def set_zsort(self, zsort):

        

        self._zsortfunc = self._zsort_functions[zsort]

        self._sort_zpos = None

        self.stale = True



    @_api.deprecated("3.10")

    def get_vector(self, segments3d):

        return self._get_vector(segments3d)



    def _get_vector(self, segments3d):

        

        if isinstance(segments3d, np.ndarray):

            _api.check_shape((None, None, 3), segments3d=segments3d)

            if isinstance(segments3d, np.ma.MaskedArray):

                self._faces = segments3d.data

                self._invalid_vertices = segments3d.mask.any(axis=-1)

            else:

                self._faces = segments3d

                self._invalid_vertices = False

        else:

                                                                                    

                                                                          

            num_faces = len(segments3d)

            num_verts = np.fromiter(map(len, segments3d), dtype=np.intp)

            max_verts = num_verts.max(initial=0)

            segments = np.empty((num_faces, max_verts, 3))

            for i, face in enumerate(segments3d):

                segments[i, :len(face)] = face

            self._faces = segments

            self._invalid_vertices = np.arange(max_verts) >= num_verts[:, None]



    def set_verts(self, verts, closed=True):

        

        self._get_vector(verts)

                                               

        super().set_verts([], False)

        self._closed = closed



    def set_verts_and_codes(self, verts, codes):

        

                                                                       

                            

        self.set_verts(verts, closed=False)

                                        

        self._codes3d = codes



    def set_3d_properties(self, axlim_clip=False):

                                                                    

                                                              

        self.update_scalarmappable()

        self._sort_zpos = None

        self.set_zsort('average')

        self._facecolor3d = PolyCollection.get_facecolor(self)

        self._edgecolor3d = PolyCollection.get_edgecolor(self)

        self._alpha3d = PolyCollection.get_alpha(self)

        self.stale = True



    def set_sort_zpos(self, val):

        

        self._sort_zpos = val

        self.stale = True



    def do_3d_projection(self):

        

        if self._A is not None:

                                                                    

                                                                      

                                                                       

                                 

             

                                                                          

                                                               

            self.update_scalarmappable()

            if self._face_is_mapped:

                self._facecolor3d = self._facecolors

            if self._edge_is_mapped:

                self._edgecolor3d = self._edgecolors



        needs_masking = np.any(self._invalid_vertices)

        num_faces = len(self._faces)

        mask = self._invalid_vertices



                                                                            

                                       

        with np.errstate(invalid='ignore', divide='ignore'):

            pfaces = proj3d._proj_transform_vectors(self._faces, self.axes.M)



        if self._axlim_clip:

            viewlim_mask = _viewlim_mask(self._faces[..., 0], self._faces[..., 1],

                                         self._faces[..., 2], self.axes)

            if np.any(viewlim_mask):

                needs_masking = True

                mask = mask | viewlim_mask



        pzs = pfaces[..., 2]

        if needs_masking:

            pzs = np.ma.MaskedArray(pzs, mask=mask)



                                                           

        cface = self._facecolor3d

        cedge = self._edgecolor3d

        if len(cface) != num_faces:

            cface = cface.repeat(num_faces, axis=0)

        if len(cedge) != num_faces:

            if len(cedge) == 0:

                cedge = cface

            else:

                cedge = cedge.repeat(num_faces, axis=0)



        if len(pzs) > 0:

            face_z = self._zsortfunc(pzs, axis=-1)

        else:

            face_z = pzs

        if needs_masking:

            face_z = face_z.data

        face_order = np.argsort(face_z, axis=-1)[::-1]



        if len(pfaces) > 0:

            faces_2d = pfaces[face_order, :, :2]

        else:

            faces_2d = pfaces

        if self._codes3d is not None and len(self._codes3d) > 0:

            if needs_masking:

                segment_mask = ~mask[face_order, :]

                faces_2d = [face[mask, :] for face, mask

                               in zip(faces_2d, segment_mask)]

            codes = [self._codes3d[idx] for idx in face_order]

            PolyCollection.set_verts_and_codes(self, faces_2d, codes)

        else:

            if needs_masking and len(faces_2d) > 0:

                invalid_vertices_2d = np.broadcast_to(

                    mask[face_order, :, None],

                    faces_2d.shape)

                faces_2d = np.ma.MaskedArray(

                        faces_2d, mask=invalid_vertices_2d)

            PolyCollection.set_verts(self, faces_2d, self._closed)



        if len(cface) > 0:

            self._facecolors2d = cface[face_order]

        else:

            self._facecolors2d = cface

        if len(self._edgecolor3d) == len(cface) and len(cedge) > 0:

            self._edgecolors2d = cedge[face_order]

        else:

            self._edgecolors2d = self._edgecolor3d



                             

        if self._sort_zpos is not None:

            zvec = np.array([[0], [0], [self._sort_zpos], [1]])

            ztrans = proj3d._proj_transform_vec(zvec, self.axes.M)

            return ztrans[2][0]

        elif pzs.size > 0:

                                                               

                                                               

                                                  

            return np.min(pzs)

        else:

            return np.nan



    def set_facecolor(self, colors):

                             

        super().set_facecolor(colors)

        self._facecolor3d = PolyCollection.get_facecolor(self)



    def set_edgecolor(self, colors):

                             

        super().set_edgecolor(colors)

        self._edgecolor3d = PolyCollection.get_edgecolor(self)



    def set_alpha(self, alpha):

                             

        artist.Artist.set_alpha(self, alpha)

        try:

            self._facecolor3d = mcolors.to_rgba_array(

                self._facecolor3d, self._alpha)

        except (AttributeError, TypeError, IndexError):

            pass

        try:

            self._edgecolors = mcolors.to_rgba_array(

                    self._edgecolor3d, self._alpha)

        except (AttributeError, TypeError, IndexError):

            pass

        self.stale = True



    def get_facecolor(self):

                             

                                                                      

        if not hasattr(self, '_facecolors2d'):

            self.axes.M = self.axes.get_proj()

            self.do_3d_projection()

        return np.asarray(self._facecolors2d)



    def get_edgecolor(self):

                             

                                                                      

        if not hasattr(self, '_edgecolors2d'):

            self.axes.M = self.axes.get_proj()

            self.do_3d_projection()

        return np.asarray(self._edgecolors2d)





def poly_collection_2d_to_3d(col, zs=0, zdir='z', axlim_clip=False):

    

    segments_3d, codes = _paths_to_3d_segments_with_codes(

            col.get_paths(), zs, zdir)

    col.__class__ = Poly3DCollection

    col.set_verts_and_codes(segments_3d, codes)

    col.set_3d_properties()

    col._axlim_clip = axlim_clip





def juggle_axes(xs, ys, zs, zdir):

    

    if zdir == 'x':

        return zs, xs, ys

    elif zdir == 'y':

        return xs, zs, ys

    elif zdir[0] == '-':

        return rotate_axes(xs, ys, zs, zdir)

    else:

        return xs, ys, zs





def rotate_axes(xs, ys, zs, zdir):

    

    if zdir in ('x', '-y'):

        return ys, zs, xs

    elif zdir in ('-x', 'y'):

        return zs, xs, ys

    else:

        return xs, ys, zs





def _zalpha(

    colors,

    zs,

    min_alpha=0.3,

    _data_scale=None,

):

    



    if len(colors) == 0 or len(zs) == 0:

        return np.zeros((0, 4))



                                                                             

    min_alpha = np.clip(min_alpha, 0, 1)



    if _data_scale is None or _data_scale == 0:

                                                                                      

        sats = np.ones_like(zs)



    else:

                                                                   

        sats = np.clip(1 - (zs - np.min(zs)) / _data_scale, min_alpha, 1)



    rgba = np.broadcast_to(mcolors.to_rgba_array(colors), (len(zs), 4))



                                                                                 

    return np.column_stack([rgba[:, :3], rgba[:, 3] * sats])





def _all_points_on_plane(xs, ys, zs, atol=1e-8):

    

    xs, ys, zs = np.asarray(xs), np.asarray(ys), np.asarray(zs)

    points = np.column_stack([xs, ys, zs])

    points = points[~np.isnan(points).any(axis=1)]

                                                                

    points = np.unique(points, axis=0)

    if len(points) <= 3:

        return True

                                                                    

    vs = (points - points[0])[1:]

    vs = vs / np.linalg.norm(vs, axis=1)[:, np.newaxis]

                                 

    vs = np.unique(vs, axis=0)

    if len(vs) <= 2:

        return True

                                                                      

    cross_norms = np.linalg.norm(np.cross(vs[0], vs[1:]), axis=1)

    zero_cross_norms = np.where(np.isclose(cross_norms, 0, atol=atol))[0] + 1

    vs = np.delete(vs, zero_cross_norms, axis=0)

    if len(vs) <= 2:

        return True

                                                             

    n = np.cross(vs[0], vs[1])

    n = n / np.linalg.norm(n)

                                                                            

                                      

    dots = np.dot(n, vs.transpose())

    return np.allclose(dots, 0, atol=atol)





def _generate_normals(polygons):

    

    if isinstance(polygons, np.ndarray):

                                                                           

                   

        n = polygons.shape[-2]

        i1, i2, i3 = 0, n//3, 2*n//3

        v1 = polygons[..., i1, :] - polygons[..., i2, :]

        v2 = polygons[..., i2, :] - polygons[..., i3, :]

    else:

                                                                       

        v1 = np.empty((len(polygons), 3))

        v2 = np.empty((len(polygons), 3))

        for poly_i, ps in enumerate(polygons):

            n = len(ps)

            ps = np.asarray(ps)

            i1, i2, i3 = 0, n//3, 2*n//3

            v1[poly_i, :] = ps[i1, :] - ps[i2, :]

            v2[poly_i, :] = ps[i2, :] - ps[i3, :]

    return np.cross(v1, v2)





def _shade_colors(color, normals, lightsource=None):

    

    if lightsource is None:

                                            

        lightsource = mcolors.LightSource(azdeg=225, altdeg=19.4712)



    with np.errstate(invalid="ignore"):

        shade = ((normals / np.linalg.norm(normals, axis=1, keepdims=True))

                 @ lightsource.direction)

    mask = ~np.isnan(shade)



    if mask.any():

                                                          

        in_norm = mcolors.Normalize(-1, 1)

        out_norm = mcolors.Normalize(0.3, 1).inverse



        def norm(x):

            return out_norm(in_norm(x))



        shade[~mask] = 0



        color = mcolors.to_rgba_array(color)

                                                                      

                                       

                                                  

        alpha = color[:, 3]

        colors = norm(shade)[:, np.newaxis] * color

        colors[:, 3] = alpha

    else:

        colors = np.asanyarray(color).copy()



    return colors

