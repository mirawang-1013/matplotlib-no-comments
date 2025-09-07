from collections.abc import Iterable, Sequence

from contextlib import ExitStack

import functools

import inspect

import logging

from numbers import Real

from operator import attrgetter

import re

import textwrap

import types



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook, _docstring, offsetbox

import matplotlib.artist as martist

import matplotlib.axis as maxis

from matplotlib.cbook import _OrderedSet, _check_1d, index_of

import matplotlib.collections as mcoll

import matplotlib.colors as mcolors

import matplotlib.font_manager as font_manager

from matplotlib.gridspec import SubplotSpec

import matplotlib.image as mimage

import matplotlib.lines as mlines

import matplotlib.patches as mpatches

from matplotlib.rcsetup import cycler, validate_axisbelow

import matplotlib.spines as mspines

import matplotlib.table as mtable

import matplotlib.text as mtext

import matplotlib.ticker as mticker

import matplotlib.transforms as mtransforms



_log = logging.getLogger(__name__)





class _axis_method_wrapper:

    



    def __init__(self, attr_name, method_name, *, doc_sub=None):

        self.attr_name = attr_name

        self.method_name = method_name

                                                                             

                                                               

        doc = inspect.getdoc(getattr(maxis.Axis, method_name))

        self._missing_subs = []

        if doc:

            doc_sub = {"this Axis": f"the {self.attr_name}", **(doc_sub or {})}

            for k, v in doc_sub.items():

                if k not in doc:                                               

                    self._missing_subs.append(k)

                doc = doc.replace(k, v)

        self.__doc__ = doc



    def __set_name__(self, owner, name):

                                                        

                                                                           

                                                                             

        get_method = attrgetter(f"{self.attr_name}.{self.method_name}")



        def wrapper(self, *args, **kwargs):

            return get_method(self)(*args, **kwargs)



        wrapper.__module__ = owner.__module__

        wrapper.__name__ = name

        wrapper.__qualname__ = f"{owner.__qualname__}.{name}"

        wrapper.__doc__ = self.__doc__

                                                                              

                                                                           

                                    

        wrapper.__signature__ = inspect.signature(

            getattr(maxis.Axis, self.method_name))



        if self._missing_subs:

            raise ValueError(

                "The definition of {} expected that the docstring of Axis.{} "

                "contains {!r} as substrings".format(

                    wrapper.__qualname__, self.method_name,

                    ", ".join(map(repr, self._missing_subs))))



        setattr(owner, name, wrapper)





class _TransformedBoundsLocator:

    



    def __init__(self, bounds, transform):

        

        self._bounds = bounds

        self._transform = transform



    def __call__(self, ax, renderer):

                                                                       

                                                                           

                                                                              

        return mtransforms.TransformedBbox(

            mtransforms.Bbox.from_bounds(*self._bounds),

            self._transform - ax.get_figure(root=False).transSubfigure)





def _process_plot_format(fmt, *, ambiguous_fmt_datakey=False):

    



    linestyle = None

    marker = None

    color = None



                                                                               

                                                                            

                                                                             

                                                           

    if fmt not in ["0", "1"]:

        try:

            color = mcolors.to_rgba(fmt)

            return linestyle, marker, color

        except ValueError:

            pass



    errfmt = ("{!r} is neither a data key nor a valid format string ({})"

              if ambiguous_fmt_datakey else

              "{!r} is not a valid format string ({})")



    i = 0

    while i < len(fmt):

        c = fmt[i]

        if fmt[i:i+2] in mlines.lineStyles:                               

            if linestyle is not None:

                raise ValueError(errfmt.format(fmt, "two linestyle symbols"))

            linestyle = fmt[i:i+2]

            i += 2

        elif c in mlines.lineStyles:

            if linestyle is not None:

                raise ValueError(errfmt.format(fmt, "two linestyle symbols"))

            linestyle = c

            i += 1

        elif c in mlines.lineMarkers:

            if marker is not None:

                raise ValueError(errfmt.format(fmt, "two marker symbols"))

            marker = c

            i += 1

        elif c in mcolors.get_named_colors_mapping():

            if color is not None:

                raise ValueError(errfmt.format(fmt, "two color symbols"))

            color = c

            i += 1

        elif c == "C":

            cn_color = re.match(r"C\d+", fmt[i:])

            if not cn_color:

                raise ValueError(errfmt.format(fmt, "'C' must be followed by a number"))

            color = mcolors.to_rgba(cn_color[0])

            i += len(cn_color[0])

        else:

            raise ValueError(errfmt.format(fmt, f"unrecognized character {c!r}"))



    if linestyle is None and marker is None:

        linestyle = mpl.rcParams['lines.linestyle']

    if linestyle is None:

        linestyle = 'None'

    if marker is None:

        marker = 'None'



    return linestyle, marker, color





class _process_plot_var_args:

    



    def __init__(self, output='Line2D'):

        _api.check_in_list(['Line2D', 'Polygon', 'coordinates'], output=output)

        self.output = output

        self.set_prop_cycle(None)



    def set_prop_cycle(self, cycler):

        self._idx = 0

        self._cycler_items = [*mpl._val_or_rc(cycler, 'axes.prop_cycle')]



    def __call__(self, axes, *args, data=None, return_kwargs=False, **kwargs):

        axes._process_unit_info(kwargs=kwargs)



        for pos_only in "xy":

            if pos_only in kwargs:

                raise _api.kwarg_error(inspect.stack()[1].function, pos_only)



        if not args:

            return



        if data is None:                      

            args = [cbook.sanitize_sequence(a) for a in args]

        else:                             

            replaced = [mpl._replacer(data, arg) for arg in args]

            if len(args) == 1:

                label_namer_idx = 0

            elif len(args) == 2:                        

                                                         

                                                                             

                                                        

                                                                       

                                                                             

                                              

                                                                           

                                                      

                try:

                    _process_plot_format(args[1])

                except ValueError:           

                    label_namer_idx = 1

                else:

                    if replaced[1] is not args[1]:            

                        _api.warn_external(

                            f"Second argument {args[1]!r} is ambiguous: could "

                            f"be a format string but is in 'data'; using as "

                            f"data.  If it was intended as data, set the "

                            f"format string to an empty string to suppress "

                            f"this warning.  If it was intended as a format "

                            f"string, explicitly pass the x-values as well.  "

                            f"Alternatively, rename the entry in 'data'.",

                            RuntimeWarning)

                        label_namer_idx = 1

                    else:            

                        label_namer_idx = 0

            elif len(args) == 3:

                label_namer_idx = 1

            else:

                raise ValueError(

                    "Using arbitrary long args with data is not supported due "

                    "to ambiguity of arguments; use multiple plotting calls "

                    "instead")

            if kwargs.get("label") is None:

                kwargs["label"] = mpl._label_from_arg(

                    replaced[label_namer_idx], args[label_namer_idx])

            args = replaced

        ambiguous_fmt_datakey = data is not None and len(args) == 2



        if len(args) >= 4 and not cbook.is_scalar_or_string(

                kwargs.get("label")):

            raise ValueError("plot() with multiple groups of data (i.e., "

                             "pairs of x and y) does not support multiple "

                             "labels")



                                                                             

                                                          



        while args:

            this, args = args[:2], args[2:]

            if args and isinstance(args[0], str):

                this += args[0],

                args = args[1:]

            yield from self._plot_args(

                axes, this, kwargs, ambiguous_fmt_datakey=ambiguous_fmt_datakey,

                return_kwargs=return_kwargs

            )



    def get_next_color(self):

        

        entry = self._cycler_items[self._idx]

        if "color" in entry:

            self._idx = (self._idx + 1) % len(self._cycler_items)                   

            return entry["color"]

        else:

            return "k"



    def _getdefaults(self, kw, ignore=frozenset()):

        

        defaults = self._cycler_items[self._idx]

        if any(kw.get(k, None) is None for k in {*defaults} - ignore):

            self._idx = (self._idx + 1) % len(self._cycler_items)                   

                                                                                    

            return {k: v for k, v in defaults.items() if k not in ignore}

        else:

            return {}



    def _setdefaults(self, defaults, kw):

        

        for k in defaults:

            if kw.get(k, None) is None:

                kw[k] = defaults[k]



    def _make_line(self, axes, x, y, kw, kwargs):

        kw = {**kw, **kwargs}                                 

        self._setdefaults(self._getdefaults(kw), kw)

        seg = mlines.Line2D(x, y, **kw)

        return seg, kw



    def _make_coordinates(self, axes, x, y, kw, kwargs):

        kw = {**kw, **kwargs}                                 

        self._setdefaults(self._getdefaults(kw), kw)

        return (x, y), kw



    def _make_polygon(self, axes, x, y, kw, kwargs):

                                                           

        x = axes.convert_xunits(x)

        y = axes.convert_yunits(y)



        kw = kw.copy()                                 

        kwargs = kwargs.copy()



                                                                   

                                                                     

                                                              

                                                                        

                                                                     

                                                                        

                                                                      

                                                              

        ignores = ({'marker', 'markersize', 'markeredgecolor',

                    'markerfacecolor', 'markeredgewidth'}

                                                               

                   | {k for k, v in kwargs.items() if v is not None})



                                                         

                                                       

                                                       

                                                                

        default_dict = self._getdefaults(kw, ignores)

        self._setdefaults(default_dict, kw)



                                                               

                                                            

                                                            

                                                                

                                                                  

                     

        facecolor = kw.get('color', None)



                                                               

        default_dict.pop('color', None)



                                                     

                                       

        self._setdefaults(default_dict, kwargs)



        seg = mpatches.Polygon(np.column_stack((x, y)),

                               facecolor=facecolor,

                               fill=kwargs.get('fill', True),

                               closed=kw['closed'])

        seg.set(**kwargs)

        return seg, kwargs



    def _plot_args(self, axes, tup, kwargs, *,

                   return_kwargs=False, ambiguous_fmt_datakey=False):

        

        if len(tup) > 1 and isinstance(tup[-1], str):

                                                                    

            *xy, fmt = tup

            linestyle, marker, color = _process_plot_format(

                fmt, ambiguous_fmt_datakey=ambiguous_fmt_datakey)

        elif len(tup) == 3:

            raise ValueError('third arg must be a format string')

        else:

            xy = tup

            linestyle, marker, color = None, None, None



                                                                        

                                                                 

        if any(v is None for v in tup):

            raise ValueError("x, y, and format string must not be None")



        kw = {}

        for prop_name, val in zip(('linestyle', 'marker', 'color'),

                                  (linestyle, marker, color)):

            if val is not None:

                                                            

                if (fmt.lower() != 'none'

                        and prop_name in kwargs

                        and val != 'None'):

                                                                            

                                                                 

                                         

                                                                       

                                                                         

                                                 

                                                                             

                                                                            

                                                                              

                                                

                    _api.warn_external(

                        f"{prop_name} is redundantly defined by the "

                        f"'{prop_name}' keyword argument and the fmt string "

                        f'"{fmt}" (-> {prop_name}={val!r}). The keyword '

                        f"argument will take precedence.")

                kw[prop_name] = val



        if len(xy) == 2:

            x = _check_1d(xy[0])

            y = _check_1d(xy[1])

        else:

            x, y = index_of(xy[-1])



        if axes.xaxis is not None:

            axes.xaxis.update_units(x)

        if axes.yaxis is not None:

            axes.yaxis.update_units(y)



        if x.shape[0] != y.shape[0]:

            raise ValueError(f"x and y must have same first dimension, but "

                             f"have shapes {x.shape} and {y.shape}")

        if x.ndim > 2 or y.ndim > 2:

            raise ValueError(f"x and y can be no greater than 2D, but have "

                             f"shapes {x.shape} and {y.shape}")

        if x.ndim == 1:

            x = x[:, np.newaxis]

        if y.ndim == 1:

            y = y[:, np.newaxis]



        if self.output == 'Line2D':

            make_artist = self._make_line

        elif self.output == 'Polygon':

            kw['closed'] = kwargs.get('closed', True)

            make_artist = self._make_polygon

        elif self.output == 'coordinates':

            make_artist = self._make_coordinates

        else:

            _api.check_in_list(['Line2D', 'Polygon', 'coordinates'], output=self.output)



        ncx, ncy = x.shape[1], y.shape[1]

        if ncx > 1 and ncy > 1 and ncx != ncy:

            raise ValueError(f"x has {ncx} columns but y has {ncy} columns")

        if ncx == 0 or ncy == 0:

            return []



        label = kwargs.get('label')

        n_datasets = max(ncx, ncy)



        if cbook.is_scalar_or_string(label):

            labels = [label] * n_datasets

        elif len(label) == n_datasets:

            labels = label

        else:

            raise ValueError(

                f"label must be scalar or have the same length as the input "

                f"data, but found {len(label)} for {n_datasets} datasets.")



        result = (make_artist(axes, x[:, j % ncx], y[:, j % ncy], kw,

                              {**kwargs, 'label': label})

                  for j, label in enumerate(labels))



        if return_kwargs:

            return list(result)

        else:

            return [l[0] for l in result]





@_api.define_aliases({"facecolor": ["fc"]})

class _AxesBase(martist.Artist):

    name = "rectilinear"



                                                                     

                                                                    

                                                                        

                                                                         

                                  

                                                                         

                 

    _axis_names = ("x", "y")

    _shared_axes = {name: cbook.Grouper() for name in _axis_names}

    _twinned_axes = cbook.Grouper()



    _subclass_uses_cla = False



    dataLim: mtransforms.Bbox

    """The bounding `.Bbox` enclosing all data displayed in the Axes."""



    spines: mspines.Spines

    """
    The `.Spines` container for the Axes' spines, i.e. the lines denoting the
    data area boundaries.
    """



    xaxis: maxis.XAxis

    """
    The `.XAxis` instance.

    Common axis-related configuration can be achieved through high-level wrapper
    methods on Axes; e.g. `ax.set_xticks <.Axes.set_xticks>` is a shortcut for
    `ax.xaxis.set_ticks <.Axis.set_ticks>`. The *xaxis* attribute gives direct
    direct access to the underlying `~.axis.Axis` if you need more control.

    See also

    - :ref:`Axis wrapper methods on Axes <axes-api-axis>`
    - :doc:`Axis API </api/axis_api>`
    """



    yaxis: maxis.YAxis

    """
    The `.YAxis` instance.

    Common axis-related configuration can be achieved through high-level wrapper
    methods on Axes; e.g. `ax.set_yticks <.Axes.set_yticks>` is a shortcut for
    `ax.yaxis.set_ticks <.Axis.set_ticks>`. The *yaxis* attribute gives direct
    access to the underlying `~.axis.Axis` if you need more control.

    See also

    - :ref:`Axis wrapper methods on Axes <axes-api-axis>`
    - :doc:`Axis API </api/axis_api>`
    """



    def __str__(self):

        return "{0}({1[0]:g},{1[1]:g};{1[2]:g}x{1[3]:g})".format(

            type(self).__name__, self._position.bounds)



    def __init__(self, fig,

                 *args,

                 facecolor=None,                                 

                 frameon=True,

                 sharex=None,                                  

                 sharey=None,                                  

                 label='',

                 xscale=None,

                 yscale=None,

                 box_aspect=None,

                 forward_navigation_events="auto",

                 **kwargs

                 ):

        



        super().__init__()

        if "rect" in kwargs:

            if args:

                raise TypeError(

                    "'rect' cannot be used together with positional arguments")

            rect = kwargs.pop("rect")

            _api.check_isinstance((mtransforms.Bbox, Iterable), rect=rect)

            args = (rect,)

        subplotspec = None

        if len(args) == 1 and isinstance(args[0], mtransforms.Bbox):

            self._position = args[0].frozen()

        elif len(args) == 1 and np.iterable(args[0]):

            self._position = mtransforms.Bbox.from_bounds(*args[0])

        else:

            self._position = self._originalPosition = mtransforms.Bbox.unit()

            subplotspec = SubplotSpec._from_subplot_args(fig, args)

        if self._position.width < 0 or self._position.height < 0:

            raise ValueError('Width and height specified must be non-negative')

        self._originalPosition = self._position.frozen()

        self.axes = self

        self._aspect = 'auto'

        self._adjustable = 'box'

        self._anchor = 'C'

        self._stale_viewlims = dict.fromkeys(self._axis_names, False)

        self._forward_navigation_events = forward_navigation_events

        self._sharex = sharex

        self._sharey = sharey

        self.set_label(label)

        self.set_figure(fig)

                                                                   

                                                                          

                                                              

        if subplotspec:

            self.set_subplotspec(subplotspec)

        else:

            self._subplotspec = None

        self.set_box_aspect(box_aspect)

        self._axes_locator = None                                      



        self._children = []



                                                                 

                            

        self._colorbars = []

        self.spines = mspines.Spines.from_dict(self._gen_axes_spines())



        self.xaxis = None                                     

        self.yaxis = None                                     

        self._init_axis()                                                      

        self._axis_map = {

            name: getattr(self, f"{name}axis") for name in self._axis_names

        }                                                           

        self._facecolor = mpl._val_or_rc(facecolor, 'axes.facecolor')

        self._frameon = frameon

        self.set_axisbelow(mpl.rcParams['axes.axisbelow'])



        self._rasterization_zorder = None

        self.clear()



                                                                      

        self.fmt_xdata = None

        self.fmt_ydata = None



        self.set_navigate(True)



        if xscale:

            self.set_xscale(xscale)

        if yscale:

            self.set_yscale(yscale)



        self._internal_update(kwargs)



        for name, axis in self._axis_map.items():

            axis.callbacks._connect_picklable(

                'units', self._unit_change_handler(name))



        rcParams = mpl.rcParams

        self.tick_params(

            top=rcParams['xtick.top'] and rcParams['xtick.minor.top'],

            bottom=rcParams['xtick.bottom'] and rcParams['xtick.minor.bottom'],

            labeltop=(rcParams['xtick.labeltop'] and

                      rcParams['xtick.minor.top']),

            labelbottom=(rcParams['xtick.labelbottom'] and

                         rcParams['xtick.minor.bottom']),

            left=rcParams['ytick.left'] and rcParams['ytick.minor.left'],

            right=rcParams['ytick.right'] and rcParams['ytick.minor.right'],

            labelleft=(rcParams['ytick.labelleft'] and

                       rcParams['ytick.minor.left']),

            labelright=(rcParams['ytick.labelright'] and

                        rcParams['ytick.minor.right']),

            which='minor')



        self.tick_params(

            top=rcParams['xtick.top'] and rcParams['xtick.major.top'],

            bottom=rcParams['xtick.bottom'] and rcParams['xtick.major.bottom'],

            labeltop=(rcParams['xtick.labeltop'] and

                      rcParams['xtick.major.top']),

            labelbottom=(rcParams['xtick.labelbottom'] and

                         rcParams['xtick.major.bottom']),

            left=rcParams['ytick.left'] and rcParams['ytick.major.left'],

            right=rcParams['ytick.right'] and rcParams['ytick.major.right'],

            labelleft=(rcParams['ytick.labelleft'] and

                       rcParams['ytick.major.left']),

            labelright=(rcParams['ytick.labelright'] and

                        rcParams['ytick.major.right']),

            which='major')



    def __init_subclass__(cls, **kwargs):

        parent_uses_cla = super(cls, cls)._subclass_uses_cla

        if 'cla' in cls.__dict__:

            _api.warn_deprecated(

                '3.6',

                pending=True,

                message=f'Overriding `Axes.cla` in {cls.__qualname__} is '

                'pending deprecation in %(since)s and will be fully '

                'deprecated in favor of `Axes.clear` in the future. '

                'Please report '

                f'this to the {cls.__module__!r} author.')

        cls._subclass_uses_cla = 'cla' in cls.__dict__ or parent_uses_cla

        super().__init_subclass__(**kwargs)



    def __getstate__(self):

        state = super().__getstate__()

                                                                              

        state["_shared_axes"] = {

            name: self._shared_axes[name].get_siblings(self)

            for name in self._axis_names if self in self._shared_axes[name]}

        state["_twinned_axes"] = (self._twinned_axes.get_siblings(self)

                                  if self in self._twinned_axes else None)

        return state



    def __setstate__(self, state):

                                                                

        shared_axes = state.pop("_shared_axes")

        for name, shared_siblings in shared_axes.items():

            self._shared_axes[name].join(*shared_siblings)

        twinned_siblings = state.pop("_twinned_axes")

        if twinned_siblings:

            self._twinned_axes.join(*twinned_siblings)

        self.__dict__ = state

        self._stale = True



    def __repr__(self):

        fields = []

        if self.get_label():

            fields += [f"label={self.get_label()!r}"]

        if hasattr(self, "get_title"):

            titles = {}

            for k in ["left", "center", "right"]:

                title = self.get_title(loc=k)

                if title:

                    titles[k] = title

            if titles:

                fields += [f"title={titles}"]

        for name, axis in self._axis_map.items():

            if axis.label and axis.label.get_text():

                fields += [f"{name}label={axis.label.get_text()!r}"]

        return f"<{self.__class__.__name__}: " + ", ".join(fields) + ">"



    def get_subplotspec(self):

        

        return self._subplotspec



    def set_subplotspec(self, subplotspec):

        

        self._subplotspec = subplotspec

        self._set_position(subplotspec.get_position(self.get_figure(root=False)))



    def get_gridspec(self):

        

        return self._subplotspec.get_gridspec() if self._subplotspec else None



    def get_window_extent(self, renderer=None):

        

        return self.bbox



    def _init_axis(self):

                                                                               

        self.xaxis = maxis.XAxis(self, clear=False)

        self.spines.bottom.register_axis(self.xaxis)

        self.spines.top.register_axis(self.xaxis)

        self.yaxis = maxis.YAxis(self, clear=False)

        self.spines.left.register_axis(self.yaxis)

        self.spines.right.register_axis(self.yaxis)



    def set_figure(self, fig):

                             

        super().set_figure(fig)



        self.bbox = mtransforms.TransformedBbox(self._position,

                                                fig.transSubfigure)

                                                      

        self.dataLim = mtransforms.Bbox.null()

        self._viewLim = mtransforms.Bbox.unit()

        self.transScale = mtransforms.TransformWrapper(

            mtransforms.IdentityTransform())



        self._set_lim_and_transforms()



    def _unstale_viewLim(self):

                                                                          

                                   

        need_scale = {

            name: any(ax._stale_viewlims[name]

                      for ax in self._shared_axes[name].get_siblings(self))

            for name in self._axis_names}

        if any(need_scale.values()):

            for name in need_scale:

                for ax in self._shared_axes[name].get_siblings(self):

                    ax._stale_viewlims[name] = False

            self.autoscale_view(**{f"scale{name}": scale

                                   for name, scale in need_scale.items()})



    @property

    def viewLim(self):

        

        self._unstale_viewLim()

        return self._viewLim



    def _request_autoscale_view(self, axis="all", tight=None):

        

        axis_names = _api.check_getitem(

            {**{k: [k] for k in self._axis_names}, "all": self._axis_names},

            axis=axis)

        for name in axis_names:

            self._stale_viewlims[name] = True

        if tight is not None:

            self._tight = tight



    def _set_lim_and_transforms(self):

        

        self.transAxes = mtransforms.BboxTransformTo(self.bbox)



                                                                   

                                                                      

                                  

        self.transScale = mtransforms.TransformWrapper(

            mtransforms.IdentityTransform())



                                                                      

                           

        self.transLimits = mtransforms.BboxTransformFrom(

            mtransforms.TransformedBbox(self._viewLim, self.transScale))



                                                                   

                                                                   

                                                                     

        self.transData = self.transScale + (self.transLimits + self.transAxes)



        self._xaxis_transform = mtransforms.blended_transform_factory(

            self.transData, self.transAxes)

        self._yaxis_transform = mtransforms.blended_transform_factory(

            self.transAxes, self.transData)



    def get_xaxis_transform(self, which='grid'):

        

        if which == 'grid':

            return self._xaxis_transform

        elif which == 'tick1':

                                                            

            return self.spines.bottom.get_spine_transform()

        elif which == 'tick2':

                                                         

            return self.spines.top.get_spine_transform()

        else:

            raise ValueError(f'unknown value for which: {which!r}')



    def get_xaxis_text1_transform(self, pad_points):

        

        labels_align = mpl.rcParams["xtick.alignment"]

        return (self.get_xaxis_transform(which='tick1') +

                mtransforms.ScaledTranslation(

                    0, -1 * pad_points / 72,

                    self.get_figure(root=False).dpi_scale_trans),

                "top", labels_align)



    def get_xaxis_text2_transform(self, pad_points):

        

        labels_align = mpl.rcParams["xtick.alignment"]

        return (self.get_xaxis_transform(which='tick2') +

                mtransforms.ScaledTranslation(

                    0, pad_points / 72,

                    self.get_figure(root=False).dpi_scale_trans),

                "bottom", labels_align)



    def get_yaxis_transform(self, which='grid'):

        

        if which == 'grid':

            return self._yaxis_transform

        elif which == 'tick1':

                                                            

            return self.spines.left.get_spine_transform()

        elif which == 'tick2':

                                                         

            return self.spines.right.get_spine_transform()

        else:

            raise ValueError(f'unknown value for which: {which!r}')



    def get_yaxis_text1_transform(self, pad_points):

        

        labels_align = mpl.rcParams["ytick.alignment"]

        return (self.get_yaxis_transform(which='tick1') +

                mtransforms.ScaledTranslation(

                    -1 * pad_points / 72, 0,

                    self.get_figure(root=False).dpi_scale_trans),

                labels_align, "right")



    def get_yaxis_text2_transform(self, pad_points):

        

        labels_align = mpl.rcParams["ytick.alignment"]

        return (self.get_yaxis_transform(which='tick2') +

                mtransforms.ScaledTranslation(

                    pad_points / 72, 0,

                    self.get_figure(root=False).dpi_scale_trans),

                labels_align, "left")



    def _update_transScale(self):

        self.transScale.set(

            mtransforms.blended_transform_factory(

                self.xaxis.get_transform(), self.yaxis.get_transform()))



    def get_position(self, original=False):

        

        if original:

            return self._originalPosition.frozen()

        else:

            locator = self.get_axes_locator()

            if not locator:

                self.apply_aspect()

            return self._position.frozen()



    def set_position(self, pos, which='both'):

        

        self._set_position(pos, which=which)

                                                                   

                                        

        self.set_in_layout(False)



    def _set_position(self, pos, which='both'):

        

        if not isinstance(pos, mtransforms.BboxBase):

            pos = mtransforms.Bbox.from_bounds(*pos)

        for ax in self._twinned_axes.get_siblings(self):

            if which in ('both', 'active'):

                ax._position.set(pos)

            if which in ('both', 'original'):

                ax._originalPosition.set(pos)

        self.stale = True



    def reset_position(self):

        

        for ax in self._twinned_axes.get_siblings(self):

            pos = ax.get_position(original=True)

            ax.set_position(pos, which='active')



    def set_axes_locator(self, locator):

        

        self._axes_locator = locator

        self.stale = True



    def get_axes_locator(self):

        

        return self._axes_locator



    def _set_artist_props(self, a):

        

        a.set_figure(self.get_figure(root=False))

        if not a.is_transform_set():

            a.set_transform(self.transData)



        a.axes = self

        if a.get_mouseover():

            self._mouseover_set.add(a)



    def _gen_axes_patch(self):

        

        return mpatches.Rectangle((0.0, 0.0), 1.0, 1.0)



    def _gen_axes_spines(self, locations=None, offset=0.0, units='inches'):

        

        return {side: mspines.Spine.linear_spine(self, side)

                for side in ['left', 'right', 'bottom', 'top']}



    def sharex(self, other):

        

        _api.check_isinstance(_AxesBase, other=other)

        if self._sharex is not None and other is not self._sharex:

            raise ValueError("x-axis is already shared")

        self._shared_axes["x"].join(self, other)

        self._sharex = other

        self.xaxis.major = other.xaxis.major                            

        self.xaxis.minor = other.xaxis.minor                          

        x0, x1 = other.get_xlim()

        self.set_xlim(x0, x1, emit=False, auto=other.get_autoscalex_on())

        self.xaxis._scale = other.xaxis._scale



    def sharey(self, other):

        

        _api.check_isinstance(_AxesBase, other=other)

        if self._sharey is not None and other is not self._sharey:

            raise ValueError("y-axis is already shared")

        self._shared_axes["y"].join(self, other)

        self._sharey = other

        self.yaxis.major = other.yaxis.major                            

        self.yaxis.minor = other.yaxis.minor                          

        y0, y1 = other.get_ylim()

        self.set_ylim(y0, y1, emit=False, auto=other.get_autoscaley_on())

        self.yaxis._scale = other.yaxis._scale



    def __clear(self):

        

                                                                           

                                                              

                                                                

                                                   



                                            

        if hasattr(self, 'patch'):

            patch_visible = self.patch.get_visible()

        else:

            patch_visible = True



        xaxis_visible = self.xaxis.get_visible()

        yaxis_visible = self.yaxis.get_visible()



        for axis in self._axis_map.values():

            axis.clear()                                    

        for spine in self.spines.values():

            spine._clear()                                      



        self.ignore_existing_data_limits = True

        self.callbacks = cbook.CallbackRegistry(

            signals=["xlim_changed", "ylim_changed", "zlim_changed"])



                                                                     

        if mpl.rcParams['xtick.minor.visible']:

            self.xaxis.set_minor_locator(mticker.AutoMinorLocator())

        if mpl.rcParams['ytick.minor.visible']:

            self.yaxis.set_minor_locator(mticker.AutoMinorLocator())



        self._xmargin = mpl.rcParams['axes.xmargin']

        self._ymargin = mpl.rcParams['axes.ymargin']

        self._tight = None

        self._use_sticky_edges = True



        self._get_lines = _process_plot_var_args()

        self._get_patches_for_fill = _process_plot_var_args('Polygon')



        self._gridOn = mpl.rcParams['axes.grid']

                                                                     

        old_children, self._children = self._children, []

        for chld in old_children:

            chld._remove_method = None

            chld._parent_figure = None

            chld.axes = None

                                                                             

        old_children.clear()

        self._mouseover_set = _OrderedSet()

        self.child_axes = []

        self._current_image = None                                      

        self._projection_init = None                               

        self.legend_ = None

        self.containers = []



        self.grid(False)                                           

        self.grid(self._gridOn, which=mpl.rcParams['axes.grid.which'],

                  axis=mpl.rcParams['axes.grid.axis'])

        props = font_manager.FontProperties(

            size=mpl.rcParams['axes.titlesize'],

            weight=mpl.rcParams['axes.titleweight'])



        y = mpl.rcParams['axes.titley']

        if y is None:

            y = 1.0

            self._autotitlepos = True

        else:

            self._autotitlepos = False



        self.title = mtext.Text(

            x=0.5, y=y, text='',

            fontproperties=props,

            verticalalignment='baseline',

            horizontalalignment='center',

            )

        self._left_title = mtext.Text(

            x=0.0, y=y, text='',

            fontproperties=props.copy(),

            verticalalignment='baseline',

            horizontalalignment='left', )

        self._right_title = mtext.Text(

            x=1.0, y=y, text='',

            fontproperties=props.copy(),

            verticalalignment='baseline',

            horizontalalignment='right',

            )

        title_offset_points = mpl.rcParams['axes.titlepad']

                                                                  

                              

        self._set_title_offset_trans(title_offset_points)



        for _title in (self.title, self._left_title, self._right_title):

            self._set_artist_props(_title)



                                                                               

                                                                          

                                        

        self.patch = self._gen_axes_patch()

        self.patch.set_figure(self.get_figure(root=False))

        self.patch.set_facecolor(self._facecolor)

        self.patch.set_edgecolor('none')

        self.patch.set_linewidth(0)

        self.patch.set_transform(self.transAxes)



        self.set_axis_on()



        self.xaxis.set_clip_path(self.patch)

        self.yaxis.set_clip_path(self.patch)



        if self._sharex is not None:

            self.xaxis.set_visible(xaxis_visible)

            self.patch.set_visible(patch_visible)

        if self._sharey is not None:

            self.yaxis.set_visible(yaxis_visible)

            self.patch.set_visible(patch_visible)



                                                                               

                                                                        

        for name, axis in self._axis_map.items():

            share = getattr(self, f"_share{name}")

            if share is not None:

                getattr(self, f"share{name}")(share)

            else:

                                                                        

                                                                

                if self.name == "polar":

                    axis._set_scale("linear")

                axis._set_lim(0, 1, auto=True)

        self._update_transScale()



        self.stale = True



    def clear(self):

        

                                                                               

                                  

        if self._subclass_uses_cla:

            self.cla()

        else:

            self.__clear()



    def cla(self):

        

                                                                               

                                  

        if self._subclass_uses_cla:

            self.__clear()

        else:

            self.clear()



    class ArtistList(Sequence):

        

        def __init__(self, axes, prop_name,

                     valid_types=None, invalid_types=None):

            

            self._axes = axes

            self._prop_name = prop_name

            self._type_check = lambda artist: (

                (not valid_types or isinstance(artist, valid_types)) and

                (not invalid_types or not isinstance(artist, invalid_types))

            )



        def __repr__(self):

            return f'<Axes.ArtistList of {len(self)} {self._prop_name}>'



        def __len__(self):

            return sum(self._type_check(artist)

                       for artist in self._axes._children)



        def __iter__(self):

            for artist in list(self._axes._children):

                if self._type_check(artist):

                    yield artist



        def __getitem__(self, key):

            return [artist

                    for artist in self._axes._children

                    if self._type_check(artist)][key]



        def __add__(self, other):

            if isinstance(other, (list, _AxesBase.ArtistList)):

                return [*self, *other]

            if isinstance(other, (tuple, _AxesBase.ArtistList)):

                return (*self, *other)

            return NotImplemented



        def __radd__(self, other):

            if isinstance(other, list):

                return other + list(self)

            if isinstance(other, tuple):

                return other + tuple(self)

            return NotImplemented



    @property

    def artists(self):

        return self.ArtistList(self, 'artists', invalid_types=(

            mcoll.Collection, mimage.AxesImage, mlines.Line2D, mpatches.Patch,

            mtable.Table, mtext.Text))



    @property

    def collections(self):

        return self.ArtistList(self, 'collections',

                               valid_types=mcoll.Collection)



    @property

    def images(self):

        return self.ArtistList(self, 'images', valid_types=mimage.AxesImage)



    @property

    def lines(self):

        return self.ArtistList(self, 'lines', valid_types=mlines.Line2D)



    @property

    def patches(self):

        return self.ArtistList(self, 'patches', valid_types=mpatches.Patch)



    @property

    def tables(self):

        return self.ArtistList(self, 'tables', valid_types=mtable.Table)



    @property

    def texts(self):

        return self.ArtistList(self, 'texts', valid_types=mtext.Text)



    def get_facecolor(self):

        

        return self.patch.get_facecolor()



    def set_facecolor(self, color):

        

        self._facecolor = color

        self.stale = True

        return self.patch.set_facecolor(color)



    def _set_title_offset_trans(self, title_offset_points):

        

        self.titleOffsetTrans = mtransforms.ScaledTranslation(

                0.0, title_offset_points / 72,

                self.get_figure(root=False).dpi_scale_trans)

        for _title in (self.title, self._left_title, self._right_title):

            _title.set_transform(self.transAxes + self.titleOffsetTrans)

            _title.set_clip_box(None)



    def set_prop_cycle(self, *args, **kwargs):

        

        if args and kwargs:

            raise TypeError("Cannot supply both positional and keyword "

                            "arguments to this method.")

                                                            

        if len(args) == 1 and args[0] is None:

            prop_cycle = None

        else:

            prop_cycle = cycler(*args, **kwargs)

        self._get_lines.set_prop_cycle(prop_cycle)

        self._get_patches_for_fill.set_prop_cycle(prop_cycle)



    def get_aspect(self):

        

        return self._aspect



    def set_aspect(self, aspect, adjustable=None, anchor=None, share=False):

        

        if cbook._str_equal(aspect, 'equal'):

            aspect = 1

        if not cbook._str_equal(aspect, 'auto'):

            aspect = float(aspect)                                 

            if aspect <= 0 or not np.isfinite(aspect):

                raise ValueError("aspect must be finite and positive ")



        if share:

            axes = {sibling for name in self._axis_names

                    for sibling in self._shared_axes[name].get_siblings(self)}

        else:

            axes = [self]



        for ax in axes:

            ax._aspect = aspect



        if adjustable is None:

            adjustable = self._adjustable

        self.set_adjustable(adjustable, share=share)                   



        if anchor is not None:

            self.set_anchor(anchor, share=share)

        self.stale = True



    def get_adjustable(self):

        

        return self._adjustable



    def set_adjustable(self, adjustable, share=False):

        

        _api.check_in_list(["box", "datalim"], adjustable=adjustable)

        if share:

            axs = {sibling for name in self._axis_names

                   for sibling in self._shared_axes[name].get_siblings(self)}

        else:

            axs = [self]

        if (adjustable == "datalim"

                and any(getattr(ax.get_data_ratio, "__func__", None)

                        != _AxesBase.get_data_ratio

                        for ax in axs)):

                                                                             

                                                                    

            raise ValueError("Cannot set Axes adjustable to 'datalim' for "

                             "Axes which override 'get_data_ratio'")

        for ax in axs:

            ax._adjustable = adjustable

        self.stale = True



    def get_box_aspect(self):

        

        return self._box_aspect



    def set_box_aspect(self, aspect=None):

        

        axs = {*self._twinned_axes.get_siblings(self),

               *self._twinned_axes.get_siblings(self)}



        if aspect is not None:

            aspect = float(aspect)

                                                          

                                          

            for ax in axs:

                ax.set_adjustable("datalim")



        for ax in axs:

            ax._box_aspect = aspect

            ax.stale = True



    def get_anchor(self):

        

        return self._anchor



    def set_anchor(self, anchor, share=False):

        

        if not (anchor in mtransforms.Bbox.coefs or len(anchor) == 2):

            raise ValueError('argument must be among %s' %

                             ', '.join(mtransforms.Bbox.coefs))

        if share:

            axes = {sibling for name in self._axis_names

                    for sibling in self._shared_axes[name].get_siblings(self)}

        else:

            axes = [self]

        for ax in axes:

            ax._anchor = anchor



        self.stale = True



    def get_data_ratio(self):

        

        txmin, txmax = self.xaxis.get_transform().transform(self.get_xbound())

        tymin, tymax = self.yaxis.get_transform().transform(self.get_ybound())

        xsize = max(abs(txmax - txmin), 1e-30)

        ysize = max(abs(tymax - tymin), 1e-30)

        return ysize / xsize



    def apply_aspect(self, position=None):

        

        if position is None:

            position = self.get_position(original=True)



        aspect = self.get_aspect()



        if aspect == 'auto' and self._box_aspect is None:

            self._set_position(position, which='active')

            return



        trans = self.get_figure(root=False).transSubfigure

        bb = mtransforms.Bbox.unit().transformed(trans)

                                                               

        fig_aspect = bb.height / bb.width



        if self._adjustable == 'box':

            if self in self._twinned_axes:

                raise RuntimeError("Adjustable 'box' is not allowed in a "

                                   "twinned Axes; use 'datalim' instead")

            box_aspect = aspect * self.get_data_ratio()

            pb = position.frozen()

            pb1 = pb.shrunk_to_aspect(box_aspect, pb, fig_aspect)

            self._set_position(pb1.anchored(self.get_anchor(), pb), 'active')

            return



                                                                     

        if self._box_aspect is not None:

            pb = position.frozen()

            pb1 = pb.shrunk_to_aspect(self._box_aspect, pb, fig_aspect)

            self._set_position(pb1.anchored(self.get_anchor(), pb), 'active')

            if aspect == "auto":

                return



                                                                           

                  

        if self._box_aspect is None:

            self._set_position(position, which='active')

        else:

            position = pb1.anchored(self.get_anchor(), pb)



        x_trf = self.xaxis.get_transform()

        y_trf = self.yaxis.get_transform()

        xmin, xmax = x_trf.transform(self.get_xbound())

        ymin, ymax = y_trf.transform(self.get_ybound())

        xsize = max(abs(xmax - xmin), 1e-30)

        ysize = max(abs(ymax - ymin), 1e-30)



        box_aspect = fig_aspect * (position.height / position.width)

        data_ratio = box_aspect / aspect



        y_expander = data_ratio * xsize / ysize - 1

                                                                      

        if abs(y_expander) < 0.005:

            return



        dL = self.dataLim

        x0, x1 = x_trf.transform(dL.intervalx)

        y0, y1 = y_trf.transform(dL.intervaly)

        xr = 1.05 * (x1 - x0)

        yr = 1.05 * (y1 - y0)



        xmarg = xsize - xr

        ymarg = ysize - yr

        Ysize = data_ratio * xsize

        Xsize = ysize / data_ratio

        Xmarg = Xsize - xr

        Ymarg = Ysize - yr

                                                                        

        xm = 0

        ym = 0



        shared_x = self in self._shared_axes["x"]

        shared_y = self in self._shared_axes["y"]



        if shared_x and shared_y:

            raise RuntimeError("set_aspect(..., adjustable='datalim') or "

                               "axis('equal') are not allowed when both axes "

                               "are shared.  Try set_aspect(..., "

                               "adjustable='box').")



                                                                    

        if shared_y:

            adjust_y = False

        else:

            if xmarg > xm and ymarg > ym:

                adjy = ((Ymarg > 0 and y_expander < 0) or

                        (Xmarg < 0 and y_expander > 0))

            else:

                adjy = y_expander > 0

            adjust_y = shared_x or adjy                   



        if adjust_y:

            yc = 0.5 * (ymin + ymax)

            y0 = yc - Ysize / 2.0

            y1 = yc + Ysize / 2.0

            if not self.get_autoscaley_on():

                _log.warning("Ignoring fixed y limits to fulfill fixed data aspect "

                             "with adjustable data limits.")

            self.set_ybound(y_trf.inverted().transform([y0, y1]))

        else:

            xc = 0.5 * (xmin + xmax)

            x0 = xc - Xsize / 2.0

            x1 = xc + Xsize / 2.0

            if not self.get_autoscalex_on():

                _log.warning("Ignoring fixed x limits to fulfill fixed data aspect "

                             "with adjustable data limits.")

            self.set_xbound(x_trf.inverted().transform([x0, x1]))



    def axis(self, arg=None, /, *, emit=True, **kwargs):

        

        if isinstance(arg, (str, bool)):

            if arg is True:

                arg = 'on'

            if arg is False:

                arg = 'off'

            arg = arg.lower()

            if arg == 'on':

                self.set_axis_on()

            elif arg == 'off':

                self.set_axis_off()

            elif arg in [

                    'equal', 'tight', 'scaled', 'auto', 'image', 'square']:

                self.set_autoscale_on(True)

                self.set_aspect('auto')

                self.autoscale_view(tight=False)

                if arg == 'equal':

                    self.set_aspect('equal', adjustable='datalim')

                elif arg == 'scaled':

                    self.set_aspect('equal', adjustable='box', anchor='C')

                    self.set_autoscale_on(False)                       

                elif arg == 'tight':

                    self.autoscale_view(tight=True)

                    self.set_autoscale_on(False)

                elif arg == 'image':

                    self.autoscale_view(tight=True)

                    self.set_autoscale_on(False)

                    self.set_aspect('equal', adjustable='box', anchor='C')

                elif arg == 'square':

                    self.set_aspect('equal', adjustable='box', anchor='C')

                    self.set_autoscale_on(False)

                    xlim = self.get_xlim()

                    ylim = self.get_ylim()

                    edge_size = max(np.diff(xlim), np.diff(ylim))[0]

                    self.set_xlim(xlim[0], xlim[0] + edge_size,

                                  emit=emit, auto=False)

                    self.set_ylim(ylim[0], ylim[0] + edge_size,

                                  emit=emit, auto=False)

            else:

                raise ValueError(f"Unrecognized string {arg!r} to axis; "

                                 "try 'on' or 'off'")

        else:

            if arg is not None:

                if len(arg) != 2*len(self._axis_names):

                    raise TypeError(

                        "The first argument to axis() must be an iterable of the form "

                        "[{}]".format(", ".join(

                            f"{name}min, {name}max" for name in self._axis_names)))

                limits = {

                    name: arg[2*i:2*(i+1)]

                    for i, name in enumerate(self._axis_names)

                }

            else:

                limits = {}

                for name in self._axis_names:

                    ax_min = kwargs.pop(f'{name}min', None)

                    ax_max = kwargs.pop(f'{name}max', None)

                    limits[name] = (ax_min, ax_max)

            for name, (ax_min, ax_max) in limits.items():

                ax_auto = (None                               

                           if ax_min is None and ax_max is None

                           else False)                       

                set_ax_lim = getattr(self, f'set_{name}lim')

                set_ax_lim(ax_min, ax_max, emit=emit, auto=ax_auto)

        if kwargs:

            raise _api.kwarg_error("axis", kwargs)

        lims = ()

        for name in self._axis_names:

            get_ax_lim = getattr(self, f'get_{name}lim')

            lims += get_ax_lim()

        return lims



    def get_legend(self):

        

        return self.legend_



    def get_images(self):

        

        return cbook.silent_list('AxesImage', self.images)



    def get_lines(self):

        

        return cbook.silent_list('Line2D', self.lines)



    def get_xaxis(self):

        

        return self.xaxis



    def get_yaxis(self):

        

        return self.yaxis



    get_xgridlines = _axis_method_wrapper("xaxis", "get_gridlines")

    get_xticklines = _axis_method_wrapper("xaxis", "get_ticklines")

    get_ygridlines = _axis_method_wrapper("yaxis", "get_gridlines")

    get_yticklines = _axis_method_wrapper("yaxis", "get_ticklines")



                                 



    def _sci(self, im):

        

        _api.check_isinstance((mcoll.Collection, mimage.AxesImage), im=im)

        if im not in self._children:

            raise ValueError("Argument must be an image or collection in this Axes")

        self._current_image = im



    def _gci(self):

        

        return self._current_image



    def has_data(self):

        

        return any(isinstance(a, (mcoll.Collection, mimage.AxesImage,

                                  mlines.Line2D, mpatches.Patch))

                   for a in self._children)



    def add_artist(self, a):

        

        a.axes = self

        self._children.append(a)

        a._remove_method = self._children.remove

        self._set_artist_props(a)

        if a.get_clip_path() is None:

            a.set_clip_path(self.patch)

        self.stale = True

        return a



    def add_child_axes(self, ax):

        



                                                                           

                         

                                      

        ax._axes = self

        ax.stale_callback = martist._stale_axes_callback



        self.child_axes.append(ax)

        ax._remove_method = functools.partial(

            self.get_figure(root=False)._remove_axes, owners=[self.child_axes])

        self.stale = True

        return ax



    def add_collection(self, collection, autolim=True):

        

        _api.check_isinstance(mcoll.Collection, collection=collection)

        if not collection.get_label():

            collection.set_label(f'_child{len(self._children)}')

        self._children.append(collection)

        collection._remove_method = self._children.remove

        self._set_artist_props(collection)



        if collection.get_clip_path() is None:

            collection.set_clip_path(self.patch)



        if autolim:

                                                             

                                                                       

            self._unstale_viewLim()

            datalim = collection.get_datalim(self.transData)

            points = datalim.get_points()

            if not np.isinf(datalim.minpos).all():

                                                                          

                                                                             

                                                                            

                                                                           

                                                                       

                points = np.concatenate([points, [datalim.minpos]])

                                                                              

                                

            x_is_data, y_is_data = (collection.get_transform()

                                    .contains_branch_seperately(self.transData))

            ox_is_data, oy_is_data = (collection.get_offset_transform()

                                      .contains_branch_seperately(self.transData))

            self.update_datalim(

                points,

                updatex=x_is_data or ox_is_data,

                updatey=y_is_data or oy_is_data,

            )

            if autolim != "_datalim_only":

                self._request_autoscale_view()



        self.stale = True

        return collection



    def add_image(self, image):

        

        _api.check_isinstance(mimage.AxesImage, image=image)

        self._set_artist_props(image)

        if not image.get_label():

            image.set_label(f'_child{len(self._children)}')

        self._children.append(image)

        image._remove_method = self._children.remove

        self.stale = True

        return image



    def _update_image_limits(self, image):

        xmin, xmax, ymin, ymax = image.get_extent()

        self.axes.update_datalim(((xmin, ymin), (xmax, ymax)))



    def add_line(self, line):

        

        _api.check_isinstance(mlines.Line2D, line=line)

        self._set_artist_props(line)

        if line.get_clip_path() is None:

            line.set_clip_path(self.patch)



        self._update_line_limits(line)

        if not line.get_label():

            line.set_label(f'_child{len(self._children)}')

        self._children.append(line)

        line._remove_method = self._children.remove

        self.stale = True

        return line



    def _add_text(self, txt):

        

        _api.check_isinstance(mtext.Text, txt=txt)

        self._set_artist_props(txt)

        self._children.append(txt)

        txt._remove_method = self._children.remove

        self.stale = True

        return txt



    def _update_line_limits(self, line):

        

        path = line.get_path()

        if path.vertices.size == 0:

            return



        line_trf = line.get_transform()



        if line_trf == self.transData:

            data_path = path

        elif any(line_trf.contains_branch_seperately(self.transData)):

                                                                              

            trf_to_data = line_trf - self.transData

                                                                               

                                                                      

                                                    

            if self.transData.is_affine:

                line_trans_path = line._get_transformed_path()

                na_path, _ = line_trans_path.get_transformed_path_and_affine()

                data_path = trf_to_data.transform_path_affine(na_path)

            else:

                data_path = trf_to_data.transform_path(path)

        else:

                                                                        

                                                                            

                                                                            

                                                                      

                          

            data_path = path



        if not data_path.vertices.size:

            return



        updatex, updatey = line_trf.contains_branch_seperately(self.transData)

        if self.name != "rectilinear":

                                                                             

                                                        

            if updatex and line_trf == self.get_yaxis_transform():

                updatex = False

            if updatey and line_trf == self.get_xaxis_transform():

                updatey = False

        self.dataLim.update_from_path(data_path,

                                      self.ignore_existing_data_limits,

                                      updatex=updatex, updatey=updatey)

        self.ignore_existing_data_limits = False



    def add_patch(self, p):

        

        _api.check_isinstance(mpatches.Patch, p=p)

        self._set_artist_props(p)

        if p.get_clip_path() is None:

            p.set_clip_path(self.patch)

        self._update_patch_limits(p)

        self._children.append(p)

        p._remove_method = self._children.remove

        return p



    def _update_patch_limits(self, patch):

        

                                                                      

                                                                      

                                                                   

                          



                                                                            

                                                                        

                    

        if (isinstance(patch, mpatches.Rectangle) and

                ((not patch.get_width()) and (not patch.get_height()))):

            return

        p = patch.get_path()

                                      

                                                                            

        vertices = []

        for curve, code in p.iter_bezier(simplify=False):

                                                         

            _, dzeros = curve.axis_aligned_extrema()

                                                                         

            vertices.append(curve([0, *dzeros, 1]))



        if len(vertices):

            vertices = np.vstack(vertices)



        patch_trf = patch.get_transform()

        updatex, updatey = patch_trf.contains_branch_seperately(self.transData)

        if not (updatex or updatey):

            return

        if self.name != "rectilinear":

                                                         

            if updatex and patch_trf == self.get_yaxis_transform():

                updatex = False

            if updatey and patch_trf == self.get_xaxis_transform():

                updatey = False

        trf_to_data = patch_trf - self.transData

        xys = trf_to_data.transform(vertices)

        self.update_datalim(xys, updatex=updatex, updatey=updatey)



    def add_table(self, tab):

        

        _api.check_isinstance(mtable.Table, tab=tab)

        self._set_artist_props(tab)

        self._children.append(tab)

        if tab.get_clip_path() is None:

            tab.set_clip_path(self.patch)

        tab._remove_method = self._children.remove

        return tab



    def add_container(self, container):

        

        label = container.get_label()

        if not label:

            container.set_label('_container%d' % len(self.containers))

        self.containers.append(container)

        container._remove_method = self.containers.remove

        return container



    def _unit_change_handler(self, axis_name, event=None):

        

        if event is None:                                                      

            return functools.partial(

                self._unit_change_handler, axis_name, event=object())

        _api.check_in_list(self._axis_map, axis_name=axis_name)

        for line in self.lines:

            line.recache_always()

        self.relim()

        self._request_autoscale_view(axis_name)



    def relim(self, visible_only=False):

        

                                                               

                                      

        self.dataLim.ignore(True)

        self.dataLim.set_points(mtransforms.Bbox.null().get_points())

        self.ignore_existing_data_limits = True



        for artist in self._children:

            if not visible_only or artist.get_visible():

                if isinstance(artist, mlines.Line2D):

                    self._update_line_limits(artist)

                elif isinstance(artist, mpatches.Patch):

                    self._update_patch_limits(artist)

                elif isinstance(artist, mimage.AxesImage):

                    self._update_image_limits(artist)



    def update_datalim(self, xys, updatex=True, updatey=True):

        

        xys = np.asarray(xys)

        if not np.any(np.isfinite(xys)):

            return

        self.dataLim.update_from_data_xy(xys, self.ignore_existing_data_limits,

                                         updatex=updatex, updatey=updatey)

        self.ignore_existing_data_limits = False



    def _process_unit_info(self, datasets=None, kwargs=None, *, convert=True):

        

                                                                            

                                                                               

                                                                          

                                           

        datasets = datasets or []

        kwargs = kwargs or {}

        axis_map = self._axis_map

        for axis_name, data in datasets:

            try:

                axis = axis_map[axis_name]

            except KeyError:

                raise ValueError(f"Invalid axis name: {axis_name!r}") from None

                                                                             

            if axis is not None and data is not None and not axis.have_units():

                axis.update_units(data)

        for axis_name, axis in axis_map.items():

                                       

            if axis is None:

                continue

                                                                        

            units = kwargs.pop(f"{axis_name}units", axis.units)

            if self.name == "polar":

                                                                     

                polar_units = {"x": "thetaunits", "y": "runits"}

                units = kwargs.pop(polar_units[axis_name], units)

            if units != axis.units and units is not None:

                axis.set_units(units)

                                                                     

                                          

                for dataset_axis_name, data in datasets:

                    if dataset_axis_name == axis_name and data is not None:

                        axis.update_units(data)

        return [axis_map[axis_name].convert_units(data)

                if convert and data is not None else data

                for axis_name, data in datasets]



    def in_axes(self, mouseevent):

        

        return self.patch.contains(mouseevent)[0]



    get_autoscalex_on = _axis_method_wrapper("xaxis", "_get_autoscale_on")

    get_autoscaley_on = _axis_method_wrapper("yaxis", "_get_autoscale_on")

    set_autoscalex_on = _axis_method_wrapper("xaxis", "_set_autoscale_on")

    set_autoscaley_on = _axis_method_wrapper("yaxis", "_set_autoscale_on")



    def get_autoscale_on(self):

        

        return all(axis._get_autoscale_on()

                   for axis in self._axis_map.values())



    def set_autoscale_on(self, b):

        

        for axis in self._axis_map.values():

            axis._set_autoscale_on(b)



    @property

    def use_sticky_edges(self):

        

        return self._use_sticky_edges



    @use_sticky_edges.setter

    def use_sticky_edges(self, b):

        self._use_sticky_edges = bool(b)

                                                                              



    def get_xmargin(self):

        

        return self._xmargin



    def get_ymargin(self):

        

        return self._ymargin



    def set_xmargin(self, m):

        

        if m <= -0.5:

            raise ValueError("margin must be greater than -0.5")

        self._xmargin = m

        self._request_autoscale_view("x")

        self.stale = True



    def set_ymargin(self, m):

        

        if m <= -0.5:

            raise ValueError("margin must be greater than -0.5")

        self._ymargin = m

        self._request_autoscale_view("y")

        self.stale = True



    def margins(self, *margins, x=None, y=None, tight=True):

        



        if margins and (x is not None or y is not None):

            raise TypeError('Cannot pass both positional and keyword '

                            'arguments for x and/or y.')

        elif len(margins) == 1:

            x = y = margins[0]

        elif len(margins) == 2:

            x, y = margins

        elif margins:

            raise TypeError('Must pass a single positional argument for all '

                            'margins, or one for each margin (x, y).')



        if x is None and y is None:

            if tight is not True:

                _api.warn_external(f'ignoring tight={tight!r} in get mode')

            return self._xmargin, self._ymargin



        if tight is not None:

            self._tight = tight

        if x is not None:

            self.set_xmargin(x)

        if y is not None:

            self.set_ymargin(y)



    def set_rasterization_zorder(self, z):

        

        self._rasterization_zorder = z

        self.stale = True



    def get_rasterization_zorder(self):

        

        return self._rasterization_zorder



    def autoscale(self, enable=True, axis='both', tight=None):

        

        if enable is None:

            scalex = True

            scaley = True

        else:

            if axis in ['x', 'both']:

                self.set_autoscalex_on(bool(enable))

                scalex = self.get_autoscalex_on()

            else:

                scalex = False

            if axis in ['y', 'both']:

                self.set_autoscaley_on(bool(enable))

                scaley = self.get_autoscaley_on()

            else:

                scaley = False

        if tight and scalex:

            self._xmargin = 0

        if tight and scaley:

            self._ymargin = 0

        if scalex:

            self._request_autoscale_view("x", tight=tight)

        if scaley:

            self._request_autoscale_view("y", tight=tight)



    def autoscale_view(self, tight=None, scalex=True, scaley=True):

        

        if tight is not None:

            self._tight = bool(tight)



        x_stickies = y_stickies = np.array([])

        if self.use_sticky_edges:

            if self._xmargin and scalex and self.get_autoscalex_on():

                x_stickies = np.sort(np.concatenate([

                    artist.sticky_edges.x

                    for ax in self._shared_axes["x"].get_siblings(self)

                    for artist in ax.get_children()]))

            if self._ymargin and scaley and self.get_autoscaley_on():

                y_stickies = np.sort(np.concatenate([

                    artist.sticky_edges.y

                    for ax in self._shared_axes["y"].get_siblings(self)

                    for artist in ax.get_children()]))

        if self.get_xscale() == 'log':

            x_stickies = x_stickies[x_stickies > 0]

        if self.get_yscale() == 'log':

            y_stickies = y_stickies[y_stickies > 0]



        def handle_single_axis(

                scale, shared_axes, name, axis, margin, stickies, set_bound):



            if not (scale and axis._get_autoscale_on()):

                return                    



            shared = shared_axes.get_siblings(self)

                                                                               

                                                                        

            values = [val for ax in shared

                      for val in getattr(ax.dataLim, f"interval{name}")

                      if np.isfinite(val)]

            if values:

                x0, x1 = (min(values), max(values))

            elif getattr(self._viewLim, f"mutated{name}")():

                                                             

                                          

                return

            else:

                x0, x1 = (-np.inf, np.inf)

                                                                              

            locator = axis.get_major_locator()

            x0, x1 = locator.nonsingular(x0, x1)

                                                                        

            minimum_minpos = min(

                getattr(ax.dataLim, f"minpos{name}") for ax in shared)



                                                                            

                                                                       

                                                                 

                                                                               

                                                                  

            tol = 1e-5 * abs(x1 - x0)

                                                          

            i0 = stickies.searchsorted(x0 + tol) - 1

            x0bound = stickies[i0] if i0 != -1 else None

                                                           

            i1 = stickies.searchsorted(x1 - tol)

            x1bound = stickies[i1] if i1 != len(stickies) else None



                                                                               

                                

            transform = axis.get_transform()

            inverse_trans = transform.inverted()

            x0, x1 = axis._scale.limit_range_for_scale(x0, x1, minimum_minpos)

            x0t, x1t = transform.transform([x0, x1])

            delta = (x1t - x0t) * margin

            if not np.isfinite(delta):

                delta = 0                                                

            x0, x1 = inverse_trans.transform([x0t - delta, x1t + delta])



                                  

            if x0bound is not None:

                x0 = max(x0, x0bound)

            if x1bound is not None:

                x1 = min(x1, x1bound)



            if not self._tight:

                x0, x1 = locator.view_limits(x0, x1)

            set_bound(x0, x1)

                                                                          



        handle_single_axis(

            scalex, self._shared_axes["x"], 'x', self.xaxis, self._xmargin,

            x_stickies, self.set_xbound)

        handle_single_axis(

            scaley, self._shared_axes["y"], 'y', self.yaxis, self._ymargin,

            y_stickies, self.set_ybound)



    def _update_title_position(self, renderer):

        

        if self._autotitlepos is not None and not self._autotitlepos:

            _log.debug('title position was updated manually, not adjusting')

            return



        titles = (self.title, self._left_title, self._right_title)



        if not any(title.get_text() for title in titles):

                                                                                      

            return



                                                                             

                  

        axs = set()

        axs.update(self.child_axes)

        axs.update(self._twinned_axes.get_siblings(self))

        axs.update(

            self.get_figure(root=False)._align_label_groups['title'].get_siblings(self))



        for ax in self.child_axes:                                          

            locator = ax.get_axes_locator()

            ax.apply_aspect(locator(self, renderer) if locator else None)



        top = -np.inf

        for ax in axs:

            bb = None

            if (ax.xaxis.get_ticks_position() in ['top', 'unknown'] or

                    ax.xaxis.get_label_position() == 'top'):

                bb = ax.xaxis.get_tightbbox(renderer)

            if bb is None:

                                                                             

                bb = ax.spines.get("outline", ax).get_window_extent()

            top = max(top, bb.ymax)



        for title in titles:

            x, _ = title.get_position()

                                                            

            title.set_position((x, 1.0))

            if title.get_text():

                for ax in axs:

                    ax.yaxis.get_tightbbox(renderer)                     

                    if ax.yaxis.offsetText.get_text():

                        bb = ax.yaxis.offsetText.get_tightbbox(renderer)

                        if bb.intersection(title.get_tightbbox(renderer), bb):

                            top = bb.ymax

            if top < 0:

                                                                             

                                         

                _log.debug('top of Axes not in the figure, so title not moved')

                return

            if title.get_window_extent(renderer).ymin < top:

                _, y = self.transAxes.inverted().transform((0, top))

                title.set_position((x, y))

                                                                      

                                             

                if title.get_window_extent(renderer).ymin < top:

                    _, y = self.transAxes.inverted().transform(

                        (0., 2 * top - title.get_window_extent(renderer).ymin))

                    title.set_position((x, y))



        ymax = max(title.get_position()[1] for title in titles)

        for title in titles:

                                                                 

            x, _ = title.get_position()

            title.set_position((x, ymax))



             

    @martist.allow_rasterization

    def draw(self, renderer):

                             

        if renderer is None:

            raise RuntimeError('No renderer defined')

        if not self.get_visible():

            return

        self._unstale_viewLim()



        renderer.open_group('axes', gid=self.get_gid())



                                                               

        self._stale = True



                                          

        locator = self.get_axes_locator()

        self.apply_aspect(locator(self, renderer) if locator else None)



        artists = self.get_children()

        artists.remove(self.patch)



                                                               

                                                                      

                                                                  

                                                                       

        if not (self.axison and self._frameon):

            for spine in self.spines.values():

                artists.remove(spine)



        self._update_title_position(renderer)



        if not self.axison:

            for _axis in self._axis_map.values():

                artists.remove(_axis)



        if not self.get_figure(root=True).canvas.is_saving():

            artists = [

                a for a in artists

                if not a.get_animated() or isinstance(a, mimage.AxesImage)]

        artists = sorted(artists, key=attrgetter('zorder'))



                                                

                                                                

        rasterization_zorder = self._rasterization_zorder



        if (rasterization_zorder is not None and

                artists and artists[0].zorder < rasterization_zorder):

            split_index = np.searchsorted(

                [art.zorder for art in artists],

                rasterization_zorder, side='right'

            )

            artists_rasterized = artists[:split_index]

            artists = artists[split_index:]

        else:

            artists_rasterized = []



        if self.axison and self._frameon:

            if artists_rasterized:

                artists_rasterized = [self.patch] + artists_rasterized

            else:

                artists = [self.patch] + artists



        if artists_rasterized:

            _draw_rasterized(self.get_figure(root=True), artists_rasterized, renderer)



        mimage._draw_list_compositing_images(

            renderer, self, artists, self.get_figure(root=True).suppressComposite)



        renderer.close_group('axes')

        self.stale = False



    def draw_artist(self, a):

        

        a.draw(self.get_figure(root=True).canvas.get_renderer())



    def redraw_in_frame(self):

        

        with ExitStack() as stack:

            for artist in [*self._axis_map.values(),

                           self.title, self._left_title, self._right_title]:

                stack.enter_context(artist._cm_set(visible=False))

            self.draw(self.get_figure(root=True).canvas.get_renderer())



                                    



    def get_frame_on(self):

        

        return self._frameon



    def set_frame_on(self, b):

        

        self._frameon = b

        self.stale = True



    def get_axisbelow(self):

        

        return self._axisbelow



    def set_axisbelow(self, b):

        

                                               

        self._axisbelow = axisbelow = validate_axisbelow(b)

        zorder = {

            True: 0.5,

            'line': 1.5,

            False: 2.5,

        }[axisbelow]

        for axis in self._axis_map.values():

            axis.set_zorder(zorder)

        self.stale = True



    @_docstring.interpd

    def grid(self, visible=None, which='major', axis='both', **kwargs):

        

        _api.check_in_list(['x', 'y', 'both'], axis=axis)

        if axis in ['x', 'both']:

            self.xaxis.grid(visible, which=which, **kwargs)

        if axis in ['y', 'both']:

            self.yaxis.grid(visible, which=which, **kwargs)



    def ticklabel_format(self, *, axis='both', style=None, scilimits=None,

                         useOffset=None, useLocale=None, useMathText=None):

        

        if isinstance(style, str):

            style = style.lower()

        axis = axis.lower()

        if scilimits is not None:

            try:

                m, n = scilimits

                m + n + 1                               

            except (ValueError, TypeError) as err:

                raise ValueError("scilimits must be a sequence of 2 integers"

                                 ) from err

        STYLES = {'sci': True, 'scientific': True, 'plain': False, '': None, None: None}

                                                                

        is_sci_style = _api.check_getitem(STYLES, style=style)

        axis_map = {**{k: [v] for k, v in self._axis_map.items()},

                    'both': list(self._axis_map.values())}

        axises = _api.check_getitem(axis_map, axis=axis)

        try:

            for axis in axises:

                if is_sci_style is not None:

                    axis.major.formatter.set_scientific(is_sci_style)

                if scilimits is not None:

                    axis.major.formatter.set_powerlimits(scilimits)

                if useOffset is not None:

                    axis.major.formatter.set_useOffset(useOffset)

                if useLocale is not None:

                    axis.major.formatter.set_useLocale(useLocale)

                if useMathText is not None:

                    axis.major.formatter.set_useMathText(useMathText)

        except AttributeError as err:

            raise AttributeError(

                "This method only works with the ScalarFormatter") from err



    def locator_params(self, axis='both', tight=None, **kwargs):

        

        _api.check_in_list([*self._axis_names, "both"], axis=axis)

        for name in self._axis_names:

            if axis in [name, "both"]:

                loc = self._axis_map[name].get_major_locator()

                loc.set_params(**kwargs)

                self._request_autoscale_view(name, tight=tight)

        self.stale = True



    def tick_params(self, axis='both', **kwargs):

        

        _api.check_in_list(['x', 'y', 'both'], axis=axis)

        if axis in ['x', 'both']:

            xkw = dict(kwargs)

            xkw.pop('left', None)

            xkw.pop('right', None)

            xkw.pop('labelleft', None)

            xkw.pop('labelright', None)

            self.xaxis.set_tick_params(**xkw)

        if axis in ['y', 'both']:

            ykw = dict(kwargs)

            ykw.pop('top', None)

            ykw.pop('bottom', None)

            ykw.pop('labeltop', None)

            ykw.pop('labelbottom', None)

            self.yaxis.set_tick_params(**ykw)



    def set_axis_off(self):

        

        self.axison = False

        self.stale = True



    def set_axis_on(self):

        

        self.axison = True

        self.stale = True



                                                     



    def get_xlabel(self):

        

        label = self.xaxis.label

        return label.get_text()



    def set_xlabel(self, xlabel, fontdict=None, labelpad=None, *,

                   loc=None, **kwargs):

        

        if labelpad is not None:

            self.xaxis.labelpad = labelpad

        protected_kw = ['x', 'horizontalalignment', 'ha']

        if {*kwargs} & {*protected_kw}:

            if loc is not None:

                raise TypeError(f"Specifying 'loc' is disallowed when any of "

                                f"its corresponding low level keyword "

                                f"arguments ({protected_kw}) are also "

                                f"supplied")



        else:

            loc = mpl._val_or_rc(loc, 'xaxis.labellocation')

            _api.check_in_list(('left', 'center', 'right'), loc=loc)



            x = {

                'left': 0,

                'center': 0.5,

                'right': 1,

            }[loc]

            kwargs.update(x=x, horizontalalignment=loc)



        return self.xaxis.set_label_text(xlabel, fontdict, **kwargs)



    def invert_xaxis(self):

        

        self.xaxis.set_inverted(not self.xaxis.get_inverted())



    set_xinverted = _axis_method_wrapper("xaxis", "set_inverted")

    get_xinverted = _axis_method_wrapper("xaxis", "get_inverted")

    xaxis_inverted = _axis_method_wrapper("xaxis", "get_inverted")

    if xaxis_inverted.__doc__:

        xaxis_inverted.__doc__ = ("[*Discouraged*] " + xaxis_inverted.__doc__ +

                                  textwrap.dedent("""

        .. admonition:: Discouraged

            The use of this method is discouraged.
            Use `.Axes.get_xinverted` instead.
        """))



    def get_xbound(self):

        

        left, right = self.get_xlim()

        if left < right:

            return left, right

        else:

            return right, left



    def set_xbound(self, lower=None, upper=None):

        

        if upper is None and np.iterable(lower):

            lower, upper = lower



        old_lower, old_upper = self.get_xbound()

        if lower is None:

            lower = old_lower

        if upper is None:

            upper = old_upper



        self.set_xlim(sorted((lower, upper),

                             reverse=bool(self.xaxis_inverted())),

                      auto=None)



    def get_xlim(self):

        

        return tuple(self.viewLim.intervalx)



    def _validate_converted_limits(self, limit, convert):

        

        if limit is not None:

            converted_limit = convert(limit)

            if isinstance(converted_limit, np.ndarray):

                converted_limit = converted_limit.squeeze()

            if (isinstance(converted_limit, Real)

                    and not np.isfinite(converted_limit)):

                raise ValueError("Axis limits cannot be NaN or Inf")

            return converted_limit



    def set_xlim(self, left=None, right=None, *, emit=True, auto=False,

                 xmin=None, xmax=None):

        

        if right is None and np.iterable(left):

            left, right = left

        if xmin is not None:

            if left is not None:

                raise TypeError("Cannot pass both 'left' and 'xmin'")

            left = xmin

        if xmax is not None:

            if right is not None:

                raise TypeError("Cannot pass both 'right' and 'xmax'")

            right = xmax

        return self.xaxis._set_lim(left, right, emit=emit, auto=auto)



    get_xscale = _axis_method_wrapper("xaxis", "get_scale")

    set_xscale = _axis_method_wrapper("xaxis", "_set_axes_scale")

    get_xticks = _axis_method_wrapper("xaxis", "get_ticklocs")

    set_xticks = _axis_method_wrapper("xaxis", "set_ticks",

                                      doc_sub={'set_ticks': 'set_xticks'})

    get_xmajorticklabels = _axis_method_wrapper("xaxis", "get_majorticklabels")

    get_xminorticklabels = _axis_method_wrapper("xaxis", "get_minorticklabels")

    get_xticklabels = _axis_method_wrapper("xaxis", "get_ticklabels")

    set_xticklabels = _axis_method_wrapper(

        "xaxis", "set_ticklabels",

        doc_sub={"Axis.set_ticks": "Axes.set_xticks"})



    def get_ylabel(self):

        

        label = self.yaxis.label

        return label.get_text()



    def set_ylabel(self, ylabel, fontdict=None, labelpad=None, *,

                   loc=None, **kwargs):

        

        if labelpad is not None:

            self.yaxis.labelpad = labelpad

        protected_kw = ['y', 'horizontalalignment', 'ha']

        if {*kwargs} & {*protected_kw}:

            if loc is not None:

                raise TypeError(f"Specifying 'loc' is disallowed when any of "

                                f"its corresponding low level keyword "

                                f"arguments ({protected_kw}) are also "

                                f"supplied")



        else:

            loc = mpl._val_or_rc(loc, 'yaxis.labellocation')

            _api.check_in_list(('bottom', 'center', 'top'), loc=loc)



            y, ha = {

                'bottom': (0, 'left'),

                'center': (0.5, 'center'),

                'top': (1, 'right')

            }[loc]

            kwargs.update(y=y, horizontalalignment=ha)



        return self.yaxis.set_label_text(ylabel, fontdict, **kwargs)



    def invert_yaxis(self):

        

        self.yaxis.set_inverted(not self.yaxis.get_inverted())



    set_yinverted = _axis_method_wrapper("yaxis", "set_inverted")

    get_yinverted = _axis_method_wrapper("yaxis", "get_inverted")

    yaxis_inverted = _axis_method_wrapper("yaxis", "get_inverted")

    if yaxis_inverted.__doc__:

        yaxis_inverted.__doc__ = ("[*Discouraged*] " + yaxis_inverted.__doc__ +

                                  textwrap.dedent("""

        .. admonition:: Discouraged

            The use of this method is discouraged.
            Use `.Axes.get_yinverted` instead.
        """))



    def get_ybound(self):

        

        bottom, top = self.get_ylim()

        if bottom < top:

            return bottom, top

        else:

            return top, bottom



    def set_ybound(self, lower=None, upper=None):

        

        if upper is None and np.iterable(lower):

            lower, upper = lower



        old_lower, old_upper = self.get_ybound()

        if lower is None:

            lower = old_lower

        if upper is None:

            upper = old_upper



        self.set_ylim(sorted((lower, upper),

                             reverse=bool(self.yaxis_inverted())),

                      auto=None)



    def get_ylim(self):

        

        return tuple(self.viewLim.intervaly)



    def set_ylim(self, bottom=None, top=None, *, emit=True, auto=False,

                 ymin=None, ymax=None):

        

        if top is None and np.iterable(bottom):

            bottom, top = bottom

        if ymin is not None:

            if bottom is not None:

                raise TypeError("Cannot pass both 'bottom' and 'ymin'")

            bottom = ymin

        if ymax is not None:

            if top is not None:

                raise TypeError("Cannot pass both 'top' and 'ymax'")

            top = ymax

        return self.yaxis._set_lim(bottom, top, emit=emit, auto=auto)



    get_yscale = _axis_method_wrapper("yaxis", "get_scale")

    set_yscale = _axis_method_wrapper("yaxis", "_set_axes_scale")

    get_yticks = _axis_method_wrapper("yaxis", "get_ticklocs")

    set_yticks = _axis_method_wrapper("yaxis", "set_ticks",

                                      doc_sub={'set_ticks': 'set_yticks'})

    get_ymajorticklabels = _axis_method_wrapper("yaxis", "get_majorticklabels")

    get_yminorticklabels = _axis_method_wrapper("yaxis", "get_minorticklabels")

    get_yticklabels = _axis_method_wrapper("yaxis", "get_ticklabels")

    set_yticklabels = _axis_method_wrapper(

        "yaxis", "set_ticklabels",

        doc_sub={"Axis.set_ticks": "Axes.set_yticks"})



    xaxis_date = _axis_method_wrapper("xaxis", "axis_date")

    yaxis_date = _axis_method_wrapper("yaxis", "axis_date")



    def format_xdata(self, x):

        

        return (self.fmt_xdata if self.fmt_xdata is not None

                else self.xaxis.get_major_formatter().format_data_short)(x)



    def format_ydata(self, y):

        

        return (self.fmt_ydata if self.fmt_ydata is not None

                else self.yaxis.get_major_formatter().format_data_short)(y)



    def format_coord(self, x, y):

        

        twins = self._twinned_axes.get_siblings(self)

        if len(twins) == 1:

            return "(x, y) = ({}, {})".format(

                "???" if x is None else self.format_xdata(x),

                "???" if y is None else self.format_ydata(y))

        screen_xy = self.transData.transform((x, y))

        xy_strs = []

                                                                                        

                                                                              

        for ax in sorted(twins, key=attrgetter("zorder")):

            data_x, data_y = ax.transData.inverted().transform(screen_xy)

            xy_strs.append(

                "({}, {})".format(ax.format_xdata(data_x), ax.format_ydata(data_y)))

        return "(x, y) = {}".format(" | ".join(xy_strs))



    def minorticks_on(self):

        

        self.xaxis.minorticks_on()

        self.yaxis.minorticks_on()



    def minorticks_off(self):

        

        self.xaxis.minorticks_off()

        self.yaxis.minorticks_off()



                              



    def can_zoom(self):

        

        return True



    def can_pan(self):

        

        return True



    def get_navigate(self):

        

        return self._navigate



    def set_navigate(self, b):

        

        self._navigate = b



    def get_navigate_mode(self):

        

        toolbar = self.figure.canvas.toolbar

        if toolbar:

            return None if toolbar.mode.name == "NONE" else toolbar.mode.name

        manager = self.figure.canvas.manager

        if manager and manager.toolmanager:

            mode = manager.toolmanager.active_toggle.get("default")

            return None if mode is None else mode.upper()



    @_api.deprecated("3.11")

    def set_navigate_mode(self, b):

        



    def _get_view(self):

        

        return {

            "xlim": self.get_xlim(), "autoscalex_on": self.get_autoscalex_on(),

            "ylim": self.get_ylim(), "autoscaley_on": self.get_autoscaley_on(),

        }



    def _set_view(self, view):

        

        self.set(**view)



    def _prepare_view_from_bbox(self, bbox, direction='in',

                                mode=None, twinx=False, twiny=False):

        

        if len(bbox) == 3:

            xp, yp, scl = bbox                

            if scl == 0:                     

                scl = 1.

            if scl > 1:

                direction = 'in'

            else:

                direction = 'out'

                scl = 1/scl

                                        

            (xmin, ymin), (xmax, ymax) = self.transData.transform(

                np.transpose([self.get_xlim(), self.get_ylim()]))

                           

            xwidth = xmax - xmin

            ywidth = ymax - ymin

            xcen = (xmax + xmin)*.5

            ycen = (ymax + ymin)*.5

            xzc = (xp*(scl - 1) + xcen)/scl

            yzc = (yp*(scl - 1) + ycen)/scl

            bbox = [xzc - xwidth/2./scl, yzc - ywidth/2./scl,

                    xzc + xwidth/2./scl, yzc + ywidth/2./scl]

        elif len(bbox) != 4:

                                                   

            _api.warn_external(

                "Warning in _set_view_from_bbox: bounding box is not a tuple "

                "of length 3 or 4. Ignoring the view change.")

            return



                          

        xmin0, xmax0 = self.get_xbound()

        ymin0, ymax0 = self.get_ybound()

                                        

        startx, starty, stopx, stopy = bbox

                                 

        (startx, starty), (stopx, stopy) = self.transData.inverted().transform(

            [(startx, starty), (stopx, stopy)])

                              

        xmin, xmax = np.clip(sorted([startx, stopx]), xmin0, xmax0)

        ymin, ymax = np.clip(sorted([starty, stopy]), ymin0, ymax0)

                                                                           

        if twinx or mode == "y":

            xmin, xmax = xmin0, xmax0

        if twiny or mode == "x":

            ymin, ymax = ymin0, ymax0



        if direction == "in":

            new_xbound = xmin, xmax

            new_ybound = ymin, ymax



        elif direction == "out":

            x_trf = self.xaxis.get_transform()

            sxmin0, sxmax0, sxmin, sxmax = x_trf.transform(

                [xmin0, xmax0, xmin, xmax])                    

            factor = (sxmax0 - sxmin0) / (sxmax - sxmin)                  

                                          

                                                                     

            sxmin1 = sxmin0 - factor * (sxmin - sxmin0)

            sxmax1 = sxmax0 + factor * (sxmax0 - sxmax)

                                     

            new_xbound = x_trf.inverted().transform([sxmin1, sxmax1])



            y_trf = self.yaxis.get_transform()

            symin0, symax0, symin, symax = y_trf.transform(

                [ymin0, ymax0, ymin, ymax])

            factor = (symax0 - symin0) / (symax - symin)

            symin1 = symin0 - factor * (symin - symin0)

            symax1 = symax0 + factor * (symax0 - symax)

            new_ybound = y_trf.inverted().transform([symin1, symax1])



        return new_xbound, new_ybound



    def _set_view_from_bbox(self, bbox, direction='in',

                            mode=None, twinx=False, twiny=False):

        

        new_xbound, new_ybound = self._prepare_view_from_bbox(

            bbox, direction=direction, mode=mode, twinx=twinx, twiny=twiny)

        if not twinx and mode != "y":

            self.set_xbound(new_xbound)

            self.set_autoscalex_on(False)

        if not twiny and mode != "x":

            self.set_ybound(new_ybound)

            self.set_autoscaley_on(False)



    def start_pan(self, x, y, button):

        

        self._pan_start = types.SimpleNamespace(

            lim=self.viewLim.frozen(),

            trans=self.transData.frozen(),

            trans_inverse=self.transData.inverted().frozen(),

            bbox=self.bbox.frozen(),

            x=x,

            y=y)



    def end_pan(self):

        

        del self._pan_start



    def _get_pan_points(self, button, key, x, y):

        

        def format_deltas(key, dx, dy):

            if key == 'control':

                if abs(dx) > abs(dy):

                    dy = dx

                else:

                    dx = dy

            elif key == 'x':

                dy = 0

            elif key == 'y':

                dx = 0

            elif key == 'shift':

                if 2 * abs(dx) < abs(dy):

                    dx = 0

                elif 2 * abs(dy) < abs(dx):

                    dy = 0

                elif abs(dx) > abs(dy):

                    dy = dy / abs(dy) * abs(dx)

                else:

                    dx = dx / abs(dx) * abs(dy)

            return dx, dy



        p = self._pan_start

        dx = x - p.x

        dy = y - p.y

        if dx == dy == 0:

            return

        if button == 1:

            dx, dy = format_deltas(key, dx, dy)

            result = p.bbox.translated(-dx, -dy).transformed(p.trans_inverse)

        elif button == 3:

            try:

                dx = -dx / self.bbox.width

                dy = -dy / self.bbox.height

                dx, dy = format_deltas(key, dx, dy)

                if self.get_aspect() != 'auto':

                    dx = dy = 0.5 * (dx + dy)

                alpha = np.power(10.0, (dx, dy))

                start = np.array([p.x, p.y])

                oldpoints = p.lim.transformed(p.trans)

                newpoints = start + alpha * (oldpoints - start)

                result = (mtransforms.Bbox(newpoints)

                          .transformed(p.trans_inverse))

            except OverflowError:

                _api.warn_external('Overflow while panning')

                return

        else:

            return



        valid = np.isfinite(result.transformed(p.trans))

        points = result.get_points().astype(object)

                                                                         

        points[~valid] = None

        return points



    def drag_pan(self, button, key, x, y):

        

        points = self._get_pan_points(button, key, x, y)

        if points is not None:

            self.set_xlim(points[:, 0])

            self.set_ylim(points[:, 1])



    def get_children(self):

                              

        return [

            *self._children,

            *self.spines.values(),

            *self._axis_map.values(),

            self.title, self._left_title, self._right_title,

            *self.child_axes,

            *([self.legend_] if self.legend_ is not None else []),

            self.patch,

        ]



    def contains(self, mouseevent):

                              

        return self.patch.contains(mouseevent)



    def contains_point(self, point):

        

        return self.patch.contains_point(point, radius=1.0)



    def get_default_bbox_extra_artists(self):

        



        artists = self.get_children()



        for axis in self._axis_map.values():

                                                                

                                                             

            artists.remove(axis)

        if not (self.axison and self._frameon):

                                                      

            for spine in self.spines.values():

                artists.remove(spine)



        artists.remove(self.title)

        artists.remove(self._left_title)

        artists.remove(self._right_title)



                                                                        

                                                                       

                                                                   

        noclip = (_AxesBase, maxis.Axis,

                  offsetbox.AnnotationBbox, offsetbox.OffsetBox)

        return [a for a in artists if a.get_visible() and a.get_in_layout()

                and (isinstance(a, noclip) or not a._fully_clipped_to_axes())]



    def get_tightbbox(self, renderer=None, *, call_axes_locator=True,

                      bbox_extra_artists=None, for_layout_only=False):

        



        bb = []

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()



        if not self.get_visible():

            return None



        locator = self.get_axes_locator()

        self.apply_aspect(

            locator(self, renderer) if locator and call_axes_locator else None)



        for axis in self._axis_map.values():

            if self.axison and axis.get_visible():

                ba = martist._get_tightbbox_for_layout_only(axis, renderer)

                if ba:

                    bb.append(ba)

        self._update_title_position(renderer)

        axbbox = self.get_window_extent(renderer)

        bb.append(axbbox)



        for title in [self.title, self._left_title, self._right_title]:

            if title.get_visible():

                bt = title.get_window_extent(renderer)

                if for_layout_only and bt.width > 0:

                                                                   

                                                                  

                                              

                    bt.x0 = (bt.x0 + bt.x1) / 2 - 0.5

                    bt.x1 = bt.x0 + 1.0

                bb.append(bt)



        bbox_artists = bbox_extra_artists

        if bbox_artists is None:

            bbox_artists = self.get_default_bbox_extra_artists()



        for a in bbox_artists:

            bbox = a.get_tightbbox(renderer)

            if (bbox is not None

                    and 0 < bbox.width < np.inf

                    and 0 < bbox.height < np.inf):

                bb.append(bbox)

        return mtransforms.Bbox.union(

            [b for b in bb if b.width != 0 or b.height != 0])



    def _make_twin_axes(self, *args, **kwargs):

        

        if 'sharex' in kwargs and 'sharey' in kwargs:

                                                                            

                                                     

            if kwargs["sharex"] is not self and kwargs["sharey"] is not self:

                raise ValueError("Twinned Axes may share only one axis")

        ss = self.get_subplotspec()

        if ss:

            twin = self.get_figure(root=False).add_subplot(ss, *args, **kwargs)

        else:

            twin = self.get_figure(root=False).add_axes(

                self.get_position(True), *args, **kwargs,

                axes_locator=_TransformedBoundsLocator(

                    [0, 0, 1, 1], self.transAxes))

        self.set_adjustable('datalim')

        twin.set_adjustable('datalim')

        twin.set_zorder(self.zorder)



        self._twinned_axes.join(self, twin)

        return twin



    def twinx(self, axes_class=None, **kwargs):

        

        if axes_class:

            kwargs["axes_class"] = axes_class

        ax2 = self._make_twin_axes(sharex=self, **kwargs)

        ax2.yaxis.tick_right()

        ax2.yaxis.set_label_position('right')

        ax2.yaxis.set_offset_position('right')

        ax2.set_autoscalex_on(self.get_autoscalex_on())

        self.yaxis.tick_left()

        ax2.xaxis.set_visible(False)

        ax2.patch.set_visible(False)

        ax2.xaxis.units = self.xaxis.units

        return ax2



    def twiny(self, axes_class=None, **kwargs):

        

        if axes_class:

            kwargs["axes_class"] = axes_class

        ax2 = self._make_twin_axes(sharey=self, **kwargs)

        ax2.xaxis.tick_top()

        ax2.xaxis.set_label_position('top')

        ax2.set_autoscaley_on(self.get_autoscaley_on())

        self.xaxis.tick_bottom()

        ax2.yaxis.set_visible(False)

        ax2.patch.set_visible(False)

        ax2.yaxis.units = self.yaxis.units

        return ax2



    def get_shared_x_axes(self):

        

        return cbook.GrouperView(self._shared_axes["x"])



    def get_shared_y_axes(self):

        

        return cbook.GrouperView(self._shared_axes["y"])



    def label_outer(self, remove_inner_ticks=False):

        

        self._label_outer_xaxis(skip_non_rectangular_axes=False,

                                remove_inner_ticks=remove_inner_ticks)

        self._label_outer_yaxis(skip_non_rectangular_axes=False,

                                remove_inner_ticks=remove_inner_ticks)



    def _get_subplotspec_with_optional_colorbar(self):

        

        ss = self.get_subplotspec()

        if any(cax.get_subplotspec() for cax in self._colorbars):

            ss = ss.get_gridspec()._subplot_spec

        return ss



    def _label_outer_xaxis(self, *, skip_non_rectangular_axes,

                           remove_inner_ticks=False):

                                           

        if skip_non_rectangular_axes and not isinstance(self.patch,

                                                        mpl.patches.Rectangle):

            return

        ss = self._get_subplotspec_with_optional_colorbar()

        if ss is None:

            return

        label_position = self.xaxis.get_label_position()

        if not ss.is_first_row():                                           

            if label_position == "top":

                self.set_xlabel("")

            top_kw = {'top': False} if remove_inner_ticks else {}

            self.xaxis.set_tick_params(

                which="both", labeltop=False, **top_kw)

            if self.xaxis.offsetText.get_position()[1] == 1:

                self.xaxis.offsetText.set_visible(False)

        if not ss.is_last_row():                                              

            if label_position == "bottom":

                self.set_xlabel("")

            bottom_kw = {'bottom': False} if remove_inner_ticks else {}

            self.xaxis.set_tick_params(

                which="both", labelbottom=False, **bottom_kw)

            if self.xaxis.offsetText.get_position()[1] == 0:

                self.xaxis.offsetText.set_visible(False)



    def _label_outer_yaxis(self, *, skip_non_rectangular_axes,

                           remove_inner_ticks=False):

                                           

        if skip_non_rectangular_axes and not isinstance(self.patch,

                                                        mpl.patches.Rectangle):

            return

        ss = self._get_subplotspec_with_optional_colorbar()

        if ss is None:

            return

        label_position = self.yaxis.get_label_position()

        if not ss.is_first_col():                                            

            if label_position == "left":

                self.set_ylabel("")

            left_kw = {'left': False} if remove_inner_ticks else {}

            self.yaxis.set_tick_params(

                which="both", labelleft=False, **left_kw)

            if self.yaxis.offsetText.get_position()[0] == 0:

                self.yaxis.offsetText.set_visible(False)

        if not ss.is_last_col():                                             

            if label_position == "right":

                self.set_ylabel("")

            right_kw = {'right': False} if remove_inner_ticks else {}

            self.yaxis.set_tick_params(

                which="both", labelright=False, **right_kw)

            if self.yaxis.offsetText.get_position()[0] == 1:

                self.yaxis.offsetText.set_visible(False)



    def set_forward_navigation_events(self, forward):

        

        self._forward_navigation_events = forward



    def get_forward_navigation_events(self):

        

        return self._forward_navigation_events





def _draw_rasterized(figure, artists, renderer):

    

    class _MinimalArtist:

        def get_rasterized(self):

            return True



        def get_agg_filter(self):

            return None



        def __init__(self, figure, artists):

            self.figure = figure

            self.artists = artists



        def get_figure(self, root=False):

            if root:

                return self.figure.get_figure(root=True)

            else:

                return self.figure



        @martist.allow_rasterization

        def draw(self, renderer):

            for a in self.artists:

                a.draw(renderer)



    return _MinimalArtist(figure, artists).draw(renderer)

