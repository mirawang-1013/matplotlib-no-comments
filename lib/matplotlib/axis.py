



import datetime

import functools

import logging

from numbers import Real

import warnings



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook

import matplotlib.artist as martist

import matplotlib.colors as mcolors

import matplotlib.lines as mlines

import matplotlib.scale as mscale

import matplotlib.text as mtext

import matplotlib.ticker as mticker

import matplotlib.transforms as mtransforms

import matplotlib.units as munits

from matplotlib.ticker import NullLocator



_log = logging.getLogger(__name__)



GRIDLINE_INTERPOLATION_STEPS = 180



                                                                 

                           

_line_inspector = martist.ArtistInspector(mlines.Line2D)

_line_param_names = _line_inspector.get_setters()

_line_param_aliases = [next(iter(d)) for d in _line_inspector.aliasd.values()]

_gridline_param_names = ['grid_' + name

                         for name in _line_param_names + _line_param_aliases]





class Tick(martist.Artist):

    

    def __init__(

        self, axes, loc, *,

        size=None,          

        width=None,

        color=None,

        tickdir=None,

        pad=None,

        labelsize=None,

        labelcolor=None,

        labelfontfamily=None,

        zorder=None,

        gridOn=None,                                                      

        tick1On=True,

        tick2On=True,

        label1On=True,

        label2On=False,

        major=True,

        labelrotation=0,

        labelrotation_mode=None,

        grid_color=None,

        grid_linestyle=None,

        grid_linewidth=None,

        grid_alpha=None,

        **kwargs,                                             

    ):

        

        super().__init__()



        if gridOn is None:

            which = mpl.rcParams['axes.grid.which']

            if major and which in ('both', 'major'):

                gridOn = mpl.rcParams['axes.grid']

            elif not major and which in ('both', 'minor'):

                gridOn = mpl.rcParams['axes.grid']

            else:

                gridOn = False



        self.set_figure(axes.get_figure(root=False))

        self.axes = axes



        self._loc = loc

        self._major = major



        name = self.__name__

        major_minor = "major" if major else "minor"

        self._size = mpl._val_or_rc(size, f"{name}.{major_minor}.size")

        self._width = mpl._val_or_rc(width, f"{name}.{major_minor}.width")

        self._base_pad = mpl._val_or_rc(pad, f"{name}.{major_minor}.pad")

        color = mpl._val_or_rc(color, f"{name}.color")

        labelcolor = mpl._val_or_rc(labelcolor, f"{name}.labelcolor")

        if cbook._str_equal(labelcolor, 'inherit'):

                                     

            labelcolor = mpl.rcParams[f"{name}.color"]

        labelsize = mpl._val_or_rc(labelsize, f"{name}.labelsize")



        self._set_labelrotation(labelrotation)



        if zorder is None:

            if major:

                zorder = mlines.Line2D.zorder + 0.01

            else:

                zorder = mlines.Line2D.zorder

        self._zorder = zorder



        grid_color = mpl._val_or_rc(

            grid_color,

            f"grid.{major_minor}.color",

            "grid.color",

        )

        grid_linestyle = mpl._val_or_rc(

            grid_linestyle,

            f"grid.{major_minor}.linestyle",

            "grid.linestyle",

        )

        grid_linewidth = mpl._val_or_rc(

            grid_linewidth,

            f"grid.{major_minor}.linewidth",

            "grid.linewidth",

        )

        if grid_alpha is None and not mcolors._has_alpha_channel(grid_color):

                                                                            

                                                                             

                                                                    

                                                                        

                                                                          

            grid_alpha = mpl._val_or_rc(

                                                                

                mpl.rcParams[f"grid.{major_minor}.alpha"],

                "grid.alpha",

            )



        grid_kw = {k[5:]: v for k, v in kwargs.items() if k != "rotation_mode"}



        self.tick1line = mlines.Line2D(

            [], [],

            color=color, linestyle="none", zorder=zorder, visible=tick1On,

            markeredgecolor=color, markersize=self._size, markeredgewidth=self._width,

        )

        self.tick2line = mlines.Line2D(

            [], [],

            color=color, linestyle="none", zorder=zorder, visible=tick2On,

            markeredgecolor=color, markersize=self._size, markeredgewidth=self._width,

        )

        self.gridline = mlines.Line2D(

            [], [],

            color=grid_color, alpha=grid_alpha, visible=gridOn,

            linestyle=grid_linestyle, linewidth=grid_linewidth, marker="",

            **grid_kw,

        )

        self.gridline.get_path()._interpolation_steps =
            GRIDLINE_INTERPOLATION_STEPS

        self.label1 = mtext.Text(

            np.nan, np.nan,

            fontsize=labelsize, color=labelcolor, visible=label1On,

            fontfamily=labelfontfamily, rotation=self._labelrotation[1],

            rotation_mode=labelrotation_mode)

        self.label2 = mtext.Text(

            np.nan, np.nan,

            fontsize=labelsize, color=labelcolor, visible=label2On,

            fontfamily=labelfontfamily, rotation=self._labelrotation[1],

            rotation_mode=labelrotation_mode)



        self._apply_tickdir(tickdir)



        for artist in [self.tick1line, self.tick2line, self.gridline,

                       self.label1, self.label2]:

            self._set_artist_props(artist)



        self.update_position(loc)



    def _set_labelrotation(self, labelrotation):

        if isinstance(labelrotation, str):

            mode = labelrotation

            angle = 0

        elif isinstance(labelrotation, (tuple, list)):

            mode, angle = labelrotation

        else:

            mode = 'default'

            angle = labelrotation

        _api.check_in_list(['auto', 'default'], labelrotation=mode)

        self._labelrotation = (mode, angle)



    @property

    def _pad(self):

        return self._base_pad + self.get_tick_padding()



    def _apply_tickdir(self, tickdir):

        

                                                                                        

                                                                                     

                                                                                       

                       

        tickdir = mpl._val_or_rc(tickdir, f'{self.__name__}.direction')

        _api.check_in_list(['in', 'out', 'inout'], tickdir=tickdir)

        self._tickdir = tickdir



    def get_tickdir(self):

        return self._tickdir



    def get_tick_padding(self):

        

        padding = {

            'in': 0.0,

            'inout': 0.5,

            'out': 1.0

        }

        return self._size * padding[self._tickdir]



    def get_children(self):

        children = [self.tick1line, self.tick2line,

                    self.gridline, self.label1, self.label2]

        return children



    def set_clip_path(self, path, transform=None):

                             

        super().set_clip_path(path, transform)

        self.gridline.set_clip_path(path, transform)

        self.stale = True



    def contains(self, mouseevent):

        

        return False, {}



    def set_pad(self, val):

        

        self._apply_params(pad=val)

        self.stale = True



    def get_pad(self):

        

        return self._base_pad



    def get_loc(self):

        

        return self._loc



    @martist.allow_rasterization

    def draw(self, renderer):

        if not self.get_visible():

            self.stale = False

            return

        renderer.open_group(self.__name__, gid=self.get_gid())

        for artist in [self.gridline, self.tick1line, self.tick2line,

                       self.label1, self.label2]:

            artist.draw(renderer)

        renderer.close_group(self.__name__)

        self.stale = False



    def set_url(self, url):

        

        super().set_url(url)

        self.label1.set_url(url)

        self.label2.set_url(url)

        self.stale = True



    def _set_artist_props(self, a):

        a.set_figure(self.get_figure(root=False))



    def get_view_interval(self):

        

        raise NotImplementedError('Derived must override')



    def _apply_params(self, **kwargs):

        for name, target in [("gridOn", self.gridline),

                             ("tick1On", self.tick1line),

                             ("tick2On", self.tick2line),

                             ("label1On", self.label1),

                             ("label2On", self.label2)]:

            if name in kwargs:

                target.set_visible(kwargs.pop(name))

        if any(k in kwargs for k in ['size', 'width', 'pad', 'tickdir']):

            self._size = kwargs.pop('size', self._size)

                                                                  

                                          

            self._width = kwargs.pop('width', self._width)

            self._base_pad = kwargs.pop('pad', self._base_pad)

                                                                            

                                         

            self._apply_tickdir(kwargs.pop('tickdir', self._tickdir))

            for line in (self.tick1line, self.tick2line):

                line.set_markersize(self._size)

                line.set_markeredgewidth(self._width)

                                                                 

            trans = self._get_text1_transform()[0]

            self.label1.set_transform(trans)

            trans = self._get_text2_transform()[0]

            self.label2.set_transform(trans)

        tick_kw = {k: v for k, v in kwargs.items() if k in ['color', 'zorder']}

        if 'color' in kwargs:

            tick_kw['markeredgecolor'] = kwargs['color']

        self.tick1line.set(**tick_kw)

        self.tick2line.set(**tick_kw)

        for k, v in tick_kw.items():

            setattr(self, '_' + k, v)



        if 'labelrotation' in kwargs:

            self._set_labelrotation(kwargs.pop('labelrotation'))

            self.label1.set(rotation=self._labelrotation[1])

            self.label2.set(rotation=self._labelrotation[1])



        label_kw = {k[5:]: v for k, v in kwargs.items()

                    if k in ['labelsize', 'labelcolor', 'labelfontfamily',

                             'labelrotation_mode']}

        self.label1.set(**label_kw)

        self.label2.set(**label_kw)



        grid_kw = {k[5:]: v for k, v in kwargs.items()

                   if k in _gridline_param_names}

        self.gridline.set(**grid_kw)



    def update_position(self, loc):

        

        raise NotImplementedError('Derived must override')



    def _get_text1_transform(self):

        raise NotImplementedError('Derived must override')



    def _get_text2_transform(self):

        raise NotImplementedError('Derived must override')





class XTick(Tick):

    

    __name__ = 'xtick'



    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

                                            

        ax = self.axes

        self.tick1line.set(

            data=([0], [0]), transform=ax.get_xaxis_transform("tick1"))

        self.tick2line.set(

            data=([0], [1]), transform=ax.get_xaxis_transform("tick2"))

        self.gridline.set(

            data=([0, 0], [0, 1]), transform=ax.get_xaxis_transform("grid"))

                                                       

        trans, va, ha = self._get_text1_transform()

        self.label1.set(

            x=0, y=0,

            verticalalignment=va, horizontalalignment=ha, transform=trans,

        )

        trans, va, ha = self._get_text2_transform()

        self.label2.set(

            x=0, y=1,

            verticalalignment=va, horizontalalignment=ha, transform=trans,

        )



    def _get_text1_transform(self):

        return self.axes.get_xaxis_text1_transform(self._pad)



    def _get_text2_transform(self):

        return self.axes.get_xaxis_text2_transform(self._pad)



    def _apply_tickdir(self, tickdir):

                             

        super()._apply_tickdir(tickdir)

        mark1, mark2 = {

            'out': (mlines.TICKDOWN, mlines.TICKUP),

            'in': (mlines.TICKUP, mlines.TICKDOWN),

            'inout': ('|', '|'),

        }[self._tickdir]

        self.tick1line.set_marker(mark1)

        self.tick2line.set_marker(mark2)



    def update_position(self, loc):

        

        self.tick1line.set_xdata((loc,))

        self.tick2line.set_xdata((loc,))

        self.gridline.set_xdata((loc,))

        self.label1.set_x(loc)

        self.label2.set_x(loc)

        self._loc = loc

        self.stale = True



    def get_view_interval(self):

                             

        return self.axes.viewLim.intervalx





class YTick(Tick):

    

    __name__ = 'ytick'



    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

                                            

        ax = self.axes

        self.tick1line.set(

            data=([0], [0]), transform=ax.get_yaxis_transform("tick1"))

        self.tick2line.set(

            data=([1], [0]), transform=ax.get_yaxis_transform("tick2"))

        self.gridline.set(

            data=([0, 1], [0, 0]), transform=ax.get_yaxis_transform("grid"))

                                                       

        trans, va, ha = self._get_text1_transform()

        self.label1.set(

            x=0, y=0,

            verticalalignment=va, horizontalalignment=ha, transform=trans,

        )

        trans, va, ha = self._get_text2_transform()

        self.label2.set(

            x=1, y=0,

            verticalalignment=va, horizontalalignment=ha, transform=trans,

        )



    def _get_text1_transform(self):

        return self.axes.get_yaxis_text1_transform(self._pad)



    def _get_text2_transform(self):

        return self.axes.get_yaxis_text2_transform(self._pad)



    def _apply_tickdir(self, tickdir):

                             

        super()._apply_tickdir(tickdir)

        mark1, mark2 = {

            'out': (mlines.TICKLEFT, mlines.TICKRIGHT),

            'in': (mlines.TICKRIGHT, mlines.TICKLEFT),

            'inout': ('_', '_'),

        }[self._tickdir]

        self.tick1line.set_marker(mark1)

        self.tick2line.set_marker(mark2)



    def update_position(self, loc):

        

        self.tick1line.set_ydata((loc,))

        self.tick2line.set_ydata((loc,))

        self.gridline.set_ydata((loc,))

        self.label1.set_y(loc)

        self.label2.set_y(loc)

        self._loc = loc

        self.stale = True



    def get_view_interval(self):

                             

        return self.axes.viewLim.intervaly





class Ticker:

    



    def __init__(self):

        self._locator = None

        self._formatter = None

        self._locator_is_default = True

        self._formatter_is_default = True



    @property

    def locator(self):

        return self._locator



    @locator.setter

    def locator(self, locator):

        if not isinstance(locator, mticker.Locator):

            raise TypeError('locator must be a subclass of '

                            'matplotlib.ticker.Locator')

        self._locator = locator



    @property

    def formatter(self):

        return self._formatter



    @formatter.setter

    def formatter(self, formatter):

        if not isinstance(formatter, mticker.Formatter):

            raise TypeError('formatter must be a subclass of '

                            'matplotlib.ticker.Formatter')

        self._formatter = formatter





class _LazyTickList:

    



    def __init__(self, major):

        self._major = major



    def __get__(self, instance, owner):

        if instance is None:

            return self

        else:

                                                                          

                                                                          

                                                                          

                                                                             

                                                                           

                                                                       

                                              

            if self._major:

                instance.majorTicks = []

                tick = instance._get_tick(major=True)

                instance.majorTicks = [tick]

                return instance.majorTicks

            else:

                instance.minorTicks = []

                tick = instance._get_tick(major=False)

                instance.minorTicks = [tick]

                return instance.minorTicks





class Axis(martist.Artist):

    

    OFFSETTEXTPAD = 3

                                                                            

                                                                            

    _tick_class = None

    converter = _api.deprecate_privatize_attribute(

                    "3.10",

                    alternative="get_converter and set_converter methods"

                )



    def __str__(self):

        return "{}({},{})".format(

            type(self).__name__, *self.axes.transAxes.transform((0, 0)))



    def __init__(self, axes, *, pickradius=15, clear=True):

        

        super().__init__()

        self._remove_overlapping_locs = True



        self.set_figure(axes.get_figure(root=False))



        self.isDefault_label = True



        self.axes = axes

        self.major = Ticker()

        self.minor = Ticker()

        self.callbacks = cbook.CallbackRegistry(signals=["units"])



        self._autolabelpos = True



        self.label = mtext.Text(

            np.nan, np.nan,

            fontsize=mpl.rcParams['axes.labelsize'],

            fontweight=mpl.rcParams['axes.labelweight'],

            color=mpl.rcParams['axes.labelcolor'],

        )                                          



        self._set_artist_props(self.label)

        self.offsetText = mtext.Text(np.nan, np.nan)

        self._set_artist_props(self.offsetText)



        self.labelpad = mpl.rcParams['axes.labelpad']



        self.pickradius = pickradius



                                                    

        self._major_tick_kw = dict()

        self._minor_tick_kw = dict()



        if clear:

            self.clear()

        else:

            self._converter = None

            self._converter_is_explicit = False

            self.units = None



        self._autoscale_on = True



    @property

    def isDefault_majloc(self):

        return self.major._locator_is_default



    @isDefault_majloc.setter

    def isDefault_majloc(self, value):

        self.major._locator_is_default = value



    @property

    def isDefault_majfmt(self):

        return self.major._formatter_is_default



    @isDefault_majfmt.setter

    def isDefault_majfmt(self, value):

        self.major._formatter_is_default = value



    @property

    def isDefault_minloc(self):

        return self.minor._locator_is_default



    @isDefault_minloc.setter

    def isDefault_minloc(self, value):

        self.minor._locator_is_default = value



    @property

    def isDefault_minfmt(self):

        return self.minor._formatter_is_default



    @isDefault_minfmt.setter

    def isDefault_minfmt(self, value):

        self.minor._formatter_is_default = value



    def _get_shared_axes(self):

        

        return self.axes._shared_axes[

            self._get_axis_name()].get_siblings(self.axes)



    def _get_shared_axis(self):

        

        name = self._get_axis_name()

        return [ax._axis_map[name] for ax in self._get_shared_axes()]



    def _get_axis_name(self):

        

        return next(name for name, axis in self.axes._axis_map.items()

                    if axis is self)



                                                                           

                                                                           

                                                                            

    majorTicks = _LazyTickList(major=True)

    minorTicks = _LazyTickList(major=False)



    def get_remove_overlapping_locs(self):

        return self._remove_overlapping_locs



    def set_remove_overlapping_locs(self, val):

        self._remove_overlapping_locs = bool(val)



    remove_overlapping_locs = property(

        get_remove_overlapping_locs, set_remove_overlapping_locs,

        doc=('If minor ticker locations that overlap with major '

             'ticker locations should be trimmed.'))



    def set_label_coords(self, x, y, transform=None):

        

        self._autolabelpos = False

        if transform is None:

            transform = self.axes.transAxes



        self.label.set_transform(transform)

        self.label.set_position((x, y))

        self.stale = True



    def get_transform(self):

        

        return self._scale.get_transform()



    def get_scale(self):

        

        return self._scale.name



    def _set_scale(self, value, **kwargs):

        if not isinstance(value, mscale.ScaleBase):

            self._scale = mscale.scale_factory(value, self, **kwargs)

        else:

            self._scale = value

        self._scale.set_default_locators_and_formatters(self)



        self.isDefault_majloc = True

        self.isDefault_minloc = True

        self.isDefault_majfmt = True

        self.isDefault_minfmt = True



                                                             

    def _set_axes_scale(self, value, **kwargs):

        

        name = self._get_axis_name()

        old_default_lims = (self.get_major_locator()

                            .nonsingular(-np.inf, np.inf))

        for ax in self._get_shared_axes():

            ax._axis_map[name]._set_scale(value, **kwargs)

            ax._update_transScale()

            ax.stale = True

        new_default_lims = (self.get_major_locator()

                            .nonsingular(-np.inf, np.inf))

        if old_default_lims != new_default_lims:

                                                                             

                                                                            

            self.axes.autoscale_view(

                **{f"scale{k}": k == name for k in self.axes._axis_names})



    def limit_range_for_scale(self, vmin, vmax):

        

        return self._scale.limit_range_for_scale(vmin, vmax, self.get_minpos())



    def _get_autoscale_on(self):

        

        return self._autoscale_on



    def _set_autoscale_on(self, b):

        

        if b is not None:

            self._autoscale_on = b



    def get_children(self):

        return [self.label, self.offsetText,

                *self.get_major_ticks(), *self.get_minor_ticks()]



    def _reset_major_tick_kw(self):

        self._major_tick_kw.clear()

        self._major_tick_kw['gridOn'] = (

                mpl.rcParams['axes.grid'] and

                mpl.rcParams['axes.grid.which'] in ('both', 'major'))



    def _reset_minor_tick_kw(self):

        self._minor_tick_kw.clear()

        self._minor_tick_kw['gridOn'] = (

                mpl.rcParams['axes.grid'] and

                mpl.rcParams['axes.grid.which'] in ('both', 'minor'))



    def clear(self):

        

        self.label._reset_visual_defaults()

                                                                    

                                                              

        self.label.set_color(mpl.rcParams['axes.labelcolor'])

        self.label.set_fontsize(mpl.rcParams['axes.labelsize'])

        self.label.set_fontweight(mpl.rcParams['axes.labelweight'])

        self.offsetText._reset_visual_defaults()

        self.labelpad = mpl.rcParams['axes.labelpad']



        self._init()



        self._set_scale('linear')



                                                                     

        self.callbacks = cbook.CallbackRegistry(signals=["units"])



                                  

        self._major_tick_kw['gridOn'] = (

                mpl.rcParams['axes.grid'] and

                mpl.rcParams['axes.grid.which'] in ('both', 'major'))

        self._minor_tick_kw['gridOn'] = (

                mpl.rcParams['axes.grid'] and

                mpl.rcParams['axes.grid.which'] in ('both', 'minor'))

        self.reset_ticks()



        self._converter = None

        self._converter_is_explicit = False

        self.units = None

        self.stale = True



    def reset_ticks(self):

        

                                      

        try:

            del self.majorTicks

        except AttributeError:

            pass

        try:

            del self.minorTicks

        except AttributeError:

            pass

        try:

            self.set_clip_path(self.axes.patch)

        except AttributeError:

            pass



    def minorticks_on(self):

        

        scale = self.get_scale()

        if scale == 'log':

            s = self._scale

            self.set_minor_locator(mticker.LogLocator(s.base, s.subs))

        elif scale == 'symlog':

            s = self._scale

            self.set_minor_locator(

                mticker.SymmetricalLogLocator(s._transform, s.subs))

        elif scale == 'asinh':

            s = self._scale

            self.set_minor_locator(

                    mticker.AsinhLocator(s.linear_width, base=s._base,

                                         subs=s._subs))

        elif scale == 'logit':

            self.set_minor_locator(mticker.LogitLocator(minor=True))

        else:

            self.set_minor_locator(mticker.AutoMinorLocator())



    def minorticks_off(self):

        

        self.set_minor_locator(mticker.NullLocator())



    def set_tick_params(self, which='major', reset=False, **kwargs):

        

        _api.check_in_list(['major', 'minor', 'both'], which=which)

        kwtrans = self._translate_tick_params(kwargs)



                                                                        

                                                      

        if reset:

            if which in ['major', 'both']:

                self._reset_major_tick_kw()

                self._major_tick_kw.update(kwtrans)

            if which in ['minor', 'both']:

                self._reset_minor_tick_kw()

                self._minor_tick_kw.update(kwtrans)

            self.reset_ticks()

        else:

            if which in ['major', 'both']:

                self._major_tick_kw.update(kwtrans)

                for tick in self.majorTicks:

                    tick._apply_params(**kwtrans)

            if which in ['minor', 'both']:

                self._minor_tick_kw.update(kwtrans)

                for tick in self.minorTicks:

                    tick._apply_params(**kwtrans)

                                                                   

            if 'label1On' in kwtrans or 'label2On' in kwtrans:

                self.offsetText.set_visible(

                    self._major_tick_kw.get('label1On', False)

                    or self._major_tick_kw.get('label2On', False))

            if 'labelcolor' in kwtrans:

                self.offsetText.set_color(kwtrans['labelcolor'])



        self.stale = True



    def get_tick_params(self, which='major'):

        

        _api.check_in_list(['major', 'minor'], which=which)

        if which == 'major':

            return self._translate_tick_params(

                self._major_tick_kw, reverse=True

            )

        return self._translate_tick_params(self._minor_tick_kw, reverse=True)



    @classmethod

    def _translate_tick_params(cls, kw, reverse=False):

        

        kw_ = {**kw}



                                                                         

        allowed_keys = [

            'size', 'width', 'color', 'tickdir', 'pad',

            'labelsize', 'labelcolor', 'labelfontfamily', 'zorder', 'gridOn',

            'tick1On', 'tick2On', 'label1On', 'label2On',

            'length', 'direction', 'left', 'bottom', 'right', 'top',

            'labelleft', 'labelbottom', 'labelright', 'labeltop',

            'labelrotation', 'labelrotation_mode',

            *_gridline_param_names]



        keymap = {

                                         

            'length': 'size',

            'direction': 'tickdir',

            'rotation': 'labelrotation',

            'rotation_mode': 'labelrotation_mode',

            'left': 'tick1On',

            'bottom': 'tick1On',

            'right': 'tick2On',

            'top': 'tick2On',

            'labelleft': 'label1On',

            'labelbottom': 'label1On',

            'labelright': 'label2On',

            'labeltop': 'label2On',

        }

        if reverse:

            kwtrans = {}

            is_x_axis = cls.axis_name == 'x'

            y_axis_keys = ['left', 'right', 'labelleft', 'labelright']

            for oldkey, newkey in keymap.items():

                if newkey in kw_:

                    if is_x_axis and oldkey in y_axis_keys:

                        continue

                    else:

                        kwtrans[oldkey] = kw_.pop(newkey)

        else:

            kwtrans = {

                newkey: kw_.pop(oldkey)

                for oldkey, newkey in keymap.items() if oldkey in kw_

            }

        if 'colors' in kw_:

            c = kw_.pop('colors')

            kwtrans['color'] = c

            kwtrans['labelcolor'] = c

                                                                  

        for key in kw_:

            if key not in allowed_keys:

                raise ValueError(

                    "keyword %s is not recognized; valid keywords are %s"

                    % (key, allowed_keys))

        kwtrans.update(kw_)

        return kwtrans



    def set_clip_path(self, path, transform=None):

        super().set_clip_path(path, transform)

        for child in self.majorTicks + self.minorTicks:

            child.set_clip_path(path, transform)

        self.stale = True



    def get_view_interval(self):

        

        raise NotImplementedError('Derived must override')



    def set_view_interval(self, vmin, vmax, ignore=False):

        

        raise NotImplementedError('Derived must override')



    def get_data_interval(self):

        

        raise NotImplementedError('Derived must override')



    def set_data_interval(self, vmin, vmax, ignore=False):

        

        raise NotImplementedError('Derived must override')



    def get_inverted(self):

        

        low, high = self.get_view_interval()

        return high < low



    def set_inverted(self, inverted):

        

        a, b = self.get_view_interval()

                                                                               

        self._set_lim(*sorted((a, b), reverse=bool(inverted)), auto=None)



    def set_default_intervals(self):

        

                                                                   

                                                                    

                                                                  

                                                             

                                                                

                                                            

                                                                   

                                                           



    def _set_lim(self, v0, v1, *, emit=True, auto):

        

        name = self._get_axis_name()



        self.axes._process_unit_info([(name, (v0, v1))], convert=False)

        v0 = self.axes._validate_converted_limits(v0, self.convert_units)

        v1 = self.axes._validate_converted_limits(v1, self.convert_units)



        if v0 is None or v1 is None:

                                                                             

                                                             

            old0, old1 = self.get_view_interval()

            if v0 is None:

                v0 = old0

            if v1 is None:

                v1 = old1



        if self.get_scale() == 'log' and (v0 <= 0 or v1 <= 0):

                                                                             

                                                             

            old0, old1 = self.get_view_interval()

            if v0 <= 0:

                _api.warn_external(f"Attempt to set non-positive {name}lim on "

                                   f"a log-scaled axis will be ignored.")

                v0 = old0

            if v1 <= 0:

                _api.warn_external(f"Attempt to set non-positive {name}lim on "

                                   f"a log-scaled axis will be ignored.")

                v1 = old1

        if v0 == v1:

            _api.warn_external(

                f"Attempting to set identical low and high {name}lims "

                f"makes transformation singular; automatically expanding.")

        reverse = bool(v0 > v1)                                                

        v0, v1 = self.get_major_locator().nonsingular(v0, v1)

        v0, v1 = self.limit_range_for_scale(v0, v1)

        v0, v1 = sorted([v0, v1], reverse=bool(reverse))



        self.set_view_interval(v0, v1, ignore=True)

                                                                           

        for ax in self._get_shared_axes():

            ax._stale_viewlims[name] = False

        self._set_autoscale_on(auto)



        if emit:

            self.axes.callbacks.process(f"{name}lim_changed", self.axes)

                                                                      

            for other in self._get_shared_axes():

                if other is self.axes:

                    continue

                other._axis_map[name]._set_lim(v0, v1, emit=False, auto=auto)

                if emit:

                    other.callbacks.process(f"{name}lim_changed", other)

                if ((other_fig := other.get_figure(root=False)) !=

                        self.get_figure(root=False)):

                    other_fig.canvas.draw_idle()



        self.stale = True

        return v0, v1



    def _set_artist_props(self, a):

        if a is None:

            return

        a.set_figure(self.get_figure(root=False))



    def _update_ticks(self):

        

        major_locs = self.get_majorticklocs()

        major_labels = self.major.formatter.format_ticks(major_locs)

        major_ticks = self.get_major_ticks(len(major_locs))

        for tick, loc, label in zip(major_ticks, major_locs, major_labels):

            tick.update_position(loc)

            tick.label1.set_text(label)

            tick.label2.set_text(label)

        minor_locs = self.get_minorticklocs()

        minor_labels = self.minor.formatter.format_ticks(minor_locs)

        minor_ticks = self.get_minor_ticks(len(minor_locs))

        for tick, loc, label in zip(minor_ticks, minor_locs, minor_labels):

            tick.update_position(loc)

            tick.label1.set_text(label)

            tick.label2.set_text(label)

        ticks = [*major_ticks, *minor_ticks]



        view_low, view_high = self.get_view_interval()

        if view_low > view_high:

            view_low, view_high = view_high, view_low



        if (hasattr(self, "axes") and self.axes.name == '3d'

                and mpl.rcParams['axes3d.automargin']):

                                                                             

                                                                            

                                                                         

                                                          

            margin = 0.019965277777777776

            delta = view_high - view_low

            view_high = view_high - delta * margin

            view_low = view_low + delta * margin



        interval_t = self.get_transform().transform([view_low, view_high])



        ticks_to_draw = []

        for tick in ticks:

            try:

                loc_t = self.get_transform().transform(tick.get_loc())

            except AssertionError:

                                                                      

                                                                          

                pass

            else:

                if mtransforms._interval_contains_close(interval_t, loc_t):

                    ticks_to_draw.append(tick)



        return ticks_to_draw



    def _get_ticklabel_bboxes(self, ticks, renderer):

        

        return ([tick.label1.get_window_extent(renderer)

                 for tick in ticks

                 if tick.label1.get_visible() and tick.label1.get_in_layout()],

                [tick.label2.get_window_extent(renderer)

                 for tick in ticks

                 if tick.label2.get_visible() and tick.label2.get_in_layout()])



    def get_tightbbox(self, renderer=None, *, for_layout_only=False):

        

        if not self.get_visible() or for_layout_only and not self.get_in_layout():

            return

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        ticks_to_draw = self._update_ticks()



        self._update_label_position(renderer)



                                                 

        tlb1, tlb2 = self._get_ticklabel_bboxes(ticks_to_draw, renderer)



        self._update_offset_text_position(tlb1, tlb2)

        self.offsetText.set_text(self.major.formatter.get_offset())



        bboxes = [

            *(a.get_window_extent(renderer)

              for a in [self.offsetText]

              if a.get_visible()),

            *tlb1, *tlb2,

        ]

                            

        if self.label.get_visible():

            bb = self.label.get_window_extent(renderer)

                                                                         

                                                                               

                                                        

            if for_layout_only:

                if self.axis_name == "x" and bb.width > 0:

                    bb.x0 = (bb.x0 + bb.x1) / 2 - 0.5

                    bb.x1 = bb.x0 + 1.0

                if self.axis_name == "y" and bb.height > 0:

                    bb.y0 = (bb.y0 + bb.y1) / 2 - 0.5

                    bb.y1 = bb.y0 + 1.0

            bboxes.append(bb)

        bboxes = [b for b in bboxes

                  if 0 < b.width < np.inf and 0 < b.height < np.inf]

        if bboxes:

            return mtransforms.Bbox.union(bboxes)

        else:

            return None



    def get_tick_padding(self):

        values = []

        if len(self.majorTicks):

            values.append(self.majorTicks[0].get_tick_padding())

        if len(self.minorTicks):

            values.append(self.minorTicks[0].get_tick_padding())

        return max(values, default=0)



    @martist.allow_rasterization

    def draw(self, renderer):

                             



        if not self.get_visible():

            return

        renderer.open_group(__name__, gid=self.get_gid())



        ticks_to_draw = self._update_ticks()

        tlb1, tlb2 = self._get_ticklabel_bboxes(ticks_to_draw, renderer)



        for tick in ticks_to_draw:

            tick.draw(renderer)



                                                                     

        self._update_label_position(renderer)

        self.label.draw(renderer)



        self._update_offset_text_position(tlb1, tlb2)

        self.offsetText.set_text(self.major.formatter.get_offset())

        self.offsetText.draw(renderer)



        renderer.close_group(__name__)

        self.stale = False



    def get_gridlines(self):

        

        ticks = self.get_major_ticks()

        return cbook.silent_list('Line2D gridline',

                                 [tick.gridline for tick in ticks])



    def set_label(self, s):

        

        raise RuntimeError(

            "A legend label cannot be assigned to an Axis. Did you mean to "

            "set the axis label via set_label_text()?")



    def get_label(self):

        

        return self.label



    def get_offset_text(self):

        

        return self.offsetText



    def get_pickradius(self):

        

        return self._pickradius



    def get_majorticklabels(self):

        

        self._update_ticks()

        ticks = self.get_major_ticks()

        labels1 = [tick.label1 for tick in ticks if tick.label1.get_visible()]

        labels2 = [tick.label2 for tick in ticks if tick.label2.get_visible()]

        return labels1 + labels2



    def get_minorticklabels(self):

        

        self._update_ticks()

        ticks = self.get_minor_ticks()

        labels1 = [tick.label1 for tick in ticks if tick.label1.get_visible()]

        labels2 = [tick.label2 for tick in ticks if tick.label2.get_visible()]

        return labels1 + labels2



    def get_ticklabels(self, minor=False, which=None):

        

        if which is not None:

            if which == 'minor':

                return self.get_minorticklabels()

            elif which == 'major':

                return self.get_majorticklabels()

            elif which == 'both':

                return self.get_majorticklabels() + self.get_minorticklabels()

            else:

                _api.check_in_list(['major', 'minor', 'both'], which=which)

        if minor:

            return self.get_minorticklabels()

        return self.get_majorticklabels()



    def get_majorticklines(self):

        

        lines = []

        ticks = self.get_major_ticks()

        for tick in ticks:

            lines.append(tick.tick1line)

            lines.append(tick.tick2line)

        return cbook.silent_list('Line2D ticklines', lines)



    def get_minorticklines(self):

        

        lines = []

        ticks = self.get_minor_ticks()

        for tick in ticks:

            lines.append(tick.tick1line)

            lines.append(tick.tick2line)

        return cbook.silent_list('Line2D ticklines', lines)



    def get_ticklines(self, minor=False):

        

        if minor:

            return self.get_minorticklines()

        return self.get_majorticklines()



    def get_majorticklocs(self):

        

        return self.major.locator()



    def get_minorticklocs(self):

        

                                                     

        minor_locs = np.asarray(self.minor.locator())

        if self.remove_overlapping_locs:

            major_locs = self.major.locator()

            transform = self._scale.get_transform()

            tr_minor_locs = transform.transform(minor_locs)

            tr_major_locs = transform.transform(major_locs)

            lo, hi = sorted(transform.transform(self.get_view_interval()))

                                                                            

                                  

            tol = (hi - lo) * 1e-5

            mask = np.isclose(tr_minor_locs[:, None], tr_major_locs[None, :],

                              atol=tol, rtol=0).any(axis=1)

            minor_locs = minor_locs[~mask]

        return minor_locs



    def get_ticklocs(self, *, minor=False):

        

        return self.get_minorticklocs() if minor else self.get_majorticklocs()



    def get_ticks_direction(self, minor=False):

        

        if minor:

            return np.array(

                [tick._tickdir for tick in self.get_minor_ticks()])

        else:

            return np.array(

                [tick._tickdir for tick in self.get_major_ticks()])



    def _get_tick(self, major):

        

        if self._tick_class is None:

            raise NotImplementedError(

                f"The Axis subclass {self.__class__.__name__} must define "

                "_tick_class or reimplement _get_tick()")

        tick_kw = self._major_tick_kw if major else self._minor_tick_kw

        return self._tick_class(self.axes, 0, major=major, **tick_kw)



    def _get_tick_label_size(self, axis_name):

        

        tick_kw = self._major_tick_kw

        size = tick_kw.get('labelsize',

                           mpl.rcParams[f'{axis_name}tick.labelsize'])

        return mtext.FontProperties(size=size).get_size_in_points()



    def _copy_tick_props(self, src, dest):

        

        if src is None or dest is None:

            return

        dest.label1.update_from(src.label1)

        dest.label2.update_from(src.label2)

        dest.tick1line.update_from(src.tick1line)

        dest.tick2line.update_from(src.tick2line)

        dest.gridline.update_from(src.gridline)

        dest.update_from(src)

        dest._loc = src._loc

        dest._size = src._size

        dest._width = src._width

        dest._base_pad = src._base_pad

        dest._labelrotation = src._labelrotation

        dest._zorder = src._zorder

        dest._tickdir = src._tickdir



    def get_label_text(self):

        

        return self.label.get_text()



    def get_major_locator(self):

        

        return self.major.locator



    def get_minor_locator(self):

        

        return self.minor.locator



    def get_major_formatter(self):

        

        return self.major.formatter



    def get_minor_formatter(self):

        

        return self.minor.formatter



    def get_major_ticks(self, numticks=None):

        

        if numticks is None:

            numticks = len(self.get_majorticklocs())



        while len(self.majorTicks) < numticks:

                                                                

            tick = self._get_tick(major=True)

            self.majorTicks.append(tick)

            self._copy_tick_props(self.majorTicks[0], tick)



        return self.majorTicks[:numticks]



    def get_minor_ticks(self, numticks=None):

        

        if numticks is None:

            numticks = len(self.get_minorticklocs())



        while len(self.minorTicks) < numticks:

                                                                

            tick = self._get_tick(major=False)

            self.minorTicks.append(tick)

            self._copy_tick_props(self.minorTicks[0], tick)



        return self.minorTicks[:numticks]



    def grid(self, visible=None, which='major', **kwargs):

        

        if kwargs:

            if visible is None:

                visible = True

            elif not visible:                                     

                _api.warn_external('First parameter to grid() is false, '

                                   'but line properties are supplied. The '

                                   'grid will be enabled.')

                visible = True

        which = which.lower()

        _api.check_in_list(['major', 'minor', 'both'], which=which)

        gridkw = {f'grid_{name}': value for name, value in kwargs.items()}

        if which in ['minor', 'both']:

            gridkw['gridOn'] = (not self._minor_tick_kw['gridOn']

                                if visible is None else visible)

            self.set_tick_params(which='minor', **gridkw)

        if which in ['major', 'both']:

            gridkw['gridOn'] = (not self._major_tick_kw['gridOn']

                                if visible is None else visible)

            self.set_tick_params(which='major', **gridkw)

        self.stale = True



    def update_units(self, data):

        

        if not self._converter_is_explicit:

            converter = munits.registry.get_converter(data)

        else:

            converter = self._converter



        if converter is None:

            return False



        neednew = self._converter != converter

        self._set_converter(converter)

        default = self._converter.default_units(data, self)

        if default is not None and self.units is None:

            self.set_units(default)



        elif neednew:

            self._update_axisinfo()

        self.stale = True

        return True



    def _update_axisinfo(self):

        

        if self._converter is None:

            return



        info = self._converter.axisinfo(self.units, self)



        if info is None:

            return

        if info.majloc is not None and
           self.major.locator != info.majloc and self.isDefault_majloc:

            self.set_major_locator(info.majloc)

            self.isDefault_majloc = True

        if info.minloc is not None and
           self.minor.locator != info.minloc and self.isDefault_minloc:

            self.set_minor_locator(info.minloc)

            self.isDefault_minloc = True

        if info.majfmt is not None and
           self.major.formatter != info.majfmt and self.isDefault_majfmt:

            self.set_major_formatter(info.majfmt)

            self.isDefault_majfmt = True

        if info.minfmt is not None and
           self.minor.formatter != info.minfmt and self.isDefault_minfmt:

            self.set_minor_formatter(info.minfmt)

            self.isDefault_minfmt = True

        if info.label is not None and self.isDefault_label:

            self.set_label_text(info.label)

            self.isDefault_label = True



        self.set_default_intervals()



    def have_units(self):

        return self._converter is not None or self.units is not None



    def convert_units(self, x):

                                                                           

        if munits._is_natively_supported(x):

            return x



        if self._converter is None:

            self._set_converter(munits.registry.get_converter(x))



        if self._converter is None:

            return x

        try:

            ret = self._converter.convert(x, self.units, self)

        except Exception as e:

            raise munits.ConversionError('Failed to convert value(s) to axis '

                                         f'units: {x!r}') from e

        return ret



    def get_converter(self):

        

        return self._converter



    def set_converter(self, converter):

        

        self._set_converter(converter)

        self._converter_is_explicit = True



    def _set_converter(self, converter):

        if self._converter is converter or self._converter == converter:

            return

        if self._converter_is_explicit:

            raise RuntimeError("Axis already has an explicit converter set")

        elif (

            self._converter is not None and

            not isinstance(converter, type(self._converter)) and

            not isinstance(self._converter, type(converter))

        ):

            _api.warn_external(

                "This axis already has a converter set and "

                "is updating to a potentially incompatible converter"

            )

        self._converter = converter



    def set_units(self, u):

        

        if u == self.units:

            return

        for axis in self._get_shared_axis():

            axis.units = u

            axis._update_axisinfo()

            axis.callbacks.process('units')

            axis.stale = True



    def get_units(self):

        

        return self.units



    def set_label_text(self, label, fontdict=None, **kwargs):

        

        self.isDefault_label = False

        self.label.set_text(label)

        if fontdict is not None:

            self.label.update(fontdict)

        self.label.update(kwargs)

        self.stale = True

        return self.label



    def set_major_formatter(self, formatter):

        

        self._set_formatter(formatter, self.major)



    def set_minor_formatter(self, formatter):

        

        self._set_formatter(formatter, self.minor)



    def _set_formatter(self, formatter, level):

        if isinstance(formatter, str):

            formatter = mticker.StrMethodFormatter(formatter)

                                                                        

                                                      

        elif (callable(formatter) and

              not isinstance(formatter, mticker.TickHelper)):

            formatter = mticker.FuncFormatter(formatter)

        else:

            _api.check_isinstance(mticker.Formatter, formatter=formatter)



        if (isinstance(formatter, mticker.FixedFormatter)

                and len(formatter.seq) > 0

                and not isinstance(level.locator, mticker.FixedLocator)):

            _api.warn_external('FixedFormatter should only be used together '

                               'with FixedLocator')



        if level == self.major:

            self.isDefault_majfmt = False

        else:

            self.isDefault_minfmt = False



        level.formatter = formatter

        formatter.set_axis(self)

        self.stale = True



    def set_major_locator(self, locator):

        

        _api.check_isinstance(mticker.Locator, locator=locator)

        self.isDefault_majloc = False

        self.major.locator = locator

        if self.major.formatter:

            self.major.formatter._set_locator(locator)

        locator.set_axis(self)

        self.stale = True



    def set_minor_locator(self, locator):

        

        _api.check_isinstance(mticker.Locator, locator=locator)

        self.isDefault_minloc = False

        self.minor.locator = locator

        if self.minor.formatter:

            self.minor.formatter._set_locator(locator)

        locator.set_axis(self)

        self.stale = True



    def set_pickradius(self, pickradius):

        

        if not isinstance(pickradius, Real) or pickradius < 0:

            raise ValueError("pick radius should be a distance")

        self._pickradius = pickradius



    pickradius = property(

        get_pickradius, set_pickradius, doc="The acceptance radius for "

        "containment tests. See also `.Axis.contains`.")



                                                                     

    @staticmethod

    def _format_with_dict(tickd, x, pos):

        return tickd.get(x, "")



    def set_ticklabels(self, labels, *, minor=False, fontdict=None, **kwargs):

        

        try:

            labels = [t.get_text() if hasattr(t, 'get_text') else t

                      for t in labels]

        except TypeError:

            raise TypeError(f"{labels:=} must be a sequence") from None

        locator = (self.get_minor_locator() if minor

                   else self.get_major_locator())

        if not labels:

                           

            formatter = mticker.NullFormatter()

        elif isinstance(locator, mticker.FixedLocator):

                                                                      

                                                                  

            if len(locator.locs) != len(labels) and len(labels) != 0:

                raise ValueError(

                    "The number of FixedLocator locations"

                    f" ({len(locator.locs)}), usually from a call to"

                    " set_ticks, does not match"

                    f" the number of labels ({len(labels)}).")

            tickd = {loc: lab for loc, lab in zip(locator.locs, labels)}

            func = functools.partial(self._format_with_dict, tickd)

            formatter = mticker.FuncFormatter(func)

        else:

            _api.warn_external(

                 "set_ticklabels() should only be used with a fixed number of "

                 "ticks, i.e. after set_ticks() or using a FixedLocator. "

                 "Otherwise, ticks may be mislabeled.")

            formatter = mticker.FixedFormatter(labels)



        with warnings.catch_warnings():

            warnings.filterwarnings(

                "ignore",

                message="FixedFormatter should only be used together with FixedLocator")

            if minor:

                self.set_minor_formatter(formatter)

                locs = self.get_minorticklocs()

                ticks = self.get_minor_ticks(len(locs))

            else:

                self.set_major_formatter(formatter)

                locs = self.get_majorticklocs()

                ticks = self.get_major_ticks(len(locs))



        ret = []

        if fontdict is not None:

            kwargs.update(fontdict)

        for pos, (loc, tick) in enumerate(zip(locs, ticks)):

            tick.update_position(loc)

            tick_label = formatter(loc, pos)

                              

            tick.label1.set_text(tick_label)

            tick.label1._internal_update(kwargs)

                              

            tick.label2.set_text(tick_label)

            tick.label2._internal_update(kwargs)

                                             

            if tick.label1.get_visible():

                ret.append(tick.label1)

            if tick.label2.get_visible():

                ret.append(tick.label2)



        self.stale = True

        return ret



    def _set_tick_locations(self, ticks, *, minor=False):

                                    



                                                                          

        ticks = self.convert_units(ticks)

        locator = mticker.FixedLocator(ticks)                         

        if len(ticks):

            for axis in self._get_shared_axis():

                                                                        

                axis.set_view_interval(min(ticks), max(ticks))

        self.axes.stale = True

        if minor:

            self.set_minor_locator(locator)

            return self.get_minor_ticks(len(ticks))

        else:

            self.set_major_locator(locator)

            return self.get_major_ticks(len(ticks))



    def set_ticks(self, ticks, labels=None, *, minor=False, **kwargs):

        

        if labels is None and kwargs:

            first_key = next(iter(kwargs))

            raise ValueError(

                f"Incorrect use of keyword argument {first_key!r}. Keyword arguments "

                "other than 'minor' modify the text labels and can only be used if "

                "'labels' are passed as well.")

        result = self._set_tick_locations(ticks, minor=minor)

        if labels is not None:

            self.set_ticklabels(labels, minor=minor, **kwargs)

        return result



    def _get_tick_boxes_siblings(self, renderer):

        

                                                                               

        name = self._get_axis_name()

        if name not in self.get_figure(root=False)._align_label_groups:

            return [], []

        grouper = self.get_figure(root=False)._align_label_groups[name]

        bboxes = []

        bboxes2 = []

                                                     

        for ax in grouper.get_siblings(self.axes):

            axis = ax._axis_map[name]

            ticks_to_draw = axis._update_ticks()

            tlb, tlb2 = axis._get_ticklabel_bboxes(ticks_to_draw, renderer)

            bboxes.extend(tlb)

            bboxes2.extend(tlb2)

        return bboxes, bboxes2



    def _update_label_position(self, renderer):

        

        raise NotImplementedError('Derived must override')



    def _update_offset_text_position(self, bboxes, bboxes2):

        

        raise NotImplementedError('Derived must override')



    def axis_date(self, tz=None):

        

                                                                            

                                                                              

                                            

        if isinstance(tz, str):

            import dateutil.tz

            tz = dateutil.tz.gettz(tz)

        self.update_units(datetime.datetime(2009, 1, 1, 0, 0, 0, 0, tz))



    def get_tick_space(self):

        

                                            

        raise NotImplementedError()



    def _get_ticks_position(self):

        

        representative_ticks = []

        if not isinstance(self.get_major_locator(), NullLocator):

            representative_ticks.append(self.majorTicks[0])

        if not isinstance(self.get_minor_locator(), NullLocator):

            representative_ticks.append(self.minorTicks[0])



        if all(tick.tick1line.get_visible()

               and not tick.tick2line.get_visible()

               and tick.label1.get_visible()

               and not tick.label2.get_visible()

               for tick in representative_ticks):

            return 1

        elif all(tick.tick2line.get_visible()

                 and not tick.tick1line.get_visible()

                 and tick.label2.get_visible()

                 and not tick.label1.get_visible()

                 for tick in representative_ticks):

            return 2

        elif all(tick.tick1line.get_visible()

                 and tick.tick2line.get_visible()

                 and tick.label1.get_visible()

                 and not tick.label2.get_visible()

                 for tick in representative_ticks):

            return "default"

        else:

            return "unknown"



    def get_label_position(self):

        

        return self.label_position



    def set_label_position(self, position):

        

        raise NotImplementedError()



    def get_minpos(self):

        raise NotImplementedError()





def _make_getset_interval(method_name, lim_name, attr_name):

    



    def getter(self):

                              

        return getattr(getattr(self.axes, lim_name), attr_name)



    def setter(self, vmin, vmax, ignore=False):

                              

        if ignore:

            setattr(getattr(self.axes, lim_name), attr_name, (vmin, vmax))

        else:

            oldmin, oldmax = getter(self)

            if oldmin < oldmax:

                setter(self, min(vmin, vmax, oldmin), max(vmin, vmax, oldmax),

                       ignore=True)

            else:

                setter(self, max(vmin, vmax, oldmin), min(vmin, vmax, oldmax),

                       ignore=True)

        self.stale = True



    getter.__name__ = f"get_{method_name}_interval"

    setter.__name__ = f"set_{method_name}_interval"



    return getter, setter





class XAxis(Axis):

    __name__ = 'xaxis'

    axis_name = 'x'                                         

    _tick_class = XTick



    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._init()



    def _init(self):

        

                                                                              

                                                                    

        self.label.set(

            x=0.5, y=0,

            verticalalignment='top', horizontalalignment='center',

            transform=mtransforms.blended_transform_factory(

                self.axes.transAxes, mtransforms.IdentityTransform()),

        )

        self.label_position = 'bottom'



        if mpl.rcParams['xtick.labelcolor'] == 'inherit':

            tick_color = mpl.rcParams['xtick.color']

        else:

            tick_color = mpl.rcParams['xtick.labelcolor']



        self.offsetText.set(

            x=1, y=0,

            verticalalignment='top', horizontalalignment='right',

            transform=mtransforms.blended_transform_factory(

                self.axes.transAxes, mtransforms.IdentityTransform()),

            fontsize=mpl.rcParams['xtick.labelsize'],

            color=tick_color

        )

        self.offset_text_position = 'bottom'



    def contains(self, mouseevent):

        

        if self._different_canvas(mouseevent):

            return False, {}

        x, y = mouseevent.x, mouseevent.y

        try:

            trans = self.axes.transAxes.inverted()

            xaxes, yaxes = trans.transform((x, y))

        except ValueError:

            return False, {}

        (l, b), (r, t) = self.axes.transAxes.transform([(0, 0), (1, 1)])

        inaxis = 0 <= xaxes <= 1 and (

            b - self._pickradius < y < b or

            t < y < t + self._pickradius)

        return inaxis, {}



    def set_label_position(self, position):

        

        self.label.set_verticalalignment(_api.check_getitem({

            'top': 'baseline', 'bottom': 'top',

        }, position=position))

        self.label_position = position

        self.stale = True



    def _update_label_position(self, renderer):

        

        if not self._autolabelpos:

            return



                                                           

                                                     

        bboxes, bboxes2 = self._get_tick_boxes_siblings(renderer=renderer)

        x, y = self.label.get_position()



        if self.label_position == 'bottom':

                                                                                       

            bbox = mtransforms.Bbox.union([

                *bboxes, self.axes.spines.get("bottom", self.axes).get_window_extent()])

            self.label.set_position(

                (x, bbox.y0 - self.labelpad * self.get_figure(root=True).dpi / 72))

        else:

                                                                                    

            bbox = mtransforms.Bbox.union([

                *bboxes2, self.axes.spines.get("top", self.axes).get_window_extent()])

            self.label.set_position(

                (x, bbox.y1 + self.labelpad * self.get_figure(root=True).dpi / 72))



    def _update_offset_text_position(self, bboxes, bboxes2):

        

        x, y = self.offsetText.get_position()

        if not hasattr(self, '_tick_position'):

            self._tick_position = 'bottom'

        if self._tick_position == 'bottom':

            if not len(bboxes):

                bottom = self.axes.bbox.ymin

            else:

                bbox = mtransforms.Bbox.union(bboxes)

                bottom = bbox.y0

            y = bottom - self.OFFSETTEXTPAD * self.get_figure(root=True).dpi / 72

        else:

            if not len(bboxes2):

                top = self.axes.bbox.ymax

            else:

                bbox = mtransforms.Bbox.union(bboxes2)

                top = bbox.y1

            y = top + self.OFFSETTEXTPAD * self.get_figure(root=True).dpi / 72

        self.offsetText.set_position((x, y))



    def set_ticks_position(self, position):

        

        if position == 'top':

            self.set_tick_params(which='both', top=True, labeltop=True,

                                 bottom=False, labelbottom=False)

            self._tick_position = 'top'

            self.offsetText.set_verticalalignment('bottom')

        elif position == 'bottom':

            self.set_tick_params(which='both', top=False, labeltop=False,

                                 bottom=True, labelbottom=True)

            self._tick_position = 'bottom'

            self.offsetText.set_verticalalignment('top')

        elif position == 'both':

            self.set_tick_params(which='both', top=True,

                                 bottom=True)

        elif position == 'none':

            self.set_tick_params(which='both', top=False,

                                 bottom=False)

        elif position == 'default':

            self.set_tick_params(which='both', top=True, labeltop=False,

                                 bottom=True, labelbottom=True)

            self._tick_position = 'bottom'

            self.offsetText.set_verticalalignment('top')

        else:

            _api.check_in_list(['top', 'bottom', 'both', 'default', 'none'],

                               position=position)

        self.stale = True



    def tick_top(self):

        

        label = True

        if 'label1On' in self._major_tick_kw:

            label = (self._major_tick_kw['label1On']

                     or self._major_tick_kw['label2On'])

        self.set_ticks_position('top')

                                                                           

        self.set_tick_params(which='both', labeltop=label)



    def tick_bottom(self):

        

        label = True

        if 'label1On' in self._major_tick_kw:

            label = (self._major_tick_kw['label1On']

                     or self._major_tick_kw['label2On'])

        self.set_ticks_position('bottom')

                                                                           

        self.set_tick_params(which='both', labelbottom=label)



    def get_ticks_position(self):

        

        return {1: "bottom", 2: "top",

                "default": "default", "unknown": "unknown"}[

                    self._get_ticks_position()]



    get_view_interval, set_view_interval = _make_getset_interval(

        "view", "viewLim", "intervalx")

    get_data_interval, set_data_interval = _make_getset_interval(

        "data", "dataLim", "intervalx")



    def get_minpos(self):

        return self.axes.dataLim.minposx



    def set_default_intervals(self):

                             

                                                                  

                               

        if (not self.axes.dataLim.mutatedx() and

                not self.axes.viewLim.mutatedx()):

            if self._converter is not None:

                info = self._converter.axisinfo(self.units, self)

                if info.default_limits is not None:

                    xmin, xmax = self.convert_units(info.default_limits)

                    self.axes.viewLim.intervalx = xmin, xmax

        self.stale = True



    def get_tick_space(self):

        ends = mtransforms.Bbox.unit().transformed(

            self.axes.transAxes - self.get_figure(root=False).dpi_scale_trans)

        length = ends.width * 72

                                                                      

                             

        size = self._get_tick_label_size('x') * 3

        if size > 0:

            return int(np.floor(length / size))

        else:

            return 2**31 - 1





class YAxis(Axis):

    __name__ = 'yaxis'

    axis_name = 'y'                                         

    _tick_class = YTick



    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._init()



    def _init(self):

        

                                                                              

                                                                    

        self.label.set(

            x=0, y=0.5,

            verticalalignment='bottom', horizontalalignment='center',

            rotation='vertical', rotation_mode='anchor',

            transform=mtransforms.blended_transform_factory(

                mtransforms.IdentityTransform(), self.axes.transAxes),

        )

        self.label_position = 'left'



        if mpl.rcParams['ytick.labelcolor'] == 'inherit':

            tick_color = mpl.rcParams['ytick.color']

        else:

            tick_color = mpl.rcParams['ytick.labelcolor']



                                                   

        self.offsetText.set(

            x=0, y=0.5,

            verticalalignment='baseline', horizontalalignment='left',

            transform=mtransforms.blended_transform_factory(

                self.axes.transAxes, mtransforms.IdentityTransform()),

            fontsize=mpl.rcParams['ytick.labelsize'],

            color=tick_color

        )

        self.offset_text_position = 'left'



    def contains(self, mouseevent):

                             

        if self._different_canvas(mouseevent):

            return False, {}

        x, y = mouseevent.x, mouseevent.y

        try:

            trans = self.axes.transAxes.inverted()

            xaxes, yaxes = trans.transform((x, y))

        except ValueError:

            return False, {}

        (l, b), (r, t) = self.axes.transAxes.transform([(0, 0), (1, 1)])

        inaxis = 0 <= yaxes <= 1 and (

            l - self._pickradius < x < l or

            r < x < r + self._pickradius)

        return inaxis, {}



    def set_label_position(self, position):

        

        self.label.set_rotation_mode('anchor')

        self.label.set_verticalalignment(_api.check_getitem({

            'left': 'bottom', 'right': 'top',

        }, position=position))

        self.label_position = position

        self.stale = True



    def _update_label_position(self, renderer):

        

        if not self._autolabelpos:

            return



                                                           

                                                     

        bboxes, bboxes2 = self._get_tick_boxes_siblings(renderer=renderer)

        x, y = self.label.get_position()



        if self.label_position == 'left':

                                                                                     

            bbox = mtransforms.Bbox.union([

                *bboxes, self.axes.spines.get("left", self.axes).get_window_extent()])

            self.label.set_position(

                (bbox.x0 - self.labelpad * self.get_figure(root=True).dpi / 72, y))

        else:

                                                                                      

            bbox = mtransforms.Bbox.union([

                *bboxes2, self.axes.spines.get("right", self.axes).get_window_extent()])

            self.label.set_position(

                (bbox.x1 + self.labelpad * self.get_figure(root=True).dpi / 72, y))



    def _update_offset_text_position(self, bboxes, bboxes2):

        

        x, _ = self.offsetText.get_position()

        if 'outline' in self.axes.spines:

                                         

            bbox = self.axes.spines['outline'].get_window_extent()

        else:

            bbox = self.axes.bbox

        top = bbox.ymax

        self.offsetText.set_position(

            (x, top + self.OFFSETTEXTPAD * self.get_figure(root=True).dpi / 72)

        )



    def set_offset_position(self, position):

        

        x, y = self.offsetText.get_position()

        x = _api.check_getitem({'left': 0, 'right': 1}, position=position)



        self.offsetText.set_ha(position)

        self.offsetText.set_position((x, y))

        self.stale = True



    def set_ticks_position(self, position):

        

        if position == 'right':

            self.set_tick_params(which='both', right=True, labelright=True,

                                 left=False, labelleft=False)

            self.set_offset_position(position)

        elif position == 'left':

            self.set_tick_params(which='both', right=False, labelright=False,

                                 left=True, labelleft=True)

            self.set_offset_position(position)

        elif position == 'both':

            self.set_tick_params(which='both', right=True,

                                 left=True)

        elif position == 'none':

            self.set_tick_params(which='both', right=False,

                                 left=False)

        elif position == 'default':

            self.set_tick_params(which='both', right=True, labelright=False,

                                 left=True, labelleft=True)

        else:

            _api.check_in_list(['left', 'right', 'both', 'default', 'none'],

                               position=position)

        self.stale = True



    def tick_right(self):

        

        label = True

        if 'label1On' in self._major_tick_kw:

            label = (self._major_tick_kw['label1On']

                     or self._major_tick_kw['label2On'])

        self.set_ticks_position('right')

                                                          

                        

        self.set_tick_params(which='both', labelright=label)



    def tick_left(self):

        

        label = True

        if 'label1On' in self._major_tick_kw:

            label = (self._major_tick_kw['label1On']

                     or self._major_tick_kw['label2On'])

        self.set_ticks_position('left')

                                                          

                        

        self.set_tick_params(which='both', labelleft=label)



    def get_ticks_position(self):

        

        return {1: "left", 2: "right",

                "default": "default", "unknown": "unknown"}[

                    self._get_ticks_position()]



    get_view_interval, set_view_interval = _make_getset_interval(

        "view", "viewLim", "intervaly")

    get_data_interval, set_data_interval = _make_getset_interval(

        "data", "dataLim", "intervaly")



    def get_minpos(self):

        return self.axes.dataLim.minposy



    def set_default_intervals(self):

                             

                                                                  

                               

        if (not self.axes.dataLim.mutatedy() and

                not self.axes.viewLim.mutatedy()):

            if self._converter is not None:

                info = self._converter.axisinfo(self.units, self)

                if info.default_limits is not None:

                    ymin, ymax = self.convert_units(info.default_limits)

                    self.axes.viewLim.intervaly = ymin, ymax

        self.stale = True



    def get_tick_space(self):

        ends = mtransforms.Bbox.unit().transformed(

            self.axes.transAxes - self.get_figure(root=False).dpi_scale_trans)

        length = ends.height * 72

                                                         

        size = self._get_tick_label_size('y') * 2

        if size > 0:

            return int(np.floor(length / size))

        else:

            return 2**31 - 1

