import numpy as np



from matplotlib import _docstring

from matplotlib.contour import ContourSet

from matplotlib.tri._triangulation import Triangulation





@_docstring.interpd

class TriContourSet(ContourSet):

    

    def __init__(self, ax, *args, **kwargs):

        

        super().__init__(ax, *args, **kwargs)



    def _process_args(self, *args, **kwargs):

        

        if isinstance(args[0], TriContourSet):

            C = args[0]._contour_generator

            if self.levels is None:

                self.levels = args[0].levels

            self.zmin = args[0].zmin

            self.zmax = args[0].zmax

            self._mins = args[0]._mins

            self._maxs = args[0]._maxs

        else:

            from matplotlib import _tri

            tri, z = self._contour_args(args, kwargs)

            C = _tri.TriContourGenerator(tri.get_cpp_triangulation(), z)

            self._mins = [tri.x.min(), tri.y.min()]

            self._maxs = [tri.x.max(), tri.y.max()]



        self._contour_generator = C

        return kwargs



    def _contour_args(self, args, kwargs):

        tri, args, kwargs = Triangulation.get_from_args_and_kwargs(*args,

                                                                   **kwargs)

        z, *args = args

        z = np.ma.asarray(z)

        if z.shape != tri.x.shape:

            raise ValueError('z array must have same length as triangulation x'

                             ' and y arrays')



                                                                              

                               

        z_check = z[np.unique(tri.get_masked_triangles())]

        if np.ma.is_masked(z_check):

            raise ValueError('z must not contain masked points within the '

                             'triangulation')

        if not np.isfinite(z_check).all():

            raise ValueError('z array must not contain non-finite values '

                             'within the triangulation')



        z = np.ma.masked_invalid(z, copy=False)

        self.zmax = float(z_check.max())

        self.zmin = float(z_check.min())

        if self.logscale and self.zmin <= 0:

            func = 'contourf' if self.filled else 'contour'

            raise ValueError(f'Cannot {func} log of negative values.')

        self._process_contour_level_args(args, z.dtype)

        return (tri, z)





_docstring.interpd.register(_tricontour_doc="""
Draw contour %%(type)s on an unstructured triangular grid.

Call signatures::

    %%(func)s(triangulation, z, [levels], ...)
    %%(func)s(x, y, z, [levels], *, [triangles=triangles], [mask=mask], ...)

The triangular grid can be specified either by passing a `.Triangulation`
object as the first parameter, or by passing the points *x*, *y* and
optionally the *triangles* and a *mask*. See `.Triangulation` for an
explanation of these parameters. If neither of *triangulation* or
*triangles* are given, the triangulation is calculated on the fly.

It is possible to pass *triangles* positionally, i.e.
``%%(func)s(x, y, triangles, z, ...)``. However, this is discouraged. For more
clarity, pass *triangles* via keyword argument.

Parameters
----------
triangulation : `.Triangulation`, optional
    An already created triangular grid.

x, y, triangles, mask
    Parameters defining the triangular grid. See `.Triangulation`.
    This is mutually exclusive with specifying *triangulation*.

z : array-like
    The height values over which the contour is drawn.  Color-mapping is
    controlled by *cmap*, *norm*, *vmin*, and *vmax*.

    .. note::
        All values in *z* must be finite. Hence, nan and inf values must
        either be removed or `~.Triangulation.set_mask` be used.

levels : int or array-like, optional
    Determines the number and positions of the contour lines / regions.

    If an int *n*, use `~matplotlib.ticker.MaxNLocator`, which tries to
    automatically choose no more than *n+1* "nice" contour levels between
    between minimum and maximum numeric values of *Z*.

    If array-like, draw contour lines at the specified levels.  The values must
    be in increasing order.

Returns
-------
`~matplotlib.tri.TriContourSet`

Other Parameters
----------------
colors : :mpltype:`color` or list of :mpltype:`color`, optional
    The colors of the levels, i.e., the contour %%(type)s.

    The sequence is cycled for the levels in ascending order. If the sequence
    is shorter than the number of levels, it is repeated.

    As a shortcut, single color strings may be used in place of one-element
    lists, i.e. ``'red'`` instead of ``['red']`` to color all levels with the
    same color. This shortcut does only work for color strings, not for other
    ways of specifying colors.

    By default (value *None*), the colormap specified by *cmap* will be used.

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

origin : {*None*, 'upper', 'lower', 'image'}, default: None
    Determines the orientation and exact position of *z* by specifying the
    position of ``z[0, 0]``.  This is only relevant, if *X*, *Y* are not given.

    - *None*: ``z[0, 0]`` is at X=0, Y=0 in the lower left corner.
    - 'lower': ``z[0, 0]`` is at X=0.5, Y=0.5 in the lower left corner.
    - 'upper': ``z[0, 0]`` is at X=N+0.5, Y=0.5 in the upper left corner.
    - 'image': Use the value from :rc:`image.origin`.

extent : (x0, x1, y0, y1), optional
    If *origin* is not *None*, then *extent* is interpreted as in `.imshow`: it
    gives the outer pixel boundaries. In this case, the position of z[0, 0] is
    the center of the pixel, not a corner. If *origin* is *None*, then
    (*x0*, *y0*) is the position of z[0, 0], and (*x1*, *y1*) is the position
    of z[-1, -1].

    This argument is ignored if *X* and *Y* are specified in the call to
    contour.

locator : ticker.Locator subclass, optional
    The locator is used to determine the contour levels if they are not given
    explicitly via *levels*.
    Defaults to `~.ticker.MaxNLocator`.

extend : {'neither', 'both', 'min', 'max'}, default: 'neither'
    Determines the ``%%(func)s``-coloring of values that are outside the
    *levels* range.

    If 'neither', values outside the *levels* range are not colored.  If 'min',
    'max' or 'both', color the values below, above or below and above the
    *levels* range.

    Values below ``min(levels)`` and above ``max(levels)`` are mapped to the
    under/over values of the `.Colormap`. Note that most colormaps do not have
    dedicated colors for these by default, so that the over and under values
    are the edge values of the colormap.  You may want to set these values
    explicitly using `.Colormap.set_under` and `.Colormap.set_over`.

    .. note::

        An existing `.TriContourSet` does not get notified if properties of its
        colormap are changed. Therefore, an explicit call to
        `.ContourSet.changed()` is needed after modifying the colormap. The
        explicit call can be left out, if a colorbar is assigned to the
        `.TriContourSet` because it internally calls `.ContourSet.changed()`.

xunits, yunits : registered units, optional
    Override axis units by specifying an instance of a
    :class:`matplotlib.units.ConversionInterface`.

antialiased : bool, optional
    Enable antialiasing, overriding the defaults.  For
    filled contours, the default is *True*.  For line contours,
    it is taken from :rc:`lines.antialiased`.""" % _docstring.interpd.params)





@_docstring.Substitution(func='tricontour', type='lines')

@_docstring.interpd

def tricontour(ax, *args, **kwargs):

    

    kwargs['filled'] = False

    return TriContourSet(ax, *args, **kwargs)





@_docstring.Substitution(func='tricontourf', type='regions')

@_docstring.interpd

def tricontourf(ax, *args, **kwargs):

    

    kwargs['filled'] = True

    return TriContourSet(ax, *args, **kwargs)

