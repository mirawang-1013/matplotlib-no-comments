



from contextlib import ExitStack

import inspect

import itertools

import functools

import logging

from numbers import Integral

import threading



import numpy as np



import matplotlib as mpl

from matplotlib import _blocking_input, backend_bases, _docstring, projections

from matplotlib.artist import (

    Artist, allow_rasterization, _finalize_rasterization)

from matplotlib.backend_bases import (

    DrawEvent, FigureCanvasBase, NonGuiException, MouseButton, _get_renderer)

import matplotlib._api as _api

import matplotlib.cbook as cbook

import matplotlib.colorbar as cbar

import matplotlib.image as mimage



from matplotlib.axes import Axes

from matplotlib.gridspec import GridSpec, SubplotParams

from matplotlib.layout_engine import (

    ConstrainedLayoutEngine, TightLayoutEngine, LayoutEngine,

    PlaceHolderLayoutEngine

)

import matplotlib.legend as mlegend

from matplotlib.patches import Rectangle

from matplotlib.text import Text

from matplotlib.transforms import (Affine2D, Bbox, BboxTransformTo,

                                   TransformedBbox)



_log = logging.getLogger(__name__)





def _stale_figure_callback(self, val):

    if (fig := self.get_figure(root=False)) is not None:

        fig.stale = val





class _AxesStack:

    



    def __init__(self):

        self._axes = {}                                   

        self._counter = itertools.count()



    def as_list(self):

        

        return [*self._axes]                                         



    def remove(self, a):

        

        self._axes.pop(a)



    def bubble(self, a):

        

        if a not in self._axes:

            raise ValueError("Axes has not been added yet")

        self._axes[a] = next(self._counter)



    def add(self, a):

        

        if a not in self._axes:

            self._axes[a] = next(self._counter)



    def current(self):

        

        return max(self._axes, key=self._axes.__getitem__, default=None)



    def __getstate__(self):

        return {

            **vars(self),

            "_counter": max(self._axes.values(), default=0)

        }



    def __setstate__(self, state):

        next_counter = state.pop('_counter')

        vars(self).update(state)

        self._counter = itertools.count(next_counter)





class FigureBase(Artist):

    

    def __init__(self, **kwargs):

        super().__init__()

                                                     

                                                              

                                                                       

                                             

        del self._axes



        self._suptitle = None

        self._supxlabel = None

        self._supylabel = None



                                                                           

                                                     

                                                              

        self._align_label_groups = {

            "x": cbook.Grouper(),

            "y": cbook.Grouper(),

            "title": cbook.Grouper()

        }



        self._localaxes = []                  

        self.artists = []

        self.lines = []

        self.patches = []

        self.texts = []

        self.images = []

        self.legends = []

        self.subfigs = []

        self.stale = True

        self.suppressComposite = None

        self.set(**kwargs)



    def _get_draw_artists(self, renderer):

        

        artists = self.get_children()



        artists.remove(self.patch)

        artists = sorted(

            (artist for artist in artists if not artist.get_animated()),

            key=lambda artist: artist.get_zorder())

        for ax in self._localaxes:

            locator = ax.get_axes_locator()

            ax.apply_aspect(locator(ax, renderer) if locator else None)



            for child in ax.get_children():

                if hasattr(child, 'apply_aspect'):

                    locator = child.get_axes_locator()

                    child.apply_aspect(

                        locator(child, renderer) if locator else None)

        return artists



    def autofmt_xdate(

            self, bottom=0.2, rotation=30, ha='right', which='major'):

        

        _api.check_in_list(['major', 'minor', 'both'], which=which)

        axes = [ax for ax in self.axes if ax._label != '<colorbar>']

        allsubplots = all(ax.get_subplotspec() for ax in axes)

        if len(axes) == 1:

            for label in self.axes[0].get_xticklabels(which=which):

                label.set_ha(ha)

                label.set_rotation(rotation)

        else:

            if allsubplots:

                for ax in axes:

                    if ax.get_subplotspec().is_last_row():

                        for label in ax.get_xticklabels(which=which):

                            label.set_ha(ha)

                            label.set_rotation(rotation)

                    else:

                        for label in ax.get_xticklabels(which=which):

                            label.set_visible(False)

                        ax.set_xlabel('')



        engine = self.get_layout_engine()

        if allsubplots and (engine is None or engine.adjust_compatible):

            self.subplots_adjust(bottom=bottom)

        self.stale = True



    def get_children(self):

        

        return [self.patch,

                *self.artists,

                *self._localaxes,

                *self.lines,

                *self.patches,

                *self.texts,

                *self.images,

                *self.legends,

                *self.subfigs]



    def get_figure(self, root=None):

        

        if self._root_figure is self:

                              

            return self



        if self._parent is self._root_figure:

                                                                                  

                    

            return self._parent



        if root is None:

                                                                                

                                             

            message = ('From Matplotlib 3.12 SubFigure.get_figure will by default '

                       'return the direct parent figure, which may be a SubFigure. '

                       'To suppress this warning, pass the root parameter.  Pass '

                       '`True` to maintain the old behavior and `False` to opt-in to '

                       'the future behavior.')

            _api.warn_deprecated('3.10', message=message)

            root = True



        if root:

            return self._root_figure



        return self._parent



    def set_figure(self, fig):

        

        no_switch = ("The parent and root figures of a (Sub)Figure are set at "

                     "instantiation and cannot be changed.")

        if fig is self._root_figure:

            _api.warn_deprecated(

                "3.10",

                message=(f"{no_switch} From Matplotlib 3.12 this operation will raise "

                         "an exception."))

            return



        raise ValueError(no_switch)



    figure = property(functools.partial(get_figure, root=True), set_figure,

                      doc=("The root `Figure`.  To get the parent of a `SubFigure`, "

                           "use the `get_figure` method."))



    def contains(self, mouseevent):

        

        if self._different_canvas(mouseevent):

            return False, {}

        inside = self.bbox.contains(mouseevent.x, mouseevent.y)

        return inside, {}



    def get_window_extent(self, renderer=None):

                             

        return self.bbox



    def _suplabels(self, t, info, **kwargs):

        



        x = kwargs.pop('x', None)

        y = kwargs.pop('y', None)

        if info['name'] in ['_supxlabel', '_suptitle']:

            autopos = y is None

        elif info['name'] == '_supylabel':

            autopos = x is None

        if x is None:

            x = info['x0']

        if y is None:

            y = info['y0']



        kwargs = cbook.normalize_kwargs(kwargs, Text)

        kwargs.setdefault('horizontalalignment', info['ha'])

        kwargs.setdefault('verticalalignment', info['va'])

        kwargs.setdefault('rotation', info['rotation'])



        if 'fontproperties' not in kwargs:

            kwargs.setdefault('fontsize', mpl.rcParams[info['size']])

            kwargs.setdefault('fontweight', mpl.rcParams[info['weight']])



        suplab = getattr(self, info['name'])

        if suplab is not None:

            suplab.set_text(t)

            suplab.set_position((x, y))

            suplab.set(**kwargs)

        else:

            suplab = self.text(x, y, t, **kwargs)

            setattr(self, info['name'], suplab)

        suplab._autopos = autopos

        self.stale = True

        return suplab



    @_docstring.Substitution(x0=0.5, y0=0.98, name='super title', ha='center',

                             va='top', rc='title')

    @_docstring.copy(_suplabels)

    def suptitle(self, t, **kwargs):

                                      

        info = {'name': '_suptitle', 'x0': 0.5, 'y0': 0.98,

                'ha': 'center', 'va': 'top', 'rotation': 0,

                'size': 'figure.titlesize', 'weight': 'figure.titleweight'}

        return self._suplabels(t, info, **kwargs)



    def get_suptitle(self):

        

        text_obj = self._suptitle

        return "" if text_obj is None else text_obj.get_text()



    @_docstring.Substitution(x0=0.5, y0=0.01, name='super xlabel', ha='center',

                             va='bottom', rc='label')

    @_docstring.copy(_suplabels)

    def supxlabel(self, t, **kwargs):

                                      

        info = {'name': '_supxlabel', 'x0': 0.5, 'y0': 0.01,

                'ha': 'center', 'va': 'bottom', 'rotation': 0,

                'size': 'figure.labelsize', 'weight': 'figure.labelweight'}

        return self._suplabels(t, info, **kwargs)



    def get_supxlabel(self):

        

        text_obj = self._supxlabel

        return "" if text_obj is None else text_obj.get_text()



    @_docstring.Substitution(x0=0.02, y0=0.5, name='super ylabel', ha='left',

                             va='center', rc='label')

    @_docstring.copy(_suplabels)

    def supylabel(self, t, **kwargs):

                                      

        info = {'name': '_supylabel', 'x0': 0.02, 'y0': 0.5,

                'ha': 'left', 'va': 'center', 'rotation': 'vertical',

                'rotation_mode': 'anchor', 'size': 'figure.labelsize',

                'weight': 'figure.labelweight'}

        return self._suplabels(t, info, **kwargs)



    def get_supylabel(self):

        

        text_obj = self._supylabel

        return "" if text_obj is None else text_obj.get_text()



    def get_edgecolor(self):

        

        return self.patch.get_edgecolor()



    def get_facecolor(self):

        

        return self.patch.get_facecolor()



    def get_frameon(self):

        

        return self.patch.get_visible()



    def set_linewidth(self, linewidth):

        

        self.patch.set_linewidth(linewidth)



    def get_linewidth(self):

        

        return self.patch.get_linewidth()



    def set_edgecolor(self, color):

        

        self.patch.set_edgecolor(color)



    def set_facecolor(self, color):

        

        self.patch.set_facecolor(color)



    def set_frameon(self, b):

        

        self.patch.set_visible(b)

        self.stale = True



    frameon = property(get_frameon, set_frameon)



    def add_artist(self, artist, clip=False):

        

        artist.set_figure(self)

        self.artists.append(artist)

        artist._remove_method = self.artists.remove



        if not artist.is_transform_set():

            artist.set_transform(self.transSubfigure)



        if clip and artist.get_clip_path() is None:

            artist.set_clip_path(self.patch)



        self.stale = True

        return artist



    @_docstring.interpd

    def add_axes(self, *args, **kwargs):

        



        if not len(args) and 'rect' not in kwargs:

            raise TypeError("add_axes() missing 1 required positional argument: 'rect'")

        elif 'rect' in kwargs:

            if len(args):

                raise TypeError("add_axes() got multiple values for argument 'rect'")

            args = (kwargs.pop('rect'), )

        if len(args) != 1:

            raise _api.nargs_error("add_axes", 1, len(args))



        if isinstance(args[0], Axes):

            a, = args

            key = a._projection_init

            if a.get_figure(root=False) is not self:

                raise ValueError(

                    "The Axes must have been created in the present figure")

        else:

            rect, = args

            if not np.isfinite(rect).all():

                raise ValueError(f'all entries in rect must be finite not {rect}')

            projection_class, pkw = self._process_projection_requirements(**kwargs)



                                                            

            a = projection_class(self, rect, **pkw)

            key = (projection_class, pkw)



        return self._add_axes_internal(a, key)



    @_docstring.interpd

    def add_subplot(self, *args, **kwargs):

        

        if 'figure' in kwargs:

                                                                           

                                                                    

            raise _api.kwarg_error("add_subplot", "figure")



        if (len(args) == 1

                and isinstance(args[0], mpl.axes._base._AxesBase)

                and args[0].get_subplotspec()):

            ax = args[0]

            key = ax._projection_init

            if ax.get_figure(root=False) is not self:

                raise ValueError("The Axes must have been created in "

                                 "the present figure")

        else:

            if not args:

                args = (1, 1, 1)

                                                                    

                                                                            

                                                                        

            if (len(args) == 1 and isinstance(args[0], Integral)

                    and 100 <= args[0] <= 999):

                args = tuple(map(int, str(args[0])))

            projection_class, pkw = self._process_projection_requirements(**kwargs)

            ax = projection_class(self, *args, **pkw)

            key = (projection_class, pkw)

        return self._add_axes_internal(ax, key)



    def _add_axes_internal(self, ax, key):

        

        self._axstack.add(ax)

        if ax not in self._localaxes:

            self._localaxes.append(ax)

        self.sca(ax)

        ax._remove_method = self.delaxes

                                                             

        ax._projection_init = key

        self.stale = True

        ax.stale_callback = _stale_figure_callback

        return ax



    def subplots(self, nrows=1, ncols=1, *, sharex=False, sharey=False,

                 squeeze=True, width_ratios=None, height_ratios=None,

                 subplot_kw=None, gridspec_kw=None):

        

        gridspec_kw = dict(gridspec_kw or {})

        if height_ratios is not None:

            if 'height_ratios' in gridspec_kw:

                raise ValueError("'height_ratios' must not be defined both as "

                                 "parameter and as key in 'gridspec_kw'")

            gridspec_kw['height_ratios'] = height_ratios

        if width_ratios is not None:

            if 'width_ratios' in gridspec_kw:

                raise ValueError("'width_ratios' must not be defined both as "

                                 "parameter and as key in 'gridspec_kw'")

            gridspec_kw['width_ratios'] = width_ratios



        gs = self.add_gridspec(nrows, ncols, figure=self, **gridspec_kw)

        axs = gs.subplots(sharex=sharex, sharey=sharey, squeeze=squeeze,

                          subplot_kw=subplot_kw)

        return axs



    def delaxes(self, ax):

        

        self._remove_axes(ax, owners=[self._axstack, self._localaxes])



    def _remove_axes(self, ax, owners):

        

        for owner in owners:

            owner.remove(ax)



        self._axobservers.process("_axes_change_event", self)

        self.stale = True

        self._root_figure.canvas.release_mouse(ax)



        for name in ax._axis_names:                                      

            grouper = ax._shared_axes[name]

            siblings = [other for other in grouper.get_siblings(ax) if other is not ax]

            if not siblings:                                                    

                continue

            grouper.remove(ax)

                                                                                      

                                                                                     

                                                      

            remaining_axis = siblings[0]._axis_map[name]

            remaining_axis.get_major_formatter().set_axis(remaining_axis)

            remaining_axis.get_major_locator().set_axis(remaining_axis)

            remaining_axis.get_minor_formatter().set_axis(remaining_axis)

            remaining_axis.get_minor_locator().set_axis(remaining_axis)



        ax._twinned_axes.remove(ax)                                        



    def clear(self, keep_observers=False):

        

        self.suppressComposite = None



                                                

        for subfig in self.subfigs:

            subfig.clear(keep_observers=keep_observers)

        self.subfigs = []



        for ax in tuple(self.axes):                          

            ax.clear()

            self.delaxes(ax)                                 



        self.artists = []

        self.lines = []

        self.patches = []

        self.texts = []

        self.images = []

        self.legends = []

        self.subplotpars.reset()

        if not keep_observers:

            self._axobservers = cbook.CallbackRegistry()

        self._suptitle = None

        self._supxlabel = None

        self._supylabel = None



        self.stale = True



                          

    def clf(self, keep_observers=False):

        

        return self.clear(keep_observers=keep_observers)



                                                                       

                                                                              

                           

                                                       

                                                               

                                                                          

    @_docstring.interpd

    def legend(self, *args, **kwargs):

        



        handles, labels, kwargs = mlegend._parse_legend_args(self.axes, *args, **kwargs)

                                                               

        kwargs.setdefault("bbox_transform", self.transSubfigure)

        l = mlegend.Legend(self, handles, labels, **kwargs)

        self.legends.append(l)

        l._remove_method = self.legends.remove

        self.stale = True

        return l



    @_docstring.interpd

    def text(self, x, y, s, fontdict=None, **kwargs):

        

        effective_kwargs = {

            'transform': self.transSubfigure,

            **(fontdict if fontdict is not None else {}),

            **kwargs,

        }

        text = Text(x=x, y=y, text=s, **effective_kwargs)

        text.set_figure(self)

        text.stale_callback = _stale_figure_callback



        self.texts.append(text)

        text._remove_method = self.texts.remove

        self.stale = True

        return text



    @_docstring.interpd

    def colorbar(

            self, mappable, cax=None, ax=None, use_gridspec=True, **kwargs):

        



        if ax is None:

            ax = getattr(mappable, "axes", None)



        if cax is None:

            if ax is None:

                raise ValueError(

                    'Unable to determine Axes to steal space for Colorbar. '

                    'Either provide the *cax* argument to use as the Axes for '

                    'the Colorbar, provide the *ax* argument to steal space '

                    'from it, or add *mappable* to an Axes.')

            fig = (                                                      

                [*ax.flat] if isinstance(ax, np.ndarray)

                else [*ax] if np.iterable(ax)

                else [ax])[0].get_figure(root=False)

            current_ax = fig.gca()

            if (fig.get_layout_engine() is not None and

                    not fig.get_layout_engine().colorbar_gridspec):

                use_gridspec = False

            if (use_gridspec

                    and isinstance(ax, mpl.axes._base._AxesBase)

                    and ax.get_subplotspec()):

                cax, kwargs = cbar.make_axes_gridspec(ax, **kwargs)

            else:

                cax, kwargs = cbar.make_axes(ax, **kwargs)

                                                                              

            fig.sca(current_ax)

            cax.grid(visible=False, which='both', axis='both')



        if (hasattr(mappable, "get_figure") and

                (mappable_host_fig := mappable.get_figure(root=True)) is not None):

                                      

            if mappable_host_fig is not self._root_figure:

                _api.warn_external(

                        f'Adding colorbar to a different Figure '

                        f'{repr(mappable_host_fig)} than '

                        f'{repr(self._root_figure)} which '

                        f'fig.colorbar is called on.')



        NON_COLORBAR_KEYS = [                                                

            'fraction', 'pad', 'shrink', 'aspect', 'anchor', 'panchor']

        cb = cbar.Colorbar(cax, mappable, **{

            k: v for k, v in kwargs.items() if k not in NON_COLORBAR_KEYS})

        cax.get_figure(root=False).stale = True

        return cb



    def subplots_adjust(self, left=None, bottom=None, right=None, top=None,

                        wspace=None, hspace=None):

        

        if (self.get_layout_engine() is not None and

                not self.get_layout_engine().adjust_compatible):

            _api.warn_external(

                "This figure was using a layout engine that is "

                "incompatible with subplots_adjust and/or tight_layout; "

                "not calling subplots_adjust.")

            return

        self.subplotpars.update(left, bottom, right, top, wspace, hspace)

        for ax in self.axes:

            if ax.get_subplotspec() is not None:

                ax._set_position(ax.get_subplotspec().get_position(self))

        self.stale = True



    def align_xlabels(self, axs=None):

        

        if axs is None:

            axs = self.axes

        axs = [ax for ax in np.ravel(axs) if ax.get_subplotspec() is not None]

        for ax in axs:

            _log.debug(' Working on: %s', ax.get_xlabel())

            rowspan = ax.get_subplotspec().rowspan

            pos = ax.xaxis.get_label_position()                 

                                                                            

                                                                 

                                                                     

                                                      

                                            

            for axc in axs:

                if axc.xaxis.get_label_position() == pos:

                    rowspanc = axc.get_subplotspec().rowspan

                    if (pos == 'top' and rowspan.start == rowspanc.start or

                            pos == 'bottom' and rowspan.stop == rowspanc.stop):

                                                                

                        self._align_label_groups['x'].join(ax, axc)



    def align_ylabels(self, axs=None):

        

        if axs is None:

            axs = self.axes

        axs = [ax for ax in np.ravel(axs) if ax.get_subplotspec() is not None]

        for ax in axs:

            _log.debug(' Working on: %s', ax.get_ylabel())

            colspan = ax.get_subplotspec().colspan

            pos = ax.yaxis.get_label_position()                 

                                                                            

                                                                    

                                                                  

                                                      

                                            

            for axc in axs:

                if axc.yaxis.get_label_position() == pos:

                    colspanc = axc.get_subplotspec().colspan

                    if (pos == 'left' and colspan.start == colspanc.start or

                            pos == 'right' and colspan.stop == colspanc.stop):

                                                                

                        self._align_label_groups['y'].join(ax, axc)



    def align_titles(self, axs=None):

        

        if axs is None:

            axs = self.axes

        axs = [ax for ax in np.ravel(axs) if ax.get_subplotspec() is not None]

        for ax in axs:

            _log.debug(' Working on: %s', ax.get_title())

            rowspan = ax.get_subplotspec().rowspan

            for axc in axs:

                rowspanc = axc.get_subplotspec().rowspan

                if (rowspan.start == rowspanc.start):

                    self._align_label_groups['title'].join(ax, axc)



    def align_labels(self, axs=None):

        

        self.align_xlabels(axs=axs)

        self.align_ylabels(axs=axs)



    def add_gridspec(self, nrows=1, ncols=1, **kwargs):

        



        _ = kwargs.pop('figure', None)                                      

        gs = GridSpec(nrows=nrows, ncols=ncols, figure=self, **kwargs)

        return gs



    def subfigures(self, nrows=1, ncols=1, squeeze=True,

                   wspace=None, hspace=None,

                   width_ratios=None, height_ratios=None,

                   **kwargs):

        

        gs = GridSpec(nrows=nrows, ncols=ncols, figure=self,

                      wspace=wspace, hspace=hspace,

                      width_ratios=width_ratios,

                      height_ratios=height_ratios,

                      left=0, right=1, bottom=0, top=1)



        sfarr = np.empty((nrows, ncols), dtype=object)

        for i in range(nrows):

            for j in range(ncols):

                sfarr[i, j] = self.add_subfigure(gs[i, j], **kwargs)



        if self.get_layout_engine() is None and (wspace is not None or

                                                 hspace is not None):

                                                                               

                                                                                

            bottoms, tops, lefts, rights = gs.get_grid_positions(self)

            for sfrow, bottom, top in zip(sfarr, bottoms, tops):

                for sf, left, right in zip(sfrow, lefts, rights):

                    bbox = Bbox.from_extents(left, bottom, right, top)

                    sf._redo_transform_rel_fig(bbox=bbox)



        if squeeze:

                                                                               

                                                                     

            return sfarr.item() if sfarr.size == 1 else sfarr.squeeze()

        else:

                                                                            

            return sfarr



    def add_subfigure(self, subplotspec, **kwargs):

        

        sf = SubFigure(self, subplotspec, **kwargs)

        self.subfigs += [sf]

        sf._remove_method = self.subfigs.remove

        sf.stale_callback = _stale_figure_callback

        self.stale = True

        return sf



    def sca(self, a):

        

        self._axstack.bubble(a)

        self._axobservers.process("_axes_change_event", self)

        return a



    def gca(self):

        

        ax = self._axstack.current()

        return ax if ax is not None else self.add_subplot()



    def _gci(self):

                                                                     

        

                                                      

        ax = self._axstack.current()

        if ax is None:

            return None

        im = ax._gci()

        if im is not None:

            return im

                                                              

                                                               

                                                                

        for ax in reversed(self.axes):

            im = ax._gci()

            if im is not None:

                return im

        return None



    def _process_projection_requirements(self, *, axes_class=None, polar=False,

                                         projection=None, **kwargs):

        

        if axes_class is not None:

            if polar or projection is not None:

                raise ValueError(

                    "Cannot combine 'axes_class' and 'projection' or 'polar'")

            projection_class = axes_class

        else:



            if polar:

                if projection is not None and projection != 'polar':

                    raise ValueError(

                        f"polar={polar}, yet projection={projection!r}. "

                        "Only one of these arguments should be supplied."

                    )

                projection = 'polar'



            if isinstance(projection, str) or projection is None:

                projection_class = projections.get_projection_class(projection)

            elif hasattr(projection, '_as_mpl_axes'):

                projection_class, extra_kwargs = projection._as_mpl_axes()

                kwargs.update(**extra_kwargs)

            else:

                raise TypeError(

                    f"projection must be a string, None or implement a "

                    f"_as_mpl_axes method, not {projection!r}")

        return projection_class, kwargs



    def get_default_bbox_extra_artists(self):

        

        bbox_artists = [artist for artist in self.get_children()

                        if (artist.get_visible() and artist.get_in_layout())]

        for ax in self.axes:

            if ax.get_visible():

                bbox_artists.extend(ax.get_default_bbox_extra_artists())

        return bbox_artists



    def get_tightbbox(self, renderer=None, *, bbox_extra_artists=None):

        



        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()



        bb = []

        if bbox_extra_artists is None:

            artists = [artist for artist in self.get_children()

                       if (artist not in self.axes and artist.get_visible()

                           and artist.get_in_layout())]

        else:

            artists = bbox_extra_artists



        for a in artists:

            bbox = a.get_tightbbox(renderer)

            if bbox is not None:

                bb.append(bbox)



        for ax in self.axes:

            if ax.get_visible():

                                                                         

                                           

                try:

                    bbox = ax.get_tightbbox(

                        renderer, bbox_extra_artists=bbox_extra_artists)

                except TypeError:

                    bbox = ax.get_tightbbox(renderer)

                bb.append(bbox)

        bb = [b for b in bb

              if (np.isfinite(b.width) and np.isfinite(b.height)

                  and (b.width != 0 or b.height != 0))]



        isfigure = hasattr(self, 'bbox_inches')

        if len(bb) == 0:

            if isfigure:

                return self.bbox_inches

            else:

                                                                        

                bb = [self.bbox]



        _bbox = Bbox.union(bb)



        if isfigure:

                                                

            _bbox = TransformedBbox(_bbox, self.dpi_scale_trans.inverted())



        return _bbox



    @staticmethod

    def _norm_per_subplot_kw(per_subplot_kw):

        expanded = {}

        for k, v in per_subplot_kw.items():

            if isinstance(k, tuple):

                for sub_key in k:

                    if sub_key in expanded:

                        raise ValueError(f'The key {sub_key!r} appears multiple times.')

                    expanded[sub_key] = v

            else:

                if k in expanded:

                    raise ValueError(f'The key {k!r} appears multiple times.')

                expanded[k] = v

        return expanded



    @staticmethod

    def _normalize_grid_string(layout):

        if '\n' not in layout:

                                

            return [list(ln) for ln in layout.split(';')]

        else:

                               

            layout = inspect.cleandoc(layout)

            return [list(ln) for ln in layout.strip('\n').split('\n')]



    def subplot_mosaic(self, mosaic, *, sharex=False, sharey=False,

                       width_ratios=None, height_ratios=None,

                       empty_sentinel='.',

                       subplot_kw=None, per_subplot_kw=None, gridspec_kw=None):

        

        subplot_kw = subplot_kw or {}

        gridspec_kw = dict(gridspec_kw or {})

        per_subplot_kw = per_subplot_kw or {}



        if height_ratios is not None:

            if 'height_ratios' in gridspec_kw:

                raise ValueError("'height_ratios' must not be defined both as "

                                 "parameter and as key in 'gridspec_kw'")

            gridspec_kw['height_ratios'] = height_ratios

        if width_ratios is not None:

            if 'width_ratios' in gridspec_kw:

                raise ValueError("'width_ratios' must not be defined both as "

                                 "parameter and as key in 'gridspec_kw'")

            gridspec_kw['width_ratios'] = width_ratios



                                   

        if isinstance(mosaic, str):

            mosaic = self._normalize_grid_string(mosaic)

            per_subplot_kw = {

                tuple(k): v for k, v in per_subplot_kw.items()

            }



        per_subplot_kw = self._norm_per_subplot_kw(per_subplot_kw)



                                                                            

        _api.check_isinstance(bool, sharex=sharex, sharey=sharey)



        def _make_array(inp):

            

            r0, *rest = inp

            if isinstance(r0, str):

                raise ValueError('List mosaic specification must be 2D')

            for j, r in enumerate(rest, start=1):

                if isinstance(r, str):

                    raise ValueError('List mosaic specification must be 2D')

                if len(r0) != len(r):

                    raise ValueError(

                        "All of the rows must be the same length, however "

                        f"the first row ({r0!r}) has length {len(r0)} "

                        f"and row {j} ({r!r}) has length {len(r)}."

                    )

            out = np.zeros((len(inp), len(r0)), dtype=object)

            for j, r in enumerate(inp):

                for k, v in enumerate(r):

                    out[j, k] = v

            return out



        def _identify_keys_and_nested(mosaic):

            

                                                           

            unique_ids = cbook._OrderedSet()

            nested = {}

            for j, row in enumerate(mosaic):

                for k, v in enumerate(row):

                    if v == empty_sentinel:

                        continue

                    elif not cbook.is_scalar_or_string(v):

                        nested[(j, k)] = _make_array(v)

                    else:

                        unique_ids.add(v)



            return tuple(unique_ids), nested



        def _do_layout(gs, mosaic, unique_ids, nested):

            

            output = dict()



                                                                           

                                                                        

                                                                      

                                                                   

             

                                                                          

                                          

            this_level = dict()



                                         

            for name in unique_ids:

                                                      

                index = np.argwhere(mosaic == name)

                start_row, start_col = np.min(index, axis=0)

                end_row, end_col = np.max(index, axis=0) + 1

                                                

                slc = (slice(start_row, end_row), slice(start_col, end_col))

                                           

                if (mosaic[slc] != name).any():

                    raise ValueError(

                        f"While trying to layout\n{mosaic!r}\n"

                        f"we found that the label {name!r} specifies a "

                        "non-rectangular or non-contiguous area.")

                                                

                this_level[(start_row, start_col)] = (name, slc, 'axes')



                                                                             

                                   

            for (j, k), nested_mosaic in nested.items():

                this_level[(j, k)] = (None, nested_mosaic, 'nested')



                                                                  

                                                  

            for key in sorted(this_level):

                name, arg, method = this_level[key]

                                                                      

                                                                          

                                                        

                if method == 'axes':

                    slc = arg

                                       

                    if name in output:

                        raise ValueError(f"There are duplicate keys {name} "

                                         f"in the layout\n{mosaic!r}")

                    ax = self.add_subplot(

                        gs[slc], **{

                            'label': str(name),

                            **subplot_kw,

                            **per_subplot_kw.get(name, {})

                        }

                    )

                    output[name] = ax

                elif method == 'nested':

                    nested_mosaic = arg

                    j, k = key

                                                       

                    rows, cols = nested_mosaic.shape

                    nested_output = _do_layout(

                        gs[j, k].subgridspec(rows, cols),

                        nested_mosaic,

                        *_identify_keys_and_nested(nested_mosaic)

                    )

                    overlap = set(output) & set(nested_output)

                    if overlap:

                        raise ValueError(

                            f"There are duplicate keys {overlap} "

                            f"between the outer layout\n{mosaic!r}\n"

                            f"and the nested layout\n{nested_mosaic}"

                        )

                    output.update(nested_output)

                else:

                    raise RuntimeError("This should never happen")

            return output



        mosaic = _make_array(mosaic)

        rows, cols = mosaic.shape

        gs = self.add_gridspec(rows, cols, **gridspec_kw)

        ret = _do_layout(gs, mosaic, *_identify_keys_and_nested(mosaic))

        ax0 = next(iter(ret.values()))

        for ax in ret.values():

            if sharex:

                ax.sharex(ax0)

                ax._label_outer_xaxis(skip_non_rectangular_axes=True)

            if sharey:

                ax.sharey(ax0)

                ax._label_outer_yaxis(skip_non_rectangular_axes=True)

        if extra := set(per_subplot_kw) - set(ret):

            raise ValueError(

                f"The keys {extra} are in *per_subplot_kw* "

                "but not in the mosaic."

            )

        return ret



    def _set_artist_props(self, a):

        if a != self:

            a.set_figure(self)

        a.stale_callback = _stale_figure_callback

        a.set_transform(self.transSubfigure)





@_docstring.interpd

class SubFigure(FigureBase):

    



    def __init__(self, parent, subplotspec, *,

                 facecolor=None,

                 edgecolor=None,

                 linewidth=0.0,

                 frameon=None,

                 **kwargs):

        

        super().__init__(**kwargs)

        if facecolor is None:

            facecolor = "none"

        edgecolor = mpl._val_or_rc(edgecolor, 'figure.edgecolor')

        frameon = mpl._val_or_rc(frameon, 'figure.frameon')



        self._subplotspec = subplotspec

        self._parent = parent

        self._root_figure = parent._root_figure



                                           

        self._axstack = parent._axstack

        self.subplotpars = parent.subplotpars

        self.dpi_scale_trans = parent.dpi_scale_trans

        self._axobservers = parent._axobservers

        self.transFigure = parent.transFigure

        self.bbox_relative = Bbox.null()

        self._redo_transform_rel_fig()

        self.figbbox = self._parent.figbbox

        self.bbox = TransformedBbox(self.bbox_relative,

                                    self._parent.transSubfigure)

        self.transSubfigure = BboxTransformTo(self.bbox)



        self.patch = Rectangle(

            xy=(0, 0), width=1, height=1, visible=frameon,

            facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth,

                                                                    

            in_layout=False, transform=self.transSubfigure)

        self._set_artist_props(self.patch)

        self.patch.set_antialiased(False)



    @property

    def canvas(self):

        return self._parent.canvas



    @property

    def dpi(self):

        return self._parent.dpi



    @dpi.setter

    def dpi(self, value):

        self._parent.dpi = value



    def get_dpi(self):

        

        return self._parent.dpi



    def set_dpi(self, val):

        

        self._parent.dpi = val

        self.stale = True



    def _get_renderer(self):

        return self._parent._get_renderer()



    def _redo_transform_rel_fig(self, bbox=None):

        

        if bbox is not None:

            self.bbox_relative.p0 = bbox.p0

            self.bbox_relative.p1 = bbox.p1

            return

                                                         

        gs = self._subplotspec.get_gridspec()

        wr = np.asarray(gs.get_width_ratios())

        hr = np.asarray(gs.get_height_ratios())

        dx = wr[self._subplotspec.colspan].sum() / wr.sum()

        dy = hr[self._subplotspec.rowspan].sum() / hr.sum()

        x0 = wr[:self._subplotspec.colspan.start].sum() / wr.sum()

        y0 = 1 - hr[:self._subplotspec.rowspan.stop].sum() / hr.sum()

        self.bbox_relative.p0 = (x0, y0)

        self.bbox_relative.p1 = (x0 + dx, y0 + dy)



    def get_constrained_layout(self):

        

        return self._parent.get_constrained_layout()



    def get_constrained_layout_pads(self, relative=False):

        

        return self._parent.get_constrained_layout_pads(relative=relative)



    def get_layout_engine(self):

        return self._parent.get_layout_engine()



    @property

    def axes(self):

        

        return self._localaxes[:]



    get_axes = axes.fget



    def draw(self, renderer):

                             



                                                                     

        if not self.get_visible():

            return



        artists = self._get_draw_artists(renderer)



        try:

            renderer.open_group('subfigure', gid=self.get_gid())

            self.patch.draw(renderer)

            mimage._draw_list_compositing_images(

                renderer, self, artists, self.get_figure(root=True).suppressComposite)

            renderer.close_group('subfigure')



        finally:

            self.stale = False





@_docstring.interpd

class Figure(FigureBase):

    



                                                                            

                                                                               

                                                                           

                                                                              

                                                                               

                                                                                   

                                                                            

                                                                               

                                                                 



    _render_lock = threading.RLock()



    def __str__(self):

        return "Figure(%gx%g)" % tuple(self.bbox.size)



    def __repr__(self):

        return "<{clsname} size {h:g}x{w:g} with {naxes} Axes>".format(

            clsname=self.__class__.__name__,

            h=self.bbox.size[0], w=self.bbox.size[1],

            naxes=len(self.axes),

        )



    def __init__(self,

                 figsize=None,

                 dpi=None,

                 *,

                 facecolor=None,

                 edgecolor=None,

                 linewidth=0.0,

                 frameon=None,

                 subplotpars=None,                       

                 tight_layout=None,                        

                 constrained_layout=None,                                    

                 layout=None,

                 **kwargs

                 ):

        

        super().__init__(**kwargs)

        self._root_figure = self

        self._layout_engine = None



        if layout is not None:

            if (tight_layout is not None):

                _api.warn_external(

                    "The Figure parameters 'layout' and 'tight_layout' cannot "

                    "be used together. Please use 'layout' only.")

            if (constrained_layout is not None):

                _api.warn_external(

                    "The Figure parameters 'layout' and 'constrained_layout' "

                    "cannot be used together. Please use 'layout' only.")

            self.set_layout_engine(layout=layout)

        elif tight_layout is not None:

            if constrained_layout is not None:

                _api.warn_external(

                    "The Figure parameters 'tight_layout' and "

                    "'constrained_layout' cannot be used together. Please use "

                    "'layout' parameter")

            self.set_layout_engine(layout='tight')

            if isinstance(tight_layout, dict):

                self.get_layout_engine().set(**tight_layout)

        elif constrained_layout is not None:

            if isinstance(constrained_layout, dict):

                self.set_layout_engine(layout='constrained')

                self.get_layout_engine().set(**constrained_layout)

            elif constrained_layout:

                self.set_layout_engine(layout='constrained')



        else:

                                                 

            self.set_layout_engine(layout=layout)



                                                                              

                                                                           

                   

        self._canvas_callbacks = cbook.CallbackRegistry(

            signals=FigureCanvasBase.events)

        connect = self._canvas_callbacks._connect_picklable

        self._mouse_key_ids = [

            connect('key_press_event', backend_bases._key_handler),

            connect('key_release_event', backend_bases._key_handler),

            connect('key_release_event', backend_bases._key_handler),

            connect('button_press_event', backend_bases._mouse_handler),

            connect('button_release_event', backend_bases._mouse_handler),

            connect('scroll_event', backend_bases._mouse_handler),

            connect('motion_notify_event', backend_bases._mouse_handler),

        ]

        self._button_pick_id = connect('button_press_event', self.pick)

        self._scroll_pick_id = connect('scroll_event', self.pick)



        figsize = mpl._val_or_rc(figsize, 'figure.figsize')

        dpi = mpl._val_or_rc(dpi, 'figure.dpi')

        facecolor = mpl._val_or_rc(facecolor, 'figure.facecolor')

        edgecolor = mpl._val_or_rc(edgecolor, 'figure.edgecolor')

        frameon = mpl._val_or_rc(frameon, 'figure.frameon')



        figsize = _parse_figsize(figsize, dpi)



        if not np.isfinite(figsize).all() or (np.array(figsize) < 0).any():

            raise ValueError('figure size must be positive finite not '

                             f'{figsize}')

        self.bbox_inches = Bbox.from_bounds(0, 0, *figsize)



        self.dpi_scale_trans = Affine2D().scale(dpi)

                                                

        self._dpi = dpi

        self.bbox = TransformedBbox(self.bbox_inches, self.dpi_scale_trans)

        self.figbbox = self.bbox

        self.transFigure = BboxTransformTo(self.bbox)

        self.transSubfigure = self.transFigure



        self.patch = Rectangle(

            xy=(0, 0), width=1, height=1, visible=frameon,

            facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth,

                                                                    

            in_layout=False)

        self._set_artist_props(self.patch)

        self.patch.set_antialiased(False)



        FigureCanvasBase(self)                    



        if subplotpars is None:

            subplotpars = SubplotParams()



        self.subplotpars = subplotpars



        self._axstack = _AxesStack()                                          

        self.clear()



    def pick(self, mouseevent):

        if not self.canvas.widgetlock.locked():

            super().pick(mouseevent)



    def _check_layout_engines_compat(self, old, new):

        

        if old is None or new is None:

            return True

        if old.colorbar_gridspec == new.colorbar_gridspec:

            return True

                                                                         

                   

        for ax in self.axes:

            if hasattr(ax, '_colorbar'):

                                                          

                return False

        return True



    def set_layout_engine(self, layout=None, **kwargs):

        

        if layout is None:

            if mpl.rcParams['figure.autolayout']:

                layout = 'tight'

            elif mpl.rcParams['figure.constrained_layout.use']:

                layout = 'constrained'

            else:

                self._layout_engine = None

                return

        if layout == 'tight':

            new_layout_engine = TightLayoutEngine(**kwargs)

        elif layout == 'constrained':

            new_layout_engine = ConstrainedLayoutEngine(**kwargs)

        elif layout == 'compressed':

            new_layout_engine = ConstrainedLayoutEngine(compress=True,

                                                        **kwargs)

        elif layout == 'none':

            if self._layout_engine is not None:

                new_layout_engine = PlaceHolderLayoutEngine(

                    self._layout_engine.adjust_compatible,

                    self._layout_engine.colorbar_gridspec

                )

            else:

                new_layout_engine = None

        elif isinstance(layout, LayoutEngine):

            new_layout_engine = layout

        else:

            raise ValueError(f"Invalid value for 'layout': {layout!r}")



        if self._check_layout_engines_compat(self._layout_engine,

                                             new_layout_engine):

            self._layout_engine = new_layout_engine

        else:

            raise RuntimeError('Colorbar layout of new layout engine not '

                               'compatible with old engine, and a colorbar '

                               'has been created.  Engine not changed.')



    def get_layout_engine(self):

        return self._layout_engine



                                                              

                                                                  

                              



    def _repr_html_(self):

                                                                            

                                 

        if 'WebAgg' in type(self.canvas).__name__:

            from matplotlib.backends import backend_webagg

            return backend_webagg.ipython_inline_display(self)



    def show(self, warn=True):

        

        if self.canvas.manager is None:

            raise AttributeError(

                "Figure.show works only for figures managed by pyplot, "

                "normally created by pyplot.figure()")

        try:

            self.canvas.manager.show()

        except NonGuiException as exc:

            if warn:

                _api.warn_external(str(exc))



    @property

    def axes(self):

        

        return self._axstack.as_list()



    get_axes = axes.fget



    @property

    def number(self):

        

                                                                              

                                                                         

                                                                           

                                                                              

                                                                               

         

                                                                            

                                                                         

         

                                                                           

                                                                      

                                                                      

        if hasattr(self, '_number'):

            return self._number

        else:

            raise AttributeError(

                "'Figure' object has no attribute 'number'. In the future this"

                "will change to returning 'None' instead.")



    @number.setter

    def number(self, num):

        _api.warn_deprecated(

            "3.10",

            message="Changing 'Figure.number' is deprecated since %(since)s and "

                    "will raise an error starting %(removal)s")

        self._number = num



    def _get_renderer(self):

        if hasattr(self.canvas, 'get_renderer'):

            return self.canvas.get_renderer()

        else:

            return _get_renderer(self)



    def _get_dpi(self):

        return self._dpi



    def _set_dpi(self, dpi, forward=True):

        

        if dpi == self._dpi:

                                                              

            return

        self._dpi = dpi

        self.dpi_scale_trans.clear().scale(dpi)

        w, h = self.get_size_inches()

        self.set_size_inches(w, h, forward=forward)



    dpi = property(_get_dpi, _set_dpi, doc="The resolution in dots per inch.")



    def get_tight_layout(self):

        

        return isinstance(self.get_layout_engine(), TightLayoutEngine)



    @_api.deprecated("3.6", alternative="set_layout_engine",

                     pending=True)

    def set_tight_layout(self, tight):

        

        tight = mpl._val_or_rc(tight, 'figure.autolayout')

        _tight = 'tight' if bool(tight) else 'none'

        _tight_parameters = tight if isinstance(tight, dict) else {}

        self.set_layout_engine(_tight, **_tight_parameters)

        self.stale = True



    def get_constrained_layout(self):

        

        return isinstance(self.get_layout_engine(), ConstrainedLayoutEngine)



    @_api.deprecated("3.6", alternative="set_layout_engine('constrained')",

                     pending=True)

    def set_constrained_layout(self, constrained):

        

        constrained = mpl._val_or_rc(constrained, 'figure.constrained_layout.use')

        _constrained = 'constrained' if bool(constrained) else 'none'

        _parameters = constrained if isinstance(constrained, dict) else {}

        self.set_layout_engine(_constrained, **_parameters)

        self.stale = True



    @_api.deprecated(

         "3.6", alternative="figure.get_layout_engine().set()",

         pending=True)

    def set_constrained_layout_pads(self, **kwargs):

        

        if isinstance(self.get_layout_engine(), ConstrainedLayoutEngine):

            self.get_layout_engine().set(**kwargs)



    @_api.deprecated("3.6", alternative="fig.get_layout_engine().get()",

                     pending=True)

    def get_constrained_layout_pads(self, relative=False):

        

        if not isinstance(self.get_layout_engine(), ConstrainedLayoutEngine):

            return None, None, None, None

        info = self.get_layout_engine().get()

        w_pad = info['w_pad']

        h_pad = info['h_pad']

        wspace = info['wspace']

        hspace = info['hspace']



        if relative and (w_pad is not None or h_pad is not None):

            renderer = self._get_renderer()

            dpi = renderer.dpi

            w_pad = w_pad * dpi / renderer.width

            h_pad = h_pad * dpi / renderer.height



        return w_pad, h_pad, wspace, hspace



    def set_canvas(self, canvas):

        

        self.canvas = canvas



    @_docstring.interpd

    def figimage(self, X, xo=0, yo=0, alpha=None, norm=None, cmap=None,

                 vmin=None, vmax=None, origin=None, resize=False, *,

                 colorizer=None, **kwargs):

        

        if resize:

            dpi = self.get_dpi()

            figsize = [x / dpi for x in (X.shape[1], X.shape[0])]

            self.set_size_inches(figsize, forward=True)



        im = mimage.FigureImage(self, cmap=cmap, norm=norm,

                                colorizer=colorizer,

                                offsetx=xo, offsety=yo,

                                origin=origin, **kwargs)

        im.stale_callback = _stale_figure_callback



        im.set_array(X)

        im.set_alpha(alpha)

        if norm is None:

            im._check_exclusionary_keywords(colorizer, vmin=vmin, vmax=vmax)

            im.set_clim(vmin, vmax)

        self.images.append(im)

        im._remove_method = self.images.remove

        self.stale = True

        return im



    def set_size_inches(self, w, h=None, forward=True):

        

        if h is None:                                              

            w, h = w

        size = np.array([w, h])

        if not np.isfinite(size).all() or (size < 0).any():

            raise ValueError(f'figure size must be positive finite not {size}')

        self.bbox_inches.p1 = size

        if forward:

            manager = self.canvas.manager

            if manager is not None:

                manager.resize(*(size * self.dpi).astype(int))

        self.stale = True



    def get_size_inches(self):

        

        return np.array(self.bbox_inches.p1)



    def get_figwidth(self):

        

        return self.bbox_inches.width



    def get_figheight(self):

        

        return self.bbox_inches.height



    def get_dpi(self):

        

        return self.dpi



    def set_dpi(self, val):

        

        self.dpi = val

        self.stale = True



    def set_figwidth(self, val, forward=True):

        

        self.set_size_inches(val, self.get_figheight(), forward=forward)



    def set_figheight(self, val, forward=True):

        

        self.set_size_inches(self.get_figwidth(), val, forward=forward)



    def clear(self, keep_observers=False):

                             

        super().clear(keep_observers=keep_observers)

                                                      

                                       

        toolbar = self.canvas.toolbar

        if toolbar is not None:

            toolbar.update()



    @_finalize_rasterization

    @allow_rasterization

    def draw(self, renderer):

                             

        if not self.get_visible():

            return



        with self._render_lock:



            artists = self._get_draw_artists(renderer)

            try:

                renderer.open_group('figure', gid=self.get_gid())

                if self.axes and self.get_layout_engine() is not None:

                    try:

                        self.get_layout_engine().execute(self)

                    except ValueError:

                        pass

                                                                      



                self.patch.draw(renderer)

                mimage._draw_list_compositing_images(

                    renderer, self, artists, self.suppressComposite)



                renderer.close_group('figure')

            finally:

                self.stale = False



            DrawEvent("draw_event", self.canvas, renderer)._process()



    def draw_without_rendering(self):

        

        renderer = _get_renderer(self)

        with renderer._draw_disabled():

            self.draw(renderer)



    def draw_artist(self, a):

        

        a.draw(self.canvas.get_renderer())



    def __getstate__(self):

        state = super().__getstate__()



                                                                          

                                                                       

                                 

        state.pop("canvas")



                                                                   

        state["_dpi"] = state.get('_original_dpi', state['_dpi'])



                                              

        state['__mpl_version__'] = mpl.__version__



                                                                             

        from matplotlib import _pylab_helpers

        if self.canvas.manager in _pylab_helpers.Gcf.figs.values():

            state['_restore_to_pylab'] = True

        return state



    def __setstate__(self, state):

        version = state.pop('__mpl_version__')

        restore_to_pylab = state.pop('_restore_to_pylab', False)



        if version != mpl.__version__:

            _api.warn_external(

                f"This figure was saved with matplotlib version {version} and "

                f"loaded with {mpl.__version__} so may not function correctly."

            )

        self.__dict__ = state



                                                              

        FigureCanvasBase(self)                    



        if restore_to_pylab:

                                              

            import matplotlib.pyplot as plt

            import matplotlib._pylab_helpers as pylab_helpers

            allnums = plt.get_fignums()

            num = max(allnums) + 1 if allnums else 1

            backend = plt._get_backend_mod()

            mgr = backend.new_figure_manager_given_figure(num, self)

            pylab_helpers.Gcf._set_new_active_manager(mgr)

            plt.draw_if_interactive()



        self.stale = True



    def add_axobserver(self, func):

        

                                                                         

                            

        self._axobservers.connect("_axes_change_event", lambda arg: func(arg))



    def savefig(self, fname, *, transparent=None, **kwargs):

        



        kwargs.setdefault('dpi', mpl.rcParams['savefig.dpi'])

        transparent = mpl._val_or_rc(transparent, 'savefig.transparent')



        with ExitStack() as stack:

            if transparent:

                def _recursively_make_subfig_transparent(exit_stack, subfig):

                    exit_stack.enter_context(

                        subfig.patch._cm_set(

                            facecolor="none", edgecolor="none"))

                    for ax in subfig.axes:

                        exit_stack.enter_context(

                            ax.patch._cm_set(

                                facecolor="none", edgecolor="none"))

                    for sub_subfig in subfig.subfigs:

                        _recursively_make_subfig_transparent(

                            exit_stack, sub_subfig)



                def _recursively_make_axes_transparent(exit_stack, ax):

                    exit_stack.enter_context(

                        ax.patch._cm_set(facecolor="none", edgecolor="none"))

                    for child_ax in ax.child_axes:

                        exit_stack.enter_context(

                            child_ax.patch._cm_set(

                                facecolor="none", edgecolor="none"))

                    for child_childax in ax.child_axes:

                        _recursively_make_axes_transparent(

                            exit_stack, child_childax)



                kwargs.setdefault('facecolor', 'none')

                kwargs.setdefault('edgecolor', 'none')

                                                                      

                for subfig in self.subfigs:

                    _recursively_make_subfig_transparent(stack, subfig)

                                            

                for ax in self.axes:

                    _recursively_make_axes_transparent(stack, ax)

            self.canvas.print_figure(fname, **kwargs)



    def ginput(self, n=1, timeout=30, show_clicks=True,

               mouse_add=MouseButton.LEFT,

               mouse_pop=MouseButton.RIGHT,

               mouse_stop=MouseButton.MIDDLE):

        

        clicks = []

        marks = []



        def handler(event):

            is_button = event.name == "button_press_event"

            is_key = event.name == "key_press_event"

                                                                         

                                                                             

                                                                             

            if (is_button and event.button == mouse_stop

                    or is_key and event.key in ["escape", "enter"]):

                self.canvas.stop_event_loop()

                             

            elif (is_button and event.button == mouse_pop

                  or is_key and event.key in ["backspace", "delete"]):

                if clicks:

                    clicks.pop()

                    if show_clicks:

                        marks.pop().remove()

                        self.canvas.draw()

                            

            elif (is_button and event.button == mouse_add

                                                        

                  or is_key and event.key is not None):

                if event.inaxes:

                    clicks.append((event.xdata, event.ydata))

                    _log.info("input %i: %f, %f",

                              len(clicks), event.xdata, event.ydata)

                    if show_clicks:

                        line = mpl.lines.Line2D([event.xdata], [event.ydata],

                                                marker="+", color="r")

                        event.inaxes.add_line(line)

                        marks.append(line)

                        self.canvas.draw()

            if len(clicks) == n and n > 0:

                self.canvas.stop_event_loop()



        _blocking_input.blocking_input_loop(

            self, ["button_press_event", "key_press_event"], timeout, handler)



                  

        for mark in marks:

            mark.remove()

        self.canvas.draw()



        return clicks



    def waitforbuttonpress(self, timeout=-1):

        

        event = None



        def handler(ev):

            nonlocal event

            event = ev

            self.canvas.stop_event_loop()



        _blocking_input.blocking_input_loop(

            self, ["button_press_event", "key_press_event"], timeout, handler)



        return None if event is None else event.name == "key_press_event"



    def tight_layout(self, *, pad=1.08, h_pad=None, w_pad=None, rect=None):

        

                                                                        

                                                                             

                               

        engine = TightLayoutEngine(pad=pad, h_pad=h_pad, w_pad=w_pad, rect=rect)

        try:

            previous_engine = self.get_layout_engine()

            self.set_layout_engine(engine)

            engine.execute(self)

            if previous_engine is not None and not isinstance(

                previous_engine, (TightLayoutEngine, PlaceHolderLayoutEngine)

            ):

                _api.warn_external('The figure layout has changed to tight')

        finally:

            self.set_layout_engine('none')





def figaspect(arg):

    



    isarray = hasattr(arg, 'shape') and not np.isscalar(arg)



                                                                              

                                                            

    figsize_min = np.array((4.0, 2.0))                               

    figsize_max = np.array((16.0, 16.0))                               



                                           

    if isarray:

        nr, nc = arg.shape[:2]

        arr_ratio = nr / nc

    else:

        arr_ratio = arg



                                    

    fig_height = mpl.rcParams['figure.figsize'][1]



                                                                     

    newsize = np.array((fig_height / arr_ratio, fig_height))



                                                                  

    newsize /= min(1.0, *(newsize / figsize_min))



                                     

    newsize /= max(1.0, *(newsize / figsize_max))



                                                                           

                                                                  

    newsize = np.clip(newsize, figsize_min, figsize_max)

    return newsize





def _parse_figsize(figsize, dpi):

    

    num_parts = len(figsize)

    if num_parts == 2:

        return figsize

    elif num_parts == 3:

        x, y, unit = figsize

        if unit == 'in':

            pass

        elif unit == 'cm':

            x /= 2.54

            y /= 2.54

        elif unit == 'px':

            x /= dpi

            y /= dpi

        else:

            raise ValueError(

                f"Invalid unit {unit!r} in 'figsize'; "

                "supported units are 'in', 'cm', 'px'"

            )

        return x, y

    else:

        raise ValueError(

            "Invalid figsize format, expected (x, y) or (x, y, unit) but got "

            f"{figsize!r}"

        )

