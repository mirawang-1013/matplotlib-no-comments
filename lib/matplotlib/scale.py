              



import inspect

import textwrap

from functools import wraps



import numpy as np



import matplotlib as mpl

from matplotlib import _api, _docstring

from matplotlib.ticker import (

    NullFormatter, ScalarFormatter, LogFormatterSciNotation, LogitFormatter,

    NullLocator, LogLocator, AutoLocator, AutoMinorLocator,

    SymmetricalLogLocator, AsinhLocator, LogitLocator)

from matplotlib.transforms import Transform, IdentityTransform





class ScaleBase:

    



    def __init__(self, axis):

        



    def get_transform(self):

        

        raise NotImplementedError()



    def set_default_locators_and_formatters(self, axis):

        

        raise NotImplementedError()



    def limit_range_for_scale(self, vmin, vmax, minpos):

        

        return vmin, vmax





def _make_axis_parameter_optional(init_func):

    

    @wraps(init_func)

    def wrapper(self, *args, **kwargs):

        if args and isinstance(args[0], mpl.axis.Axis):

            return init_func(self, *args, **kwargs)

        else:

                                                                  

            axis = kwargs.pop('axis', None)

            return init_func(self, axis, *args, **kwargs)

    return wrapper





class LinearScale(ScaleBase):

    



    name = 'linear'



    @_make_axis_parameter_optional

    def __init__(self, axis):

                                                                               

                                                                               

                                          

                      



    def set_default_locators_and_formatters(self, axis):

                             

        axis.set_major_locator(AutoLocator())

        axis.set_major_formatter(ScalarFormatter())

        axis.set_minor_formatter(NullFormatter())

                                                                     

        if (axis.axis_name == 'x' and mpl.rcParams['xtick.minor.visible'] or

                axis.axis_name == 'y' and mpl.rcParams['ytick.minor.visible']):

            axis.set_minor_locator(AutoMinorLocator())

        else:

            axis.set_minor_locator(NullLocator())



    def get_transform(self):

        

        return IdentityTransform()





class FuncTransform(Transform):

    



    input_dims = output_dims = 1



    def __init__(self, forward, inverse):

        

        super().__init__()

        if callable(forward) and callable(inverse):

            self._forward = forward

            self._inverse = inverse

        else:

            raise ValueError('arguments to FuncTransform must be functions')



    def transform_non_affine(self, values):

        return self._forward(values)



    def inverted(self):

        return FuncTransform(self._inverse, self._forward)





class FuncScale(ScaleBase):

    



    name = 'function'



    @_make_axis_parameter_optional

    def __init__(self, axis, functions):

        

        forward, inverse = functions

        transform = FuncTransform(forward, inverse)

        self._transform = transform



    def get_transform(self):

        

        return self._transform



    def set_default_locators_and_formatters(self, axis):

                             

        axis.set_major_locator(AutoLocator())

        axis.set_major_formatter(ScalarFormatter())

        axis.set_minor_formatter(NullFormatter())

                                                                     

        if (axis.axis_name == 'x' and mpl.rcParams['xtick.minor.visible'] or

                axis.axis_name == 'y' and mpl.rcParams['ytick.minor.visible']):

            axis.set_minor_locator(AutoMinorLocator())

        else:

            axis.set_minor_locator(NullLocator())





class LogTransform(Transform):

    input_dims = output_dims = 1



    def __init__(self, base, nonpositive='clip'):

        super().__init__()

        if base <= 0 or base == 1:

            raise ValueError('The log base cannot be <= 0 or == 1')

        self.base = base

        self._clip = _api.check_getitem(

            {"clip": True, "mask": False}, nonpositive=nonpositive)



    def __str__(self):

        return "{}(base={}, nonpositive={!r})".format(

            type(self).__name__, self.base, "clip" if self._clip else "mask")



    def transform_non_affine(self, values):

                                                                          

        with np.errstate(divide="ignore", invalid="ignore"):

            log = {np.e: np.log, 2: np.log2, 10: np.log10}.get(self.base)

            if log:                                                         

                out = log(values)

            else:

                out = np.log(values)

                out /= np.log(self.base)

            if self._clip:

                                                                              

                                                                       

                                                                             

                                                                   

                                                                              

                                                                             

                                                                              

                                                         

                                     

                out[values <= 0] = -1000

        return out



    def inverted(self):

        return InvertedLogTransform(self.base)





class InvertedLogTransform(Transform):

    input_dims = output_dims = 1



    def __init__(self, base):

        super().__init__()

        self.base = base



    def __str__(self):

        return f"{type(self).__name__}(base={self.base})"



    def transform_non_affine(self, values):

        return np.power(self.base, values)



    def inverted(self):

        return LogTransform(self.base)





class LogScale(ScaleBase):

    

    name = 'log'



    @_make_axis_parameter_optional

    def __init__(self, axis=None, *, base=10, subs=None, nonpositive="clip"):

        

        self._transform = LogTransform(base, nonpositive)

        self.subs = subs



    base = property(lambda self: self._transform.base)



    def set_default_locators_and_formatters(self, axis):

                             

        axis.set_major_locator(LogLocator(self.base))

        axis.set_major_formatter(LogFormatterSciNotation(self.base))

        axis.set_minor_locator(LogLocator(self.base, self.subs))

        axis.set_minor_formatter(

            LogFormatterSciNotation(self.base,

                                    labelOnlyBase=(self.subs is not None)))



    def get_transform(self):

        

        return self._transform



    def limit_range_for_scale(self, vmin, vmax, minpos):

        

        if not np.isfinite(minpos):

            minpos = 1e-300                                                  



        return (minpos if vmin <= 0 else vmin,

                minpos if vmax <= 0 else vmax)





class FuncScaleLog(LogScale):

    



    name = 'functionlog'



    @_make_axis_parameter_optional

    def __init__(self, axis, functions, base=10):

        

        forward, inverse = functions

        self.subs = None

        self._transform = FuncTransform(forward, inverse) + LogTransform(base)



    @property

    def base(self):

        return self._transform._b.base                             



    def get_transform(self):

        

        return self._transform





class SymmetricalLogTransform(Transform):

    input_dims = output_dims = 1



    def __init__(self, base, linthresh, linscale):

        super().__init__()

        if base <= 1.0:

            raise ValueError("'base' must be larger than 1")

        if linthresh <= 0.0:

            raise ValueError("'linthresh' must be positive")

        if linscale <= 0.0:

            raise ValueError("'linscale' must be positive")

        self.base = base

        self.linthresh = linthresh

        self.linscale = linscale

        self._linscale_adj = (linscale / (1.0 - self.base ** -1))

        self._log_base = np.log(base)



    def transform_non_affine(self, values):

        abs_a = np.abs(values)

        with np.errstate(divide="ignore", invalid="ignore"):

            out = np.sign(values) * self.linthresh * (

                self._linscale_adj +

                np.log(abs_a / self.linthresh) / self._log_base)

            inside = abs_a <= self.linthresh

        out[inside] = values[inside] * self._linscale_adj

        return out



    def inverted(self):

        return InvertedSymmetricalLogTransform(self.base, self.linthresh,

                                               self.linscale)





class InvertedSymmetricalLogTransform(Transform):

    input_dims = output_dims = 1



    def __init__(self, base, linthresh, linscale):

        super().__init__()

        symlog = SymmetricalLogTransform(base, linthresh, linscale)

        self.base = base

        self.linthresh = linthresh

        self.invlinthresh = symlog.transform(linthresh)

        self.linscale = linscale

        self._linscale_adj = (linscale / (1.0 - self.base ** -1))



    def transform_non_affine(self, values):

        abs_a = np.abs(values)

        with np.errstate(divide="ignore", invalid="ignore"):

            out = np.sign(values) * self.linthresh * (

                np.power(self.base,

                         abs_a / self.linthresh - self._linscale_adj))

            inside = abs_a <= self.invlinthresh

        out[inside] = values[inside] / self._linscale_adj

        return out



    def inverted(self):

        return SymmetricalLogTransform(self.base,

                                       self.linthresh, self.linscale)





class SymmetricalLogScale(ScaleBase):

    

    name = 'symlog'



    @_make_axis_parameter_optional

    def __init__(self, axis=None, *, base=10, linthresh=2, subs=None, linscale=1):

        self._transform = SymmetricalLogTransform(base, linthresh, linscale)

        self.subs = subs



    base = property(lambda self: self._transform.base)

    linthresh = property(lambda self: self._transform.linthresh)

    linscale = property(lambda self: self._transform.linscale)



    def set_default_locators_and_formatters(self, axis):

                             

        axis.set_major_locator(SymmetricalLogLocator(self.get_transform()))

        axis.set_major_formatter(LogFormatterSciNotation(self.base))

        axis.set_minor_locator(SymmetricalLogLocator(self.get_transform(),

                                                     self.subs))

        axis.set_minor_formatter(NullFormatter())



    def get_transform(self):

        

        return self._transform





class AsinhTransform(Transform):

    

    input_dims = output_dims = 1



    def __init__(self, linear_width):

        super().__init__()

        if linear_width <= 0.0:

            raise ValueError("Scale parameter 'linear_width' " +

                             "must be strictly positive")

        self.linear_width = linear_width



    def transform_non_affine(self, values):

        return self.linear_width * np.arcsinh(values / self.linear_width)



    def inverted(self):

        return InvertedAsinhTransform(self.linear_width)





class InvertedAsinhTransform(Transform):

    

    input_dims = output_dims = 1



    def __init__(self, linear_width):

        super().__init__()

        self.linear_width = linear_width



    def transform_non_affine(self, values):

        return self.linear_width * np.sinh(values / self.linear_width)



    def inverted(self):

        return AsinhTransform(self.linear_width)





class AsinhScale(ScaleBase):

    



    name = 'asinh'



    auto_tick_multipliers = {

        3: (2, ),

        4: (2, ),

        5: (2, ),

        8: (2, 4),

        10: (2, 5),

        16: (2, 4, 8),

        64: (4, 16),

        1024: (256, 512)

    }



    @_make_axis_parameter_optional

    def __init__(self, axis=None, *, linear_width=1.0,

                 base=10, subs='auto', **kwargs):

        

        super().__init__(axis)

        self._transform = AsinhTransform(linear_width)

        self._base = int(base)

        if subs == 'auto':

            self._subs = self.auto_tick_multipliers.get(self._base)

        else:

            self._subs = subs



    linear_width = property(lambda self: self._transform.linear_width)



    def get_transform(self):

        return self._transform



    def set_default_locators_and_formatters(self, axis):

        axis.set(major_locator=AsinhLocator(self.linear_width,

                                            base=self._base),

                 minor_locator=AsinhLocator(self.linear_width,

                                            base=self._base,

                                            subs=self._subs),

                 minor_formatter=NullFormatter())

        if self._base > 1:

            axis.set_major_formatter(LogFormatterSciNotation(self._base))

        else:

            axis.set_major_formatter('{x:.3g}')





class LogitTransform(Transform):

    input_dims = output_dims = 1



    def __init__(self, nonpositive='mask'):

        super().__init__()

        _api.check_in_list(['mask', 'clip'], nonpositive=nonpositive)

        self._nonpositive = nonpositive

        self._clip = {"clip": True, "mask": False}[nonpositive]



    def transform_non_affine(self, values):

        

        with np.errstate(divide="ignore", invalid="ignore"):

            out = np.log10(values / (1 - values))

        if self._clip:                                              

            out[values <= 0] = -1000

            out[1 <= values] = 1000

        return out



    def inverted(self):

        return LogisticTransform(self._nonpositive)



    def __str__(self):

        return f"{type(self).__name__}({self._nonpositive!r})"





class LogisticTransform(Transform):

    input_dims = output_dims = 1



    def __init__(self, nonpositive='mask'):

        super().__init__()

        self._nonpositive = nonpositive



    def transform_non_affine(self, values):

        

        return 1.0 / (1 + 10**(-values))



    def inverted(self):

        return LogitTransform(self._nonpositive)



    def __str__(self):

        return f"{type(self).__name__}({self._nonpositive!r})"





class LogitScale(ScaleBase):

    

    name = 'logit'



    @_make_axis_parameter_optional

    def __init__(self, axis=None, nonpositive='mask', *,

                 one_half=r"\frac{1}{2}", use_overline=False):

        

        self._transform = LogitTransform(nonpositive)

        self._use_overline = use_overline

        self._one_half = one_half



    def get_transform(self):

        

        return self._transform



    def set_default_locators_and_formatters(self, axis):

                             

                                             

        axis.set_major_locator(LogitLocator())

        axis.set_major_formatter(

            LogitFormatter(

                one_half=self._one_half,

                use_overline=self._use_overline

            )

        )

        axis.set_minor_locator(LogitLocator(minor=True))

        axis.set_minor_formatter(

            LogitFormatter(

                minor=True,

                one_half=self._one_half,

                use_overline=self._use_overline

            )

        )



    def limit_range_for_scale(self, vmin, vmax, minpos):

        

        if not np.isfinite(minpos):

            minpos = 1e-7                                                  

        return (minpos if vmin <= 0 else vmin,

                1 - minpos if vmax >= 1 else vmax)





_scale_mapping = {

    'linear': LinearScale,

    'log':    LogScale,

    'symlog': SymmetricalLogScale,

    'asinh':  AsinhScale,

    'logit':  LogitScale,

    'function': FuncScale,

    'functionlog': FuncScaleLog,

    }



                           

                                                                                

                                                                                   

                     

_scale_has_axis_parameter = {

    'linear': True,

    'log': True,

    'symlog': True,

    'asinh': True,

    'logit': True,

    'function': True,

    'functionlog': True,

}





def get_scale_names():

    

    return sorted(_scale_mapping)





def scale_factory(scale, axis, **kwargs):

    

    scale_cls = _api.check_getitem(_scale_mapping, scale=scale)



    if _scale_has_axis_parameter[scale]:

        return scale_cls(axis, **kwargs)

    else:

        return scale_cls(**kwargs)





if scale_factory.__doc__:

    scale_factory.__doc__ = scale_factory.__doc__ % {

        "names": ", ".join(map(repr, get_scale_names()))}





def register_scale(scale_class):

    

    _scale_mapping[scale_class.name] = scale_class



                                                   

    has_axis_parameter = "axis" in inspect.signature(scale_class).parameters

    _scale_has_axis_parameter[scale_class.name] = has_axis_parameter

    if has_axis_parameter:

        _api.warn_deprecated(

            "3.11",

            message=f"The scale {scale_class.__qualname__!r} uses an 'axis' parameter "

                    "in the constructors. This parameter is pending-deprecated since "

                    "matplotlib 3.11. It will be fully deprecated in 3.13 and removed "

                    "in 3.15. Starting with 3.11, 'register_scale()' accepts scales "

                    "without the *axis* parameter.",

            pending=True,

        )





def _get_scale_docs():

    

    docs = []

    for name, scale_class in _scale_mapping.items():

        docstring = inspect.getdoc(scale_class.__init__) or ""

        docs.extend([

            f"    {name!r}",

            "",

            textwrap.indent(docstring, " " * 8),

            ""

        ])

    return "\n".join(docs)





_docstring.interpd.register(

    scale_type='{%s}' % ', '.join([repr(x) for x in get_scale_names()]),

    scale_docs=_get_scale_docs().rstrip(),

    )

