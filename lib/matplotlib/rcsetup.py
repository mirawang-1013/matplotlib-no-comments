



import ast

from functools import lru_cache, reduce

from numbers import Real

import operator

import os

import re



import numpy as np



import matplotlib as mpl

from matplotlib import _api, cbook

from matplotlib.backends import backend_registry

from matplotlib.cbook import ls_mapper

from matplotlib.colors import Colormap, is_color_like

from matplotlib._fontconfig_pattern import parse_fontconfig_pattern

from matplotlib._enums import JoinStyle, CapStyle



                                                                  

from cycler import Cycler, cycler as ccycler





class ValidateInStrings:

    def __init__(self, key, valid, ignorecase=False, *,

                 _deprecated_since=None):

        

        self.key = key

        self.ignorecase = ignorecase

        self._deprecated_since = _deprecated_since



        def func(s):

            if ignorecase:

                return s.lower()

            else:

                return s

        self.valid = {func(k): k for k in valid}



    def __call__(self, s):

        if self._deprecated_since:

            name, = (k for k, v in globals().items() if v is self)

            _api.warn_deprecated(

                self._deprecated_since, name=name, obj_type="function")

        if self.ignorecase and isinstance(s, str):

            s = s.lower()

        if s in self.valid:

            return self.valid[s]

        msg = (f"{s!r} is not a valid value for {self.key}; supported values "

               f"are {[*self.valid.values()]}")

        if (isinstance(s, str)

                and (s.startswith('"') and s.endswith('"')

                     or s.startswith("'") and s.endswith("'"))

                and s[1:-1] in self.valid):

            msg += "; remove quotes surrounding your string"

        raise ValueError(msg)





def _single_string_color_list(s, scalar_validator):

    

    try:

        colors = mpl.color_sequences[s]

    except KeyError:

        try:

                                                                  

                                                               

            colors = [scalar_validator(v.strip()) for v in s if v.strip()]

        except ValueError:

            raise ValueError(f'{s!r} is neither a color sequence name nor can '

                             'it be interpreted as a list of colors')



    return colors





@lru_cache

def _listify_validator(scalar_validator, allow_stringlist=False, *,

                       n=None, doc=None):

    def f(s):

        if isinstance(s, str):

            try:

                val = [scalar_validator(v.strip()) for v in s.split(',')

                       if v.strip()]

            except Exception:

                if allow_stringlist:

                                                 

                    val = _single_string_color_list(s, scalar_validator)

                else:

                    raise

                                                                              

                                                                      

        elif np.iterable(s) and not isinstance(s, (set, frozenset)):

                                                                        

                                                                       

                                                                      

                                                                           

            val = [scalar_validator(v) for v in s

                   if not isinstance(v, str) or v]

        else:

            raise ValueError(

                f"Expected str or other non-set iterable, but got {s}")

        if n is not None and len(val) != n:

            raise ValueError(

                f"Expected {n} values, but there are {len(val)} values in {s}")

        return val



    try:

        f.__name__ = f"{scalar_validator.__name__}list"

    except AttributeError:                   

        f.__name__ = f"{type(scalar_validator).__name__}List"

    f.__qualname__ = f.__qualname__.rsplit(".", 1)[0] + "." + f.__name__

    f.__doc__ = doc if doc is not None else scalar_validator.__doc__

    return f





def validate_any(s):

    return s

validate_anylist = _listify_validator(validate_any)





def _validate_date(s):

    try:

        np.datetime64(s)

        return s

    except ValueError:

        raise ValueError(

            f'{s!r} should be a string that can be parsed by numpy.datetime64')





def validate_bool(b):

    

    if isinstance(b, str):

        b = b.lower()

    if b in ('t', 'y', 'yes', 'on', 'true', '1', 1, True):

        return True

    elif b in ('f', 'n', 'no', 'off', 'false', '0', 0, False):

        return False

    else:

        raise ValueError(f'Cannot convert {b!r} to bool')





def validate_axisbelow(s):

    try:

        return validate_bool(s)

    except ValueError:

        if isinstance(s, str):

            if s == 'line':

                return 'line'

    raise ValueError(f'{s!r} cannot be interpreted as'

                     ' True, False, or "line"')





def validate_dpi(s):

    

    if s == 'figure':

        return s

    try:

        return float(s)

    except ValueError as e:

        raise ValueError(f'{s!r} is not string "figure" and '

                         f'could not convert {s!r} to float') from e





def _make_type_validator(cls, *, allow_none=False):

    



    def validator(s):

        if (allow_none and

                (s is None or cbook._str_lower_equal(s, "none"))):

            if cbook._str_lower_equal(s, "none") and s != "None":

                _api.warn_deprecated(

                    "3.11",

                    message=f"Using the capitalization {s!r} in matplotlibrc for "

                            "*None* is deprecated in %(removal)s and will lead to an "

                            "error from version 3.13 onward. Please use 'None' "

                            "instead."

                )

            return None

        if cls is str and not isinstance(s, str):

            raise ValueError(f'Could not convert {s!r} to str')

        try:

            return cls(s)

        except (TypeError, ValueError) as e:

            raise ValueError(

                f'Could not convert {s!r} to {cls.__name__}') from e



    validator.__name__ = f"validate_{cls.__name__}"

    if allow_none:

        validator.__name__ += "_or_None"

    validator.__qualname__ = (

        validator.__qualname__.rsplit(".", 1)[0] + "." + validator.__name__)

    return validator





validate_string = _make_type_validator(str)

validate_string_or_None = _make_type_validator(str, allow_none=True)

validate_stringlist = _listify_validator(

    validate_string, doc='return a list of strings')

validate_int = _make_type_validator(int)

validate_int_or_None = _make_type_validator(int, allow_none=True)

validate_float = _make_type_validator(float)

validate_float_or_None = _make_type_validator(float, allow_none=True)

validate_floatlist = _listify_validator(

    validate_float, doc='return a list of floats')





def _validate_marker(s):

    try:

        return validate_int(s)

    except ValueError as e:

        try:

            return validate_string(s)

        except ValueError as e:

            raise ValueError('Supported markers are [string, int]') from e





_validate_markerlist = _listify_validator(

    _validate_marker, doc='return a list of markers')





def _validate_pathlike(s):

    if isinstance(s, (str, os.PathLike)):

                                                                           

                                                                              

        return os.fsdecode(s)

    else:

        return validate_string(s)





def validate_fonttype(s):

    

    fonttypes = {'type3':    3,

                 'truetype': 42}

    try:

        fonttype = validate_int(s)

    except ValueError:

        try:

            return fonttypes[s.lower()]

        except KeyError as e:

            raise ValueError('Supported Postscript/PDF font types are %s'

                             % list(fonttypes)) from e

    else:

        if fonttype not in fonttypes.values():

            raise ValueError(

                'Supported Postscript/PDF font types are %s' %

                list(fonttypes.values()))

        return fonttype





_auto_backend_sentinel = object()





def validate_backend(s):

    if s is _auto_backend_sentinel or backend_registry.is_valid_backend(s):

        return s

    else:

        msg = (f"'{s}' is not a valid value for backend; supported values are "

               f"{backend_registry.list_all()}")

        raise ValueError(msg)





def _validate_toolbar(s):

    s = ValidateInStrings(

        'toolbar', ['None', 'toolbar2', 'toolmanager'], ignorecase=True)(s)

    if s == 'toolmanager':

        _api.warn_external(

            "Treat the new Tool classes introduced in v1.5 as experimental "

            "for now; the API and rcParam may change in future versions.")

    return s





def validate_color_or_inherit(s):

    

    if cbook._str_equal(s, 'inherit'):

        return s

    return validate_color(s)





def validate_color_or_auto(s):

    if cbook._str_equal(s, 'auto'):

        return s

    return validate_color(s)





def _validate_color_or_edge(s):

    if cbook._str_equal(s, 'edge'):

        return s

    return validate_color(s)





def validate_color_for_prop_cycle(s):

                                                            

    if isinstance(s, str) and re.match("^C[0-9]$", s):

        raise ValueError(f"Cannot put cycle reference ({s!r}) in prop_cycler")

    return validate_color(s)





def _validate_color_or_linecolor(s):

    if cbook._str_equal(s, 'linecolor'):

        return s

    elif cbook._str_equal(s, 'mfc') or cbook._str_equal(s, 'markerfacecolor'):

        return 'markerfacecolor'

    elif cbook._str_equal(s, 'mec') or cbook._str_equal(s, 'markeredgecolor'):

        return 'markeredgecolor'

    elif s is None:

        return None

    elif isinstance(s, str) and len(s) == 6 or len(s) == 8:

        stmp = '#' + s

        if is_color_like(stmp):

            return stmp

        if s.lower() == 'none':

            return None

    elif is_color_like(s):

        return s



    raise ValueError(f'{s!r} does not look like a color arg')





def validate_color(s):

    

    if isinstance(s, str):

        if s.lower() == 'none':

            return 'none'

        if len(s) == 6 or len(s) == 8:

            stmp = '#' + s

            if is_color_like(stmp):

                return stmp



    if is_color_like(s):

        return s



                                                                               

    try:

        color = ast.literal_eval(s)

    except (SyntaxError, ValueError):

        pass

    else:

        if is_color_like(color):

            return color



    raise ValueError(f'{s!r} does not look like a color arg')





def _validate_color_or_None(s):

    if s is None or cbook._str_equal(s, "None"):

        return None

    return validate_color(s)





validate_colorlist = _listify_validator(

    validate_color, allow_stringlist=True, doc='return a list of colorspecs')





def _validate_cmap(s):

    _api.check_isinstance((str, Colormap), cmap=s)

    return s





def validate_aspect(s):

    if s in ('auto', 'equal'):

        return s

    try:

        return float(s)

    except ValueError as e:

        raise ValueError('not a valid aspect specification') from e





def validate_fontsize_None(s):

    if s is None or s == 'None':

        return None

    else:

        return validate_fontsize(s)





def validate_fontsize(s):

    fontsizes = ['xx-small', 'x-small', 'small', 'medium', 'large',

                 'x-large', 'xx-large', 'smaller', 'larger']

    if isinstance(s, str):

        s = s.lower()

    if s in fontsizes:

        return s

    try:

        return float(s)

    except ValueError as e:

        raise ValueError("%s is not a valid font size. Valid font sizes "

                         "are %s." % (s, ", ".join(fontsizes))) from e





validate_fontsizelist = _listify_validator(validate_fontsize)





def validate_fontweight(s):

    weights = [

        'ultralight', 'light', 'normal', 'regular', 'book', 'medium', 'roman',

        'semibold', 'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black']

                                                                        

    if s in weights:

        return s

    try:

        return int(s)

    except (ValueError, TypeError) as e:

        raise ValueError(f'{s} is not a valid font weight.') from e





def validate_fontstretch(s):

    stretchvalues = [

        'ultra-condensed', 'extra-condensed', 'condensed', 'semi-condensed',

        'normal', 'semi-expanded', 'expanded', 'extra-expanded',

        'ultra-expanded']

                                                                              

    if s in stretchvalues:

        return s

    try:

        return int(s)

    except (ValueError, TypeError) as e:

        raise ValueError(f'{s} is not a valid font stretch.') from e





def validate_font_properties(s):

    parse_fontconfig_pattern(s)

    return s





def _validate_mathtext_fallback(s):

    _fallback_fonts = ['cm', 'stix', 'stixsans']

    if isinstance(s, str):

        s = s.lower()

    if s is None or s == 'none':

        return None

    elif s.lower() in _fallback_fonts:

        return s

    else:

        raise ValueError(

            f"{s} is not a valid fallback font name. Valid fallback font "

            f"names are {','.join(_fallback_fonts)}. Passing 'None' will turn "

            "fallback off.")





def validate_whiskers(s):

    try:

        return _listify_validator(validate_float, n=2)(s)

    except (TypeError, ValueError):

        try:

            return float(s)

        except ValueError as e:

            raise ValueError("Not a valid whisker value [float, "

                             "(float, float)]") from e





def validate_ps_distiller(s):

    if isinstance(s, str):

        s = s.lower()

    if s in ('none', None, 'false', False):

        return None

    else:

        return ValidateInStrings('ps.usedistiller', ['ghostscript', 'xpdf'])(s)





                                                                       

                                                                          

_validate_named_linestyle = ValidateInStrings(

    'linestyle',

    [*ls_mapper.keys(), *ls_mapper.values(), 'None', 'none', ' ', ''],

    ignorecase=True)





def _validate_linestyle(ls):

    

    if isinstance(ls, str):

        try:                                                                  

            return _validate_named_linestyle(ls)

        except ValueError:

            pass

        try:

            ls = ast.literal_eval(ls)                         

        except (SyntaxError, ValueError):

            pass                                              



    def _is_iterable_not_string_like(x):

                                                                  

                                                                         

        return np.iterable(x) and not isinstance(x, (str, bytes, bytearray))



    if _is_iterable_not_string_like(ls):

        if len(ls) == 2 and _is_iterable_not_string_like(ls[1]):

                                               

            offset, onoff = ls

        else:

                                                                              

            offset = 0

            onoff = ls



        if (isinstance(offset, Real)

                and len(onoff) % 2 == 0

                and all(isinstance(elem, Real) for elem in onoff)):

            return (offset, onoff)



    raise ValueError(f"linestyle {ls!r} is not a valid on-off ink sequence.")





def _validate_linestyle_or_None(s):

    if s is None or cbook._str_equal(s, "None"):

        return None



    return _validate_linestyle(s)





validate_fillstyle = ValidateInStrings(

    'markers.fillstyle', ['full', 'left', 'right', 'bottom', 'top', 'none'])





validate_fillstylelist = _listify_validator(validate_fillstyle)





def validate_markevery(s):

    

                                                      

    if isinstance(s, (slice, float, int, type(None))):

        return s

                                   

    if isinstance(s, tuple):

        if (len(s) == 2

                and (all(isinstance(e, int) for e in s)

                     or all(isinstance(e, float) for e in s))):

            return s

        else:

            raise TypeError(

                "'markevery' tuple must be pair of ints or of floats")

                                  

    if isinstance(s, list):

        if all(isinstance(e, int) for e in s):

            return s

        else:

            raise TypeError(

                "'markevery' list must have all elements of type int")

    raise TypeError("'markevery' is of an invalid type")





validate_markeverylist = _listify_validator(validate_markevery)





def validate_bbox(s):

    if isinstance(s, str):

        s = s.lower()

        if s == 'tight':

            return s

        if s == 'standard':

            return None

        raise ValueError("bbox should be 'tight' or 'standard'")

    elif s is not None:

                                                                    

        raise ValueError("bbox should be 'tight' or 'standard'")

    return s





def validate_sketch(s):



    if isinstance(s, str):

        s = s.lower().strip()

        if s.startswith("(") and s.endswith(")"):

            s = s[1:-1]

    if s == 'none' or s is None:

        return None

    try:

        return tuple(_listify_validator(validate_float, n=3)(s))

    except ValueError as exc:

        raise ValueError("Expected a (scale, length, randomness) tuple") from exc





def _validate_greaterthan_minushalf(s):

    s = validate_float(s)

    if s > -0.5:

        return s

    else:

        raise RuntimeError(f'Value must be >-0.5; got {s}')





def _validate_greaterequal0_lessequal1(s):

    s = validate_float(s)

    if 0 <= s <= 1:

        return s

    else:

        raise RuntimeError(f'Value must be >=0 and <=1; got {s}')





def _validate_int_greaterequal0(s):

    s = validate_int(s)

    if s >= 0:

        return s

    else:

        raise RuntimeError(f'Value must be >=0; got {s}')





def validate_hatch(s):

    

    if not isinstance(s, str):

        raise ValueError("Hatch pattern must be a string")

    _api.check_isinstance(str, hatch_pattern=s)

    unknown = set(s) - {'\\', '/', '|', '-', '+', '*', '.', 'x', 'o', 'O'}

    if unknown:

        raise ValueError("Unknown hatch symbol(s): %s" % list(unknown))

    return s





validate_hatchlist = _listify_validator(validate_hatch)

validate_dashlist = _listify_validator(validate_floatlist)





def _validate_minor_tick_ndivs(n):

    



    if cbook._str_lower_equal(n, 'auto'):

        return n

    try:

        n = _validate_int_greaterequal0(n)

        return n

    except (RuntimeError, ValueError):

        pass



    raise ValueError("'tick.minor.ndivs' must be 'auto' or non-negative int")





_prop_validators = {

        'color': _listify_validator(validate_color_for_prop_cycle,

                                    allow_stringlist=True),

        'linewidth': validate_floatlist,

        'linestyle': _listify_validator(_validate_linestyle),

        'facecolor': validate_colorlist,

        'edgecolor': validate_colorlist,

        'joinstyle': _listify_validator(JoinStyle),

        'capstyle': _listify_validator(CapStyle),

        'fillstyle': validate_fillstylelist,

        'markerfacecolor': validate_colorlist,

        'markersize': validate_floatlist,

        'markeredgewidth': validate_floatlist,

        'markeredgecolor': validate_colorlist,

        'markevery': validate_markeverylist,

        'alpha': validate_floatlist,

        'marker': _validate_markerlist,

        'hatch': validate_hatchlist,

        'dashes': validate_dashlist,

    }

_prop_aliases = {

        'c': 'color',

        'lw': 'linewidth',

        'ls': 'linestyle',

        'fc': 'facecolor',

        'ec': 'edgecolor',

        'mfc': 'markerfacecolor',

        'mec': 'markeredgecolor',

        'mew': 'markeredgewidth',

        'ms': 'markersize',

    }





def cycler(*args, **kwargs):

    

    if args and kwargs:

        raise TypeError("cycler() can only accept positional OR keyword "

                        "arguments -- not both.")

    elif not args and not kwargs:

        raise TypeError("cycler() must have positional OR keyword arguments")



    if len(args) == 1:

        if not isinstance(args[0], Cycler):

            raise TypeError("If only one positional argument given, it must "

                            "be a Cycler instance.")

        return validate_cycler(args[0])

    elif len(args) == 2:

        pairs = [(args[0], args[1])]

    elif len(args) > 2:

        raise _api.nargs_error('cycler', '0-2', len(args))

    else:

        pairs = kwargs.items()



    validated = []

    for prop, vals in pairs:

        norm_prop = _prop_aliases.get(prop, prop)

        validator = _prop_validators.get(norm_prop, None)

        if validator is None:

            raise TypeError("Unknown artist property: %s" % prop)

        vals = validator(vals)

                                                                

                                                      

        validated.append((norm_prop, vals))



    return reduce(operator.add, (ccycler(k, v) for k, v in validated))





class _DunderChecker(ast.NodeVisitor):

    def visit_Attribute(self, node):

        if node.attr.startswith("__") and node.attr.endswith("__"):

            raise ValueError("cycler strings with dunders are forbidden")

        self.generic_visit(node)





                                               

_validate_named_legend_loc = ValidateInStrings(

    'legend.loc',

    [

        "best",

        "upper right", "upper left", "lower left", "lower right", "right",

        "center left", "center right", "lower center", "upper center",

        "center"],

    ignorecase=True)





def _validate_legend_loc(loc):

    

    if isinstance(loc, str):

        try:

            return _validate_named_legend_loc(loc)

        except ValueError:

            pass

        try:

            loc = ast.literal_eval(loc)

        except (SyntaxError, ValueError):

            pass

    if isinstance(loc, int):

        if 0 <= loc <= 10:

            return loc

    if isinstance(loc, tuple):

        if len(loc) == 2 and all(isinstance(e, Real) for e in loc):

            return loc

    raise ValueError(f"{loc} is not a valid legend location.")





def validate_cycler(s):

    

    if isinstance(s, str):

                                                

                                                                       

                                            

                                                                             

                                                                     

                                                                            

                                                  

                                         

                                                                             

                                                                   

                            

        try:

            _DunderChecker().visit(ast.parse(s))

            s = eval(s, {'cycler': cycler, '__builtins__': {}})

        except BaseException as e:

            raise ValueError(f"{s!r} is not a valid cycler construction: {e}"

                             ) from e

                                                       

                         

    if isinstance(s, Cycler):

        cycler_inst = s

    else:

        raise ValueError(f"Object is not a string or Cycler instance: {s!r}")



    unknowns = cycler_inst.keys - (set(_prop_validators) | set(_prop_aliases))

    if unknowns:

        raise ValueError("Unknown artist properties: %s" % unknowns)



                                                                        

                                                        

    checker = set()

    for prop in cycler_inst.keys:

        norm_prop = _prop_aliases.get(prop, prop)

        if norm_prop != prop and norm_prop in cycler_inst.keys:

            raise ValueError(f"Cannot specify both {norm_prop!r} and alias "

                             f"{prop!r} in the same prop_cycle")

        if norm_prop in checker:

            raise ValueError(f"Another property was already aliased to "

                             f"{norm_prop!r}. Collision normalizing {prop!r}.")

        checker.update([norm_prop])



                                                                     

                                     

    assert len(checker) == len(cycler_inst.keys)



                                                  

    for prop in cycler_inst.keys:

        norm_prop = _prop_aliases.get(prop, prop)

        cycler_inst.change_key(prop, norm_prop)



    for key, vals in cycler_inst.by_key().items():

        _prop_validators[key](vals)



    return cycler_inst





def validate_hist_bins(s):

    valid_strs = ["auto", "sturges", "fd", "doane", "scott", "rice", "sqrt"]

    if isinstance(s, str) and s in valid_strs:

        return s

    try:

        return int(s)

    except (TypeError, ValueError):

        pass

    try:

        return validate_floatlist(s)

    except ValueError:

        pass

    raise ValueError(f"'hist.bins' must be one of {valid_strs}, an int or"

                     " a sequence of floats")





class _ignorecase(list):

    





def _convert_validator_spec(key, conv):

    if isinstance(conv, list):

        ignorecase = isinstance(conv, _ignorecase)

        return ValidateInStrings(key, conv, ignorecase=ignorecase)

    else:

        return conv





                                    

                                                                             

                    

                                                                                  

                                                                      

_validators = {

    "backend":           validate_backend,

    "backend_fallback":  validate_bool,

    "figure.hooks":      validate_stringlist,

    "toolbar":           _validate_toolbar,

    "interactive":       validate_bool,

    "timezone":          validate_string,



    "webagg.port":            validate_int,

    "webagg.address":         validate_string,

    "webagg.open_in_browser": validate_bool,

    "webagg.port_retries":    validate_int,



                

    "lines.linewidth":       validate_float,                        

    "lines.linestyle":       _validate_linestyle,              

    "lines.color":           validate_color,                              

    "lines.marker":          _validate_marker,               

    "lines.markerfacecolor": validate_color_or_auto,                 

    "lines.markeredgecolor": validate_color_or_auto,                 

    "lines.markeredgewidth": validate_float,

    "lines.markersize":      validate_float,                         

    "lines.antialiased":     validate_bool,                            

    "lines.dash_joinstyle":  JoinStyle,

    "lines.solid_joinstyle": JoinStyle,

    "lines.dash_capstyle":   CapStyle,

    "lines.solid_capstyle":  CapStyle,

    "lines.dashed_pattern":  validate_floatlist,

    "lines.dashdot_pattern": validate_floatlist,

    "lines.dotted_pattern":  validate_floatlist,

    "lines.scale_dashes":    validate_bool,



                  

    "markers.fillstyle": validate_fillstyle,



                          

    "pcolor.shading": ["auto", "flat", "nearest", "gouraud"],

    "pcolormesh.snap": validate_bool,



                  

    "patch.linewidth":       validate_float,                        

    "patch.edgecolor":       validate_color,

    "patch.force_edgecolor": validate_bool,

    "patch.facecolor":       validate_color,                        

    "patch.antialiased":     validate_bool,                            



                  

    "hatch.color":     _validate_color_or_edge,

    "hatch.linewidth": validate_float,



                           

    "hist.bins": validate_hist_bins,



                         

    "boxplot.notch":       validate_bool,

    "boxplot.vertical":    validate_bool,

    "boxplot.whiskers":    validate_whiskers,

    "boxplot.bootstrap":   validate_int_or_None,

    "boxplot.patchartist": validate_bool,

    "boxplot.showmeans":   validate_bool,

    "boxplot.showcaps":    validate_bool,

    "boxplot.showbox":     validate_bool,

    "boxplot.showfliers":  validate_bool,

    "boxplot.meanline":    validate_bool,



    "boxplot.flierprops.color":           validate_color,

    "boxplot.flierprops.marker":          _validate_marker,

    "boxplot.flierprops.markerfacecolor": validate_color_or_auto,

    "boxplot.flierprops.markeredgecolor": validate_color,

    "boxplot.flierprops.markeredgewidth": validate_float,

    "boxplot.flierprops.markersize":      validate_float,

    "boxplot.flierprops.linestyle":       _validate_linestyle,

    "boxplot.flierprops.linewidth":       validate_float,



    "boxplot.boxprops.color":     validate_color,

    "boxplot.boxprops.linewidth": validate_float,

    "boxplot.boxprops.linestyle": _validate_linestyle,



    "boxplot.whiskerprops.color":     validate_color,

    "boxplot.whiskerprops.linewidth": validate_float,

    "boxplot.whiskerprops.linestyle": _validate_linestyle,



    "boxplot.capprops.color":     validate_color,

    "boxplot.capprops.linewidth": validate_float,

    "boxplot.capprops.linestyle": _validate_linestyle,



    "boxplot.medianprops.color":     validate_color,

    "boxplot.medianprops.linewidth": validate_float,

    "boxplot.medianprops.linestyle": _validate_linestyle,



    "boxplot.meanprops.color":           validate_color,

    "boxplot.meanprops.marker":          _validate_marker,

    "boxplot.meanprops.markerfacecolor": validate_color,

    "boxplot.meanprops.markeredgecolor": validate_color,

    "boxplot.meanprops.markersize":      validate_float,

    "boxplot.meanprops.linestyle":       _validate_linestyle,

    "boxplot.meanprops.linewidth":       validate_float,



                 

    "font.enable_last_resort":     validate_bool,

    "font.family":     validate_stringlist,                       

    "font.style":      validate_string,

    "font.variant":    validate_string,

    "font.stretch":    validate_fontstretch,

    "font.weight":     validate_fontweight,

    "font.size":       validate_float,                            

    "font.serif":      validate_stringlist,

    "font.sans-serif": validate_stringlist,

    "font.cursive":    validate_stringlist,

    "font.fantasy":    validate_stringlist,

    "font.monospace":  validate_stringlist,



                

    "text.color":          validate_color,

    "text.usetex":         validate_bool,

    "text.latex.preamble": validate_string,

    "text.hinting":        ["default", "no_autohint", "force_autohint",

                            "no_hinting", "auto", "native", "either", "none"],

    "text.hinting_factor": validate_int,

    "text.kerning_factor": validate_int,

    "text.antialiased":    validate_bool,

    "text.parse_math":     validate_bool,



    "mathtext.cal":            validate_font_properties,

    "mathtext.rm":             validate_font_properties,

    "mathtext.tt":             validate_font_properties,

    "mathtext.it":             validate_font_properties,

    "mathtext.bf":             validate_font_properties,

    "mathtext.bfit":           validate_font_properties,

    "mathtext.sf":             validate_font_properties,

    "mathtext.fontset":        ["dejavusans", "dejavuserif", "cm", "stix",

                                "stixsans", "custom"],

    "mathtext.default":        ["rm", "cal", "bfit", "it", "tt", "sf", "bf", "default",

                                "bb", "frak", "scr", "regular"],

    "mathtext.fallback":       _validate_mathtext_fallback,



    "image.aspect":              validate_aspect,                         

    "image.interpolation":       validate_string,

    "image.interpolation_stage": ["auto", "data", "rgba"],

    "image.cmap":                _validate_cmap,                   

    "image.lut":                 validate_int,                

    "image.origin":              ["upper", "lower"],

    "image.resample":            validate_bool,

                                                                           

                                               

    "image.composite_image": validate_bool,



                   

    "contour.negative_linestyle": _validate_linestyle,

    "contour.corner_mask":        validate_bool,

    "contour.linewidth":          validate_float_or_None,

    "contour.algorithm":          ["mpl2005", "mpl2014", "serial", "threaded"],



                    

    "errorbar.capsize": validate_float,



                

                                 

    "xaxis.labellocation": ["left", "center", "right"],

    "yaxis.labellocation": ["bottom", "center", "top"],



                

    "axes.axisbelow":        validate_axisbelow,

    "axes.facecolor":        validate_color,                    

    "axes.edgecolor":        validate_color,              

    "axes.linewidth":        validate_float,                  



    "axes.spines.left":      validate_bool,                                  

    "axes.spines.right":     validate_bool,                                    

    "axes.spines.bottom":    validate_bool,                           

    "axes.spines.top":       validate_bool,



    "axes.titlesize":     validate_fontsize,                       

    "axes.titlelocation": ["left", "center", "right"],                        

    "axes.titleweight":   validate_fontweight,                          

    "axes.titlecolor":    validate_color_or_auto,                         

                                                 

    "axes.titley":        validate_float_or_None,

                                                     

    "axes.titlepad":      validate_float,

    "axes.grid":          validate_bool,                       

    "axes.grid.which":    ["minor", "both", "major"],                         

    "axes.grid.axis":     ["x", "y", "both"],             

    "axes.labelsize":     validate_fontsize,                            

    "axes.labelpad":      validate_float,                                

    "axes.labelweight":   validate_fontweight,                            

    "axes.labelcolor":    validate_color,                       

                                                                            

                                     

    "axes.formatter.limits": _listify_validator(validate_int, n=2),

                                        

    "axes.formatter.use_locale": validate_bool,

    "axes.formatter.use_mathtext": validate_bool,

                                                       

    "axes.formatter.min_exponent": validate_int,

    "axes.formatter.useoffset": validate_bool,

    "axes.formatter.offset_threshold": validate_int,

    "axes.unicode_minus": validate_bool,

                                                                    

                                                               

    "axes.prop_cycle": validate_cycler,

                                                       

                                                                          

    "axes.autolimit_mode": ["data", "round_numbers"],

    "axes.xmargin": _validate_greaterthan_minushalf,                         

    "axes.ymargin": _validate_greaterthan_minushalf,                         

    "axes.zmargin": _validate_greaterthan_minushalf,                         



    "polaraxes.grid":    validate_bool,                             

    "axes3d.grid":       validate_bool,                   

    "axes3d.automargin": validate_bool,                                 

                                                                          



    "axes3d.xaxis.panecolor":    validate_color,                      

    "axes3d.yaxis.panecolor":    validate_color,                      

    "axes3d.zaxis.panecolor":    validate_color,                      



    "axes3d.depthshade": validate_bool,                                    

    "axes3d.depthshade_minalpha": validate_float,                                     



    "axes3d.mouserotationstyle": ["azel", "trackball", "sphere", "arcball"],

    "axes3d.trackballsize": validate_float,

    "axes3d.trackballborder": validate_float,



                   

    "scatter.marker":     _validate_marker,

    "scatter.edgecolors": validate_string,



    "date.epoch": _validate_date,

    "date.autoformatter.year":        validate_string,

    "date.autoformatter.month":       validate_string,

    "date.autoformatter.day":         validate_string,

    "date.autoformatter.hour":        validate_string,

    "date.autoformatter.minute":      validate_string,

    "date.autoformatter.second":      validate_string,

    "date.autoformatter.microsecond": validate_string,



    'date.converter':          ['auto', 'concise'],

                                                      

    'date.interval_multiples': validate_bool,



                       

    "legend.fancybox": validate_bool,

    "legend.loc": _validate_legend_loc,



                                             

    "legend.numpoints":      validate_int,

                                                         

    "legend.scatterpoints":  validate_int,

    "legend.fontsize":       validate_fontsize,

    "legend.title_fontsize": validate_fontsize_None,

                         

    "legend.labelcolor":     _validate_color_or_linecolor,

                                                      

    "legend.markerscale":    validate_float,

                                                                       

    "legend.shadow":         validate_bool,

                                                  

    "legend.frameon":        validate_bool,

                                     

    "legend.framealpha":     validate_float_or_None,



                                                                

    "legend.borderpad":      validate_float,                      

                                                   

    "legend.labelspacing":   validate_float,

                                    

    "legend.handlelength":   validate_float,

                                    

    "legend.handleheight":   validate_float,

                                                       

    "legend.handletextpad":  validate_float,

                                                 

    "legend.borderaxespad":  validate_float,

                                                 

    "legend.columnspacing":  validate_float,

    "legend.facecolor":      validate_color_or_inherit,

    "legend.edgecolor":      validate_color_or_inherit,



                     

    "xtick.top":           validate_bool,                              

    "xtick.bottom":        validate_bool,                                 

    "xtick.labeltop":      validate_bool,                         

    "xtick.labelbottom":   validate_bool,                            

    "xtick.major.size":    validate_float,                                 

    "xtick.minor.size":    validate_float,                                 

    "xtick.major.width":   validate_float,                                  

    "xtick.minor.width":   validate_float,                                  

    "xtick.major.pad":     validate_float,                                  

    "xtick.minor.pad":     validate_float,                                  

    "xtick.color":         validate_color,                      

    "xtick.labelcolor":    validate_color_or_inherit,                         

    "xtick.minor.visible": validate_bool,                                  

    "xtick.minor.top":     validate_bool,                             

    "xtick.minor.bottom":  validate_bool,                                

    "xtick.major.top":     validate_bool,                             

    "xtick.major.bottom":  validate_bool,                                

                            

    "xtick.minor.ndivs":   _validate_minor_tick_ndivs,

    "xtick.labelsize":     validate_fontsize,                            

    "xtick.direction":     ["out", "in", "inout"],                       

    "xtick.alignment":     ["center", "right", "left"],



    "ytick.left":          validate_bool,                               

    "ytick.right":         validate_bool,                                

    "ytick.labelleft":     validate_bool,                                     

    "ytick.labelright":    validate_bool,                                      

    "ytick.major.size":    validate_float,                                 

    "ytick.minor.size":    validate_float,                                 

    "ytick.major.width":   validate_float,                                  

    "ytick.minor.width":   validate_float,                                  

    "ytick.major.pad":     validate_float,                                  

    "ytick.minor.pad":     validate_float,                                  

    "ytick.color":         validate_color,                      

    "ytick.labelcolor":    validate_color_or_inherit,                         

    "ytick.minor.visible": validate_bool,                                  

    "ytick.minor.left":    validate_bool,                              

    "ytick.minor.right":   validate_bool,                               

    "ytick.major.left":    validate_bool,                              

    "ytick.major.right":   validate_bool,                               

                            

    "ytick.minor.ndivs":   _validate_minor_tick_ndivs,

    "ytick.labelsize":     validate_fontsize,                            

    "ytick.direction":     ["out", "in", "inout"],                       

    "ytick.alignment":     [

        "center", "top", "bottom", "baseline", "center_baseline"],



    "grid.color":        validate_color,              

    "grid.linestyle":    _validate_linestyle,         

    "grid.linewidth":    validate_float,                

    "grid.alpha":        validate_float,



    "grid.major.color":        _validate_color_or_None,              

    "grid.major.linestyle":    _validate_linestyle_or_None,         

    "grid.major.linewidth":    validate_float_or_None,                

    "grid.major.alpha":        validate_float_or_None,



    "grid.minor.color":        _validate_color_or_None,              

    "grid.minor.linestyle":    _validate_linestyle_or_None,         

    "grid.minor.linewidth":    validate_float_or_None,                

    "grid.minor.alpha":        validate_float_or_None,



                   

                  

    "figure.titlesize":   validate_fontsize,

    "figure.titleweight": validate_fontweight,



                   

    "figure.labelsize":   validate_fontsize,

    "figure.labelweight": validate_fontweight,



                                            

    "figure.figsize":          _listify_validator(validate_float, n=2),

    "figure.dpi":              validate_float,

    "figure.facecolor":        validate_color,

    "figure.edgecolor":        validate_color,

    "figure.frameon":          validate_bool,

    "figure.autolayout":       validate_bool,

    "figure.max_open_warning": validate_int,

    "figure.raise_window":     validate_bool,

    "macosx.window_mode":      ["system", "tab", "window"],



    "figure.subplot.left":   validate_float,

    "figure.subplot.right":  validate_float,

    "figure.subplot.bottom": validate_float,

    "figure.subplot.top":    validate_float,

    "figure.subplot.wspace": validate_float,

    "figure.subplot.hspace": validate_float,



    "figure.constrained_layout.use": validate_bool,                           

                                                                           

                                                                      

    "figure.constrained_layout.hspace": validate_float,

    "figure.constrained_layout.wspace": validate_float,

                                        

    "figure.constrained_layout.h_pad": validate_float,

    "figure.constrained_layout.w_pad": validate_float,



                                 

    'savefig.dpi':          validate_dpi,

    'savefig.facecolor':    validate_color_or_auto,

    'savefig.edgecolor':    validate_color_or_auto,

    'savefig.orientation':  ['landscape', 'portrait'],

    "savefig.format":       validate_string,

    "savefig.bbox":         validate_bbox,                                   

    "savefig.pad_inches":   validate_float,

                                             

    "savefig.directory":    _validate_pathlike,

    "savefig.transparent":  validate_bool,



    "tk.window_focus": validate_bool,                                  



                            

    "ps.papersize":       _ignorecase(

                                ["figure", "letter", "legal", "ledger",

                                 *[f"{ab}{i}" for ab in "ab" for i in range(11)]]),

    "ps.useafm":          validate_bool,

                                                  

    "ps.usedistiller":    validate_ps_distiller,

    "ps.distiller.res":   validate_int,       

    "ps.fonttype":        validate_fonttype,                              

    "pdf.compression":    validate_int,                                       

    "pdf.inheritcolor":   validate_bool,                               

                                                                              

    "pdf.use14corefonts": validate_bool,

    "pdf.fonttype":       validate_fonttype,                              



    "pgf.texsystem": ["xelatex", "lualatex", "pdflatex"],                      

    "pgf.rcfonts":   validate_bool,                                         

    "pgf.preamble":  validate_string,                         



                                               

    "svg.image_inline": validate_bool,

    "svg.fonttype": ["none", "path"],                                         

    "svg.hashsalt": validate_string_or_None,

    "svg.id": validate_string_or_None,



                                                           

    "docstring.hardcopy": validate_bool,



    "path.simplify":           validate_bool,

    "path.simplify_threshold": _validate_greaterequal0_lessequal1,

    "path.snap":               validate_bool,

    "path.sketch":             validate_sketch,

    "path.effects":            validate_anylist,

    "agg.path.chunksize":      validate_int,                         



                                                                    

    "keymap.fullscreen": validate_stringlist,

    "keymap.home":       validate_stringlist,

    "keymap.back":       validate_stringlist,

    "keymap.forward":    validate_stringlist,

    "keymap.pan":        validate_stringlist,

    "keymap.zoom":       validate_stringlist,

    "keymap.save":       validate_stringlist,

    "keymap.quit":       validate_stringlist,

    "keymap.quit_all":   validate_stringlist,                           

    "keymap.grid":       validate_stringlist,

    "keymap.grid_minor": validate_stringlist,

    "keymap.yscale":     validate_stringlist,

    "keymap.xscale":     validate_stringlist,

    "keymap.help":       validate_stringlist,

    "keymap.copy":       validate_stringlist,



                        

    "animation.html":         ["html5", "jshtml", "none"],

                                                               

                             

    "animation.embed_limit":  validate_float,

    "animation.writer":       validate_string,

    "animation.codec":        validate_string,

    "animation.bitrate":      validate_int,

                                                           

    "animation.frame_format": ["png", "jpeg", "tiff", "raw", "rgba", "ppm",

                               "sgi", "bmp", "pbm", "svg"],

                                                                        

    "animation.ffmpeg_path":  _validate_pathlike,

                                                                

    "animation.ffmpeg_args":  validate_stringlist,

                                                                          

    "animation.convert_path": _validate_pathlike,

                                                                  

    "animation.convert_args": validate_stringlist,



                                          

                                                                       

                                                                      

                                                                  

    "_internal.classic_mode": validate_bool

}

_hardcoded_defaults = {                              

                                             

                                   

    "_internal.classic_mode": False,

                                      

                              

                                                                      

}

_validators = {k: _convert_validator_spec(k, conv)

               for k, conv in _validators.items()}

