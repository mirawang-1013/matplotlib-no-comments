



import itertools

import logging

import numbers

import time



import numpy as np



import matplotlib as mpl

from matplotlib import _api, _docstring, cbook, colors, offsetbox

from matplotlib.artist import Artist, allow_rasterization

from matplotlib.cbook import silent_list

from matplotlib.font_manager import FontProperties

from matplotlib.lines import Line2D

from matplotlib.patches import (Patch, Rectangle, Shadow, FancyBboxPatch,

                                StepPatch)

from matplotlib.collections import (

    Collection, CircleCollection, LineCollection, PathCollection,

    PolyCollection, RegularPolyCollection)

from matplotlib.text import Text

from matplotlib.transforms import Bbox, BboxBase, TransformedBbox

from matplotlib.transforms import BboxTransformTo, BboxTransformFrom

from matplotlib.offsetbox import (

    AnchoredOffsetbox, DraggableOffsetBox,

    HPacker, VPacker,

    DrawingArea, TextArea,

)

from matplotlib.container import ErrorbarContainer, BarContainer, StemContainer

from . import legend_handler





class DraggableLegend(DraggableOffsetBox):

    def __init__(self, legend, use_blit=False, update="loc"):

        

        self.legend = legend



        _api.check_in_list(["loc", "bbox"], update=update)

        self._update = update



        super().__init__(legend, legend._legend_box, use_blit=use_blit)



    def finalize_offset(self):

        if self._update == "loc":

            self._update_loc(self.get_loc_in_canvas())

        elif self._update == "bbox":

            self._update_bbox_to_anchor(self.get_loc_in_canvas())



    def _update_loc(self, loc_in_canvas):

        bbox = self.legend.get_bbox_to_anchor()

                                                                 

                                                               

        if bbox.width == 0 or bbox.height == 0:

            self.legend.set_bbox_to_anchor(None)

            bbox = self.legend.get_bbox_to_anchor()

        _bbox_transform = BboxTransformFrom(bbox)

        self.legend._loc = tuple(_bbox_transform.transform(loc_in_canvas))



    def _update_bbox_to_anchor(self, loc_in_canvas):

        loc_in_bbox = self.legend.axes.transAxes.transform(loc_in_canvas)

        self.legend.set_bbox_to_anchor(loc_in_bbox)





_legend_kw_doc_base = """
bbox_to_anchor : `.BboxBase`, 2-tuple, or 4-tuple of floats
    Box that is used to position the legend in conjunction with *loc*.
    Defaults to ``axes.bbox`` (if called as a method to `.Axes.legend`) or
    ``figure.bbox`` (if ``figure.legend``).  This argument allows arbitrary
    placement of the legend.

    Bbox coordinates are interpreted in the coordinate system given by
    *bbox_transform*, with the default transform
    Axes or Figure coordinates, depending on which ``legend`` is called.

    If a 4-tuple or `.BboxBase` is given, then it specifies the bbox
    ``(x, y, width, height)`` that the legend is placed in.
    To put the legend in the best location in the bottom right
    quadrant of the Axes (or figure)::

        loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5)

    A 2-tuple ``(x, y)`` places the corner of the legend specified by *loc* at
    x, y.  For example, to put the legend's upper right-hand corner in the
    center of the Axes (or figure) the following keywords can be used::

        loc='upper right', bbox_to_anchor=(0.5, 0.5)

ncols : int, default: 1
    The number of columns that the legend has.

    For backward compatibility, the spelling *ncol* is also supported
    but it is discouraged. If both are given, *ncols* takes precedence.

prop : None or `~matplotlib.font_manager.FontProperties` or dict
    The font properties of the legend. If None (default), the current
    :data:`matplotlib.rcParams` will be used.

fontsize : int or {'xx-small', 'x-small', 'small', 'medium', 'large', \
'x-large', 'xx-large'}
    The font size of the legend. If the value is numeric the size will be the
    absolute font size in points. String values are relative to the current
    default font size. This argument is only used if *prop* is not specified.

labelcolor : str or list, default: :rc:`legend.labelcolor`
    The color of the text in the legend. Either a valid color string
    (for example, 'red'), or a list of color strings. The labelcolor can
    also be made to match the color of the line or marker using 'linecolor',
    'markerfacecolor' (or 'mfc'), or 'markeredgecolor' (or 'mec').

    Labelcolor can be set globally using :rc:`legend.labelcolor`. If None,
    use :rc:`text.color`.

numpoints : int, default: :rc:`legend.numpoints`
    The number of marker points in the legend when creating a legend
    entry for a `.Line2D` (line).

scatterpoints : int, default: :rc:`legend.scatterpoints`
    The number of marker points in the legend when creating
    a legend entry for a `.PathCollection` (scatter plot).

scatteryoffsets : iterable of floats, default: ``[0.375, 0.5, 0.3125]``
    The vertical offset (relative to the font size) for the markers
    created for a scatter plot legend entry. 0.0 is at the base the
    legend text, and 1.0 is at the top. To draw all markers at the
    same height, set to ``[0.5]``.

markerscale : float, default: :rc:`legend.markerscale`
    The relative size of legend markers compared to the originally drawn ones.

markerfirst : bool, default: True
    If *True*, legend marker is placed to the left of the legend label.
    If *False*, legend marker is placed to the right of the legend label.

reverse : bool, default: False
    If *True*, the legend labels are displayed in reverse order from the input.
    If *False*, the legend labels are displayed in the same order as the input.

    .. versionadded:: 3.7

frameon : bool, default: :rc:`legend.frameon`
    Whether the legend should be drawn on a patch (frame).

fancybox : bool, default: :rc:`legend.fancybox`
    Whether round edges should be enabled around the `.FancyBboxPatch` which
    makes up the legend's background.

shadow : None, bool or dict, default: :rc:`legend.shadow`
    Whether to draw a shadow behind the legend.
    The shadow can be configured using `.Patch` keywords.
    Customization via :rc:`legend.shadow` is currently not supported.

framealpha : float, default: :rc:`legend.framealpha`
    The alpha transparency of the legend's background.
    If *shadow* is activated and *framealpha* is ``None``, the default value is
    ignored.

facecolor : "inherit" or color, default: :rc:`legend.facecolor`
    The legend's background color.
    If ``"inherit"``, use :rc:`axes.facecolor`.

edgecolor : "inherit" or color, default: :rc:`legend.edgecolor`
    The legend's background patch edge color.
    If ``"inherit"``, use :rc:`axes.edgecolor`.

mode : {"expand", None}
    If *mode* is set to ``"expand"`` the legend will be horizontally
    expanded to fill the Axes area (or *bbox_to_anchor* if defines
    the legend's size).

bbox_transform : None or `~matplotlib.transforms.Transform`
    The transform for the bounding box (*bbox_to_anchor*). For a value
    of ``None`` (default) the Axes'
    :data:`!matplotlib.axes.Axes.transAxes` transform will be used.

title : str or None
    The legend's title. Default is no title (``None``).

title_fontproperties : None or `~matplotlib.font_manager.FontProperties` or dict
    The font properties of the legend's title. If None (default), the
    *title_fontsize* argument will be used if present; if *title_fontsize* is
    also None, the current :rc:`legend.title_fontsize` will be used.

title_fontsize : int or {'xx-small', 'x-small', 'small', 'medium', 'large', \
'x-large', 'xx-large'}, default: :rc:`legend.title_fontsize`
    The font size of the legend's title.
    Note: This cannot be combined with *title_fontproperties*. If you want
    to set the fontsize alongside other font properties, use the *size*
    parameter in *title_fontproperties*.

alignment : {'center', 'left', 'right'}, default: 'center'
    The alignment of the legend title and the box of entries. The entries
    are aligned as a single block, so that markers always lined up.

borderpad : float, default: :rc:`legend.borderpad`
    The fractional whitespace inside the legend border, in font-size units.

labelspacing : float, default: :rc:`legend.labelspacing`
    The vertical space between the legend entries, in font-size units.

handlelength : float, default: :rc:`legend.handlelength`
    The length of the legend handles, in font-size units.

handleheight : float, default: :rc:`legend.handleheight`
    The height of the legend handles, in font-size units.

handletextpad : float, default: :rc:`legend.handletextpad`
    The pad between the legend handle and text, in font-size units.

borderaxespad : float, default: :rc:`legend.borderaxespad`
    The pad between the Axes and legend border, in font-size units.

columnspacing : float, default: :rc:`legend.columnspacing`
    The spacing between columns, in font-size units.

handler_map : dict or None
    The custom dictionary mapping instances or types to a legend
    handler. This *handler_map* updates the default handler map
    found at `matplotlib.legend.Legend.get_legend_handler_map`.

draggable : bool, default: False
    Whether the legend can be dragged with the mouse.
"""



_loc_doc_base = """
loc : str or pair of floats, default: {default}
    The location of the legend.

    The strings ``'upper left'``, ``'upper right'``, ``'lower left'``,
    ``'lower right'`` place the legend at the corresponding corner of the
    {parent}.

    The strings ``'upper center'``, ``'lower center'``, ``'center left'``,
    ``'center right'`` place the legend at the center of the corresponding edge
    of the {parent}.

    The string ``'center'`` places the legend at the center of the {parent}.
{best}
    The location can also be a 2-tuple giving the coordinates of the lower-left
    corner of the legend in {parent} coordinates (in which case *bbox_to_anchor*
    will be ignored).

    For back-compatibility, ``'center right'`` (but no other location) can also
    be spelled ``'right'``, and each "string" location can also be given as a
    numeric value:

    ==================   =============
    Location String      Location Code
    ==================   =============
    'best' (Axes only)   0
    'upper right'        1
    'upper left'         2
    'lower left'         3
    'lower right'        4
    'right'              5
    'center left'        6
    'center right'       7
    'lower center'       8
    'upper center'       9
    'center'             10
    ==================   =============
    {outside}"""



_loc_doc_best = """
    The string ``'best'`` places the legend at the location, among the nine
    locations defined so far, with the minimum overlap with other drawn
    artists.  This option can be quite slow for plots with large amounts of
    data; your plotting speed may benefit from providing a specific location.
"""



_legend_kw_axes_st = (

    _loc_doc_base.format(parent='axes', default=':rc:`legend.loc`',

                         best=_loc_doc_best, outside='') +

    _legend_kw_doc_base)

_docstring.interpd.register(_legend_kw_axes=_legend_kw_axes_st)



_outside_doc = """
    If a figure is using the constrained layout manager, the string codes
    of the *loc* keyword argument can get better layout behaviour using the
    prefix 'outside'. There is ambiguity at the corners, so 'outside
    upper right' will make space for the legend above the rest of the
    axes in the layout, and 'outside right upper' will make space on the
    right side of the layout.  In addition to the values of *loc*
    listed above, we have 'outside right upper', 'outside right lower',
    'outside left upper', and 'outside left lower'.  See
    :ref:`legend_guide` for more details.
"""



_legend_kw_figure_st = (

    _loc_doc_base.format(parent='figure', default="'upper right'",

                         best='', outside=_outside_doc) +

    _legend_kw_doc_base)

_docstring.interpd.register(_legend_kw_figure=_legend_kw_figure_st)



_legend_kw_both_st = (

    _loc_doc_base.format(parent='axes/figure',

                         default=":rc:`legend.loc` for Axes, 'upper right' for Figure",

                         best=_loc_doc_best, outside=_outside_doc) +

    _legend_kw_doc_base)

_docstring.interpd.register(_legend_kw_doc=_legend_kw_both_st)



_legend_kw_set_loc_st = (

    _loc_doc_base.format(parent='axes/figure',

                         default=":rc:`legend.loc` for Axes, 'upper right' for Figure",

                         best=_loc_doc_best, outside=_outside_doc))

_docstring.interpd.register(_legend_kw_set_loc_doc=_legend_kw_set_loc_st)





class Legend(Artist):

    



                                                 

    codes = {'best': 0, **AnchoredOffsetbox.codes}

    zorder = 5



    def __str__(self):

        return "Legend"



    @_docstring.interpd

    def __init__(

        self, parent, handles, labels,

        *,

        loc=None,

        numpoints=None,                                           

        markerscale=None,                                                  

        markerfirst=True,                                                    

        reverse=False,                                                    

        scatterpoints=None,                            

        scatteryoffsets=None,

        prop=None,                                            

        fontsize=None,                                          

        labelcolor=None,                                    



                                                              

        borderpad=None,                                           

        labelspacing=None,                                              

        handlelength=None,                                 

        handleheight=None,                                 

        handletextpad=None,                                          

        borderaxespad=None,                                          

        columnspacing=None,                           



        ncols=1,                        

        mode=None,                                                        



        fancybox=None,                                                      

        shadow=None,

        title=None,                         

        title_fontsize=None,                          

        framealpha=None,                       

        edgecolor=None,                              

        facecolor=None,                              



        bbox_to_anchor=None,                                             

        bbox_transform=None,                          

        frameon=None,                     

        handler_map=None,

        title_fontproperties=None,                                   

        alignment="center",                                                    

        ncol=1,                                              

        draggable=False                                                    

    ):

        

                                                

        from matplotlib.axes import Axes

        from matplotlib.figure import FigureBase



        super().__init__()



        if prop is None:

            self.prop = FontProperties(size=mpl._val_or_rc(fontsize, "legend.fontsize"))

        else:

            self.prop = FontProperties._from_any(prop)

            if isinstance(prop, dict) and "size" not in prop:

                self.prop.set_size(mpl.rcParams["legend.fontsize"])



        self._fontsize = self.prop.get_size_in_points()



        self.texts = []

        self.legend_handles = []

        self._legend_title_box = None



                                                                       

                    

        self._custom_handler_map = handler_map



        self.numpoints = mpl._val_or_rc(numpoints, 'legend.numpoints')

        self.markerscale = mpl._val_or_rc(markerscale, 'legend.markerscale')

        self.scatterpoints = mpl._val_or_rc(scatterpoints, 'legend.scatterpoints')

        self.borderpad = mpl._val_or_rc(borderpad, 'legend.borderpad')

        self.labelspacing = mpl._val_or_rc(labelspacing, 'legend.labelspacing')

        self.handlelength = mpl._val_or_rc(handlelength, 'legend.handlelength')

        self.handleheight = mpl._val_or_rc(handleheight, 'legend.handleheight')

        self.handletextpad = mpl._val_or_rc(handletextpad, 'legend.handletextpad')

        self.borderaxespad = mpl._val_or_rc(borderaxespad, 'legend.borderaxespad')

        self.columnspacing = mpl._val_or_rc(columnspacing, 'legend.columnspacing')

        self.shadow = mpl._val_or_rc(shadow, 'legend.shadow')



        if reverse:

            labels = [*reversed(labels)]

            handles = [*reversed(handles)]



        handles = list(handles)

        if len(handles) < 2:

            ncols = 1

        self._ncols = ncols if ncols != 1 else ncol



        if self.numpoints <= 0:

            raise ValueError("numpoints must be > 0; it was %d" % numpoints)



                                                            

        if scatteryoffsets is None:

            self._scatteryoffsets = np.array([3. / 8., 4. / 8., 2.5 / 8.])

        else:

            self._scatteryoffsets = np.asarray(scatteryoffsets)

        reps = self.scatterpoints // len(self._scatteryoffsets) + 1

        self._scatteryoffsets = np.tile(self._scatteryoffsets,

                                        reps)[:self.scatterpoints]



                                                             

                                                                      

                 

        self._legend_box = None



        if isinstance(parent, Axes):

            self.isaxes = True

            self.axes = parent

            self.set_figure(parent.get_figure(root=False))

        elif isinstance(parent, FigureBase):

            self.isaxes = False

            self.set_figure(parent)

        else:

            raise TypeError(

                "Legend needs either Axes or FigureBase as parent"

            )

        self.parent = parent



        self._mode = mode

        self.set_bbox_to_anchor(bbox_to_anchor, bbox_transform)



                                            

                                                  

                                      



        self._shadow_props = {'ox': 2, 'oy': -2}                            

        if isinstance(self.shadow, dict):

            self._shadow_props.update(self.shadow)

            self.shadow = True

        elif self.shadow in (0, 1, True, False):

            self.shadow = bool(self.shadow)

        else:

            raise ValueError(

                'Legend shadow must be a dict or bool, not '

                f'{self.shadow!r} of type {type(self.shadow)}.'

            )



                                                                    

                                                                      



        facecolor = mpl._val_or_rc(facecolor, "legend.facecolor")

        if facecolor == 'inherit':

            facecolor = mpl.rcParams["axes.facecolor"]



        edgecolor = mpl._val_or_rc(edgecolor, "legend.edgecolor")

        if edgecolor == 'inherit':

            edgecolor = mpl.rcParams["axes.edgecolor"]



        fancybox = mpl._val_or_rc(fancybox, "legend.fancybox")



        self.legendPatch = FancyBboxPatch(

            xy=(0, 0), width=1, height=1,

            facecolor=facecolor, edgecolor=edgecolor,

                                                            

            alpha=(framealpha if framealpha is not None

                   else 1 if shadow

                   else mpl.rcParams["legend.framealpha"]),

                                                                             

                                                                              

            boxstyle=("round,pad=0,rounding_size=0.2" if fancybox

                      else "square,pad=0"),

            mutation_scale=self._fontsize,

            snap=True,

            visible=mpl._val_or_rc(frameon, "legend.frameon")

        )

        self._set_artist_props(self.legendPatch)



        _api.check_in_list(["center", "left", "right"], alignment=alignment)

        self._alignment = alignment



                                 

        self._init_legend_box(handles, labels, markerfirst)



                             

        self.set_loc(loc)



                                           

        if title_fontsize is not None and title_fontproperties is not None:

            raise ValueError(

                "title_fontsize and title_fontproperties can't be specified "

                "at the same time. Only use one of them. ")

        title_prop_fp = FontProperties._from_any(title_fontproperties)

        if isinstance(title_fontproperties, dict):

            if "size" not in title_fontproperties:

                title_fontsize = mpl.rcParams["legend.title_fontsize"]

                title_prop_fp.set_size(title_fontsize)

        elif title_fontsize is not None:

            title_prop_fp.set_size(title_fontsize)

        elif not isinstance(title_fontproperties, FontProperties):

            title_fontsize = mpl.rcParams["legend.title_fontsize"]

            title_prop_fp.set_size(title_fontsize)



        self.set_title(title, prop=title_prop_fp)



        self._draggable = None

        self.set_draggable(state=draggable)



                            



        color_getters = {                                            

            'linecolor':       ['get_markerfacecolor',

                                'get_facecolor',

                                'get_markeredgecolor',

                                'get_edgecolor',

                                'get_color'],

            'markerfacecolor': ['get_markerfacecolor', 'get_facecolor'],

            'mfc':             ['get_markerfacecolor', 'get_facecolor'],

            'markeredgecolor': ['get_markeredgecolor', 'get_edgecolor'],

            'mec':             ['get_markeredgecolor', 'get_edgecolor'],

        }

        labelcolor = mpl._val_or_rc(mpl._val_or_rc(labelcolor, 'legend.labelcolor'),

                                    'text.color')

        if isinstance(labelcolor, str) and labelcolor in color_getters:

            getter_names = color_getters[labelcolor]

            for handle, text in zip(self.legend_handles, self.texts):

                try:

                    if handle.get_array() is not None:

                        continue

                except AttributeError:

                    pass

                for getter_name in getter_names:

                    try:

                        color = getattr(handle, getter_name)()

                    except AttributeError:

                        continue

                    if isinstance(color, np.ndarray):

                        if color.size == 0:

                            continue

                        elif (color.shape[0] == 1 or np.isclose(color, color[0]).all()):

                            text.set_color(color[0])

                        else:

                            pass

                    elif cbook._str_lower_equal(color, 'none'):

                        continue

                    elif mpl.colors.to_rgba(color)[3] == 0:

                        continue

                    else:

                        text.set_color(color)

                    break

        elif cbook._str_equal(labelcolor, 'none'):

            for text in self.texts:

                text.set_color(labelcolor)

        elif np.iterable(labelcolor):

            for text, color in zip(self.texts,

                                   itertools.cycle(

                                       colors.to_rgba_array(labelcolor))):

                text.set_color(color)

        else:

            raise ValueError(f"Invalid labelcolor: {labelcolor!r}")



    def _set_artist_props(self, a):

        

        a.set_figure(self.get_figure(root=False))

        if self.isaxes:

            a.axes = self.axes



        a.set_transform(self.get_transform())



    @_docstring.interpd

    def set_loc(self, loc=None):

        

        loc0 = loc

        self._loc_used_default = loc is None

        if loc is None:

            loc = mpl.rcParams["legend.loc"]

            if not self.isaxes and loc in [0, 'best']:

                loc = 'upper right'



        type_err_message = ("loc must be string, coordinate tuple, or"

                            f" an integer 0-10, not {loc!r}")



                                 

        self._outside_loc = None

        if isinstance(loc, str):

            if loc.split()[0] == 'outside':

                                

                loc = loc.split('outside ')[1]

                                                 

                self._outside_loc = loc.replace('center ', '')

                             

                self._outside_loc = self._outside_loc.split()[0]

                locs = loc.split()

                if len(locs) > 1 and locs[0] in ('right', 'left'):

                                                                    

                    if locs[0] != 'center':

                        locs = locs[::-1]

                    loc = locs[0] + ' ' + locs[1]

                                                     

            loc = _api.check_getitem(self.codes, loc=loc)

        elif np.iterable(loc):

                                        

            loc = tuple(loc)

                                                            

            if len(loc) != 2 or not all(isinstance(e, numbers.Real) for e in loc):

                raise ValueError(type_err_message)

        elif isinstance(loc, int):

                                                                    

            if loc < 0 or loc > 10:

                raise ValueError(type_err_message)

        else:

                                                       

            raise ValueError(type_err_message)



        if self.isaxes and self._outside_loc:

            raise ValueError(

                f"'outside' option for loc='{loc0}' keyword argument only "

                "works for figure legends")



        if not self.isaxes and loc == 0:

            raise ValueError(

                "Automatic legend placement (loc='best') not implemented for "

                "figure legend")



        tmp = self._loc_used_default

        self._set_loc(loc)

        self._loc_used_default = tmp                                   



    def _set_loc(self, loc):

                                                                  

                                                                    

                                   

        self._loc_used_default = False

        self._loc_real = loc

        self.stale = True

        self._legend_box.set_offset(self._findoffset)



    def set_ncols(self, ncols):

        

        self._ncols = ncols



    def _get_loc(self):

        return self._loc_real



    _loc = property(_get_loc, _set_loc)



    def _findoffset(self, width, height, xdescent, ydescent, renderer):

        



        if self._loc == 0:           

            x, y = self._find_best_position(width, height, renderer)

        elif self._loc in Legend.codes.values():                   

            bbox = Bbox.from_bounds(0, 0, width, height)

            x, y = self._get_anchored_bbox(self._loc, bbox,

                                           self.get_bbox_to_anchor(),

                                           renderer)

        else:                               

            fx, fy = self._loc

            bbox = self.get_bbox_to_anchor()

            x, y = bbox.x0 + bbox.width * fx, bbox.y0 + bbox.height * fy



        return x + xdescent, y + ydescent



    @allow_rasterization

    def draw(self, renderer):

                             

        if not self.get_visible():

            return



        renderer.open_group('legend', gid=self.get_gid())



        fontsize = renderer.points_to_pixels(self._fontsize)



                                                                 

                                          

        if self._mode in ["expand"]:

            pad = 2 * (self.borderaxespad + self.borderpad) * fontsize

            self._legend_box.set_width(self.get_bbox_to_anchor().width - pad)



                                                                   

                                                       

        bbox = self._legend_box.get_window_extent(renderer)

        self.legendPatch.set_bounds(bbox.bounds)

        self.legendPatch.set_mutation_scale(fontsize)



                                              

                                                                             



        if self.shadow:

            Shadow(self.legendPatch, **self._shadow_props).draw(renderer)



        self.legendPatch.draw(renderer)

        self._legend_box.draw(renderer)



        renderer.close_group('legend')

        self.stale = False



                                                                   

                                       



    _default_handler_map = {

        StemContainer: legend_handler.HandlerStem(),

        ErrorbarContainer: legend_handler.HandlerErrorbar(),

        Line2D: legend_handler.HandlerLine2D(),

        Patch: legend_handler.HandlerPatch(),

        StepPatch: legend_handler.HandlerStepPatch(),

        LineCollection: legend_handler.HandlerLineCollection(),

        RegularPolyCollection: legend_handler.HandlerRegularPolyCollection(),

        CircleCollection: legend_handler.HandlerCircleCollection(),

        BarContainer: legend_handler.HandlerPatch(

            update_func=legend_handler.update_from_first_child),

        tuple: legend_handler.HandlerTuple(),

        PathCollection: legend_handler.HandlerPathCollection(),

        PolyCollection: legend_handler.HandlerPolyCollection()

        }



                                                                    

                                     



    @classmethod

    def get_default_handler_map(cls):

        

        return cls._default_handler_map



    @classmethod

    def set_default_handler_map(cls, handler_map):

        

        cls._default_handler_map = handler_map



    @classmethod

    def update_default_handler_map(cls, handler_map):

        

        cls._default_handler_map.update(handler_map)



    def get_legend_handler_map(self):

        

        default_handler_map = self.get_default_handler_map()

        return ({**default_handler_map, **self._custom_handler_map}

                if self._custom_handler_map else default_handler_map)



    @staticmethod

    def get_legend_handler(legend_handler_map, orig_handle):

        

        try:

            return legend_handler_map[orig_handle]

        except (TypeError, KeyError):                            

            pass

        for handle_type in type(orig_handle).mro():

            try:

                return legend_handler_map[handle_type]

            except KeyError:

                pass

        return None



    def _init_legend_box(self, handles, labels, markerfirst=True):

        



        fontsize = self._fontsize



                                                                    

                                                                        

                                                    

                                                                      

                                                                



        text_list = []                              

        handle_list = []                                

        handles_and_labels = []



                                                                      

                                                   

        descent = 0.35 * fontsize * (self.handleheight - 0.7)              

        height = fontsize * self.handleheight - descent

                                                                      

                                                                     

                                              



                                                                     

                                                                 

                                                            

                                                                   

        legend_handler_map = self.get_legend_handler_map()



        for orig_handle, label in zip(handles, labels):

            handler = self.get_legend_handler(legend_handler_map, orig_handle)

            if handler is None:

                _api.warn_external(

                             "Legend does not support handles for "

                             f"{type(orig_handle).__name__} "

                             "instances.\nA proxy artist may be used "

                             "instead.\nSee: https://matplotlib.org/"

                             "stable/users/explain/axes/legend_guide.html"

                             "#controlling-the-legend-entries")

                                                                      

                handle_list.append(None)

            else:

                textbox = TextArea(label, multilinebaseline=True,

                                   textprops=dict(

                                       verticalalignment='baseline',

                                       horizontalalignment='left',

                                       fontproperties=self.prop))

                handlebox = DrawingArea(width=self.handlelength * fontsize,

                                        height=height,

                                        xdescent=0., ydescent=descent)



                text_list.append(textbox._text)

                                                                       

                                         

                handle_list.append(handler.legend_artist(self, orig_handle,

                                                         fontsize, handlebox))

                handles_and_labels.append((handlebox, textbox))



        columnbox = []

                                                                              

                                                                        

                                                                              

                               

        for handles_and_labels_column in filter(

                len, np.array_split(handles_and_labels, self._ncols)):

                                                      

            itemboxes = [HPacker(pad=0,

                                 sep=self.handletextpad * fontsize,

                                 children=[h, t] if markerfirst else [t, h],

                                 align="baseline")

                         for h, t in handles_and_labels_column]

                            

            alignment = "baseline" if markerfirst else "right"

            columnbox.append(VPacker(pad=0,

                                     sep=self.labelspacing * fontsize,

                                     align=alignment,

                                     children=itemboxes))



        mode = "expand" if self._mode == "expand" else "fixed"

        sep = self.columnspacing * fontsize

        self._legend_handle_box = HPacker(pad=0,

                                          sep=sep, align="baseline",

                                          mode=mode,

                                          children=columnbox)

        self._legend_title_box = TextArea("")

        self._legend_box = VPacker(pad=self.borderpad * fontsize,

                                   sep=self.labelspacing * fontsize,

                                   align=self._alignment,

                                   children=[self._legend_title_box,

                                             self._legend_handle_box])

        self._legend_box.set_figure(self.get_figure(root=False))

        self._legend_box.axes = self.axes

        self.texts = text_list

        self.legend_handles = handle_list



    def _auto_legend_data(self, renderer):

        

        assert self.isaxes                                                   

        bboxes = []

        lines = []

        offsets = []

        for artist in self.parent._children:

            if isinstance(artist, Line2D):

                lines.append(

                    artist.get_transform().transform_path(artist.get_path()))

            elif isinstance(artist, Rectangle):

                bboxes.append(

                    artist.get_bbox().transformed(artist.get_data_transform()))

            elif isinstance(artist, Patch):

                lines.append(

                    artist.get_transform().transform_path(artist.get_path()))

            elif isinstance(artist, PolyCollection):

                lines.extend(artist.get_transform().transform_path(path)

                             for path in artist.get_paths())

            elif isinstance(artist, Collection):

                transform, transOffset, hoffsets, _ = artist._prepare_points()

                if len(hoffsets):

                    offsets.extend(transOffset.transform(hoffsets))

            elif isinstance(artist, Text):

                bboxes.append(artist.get_window_extent(renderer))



        return bboxes, lines, offsets



    def get_children(self):

                             

        return [self._legend_box, self.get_frame()]



    def get_frame(self):

        

        return self.legendPatch



    def get_lines(self):

        

        return [h for h in self.legend_handles if isinstance(h, Line2D)]



    def get_patches(self):

        

        return silent_list('Patch',

                           [h for h in self.legend_handles

                            if isinstance(h, Patch)])



    def get_texts(self):

        

        return silent_list('Text', self.texts)



    def set_alignment(self, alignment):

        

        _api.check_in_list(["center", "left", "right"], alignment=alignment)

        self._alignment = alignment

        self._legend_box.align = alignment



    def get_alignment(self):

        

        return self._legend_box.align



    def set_title(self, title, prop=None):

        

        self._legend_title_box._text.set_text(title)

        if title:

            self._legend_title_box._text.set_visible(True)

            self._legend_title_box.set_visible(True)

        else:

            self._legend_title_box._text.set_visible(False)

            self._legend_title_box.set_visible(False)



        if prop is not None:

            self._legend_title_box._text.set_fontproperties(prop)



        self.stale = True



    def get_title(self):

        

        return self._legend_title_box._text



    def get_window_extent(self, renderer=None):

                             

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        return self._legend_box.get_window_extent(renderer=renderer)



    def get_tightbbox(self, renderer=None):

                             

        return self._legend_box.get_window_extent(renderer)



    def get_frame_on(self):

        

        return self.legendPatch.get_visible()



    def set_frame_on(self, b):

        

        self.legendPatch.set_visible(b)

        self.stale = True



    draw_frame = set_frame_on                     



    def get_bbox_to_anchor(self):

        

        if self._bbox_to_anchor is None:

            return self.parent.bbox

        else:

            return self._bbox_to_anchor



    def set_bbox_to_anchor(self, bbox, transform=None):

        

        if bbox is None:

            self._bbox_to_anchor = None

            return

        elif isinstance(bbox, BboxBase):

            self._bbox_to_anchor = bbox

        else:

            try:

                l = len(bbox)

            except TypeError as err:

                raise ValueError(f"Invalid bbox: {bbox}") from err



            if l == 2:

                bbox = [bbox[0], bbox[1], 0, 0]



            self._bbox_to_anchor = Bbox.from_bounds(*bbox)



        if transform is None:

            transform = BboxTransformTo(self.parent.bbox)



        self._bbox_to_anchor = TransformedBbox(self._bbox_to_anchor,

                                               transform)

        self.stale = True



    def _get_anchored_bbox(self, loc, bbox, parentbbox, renderer):

        

        pad = self.borderaxespad * renderer.points_to_pixels(self._fontsize)

        return offsetbox._get_anchored_bbox(

            loc, bbox, parentbbox,

            pad, pad)



    def _find_best_position(self, width, height, renderer):

        

        assert self.isaxes                                                   



        start_time = time.perf_counter()



        bboxes, lines, offsets = self._auto_legend_data(renderer)



        bbox = Bbox.from_bounds(0, 0, width, height)



        candidates = []

        for idx in range(1, len(self.codes)):

            l, b = self._get_anchored_bbox(idx, bbox,

                                           self.get_bbox_to_anchor(),

                                           renderer)

            legendBox = Bbox.from_bounds(l, b, width, height)

                                                                             

                                                                          

            badness = (sum(legendBox.count_contains(line.vertices)

                           for line in lines)

                       + legendBox.count_contains(offsets)

                       + legendBox.count_overlaps(bboxes)

                       + sum(line.intersects_bbox(legendBox, filled=False)

                             for line in lines))

                                                                      

            candidates.append((badness, idx, (l, b)))

            if badness == 0:

                break



        _, _, (l, b) = min(candidates)



        if self._loc_used_default and time.perf_counter() - start_time > 1:

            _api.warn_external(

                'Creating legend with loc="best" can be slow with large '

                'amounts of data.')



        return l, b



    def contains(self, mouseevent):

        return self.legendPatch.contains(mouseevent)



    def set_draggable(self, state, use_blit=False, update='loc'):

        

        if state:

            if self._draggable is None:

                self._draggable = DraggableLegend(self,

                                                  use_blit,

                                                  update=update)

        else:

            if self._draggable is not None:

                self._draggable.disconnect()

            self._draggable = None

        return self._draggable



    def get_draggable(self):

        

        return self._draggable is not None





                                                                         

                

def _get_legend_handles(axs, legend_handler_map=None):

    

    handles_original = []

    for ax in axs:

        handles_original += [

            *(a for a in ax._children

              if isinstance(a, (Line2D, Patch, Collection, Text))),

            *ax.containers]

                                

        if hasattr(ax, 'parasites'):

            for axx in ax.parasites:

                handles_original += [

                    *(a for a in axx._children

                      if isinstance(a, (Line2D, Patch, Collection, Text))),

                    *axx.containers]



    handler_map = {**Legend.get_default_handler_map(),

                   **(legend_handler_map or {})}

    has_handler = Legend.get_legend_handler

    for handle in handles_original:

        label = handle.get_label()

        if label != '_nolegend_' and has_handler(handler_map, handle):

            yield handle

        elif (label and not label.startswith('_') and

                not has_handler(handler_map, handle)):

            _api.warn_external(

                             "Legend does not support handles for "

                             f"{type(handle).__name__} "

                             "instances.\nSee: https://matplotlib.org/stable/"

                             "tutorials/intermediate/legend_guide.html"

                             "#implementing-a-custom-legend-handler")

            continue





def _get_legend_handles_labels(axs, legend_handler_map=None):

    

    handles = []

    labels = []

    for handle in _get_legend_handles(axs, legend_handler_map):

        label = handle.get_label()

        if label and not label.startswith('_'):

            handles.append(handle)

            labels.append(label)

    return handles, labels





def _parse_legend_args(axs, *args, handles=None, labels=None, **kwargs):

    

    log = logging.getLogger(__name__)



    handlers = kwargs.get('handler_map')



    if (handles is not None or labels is not None) and args:

        raise TypeError("When passing handles and labels, they must both be "

                        "passed positionally or both as keywords.")



    if (hasattr(handles, "__len__") and

            hasattr(labels, "__len__") and

            len(handles) != len(labels)):

        _api.warn_external(f"Mismatched number of handles and labels: "

                           f"len(handles) = {len(handles)} "

                           f"len(labels) = {len(labels)}")

                                                                

    if handles and labels:

        handles, labels = zip(*zip(handles, labels))



    elif handles is not None and labels is None:

        labels = [handle.get_label() for handle in handles]



    elif labels is not None and handles is None:

                                                  

        handles = [handle for handle, label

                   in zip(_get_legend_handles(axs, handlers), labels)]



    elif len(args) == 0:                                                    

        handles, labels = _get_legend_handles_labels(axs, handlers)

        if not handles:

            _api.warn_external(

                "No artists with labels found to put in legend.  Note that "

                "artists whose label start with an underscore are ignored "

                "when legend() is called with no argument.")



    elif len(args) == 1:                                                           

        labels, = args

        if any(isinstance(l, Artist) for l in labels):

            raise TypeError("A single argument passed to legend() must be a "

                            "list of labels, but found an Artist in there.")



                                                  

        handles = [handle for handle, label

                   in zip(_get_legend_handles(axs, handlers), labels)]



    elif len(args) == 2:                                            

        handles, labels = args[:2]



    else:

        raise _api.nargs_error('legend', '0-2', len(args))



    return handles, labels, kwargs

