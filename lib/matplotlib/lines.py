



import copy



from numbers import Integral, Number, Real

import logging



import numpy as np



import matplotlib as mpl

from . import _api, cbook, colors as mcolors, _docstring

from .artist import Artist, allow_rasterization

from .cbook import (

    _to_unmasked_float_array, ls_mapper, ls_mapper_r, STEP_LOOKUP_MAP)

from .markers import MarkerStyle

from .path import Path

from .transforms import Bbox, BboxTransformTo, TransformedPath

from ._enums import JoinStyle, CapStyle



                                                                  

                

from . import _path

from .markers import (        

    CARETLEFT, CARETRIGHT, CARETUP, CARETDOWN,

    CARETLEFTBASE, CARETRIGHTBASE, CARETUPBASE, CARETDOWNBASE,

    TICKLEFT, TICKRIGHT, TICKUP, TICKDOWN)



_log = logging.getLogger(__name__)





def _get_dash_pattern(style):

    

                                        

    if isinstance(style, str):

        style = ls_mapper.get(style, style)

                      

    if style in ['solid', 'None']:

        offset = 0

        dashes = None

                   

    elif style in ['dashed', 'dashdot', 'dotted']:

        offset = 0

        dashes = tuple(mpl.rcParams[f'lines.{style}_pattern'])

     

    elif isinstance(style, tuple):

        offset, dashes = style

        if offset is None:

            raise ValueError(f'Unrecognized linestyle: {style!r}')

    else:

        raise ValueError(f'Unrecognized linestyle: {style!r}')



                                                                     

    if dashes is not None:

        dsum = sum(dashes)

        if dsum:

            offset %= dsum



    return offset, dashes





def _get_dash_patterns(styles):

    

    try:

        patterns = [_get_dash_pattern(styles)]

    except ValueError:

        try:

            patterns = [_get_dash_pattern(x) for x in styles]

        except ValueError as err:

            emsg = f'Do not know how to convert {styles!r} to dashes'

            raise ValueError(emsg) from err



    return patterns





def _get_inverse_dash_pattern(offset, dashes):

    

                                                                           

               

    gaps = dashes[-1:] + dashes[:-1]

                                                              

                                                                               

    offset_gaps = offset + dashes[-1]



    return offset_gaps, gaps





def _scale_dashes(offset, dashes, lw):

    if not mpl.rcParams['lines.scale_dashes']:

        return offset, dashes

    scaled_offset = offset * lw

    scaled_dashes = ([x * lw if x is not None else None for x in dashes]

                     if dashes is not None else None)

    return scaled_offset, scaled_dashes





def segment_hits(cx, cy, x, y, radius):

    

                                     

    if len(x) <= 1:

        res, = np.nonzero((cx - x) ** 2 + (cy - y) ** 2 <= radius ** 2)

        return res



                                                

    xr, yr = x[:-1], y[:-1]



                                                                     

                              

    dx, dy = x[1:] - xr, y[1:] - yr

    Lnorm_sq = dx ** 2 + dy ** 2                                       

    u = ((cx - xr) * dx + (cy - yr) * dy) / Lnorm_sq

    candidates = (u >= 0) & (u <= 1)



                                                                  

                                                                

                                                             

                                                         

    point_hits = (cx - x) ** 2 + (cy - y) ** 2 <= radius ** 2

    candidates = candidates & ~(point_hits[:-1] | point_hits[1:])



                                                                        

                    

    px, py = xr + u * dx, yr + u * dy

    line_hits = (cx - px) ** 2 + (cy - py) ** 2 <= radius ** 2

    line_hits = line_hits & candidates

    points, = point_hits.ravel().nonzero()

    lines, = line_hits.ravel().nonzero()

    return np.concatenate((points, lines))





def _mark_every_path(markevery, tpath, affine, ax):

    

                                                         

    codes, verts = tpath.codes, tpath.vertices



    def _slice_or_none(in_v, slc):

        

        if in_v is None:

            return None

        return in_v[slc]



                                                           

    if isinstance(markevery, Integral):

        markevery = (0, markevery)

                                                              

    elif isinstance(markevery, Real):

        markevery = (0.0, markevery)



    if isinstance(markevery, tuple):

        if len(markevery) != 2:

            raise ValueError('`markevery` is a tuple but its len is not 2; '

                             f'markevery={markevery}')

        start, step = markevery

                                         

        if isinstance(step, Integral):

                                                            

            if not isinstance(start, Integral):

                raise ValueError(

                    '`markevery` is a tuple with len 2 and second element is '

                    'an int, but the first element is not an int; '

                    f'markevery={markevery}')

                                           



            return Path(verts[slice(start, None, step)],

                        _slice_or_none(codes, slice(start, None, step)))



        elif isinstance(step, Real):

            if not isinstance(start, Real):

                raise ValueError(

                    '`markevery` is a tuple with len 2 and second element is '

                    'a float, but the first element is not a float or an int; '

                    f'markevery={markevery}')

            if ax is None:

                raise ValueError(

                    "markevery is specified relative to the Axes size, but "

                    "the line does not have a Axes as parent")



                                                                      

            fin = np.isfinite(verts).all(axis=1)

            fverts = verts[fin]

            disp_coords = affine.transform(fverts)



            delta = np.empty((len(disp_coords), 2))

            delta[0, :] = 0

            delta[1:, :] = disp_coords[1:, :] - disp_coords[:-1, :]

            delta = np.hypot(*delta.T).cumsum()

                                                                        

                                                              

            (x0, y0), (x1, y1) = ax.transAxes.transform([[0, 0], [1, 1]])

            scale = np.hypot(x1 - x0, y1 - y0)

            marker_delta = np.arange(start * scale, delta[-1], step * scale)

                                                               

                                                      

            inds = np.abs(delta[np.newaxis, :] - marker_delta[:, np.newaxis])

            inds = inds.argmin(axis=1)

            inds = np.unique(inds)

                                      

            return Path(fverts[inds], _slice_or_none(codes, inds))

        else:

            raise ValueError(

                f"markevery={markevery!r} is a tuple with len 2, but its "

                f"second element is not an int or a float")



    elif isinstance(markevery, slice):

                                                      

        return Path(verts[markevery], _slice_or_none(codes, markevery))



    elif np.iterable(markevery):

                        

        try:

            return Path(verts[markevery], _slice_or_none(codes, markevery))

        except (ValueError, IndexError) as err:

            raise ValueError(

                f"markevery={markevery!r} is iterable but not a valid numpy "

                f"fancy index") from err

    else:

        raise ValueError(f"markevery={markevery!r} is not a recognized value")





@_docstring.interpd

@_api.define_aliases({

    "antialiased": ["aa"],

    "color": ["c"],

    "drawstyle": ["ds"],

    "linestyle": ["ls"],

    "linewidth": ["lw"],

    "markeredgecolor": ["mec"],

    "markeredgewidth": ["mew"],

    "markerfacecolor": ["mfc"],

    "markerfacecoloralt": ["mfcalt"],

    "markersize": ["ms"],

})

class Line2D(Artist):

    



    lineStyles = _lineStyles = {                           

        '-':    '_draw_solid',

        '--':   '_draw_dashed',

        '-.':   '_draw_dash_dot',

        ':':    '_draw_dotted',

        'None': '_draw_nothing',

        ' ':    '_draw_nothing',

        '':     '_draw_nothing',

    }



    _drawStyles_l = {

        'default':    '_draw_lines',

        'steps-mid':  '_draw_steps_mid',

        'steps-pre':  '_draw_steps_pre',

        'steps-post': '_draw_steps_post',

    }



    _drawStyles_s = {

        'steps': '_draw_steps_pre',

    }



                                          

    drawStyles = {**_drawStyles_l, **_drawStyles_s}

                                                

    drawStyleKeys = [*_drawStyles_l, *_drawStyles_s]



                                                            

                 

    markers = MarkerStyle.markers

    filled_markers = MarkerStyle.filled_markers

    fillStyles = MarkerStyle.fillstyles



    zorder = 2



    _subslice_optim_min_size = 1000



    def __str__(self):

        if self._label != "":

            return f"Line2D({self._label})"

        elif self._x is None:

            return "Line2D()"

        elif len(self._x) > 3:

            return "Line2D(({:g},{:g}),({:g},{:g}),...,({:g},{:g}))".format(

                self._x[0], self._y[0],

                self._x[1], self._y[1],

                self._x[-1], self._y[-1])

        else:

            return "Line2D(%s)" % ",".join(

                map("({:g},{:g})".format, self._x, self._y))



    def __init__(self, xdata, ydata, *,

                 linewidth=None,                           

                 linestyle=None,

                 color=None,

                 gapcolor=None,

                 marker=None,

                 markersize=None,

                 markeredgewidth=None,

                 markeredgecolor=None,

                 markerfacecolor=None,

                 markerfacecoloralt='none',

                 fillstyle=None,

                 antialiased=None,

                 dash_capstyle=None,

                 solid_capstyle=None,

                 dash_joinstyle=None,

                 solid_joinstyle=None,

                 pickradius=5,

                 drawstyle=None,

                 markevery=None,

                 **kwargs

                 ):

        

        super().__init__()



                                            

        if not np.iterable(xdata):

            raise RuntimeError('xdata must be a sequence')

        if not np.iterable(ydata):

            raise RuntimeError('ydata must be a sequence')



        linewidth = mpl._val_or_rc(linewidth, 'lines.linewidth')

        linestyle = mpl._val_or_rc(linestyle, 'lines.linestyle')

        marker = mpl._val_or_rc(marker, 'lines.marker')

        color = mpl._val_or_rc(color, 'lines.color')

        markersize = mpl._val_or_rc(markersize, 'lines.markersize')

        antialiased = mpl._val_or_rc(antialiased, 'lines.antialiased')

        dash_capstyle = mpl._val_or_rc(dash_capstyle, 'lines.dash_capstyle')

        dash_joinstyle = mpl._val_or_rc(dash_joinstyle, 'lines.dash_joinstyle')

        solid_capstyle = mpl._val_or_rc(solid_capstyle, 'lines.solid_capstyle')

        solid_joinstyle = mpl._val_or_rc(solid_joinstyle, 'lines.solid_joinstyle')



        if drawstyle is None:

            drawstyle = 'default'



        self._dashcapstyle = None

        self._dashjoinstyle = None

        self._solidjoinstyle = None

        self._solidcapstyle = None

        self.set_dash_capstyle(dash_capstyle)

        self.set_dash_joinstyle(dash_joinstyle)

        self.set_solid_capstyle(solid_capstyle)

        self.set_solid_joinstyle(solid_joinstyle)



        self._linestyles = None

        self._drawstyle = None

        self._linewidth = linewidth

        self._unscaled_dash_pattern = (0, None)                

        self._dash_pattern = (0, None)                                      



        self.set_linewidth(linewidth)

        self.set_linestyle(linestyle)

        self.set_drawstyle(drawstyle)



        self._color = None

        self.set_color(color)

        if marker is None:

            marker = 'none'            

        if not isinstance(marker, MarkerStyle):

            self._marker = MarkerStyle(marker, fillstyle)

        else:

            self._marker = marker



        self._gapcolor = None

        self.set_gapcolor(gapcolor)



        self._markevery = None

        self._markersize = None

        self._antialiased = None



        self.set_markevery(markevery)

        self.set_antialiased(antialiased)

        self.set_markersize(markersize)



        self._markeredgecolor = None

        self._markeredgewidth = None

        self._markerfacecolor = None

        self._markerfacecoloralt = None



        self.set_markerfacecolor(markerfacecolor)                          

        self.set_markerfacecoloralt(markerfacecoloralt)

        self.set_markeredgecolor(markeredgecolor)                          

        self.set_markeredgewidth(markeredgewidth)



                                                                 

                                                      

        self._internal_update(kwargs)

        self.pickradius = pickradius

        self.ind_offset = 0

        if (isinstance(self._picker, Number) and

                not isinstance(self._picker, bool)):

            self._pickradius = self._picker



        self._xorig = np.asarray([])

        self._yorig = np.asarray([])

        self._invalidx = True

        self._invalidy = True

        self._x = None

        self._y = None

        self._xy = None

        self._path = None

        self._transformed_path = None

        self._subslice = False

        self._x_filled = None                                        



        self.set_data(xdata, ydata)



    def contains(self, mouseevent):

        

        if self._different_canvas(mouseevent):

            return False, {}



                                        

        if self._invalidy or self._invalidx:

            self.recache()

        if len(self._xy) == 0:

            return False, {}



                                  

        transformed_path = self._get_transformed_path()

        path, affine = transformed_path.get_transformed_path_and_affine()

        path = affine.transform_path(path)

        xy = path.vertices

        xt = xy[:, 0]

        yt = xy[:, 1]



                                                   

        fig = self.get_figure(root=True)

        if fig is None:

            _log.warning('no figure set when check if mouse is on line')

            pixels = self._pickradius

        else:

            pixels = fig.dpi / 72. * self._pickradius



                                                                           

                                                                             

                                      

        with np.errstate(all='ignore'):

                                 

            if self._linestyle in ['None', None]:

                                                        

                ind, = np.nonzero(

                    (xt - mouseevent.x) ** 2 + (yt - mouseevent.y) ** 2

                    <= pixels ** 2)

            else:

                                                       

                ind = segment_hits(mouseevent.x, mouseevent.y, xt, yt, pixels)

                if self._drawstyle.startswith("steps"):

                    ind //= 2



        ind += self.ind_offset



                                           

        return len(ind) > 0, dict(ind=ind)



    def get_pickradius(self):

        

        return self._pickradius



    def set_pickradius(self, pickradius):

        

        if not isinstance(pickradius, Real) or pickradius < 0:

            raise ValueError("pick radius should be a distance")

        self._pickradius = pickradius



    pickradius = property(get_pickradius, set_pickradius)



    def get_fillstyle(self):

        

        return self._marker.get_fillstyle()



    def set_fillstyle(self, fs):

        

        self.set_marker(MarkerStyle(self._marker.get_marker(), fs))

        self.stale = True



    def set_markevery(self, every):

        

        self._markevery = every

        self.stale = True



    def get_markevery(self):

        

        return self._markevery



    def set_picker(self, p):

        

        if not callable(p):

            self.set_pickradius(p)

        self._picker = p



    def get_bbox(self):

        

        bbox = Bbox([[0, 0], [0, 0]])

        bbox.update_from_data_xy(self.get_xydata())

        return bbox



    def get_window_extent(self, renderer=None):

        bbox = Bbox([[0, 0], [0, 0]])

        trans_data_to_xy = self.get_transform().transform

        bbox.update_from_data_xy(trans_data_to_xy(self.get_xydata()),

                                 ignore=True)

                                         

        if self._marker:

            ms = (self._markersize / 72.0 * self.get_figure(root=True).dpi) * 0.5

            bbox = bbox.padded(ms)

        return bbox



    def set_data(self, *args):

        

        if len(args) == 1:

            (x, y), = args

        else:

            x, y = args



        self.set_xdata(x)

        self.set_ydata(y)



    def recache_always(self):

        self.recache(always=True)



    def recache(self, always=False):

        if always or self._invalidx:

            xconv = self.convert_xunits(self._xorig)

            x = _to_unmasked_float_array(xconv).ravel()

        else:

            x = self._x

        if always or self._invalidy:

            yconv = self.convert_yunits(self._yorig)

            y = _to_unmasked_float_array(yconv).ravel()

        else:

            y = self._y



        self._xy = np.column_stack(np.broadcast_arrays(x, y)).astype(float)

        self._x, self._y = self._xy.T         



        self._subslice = False

        if (self.axes

                and len(x) > self._subslice_optim_min_size

                and _path.is_sorted_and_has_non_nan(x)

                and self.axes.name == 'rectilinear'

                and self.axes.get_xscale() == 'linear'

                and self._markevery is None

                and self.get_clip_on()

                and self.get_transform() == self.axes.transData):

            self._subslice = True

            nanmask = np.isnan(x)

            if nanmask.any():

                self._x_filled = self._x.copy()

                indices = np.arange(len(x))

                self._x_filled[nanmask] = np.interp(

                    indices[nanmask], indices[~nanmask], self._x[~nanmask])

            else:

                self._x_filled = self._x



        if self._path is not None:

            interpolation_steps = self._path._interpolation_steps

        else:

            interpolation_steps = 1

        xy = STEP_LOOKUP_MAP[self._drawstyle](*self._xy.T)

        self._path = Path(np.asarray(xy).T,

                          _interpolation_steps=interpolation_steps)

        self._transformed_path = None

        self._invalidx = False

        self._invalidy = False



    def _transform_path(self, subslice=None):

        

                                                                

        if subslice is not None:

            xy = STEP_LOOKUP_MAP[self._drawstyle](*self._xy[subslice, :].T)

            _path = Path(np.asarray(xy).T,

                         _interpolation_steps=self._path._interpolation_steps)

        else:

            _path = self._path

        self._transformed_path = TransformedPath(_path, self.get_transform())



    def _get_transformed_path(self):

        

        if self._transformed_path is None:

            self._transform_path()

        return self._transformed_path



    def set_transform(self, t):

                             

        self._invalidx = True

        self._invalidy = True

        super().set_transform(t)



    @allow_rasterization

    def draw(self, renderer):

                             



        if not self.get_visible():

            return



        if self._invalidy or self._invalidx:

            self.recache()

        self.ind_offset = 0                                 

        if self._subslice and self.axes:

            x0, x1 = self.axes.get_xbound()

            i0 = self._x_filled.searchsorted(x0, 'left')

            i1 = self._x_filled.searchsorted(x1, 'right')

            subslice = slice(max(i0 - 1, 0), i1 + 1)

            self.ind_offset = subslice.start

            self._transform_path(subslice)

        else:

            subslice = None



        if self.get_path_effects():

            from matplotlib.patheffects import PathEffectRenderer

            renderer = PathEffectRenderer(self.get_path_effects(), renderer)



        renderer.open_group('line2d', self.get_gid())

        if self._lineStyles[self._linestyle] != '_draw_nothing':

            tpath, affine = (self._get_transformed_path()

                             .get_transformed_path_and_affine())

            if len(tpath.vertices):

                gc = renderer.new_gc()

                self._set_gc_clip(gc)

                gc.set_url(self.get_url())



                gc.set_antialiased(self._antialiased)

                gc.set_linewidth(self._linewidth)



                if self.is_dashed():

                    cap = self._dashcapstyle

                    join = self._dashjoinstyle

                else:

                    cap = self._solidcapstyle

                    join = self._solidjoinstyle

                gc.set_joinstyle(join)

                gc.set_capstyle(cap)

                gc.set_snap(self.get_snap())

                if self.get_sketch_params() is not None:

                    gc.set_sketch_params(*self.get_sketch_params())



                                                                 

                if self.is_dashed() and self._gapcolor is not None:

                    lc_rgba = mcolors.to_rgba(self._gapcolor, self._alpha)

                    gc.set_foreground(lc_rgba, isRGBA=True)



                    offset_gaps, gaps = _get_inverse_dash_pattern(

                        *self._dash_pattern)



                    gc.set_dashes(offset_gaps, gaps)

                    renderer.draw_path(gc, tpath, affine.frozen())



                lc_rgba = mcolors.to_rgba(self._color, self._alpha)

                gc.set_foreground(lc_rgba, isRGBA=True)



                gc.set_dashes(*self._dash_pattern)

                renderer.draw_path(gc, tpath, affine.frozen())

                gc.restore()



        if self._marker and self._markersize > 0:

            gc = renderer.new_gc()

            self._set_gc_clip(gc)

            gc.set_url(self.get_url())

            gc.set_linewidth(self._markeredgewidth)

            gc.set_antialiased(self._antialiased)



            ec_rgba = mcolors.to_rgba(

                self.get_markeredgecolor(), self._alpha)

            fc_rgba = mcolors.to_rgba(

                self._get_markerfacecolor(), self._alpha)

            fcalt_rgba = mcolors.to_rgba(

                self._get_markerfacecolor(alt=True), self._alpha)

                                                                           

                                                                             

            if (cbook._str_equal(self._markeredgecolor, "auto")

                    and not cbook._str_lower_equal(

                        self.get_markerfacecolor(), "none")):

                ec_rgba = ec_rgba[:3] + (fc_rgba[3],)

            gc.set_foreground(ec_rgba, isRGBA=True)

            if self.get_sketch_params() is not None:

                scale, length, randomness = self.get_sketch_params()

                gc.set_sketch_params(scale/2, length/2, 2*randomness)



            marker = self._marker



                                                                               

                                                           

            if self.get_drawstyle() != "default":

                with cbook._setattr_cm(

                        self, _drawstyle="default", _transformed_path=None):

                    self.recache()

                    self._transform_path(subslice)

                    tpath, affine = (self._get_transformed_path()

                                     .get_transformed_points_and_affine())

            else:

                tpath, affine = (self._get_transformed_path()

                                 .get_transformed_points_and_affine())



            if len(tpath.vertices):

                                                                

                markevery = self.get_markevery()

                if markevery is not None:

                    subsampled = _mark_every_path(

                        markevery, tpath, affine, self.axes)

                else:

                    subsampled = tpath



                snap = marker.get_snap_threshold()

                if isinstance(snap, Real):

                    snap = renderer.points_to_pixels(self._markersize) >= snap

                gc.set_snap(snap)

                gc.set_joinstyle(marker.get_joinstyle())

                gc.set_capstyle(marker.get_capstyle())

                marker_path = marker.get_path()

                marker_trans = marker.get_transform()

                w = renderer.points_to_pixels(self._markersize)



                if cbook._str_equal(marker.get_marker(), ","):

                    gc.set_linewidth(0)

                else:

                                                                   

                    marker_trans = marker_trans.scale(w)

                renderer.draw_markers(gc, marker_path, marker_trans,

                                      subsampled, affine.frozen(),

                                      fc_rgba)



                alt_marker_path = marker.get_alt_path()

                if alt_marker_path:

                    alt_marker_trans = marker.get_alt_transform()

                    alt_marker_trans = alt_marker_trans.scale(w)

                    renderer.draw_markers(

                            gc, alt_marker_path, alt_marker_trans, subsampled,

                            affine.frozen(), fcalt_rgba)



            gc.restore()



        renderer.close_group('line2d')

        self.stale = False



    def get_antialiased(self):

        

        return self._antialiased



    def get_color(self):

        

        return self._color



    def get_drawstyle(self):

        

        return self._drawstyle



    def get_gapcolor(self):

        

        return self._gapcolor



    def get_linestyle(self):

        

        return self._linestyle



    def get_linewidth(self):

        

        return self._linewidth



    def get_marker(self):

        

        return self._marker.get_marker()



    def get_markeredgecolor(self):

        

        mec = self._markeredgecolor

        if cbook._str_equal(mec, 'auto'):

            if mpl.rcParams['_internal.classic_mode']:

                if self._marker.get_marker() in ('.', ','):

                    return self._color

                if (self._marker.is_filled()

                        and self._marker.get_fillstyle() != 'none'):

                    return 'k'                             

            return self._color

        else:

            return mec



    def get_markeredgewidth(self):

        

        return self._markeredgewidth



    def _get_markerfacecolor(self, alt=False):

        if self._marker.get_fillstyle() == 'none':

            return 'none'

        fc = self._markerfacecoloralt if alt else self._markerfacecolor

        if cbook._str_lower_equal(fc, 'auto'):

            return self._color

        else:

            return fc



    def get_markerfacecolor(self):

        

        return self._get_markerfacecolor(alt=False)



    def get_markerfacecoloralt(self):

        

        return self._get_markerfacecolor(alt=True)



    def get_markersize(self):

        

        return self._markersize



    def get_data(self, orig=True):

        

        return self.get_xdata(orig=orig), self.get_ydata(orig=orig)



    def get_xdata(self, orig=True):

        

        if orig:

            return self._xorig

        if self._invalidx:

            self.recache()

        return self._x



    def get_ydata(self, orig=True):

        

        if orig:

            return self._yorig

        if self._invalidy:

            self.recache()

        return self._y



    def get_path(self):

        

        if self._invalidy or self._invalidx:

            self.recache()

        return self._path



    def get_xydata(self):

        

        if self._invalidy or self._invalidx:

            self.recache()

        return self._xy



    def set_antialiased(self, b):

        

        if self._antialiased != b:

            self.stale = True

        self._antialiased = b



    def set_color(self, color):

        

        mcolors._check_color_like(color=color)

        self._color = color

        self.stale = True



    def set_drawstyle(self, drawstyle):

        

        if drawstyle is None:

            drawstyle = 'default'

        _api.check_in_list(self.drawStyles, drawstyle=drawstyle)

        if self._drawstyle != drawstyle:

            self.stale = True

                                                         

            self._invalidx = True

        self._drawstyle = drawstyle



    def set_gapcolor(self, gapcolor):

        

        if gapcolor is not None:

            mcolors._check_color_like(color=gapcolor)

        self._gapcolor = gapcolor

        self.stale = True



    def set_linewidth(self, w):

        

        w = float(w)

        if self._linewidth != w:

            self.stale = True

        self._linewidth = w

        self._dash_pattern = _scale_dashes(*self._unscaled_dash_pattern, w)



    def set_linestyle(self, ls):

        

        if isinstance(ls, str):

            if ls in [' ', '', 'none']:

                ls = 'None'

            _api.check_in_list([*self._lineStyles, *ls_mapper_r], ls=ls)

            if ls not in self._lineStyles:

                ls = ls_mapper_r[ls]

            self._linestyle = ls

        else:

            self._linestyle = '--'

        self._unscaled_dash_pattern = _get_dash_pattern(ls)

        self._dash_pattern = _scale_dashes(

            *self._unscaled_dash_pattern, self._linewidth)

        self.stale = True



    @_docstring.interpd

    def set_marker(self, marker):

        

        self._marker = MarkerStyle(marker, self._marker.get_fillstyle())

        self.stale = True



    def _set_markercolor(self, name, has_rcdefault, val):

        if val is None:

            val = mpl.rcParams[f"lines.{name}"] if has_rcdefault else "auto"

        attr = f"_{name}"

        current = getattr(self, attr)

        if current is None:

            self.stale = True

        else:

            neq = current != val

                                                                              

            if neq.any() if isinstance(neq, np.ndarray) else neq:

                self.stale = True

        setattr(self, attr, val)



    def set_markeredgecolor(self, ec):

        

        self._set_markercolor("markeredgecolor", True, ec)



    def set_markerfacecolor(self, fc):

        

        self._set_markercolor("markerfacecolor", True, fc)



    def set_markerfacecoloralt(self, fc):

        

        self._set_markercolor("markerfacecoloralt", False, fc)



    def set_markeredgewidth(self, ew):

        

        ew = mpl._val_or_rc(ew, 'lines.markeredgewidth')

        if self._markeredgewidth != ew:

            self.stale = True

        self._markeredgewidth = ew



    def set_markersize(self, sz):

        

        sz = float(sz)

        if self._markersize != sz:

            self.stale = True

        self._markersize = sz



    def set_xdata(self, x):

        

        if not np.iterable(x):

            raise RuntimeError('x must be a sequence')

        self._xorig = copy.copy(x)

        self._invalidx = True

        self.stale = True



    def set_ydata(self, y):

        

        if not np.iterable(y):

            raise RuntimeError('y must be a sequence')

        self._yorig = copy.copy(y)

        self._invalidy = True

        self.stale = True



    def set_dashes(self, seq):

        

        if seq == (None, None) or len(seq) == 0:

            self.set_linestyle('-')

        else:

            self.set_linestyle((0, seq))



    def update_from(self, other):

        

        super().update_from(other)

        self._linestyle = other._linestyle

        self._linewidth = other._linewidth

        self._color = other._color

        self._gapcolor = other._gapcolor

        self._markersize = other._markersize

        self._markerfacecolor = other._markerfacecolor

        self._markerfacecoloralt = other._markerfacecoloralt

        self._markeredgecolor = other._markeredgecolor

        self._markeredgewidth = other._markeredgewidth

        self._unscaled_dash_pattern = other._unscaled_dash_pattern

        self._dash_pattern = other._dash_pattern

        self._dashcapstyle = other._dashcapstyle

        self._dashjoinstyle = other._dashjoinstyle

        self._solidcapstyle = other._solidcapstyle

        self._solidjoinstyle = other._solidjoinstyle



        self._marker = MarkerStyle(marker=other._marker)

        self._drawstyle = other._drawstyle



    @_docstring.interpd

    def set_dash_joinstyle(self, s):

        

        js = JoinStyle(s)

        if self._dashjoinstyle != js:

            self.stale = True

        self._dashjoinstyle = js



    @_docstring.interpd

    def set_solid_joinstyle(self, s):

        

        js = JoinStyle(s)

        if self._solidjoinstyle != js:

            self.stale = True

        self._solidjoinstyle = js



    def get_dash_joinstyle(self):

        

        return self._dashjoinstyle.name



    def get_solid_joinstyle(self):

        

        return self._solidjoinstyle.name



    @_docstring.interpd

    def set_dash_capstyle(self, s):

        

        cs = CapStyle(s)

        if self._dashcapstyle != cs:

            self.stale = True

        self._dashcapstyle = cs



    @_docstring.interpd

    def set_solid_capstyle(self, s):

        

        cs = CapStyle(s)

        if self._solidcapstyle != cs:

            self.stale = True

        self._solidcapstyle = cs



    def get_dash_capstyle(self):

        

        return self._dashcapstyle.name



    def get_solid_capstyle(self):

        

        return self._solidcapstyle.name



    def is_dashed(self):

        

        return self._linestyle in ('--', '-.', ':')





class AxLine(Line2D):

    



    def __init__(self, xy1, xy2, slope, **kwargs):

        

        super().__init__([0, 1], [0, 1], **kwargs)



        if (xy2 is None and slope is None or

                xy2 is not None and slope is not None):

            raise TypeError(

                "Exactly one of 'xy2' and 'slope' must be given")



        self._slope = slope

        self._xy1 = xy1

        self._xy2 = xy2



    def get_transform(self):

        ax = self.axes

        points_transform = self._transform - ax.transData + ax.transScale



        if self._xy2 is not None:

                                   

            (x1, y1), (x2, y2) =
                points_transform.transform([self._xy1, self._xy2])

            dx = x2 - x1

            dy = y2 - y1

            if dx == 0:

                if dy == 0:

                    raise ValueError(

                        f"Cannot draw a line through two identical points "

                        f"(x={(x1, x2)}, y={(y1, y2)})")

                slope = np.inf

            else:

                slope = dy / dx

        else:

                                              

            x1, y1 = points_transform.transform(self._xy1)

            slope = self._slope

        (vxlo, vylo), (vxhi, vyhi) = ax.transScale.transform(ax.viewLim)

                                                                     

                                                            

        if slope == 0:

            start = vxlo, y1

            stop = vxhi, y1

        elif np.isinf(slope):

            start = x1, vylo

            stop = x1, vyhi

        else:

            _, start, stop, _ = sorted([

                (vxlo, y1 + (vxlo - x1) * slope),

                (vxhi, y1 + (vxhi - x1) * slope),

                (x1 + (vylo - y1) / slope, vylo),

                (x1 + (vyhi - y1) / slope, vyhi),

            ])

        return (BboxTransformTo(Bbox([start, stop]))

                + ax.transLimits + ax.transAxes)



    def draw(self, renderer):

        self._transformed_path = None                

        super().draw(renderer)



    def get_xy1(self):

        

        return self._xy1



    def get_xy2(self):

        

        return self._xy2



    def get_slope(self):

        

        return self._slope



    def set_xy1(self, *args, **kwargs):

        

        params = _api.select_matching_signature([

            lambda self, x, y: locals(), lambda self, xy1: locals(),

        ], self, *args, **kwargs)

        if "x" in params:

            _api.warn_deprecated("3.10", message=(

                "Passing x and y separately to AxLine.set_xy1 is deprecated since "

                "%(since)s; pass them as a single tuple instead."))

            xy1 = params["x"], params["y"]

        else:

            xy1 = params["xy1"]

        self._xy1 = xy1



    def set_xy2(self, *args, **kwargs):

        

        if self._slope is None:

            params = _api.select_matching_signature([

                lambda self, x, y: locals(), lambda self, xy2: locals(),

            ], self, *args, **kwargs)

            if "x" in params:

                _api.warn_deprecated("3.10", message=(

                    "Passing x and y separately to AxLine.set_xy2 is deprecated since "

                    "%(since)s; pass them as a single tuple instead."))

                xy2 = params["x"], params["y"]

            else:

                xy2 = params["xy2"]

            self._xy2 = xy2

        else:

            raise ValueError("Cannot set an 'xy2' value while 'slope' is set;"

                             " they differ but their functionalities overlap")



    def set_slope(self, slope):

        

        if self._xy2 is None:

            self._slope = slope

        else:

            raise ValueError("Cannot set a 'slope' value while 'xy2' is set;"

                             " they differ but their functionalities overlap")





class VertexSelector:

    



    def __init__(self, line):

        

        if line.axes is None:

            raise RuntimeError('You must first add the line to the Axes')

        if line.get_picker() is None:

            raise RuntimeError('You must first set the picker property '

                               'of the line')

        self.axes = line.axes

        self.line = line

        self.cid = self.canvas.callbacks._connect_picklable(

            'pick_event', self.onpick)

        self.ind = set()



    canvas = property(lambda self: self.axes.get_figure(root=True).canvas)



    def process_selected(self, ind, xs, ys):

        

        pass



    def onpick(self, event):

        

        if event.artist is not self.line:

            return

        self.ind ^= set(event.ind)

        ind = sorted(self.ind)

        xdata, ydata = self.line.get_data()

        self.process_selected(ind, xdata[ind], ydata[ind])





lineStyles = Line2D._lineStyles

lineMarkers = MarkerStyle.markers

drawStyles = Line2D.drawStyles

fillStyles = MarkerStyle.fillstyles

