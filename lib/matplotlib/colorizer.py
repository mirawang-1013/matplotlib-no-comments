



import functools



import numpy as np

from numpy import ma



from matplotlib import _api, colors, cbook, scale, artist

import matplotlib as mpl



mpl._docstring.interpd.register(

    colorizer_doc="""\
colorizer : `~matplotlib.colorizer.Colorizer` or None, default: None
    The Colorizer object used to map color to data. If None, a Colorizer
    object is created from a *norm* and *cmap*.""",

    )





class Colorizer:

    

    def __init__(self, cmap=None, norm=None):



        self._cmap = None

        self._set_cmap(cmap)



        self._id_norm = None

        self._norm = None

        self.norm = norm



        self.callbacks = cbook.CallbackRegistry(signals=["changed"])

        self.colorbar = None



    def _scale_norm(self, norm, vmin, vmax, A):

        

        if vmin is not None or vmax is not None:

            self.set_clim(vmin, vmax)

            if isinstance(norm, colors.Normalize):

                raise ValueError(

                    "Passing a Normalize instance simultaneously with "

                    "vmin/vmax is not supported.  Please pass vmin/vmax "

                    "directly to the norm when creating it.")



                                                                   

                                             

        self.autoscale_None(A)



    @property

    def norm(self):

        return self._norm



    @norm.setter

    def norm(self, norm):

        _api.check_isinstance((colors.Norm, str, None), norm=norm)

        if norm is None:

            norm = colors.Normalize()

        elif isinstance(norm, str):

            try:

                scale_cls = scale._scale_mapping[norm]

            except KeyError:

                raise ValueError(

                    "Invalid norm str name; the following values are "

                    f"supported: {', '.join(scale._scale_mapping)}"

                ) from None

            norm = _auto_norm_from_scale(scale_cls)()



        if norm is self.norm:

                                         

            return



        in_init = self.norm is None

                                                                

        if not in_init:

            self.norm.callbacks.disconnect(self._id_norm)

        self._norm = norm

        self._id_norm = self.norm.callbacks.connect('changed',

                                                    self.changed)

        if not in_init:

            self.changed()



    def to_rgba(self, x, alpha=None, bytes=False, norm=True):

        

                                                    

        if isinstance(x, np.ndarray) and x.ndim == 3:

            return self._pass_image_data(x, alpha, bytes, norm)



                                                 

        x = ma.asarray(x)

        if norm:

            x = self.norm(x)

        rgba = self.cmap(x, alpha=alpha, bytes=bytes)

        return rgba



    @staticmethod

    def _pass_image_data(x, alpha=None, bytes=False, norm=True):

        

        if x.shape[2] == 3:

            if alpha is None:

                alpha = 1

            if x.dtype == np.uint8:

                alpha = np.uint8(alpha * 255)

            m, n = x.shape[:2]

            xx = np.empty(shape=(m, n, 4), dtype=x.dtype)

            xx[:, :, :3] = x

            xx[:, :, 3] = alpha

        elif x.shape[2] == 4:

            xx = x

        else:

            raise ValueError("Third dimension must be 3 or 4")

        if xx.dtype.kind == 'f':

                                                      

            if np.any(nans := np.isnan(x)):

                if x.shape[2] == 4:

                    xx = xx.copy()

                xx[np.any(nans, axis=2), :] = 0



            if norm and (xx.max() > 1 or xx.min() < 0):

                raise ValueError("Floating point image RGB values "

                                 "must be in the 0..1 range.")

            if bytes:

                xx = (xx * 255).astype(np.uint8)

        elif xx.dtype == np.uint8:

            if not bytes:

                xx = xx.astype(np.float32) / 255

        else:

            raise ValueError("Image RGB array must be uint8 or "

                             "floating point; found %s" % xx.dtype)

                                                              

                                                                            

        if np.ma.is_masked(x):

            xx[np.any(np.ma.getmaskarray(x), axis=2), 3] = 0

        return xx



    def autoscale(self, A):

        

        if A is None:

            raise TypeError('You must first set_array for mappable')

                                                                        

                                                    

        self.norm.autoscale(A)



    def autoscale_None(self, A):

        

        if A is None:

            raise TypeError('You must first set_array for mappable')

                                                                        

                                                    

        self.norm.autoscale_None(A)



    def _set_cmap(self, cmap):

        

                                               

        from matplotlib import cm

        in_init = self._cmap is None

        self._cmap = cm._ensure_cmap(cmap)

        if not in_init:

            self.changed()                                       



    @property

    def cmap(self):

        return self._cmap



    @cmap.setter

    def cmap(self, cmap):

        self._set_cmap(cmap)



    def set_clim(self, vmin=None, vmax=None):

        

                                                                        

                                                                                 

                                                                

        if vmax is None:

            try:

                vmin, vmax = vmin

            except (TypeError, ValueError):

                pass



        orig_vmin_vmax = self.norm.vmin, self.norm.vmax



                                                                         

                                              

        with self.norm.callbacks.blocked(signal='changed'):

            if vmin is not None:

                self.norm.vmin = vmin

            if vmax is not None:

                self.norm.vmax = vmax



                                                        

        if orig_vmin_vmax != (self.norm.vmin, self.norm.vmax):

            self.norm.callbacks.process('changed')



    def get_clim(self):

        

        return self.norm.vmin, self.norm.vmax



    def changed(self):

        

        self.callbacks.process('changed')

        self.stale = True



    @property

    def vmin(self):

        return self.get_clim()[0]



    @vmin.setter

    def vmin(self, vmin):

        self.set_clim(vmin=vmin)



    @property

    def vmax(self):

        return self.get_clim()[1]



    @vmax.setter

    def vmax(self, vmax):

        self.set_clim(vmax=vmax)



    @property

    def clip(self):

        return self.norm.clip



    @clip.setter

    def clip(self, clip):

        self.norm.clip = clip





class _ColorizerInterface:

    

    def _scale_norm(self, norm, vmin, vmax):

        self._colorizer._scale_norm(norm, vmin, vmax, self._A)



    def to_rgba(self, x, alpha=None, bytes=False, norm=True):

        

        return self._colorizer.to_rgba(x, alpha=alpha, bytes=bytes, norm=norm)



    def get_clim(self):

        

        return self._colorizer.get_clim()



    def set_clim(self, vmin=None, vmax=None):

        

                                                                        

                                                    

        self._colorizer.set_clim(vmin, vmax)



    def get_alpha(self):

        try:

            return super().get_alpha()

        except AttributeError:

            return 1



    @property

    def cmap(self):

        return self._colorizer.cmap



    @cmap.setter

    def cmap(self, cmap):

        self._colorizer.cmap = cmap



    def get_cmap(self):

        

        return self._colorizer.cmap



    def set_cmap(self, cmap):

        

        self.cmap = cmap



    @property

    def norm(self):

        return self._colorizer.norm



    @norm.setter

    def norm(self, norm):

        self._colorizer.norm = norm



    def set_norm(self, norm):

        

        self.norm = norm



    def autoscale(self):

        

        self._colorizer.autoscale(self._A)



    def autoscale_None(self):

        

        self._colorizer.autoscale_None(self._A)



    @property

    def colorbar(self):

        

        return self._colorizer.colorbar



    @colorbar.setter

    def colorbar(self, colorbar):

        self._colorizer.colorbar = colorbar



    def _format_cursor_data_override(self, data):

                                                                         

                                                                            

                                                                              

                                                                             

                                                                    



                                                                                

                                                                  

        n = self.cmap.N

        if np.ma.getmask(data):

            return "[]"

        normed = self.norm(data)

        if np.isfinite(normed):

            if isinstance(self.norm, colors.BoundaryNorm):

                                                         

                cur_idx = np.argmin(np.abs(self.norm.boundaries - data))

                neigh_idx = max(0, cur_idx - 1)

                                                    

                delta = np.diff(

                    self.norm.boundaries[neigh_idx:cur_idx + 2]

                ).max()

            elif self.norm.vmin == self.norm.vmax:

                                                                

                delta = np.abs(self.norm.vmin * .1)

            else:

                                                           

                neighbors = self.norm.inverse(

                    (int(normed * n) + np.array([0, 1])) / n)

                delta = abs(neighbors - data).max()

            g_sig_digits = cbook._g_sig_digits(data, delta)

        else:

            g_sig_digits = 3                                  

        return f"[{data:-#.{g_sig_digits}g}]"





class _ScalarMappable(_ColorizerInterface):

    



                                                   

                                                           

                                   



                                                                 

                                                 

                                                       

                                                                 

                                                    

                                                                   

                                                           

                                                           

                                      

                                                           

    def __init__(self, norm=None, cmap=None, *, colorizer=None, **kwargs):

        

        super().__init__(**kwargs)

        self._A = None

        self._colorizer = self._get_colorizer(colorizer=colorizer, norm=norm, cmap=cmap)



        self.colorbar = None

        self._id_colorizer = self._colorizer.callbacks.connect('changed', self.changed)

        self.callbacks = cbook.CallbackRegistry(signals=["changed"])



    def set_array(self, A):

        

        if A is None:

            self._A = None

            return



        A = cbook.safe_masked_invalid(A, copy=True)

        if not np.can_cast(A.dtype, float, "same_kind"):

            raise TypeError(f"Image data of dtype {A.dtype} cannot be "

                            "converted to float")



        self._A = A

        if not self.norm.scaled():

            self._colorizer.autoscale_None(A)



    def get_array(self):

        

        return self._A



    def changed(self):

        

        self.callbacks.process('changed', self)

        self.stale = True



    @staticmethod

    def _check_exclusionary_keywords(colorizer, **kwargs):

        

        if colorizer is not None:

            if any([val is not None for val in kwargs.values()]):

                raise ValueError("The `colorizer` keyword cannot be used simultaneously"

                                 " with any of the following keywords: "

                                 + ", ".join(f'`{key}`' for key in kwargs.keys()))



    @staticmethod

    def _get_colorizer(cmap, norm, colorizer):

        if isinstance(colorizer, Colorizer):

            _ScalarMappable._check_exclusionary_keywords(

                Colorizer, cmap=cmap, norm=norm

            )

            return colorizer

        return Colorizer(cmap, norm)



                                                                              

mpl._docstring.interpd.register(

    cmap_doc="""\
cmap : str or `~matplotlib.colors.Colormap`, default: :rc:`image.cmap`
    The Colormap instance or registered colormap name used to map scalar data
    to colors.""",

    norm_doc="""\
norm : str or `~matplotlib.colors.Normalize`, optional
    The normalization method used to scale scalar data to the [0, 1] range
    before mapping to colors using *cmap*. By default, a linear scaling is
    used, mapping the lowest value to 0 and the highest to 1.

    If given, this can be one of the following:

    - An instance of `.Normalize` or one of its subclasses
      (see :ref:`colormapnorms`).
    - A scale name, i.e. one of "linear", "log", "symlog", "logit", etc.  For a
      list of available scales, call `matplotlib.scale.get_scale_names()`.
      In that case, a suitable `.Normalize` subclass is dynamically generated
      and instantiated.""",

    vmin_vmax_doc="""\
vmin, vmax : float, optional
    When using scalar data and no explicit *norm*, *vmin* and *vmax* define
    the data range that the colormap covers. By default, the colormap covers
    the complete value range of the supplied data. It is an error to use
    *vmin*/*vmax* when a *norm* instance is given (but using a `str` *norm*
    name together with *vmin*/*vmax* is acceptable).""",

)





class ColorizingArtist(_ScalarMappable, artist.Artist):

    

    def __init__(self, colorizer, **kwargs):

        

        _api.check_isinstance(Colorizer, colorizer=colorizer)

        super().__init__(colorizer=colorizer, **kwargs)



    @property

    def colorizer(self):

        return self._colorizer



    @colorizer.setter

    def colorizer(self, cl):

        _api.check_isinstance(Colorizer, colorizer=cl)

        self._colorizer.callbacks.disconnect(self._id_colorizer)

        self._colorizer = cl

        self._id_colorizer = cl.callbacks.connect('changed', self.changed)



    def _set_colorizer_check_keywords(self, colorizer, **kwargs):

        

        self._check_exclusionary_keywords(colorizer, **kwargs)

        self.colorizer = colorizer





def _auto_norm_from_scale(scale_cls):

    

                                                              

                                          

    try:

        norm = colors.make_norm_from_scale(

            functools.partial(scale_cls, nonpositive="mask"))(

            colors.Normalize)()

    except TypeError:

        norm = colors.make_norm_from_scale(scale_cls)(

            colors.Normalize)()

    return type(norm)

