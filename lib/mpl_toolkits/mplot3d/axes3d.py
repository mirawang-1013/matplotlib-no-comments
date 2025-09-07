



from collections import defaultdict

import itertools

import math

import textwrap

import warnings



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook, _docstring, _preprocess_data

import matplotlib.artist as martist

import matplotlib.collections as mcoll

import matplotlib.colors as mcolors

import matplotlib.image as mimage

import matplotlib.lines as mlines

import matplotlib.patches as mpatches

import matplotlib.container as mcontainer

import matplotlib.transforms as mtransforms

from matplotlib.axes import Axes

from matplotlib.axes._base import _axis_method_wrapper, _process_plot_format

from matplotlib.transforms import Bbox

from matplotlib.tri._triangulation import Triangulation



from . import art3d

from . import proj3d

from . import axis3d





@_docstring.interpd

@_api.define_aliases({

    "xlim": ["xlim3d"], "ylim": ["ylim3d"], "zlim": ["zlim3d"]})

class Axes3D(Axes):

    

    name = '3d'



    _axis_names = ("x", "y", "z")

    Axes._shared_axes["z"] = cbook.Grouper()

    Axes._shared_axes["view"] = cbook.Grouper()



    def __init__(

        self, fig, rect=None, *args,

        elev=30, azim=-60, roll=0, shareview=None, sharez=None,

        proj_type='persp', focal_length=None,

        box_aspect=None,

        computed_zorder=True,

        **kwargs,

    ):

        



        if rect is None:

            rect = [0.0, 0.0, 1.0, 1.0]



        self.initial_azim = azim

        self.initial_elev = elev

        self.initial_roll = roll

        self.set_proj_type(proj_type, focal_length)

        self.computed_zorder = computed_zorder



        self.xy_viewLim = Bbox.unit()

        self.zz_viewLim = Bbox.unit()

        xymargin = 0.05 * 10/11                           

        self.xy_dataLim = Bbox([[xymargin, xymargin],

                                [1 - xymargin, 1 - xymargin]])

                                                                           

        self.zz_dataLim = Bbox.unit()



                                                           

                                                                   

        self.view_init(self.initial_elev, self.initial_azim, self.initial_roll)



        self._sharez = sharez

        if sharez is not None:

            self._shared_axes["z"].join(self, sharez)

            self._adjustable = 'datalim'



        self._shareview = shareview

        if shareview is not None:

            self._shared_axes["view"].join(self, shareview)



        if kwargs.pop('auto_add_to_figure', False):

            raise AttributeError(

                'auto_add_to_figure is no longer supported for Axes3D. '

                'Use fig.add_axes(ax) instead.'

            )



        super().__init__(

            fig, rect, frameon=True, box_aspect=box_aspect, *args, **kwargs

        )

                                               

        super().set_axis_off()

                                                

        self.set_axis_on()

        self.M = None

        self.invM = None



        self._view_margin = 1/48                                 

        self.autoscale_view()



                                                                

        self.fmt_zdata = None



        self.mouse_init()

        fig = self.get_figure(root=True)

        fig.canvas.callbacks._connect_picklable(

            'motion_notify_event', self._on_move)

        fig.canvas.callbacks._connect_picklable(

            'button_press_event', self._button_press)

        fig.canvas.callbacks._connect_picklable(

            'button_release_event', self._button_release)

        self.set_top_view()



        self.patch.set_linewidth(0)

                                                    

        pseudo_bbox = self.transLimits.inverted().transform([(0, 0), (1, 1)])

        self._pseudo_w, self._pseudo_h = pseudo_bbox[1] - pseudo_bbox[0]



                                                                             

                                       

        self.spines[:].set_visible(False)



    def set_axis_off(self):

        self._axis3don = False

        self.stale = True



    def set_axis_on(self):

        self._axis3don = True

        self.stale = True



    def convert_zunits(self, z):

        

        return self.zaxis.convert_units(z)



    def set_top_view(self):

                                                                       

                                                                  

        xdwl = 0.95 / self._dist

        xdw = 0.9 / self._dist

        ydwl = 0.95 / self._dist

        ydw = 0.9 / self._dist

                               

        self.viewLim.intervalx = (-xdwl, xdw)

        self.viewLim.intervaly = (-ydwl, ydw)

        self.stale = True



    def _init_axis(self):

        

        self.xaxis = axis3d.XAxis(self)

        self.yaxis = axis3d.YAxis(self)

        self.zaxis = axis3d.ZAxis(self)



    def get_zaxis(self):

        

        return self.zaxis



    get_zgridlines = _axis_method_wrapper("zaxis", "get_gridlines")

    get_zticklines = _axis_method_wrapper("zaxis", "get_ticklines")



    def _transformed_cube(self, vals):

        

        minx, maxx, miny, maxy, minz, maxz = vals

        xyzs = [(minx, miny, minz),

                (maxx, miny, minz),

                (maxx, maxy, minz),

                (minx, maxy, minz),

                (minx, miny, maxz),

                (maxx, miny, maxz),

                (maxx, maxy, maxz),

                (minx, maxy, maxz)]

        return proj3d._proj_points(xyzs, self.M)



    def set_aspect(self, aspect, adjustable=None, anchor=None, share=False):

        

        _api.check_in_list(('auto', 'equal', 'equalxy', 'equalyz', 'equalxz'),

                           aspect=aspect)

        super().set_aspect(

            aspect='auto', adjustable=adjustable, anchor=anchor, share=share)

        self._aspect = aspect



        if aspect in ('equal', 'equalxy', 'equalxz', 'equalyz'):

            ax_indices = self._equal_aspect_axis_indices(aspect)



            view_intervals = np.array([self.xaxis.get_view_interval(),

                                       self.yaxis.get_view_interval(),

                                       self.zaxis.get_view_interval()])

            ptp = np.ptp(view_intervals, axis=1)

            if self._adjustable == 'datalim':

                mean = np.mean(view_intervals, axis=1)

                scale = max(ptp[ax_indices] / self._box_aspect[ax_indices])

                deltas = scale * self._box_aspect



                for i, set_lim in enumerate((self.set_xlim3d,

                                             self.set_ylim3d,

                                             self.set_zlim3d)):

                    if i in ax_indices:

                        set_lim(mean[i] - deltas[i]/2., mean[i] + deltas[i]/2.,

                                auto=True, view_margin=None)

            else:         

                                                                            

                                                                   

                                                        

                box_aspect = np.array(self._box_aspect)

                box_aspect[ax_indices] = ptp[ax_indices]

                remaining_ax_indices = {0, 1, 2}.difference(ax_indices)

                if remaining_ax_indices:

                    remaining = remaining_ax_indices.pop()

                    old_diag = np.linalg.norm(self._box_aspect[ax_indices])

                    new_diag = np.linalg.norm(box_aspect[ax_indices])

                    box_aspect[remaining] *= new_diag / old_diag

                self.set_box_aspect(box_aspect)



    def _equal_aspect_axis_indices(self, aspect):

        

        ax_indices = []                    

        if aspect == 'equal':

            ax_indices = [0, 1, 2]

        elif aspect == 'equalxy':

            ax_indices = [0, 1]

        elif aspect == 'equalxz':

            ax_indices = [0, 2]

        elif aspect == 'equalyz':

            ax_indices = [1, 2]

        return ax_indices



    def set_box_aspect(self, aspect, *, zoom=1):

        

        if zoom <= 0:

            raise ValueError(f'Argument zoom = {zoom} must be > 0')



        if aspect is None:

            aspect = np.asarray((4, 4, 3), dtype=float)

        else:

            aspect = np.asarray(aspect, dtype=float)

            _api.check_shape((3,), aspect=aspect)

                                                                               

                                                                        

                                                                               

                                

        aspect *= 1.8294640721620434 * 25/24 * zoom / np.linalg.norm(aspect)



        self._box_aspect = self._roll_to_vertical(aspect, reverse=True)

        self.stale = True



    def apply_aspect(self, position=None):

        if position is None:

            position = self.get_position(original=True)



                                                                            

                                                                              

                                                       

        trans = self.get_figure().transSubfigure

        bb = mtransforms.Bbox.unit().transformed(trans)

                                                               

        fig_aspect = bb.height / bb.width



        box_aspect = 1

        pb = position.frozen()

        pb1 = pb.shrunk_to_aspect(box_aspect, pb, fig_aspect)

        self._set_position(pb1.anchored(self.get_anchor(), pb), 'active')



    @martist.allow_rasterization

    def draw(self, renderer):

        if not self.get_visible():

            return

        self._unstale_viewLim()



                                   

        self.patch.draw(renderer)

        self._frameon = False



                               

                                                             

                                                                  

                                                                     

                     

        locator = self.get_axes_locator()

        self.apply_aspect(locator(self, renderer) if locator else None)



                                                   

        self.M = self.get_proj()

        self.invM = np.linalg.inv(self.M)



        collections_and_patches = (

            artist for artist in self._children

            if isinstance(artist, (mcoll.Collection, mpatches.Patch))

            and artist.get_visible())

        if self.computed_zorder:

                                                                        

                                                             

            zorder_offset = max(axis.get_zorder()

                                for axis in self._axis_map.values()) + 1

            collection_zorder = patch_zorder = zorder_offset



            for artist in sorted(collections_and_patches,

                                 key=lambda artist: artist.do_3d_projection(),

                                 reverse=True):

                if isinstance(artist, mcoll.Collection):

                    artist.zorder = collection_zorder

                    collection_zorder += 1

                elif isinstance(artist, mpatches.Patch):

                    artist.zorder = patch_zorder

                    patch_zorder += 1

        else:

            for artist in collections_and_patches:

                artist.do_3d_projection()



        if self._axis3don:

                              

            for axis in self._axis_map.values():

                axis.draw_pane(renderer)

                            

            for axis in self._axis_map.values():

                axis.draw_grid(renderer)

                                                

            for axis in self._axis_map.values():

                axis.draw(renderer)



                   

        super().draw(renderer)



    def get_axis_position(self):

        tc = self._transformed_cube(self.get_w_lims())

        xhigh = tc[1][2] > tc[2][2]

        yhigh = tc[3][2] > tc[2][2]

        zhigh = tc[0][2] > tc[2][2]

        return xhigh, yhigh, zhigh



    def update_datalim(self, xys, **kwargs):

        

        pass



    get_autoscalez_on = _axis_method_wrapper("zaxis", "_get_autoscale_on")

    set_autoscalez_on = _axis_method_wrapper("zaxis", "_set_autoscale_on")



    def get_zmargin(self):

        

        return self._zmargin



    def set_zmargin(self, m):

        

        if m <= -0.5:

            raise ValueError("margin must be greater than -0.5")

        self._zmargin = m

        self._request_autoscale_view("z")

        self.stale = True



    def margins(self, *margins, x=None, y=None, z=None, tight=True):

        

        if margins and (x is not None or y is not None or z is not None):

            raise TypeError('Cannot pass both positional and keyword '

                            'arguments for x, y, and/or z.')

        elif len(margins) == 1:

            x = y = z = margins[0]

        elif len(margins) == 3:

            x, y, z = margins

        elif margins:

            raise TypeError('Must pass a single positional argument for all '

                            'margins, or one for each margin (x, y, z).')



        if x is None and y is None and z is None:

            if tight is not True:

                _api.warn_external(f'ignoring tight={tight!r} in get mode')

            return self._xmargin, self._ymargin, self._zmargin



        if x is not None:

            self.set_xmargin(x)

        if y is not None:

            self.set_ymargin(y)

        if z is not None:

            self.set_zmargin(z)



        self.autoscale_view(

            tight=tight, scalex=(x is not None), scaley=(y is not None),

            scalez=(z is not None)

        )



    def autoscale(self, enable=True, axis='both', tight=None):

        

        if enable is None:

            scalex = True

            scaley = True

            scalez = True

        else:

            if axis in ['x', 'both']:

                self.set_autoscalex_on(enable)

                scalex = self.get_autoscalex_on()

            else:

                scalex = False

            if axis in ['y', 'both']:

                self.set_autoscaley_on(enable)

                scaley = self.get_autoscaley_on()

            else:

                scaley = False

            if axis in ['z', 'both']:

                self.set_autoscalez_on(enable)

                scalez = self.get_autoscalez_on()

            else:

                scalez = False

        if scalex:

            self._request_autoscale_view("x", tight=tight)

        if scaley:

            self._request_autoscale_view("y", tight=tight)

        if scalez:

            self._request_autoscale_view("z", tight=tight)



    def auto_scale_xyz(self, X, Y, Z=None, had_data=None):

                                                                            

                                                          

        if np.shape(X) == np.shape(Y):

            self.xy_dataLim.update_from_data_xy(

                np.column_stack([np.ravel(X), np.ravel(Y)]), not had_data)

        else:

            self.xy_dataLim.update_from_data_x(X, not had_data)

            self.xy_dataLim.update_from_data_y(Y, not had_data)

        if Z is not None:

            self.zz_dataLim.update_from_data_x(Z, not had_data)

                                                             

        self.autoscale_view()



    def autoscale_view(self, tight=None,

                       scalex=True, scaley=True, scalez=True):

        

                                                                 

                                                                     

        if tight is None:

            _tight = self._tight

            if not _tight:

                                                         

                for artist in self._children:

                    if isinstance(artist, mimage.AxesImage):

                        _tight = True

                    elif isinstance(artist, (mlines.Line2D, mpatches.Patch)):

                        _tight = False

                        break

        else:

            _tight = self._tight = bool(tight)



        if scalex and self.get_autoscalex_on():

            x0, x1 = self.xy_dataLim.intervalx

            xlocator = self.xaxis.get_major_locator()

            x0, x1 = xlocator.nonsingular(x0, x1)

            if self._xmargin > 0:

                delta = (x1 - x0) * self._xmargin

                x0 -= delta

                x1 += delta

            if not _tight:

                x0, x1 = xlocator.view_limits(x0, x1)

            self.set_xbound(x0, x1, self._view_margin)



        if scaley and self.get_autoscaley_on():

            y0, y1 = self.xy_dataLim.intervaly

            ylocator = self.yaxis.get_major_locator()

            y0, y1 = ylocator.nonsingular(y0, y1)

            if self._ymargin > 0:

                delta = (y1 - y0) * self._ymargin

                y0 -= delta

                y1 += delta

            if not _tight:

                y0, y1 = ylocator.view_limits(y0, y1)

            self.set_ybound(y0, y1, self._view_margin)



        if scalez and self.get_autoscalez_on():

            z0, z1 = self.zz_dataLim.intervalx

            zlocator = self.zaxis.get_major_locator()

            z0, z1 = zlocator.nonsingular(z0, z1)

            if self._zmargin > 0:

                delta = (z1 - z0) * self._zmargin

                z0 -= delta

                z1 += delta

            if not _tight:

                z0, z1 = zlocator.view_limits(z0, z1)

            self.set_zbound(z0, z1, self._view_margin)



    def get_w_lims(self):

        

        minx, maxx = self.get_xlim3d()

        miny, maxy = self.get_ylim3d()

        minz, maxz = self.get_zlim3d()

        return minx, maxx, miny, maxy, minz, maxz



    def _set_bound3d(self, get_bound, set_lim, axis_inverted,

                     lower=None, upper=None, view_margin=None):

        

        if upper is None and np.iterable(lower):

            lower, upper = lower



        old_lower, old_upper = get_bound()

        if lower is None:

            lower = old_lower

        if upper is None:

            upper = old_upper



        set_lim(sorted((lower, upper), reverse=bool(axis_inverted())),

                auto=None, view_margin=view_margin)



    def set_xbound(self, lower=None, upper=None, view_margin=None):

        

        self._set_bound3d(self.get_xbound, self.set_xlim, self.xaxis_inverted,

                          lower, upper, view_margin)



    def set_ybound(self, lower=None, upper=None, view_margin=None):

        

        self._set_bound3d(self.get_ybound, self.set_ylim, self.yaxis_inverted,

                          lower, upper, view_margin)



    def set_zbound(self, lower=None, upper=None, view_margin=None):

        

        self._set_bound3d(self.get_zbound, self.set_zlim, self.zaxis_inverted,

                          lower, upper, view_margin)



    def _set_lim3d(self, axis, lower=None, upper=None, *, emit=True,

                   auto=False, view_margin=None, axmin=None, axmax=None):

        

        if upper is None:

            if np.iterable(lower):

                lower, upper = lower

            elif axmax is None:

                upper = axis.get_view_interval()[1]

        if lower is None and axmin is None:

            lower = axis.get_view_interval()[0]

        if axmin is not None:

            if lower is not None:

                raise TypeError("Cannot pass both 'lower' and 'min'")

            lower = axmin

        if axmax is not None:

            if upper is not None:

                raise TypeError("Cannot pass both 'upper' and 'max'")

            upper = axmax

        if np.isinf(lower) or np.isinf(upper):

            raise ValueError(f"Axis limits {lower}, {upper} cannot be infinite")

        if view_margin is None:

            if mpl.rcParams['axes3d.automargin']:

                view_margin = self._view_margin

            else:

                view_margin = 0

        delta = (upper - lower) * view_margin

        lower -= delta

        upper += delta

        return axis._set_lim(lower, upper, emit=emit, auto=auto)



    def set_xlim(self, left=None, right=None, *, emit=True, auto=False,

                 view_margin=None, xmin=None, xmax=None):

        

        return self._set_lim3d(self.xaxis, left, right, emit=emit, auto=auto,

                               view_margin=view_margin, axmin=xmin, axmax=xmax)



    def set_ylim(self, bottom=None, top=None, *, emit=True, auto=False,

                 view_margin=None, ymin=None, ymax=None):

        

        return self._set_lim3d(self.yaxis, bottom, top, emit=emit, auto=auto,

                               view_margin=view_margin, axmin=ymin, axmax=ymax)



    def set_zlim(self, bottom=None, top=None, *, emit=True, auto=False,

                 view_margin=None, zmin=None, zmax=None):

        

        return self._set_lim3d(self.zaxis, bottom, top, emit=emit, auto=auto,

                               view_margin=view_margin, axmin=zmin, axmax=zmax)



    set_xlim3d = set_xlim

    set_ylim3d = set_ylim

    set_zlim3d = set_zlim



    def get_xlim(self):

                             

        return tuple(self.xy_viewLim.intervalx)



    def get_ylim(self):

                             

        return tuple(self.xy_viewLim.intervaly)



    def get_zlim(self):

        

        return tuple(self.zz_viewLim.intervalx)



    get_zscale = _axis_method_wrapper("zaxis", "get_scale")



                                                               

    set_xscale = _axis_method_wrapper("xaxis", "_set_axes_scale")

    set_yscale = _axis_method_wrapper("yaxis", "_set_axes_scale")

    set_zscale = _axis_method_wrapper("zaxis", "_set_axes_scale")

    set_xscale.__doc__, set_yscale.__doc__, set_zscale.__doc__ = map(

        """
        Set the {}-axis scale.

        Parameters
        ----------
        value : {{"linear"}}
            The axis scale type to apply.  3D Axes currently only support
            linear scales; other scales yield nonsensical results.

        **kwargs
            Keyword arguments are nominally forwarded to the scale class, but
            none of them is applicable for linear scales.
        """.format,

        ["x", "y", "z"])



    get_zticks = _axis_method_wrapper("zaxis", "get_ticklocs")

    set_zticks = _axis_method_wrapper("zaxis", "set_ticks")

    get_zmajorticklabels = _axis_method_wrapper("zaxis", "get_majorticklabels")

    get_zminorticklabels = _axis_method_wrapper("zaxis", "get_minorticklabels")

    get_zticklabels = _axis_method_wrapper("zaxis", "get_ticklabels")

    set_zticklabels = _axis_method_wrapper(

        "zaxis", "set_ticklabels",

        doc_sub={"Axis.set_ticks": "Axes3D.set_zticks"})



    zaxis_date = _axis_method_wrapper("zaxis", "axis_date")

    if zaxis_date.__doc__:

        zaxis_date.__doc__ += textwrap.dedent("""

        Notes
        -----
        This function is merely provided for completeness, but 3D Axes do not
        support dates for ticks, and so this may not work as expected.
        """)



    def clabel(self, *args, **kwargs):

        

        return None



    def view_init(self, elev=None, azim=None, roll=None, vertical_axis="z",

                  share=False):

        



        self._dist = 10                                                      



        if elev is None:

            elev = self.initial_elev

        if azim is None:

            azim = self.initial_azim

        if roll is None:

            roll = self.initial_roll

        vertical_axis = _api.check_getitem(

            {name: idx for idx, name in enumerate(self._axis_names)},

            vertical_axis=vertical_axis,

        )



        if share:

            axes = {sibling for sibling

                    in self._shared_axes['view'].get_siblings(self)}

        else:

            axes = [self]



        for ax in axes:

            ax.elev = elev

            ax.azim = azim

            ax.roll = roll

            ax._vertical_axis = vertical_axis



    def set_proj_type(self, proj_type, focal_length=None):

        

        _api.check_in_list(['persp', 'ortho'], proj_type=proj_type)

        if proj_type == 'persp':

            if focal_length is None:

                focal_length = 1

            elif focal_length <= 0:

                raise ValueError(f"focal_length = {focal_length} must be "

                                 "greater than 0")

            self._focal_length = focal_length

        else:            

            if focal_length not in (None, np.inf):

                raise ValueError(f"focal_length = {focal_length} must be "

                                 f"None for proj_type = {proj_type}")

            self._focal_length = np.inf



    def _roll_to_vertical(

        self, arr: "np.typing.ArrayLike", reverse: bool = False

    ) -> np.ndarray:

        

        if reverse:

            return np.roll(arr, (self._vertical_axis - 2) * -1)

        else:

            return np.roll(arr, (self._vertical_axis - 2))



    def get_proj(self):

        



                                                              

        box_aspect = self._roll_to_vertical(self._box_aspect)

        worldM = proj3d.world_transformation(

            *self.get_xlim3d(),

            *self.get_ylim3d(),

            *self.get_zlim3d(),

            pb_aspect=box_aspect,

        )



                                                        

        R = 0.5 * box_aspect



                                               

                                              

                                                                      

                                                                               

                                                                             

        elev_rad = np.deg2rad(self.elev)

        azim_rad = np.deg2rad(self.azim)

        p0 = np.cos(elev_rad) * np.cos(azim_rad)

        p1 = np.cos(elev_rad) * np.sin(azim_rad)

        p2 = np.sin(elev_rad)



                                                                      

                                                                   

        ps = self._roll_to_vertical([p0, p1, p2])



                                                                       

                                                                

        eye = R + self._dist * ps



                                                         

        u, v, w = self._calc_view_axes(eye)

        self._view_u = u                                              

        self._view_v = v                                            

        self._view_w = w                                



                                                                  

        if self._focal_length == np.inf:

                                     

            viewM = proj3d._view_transformation_uvw(u, v, w, eye)

            projM = proj3d._ortho_transformation(-self._dist, self._dist)

        else:

                                    

                                                                               

            eye_focal = R + self._dist * ps * self._focal_length

            viewM = proj3d._view_transformation_uvw(u, v, w, eye_focal)

            projM = proj3d._persp_transformation(-self._dist,

                                                 self._dist,

                                                 self._focal_length)



                                                                             

        M0 = np.dot(viewM, worldM)

        M = np.dot(projM, M0)

        return M



    def mouse_init(self, rotate_btn=1, pan_btn=2, zoom_btn=3):

        

        self.button_pressed = None

                                                           

                                                          

                                                   

        self._rotate_btn = np.atleast_1d(rotate_btn).tolist()

        self._pan_btn = np.atleast_1d(pan_btn).tolist()

        self._zoom_btn = np.atleast_1d(zoom_btn).tolist()



    def disable_mouse_rotation(self):

        

        self.mouse_init(rotate_btn=[], pan_btn=[], zoom_btn=[])



    def can_zoom(self):

                              

        return True



    def can_pan(self):

                              

        return True



    def sharez(self, other):

        

        _api.check_isinstance(Axes3D, other=other)

        if self._sharez is not None and other is not self._sharez:

            raise ValueError("z-axis is already shared")

        self._shared_axes["z"].join(self, other)

        self._sharez = other

        self.zaxis.major = other.zaxis.major                            

        self.zaxis.minor = other.zaxis.minor                          

        z0, z1 = other.get_zlim()

        self.set_zlim(z0, z1, emit=False, auto=other.get_autoscalez_on())

        self.zaxis._scale = other.zaxis._scale



    def shareview(self, other):

        

        _api.check_isinstance(Axes3D, other=other)

        if self._shareview is not None and other is not self._shareview:

            raise ValueError("view angles are already shared")

        self._shared_axes["view"].join(self, other)

        self._shareview = other

        vertical_axis = self._axis_names[other._vertical_axis]

        self.view_init(elev=other.elev, azim=other.azim, roll=other.roll,

                       vertical_axis=vertical_axis, share=True)



    def clear(self):

                              

        super().clear()

        if self._focal_length == np.inf:

            self._zmargin = mpl.rcParams['axes.zmargin']

        else:

            self._zmargin = 0.



        xymargin = 0.05 * 10/11                           

        self.xy_dataLim = Bbox([[xymargin, xymargin],

                                [1 - xymargin, 1 - xymargin]])

                                                                           

        self.zz_dataLim = Bbox.unit()

        self._view_margin = 1/48                                 

        self.autoscale_view()



        self.grid(mpl.rcParams['axes3d.grid'])



    def _button_press(self, event):

        if event.inaxes == self:

            self.button_pressed = event.button

            self._sx, self._sy = event.xdata, event.ydata

            toolbar = self.get_figure(root=True).canvas.toolbar

            if toolbar and toolbar._nav_stack() is None:

                toolbar.push_current()

            if toolbar:

                toolbar.set_message(toolbar._mouse_event_to_message(event))



    def _button_release(self, event):

        self.button_pressed = None

        toolbar = self.get_figure(root=True).canvas.toolbar

                                                                       

                                                                              

        if toolbar and self.get_navigate_mode() is None:

            toolbar.push_current()

        if toolbar:

            toolbar.set_message(toolbar._mouse_event_to_message(event))



    def _get_view(self):

                             

        return {

            "xlim": self.get_xlim(), "autoscalex_on": self.get_autoscalex_on(),

            "ylim": self.get_ylim(), "autoscaley_on": self.get_autoscaley_on(),

            "zlim": self.get_zlim(), "autoscalez_on": self.get_autoscalez_on(),

        }, (self.elev, self.azim, self.roll)



    def _set_view(self, view):

                             

        props, (elev, azim, roll) = view

        self.set(**props)

        self.elev = elev

        self.azim = azim

        self.roll = roll



    def format_zdata(self, z):

        

        try:

            return self.fmt_zdata(z)

        except (AttributeError, TypeError):

            func = self.zaxis.get_major_formatter().format_data_short

            val = func(z)

            return val



    def format_coord(self, xv, yv, renderer=None):

        

        coords = ''



        if self.button_pressed in self._rotate_btn:

                                                         

            coords = self._rotation_coords()



        elif self.M is not None:

            coords = self._location_coords(xv, yv, renderer)



        return coords



    def _rotation_coords(self):

        

        norm_elev = art3d._norm_angle(self.elev)

        norm_azim = art3d._norm_angle(self.azim)

        norm_roll = art3d._norm_angle(self.roll)

        coords = (f"elevation={norm_elev:.0f}\N{DEGREE SIGN}, "

                  f"azimuth={norm_azim:.0f}\N{DEGREE SIGN}, "

                  f"roll={norm_roll:.0f}\N{DEGREE SIGN}"

                  ).replace("-", "\N{MINUS SIGN}")

        return coords



    def _location_coords(self, xv, yv, renderer):

        

        p1, pane_idx = self._calc_coord(xv, yv, renderer)

        xs = self.format_xdata(p1[0])

        ys = self.format_ydata(p1[1])

        zs = self.format_zdata(p1[2])

        if pane_idx == 0:

            coords = f'x pane={xs}, y={ys}, z={zs}'

        elif pane_idx == 1:

            coords = f'x={xs}, y pane={ys}, z={zs}'

        elif pane_idx == 2:

            coords = f'x={xs}, y={ys}, z pane={zs}'

        return coords



    def _get_camera_loc(self):

        

        cx, cy, cz, dx, dy, dz = self._get_w_centers_ranges()

        c = np.array([cx, cy, cz])

        r = np.array([dx, dy, dz])



        if self._focal_length == np.inf:                           

            focal_length = 1e9                                           

        else:                          

            focal_length = self._focal_length

        eye = c + self._view_w * self._dist * r / self._box_aspect * focal_length

        return eye



    def _calc_coord(self, xv, yv, renderer=None):

        

        if self._focal_length == np.inf:                           

            zv = 1

        else:                          

            zv = -1 / self._focal_length



                                                         

        p1 = np.array(proj3d.inv_transform(xv, yv, zv, self.invM)).ravel()



                                                                       

        vec = self._get_camera_loc() - p1



                                                     

        pane_locs = []

        for axis in self._axis_map.values():

            xys, loc = axis.active_pane()

            pane_locs.append(loc)



                                                                             

        scales = np.zeros(3)

        for i in range(3):

            if vec[i] == 0:

                scales[i] = np.inf

            else:

                scales[i] = (p1[i] - pane_locs[i]) / vec[i]

        pane_idx = np.argmin(abs(scales))

        scale = scales[pane_idx]



                                                 

        p2 = p1 - scale*vec

        return p2, pane_idx



    def _arcball(self, x: float, y: float) -> np.ndarray:

        

        s = mpl.rcParams['axes3d.trackballsize'] / 2

        b = mpl.rcParams['axes3d.trackballborder'] / s

        x /= s

        y /= s

        r2 = x*x + y*y

        r = np.sqrt(r2)

        ra = 1 + b

        a = b * (1 + b/2)

        ri = 2/(ra + 1/ra)

        if r < ri:

            p = np.array([np.sqrt(1 - r2), x, y])

        elif r < ra:

            dr = ra - r

            p = np.array([a - np.sqrt((a + dr) * (a - dr)), x, y])

            p /= np.linalg.norm(p)

        else:

            p = np.array([0, x/r, y/r])

        return p



    def _on_move(self, event):

        



        if not self.button_pressed:

            return



        if self.get_navigate_mode() is not None:

                                                               

                              

            return



        if self.M is None:

            return



        x, y = event.xdata, event.ydata

                                             

        if x is None or event.inaxes != self:

            return



        dx, dy = x - self._sx, y - self._sy

        w = self._pseudo_w

        h = self._pseudo_h



                  

        if self.button_pressed in self._rotate_btn:

                                  

                                          

            if dx == 0 and dy == 0:

                return



            style = mpl.rcParams['axes3d.mouserotationstyle']

            if style == 'azel':

                roll = np.deg2rad(self.roll)

                delev = -(dy/h)*180*np.cos(roll) + (dx/w)*180*np.sin(roll)

                dazim = -(dy/h)*180*np.sin(roll) - (dx/w)*180*np.cos(roll)

                elev = self.elev + delev

                azim = self.azim + dazim

                roll = self.roll

            else:

                q = _Quaternion.from_cardan_angles(

                        *np.deg2rad((self.elev, self.azim, self.roll)))



                if style == 'trackball':

                    k = np.array([0, -dy/h, dx/w])

                    nk = np.linalg.norm(k)

                    th = nk / mpl.rcParams['axes3d.trackballsize']

                    dq = _Quaternion(np.cos(th), k*np.sin(th)/nk)

                else:                       

                    current_vec = self._arcball(self._sx/w, self._sy/h)

                    new_vec = self._arcball(x/w, y/h)

                    if style == 'sphere':

                        dq = _Quaternion.rotate_from_to(current_vec, new_vec)

                    else:             

                        dq = _Quaternion(0, new_vec) * _Quaternion(0, -current_vec)



                q = dq * q

                elev, azim, roll = np.rad2deg(q.as_cardan_angles())



                         

            vertical_axis = self._axis_names[self._vertical_axis]

            self.view_init(

                elev=elev,

                azim=azim,

                roll=roll,

                vertical_axis=vertical_axis,

                share=True,

            )

            self.stale = True



             

        elif self.button_pressed in self._pan_btn:

                                                        

            px, py = self.transData.transform([self._sx, self._sy])

            self.start_pan(px, py, 2)

                                                     

            self.drag_pan(2, None, event.x, event.y)

            self.end_pan()



              

        elif self.button_pressed in self._zoom_btn:

                                                

            scale = h/(h - dy)

            self._scale_axis_limits(scale, scale, scale)



                                                                

        self._sx, self._sy = x, y

                                                                

        self.get_figure(root=True).canvas.draw_idle()



    def drag_pan(self, button, key, x, y):

                             



                                                 

        p = self._pan_start

        (xdata, ydata), (xdata_start, ydata_start) = p.trans_inverse.transform(

            [(x, y), (p.x, p.y)])

        self._sx, self._sy = xdata, ydata

                                                                          

                                          

        self.start_pan(x, y, button)

        du, dv = xdata - xdata_start, ydata - ydata_start

        dw = 0

        if key == 'x':

            dv = 0

        elif key == 'y':

            du = 0

        if du == 0 and dv == 0:

            return



                                                               

        R = np.array([self._view_u, self._view_v, self._view_w])

        R = -R / self._box_aspect * self._dist

        duvw_projected = R.T @ np.array([du, dv, dw])



                                

        minx, maxx, miny, maxy, minz, maxz = self.get_w_lims()

        dx = (maxx - minx) * duvw_projected[0]

        dy = (maxy - miny) * duvw_projected[1]

        dz = (maxz - minz) * duvw_projected[2]



                                 

        self.set_xlim3d(minx + dx, maxx + dx, auto=None)

        self.set_ylim3d(miny + dy, maxy + dy, auto=None)

        self.set_zlim3d(minz + dz, maxz + dz, auto=None)



    def _calc_view_axes(self, eye):

        

        elev_rad = np.deg2rad(art3d._norm_angle(self.elev))

        roll_rad = np.deg2rad(art3d._norm_angle(self.roll))



                                                       

        R = 0.5 * self._roll_to_vertical(self._box_aspect)



                                                                

                                                                    

                             

        V = np.zeros(3)

        V[self._vertical_axis] = -1 if abs(elev_rad) > np.pi/2 else 1



        u, v, w = proj3d._view_axes(eye, R, V, roll_rad)

        return u, v, w



    def _set_view_from_bbox(self, bbox, direction='in',

                            mode=None, twinx=False, twiny=False):

        

        (start_x, start_y, stop_x, stop_y) = bbox

        if mode == 'x':

            start_y = self.bbox.min[1]

            stop_y = self.bbox.max[1]

        elif mode == 'y':

            start_x = self.bbox.min[0]

            stop_x = self.bbox.max[0]



                                     

        start_x, stop_x = np.clip(sorted([start_x, stop_x]),

                                  self.bbox.min[0], self.bbox.max[0])

        start_y, stop_y = np.clip(sorted([start_y, stop_y]),

                                  self.bbox.min[1], self.bbox.max[1])



                                                               

        zoom_center_x = (start_x + stop_x)/2

        zoom_center_y = (start_y + stop_y)/2



        ax_center_x = (self.bbox.max[0] + self.bbox.min[0])/2

        ax_center_y = (self.bbox.max[1] + self.bbox.min[1])/2



        self.start_pan(zoom_center_x, zoom_center_y, 2)

        self.drag_pan(2, None, ax_center_x, ax_center_y)

        self.end_pan()



                              

        dx = abs(start_x - stop_x)

        dy = abs(start_y - stop_y)

        scale_u = dx / (self.bbox.max[0] - self.bbox.min[0])

        scale_v = dy / (self.bbox.max[1] - self.bbox.min[1])



                                  

        scale = max(scale_u, scale_v)



                  

        if direction == 'out':

            scale = 1 / scale



        self._zoom_data_limits(scale, scale, scale)



    def _zoom_data_limits(self, scale_u, scale_v, scale_w):

        

        scale = np.array([scale_u, scale_v, scale_w])



                                                                

        if not np.allclose(scale, scale_u):

                                                                             

            R = np.array([self._view_u, self._view_v, self._view_w])

            S = scale * np.eye(3)

            scale = np.linalg.norm(R.T @ S, axis=1)



                                                                          

            if self._aspect in ('equal', 'equalxy', 'equalxz', 'equalyz'):

                ax_idxs = self._equal_aspect_axis_indices(self._aspect)

                min_ax_idxs = np.argmin(np.abs(scale[ax_idxs] - 1))

                scale[ax_idxs] = scale[ax_idxs][min_ax_idxs]



        self._scale_axis_limits(scale[0], scale[1], scale[2])



    def _scale_axis_limits(self, scale_x, scale_y, scale_z):

        

                                         

        cx, cy, cz, dx, dy, dz = self._get_w_centers_ranges()



                                    

        self.set_xlim3d(cx - dx*scale_x/2, cx + dx*scale_x/2, auto=None)

        self.set_ylim3d(cy - dy*scale_y/2, cy + dy*scale_y/2, auto=None)

        self.set_zlim3d(cz - dz*scale_z/2, cz + dz*scale_z/2, auto=None)



    def _get_w_centers_ranges(self):

        

                                         

        minx, maxx, miny, maxy, minz, maxz = self.get_w_lims()

        cx = (maxx + minx)/2

        cy = (maxy + miny)/2

        cz = (maxz + minz)/2



                                        

        dx = (maxx - minx)

        dy = (maxy - miny)

        dz = (maxz - minz)

        return cx, cy, cz, dx, dy, dz



    def set_zlabel(self, zlabel, fontdict=None, labelpad=None, **kwargs):

        

        if labelpad is not None:

            self.zaxis.labelpad = labelpad

        return self.zaxis.set_label_text(zlabel, fontdict, **kwargs)



    def get_zlabel(self):

        

        label = self.zaxis.label

        return label.get_text()



                                    



                                                         

                                                       

    get_frame_on = None

    set_frame_on = None



    def grid(self, visible=True, **kwargs):

        

                                               

        if len(kwargs):

            visible = True

        self._draw_grid = visible

        self.stale = True



    def tick_params(self, axis='both', **kwargs):

        

        _api.check_in_list(['x', 'y', 'z', 'both'], axis=axis)

        if axis in ['x', 'y', 'both']:

            super().tick_params(axis, **kwargs)

        if axis in ['z', 'both']:

            zkw = dict(kwargs)

            zkw.pop('top', None)

            zkw.pop('bottom', None)

            zkw.pop('labeltop', None)

            zkw.pop('labelbottom', None)

            self.zaxis.set_tick_params(**zkw)



                                                     



    def invert_zaxis(self):

        

        bottom, top = self.get_zlim()

        self.set_zlim(top, bottom, auto=None)



    set_zinverted = _axis_method_wrapper("zaxis", "set_inverted")

    get_zinverted = _axis_method_wrapper("zaxis", "get_inverted")

    zaxis_inverted = _axis_method_wrapper("zaxis", "get_inverted")

    if zaxis_inverted.__doc__:

        zaxis_inverted.__doc__ = ("[*Discouraged*] " + zaxis_inverted.__doc__ +

                                  textwrap.dedent("""

        .. admonition:: Discouraged

            The use of this method is discouraged.
            Use `.Axes3D.get_zinverted` instead.
        """))



    def get_zbound(self):

        

        lower, upper = self.get_zlim()

        if lower < upper:

            return lower, upper

        else:

            return upper, lower



    def text(self, x, y, z, s, zdir=None, *, axlim_clip=False, **kwargs):

        

        text = super().text(x, y, s, **kwargs)

        art3d.text_2d_to_3d(text, z, zdir, axlim_clip)

        return text



    text3D = text

    text2D = Axes.text



    def plot(self, xs, ys, *args, zdir='z', axlim_clip=False, **kwargs):

        

        had_data = self.has_data()



                                                                         

                                                                    

                                    

        if args and not isinstance(args[0], str):

            zs, *args = args

            if 'zs' in kwargs:

                raise TypeError("plot() for multiple values for argument 'zs'")

        else:

            zs = kwargs.pop('zs', 0)



        xs, ys, zs = cbook._broadcast_with_masks(xs, ys, zs)



        lines = super().plot(xs, ys, *args, **kwargs)

        for line in lines:

            art3d.line_2d_to_3d(line, zs=zs, zdir=zdir, axlim_clip=axlim_clip)



        xs, ys, zs = art3d.juggle_axes(xs, ys, zs, zdir)

        self.auto_scale_xyz(xs, ys, zs, had_data)

        return lines



    plot3D = plot



    def fill_between(self, x1, y1, z1, x2, y2, z2, *,

                     where=None, mode='auto', facecolors=None, shade=None,

                     axlim_clip=False, **kwargs):

        

        _api.check_in_list(['auto', 'quad', 'polygon'], mode=mode)



        had_data = self.has_data()

        x1, y1, z1, x2, y2, z2 = cbook._broadcast_with_masks(x1, y1, z1, x2, y2, z2)



        if facecolors is None:

            facecolors = [self._get_patches_for_fill.get_next_color()]

        facecolors = list(mcolors.to_rgba_array(facecolors))



        if where is None:

            where = True

        else:

            where = np.asarray(where, dtype=bool)

            if where.size != x1.size:

                raise ValueError(f"where size ({where.size}) does not match "

                                 f"size ({x1.size})")

        where = where & ~np.isnan(x1)                                                



        if mode == 'auto':

            if art3d._all_points_on_plane(np.concatenate((x1[where], x2[where])),

                                          np.concatenate((y1[where], y2[where])),

                                          np.concatenate((z1[where], z2[where])),

                                          atol=1e-12):

                mode = 'polygon'

            else:

                mode = 'quad'



        if shade is None:

            if mode == 'quad':

                shade = True

            else:

                shade = False



        polys = []

        for idx0, idx1 in cbook.contiguous_regions(where):

            x1i = x1[idx0:idx1]

            y1i = y1[idx0:idx1]

            z1i = z1[idx0:idx1]

            x2i = x2[idx0:idx1]

            y2i = y2[idx0:idx1]

            z2i = z2[idx0:idx1]



            if not len(x1i):

                continue



            if mode == 'quad':

                                                                                 

                n_polys_i = len(x1i) - 1

                polys_i = np.empty((n_polys_i, 4, 3))

                polys_i[:, 0, :] = np.column_stack((x1i[:-1], y1i[:-1], z1i[:-1]))

                polys_i[:, 1, :] = np.column_stack((x1i[1:], y1i[1:], z1i[1:]))

                polys_i[:, 2, :] = np.column_stack((x2i[1:], y2i[1:], z2i[1:]))

                polys_i[:, 3, :] = np.column_stack((x2i[:-1], y2i[:-1], z2i[:-1]))

                polys = polys + [*polys_i]

            elif mode == 'polygon':

                line1 = np.column_stack((x1i, y1i, z1i))

                line2 = np.column_stack((x2i[::-1], y2i[::-1], z2i[::-1]))

                poly = np.concatenate((line1, line2), axis=0)

                polys.append(poly)



        polyc = art3d.Poly3DCollection(polys, facecolors=facecolors, shade=shade,

                                       axlim_clip=axlim_clip, **kwargs)

        self.add_collection(polyc, autolim="_datalim_only")



        self.auto_scale_xyz([x1, x2], [y1, y2], [z1, z2], had_data)

        return polyc



    def plot_surface(self, X, Y, Z, *, norm=None, vmin=None,

                     vmax=None, lightsource=None, axlim_clip=False, **kwargs):

        



        had_data = self.has_data()



        if Z.ndim != 2:

            raise ValueError("Argument Z must be 2-dimensional.")



        Z = cbook._to_unmasked_float_array(Z)

        X, Y, Z = np.broadcast_arrays(X, Y, Z)

        rows, cols = Z.shape



        has_stride = 'rstride' in kwargs or 'cstride' in kwargs

        has_count = 'rcount' in kwargs or 'ccount' in kwargs



        if has_stride and has_count:

            raise ValueError("Cannot specify both stride and count arguments")



        rstride = kwargs.pop('rstride', 10)

        cstride = kwargs.pop('cstride', 10)

        rcount = kwargs.pop('rcount', 50)

        ccount = kwargs.pop('ccount', 50)



        if mpl.rcParams['_internal.classic_mode']:

                                                                

                                                  

                                             

            compute_strides = has_count

        else:

                                                               

                                                             

            compute_strides = not has_stride



        if compute_strides:

            rstride = int(max(np.ceil(rows / rcount), 1))

            cstride = int(max(np.ceil(cols / ccount), 1))



        fcolors = kwargs.pop('facecolors', None)



        cmap = kwargs.get('cmap', None)

        shade = kwargs.pop('shade', cmap is None)

        if shade is None:

            raise ValueError("shade cannot be None.")



        colset = []                         

        if (rows - 1) % rstride == 0 and
           (cols - 1) % cstride == 0 and
           fcolors is None:

            polys = np.stack(

                [cbook._array_patch_perimeters(a, rstride, cstride)

                 for a in (X, Y, Z)],

                axis=-1)

        else:

                                                         

            row_inds = list(range(0, rows-1, rstride)) + [rows-1]

            col_inds = list(range(0, cols-1, cstride)) + [cols-1]



            polys = []

            for rs, rs_next in itertools.pairwise(row_inds):

                for cs, cs_next in itertools.pairwise(col_inds):

                    ps = [

                                                                    

                        cbook._array_perimeter(a[rs:rs_next+1, cs:cs_next+1])

                        for a in (X, Y, Z)

                    ]

                                                

                    ps = np.array(ps).T

                    polys.append(ps)



                    if fcolors is not None:

                        colset.append(fcolors[rs][cs])



                                                                                    

                                                                                     

                                      

        if not isinstance(polys, np.ndarray) or not np.isfinite(polys).all():

            new_polys = []

            new_colset = []



                                                                            

                                                                              

                                                                

            for p, col in itertools.zip_longest(polys, colset):

                new_poly = np.array(p)[np.isfinite(p).all(axis=1)]

                if len(new_poly):

                    new_polys.append(new_poly)

                    new_colset.append(col)



                                                                        

            polys = new_polys

            if fcolors is not None:

                colset = new_colset



                                                                              

                     



        if fcolors is not None:

            polyc = art3d.Poly3DCollection(

                polys, edgecolors=colset, facecolors=colset, shade=shade,

                lightsource=lightsource, axlim_clip=axlim_clip, **kwargs)

        elif cmap:

            polyc = art3d.Poly3DCollection(polys, axlim_clip=axlim_clip, **kwargs)

                                                                   

            if isinstance(polys, np.ndarray):

                avg_z = polys[..., 2].mean(axis=-1)

            else:

                avg_z = np.array([ps[:, 2].mean() for ps in polys])

            polyc.set_array(avg_z)

            if vmin is not None or vmax is not None:

                polyc.set_clim(vmin, vmax)

            if norm is not None:

                polyc.set_norm(norm)

        else:

            color = kwargs.pop('color', None)

            if color is None:

                color = self._get_lines.get_next_color()

            color = np.array(mcolors.to_rgba(color))



            polyc = art3d.Poly3DCollection(

                polys, facecolors=color, shade=shade, lightsource=lightsource,

                axlim_clip=axlim_clip, **kwargs)



        self.add_collection(polyc, autolim="_datalim_only")

        self.auto_scale_xyz(X, Y, Z, had_data)



        return polyc



    def plot_wireframe(self, X, Y, Z, *, axlim_clip=False, **kwargs):

        



        had_data = self.has_data()

        if Z.ndim != 2:

            raise ValueError("Argument Z must be 2-dimensional.")

                                      

        X, Y, Z = np.broadcast_arrays(X, Y, Z)

        rows, cols = Z.shape



        has_stride = 'rstride' in kwargs or 'cstride' in kwargs

        has_count = 'rcount' in kwargs or 'ccount' in kwargs



        if has_stride and has_count:

            raise ValueError("Cannot specify both stride and count arguments")



        rstride = kwargs.pop('rstride', 1)

        cstride = kwargs.pop('cstride', 1)

        rcount = kwargs.pop('rcount', 50)

        ccount = kwargs.pop('ccount', 50)



        if mpl.rcParams['_internal.classic_mode']:

                                                                

                                                  

                                             

            if has_count:

                rstride = int(max(np.ceil(rows / rcount), 1)) if rcount else 0

                cstride = int(max(np.ceil(cols / ccount), 1)) if ccount else 0

        else:

                                                               

                                                             

            if not has_stride:

                rstride = int(max(np.ceil(rows / rcount), 1)) if rcount else 0

                cstride = int(max(np.ceil(cols / ccount), 1)) if ccount else 0



        if rstride == 0 and cstride == 0:

            raise ValueError("Either rstride or cstride must be non zero")



                                                                    

                                                                      

                                                                 

        tX, tY, tZ = np.transpose(X), np.transpose(Y), np.transpose(Z)



                                                                     

                                                                                  

        if rstride == 0 or Z.size == 0:

            rii = np.array([], dtype=int)

        elif (rows - 1) % rstride == 0:

                                                    

            rii = np.arange(0, rows, rstride)

        else:

                                

            rii = np.arange(0, rows + rstride, rstride)

            rii[-1] = rows - 1



        if cstride == 0 or Z.size == 0:

            cii = np.array([], dtype=int)

        elif (cols - 1) % cstride == 0:

                                                    

            cii = np.arange(0, cols, cstride)

        else:

                                

            cii = np.arange(0, cols + cstride, cstride)

            cii[-1] = cols - 1



        row_lines = np.stack([X[rii], Y[rii], Z[rii]], axis=-1)

        col_lines = np.stack([tX[cii], tY[cii], tZ[cii]], axis=-1)



                                                                                     

                                                                                      

                                                    

                                                                                

                                                                            

        self.auto_scale_xyz(row_lines[..., 0], row_lines[..., 1], row_lines[..., 2],

                            had_data)

        self.auto_scale_xyz(col_lines[..., 0], col_lines[..., 1], col_lines[..., 2],

                            had_data=True)



        lines = list(row_lines) + list(col_lines)

        linec = art3d.Line3DCollection(lines, axlim_clip=axlim_clip, **kwargs)

        self.add_collection(linec, autolim="_datalim_only")



        return linec



    def plot_trisurf(self, *args, color=None, norm=None, vmin=None, vmax=None,

                     lightsource=None, axlim_clip=False, **kwargs):

        



        had_data = self.has_data()



                                           

        if color is None:

            color = self._get_lines.get_next_color()

        color = np.array(mcolors.to_rgba(color))



        cmap = kwargs.get('cmap', None)

        shade = kwargs.pop('shade', cmap is None)



        tri, args, kwargs =
            Triangulation.get_from_args_and_kwargs(*args, **kwargs)

        try:

            z = kwargs.pop('Z')

        except KeyError:

                                                                            

            z, *args = args

        z = np.asarray(z)



        triangles = tri.get_masked_triangles()

        xt = tri.x[triangles]

        yt = tri.y[triangles]

        zt = z[triangles]

        verts = np.stack((xt, yt, zt), axis=-1)



        if cmap:

            polyc = art3d.Poly3DCollection(verts, *args,

                                           axlim_clip=axlim_clip, **kwargs)

                                                            

            avg_z = verts[:, :, 2].mean(axis=1)

            polyc.set_array(avg_z)

            if vmin is not None or vmax is not None:

                polyc.set_clim(vmin, vmax)

            if norm is not None:

                polyc.set_norm(norm)

        else:

            polyc = art3d.Poly3DCollection(

                verts, *args, shade=shade, lightsource=lightsource,

                facecolors=color, axlim_clip=axlim_clip, **kwargs)



        self.add_collection(polyc, autolim="_datalim_only")

        self.auto_scale_xyz(tri.x, tri.y, z, had_data)



        return polyc



    def _3d_extend_contour(self, cset, stride=5):

        



        dz = (cset.levels[1] - cset.levels[0]) / 2

        polyverts = []

        colors = []

        for idx, level in enumerate(cset.levels):

            path = cset.get_paths()[idx]

            subpaths = [*path._iter_connected_components()]

            color = cset.get_edgecolor()[idx]

            top = art3d._paths_to_3d_segments(subpaths, level - dz)

            bot = art3d._paths_to_3d_segments(subpaths, level + dz)

            if not len(top[0]):

                continue

            nsteps = max(round(len(top[0]) / stride), 2)

            stepsize = (len(top[0]) - 1) / (nsteps - 1)

            polyverts.extend([

                (top[0][round(i * stepsize)], top[0][round((i + 1) * stepsize)],

                 bot[0][round((i + 1) * stepsize)], bot[0][round(i * stepsize)])

                for i in range(round(nsteps) - 1)])

            colors.extend([color] * (round(nsteps) - 1))

        self.add_collection3d(art3d.Poly3DCollection(

            np.array(polyverts),                                               

            facecolors=colors, edgecolors=colors, shade=True))

        cset.remove()



    def add_contour_set(

            self, cset, extend3d=False, stride=5, zdir='z', offset=None,

            axlim_clip=False):

        zdir = '-' + zdir

        if extend3d:

            self._3d_extend_contour(cset, stride)

        else:

            art3d.collection_2d_to_3d(

                cset, zs=offset if offset is not None else cset.levels, zdir=zdir,

                axlim_clip=axlim_clip)



    def add_contourf_set(self, cset, zdir='z', offset=None, *, axlim_clip=False):

        self._add_contourf_set(cset, zdir=zdir, offset=offset,

                               axlim_clip=axlim_clip)



    def _add_contourf_set(self, cset, zdir='z', offset=None, axlim_clip=False):

        

        zdir = '-' + zdir



        midpoints = cset.levels[:-1] + np.diff(cset.levels) / 2

                                                               

        if cset._extend_min:

            min_level = cset.levels[0] - np.diff(cset.levels[:2]) / 2

            midpoints = np.insert(midpoints, 0, min_level)

        if cset._extend_max:

            max_level = cset.levels[-1] + np.diff(cset.levels[-2:]) / 2

            midpoints = np.append(midpoints, max_level)



        art3d.collection_2d_to_3d(

            cset, zs=offset if offset is not None else midpoints, zdir=zdir,

            axlim_clip=axlim_clip)

        return midpoints



    @_preprocess_data()

    def contour(self, X, Y, Z, *args,

                extend3d=False, stride=5, zdir='z', offset=None, axlim_clip=False,

                **kwargs):

        

        had_data = self.has_data()



        jX, jY, jZ = art3d.rotate_axes(X, Y, Z, zdir)

        cset = super().contour(jX, jY, jZ, *args, **kwargs)

        self.add_contour_set(cset, extend3d, stride, zdir, offset, axlim_clip)



        self.auto_scale_xyz(X, Y, Z, had_data)

        return cset



    contour3D = contour



    @_preprocess_data()

    def tricontour(self, *args,

                   extend3d=False, stride=5, zdir='z', offset=None, axlim_clip=False,

                   **kwargs):

        

        had_data = self.has_data()



        tri, args, kwargs = Triangulation.get_from_args_and_kwargs(

                *args, **kwargs)

        X = tri.x

        Y = tri.y

        if 'Z' in kwargs:

            Z = kwargs.pop('Z')

        else:

                                                                             

            Z, *args = args



        jX, jY, jZ = art3d.rotate_axes(X, Y, Z, zdir)

        tri = Triangulation(jX, jY, tri.triangles, tri.mask)



        cset = super().tricontour(tri, jZ, *args, **kwargs)

        self.add_contour_set(cset, extend3d, stride, zdir, offset, axlim_clip)



        self.auto_scale_xyz(X, Y, Z, had_data)

        return cset



    def _auto_scale_contourf(self, X, Y, Z, zdir, levels, had_data):

                                                                    

                                                                         

        dim_vals = {'x': X, 'y': Y, 'z': Z, zdir: levels}

                                                                        

                                                                   

        limits = [(np.nanmin(dim_vals[dim]), np.nanmax(dim_vals[dim]))

                  for dim in ['x', 'y', 'z']]

        self.auto_scale_xyz(*limits, had_data)



    @_preprocess_data()

    def contourf(self, X, Y, Z, *args,

                 zdir='z', offset=None, axlim_clip=False, **kwargs):

        

        had_data = self.has_data()



        jX, jY, jZ = art3d.rotate_axes(X, Y, Z, zdir)

        cset = super().contourf(jX, jY, jZ, *args, **kwargs)

        levels = self._add_contourf_set(cset, zdir, offset, axlim_clip)



        self._auto_scale_contourf(X, Y, Z, zdir, levels, had_data)

        return cset



    contourf3D = contourf



    @_preprocess_data()

    def tricontourf(self, *args, zdir='z', offset=None, axlim_clip=False, **kwargs):

        

        had_data = self.has_data()



        tri, args, kwargs = Triangulation.get_from_args_and_kwargs(

                *args, **kwargs)

        X = tri.x

        Y = tri.y

        if 'Z' in kwargs:

            Z = kwargs.pop('Z')

        else:

                                                                              

            Z, *args = args



        jX, jY, jZ = art3d.rotate_axes(X, Y, Z, zdir)

        tri = Triangulation(jX, jY, tri.triangles, tri.mask)



        cset = super().tricontourf(tri, jZ, *args, **kwargs)

        levels = self._add_contourf_set(cset, zdir, offset, axlim_clip)



        self._auto_scale_contourf(X, Y, Z, zdir, levels, had_data)

        return cset



    def add_collection3d(self, col, zs=0, zdir='z', autolim=True, *,

                         axlim_clip=False):

        

        had_data = self.has_data()



        zvals = np.atleast_1d(zs)

        zsortval = (np.min(zvals) if zvals.size

                    else 0)                            



                                                                 

                                                                   

                                                       

        if type(col) is mcoll.PolyCollection:

            art3d.poly_collection_2d_to_3d(col, zs=zs, zdir=zdir,

                                           axlim_clip=axlim_clip)

            col.set_sort_zpos(zsortval)

        elif type(col) is mcoll.LineCollection:

            art3d.line_collection_2d_to_3d(col, zs=zs, zdir=zdir,

                                           axlim_clip=axlim_clip)

            col.set_sort_zpos(zsortval)

        elif type(col) is mcoll.PatchCollection:

            art3d.patch_collection_2d_to_3d(col, zs=zs, zdir=zdir,

                                            axlim_clip=axlim_clip)

            col.set_sort_zpos(zsortval)



        if autolim:

            if isinstance(col, art3d.Line3DCollection):

                self.auto_scale_xyz(*np.array(col._segments3d).transpose(),

                                    had_data=had_data)

            elif isinstance(col, art3d.Poly3DCollection):

                self.auto_scale_xyz(col._faces[..., 0],

                                    col._faces[..., 1],

                                    col._faces[..., 2], had_data=had_data)

            elif isinstance(col, art3d.Patch3DCollection):

                pass

                                                                              

                                                                                

                                                                                       



        collection = super().add_collection(col, autolim="_datalim_only")

        return collection



    @_preprocess_data(replace_names=["xs", "ys", "zs", "s",

                                     "edgecolors", "c", "facecolor",

                                     "facecolors", "color"])

    def scatter(self, xs, ys, zs=0, zdir='z', s=20, c=None, depthshade=None,

                *args,

                depthshade_minalpha=None,

                axlim_clip=False,

                **kwargs):

        



        had_data = self.has_data()

        zs_orig = zs



        xs, ys, zs = cbook._broadcast_with_masks(xs, ys, zs)

        s = np.ma.ravel(s)                                            



        xs, ys, zs, s, c, color = cbook.delete_masked_points(

            xs, ys, zs, s, c, kwargs.get('color', None)

            )

        if kwargs.get("color") is not None:

            kwargs['color'] = color

        if depthshade is None:

            depthshade = mpl.rcParams['axes3d.depthshade']

        if depthshade_minalpha is None:

            depthshade_minalpha = mpl.rcParams['axes3d.depthshade_minalpha']



                                                          

        if np.may_share_memory(zs_orig, zs):                             

            zs = zs.copy()



        patches = super().scatter(xs, ys, s=s, c=c, *args, **kwargs)

        art3d.patch_collection_2d_to_3d(

            patches,

            zs=zs,

            zdir=zdir,

            depthshade=depthshade,

            depthshade_minalpha=depthshade_minalpha,

            axlim_clip=axlim_clip,

        )

        if self._zmargin < 0.05 and xs.size > 0:

            self.set_zmargin(0.05)



        self.auto_scale_xyz(xs, ys, zs, had_data)



        return patches



    scatter3D = scatter



    @_preprocess_data()

    def bar(self, left, height, zs=0, zdir='z', *args,

            axlim_clip=False, **kwargs):

        

        had_data = self.has_data()



        patches = super().bar(left, height, *args, **kwargs)



        zs = np.broadcast_to(zs, len(left), subok=True)



        verts = []

        verts_zs = []

        for p, z in zip(patches, zs):

            vs = art3d._get_patch_verts(p)

            verts += vs.tolist()

            verts_zs += [z] * len(vs)

            art3d.patch_2d_to_3d(p, z, zdir, axlim_clip)

            if 'alpha' in kwargs:

                p.set_alpha(kwargs['alpha'])



        if len(verts) > 0:

                                                               

                                                             

                                                     

            xs, ys = zip(*verts)

        else:

            xs, ys = [], []



        xs, ys, verts_zs = art3d.juggle_axes(xs, ys, verts_zs, zdir)

        self.auto_scale_xyz(xs, ys, verts_zs, had_data)



        return patches



    @_preprocess_data()

    def bar3d(self, x, y, z, dx, dy, dz, color=None,

              zsort='average', shade=True, lightsource=None, *args,

              axlim_clip=False, **kwargs):

        



        had_data = self.has_data()



        x, y, z, dx, dy, dz = np.broadcast_arrays(

            np.atleast_1d(x), y, z, dx, dy, dz)

        minx = np.min(x)

        maxx = np.max(x + dx)

        miny = np.min(y)

        maxy = np.max(y + dy)

        minz = np.min(z)

        maxz = np.max(z + dz)



                         

                                                                       

                                                                     

        cuboid = np.array([

                

            (

                (0, 0, 0),

                (0, 1, 0),

                (1, 1, 0),

                (1, 0, 0),

            ),

                

            (

                (0, 0, 1),

                (1, 0, 1),

                (1, 1, 1),

                (0, 1, 1),

            ),

                

            (

                (0, 0, 0),

                (1, 0, 0),

                (1, 0, 1),

                (0, 0, 1),

            ),

                

            (

                (0, 1, 0),

                (0, 1, 1),

                (1, 1, 1),

                (1, 1, 0),

            ),

                

            (

                (0, 0, 0),

                (0, 0, 1),

                (0, 1, 1),

                (0, 1, 0),

            ),

                

            (

                (1, 0, 0),

                (1, 1, 0),

                (1, 1, 1),

                (1, 0, 1),

            ),

        ])



                                               

        polys = np.empty(x.shape + cuboid.shape)



                                           

        for i, p, dp in [(0, x, dx), (1, y, dy), (2, z, dz)]:

            p = p[..., np.newaxis, np.newaxis]

            dp = dp[..., np.newaxis, np.newaxis]

            polys[..., i] = p + dp * cuboid[..., i]



                                     

        polys = polys.reshape((-1,) + polys.shape[2:])



        facecolors = []

        if color is None:

            color = [self._get_patches_for_fill.get_next_color()]



        color = list(mcolors.to_rgba_array(color))



        if len(color) == len(x):

                                                                     

            for c in color:

                facecolors.extend([c] * 6)

        else:

                                                                           

            facecolors = color

            if len(facecolors) < len(x):

                facecolors *= (6 * len(x))



        col = art3d.Poly3DCollection(polys,

                                     zsort=zsort,

                                     facecolors=facecolors,

                                     shade=shade,

                                     lightsource=lightsource,

                                     axlim_clip=axlim_clip,

                                     *args, **kwargs)

        self.add_collection(col, autolim="_datalim_only")



        self.auto_scale_xyz((minx, maxx), (miny, maxy), (minz, maxz), had_data)



        return col



    def set_title(self, label, fontdict=None, loc='center', **kwargs):

                             

        ret = super().set_title(label, fontdict=fontdict, loc=loc, **kwargs)

        (x, y) = self.title.get_position()

        self.title.set_y(0.92 * y)

        return ret



    @_preprocess_data()

    def quiver(self, X, Y, Z, U, V, W, *,

               length=1, arrow_length_ratio=.3, pivot='tail', normalize=False,

               axlim_clip=False, **kwargs):

        



        def calc_arrows(UVW):

                                                                  

            x = UVW[:, 0]

            y = UVW[:, 1]

            norm = np.linalg.norm(UVW[:, :2], axis=1)

            x_p = np.divide(y, norm, where=norm != 0, out=np.zeros_like(x))

            y_p = np.divide(-x,  norm, where=norm != 0, out=np.ones_like(x))

                                                              

            rangle = math.radians(15)

            c = math.cos(rangle)

            s = math.sin(rangle)

                                                                

            r13 = y_p * s

            r32 = x_p * s

            r12 = x_p * y_p * (1 - c)

            Rpos = np.array(

                [[c + (x_p ** 2) * (1 - c), r12, r13],

                 [r12, c + (y_p ** 2) * (1 - c), -r32],

                 [-r13, r32, np.full_like(x_p, c)]])

                                                         

            Rneg = Rpos.copy()

            Rneg[[0, 1, 2, 2], [2, 2, 0, 1]] *= -1

                                                                               

            Rpos_vecs = np.einsum("ij...,...j->...i", Rpos, UVW)

            Rneg_vecs = np.einsum("ij...,...j->...i", Rneg, UVW)

                                          

            return np.stack([Rpos_vecs, Rneg_vecs], axis=1)



        had_data = self.has_data()



        input_args = cbook._broadcast_with_masks(X, Y, Z, U, V, W,

                                                 compress=True)



        if any(len(v) == 0 for v in input_args):

                                                                           

            linec = art3d.Line3DCollection([], **kwargs)

            self.add_collection(linec, autolim="_datalim_only")

            return linec



        shaft_dt = np.array([0., length], dtype=float)

        arrow_dt = shaft_dt * arrow_length_ratio



        _api.check_in_list(['tail', 'middle', 'tip'], pivot=pivot)

        if pivot == 'tail':

            shaft_dt -= length

        elif pivot == 'middle':

            shaft_dt -= length / 2



        XYZ = np.column_stack(input_args[:3])

        UVW = np.column_stack(input_args[3:]).astype(float)



                               

        if normalize:

            norm = np.linalg.norm(UVW, axis=1)

            norm[norm == 0] = 1

            UVW = UVW / norm.reshape((-1, 1))



        if len(XYZ) > 0:

                                                                       

            shafts = (XYZ - np.multiply.outer(shaft_dt, UVW)).swapaxes(0, 1)

                                                                              

            head_dirs = calc_arrows(UVW)

                                                                          

            heads = shafts[:, :1] - np.multiply.outer(arrow_dt, head_dirs)

                                                      

            heads = heads.reshape((len(arrow_dt), -1, 3))

                                              

            heads = heads.swapaxes(0, 1)



            lines = [*shafts, *heads[::2], *heads[1::2]]

        else:

            lines = []



        linec = art3d.Line3DCollection(lines, axlim_clip=axlim_clip, **kwargs)

        self.add_collection(linec, autolim="_datalim_only")



        self.auto_scale_xyz(XYZ[:, 0], XYZ[:, 1], XYZ[:, 2], had_data)



        return linec



    quiver3D = quiver



    def voxels(self, *args, facecolors=None, edgecolors=None, shade=True,

               lightsource=None, axlim_clip=False, **kwargs):

        



                                                                          

                                                                          

        if len(args) >= 3:

                                                

            def voxels(__x, __y, __z, filled, **kwargs):

                return (__x, __y, __z), filled, kwargs

        else:

            def voxels(filled, **kwargs):

                return None, filled, kwargs



        xyz, filled, kwargs = voxels(*args, **kwargs)



                          

        if filled.ndim != 3:

            raise ValueError("Argument filled must be 3-dimensional")

        size = np.array(filled.shape, dtype=np.intp)



                                                                           

        coord_shape = tuple(size + 1)

        if xyz is None:

            x, y, z = np.indices(coord_shape)

        else:

            x, y, z = (np.broadcast_to(c, coord_shape) for c in xyz)



        def _broadcast_color_arg(color, name):

            if np.ndim(color) in (0, 1):

                                                       

                return np.broadcast_to(color, filled.shape + np.shape(color))

            elif np.ndim(color) in (3, 4):

                                                                     

                if np.shape(color)[:3] != filled.shape:

                    raise ValueError(

                        f"When multidimensional, {name} must match the shape "

                        "of filled")

                return color

            else:

                raise ValueError(f"Invalid {name} argument")



                                             

        if facecolors is None:

            facecolors = self._get_patches_for_fill.get_next_color()

        facecolors = _broadcast_color_arg(facecolors, 'facecolors')



                                                

        edgecolors = _broadcast_color_arg(edgecolors, 'edgecolors')



                                                                         

        self.auto_scale_xyz(x, y, z)



                                             

        square = np.array([

            [0, 0, 0],

            [1, 0, 0],

            [1, 1, 0],

            [0, 1, 0],

        ], dtype=np.intp)



        voxel_faces = defaultdict(list)



        def permutation_matrices(n):

            

            mat = np.eye(n, dtype=np.intp)

            for i in range(n):

                yield mat

                mat = np.roll(mat, 1, axis=0)



                                                                             

                   

        for permute in permutation_matrices(3):

                                                    

            pc, qc, rc = permute.T.dot(size)

            pinds = np.arange(pc)

            qinds = np.arange(qc)

            rinds = np.arange(rc)



            square_rot_pos = square.dot(permute.T)

            square_rot_neg = square_rot_pos[::-1]



                                              

            for p in pinds:

                for q in qinds:

                                                                            

                                                                           

                                                                   



                                      

                    p0 = permute.dot([p, q, 0])

                    i0 = tuple(p0)

                    if filled[i0]:

                        voxel_faces[i0].append(p0 + square_rot_neg)



                                       

                    for r1, r2 in itertools.pairwise(rinds):

                        p1 = permute.dot([p, q, r1])

                        p2 = permute.dot([p, q, r2])



                        i1 = tuple(p1)

                        i2 = tuple(p2)



                        if filled[i1] and not filled[i2]:

                            voxel_faces[i1].append(p2 + square_rot_pos)

                        elif not filled[i1] and filled[i2]:

                            voxel_faces[i2].append(p2 + square_rot_neg)



                                      

                    pk = permute.dot([p, q, rc-1])

                    pk2 = permute.dot([p, q, rc])

                    ik = tuple(pk)

                    if filled[ik]:

                        voxel_faces[ik].append(pk2 + square_rot_pos)



                                                                          

               

        polygons = {}

        for coord, faces_inds in voxel_faces.items():

                                               

            if xyz is None:

                faces = faces_inds

            else:

                faces = []

                for face_inds in faces_inds:

                    ind = face_inds[:, 0], face_inds[:, 1], face_inds[:, 2]

                    face = np.empty(face_inds.shape)

                    face[:, 0] = x[ind]

                    face[:, 1] = y[ind]

                    face[:, 2] = z[ind]

                    faces.append(face)



                             

            facecolor = facecolors[coord]

            edgecolor = edgecolors[coord]



            poly = art3d.Poly3DCollection(

                faces, facecolors=facecolor, edgecolors=edgecolor,

                shade=shade, lightsource=lightsource, axlim_clip=axlim_clip,

                **kwargs)

            self.add_collection3d(poly)

            polygons[coord] = poly



        return polygons



    @_preprocess_data(replace_names=["x", "y", "z", "xerr", "yerr", "zerr"])

    def errorbar(self, x, y, z, zerr=None, yerr=None, xerr=None, fmt='',

                 barsabove=False, errorevery=1, ecolor=None, elinewidth=None,

                 capsize=None, capthick=None, xlolims=False, xuplims=False,

                 ylolims=False, yuplims=False, zlolims=False, zuplims=False,

                 axlim_clip=False,

                 **kwargs):

        

        had_data = self.has_data()



        kwargs = cbook.normalize_kwargs(kwargs, mlines.Line2D)

                                                                         

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        kwargs.setdefault('zorder', 2)



        self._process_unit_info([("x", x), ("y", y), ("z", z)], kwargs,

                                convert=False)



                                                                      

                        

        x = x if np.iterable(x) else [x]

        y = y if np.iterable(y) else [y]

        z = z if np.iterable(z) else [z]



        if not len(x) == len(y) == len(z):

            raise ValueError("'x', 'y', and 'z' must have the same size")



        everymask = self._errorevery_to_mask(x, errorevery)



        label = kwargs.pop("label", None)

        kwargs['label'] = '_nolegend_'



                                                                              

                                                                              

                                                                              

                          

        (data_line, base_style), = self._get_lines._plot_args(

            self, (x, y) if fmt == '' else (x, y, fmt), kwargs, return_kwargs=True)

        art3d.line_2d_to_3d(data_line, zs=z, axlim_clip=axlim_clip)



                                                                             

        if barsabove:

            data_line.set_zorder(kwargs['zorder'] - .1)

        else:

            data_line.set_zorder(kwargs['zorder'] + .1)



                                                                            

        if fmt.lower() != 'none':

            self.add_line(data_line)

        else:

            data_line = None

                                                                     

            base_style.pop('color')



        if 'color' not in base_style:

            base_style['color'] = 'C0'

        if ecolor is None:

            ecolor = base_style['color']



                                                                             

                                  

        for key in ['marker', 'markersize', 'markerfacecolor',

                    'markeredgewidth', 'markeredgecolor', 'markevery',

                    'linestyle', 'fillstyle', 'drawstyle', 'dash_capstyle',

                    'dash_joinstyle', 'solid_capstyle', 'solid_joinstyle']:

            base_style.pop(key, None)



                                                                  

        eb_lines_style = {**base_style, 'color': ecolor}



        if elinewidth:

            eb_lines_style['linewidth'] = elinewidth

        elif 'linewidth' in kwargs:

            eb_lines_style['linewidth'] = kwargs['linewidth']



        for key in ('transform', 'alpha', 'zorder', 'rasterized'):

            if key in kwargs:

                eb_lines_style[key] = kwargs[key]



                                                    

        eb_cap_style = {**base_style, 'linestyle': 'None'}

        if capsize is None:

            capsize = mpl.rcParams["errorbar.capsize"]

        if capsize > 0:

            eb_cap_style['markersize'] = 2. * capsize

        if capthick is not None:

            eb_cap_style['markeredgewidth'] = capthick

        eb_cap_style['color'] = ecolor



        def _apply_mask(arrays, mask):

                                                                               

                                                    

            return [[*itertools.compress(array, mask)] for array in arrays]



        def _extract_errs(err, data, lomask, himask):

                                                                 

            if len(err.shape) == 2:

                low_err, high_err = err

            else:

                low_err, high_err = err, err



            lows = np.where(lomask | ~everymask, data, data - low_err)

            highs = np.where(himask | ~everymask, data, data + high_err)



            return lows, highs



                                                                      

        errlines, caplines, limmarks = [], [], []



                                                             

        coorderrs = []



                                                                    

                                                                       

        capmarker = {0: '|', 1: '|', 2: '_'}

        i_xyz = {'x': 0, 'y': 1, 'z': 2}



                                                                               

                                                                              

                                                                            

                                                                           

                                       

        quiversize = eb_cap_style.get('markersize',

                                      mpl.rcParams['lines.markersize']) ** 2

        quiversize *= self.get_figure(root=True).dpi / 72

        quiversize = self.transAxes.inverted().transform([

            (0, 0), (quiversize, quiversize)])

        quiversize = np.mean(np.diff(quiversize, axis=0))

                                                                            

                                                                              

                                                                      

        with cbook._setattr_cm(self, elev=0, azim=0, roll=0):

            invM = np.linalg.inv(self.get_proj())

                                                                             

                                       

        quiversize = np.dot(invM, [quiversize, 0, 0, 0])[1]

                                                                             

                                                                              

                                                                            

        quiversize *= 1.8660254037844388

        eb_quiver_style = {**eb_cap_style,

                           'length': quiversize, 'arrow_length_ratio': 1}

        eb_quiver_style.pop('markersize', None)



                                                                      

        for zdir, data, err, lolims, uplims in zip(

                ['x', 'y', 'z'], [x, y, z], [xerr, yerr, zerr],

                [xlolims, ylolims, zlolims], [xuplims, yuplims, zuplims]):



            dir_vector = art3d.get_dir_vector(zdir)

            i_zdir = i_xyz[zdir]



            if err is None:

                continue



            if not np.iterable(err):

                err = [err] * len(data)



            err = np.atleast_1d(err)



                                                                     

            lolims = np.broadcast_to(lolims, len(data)).astype(bool)

            uplims = np.broadcast_to(uplims, len(data)).astype(bool)



                                                                              

                                                                       

                                                                      

            coorderr = [

                _extract_errs(err * dir_vector[i], coord, lolims, uplims)

                for i, coord in enumerate([x, y, z])]

            (xl, xh), (yl, yh), (zl, zh) = coorderr



                                                                       

            nolims = ~(lolims | uplims)

            if nolims.any() and capsize > 0:

                lo_caps_xyz = _apply_mask([xl, yl, zl], nolims & everymask)

                hi_caps_xyz = _apply_mask([xh, yh, zh], nolims & everymask)



                                                                   

                                                                        

                cap_lo = art3d.Line3D(*lo_caps_xyz, ls='',

                                      marker=capmarker[i_zdir],

                                      axlim_clip=axlim_clip,

                                      **eb_cap_style)

                cap_hi = art3d.Line3D(*hi_caps_xyz, ls='',

                                      marker=capmarker[i_zdir],

                                      axlim_clip=axlim_clip,

                                      **eb_cap_style)

                self.add_line(cap_lo)

                self.add_line(cap_hi)

                caplines.append(cap_lo)

                caplines.append(cap_hi)



            if lolims.any():

                xh0, yh0, zh0 = _apply_mask([xh, yh, zh], lolims & everymask)

                self.quiver(xh0, yh0, zh0, *dir_vector, **eb_quiver_style)

            if uplims.any():

                xl0, yl0, zl0 = _apply_mask([xl, yl, zl], uplims & everymask)

                self.quiver(xl0, yl0, zl0, *-dir_vector, **eb_quiver_style)



            errline = art3d.Line3DCollection(np.array(coorderr).T,

                                             axlim_clip=axlim_clip,

                                             **eb_lines_style)

            self.add_collection(errline, autolim="_datalim_only")

            errlines.append(errline)

            coorderrs.append(coorderr)



        coorderrs = np.array(coorderrs)



        def _digout_minmax(err_arr, coord_label):

            return (np.nanmin(err_arr[:, i_xyz[coord_label], :, :]),

                    np.nanmax(err_arr[:, i_xyz[coord_label], :, :]))



        minx, maxx = _digout_minmax(coorderrs, 'x')

        miny, maxy = _digout_minmax(coorderrs, 'y')

        minz, maxz = _digout_minmax(coorderrs, 'z')

        self.auto_scale_xyz((minx, maxx), (miny, maxy), (minz, maxz), had_data)



                                                                               

        errorbar_container = mcontainer.ErrorbarContainer(

            (data_line, tuple(caplines), tuple(errlines)),

            has_xerr=(xerr is not None or yerr is not None),

            has_yerr=(zerr is not None),

            label=label)

        self.containers.append(errorbar_container)



        return errlines, caplines, limmarks



    def get_tightbbox(self, renderer=None, *, call_axes_locator=True,

                      bbox_extra_artists=None, for_layout_only=False):

        ret = super().get_tightbbox(renderer,

                                    call_axes_locator=call_axes_locator,

                                    bbox_extra_artists=bbox_extra_artists,

                                    for_layout_only=for_layout_only)

        batch = [ret]

        if self._axis3don:

            for axis in self._axis_map.values():

                if axis.get_visible():

                    axis_bb = martist._get_tightbbox_for_layout_only(

                        axis, renderer)

                    if axis_bb:

                        batch.append(axis_bb)

        return mtransforms.Bbox.union(batch)



    @_preprocess_data()

    def stem(self, x, y, z, *, linefmt='C0-', markerfmt='C0o', basefmt='C3-',

             bottom=0, label=None, orientation='z', axlim_clip=False):

        



        from matplotlib.container import StemContainer



        had_data = self.has_data()



        _api.check_in_list(['x', 'y', 'z'], orientation=orientation)



        xlim = (np.min(x), np.max(x))

        ylim = (np.min(y), np.max(y))

        zlim = (np.min(z), np.max(z))



                                                                               

                                                      

        if orientation == 'x':

            basex, basexlim = y, ylim

            basey, baseylim = z, zlim

            lines = [[(bottom, thisy, thisz), (thisx, thisy, thisz)]

                     for thisx, thisy, thisz in zip(x, y, z)]

        elif orientation == 'y':

            basex, basexlim = x, xlim

            basey, baseylim = z, zlim

            lines = [[(thisx, bottom, thisz), (thisx, thisy, thisz)]

                     for thisx, thisy, thisz in zip(x, y, z)]

        else:

            basex, basexlim = x, xlim

            basey, baseylim = y, ylim

            lines = [[(thisx, thisy, bottom), (thisx, thisy, thisz)]

                     for thisx, thisy, thisz in zip(x, y, z)]



                                         

        linestyle, linemarker, linecolor = _process_plot_format(linefmt)

        linestyle = mpl._val_or_rc(linestyle, 'lines.linestyle')



                                            

        baseline, = self.plot(basex, basey, basefmt, zs=bottom,

                              zdir=orientation, label='_nolegend_')

        stemlines = art3d.Line3DCollection(

            lines, linestyles=linestyle, colors=linecolor, label='_nolegend_',

            axlim_clip=axlim_clip)

        self.add_collection(stemlines, autolim="_datalim_only")

        markerline, = self.plot(x, y, z, markerfmt, label='_nolegend_')



        stem_container = StemContainer((markerline, stemlines, baseline),

                                       label=label)

        self.add_container(stem_container)



        jx, jy, jz = art3d.juggle_axes(basexlim, baseylim, [bottom, bottom],

                                       orientation)

        self.auto_scale_xyz([*jx, *xlim], [*jy, *ylim], [*jz, *zlim], had_data)



        return stem_container



    stem3D = stem





def get_test_data(delta=0.05):

    

    x = y = np.arange(-3.0, 3.0, delta)

    X, Y = np.meshgrid(x, y)



    Z1 = np.exp(-(X**2 + Y**2) / 2) / (2 * np.pi)

    Z2 = (np.exp(-(((X - 1) / 1.5)**2 + ((Y - 1) / 0.5)**2) / 2) /

          (2 * np.pi * 0.5 * 1.5))

    Z = Z2 - Z1



    X = X * 10

    Y = Y * 10

    Z = Z * 500

    return X, Y, Z





class _Quaternion:

    



    def __init__(self, scalar, vector):

        self.scalar = scalar

        self.vector = np.array(vector)



    def __neg__(self):

        return self.__class__(-self.scalar, -self.vector)



    def __mul__(self, other):

        

        return self.__class__(

            self.scalar*other.scalar - np.dot(self.vector, other.vector),

            self.scalar*other.vector + self.vector*other.scalar

            + np.cross(self.vector, other.vector))



    def conjugate(self):

        

        return self.__class__(self.scalar, -self.vector)



    @property

    def norm(self):

        

        return self.scalar*self.scalar + np.dot(self.vector, self.vector)



    def normalize(self):

        

        n = np.sqrt(self.norm)

        return self.__class__(self.scalar/n, self.vector/n)



    def reciprocal(self):

        

        n = self.norm

        return self.__class__(self.scalar/n, -self.vector/n)



    def __div__(self, other):

        return self*other.reciprocal()



    __truediv__ = __div__



    def rotate(self, v):

                                                        

                                              

        v = self.__class__(0, v)

        v = self*v/self

        return v.vector



    def __eq__(self, other):

        return (self.scalar == other.scalar) and (self.vector == other.vector).all



    def __repr__(self):

        return "_Quaternion({}, {})".format(repr(self.scalar), repr(self.vector))



    @classmethod

    def rotate_from_to(cls, r1, r2):

        

        k = np.cross(r1, r2)

        nk = np.linalg.norm(k)

        th = np.arctan2(nk, np.dot(r1, r2))

        th /= 2

        if nk == 0:                                           

            if np.dot(r1, r2) < 0:

                warnings.warn("Rotation defined by anti-parallel vectors is ambiguous")

                k = np.zeros(3)

                k[np.argmin(r1*r1)] = 1                                            

                k = np.cross(r1, k)

                k = k / np.linalg.norm(k)                               

                q = cls(0, k)

            else:

                q = cls(1, [0, 0, 0])                    

        else:

            q = cls(np.cos(th), k*np.sin(th)/nk)

        return q



    @classmethod

    def from_cardan_angles(cls, elev, azim, roll):

        

        ca, sa = np.cos(azim/2), np.sin(azim/2)

        ce, se = np.cos(elev/2), np.sin(elev/2)

        cr, sr = np.cos(roll/2), np.sin(roll/2)



        qw = ca*ce*cr + sa*se*sr

        qx = ca*ce*sr - sa*se*cr

        qy = ca*se*cr + sa*ce*sr

        qz = ca*se*sr - sa*ce*cr

        return cls(qw, [qx, qy, qz])



    def as_cardan_angles(self):

        

        qw = self.scalar

        qx, qy, qz = self.vector[..., :]

        azim = np.arctan2(2*(-qw*qz+qx*qy), qw*qw+qx*qx-qy*qy-qz*qz)

        elev = np.arcsin(np.clip(2*(qw*qy+qz*qx)/(qw*qw+qx*qx+qy*qy+qz*qz), -1, 1))

        roll = np.arctan2(2*(qw*qx-qy*qz), qw*qw-qx*qx-qy*qy+qz*qz)

        return elev, azim, roll

