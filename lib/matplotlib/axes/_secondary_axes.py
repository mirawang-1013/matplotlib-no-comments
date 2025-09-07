import functools

import numbers



import numpy as np



from matplotlib import _api, _docstring, transforms

import matplotlib.ticker as mticker

from matplotlib.axes._base import _AxesBase, _TransformedBoundsLocator

from matplotlib.axis import Axis

from matplotlib.transforms import Transform





class SecondaryAxis(_AxesBase):

    



    def __init__(self, parent, orientation, location, functions, transform=None,

                 **kwargs):

        

        _api.check_in_list(["x", "y"], orientation=orientation)

        self._functions = functions

        self._parent = parent

        self._orientation = orientation

        self._ticks_set = False



        fig = self._parent.get_figure(root=False)

        if self._orientation == 'x':

            super().__init__(fig, [0, 1., 1, 0.0001], **kwargs)

            self._axis = self.xaxis

            self._locstrings = ['top', 'bottom']

            self._otherstrings = ['left', 'right']

        else:       

            super().__init__(fig, [0, 1., 0.0001, 1], **kwargs)

            self._axis = self.yaxis

            self._locstrings = ['right', 'left']

            self._otherstrings = ['top', 'bottom']

        self._parentscale = None

                                                                 



        self.set_location(location, transform)

        self.set_functions(functions)



                  

        otheraxis = self.yaxis if self._orientation == 'x' else self.xaxis

        otheraxis.set_major_locator(mticker.NullLocator())

        otheraxis.set_ticks_position('none')



        self.spines[self._otherstrings].set_visible(False)

        self.spines[self._locstrings].set_visible(True)



        if self._pos < 0.5:

                                          

            self._locstrings = self._locstrings[::-1]

        self.set_alignment(self._locstrings[0])



    def set_alignment(self, align):

        

        _api.check_in_list(self._locstrings, align=align)

        if align == self._locstrings[1]:                                   

            self._locstrings = self._locstrings[::-1]

        self.spines[self._locstrings[0]].set_visible(True)

        self.spines[self._locstrings[1]].set_visible(False)

        self._axis.set_ticks_position(align)

        self._axis.set_label_position(align)



    def set_location(self, location, transform=None):

        



        _api.check_isinstance((transforms.Transform, None), transform=transform)



                                                                   

        if isinstance(location, str):

            _api.check_in_list(self._locstrings, location=location)

            self._pos = 1. if location in ('top', 'right') else 0.

        elif isinstance(location, numbers.Real):

            self._pos = location

        else:

            raise ValueError(

                f"location must be {self._locstrings[0]!r}, "

                f"{self._locstrings[1]!r}, or a float, not {location!r}")



        self._loc = location



        if self._orientation == 'x':

                                                                               

                                                                              

            bounds = [0, self._pos, 1., 1e-10]



                                                                              

                                                                                

                                   

            if transform is not None:

                transform = transforms.blended_transform_factory(

                    self._parent.transAxes, transform)

        else:       

            bounds = [self._pos, 0, 1e-10, 1]

            if transform is not None:

                transform = transforms.blended_transform_factory(

                    transform, self._parent.transAxes)                       



                                                                 

        if transform is None:

            transform = self._parent.transAxes



                                                                         

                                                                     

                             

                                                             

        self.set_axes_locator(_TransformedBoundsLocator(bounds, transform))



    def apply_aspect(self, position=None):

                              

        self._set_lims()

        super().apply_aspect(position)



    @functools.wraps(_AxesBase.set_xticks)

    def set_xticks(self, *args, **kwargs):

        if self._orientation == "y":

            raise TypeError("Cannot set xticks on a secondary y-axis")

        ret = super().set_xticks(*args, **kwargs)

        self._ticks_set = True

        return ret



    @functools.wraps(_AxesBase.set_yticks)

    def set_yticks(self, *args, **kwargs):

        if self._orientation == "x":

            raise TypeError("Cannot set yticks on a secondary x-axis")

        ret = super().set_yticks(*args, **kwargs)

        self._ticks_set = True

        return ret



    @functools.wraps(Axis.set_ticks)

    def set_ticks(self, *args, **kwargs):

        ret = self._axis.set_ticks(*args, **kwargs)

        self._ticks_set = True

        return ret



    def set_functions(self, functions):

        



        if (isinstance(functions, tuple) and len(functions) == 2 and

                callable(functions[0]) and callable(functions[1])):

                                                                     

                                  

            self._functions = functions

        elif isinstance(functions, Transform):

            self._functions = (

                 functions.transform,

                 lambda x: functions.inverted().transform(x)

            )

        elif functions is None:

            self._functions = (lambda x: x, lambda x: x)

        else:

            raise ValueError('functions argument of secondary Axes '

                             'must be a two-tuple of callable functions '

                             'with the first function being the transform '

                             'and the second being the inverse')

        self._set_scale()



    def draw(self, renderer):

        

        self._set_lims()

                                                                   

        self._set_scale()

        super().draw(renderer)



    def _set_scale(self):

        



        if self._orientation == 'x':

            pscale = self._parent.xaxis.get_scale()

            set_scale = self.set_xscale

        else:       

            pscale = self._parent.yaxis.get_scale()

            set_scale = self.set_yscale

        if pscale == self._parentscale:

            return



        if self._ticks_set:

            ticks = self._axis.get_ticklocs()



                                                                 

        set_scale('functionlog' if pscale == 'log' else 'function',

                  functions=self._functions[::-1])



                                                              

                                                    

        if self._ticks_set:

            self._axis.set_major_locator(mticker.FixedLocator(ticks))



                                                                         

        self._parentscale = pscale



    def _set_lims(self):

        

        if self._orientation == 'x':

            lims = self._parent.get_xlim()

            set_lim = self.set_xlim

        else:       

            lims = self._parent.get_ylim()

            set_lim = self.set_ylim

        order = lims[0] < lims[1]

        lims = self._functions[0](np.array(lims))

        neworder = lims[0] < lims[1]

        if neworder != order:

                                                                        

            lims = lims[::-1]

        set_lim(lims)



    def set_aspect(self, *args, **kwargs):

        

        _api.warn_external("Secondary Axes can't set the aspect ratio")



    def set_color(self, color):

        

        axis = self._axis_map[self._orientation]

        axis.set_tick_params(colors=color)

        for spine in self.spines.values():

            if spine.axis is axis:

                spine.set_color(color)

        axis.label.set_color(color)





_secax_docstring = '''
Warnings
--------
This method is experimental as of 3.1, and the API may change.

Parameters
----------
location : {'top', 'bottom', 'left', 'right'} or float
    The position to put the secondary axis.  Strings can be 'top' or
    'bottom' for orientation='x' and 'right' or 'left' for
    orientation='y'. A float indicates the relative position on the
    parent Axes to put the new Axes, 0.0 being the bottom (or left)
    and 1.0 being the top (or right).

functions : 2-tuple of func, or Transform with an inverse

    If a 2-tuple of functions, the user specifies the transform
    function and its inverse.  i.e.
    ``functions=(lambda x: 2 / x, lambda x: 2 / x)`` would be an
    reciprocal transform with a factor of 2. Both functions must accept
    numpy arrays as input.

    The user can also directly supply a subclass of
    `.transforms.Transform` so long as it has an inverse.

    See :doc:`/gallery/subplots_axes_and_figures/secondary_axis`
    for examples of making these conversions.

transform : `.Transform`, optional
    If specified, *location* will be
    placed relative to this transform (in the direction of the axis)
    rather than the parent's axis. i.e. a secondary x-axis will
    use the provided y transform and the x transform of the parent.

    .. versionadded:: 3.9

Returns
-------
ax : axes._secondary_axes.SecondaryAxis

Other Parameters
----------------
**kwargs : `~matplotlib.axes.Axes` properties.
    Other miscellaneous Axes parameters.
'''

_docstring.interpd.register(_secax_docstring=_secax_docstring)

