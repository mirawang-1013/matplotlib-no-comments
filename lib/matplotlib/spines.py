from collections.abc import MutableMapping

import functools



import numpy as np



import matplotlib as mpl

from matplotlib import _api, _docstring

from matplotlib.artist import allow_rasterization

import matplotlib.transforms as mtransforms

import matplotlib.patches as mpatches

import matplotlib.path as mpath





class Spine(mpatches.Patch):

    

    def __str__(self):

        return "Spine"



    @_docstring.interpd

    def __init__(self, axes, spine_type, path, **kwargs):

        

        super().__init__(**kwargs)

        self.axes = axes

        self.set_figure(self.axes.get_figure(root=False))

        self.spine_type = spine_type

        self.set_facecolor('none')

        self.set_edgecolor(mpl.rcParams['axes.edgecolor'])

        self.set_linewidth(mpl.rcParams['axes.linewidth'])

        self.set_capstyle('projecting')

        self.axis = None



        self.set_zorder(2.5)

        self.set_transform(self.axes.transData)                     



        self._bounds = None                  



                                                                     

                                                                      

                                                                 

        self._position = None

        _api.check_isinstance(mpath.Path, path=path)

        self._path = path



                                                                  

                                                        

                                                                      

                                                                  

                                                                              

                                  

        self._patch_type = 'line'



                                                

                                                                        

        self._patch_transform = mtransforms.IdentityTransform()



    def set_patch_arc(self, center, radius, theta1, theta2):

        

        self._patch_type = 'arc'

        self._center = center

        self._width = radius * 2

        self._height = radius * 2

        self._theta1 = theta1

        self._theta2 = theta2

        self._path = mpath.Path.arc(theta1, theta2)

                                     

        self.set_transform(self.axes.transAxes)

        self.stale = True



    def set_patch_circle(self, center, radius):

        

        self._patch_type = 'circle'

        self._center = center

        self._width = radius * 2

        self._height = radius * 2

                                        

        self.set_transform(self.axes.transAxes)

        self.stale = True



    def set_patch_line(self):

        

        self._patch_type = 'line'

        self.stale = True



                                            

    def _recompute_transform(self):

        

        assert self._patch_type in ('arc', 'circle')

        center = (self.convert_xunits(self._center[0]),

                  self.convert_yunits(self._center[1]))

        width = self.convert_xunits(self._width)

        height = self.convert_yunits(self._height)

        self._patch_transform = mtransforms.Affine2D()
            .scale(width * 0.5, height * 0.5)
            .translate(*center)



    def get_patch_transform(self):

        if self._patch_type in ('arc', 'circle'):

            self._recompute_transform()

            return self._patch_transform

        else:

            return super().get_patch_transform()



    def get_window_extent(self, renderer=None):

        

                                                                               

        self._adjust_location()

        bb = super().get_window_extent(renderer=renderer)

        if self.axis is None or not self.axis.get_visible():

            return bb

        bboxes = [bb]

        drawn_ticks = self.axis._update_ticks()



        major_tick = next(iter({*drawn_ticks} & {*self.axis.majorTicks}), None)

        minor_tick = next(iter({*drawn_ticks} & {*self.axis.minorTicks}), None)

        for tick in [major_tick, minor_tick]:

            if tick is None:

                continue

            bb0 = bb.frozen()

            tickl = tick._size

            tickdir = tick._tickdir

            if tickdir == 'out':

                padout = 1

                padin = 0

            elif tickdir == 'in':

                padout = 0

                padin = 1

            else:

                padout = 0.5

                padin = 0.5

            dpi = self.get_figure(root=True).dpi

            padout = padout * tickl / 72 * dpi

            padin = padin * tickl / 72 * dpi



            if tick.tick1line.get_visible():

                if self.spine_type == 'left':

                    bb0.x0 = bb0.x0 - padout

                    bb0.x1 = bb0.x1 + padin

                elif self.spine_type == 'bottom':

                    bb0.y0 = bb0.y0 - padout

                    bb0.y1 = bb0.y1 + padin



            if tick.tick2line.get_visible():

                if self.spine_type == 'right':

                    bb0.x1 = bb0.x1 + padout

                    bb0.x0 = bb0.x0 - padin

                elif self.spine_type == 'top':

                    bb0.y1 = bb0.y1 + padout

                    bb0.y0 = bb0.y0 - padout

            bboxes.append(bb0)



        return mtransforms.Bbox.union(bboxes)



    def get_path(self):

        return self._path



    def _ensure_position_is_set(self):

        if self._position is None:

                              

            self._position = ('outward', 0.0)             

            self.set_position(self._position)



    def register_axis(self, axis):

        

        self.axis = axis

        self.stale = True



    def clear(self):

        

        self._clear()

        if self.axis is not None:

            self.axis.clear()



    def _clear(self):

        

        self._position = None                  



    def _get_bounds_or_viewLim(self):

        

        if self._bounds is not None:

            low, high = self._bounds

        elif self.spine_type in ('left', 'right'):

            low, high = self.axes.viewLim.intervaly

        elif self.spine_type in ('top', 'bottom'):

            low, high = self.axes.viewLim.intervalx

        else:

            raise ValueError(f'spine_type: {self.spine_type} not supported')

        return low, high



    def _adjust_location(self):

        



        if self.spine_type == 'circle':

            return



        low, high = self._get_bounds_or_viewLim()



        if self._patch_type == 'arc':

            if self.spine_type in ('bottom', 'top'):

                try:

                    direction = self.axes.get_theta_direction()

                except AttributeError:

                    direction = 1

                try:

                    offset = self.axes.get_theta_offset()

                except AttributeError:

                    offset = 0

                low = low * direction + offset

                high = high * direction + offset

                if low > high:

                    low, high = high, low



                self._path = mpath.Path.arc(np.rad2deg(low), np.rad2deg(high))



                if self.spine_type == 'bottom':

                    if self.axis is None:

                        tr = mtransforms.IdentityTransform()

                    else:

                        tr = self.axis.get_transform()

                    rmin, rmax = tr.transform(self.axes.viewLim.intervaly)

                    try:

                        rorigin = self.axes.get_rorigin()

                    except AttributeError:

                        rorigin = rmin

                    else:

                        rorigin = tr.transform(rorigin)

                    scaled_diameter = (rmin - rorigin) / (rmax - rorigin)

                    self._height = scaled_diameter

                    self._width = scaled_diameter



            else:

                raise ValueError('unable to set bounds for spine "%s"' %

                                 self.spine_type)

        else:

            v1 = self._path.vertices

            assert v1.shape == (2, 2), 'unexpected vertices shape'

            if self.spine_type in ['left', 'right']:

                v1[0, 1] = low

                v1[1, 1] = high

            elif self.spine_type in ['bottom', 'top']:

                v1[0, 0] = low

                v1[1, 0] = high

            else:

                raise ValueError('unable to set bounds for spine "%s"' %

                                 self.spine_type)



    @allow_rasterization

    def draw(self, renderer):

        self._adjust_location()

        ret = super().draw(renderer)

        self.stale = False

        return ret



    def set_position(self, position):

        

        if position in ('center', 'zero'):                     

            pass

        else:

            if len(position) != 2:

                raise ValueError("position should be 'center' or 2-tuple")

            if position[0] not in ['outward', 'axes', 'data']:

                raise ValueError("position[0] should be one of 'outward', "

                                 "'axes', or 'data' ")

        self._position = position

        self.set_transform(self.get_spine_transform())

        if self.axis is not None:

            self.axis.reset_ticks()

        self.stale = True



    def get_position(self):

        

        self._ensure_position_is_set()

        return self._position



    def get_spine_transform(self):

        

        self._ensure_position_is_set()



        position = self._position

        if isinstance(position, str):

            if position == 'center':

                position = ('axes', 0.5)

            elif position == 'zero':

                position = ('data', 0)

        assert len(position) == 2, 'position should be 2-tuple'

        position_type, amount = position

        _api.check_in_list(['axes', 'outward', 'data'],

                           position_type=position_type)

        if self.spine_type in ['left', 'right']:

            base_transform = self.axes.get_yaxis_transform(which='grid')

        elif self.spine_type in ['top', 'bottom']:

            base_transform = self.axes.get_xaxis_transform(which='grid')

        else:

            raise ValueError(f'unknown spine spine_type: {self.spine_type!r}')



        if position_type == 'outward':

            if amount == 0:                                

                return base_transform

            else:

                offset_vec = {'left': (-1, 0), 'right': (1, 0),

                              'bottom': (0, -1), 'top': (0, 1),

                              }[self.spine_type]

                                                  

                offset_dots = amount * np.array(offset_vec) / 72

                return (base_transform

                        + mtransforms.ScaledTranslation(

                            *offset_dots, self.get_figure(root=False).dpi_scale_trans))

        elif position_type == 'axes':

            if self.spine_type in ['left', 'right']:

                                                   

                return (mtransforms.Affine2D.from_values(0, 0, 0, 1, amount, 0)

                        + base_transform)

            elif self.spine_type in ['bottom', 'top']:

                                                   

                return (mtransforms.Affine2D.from_values(1, 0, 0, 0, 0, amount)

                        + base_transform)

        elif position_type == 'data':

            if self.spine_type in ('right', 'top'):

                                                                          

                                                                         

                                                                               

                amount -= 1

            if self.spine_type in ('left', 'right'):

                return mtransforms.blended_transform_factory(

                    mtransforms.Affine2D().translate(amount, 0)

                    + self.axes.transData,

                    self.axes.transData)

            elif self.spine_type in ('bottom', 'top'):

                return mtransforms.blended_transform_factory(

                    self.axes.transData,

                    mtransforms.Affine2D().translate(0, amount)

                    + self.axes.transData)



    def set_bounds(self, low=None, high=None):

        

        if self.spine_type == 'circle':

            raise ValueError(

                'set_bounds() method incompatible with circular spines')

        if high is None and np.iterable(low):

            low, high = low

        old_low, old_high = self._get_bounds_or_viewLim()

        if low is None:

            low = old_low

        if high is None:

            high = old_high

        self._bounds = (low, high)

        self.stale = True



    def get_bounds(self):

        

        return self._bounds



    @classmethod

    def linear_spine(cls, axes, spine_type, **kwargs):

        

                                                                    

        if spine_type == 'left':

            path = mpath.Path([(0.0, 0.999), (0.0, 0.999)])

        elif spine_type == 'right':

            path = mpath.Path([(1.0, 0.999), (1.0, 0.999)])

        elif spine_type == 'bottom':

            path = mpath.Path([(0.999, 0.0), (0.999, 0.0)])

        elif spine_type == 'top':

            path = mpath.Path([(0.999, 1.0), (0.999, 1.0)])

        else:

            raise ValueError('unable to make path for spine "%s"' % spine_type)

        result = cls(axes, spine_type, path, **kwargs)

        result.set_visible(mpl.rcParams[f'axes.spines.{spine_type}'])



        return result



    @classmethod

    def arc_spine(cls, axes, spine_type, center, radius, theta1, theta2,

                  **kwargs):

        

        path = mpath.Path.arc(theta1, theta2)

        result = cls(axes, spine_type, path, **kwargs)

        result.set_patch_arc(center, radius, theta1, theta2)

        return result



    @classmethod

    def circular_spine(cls, axes, center, radius, **kwargs):

        

        path = mpath.Path.unit_circle()

        spine_type = 'circle'

        result = cls(axes, spine_type, path, **kwargs)

        result.set_patch_circle(center, radius)

        return result



    def set_color(self, c):

        

        self.set_edgecolor(c)

        self.stale = True





class SpinesProxy:

    

    def __init__(self, spine_dict):

        self._spine_dict = spine_dict



    def __getattr__(self, name):

        broadcast_targets = [spine for spine in self._spine_dict.values()

                             if hasattr(spine, name)]

        if (name != 'set' and not name.startswith('set_')) or not broadcast_targets:

            raise AttributeError(

                f"'SpinesProxy' object has no attribute '{name}'")



        def x(_targets, _funcname, *args, **kwargs):

            for spine in _targets:

                getattr(spine, _funcname)(*args, **kwargs)

        x = functools.partial(x, broadcast_targets, name)

        x.__doc__ = broadcast_targets[0].__doc__

        return x



    def __dir__(self):

        names = []

        for spine in self._spine_dict.values():

            names.extend(name

                         for name in dir(spine) if name.startswith('set_'))

        return list(sorted(set(names)))





class Spines(MutableMapping):

    

    def __init__(self, **kwargs):

        self._dict = kwargs



    @classmethod

    def from_dict(cls, d):

        return cls(**d)



    def __getstate__(self):

        return self._dict



    def __setstate__(self, state):

        self.__init__(**state)



    def __getattr__(self, name):

        try:

            return self._dict[name]

        except KeyError:

            raise AttributeError(

                f"'Spines' object does not contain a '{name}' spine")



    def __getitem__(self, key):

        if isinstance(key, list):

            unknown_keys = [k for k in key if k not in self._dict]

            if unknown_keys:

                raise KeyError(', '.join(unknown_keys))

            return SpinesProxy({k: v for k, v in self._dict.items()

                                if k in key})

        if isinstance(key, tuple):

            raise ValueError('Multiple spines must be passed as a single list')

        if isinstance(key, slice):

            if key.start is None and key.stop is None and key.step is None:

                return SpinesProxy(self._dict)

            else:

                raise ValueError(

                    'Spines does not support slicing except for the fully '

                    'open slice [:] to access all spines.')

        return self._dict[key]



    def __setitem__(self, key, value):

                                                      

        self._dict[key] = value



    def __delitem__(self, key):

                                                        

        del self._dict[key]



    def __iter__(self):

        return iter(self._dict)



    def __len__(self):

        return len(self._dict)

