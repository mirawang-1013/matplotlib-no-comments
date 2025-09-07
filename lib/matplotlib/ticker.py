



import itertools

import logging

import locale

import math

from numbers import Integral

import string



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook

from matplotlib import transforms as mtransforms



_log = logging.getLogger(__name__)



__all__ = ('TickHelper', 'Formatter', 'FixedFormatter',

           'NullFormatter', 'FuncFormatter', 'FormatStrFormatter',

           'StrMethodFormatter', 'ScalarFormatter', 'LogFormatter',

           'LogFormatterExponent', 'LogFormatterMathtext',

           'LogFormatterSciNotation',

           'LogitFormatter', 'EngFormatter', 'PercentFormatter',

           'Locator', 'IndexLocator', 'FixedLocator', 'NullLocator',

           'LinearLocator', 'LogLocator', 'AutoLocator',

           'MultipleLocator', 'MaxNLocator', 'AutoMinorLocator',

           'SymmetricalLogLocator', 'AsinhLocator', 'LogitLocator')





class _DummyAxis:

    __name__ = "dummy"



    def __init__(self, minpos=0):

        self._data_interval = (0, 1)

        self._view_interval = (0, 1)

        self._minpos = minpos



    def get_view_interval(self):

        return self._view_interval



    def set_view_interval(self, vmin, vmax):

        self._view_interval = (vmin, vmax)



    def get_minpos(self):

        return self._minpos



    def get_data_interval(self):

        return self._data_interval



    def set_data_interval(self, vmin, vmax):

        self._data_interval = (vmin, vmax)



    def get_tick_space(self):

                                                        

        return 9





class TickHelper:

    axis = None



    def set_axis(self, axis):

        self.axis = axis



    def create_dummy_axis(self, **kwargs):

        if self.axis is None:

            self.axis = _DummyAxis(**kwargs)





class Formatter(TickHelper):

    

                                                          

                     

    locs = []



    def __call__(self, x, pos=None):

        

        raise NotImplementedError('Derived must override')



    def format_ticks(self, values):

        

        self.set_locs(values)

        return [self(value, i) for i, value in enumerate(values)]



    def format_data(self, value):

        

        return self.__call__(value)



    def format_data_short(self, value):

        

        return self.format_data(value)



    def get_offset(self):

        return ''



    def set_locs(self, locs):

        

        self.locs = locs



    @staticmethod

    def fix_minus(s):

        

        return (s.replace('-', '\N{MINUS SIGN}')

                if mpl.rcParams['axes.unicode_minus']

                else s)



    def _set_locator(self, locator):

        

        pass





class NullFormatter(Formatter):

    



    def __call__(self, x, pos=None):

                             

        return ''





class FixedFormatter(Formatter):

    



    def __init__(self, seq):

        

        self.seq = seq

        self.offset_string = ''



    def __call__(self, x, pos=None):

        

        if pos is None or pos >= len(self.seq):

            return ''

        else:

            return self.seq[pos]



    def get_offset(self):

        return self.offset_string



    def set_offset_string(self, ofs):

        self.offset_string = ofs





class FuncFormatter(Formatter):

    



    def __init__(self, func):

        self.func = func

        self.offset_string = ""



    def __call__(self, x, pos=None):

        

        return self.func(x, pos)



    def get_offset(self):

        return self.offset_string



    def set_offset_string(self, ofs):

        self.offset_string = ofs





class FormatStrFormatter(Formatter):

    



    def __init__(self, fmt):

        self.fmt = fmt



    def __call__(self, x, pos=None):

        

        return self.fmt % x





class _UnicodeMinusFormat(string.Formatter):

    



    def format_field(self, value, format_spec):

        return Formatter.fix_minus(super().format_field(value, format_spec))





class StrMethodFormatter(Formatter):

    



    def __init__(self, fmt):

        self.fmt = fmt



    def __call__(self, x, pos=None):

        

        return _UnicodeMinusFormat().format(self.fmt, x=x, pos=pos)





class ScalarFormatter(Formatter):

    



    def __init__(self, useOffset=None, useMathText=None, useLocale=None, *,

                 usetex=None):

        useOffset = mpl._val_or_rc(useOffset, 'axes.formatter.useoffset')

        self._offset_threshold = mpl.rcParams['axes.formatter.offset_threshold']

        self.set_useOffset(useOffset)

        self.set_usetex(usetex)

        self.set_useMathText(useMathText)

        self.orderOfMagnitude = 0

        self.format = ''

        self._scientific = True

        self._powerlimits = mpl.rcParams['axes.formatter.limits']

        self.set_useLocale(useLocale)



    def get_usetex(self):

        

        return self._usetex



    def set_usetex(self, val):

        

        self._usetex = mpl._val_or_rc(val, 'text.usetex')



    usetex = property(fget=get_usetex, fset=set_usetex)



    def get_useOffset(self):

        

        return self._useOffset



    def set_useOffset(self, val):

        

        if isinstance(val, bool):

            self.offset = 0

            self._useOffset = val

        else:

            self._useOffset = False

            self.offset = val



    useOffset = property(fget=get_useOffset, fset=set_useOffset)



    def get_useLocale(self):

        

        return self._useLocale



    def set_useLocale(self, val):

        

        self._useLocale = mpl._val_or_rc(val, 'axes.formatter.use_locale')



    useLocale = property(fget=get_useLocale, fset=set_useLocale)



    def _format_maybe_minus_and_locale(self, fmt, arg):

        

        return self.fix_minus(

                                                                                      

                                                                  

                (",".join(locale.format_string(part, (arg,), True).replace(",", "{,}")

                          for part in fmt.split(",")) if self._useMathText

                 else locale.format_string(fmt, (arg,), True))

                if self._useLocale

                else fmt % arg)



    def get_useMathText(self):

        

        return self._useMathText



    def set_useMathText(self, val):

        

        if val is None:

            self._useMathText = mpl.rcParams['axes.formatter.use_mathtext']

            if self._useMathText is False:

                try:

                    from matplotlib import font_manager

                    ufont = font_manager.findfont(

                        font_manager.FontProperties(

                            family=mpl.rcParams["font.family"]

                        ),

                        fallback_to_default=False,

                    )

                except ValueError:

                    ufont = None



                if ufont == str(cbook._get_data_path("fonts/ttf/cmr10.ttf")):

                    _api.warn_external(

                        "cmr10 font should ideally be used with "

                        "mathtext, set axes.formatter.use_mathtext to True"

                    )

        else:

            self._useMathText = val



    useMathText = property(fget=get_useMathText, fset=set_useMathText)



    def __call__(self, x, pos=None):

        

        if len(self.locs) == 0:

            return ''

        else:

            xp = (x - self.offset) / (10. ** self.orderOfMagnitude)

            if abs(xp) < 1e-8:

                xp = 0

            return self._format_maybe_minus_and_locale(self.format, xp)



    def set_scientific(self, b):

        

        self._scientific = bool(b)



    def set_powerlimits(self, lims):

        

        if len(lims) != 2:

            raise ValueError("'lims' must be a sequence of length 2")

        self._powerlimits = lims



    def format_data_short(self, value):

                             

        if value is np.ma.masked:

            return ""

        if isinstance(value, Integral):

            fmt = "%d"

        else:

            if getattr(self.axis, "__name__", "") in ["xaxis", "yaxis"]:

                if self.axis.__name__ == "xaxis":

                    axis_trf = self.axis.axes.get_xaxis_transform()

                    axis_inv_trf = axis_trf.inverted()

                    screen_xy = axis_trf.transform((value, 0))

                    neighbor_values = axis_inv_trf.transform(

                        screen_xy + [[-1, 0], [+1, 0]])[:, 0]

                else:          

                    axis_trf = self.axis.axes.get_yaxis_transform()

                    axis_inv_trf = axis_trf.inverted()

                    screen_xy = axis_trf.transform((0, value))

                    neighbor_values = axis_inv_trf.transform(

                        screen_xy + [[0, -1], [0, +1]])[:, 1]

                delta = abs(neighbor_values - value).max()

            else:

                                                                  

                a, b = self.axis.get_view_interval()

                delta = (b - a) / 1e4

            fmt = f"%-#.{cbook._g_sig_digits(value, delta)}g"

        return self._format_maybe_minus_and_locale(fmt, value)



    def format_data(self, value):

                             

        e = math.floor(math.log10(abs(value)))

        s = round(value / 10**e, 10)

        significand = self._format_maybe_minus_and_locale(

            "%d" if s % 1 == 0 else "%1.10g", s)

        if e == 0:

            return significand

        exponent = self._format_maybe_minus_and_locale("%d", e)

        if self._useMathText or self._usetex:

            exponent = "10^{%s}" % exponent

            return (exponent if s == 1                           

                    else rf"{significand} \times {exponent}")

        else:

            return f"{significand}e{exponent}"



    def get_offset(self):

        

        if len(self.locs) == 0:

            return ''

        if self.orderOfMagnitude or self.offset:

            offsetStr = ''

            sciNotStr = ''

            if self.offset:

                offsetStr = self.format_data(self.offset)

                if self.offset > 0:

                    offsetStr = '+' + offsetStr

            if self.orderOfMagnitude:

                if self._usetex or self._useMathText:

                    sciNotStr = self.format_data(10 ** self.orderOfMagnitude)

                else:

                    sciNotStr = '1e%d' % self.orderOfMagnitude

            if self._useMathText or self._usetex:

                if sciNotStr != '':

                    sciNotStr = r'\times\mathdefault{%s}' % sciNotStr

                s = fr'${sciNotStr}\mathdefault{ {offsetStr}} $'

            else:

                s = ''.join((sciNotStr, offsetStr))

            return self.fix_minus(s)

        return ''



    def set_locs(self, locs):

                             

        self.locs = locs

        if len(self.locs) > 0:

            if self._useOffset:

                self._compute_offset()

            self._set_order_of_magnitude()

            self._set_format()



    def _compute_offset(self):

        locs = self.locs

                                    

        vmin, vmax = sorted(self.axis.get_view_interval())

        locs = np.asarray(locs)

        locs = locs[(vmin <= locs) & (locs <= vmax)]

        if not len(locs):

            self.offset = 0

            return

        lmin, lmax = locs.min(), locs.max()

                                                                            

                        

        if lmin == lmax or lmin <= 0 <= lmax:

            self.offset = 0

            return

                                                                               

                                              

        abs_min, abs_max = sorted([abs(float(lmin)), abs(float(lmax))])

        sign = math.copysign(1, lmin)

                                                                             

                                     

                                                                               

                          

        oom_max = np.ceil(math.log10(abs_max))

        oom = 1 + next(oom for oom in itertools.count(oom_max, -1)

                       if abs_min // 10 ** oom != abs_max // 10 ** oom)

        if (abs_max - abs_min) / 10 ** oom <= 1e-2:

                                                                              

                                     

                                                                             

                                                         

            oom = 1 + next(oom for oom in itertools.count(oom_max, -1)

                           if abs_max // 10 ** oom - abs_min // 10 ** oom > 1)

                                                                        

        n = self._offset_threshold - 1

        self.offset = (sign * (abs_max // 10 ** oom) * 10 ** oom

                       if abs_max // 10 ** oom >= 10**n

                       else 0)



    def _set_order_of_magnitude(self):

                                                                             

                                                                           

                                                                             

        if not self._scientific:

            self.orderOfMagnitude = 0

            return

        if self._powerlimits[0] == self._powerlimits[1] != 0:

                                                                

            self.orderOfMagnitude = self._powerlimits[0]

            return

                                   

        vmin, vmax = sorted(self.axis.get_view_interval())

        locs = np.asarray(self.locs)

        locs = locs[(vmin <= locs) & (locs <= vmax)]

        locs = np.abs(locs)

        if not len(locs):

            self.orderOfMagnitude = 0

            return

        if self.offset:

            oom = math.floor(math.log10(vmax - vmin))

        else:

            val = locs.max()

            if val == 0:

                oom = 0

            else:

                oom = math.floor(math.log10(val))

        if oom <= self._powerlimits[0]:

            self.orderOfMagnitude = oom

        elif oom >= self._powerlimits[1]:

            self.orderOfMagnitude = oom

        else:

            self.orderOfMagnitude = 0



    def _set_format(self):

                                                            

        if len(self.locs) < 2:

                                                                         

            _locs = [*self.locs, *self.axis.get_view_interval()]

        else:

            _locs = self.locs

        locs = (np.asarray(_locs) - self.offset) / 10. ** self.orderOfMagnitude

        loc_range = np.ptp(locs)

                                                                 

        if loc_range == 0:

            loc_range = np.max(np.abs(locs))

                                    

        if loc_range == 0:

            loc_range = 1

        if len(self.locs) < 2:

                                                                          

            locs = locs[:-2]

        loc_range_oom = int(math.floor(math.log10(loc_range)))

                         

        sigfigs = max(0, 3 - loc_range_oom)

                           

        thresh = 1e-3 * 10 ** loc_range_oom

        while sigfigs >= 0:

            if np.abs(locs - np.round(locs, decimals=sigfigs)).max() < thresh:

                sigfigs -= 1

            else:

                break

        sigfigs += 1

        self.format = f'%1.{sigfigs}f'

        if self._usetex or self._useMathText:

            self.format = r'$\mathdefault{%s}$' % self.format





class LogFormatter(Formatter):

    



    def __init__(self, base=10.0, labelOnlyBase=False,

                 minor_thresholds=None,

                 linthresh=None):



        self.set_base(base)

        self.set_label_minor(labelOnlyBase)

        if minor_thresholds is None:

            if mpl.rcParams['_internal.classic_mode']:

                minor_thresholds = (0, 0)

            else:

                minor_thresholds = (1, 0.4)

        self.minor_thresholds = minor_thresholds

        self._sublabels = None

        self._linthresh = linthresh



    def set_base(self, base):

        

        self._base = float(base)



    def set_label_minor(self, labelOnlyBase):

        

        self.labelOnlyBase = labelOnlyBase



    def set_locs(self, locs=None):

        

        if np.isinf(self.minor_thresholds[0]):

            self._sublabels = None

            return



                             

        linthresh = self._linthresh

        if linthresh is None:

            try:

                linthresh = self.axis.get_transform().linthresh

            except AttributeError:

                pass



        vmin, vmax = self.axis.get_view_interval()

        if vmin > vmax:

            vmin, vmax = vmax, vmin



        if linthresh is None and vmin <= 0:

                                           

                                                                 

                                                                

            self._sublabels = {1}                        

            return



        b = self._base



        if linthresh is not None:          

                                                                               

            numdec = numticks = 0

            if vmin < -linthresh:

                rhs = min(vmax, -linthresh)

                numticks += (

                    math.floor(math.log(abs(rhs), b))

                    - math.floor(math.nextafter(math.log(abs(vmin), b), -math.inf)))

                numdec += math.log(vmin / rhs, b)

            if vmax > linthresh:

                lhs = max(vmin, linthresh)

                numticks += (

                    math.floor(math.log(vmax, b))

                    - math.floor(math.nextafter(math.log(lhs, b), -math.inf)))

                numdec += math.log(vmax / lhs, b)

        else:

            lmin = math.log(vmin, b)

            lmax = math.log(vmax, b)

                                                                            

                                                                   

            numticks = (math.floor(lmax)

                        - math.floor(math.nextafter(lmin, -math.inf)))

            numdec = abs(lmax - lmin)



        if numticks > self.minor_thresholds[0]:

                              

            self._sublabels = {1}

        elif numdec > self.minor_thresholds[1]:

                                                                  

                                                               

                                                         

            c = np.geomspace(1, b, int(b)//2 + 1)

            self._sublabels = set(np.round(c))

                                                           

        else:

                                                     

            self._sublabels = set(np.arange(1, b + 1))



    def _num_to_string(self, x, vmin, vmax):

        return self._pprint_val(x, vmax - vmin) if 1 <= x <= 10000 else f"{x:1.0e}"



    def __call__(self, x, pos=None):

                             

        if x == 0.0:          

            return '0'



        x = abs(x)

        b = self._base

                                

        fx = math.log(x) / math.log(b)

        is_x_decade = _is_close_to_int(fx)

        exponent = round(fx) if is_x_decade else np.floor(fx)

        coeff = round(b ** (fx - exponent))



        if self.labelOnlyBase and not is_x_decade:

            return ''

        if self._sublabels is not None and coeff not in self._sublabels:

            return ''



        vmin, vmax = self.axis.get_view_interval()

        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander=0.05)

        s = self._num_to_string(x, vmin, vmax)

        return self.fix_minus(s)



    def format_data(self, value):

        with cbook._setattr_cm(self, labelOnlyBase=False):

            return cbook.strip_math(self.__call__(value))



    def format_data_short(self, value):

                             

        return ('%-12g' % value).rstrip()



    def _pprint_val(self, x, d):

                                                                            

        if abs(x) < 1e4 and x == int(x):

            return '%d' % x

        fmt = ('%1.3e' if d < 1e-2 else

               '%1.3f' if d <= 1 else

               '%1.2f' if d <= 10 else

               '%1.1f' if d <= 1e5 else

               '%1.1e')

        s = fmt % x

        tup = s.split('e')

        if len(tup) == 2:

            mantissa = tup[0].rstrip('0').rstrip('.')

            exponent = int(tup[1])

            if exponent:

                s = '%se%d' % (mantissa, exponent)

            else:

                s = mantissa

        else:

            s = s.rstrip('0').rstrip('.')

        return s





class LogFormatterExponent(LogFormatter):

    



    def _num_to_string(self, x, vmin, vmax):

        fx = math.log(x) / math.log(self._base)

        if 1 <= abs(fx) <= 10000:

            fd = math.log(vmax - vmin) / math.log(self._base)

            s = self._pprint_val(fx, fd)

        else:

            s = f"{fx:1.0g}"

        return s





class LogFormatterMathtext(LogFormatter):

    



    def _non_decade_format(self, sign_string, base, fx, usetex):

        

        return r'$\mathdefault{%s%s^{%.2f}}$' % (sign_string, base, fx)



    def __call__(self, x, pos=None):

                             

        if x == 0:          

            return r'$\mathdefault{0}$'



        sign_string = '-' if x < 0 else ''

        x = abs(x)

        b = self._base



                                

        fx = math.log(x) / math.log(b)

        is_x_decade = _is_close_to_int(fx)

        exponent = round(fx) if is_x_decade else np.floor(fx)

        coeff = round(b ** (fx - exponent))



        if self.labelOnlyBase and not is_x_decade:

            return ''

        if self._sublabels is not None and coeff not in self._sublabels:

            return ''



        if is_x_decade:

            fx = round(fx)



                                                                   

        if b % 1 == 0.0:

            base = '%d' % b

        else:

            base = '%s' % b



        if abs(fx) < mpl.rcParams['axes.formatter.min_exponent']:

            return r'$\mathdefault{%s%g}$' % (sign_string, x)

        elif not is_x_decade:

            usetex = mpl.rcParams['text.usetex']

            return self._non_decade_format(sign_string, base, fx, usetex)

        else:

            return r'$\mathdefault{%s%s^{%d}}$' % (sign_string, base, fx)





class LogFormatterSciNotation(LogFormatterMathtext):

    



    def _non_decade_format(self, sign_string, base, fx, usetex):

        

        b = float(base)

        exponent = math.floor(fx)

        coeff = b ** (fx - exponent)

        if _is_close_to_int(coeff):

            coeff = round(coeff)

        return r'$\mathdefault{%s%g\times%s^{%d}}$'
            % (sign_string, coeff, base, exponent)





class LogitFormatter(Formatter):

    



    def __init__(

        self,

        *,

        use_overline=False,

        one_half=r"\frac{1}{2}",

        minor=False,

        minor_threshold=25,

        minor_number=6,

    ):

        

        self._use_overline = use_overline

        self._one_half = one_half

        self._minor = minor

        self._labelled = set()

        self._minor_threshold = minor_threshold

        self._minor_number = minor_number



    def use_overline(self, use_overline):

        

        self._use_overline = use_overline



    def set_one_half(self, one_half):

        

        self._one_half = one_half



    def set_minor_threshold(self, minor_threshold):

        

        self._minor_threshold = minor_threshold



    def set_minor_number(self, minor_number):

        

        self._minor_number = minor_number



    def set_locs(self, locs):

        self.locs = np.array(locs)

        self._labelled.clear()



        if not self._minor:

            return None

        if all(

            _is_decade(x, rtol=1e-7)

            or _is_decade(1 - x, rtol=1e-7)

            or (_is_close_to_int(2 * x) and

                int(np.round(2 * x)) == 1)

            for x in locs

        ):

                                                               

            return None

        if len(locs) < self._minor_threshold:

            if len(locs) < self._minor_number:

                self._labelled.update(locs)

            else:

                                                                              

                                                                               

                                                                           

                                                   

                                                                              

                                                                             

                                                                          

                                              

                diff = np.diff(-np.log(1 / self.locs - 1))

                space_pessimistic = np.minimum(

                    np.concatenate(((np.inf,), diff)),

                    np.concatenate((diff, (np.inf,))),

                )

                space_sum = (

                    np.concatenate(((0,), diff))

                    + np.concatenate((diff, (0,)))

                )

                good_minor = sorted(

                    range(len(self.locs)),

                    key=lambda i: (space_pessimistic[i], space_sum[i]),

                )[-self._minor_number:]

                self._labelled.update(locs[i] for i in good_minor)



    def _format_value(self, x, locs, sci_notation=True):

        if sci_notation:

            exponent = math.floor(np.log10(x))

            min_precision = 0

        else:

            exponent = 0

            min_precision = 1

        value = x * 10 ** (-exponent)

        if len(locs) < 2:

            precision = min_precision

        else:

            diff = np.sort(np.abs(locs - x))[1]

            precision = -np.log10(diff) + exponent

            precision = (

                int(np.round(precision))

                if _is_close_to_int(precision)

                else math.ceil(precision)

            )

            if precision < min_precision:

                precision = min_precision

        mantissa = r"%.*f" % (precision, value)

        if not sci_notation:

            return mantissa

        s = r"%s\cdot10^{%d}" % (mantissa, exponent)

        return s



    def _one_minus(self, s):

        if self._use_overline:

            return r"\overline{%s}" % s

        else:

            return f"1-{s}"



    def __call__(self, x, pos=None):

        if self._minor and x not in self._labelled:

            return ""

        if x <= 0 or x >= 1:

            return ""

        if _is_close_to_int(2 * x) and round(2 * x) == 1:

            s = self._one_half

        elif x < 0.5 and _is_decade(x, rtol=1e-7):

            exponent = round(math.log10(x))

            s = "10^{%d}" % exponent

        elif x > 0.5 and _is_decade(1 - x, rtol=1e-7):

            exponent = round(math.log10(1 - x))

            s = self._one_minus("10^{%d}" % exponent)

        elif x < 0.1:

            s = self._format_value(x, self.locs)

        elif x > 0.9:

            s = self._one_minus(self._format_value(1-x, 1-self.locs))

        else:

            s = self._format_value(x, self.locs, sci_notation=False)

        return r"$\mathdefault{%s}$" % s



    def format_data_short(self, value):

                             

                                                                          

        if value < 0.1:

            return f"{value:e}"

        if value < 0.9:

            return f"{value:f}"

        return f"1-{1 - value:e}"





class EngFormatter(ScalarFormatter):

    



                                 

    ENG_PREFIXES = {

        -30: "q",

        -27: "r",

        -24: "y",

        -21: "z",

        -18: "a",

        -15: "f",

        -12: "p",

         -9: "n",

         -6: "\N{MICRO SIGN}",

         -3: "m",

          0: "",

          3: "k",

          6: "M",

          9: "G",

         12: "T",

         15: "P",

         18: "E",

         21: "Z",

         24: "Y",

         27: "R",

         30: "Q"

    }



    def __init__(self, unit="", places=None, sep=" ", *, usetex=None,

                 useMathText=None, useOffset=False):

        

        self.unit = unit

        self.places = places

        self.sep = sep

        super().__init__(

            useOffset=useOffset,

            useMathText=useMathText,

            useLocale=False,

            usetex=usetex,

        )



    def __call__(self, x, pos=None):

        

        if len(self.locs) == 0 or self.offset == 0:

            return self.fix_minus(self.format_data(x))

        else:

            xp = (x - self.offset) / (10. ** self.orderOfMagnitude)

            if abs(xp) < 1e-8:

                xp = 0

            return self._format_maybe_minus_and_locale(self.format, xp)



    def set_locs(self, locs):

                             

        self.locs = locs

        if len(self.locs) > 0:

            vmin, vmax = sorted(self.axis.get_view_interval())

            if self._useOffset:

                self._compute_offset()

                if self.offset != 0:

                                                                 

                                                                               

                                                                          

                                                                           

                                                                       

                                                                           

                            

                    self.offset = round((vmin + vmax)/2, 3)

                                                         

            self.orderOfMagnitude = math.floor(math.log(vmax - vmin, 1000))*3

            self._set_format()



                                                                      

                                                                               

                                                                             

                                                                           

                          

    def get_offset(self):

                             

        if len(self.locs) == 0:

            return ''

        if self.offset:

            offsetStr = ''

            if self.offset:

                offsetStr = self.format_data(self.offset)

                if self.offset > 0:

                    offsetStr = '+' + offsetStr

            sciNotStr = self.format_data(10 ** self.orderOfMagnitude)

            if self._useMathText or self._usetex:

                if sciNotStr != '':

                    sciNotStr = r'\times%s' % sciNotStr

                s = f'${sciNotStr}{offsetStr}$'

            else:

                s = sciNotStr + offsetStr

            return self.fix_minus(s)

        return ''



    def format_eng(self, num):

        

        return self.format_data(num)



    def format_data(self, value):

        

        sign = 1

        fmt = "g" if self.places is None else f".{self.places:d}f"



        if value < 0:

            sign = -1

            value = -value



        if value != 0:

            pow10 = int(math.floor(math.log10(value) / 3) * 3)

        else:

            pow10 = 0

                                                                

                                                            

                                           

            value = 0.0



        pow10 = np.clip(pow10, min(self.ENG_PREFIXES), max(self.ENG_PREFIXES))



        mant = sign * value / (10.0 ** pow10)

                                                                              

                                                                              

                                                

        if (abs(float(format(mant, fmt))) >= 1000

                and pow10 < max(self.ENG_PREFIXES)):

            mant /= 1000

            pow10 += 3



        unit_prefix = self.ENG_PREFIXES[int(pow10)]

        if self.unit or unit_prefix:

            suffix = f"{self.sep}{unit_prefix}{self.unit}"

        else:

            suffix = ""

        if self._usetex or self._useMathText:

            return f"${mant:{fmt}}${suffix}"

        else:

            return f"{mant:{fmt}}{suffix}"





class PercentFormatter(Formatter):

    

    def __init__(self, xmax=100, decimals=None, symbol='%', is_latex=False):

        self.xmax = xmax + 0.0

        self.decimals = decimals

        self._symbol = symbol

        self._is_latex = is_latex



    def __call__(self, x, pos=None):

        

        ax_min, ax_max = self.axis.get_view_interval()

        display_range = abs(ax_max - ax_min)

        return self.fix_minus(self.format_pct(x, display_range))



    def format_pct(self, x, display_range):

        

        x = self.convert_to_pct(x)

        if self.decimals is None:

                                                                    

            scaled_range = self.convert_to_pct(display_range)

            if scaled_range <= 0:

                decimals = 0

            else:

                                                                              

                                                                              

                                                                         

                                                                            

                decimals = math.ceil(2.0 - math.log10(2.0 * scaled_range))

                if decimals > 5:

                    decimals = 5

                elif decimals < 0:

                    decimals = 0

        else:

            decimals = self.decimals

        s = f'{x:0.{int(decimals)}f}'



        return s + self.symbol



    def convert_to_pct(self, x):

        return 100.0 * (x / self.xmax)



    @property

    def symbol(self):

        

        symbol = self._symbol

        if not symbol:

            symbol = ''

        elif not self._is_latex and mpl.rcParams['text.usetex']:

                                                                 

                                                                      

                                       

            for spec in r'\#$%&~_^{}':

                symbol = symbol.replace(spec, '\\' + spec)

        return symbol



    @symbol.setter

    def symbol(self, symbol):

        self._symbol = symbol





class Locator(TickHelper):

    



                                                                  

                                                    

                                                                      

                               

    MAXTICKS = 1000



    def tick_values(self, vmin, vmax):

        

        raise NotImplementedError('Derived must override')



    def set_params(self, **kwargs):

        

        _api.warn_external(

            "'set_params()' not defined for locator of type " +

            str(type(self)))



    def __call__(self):

        

                                                                           

                                                                     

        raise NotImplementedError('Derived must override')



    def raise_if_exceeds(self, locs):

        

        if len(locs) >= self.MAXTICKS:

            _log.warning(

                "Locator attempting to generate %s ticks ([%s, ..., %s]), "

                "which exceeds Locator.MAXTICKS (%s).",

                len(locs), locs[0], locs[-1], self.MAXTICKS)

        return locs



    def nonsingular(self, v0, v1):

        

        return mtransforms.nonsingular(v0, v1, expander=.05)



    def view_limits(self, vmin, vmax):

        

        return mtransforms.nonsingular(vmin, vmax)





class IndexLocator(Locator):

    



    def __init__(self, base, offset):

        

        self._base = base

        self.offset = offset



    def set_params(self, base=None, offset=None):

        

        if base is not None:

            self._base = base

        if offset is not None:

            self.offset = offset



    def __call__(self):

        

        dmin, dmax = self.axis.get_data_interval()

        return self.tick_values(dmin, dmax)



    def tick_values(self, vmin, vmax):

        return self.raise_if_exceeds(

            np.arange(vmin + self.offset, vmax + 1, self._base))





class FixedLocator(Locator):

    



    def __init__(self, locs, nbins=None):

        self.locs = np.asarray(locs)

        _api.check_shape((None,), locs=self.locs)

        self.nbins = max(nbins, 2) if nbins is not None else None



    def set_params(self, nbins=None):

        

        if nbins is not None:

            self.nbins = nbins



    def __call__(self):

        return self.tick_values(None, None)



    def tick_values(self, vmin, vmax):

        

        if self.nbins is None:

            return self.locs

        step = max(int(np.ceil(len(self.locs) / self.nbins)), 1)

        ticks = self.locs[::step]

        for i in range(1, step):

            ticks1 = self.locs[i::step]

            if np.abs(ticks1).min() < np.abs(ticks).min():

                ticks = ticks1

        return self.raise_if_exceeds(ticks)





class NullLocator(Locator):

    



    def __call__(self):

        return self.tick_values(None, None)



    def tick_values(self, vmin, vmax):

        

        return []





class LinearLocator(Locator):

    



    def __init__(self, numticks=None, presets=None):

        

        self.numticks = numticks

        if presets is None:

            self.presets = {}

        else:

            self.presets = presets



    @property

    def numticks(self):

                                 

        return self._numticks if self._numticks is not None else 11



    @numticks.setter

    def numticks(self, numticks):

        self._numticks = numticks



    def set_params(self, numticks=None, presets=None):

        

        if presets is not None:

            self.presets = presets

        if numticks is not None:

            self.numticks = numticks



    def __call__(self):

        

        vmin, vmax = self.axis.get_view_interval()

        return self.tick_values(vmin, vmax)



    def tick_values(self, vmin, vmax):

        vmin, vmax = mtransforms.nonsingular(vmin, vmax, expander=0.05)



        if (vmin, vmax) in self.presets:

            return self.presets[(vmin, vmax)]



        if self.numticks == 0:

            return []

        ticklocs = np.linspace(vmin, vmax, self.numticks)



        return self.raise_if_exceeds(ticklocs)



    def view_limits(self, vmin, vmax):

        



        if vmax < vmin:

            vmin, vmax = vmax, vmin



        if vmin == vmax:

            vmin -= 1

            vmax += 1



        if mpl.rcParams['axes.autolimit_mode'] == 'round_numbers':

            exponent, remainder = divmod(

                math.log10(vmax - vmin), math.log10(max(self.numticks - 1, 1)))

            exponent -= (remainder < .5)

            scale = max(self.numticks - 1, 1) ** (-exponent)

            vmin = math.floor(scale * vmin) / scale

            vmax = math.ceil(scale * vmax) / scale



        return mtransforms.nonsingular(vmin, vmax)





class MultipleLocator(Locator):

    



    def __init__(self, base=1.0, offset=0.0):

        

        self._edge = _Edge_integer(base, 0)

        self._offset = offset



    def set_params(self, base=None, offset=None):

        

        if base is not None:

            self._edge = _Edge_integer(base, 0)

        if offset is not None:

            self._offset = offset



    def __call__(self):

        

        vmin, vmax = self.axis.get_view_interval()

        return self.tick_values(vmin, vmax)



    def tick_values(self, vmin, vmax):

        if vmax < vmin:

            vmin, vmax = vmax, vmin

        step = self._edge.step

        vmin -= self._offset

        vmax -= self._offset

        vmin = self._edge.ge(vmin) * step

        n = (vmax - vmin + 0.001 * step) // step

        locs = vmin - step + np.arange(n + 3) * step + self._offset

        return self.raise_if_exceeds(locs)



    def view_limits(self, dmin, dmax):

        

        if mpl.rcParams['axes.autolimit_mode'] == 'round_numbers':

            vmin = self._edge.le(dmin - self._offset) * self._edge.step + self._offset

            vmax = self._edge.ge(dmax - self._offset) * self._edge.step + self._offset

            if vmin == vmax:

                vmin -= 1

                vmax += 1

        else:

            vmin = dmin

            vmax = dmax



        return mtransforms.nonsingular(vmin, vmax)





def scale_range(vmin, vmax, n=1, threshold=100):

    dv = abs(vmax - vmin)                                        

    meanv = (vmax + vmin) / 2

    if abs(meanv) / dv < threshold:

        offset = 0

    else:

        offset = math.copysign(10 ** (math.log10(abs(meanv)) // 1), meanv)

    scale = 10 ** (math.log10(dv / n) // 1)

    return scale, offset





class _Edge_integer:

    



    def __init__(self, step, offset):

        

        if step <= 0:

            raise ValueError("'step' must be positive")

        self.step = step

        self._offset = abs(offset)



    def closeto(self, ms, edge):

                                                                        

        if self._offset > 0:

            digits = np.log10(self._offset / self.step)

            tol = max(1e-10, 10 ** (digits - 12))

            tol = min(0.4999, tol)

        else:

            tol = 1e-10

        return abs(ms - edge) < tol



    def le(self, x):

        

        d, m = divmod(x, self.step)

        if self.closeto(m / self.step, 1):

            return d + 1

        return d



    def ge(self, x):

        

        d, m = divmod(x, self.step)

        if self.closeto(m / self.step, 0):

            return d

        return d + 1





class MaxNLocator(Locator):

    

    default_params = dict(nbins=10,

                          steps=None,

                          integer=False,

                          symmetric=False,

                          prune=None,

                          min_n_ticks=2)



    def __init__(self, nbins=None, **kwargs):

        

        if nbins is not None:

            kwargs['nbins'] = nbins

        self.set_params(**{**self.default_params, **kwargs})



    @staticmethod

    def _validate_steps(steps):

        if not np.iterable(steps):

            raise ValueError('steps argument must be an increasing sequence '

                             'of numbers between 1 and 10 inclusive')

        steps = np.asarray(steps)

        if np.any(np.diff(steps) <= 0) or steps[-1] > 10 or steps[0] < 1:

            raise ValueError('steps argument must be an increasing sequence '

                             'of numbers between 1 and 10 inclusive')

        if steps[0] != 1:

            steps = np.concatenate([[1], steps])

        if steps[-1] != 10:

            steps = np.concatenate([steps, [10]])

        return steps



    @staticmethod

    def _staircase(steps):

                                                                         

                                                              

        return np.concatenate([0.1 * steps[:-1], steps, [10 * steps[1]]])



    def set_params(self, **kwargs):

        

        if 'nbins' in kwargs:

            self._nbins = kwargs.pop('nbins')

            if self._nbins != 'auto':

                self._nbins = int(self._nbins)

        if 'symmetric' in kwargs:

            self._symmetric = kwargs.pop('symmetric')

        if 'prune' in kwargs:

            prune = kwargs.pop('prune')

            _api.check_in_list(['upper', 'lower', 'both', None], prune=prune)

            self._prune = prune

        if 'min_n_ticks' in kwargs:

            self._min_n_ticks = max(1, kwargs.pop('min_n_ticks'))

        if 'steps' in kwargs:

            steps = kwargs.pop('steps')

            if steps is None:

                self._steps = np.array([1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10])

            else:

                self._steps = self._validate_steps(steps)

            self._extended_steps = self._staircase(self._steps)

        if 'integer' in kwargs:

            self._integer = kwargs.pop('integer')

        if kwargs:

            raise _api.kwarg_error("set_params", kwargs)



    def _raw_ticks(self, vmin, vmax):

        

        if self._nbins == 'auto':

            if self.axis is not None:

                nbins = np.clip(self.axis.get_tick_space(),

                                max(1, self._min_n_ticks - 1), 9)

            else:

                nbins = 9

        else:

            nbins = self._nbins



        scale, offset = scale_range(vmin, vmax, nbins)

        _vmin = vmin - offset

        _vmax = vmax - offset

        steps = self._extended_steps * scale

        if self._integer:

                                                      

            igood = (steps < 1) | (np.abs(steps - np.round(steps)) < 0.001)

            steps = steps[igood]



        raw_step = ((_vmax - _vmin) / nbins)

        if hasattr(self.axis, "axes") and self.axis.axes.name == '3d':

                                                                            

                                                                          

                                                          

            raw_step = raw_step * 23/24

        large_steps = steps >= raw_step

        if mpl.rcParams['axes.autolimit_mode'] == 'round_numbers':

                                                                   

                                                           

            floored_vmins = (_vmin // steps) * steps

            floored_vmaxs = floored_vmins + steps * nbins

            large_steps = large_steps & (floored_vmaxs >= _vmax)



                                           

        if any(large_steps):

            istep = np.nonzero(large_steps)[0][0]

        else:

            istep = len(steps) - 1



                                                                             

                                                                     

                                                                      

        for step in steps[:istep+1][::-1]:



            if (self._integer and

                    np.floor(_vmax) - np.ceil(_vmin) >= self._min_n_ticks - 1):

                step = max(1, step)

            best_vmin = (_vmin // step) * step



                                                                           

                                                                            

                                                                       

                                             

            edge = _Edge_integer(step, offset)

            low = edge.le(_vmin - best_vmin)

            high = edge.ge(_vmax - best_vmin)

            ticks = np.arange(low, high + 1) * step + best_vmin

                                                          

            nticks = ((ticks <= _vmax) & (ticks >= _vmin)).sum()

            if nticks >= self._min_n_ticks:

                break

        return ticks + offset



    def __call__(self):

        vmin, vmax = self.axis.get_view_interval()

        return self.tick_values(vmin, vmax)



    def tick_values(self, vmin, vmax):

        if self._symmetric:

            vmax = max(abs(vmin), abs(vmax))

            vmin = -vmax

        vmin, vmax = mtransforms.nonsingular(

            vmin, vmax, expander=1e-13, tiny=1e-14)

        locs = self._raw_ticks(vmin, vmax)



        prune = self._prune

        if prune == 'lower':

            locs = locs[1:]

        elif prune == 'upper':

            locs = locs[:-1]

        elif prune == 'both':

            locs = locs[1:-1]

        return self.raise_if_exceeds(locs)



    def view_limits(self, dmin, dmax):

        if self._symmetric:

            dmax = max(abs(dmin), abs(dmax))

            dmin = -dmax



        dmin, dmax = mtransforms.nonsingular(

            dmin, dmax, expander=1e-12, tiny=1e-13)



        if mpl.rcParams['axes.autolimit_mode'] == 'round_numbers':

            return self._raw_ticks(dmin, dmax)[[0, -1]]

        else:

            return dmin, dmax





def _is_decade(x, *, base=10, rtol=None):

    

    if not np.isfinite(x):

        return False

    if x == 0.0:

        return True

    lx = np.log(abs(x)) / np.log(base)

    if rtol is None:

        return np.isclose(lx, np.round(lx))

    else:

        return np.isclose(lx, np.round(lx), rtol=rtol)





def _decade_less_equal(x, base):

    

    return (x if x == 0 else

            -_decade_greater_equal(-x, base) if x < 0 else

            base ** np.floor(np.log(x) / np.log(base)))





def _decade_greater_equal(x, base):

    

    return (x if x == 0 else

            -_decade_less_equal(-x, base) if x < 0 else

            base ** np.ceil(np.log(x) / np.log(base)))





def _decade_less(x, base):

    

    if x < 0:

        return -_decade_greater(-x, base)

    less = _decade_less_equal(x, base)

    if less == x:

        less /= base

    return less





def _decade_greater(x, base):

    

    if x < 0:

        return -_decade_less(-x, base)

    greater = _decade_greater_equal(x, base)

    if greater == x:

        greater *= base

    return greater





def _is_close_to_int(x):

    return math.isclose(x, round(x))





class LogLocator(Locator):

    



    def __init__(self, base=10.0, subs=(1.0,), *, numticks=None):

        

        if numticks is None:

            if mpl.rcParams['_internal.classic_mode']:

                numticks = 15

            else:

                numticks = 'auto'

        self._base = float(base)

        self._set_subs(subs)

        self.numticks = numticks



    def set_params(self, base=None, subs=None, *, numticks=None):

        

        if base is not None:

            self._base = float(base)

        if subs is not None:

            self._set_subs(subs)

        if numticks is not None:

            self.numticks = numticks



    def _set_subs(self, subs):

        

        if subs is None:                                     

            self._subs = 'auto'

        elif isinstance(subs, str):

            _api.check_in_list(('all', 'auto'), subs=subs)

            self._subs = subs

        else:

            try:

                self._subs = np.asarray(subs, dtype=float)

            except ValueError as e:

                raise ValueError("subs must be None, 'all', 'auto' or "

                                 "a sequence of floats, not "

                                 f"{subs}.") from e

            if self._subs.ndim != 1:

                raise ValueError("A sequence passed to subs must be "

                                 "1-dimensional, not "

                                 f"{self._subs.ndim}-dimensional.")



    def __call__(self):

        

        vmin, vmax = self.axis.get_view_interval()

        return self.tick_values(vmin, vmax)



    def _log_b(self, x):

                                                                              

                                                                             

                               

        return (np.log10(x) if self._base == 10 else

                np.log2(x) if self._base == 2 else

                np.log(x) / np.log(self._base))



    def tick_values(self, vmin, vmax):

        n_request = (

            self.numticks if self.numticks != "auto" else

            np.clip(self.axis.get_tick_space(), 2, 9) if self.axis is not None else

            9)



        b = self._base

        if vmin <= 0.0:

            if self.axis is not None:

                vmin = self.axis.get_minpos()



            if vmin <= 0.0 or not np.isfinite(vmin):

                raise ValueError(

                    "Data has no positive values, and therefore cannot be log-scaled.")



        if vmax < vmin:

            vmin, vmax = vmax, vmin

                                                                              

                                                                            

        efmin, efmax = self._log_b([vmin, vmax])

        emin = math.ceil(efmin)

        emax = math.floor(efmax)

        n_avail = emax - emin + 1                                           



        if isinstance(self._subs, str):

            if n_avail >= 10 or b < 3:

                if self._subs == 'auto':

                    return np.array([])                           

                else:

                    subs = np.array([1.0])               

            else:

                _first = 2.0 if self._subs == 'auto' else 1.0

                subs = np.arange(_first, b)

        else:

            subs = self._subs



                                                                             

                                                                            

        if mpl.rcParams["_internal.classic_mode"]:                          

            stride = max(math.ceil((n_avail - 1) / (n_request - 1)), 1)

            decades = np.arange(emin - stride, emax + stride + 1, stride)

        else:

                                                                             

                                                                            

                                                                      

                                                                            

                                                                        

                                                                            

                                                                            

                                                                             

                                                                              

            stride = n_avail // (n_request + 1) + 1

            nr = math.ceil(n_avail / stride)

            if nr <= n_request:

                n_request = nr

            else:

                assert nr == n_request + 1

            if n_request == 0:                                              

                decades = [emin - 1, emax + 1]

                stride = decades[1] - decades[0]

            elif n_request == 1:                                  

                mid = round((efmin + efmax) / 2)

                stride = max(mid - (emin - 1), (emax + 1) - mid)

                decades = [mid - stride, mid, mid + stride]

            else:

                                                                             

                                                                          

                                                                         

                                                                       

                                                       

                      

                                                                         

                                  

                                                        

                      

                                                                         

                                                                             

                                             

                stride = (n_avail - 1) // (n_request - 1)

                if stride < n_avail / n_request:                           

                    stride = n_avail // n_request

                                                                         

                                                                       

                                                                           

                                                                         

                                       

                olo = max(n_avail - stride * n_request, 0)

                ohi = min(n_avail - stride * (n_request - 1), stride)

                                                                          

                                                                             

                                                                            

                offset = (-emin) % stride

                if not olo <= offset < ohi:

                    offset = olo

                decades = range(emin + offset - stride, emax + stride + 1, stride)



                                                                            

                                

        is_minor = len(subs) > 1 or (len(subs) == 1 and subs[0] != 1.0)

        if is_minor:

            if stride == 1 or n_avail <= 1:

                                                                                 

                ticklocs = np.concatenate([

                    subs * b**decade for decade in range(emin - 1, emax + 1)])

            else:

                ticklocs = np.array([])

        else:

            ticklocs = b ** np.array(decades)



        if (len(subs) > 1

                and stride == 1

                and (len(decades) - 2         

                     + ((vmin <= ticklocs) & (ticklocs <= vmax)).sum())         

                     <= 1):

                                                                           

                                                                           

                                                                  

            return AutoLocator().tick_values(vmin, vmax)

        else:

            return self.raise_if_exceeds(ticklocs)



    def view_limits(self, vmin, vmax):

        

        b = self._base



        vmin, vmax = self.nonsingular(vmin, vmax)



        if mpl.rcParams['axes.autolimit_mode'] == 'round_numbers':

            vmin = _decade_less_equal(vmin, b)

            vmax = _decade_greater_equal(vmax, b)



        return vmin, vmax



    def nonsingular(self, vmin, vmax):

        if vmin > vmax:

            vmin, vmax = vmax, vmin

        if not np.isfinite(vmin) or not np.isfinite(vmax):

            vmin, vmax = 1, 10                                       

        elif vmax <= 0:

            _api.warn_external(

                "Data has no positive values, and therefore cannot be "

                "log-scaled.")

            vmin, vmax = 1, 10

        else:

                                    

            minpos = min(axis.get_minpos() for axis in self.axis._get_shared_axis())

            if not np.isfinite(minpos):

                minpos = 1e-300                                  

            if vmin <= 0:

                vmin = minpos

            if vmin == vmax:

                vmin = _decade_less(vmin, self._base)

                vmax = _decade_greater(vmax, self._base)

        return vmin, vmax





class SymmetricalLogLocator(Locator):

    



    def __init__(self, transform=None, subs=None, linthresh=None, base=None):

        

        if transform is not None:

            self._base = transform.base

            self._linthresh = transform.linthresh

        elif linthresh is not None and base is not None:

            self._base = base

            self._linthresh = linthresh

        else:

            raise ValueError("Either transform, or both linthresh "

                             "and base, must be provided.")

        if subs is None:

            self._subs = [1.0]

        else:

            self._subs = subs

        self.numticks = 15



    def set_params(self, subs=None, numticks=None):

        

        if numticks is not None:

            self.numticks = numticks

        if subs is not None:

            self._subs = subs



    def __call__(self):

        

                                                   

        vmin, vmax = self.axis.get_view_interval()

        return self.tick_values(vmin, vmax)



    def tick_values(self, vmin, vmax):

        linthresh = self._linthresh



        if vmax < vmin:

            vmin, vmax = vmax, vmin



                                                                 

                                        

         

                                        

                                        

         

                                                                   

                                                               

                                     

         

                                                               

                                                                  

                                      

         

                                                                    

                        

         

                                                                       

                                                    

        if -linthresh <= vmin < vmax <= linthresh:

                                              

            return sorted({vmin, 0, vmax})



                                    

        has_a = (vmin < -linthresh)

                                    

        has_c = (vmax > linthresh)



                                          

        has_b = (has_a and vmax > -linthresh) or (has_c and vmin < linthresh)



        base = self._base



        def get_log_range(lo, hi):

            lo = np.floor(np.log(lo) / np.log(base))

            hi = np.ceil(np.log(hi) / np.log(base))

            return lo, hi



                                                                

        a_lo, a_hi = (0, 0)

        if has_a:

            a_upper_lim = min(-linthresh, vmax)

            a_lo, a_hi = get_log_range(abs(a_upper_lim), abs(vmin) + 1)



        c_lo, c_hi = (0, 0)

        if has_c:

            c_lower_lim = max(linthresh, vmin)

            c_lo, c_hi = get_log_range(c_lower_lim, vmax + 1)



                                                                           

        total_ticks = (a_hi - a_lo) + (c_hi - c_lo)

        if has_b:

            total_ticks += 1

        stride = max(total_ticks // (self.numticks - 1), 1)



        decades = []

        if has_a:

            decades.extend(-1 * (base ** (np.arange(a_lo, a_hi,

                                                    stride)[::-1])))



        if has_b:

            decades.append(0.0)



        if has_c:

            decades.extend(base ** (np.arange(c_lo, c_hi, stride)))



        subs = np.asarray(self._subs)



        if len(subs) > 1 or subs[0] != 1.0:

            ticklocs = []

            for decade in decades:

                if decade == 0:

                    ticklocs.append(decade)

                else:

                    ticklocs.extend(subs * decade)

        else:

            ticklocs = decades



        return self.raise_if_exceeds(np.array(ticklocs))



    def view_limits(self, vmin, vmax):

        

        b = self._base

        if vmax < vmin:

            vmin, vmax = vmax, vmin



        if mpl.rcParams['axes.autolimit_mode'] == 'round_numbers':

            vmin = _decade_less_equal(vmin, b)

            vmax = _decade_greater_equal(vmax, b)

            if vmin == vmax:

                vmin = _decade_less(vmin, b)

                vmax = _decade_greater(vmax, b)



        return mtransforms.nonsingular(vmin, vmax)





class AsinhLocator(Locator):

    

    def __init__(self, linear_width, numticks=11, symthresh=0.2,

                 base=10, subs=None):

        

        super().__init__()

        self.linear_width = linear_width

        self.numticks = numticks

        self.symthresh = symthresh

        self.base = base

        self.subs = subs



    def set_params(self, numticks=None, symthresh=None,

                   base=None, subs=None):

        

        if numticks is not None:

            self.numticks = numticks

        if symthresh is not None:

            self.symthresh = symthresh

        if base is not None:

            self.base = base

        if subs is not None:

            self.subs = subs if len(subs) > 0 else None



    def __call__(self):

        vmin, vmax = self.axis.get_view_interval()

        if (vmin * vmax) < 0 and abs(1 + vmax / vmin) < self.symthresh:

                                                                     

            bound = max(abs(vmin), abs(vmax))

            return self.tick_values(-bound, bound)

        else:

            return self.tick_values(vmin, vmax)



    def tick_values(self, vmin, vmax):

                                                                    

        ymin, ymax = self.linear_width * np.arcsinh(np.array([vmin, vmax])

                                                    / self.linear_width)

        ys = np.linspace(ymin, ymax, self.numticks)

        zero_dev = abs(ys / (ymax - ymin))

        if ymin * ymax < 0:

                                                                                     

            ys = np.hstack([ys[(zero_dev > 0.5 / self.numticks)], 0.0])



                                                           

        xs = self.linear_width * np.sinh(ys / self.linear_width)

        zero_xs = (ys == 0)



                                                                                      

                                                                                        

        with np.errstate(divide="ignore"):                                      

            if self.base > 1:

                pows = (np.sign(xs)

                        * self.base ** np.floor(np.log(abs(xs)) / math.log(self.base)))

                qs = np.outer(pows, self.subs).flatten() if self.subs else pows

            else:                                                                      

                pows = np.where(zero_xs, 1, 10**np.floor(np.log10(abs(xs))))

                qs = pows * np.round(xs / pows)

        ticks = np.array(sorted(set(qs)))



        return ticks if len(ticks) >= 2 else np.linspace(vmin, vmax, self.numticks)





class LogitLocator(MaxNLocator):

    



    def __init__(self, minor=False, *, nbins="auto"):

        



        self._minor = minor

        super().__init__(nbins=nbins, steps=[1, 2, 5, 10])



    def set_params(self, minor=None, **kwargs):

        

        if minor is not None:

            self._minor = minor

        super().set_params(**kwargs)



    @property

    def minor(self):

        return self._minor



    @minor.setter

    def minor(self, value):

        self.set_params(minor=value)



    def tick_values(self, vmin, vmax):

                                          

        if hasattr(self.axis, "axes") and self.axis.axes.name == "polar":

            raise NotImplementedError("Polar axis cannot be logit scaled yet")



        if self._nbins == "auto":

            if self.axis is not None:

                nbins = self.axis.get_tick_space()

                if nbins < 2:

                    nbins = 2

            else:

                nbins = 9

        else:

            nbins = self._nbins



                                                 

                                                                   

                                                                   

        def ideal_ticks(x):

            return 10 ** x if x < 0 else 1 - (10 ** (-x)) if x > 0 else 0.5



        vmin, vmax = self.nonsingular(vmin, vmax)

        binf = int(

            np.floor(np.log10(vmin))

            if vmin < 0.5

            else 0

            if vmin < 0.9

            else -np.ceil(np.log10(1 - vmin))

        )

        bsup = int(

            np.ceil(np.log10(vmax))

            if vmax <= 0.5

            else 1

            if vmax <= 0.9

            else -np.floor(np.log10(1 - vmax))

        )

        numideal = bsup - binf - 1

        if numideal >= 2:

                                                                           

            if numideal > nbins:

                                                                              

                                             

                subsampling_factor = math.ceil(numideal / nbins)

                if self._minor:

                    ticklocs = [

                        ideal_ticks(b)

                        for b in range(binf, bsup + 1)

                        if (b % subsampling_factor) != 0

                    ]

                else:

                    ticklocs = [

                        ideal_ticks(b)

                        for b in range(binf, bsup + 1)

                        if (b % subsampling_factor) == 0

                    ]

                return self.raise_if_exceeds(np.array(ticklocs))

            if self._minor:

                ticklocs = []

                for b in range(binf, bsup):

                    if b < -1:

                        ticklocs.extend(np.arange(2, 10) * 10 ** b)

                    elif b == -1:

                        ticklocs.extend(np.arange(2, 5) / 10)

                    elif b == 0:

                        ticklocs.extend(np.arange(6, 9) / 10)

                    else:

                        ticklocs.extend(

                            1 - np.arange(2, 10)[::-1] * 10 ** (-b - 1)

                        )

                return self.raise_if_exceeds(np.array(ticklocs))

            ticklocs = [ideal_ticks(b) for b in range(binf, bsup + 1)]

            return self.raise_if_exceeds(np.array(ticklocs))

                                                                       

        if self._minor:

            return []

        return super().tick_values(vmin, vmax)



    def nonsingular(self, vmin, vmax):

        standard_minpos = 1e-7

        initial_range = (standard_minpos, 1 - standard_minpos)

        if vmin > vmax:

            vmin, vmax = vmax, vmin

        if not np.isfinite(vmin) or not np.isfinite(vmax):

            vmin, vmax = initial_range                                       

        elif vmax <= 0 or vmin >= 1:

                                                           

                                                                   

            _api.warn_external(

                "Data has no values between 0 and 1, and therefore cannot be "

                "logit-scaled."

            )

            vmin, vmax = initial_range

        else:

            minpos = (

                self.axis.get_minpos()

                if self.axis is not None

                else standard_minpos

            )

            if not np.isfinite(minpos):

                minpos = standard_minpos                                  

            if vmin <= 0:

                vmin = minpos

                                                                               

                                                                   

                                                                              

                                                                              

            if vmax >= 1:

                vmax = 1 - minpos

            if vmin == vmax:

                vmin, vmax = 0.1 * vmin, 1 - 0.1 * vmin



        return vmin, vmax





class AutoLocator(MaxNLocator):

    

    def __init__(self):

        

        if mpl.rcParams['_internal.classic_mode']:

            nbins = 9

            steps = [1, 2, 5, 10]

        else:

            nbins = 'auto'

            steps = [1, 2, 2.5, 5, 10]

        super().__init__(nbins=nbins, steps=steps)





class AutoMinorLocator(Locator):

    



    def __init__(self, n=None):

        

        self.ndivs = n



    def __call__(self):

                             

        if self.axis.get_scale() == 'log':

            _api.warn_external('AutoMinorLocator does not work on logarithmic scales')

            return []



        majorlocs = np.unique(self.axis.get_majorticklocs())

        if len(majorlocs) < 2:

                                                                         

                                                                                      

                                                                                  

            return []

        majorstep = majorlocs[1] - majorlocs[0]



        if self.ndivs is None:

            self.ndivs = mpl.rcParams[

                'ytick.minor.ndivs' if self.axis.axis_name == 'y'

                else 'xtick.minor.ndivs']                    



        if self.ndivs == 'auto':

            majorstep_mantissa = 10 ** (np.log10(majorstep) % 1)

            ndivs = 5 if np.isclose(majorstep_mantissa, [1, 2.5, 5, 10]).any() else 4

        else:

            ndivs = self.ndivs



        minorstep = majorstep / ndivs



        vmin, vmax = sorted(self.axis.get_view_interval())

        t0 = majorlocs[0]

        tmin = round((vmin - t0) / minorstep)

        tmax = round((vmax - t0) / minorstep) + 1

        locs = (np.arange(tmin, tmax) * minorstep) + t0



        return self.raise_if_exceeds(locs)



    def tick_values(self, vmin, vmax):

        raise NotImplementedError(

            f"Cannot get tick locations for a {type(self).__name__}")

