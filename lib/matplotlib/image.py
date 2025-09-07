



import math

import os

import logging

from pathlib import Path

import warnings



import numpy as np

import PIL.Image

import PIL.PngImagePlugin



import matplotlib as mpl

from matplotlib import _api, cbook

                                                                    

from matplotlib import _image

                                                                    

                     

from matplotlib._image import *                    

import matplotlib.artist as martist

import matplotlib.colorizer as mcolorizer

from matplotlib.backend_bases import FigureCanvasBase

import matplotlib.colors as mcolors

from matplotlib.transforms import (

    Affine2D, BboxBase, Bbox, BboxTransform, BboxTransformTo,

    IdentityTransform, TransformedBbox)



_log = logging.getLogger(__name__)



                                               

_interpd_ = {

    'auto': _image.NEAREST,                                       

    'none': _image.NEAREST,                                           

    'nearest': _image.NEAREST,

    'bilinear': _image.BILINEAR,

    'bicubic': _image.BICUBIC,

    'spline16': _image.SPLINE16,

    'spline36': _image.SPLINE36,

    'hanning': _image.HANNING,

    'hamming': _image.HAMMING,

    'hermite': _image.HERMITE,

    'kaiser': _image.KAISER,

    'quadric': _image.QUADRIC,

    'catrom': _image.CATROM,

    'gaussian': _image.GAUSSIAN,

    'bessel': _image.BESSEL,

    'mitchell': _image.MITCHELL,

    'sinc': _image.SINC,

    'lanczos': _image.LANCZOS,

    'blackman': _image.BLACKMAN,

    'antialiased': _image.NEAREST,                                       

}



interpolations_names = set(_interpd_)





def composite_images(images, renderer, magnification=1.0):

    

    if len(images) == 0:

        return np.empty((0, 0, 4), dtype=np.uint8), 0, 0



    parts = []

    bboxes = []

    for image in images:

        data, x, y, trans = image.make_image(renderer, magnification)

        if data is not None:

            x *= magnification

            y *= magnification

            parts.append((data, x, y, image._get_scalar_alpha()))

            bboxes.append(

                Bbox([[x, y], [x + data.shape[1], y + data.shape[0]]]))



    if len(parts) == 0:

        return np.empty((0, 0, 4), dtype=np.uint8), 0, 0



    bbox = Bbox.union(bboxes)



    output = np.zeros(

        (int(bbox.height), int(bbox.width), 4), dtype=np.uint8)



    for data, x, y, alpha in parts:

        trans = Affine2D().translate(x - bbox.x0, y - bbox.y0)

        _image.resample(data, output, trans, _image.NEAREST,

                        resample=False, alpha=alpha)



    return output, bbox.x0 / magnification, bbox.y0 / magnification





def _draw_list_compositing_images(

        renderer, parent, artists, suppress_composite=None):

    

    has_images = any(isinstance(x, _ImageBase) for x in artists)



                                                                    

    not_composite = (suppress_composite if suppress_composite is not None

                     else renderer.option_image_nocomposite())



    if not_composite or not has_images:

        for a in artists:

            a.draw(renderer)

    else:

                                                

        image_group = []

        mag = renderer.get_image_magnification()



        def flush_images():

            if len(image_group) == 1:

                image_group[0].draw(renderer)

            elif len(image_group) > 1:

                data, l, b = composite_images(image_group, renderer, mag)

                if data.size != 0:

                    gc = renderer.new_gc()

                    gc.set_clip_rectangle(parent.bbox)

                    gc.set_clip_path(parent.get_clip_path())

                    renderer.draw_image(gc, round(l), round(b), data)

                    gc.restore()

            del image_group[:]



        for a in artists:

            if (isinstance(a, _ImageBase) and a.can_composite() and

                    a.get_clip_on() and not a.get_clip_path()):

                image_group.append(a)

            else:

                flush_images()

                a.draw(renderer)

        flush_images()





def _resample(

        image_obj, data, out_shape, transform, *, resample=None, alpha=1):

    

                                                                          

                                                                          

             

    msg = ('Data with more than {n} cannot be accurately displayed. '

           'Downsampling to less than {n} before displaying. '

           'To remove this warning, manually downsample your data.')

    if data.shape[1] > 2**23:

        warnings.warn(msg.format(n='2**23 columns'))

        step = int(np.ceil(data.shape[1] / 2**23))

        data = data[:, ::step]

        transform = Affine2D().scale(step, 1) + transform

    if data.shape[0] > 2**24:

        warnings.warn(msg.format(n='2**24 rows'))

        step = int(np.ceil(data.shape[0] / 2**24))

        data = data[::step, :]

        transform = Affine2D().scale(1, step) + transform

                                                                        

                                                             

                      

    interpolation = image_obj.get_interpolation()

    if interpolation in ['antialiased', 'auto']:

                                                               

                                               

        pos = np.array([[0, 0], [data.shape[1], data.shape[0]]])

        disp = transform.transform(pos)

        dispx = np.abs(np.diff(disp[:, 0]))

        dispy = np.abs(np.diff(disp[:, 1]))

        if ((dispx > 3 * data.shape[1] or

                dispx == data.shape[1] or

                dispx == 2 * data.shape[1]) and

            (dispy > 3 * data.shape[0] or

                dispy == data.shape[0] or

                dispy == 2 * data.shape[0])):

            interpolation = 'nearest'

        else:

            interpolation = 'hanning'

    out = np.zeros(out_shape + data.shape[2:], data.dtype)                   

    if resample is None:

        resample = image_obj.get_resample()

    _image.resample(data, out, transform,

                    _interpd_[interpolation],

                    resample,

                    alpha,

                    image_obj.get_filternorm(),

                    image_obj.get_filterrad())

    return out





def _rgb_to_rgba(A):

    

    rgba = np.zeros((A.shape[0], A.shape[1], 4), dtype=A.dtype)

    rgba[:, :, :3] = A

    if rgba.dtype == np.uint8:

        rgba[:, :, 3] = 255

    else:

        rgba[:, :, 3] = 1.0

    return rgba





class _ImageBase(mcolorizer.ColorizingArtist):

    



    zorder = 0



    def __init__(self, ax,

                 cmap=None,

                 norm=None,

                 colorizer=None,

                 interpolation=None,

                 origin=None,

                 filternorm=True,

                 filterrad=4.0,

                 resample=False,

                 *,

                 interpolation_stage=None,

                 **kwargs

                 ):

        super().__init__(self._get_colorizer(cmap, norm, colorizer))

        origin = mpl._val_or_rc(origin, 'image.origin')

        _api.check_in_list(["upper", "lower"], origin=origin)

        self.origin = origin

        self.set_filternorm(filternorm)

        self.set_filterrad(filterrad)

        self.set_interpolation(interpolation)

        self.set_interpolation_stage(interpolation_stage)

        self.set_resample(resample)

        self.axes = ax



        self._imcache = None



        self._internal_update(kwargs)



    def __str__(self):

        try:

            shape = self.get_shape()

            return f"{type(self).__name__}(shape={shape!r})"

        except RuntimeError:

            return type(self).__name__



    def __getstate__(self):

                                                                

        return {**super().__getstate__(), "_imcache": None}



    def get_size(self):

        

        return self.get_shape()[:2]



    def get_shape(self):

        

        if self._A is None:

            raise RuntimeError('You must first set the image array')



        return self._A.shape



    def set_alpha(self, alpha):

        

        martist.Artist._set_alpha_for_array(self, alpha)

        if np.ndim(alpha) not in (0, 2):

            raise TypeError('alpha must be a float, two-dimensional '

                            'array, or None')

        self._imcache = None



    def _get_scalar_alpha(self):

        

        return 1.0 if self._alpha is None or np.ndim(self._alpha) > 0
            else self._alpha



    def changed(self):

        

        self._imcache = None

        super().changed()



    def _make_image(self, A, in_bbox, out_bbox, clip_bbox, magnification=1.0,

                    unsampled=False, round_to_pixel_border=True):

        

        if A is None:

            raise RuntimeError('You must first set the image '

                               'array or the image attribute')

        if A.size == 0:

            raise RuntimeError("_make_image must get a non-empty image. "

                               "Your Artist's draw method must filter before "

                               "this method is called.")



        clipped_bbox = Bbox.intersection(out_bbox, clip_bbox)



        if clipped_bbox is None:

            return None, 0, 0, None



        out_width_base = clipped_bbox.width * magnification

        out_height_base = clipped_bbox.height * magnification



        if out_width_base == 0 or out_height_base == 0:

            return None, 0, 0, None



        if self.origin == 'upper':

                                                                      

                                                                      

                                                                 

            t0 = Affine2D().translate(0, -A.shape[0]).scale(1, -1)

        else:

            t0 = IdentityTransform()



        t0 += (

            Affine2D()

            .scale(

                in_bbox.width / A.shape[1],

                in_bbox.height / A.shape[0])

            .translate(in_bbox.x0, in_bbox.y0)

            + self.get_transform())



        t = (t0

             + (Affine2D()

                .translate(-clipped_bbox.x0, -clipped_bbox.y0)

                .scale(magnification)))



                                                                            

                                                                         

                                                                           

        if ((not unsampled) and t.is_affine and round_to_pixel_border and

                (out_width_base % 1.0 != 0.0 or out_height_base % 1.0 != 0.0)):

            out_width = math.ceil(out_width_base)

            out_height = math.ceil(out_height_base)

            extra_width = (out_width - out_width_base) / out_width_base

            extra_height = (out_height - out_height_base) / out_height_base

            t += Affine2D().scale(1.0 + extra_width, 1.0 + extra_height)

        else:

            out_width = int(out_width_base)

            out_height = int(out_height_base)

        out_shape = (out_height, out_width)



        if not unsampled:

            if not (A.ndim == 2 or A.ndim == 3 and A.shape[-1] in (3, 4)):

                raise ValueError(f"Invalid shape {A.shape} for image data")



            float_rgba_in = A.ndim == 3 and A.shape[-1] == 4 and A.dtype.kind == 'f'



                                                                  

                     

            interpolation_stage = self._interpolation_stage

            if interpolation_stage in ['antialiased', 'auto']:

                pos = np.array([[0, 0], [A.shape[1], A.shape[0]]])

                disp = t.transform(pos)

                dispx = np.abs(np.diff(disp[:, 0])) / A.shape[1]

                dispy = np.abs(np.diff(disp[:, 1])) / A.shape[0]

                if (dispx < 3) or (dispy < 3):

                    interpolation_stage = 'rgba'

                else:

                    interpolation_stage = 'data'



            if A.ndim == 2 and interpolation_stage == 'data':

                                                                       

                                                                          

                                                                               

                                                                  



                if A.dtype.kind == 'f':                                     

                    scaled_dtype = np.dtype("f8" if A.dtype.itemsize > 4 else "f4")

                    if scaled_dtype.itemsize < A.dtype.itemsize:

                        _api.warn_external(f"Casting input data from {A.dtype}"

                                           f" to {scaled_dtype} for imshow.")

                else:                      

                                                  

                                                                            

                                                                            

                    da = A.max().astype("f8") - A.min().astype("f8")

                    scaled_dtype = "f8" if da > 1e8 else "f4"



                                                                             

                A_resampled = _resample(self, A.astype(scaled_dtype), out_shape, t)



                                                                     

                if isinstance(self.norm, mcolors.NoNorm):

                    A_resampled = A_resampled.astype(A.dtype)



                                                                         

                                                                         

                                                                             

                                                                             

                mask = (np.where(A.mask, np.float32(np.nan), np.float32(1))

                        if A.mask.shape == A.shape                   

                        else np.ones_like(A, np.float32))

                                                                       

                                            

                out_alpha = _resample(self, mask, out_shape, t, resample=True)

                del mask                                        

                out_mask = np.isnan(out_alpha)

                out_alpha[out_mask] = 1

                                                                  

                alpha = self.get_alpha()

                if alpha is not None and np.ndim(alpha) > 0:

                    out_alpha *= _resample(self, alpha, out_shape, t, resample=True)

                                               

                resampled_masked = np.ma.masked_array(A_resampled, out_mask)

                res = self.norm(resampled_masked)

            else:

                if A.ndim == 2:                                

                    self.norm.autoscale_None(A)

                    A = self.to_rgba(A)

                if A.dtype == np.uint8:

                                                                                

                    A = np.divide(A, 0xff, dtype=np.float32)

                alpha = self.get_alpha()

                post_apply_alpha = False

                if alpha is None:                                 

                    if A.shape[2] == 3:                              

                        A = np.dstack([A, np.ones(A.shape[:2])])

                elif np.ndim(alpha) > 0:               

                                                                                     

                    A = np.dstack([A[..., :3], alpha])

                else:                

                    if A.shape[2] == 3:                          

                        A = np.dstack([A, np.full(A.shape[:2], alpha, np.float32)])

                    else:                                                   

                        post_apply_alpha = True

                                                                         

                                                                

                                                             

                if float_rgba_in and np.ndim(alpha) == 0 and np.any(A[..., 3] < 1):

                                                       

                    A = A.copy()

                A[..., :3] *= A[..., 3:]

                res = _resample(self, A, out_shape, t)

                np.divide(res[..., :3], res[..., 3:], out=res[..., :3],

                            where=res[..., 3:] != 0)

                if post_apply_alpha:

                    res[..., 3] *= alpha



                                                                        

                                                  

            output = self.to_rgba(res, bytes=True, norm=False)

                                                                 



                                                                           

            if A.ndim == 2:

                alpha = self._get_scalar_alpha()

                alpha_channel = output[:, :, 3]

                alpha_channel[:] = (                                  

                    alpha_channel.astype(np.float32) * out_alpha * alpha)



        else:

            if self._imcache is None:

                self._imcache = self.to_rgba(A, bytes=True, norm=(A.ndim == 2))

            output = self._imcache



                                                                             

            subset = TransformedBbox(clip_bbox, t0.inverted()).frozen()

            output = output[

                int(max(subset.ymin, 0)):

                int(min(subset.ymax + 1, output.shape[0])),

                int(max(subset.xmin, 0)):

                int(min(subset.xmax + 1, output.shape[1]))]



            t = Affine2D().translate(

                int(max(subset.xmin, 0)), int(max(subset.ymin, 0))) + t



        return output, clipped_bbox.x0, clipped_bbox.y0, t



    def make_image(self, renderer, magnification=1.0, unsampled=False):

        

        raise NotImplementedError('The make_image method must be overridden')



    def _check_unsampled_image(self):

        

        return False



    @martist.allow_rasterization

    def draw(self, renderer):

                                                    

        if not self.get_visible():

            self.stale = False

            return

                                                     

        if self.get_array().size == 0:

            self.stale = False

            return

                                    

        gc = renderer.new_gc()

        self._set_gc_clip(gc)

        gc.set_alpha(self._get_scalar_alpha())

        gc.set_url(self.get_url())

        gc.set_gid(self.get_gid())

        if (renderer.option_scale_image()                                      

                and self._check_unsampled_image()

                and self.get_transform().is_affine):

            im, l, b, trans = self.make_image(renderer, unsampled=True)

            if im is not None:

                trans = Affine2D().scale(im.shape[1], im.shape[0]) + trans

                renderer.draw_image(gc, l, b, im, trans)

        else:

            im, l, b, trans = self.make_image(

                renderer, renderer.get_image_magnification())

            if im is not None:

                renderer.draw_image(gc, l, b, im)

        gc.restore()

        self.stale = False



    def contains(self, mouseevent):

        

        if (self._different_canvas(mouseevent)

                                                 

                or not self.axes.contains(mouseevent)[0]):

            return False, {}

                                                                 

                                                          

                                                               

                                                              

        trans = self.get_transform().inverted()

        x, y = trans.transform([mouseevent.x, mouseevent.y])

        xmin, xmax, ymin, ymax = self.get_extent()

                                                               

        inside = (x is not None and (x - xmin) * (x - xmax) <= 0

                  and y is not None and (y - ymin) * (y - ymax) <= 0)

        return inside, {}



    def write_png(self, fname):

        

        im = self.to_rgba(self._A[::-1] if self.origin == 'lower' else self._A,

                          bytes=True, norm=True)

        PIL.Image.fromarray(im).save(fname, format="png")



    @staticmethod

    def _normalize_image_array(A):

        

        A = cbook.safe_masked_invalid(A, copy=True)

        if A.dtype != np.uint8 and not np.can_cast(A.dtype, float, "same_kind"):

            raise TypeError(f"Image data of dtype {A.dtype} cannot be "

                            f"converted to float")

        if A.ndim == 3 and A.shape[-1] == 1:

            A = A.squeeze(-1)                                                        

        if not (A.ndim == 2 or A.ndim == 3 and A.shape[-1] in [3, 4]):

            raise TypeError(f"Invalid shape {A.shape} for image data")

        if A.ndim == 3:

                                                                         

                                                                              

                                                                           

                                                        

            high = 255 if np.issubdtype(A.dtype, np.integer) else 1

            if A.min() < 0 or high < A.max():

                _log.warning(

                    'Clipping input data to the valid range for imshow with '

                    'RGB data ([0..1] for floats or [0..255] for integers). '

                    'Got range [%s..%s].',

                    A.min(), A.max()

                )

                A = np.clip(A, 0, high)

                                                     

            if A.dtype != np.uint8 and np.issubdtype(A.dtype, np.integer):

                A = A.astype(np.uint8)

        return A



    def set_data(self, A):

        

        if isinstance(A, PIL.Image.Image):

            A = pil_to_array(A)                                     

        self._A = self._normalize_image_array(A)

        self._imcache = None

        self.stale = True



    def set_array(self, A):

        

                                                              

                                                                             

        self.set_data(A)



    def get_interpolation(self):

        

        return self._interpolation



    def set_interpolation(self, s):

        

        s = mpl._val_or_rc(s, 'image.interpolation').lower()

        _api.check_in_list(interpolations_names, interpolation=s)

        self._interpolation = s

        self.stale = True



    def get_interpolation_stage(self):

        

        return self._interpolation_stage



    def set_interpolation_stage(self, s):

        

        s = mpl._val_or_rc(s, 'image.interpolation_stage')

        _api.check_in_list(['data', 'rgba', 'auto'], s=s)

        self._interpolation_stage = s

        self.stale = True



    def can_composite(self):

        

        trans = self.get_transform()

        return (

            self._interpolation != 'none' and

            trans.is_affine and

            trans.is_separable)



    def set_resample(self, v):

        

        v = mpl._val_or_rc(v, 'image.resample')

        self._resample = v

        self.stale = True



    def get_resample(self):

        

        return self._resample



    def set_filternorm(self, filternorm):

        

        self._filternorm = bool(filternorm)

        self.stale = True



    def get_filternorm(self):

        

        return self._filternorm



    def set_filterrad(self, filterrad):

        

        r = float(filterrad)

        if r <= 0:

            raise ValueError("The filter radius must be a positive number")

        self._filterrad = r

        self.stale = True



    def get_filterrad(self):

        

        return self._filterrad





class AxesImage(_ImageBase):

    



    def __init__(self, ax,

                 *,

                 cmap=None,

                 norm=None,

                 colorizer=None,

                 interpolation=None,

                 origin=None,

                 extent=None,

                 filternorm=True,

                 filterrad=4.0,

                 resample=False,

                 interpolation_stage=None,

                 **kwargs

                 ):



        self._extent = extent



        super().__init__(

            ax,

            cmap=cmap,

            norm=norm,

            colorizer=colorizer,

            interpolation=interpolation,

            origin=origin,

            filternorm=filternorm,

            filterrad=filterrad,

            resample=resample,

            interpolation_stage=interpolation_stage,

            **kwargs

        )



    def get_window_extent(self, renderer=None):

        x0, x1, y0, y1 = self._extent

        bbox = Bbox.from_extents([x0, y0, x1, y1])

        return bbox.transformed(self.get_transform())



    def make_image(self, renderer, magnification=1.0, unsampled=False):

                             

        trans = self.get_transform()

                                                    

        x1, x2, y1, y2 = self.get_extent()

        bbox = Bbox(np.array([[x1, y1], [x2, y2]]))

        transformed_bbox = TransformedBbox(bbox, trans)

        clip = ((self.get_clip_box() or self.axes.bbox) if self.get_clip_on()

                else self.get_figure(root=True).bbox)

        return self._make_image(self._A, bbox, transformed_bbox, clip,

                                magnification, unsampled=unsampled)



    def _check_unsampled_image(self):

        

        return self.get_interpolation() == "none"



    def set_extent(self, extent, **kwargs):

        

        (xmin, xmax), (ymin, ymax) = self.axes._process_unit_info(

            [("x", [extent[0], extent[1]]),

             ("y", [extent[2], extent[3]])],

            kwargs)

        if kwargs:

            raise _api.kwarg_error("set_extent", kwargs)

        xmin = self.axes._validate_converted_limits(

            xmin, self.convert_xunits)

        xmax = self.axes._validate_converted_limits(

            xmax, self.convert_xunits)

        ymin = self.axes._validate_converted_limits(

            ymin, self.convert_yunits)

        ymax = self.axes._validate_converted_limits(

            ymax, self.convert_yunits)

        extent = [xmin, xmax, ymin, ymax]



        self._extent = extent

        corners = (xmin, ymin), (xmax, ymax)

        self.axes.update_datalim(corners)

        self.sticky_edges.x[:] = [xmin, xmax]

        self.sticky_edges.y[:] = [ymin, ymax]

        if self.axes.get_autoscalex_on():

            self.axes.set_xlim(xmin, xmax, auto=None)

        if self.axes.get_autoscaley_on():

            self.axes.set_ylim(ymin, ymax, auto=None)

        self.stale = True



    def get_extent(self):

        

        if self._extent is not None:

            return self._extent

        else:

            sz = self.get_size()

            numrows, numcols = sz

            if self.origin == 'upper':

                return (-0.5, numcols-0.5, numrows-0.5, -0.5)

            else:

                return (-0.5, numcols-0.5, -0.5, numrows-0.5)



    def get_cursor_data(self, event):

        

        xmin, xmax, ymin, ymax = self.get_extent()

        if self.origin == 'upper':

            ymin, ymax = ymax, ymin

        arr = self.get_array()

        data_extent = Bbox([[xmin, ymin], [xmax, ymax]])

        array_extent = Bbox([[0, 0], [arr.shape[1], arr.shape[0]]])

        trans = self.get_transform().inverted()

        trans += BboxTransform(boxin=data_extent, boxout=array_extent)

        point = trans.transform([event.x, event.y])

        if any(np.isnan(point)):

            return None

        j, i = point.astype(int)

                                              

        if not (0 <= i < arr.shape[0]) or not (0 <= j < arr.shape[1]):

            return None

        else:

            return arr[i, j]





class NonUniformImage(AxesImage):

    



    def __init__(self, ax, *, interpolation='nearest', **kwargs):

        

        super().__init__(ax, **kwargs)

        self.set_interpolation(interpolation)



    def _check_unsampled_image(self):

        

        return False



    def make_image(self, renderer, magnification=1.0, unsampled=False):

                             

        if self._A is None:

            raise RuntimeError('You must first set the image array')

        if unsampled:

            raise ValueError('unsampled not supported on NonUniformImage')

        A = self._A

        if A.ndim == 2:

            if A.dtype != np.uint8:

                A = self.to_rgba(A, bytes=True)

            else:

                A = np.repeat(A[:, :, np.newaxis], 4, 2)

                A[:, :, 3] = 255

        else:

            if A.dtype != np.uint8:

                A = (255*A).astype(np.uint8)

            if A.shape[2] == 3:

                B = np.zeros(tuple([*A.shape[0:2], 4]), np.uint8)

                B[:, :, 0:3] = A

                B[:, :, 3] = 255

                A = B

        l, b, r, t = self.axes.bbox.extents

        width = int(((round(r) + 0.5) - (round(l) - 0.5)) * magnification)

        height = int(((round(t) + 0.5) - (round(b) - 0.5)) * magnification)



        invertedTransform = self.axes.transData.inverted()

        x_pix = invertedTransform.transform(

            [(x, b) for x in np.linspace(l, r, width)])[:, 0]

        y_pix = invertedTransform.transform(

            [(l, y) for y in np.linspace(b, t, height)])[:, 1]



        if self._interpolation == "nearest":

            x_mid = (self._Ax[:-1] + self._Ax[1:]) / 2

            y_mid = (self._Ay[:-1] + self._Ay[1:]) / 2

            x_int = x_mid.searchsorted(x_pix)

            y_int = y_mid.searchsorted(y_pix)

                                                                            

                                                                        

                                                                       

            im = (

                np.ascontiguousarray(A).view(np.uint32).ravel()[

                    np.add.outer(y_int * A.shape[1], x_int)]

                .view(np.uint8).reshape((height, width, 4)))

        else:                                     

                                                                       

            x_int = np.clip(

                self._Ax.searchsorted(x_pix) - 1, 0, len(self._Ax) - 2)

            y_int = np.clip(

                self._Ay.searchsorted(y_pix) - 1, 0, len(self._Ay) - 2)

            idx_int = np.add.outer(y_int * A.shape[1], x_int)

            x_frac = np.clip(

                np.divide(x_pix - self._Ax[x_int], np.diff(self._Ax)[x_int],

                          dtype=np.float32),                                 

                0, 1)

            y_frac = np.clip(

                np.divide(y_pix - self._Ay[y_int], np.diff(self._Ay)[y_int],

                          dtype=np.float32),

                0, 1)

            f00 = np.outer(1 - y_frac, 1 - x_frac)

            f10 = np.outer(y_frac, 1 - x_frac)

            f01 = np.outer(1 - y_frac, x_frac)

            f11 = np.outer(y_frac, x_frac)

            im = np.empty((height, width, 4), np.uint8)

            for chan in range(4):

                ac = A[:, :, chan].reshape(-1)                              

                                                                           

                                                    

                buf = f00 * ac[idx_int]

                buf += f10 * ac[A.shape[1]:][idx_int]

                buf += f01 * ac[1:][idx_int]

                buf += f11 * ac[A.shape[1] + 1:][idx_int]

                im[:, :, chan] = buf                              

        return im, l, b, IdentityTransform()



    def set_data(self, x, y, A):

        

        A = self._normalize_image_array(A)

        x = np.array(x, np.float32)

        y = np.array(y, np.float32)

        if not (x.ndim == y.ndim == 1 and A.shape[:2] == y.shape + x.shape):

            raise TypeError("Axes don't match array shape")

        self._A = A

        self._Ax = x

        self._Ay = y

        self._imcache = None

        self.stale = True



    def set_array(self, *args):

        raise NotImplementedError('Method not supported')



    def set_interpolation(self, s):

        

        if s is not None and s not in ('nearest', 'bilinear'):

            raise NotImplementedError('Only nearest neighbor and '

                                      'bilinear interpolations are supported')

        super().set_interpolation(s)



    def get_extent(self):

        if self._A is None:

            raise RuntimeError('Must set data first')

        return self._Ax[0], self._Ax[-1], self._Ay[0], self._Ay[-1]



    def set_filternorm(self, filternorm):

        pass



    def set_filterrad(self, filterrad):

        pass



    def set_norm(self, norm):

        if self._A is not None:

            raise RuntimeError('Cannot change colors after loading data')

        super().set_norm(norm)



    def set_cmap(self, cmap):

        if self._A is not None:

            raise RuntimeError('Cannot change colors after loading data')

        super().set_cmap(cmap)



    def get_cursor_data(self, event):

                             

        x, y = event.xdata, event.ydata

        if (x < self._Ax[0] or x > self._Ax[-1] or

                y < self._Ay[0] or y > self._Ay[-1]):

            return None

        j = np.searchsorted(self._Ax, x) - 1

        i = np.searchsorted(self._Ay, y) - 1

        return self._A[i, j]





class PcolorImage(AxesImage):

    



    def __init__(self, ax,

                 x=None,

                 y=None,

                 A=None,

                 *,

                 cmap=None,

                 norm=None,

                 colorizer=None,

                 **kwargs

                 ):

        

        super().__init__(ax, norm=norm, cmap=cmap, colorizer=colorizer)

        self._internal_update(kwargs)

        if A is not None:

            self.set_data(x, y, A)



    def make_image(self, renderer, magnification=1.0, unsampled=False):

                             

        if self._A is None:

            raise RuntimeError('You must first set the image array')

        if unsampled:

            raise ValueError('unsampled not supported on PColorImage')



        if self._imcache is None:

            A = self.to_rgba(self._A, bytes=True)

            self._imcache = np.pad(A, [(1, 1), (1, 1), (0, 0)], "constant")

        padded_A = self._imcache

        bg = mcolors.to_rgba(self.axes.patch.get_facecolor(), 0)

        bg = (np.array(bg) * 255).astype(np.uint8)

        if (padded_A[0, 0] != bg).all():

            padded_A[[0, -1], :] = padded_A[:, [0, -1]] = bg



        l, b, r, t = self.axes.bbox.extents

        width = (round(r) + 0.5) - (round(l) - 0.5)

        height = (round(t) + 0.5) - (round(b) - 0.5)

        width = round(width * magnification)

        height = round(height * magnification)

        vl = self.axes.viewLim



        x_pix = np.linspace(vl.x0, vl.x1, width)

        y_pix = np.linspace(vl.y0, vl.y1, height)

        x_int = self._Ax.searchsorted(x_pix)

        y_int = self._Ay.searchsorted(y_pix)

        im = (                                                              

            padded_A.view(np.uint32).ravel()[

                np.add.outer(y_int * padded_A.shape[1], x_int)]

            .view(np.uint8).reshape((height, width, 4)))

        return im, l, b, IdentityTransform()



    def _check_unsampled_image(self):

        return False



    def set_data(self, x, y, A):

        

        A = self._normalize_image_array(A)

        x = np.arange(0., A.shape[1] + 1) if x is None else np.array(x, float).ravel()

        y = np.arange(0., A.shape[0] + 1) if y is None else np.array(y, float).ravel()

        if A.shape[:2] != (y.size - 1, x.size - 1):

            raise ValueError(

                "Axes don't match array shape. Got %s, expected %s." %

                (A.shape[:2], (y.size - 1, x.size - 1)))

                                                                      

        if x[-1] < x[0]:

            x = x[::-1]

            A = A[:, ::-1]

        if y[-1] < y[0]:

            y = y[::-1]

            A = A[::-1]

        self._A = A

        self._Ax = x

        self._Ay = y

        self._imcache = None

        self.stale = True



    def set_array(self, *args):

        raise NotImplementedError('Method not supported')



    def get_cursor_data(self, event):

                             

        x, y = event.xdata, event.ydata

        if (x < self._Ax[0] or x > self._Ax[-1] or

                y < self._Ay[0] or y > self._Ay[-1]):

            return None

        j = np.searchsorted(self._Ax, x) - 1

        i = np.searchsorted(self._Ay, y) - 1

        return self._A[i, j]





class FigureImage(_ImageBase):

    



    zorder = 0



    _interpolation = 'nearest'



    def __init__(self, fig,

                 *,

                 cmap=None,

                 norm=None,

                 colorizer=None,

                 offsetx=0,

                 offsety=0,

                 origin=None,

                 **kwargs

                 ):

        

        super().__init__(

            None,

            norm=norm,

            cmap=cmap,

            colorizer=colorizer,

            origin=origin

        )

        self.set_figure(fig)

        self.ox = offsetx

        self.oy = offsety

        self._internal_update(kwargs)

        self.magnification = 1.0



    def get_extent(self):

        

        numrows, numcols = self.get_size()

        return (-0.5 + self.ox, numcols-0.5 + self.ox,

                -0.5 + self.oy, numrows-0.5 + self.oy)



    def make_image(self, renderer, magnification=1.0, unsampled=False):

                             

        fig = self.get_figure(root=True)

        fac = renderer.dpi/fig.dpi

                                                                 

                                                                   

                                                                  

        bbox = Bbox([[self.ox/fac, self.oy/fac],

                     [(self.ox/fac + self._A.shape[1]),

                     (self.oy/fac + self._A.shape[0])]])

        width, height = fig.get_size_inches()

        width *= renderer.dpi

        height *= renderer.dpi

        clip = Bbox([[0, 0], [width, height]])

        return self._make_image(

            self._A, bbox, bbox, clip, magnification=magnification / fac,

            unsampled=unsampled, round_to_pixel_border=False)



    def set_data(self, A):

        

        super().set_data(A)

        self.stale = True





class BboxImage(_ImageBase):

    

    def __init__(self, bbox,

                 *,

                 cmap=None,

                 norm=None,

                 colorizer=None,

                 interpolation=None,

                 origin=None,

                 filternorm=True,

                 filterrad=4.0,

                 resample=False,

                 **kwargs

                 ):



        super().__init__(

            None,

            cmap=cmap,

            norm=norm,

            colorizer=colorizer,

            interpolation=interpolation,

            origin=origin,

            filternorm=filternorm,

            filterrad=filterrad,

            resample=resample,

            **kwargs

        )

        self.bbox = bbox



    def get_window_extent(self, renderer=None):

        if isinstance(self.bbox, BboxBase):

            return self.bbox

        elif callable(self.bbox):

            if renderer is None:

                renderer = self.get_figure()._get_renderer()

            return self.bbox(renderer)

        else:

            raise ValueError("Unknown type of bbox")



    def contains(self, mouseevent):

        

        if self._different_canvas(mouseevent) or not self.get_visible():

            return False, {}

        x, y = mouseevent.x, mouseevent.y

        inside = self.get_window_extent().contains(x, y)

        return inside, {}



    def make_image(self, renderer, magnification=1.0, unsampled=False):

                             

        width, height = renderer.get_canvas_width_height()

        bbox_in = self.get_window_extent(renderer).frozen()

        bbox_in._points /= [width, height]

        bbox_out = self.get_window_extent(renderer)

        clip = Bbox([[0, 0], [width, height]])

        self._transform = BboxTransformTo(clip)

        return self._make_image(

            self._A,

            bbox_in, bbox_out, clip, magnification, unsampled=unsampled)





def imread(fname, format=None):

    

                                                                       

    from urllib import parse



    if format is None:

        if isinstance(fname, str):

            parsed = parse.urlparse(fname)

                                                                            

                                           

            if len(parsed.scheme) > 1:

                ext = 'png'

            else:

                ext = Path(fname).suffix.lower()[1:]

        elif hasattr(fname, 'geturl'):                          

                                                                             

                                                                               

                                                                     

                                                                              

                                         

            ext = 'png'

        elif hasattr(fname, 'name'):

            ext = Path(fname.name).suffix.lower()[1:]

        else:

            ext = 'png'

    else:

        ext = format

    img_open = (

        PIL.PngImagePlugin.PngImageFile if ext == 'png' else PIL.Image.open)

    if isinstance(fname, str) and len(parse.urlparse(fname).scheme) > 1:

                                              

        raise ValueError(

            "Please open the URL for reading and pass the "

            "result to Pillow, e.g. with "

            "``np.array(PIL.Image.open(urllib.request.urlopen(url)))``."

            )

    with img_open(fname) as image:

        return (_pil_png_to_float_array(image)

                if isinstance(image, PIL.PngImagePlugin.PngImageFile) else

                pil_to_array(image))





def imsave(fname, arr, vmin=None, vmax=None, cmap=None, format=None,

           origin=None, dpi=100, *, metadata=None, pil_kwargs=None):

    

    from matplotlib.figure import Figure



                                                                       

    arr = np.asanyarray(arr)



    if isinstance(fname, os.PathLike):

        fname = os.fspath(fname)

    if format is None:

        format = (Path(fname).suffix[1:] if isinstance(fname, str)

                  else mpl.rcParams["savefig.format"]).lower()

    if format in ["pdf", "ps", "eps", "svg"]:

                                                     

        if pil_kwargs is not None:

            raise ValueError(

                f"Cannot use 'pil_kwargs' when saving to {format}")

        fig = Figure(dpi=dpi, frameon=False)

        fig.figimage(arr, cmap=cmap, vmin=vmin, vmax=vmax, origin=origin,

                     resize=True)

        fig.savefig(fname, dpi=dpi, format=format, transparent=True,

                    metadata=metadata)

    else:

                                                                            

                                                         

        origin = mpl._val_or_rc(origin, "image.origin")

        _api.check_in_list(('upper', 'lower'), origin=origin)

        if origin == "lower":

            arr = arr[::-1]

        if (isinstance(arr, memoryview) and arr.format == "B"

                and arr.ndim == 3 and arr.shape[-1] == 4):

                                                                            

                                                                               

                                                                             

                                             

            rgba = arr

        else:

            sm = mcolorizer.Colorizer(cmap=cmap)

            sm.set_clim(vmin, vmax)

            rgba = sm.to_rgba(arr, bytes=True)

        if pil_kwargs is None:

            pil_kwargs = {}

        else:

                                                                               

            pil_kwargs = pil_kwargs.copy()

        pil_shape = (rgba.shape[1], rgba.shape[0])

        rgba = np.require(rgba, requirements='C')

        image = PIL.Image.frombuffer(

            "RGBA", pil_shape, rgba, "raw", "RGBA", 0, 1)

        if format == "png":

                                                                            

                                                                

            if "pnginfo" in pil_kwargs:

                if metadata:

                    _api.warn_external("'metadata' is overridden by the "

                                       "'pnginfo' entry in 'pil_kwargs'.")

            else:

                metadata = {

                    "Software": (f"Matplotlib version{mpl.__version__}, "

                                 f"https://matplotlib.org/"),

                    **(metadata if metadata is not None else {}),

                }

                pil_kwargs["pnginfo"] = pnginfo = PIL.PngImagePlugin.PngInfo()

                for k, v in metadata.items():

                    if v is not None:

                        pnginfo.add_text(k, v)

        elif metadata is not None:

            raise ValueError(f"metadata not supported for format {format!r}")

        if format in ["jpg", "jpeg"]:

            format = "jpeg"                                   

            facecolor = mpl.rcParams["savefig.facecolor"]

            if cbook._str_equal(facecolor, "auto"):

                facecolor = mpl.rcParams["figure.facecolor"]

            color = tuple(int(x * 255) for x in mcolors.to_rgb(facecolor))

            background = PIL.Image.new("RGB", pil_shape, color)

            background.paste(image, image)

            image = background

        pil_kwargs.setdefault("format", format)

        pil_kwargs.setdefault("dpi", (dpi, dpi))

        image.save(fname, **pil_kwargs)





def pil_to_array(pilImage):

    

    if pilImage.mode in ['RGBA', 'RGBX', 'RGB', 'L']:

                                                              

        return np.asarray(pilImage)

    elif pilImage.mode.startswith('I;16'):

                                              

        raw = pilImage.tobytes('raw', pilImage.mode)

        if pilImage.mode.endswith('B'):

            x = np.frombuffer(raw, '>u2')

        else:

            x = np.frombuffer(raw, '<u2')

        return x.reshape(pilImage.size[::-1]).astype('=u2')

    else:                                   

        try:

            pilImage = pilImage.convert('RGBA')

        except ValueError as err:

            raise RuntimeError('Unknown image mode') from err

        return np.asarray(pilImage)                           





def _pil_png_to_float_array(pil_png):

    

                                                                               

                              

                                                                      

                                                                               

                

    mode = pil_png.mode

    rawmode = pil_png.png.im_rawmode

    if rawmode == "1":              

        return np.asarray(pil_png, np.float32)

    if rawmode == "L;2":              

        return np.divide(pil_png, 2**2 - 1, dtype=np.float32)

    if rawmode == "L;4":              

        return np.divide(pil_png, 2**4 - 1, dtype=np.float32)

    if rawmode == "L":              

        return np.divide(pil_png, 2**8 - 1, dtype=np.float32)

    if rawmode == "I;16B":              

        return np.divide(pil_png, 2**16 - 1, dtype=np.float32)

    if mode == "RGB":        

        return np.divide(pil_png, 2**8 - 1, dtype=np.float32)

    if mode == "P":            

        return np.divide(pil_png.convert("RGBA"), 2**8 - 1, dtype=np.float32)

    if mode == "LA":                      

        return np.divide(pil_png.convert("RGBA"), 2**8 - 1, dtype=np.float32)

    if mode == "RGBA":         

        return np.divide(pil_png, 2**8 - 1, dtype=np.float32)

    raise ValueError(f"Unknown PIL rawmode: {rawmode}")





def thumbnail(infile, thumbfile, scale=0.1, interpolation='bilinear',

              preview=False):

    



    im = imread(infile)

    rows, cols, depth = im.shape



                                                                              

    dpi = 100



    height = rows / dpi * scale

    width = cols / dpi * scale



    if preview:

                                           

        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(width, height), dpi=dpi)

    else:

        from matplotlib.figure import Figure

        fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvasBase(fig)



    ax = fig.add_axes((0, 0, 1, 1), aspect='auto',

                      frameon=False, xticks=[], yticks=[])

    ax.imshow(im, aspect='auto', resample=True, interpolation=interpolation)

    fig.savefig(thumbfile, dpi=dpi)

    return fig

