import functools

import itertools

import logging

import math

from numbers import Integral, Number, Real



import re

import numpy as np



import matplotlib as mpl

import matplotlib.category                                                    

import matplotlib.cbook as cbook

import matplotlib.collections as mcoll

import matplotlib.colorizer as mcolorizer

import matplotlib.colors as mcolors

import matplotlib.contour as mcontour

import matplotlib.dates                                                            

import matplotlib.image as mimage

import matplotlib.inset as minset

import matplotlib.legend as mlegend

import matplotlib.lines as mlines

import matplotlib.markers as mmarkers

import matplotlib.mlab as mlab

import matplotlib.patches as mpatches

import matplotlib.path as mpath

import matplotlib.quiver as mquiver

import matplotlib.stackplot as mstack

import matplotlib.streamplot as mstream

import matplotlib.table as mtable

import matplotlib.text as mtext

import matplotlib.ticker as mticker

import matplotlib.transforms as mtransforms

import matplotlib.tri as mtri

import matplotlib.units as munits

from matplotlib import _api, _docstring, _preprocess_data

from matplotlib.axes._base import (

    _AxesBase, _TransformedBoundsLocator, _process_plot_format)

from matplotlib.axes._secondary_axes import SecondaryAxis

from matplotlib.container import BarContainer, ErrorbarContainer, StemContainer

from matplotlib.transforms import _ScaledRotation



_log = logging.getLogger(__name__)





                                                                  

                                                         





def _make_axes_method(func):

    

    func.__qualname__ = f"Axes.{func.__name__}"

    return func





class _GroupedBarReturn:

    

    def __init__(self, bar_containers):

        self.bar_containers = bar_containers



    def remove(self):

        [b.remove() for b in self.bar_containers]





@_docstring.interpd

class Axes(_AxesBase):

    

                                   



    def get_title(self, loc="center"):

        

        titles = {'left': self._left_title,

                  'center': self.title,

                  'right': self._right_title}

        title = _api.check_getitem(titles, loc=loc.lower())

        return title.get_text()



    def set_title(self, label, fontdict=None, loc=None, pad=None, *, y=None,

                  **kwargs):

        

        loc = mpl._val_or_rc(loc, 'axes.titlelocation').lower()

        y = mpl._val_or_rc(y, 'axes.titley')

        if y is None:

            y = 1.0

        else:

            self._autotitlepos = False

        kwargs['y'] = y



        titles = {'left': self._left_title,

                  'center': self.title,

                  'right': self._right_title}

        title = _api.check_getitem(titles, loc=loc)

        default = {

            'fontsize': mpl.rcParams['axes.titlesize'],

            'fontweight': mpl.rcParams['axes.titleweight'],

            'verticalalignment': 'baseline',

            'horizontalalignment': loc}

        titlecolor = mpl.rcParams['axes.titlecolor']

        if not cbook._str_lower_equal(titlecolor, 'auto'):

            default["color"] = titlecolor

        self._set_title_offset_trans(float(mpl._val_or_rc(pad, 'axes.titlepad')))

        title.set_text(label)

        title.update(default)

        if fontdict is not None:

            title.update(fontdict)

        title._internal_update(kwargs)

        return title



    def get_legend_handles_labels(self, legend_handler_map=None):

        

                                 

        handles, labels = mlegend._get_legend_handles_labels(

            [self], legend_handler_map)

        return handles, labels



    @_docstring.interpd

    def legend(self, *args, **kwargs):

        

        handles, labels, kwargs = mlegend._parse_legend_args([self], *args, **kwargs)

        self.legend_ = mlegend.Legend(self, handles, labels, **kwargs)

        self.legend_._remove_method = self._remove_legend

        return self.legend_



    def _remove_legend(self, legend):

        self.legend_ = None



    def inset_axes(self, bounds, *, transform=None, zorder=5, **kwargs):

        

        if transform is None:

            transform = self.transAxes

        kwargs.setdefault('label', 'inset_axes')



                                                                   

        inset_locator = _TransformedBoundsLocator(bounds, transform)

        bounds = inset_locator(self, None).bounds

        fig = self.get_figure(root=False)

        projection_class, pkw = fig._process_projection_requirements(**kwargs)

        inset_ax = projection_class(fig, bounds, zorder=zorder, **pkw)



                                                                 

                                                              

        inset_ax.set_axes_locator(inset_locator)



        self.add_child_axes(inset_ax)



        return inset_ax



    @_docstring.interpd

    def indicate_inset(self, bounds=None, inset_ax=None, *, transform=None,

                       facecolor='none', edgecolor='0.5', alpha=0.5,

                       zorder=None, **kwargs):

        

                                                                          

                          

        self.apply_aspect()



        if transform is None:

            transform = self.transData

        kwargs.setdefault('label', '_indicate_inset')



        indicator_patch = minset.InsetIndicator(

            bounds, inset_ax=inset_ax,

            facecolor=facecolor, edgecolor=edgecolor, alpha=alpha,

            zorder=zorder, transform=transform, **kwargs)

        self.add_artist(indicator_patch)



        return indicator_patch



    def indicate_inset_zoom(self, inset_ax, **kwargs):

        



        return self.indicate_inset(None, inset_ax, **kwargs)



    @_docstring.interpd

    def secondary_xaxis(self, location, functions=None, *, transform=None, **kwargs):

        

        if not (location in ['top', 'bottom'] or isinstance(location, Real)):

            raise ValueError('secondary_xaxis location must be either '

                             'a float or "top"/"bottom"')



        secondary_ax = SecondaryAxis(self, 'x', location, functions,

                                     transform, **kwargs)

        self.add_child_axes(secondary_ax)

        return secondary_ax



    @_docstring.interpd

    def secondary_yaxis(self, location, functions=None, *, transform=None, **kwargs):

        

        if not (location in ['left', 'right'] or isinstance(location, Real)):

            raise ValueError('secondary_yaxis location must be either '

                             'a float or "left"/"right"')



        secondary_ax = SecondaryAxis(self, 'y', location, functions,

                                     transform, **kwargs)

        self.add_child_axes(secondary_ax)

        return secondary_ax



    @_docstring.interpd

    def text(self, x, y, s, fontdict=None, **kwargs):

        

        effective_kwargs = {

            'verticalalignment': 'baseline',

            'horizontalalignment': 'left',

            'transform': self.transData,

            'clip_on': False,

            **(fontdict if fontdict is not None else {}),

            **kwargs,

        }

        t = mtext.Text(x, y, text=s, **effective_kwargs)

        if t.get_clip_path() is None:

            t.set_clip_path(self.patch)

        self._add_text(t)

        return t



    @_docstring.interpd

    def annotate(self, text, xy, xytext=None, xycoords='data', textcoords=None,

                 arrowprops=None, annotation_clip=None, **kwargs):

                                                              

                                    

        a = mtext.Annotation(text, xy, xytext=xytext, xycoords=xycoords,

                             textcoords=textcoords, arrowprops=arrowprops,

                             annotation_clip=annotation_clip, **kwargs)

        a.set_transform(mtransforms.IdentityTransform())

        if kwargs.get('clip_on', False) and a.get_clip_path() is None:

            a.set_clip_path(self.patch)

        self._add_text(a)

        return a

    annotate.__doc__ = mtext.Annotation.__init__.__doc__

                        



    @_docstring.interpd

    def axhline(self, y=0, xmin=0, xmax=1, **kwargs):

        

        self._check_no_units([xmin, xmax], ['xmin', 'xmax'])

        if "transform" in kwargs:

            raise ValueError("'transform' is not allowed as a keyword "

                             "argument; axhline generates its own transform.")

        ymin, ymax = self.get_ybound()



                                                                       

        yy, = self._process_unit_info([("y", y)], kwargs)

        scaley = (yy < ymin) or (yy > ymax)



        trans = self.get_yaxis_transform(which='grid')

        l = mlines.Line2D([xmin, xmax], [y, y], transform=trans, **kwargs)

        self.add_line(l)

        l.get_path()._interpolation_steps = mpl.axis.GRIDLINE_INTERPOLATION_STEPS

        if scaley:

            self._request_autoscale_view("y")

        return l



    @_docstring.interpd

    def axvline(self, x=0, ymin=0, ymax=1, **kwargs):

        

        self._check_no_units([ymin, ymax], ['ymin', 'ymax'])

        if "transform" in kwargs:

            raise ValueError("'transform' is not allowed as a keyword "

                             "argument; axvline generates its own transform.")

        xmin, xmax = self.get_xbound()



                                                                       

        xx, = self._process_unit_info([("x", x)], kwargs)

        scalex = (xx < xmin) or (xx > xmax)



        trans = self.get_xaxis_transform(which='grid')

        l = mlines.Line2D([x, x], [ymin, ymax], transform=trans, **kwargs)

        self.add_line(l)

        l.get_path()._interpolation_steps = mpl.axis.GRIDLINE_INTERPOLATION_STEPS

        if scalex:

            self._request_autoscale_view("x")

        return l



    @staticmethod

    def _check_no_units(vals, names):

                                                           

        for val, name in zip(vals, names):

            if not munits._is_natively_supported(val):

                raise ValueError(f"{name} must be a single scalar value, "

                                 f"but got {val}")



    @_docstring.interpd

    def axline(self, xy1, xy2=None, *, slope=None, **kwargs):

        

        if slope is not None and (self.get_xscale() != 'linear' or

                                  self.get_yscale() != 'linear'):

            raise TypeError("'slope' cannot be used with non-linear scales")



        datalim = [xy1] if xy2 is None else [xy1, xy2]

        if "transform" in kwargs:

                                                                            

                                                 

            datalim = []



        line = mlines.AxLine(xy1, xy2, slope, **kwargs)

                                                            

        self._set_artist_props(line)

        if line.get_clip_path() is None:

            line.set_clip_path(self.patch)

        if not line.get_label():

            line.set_label(f"_child{len(self._children)}")

        self._children.append(line)

        line._remove_method = self._children.remove

        self.update_datalim(datalim)



        self._request_autoscale_view()

        return line



    @_docstring.interpd

    def axhspan(self, ymin, ymax, xmin=0, xmax=1, **kwargs):

        

                           

        self._check_no_units([xmin, xmax], ['xmin', 'xmax'])

        (ymin, ymax), = self._process_unit_info([("y", [ymin, ymax])], kwargs)



        p = mpatches.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, **kwargs)

        p.set_transform(self.get_yaxis_transform(which="grid"))

                                                                             

                                                                       

                                                       

        ix = self.dataLim.intervalx.copy()

        mx = self.dataLim.minposx

        self.add_patch(p)

        self.dataLim.intervalx = ix

        self.dataLim.minposx = mx

        p.get_path()._interpolation_steps = mpl.axis.GRIDLINE_INTERPOLATION_STEPS

        self._request_autoscale_view("y")

        return p



    @_docstring.interpd

    def axvspan(self, xmin, xmax, ymin=0, ymax=1, **kwargs):

        

                           

        self._check_no_units([ymin, ymax], ['ymin', 'ymax'])

        (xmin, xmax), = self._process_unit_info([("x", [xmin, xmax])], kwargs)



        p = mpatches.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, **kwargs)

        p.set_transform(self.get_xaxis_transform(which="grid"))

                                                                             

                                                                       

                                                       

        iy = self.dataLim.intervaly.copy()

        my = self.dataLim.minposy

        self.add_patch(p)

        self.dataLim.intervaly = iy

        self.dataLim.minposy = my

        p.get_path()._interpolation_steps = mpl.axis.GRIDLINE_INTERPOLATION_STEPS

        self._request_autoscale_view("x")

        return p



    @_api.make_keyword_only("3.10", "label")

    @_preprocess_data(replace_names=["y", "xmin", "xmax", "colors"],

                      label_namer="y")

    def hlines(self, y, xmin, xmax, colors=None, linestyles='solid',

               label='', **kwargs):

        



                                                                           

        xmin, xmax, y = self._process_unit_info(

            [("x", xmin), ("x", xmax), ("y", y)], kwargs)



        if not np.iterable(y):

            y = [y]

        if not np.iterable(xmin):

            xmin = [xmin]

        if not np.iterable(xmax):

            xmax = [xmax]



                                                     

        y, xmin, xmax = cbook._combine_masks(y, xmin, xmax)

        y = np.ravel(y)

        xmin = np.ravel(xmin)

        xmax = np.ravel(xmax)



        masked_verts = np.ma.empty((len(y), 2, 2))

        masked_verts[:, 0, 0] = xmin

        masked_verts[:, 0, 1] = y

        masked_verts[:, 1, 0] = xmax

        masked_verts[:, 1, 1] = y



        lines = mcoll.LineCollection(masked_verts, colors=colors,

                                     linestyles=linestyles, label=label)

        self.add_collection(lines, autolim=False)

        lines._internal_update(kwargs)



        if len(y) > 0:

                                                                             

                                                                              

                                                                          

            updatex = True

            updatey = True

            if self.name == "rectilinear":

                datalim = lines.get_datalim(self.transData)

                t = lines.get_transform()

                updatex, updatey = t.contains_branch_seperately(self.transData)

                minx = np.nanmin(datalim.xmin)

                maxx = np.nanmax(datalim.xmax)

                miny = np.nanmin(datalim.ymin)

                maxy = np.nanmax(datalim.ymax)

            else:

                minx = np.nanmin(masked_verts[..., 0])

                maxx = np.nanmax(masked_verts[..., 0])

                miny = np.nanmin(masked_verts[..., 1])

                maxy = np.nanmax(masked_verts[..., 1])



            corners = (minx, miny), (maxx, maxy)

            self.update_datalim(corners, updatex, updatey)

            self._request_autoscale_view()

        return lines



    @_api.make_keyword_only("3.10", "label")

    @_preprocess_data(replace_names=["x", "ymin", "ymax", "colors"],

                      label_namer="x")

    def vlines(self, x, ymin, ymax, colors=None, linestyles='solid',

               label='', **kwargs):

        



                                                                           

        x, ymin, ymax = self._process_unit_info(

            [("x", x), ("y", ymin), ("y", ymax)], kwargs)



        if not np.iterable(x):

            x = [x]

        if not np.iterable(ymin):

            ymin = [ymin]

        if not np.iterable(ymax):

            ymax = [ymax]



                                                     

        x, ymin, ymax = cbook._combine_masks(x, ymin, ymax)

        x = np.ravel(x)

        ymin = np.ravel(ymin)

        ymax = np.ravel(ymax)



        masked_verts = np.ma.empty((len(x), 2, 2))

        masked_verts[:, 0, 0] = x

        masked_verts[:, 0, 1] = ymin

        masked_verts[:, 1, 0] = x

        masked_verts[:, 1, 1] = ymax



        lines = mcoll.LineCollection(masked_verts, colors=colors,

                                     linestyles=linestyles, label=label)

        self.add_collection(lines, autolim=False)

        lines._internal_update(kwargs)



        if len(x) > 0:

                                                                             

                                                                              

                                                                          

            updatex = True

            updatey = True

            if self.name == "rectilinear":

                datalim = lines.get_datalim(self.transData)

                t = lines.get_transform()

                updatex, updatey = t.contains_branch_seperately(self.transData)

                minx = np.nanmin(datalim.xmin)

                maxx = np.nanmax(datalim.xmax)

                miny = np.nanmin(datalim.ymin)

                maxy = np.nanmax(datalim.ymax)

            else:

                minx = np.nanmin(masked_verts[..., 0])

                maxx = np.nanmax(masked_verts[..., 0])

                miny = np.nanmin(masked_verts[..., 1])

                maxy = np.nanmax(masked_verts[..., 1])



            corners = (minx, miny), (maxx, maxy)

            self.update_datalim(corners, updatex, updatey)

            self._request_autoscale_view()

        return lines



    @_api.make_keyword_only("3.10", "orientation")

    @_preprocess_data(replace_names=["positions", "lineoffsets",

                                     "linelengths", "linewidths",

                                     "colors", "linestyles"])

    @_docstring.interpd

    def eventplot(self, positions, orientation='horizontal', lineoffsets=1,

                  linelengths=1, linewidths=None, colors=None, alpha=None,

                  linestyles='solid', **kwargs):

        



        lineoffsets, linelengths = self._process_unit_info(

                [("y", lineoffsets), ("y", linelengths)], kwargs)



                                                               

        if not np.iterable(positions):

            positions = [positions]

        elif any(np.iterable(position) for position in positions):

            positions = [np.asanyarray(position) for position in positions]

        else:

            positions = [np.asanyarray(positions)]



        poss = []

        for position in positions:

            poss += self._process_unit_info([("x", position)], kwargs)

        positions = poss



                                                                               

                                                                          

        colors = cbook._local_over_kwdict(colors, kwargs, 'color')

        linewidths = cbook._local_over_kwdict(linewidths, kwargs, 'linewidth')

        linestyles = cbook._local_over_kwdict(linestyles, kwargs, 'linestyle')



        if not np.iterable(lineoffsets):

            lineoffsets = [lineoffsets]

        if not np.iterable(linelengths):

            linelengths = [linelengths]

        if not np.iterable(linewidths):

            linewidths = [linewidths]

        if not np.iterable(colors):

            colors = [colors]

        if not np.iterable(alpha):

            alpha = [alpha]

        if hasattr(linestyles, 'lower') or not np.iterable(linestyles):

            linestyles = [linestyles]



        lineoffsets = np.asarray(lineoffsets)

        linelengths = np.asarray(linelengths)

        linewidths = np.asarray(linewidths)



        if len(lineoffsets) == 0:

            raise ValueError('lineoffsets cannot be empty')

        if len(linelengths) == 0:

            raise ValueError('linelengths cannot be empty')

        if len(linestyles) == 0:

            raise ValueError('linestyles cannot be empty')

        if len(linewidths) == 0:

            raise ValueError('linewidths cannot be empty')

        if len(alpha) == 0:

            raise ValueError('alpha cannot be empty')

        if len(colors) == 0:

            colors = [None]

        try:

                                                                          

                                                                       

            colors = mcolors.to_rgba_array(colors)

        except ValueError:

                                                                       

                                                                    

                                                    

            pass



        if len(lineoffsets) == 1 and len(positions) != 1:

            lineoffsets = np.tile(lineoffsets, len(positions))

            lineoffsets[0] = 0

            lineoffsets = np.cumsum(lineoffsets)

        if len(linelengths) == 1:

            linelengths = np.tile(linelengths, len(positions))

        if len(linewidths) == 1:

            linewidths = np.tile(linewidths, len(positions))

        if len(colors) == 1:

            colors = list(colors) * len(positions)

        if len(alpha) == 1:

            alpha = list(alpha) * len(positions)

        if len(linestyles) == 1:

            linestyles = [linestyles] * len(positions)



        if len(lineoffsets) != len(positions):

            raise ValueError('lineoffsets and positions are unequal sized '

                             'sequences')

        if len(linelengths) != len(positions):

            raise ValueError('linelengths and positions are unequal sized '

                             'sequences')

        if len(linewidths) != len(positions):

            raise ValueError('linewidths and positions are unequal sized '

                             'sequences')

        if len(colors) != len(positions):

            raise ValueError('colors and positions are unequal sized '

                             'sequences')

        if len(alpha) != len(positions):

            raise ValueError('alpha and positions are unequal sized '

                             'sequences')

        if len(linestyles) != len(positions):

            raise ValueError('linestyles and positions are unequal sized '

                             'sequences')



        colls = []

        for position, lineoffset, linelength, linewidth, color, alpha_,
            linestyle in
                zip(positions, lineoffsets, linelengths, linewidths,

                    colors, alpha, linestyles):

            coll = mcoll.EventCollection(position,

                                         orientation=orientation,

                                         lineoffset=lineoffset,

                                         linelength=linelength,

                                         linewidth=linewidth,

                                         color=color,

                                         alpha=alpha_,

                                         linestyle=linestyle)

            self.add_collection(coll, autolim=False)

            coll._internal_update(kwargs)

            colls.append(coll)



        if len(positions) > 0:

                                

            min_max = [(np.min(_p), np.max(_p)) for _p in positions

                       if len(_p) > 0]

                                                                  

            if len(min_max) > 0:

                mins, maxes = zip(*min_max)

                minpos = np.min(mins)

                maxpos = np.max(maxes)



                minline = (lineoffsets - linelengths).min()

                maxline = (lineoffsets + linelengths).max()



                if orientation == "vertical":

                    corners = (minline, minpos), (maxline, maxpos)

                else:                

                    corners = (minpos, minline), (maxpos, maxline)

                self.update_datalim(corners)

                self._request_autoscale_view()



        return colls



                       



                                                            

                             

    @_docstring.interpd

    def plot(self, *args, scalex=True, scaley=True, data=None, **kwargs):

        

        kwargs = cbook.normalize_kwargs(kwargs, mlines.Line2D)

        lines = [*self._get_lines(self, *args, data=data, **kwargs)]

        for line in lines:

            self.add_line(line)

        if scalex:

            self._request_autoscale_view("x")

        if scaley:

            self._request_autoscale_view("y")

        return lines



                                                         

    @_docstring.interpd

    def loglog(self, *args, **kwargs):

        

        dx = {k: v for k, v in kwargs.items()

              if k in ['base', 'subs', 'nonpositive',

                       'basex', 'subsx', 'nonposx']}

        self.set_xscale('log', **dx)

        dy = {k: v for k, v in kwargs.items()

              if k in ['base', 'subs', 'nonpositive',

                       'basey', 'subsy', 'nonposy']}

        self.set_yscale('log', **dy)

        return self.plot(

            *args, **{k: v for k, v in kwargs.items() if k not in {*dx, *dy}})



                                                         

    @_docstring.interpd

    def semilogx(self, *args, **kwargs):

        

        d = {k: v for k, v in kwargs.items()

             if k in ['base', 'subs', 'nonpositive',

                      'basex', 'subsx', 'nonposx']}

        self.set_xscale('log', **d)

        return self.plot(

            *args, **{k: v for k, v in kwargs.items() if k not in d})



                                                         

    @_docstring.interpd

    def semilogy(self, *args, **kwargs):

        

        d = {k: v for k, v in kwargs.items()

             if k in ['base', 'subs', 'nonpositive',

                      'basey', 'subsy', 'nonposy']}

        self.set_yscale('log', **d)

        return self.plot(

            *args, **{k: v for k, v in kwargs.items() if k not in d})



    @_preprocess_data(replace_names=["x"], label_namer="x")

    def acorr(self, x, **kwargs):

        

        return self.xcorr(x, x, **kwargs)



    @_api.make_keyword_only("3.10", "normed")

    @_preprocess_data(replace_names=["x", "y"], label_namer="y")

    def xcorr(self, x, y, normed=True, detrend=mlab.detrend_none,

              usevlines=True, maxlags=10, **kwargs):

        

        Nx = len(x)

        if Nx != len(y):

            raise ValueError('x and y must be equal length')



        x = detrend(np.asarray(x))

        y = detrend(np.asarray(y))



        correls = np.correlate(x, y, mode="full")



        if normed:

            correls = correls / np.sqrt(np.dot(x, x) * np.dot(y, y))



        if maxlags is None:

            maxlags = Nx - 1



        if maxlags >= Nx or maxlags < 1:

            raise ValueError('maxlags must be None or strictly '

                             'positive < %d' % Nx)



        lags = np.arange(-maxlags, maxlags + 1)

        correls = correls[Nx - 1 - maxlags:Nx + maxlags]



        if usevlines:

            a = self.vlines(lags, [0], correls, **kwargs)

                                                                        

            kwargs.pop('label', '')

            b = self.axhline(**kwargs)

        else:

            kwargs.setdefault('marker', 'o')

            kwargs.setdefault('linestyle', 'None')

            a, = self.plot(lags, correls, **kwargs)

            b = None

        return lags, correls, a, b



                             



                                                         

    def step(self, x, y, *args, where='pre', data=None, **kwargs):

        

        _api.check_in_list(('pre', 'post', 'mid'), where=where)

        kwargs['drawstyle'] = 'steps-' + where

        return self.plot(x, y, *args, data=data, **kwargs)



    @staticmethod

    def _convert_dx(dx, x0, xconv, convert):

        



                                 

        assert type(xconv) is np.ndarray



        if xconv.size == 0:

                                                                  

            return convert(dx)



        try:

                                                            

                                              



                                                                 

                                                               

                                                       

                                                                         

                                                                       

                                                                   

                                

            try:

                x0 = cbook._safe_first_finite(x0)

            except (TypeError, IndexError, KeyError):

                pass



            try:

                x = cbook._safe_first_finite(xconv)

            except (TypeError, IndexError, KeyError):

                x = xconv



            delist = False

            if not np.iterable(dx):

                dx = [dx]

                delist = True

            dx = [convert(x0 + ddx) - x for ddx in dx]

            if delist:

                dx = dx[0]

        except (ValueError, TypeError, AttributeError):

                                                                       

                                                        

            dx = convert(dx)

        return dx



    def _parse_bar_color_args(self, kwargs):

        

        color = kwargs.pop('color', None)



        facecolor = kwargs.pop('facecolor', color)

        edgecolor = kwargs.pop('edgecolor', None)



        facecolor = (facecolor if facecolor is not None

                     else self._get_patches_for_fill.get_next_color())



        try:

            facecolor = mcolors.to_rgba_array(facecolor)

        except ValueError as err:

            raise ValueError(

                "'facecolor' or 'color' argument must be a valid color or "

                "sequence of colors."

            ) from err



        return facecolor, edgecolor



    @_preprocess_data()

    @_docstring.interpd

    def bar(self, x, height, width=0.8, bottom=None, *, align="center",

            **kwargs):

        

        kwargs = cbook.normalize_kwargs(kwargs, mpatches.Patch)

        facecolor, edgecolor = self._parse_bar_color_args(kwargs)



        linewidth = kwargs.pop('linewidth', None)

        hatch = kwargs.pop('hatch', None)



                                                                          

                                                                      

        xerr = kwargs.pop('xerr', None)

        yerr = kwargs.pop('yerr', None)

        error_kw = kwargs.pop('error_kw', None)

        error_kw = {} if error_kw is None else error_kw.copy()

        ezorder = error_kw.pop('zorder', None)

        if ezorder is None:

            ezorder = kwargs.get('zorder', None)

            if ezorder is not None:

                                                                          

                                                    

                ezorder += 0.01

        error_kw.setdefault('zorder', ezorder)

        ecolor = kwargs.pop('ecolor', 'k')

        capsize = kwargs.pop('capsize', mpl.rcParams["errorbar.capsize"])

        error_kw.setdefault('ecolor', ecolor)

        error_kw.setdefault('capsize', capsize)



                                                                           

                                                                      

                                                       

        orientation = kwargs.pop('orientation', 'vertical')

        _api.check_in_list(['vertical', 'horizontal'], orientation=orientation)

        log = kwargs.pop('log', False)

        label = kwargs.pop('label', '')

        tick_labels = kwargs.pop('tick_label', None)



        y = bottom                                

        if orientation == 'vertical':

            if y is None:

                y = 0

        else:              

            if x is None:

                x = 0



        if orientation == 'vertical':

                                                                        

                                                                             

                                                                                

            self._process_unit_info(

                [("x", x), ("y", y), ("y", height)], kwargs, convert=False)

            if log:

                self.set_yscale('log', nonpositive='clip')

        else:              

                                                                      

                                                                            

                                                                                

            self._process_unit_info(

                [("x", x), ("x", width), ("y", y)], kwargs, convert=False)

            if log:

                self.set_xscale('log', nonpositive='clip')



                                                                 

                              

        if self.xaxis is not None:

            x0 = x

            x = np.asarray(self.convert_xunits(x))

            width = self._convert_dx(width, x0, x, self.convert_xunits)

            if xerr is not None:

                xerr = self._convert_dx(xerr, x0, x, self.convert_xunits)

        if self.yaxis is not None:

            y0 = y

            y = np.asarray(self.convert_yunits(y))

            height = self._convert_dx(height, y0, y, self.convert_yunits)

            if yerr is not None:

                yerr = self._convert_dx(yerr, y0, y, self.convert_yunits)

        try:

            x, height, width, y, linewidth, hatch = np.broadcast_arrays(

                                         

                np.atleast_1d(x), height, width, y, linewidth, hatch

            )

        except ValueError as e:

            arg_map = {

                "arg 0": "'x'",

                "arg 1": "'height'",

                "arg 2": "'width'",

                "arg 3": "'y'",

                "arg 4": "'linewidth'",

                "arg 5": "'hatch'"

            }

            error_message = str(e)

            for arg, name in arg_map.items():

                error_message = error_message.replace(arg, name)

            if error_message != str(e):

                raise ValueError(error_message) from e

            else:

                raise



                                                                     

        if orientation == 'vertical':

            tick_label_axis = self.xaxis

            tick_label_position = x

        else:              

            tick_label_axis = self.yaxis

            tick_label_position = y



        if not isinstance(label, str) and np.iterable(label):

            bar_container_label = '_nolegend_'

            patch_labels = label

        else:

            bar_container_label = label

            patch_labels = ['_nolegend_'] * len(x)

        if len(patch_labels) != len(x):

            raise ValueError(f'number of labels ({len(patch_labels)}) '

                             f'does not match number of bars ({len(x)}).')



        linewidth = itertools.cycle(np.atleast_1d(linewidth))

        hatch = itertools.cycle(np.atleast_1d(hatch))

        facecolor = itertools.chain(itertools.cycle(facecolor),

                                                                  

                                    itertools.repeat('none'))

        if edgecolor is None:

            edgecolor = itertools.repeat(None)

        else:

            edgecolor = itertools.chain(

                itertools.cycle(mcolors.to_rgba_array(edgecolor)),

                                                  

                itertools.repeat('none'))



                                                           

                                             

        _api.check_in_list(['center', 'edge'], align=align)

        if align == 'center':

            if orientation == 'vertical':

                try:

                    left = x - width / 2

                except TypeError as e:

                    raise TypeError(f'the dtypes of parameters x ({x.dtype}) '

                                    f'and width ({width.dtype}) '

                                    f'are incompatible') from e

                bottom = y

            else:              

                try:

                    bottom = y - height / 2

                except TypeError as e:

                    raise TypeError(f'the dtypes of parameters y ({y.dtype}) '

                                    f'and height ({height.dtype}) '

                                    f'are incompatible') from e

                left = x

        else:        

            left = x

            bottom = y



        patches = []

        args = zip(left, bottom, width, height, facecolor, edgecolor, linewidth,

                   hatch, patch_labels)

        for l, b, w, h, c, e, lw, htch, lbl in args:

            r = mpatches.Rectangle(

                xy=(l, b), width=w, height=h,

                facecolor=c,

                edgecolor=e,

                linewidth=lw,

                label=lbl,

                hatch=htch,

                )

            r._internal_update(kwargs)

            r.get_path()._interpolation_steps = 100

            if orientation == 'vertical':

                r.sticky_edges.y.append(b)

            else:              

                r.sticky_edges.x.append(l)

            self.add_patch(r)

            patches.append(r)



        if xerr is not None or yerr is not None:

            if orientation == 'vertical':

                                                                           

                ex = [l + 0.5 * w for l, w in zip(left, width)]

                ey = [b + h for b, h in zip(bottom, height)]



            else:              

                                                                           

                ex = [l + w for l, w in zip(left, width)]

                ey = [b + 0.5 * h for b, h in zip(bottom, height)]



            error_kw.setdefault("label", '_nolegend_')



            errorbar = self.errorbar(ex, ey, yerr=yerr, xerr=xerr, fmt='none',

                                     **error_kw)

        else:

            errorbar = None



        self._request_autoscale_view()



        if orientation == 'vertical':

            datavalues = height

        else:              

            datavalues = width



        bar_container = BarContainer(patches, errorbar, datavalues=datavalues,

                                     orientation=orientation,

                                     label=bar_container_label)

        self.add_container(bar_container)



        if tick_labels is not None:

            tick_labels = np.broadcast_to(tick_labels, len(patches))

            tick_label_axis.set_ticks(tick_label_position)

            tick_label_axis.set_ticklabels(tick_labels)



        return bar_container



                                                        

    @_docstring.interpd

    def barh(self, y, width, height=0.8, left=None, *, align="center",

             data=None, **kwargs):

        

        kwargs.setdefault('orientation', 'horizontal')

        patches = self.bar(x=left, height=height, width=width, bottom=y,

                           align=align, data=data, **kwargs)

        return patches



    def bar_label(self, container, labels=None, *, fmt="%g", label_type="edge",

                  padding=0, **kwargs):

        

        for key in ['horizontalalignment', 'ha', 'verticalalignment', 'va']:

            if key in kwargs:

                raise ValueError(

                    f"Passing {key!r} to bar_label() is not supported.")



        a, b = self.yaxis.get_view_interval()

        y_inverted = a > b

        c, d = self.xaxis.get_view_interval()

        x_inverted = c > d



                                                                             

                                                                    

        def sign(x):

            return 1 if x >= 0 else -1



        _api.check_in_list(['edge', 'center'], label_type=label_type)



        bars = container.patches

        errorbar = container.errorbar

        datavalues = container.datavalues

        orientation = container.orientation



        if errorbar:

                                                                            

            lines = errorbar.lines                                            

            barlinecols = lines[2]                                             

            barlinecol = barlinecols[0]                                      

            errs = barlinecol.get_segments()

        else:

            errs = []



        if labels is None:

            labels = []



        annotations = []



        if np.iterable(padding):

                                               

            padding = np.asarray(padding)

            if len(padding) != len(bars):

                raise ValueError(

                    f"padding must be of length {len(bars)} when passed as a sequence")

        else:

                                               

            padding = [padding] * len(bars)



        for bar, err, dat, lbl, pad in itertools.zip_longest(

                bars, errs, datavalues, labels, padding

        ):

            (x0, y0), (x1, y1) = bar.get_bbox().get_points()

            xc, yc = (x0 + x1) / 2, (y0 + y1) / 2



            if orientation == "vertical":

                extrema = max(y0, y1) if dat >= 0 else min(y0, y1)

                length = abs(y0 - y1)

            else:              

                extrema = max(x0, x1) if dat >= 0 else min(x0, x1)

                length = abs(x0 - x1)



            if err is None or np.size(err) == 0:

                endpt = extrema

            elif orientation == "vertical":

                endpt = err[:, 1].max() if dat >= 0 else err[:, 1].min()

            else:              

                endpt = err[:, 0].max() if dat >= 0 else err[:, 0].min()



            if label_type == "center":

                value = sign(dat) * length

            else:        

                value = extrema



            if label_type == "center":

                xy = (0.5, 0.5)

                kwargs["xycoords"] = (

                    lambda r, b=bar:

                        mtransforms.Bbox.intersection(

                            b.get_window_extent(r), b.get_clip_box()

                        ) or mtransforms.Bbox.null()

                )

            else:        

                if orientation == "vertical":

                    xy = xc, endpt

                else:              

                    xy = endpt, yc



            if orientation == "vertical":

                y_direction = -1 if y_inverted else 1

                xytext = 0, y_direction * sign(dat) * pad

            else:              

                x_direction = -1 if x_inverted else 1

                xytext = x_direction * sign(dat) * pad, 0



            if label_type == "center":

                ha, va = "center", "center"

            else:        

                if orientation == "vertical":

                    ha = 'center'

                    if y_inverted:

                        va = 'top' if dat > 0 else 'bottom'                    

                    else:

                        va = 'top' if dat < 0 else 'bottom'                    

                else:              

                    if x_inverted:

                        ha = 'right' if dat > 0 else 'left'                    

                    else:

                        ha = 'right' if dat < 0 else 'left'                    

                    va = 'center'



            if np.isnan(dat):

                lbl = ''



            if lbl is None:

                if isinstance(fmt, str):

                    lbl = cbook._auto_format_str(fmt, value)

                elif callable(fmt):

                    lbl = fmt(value)

                else:

                    raise TypeError("fmt must be a str or callable")

            annotation = self.annotate(lbl,

                                       xy, xytext, textcoords="offset points",

                                       ha=ha, va=va, **kwargs)

            annotations.append(annotation)



        return annotations



    @_preprocess_data()

    @_docstring.interpd

    def broken_barh(self, xranges, yrange, align="bottom", **kwargs):

        

                                      

        xdata = cbook._safe_first_finite(xranges) if len(xranges) else None

        ydata = cbook._safe_first_finite(yrange) if len(yrange) else None

        self._process_unit_info(

            [("x", xdata), ("y", ydata)], kwargs, convert=False)



        vertices = []

        y0, dy = yrange



        _api.check_in_list(['bottom', 'center', 'top'], align=align)

        if align == "bottom":

            y0, y1 = self.convert_yunits((y0, y0 + dy))

        elif align == "center":

            y0, y1 = self.convert_yunits((y0 - dy/2, y0 + dy/2))

        else:

            y0, y1 = self.convert_yunits((y0 - dy, y0))



        for xr in xranges:                                                 

            try:

                x0, dx = xr

            except Exception:

                raise ValueError(

                    "each range in xrange must be a sequence with two "

                    "elements (i.e. xrange must be an (N, 2) array)") from None

            x0, x1 = self.convert_xunits((x0, x0 + dx))

            vertices.append([(x0, y0), (x0, y1), (x1, y1), (x1, y0)])



        col = mcoll.PolyCollection(np.array(vertices), **kwargs)

        self.add_collection(col)



        return col



    @_docstring.interpd

    def grouped_bar(self, heights, *, positions=None, group_spacing=1.5, bar_spacing=0,

                    tick_labels=None, labels=None, orientation="vertical", colors=None,

                    **kwargs):

        

        if cbook._is_pandas_dataframe(heights):

            if labels is None:

                labels = heights.columns.tolist()

            if tick_labels is None:

                tick_labels = heights.index.tolist()

            heights = heights.to_numpy().T

        elif hasattr(heights, 'keys'):        

            if labels is not None:

                raise ValueError("'labels' cannot be used if 'heights' is a mapping")

            labels = heights.keys()

            heights = list(heights.values())

        elif hasattr(heights, 'shape'):               

            heights = heights.T



        num_datasets = len(heights)

        num_groups = len(next(iter(heights)))                               



                                                                          

                                                 

        if not hasattr(heights, 'shape'):

            for i, dataset in enumerate(heights):

                if len(dataset) != num_groups:

                    raise ValueError(

                        "'heights' contains datasets with different number of "

                        f"elements. dataset 0 has {num_groups} elements but "

                        f"dataset {i} has {len(dataset)} elements."

                    )



        if positions is None:

            group_centers = np.arange(num_groups)

            group_distance = 1

        else:

            group_centers = np.asanyarray(positions)

            if len(group_centers) > 1:

                d = np.diff(group_centers)

                if not np.allclose(d, d.mean()):

                    raise ValueError("'positions' must be equidistant")

                group_distance = d[0]

            else:

                group_distance = 1



        _api.check_in_list(["vertical", "horizontal"], orientation=orientation)



        if colors is None:

            colors = itertools.cycle([None])

        else:

                                                                   

                                                                        

            colors = itertools.cycle(colors)



        bar_width = (group_distance /

                     (num_datasets + (num_datasets - 1) * bar_spacing + group_spacing))

        bar_spacing_abs = bar_spacing * bar_width

        margin_abs = 0.5 * group_spacing * bar_width



        if labels is None:

            labels = [None] * num_datasets

        else:

            assert len(labels) == num_datasets



                                                                                   

                                      

        bar_containers = []

        for i, (hs, label, color) in enumerate(zip(heights, labels, colors)):

            lefts = (group_centers - 0.5 * group_distance + margin_abs

                     + i * (bar_width + bar_spacing_abs))

            if orientation == "vertical":

                bc = self.bar(lefts, hs, width=bar_width, align="edge",

                              label=label, color=color, **kwargs)

            else:

                bc = self.barh(lefts, hs, height=bar_width, align="edge",

                               label=label, color=color, **kwargs)

            bar_containers.append(bc)



        if tick_labels is not None:

            if orientation == "vertical":

                self.xaxis.set_ticks(group_centers, labels=tick_labels)

            else:

                self.yaxis.set_ticks(group_centers, labels=tick_labels)



        return _GroupedBarReturn(bar_containers)



    @_preprocess_data()

    def stem(self, *args, linefmt=None, markerfmt=None, basefmt=None, bottom=0,

             label=None, orientation='vertical'):

        

        if not 1 <= len(args) <= 3:

            raise _api.nargs_error('stem', '1-3', len(args))

        _api.check_in_list(['horizontal', 'vertical'], orientation=orientation)



        if len(args) == 1:

            heads, = args

            locs = np.arange(len(heads))

            args = ()

        elif isinstance(args[1], str):

            heads, *args = args

            locs = np.arange(len(heads))

        else:

            locs, heads, *args = args



        if orientation == 'vertical':

            locs, heads = self._process_unit_info([("x", locs), ("y", heads)])

        else:              

            heads, locs = self._process_unit_info([("x", heads), ("y", locs)])



        heads = cbook._check_1d(heads)

        locs = cbook._check_1d(locs)



                             

        if linefmt is None:

            linefmt = args[0] if len(args) > 0 else "C0-"

        linestyle, linemarker, linecolor = _process_plot_format(linefmt)



                               

        if markerfmt is None:

                                                     

            markerfmt = "o"

        if markerfmt == '':

            markerfmt = ' '                                                 

        markerstyle, markermarker, markercolor = _process_plot_format(markerfmt)

        if markermarker is None:

            markermarker = 'o'

        if markerstyle is None:

            markerstyle = 'None'

        if markercolor is None:

            markercolor = linecolor



                                 

        if basefmt is None:

            basefmt = ("C2-" if mpl.rcParams["_internal.classic_mode"] else

                       "C3-")

        basestyle, basemarker, basecolor = _process_plot_format(basefmt)



                                                                           

        linestyle = mpl._val_or_rc(linestyle, 'lines.linestyle')

        xlines = self.vlines if orientation == "vertical" else self.hlines

        stemlines = xlines(

            locs, bottom, heads,

            colors=linecolor, linestyles=linestyle, label="_nolegend_")



        if orientation == 'horizontal':

            marker_x = heads

            marker_y = locs

            baseline_x = [bottom, bottom]

            baseline_y = [np.min(locs), np.max(locs)]

        else:

            marker_x = locs

            marker_y = heads

            baseline_x = [np.min(locs), np.max(locs)]

            baseline_y = [bottom, bottom]



        markerline, = self.plot(marker_x, marker_y,

                                color=markercolor, linestyle=markerstyle,

                                marker=markermarker, label="_nolegend_")



        baseline, = self.plot(baseline_x, baseline_y,

                              color=basecolor, linestyle=basestyle,

                              marker=basemarker, label="_nolegend_")

        baseline.get_path()._interpolation_steps =
            mpl.axis.GRIDLINE_INTERPOLATION_STEPS



        stem_container = StemContainer((markerline, stemlines, baseline),

                                       label=label)

        self.add_container(stem_container)

        return stem_container



    @_api.make_keyword_only("3.10", "explode")

    @_preprocess_data(replace_names=["x", "explode", "labels", "colors"])

    def pie(self, x, explode=None, labels=None, colors=None,

            autopct=None, pctdistance=0.6, shadow=False, labeldistance=1.1,

            startangle=0, radius=1, counterclock=True,

            wedgeprops=None, textprops=None, center=(0, 0),

            frame=False, rotatelabels=False, *, normalize=True, hatch=None):

        

        self.set_aspect('equal')

                                                                          

                                          

        x = np.asarray(x, np.float32)

        if x.ndim > 1:

            raise ValueError("x must be 1D")



        if np.any(x < 0):

            raise ValueError("Wedge sizes 'x' must be non negative values")



        if not np.all(np.isfinite(x)):

            raise ValueError('Wedge sizes must be finite numbers')



        sx = x.sum()



        if sx == 0:

            raise ValueError('All wedge sizes are zero')



        if normalize:

            x = x / sx

        elif sx > 1:

            raise ValueError('Cannot plot an unnormalized pie with sum(x) > 1')

        if labels is None:

            labels = [''] * len(x)

        if explode is None:

            explode = [0] * len(x)

        if len(x) != len(labels):

            raise ValueError(f"'labels' must be of length 'x', not {len(labels)}")

        if len(x) != len(explode):

            raise ValueError(f"'explode' must be of length 'x', not {len(explode)}")

        if colors is None:

            get_next_color = self._get_patches_for_fill.get_next_color

        else:

            color_cycle = itertools.cycle(colors)



            def get_next_color():

                return next(color_cycle)



        hatch_cycle = itertools.cycle(np.atleast_1d(hatch))



        _api.check_isinstance(Real, radius=radius, startangle=startangle)

        if radius <= 0:

            raise ValueError(f"'radius' must be a positive number, not {radius}")



                                                             

        theta1 = startangle / 360



        if wedgeprops is None:

            wedgeprops = {}

        if textprops is None:

            textprops = {}



        texts = []

        slices = []

        autotexts = []



        for frac, label, expl in zip(x, labels, explode):

            x, y = center

            theta2 = (theta1 + frac) if counterclock else (theta1 - frac)

            thetam = 2 * np.pi * 0.5 * (theta1 + theta2)

            x += expl * math.cos(thetam)

            y += expl * math.sin(thetam)



            w = mpatches.Wedge((x, y), radius, 360. * min(theta1, theta2),

                               360. * max(theta1, theta2),

                               facecolor=get_next_color(),

                               hatch=next(hatch_cycle),

                               clip_on=False,

                               label=label)

            w.set(**wedgeprops)

            slices.append(w)

            self.add_patch(w)



            if shadow:

                                                                              

                                                         

                shadow_dict = {'ox': -0.02, 'oy': -0.02, 'label': '_nolegend_'}

                if isinstance(shadow, dict):

                    shadow_dict.update(shadow)

                self.add_patch(mpatches.Shadow(w, **shadow_dict))



            if labeldistance is not None:

                xt = x + labeldistance * radius * math.cos(thetam)

                yt = y + labeldistance * radius * math.sin(thetam)

                label_alignment_h = 'left' if xt > 0 else 'right'

                label_alignment_v = 'center'

                label_rotation = 'horizontal'

                if rotatelabels:

                    label_alignment_v = 'bottom' if yt > 0 else 'top'

                    label_rotation = (np.rad2deg(thetam)

                                      + (0 if xt > 0 else 180))

                t = self.text(xt, yt, label,

                              clip_on=False,

                              horizontalalignment=label_alignment_h,

                              verticalalignment=label_alignment_v,

                              rotation=label_rotation,

                              size=mpl.rcParams['xtick.labelsize'])

                t.set(**textprops)

                texts.append(t)



            if autopct is not None:

                xt = x + pctdistance * radius * math.cos(thetam)

                yt = y + pctdistance * radius * math.sin(thetam)

                if isinstance(autopct, str):

                    s = autopct % (100. * frac)

                elif callable(autopct):

                    s = autopct(100. * frac)

                else:

                    raise TypeError(

                        'autopct must be callable or a format string')

                if mpl._val_or_rc(textprops.get("usetex"), "text.usetex"):

                                                                     

                    s = re.sub(r"([^\\])%", r"\1\\%", s)

                t = self.text(xt, yt, s,

                              clip_on=False,

                              horizontalalignment='center',

                              verticalalignment='center')

                t.set(**textprops)

                autotexts.append(t)



            theta1 = theta2



        if frame:

            self._request_autoscale_view()

        else:

            self.set(frame_on=False, xticks=[], yticks=[],

                     xlim=(-1.25 + center[0], 1.25 + center[0]),

                     ylim=(-1.25 + center[1], 1.25 + center[1]))



        if autopct is None:

            return slices, texts

        else:

            return slices, texts, autotexts



    @staticmethod

    def _errorevery_to_mask(x, errorevery):

        

        if isinstance(errorevery, Integral):

            errorevery = (0, errorevery)

        if isinstance(errorevery, tuple):

            if (len(errorevery) == 2 and

                    isinstance(errorevery[0], Integral) and

                    isinstance(errorevery[1], Integral)):

                errorevery = slice(errorevery[0], None, errorevery[1])

            else:

                raise ValueError(

                    f'{errorevery=!r} is a not a tuple of two integers')

        elif isinstance(errorevery, slice):

            pass

        elif not isinstance(errorevery, str) and np.iterable(errorevery):

            try:

                x[errorevery]                  

            except (ValueError, IndexError) as err:

                raise ValueError(

                    f"{errorevery=!r} is iterable but not a valid NumPy fancy "

                    "index to match 'xerr'/'yerr'") from err

        else:

            raise ValueError(f"{errorevery=!r} is not a recognized value")

        everymask = np.zeros(len(x), bool)

        everymask[errorevery] = True

        return everymask



    @_api.make_keyword_only("3.10", "ecolor")

    @_preprocess_data(replace_names=["x", "y", "xerr", "yerr"],

                      label_namer="y")

    @_docstring.interpd

    def errorbar(self, x, y, yerr=None, xerr=None,

                 fmt='', ecolor=None, elinewidth=None, capsize=None,

                 barsabove=False, lolims=False, uplims=False,

                 xlolims=False, xuplims=False, errorevery=1,

                 capthick=None, elinestyle=None,

                 **kwargs):

        

        kwargs = cbook.normalize_kwargs(kwargs, mlines.Line2D)

                                                                         

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        kwargs.setdefault('zorder', 2)



                                                   

        if not isinstance(x, np.ndarray):

            x = np.asarray(x, dtype=object)

        if not isinstance(y, np.ndarray):

            y = np.asarray(y, dtype=object)



        def _upcast_err(err):

            



            if (

                                                  

                    np.iterable(err) and

                                         

                    len(err) > 0 and

                                                                     

                                                                           

                                                                              

                            

                    isinstance(cbook._safe_first_finite(err), np.ndarray)

            ):

                                                   

                atype = type(cbook._safe_first_finite(err))

                                                                          

                if atype is np.ndarray:

                                                                    

                                                              

                    return np.asarray(err, dtype=object)

                                                                         

                                                                      

                return atype(err)

                                                  

            return np.asarray(err, dtype=object)



        if xerr is not None and not isinstance(xerr, np.ndarray):

            xerr = _upcast_err(xerr)

        if yerr is not None and not isinstance(yerr, np.ndarray):

            yerr = _upcast_err(yerr)

        x, y = np.atleast_1d(x, y)                                        

        if len(x) != len(y):

            raise ValueError("'x' and 'y' must have the same size")



        everymask = self._errorevery_to_mask(x, errorevery)



        label = kwargs.pop("label", None)

        kwargs['label'] = '_nolegend_'



                                                                              

                                                                              

                                                                              

                          

        (data_line, base_style), = self._get_lines._plot_args(

            self, (x, y) if fmt == '' else (x, y, fmt), kwargs, return_kwargs=True)



                                                                             

        if barsabove:

            data_line.set_zorder(kwargs['zorder'] - .1)

        else:

            data_line.set_zorder(kwargs['zorder'] + .1)



                                                                            

        if fmt.lower() != 'none':

            self.add_line(data_line)

        else:

            data_line = None

                                                                         

                                                                         

                       

            base_style.pop('color')

            if 'color' in kwargs:

                base_style['color'] = kwargs.pop('color')



        if 'color' not in base_style:

            base_style['color'] = 'C0'

        if ecolor is None:

            ecolor = base_style['color']



                                                                             

                                  

        for key in ['marker', 'markersize', 'markerfacecolor',

                    'markerfacecoloralt',

                    'markeredgewidth', 'markeredgecolor', 'markevery',

                    'linestyle', 'fillstyle', 'drawstyle', 'dash_capstyle',

                    'dash_joinstyle', 'solid_capstyle', 'solid_joinstyle',

                    'dashes']:

            base_style.pop(key, None)



                                                                  

        eb_lines_style = {**base_style, 'color': ecolor}



        if elinewidth is not None:

            eb_lines_style['linewidth'] = elinewidth

        elif 'linewidth' in kwargs:

            eb_lines_style['linewidth'] = kwargs['linewidth']



        for key in ('transform', 'alpha', 'zorder', 'rasterized'):

            if key in kwargs:

                eb_lines_style[key] = kwargs[key]



        if elinestyle is not None:

            eb_lines_style['linestyle'] = elinestyle



                                                    

        eb_cap_style = {**base_style, 'linestyle': 'none'}

        capsize = mpl._val_or_rc(capsize, "errorbar.capsize")

        if capsize > 0:

            eb_cap_style['markersize'] = 2. * capsize

        if capthick is not None:

            eb_cap_style['markeredgewidth'] = capthick



                                                         

                                                  

        for key in ('markeredgewidth', 'transform', 'alpha',

                    'zorder', 'rasterized'):

            if key in kwargs:

                eb_cap_style[key] = kwargs[key]

        eb_cap_style["markeredgecolor"] = ecolor



        barcols = []

        caplines = {'x': [], 'y': []}



                                   

        def apply_mask(arrays, mask):

            return [array[mask] for array in arrays]



                                                            

        for (dep_axis, dep, err, lolims, uplims, indep, lines_func,

             marker, lomarker, himarker) in [

                ("x", x, xerr, xlolims, xuplims, y, self.hlines,

                 "|", mlines.CARETRIGHTBASE, mlines.CARETLEFTBASE),

                ("y", y, yerr, lolims, uplims, x, self.vlines,

                 "_", mlines.CARETUPBASE, mlines.CARETDOWNBASE),

        ]:

            if err is None:

                continue

            lolims = np.broadcast_to(lolims, len(dep)).astype(bool)

            uplims = np.broadcast_to(uplims, len(dep)).astype(bool)

            try:

                np.broadcast_to(err, (2, len(dep)))

            except ValueError:

                raise ValueError(

                    f"'{dep_axis}err' (shape: {np.shape(err)}) must be a "

                    f"scalar or a 1D or (2, n) array-like whose shape matches "

                    f"'{dep_axis}' (shape: {np.shape(dep)})") from None

            if err.dtype is np.dtype(object) and np.any(err == None):              

                raise ValueError(

                    f"'{dep_axis}err' must not contain None. "

                    "Use NaN if you want to skip a value.")



                                                                        

                                                                      

                                                                             

                                                                       

                                                         

            if np.any((check := err[err == err]) < -check):

                raise ValueError(

                    f"'{dep_axis}err' must not contain negative values")

                          

                                                    

                                                                    

                                                         

            low, high = dep + np.vstack([-(1 - lolims), 1 - uplims]) * err

            barcols.append(lines_func(

                *apply_mask([indep, low, high], everymask), **eb_lines_style))

            if self.name == "polar" and dep_axis == "x":

                for b in barcols:

                    for p in b.get_paths():

                        p._interpolation_steps = 2

                                                                     

            nolims = ~(lolims | uplims)

            if nolims.any() and capsize > 0:

                indep_masked, lo_masked, hi_masked = apply_mask(

                    [indep, low, high], nolims & everymask)

                for lh_masked in [lo_masked, hi_masked]:

                                                                              

                                                                            

                                                                               

                    line = mlines.Line2D(indep_masked, indep_masked,

                                         marker=marker, **eb_cap_style)

                    line.set(**{f"{dep_axis}data": lh_masked})

                    caplines[dep_axis].append(line)

            for idx, (lims, hl) in enumerate([(lolims, high), (uplims, low)]):

                if not lims.any():

                    continue

                hlmarker = (

                    himarker

                    if self._axis_map[dep_axis].get_inverted() ^ idx

                    else lomarker)

                x_masked, y_masked, hl_masked = apply_mask(

                    [x, y, hl], lims & everymask)

                                                                       

                line = mlines.Line2D(x_masked, y_masked,

                                     marker=hlmarker, **eb_cap_style)

                line.set(**{f"{dep_axis}data": hl_masked})

                caplines[dep_axis].append(line)

                if capsize > 0:

                    caplines[dep_axis].append(mlines.Line2D(

                        x_masked, y_masked, marker=marker, **eb_cap_style))

        if self.name == 'polar':

            trans_shift = self.transShift

            for axis in caplines:

                for l in caplines[axis]:

                                                                       

                    for theta, r in zip(l.get_xdata(), l.get_ydata()):

                        rotation = _ScaledRotation(theta=theta, trans_shift=trans_shift)

                        if axis == 'y':

                            rotation += mtransforms.Affine2D().rotate(np.pi / 2)

                        ms = mmarkers.MarkerStyle(marker=marker,

                                                  transform=rotation)

                        self.add_line(mlines.Line2D([theta], [r], marker=ms,

                                                    **eb_cap_style))

        else:

            for axis in caplines:

                for l in caplines[axis]:

                    self.add_line(l)



        self._request_autoscale_view()

        caplines = caplines['x'] + caplines['y']

        errorbar_container = ErrorbarContainer(

            (data_line, tuple(caplines), tuple(barcols)),

            has_xerr=(xerr is not None), has_yerr=(yerr is not None),

            label=label)

        self.add_container(errorbar_container)



        return errorbar_container                           



    @_api.make_keyword_only("3.10", "notch")

    @_preprocess_data()

    @_api.rename_parameter("3.9", "labels", "tick_labels")

    def boxplot(self, x, notch=None, sym=None, vert=None,

                orientation='vertical', whis=None, positions=None,

                widths=None, patch_artist=None, bootstrap=None,

                usermedians=None, conf_intervals=None,

                meanline=None, showmeans=None, showcaps=None,

                showbox=None, showfliers=None, boxprops=None,

                tick_labels=None, flierprops=None, medianprops=None,

                meanprops=None, capprops=None, whiskerprops=None,

                manage_ticks=True, autorange=False, zorder=None,

                capwidths=None, label=None):

        



                                                

        whis = mpl._val_or_rc(whis, 'boxplot.whiskers')

        bootstrap = mpl._val_or_rc(bootstrap, 'boxplot.bootstrap')



        bxpstats = cbook.boxplot_stats(x, whis=whis, bootstrap=bootstrap,

                                       labels=tick_labels, autorange=autorange)

        notch = mpl._val_or_rc(notch, 'boxplot.notch')

        patch_artist = mpl._val_or_rc(patch_artist, 'boxplot.patchartist')

        meanline = mpl._val_or_rc(meanline, 'boxplot.meanline')

        showmeans = mpl._val_or_rc(showmeans, 'boxplot.showmeans')

        showcaps = mpl._val_or_rc(showcaps, 'boxplot.showcaps')

        showbox = mpl._val_or_rc(showbox, 'boxplot.showbox')

        showfliers = mpl._val_or_rc(showfliers, 'boxplot.showfliers')



        if boxprops is None:

            boxprops = {}

        if whiskerprops is None:

            whiskerprops = {}

        if capprops is None:

            capprops = {}

        if medianprops is None:

            medianprops = {}

        if meanprops is None:

            meanprops = {}

        if flierprops is None:

            flierprops = {}



        if patch_artist:

            boxprops['linestyle'] = 'solid'                            

            if 'color' in boxprops:

                boxprops['edgecolor'] = boxprops.pop('color')



                                                                    

                                                                     

                                                

                                                                            

                                 

        if sym is not None:

                                                             

                                                                            

                           

            if sym == '':

                                                                            

                flierprops = dict(linestyle='none', marker='', color='none')

                                                     

                showfliers = False

                                           

            else:

                                           

                                     

                _, marker, color = _process_plot_format(sym)

                                             

                if marker is not None:

                    flierprops['marker'] = marker

                                            

                if color is not None:

                                                                     

                                                                       

                                

                    flierprops['color'] = color

                    flierprops['markerfacecolor'] = color

                    flierprops['markeredgecolor'] = color



                                       

        if usermedians is not None:

            if (len(np.ravel(usermedians)) != len(bxpstats) or

                    np.shape(usermedians)[0] != len(bxpstats)):

                raise ValueError(

                    "'usermedians' and 'x' have different lengths")

            else:

                                               

                for stats, med in zip(bxpstats, usermedians):

                    if med is not None:

                        stats['med'] = med



        if conf_intervals is not None:

            if len(conf_intervals) != len(bxpstats):

                raise ValueError(

                    "'conf_intervals' and 'x' have different lengths")

            else:

                for stats, ci in zip(bxpstats, conf_intervals):

                    if ci is not None:

                        if len(ci) != 2:

                            raise ValueError('each confidence interval must '

                                             'have two values')

                        else:

                            if ci[0] is not None:

                                stats['cilo'] = ci[0]

                            if ci[1] is not None:

                                stats['cihi'] = ci[1]



        artists = self.bxp(bxpstats, positions=positions, widths=widths,

                           vert=vert, patch_artist=patch_artist,

                           shownotches=notch, showmeans=showmeans,

                           showcaps=showcaps, showbox=showbox,

                           boxprops=boxprops, flierprops=flierprops,

                           medianprops=medianprops, meanprops=meanprops,

                           meanline=meanline, showfliers=showfliers,

                           capprops=capprops, whiskerprops=whiskerprops,

                           manage_ticks=manage_ticks, zorder=zorder,

                           capwidths=capwidths, label=label,

                           orientation=orientation)

        return artists



    @_api.make_keyword_only("3.10", "widths")

    def bxp(self, bxpstats, positions=None, widths=None, vert=None,

            orientation='vertical', patch_artist=False, shownotches=False,

            showmeans=False, showcaps=True, showbox=True, showfliers=True,

            boxprops=None, whiskerprops=None, flierprops=None,

            medianprops=None, capprops=None, meanprops=None,

            meanline=False, manage_ticks=True, zorder=None,

            capwidths=None, label=None):

        

                                                      

        medianprops = {

            "solid_capstyle": "butt",

            "dash_capstyle": "butt",

            **(medianprops or {}),

        }

        meanprops = {

            "solid_capstyle": "butt",

            "dash_capstyle": "butt",

            **(meanprops or {}),

        }



                                       

        whiskers = []

        caps = []

        boxes = []

        medians = []

        means = []

        fliers = []



                                   

        datalabels = []



                                              

        if zorder is None:

            zorder = mlines.Line2D.zorder



        zdelta = 0.1



        def merge_kw_rc(subkey, explicit, zdelta=0, usemarker=True):

            d = {k.split('.')[-1]: v for k, v in mpl.rcParams.items()

                 if k.startswith(f'boxplot.{subkey}props')}

            d['zorder'] = zorder + zdelta

            if not usemarker:

                d['marker'] = ''

            d.update(cbook.normalize_kwargs(explicit, mlines.Line2D))

            return d



        box_kw = {

            'linestyle': mpl.rcParams['boxplot.boxprops.linestyle'],

            'linewidth': mpl.rcParams['boxplot.boxprops.linewidth'],

            'edgecolor': mpl.rcParams['boxplot.boxprops.color'],

            'facecolor': ('white' if mpl.rcParams['_internal.classic_mode']

                          else mpl.rcParams['patch.facecolor']),

            'zorder': zorder,

            **cbook.normalize_kwargs(boxprops, mpatches.PathPatch)

        } if patch_artist else merge_kw_rc('box', boxprops, usemarker=False)

        whisker_kw = merge_kw_rc('whisker', whiskerprops, usemarker=False)

        cap_kw = merge_kw_rc('cap', capprops, usemarker=False)

        flier_kw = merge_kw_rc('flier', flierprops)

        median_kw = merge_kw_rc('median', medianprops, zdelta, usemarker=False)

        mean_kw = merge_kw_rc('mean', meanprops, zdelta)

        removed_prop = 'marker' if meanline else 'linestyle'

                                                                             

        if meanprops is None or removed_prop not in meanprops:

            mean_kw[removed_prop] = ''



                                                                 

                                                                

                          

        if vert is None:

            vert = mpl.rcParams['boxplot.vertical']

        else:

            _api.warn_deprecated(

                "3.11",

                name="vert: bool",

                alternative="orientation: {'vertical', 'horizontal'}",

            )

        if vert is False:

            orientation = 'horizontal'

        _api.check_in_list(['horizontal', 'vertical'], orientation=orientation)



        if not mpl.rcParams['boxplot.vertical']:

            _api.warn_deprecated(

                "3.10",

                name='boxplot.vertical', obj_type="rcparam"

            )



                                      

        maybe_swap = slice(None) if orientation == 'vertical' else slice(None, None, -1)



        def do_plot(xs, ys, **kwargs):

            return self.plot(*[xs, ys][maybe_swap], **kwargs)[0]



        def do_patch(xs, ys, **kwargs):

            path = mpath.Path._create_closed(

                np.column_stack([xs, ys][maybe_swap]))

            patch = mpatches.PathPatch(path, **kwargs)

            self.add_artist(patch)

            return patch



                          

        N = len(bxpstats)

        datashape_message = ("List of boxplot statistics and `{0}` "

                             "values must have same the length")

                        

        if positions is None:

            positions = list(range(1, N + 1))

        elif len(positions) != N:

            raise ValueError(datashape_message.format("positions"))



        positions = np.array(positions)

        if len(positions) > 0 and not all(isinstance(p, Real) for p in positions):

            raise TypeError("positions should be an iterable of numbers")



               

        if widths is None:

            widths = [np.clip(0.15 * np.ptp(positions), 0.15, 0.5)] * N

        elif np.isscalar(widths):

            widths = [widths] * N

        elif len(widths) != N:

            raise ValueError(datashape_message.format("widths"))



                  

        if capwidths is None:

            capwidths = 0.5 * np.array(widths)

        elif np.isscalar(capwidths):

            capwidths = [capwidths] * N

        elif len(capwidths) != N:

            raise ValueError(datashape_message.format("capwidths"))



        for pos, width, stats, capwidth in zip(positions, widths, bxpstats,

                                               capwidths):

                                     

            datalabels.append(stats.get('label', pos))



                            

            whis_x = [pos, pos]

            whislo_y = [stats['q1'], stats['whislo']]

            whishi_y = [stats['q3'], stats['whishi']]

                        

            cap_left = pos - capwidth * 0.5

            cap_right = pos + capwidth * 0.5

            cap_x = [cap_left, cap_right]

            cap_lo = np.full(2, stats['whislo'])

            cap_hi = np.full(2, stats['whishi'])

                                   

            box_left = pos - width * 0.5

            box_right = pos + width * 0.5

            med_y = [stats['med'], stats['med']]

                           

            if shownotches:

                notch_left = pos - width * 0.25

                notch_right = pos + width * 0.25

                box_x = [box_left, box_right, box_right, notch_right,

                         box_right, box_right, box_left, box_left, notch_left,

                         box_left, box_left]

                box_y = [stats['q1'], stats['q1'], stats['cilo'],

                         stats['med'], stats['cihi'], stats['q3'],

                         stats['q3'], stats['cihi'], stats['med'],

                         stats['cilo'], stats['q1']]

                med_x = [notch_left, notch_right]

                         

            else:

                box_x = [box_left, box_right, box_right, box_left, box_left]

                box_y = [stats['q1'], stats['q1'], stats['q3'], stats['q3'],

                         stats['q1']]

                med_x = [box_left, box_right]



                                

            if showbox:

                do_box = do_patch if patch_artist else do_plot

                boxes.append(do_box(box_x, box_y, **box_kw))

                median_kw.setdefault('label', '_nolegend_')

                               

            whisker_kw.setdefault('label', '_nolegend_')

            whiskers.append(do_plot(whis_x, whislo_y, **whisker_kw))

            whiskers.append(do_plot(whis_x, whishi_y, **whisker_kw))

                                 

            if showcaps:

                cap_kw.setdefault('label', '_nolegend_')

                caps.append(do_plot(cap_x, cap_lo, **cap_kw))

                caps.append(do_plot(cap_x, cap_hi, **cap_kw))

                              

            medians.append(do_plot(med_x, med_y, **median_kw))

                                  

            if showmeans:

                if meanline:

                    means.append(do_plot(

                        [box_left, box_right], [stats['mean'], stats['mean']],

                        **mean_kw

                    ))

                else:

                    means.append(do_plot([pos], [stats['mean']], **mean_kw))

                                   

            if showfliers:

                flier_kw.setdefault('label', '_nolegend_')

                flier_x = np.full(len(stats['fliers']), pos, dtype=np.float64)

                flier_y = stats['fliers']

                fliers.append(do_plot(flier_x, flier_y, **flier_kw))



                           

        if label:

            box_or_med = boxes if showbox and patch_artist else medians

            if cbook.is_scalar_or_string(label):

                                                        

                box_or_med[0].set_label(label)

            else:                       

                if len(box_or_med) != len(label):

                    raise ValueError(datashape_message.format("label"))

                for artist, lbl in zip(box_or_med, label):

                    artist.set_label(lbl)



        if manage_ticks:

            axis_name = "x" if orientation == 'vertical' else "y"

            interval = getattr(self.dataLim, f"interval{axis_name}")

            axis = self._axis_map[axis_name]

            positions = axis.convert_units(positions)

                                                                         

                                                                        

                                                                             

                                                                              

                                                                            

                                                                           

            interval[:] = (min(interval[0], min(positions) - .5),

                           max(interval[1], max(positions) + .5))

            for median, position in zip(medians, positions):

                getattr(median.sticky_edges, axis_name).extend(

                    [position - .5, position + .5])

                                                                   

            locator = axis.get_major_locator()

            if not isinstance(axis.get_major_locator(),

                              mticker.FixedLocator):

                locator = mticker.FixedLocator([])

                axis.set_major_locator(locator)

            locator.locs = np.array([*locator.locs, *positions])

            formatter = axis.get_major_formatter()

            if not isinstance(axis.get_major_formatter(),

                              mticker.FixedFormatter):

                formatter = mticker.FixedFormatter([])

                axis.set_major_formatter(formatter)

            formatter.seq = [*formatter.seq, *datalabels]



            self._request_autoscale_view()



        return dict(whiskers=whiskers, caps=caps, boxes=boxes,

                    medians=medians, fliers=fliers, means=means)



    @staticmethod

    def _parse_scatter_color_args(c, edgecolors, kwargs, xsize,

                                  get_next_color_func):

        

        facecolors = kwargs.pop('facecolors', None)

        facecolors = kwargs.pop('facecolor', facecolors)

        edgecolors = kwargs.pop('edgecolor', edgecolors)



        kwcolor = kwargs.pop('color', None)



        if kwcolor is not None and c is not None:

            raise ValueError("Supply a 'c' argument or a 'color'"

                             " kwarg but not both; they differ but"

                             " their functionalities overlap.")



        if kwcolor is not None:

            try:

                mcolors.to_rgba_array(kwcolor)

            except ValueError as err:

                raise ValueError(

                    "'color' kwarg must be a color or sequence of color "

                    "specs.  For a sequence of values to be color-mapped, use "

                    "the 'c' argument instead.") from err

            if edgecolors is None:

                edgecolors = kwcolor

            if facecolors is None:

                facecolors = kwcolor



        if edgecolors is None and not mpl.rcParams['_internal.classic_mode']:

            edgecolors = mpl.rcParams['scatter.edgecolors']



                                                                             

        if c is not None and facecolors is not None:

            _api.warn_external(

                "You passed both c and facecolor/facecolors for the markers. "

                "c has precedence over facecolor/facecolors. "

                "This behavior may change in the future."

            )



        c_was_none = c is None

        if c is None:

            c = (facecolors if facecolors is not None

                 else "b" if mpl.rcParams['_internal.classic_mode']

                 else get_next_color_func())

        c_is_string_or_strings = (

            isinstance(c, str)

            or (np.iterable(c) and len(c) > 0

                and isinstance(cbook._safe_first_finite(c), str)))



        def invalid_shape_exception(csize, xsize):

            return ValueError(

                f"'c' argument has {csize} elements, which is inconsistent "

                f"with 'x' and 'y' with size {xsize}.")



        c_is_mapped = False                                  

        valid_shape = True                                  

        if not c_was_none and kwcolor is None and not c_is_string_or_strings:

            try:                                                    

                c = np.asanyarray(c, dtype=float)

            except ValueError:

                pass                                                          

            else:

                                                                         

                                                   

                if c.shape == (1, 4) or c.shape == (1, 3):

                    c_is_mapped = False

                    if c.size != xsize:

                        valid_shape = False

                                                                             

                                                                   

                elif c.size == xsize:

                    c = c.ravel()

                    c_is_mapped = True

                else:                                                    

                    if c.shape in ((3,), (4,)):

                        _api.warn_external(

                            "*c* argument looks like a single numeric RGB or "

                            "RGBA sequence, which should be avoided as value-"

                            "mapping will have precedence in case its length "

                            "matches with *x* & *y*.  Please use the *color* "

                            "keyword-argument or provide a 2D array "

                            "with a single row if you intend to specify "

                            "the same RGB or RGBA value for all points.")

                    valid_shape = False

        if not c_is_mapped:

            try:                                                   

                colors = mcolors.to_rgba_array(c)

            except (TypeError, ValueError) as err:

                if "RGBA values should be within 0-1 range" in str(err):

                    raise

                else:

                    if not valid_shape:

                        raise invalid_shape_exception(c.size, xsize) from err

                                                                               

                                                                              

                    raise ValueError(

                        f"'c' argument must be a color, a sequence of colors, "

                        f"or a sequence of numbers, not {c!r}") from err

            else:

                if len(colors) not in (0, 1, xsize):

                                                                          

                                                                             

                    raise invalid_shape_exception(len(colors), xsize)

        else:

            colors = None                                              

        return c, colors, edgecolors



    @_api.make_keyword_only("3.10", "marker")

    @_preprocess_data(replace_names=["x", "y", "s", "linewidths",

                                     "edgecolors", "c", "facecolor",

                                     "facecolors", "color"],

                      label_namer="y")

    @_docstring.interpd

    def scatter(self, x, y, s=None, c=None, marker=None, cmap=None, norm=None,

                vmin=None, vmax=None, alpha=None, linewidths=None, *,

                edgecolors=None, colorizer=None, plotnonfinite=False, **kwargs):

        

                                                         

                                              

        if edgecolors is not None:

            kwargs.update({'edgecolors': edgecolors})

        if linewidths is not None:

            kwargs.update({'linewidths': linewidths})



        kwargs = cbook.normalize_kwargs(kwargs, mcoll.Collection)

                                                        

                                                       

        linewidths = kwargs.pop('linewidth', None)

        edgecolors = kwargs.pop('edgecolor', None)

                                                                             

        x, y = self._process_unit_info([("x", x), ("y", y)], kwargs)

                                                            

                                                

        x = np.ma.ravel(x)

        y = np.ma.ravel(y)

        if x.size != y.size:

            raise ValueError("x and y must be the same size")



        if s is None:

            s = (20 if mpl.rcParams['_internal.classic_mode'] else

                 mpl.rcParams['lines.markersize'] ** 2.0)

        s = np.ma.ravel(s)

        if (len(s) not in (1, x.size) or

                (not np.issubdtype(s.dtype, np.floating) and

                 not np.issubdtype(s.dtype, np.integer))):

            raise ValueError(

                "s must be a scalar, "

                "or float array-like with the same size as x and y")



                                                                        

        orig_edgecolor = edgecolors

        if edgecolors is None:

            orig_edgecolor = kwargs.get('edgecolor', None)

        c, colors, edgecolors =
            self._parse_scatter_color_args(

                c, edgecolors, kwargs, x.size,

                get_next_color_func=self._get_patches_for_fill.get_next_color)



        if plotnonfinite and colors is None:

            c = np.ma.masked_invalid(c)

            x, y, s, edgecolors, linewidths =
                cbook._combine_masks(x, y, s, edgecolors, linewidths)

        else:

            x, y, s, c, colors, edgecolors, linewidths =
                cbook._combine_masks(

                    x, y, s, c, colors, edgecolors, linewidths)

                                                                    

        if (x.size in (3, 4)

                and np.ma.is_masked(edgecolors)

                and not np.ma.is_masked(orig_edgecolor)):

            edgecolors = edgecolors.data



        scales = s                                   



                                           

        marker = mpl._val_or_rc(marker, 'scatter.marker')



        if isinstance(marker, mmarkers.MarkerStyle):

            marker_obj = marker

        else:

            marker_obj = mmarkers.MarkerStyle(marker)

        if cbook._str_equal(marker_obj.get_marker(), ","):

            _api.warn_external(

                "The pixel maker ',' is not supported on scatter(); using "

                "a finite-sized square instead, which is not necessarily 1 pixel in "

                "size. Use the square marker 's' instead to suppress this warning."

            )



        path = marker_obj.get_path().transformed(

            marker_obj.get_transform())

        if not marker_obj.is_filled():

            if orig_edgecolor is not None:

                _api.warn_external(

                    f"You passed a edgecolor/edgecolors ({orig_edgecolor!r}) "

                    f"for an unfilled marker ({marker!r}).  Matplotlib is "

                    "ignoring the edgecolor in favor of the facecolor.  This "

                    "behavior may change in the future."

                )

                                                                   

                                                               

                                                                      

                     

             

                                                 

                                                                             

                                         

             

                                                                  

                           

            if marker_obj.get_fillstyle() == 'none':

                                                           

                edgecolors = colors

                                                                          

                                                                    

                                                              

                colors = 'none'

            else:

                                                                     

                         

                edgecolors = 'face'



            if linewidths is None:

                linewidths = mpl.rcParams['lines.linewidth']

            elif np.iterable(linewidths):

                linewidths = [

                    lw if lw is not None else mpl.rcParams['lines.linewidth']

                    for lw in linewidths]



        offsets = np.ma.column_stack([x, y])



        collection = mcoll.PathCollection(

            (path,), scales,

            facecolors=colors,

            edgecolors=edgecolors,

            linewidths=linewidths,

            offsets=offsets,

            offset_transform=kwargs.pop('transform', self.transData),

            alpha=alpha,

        )

        collection.set_transform(mtransforms.IdentityTransform())

        if colors is None:

            if colorizer:

                collection._set_colorizer_check_keywords(colorizer, cmap=cmap,

                                                         norm=norm, vmin=vmin,

                                                         vmax=vmax)

            else:

                collection.set_cmap(cmap)

                collection.set_norm(norm)

            collection.set_array(c)

            collection._scale_norm(norm, vmin, vmax)

        else:

            extra_kwargs = {

                    'cmap': cmap, 'norm': norm, 'vmin': vmin, 'vmax': vmax

                    }

            extra_keys = [k for k, v in extra_kwargs.items() if v is not None]

            if any(extra_keys):

                keys_str = ", ".join(f"'{k}'" for k in extra_keys)

                _api.warn_external(

                    "No data for colormapping provided via 'c'. "

                    f"Parameters {keys_str} will be ignored")

        collection._internal_update(kwargs)



                            

                                                   

                                                       

                                                    

                                    

        if mpl.rcParams['_internal.classic_mode']:

            if self._xmargin < 0.05 and x.size > 0:

                self.set_xmargin(0.05)

            if self._ymargin < 0.05 and x.size > 0:

                self.set_ymargin(0.05)



        self.add_collection(collection)



        return collection



    @_api.make_keyword_only("3.10", "gridsize")

    @_preprocess_data(replace_names=["x", "y", "C"], label_namer="y")

    @_docstring.interpd

    def hexbin(self, x, y, C=None, gridsize=100, bins=None,

               xscale='linear', yscale='linear', extent=None,

               cmap=None, norm=None, vmin=None, vmax=None,

               alpha=None, linewidths=None, edgecolors='face',

               reduce_C_function=np.mean, mincnt=None, marginals=False,

               colorizer=None, **kwargs):

        

        self._process_unit_info([("x", x), ("y", y)], kwargs, convert=False)



        x, y, C = cbook.delete_masked_points(x, y, C)



                                          

        if np.iterable(gridsize):

            nx, ny = gridsize

        else:

            nx = gridsize

            ny = int(nx / math.sqrt(3))

                                                  

        x = np.asarray(x, float)

        y = np.asarray(y, float)



                                                          

        tx = x

        ty = y



        if xscale == 'log':

            if np.any(x <= 0.0):

                raise ValueError(

                    "x contains non-positive values, so cannot be log-scaled")

            tx = np.log10(tx)

        if yscale == 'log':

            if np.any(y <= 0.0):

                raise ValueError(

                    "y contains non-positive values, so cannot be log-scaled")

            ty = np.log10(ty)

        if extent is not None:

            xmin, xmax, ymin, ymax = extent

            if xmin > xmax:

                raise ValueError("In extent, xmax must be greater than xmin")

            if ymin > ymax:

                raise ValueError("In extent, ymax must be greater than ymin")

        else:

            xmin, xmax = (tx.min(), tx.max()) if len(x) else (0, 1)

            ymin, ymax = (ty.min(), ty.max()) if len(y) else (0, 1)



                                                                          

            xmin, xmax = mtransforms.nonsingular(xmin, xmax, expander=0.1)

            ymin, ymax = mtransforms.nonsingular(ymin, ymax, expander=0.1)



        nx1 = nx + 1

        ny1 = ny + 1

        nx2 = nx

        ny2 = ny

        n = nx1 * ny1 + nx2 * ny2



                                                                        

                                                                   

        padding = 1.e-9 * (xmax - xmin)

        xmin -= padding

        xmax += padding

        sx = (xmax - xmin) / nx

        sy = (ymax - ymin) / ny

                                                 

        ix = (tx - xmin) / sx

        iy = (ty - ymin) / sy

        ix1 = np.round(ix).astype(int)

        iy1 = np.round(iy).astype(int)

        ix2 = np.floor(ix).astype(int)

        iy2 = np.floor(iy).astype(int)

                                                                              

        i1 = np.where((0 <= ix1) & (ix1 < nx1) & (0 <= iy1) & (iy1 < ny1),

                      ix1 * ny1 + iy1 + 1, 0)

        i2 = np.where((0 <= ix2) & (ix2 < nx2) & (0 <= iy2) & (iy2 < ny2),

                      ix2 * ny2 + iy2 + 1, 0)



        d1 = (ix - ix1) ** 2 + 3.0 * (iy - iy1) ** 2

        d2 = (ix - ix2 - 0.5) ** 2 + 3.0 * (iy - iy2 - 0.5) ** 2

        bdist = (d1 < d2)



        if C is None:                                   

            counts1 = np.bincount(i1[bdist], minlength=1 + nx1 * ny1)[1:]

            counts2 = np.bincount(i2[~bdist], minlength=1 + nx2 * ny2)[1:]

            accum = np.concatenate([counts1, counts2]).astype(float)

            if mincnt is not None:

                accum[accum < mincnt] = np.nan

            C = np.ones(len(x))

        else:

                                                            

            Cs_at_i1 = [[] for _ in range(1 + nx1 * ny1)]

            Cs_at_i2 = [[] for _ in range(1 + nx2 * ny2)]

            for i in range(len(x)):

                if bdist[i]:

                    Cs_at_i1[i1[i]].append(C[i])

                else:

                    Cs_at_i2[i2[i]].append(C[i])

            if mincnt is None:

                mincnt = 1

            accum = np.array(

                [reduce_C_function(acc) if len(acc) >= mincnt else np.nan

                 for Cs_at_i in [Cs_at_i1, Cs_at_i2]

                 for acc in Cs_at_i[1:]],                                   

                float)



        good_idxs = ~np.isnan(accum)



        offsets = np.zeros((n, 2), float)

        offsets[:nx1 * ny1, 0] = np.repeat(np.arange(nx1), ny1)

        offsets[:nx1 * ny1, 1] = np.tile(np.arange(ny1), nx1)

        offsets[nx1 * ny1:, 0] = np.repeat(np.arange(nx2) + 0.5, ny2)

        offsets[nx1 * ny1:, 1] = np.tile(np.arange(ny2), nx2) + 0.5

        offsets[:, 0] *= sx

        offsets[:, 1] *= sy

        offsets[:, 0] += xmin

        offsets[:, 1] += ymin

                                               

        offsets = offsets[good_idxs, :]

        accum = accum[good_idxs]



        polygon = [sx, sy / 3] * np.array(

            [[.5, -.5], [.5, .5], [0., 1.], [-.5, .5], [-.5, -.5], [0., -1.]])



        if linewidths is None:

            linewidths = [mpl.rcParams['patch.linewidth']]



        if xscale == 'log' or yscale == 'log':

            polygons = np.expand_dims(polygon, 0)

            if xscale == 'log':

                polygons[:, :, 0] = 10.0 ** polygons[:, :, 0]

                xmin = 10.0 ** xmin

                xmax = 10.0 ** xmax

                self.set_xscale(xscale)

            if yscale == 'log':

                polygons[:, :, 1] = 10.0 ** polygons[:, :, 1]

                ymin = 10.0 ** ymin

                ymax = 10.0 ** ymax

                self.set_yscale(yscale)

        else:

            polygons = [polygon]



        collection = mcoll.PolyCollection(

            polygons,

            edgecolors=edgecolors,

            linewidths=linewidths,

            offsets=offsets,

            offset_transform=mtransforms.AffineDeltaTransform(self.transData)

        )



                                         

        if cbook._str_equal(bins, 'log'):

            if norm is not None:

                _api.warn_external("Only one of 'bins' and 'norm' arguments "

                                   f"can be supplied, ignoring {bins=}")

            else:

                norm = mcolors.LogNorm(vmin=vmin, vmax=vmax)

                vmin = vmax = None

            bins = None



        if bins is not None:

            if not np.iterable(bins):

                minimum, maximum = min(accum), max(accum)

                bins -= 1                           

                bins = minimum + (maximum - minimum) * np.arange(bins) / bins

            bins = np.sort(bins)

            accum = bins.searchsorted(accum)



        if colorizer:

            collection._set_colorizer_check_keywords(colorizer, cmap=cmap,

                                                     norm=norm, vmin=vmin,

                                                     vmax=vmax)

        else:

            collection.set_cmap(cmap)

            collection.set_norm(norm)

        collection.set_array(accum)

        collection.set_alpha(alpha)

        collection._internal_update(kwargs)

        collection._scale_norm(norm, vmin, vmax)



                                                                            

        if norm is not None:

            if collection.norm.vmin is None and collection.norm.vmax is None:

                collection.norm.autoscale()



        corners = ((xmin, ymin), (xmax, ymax))

        self.update_datalim(corners)

        self._request_autoscale_view(tight=True)



                                 

        self.add_collection(collection, autolim=False)

        if not marginals:

            return collection



                           

        bars = []

        for zname, z, zmin, zmax, zscale, nbins in [

                ("x", x, xmin, xmax, xscale, nx),

                ("y", y, ymin, ymax, yscale, 2 * ny),

        ]:



            if zscale == "log":

                bin_edges = np.geomspace(zmin, zmax, nbins + 1)

            else:

                bin_edges = np.linspace(zmin, zmax, nbins + 1)



            verts = np.empty((nbins, 4, 2))

            verts[:, 0, 0] = verts[:, 1, 0] = bin_edges[:-1]

            verts[:, 2, 0] = verts[:, 3, 0] = bin_edges[1:]

            verts[:, 0, 1] = verts[:, 3, 1] = .00

            verts[:, 1, 1] = verts[:, 2, 1] = .05

            if zname == "y":

                verts = verts[:, :, ::-1]                 



                                                           

            bin_idxs = np.searchsorted(bin_edges, z) - 1

            values = np.empty(nbins)

            for i in range(nbins):

                                                                       

                                    

                ci = C[bin_idxs == i]

                values[i] = reduce_C_function(ci) if len(ci) > 0 else np.nan



            mask = ~np.isnan(values)

            verts = verts[mask]

            values = values[mask]



            trans = getattr(self, f"get_{zname}axis_transform")(which="grid")

            bar = mcoll.PolyCollection(

                verts, transform=trans, edgecolors="face")

            bar.set_array(values)

            bar.set_cmap(cmap)

            bar.set_norm(norm)

            bar.set_alpha(alpha)

            bar._internal_update(kwargs)

            bars.append(self.add_collection(bar, autolim=False))



        collection.hbar, collection.vbar = bars



        def on_changed(collection):

            collection.hbar.set_cmap(collection.get_cmap())

            collection.hbar.set_cmap(collection.get_cmap())

            collection.vbar.set_clim(collection.get_clim())

            collection.vbar.set_clim(collection.get_clim())



        collection.callbacks.connect('changed', on_changed)



        return collection



    @_docstring.interpd

    def arrow(self, x, y, dx, dy, **kwargs):

        

                                                               

                                                   

        x = self.convert_xunits(x)

        y = self.convert_yunits(y)

        dx = self.convert_xunits(dx)

        dy = self.convert_yunits(dy)



        a = mpatches.FancyArrow(x, y, dx, dy, **kwargs)

        self.add_patch(a)

        self._request_autoscale_view()

        return a



    @_docstring.copy(mquiver.QuiverKey.__init__)

    def quiverkey(self, Q, X, Y, U, label, **kwargs):

        qk = mquiver.QuiverKey(Q, X, Y, U, label, **kwargs)

        self.add_artist(qk)

        return qk



                                                      

    def _quiver_units(self, args, kwargs):

        if len(args) > 3:

            x, y = args[0:2]

            x, y = self._process_unit_info([("x", x), ("y", y)], kwargs)

            return (x, y) + args[2:]

        return args



                                                                           

    @_preprocess_data()

    @_docstring.interpd

    def quiver(self, *args, **kwargs):

        

                                                        

        args = self._quiver_units(args, kwargs)

        q = mquiver.Quiver(self, *args, **kwargs)

        self.add_collection(q)

        return q



                                                                              

    @_preprocess_data()

    @_docstring.interpd

    def barbs(self, *args, **kwargs):

        

                                                        

        args = self._quiver_units(args, kwargs)

        b = mquiver.Barbs(self, *args, **kwargs)

        self.add_collection(b)

        return b



                                                            

                             

    def fill(self, *args, data=None, **kwargs):

        

                                                                          

        kwargs = cbook.normalize_kwargs(kwargs, mlines.Line2D)

                                                                          

        patches = [*self._get_patches_for_fill(self, *args, data=data, **kwargs)]

        for poly in patches:

            self.add_patch(poly)

        self._request_autoscale_view()

        return patches



    def _fill_between_x_or_y(

            self, ind_dir, ind, dep1, dep2=0, *,

            where=None, interpolate=False, step=None, **kwargs):

                                                                        

                                                                            

                                                                            

                                               

        

        dep_dir = mcoll.FillBetweenPolyCollection._f_dir_from_t(ind_dir)



        if not mpl.rcParams["_internal.classic_mode"]:

            kwargs = cbook.normalize_kwargs(kwargs, mcoll.Collection)

            if not any(c in kwargs for c in ("color", "facecolor")):

                kwargs["facecolor"] = self._get_patches_for_fill.get_next_color()



        ind, dep1, dep2 = self._fill_between_process_units(

            ind_dir, dep_dir, ind, dep1, dep2, **kwargs)



        collection = mcoll.FillBetweenPolyCollection(

            ind_dir, ind, dep1, dep2,

            where=where, interpolate=interpolate, step=step, **kwargs)



        self.add_collection(collection)

        return collection



    def _fill_between_process_units(self, ind_dir, dep_dir, ind, dep1, dep2, **kwargs):

        

        return map(np.ma.masked_invalid, self._process_unit_info(

            [(ind_dir, ind), (dep_dir, dep1), (dep_dir, dep2)], kwargs))



    def fill_between(self, x, y1, y2=0, where=None, interpolate=False,

                     step=None, **kwargs):

        return self._fill_between_x_or_y(

            "x", x, y1, y2,

            where=where, interpolate=interpolate, step=step, **kwargs)



    if _fill_between_x_or_y.__doc__:

        fill_between.__doc__ = _fill_between_x_or_y.__doc__.format(

            dir="horizontal", ind="x", dep="y"

        )

    fill_between = _preprocess_data(

        _docstring.interpd(fill_between),

        replace_names=["x", "y1", "y2", "where"])



    def fill_betweenx(self, y, x1, x2=0, where=None,

                      step=None, interpolate=False, **kwargs):

        return self._fill_between_x_or_y(

            "y", y, x1, x2,

            where=where, interpolate=interpolate, step=step, **kwargs)



    if _fill_between_x_or_y.__doc__:

        fill_betweenx.__doc__ = _fill_between_x_or_y.__doc__.format(

            dir="vertical", ind="y", dep="x"

        )

    fill_betweenx = _preprocess_data(

        _docstring.interpd(fill_betweenx),

        replace_names=["y", "x1", "x2", "where"])



                                                                



    @_preprocess_data()

    @_docstring.interpd

    def imshow(self, X, cmap=None, norm=None, *, aspect=None,

               interpolation=None, alpha=None,

               vmin=None, vmax=None, colorizer=None, origin=None, extent=None,

               interpolation_stage=None, filternorm=True, filterrad=4.0,

               resample=None, url=None, **kwargs):

        

        im = mimage.AxesImage(self, cmap=cmap, norm=norm, colorizer=colorizer,

                              interpolation=interpolation, origin=origin,

                              extent=extent, filternorm=filternorm,

                              filterrad=filterrad, resample=resample,

                              interpolation_stage=interpolation_stage,

                              **kwargs)



        if aspect is None and not (

                im.is_transform_set()

                and not im.get_transform().contains_branch(self.transData)):

            aspect = mpl.rcParams['image.aspect']

        if aspect is not None:

            self.set_aspect(aspect)



        im.set_data(X)

        im.set_alpha(alpha)

        if im.get_clip_path() is None:

                                                                          

            im.set_clip_path(self.patch)

        im._check_exclusionary_keywords(colorizer, vmin=vmin, vmax=vmax)

        im._scale_norm(norm, vmin, vmax)

        im.set_url(url)



                                                             

                                                          

        im.set_extent(im.get_extent())



        self.add_image(im)

        return im



    def _pcolorargs(self, funcname, *args, shading='auto', **kwargs):

                                          

                                                      

                                                            

                                                              

                              



        _valid_shading = ['gouraud', 'nearest', 'flat', 'auto']

        try:

            _api.check_in_list(_valid_shading, shading=shading)

        except ValueError:

            _api.warn_external(f"shading value '{shading}' not in list of "

                               f"valid values {_valid_shading}. Setting "

                               "shading='auto'.")

            shading = 'auto'



        if len(args) == 1:

            C = np.asanyarray(args[0])

            nrows, ncols = C.shape[:2]

            if shading in ['gouraud', 'nearest']:

                X, Y = np.meshgrid(np.arange(ncols), np.arange(nrows))

            else:

                X, Y = np.meshgrid(np.arange(ncols + 1), np.arange(nrows + 1))

                shading = 'flat'

        elif len(args) == 3:

                                           

            C = np.asanyarray(args[2])

                                                                         

            X, Y = args[:2]

            X, Y = self._process_unit_info([("x", X), ("y", Y)], kwargs)

            X, Y = (cbook.safe_masked_invalid(a, copy=True) for a in [X, Y])



            if funcname == 'pcolormesh':

                if np.ma.is_masked(X) or np.ma.is_masked(Y):

                    raise ValueError(

                        'x and y arguments to pcolormesh cannot have '

                        'non-finite values or be of type '

                        'numpy.ma.MaskedArray with masked values')

            nrows, ncols = C.shape[:2]

        else:

            raise _api.nargs_error(funcname, takes="1 or 3", given=len(args))



        Nx = X.shape[-1]

        Ny = Y.shape[0]

        if X.ndim != 2 or X.shape[0] == 1:

            x = X.reshape(1, Nx)

            X = x.repeat(Ny, axis=0)

        if Y.ndim != 2 or Y.shape[1] == 1:

            y = Y.reshape(Ny, 1)

            Y = y.repeat(Nx, axis=1)

        if X.shape != Y.shape:

            raise TypeError(f'Incompatible X, Y inputs to {funcname}; '

                            f'see help({funcname})')



        if shading == 'auto':

            if ncols == Nx and nrows == Ny:

                shading = 'nearest'

            else:

                shading = 'flat'



        if shading == 'flat':

            if (Nx, Ny) != (ncols + 1, nrows + 1):

                raise TypeError(f"Dimensions of C {C.shape} should"

                                f" be one smaller than X({Nx}) and Y({Ny})"

                                f" while using shading='flat'"

                                f" see help({funcname})")

        else:                             

            if (Nx, Ny) != (ncols, nrows):

                raise TypeError('Dimensions of C %s are incompatible with'

                                ' X (%d) and/or Y (%d); see help(%s)' % (

                                    C.shape, Nx, Ny, funcname))

            if shading == 'nearest':

                                                                    

                                                                            

                                 

                def _interp_grid(X, require_monotonicity=False):

                                                                               

                                                                            

                                                                            

                                                                   

                    if np.shape(X)[1] > 1:

                        dX = np.diff(X, axis=1) * 0.5

                        if (require_monotonicity and

                                not (np.all(dX >= 0) or np.all(dX <= 0))):

                            _api.warn_external(

                                f"The input coordinates to {funcname} are "

                                "interpreted as cell centers, but are not "

                                "monotonically increasing or decreasing. "

                                "This may lead to incorrectly calculated cell "

                                "edges, in which case, please supply "

                                f"explicit cell edges to {funcname}.")



                        hstack = np.ma.hstack if np.ma.isMA(X) else np.hstack

                        X = hstack((X[:, [0]] - dX[:, [0]],

                                    X[:, :-1] + dX,

                                    X[:, [-1]] + dX[:, [-1]]))

                    else:

                                                                              

                                                          

                        X = np.hstack((X, X))

                    return X



                if ncols == Nx:

                    X = _interp_grid(X, require_monotonicity=True)

                    Y = _interp_grid(Y)

                if nrows == Ny:

                    X = _interp_grid(X.T).T

                    Y = _interp_grid(Y.T, require_monotonicity=True).T

                shading = 'flat'



        C = cbook.safe_masked_invalid(C, copy=True)

        return X, Y, C, shading



    @_preprocess_data()

    @_docstring.interpd

    def pcolor(self, *args, shading=None, alpha=None, norm=None, cmap=None,

               vmin=None, vmax=None, colorizer=None, **kwargs):

        



        if shading is None:

            shading = mpl.rcParams['pcolor.shading']

        shading = shading.lower()

        X, Y, C, shading = self._pcolorargs('pcolor', *args, shading=shading,

                                            kwargs=kwargs)

        linewidths = (0.25,)

        if 'linewidth' in kwargs:

            kwargs['linewidths'] = kwargs.pop('linewidth')

        kwargs.setdefault('linewidths', linewidths)



        if 'edgecolor' in kwargs:

            kwargs['edgecolors'] = kwargs.pop('edgecolor')

        ec = kwargs.setdefault('edgecolors', 'none')



                                                                      

                                                               

                                                              

                                                    

        if 'antialiaseds' in kwargs:

            kwargs['antialiased'] = kwargs.pop('antialiaseds')

        if 'antialiased' not in kwargs and cbook._str_lower_equal(ec, "none"):

            kwargs['antialiased'] = False



        kwargs.setdefault('snap', False)



        if np.ma.isMaskedArray(X) or np.ma.isMaskedArray(Y):

            stack = np.ma.stack

            X = np.ma.asarray(X)

            Y = np.ma.asarray(Y)

                                          

            x = X.compressed()

            y = Y.compressed()

        else:

            stack = np.stack

            x = X

            y = Y

        coords = stack([X, Y], axis=-1)



        collection = mcoll.PolyQuadMesh(

            coords, array=C, cmap=cmap, norm=norm, colorizer=colorizer,

            alpha=alpha, **kwargs)

        collection._check_exclusionary_keywords(colorizer, vmin=vmin, vmax=vmax)

        collection._scale_norm(norm, vmin, vmax)



        coords = coords.reshape(-1, 2)                                         

        self._update_pcolor_lims(collection, coords)

        return collection



    @_preprocess_data()

    @_docstring.interpd

    def pcolormesh(self, *args, alpha=None, norm=None, cmap=None, vmin=None,

                   vmax=None, colorizer=None, shading=None, antialiased=False,

                   **kwargs):

        

        shading = mpl._val_or_rc(shading, 'pcolor.shading').lower()

        kwargs.setdefault('edgecolors', 'none')



        X, Y, C, shading = self._pcolorargs('pcolormesh', *args,

                                            shading=shading, kwargs=kwargs)

        coords = np.stack([X, Y], axis=-1)



        kwargs.setdefault('snap', mpl.rcParams['pcolormesh.snap'])



        collection = mcoll.QuadMesh(

            coords, antialiased=antialiased, shading=shading,

            array=C, cmap=cmap, norm=norm, colorizer=colorizer, alpha=alpha, **kwargs)

        collection._check_exclusionary_keywords(colorizer, vmin=vmin, vmax=vmax)

        collection._scale_norm(norm, vmin, vmax)



        coords = coords.reshape(-1, 2)                                         

        self._update_pcolor_lims(collection, coords)

        return collection



    def _update_pcolor_lims(self, collection, coords):

        

                                                    

        t = collection._transform

        if (not isinstance(t, mtransforms.Transform) and

                hasattr(t, '_as_mpl_transform')):

            t = t._as_mpl_transform(self.axes)



        if t and any(t.contains_branch_seperately(self.transData)):

            trans_to_data = t - self.transData

            coords = trans_to_data.transform(coords)



        self.add_collection(collection, autolim=False)



        minx, miny = np.min(coords, axis=0)

        maxx, maxy = np.max(coords, axis=0)

        collection.sticky_edges.x[:] = [minx, maxx]

        collection.sticky_edges.y[:] = [miny, maxy]

        self.update_datalim(coords)

        self._request_autoscale_view()



    @_preprocess_data()

    @_docstring.interpd

    def pcolorfast(self, *args, alpha=None, norm=None, cmap=None, vmin=None,

                   vmax=None, colorizer=None, **kwargs):

        



        C = args[-1]

        nr, nc = np.shape(C)[:2]

        if len(args) == 1:

            style = "image"

            x = [0, nc]

            y = [0, nr]

        elif len(args) == 3:

            x, y = args[:2]

            x = np.asarray(x)

            y = np.asarray(y)

            if x.ndim == 1 and y.ndim == 1:

                if x.size == 2 and y.size == 2:

                    style = "image"

                else:

                    if x.size != nc + 1:

                        raise ValueError(

                            f"Length of X ({x.size}) must be one larger than the "

                            f"number of columns in C ({nc})")

                    if y.size != nr + 1:

                        raise ValueError(

                            f"Length of Y ({y.size}) must be one larger than the "

                            f"number of rows in C ({nr})"

                        )

                    dx = np.diff(x)

                    dy = np.diff(y)

                    if (np.ptp(dx) < 0.01 * abs(dx.mean()) and

                            np.ptp(dy) < 0.01 * abs(dy.mean())):

                        style = "image"

                    else:

                        style = "pcolorimage"

            elif x.ndim == 2 and y.ndim == 2:

                style = "quadmesh"

            else:

                raise TypeError(

                    f"When 3 positional parameters are passed to pcolorfast, the first "

                    f"two (X and Y) must be both 1D or both 2D; the given X was "

                    f"{x.ndim}D and the given Y was {y.ndim}D")

        else:

            raise _api.nargs_error('pcolorfast', '1 or 3', len(args))



        mcolorizer.ColorizingArtist._check_exclusionary_keywords(colorizer, vmin=vmin,

                                                                 vmax=vmax)

        if style == "quadmesh":

                                                                   

            coords = np.stack([x, y], axis=-1)

            if np.ndim(C) not in {2, 3}:

                raise ValueError("C must be 2D or 3D")

            collection = mcoll.QuadMesh(

                coords, array=C,

                alpha=alpha, cmap=cmap, norm=norm, colorizer=colorizer,

                antialiased=False, edgecolors="none")

            self.add_collection(collection, autolim=False)

            xl, xr, yb, yt = x.min(), x.max(), y.min(), y.max()

            ret = collection



        else:                                     

            extent = xl, xr, yb, yt = x[0], x[-1], y[0], y[-1]

            if style == "image":

                im = mimage.AxesImage(

                    self, cmap=cmap, norm=norm, colorizer=colorizer,

                    data=C, alpha=alpha, extent=extent,

                    interpolation='nearest', origin='lower',

                    **kwargs)

            elif style == "pcolorimage":

                im = mimage.PcolorImage(

                    self, x, y, C,

                    cmap=cmap, norm=norm, colorizer=colorizer, alpha=alpha,

                    extent=extent, **kwargs)

            self.add_image(im)

            ret = im



        if np.ndim(C) == 2:                                                  

            ret._scale_norm(norm, vmin, vmax)



        if ret.get_clip_path() is None:

                                                                          

            ret.set_clip_path(self.patch)



        ret.sticky_edges.x[:] = [xl, xr]

        ret.sticky_edges.y[:] = [yb, yt]

        self.update_datalim(np.array([[xl, yb], [xr, yt]]))

        self._request_autoscale_view(tight=True)

        return ret



    @_preprocess_data()

    @_docstring.interpd

    def contour(self, *args, **kwargs):

        

        kwargs['filled'] = False

        contours = mcontour.QuadContourSet(self, *args, **kwargs)

        self._request_autoscale_view()

        return contours



    @_preprocess_data()

    @_docstring.interpd

    def contourf(self, *args, **kwargs):

        

        kwargs['filled'] = True

        contours = mcontour.QuadContourSet(self, *args, **kwargs)

        self._request_autoscale_view()

        return contours



    def clabel(self, CS, levels=None, **kwargs):

        

        return CS.clabel(levels, **kwargs)



                      



    @_api.make_keyword_only("3.10", "range")

    @_preprocess_data(replace_names=["x", 'weights'], label_namer="x")

    def hist(self, x, bins=None, range=None, density=False, weights=None,

             cumulative=False, bottom=None, histtype='bar', align='mid',

             orientation='vertical', rwidth=None, log=False,

             color=None, label=None, stacked=False, **kwargs):

        

                                      

        bin_range = range

        from builtins import range



        kwargs = cbook.normalize_kwargs(kwargs, mpatches.Patch)



        if np.isscalar(x):

            x = [x]



        bins = mpl._val_or_rc(bins, 'hist.bins')



                                                                          

        _api.check_in_list(['bar', 'barstacked', 'step', 'stepfilled'],

                           histtype=histtype)

        _api.check_in_list(['left', 'mid', 'right'], align=align)

        _api.check_in_list(['horizontal', 'vertical'], orientation=orientation)



        if histtype == 'barstacked' and not stacked:

            stacked = True



                                     

        x = cbook._reshape_2D(x, 'x')

        nx = len(x)                      



                                                                         

                                                                            

                        

        if orientation == "vertical":

            convert_units = self.convert_xunits

            x = [*self._process_unit_info([("x", x[0])], kwargs),

                 *map(convert_units, x[1:])]

        else:              

            convert_units = self.convert_yunits

            x = [*self._process_unit_info([("y", x[0])], kwargs),

                 *map(convert_units, x[1:])]



        if bin_range is not None:

            bin_range = convert_units(bin_range)



        if not cbook.is_scalar_or_string(bins):

            bins = convert_units(bins)



                                                         

        if weights is not None:

            w = cbook._reshape_2D(weights, 'weights')

        else:

            w = [None] * nx



        if len(w) != nx:

            raise ValueError('weights should have the same shape as x')



        input_empty = True

        for xi, wi in zip(x, w):

            len_xi = len(xi)

            if wi is not None and len(wi) != len_xi:

                raise ValueError('weights should have the same shape as x')

            if len_xi:

                input_empty = False



        if color is None:

            colors = [self._get_lines.get_next_color() for i in range(nx)]

        else:

            colors = mcolors.to_rgba_array(color)

            if len(colors) != nx:

                raise ValueError(f"The 'color' keyword argument must have one "

                                 f"color per dataset, but {nx} datasets and "

                                 f"{len(colors)} colors were provided")



        hist_kwargs = dict()



                                                                  

                                                                   

                                                            

        if bin_range is None:

            xmin = np.inf

            xmax = -np.inf

            for xi in x:

                if len(xi):

                                                  

                                                             

                    xmin = min(xmin, np.nanmin(xi))

                    xmax = max(xmax, np.nanmax(xi))

            if xmin <= xmax:                                                

                bin_range = (xmin, xmax)



                                                                   

                                                                    

                                          

        if not input_empty and len(x) > 1:

            if weights is not None:

                _w = np.concatenate(w)

            else:

                _w = None

            bins = np.histogram_bin_edges(

                np.concatenate(x), bins, bin_range, _w)

        else:

            hist_kwargs['range'] = bin_range



        density = bool(density)

        if density and not stacked:

            hist_kwargs['density'] = density



                                                                 

        tops = []                                         

                               

        for i in range(nx):

                                                     

                                                       

            m, bins = np.histogram(x[i], bins, weights=w[i], **hist_kwargs)

            tops.append(m)

        tops = np.array(tops, float)                                        

        bins = np.array(bins, float)                              

        if stacked:

            tops = tops.cumsum(axis=0)

                                                                         

                                              

            if density:

                tops = (tops / np.diff(bins)) / tops[-1].sum()

        if cumulative:

            slc = slice(None)

            if isinstance(cumulative, Number) and cumulative < 0:

                slc = slice(None, None, -1)

            if density:

                tops = (tops * np.diff(bins))[:, slc].cumsum(axis=1)[:, slc]

            else:

                tops = tops[:, slc].cumsum(axis=1)[:, slc]



        patches = []



        if histtype.startswith('bar'):



            totwidth = np.diff(bins)



            if rwidth is not None:

                dr = np.clip(rwidth, 0, 1)

            elif (len(tops) > 1 and

                  ((not stacked) or mpl.rcParams['_internal.classic_mode'])):

                dr = 0.8

            else:

                dr = 1.0



            if histtype == 'bar' and not stacked:

                width = dr * totwidth / nx

                dw = width

                boffset = -0.5 * dr * totwidth * (1 - 1 / nx)

            elif histtype == 'barstacked' or stacked:

                width = dr * totwidth

                boffset, dw = 0.0, 0.0



            if align == 'mid':

                boffset += 0.5 * totwidth

            elif align == 'right':

                boffset += totwidth



            if orientation == 'horizontal':

                _barfunc = self.barh

                bottom_kwarg = 'left'

            else:                             

                _barfunc = self.bar

                bottom_kwarg = 'bottom'



            for top, color in zip(tops, colors):

                if bottom is None:

                    bottom = np.zeros(len(top))

                if stacked:

                    height = top - bottom

                else:

                    height = top

                bars = _barfunc(bins[:-1]+boffset, height, width,

                                align='center', log=log,

                                color=color, **{bottom_kwarg: bottom})

                patches.append(bars)

                if stacked:

                    bottom = top

                boffset += dw

                                                                             

                                                                           

                                 

            for bars in patches[1:]:

                for patch in bars:

                    patch.sticky_edges.x[:] = patch.sticky_edges.y[:] = []



        elif histtype.startswith('step'):

                                                       

            x = np.zeros(4 * len(bins) - 3)

            y = np.zeros(4 * len(bins) - 3)



            x[0:2*len(bins)-1:2], x[1:2*len(bins)-1:2] = bins, bins[:-1]

            x[2*len(bins)-1:] = x[1:2*len(bins)-1][::-1]



            if bottom is None:

                bottom = 0



            y[1:2*len(bins)-1:2] = y[2:2*len(bins):2] = bottom

            y[2*len(bins)-1:] = y[1:2*len(bins)-1][::-1]



            if log:

                if orientation == 'horizontal':

                    self.set_xscale('log', nonpositive='clip')

                else:                             

                    self.set_yscale('log', nonpositive='clip')



            if align == 'left':

                x -= 0.5*(bins[1]-bins[0])

            elif align == 'right':

                x += 0.5*(bins[1]-bins[0])



                                                                              

                             

            fill = (histtype == 'stepfilled')



            xvals, yvals = [], []

            for top in tops:

                if stacked:

                                                                    

                    y[2*len(bins)-1:] = y[1:2*len(bins)-1][::-1]

                                             

                y[1:2*len(bins)-1:2] = y[2:2*len(bins):2] = top + bottom



                                                                    

                                                                      

                                                                          

                                                            

                y[0] = y[-1]



                if orientation == 'horizontal':

                    xvals.append(y.copy())

                    yvals.append(x.copy())

                else:

                    xvals.append(x.copy())

                    yvals.append(y.copy())



                                             

            split = -1 if fill else 2 * len(bins)

                                                                 

                                                            

                                       

            for x, y, color in reversed(list(zip(xvals, yvals, colors))):

                patches.append(self.fill(

                    x[:split], y[:split],

                    closed=True if fill else None,

                    facecolor=color,

                    edgecolor=None if fill else color,

                    fill=fill if fill else None,

                    zorder=None if fill else mlines.Line2D.zorder))

            for patch_list in patches:

                for patch in patch_list:

                    if orientation == 'vertical':

                        patch.sticky_edges.y.append(0)

                    elif orientation == 'horizontal':

                        patch.sticky_edges.x.append(0)



                                                                     

            patches.reverse()



                                                                           

                                                                

        labels = [] if label is None else np.atleast_1d(np.asarray(label, str))



        if histtype == "step":

            ec = kwargs.get('edgecolor', colors)

        else:

            ec = kwargs.get('edgecolor', None)

        if ec is None or cbook._str_lower_equal(ec, 'none'):

            edgecolors = itertools.repeat(ec)

        else:

            edgecolors = itertools.cycle(mcolors.to_rgba_array(ec))



        fc = kwargs.get('facecolor', colors)

        if cbook._str_lower_equal(fc, 'none'):

            facecolors = itertools.repeat(fc)

        else:

            facecolors = itertools.cycle(mcolors.to_rgba_array(fc))



        hatches = itertools.cycle(np.atleast_1d(kwargs.get('hatch', None)))

        linewidths = itertools.cycle(np.atleast_1d(kwargs.get('linewidth', None)))

        if 'linestyle' in kwargs:

            linestyles = itertools.cycle(mlines._get_dash_patterns(kwargs['linestyle']))

        else:

            linestyles = itertools.repeat(None)



        for patch, lbl in itertools.zip_longest(patches, labels):

            if not patch:

                continue

            p = patch[0]

            kwargs.update({

                'hatch': next(hatches),

                'linewidth': next(linewidths),

                'linestyle': next(linestyles),

                'edgecolor': next(edgecolors),

                'facecolor': next(facecolors),

            })

            p._internal_update(kwargs)

            if lbl is not None:

                p.set_label(lbl)

            for p in patch[1:]:

                p._internal_update(kwargs)

                p.set_label('_nolegend_')



        if nx == 1:

            return tops[0], bins, patches[0]

        else:

            patch_type = ("BarContainer" if histtype.startswith("bar")

                          else "list[Polygon]")

            return tops, bins, cbook.silent_list(patch_type, patches)



    @_preprocess_data()

    def stairs(self, values, edges=None, *,

               orientation='vertical', baseline=0, fill=False, **kwargs):

        



        if 'color' in kwargs:

            _color = kwargs.pop('color')

        else:

            _color = self._get_lines.get_next_color()

        if fill:

            kwargs.setdefault('linewidth', 0)

            kwargs.setdefault('facecolor', _color)

        else:

            kwargs.setdefault('edgecolor', _color)



        if edges is None:

            edges = np.arange(len(values) + 1)



        edges, values, baseline = self._process_unit_info(

            [("x", edges), ("y", values), ("y", baseline)], kwargs)



        patch = mpatches.StepPatch(values,

                                   edges,

                                   baseline=baseline,

                                   orientation=orientation,

                                   fill=fill,

                                   **kwargs)

        self.add_patch(patch)

        if baseline is None and fill:

            _api.warn_external(

                f"Both {baseline=} and {fill=} have been passed. "

                "baseline=None is only intended for unfilled stair plots. "

                "Because baseline is None, the Path used to draw the stairs will "

                "not be closed, thus because fill is True the polygon will be closed "

                "by drawing an (unstroked) edge from the first to last point.  It is "

                "very likely that the resulting fill patterns is not the desired "

                "result."

            )



        if baseline is not None:

            if orientation == 'vertical':

                patch.sticky_edges.y.append(np.min(baseline))

                self.update_datalim([(edges[0], np.min(baseline))])

            else:

                patch.sticky_edges.x.append(np.min(baseline))

                self.update_datalim([(np.min(baseline), edges[0])])

        self._request_autoscale_view()

        return patch



    @_api.make_keyword_only("3.10", "range")

    @_preprocess_data(replace_names=["x", "y", "weights"])

    @_docstring.interpd

    def hist2d(self, x, y, bins=10, range=None, density=False, weights=None,

               cmin=None, cmax=None, **kwargs):

        



        h, xedges, yedges = np.histogram2d(x, y, bins=bins, range=range,

                                           density=density, weights=weights)



        if cmin is not None:

            h[h < cmin] = None

        if cmax is not None:

            h[h > cmax] = None



        pc = self.pcolormesh(xedges, yedges, h.T, **kwargs)

        self.set_xlim(xedges[0], xedges[-1])

        self.set_ylim(yedges[0], yedges[-1])



        return h, xedges, yedges, pc



    @_preprocess_data(replace_names=["x", "weights"], label_namer="x")

    @_docstring.interpd

    def ecdf(self, x, weights=None, *, complementary=False,

             orientation="vertical", compress=False, **kwargs):

        

        _api.check_in_list(["horizontal", "vertical"], orientation=orientation)

        if "drawstyle" in kwargs or "ds" in kwargs:

            raise TypeError("Cannot pass 'drawstyle' or 'ds' to ecdf()")

        if np.ma.getmask(x).any():

            raise ValueError("ecdf() does not support masked entries")

        x = np.asarray(x)

        if np.isnan(x).any():

            raise ValueError("ecdf() does not support NaNs")

        argsort = np.argsort(x)

        x = x[argsort]

        if weights is None:

                                                                              

            cum_weights = (1 + np.arange(len(x))) / len(x)

        else:

            weights = np.take(weights, argsort)                                         

            cum_weights = np.cumsum(weights / np.sum(weights))

        if compress:

                                             

            compress_idxs = [0, *(x[:-1] != x[1:]).nonzero()[0] + 1]

            x = x[compress_idxs]

            cum_weights = cum_weights[compress_idxs]

        if orientation == "vertical":

            if not complementary:

                line, = self.plot([x[0], *x], [0, *cum_weights],

                                  drawstyle="steps-post", **kwargs)

            else:

                line, = self.plot([*x, x[-1]], [1, *1 - cum_weights],

                                  drawstyle="steps-pre", **kwargs)

            line.sticky_edges.y[:] = [0, 1]

        else:                                

            if not complementary:

                line, = self.plot([0, *cum_weights], [x[0], *x],

                                  drawstyle="steps-pre", **kwargs)

            else:

                line, = self.plot([1, *1 - cum_weights], [*x, x[-1]],

                                  drawstyle="steps-post", **kwargs)

            line.sticky_edges.x[:] = [0, 1]

        return line



    @_api.make_keyword_only("3.10", "NFFT")

    @_preprocess_data(replace_names=["x"])

    @_docstring.interpd

    def psd(self, x, NFFT=None, Fs=None, Fc=None, detrend=None,

            window=None, noverlap=None, pad_to=None,

            sides=None, scale_by_freq=None, return_line=None, **kwargs):

        

        if Fc is None:

            Fc = 0



        pxx, freqs = mlab.psd(x=x, NFFT=NFFT, Fs=Fs, detrend=detrend,

                              window=window, noverlap=noverlap, pad_to=pad_to,

                              sides=sides, scale_by_freq=scale_by_freq)

        freqs += Fc



        if scale_by_freq in (None, True):

            psd_units = 'dB/Hz'

        else:

            psd_units = 'dB'



        line = self.plot(freqs, 10 * np.log10(pxx), **kwargs)

        self.set_xlabel('Frequency')

        self.set_ylabel('Power Spectral Density (%s)' % psd_units)

        self.grid(True)



        vmin, vmax = self.get_ybound()

        step = max(10 * int(np.log10(vmax - vmin)), 1)

        ticks = np.arange(math.floor(vmin), math.ceil(vmax) + 1, step)

        self.set_yticks(ticks)



        if return_line is None or not return_line:

            return pxx, freqs

        else:

            return pxx, freqs, line



    @_api.make_keyword_only("3.10", "NFFT")

    @_preprocess_data(replace_names=["x", "y"], label_namer="y")

    @_docstring.interpd

    def csd(self, x, y, NFFT=None, Fs=None, Fc=None, detrend=None,

            window=None, noverlap=None, pad_to=None,

            sides=None, scale_by_freq=None, return_line=None, **kwargs):

        

        if Fc is None:

            Fc = 0



        pxy, freqs = mlab.csd(x=x, y=y, NFFT=NFFT, Fs=Fs, detrend=detrend,

                              window=window, noverlap=noverlap, pad_to=pad_to,

                              sides=sides, scale_by_freq=scale_by_freq)

                        

        freqs += Fc



        line = self.plot(freqs, 10 * np.log10(np.abs(pxy)), **kwargs)

        self.set_xlabel('Frequency')

        self.set_ylabel('Cross Spectrum Magnitude (dB)')

        self.grid(True)



        vmin, vmax = self.get_ybound()

        step = max(10 * int(np.log10(vmax - vmin)), 1)

        ticks = np.arange(math.floor(vmin), math.ceil(vmax) + 1, step)

        self.set_yticks(ticks)



        if return_line is None or not return_line:

            return pxy, freqs

        else:

            return pxy, freqs, line



    @_api.make_keyword_only("3.10", "Fs")

    @_preprocess_data(replace_names=["x"])

    @_docstring.interpd

    def magnitude_spectrum(self, x, Fs=None, Fc=None, window=None,

                           pad_to=None, sides=None, scale=None,

                           **kwargs):

        

        if Fc is None:

            Fc = 0



        spec, freqs = mlab.magnitude_spectrum(x=x, Fs=Fs, window=window,

                                              pad_to=pad_to, sides=sides)

        freqs += Fc



        yunits = _api.check_getitem(

            {None: 'energy', 'default': 'energy', 'linear': 'energy',

             'dB': 'dB'},

            scale=scale)

        if yunits == 'energy':

            Z = spec

        else:                  

            Z = 20. * np.log10(spec)



        line, = self.plot(freqs, Z, **kwargs)

        self.set_xlabel('Frequency')

        self.set_ylabel('Magnitude (%s)' % yunits)



        return spec, freqs, line



    @_api.make_keyword_only("3.10", "Fs")

    @_preprocess_data(replace_names=["x"])

    @_docstring.interpd

    def angle_spectrum(self, x, Fs=None, Fc=None, window=None,

                       pad_to=None, sides=None, **kwargs):

        

        if Fc is None:

            Fc = 0



        spec, freqs = mlab.angle_spectrum(x=x, Fs=Fs, window=window,

                                          pad_to=pad_to, sides=sides)

        freqs += Fc



        lines = self.plot(freqs, spec, **kwargs)

        self.set_xlabel('Frequency')

        self.set_ylabel('Angle (radians)')



        return spec, freqs, lines[0]



    @_api.make_keyword_only("3.10", "Fs")

    @_preprocess_data(replace_names=["x"])

    @_docstring.interpd

    def phase_spectrum(self, x, Fs=None, Fc=None, window=None,

                       pad_to=None, sides=None, **kwargs):

        

        if Fc is None:

            Fc = 0



        spec, freqs = mlab.phase_spectrum(x=x, Fs=Fs, window=window,

                                          pad_to=pad_to, sides=sides)

        freqs += Fc



        lines = self.plot(freqs, spec, **kwargs)

        self.set_xlabel('Frequency')

        self.set_ylabel('Phase (radians)')



        return spec, freqs, lines[0]



    @_api.make_keyword_only("3.10", "NFFT")

    @_preprocess_data(replace_names=["x", "y"])

    @_docstring.interpd

    def cohere(self, x, y, NFFT=256, Fs=2, Fc=0, detrend=mlab.detrend_none,

               window=mlab.window_hanning, noverlap=0, pad_to=None,

               sides='default', scale_by_freq=None, **kwargs):

        

        cxy, freqs = mlab.cohere(x=x, y=y, NFFT=NFFT, Fs=Fs, detrend=detrend,

                                 window=window, noverlap=noverlap,

                                 scale_by_freq=scale_by_freq, sides=sides,

                                 pad_to=pad_to)

        freqs += Fc



        self.plot(freqs, cxy, **kwargs)

        self.set_xlabel('Frequency')

        self.set_ylabel('Coherence')

        self.grid(True)



        return cxy, freqs



    @_api.make_keyword_only("3.10", "NFFT")

    @_preprocess_data(replace_names=["x"])

    @_docstring.interpd

    def specgram(self, x, NFFT=None, Fs=None, Fc=None, detrend=None,

                 window=None, noverlap=None,

                 cmap=None, xextent=None, pad_to=None, sides=None,

                 scale_by_freq=None, mode=None, scale=None,

                 vmin=None, vmax=None, **kwargs):

        

        if NFFT is None:

            NFFT = 256                                      

        if Fc is None:

            Fc = 0                                              

        if noverlap is None:

            noverlap = 128                                      

        if Fs is None:

            Fs = 2                                              



        if mode == 'complex':

            raise ValueError('Cannot plot a complex specgram')



        if scale is None or scale == 'default':

            if mode in ['angle', 'phase']:

                scale = 'linear'

            else:

                scale = 'dB'

        elif mode in ['angle', 'phase'] and scale == 'dB':

            raise ValueError('Cannot use dB scale with angle or phase mode')



        spec, freqs, t = mlab.specgram(x=x, NFFT=NFFT, Fs=Fs,

                                       detrend=detrend, window=window,

                                       noverlap=noverlap, pad_to=pad_to,

                                       sides=sides,

                                       scale_by_freq=scale_by_freq,

                                       mode=mode)



        if scale == 'linear':

            Z = spec

        elif scale == 'dB':

            if mode is None or mode == 'default' or mode == 'psd':

                Z = 10. * np.log10(spec)

            else:

                Z = 20. * np.log10(spec)

        else:

            raise ValueError(f'Unknown scale {scale!r}')



        Z = np.flipud(Z)



        if xextent is None:

                                                           

            pad_xextent = (NFFT-noverlap) / Fs / 2

            xextent = np.min(t) - pad_xextent, np.max(t) + pad_xextent

        xmin, xmax = xextent

        freqs += Fc

        extent = xmin, xmax, freqs[0], freqs[-1]



        if 'origin' in kwargs:

            raise _api.kwarg_error("specgram", "origin")



        im = self.imshow(Z, cmap, extent=extent, vmin=vmin, vmax=vmax,

                         origin='upper', **kwargs)

        self.axis('auto')



        return spec, freqs, t, im



    @_api.make_keyword_only("3.10", "precision")

    @_docstring.interpd

    def spy(self, Z, precision=0, marker=None, markersize=None,

            aspect='equal', origin="upper", **kwargs):

        

        if marker is None and markersize is None and hasattr(Z, 'tocoo'):

            marker = 's'

        _api.check_in_list(["upper", "lower"], origin=origin)

        if marker is None and markersize is None:

            Z = np.asarray(Z)

            mask = np.abs(Z) > precision



            if 'cmap' not in kwargs:

                kwargs['cmap'] = mcolors.ListedColormap(['w', 'k'],

                                                        name='binary')

            if 'interpolation' in kwargs:

                raise _api.kwarg_error("spy", "interpolation")

            if 'norm' not in kwargs:

                kwargs['norm'] = mcolors.NoNorm()

            ret = self.imshow(mask, interpolation='nearest',

                              aspect=aspect, origin=origin,

                              **kwargs)

        else:

            if hasattr(Z, 'tocoo'):

                c = Z.tocoo()

                if precision == 'present':

                    y = c.row

                    x = c.col

                else:

                    nonzero = np.abs(c.data) > precision

                    y = c.row[nonzero]

                    x = c.col[nonzero]

            else:

                Z = np.asarray(Z)

                nonzero = np.abs(Z) > precision

                y, x = np.nonzero(nonzero)

            if marker is None:

                marker = 's'

            if markersize is None:

                markersize = 10

            if 'linestyle' in kwargs:

                raise _api.kwarg_error("spy", "linestyle")

            ret = mlines.Line2D(

                x, y, linestyle='None', marker=marker, markersize=markersize,

                **kwargs)

            self.add_line(ret)

            nr, nc = Z.shape

            self.set_xlim(-0.5, nc - 0.5)

            if origin == "upper":

                self.set_ylim(nr - 0.5, -0.5)

            else:

                self.set_ylim(-0.5, nr - 0.5)

            self.set_aspect(aspect)

        self.title.set_y(1.05)

        if origin == "upper":

            self.xaxis.tick_top()

        else:         

            self.xaxis.tick_bottom()

        self.xaxis.set_ticks_position('both')

        self.xaxis.set_major_locator(

            mticker.MaxNLocator(nbins=9, steps=[1, 2, 5, 10], integer=True))

        self.yaxis.set_major_locator(

            mticker.MaxNLocator(nbins=9, steps=[1, 2, 5, 10], integer=True))

        return ret



    def matshow(self, Z, **kwargs):

        

        Z = np.asanyarray(Z)

        kw = {'origin': 'upper',

              'interpolation': 'nearest',

              'aspect': 'equal',                                        

              **kwargs}

        im = self.imshow(Z, **kw)

        self.title.set_y(1.05)

        self.xaxis.tick_top()

        self.xaxis.set_ticks_position('both')

        self.xaxis.set_major_locator(

            mticker.MaxNLocator(nbins=9, steps=[1, 2, 5, 10], integer=True))

        self.yaxis.set_major_locator(

            mticker.MaxNLocator(nbins=9, steps=[1, 2, 5, 10], integer=True))

        return im



    @_api.make_keyword_only("3.10", "vert")

    @_preprocess_data(replace_names=["dataset"])

    def violinplot(self, dataset, positions=None, vert=None,

                   orientation='vertical', widths=0.5, showmeans=False,

                   showextrema=True, showmedians=False, quantiles=None,

                   points=100, bw_method=None, side='both',

                   facecolor=None, linecolor=None):

        



        def _kde_method(X, coords):

                                                            

            X = cbook._unpack_to_numpy(X)

                                                                       

            if np.all(X[0] == X):

                return (X[0] == coords).astype(float)

            kde = mlab.GaussianKDE(X, bw_method)

            return kde.evaluate(coords)



        vpstats = cbook.violin_stats(dataset, _kde_method, points=points,

                                     quantiles=quantiles)

        return self.violin(vpstats, positions=positions, vert=vert,

                           orientation=orientation, widths=widths,

                           showmeans=showmeans, showextrema=showextrema,

                           showmedians=showmedians, side=side,

                           facecolor=facecolor, linecolor=linecolor)



    @_api.make_keyword_only("3.10", "vert")

    def violin(self, vpstats, positions=None, vert=None,

               orientation='vertical', widths=0.5, showmeans=False,

               showextrema=True, showmedians=False, side='both',

               facecolor=None, linecolor=None):

        



                                                             

        means = []

        mins = []

        maxes = []

        medians = []

        quantiles = []



        qlens = []                                        



        artists = {}                              



        N = len(vpstats)

        datashape_message = ("List of violinplot statistics and `{0}` "

                             "values must have the same length")



                                                                 

                                                           

                                

        if vert is not None:

            _api.warn_deprecated(

                "3.11",

                name="vert: bool",

                alternative="orientation: {'vertical', 'horizontal'}",

            )

            orientation = 'vertical' if vert else 'horizontal'

        _api.check_in_list(['horizontal', 'vertical'], orientation=orientation)



                            

        if positions is None:

            positions = range(1, N + 1)

        elif len(positions) != N:

            raise ValueError(datashape_message.format("positions"))



                         

        if np.isscalar(widths):

            widths = [widths] * N

        elif len(widths) != N:

            raise ValueError(datashape_message.format("widths"))



                       

        _api.check_in_list(["both", "low", "high"], side=side)



                                                               

        line_ends = [[-0.25 if side in ['both', 'low'] else 0],

                     [0.25 if side in ['both', 'high'] else 0]]
                          * np.array(widths) + positions



                                                                            

        def cycle_color(color, alpha=None):

            rgba = mcolors.to_rgba_array(color, alpha=alpha)

            color_cycler = itertools.chain(itertools.cycle(rgba),

                                           itertools.repeat('none'))

            color_list = []

            for _ in range(N):

                color_list.append(next(color_cycler))

            return color_list



                                                                                       

        if facecolor is None or linecolor is None:

            if not mpl.rcParams['_internal.classic_mode']:

                next_color = self._get_lines.get_next_color()



        if facecolor is not None:

            facecolor = cycle_color(facecolor)

        else:

            default_facealpha = 0.3

                                                             

            if mpl.rcParams['_internal.classic_mode']:

                facecolor = cycle_color('y', alpha=default_facealpha)

            else:

                facecolor = cycle_color(next_color, alpha=default_facealpha)



        if mpl.rcParams['_internal.classic_mode']:

                                                                         

                                                             

            body_edgecolor = ("k", 0.3)

        else:

            body_edgecolor = None



        if linecolor is not None:

            linecolor = cycle_color(linecolor)

        else:

            if mpl.rcParams['_internal.classic_mode']:

                linecolor = cycle_color('r')

            else:

                linecolor = cycle_color(next_color)



                                                                   

        if orientation == 'vertical':

            fill = self.fill_betweenx

            if side in ['low', 'high']:

                perp_lines = functools.partial(self.hlines, colors=linecolor,

                                                capstyle='projecting')

                par_lines = functools.partial(self.vlines, colors=linecolor,

                                                capstyle='projecting')

            else:

                perp_lines = functools.partial(self.hlines, colors=linecolor)

                par_lines = functools.partial(self.vlines, colors=linecolor)

        else:

            fill = self.fill_between

            if side in ['low', 'high']:

                perp_lines = functools.partial(self.vlines, colors=linecolor,

                                                capstyle='projecting')

                par_lines = functools.partial(self.hlines, colors=linecolor,

                                                capstyle='projecting')

            else:

                perp_lines = functools.partial(self.vlines, colors=linecolor)

                par_lines = functools.partial(self.hlines, colors=linecolor)



                        

        bodies = []

        bodies_zip = zip(vpstats, positions, widths, facecolor)

        for stats, pos, width, facecolor in bodies_zip:

                                                                            

            vals = np.array(stats['vals'])

            vals = 0.5 * width * vals / vals.max()

            bodies += [fill(stats['coords'],

                            -vals + pos if side in ['both', 'low'] else pos,

                            vals + pos if side in ['both', 'high'] else pos,

                            facecolor=facecolor, edgecolor=body_edgecolor)]

            means.append(stats['mean'])

            mins.append(stats['min'])

            maxes.append(stats['max'])

            medians.append(stats['median'])

            q = stats.get('quantiles')                             

            if q is None:

                q = []

            quantiles.extend(q)

            qlens.append(len(q))

        artists['bodies'] = bodies



        if showmeans:                

            artists['cmeans'] = perp_lines(means, *line_ends)

        if showextrema:                  

            artists['cmaxes'] = perp_lines(maxes, *line_ends)

            artists['cmins'] = perp_lines(mins, *line_ends)

            artists['cbars'] = par_lines(positions, mins, maxes)

        if showmedians:                  

            artists['cmedians'] = perp_lines(medians, *line_ends)

        if quantiles:                                                        

            artists['cquantiles'] = perp_lines(

                quantiles, *np.repeat(line_ends, qlens, axis=1))



        return artists



                                                             



    table = _make_axes_method(mtable.table)



                                                                    

    stackplot = _preprocess_data()(_make_axes_method(mstack.stackplot))



    streamplot = _preprocess_data(

            replace_names=["x", "y", "u", "v", "start_points"])(

        _make_axes_method(mstream.streamplot))



    tricontour = _make_axes_method(mtri.tricontour)

    tricontourf = _make_axes_method(mtri.tricontourf)

    tripcolor = _make_axes_method(mtri.tripcolor)

    triplot = _make_axes_method(mtri.triplot)



    def _get_aspect_ratio(self):

        

        figure_size = self.get_figure().get_size_inches()

        ll, ur = self.get_position() * figure_size

        width, height = ur - ll

        return height / (width * self.get_data_ratio())

