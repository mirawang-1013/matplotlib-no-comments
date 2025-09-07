



from contextlib import ExitStack

import functools

import math

from numbers import Integral



import numpy as np

from numpy import ma



import matplotlib as mpl

from matplotlib import _api, _docstring

from matplotlib.backend_bases import MouseButton

from matplotlib.lines import Line2D

from matplotlib.path import Path

from matplotlib.text import Text

import matplotlib.ticker as ticker

import matplotlib.cm as cm

import matplotlib.colors as mcolors

import matplotlib.collections as mcoll

import matplotlib.font_manager as font_manager

import matplotlib.cbook as cbook

import matplotlib.patches as mpatches

import matplotlib.transforms as mtransforms

from . import artist





def _contour_labeler_event_handler(cs, inline, inline_spacing, event):

    canvas = cs.axes.get_figure(root=True).canvas

    is_button = event.name == "button_press_event"

    is_key = event.name == "key_press_event"

                                                                 

                                                                     

                                                                     

    if (is_button and event.button == MouseButton.MIDDLE

            or is_key and event.key in ["escape", "enter"]):

        canvas.stop_event_loop()

                     

    elif (is_button and event.button == MouseButton.RIGHT

          or is_key and event.key in ["backspace", "delete"]):

                                                                               

                                                                             

                                                                         

        if not inline:

            cs.pop_label()

            canvas.draw()

                    

    elif (is_button and event.button == MouseButton.LEFT

                                                

          or is_key and event.key is not None):

        if cs.axes.contains(event)[0]:

            cs.add_label_near(event.x, event.y, transform=False,

                              inline=inline, inline_spacing=inline_spacing)

            canvas.draw()





class ContourLabeler:

    



    def clabel(self, levels=None, *,

               fontsize=None, inline=True, inline_spacing=5, fmt=None,

               colors=None, use_clabeltext=False, manual=False,

               rightside_up=True, zorder=None):

        



                                                                      

                                                                              

                                                                             

         

                                                                              

                                                                           

                                                                      



        if fmt is None:

            fmt = ticker.ScalarFormatter(useOffset=False)

            fmt.create_dummy_axis()

        self.labelFmt = fmt

        self._use_clabeltext = use_clabeltext

        self.labelManual = manual

        self.rightside_up = rightside_up

        self._clabel_zorder = 2 + self.get_zorder() if zorder is None else zorder



        if levels is None:

            levels = self.levels

            indices = list(range(len(self.cvalues)))

        else:

            levlabs = list(levels)

            indices, levels = [], []

            for i, lev in enumerate(self.levels):

                if lev in levlabs:

                    indices.append(i)

                    levels.append(lev)

            if len(levels) < len(levlabs):

                raise ValueError(f"Specified levels {levlabs} don't match "

                                 f"available levels {self.levels}")

        self.labelLevelList = levels

        self.labelIndiceList = indices



        self._label_font_props = font_manager.FontProperties(size=fontsize)



        if colors is None:

            self.labelMappable = self

            self.labelCValueList = np.take(self.cvalues, self.labelIndiceList)

        else:

                                                     

                                                                             

                                          

            num_levels = len(self.labelLevelList)

            colors = cbook._resize_sequence(mcolors.to_rgba_array(colors), num_levels)

            self.labelMappable = cm.ScalarMappable(

                cmap=mcolors.ListedColormap(colors), norm=mcolors.NoNorm())

            self.labelCValueList = list(range(num_levels))



        self.labelXYs = []



        if np.iterable(manual):

            for x, y in manual:

                self.add_label_near(x, y, inline, inline_spacing)

        elif manual:

            print('Select label locations manually using first mouse button.')

            print('End manual selection with second mouse button.')

            if not inline:

                print('Remove last label by clicking third mouse button.')

            mpl._blocking_input.blocking_input_loop(

                self.axes.get_figure(root=True),

                ["button_press_event", "key_press_event"],

                timeout=-1, handler=functools.partial(

                    _contour_labeler_event_handler,

                    self, inline, inline_spacing))

        else:

            self.labels(inline, inline_spacing)



        return cbook.silent_list('text.Text', self.labelTexts)



    def print_label(self, linecontour, labelwidth):

        

        return (len(linecontour) > 10 * labelwidth

                or (len(linecontour)

                    and (np.ptp(linecontour, axis=0) > 1.2 * labelwidth).any()))



    def too_close(self, x, y, lw):

        

        thresh = (1.2 * lw) ** 2

        return any((x - loc[0]) ** 2 + (y - loc[1]) ** 2 < thresh

                   for loc in self.labelXYs)



    def _get_nth_label_width(self, nth):

        

        fig = self.axes.get_figure(root=False)

        renderer = fig.get_figure(root=True)._get_renderer()

        return (Text(0, 0,

                     self.get_text(self.labelLevelList[nth], self.labelFmt),

                     figure=fig, fontproperties=self._label_font_props)

                .get_window_extent(renderer).width)



    def get_text(self, lev, fmt):

        

        if isinstance(lev, str):

            return lev

        elif isinstance(fmt, dict):

            return fmt.get(lev, '%1.3f')

        elif callable(getattr(fmt, "format_ticks", None)):

            return fmt.format_ticks([*self.labelLevelList, lev])[-1]

        elif callable(fmt):

            return fmt(lev)

        else:

            return fmt % lev



    def locate_label(self, linecontour, labelwidth):

        

        ctr_size = len(linecontour)

        n_blocks = int(np.ceil(ctr_size / labelwidth)) if labelwidth > 1 else 1

        block_size = ctr_size if n_blocks == 1 else int(labelwidth)

                                                                              

                                                                               

                                                                   

        xx = np.resize(linecontour[:, 0], (n_blocks, block_size))

        yy = np.resize(linecontour[:, 1], (n_blocks, block_size))

        yfirst = yy[:, :1]

        ylast = yy[:, -1:]

        xfirst = xx[:, :1]

        xlast = xx[:, -1:]

        s = (yfirst - yy) * (xlast - xfirst) - (xfirst - xx) * (ylast - yfirst)

        l = np.hypot(xlast - xfirst, ylast - yfirst)

                                                                              

        with np.errstate(divide='ignore', invalid='ignore'):

            distances = (abs(s) / l).sum(axis=-1)

                                                                            

                                                                            

                                                   

        hbsize = block_size // 2

        adist = np.argsort(distances)

                                                                              

                         

        for idx in np.append(adist, adist[0]):

            x, y = xx[idx, hbsize], yy[idx, hbsize]

            if not self.too_close(x, y, labelwidth):

                break

        return x, y, (idx * block_size + hbsize) % ctr_size



    def _split_path_and_get_label_rotation(self, path, idx, screen_pos, lw, spacing=5):

        

        xys = path.vertices

        codes = path.codes



                                                                                        

                                                                                   

                                                                                        

                                                                               

                                                                                        

                                             

        pos = self.get_transform().inverted().transform(screen_pos)

        if not np.allclose(pos, xys[idx]):

            xys = np.insert(xys, idx, pos, axis=0)

            codes = np.insert(codes, idx, Path.LINETO)



                                                                                     

                                                                               

                                                    

        movetos = (codes == Path.MOVETO).nonzero()[0]

        start = movetos[movetos <= idx][-1]

        try:

            stop = movetos[movetos > idx][0]

        except IndexError:

            stop = len(codes)



                                                        

        cc_xys = xys[start:stop]

        idx -= start



                                                                       

        is_closed_path = codes[stop - 1] == Path.CLOSEPOLY

        if is_closed_path:

            cc_xys = np.concatenate([cc_xys[idx:-1], cc_xys[:idx+1]])

            idx = 0



                                                              

        def interp_vec(x, xp, fp): return [np.interp(x, xp, col) for col in fp.T]



                                                                                      

        screen_xys = self.get_transform().transform(cc_xys)

        path_cpls = np.insert(

            np.cumsum(np.hypot(*np.diff(screen_xys, axis=0).T)), 0, 0)

        path_cpls -= path_cpls[idx]



                                                                   

        target_cpls = np.array([-lw/2, lw/2])

        if is_closed_path:                                                

            target_cpls[0] += (path_cpls[-1] - path_cpls[0])

        (sx0, sx1), (sy0, sy1) = interp_vec(target_cpls, path_cpls, screen_xys)

        angle = np.rad2deg(np.arctan2(sy1 - sy0, sx1 - sx0))                 

        if self.rightside_up:                                          

            angle = (angle + 90) % 180 - 90



        target_cpls += [-spacing, +spacing]                            



                                                                              

        i0, i1 = np.interp(target_cpls, path_cpls, range(len(path_cpls)),

                           left=-1, right=-1)

        i0 = math.floor(i0)

        i1 = math.ceil(i1)

        (x0, x1), (y0, y1) = interp_vec(target_cpls, path_cpls, cc_xys)



                                                            

        new_xy_blocks = []

        new_code_blocks = []

        if is_closed_path:

            if i0 != -1 and i1 != -1:

                                                                                  

                                                                                

                                                      

                points = cc_xys[i1:i0+1]

                new_xy_blocks.extend([[(x1, y1)], points, [(x0, y0)]])

                nlines = len(points) + 1

                new_code_blocks.extend([[Path.MOVETO], [Path.LINETO] * nlines])

        else:

            if i0 != -1:

                new_xy_blocks.extend([cc_xys[:i0 + 1], [(x0, y0)]])

                new_code_blocks.extend([[Path.MOVETO], [Path.LINETO] * (i0 + 1)])

            if i1 != -1:

                new_xy_blocks.extend([[(x1, y1)], cc_xys[i1:]])

                new_code_blocks.extend([

                    [Path.MOVETO], [Path.LINETO] * (len(cc_xys) - i1)])



                                

        xys = np.concatenate([xys[:start], *new_xy_blocks, xys[stop:]])

        codes = np.concatenate([codes[:start], *new_code_blocks, codes[stop:]])



        return angle, Path(xys, codes)



    def add_label(self, x, y, rotation, lev, cvalue):

        

        data_x, data_y = self.axes.transData.inverted().transform((x, y))

        t = Text(

            data_x, data_y,

            text=self.get_text(lev, self.labelFmt),

            rotation=rotation,

            horizontalalignment='center', verticalalignment='center',

            zorder=self._clabel_zorder,

            color=self.labelMappable.to_rgba(cvalue, alpha=self.get_alpha()),

            fontproperties=self._label_font_props,

            clip_box=self.axes.bbox)

        if self._use_clabeltext:

            data_rotation, = self.axes.transData.inverted().transform_angles(

                [rotation], [[x, y]])

            t.set(rotation=data_rotation, transform_rotates_text=True)

        self.labelTexts.append(t)

        self.labelCValues.append(cvalue)

        self.labelXYs.append((x, y))

                                                                         

        self.axes.add_artist(t)



    def add_label_near(self, x, y, inline=True, inline_spacing=5,

                       transform=None):

        



        if transform is None:

            transform = self.axes.transData

        if transform:

            x, y = transform.transform((x, y))



        idx_level_min, idx_vtx_min, proj = self._find_nearest_contour(

            (x, y), self.labelIndiceList)

        path = self._paths[idx_level_min]

        level = self.labelIndiceList.index(idx_level_min)

        label_width = self._get_nth_label_width(level)

        rotation, path = self._split_path_and_get_label_rotation(

            path, idx_vtx_min, proj, label_width, inline_spacing)

        self.add_label(*proj, rotation, self.labelLevelList[idx_level_min],

                       self.labelCValueList[idx_level_min])



        if inline:

            self._paths[idx_level_min] = path



    def pop_label(self, index=-1):

        

        self.labelCValues.pop(index)

        t = self.labelTexts.pop(index)

        t.remove()



    def labels(self, inline, inline_spacing):

        for idx, (icon, lev, cvalue) in enumerate(zip(

                self.labelIndiceList,

                self.labelLevelList,

                self.labelCValueList,

        )):

            trans = self.get_transform()

            label_width = self._get_nth_label_width(idx)

            additions = []

            for subpath in self._paths[icon]._iter_connected_components():

                screen_xys = trans.transform(subpath.vertices)

                                                  

                if self.print_label(screen_xys, label_width):

                    x, y, idx = self.locate_label(screen_xys, label_width)

                    rotation, path = self._split_path_and_get_label_rotation(

                        subpath, idx, (x, y),

                        label_width, inline_spacing)

                    self.add_label(x, y, rotation, lev, cvalue)                     

                    if inline:                               

                        additions.append(path)

                else:                                      

                    additions.append(subpath)

                                                                                       

                          

            if inline:

                self._paths[icon] = Path.make_compound_path(*additions)



    def remove(self):

        super().remove()

        for text in self.labelTexts:

            text.remove()





def _find_closest_point_on_path(xys, p):

    

    if len(xys) == 1:

        return (((p - xys[0]) ** 2).sum(), xys[0], (0, 0))

    dxys = xys[1:] - xys[:-1]                               

    norms = (dxys ** 2).sum(axis=1)

    norms[norms == 0] = 1                                                

    rel_projs = np.clip(                                                     

        ((p - xys[:-1]) * dxys).sum(axis=1) / norms,

        0, 1)[:, None]

    projs = xys[:-1] + rel_projs * dxys                                        

    d2s = ((projs - p) ** 2).sum(axis=1)                      

    imin = np.argmin(d2s)

    return (d2s[imin], projs[imin], (imin, imin+1))





_docstring.interpd.register(contour_set_attributes=r"""
Attributes
----------
levels : array
    The values of the contour levels.

layers : array
    Same as levels for line contours; half-way between
    levels for filled contours.  See ``ContourSet._process_colors``.
""")





@_docstring.interpd

class ContourSet(ContourLabeler, mcoll.Collection):

    



    def __init__(self, ax, *args,

                 levels=None, filled=False, linewidths=None, linestyles=None,

                 hatches=(None,), alpha=None, origin=None, extent=None,

                 cmap=None, colors=None, norm=None, vmin=None, vmax=None,

                 colorizer=None, extend='neither', antialiased=None, nchunk=0,

                 locator=None, transform=None, negative_linestyles=None,

                 **kwargs):

        

        if antialiased is None and filled:

                                                                      

            antialiased = False

                                                                  

                                                                         

        super().__init__(

            antialiaseds=antialiased,

            alpha=alpha,

            transform=transform,

            colorizer=colorizer,

        )

        self.axes = ax

        self.levels = levels

        self.filled = filled

        self.hatches = hatches

        self.origin = origin

        self.extent = extent

        self.colors = colors

        self.extend = extend



        self.nchunk = nchunk

        self.locator = locator



        if "color" in kwargs:

            raise _api.kwarg_error("ContourSet.__init__", "color")



        if colorizer:

            self._set_colorizer_check_keywords(colorizer, cmap=cmap,

                                               norm=norm, vmin=vmin,

                                               vmax=vmax, colors=colors)

            norm = colorizer.norm

            cmap = colorizer.cmap

        if (isinstance(norm, mcolors.LogNorm)

                or isinstance(self.locator, ticker.LogLocator)):

            self.logscale = True

            if norm is None:

                norm = mcolors.LogNorm()

        else:

            self.logscale = False



        _api.check_in_list([None, 'lower', 'upper', 'image'], origin=origin)

        if self.extent is not None and len(self.extent) != 4:

            raise ValueError(

                "If given, 'extent' must be None or (x0, x1, y0, y1)")

        if self.colors is not None and cmap is not None:

            raise ValueError('Either colors or cmap must be None')

        if self.origin == 'image':

            self.origin = mpl.rcParams['image.origin']



        self._orig_linestyles = linestyles                              

        self.negative_linestyles = mpl._val_or_rc(negative_linestyles,

                                                  'contour.negative_linestyle')



        kwargs = self._process_args(*args, **kwargs)

        self._process_levels()



        self._extend_min = self.extend in ['min', 'both']

        self._extend_max = self.extend in ['max', 'both']

        if self.colors is not None:

            if mcolors.is_color_like(self.colors):

                color_sequence = [self.colors]

            else:

                color_sequence = self.colors



            ncolors = len(self.levels)

            if self.filled:

                ncolors -= 1

            i0 = 0



                                                                     

                                   



            use_set_under_over = False

                                                                            

                                                                             

                                                                              

                                                       

            total_levels = (ncolors +

                            int(self._extend_min) +

                            int(self._extend_max))

            if (len(color_sequence) == total_levels and

                    (self._extend_min or self._extend_max)):

                use_set_under_over = True

                if self._extend_min:

                    i0 = 1



            cmap = mcolors.ListedColormap(

                cbook._resize_sequence(color_sequence[i0:], ncolors))



            if use_set_under_over:

                if self._extend_min:

                    cmap.set_under(color_sequence[0])

                if self._extend_max:

                    cmap.set_over(color_sequence[-1])



                                              

        self.labelTexts = []

        self.labelCValues = []



        self.set_cmap(cmap)

        if norm is not None:

            self.set_norm(norm)

        with self.norm.callbacks.blocked(signal="changed"):

            if vmin is not None:

                self.norm.vmin = vmin

            if vmax is not None:

                self.norm.vmax = vmax

        self.norm._changed()

        self._process_colors()



        if self._paths is None:

            self._paths = self._make_paths_from_contour_generator()



        if self.filled:

            if linewidths is not None:

                _api.warn_external('linewidths is ignored by contourf')

                                             

            lowers, uppers = self._get_lowers_and_uppers()

            self.set(edgecolor="none")

        else:

            self.set(

                facecolor="none",

                linewidths=self._process_linewidths(linewidths),

                linestyle=self._process_linestyles(linestyles),

                label="_nolegend_",

                                                                           

                                                                              

                zorder=2,

            )

        self.set(**kwargs)                                          



        self.axes.add_collection(self, autolim=False)

        self.sticky_edges.x[:] = [self._mins[0], self._maxs[0]]

        self.sticky_edges.y[:] = [self._mins[1], self._maxs[1]]

        self.axes.update_datalim([self._mins, self._maxs])

        self.axes.autoscale_view(tight=True)



        self.changed()                  



    allsegs = property(lambda self: [

        [subp.vertices for subp in p._iter_connected_components()]

        for p in self.get_paths()])

    allkinds = property(lambda self: [

        [subp.codes for subp in p._iter_connected_components()]

        for p in self.get_paths()])

    alpha = property(lambda self: self.get_alpha())

    linestyles = property(lambda self: self._orig_linestyles)



    def get_transform(self):

        

        if self._transform is None:

            self._transform = self.axes.transData

        elif (not isinstance(self._transform, mtransforms.Transform)

              and hasattr(self._transform, '_as_mpl_transform')):

            self._transform = self._transform._as_mpl_transform(self.axes)

        return self._transform



    def __getstate__(self):

        state = self.__dict__.copy()

                                                                           

                                                                           

                          

        state['_contour_generator'] = None

        return state



    def legend_elements(self, variable_name='x', str_format=str):

        

        artists = []

        labels = []



        if self.filled:

            lowers, uppers = self._get_lowers_and_uppers()

            n_levels = len(self._paths)

            for idx in range(n_levels):

                artists.append(mpatches.Rectangle(

                    (0, 0), 1, 1,

                    facecolor=self.get_facecolor()[idx],

                    hatch=self.hatches[idx % len(self.hatches)],

                ))

                lower = str_format(lowers[idx])

                upper = str_format(uppers[idx])

                if idx == 0 and self.extend in ('min', 'both'):

                    labels.append(fr'${variable_name} \leq {lower}s$')

                elif idx == n_levels - 1 and self.extend in ('max', 'both'):

                    labels.append(fr'${variable_name} > {upper}s$')

                else:

                    labels.append(fr'${lower} < {variable_name} \leq {upper}$')

        else:

            for idx, level in enumerate(self.levels):

                artists.append(Line2D(

                    [], [],

                    color=self.get_edgecolor()[idx],

                    linewidth=self.get_linewidths()[idx],

                    linestyle=self.get_linestyles()[idx],

                ))

                labels.append(fr'${variable_name} = {str_format(level)}$')



        return artists, labels



    def _process_args(self, *args, **kwargs):

        

        self.levels = args[0]

        allsegs = args[1]

        allkinds = args[2] if len(args) > 2 else None

        self.zmax = np.max(self.levels)

        self.zmin = np.min(self.levels)



        if allkinds is None:

            allkinds = [[None] * len(segs) for segs in allsegs]



                                              

        if self.filled:

            if len(allsegs) != len(self.levels) - 1:

                raise ValueError('must be one less number of segments as '

                                 'levels')

        else:

            if len(allsegs) != len(self.levels):

                raise ValueError('must be same number of segments as levels')



                                   

        if len(allkinds) != len(allsegs):

            raise ValueError('allkinds has different length to allsegs')



                                                            

        flatseglist = [s for seg in allsegs for s in seg]

        points = np.concatenate(flatseglist, axis=0)

        self._mins = points.min(axis=0)

        self._maxs = points.max(axis=0)



                                                                                      

                                                                                        

                                                                                      

                                                                                     

                                                       

        self._paths = [Path.make_compound_path(*map(Path, segs, kinds))

                       for segs, kinds in zip(allsegs, allkinds)]



        return kwargs



    def _make_paths_from_contour_generator(self):

        

        if self._paths is not None:

            return self._paths

        cg = self._contour_generator

        empty_path = Path(np.empty((0, 2)))

        vertices_and_codes = (

            map(cg.create_filled_contour, *self._get_lowers_and_uppers())

            if self.filled else

            map(cg.create_contour, self.levels))

        return [Path(np.concatenate(vs), np.concatenate(cs)) if len(vs) else empty_path

                for vs, cs in vertices_and_codes]



    def _get_lowers_and_uppers(self):

        

        lowers = self._levels[:-1]

        if self.zmin == lowers[0]:

                                                       

            lowers = lowers.copy()                                   

            if self.logscale:

                lowers[0] = 0.99 * self.zmin

            else:

                lowers[0] -= 1

        uppers = self._levels[1:]

        return (lowers, uppers)



    def changed(self):

        if not hasattr(self, "cvalues"):

            self._process_colors()                 

                                                                     

                                                                 

                                                                        

                                                                

        self.norm.autoscale_None(self.levels)

        self.set_array(self.cvalues)

        self.update_scalarmappable()

        alphas = np.broadcast_to(self.get_alpha(), len(self.cvalues))

        for label, cv, alpha in zip(self.labelTexts, self.labelCValues, alphas):

            label.set_alpha(alpha)

            label.set_color(self.labelMappable.to_rgba(cv))

        super().changed()



    def _ensure_locator_exists(self, N):

        

        if self.locator is None:

            if self.logscale:

                self.locator = ticker.LogLocator(numticks=N)

            else:

                if N is None:

                    N = 7                      

                self.locator = ticker.MaxNLocator(N + 1, min_n_ticks=1)



    def _autolev(self):

        

        lev = self.locator.tick_values(self.zmin, self.zmax)



        try:

            if self.locator._symmetric:

                return lev

        except AttributeError:

            pass



                                                           

        under = np.nonzero(lev < self.zmin)[0]

        i0 = under[-1] if len(under) else 0

        over = np.nonzero(lev > self.zmax)[0]

        i1 = over[0] + 1 if len(over) else len(lev)

        if self.extend in ('min', 'both'):

            i0 += 1

        if self.extend in ('max', 'both'):

            i1 -= 1



        if i1 - i0 < 3:

            i0, i1 = 0, len(lev)



        return lev[i0:i1]



    def _process_contour_level_args(self, args, z_dtype):

        

        levels_arg = self.levels

        if levels_arg is None:

            if args:

                                                 

                levels_arg = args[0]

            elif np.issubdtype(z_dtype, bool):

                                                        

                levels_arg = [0, .5, 1] if self.filled else [.5]



        if isinstance(levels_arg, Integral) or levels_arg is None:

            self._ensure_locator_exists(levels_arg)

            self.levels = self._autolev()

        else:

            self.levels = np.asarray(levels_arg, np.float64)



        if self.filled and len(self.levels) < 2:

            raise ValueError("Filled contours require at least 2 levels.")

        if len(self.levels) > 1 and np.min(np.diff(self.levels)) <= 0.0:

            raise ValueError("Contour levels must be increasing")



    def _process_levels(self):

        

                                                                

                                                                

                                                       

        self._levels = list(self.levels)



        if self.logscale:

            lower, upper = 1e-250, 1e250

        else:

            lower, upper = -1e250, 1e250



        if self.extend in ('both', 'min'):

            self._levels.insert(0, lower)

        if self.extend in ('both', 'max'):

            self._levels.append(upper)

        self._levels = np.asarray(self._levels)



        if not self.filled:

            self.layers = self.levels

            return



                                                                  

        if self.logscale:

                                                               

            self.layers = (np.sqrt(self._levels[:-1])

                           * np.sqrt(self._levels[1:]))

        else:

            self.layers = 0.5 * (self._levels[:-1] + self._levels[1:])



    def _process_colors(self):

        

        self.monochrome = self.cmap.monochrome

        if self.colors is not None:

                                                    

            i0, i1 = 0, len(self.levels)

            if self.filled:

                i1 -= 1

                                                          

                if self.extend in ('both', 'min'):

                    i0 -= 1

                if self.extend in ('both', 'max'):

                    i1 += 1

            self.cvalues = list(range(i0, i1))

            self.set_norm(mcolors.NoNorm())

        else:

            self.cvalues = self.layers

        self.norm.autoscale_None(self.levels)

        self.set_array(self.cvalues)

        self.update_scalarmappable()

        if self.extend in ('both', 'max', 'min'):

            self.norm.clip = False



    def _process_linewidths(self, linewidths):

        Nlev = len(self.levels)

        if linewidths is None:

            default_linewidth = mpl.rcParams['contour.linewidth']

            if default_linewidth is None:

                default_linewidth = mpl.rcParams['lines.linewidth']

            return [default_linewidth] * Nlev

        elif not np.iterable(linewidths):

            return [linewidths] * Nlev

        else:

            linewidths = list(linewidths)

            return (linewidths * math.ceil(Nlev / len(linewidths)))[:Nlev]



    def _process_linestyles(self, linestyles):

        Nlev = len(self.levels)

        if linestyles is None:

            tlinestyles = ['solid'] * Nlev

            if self.monochrome:

                eps = - (self.zmax - self.zmin) * 1e-15

                for i, lev in enumerate(self.levels):

                    if lev < eps:

                        tlinestyles[i] = self.negative_linestyles

        else:

            if isinstance(linestyles, str):

                tlinestyles = [linestyles] * Nlev

            elif np.iterable(linestyles):

                tlinestyles = list(linestyles)

                if len(tlinestyles) < Nlev:

                    nreps = int(np.ceil(Nlev / len(linestyles)))

                    tlinestyles = tlinestyles * nreps

                if len(tlinestyles) > Nlev:

                    tlinestyles = tlinestyles[:Nlev]

            else:

                raise ValueError("Unrecognized type for linestyles kwarg")

        return tlinestyles



    def _find_nearest_contour(self, xy, indices=None):

        



                                                                                      

                                                                                    

                                              



        if self.filled:

            raise ValueError("Method does not support filled contours")



        if indices is None:

            indices = range(len(self._paths))



        d2min = np.inf

        idx_level_min = idx_vtx_min = proj_min = None



        for idx_level in indices:

            path = self._paths[idx_level]

            idx_vtx_start = 0

            for subpath in path._iter_connected_components():

                if not len(subpath.vertices):

                    continue

                lc = self.get_transform().transform(subpath.vertices)

                d2, proj, leg = _find_closest_point_on_path(lc, xy)

                if d2 < d2min:

                    d2min = d2

                    idx_level_min = idx_level

                    idx_vtx_min = leg[1] + idx_vtx_start

                    proj_min = proj

                idx_vtx_start += len(subpath)



        return idx_level_min, idx_vtx_min, proj_min



    def find_nearest_contour(self, x, y, indices=None, pixel=True):

        

        segment = index = d2 = None



        with ExitStack() as stack:

            if not pixel:

                                                                                    

                                                                                     

                stack.enter_context(self._cm_set(

                    transform=mtransforms.IdentityTransform()))



            i_level, i_vtx, (xmin, ymin) = self._find_nearest_contour((x, y), indices)



        if i_level is not None:

            cc_cumlens = np.cumsum(

                [*map(len, self._paths[i_level]._iter_connected_components())])

            segment = cc_cumlens.searchsorted(i_vtx, "right")

            index = i_vtx if segment == 0 else i_vtx - cc_cumlens[segment - 1]

            d2 = (xmin-x)**2 + (ymin-y)**2



        return (i_level, segment, index, xmin, ymin, d2)



    @artist.allow_rasterization

    def draw(self, renderer):

        paths = self._paths

        n_paths = len(paths)

        if not self.filled or all(hatch is None for hatch in self.hatches):

            super().draw(renderer)

            return

                                                               

        edgecolors = self.get_edgecolors()

        if edgecolors.size == 0:

            edgecolors = ("none",)

        for idx in range(n_paths):

            with cbook._setattr_cm(self, _paths=[paths[idx]]), self._cm_set(

                hatch=self.hatches[idx % len(self.hatches)],

                array=[self.get_array()[idx]],

                linewidths=[self.get_linewidths()[idx % len(self.get_linewidths())]],

                linestyles=[self.get_linestyles()[idx % len(self.get_linestyles())]],

                edgecolors=edgecolors[idx % len(edgecolors)],

            ):

                super().draw(renderer)





@_docstring.interpd

class QuadContourSet(ContourSet):

    



    def _process_args(self, *args, corner_mask=None, algorithm=None, **kwargs):

        

        if args and isinstance(args[0], QuadContourSet):

            if self.levels is None:

                self.levels = args[0].levels

            self.zmin = args[0].zmin

            self.zmax = args[0].zmax

            self._corner_mask = args[0]._corner_mask

            contour_generator = args[0]._contour_generator

            self._mins = args[0]._mins

            self._maxs = args[0]._maxs

            self._algorithm = args[0]._algorithm

        else:

            import contourpy



            algorithm = mpl._val_or_rc(algorithm, 'contour.algorithm')

            mpl.rcParams.validate["contour.algorithm"](algorithm)

            self._algorithm = algorithm



            if corner_mask is None:

                if self._algorithm == "mpl2005":

                                                                         

                                                             

                    corner_mask = False

                else:

                    corner_mask = mpl.rcParams['contour.corner_mask']

            self._corner_mask = corner_mask



            x, y, z = self._contour_args(args, kwargs)



            contour_generator = contourpy.contour_generator(

                x, y, z, name=self._algorithm, corner_mask=self._corner_mask,

                line_type=contourpy.LineType.SeparateCode,

                fill_type=contourpy.FillType.OuterCode,

                chunk_size=self.nchunk)



            t = self.get_transform()



                                                                     

                                                                             

            if (t != self.axes.transData and

                    any(t.contains_branch_seperately(self.axes.transData))):

                trans_to_data = t - self.axes.transData

                pts = np.vstack([x.flat, y.flat]).T

                transformed_pts = trans_to_data.transform(pts)

                x = transformed_pts[..., 0]

                y = transformed_pts[..., 1]



            self._mins = [ma.min(x), ma.min(y)]

            self._maxs = [ma.max(x), ma.max(y)]



        self._contour_generator = contour_generator



        return kwargs



    def _contour_args(self, args, kwargs):

        if self.filled:

            fn = 'contourf'

        else:

            fn = 'contour'

        nargs = len(args)



        if 0 < nargs <= 2:

            z, *args = args

            z = ma.asarray(z)

            x, y = self._initialize_x_y(z)

        elif 2 < nargs <= 4:

            x, y, z_orig, *args = args

            x, y, z = self._check_xyz(x, y, z_orig, kwargs)



        else:

            raise _api.nargs_error(fn, takes="from 1 to 4", given=nargs)

        z = ma.masked_invalid(z, copy=False)

        self.zmax = z.max().astype(float)

        self.zmin = z.min().astype(float)

        if self.logscale and self.zmin <= 0:

            z = ma.masked_where(z <= 0, z)

            _api.warn_external('Log scale: values of z <= 0 have been masked')

            self.zmin = z.min().astype(float)

        self._process_contour_level_args(args, z.dtype)

        return (x, y, z)



    def _check_xyz(self, x, y, z, kwargs):

        

        x, y = self.axes._process_unit_info([("x", x), ("y", y)], kwargs)



        x = np.asarray(x, dtype=np.float64)

        y = np.asarray(y, dtype=np.float64)

        z = ma.asarray(z)



        if z.ndim != 2:

            raise TypeError(f"Input z must be 2D, not {z.ndim}D")

        if z.shape[0] < 2 or z.shape[1] < 2:

            raise TypeError(f"Input z must be at least a (2, 2) shaped array, "

                            f"but has shape {z.shape}")

        Ny, Nx = z.shape



        if x.ndim != y.ndim:

            raise TypeError(f"Number of dimensions of x ({x.ndim}) and y "

                            f"({y.ndim}) do not match")

        if x.ndim == 1:

            nx, = x.shape

            ny, = y.shape

            if nx != Nx:

                raise TypeError(f"Length of x ({nx}) must match number of "

                                f"columns in z ({Nx})")

            if ny != Ny:

                raise TypeError(f"Length of y ({ny}) must match number of "

                                f"rows in z ({Ny})")

            x, y = np.meshgrid(x, y)

        elif x.ndim == 2:

            if x.shape != z.shape:

                raise TypeError(

                    f"Shapes of x {x.shape} and z {z.shape} do not match")

            if y.shape != z.shape:

                raise TypeError(

                    f"Shapes of y {y.shape} and z {z.shape} do not match")

        else:

            raise TypeError(f"Inputs x and y must be 1D or 2D, not {x.ndim}D")



        return x, y, z



    def _initialize_x_y(self, z):

        

        if z.ndim != 2:

            raise TypeError(f"Input z must be 2D, not {z.ndim}D")

        elif z.shape[0] < 2 or z.shape[1] < 2:

            raise TypeError(f"Input z must be at least a (2, 2) shaped array, "

                            f"but has shape {z.shape}")

        else:

            Ny, Nx = z.shape

        if self.origin is None:                           

            if self.extent is None:

                return np.meshgrid(np.arange(Nx), np.arange(Ny))

            else:

                x0, x1, y0, y1 = self.extent

                x = np.linspace(x0, x1, Nx)

                y = np.linspace(y0, y1, Ny)

                return np.meshgrid(x, y)

                               

        if self.extent is None:

            x0, x1, y0, y1 = (0, Nx, 0, Ny)

        else:

            x0, x1, y0, y1 = self.extent

        dx = (x1 - x0) / Nx

        dy = (y1 - y0) / Ny

        x = x0 + (np.arange(Nx) + 0.5) * dx

        y = y0 + (np.arange(Ny) + 0.5) * dy

        if self.origin == 'upper':

            y = y[::-1]

        return np.meshgrid(x, y)





_docstring.interpd.register(contour_doc="""
`.contour` and `.contourf` draw contour lines and filled contours,
respectively.  Except as noted, function signatures and return values
are the same for both versions.

Parameters
----------
X, Y : array-like, optional
    The coordinates of the values in *Z*.

    *X* and *Y* must both be 2D with the same shape as *Z* (e.g.
    created via `numpy.meshgrid`), or they must both be 1-D such
    that ``len(X) == N`` is the number of columns in *Z* and
    ``len(Y) == M`` is the number of rows in *Z*.

    *X* and *Y* must both be ordered monotonically.

    If not given, they are assumed to be integer indices, i.e.
    ``X = range(N)``, ``Y = range(M)``.

Z : (M, N) array-like
    The height values over which the contour is drawn.  Color-mapping is
    controlled by *cmap*, *norm*, *vmin*, and *vmax*.

levels : int or array-like, optional
    Determines the number and positions of the contour lines / regions.

    If an int *n*, use `~matplotlib.ticker.MaxNLocator`, which tries
    to automatically choose no more than *n+1* "nice" contour levels
    between minimum and maximum numeric values of *Z*.

    If array-like, draw contour lines at the specified levels.
    The values must be in increasing order.

Returns
-------
`~.contour.QuadContourSet`

Other Parameters
----------------
corner_mask : bool, default: :rc:`contour.corner_mask`
    Enable/disable corner masking, which only has an effect if *Z* is
    a masked array.  If ``False``, any quad touching a masked point is
    masked out.  If ``True``, only the triangular corners of quads
    nearest those points are always masked out, other triangular
    corners comprising three unmasked points are contoured as usual.

colors : :mpltype:`color` or list of :mpltype:`color`, optional
    The colors of the levels, i.e. the lines for `.contour` and the
    areas for `.contourf`.

    The sequence is cycled for the levels in ascending order. If the
    sequence is shorter than the number of levels, it's repeated.

    As a shortcut, a single color may be used in place of one-element lists, i.e.
    ``'red'`` instead of ``['red']`` to color all levels with the same color.

    .. versionchanged:: 3.10
        Previously a single color had to be expressed as a string, but now any
        valid color format may be passed.

    By default (value *None*), the colormap specified by *cmap*
    will be used.

alpha : float, default: 1
    The alpha blending value, between 0 (transparent) and 1 (opaque).

%(cmap_doc)s

    This parameter is ignored if *colors* is set.

%(norm_doc)s

    This parameter is ignored if *colors* is set.

%(vmin_vmax_doc)s

    If *vmin* or *vmax* are not given, the default color scaling is based on
    *levels*.

    This parameter is ignored if *colors* is set.

%(colorizer_doc)s

    This parameter is ignored if *colors* is set.

origin : {*None*, 'upper', 'lower', 'image'}, default: None
    Determines the orientation and exact position of *Z* by specifying
    the position of ``Z[0, 0]``.  This is only relevant, if *X*, *Y*
    are not given.

    - *None*: ``Z[0, 0]`` is at X=0, Y=0 in the lower left corner.
    - 'lower': ``Z[0, 0]`` is at X=0.5, Y=0.5 in the lower left corner.
    - 'upper': ``Z[0, 0]`` is at X=N+0.5, Y=0.5 in the upper left
      corner.
    - 'image': Use the value from :rc:`image.origin`.

extent : (x0, x1, y0, y1), optional
    If *origin* is not *None*, then *extent* is interpreted as in
    `.imshow`: it gives the outer pixel boundaries. In this case, the
    position of Z[0, 0] is the center of the pixel, not a corner. If
    *origin* is *None*, then (*x0*, *y0*) is the position of Z[0, 0],
    and (*x1*, *y1*) is the position of Z[-1, -1].

    This argument is ignored if *X* and *Y* are specified in the call
    to contour.

locator : ticker.Locator subclass, optional
    The locator is used to determine the contour levels if they
    are not given explicitly via *levels*.
    Defaults to `~.ticker.MaxNLocator`.

extend : {'neither', 'both', 'min', 'max'}, default: 'neither'
    Determines the ``contourf``-coloring of values that are outside the
    *levels* range.

    If 'neither', values outside the *levels* range are not colored.
    If 'min', 'max' or 'both', color the values below, above or below
    and above the *levels* range.

    Values below ``min(levels)`` and above ``max(levels)`` are mapped
    to the under/over values of the `.Colormap`. Note that most
    colormaps do not have dedicated colors for these by default, so
    that the over and under values are the edge values of the colormap.
    You may want to set these values explicitly using
    `.Colormap.set_under` and `.Colormap.set_over`.

    .. note::

        An existing `.QuadContourSet` does not get notified if
        properties of its colormap are changed. Therefore, an explicit
        call `~.ContourSet.changed()` is needed after modifying the
        colormap. The explicit call can be left out, if a colorbar is
        assigned to the `.QuadContourSet` because it internally calls
        `~.ContourSet.changed()`.

    Example::

        x = np.arange(1, 10)
        y = x.reshape(-1, 1)
        h = x * y

        cs = plt.contourf(h, levels=[10, 30, 50],
            colors=['#808080', '#A0A0A0', '#C0C0C0'], extend='both')
        cs.cmap.set_over('red')
        cs.cmap.set_under('blue')
        cs.changed()

xunits, yunits : registered units, optional
    Override axis units by specifying an instance of a
    :class:`matplotlib.units.ConversionInterface`.

antialiased : bool, optional
    Enable antialiasing, overriding the defaults.  For
    filled contours, the default is *False*.  For line contours,
    it is taken from :rc:`lines.antialiased`.

nchunk : int >= 0, optional
    If 0, no subdivision of the domain.  Specify a positive integer to
    divide the domain into subdomains of *nchunk* by *nchunk* quads.
    Chunking reduces the maximum length of polygons generated by the
    contouring algorithm which reduces the rendering workload passed
    on to the backend and also requires slightly less RAM.  It can
    however introduce rendering artifacts at chunk boundaries depending
    on the backend, the *antialiased* flag and value of *alpha*.

linewidths : float or array-like, default: :rc:`contour.linewidth`
    *Only applies to* `.contour`.

    The line width of the contour lines.

    If a number, all levels will be plotted with this linewidth.

    If a sequence, the levels in ascending order will be plotted with
    the linewidths in the order specified.

    If None, this falls back to :rc:`lines.linewidth`.

linestyles : {*None*, 'solid', 'dashed', 'dashdot', 'dotted'}, optional
    *Only applies to* `.contour`.

    If *linestyles* is *None*, the default is 'solid' unless the lines are
    monochrome. In that case, negative contours will instead take their
    linestyle from the *negative_linestyles* argument.

    *linestyles* can also be an iterable of the above strings specifying a set
    of linestyles to be used. If this iterable is shorter than the number of
    contour levels it will be repeated as necessary.

negative_linestyles : {*None*, 'solid', 'dashed', 'dashdot', 'dotted'}, \
                       optional
    *Only applies to* `.contour`.

    If *linestyles* is *None* and the lines are monochrome, this argument
    specifies the line style for negative contours.

    If *negative_linestyles* is *None*, the default is taken from
    :rc:`contour.negative_linestyle`.

    *negative_linestyles* can also be an iterable of the above strings
    specifying a set of linestyles to be used. If this iterable is shorter than
    the number of contour levels it will be repeated as necessary.

hatches : list[str], optional
    *Only applies to* `.contourf`.

    A list of cross hatch patterns to use on the filled areas.
    If None, no hatching will be added to the contour.

algorithm : {'mpl2005', 'mpl2014', 'serial', 'threaded'}, optional
    Which contouring algorithm to use to calculate the contour lines and
    polygons. The algorithms are implemented in
    `ContourPy <https://github.com/contourpy/contourpy>`_, consult the
    `ContourPy documentation <https://contourpy.readthedocs.io>`_ for
    further information.

    The default is taken from :rc:`contour.algorithm`.

clip_path : `~matplotlib.patches.Patch` or `.Path` or `.TransformedPath`
    Set the clip path.  See `~matplotlib.artist.Artist.set_clip_path`.

    .. versionadded:: 3.8

data : indexable object, optional
    DATA_PARAMETER_PLACEHOLDER

rasterized : bool, optional
    *Only applies to* `.contourf`.
    Rasterize the contour plot when drawing vector graphics.  This can
    speed up rendering and produce smaller files for large data sets.
    See also :doc:`/gallery/misc/rasterization_demo`.


Notes
-----
1. `.contourf` differs from the MATLAB version in that it does not draw
   the polygon edges. To draw edges, add line contours with calls to
   `.contour`.

2. `.contourf` fills intervals that are closed at the top; that is, for
   boundaries *z1* and *z2*, the filled region is::

      z1 < Z <= z2

   except for the lowest interval, which is closed on both sides (i.e.
   it includes the lowest value).

3. `.contour` and `.contourf` use a `marching squares
   <https://en.wikipedia.org/wiki/Marching_squares>`_ algorithm to
   compute contour locations.  More information can be found in
   `ContourPy documentation <https://contourpy.readthedocs.io>`_.
""" % _docstring.interpd.params)

