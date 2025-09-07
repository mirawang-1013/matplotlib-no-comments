



import logging



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook, collections, colors, contour, ticker

import matplotlib.artist as martist

import matplotlib.colorizer as mcolorizer

import matplotlib.patches as mpatches

import matplotlib.path as mpath

import matplotlib.spines as mspines

import matplotlib.transforms as mtransforms

from matplotlib import _docstring



_log = logging.getLogger(__name__)



_docstring.interpd.register(

    _make_axes_kw_doc="""
location : None or {'left', 'right', 'top', 'bottom'}
    The location, relative to the parent Axes, where the colorbar Axes
    is created.  It also determines the *orientation* of the colorbar
    (colorbars on the left and right are vertical, colorbars at the top
    and bottom are horizontal).  If None, the location will come from the
    *orientation* if it is set (vertical colorbars on the right, horizontal
    ones at the bottom), or default to 'right' if *orientation* is unset.

orientation : None or {'vertical', 'horizontal'}
    The orientation of the colorbar.  It is preferable to set the *location*
    of the colorbar, as that also determines the *orientation*; passing
    incompatible values for *location* and *orientation* raises an exception.

fraction : float, default: 0.15
    Fraction of original Axes to use for colorbar.

shrink : float, default: 1.0
    Fraction by which to multiply the size of the colorbar.

aspect : float, default: 20
    Ratio of long to short dimensions.

pad : float, default: 0.05 if vertical, 0.15 if horizontal
    Fraction of original Axes between colorbar and new image Axes.

anchor : (float, float), optional
    The anchor point of the colorbar Axes.
    Defaults to (0.0, 0.5) if vertical; (0.5, 1.0) if horizontal.

panchor : (float, float), or *False*, optional
    The anchor point of the colorbar parent Axes. If *False*, the parent
    axes' anchor will be unchanged.
    Defaults to (1.0, 0.5) if vertical; (0.5, 0.0) if horizontal.""",

    _colormap_kw_doc="""
extend : {'neither', 'both', 'min', 'max'}
    Make pointed end(s) for out-of-range values (unless 'neither').  These are
    set for a given colormap using the colormap set_under and set_over methods.

extendfrac : {*None*, 'auto', length, lengths}
    If set to *None*, both the minimum and maximum triangular colorbar
    extensions will have a length of 5% of the interior colorbar length (this
    is the default setting).

    If set to 'auto', makes the triangular colorbar extensions the same lengths
    as the interior boxes (when *spacing* is set to 'uniform') or the same
    lengths as the respective adjacent interior boxes (when *spacing* is set to
    'proportional').

    If a scalar, indicates the length of both the minimum and maximum
    triangular colorbar extensions as a fraction of the interior colorbar
    length.  A two-element sequence of fractions may also be given, indicating
    the lengths of the minimum and maximum colorbar extensions respectively as
    a fraction of the interior colorbar length.

extendrect : bool
    If *False* the minimum and maximum colorbar extensions will be triangular
    (the default).  If *True* the extensions will be rectangular.

ticks : None or list of ticks or Locator
    If None, ticks are determined automatically from the input.

format : None or str or Formatter
    If None, `~.ticker.ScalarFormatter` is used.
    Format strings, e.g., ``"%4.2e"`` or ``"{x:.2e}"``, are supported.
    An alternative `~.ticker.Formatter` may be given instead.

drawedges : bool
    Whether to draw lines at color boundaries.

label : str
    The label on the colorbar's long axis.

boundaries, values : None or a sequence
    If unset, the colormap will be displayed on a 0-1 scale.
    If sequences, *values* must have a length 1 less than *boundaries*.  For
    each region delimited by adjacent entries in *boundaries*, the color mapped
    to the corresponding value in *values* will be used.  The size of each
    region is determined by the *spacing* parameter.
    Normally only useful for indexed colors (i.e. ``norm=NoNorm()``) or other
    unusual circumstances.

spacing : {'uniform', 'proportional'}
    For discrete colorbars (`.BoundaryNorm` or contours), 'uniform' gives each
    color the same space; 'proportional' makes the space proportional to the
    data interval.""")





def _set_ticks_on_axis_warn(*args, **kwargs):

                                                         

                                                     

    _api.warn_external("Use the colorbar set_ticks() method instead.")





class _ColorbarSpine(mspines.Spine):

    def __init__(self, axes):

        self._ax = axes

        super().__init__(axes, 'colorbar', mpath.Path(np.empty((0, 2))))

        mpatches.Patch.set_transform(self, axes.transAxes)



    def get_window_extent(self, renderer=None):

                                                                               

                                                                         

                            

        return mpatches.Patch.get_window_extent(self, renderer=renderer)



    def set_xy(self, xy):

        self._path = mpath.Path(xy, closed=True)

        self._xy = xy

        self.stale = True



    def draw(self, renderer):

        ret = mpatches.Patch.draw(self, renderer)

        self.stale = False

        return ret





class _ColorbarAxesLocator:

    

    def __init__(self, cbar):

        self._cbar = cbar

        self._orig_locator = cbar.ax._axes_locator



    def __call__(self, ax, renderer):

        if self._orig_locator is not None:

            pos = self._orig_locator(ax, renderer)

        else:

            pos = ax.get_position(original=True)

        if self._cbar.extend == 'neither':

            return pos



        y, extendlen = self._cbar._proportional_y()

        if not self._cbar._extend_lower():

            extendlen[0] = 0

        if not self._cbar._extend_upper():

            extendlen[1] = 0

        len = sum(extendlen) + 1

        shrink = 1 / len

        offset = extendlen[0] / len

                                                                  

                           

        if hasattr(ax, '_colorbar_info'):

            aspect = ax._colorbar_info['aspect']

        else:

            aspect = False

                                                           

                                

        if self._cbar.orientation == 'vertical':

            if aspect:

                self._cbar.ax.set_box_aspect(aspect*shrink)

            pos = pos.shrunk(1, shrink).translated(0, offset * pos.height)

        else:

            if aspect:

                self._cbar.ax.set_box_aspect(1/(aspect * shrink))

            pos = pos.shrunk(shrink, 1).translated(offset * pos.width, 0)

        return pos



    def get_subplotspec(self):

                                   

        return (

            self._cbar.ax.get_subplotspec()

            or getattr(self._orig_locator, "get_subplotspec", lambda: None)())





@_docstring.interpd

class Colorbar:

    



    n_rasterize = 50                                                       



    def __init__(

        self, ax, mappable=None, *,

        alpha=None,

        location=None,

        extend=None,

        extendfrac=None,

        extendrect=False,

        ticks=None,

        format=None,

        values=None,

        boundaries=None,

        spacing='uniform',

        drawedges=False,

        label='',

        cmap=None, norm=None,                             

        orientation=None, ticklocation='auto',                             

    ):

        

        if mappable is None:

            colorizer = mcolorizer.Colorizer(norm=norm, cmap=cmap)

            mappable = mcolorizer.ColorizingArtist(colorizer)



        self.mappable = mappable

        cmap = mappable.cmap

        norm = mappable.norm



        filled = True

        if isinstance(mappable, contour.ContourSet):

            cs = mappable

            alpha = cs.get_alpha()

            boundaries = cs._levels

            values = cs.cvalues

            extend = cs.extend

            filled = cs.filled

            if ticks is None:

                ticks = ticker.FixedLocator(cs.levels, nbins=10)

        elif isinstance(mappable, martist.Artist):

            alpha = mappable.get_alpha()



        mappable.colorbar = self

        mappable.colorbar_cid = mappable.callbacks.connect(

            'changed', self.update_normal)



        location_orientation = _get_orientation_from_location(location)



        _api.check_in_list(

            [None, 'vertical', 'horizontal'], orientation=orientation)

        _api.check_in_list(

            ['auto', 'left', 'right', 'top', 'bottom'],

            ticklocation=ticklocation)

        _api.check_in_list(

            ['uniform', 'proportional'], spacing=spacing)



        if location_orientation is not None and orientation is not None:

            if location_orientation != orientation:

                raise TypeError(

                    "location and orientation are mutually exclusive")

        else:

            orientation = orientation or location_orientation or "vertical"



        self.ax = ax

        self.ax._axes_locator = _ColorbarAxesLocator(self)



        if extend is None:

            if (not isinstance(mappable, contour.ContourSet)

                    and getattr(cmap, 'colorbar_extend', False) is not False):

                extend = cmap.colorbar_extend

            elif hasattr(norm, 'extend'):

                extend = norm.extend

            else:

                extend = 'neither'

        self.alpha = None

                                                             

        self.set_alpha(alpha)

        self.cmap = cmap

        self.norm = norm

        self.values = values

        self.boundaries = boundaries

        self.extend = extend

        self._inside = _api.check_getitem(

            {'neither': slice(0, None), 'both': slice(1, -1),

             'min': slice(1, None), 'max': slice(0, -1)},

            extend=extend)

        self.spacing = spacing

        self.orientation = orientation

        self.drawedges = drawedges

        self._filled = filled

        self.extendfrac = extendfrac

        self.extendrect = extendrect

        self._extend_patches = []

        self.solids = None

        self.solids_patches = []

        self.lines = []



        for spine in self.ax.spines.values():

            spine.set_visible(False)

        self.outline = self.ax.spines['outline'] = _ColorbarSpine(self.ax)



        self.dividers = collections.LineCollection(

            [],

            colors=[mpl.rcParams['axes.edgecolor']],

            linewidths=[0.5 * mpl.rcParams['axes.linewidth']],

            clip_on=False)

        self.ax.add_collection(self.dividers, autolim=False)



        self._locator = None

        self._minorlocator = None

        self._formatter = None

        self._minorformatter = None



        if ticklocation == 'auto':

            ticklocation = _get_ticklocation_from_orientation(

                orientation) if location is None else location

        self.ticklocation = ticklocation



        self.set_label(label)

        self._reset_locator_formatter_scale()



        if np.iterable(ticks):

            self._locator = ticker.FixedLocator(ticks, nbins=len(ticks))

        else:

            self._locator = ticks



        if isinstance(format, str):

                                                                            

            try:

                self._formatter = ticker.FormatStrFormatter(format)

                _ = self._formatter(0)

            except (TypeError, ValueError):

                self._formatter = ticker.StrMethodFormatter(format)

        else:

            self._formatter = format                                    

        self._draw_all()



        if isinstance(mappable, contour.ContourSet) and not mappable.filled:

            self.add_lines(mappable)



                                                        

        self.ax._colorbar = self

                                                           

        if (isinstance(self.norm, (colors.BoundaryNorm, colors.NoNorm)) or

                isinstance(self.mappable, contour.ContourSet)):

            self.ax.set_navigate(False)



                                                                            

        self._interactive_funcs = ["_get_view", "_set_view",

                                   "_set_view_from_bbox", "drag_pan"]

        for x in self._interactive_funcs:

            setattr(self.ax, x, getattr(self, x))

                                                                  

        self.ax.cla = self._cbar_cla

                                                                            

        self._extend_cid1 = self.ax.callbacks.connect(

            "xlim_changed", self._do_extends)

        self._extend_cid2 = self.ax.callbacks.connect(

            "ylim_changed", self._do_extends)



    @property

    def long_axis(self):

        

        if self.orientation == 'vertical':

            return self.ax.yaxis

        return self.ax.xaxis



    @property

    def locator(self):

        

        return self.long_axis.get_major_locator()



    @locator.setter

    def locator(self, loc):

        self.long_axis.set_major_locator(loc)

        self._locator = loc



    @property

    def minorlocator(self):

        

        return self.long_axis.get_minor_locator()



    @minorlocator.setter

    def minorlocator(self, loc):

        self.long_axis.set_minor_locator(loc)

        self._minorlocator = loc



    @property

    def formatter(self):

        

        return self.long_axis.get_major_formatter()



    @formatter.setter

    def formatter(self, fmt):

        self.long_axis.set_major_formatter(fmt)

        self._formatter = fmt



    @property

    def minorformatter(self):

        

        return self.long_axis.get_minor_formatter()



    @minorformatter.setter

    def minorformatter(self, fmt):

        self.long_axis.set_minor_formatter(fmt)

        self._minorformatter = fmt



    def _cbar_cla(self):

        

        for x in self._interactive_funcs:

            delattr(self.ax, x)

                                                                    

        del self.ax.cla

        self.ax.cla()



    def update_normal(self, mappable=None):

        

        if mappable:

                                                          

                                                                                    

                                                                                      

                                                                                  

                                                                                

                                       

                                                                                    

                         

            self.mappable = mappable

        _log.debug('colorbar update normal %r %r', self.mappable.norm, self.norm)

        self.set_alpha(self.mappable.get_alpha())

        self.cmap = self.mappable.cmap

        if self.mappable.norm != self.norm:

            self.norm = self.mappable.norm

            self._reset_locator_formatter_scale()



        self._draw_all()

        if isinstance(self.mappable, contour.ContourSet):

            CS = self.mappable

            if not CS.filled:

                self.add_lines(CS)

        self.stale = True



    def _draw_all(self):

        

        if self.orientation == 'vertical':

            if mpl.rcParams['ytick.minor.visible']:

                self.minorticks_on()

        else:

            if mpl.rcParams['xtick.minor.visible']:

                self.minorticks_on()

        self.long_axis.set(label_position=self.ticklocation,

                              ticks_position=self.ticklocation)

        self._short_axis().set_ticks([])

        self._short_axis().set_ticks([], minor=True)



                                                                      

                                                                     

                                                                    

                

        self._process_values()

                                                                           

                     

        self.vmin, self.vmax = self._boundaries[self._inside][[0, -1]]

                               

        X, Y = self._mesh()

                                                                              

                                                           

        self._do_extends()

        lower, upper = self.vmin, self.vmax

        if self.long_axis.get_inverted():

                                                                    

            lower, upper = upper, lower

        if self.orientation == 'vertical':

            self.ax.set_xlim(0, 1)

            self.ax.set_ylim(lower, upper)

        else:

            self.ax.set_ylim(0, 1)

            self.ax.set_xlim(lower, upper)



                                                                             

                                                                     

        self.update_ticks()



        if self._filled:

            ind = np.arange(len(self._values))

            if self._extend_lower():

                ind = ind[1:]

            if self._extend_upper():

                ind = ind[:-1]

            self._add_solids(X, Y, self._values[ind, np.newaxis])



    def _add_solids(self, X, Y, C):

        

                                         

        if self.solids is not None:

            self.solids.remove()

        for solid in self.solids_patches:

            solid.remove()

                                                                               

                                                   

        mappable = getattr(self, 'mappable', None)

        if (isinstance(mappable, contour.ContourSet)

                and any(hatch is not None for hatch in mappable.hatches)):

            self._add_solids_patches(X, Y, C, mappable)

        else:

            self.solids = self.ax.pcolormesh(

                X, Y, C, cmap=self.cmap, norm=self.norm, alpha=self.alpha,

                edgecolors='none', shading='flat')

            if not self.drawedges:

                if len(self._y) >= self.n_rasterize:

                    self.solids.set_rasterized(True)

        self._update_dividers()



    def _update_dividers(self):

        if not self.drawedges:

            self.dividers.set_segments([])

            return

                                        

        if self.orientation == 'vertical':

            lims = self.ax.get_ylim()

            bounds = (lims[0] < self._y) & (self._y < lims[1])

        else:

            lims = self.ax.get_xlim()

            bounds = (lims[0] < self._y) & (self._y < lims[1])

        y = self._y[bounds]

                                                           

        if self._extend_lower():

            y = np.insert(y, 0, lims[0])

        if self._extend_upper():

            y = np.append(y, lims[1])

        X, Y = np.meshgrid([0, 1], y)

        if self.orientation == 'vertical':

            segments = np.dstack([X, Y])

        else:

            segments = np.dstack([Y, X])

        self.dividers.set_segments(segments)



    def _add_solids_patches(self, X, Y, C, mappable):

        hatches = mappable.hatches * (len(C) + 1)                        

        if self._extend_lower():

                                                                

            hatches = hatches[1:]

        patches = []

        for i in range(len(X) - 1):

            xy = np.array([[X[i, 0], Y[i, 1]],

                           [X[i, 1], Y[i, 0]],

                           [X[i + 1, 1], Y[i + 1, 0]],

                           [X[i + 1, 0], Y[i + 1, 1]]])

            patch = mpatches.PathPatch(mpath.Path(xy),

                                       facecolor=self.cmap(self.norm(C[i][0])),

                                       hatch=hatches[i], linewidth=0,

                                       antialiased=False, alpha=self.alpha)

            self.ax.add_patch(patch)

            patches.append(patch)

        self.solids_patches = patches



    def _do_extends(self, ax=None):

        

                                              

        for patch in self._extend_patches:

            patch.remove()

        self._extend_patches = []

                                                                      

                                 

        _, extendlen = self._proportional_y()

        bot = 0 - (extendlen[0] if self._extend_lower() else 0)

        top = 1 + (extendlen[1] if self._extend_upper() else 0)



                                                                            

        if not self.extendrect:

                       

            xyout = np.array([[0, 0], [0.5, bot], [1, 0],

                              [1, 1], [0.5, top], [0, 1], [0, 0]])

        else:

                        

            xyout = np.array([[0, 0], [0, bot], [1, bot], [1, 0],

                              [1, 1], [1, top], [0, top], [0, 1],

                              [0, 0]])



        if self.orientation == 'horizontal':

            xyout = xyout[:, ::-1]



                                          

        self.outline.set_xy(xyout)

        if not self._filled:

            return



                                                                        

                                                        

        mappable = getattr(self, 'mappable', None)

        if (isinstance(mappable, contour.ContourSet)

                and any(hatch is not None for hatch in mappable.hatches)):

            hatches = mappable.hatches * (len(self._y) + 1)

        else:

            hatches = [None] * (len(self._y) + 1)



        if self._extend_lower():

            if not self.extendrect:

                          

                xy = np.array([[0, 0], [0.5, bot], [1, 0]])

            else:

                           

                xy = np.array([[0, 0], [0, bot], [1., bot], [1, 0]])

            if self.orientation == 'horizontal':

                xy = xy[:, ::-1]

                           

            val = -1 if self.long_axis.get_inverted() else 0

            color = self.cmap(self.norm(self._values[val]))

            patch = mpatches.PathPatch(

                mpath.Path(xy), facecolor=color, alpha=self.alpha,

                linewidth=0, antialiased=False,

                transform=self.ax.transAxes,

                hatch=hatches[0], clip_on=False,

                                                                      

                                                  

                zorder=np.nextafter(self.ax.patch.zorder, -np.inf))

            self.ax.add_patch(patch)

            self._extend_patches.append(patch)

                                                                

            hatches = hatches[1:]

        if self._extend_upper():

            if not self.extendrect:

                          

                xy = np.array([[0, 1], [0.5, top], [1, 1]])

            else:

                           

                xy = np.array([[0, 1], [0, top], [1, top], [1, 1]])

            if self.orientation == 'horizontal':

                xy = xy[:, ::-1]

                           

            val = 0 if self.long_axis.get_inverted() else -1

            color = self.cmap(self.norm(self._values[val]))

            hatch_idx = len(self._y) - 1

            patch = mpatches.PathPatch(

                mpath.Path(xy), facecolor=color, alpha=self.alpha,

                linewidth=0, antialiased=False,

                transform=self.ax.transAxes, hatch=hatches[hatch_idx],

                clip_on=False,

                                                                      

                                                  

                zorder=np.nextafter(self.ax.patch.zorder, -np.inf))

            self.ax.add_patch(patch)

            self._extend_patches.append(patch)



        self._update_dividers()



    def add_lines(self, *args, **kwargs):

        

        params = _api.select_matching_signature(

            [lambda self, CS, erase=True: locals(),

             lambda self, levels, colors, linewidths, erase=True: locals()],

            self, *args, **kwargs)

        if "CS" in params:

            self, cs, erase = params.values()

            if not isinstance(cs, contour.ContourSet) or cs.filled:

                raise ValueError("If a single artist is passed to add_lines, "

                                 "it must be a ContourSet of lines")

                                                                             

            return self.add_lines(

                cs.levels,

                cs.to_rgba(cs.cvalues, cs.alpha),

                cs.get_linewidths(),

                erase=erase)

        else:

            self, levels, colors, linewidths, erase = params.values()



        y = self._locate(levels)

        rtol = (self._y[-1] - self._y[0]) * 1e-10

        igood = (y < self._y[-1] + rtol) & (y > self._y[0] - rtol)

        y = y[igood]

        if np.iterable(colors):

            colors = np.asarray(colors)[igood]

        if np.iterable(linewidths):

            linewidths = np.asarray(linewidths)[igood]

        X, Y = np.meshgrid([0, 1], y)

        if self.orientation == 'vertical':

            xy = np.stack([X, Y], axis=-1)

        else:

            xy = np.stack([Y, X], axis=-1)

        col = collections.LineCollection(xy, linewidths=linewidths,

                                         colors=colors)



        if erase and self.lines:

            for lc in self.lines:

                lc.remove()

            self.lines = []

        self.lines.append(col)



                                                                           

        fac = np.max(linewidths) / 72

        xy = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])

        inches = self.ax.get_figure().dpi_scale_trans

                       

        xy = inches.inverted().transform(self.ax.transAxes.transform(xy))

        xy[[0, 1, 4], 1] -= fac

        xy[[2, 3], 1] += fac

                               

        xy = self.ax.transAxes.inverted().transform(inches.transform(xy))

        col.set_clip_path(mpath.Path(xy, closed=True),

                          self.ax.transAxes)

        self.ax.add_collection(col, autolim=False)

        self.stale = True



    def update_ticks(self):

        

                                                                               

        self._get_ticker_locator_formatter()

        self.long_axis.set_major_locator(self._locator)

        self.long_axis.set_minor_locator(self._minorlocator)

        self.long_axis.set_major_formatter(self._formatter)



    def _get_ticker_locator_formatter(self):

        

        locator = self._locator

        formatter = self._formatter

        minorlocator = self._minorlocator

        if isinstance(self.norm, colors.BoundaryNorm):

            b = self.norm.boundaries

            if locator is None:

                locator = ticker.FixedLocator(b, nbins=10)

            if minorlocator is None:

                minorlocator = ticker.FixedLocator(b)

        elif isinstance(self.norm, colors.NoNorm):

            if locator is None:

                                                                        

                nv = len(self._values)

                base = 1 + int(nv / 10)

                locator = ticker.IndexLocator(base=base, offset=.5)

        elif self.boundaries is not None:

            b = self._boundaries[self._inside]

            if locator is None:

                locator = ticker.FixedLocator(b, nbins=10)

        else:               

            if locator is None:

                                                                           

                                

                locator = self.long_axis.get_major_locator()

            if minorlocator is None:

                minorlocator = self.long_axis.get_minor_locator()



        if minorlocator is None:

            minorlocator = ticker.NullLocator()



        if formatter is None:

            formatter = self.long_axis.get_major_formatter()



        self._locator = locator

        self._formatter = formatter

        self._minorlocator = minorlocator

        _log.debug('locator: %r', locator)



    def set_ticks(self, ticks, *, labels=None, minor=False, **kwargs):

        

        if np.iterable(ticks):

            self.long_axis.set_ticks(ticks, labels=labels, minor=minor,

                                        **kwargs)

            self._locator = self.long_axis.get_major_locator()

        else:

            self._locator = ticks

            self.long_axis.set_major_locator(self._locator)

        self.stale = True



    def get_ticks(self, minor=False):

        

        if minor:

            return self.long_axis.get_minorticklocs()

        else:

            return self.long_axis.get_majorticklocs()



    def set_ticklabels(self, ticklabels, *, minor=False, **kwargs):

        

        self.long_axis.set_ticklabels(ticklabels, minor=minor, **kwargs)



    def minorticks_on(self):

        

        self.ax.minorticks_on()

        self._short_axis().set_minor_locator(ticker.NullLocator())



    def minorticks_off(self):

        

        self._minorlocator = ticker.NullLocator()

        self.long_axis.set_minor_locator(self._minorlocator)



    def set_label(self, label, *, loc=None, **kwargs):

        

        if self.orientation == "vertical":

            self.ax.set_ylabel(label, loc=loc, **kwargs)

        else:

            self.ax.set_xlabel(label, loc=loc, **kwargs)

        self.stale = True



    def set_alpha(self, alpha):

        

        self.alpha = None if isinstance(alpha, np.ndarray) else alpha



    def _set_scale(self, scale, **kwargs):

        

        self.long_axis._set_axes_scale(scale, **kwargs)



    def remove(self):

        

        if hasattr(self.ax, '_colorbar_info'):

            parents = self.ax._colorbar_info['parents']

            for a in parents:

                if self.ax in a._colorbars:

                    a._colorbars.remove(self.ax)



        self.ax.remove()



        self.mappable.callbacks.disconnect(self.mappable.colorbar_cid)

        self.mappable.colorbar = None

        self.mappable.colorbar_cid = None

                                        

        self.ax.callbacks.disconnect(self._extend_cid1)

        self.ax.callbacks.disconnect(self._extend_cid2)



        try:

            ax = self.mappable.axes

        except AttributeError:

            return

        try:

            subplotspec = self.ax.get_subplotspec().get_gridspec()._subplot_spec

        except AttributeError:                          

            pos = ax.get_position(original=True)

            ax._set_position(pos)

        else:                         

            ax.set_subplotspec(subplotspec)



    def _process_values(self):

        

        if self.values is not None:

                                                     

            self._values = np.array(self.values)

            if self.boundaries is None:

                                           

                b = np.zeros(len(self.values) + 1)

                b[1:-1] = 0.5 * (self._values[:-1] + self._values[1:])

                b[0] = 2.0 * b[1] - b[2]

                b[-1] = 2.0 * b[-2] - b[-3]

                self._boundaries = b

                return

            self._boundaries = np.array(self.boundaries)

            return



                                                      

        if isinstance(self.norm, colors.BoundaryNorm):

            b = self.norm.boundaries

        elif isinstance(self.norm, colors.NoNorm):

                                                                           

            b = np.arange(self.cmap.N + 1) - .5

        elif self.boundaries is not None:

            b = self.boundaries

        else:

                                                                      

            N = self.cmap.N + 1

            b, _ = self._uniform_y(N)

                                         

        if self._extend_lower():

            b = np.hstack((b[0] - 1, b))

        if self._extend_upper():

            b = np.hstack((b, b[-1] + 1))



                                          

        if self.mappable.get_array() is not None:

            self.mappable.autoscale_None()

        if not self.norm.scaled():

                                                                              

            self.norm.vmin = 0

            self.norm.vmax = 1

        self.norm.vmin, self.norm.vmax = mtransforms.nonsingular(

            self.norm.vmin, self.norm.vmax, expander=0.1)

        if (not isinstance(self.norm, colors.BoundaryNorm) and

                (self.boundaries is None)):

            b = self.norm.inverse(b)



        self._boundaries = np.asarray(b, dtype=float)

        self._values = 0.5 * (self._boundaries[:-1] + self._boundaries[1:])

        if isinstance(self.norm, colors.NoNorm):

            self._values = (self._values + 0.00001).astype(np.int16)



    def _mesh(self):

        

        y, _ = self._proportional_y()

                                                                          

                                                                    

                                                                         

                         

        if (isinstance(self.norm, (colors.BoundaryNorm, colors.NoNorm))

                or self.boundaries is not None):

                               

            y = y * (self.vmax - self.vmin) + self.vmin

        else:

                                                                       

                                                                           

                                                       

            with (self.norm.callbacks.blocked(),

                  cbook._setattr_cm(self.norm, vmin=self.vmin, vmax=self.vmax)):

                y = self.norm.inverse(y)

        self._y = y

        X, Y = np.meshgrid([0., 1.], y)

        if self.orientation == 'vertical':

            return (X, Y)

        else:

            return (Y, X)



    def _forward_boundaries(self, x):

                                                   

        b = self._boundaries

        y = np.interp(x, b, np.linspace(0, 1, len(b)))

                                                    

        eps = (b[-1] - b[0]) * 1e-6

                                                              

                                  

        y[x < b[0]-eps] = -1

        y[x > b[-1]+eps] = 2

        return y



    def _inverse_boundaries(self, x):

                             

        b = self._boundaries

        return np.interp(x, np.linspace(0, 1, len(b)), b)



    def _reset_locator_formatter_scale(self):

        

        self._process_values()

        self._locator = None

        self._minorlocator = None

        self._formatter = None

        self._minorformatter = None

        if (isinstance(self.mappable, contour.ContourSet) and

                isinstance(self.norm, colors.LogNorm)):

                                                                

            self._set_scale('log')

        elif (self.boundaries is not None or

                isinstance(self.norm, colors.BoundaryNorm)):

            if self.spacing == 'uniform':

                funcs = (self._forward_boundaries, self._inverse_boundaries)

                self._set_scale('function', functions=funcs)

            elif self.spacing == 'proportional':

                self._set_scale('linear')

        elif getattr(self.norm, '_scale', None):

                                                                  

            self._set_scale(self.norm._scale)

        elif type(self.norm) is colors.Normalize:

                              

            self._set_scale('linear')

        else:

                                                                       

                       

            funcs = (self.norm, self.norm.inverse)

            self._set_scale('function', functions=funcs)



    def _locate(self, x):

        

        if isinstance(self.norm, (colors.NoNorm, colors.BoundaryNorm)):

            b = self._boundaries

            xn = x

        else:

                                                             

                                                         

            b = self.norm(self._boundaries, clip=False).filled()

            xn = self.norm(x, clip=False).filled()



        bunique = b[self._inside]

        yunique = self._y



        z = np.interp(xn, bunique, yunique)

        return z



                     



    def _uniform_y(self, N):

        

        automin = automax = 1. / (N - 1.)

        extendlength = self._get_extension_lengths(self.extendfrac,

                                                   automin, automax,

                                                   default=0.05)

        y = np.linspace(0, 1, N)

        return y, extendlength



    def _proportional_y(self):

        

        if (isinstance(self.norm, colors.BoundaryNorm) or

                self.boundaries is not None):

            y = (self._boundaries - self._boundaries[self._inside][0])

            y = y / (self._boundaries[self._inside][-1] -

                     self._boundaries[self._inside][0])

                                                            

                                 

            if self.spacing == 'uniform':

                yscaled = self._forward_boundaries(self._boundaries)

            else:

                yscaled = y

        else:

            y = self.norm(self._boundaries.copy())

            y = np.ma.filled(y, np.nan)

                                                          

            yscaled = y

        y = y[self._inside]

        yscaled = yscaled[self._inside]

                              

        norm = colors.Normalize(y[0], y[-1])

        y = np.ma.filled(norm(y), np.nan)

        norm = colors.Normalize(yscaled[0], yscaled[-1])

        yscaled = np.ma.filled(norm(yscaled), np.nan)

                                                                             

                                                                        

        automin = yscaled[1] - yscaled[0]

        automax = yscaled[-1] - yscaled[-2]

        extendlength = [0, 0]

        if self._extend_lower() or self._extend_upper():

            extendlength = self._get_extension_lengths(

                    self.extendfrac, automin, automax, default=0.05)

        return y, extendlength



    def _get_extension_lengths(self, frac, automin, automax, default=0.05):

        

                                

        extendlength = np.array([default, default])

        if isinstance(frac, str):

            _api.check_in_list(['auto'], extendfrac=frac.lower())

                                                              

            extendlength[:] = [automin, automax]

        elif frac is not None:

            try:

                                                                      

                extendlength[:] = frac

                                                                    

                                                   

                if np.isnan(extendlength).any():

                    raise ValueError()

            except (TypeError, ValueError) as err:

                                                                           

                raise ValueError('invalid value for extendfrac') from err

        return extendlength



    def _extend_lower(self):

        

        minmax = "max" if self.long_axis.get_inverted() else "min"

        return self.extend in ('both', minmax)



    def _extend_upper(self):

        

        minmax = "min" if self.long_axis.get_inverted() else "max"

        return self.extend in ('both', minmax)



    def _short_axis(self):

        

        if self.orientation == 'vertical':

            return self.ax.xaxis

        return self.ax.yaxis



    def _get_view(self):

                             

                                                                    

        return self.norm.vmin, self.norm.vmax



    def _set_view(self, view):

                             

                                                                    

        self.norm.vmin, self.norm.vmax = view



    def _set_view_from_bbox(self, bbox, direction='in',

                            mode=None, twinx=False, twiny=False):

                             

                                                                           

        new_xbound, new_ybound = self.ax._prepare_view_from_bbox(

            bbox, direction=direction, mode=mode, twinx=twinx, twiny=twiny)

        if self.orientation == 'horizontal':

            self.norm.vmin, self.norm.vmax = new_xbound

        elif self.orientation == 'vertical':

            self.norm.vmin, self.norm.vmax = new_ybound



    def drag_pan(self, button, key, x, y):

                             

        points = self.ax._get_pan_points(button, key, x, y)

        if points is not None:

            if self.orientation == 'horizontal':

                self.norm.vmin, self.norm.vmax = points[:, 0]

            elif self.orientation == 'vertical':

                self.norm.vmin, self.norm.vmax = points[:, 1]





ColorbarBase = Colorbar                  





def _normalize_location_orientation(location, orientation):

    if location is None:

        location = _get_ticklocation_from_orientation(orientation)

    loc_settings = _api.check_getitem({

        "left":   {"location": "left", "anchor": (1.0, 0.5),

                   "panchor": (0.0, 0.5), "pad": 0.10},

        "right":  {"location": "right", "anchor": (0.0, 0.5),

                   "panchor": (1.0, 0.5), "pad": 0.05},

        "top":    {"location": "top", "anchor": (0.5, 0.0),

                   "panchor": (0.5, 1.0), "pad": 0.05},

        "bottom": {"location": "bottom", "anchor": (0.5, 1.0),

                   "panchor": (0.5, 0.0), "pad": 0.15},

    }, location=location)

    loc_settings["orientation"] = _get_orientation_from_location(location)

    if orientation is not None and orientation != loc_settings["orientation"]:

                                                             

        raise TypeError("location and orientation are mutually exclusive")

    return loc_settings





def _get_orientation_from_location(location):

    return _api.check_getitem(

        {None: None, "left": "vertical", "right": "vertical",

         "top": "horizontal", "bottom": "horizontal"}, location=location)





def _get_ticklocation_from_orientation(orientation):

    return _api.check_getitem(

        {None: "right", "vertical": "right", "horizontal": "bottom"},

        orientation=orientation)





@_docstring.interpd

def make_axes(parents, location=None, orientation=None, fraction=0.15,

              shrink=1.0, aspect=20, **kwargs):

    

    loc_settings = _normalize_location_orientation(location, orientation)

                                                                     

                        

    kwargs['orientation'] = loc_settings['orientation']

    location = kwargs['ticklocation'] = loc_settings['location']



    anchor = kwargs.pop('anchor', loc_settings['anchor'])

    panchor = kwargs.pop('panchor', loc_settings['panchor'])

    aspect0 = aspect

                                                                    

                                                                     

                                          

    if isinstance(parents, np.ndarray):

        parents = list(parents.flat)

    elif np.iterable(parents):

        parents = list(parents)

    else:

        parents = [parents]



    fig = parents[0].get_figure()



    pad0 = 0.05 if fig.get_constrained_layout() else loc_settings['pad']

    pad = kwargs.pop('pad', pad0)



    if not all(fig is ax.get_figure() for ax in parents):

        raise ValueError('Unable to create a colorbar Axes as not all '

                         'parents share the same figure.')



                                                      

    parents_bbox = mtransforms.Bbox.union(

        [ax.get_position(original=True).frozen() for ax in parents])



    pb = parents_bbox

    if location in ('left', 'right'):

        if location == 'left':

            pbcb, _, pb1 = pb.splitx(fraction, fraction + pad)

        else:

            pb1, _, pbcb = pb.splitx(1 - fraction - pad, 1 - fraction)

        pbcb = pbcb.shrunk(1.0, shrink).anchored(anchor, pbcb)

    else:

        if location == 'bottom':

            pbcb, _, pb1 = pb.splity(fraction, fraction + pad)

        else:

            pb1, _, pbcb = pb.splity(1 - fraction - pad, 1 - fraction)

        pbcb = pbcb.shrunk(shrink, 1.0).anchored(anchor, pbcb)



                                                                             

        aspect = 1.0 / aspect



                                                                    

                          

    shrinking_trans = mtransforms.BboxTransform(parents_bbox, pb1)



                                                                   

    for ax in parents:

        new_posn = shrinking_trans.transform(ax.get_position(original=True))

        new_posn = mtransforms.Bbox(new_posn)

        ax._set_position(new_posn)

        if panchor is not False:

            ax.set_anchor(panchor)



    cax = fig.add_axes(pbcb, label="<colorbar>")

    for a in parents:

        a._colorbars.append(cax)                                     

    cax._colorbar_info = dict(

        parents=parents,

        location=location,

        shrink=shrink,

        anchor=anchor,

        panchor=panchor,

        fraction=fraction,

        aspect=aspect0,

        pad=pad)

                                                    

    cax.set_anchor(anchor)

    cax.set_box_aspect(aspect)

    cax.set_aspect('auto')



    return cax, kwargs





@_docstring.interpd

def make_axes_gridspec(parent, *, location=None, orientation=None,

                       fraction=0.15, shrink=1.0, aspect=20, **kwargs):

    



    loc_settings = _normalize_location_orientation(location, orientation)

    kwargs['orientation'] = loc_settings['orientation']

    location = kwargs['ticklocation'] = loc_settings['location']



    aspect0 = aspect

    anchor = kwargs.pop('anchor', loc_settings['anchor'])

    panchor = kwargs.pop('panchor', loc_settings['panchor'])

    pad = kwargs.pop('pad', loc_settings["pad"])

    wh_space = 2 * pad / (1 - pad)



    if location in ('left', 'right'):

        gs = parent.get_subplotspec().subgridspec(

            3, 2, wspace=wh_space, hspace=0,

            height_ratios=[(1-anchor[1])*(1-shrink), shrink, anchor[1]*(1-shrink)])

        if location == 'left':

            gs.set_width_ratios([fraction, 1 - fraction - pad])

            ss_main = gs[:, 1]

            ss_cb = gs[1, 0]

        else:

            gs.set_width_ratios([1 - fraction - pad, fraction])

            ss_main = gs[:, 0]

            ss_cb = gs[1, 1]

    else:

        gs = parent.get_subplotspec().subgridspec(

            2, 3, hspace=wh_space, wspace=0,

            width_ratios=[anchor[0]*(1-shrink), shrink, (1-anchor[0])*(1-shrink)])

        if location == 'top':

            gs.set_height_ratios([fraction, 1 - fraction - pad])

            ss_main = gs[1, :]

            ss_cb = gs[0, 1]

        else:

            gs.set_height_ratios([1 - fraction - pad, fraction])

            ss_main = gs[0, :]

            ss_cb = gs[1, 1]

        aspect = 1 / aspect



    parent.set_subplotspec(ss_main)

    if panchor is not False:

        parent.set_anchor(panchor)



    fig = parent.get_figure()

    cax = fig.add_subplot(ss_cb, label="<colorbar>")

    parent._colorbars.append(cax)                                     

    cax.set_anchor(anchor)

    cax.set_box_aspect(aspect)

    cax.set_aspect('auto')

    cax._colorbar_info = dict(

        location=location,

        parents=[parent],

        shrink=shrink,

        anchor=anchor,

        panchor=panchor,

        fraction=fraction,

        aspect=aspect0,

        pad=pad)



    return cax, kwargs

