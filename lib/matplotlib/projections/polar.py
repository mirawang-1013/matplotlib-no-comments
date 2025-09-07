import math

import types



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook

from matplotlib.axes import Axes

import matplotlib.axis as maxis

import matplotlib.markers as mmarkers

import matplotlib.patches as mpatches

from matplotlib.path import Path

import matplotlib.ticker as mticker

import matplotlib.transforms as mtransforms

from matplotlib.spines import Spine





class PolarTransform(mtransforms.Transform):

    



    input_dims = output_dims = 2



    def __init__(self, axis=None, use_rmin=True, *, scale_transform=None):

        

        super().__init__()

        self._axis = axis

        self._use_rmin = use_rmin

        self._scale_transform = scale_transform



    __str__ = mtransforms._make_str_method(

        "_axis",

        use_rmin="_use_rmin"

    )



    def _get_rorigin(self):

                                                                            

        return self._scale_transform.transform(

            (0, self._axis.get_rorigin()))[1]



    def transform_non_affine(self, values):

                             

        theta, r = np.transpose(values)

        if self._use_rmin and self._axis is not None:

            r = (r - self._get_rorigin()) * self._axis.get_rsign()

        r = np.where(r >= 0, r, np.nan)

        return np.column_stack([r * np.cos(theta), r * np.sin(theta)])



    def transform_path_non_affine(self, path):

                             

        if not len(path) or path._interpolation_steps == 1:

            return Path(self.transform_non_affine(path.vertices), path.codes)

        xys = []

        codes = []

        last_t = last_r = None

        for trs, c in path.iter_segments():

            trs = trs.reshape((-1, 2))

            if c == Path.LINETO:

                (t, r), = trs

                if t == last_t:                                     

                    xys.extend(self.transform_non_affine(trs))

                    codes.append(Path.LINETO)

                elif r == last_r:                             

                                                                      

                                                                            

                                         

                    last_td, td = np.rad2deg([last_t, t])

                    if self._use_rmin and self._axis is not None:

                        r = ((r - self._get_rorigin())

                             * self._axis.get_rsign())

                    if last_td <= td:

                        while td - last_td > 360:

                            arc = Path.arc(last_td, last_td + 360)

                            xys.extend(arc.vertices[1:] * r)

                            codes.extend(arc.codes[1:])

                            last_td += 360

                        arc = Path.arc(last_td, td)

                        xys.extend(arc.vertices[1:] * r)

                        codes.extend(arc.codes[1:])

                    else:

                                                                              

                                                               

                        while last_td - td > 360:

                            arc = Path.arc(last_td - 360, last_td)

                            xys.extend(arc.vertices[::-1][1:] * r)

                            codes.extend(arc.codes[1:])

                            last_td -= 360

                        arc = Path.arc(td, last_td)

                        xys.extend(arc.vertices[::-1][1:] * r)

                        codes.extend(arc.codes[1:])

                else:                

                    trs = cbook.simple_linear_interpolation(

                        np.vstack([(last_t, last_r), trs]),

                        path._interpolation_steps)[1:]

                    xys.extend(self.transform_non_affine(trs))

                    codes.extend([Path.LINETO] * len(trs))

            else:                        

                xys.extend(self.transform_non_affine(trs))

                codes.extend([c] * len(trs))

            last_t, last_r = trs[-1]

        return Path(xys, codes)



    def inverted(self):

                             

        return PolarAxes.InvertedPolarTransform(self._axis, self._use_rmin)





class PolarAffine(mtransforms.Affine2DBase):

    

    def __init__(self, scale_transform, limits):

        

        super().__init__()

        self._scale_transform = scale_transform

        self._limits = limits

        self.set_children(scale_transform, limits)

        self._mtx = None



    __str__ = mtransforms._make_str_method("_scale_transform", "_limits")



    def get_matrix(self):

                             

        if self._invalid:

            limits_scaled = self._limits.transformed(self._scale_transform)

            yscale = limits_scaled.ymax - limits_scaled.ymin

            affine = mtransforms.Affine2D()
                .scale(0.5 / yscale)
                .translate(0.5, 0.5)

            self._mtx = affine.get_matrix()

            self._inverted = None

            self._invalid = 0

        return self._mtx





class InvertedPolarTransform(mtransforms.Transform):

    

    input_dims = output_dims = 2



    def __init__(self, axis=None, use_rmin=True):

        

        super().__init__()

        self._axis = axis

        self._use_rmin = use_rmin



    __str__ = mtransforms._make_str_method(

        "_axis",

        use_rmin="_use_rmin")



    def transform_non_affine(self, values):

                             

        x, y = values.T

        r = np.hypot(x, y)

        theta = np.arctan2(y, x) % (2 * np.pi)

        if self._use_rmin and self._axis is not None:

            r += self._axis.get_rorigin()

            r *= self._axis.get_rsign()

        return np.column_stack([theta, r])



    def inverted(self):

                             

        return PolarAxes.PolarTransform(self._axis, self._use_rmin)





class ThetaFormatter(mticker.Formatter):

    



    def __call__(self, x, pos=None):

        vmin, vmax = self.axis.get_view_interval()

        d = np.rad2deg(abs(vmax - vmin))

        digits = max(-int(np.log10(d) - 1.5), 0)

        return f"{np.rad2deg(x):0.{digits}f}\N{DEGREE SIGN}"





class _AxisWrapper:

    def __init__(self, axis):

        self._axis = axis



    def get_view_interval(self):

        return np.rad2deg(self._axis.get_view_interval())



    def set_view_interval(self, vmin, vmax):

        self._axis.set_view_interval(*np.deg2rad((vmin, vmax)))



    def get_minpos(self):

        return np.rad2deg(self._axis.get_minpos())



    def get_data_interval(self):

        return np.rad2deg(self._axis.get_data_interval())



    def set_data_interval(self, vmin, vmax):

        self._axis.set_data_interval(*np.deg2rad((vmin, vmax)))



    def get_tick_space(self):

        return self._axis.get_tick_space()





class ThetaLocator(mticker.Locator):

    



    def __init__(self, base):

        self.base = base

        self.axis = self.base.axis = _AxisWrapper(self.base.axis)



    def set_axis(self, axis):

        self.axis = _AxisWrapper(axis)

        self.base.set_axis(self.axis)



    def __call__(self):

        lim = self.axis.get_view_interval()

        if _is_full_circle_deg(lim[0], lim[1]):

            return np.deg2rad(min(lim)) + np.arange(8) * 2 * np.pi / 8

        else:

            return np.deg2rad(self.base())



    def view_limits(self, vmin, vmax):

        vmin, vmax = np.rad2deg((vmin, vmax))

        return np.deg2rad(self.base.view_limits(vmin, vmax))





class ThetaTick(maxis.XTick):

    



    def __init__(self, axes, *args, **kwargs):

        self._text1_translate = mtransforms.ScaledTranslation(

            0, 0, axes.get_figure(root=False).dpi_scale_trans)

        self._text2_translate = mtransforms.ScaledTranslation(

            0, 0, axes.get_figure(root=False).dpi_scale_trans)

        super().__init__(axes, *args, **kwargs)

        self.label1.set(

            rotation_mode='anchor',

            transform=self.label1.get_transform() + self._text1_translate)

        self.label2.set(

            rotation_mode='anchor',

            transform=self.label2.get_transform() + self._text2_translate)



    def _apply_params(self, **kwargs):

        super()._apply_params(**kwargs)

                                                                 

        trans = self.label1.get_transform()

        if not trans.contains_branch(self._text1_translate):

            self.label1.set_transform(trans + self._text1_translate)

        trans = self.label2.get_transform()

        if not trans.contains_branch(self._text2_translate):

            self.label2.set_transform(trans + self._text2_translate)



    def _update_padding(self, pad, angle):

        padx = pad * np.cos(angle) / 72

        pady = pad * np.sin(angle) / 72

        self._text1_translate._t = (padx, pady)

        self._text1_translate.invalidate()

        self._text2_translate._t = (-padx, -pady)

        self._text2_translate.invalidate()



    def update_position(self, loc):

        super().update_position(loc)

        axes = self.axes

        angle = loc * axes.get_theta_direction() + axes.get_theta_offset()

        text_angle = np.rad2deg(angle) % 360 - 90

        angle -= np.pi / 2



        marker = self.tick1line.get_marker()

        if marker in (mmarkers.TICKUP, '|'):

            trans = mtransforms.Affine2D().scale(1, 1).rotate(angle)

        elif marker == mmarkers.TICKDOWN:

            trans = mtransforms.Affine2D().scale(1, -1).rotate(angle)

        else:

                                                    

            trans = self.tick1line._marker._transform

        self.tick1line._marker._transform = trans



        marker = self.tick2line.get_marker()

        if marker in (mmarkers.TICKUP, '|'):

            trans = mtransforms.Affine2D().scale(1, 1).rotate(angle)

        elif marker == mmarkers.TICKDOWN:

            trans = mtransforms.Affine2D().scale(1, -1).rotate(angle)

        else:

                                                    

            trans = self.tick2line._marker._transform

        self.tick2line._marker._transform = trans



        mode, user_angle = self._labelrotation

        if mode == 'default':

            text_angle = user_angle

        else:

            if text_angle > 90:

                text_angle -= 180

            elif text_angle < -90:

                text_angle += 180

            text_angle += user_angle

        self.label1.set_rotation(text_angle)

        self.label2.set_rotation(text_angle)



                                                                               

                                                                     

        pad = self._pad + 7

        self._update_padding(pad,

                             self._loc * axes.get_theta_direction() +

                             axes.get_theta_offset())





class ThetaAxis(maxis.XAxis):

    

    __name__ = 'thetaaxis'

    axis_name = 'theta'                                         

    _tick_class = ThetaTick



    def _wrap_locator_formatter(self):

        self.set_major_locator(ThetaLocator(self.get_major_locator()))

        self.set_major_formatter(ThetaFormatter())

        self.isDefault_majloc = True

        self.isDefault_majfmt = True



    def clear(self):

                             

        super().clear()

        self.set_ticks_position('none')

        self._wrap_locator_formatter()



    def _set_scale(self, value, **kwargs):

        if value != 'linear':

            raise NotImplementedError(

                "The xscale cannot be set on a polar plot")

        super()._set_scale(value, **kwargs)

                                                                            

                                                                             

                                       

        self.get_major_locator().set_params(steps=[1, 1.5, 3, 4.5, 9, 10])

        self._wrap_locator_formatter()



    def _copy_tick_props(self, src, dest):

        

        if src is None or dest is None:

            return

        super()._copy_tick_props(src, dest)



                                                                            

        trans = dest._get_text1_transform()[0]

        dest.label1.set_transform(trans + dest._text1_translate)

        trans = dest._get_text2_transform()[0]

        dest.label2.set_transform(trans + dest._text2_translate)





class RadialLocator(mticker.Locator):

    



    @_api.delete_parameter("3.11", "axes")

    def __init__(self, base, axes=None):

        self.base = base

        self._axes = axes



    def set_axis(self, axis):

        self.base.set_axis(axis)



    def __call__(self):

                                                                       

        ax = self.base.axis.axes

        if _is_full_circle_rad(*ax.viewLim.intervalx):

            rorigin = ax.get_rorigin() * ax.get_rsign()

            if ax.get_rmin() <= rorigin:

                return [tick for tick in self.base() if tick > rorigin]

        return self.base()



    def _zero_in_bounds(self):

        

        vmin, vmax = self.base.axis._scale.limit_range_for_scale(0, 1, 1e-5)

        return vmin == 0



    def nonsingular(self, vmin, vmax):

                             

        if self._zero_in_bounds() and (vmin, vmax) == (-np.inf, np.inf):

                                 

            return (0, 1)

        else:

            return self.base.nonsingular(vmin, vmax)



    def view_limits(self, vmin, vmax):

        vmin, vmax = self.base.view_limits(vmin, vmax)

        if self._zero_in_bounds() and vmax > vmin:

                                           

            vmin = min(0, vmin)

        return mtransforms.nonsingular(vmin, vmax)





class _ThetaShift(mtransforms.ScaledTranslation):

    

    def __init__(self, axes, pad, mode):

        super().__init__(pad, pad, axes.get_figure(root=False).dpi_scale_trans)

        self.set_children(axes._realViewLim)

        self.axes = axes

        self.mode = mode

        self.pad = pad



    __str__ = mtransforms._make_str_method("axes", "pad", "mode")



    def get_matrix(self):

        if self._invalid:

            if self.mode == 'rlabel':

                angle = (

                    np.deg2rad(self.axes.get_rlabel_position()

                               * self.axes.get_theta_direction())

                    + self.axes.get_theta_offset()

                    - np.pi / 2

                )

            elif self.mode == 'min':

                angle = self.axes._realViewLim.xmin - np.pi / 2

            elif self.mode == 'max':

                angle = self.axes._realViewLim.xmax + np.pi / 2

            self._t = (self.pad * np.cos(angle) / 72, self.pad * np.sin(angle) / 72)

        return super().get_matrix()





class RadialTick(maxis.YTick):

    



    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.label1.set_rotation_mode('anchor')

        self.label2.set_rotation_mode('anchor')



    def _determine_anchor(self, mode, angle, start):

                                                                              

                                                                               

        if mode == 'auto':

            if start:

                if -90 <= angle <= 90:

                    return 'left', 'center'

                else:

                    return 'right', 'center'

            else:

                if -90 <= angle <= 90:

                    return 'right', 'center'

                else:

                    return 'left', 'center'

        else:

            if start:

                if angle < -68.5:

                    return 'center', 'top'

                elif angle < -23.5:

                    return 'left', 'top'

                elif angle < 22.5:

                    return 'left', 'center'

                elif angle < 67.5:

                    return 'left', 'bottom'

                elif angle < 112.5:

                    return 'center', 'bottom'

                elif angle < 157.5:

                    return 'right', 'bottom'

                elif angle < 202.5:

                    return 'right', 'center'

                elif angle < 247.5:

                    return 'right', 'top'

                else:

                    return 'center', 'top'

            else:

                if angle < -68.5:

                    return 'center', 'bottom'

                elif angle < -23.5:

                    return 'right', 'bottom'

                elif angle < 22.5:

                    return 'right', 'center'

                elif angle < 67.5:

                    return 'right', 'top'

                elif angle < 112.5:

                    return 'center', 'top'

                elif angle < 157.5:

                    return 'left', 'top'

                elif angle < 202.5:

                    return 'left', 'center'

                elif angle < 247.5:

                    return 'left', 'bottom'

                else:

                    return 'center', 'bottom'



    def update_position(self, loc):

        super().update_position(loc)

        axes = self.axes

        thetamin = axes.get_thetamin()

        thetamax = axes.get_thetamax()

        direction = axes.get_theta_direction()

        offset_rad = axes.get_theta_offset()

        offset = np.rad2deg(offset_rad)

        full = _is_full_circle_deg(thetamin, thetamax)



        if full:

            angle = (axes.get_rlabel_position() * direction +

                     offset) % 360 - 90

            tick_angle = 0

        else:

            angle = (thetamin * direction + offset) % 360 - 90

            if direction > 0:

                tick_angle = np.deg2rad(angle)

            else:

                tick_angle = np.deg2rad(angle + 180)

        text_angle = (angle + 90) % 180 - 90                        

        mode, user_angle = self._labelrotation

        if mode == 'auto':

            text_angle += user_angle

        else:

            text_angle = user_angle



        if full:

            ha = self.label1.get_horizontalalignment()

            va = self.label1.get_verticalalignment()

        else:

            ha, va = self._determine_anchor(mode, angle, direction > 0)

        self.label1.set_horizontalalignment(ha)

        self.label1.set_verticalalignment(va)

        self.label1.set_rotation(text_angle)



        marker = self.tick1line.get_marker()

        if marker == mmarkers.TICKLEFT:

            trans = mtransforms.Affine2D().rotate(tick_angle)

        elif marker == '_':

            trans = mtransforms.Affine2D().rotate(tick_angle + np.pi / 2)

        elif marker == mmarkers.TICKRIGHT:

            trans = mtransforms.Affine2D().scale(-1, 1).rotate(tick_angle)

        else:

                                                    

            trans = self.tick1line._marker._transform

        self.tick1line._marker._transform = trans



        if full:

            self.label2.set_visible(False)

            self.tick2line.set_visible(False)

        angle = (thetamax * direction + offset) % 360 - 90

        if direction > 0:

            tick_angle = np.deg2rad(angle)

        else:

            tick_angle = np.deg2rad(angle + 180)

        text_angle = (angle + 90) % 180 - 90                        

        mode, user_angle = self._labelrotation

        if mode == 'auto':

            text_angle += user_angle

        else:

            text_angle = user_angle



        ha, va = self._determine_anchor(mode, angle, direction < 0)

        self.label2.set_ha(ha)

        self.label2.set_va(va)

        self.label2.set_rotation(text_angle)



        marker = self.tick2line.get_marker()

        if marker == mmarkers.TICKLEFT:

            trans = mtransforms.Affine2D().rotate(tick_angle)

        elif marker == '_':

            trans = mtransforms.Affine2D().rotate(tick_angle + np.pi / 2)

        elif marker == mmarkers.TICKRIGHT:

            trans = mtransforms.Affine2D().scale(-1, 1).rotate(tick_angle)

        else:

                                                    

            trans = self.tick2line._marker._transform

        self.tick2line._marker._transform = trans





class RadialAxis(maxis.YAxis):

    

    __name__ = 'radialaxis'

    axis_name = 'radius'                                         

    _tick_class = RadialTick



    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.sticky_edges.y.append(0)



    def set_major_locator(self, locator):

        if not isinstance(locator, RadialLocator):

            locator = RadialLocator(locator)

        super().set_major_locator(locator)



    def clear(self):

                             

        super().clear()

        self.set_ticks_position('none')





def _is_full_circle_deg(thetamin, thetamax):

    

    return abs(abs(thetamax - thetamin) - 360.0) < 1e-12





def _is_full_circle_rad(thetamin, thetamax):

    

    return abs(abs(thetamax - thetamin) - 2 * np.pi) < 1.74e-14





class _WedgeBbox(mtransforms.Bbox):

    

    def __init__(self, center, viewLim, originLim, **kwargs):

        super().__init__([[0, 0], [1, 1]], **kwargs)

        self._center = center

        self._viewLim = viewLim

        self._originLim = originLim

        self.set_children(viewLim, originLim)



    __str__ = mtransforms._make_str_method("_center", "_viewLim", "_originLim")



    def get_points(self):

                             

        if self._invalid:

            points = self._viewLim.get_points().copy()

                                                      

            points[:, 0] *= 180 / np.pi

            if points[0, 0] > points[1, 0]:

                points[:, 0] = points[::-1, 0]



                                                         

            points[:, 1] -= self._originLim.y0



                                                       

            rscale = 0.5 / points[1, 1]

            points[:, 1] *= rscale

            width = min(points[1, 1] - points[0, 1], 0.5)



                                              

            wedge = mpatches.Wedge(self._center, points[1, 1],

                                   points[0, 0], points[1, 0],

                                   width=width)

            self.update_from_path(wedge.get_path())



                                        

            w, h = self._points[1] - self._points[0]

            deltah = max(w - h, 0) / 2

            deltaw = max(h - w, 0) / 2

            self._points += np.array([[-deltaw, -deltah], [deltaw, deltah]])



            self._invalid = 0



        return self._points





class PolarAxes(Axes):

    

    name = 'polar'



    def __init__(self, *args,

                 theta_offset=0, theta_direction=1, rlabel_position=22.5,

                 **kwargs):

                             

        self._default_theta_offset = theta_offset

        self._default_theta_direction = theta_direction

        self._default_rlabel_position = np.deg2rad(rlabel_position)

        super().__init__(*args, **kwargs)

        self.use_sticky_edges = True

        self.set_aspect('equal', adjustable='box', anchor='C')

        self.clear()



    def clear(self):

                             

        super().clear()



        self.title.set_y(1.05)



        start = self.spines.get('start', None)

        if start:

            start.set_visible(False)

        end = self.spines.get('end', None)

        if end:

            end.set_visible(False)

        self.set_xlim(0.0, 2 * np.pi)



        self.grid(mpl.rcParams['polaraxes.grid'])

        inner = self.spines.get('inner', None)

        if inner:

            inner.set_visible(False)



        self.set_rorigin(None)

        self.set_theta_offset(self._default_theta_offset)

        self.set_theta_direction(self._default_theta_direction)



    def _init_axis(self):

                                                                               

        self.xaxis = ThetaAxis(self, clear=False)

        self.yaxis = RadialAxis(self, clear=False)

        self.spines['polar'].register_axis(self.yaxis)

        inner_spine = self.spines.get('inner', None)

        if inner_spine is not None:

                                                  

            inner_spine.register_axis(self.yaxis)



    def _set_lim_and_transforms(self):

                                                                         

                                        

        self._originViewLim = mtransforms.LockableBbox(self.viewLim)



                                              

        self._direction = mtransforms.Affine2D()
            .scale(self._default_theta_direction, 1.0)

        self._theta_offset = mtransforms.Affine2D()
            .translate(self._default_theta_offset, 0.0)

        self.transShift = self._direction + self._theta_offset

                                                                           

                                 

        self._realViewLim = mtransforms.TransformedBbox(self.viewLim,

                                                        self.transShift)



                                                                  

                                                                      

        self.transScale = mtransforms.TransformWrapper(

            mtransforms.IdentityTransform())



                                                                             

                                                                             

                 

        self.axesLim = _WedgeBbox((0.5, 0.5),

                                  self._realViewLim, self._originViewLim)



                                           

        self.transWedge = mtransforms.BboxTransformFrom(self.axesLim)



                                            

        self.transAxes = mtransforms.BboxTransformTo(self.bbox)



                                                                    

                                          

        self.transProjection = self.PolarTransform(

            self,

            scale_transform=self.transScale

        )

                                    

        self.transProjection.set_children(self._originViewLim)



                                                                      

                           

        self.transProjectionAffine = self.PolarAffine(self.transScale,

                                                      self._originViewLim)



                                                                     

                                    

         

                                                              

                                              

                                                            

                                                

                                                                         

                                                                     

                                            

                                                                

        self.transData = (

            self.transScale +

            self.transShift +

            self.transProjection +

            (

                self.transProjectionAffine +

                self.transWedge +

                self.transAxes

            )

        )



                                                            

                                                                              

                                          

        self._xaxis_transform = (

            mtransforms.blended_transform_factory(

                mtransforms.IdentityTransform(),

                mtransforms.BboxTransformTo(self.viewLim)) +

            self.transData)

                                                                             

                                                                      

        flipr_transform = mtransforms.Affine2D()
            .translate(0.0, -0.5)
            .scale(1.0, -1.0)
            .translate(0.0, 0.5)

        self._xaxis_text_transform = flipr_transform + self._xaxis_transform



                                                                      

                                                                        

                   

        self._yaxis_transform = (

            mtransforms.blended_transform_factory(

                mtransforms.BboxTransformTo(self.viewLim),

                mtransforms.IdentityTransform()) +

            self.transData)

                                                                             

        self._r_label_position = mtransforms.Affine2D()
            .translate(self._default_rlabel_position, 0.0)

        self._yaxis_text_transform = mtransforms.TransformWrapper(

            self._r_label_position + self.transData)



    def get_xaxis_transform(self, which='grid'):

        _api.check_in_list(['tick1', 'tick2', 'grid'], which=which)

        return self._xaxis_transform



    def get_xaxis_text1_transform(self, pad):

        return self._xaxis_text_transform, 'center', 'center'



    def get_xaxis_text2_transform(self, pad):

        return self._xaxis_text_transform, 'center', 'center'



    def get_yaxis_transform(self, which='grid'):

        if which in ('tick1', 'tick2'):

            return self._yaxis_text_transform

        elif which == 'grid':

            return self._yaxis_transform

        else:

            _api.check_in_list(['tick1', 'tick2', 'grid'], which=which)



    def get_yaxis_text1_transform(self, pad):

        thetamin, thetamax = self._realViewLim.intervalx

        if _is_full_circle_rad(thetamin, thetamax):

            return self._yaxis_text_transform, 'bottom', 'left'

        elif self.get_theta_direction() > 0:

            halign = 'left'

            pad_shift = _ThetaShift(self, pad, 'min')

        else:

            halign = 'right'

            pad_shift = _ThetaShift(self, pad, 'max')

        return self._yaxis_text_transform + pad_shift, 'center', halign



    def get_yaxis_text2_transform(self, pad):

        if self.get_theta_direction() > 0:

            halign = 'right'

            pad_shift = _ThetaShift(self, pad, 'max')

        else:

            halign = 'left'

            pad_shift = _ThetaShift(self, pad, 'min')

        return self._yaxis_text_transform + pad_shift, 'center', halign



    def draw(self, renderer):

        self._unstale_viewLim()

        thetamin, thetamax = np.rad2deg(self._realViewLim.intervalx)

        if thetamin > thetamax:

            thetamin, thetamax = thetamax, thetamin

        rscale_tr = self.yaxis.get_transform()

        rmin, rmax = ((rscale_tr.transform(self._realViewLim.intervaly) -

                       rscale_tr.transform(self.get_rorigin())) *

                      self.get_rsign())

        if isinstance(self.patch, mpatches.Wedge):

                                                                             

                                                            

            center = self.transWedge.transform((0.5, 0.5))

            self.patch.set_center(center)

            self.patch.set_theta1(thetamin)

            self.patch.set_theta2(thetamax)



            edge, _ = self.transWedge.transform((1, 0))

            radius = edge - center[0]

            width = min(radius * (rmax - rmin) / rmax, radius)

            self.patch.set_radius(radius)

            self.patch.set_width(width)



            inner_width = radius - width

            inner = self.spines.get('inner', None)

            if inner:

                inner.set_visible(inner_width != 0.0)



        visible = not _is_full_circle_deg(thetamin, thetamax)

                                                                             

                                                              

        start = self.spines.get('start', None)

        end = self.spines.get('end', None)

        if start:

            start.set_visible(visible)

        if end:

            end.set_visible(visible)

        if visible:

            yaxis_text_transform = self._yaxis_transform

        else:

            yaxis_text_transform = self._r_label_position + self.transData

        if self._yaxis_text_transform != yaxis_text_transform:

            self._yaxis_text_transform.set(yaxis_text_transform)

            self.yaxis.reset_ticks()

            self.yaxis.set_clip_path(self.patch)



        super().draw(renderer)



    def _gen_axes_patch(self):

        return mpatches.Wedge((0.5, 0.5), 0.5, 0.0, 360.0)



    def _gen_axes_spines(self):

        spines = {

            'polar': Spine.arc_spine(self, 'top', (0.5, 0.5), 0.5, 0, 360),

            'start': Spine.linear_spine(self, 'left'),

            'end': Spine.linear_spine(self, 'right'),

            'inner': Spine.arc_spine(self, 'bottom', (0.5, 0.5), 0.0, 0, 360),

        }

        spines['polar'].set_transform(self.transWedge + self.transAxes)

        spines['inner'].set_transform(self.transWedge + self.transAxes)

        spines['start'].set_transform(self._yaxis_transform)

        spines['end'].set_transform(self._yaxis_transform)

        return spines



    def set_thetamax(self, thetamax):

        

        self.viewLim.x1 = np.deg2rad(thetamax)



    def get_thetamax(self):

        

        return np.rad2deg(self.viewLim.xmax)



    def set_thetamin(self, thetamin):

        

        self.viewLim.x0 = np.deg2rad(thetamin)



    def get_thetamin(self):

        

        return np.rad2deg(self.viewLim.xmin)



    def set_thetalim(self, *args, **kwargs):

        

        orig_lim = self.get_xlim()              

        if 'thetamin' in kwargs:

            kwargs['xmin'] = np.deg2rad(kwargs.pop('thetamin'))

        if 'thetamax' in kwargs:

            kwargs['xmax'] = np.deg2rad(kwargs.pop('thetamax'))

        new_min, new_max = self.set_xlim(*args, **kwargs)

                                                                              

                                                               

        if abs(new_max - new_min) > 2 * np.pi:

            self.set_xlim(orig_lim)                        

            raise ValueError("The angle range must be less than a full circle")

        return tuple(np.rad2deg((new_min, new_max)))



    def set_theta_offset(self, offset):

        

        mtx = self._theta_offset.get_matrix()

        mtx[0, 2] = offset

        self._theta_offset.invalidate()



    def get_theta_offset(self):

        

        return self._theta_offset.get_matrix()[0, 2]



    def set_theta_zero_location(self, loc, offset=0.0):

        

        mapping = {

            'N': np.pi * 0.5,

            'NW': np.pi * 0.75,

            'W': np.pi,

            'SW': np.pi * 1.25,

            'S': np.pi * 1.5,

            'SE': np.pi * 1.75,

            'E': 0,

            'NE': np.pi * 0.25}

        return self.set_theta_offset(mapping[loc] + np.deg2rad(offset))



    def set_theta_direction(self, direction):

        

        mtx = self._direction.get_matrix()

        if direction in ('clockwise', -1):

            mtx[0, 0] = -1

        elif direction in ('counterclockwise', 'anticlockwise', 1):

            mtx[0, 0] = 1

        else:

            _api.check_in_list(

                [-1, 1, 'clockwise', 'counterclockwise', 'anticlockwise'],

                direction=direction)

        self._direction.invalidate()



    def get_theta_direction(self):

        

        return self._direction.get_matrix()[0, 0]



    def set_rmax(self, rmax):

        

        self.viewLim.y1 = rmax



    def get_rmax(self):

        

        return self.viewLim.ymax



    def set_rmin(self, rmin):

        

        self.viewLim.y0 = rmin



    def get_rmin(self):

        

        return self.viewLim.ymin



    def set_rorigin(self, rorigin):

        

        self._originViewLim.locked_y0 = rorigin



    def get_rorigin(self):

        

        return self._originViewLim.y0



    def get_rsign(self):

        return np.sign(self._originViewLim.y1 - self._originViewLim.y0)



    def set_rlim(self, bottom=None, top=None, *,

                 emit=True, auto=False, **kwargs):

        

        if 'rmin' in kwargs:

            if bottom is None:

                bottom = kwargs.pop('rmin')

            else:

                raise ValueError('Cannot supply both positional "bottom"'

                                 'argument and kwarg "rmin"')

        if 'rmax' in kwargs:

            if top is None:

                top = kwargs.pop('rmax')

            else:

                raise ValueError('Cannot supply both positional "top"'

                                 'argument and kwarg "rmax"')

        return self.set_ylim(bottom=bottom, top=top, emit=emit, auto=auto,

                             **kwargs)



    def get_rlabel_position(self):

        

        return np.rad2deg(self._r_label_position.get_matrix()[0, 2])



    def set_rlabel_position(self, value):

        

        self._r_label_position.clear().translate(np.deg2rad(value), 0.0)



    def set_rscale(self, *args, **kwargs):

        return Axes.set_yscale(self, *args, **kwargs)



    def set_rticks(self, *args, **kwargs):

        return Axes.set_yticks(self, *args, **kwargs)



    def set_thetagrids(self, angles, labels=None, fmt=None, **kwargs):

        



                                                      

        angles = self.convert_yunits(angles)

        angles = np.deg2rad(angles)

        self.set_xticks(angles)

        if labels is not None:

            self.set_xticklabels(labels)

        elif fmt is not None:

            self.xaxis.set_major_formatter(mticker.FormatStrFormatter(fmt))

        for t in self.xaxis.get_ticklabels():

            t._internal_update(kwargs)

        return self.xaxis.get_ticklines(), self.xaxis.get_ticklabels()



    def set_rgrids(self, radii, labels=None, angle=None, fmt=None, **kwargs):

        

                                                      

        radii = self.convert_xunits(radii)

        radii = np.asarray(radii)



        self.set_yticks(radii)

        if labels is not None:

            self.set_yticklabels(labels)

        elif fmt is not None:

            self.yaxis.set_major_formatter(mticker.FormatStrFormatter(fmt))

        if angle is None:

            angle = self.get_rlabel_position()

        self.set_rlabel_position(angle)

        for t in self.yaxis.get_ticklabels():

            t._internal_update(kwargs)

        return self.yaxis.get_gridlines(), self.yaxis.get_ticklabels()



    def format_coord(self, theta, r):

                             

        screen_xy = self.transData.transform((theta, r))

        screen_xys = screen_xy + np.stack(

            np.meshgrid([-1, 0, 1], [-1, 0, 1])).reshape((2, -1)).T

        ts, rs = self.transData.inverted().transform(screen_xys).T

        delta_t = abs((ts - theta + np.pi) % (2 * np.pi) - np.pi).max()

        delta_t_halfturns = delta_t / np.pi

        delta_t_degrees = delta_t_halfturns * 180

        delta_r = abs(rs - r).max()

        if theta < 0:

            theta += 2 * np.pi

        theta_halfturns = theta / np.pi

        theta_degrees = theta_halfturns * 180



                                                                          

                                                                             

                                                                   

        def format_sig(value, delta, opt, fmt):

                                                             

            prec = (max(0, -math.floor(math.log10(delta))) if fmt == "f" else

                    cbook._g_sig_digits(value, delta))

            return f"{value:-{opt}.{prec}{fmt}}"



                                                                



        if self.fmt_ydata is None:

            r_label = format_sig(r, delta_r, "#", "g")

        else:

            r_label = self.format_ydata(r)



        if self.fmt_xdata is None:

            return ('\N{GREEK SMALL LETTER THETA}={}\N{GREEK SMALL LETTER PI} '

                    '({}\N{DEGREE SIGN}), r={}').format(

                    format_sig(theta_halfturns, delta_t_halfturns, "", "f"),

                    format_sig(theta_degrees, delta_t_degrees, "", "f"),

                    r_label

                )

        else:

            return '\N{GREEK SMALL LETTER THETA}={}, r={}'.format(

                        self.format_xdata(theta),

                        r_label

                        )



    def get_data_ratio(self):

        

        return 1.0



                             



    def can_zoom(self):

        

        return False



    def can_pan(self):

        

        return True



    def start_pan(self, x, y, button):

        angle = np.deg2rad(self.get_rlabel_position())

        mode = ''

        if button == 1:

            epsilon = np.pi / 45.0

            t, r = self.transData.inverted().transform((x, y))

            if angle - epsilon <= t <= angle + epsilon:

                mode = 'drag_r_labels'

        elif button == 3:

            mode = 'zoom'



        self._pan_start = types.SimpleNamespace(

            rmax=self.get_rmax(),

            trans=self.transData.frozen(),

            trans_inverse=self.transData.inverted().frozen(),

            r_label_angle=self.get_rlabel_position(),

            x=x,

            y=y,

            mode=mode)



    def end_pan(self):

        del self._pan_start



    def drag_pan(self, button, key, x, y):

        p = self._pan_start



        if p.mode == 'drag_r_labels':

            (startt, startr), (t, r) = p.trans_inverse.transform(

                [(p.x, p.y), (x, y)])



                             

            dt = np.rad2deg(startt - t)

            self.set_rlabel_position(p.r_label_angle - dt)



            trans, vert1, horiz1 = self.get_yaxis_text1_transform(0.0)

            trans, vert2, horiz2 = self.get_yaxis_text2_transform(0.0)

            for t in self.yaxis.majorTicks + self.yaxis.minorTicks:

                t.label1.set_va(vert1)

                t.label1.set_ha(horiz1)

                t.label2.set_va(vert2)

                t.label2.set_ha(horiz2)



        elif p.mode == 'zoom':

            (startt, startr), (t, r) = p.trans_inverse.transform(

                [(p.x, p.y), (x, y)])



                         

            scale = r / startr

            self.set_rmax(p.rmax / scale)





                                                                            

                                                                        

                                                                       

                                                                             

                                                                               

                                                  

PolarAxes.PolarTransform = PolarTransform

PolarAxes.PolarAffine = PolarAffine

PolarAxes.InvertedPolarTransform = InvertedPolarTransform

PolarAxes.ThetaFormatter = ThetaFormatter

PolarAxes.RadialLocator = RadialLocator

PolarAxes.ThetaLocator = ThetaLocator

