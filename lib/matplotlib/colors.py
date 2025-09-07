



import base64

from collections.abc import Sequence, Mapping

from abc import ABC, abstractmethod

import functools

import importlib

import inspect

import io

import itertools

from numbers import Real

import re



from PIL import Image

from PIL.PngImagePlugin import PngInfo



import matplotlib as mpl

import numpy as np

from matplotlib import _api, _cm, cbook, scale, _image

from ._color_data import BASE_COLORS, TABLEAU_COLORS, CSS4_COLORS, XKCD_COLORS





class _ColorMapping(dict):

    def __init__(self, mapping):

        super().__init__(mapping)

        self.cache = {}



    def __setitem__(self, key, value):

        super().__setitem__(key, value)

        self.cache.clear()



    def __delitem__(self, key):

        super().__delitem__(key)

        self.cache.clear()





_colors_full_map = {}

                                

_colors_full_map.update(XKCD_COLORS)

_colors_full_map.update({k.replace('grey', 'gray'): v

                         for k, v in XKCD_COLORS.items()

                         if 'grey' in k})

_colors_full_map.update(CSS4_COLORS)

_colors_full_map.update(TABLEAU_COLORS)

_colors_full_map.update({k.replace('gray', 'grey'): v

                         for k, v in TABLEAU_COLORS.items()

                         if 'gray' in k})

_colors_full_map.update(BASE_COLORS)

_colors_full_map = _ColorMapping(_colors_full_map)



_REPR_PNG_SIZE = (512, 64)

_BIVAR_REPR_PNG_SIZE = 256





def get_named_colors_mapping():

    

    return _colors_full_map





class ColorSequenceRegistry(Mapping):

    



    _BUILTIN_COLOR_SEQUENCES = {

        'tab10': _cm._tab10_data,

        'tab20': _cm._tab20_data,

        'tab20b': _cm._tab20b_data,

        'tab20c': _cm._tab20c_data,

        'Pastel1': _cm._Pastel1_data,

        'Pastel2': _cm._Pastel2_data,

        'Paired': _cm._Paired_data,

        'Accent': _cm._Accent_data,

        'Dark2': _cm._Dark2_data,

        'Set1': _cm._Set1_data,

        'Set2': _cm._Set2_data,

        'Set3': _cm._Set3_data,

        'petroff6': _cm._petroff6_data,

        'petroff8': _cm._petroff8_data,

        'petroff10': _cm._petroff10_data,

    }



    def __init__(self):

        self._color_sequences = {**self._BUILTIN_COLOR_SEQUENCES}



    def __getitem__(self, item):

        try:

            return list(self._color_sequences[item])

        except KeyError:

            raise KeyError(f"{item!r} is not a known color sequence name")



    def __iter__(self):

        return iter(self._color_sequences)



    def __len__(self):

        return len(self._color_sequences)



    def __str__(self):

        return ('ColorSequenceRegistry; available colormaps:\n' +

                ', '.join(f"'{name}'" for name in self))



    def register(self, name, color_list):

        

        if name in self._BUILTIN_COLOR_SEQUENCES:

            raise ValueError(f"{name!r} is a reserved name for a builtin "

                             "color sequence")



        color_list = list(color_list)                                      

        for color in color_list:

            try:

                to_rgba(color)

            except ValueError:

                raise ValueError(

                    f"{color!r} is not a valid color specification")



        self._color_sequences[name] = color_list



    def unregister(self, name):

        

        if name in self._BUILTIN_COLOR_SEQUENCES:

            raise ValueError(

                f"Cannot unregister builtin color sequence {name!r}")

        self._color_sequences.pop(name, None)





_color_sequences = ColorSequenceRegistry()





def _sanitize_extrema(ex):

    if ex is None:

        return ex

    try:

        ret = ex.item()

    except AttributeError:

        ret = float(ex)

    return ret



_nth_color_re = re.compile(r"\AC[0-9]+\Z")





def _is_nth_color(c):

    

    return isinstance(c, str) and _nth_color_re.match(c)





def is_color_like(c):

    

                                                                             

    if _is_nth_color(c):

        return True

    try:

        to_rgba(c)

    except (TypeError, ValueError):

        return False

    else:

        return True





def _has_alpha_channel(c):

    

                                                                           

                                                                               

                                    



                                                                                  

    if isinstance(c, str):

        if c[0] == '#' and (len(c) == 5 or len(c) == 9):

                                             

            return True

    else:

                                                                         

                                                     

        if len(c) == 4:

                                           

            return True



                                                      

                                                                              

        if len(c) == 2 and (c[1] is not None or _has_alpha_channel(c[0])):

                                                                 

            return True



                                                

    return False





def _check_color_like(**kwargs):

    

    for k, v in kwargs.items():

        if not is_color_like(v):

            raise ValueError(

                f"{v!r} is not a valid value for {k}: supported inputs are "

                f"(r, g, b) and (r, g, b, a) 0-1 float tuples; "

                f"'#rrggbb', '#rrggbbaa', '#rgb', '#rgba' strings; "

                f"named color strings; "

                f"string reprs of 0-1 floats for grayscale values; "

                f"'C0', 'C1', ... strings for colors of the color cycle; "

                f"and pairs combining one of the above with an alpha value")





def same_color(c1, c2):

    

    c1 = to_rgba_array(c1)

    c2 = to_rgba_array(c2)

    n1 = max(c1.shape[0], 1)                                                 

    n2 = max(c2.shape[0], 1)                                                 



    if n1 != n2:

        raise ValueError('Different number of elements passed.')

                                                                             

                                                                             

                           

    return c1.shape == c2.shape and (c1 == c2).all()





def to_rgba(c, alpha=None):

    

    if isinstance(c, tuple) and len(c) == 2:

        if alpha is None:

            c, alpha = c

        else:

            c = c[0]

                                                                    

    if _is_nth_color(c):

        prop_cycler = mpl.rcParams['axes.prop_cycle']

        colors = prop_cycler.by_key().get('color', ['k'])

        c = colors[int(c[1:]) % len(colors)]

    try:

        rgba = _colors_full_map.cache[c, alpha]

    except (KeyError, TypeError):                                

        rgba = None

    if rgba is None:                                                        

        rgba = _to_rgba_no_colorcycle(c, alpha)

        try:

            _colors_full_map.cache[c, alpha] = rgba

        except TypeError:

            pass

    return rgba





def _to_rgba_no_colorcycle(c, alpha=None):

    

    if alpha is not None and not 0 <= alpha <= 1:

        raise ValueError("'alpha' must be between 0 and 1, inclusive")

    orig_c = c

    if c is np.ma.masked:

        return (0., 0., 0., 0.)

    if isinstance(c, str):

        if c.lower() == "none":

            return (0., 0., 0., 0.)

                      

        try:

                                                                         

            c = _colors_full_map[c]

        except KeyError:

            if len(c) != 1:

                try:

                    c = _colors_full_map[c.lower()]

                except KeyError:

                    pass

    if isinstance(c, str):

        if re.fullmatch("#[a-fA-F0-9]+", c):

            if len(c) == 7:                       

                return (*[n / 0xff for n in bytes.fromhex(c[1:])],

                        alpha if alpha is not None else 1.)

            elif len(c) == 4:                                           

                return (*[int(n, 16) / 0xf for n in c[1:]],

                        alpha if alpha is not None else 1.)

            elif len(c) == 9:                         

                color = [n / 0xff for n in bytes.fromhex(c[1:])]

                if alpha is not None:

                    color[-1] = alpha

                return tuple(color)

            elif len(c) == 5:                                              

                color = [int(n, 16) / 0xf for n in c[1:]]

                if alpha is not None:

                    color[-1] = alpha

                return tuple(color)

            else:

                raise ValueError(f"Invalid hex color specifier: {orig_c!r}")

                      

        try:

            c = float(c)

        except ValueError:

            pass

        else:

            if not (0 <= c <= 1):

                raise ValueError(

                    f"Invalid string grayscale value {orig_c!r}. "

                    f"Value must be within 0-1 range")

            return c, c, c, alpha if alpha is not None else 1.

        raise ValueError(f"Invalid RGBA argument: {orig_c!r}")

                                   

    if isinstance(c, np.ndarray):

        if c.ndim == 2 and c.shape[0] == 1:

            c = c.reshape(-1)

                  

    if not np.iterable(c):

        raise ValueError(f"Invalid RGBA argument: {orig_c!r}")

    if len(c) not in [3, 4]:

        raise ValueError("RGBA sequence should have length 3 or 4")

    if not all(isinstance(x, Real) for x in c):

                                                                               

                                                                       

        raise ValueError(f"Invalid RGBA argument: {orig_c!r}")

                                                                     

    c = tuple(map(float, c))

    if len(c) == 3 and alpha is None:

        alpha = 1

    if alpha is not None:

        c = c[:3] + (alpha,)

    if any(elem < 0 or elem > 1 for elem in c):

        raise ValueError("RGBA values should be within 0-1 range")

    return c





def to_rgba_array(c, alpha=None):

    

    if isinstance(c, tuple) and len(c) == 2 and isinstance(c[1], Real):

        if alpha is None:

            c, alpha = c

        else:

            c = c[0]

                                                                            

                                                                             

                  

    if np.iterable(alpha):

        alpha = np.asarray(alpha).ravel()

    if (isinstance(c, np.ndarray) and c.dtype.kind in "if"

            and c.ndim == 2 and c.shape[1] in [3, 4]):

        mask = c.mask.any(axis=1) if np.ma.is_masked(c) else None

        c = np.ma.getdata(c)

        if np.iterable(alpha):

            if c.shape[0] == 1 and alpha.shape[0] > 1:

                c = np.tile(c, (alpha.shape[0], 1))

            elif c.shape[0] != alpha.shape[0]:

                raise ValueError("The number of colors must match the number"

                                 " of alpha values if there are more than one"

                                 " of each.")

        if c.shape[1] == 3:

            result = np.column_stack([c, np.zeros(len(c))])

            result[:, -1] = alpha if alpha is not None else 1.

        elif c.shape[1] == 4:

            result = c.copy()

            if alpha is not None:

                result[:, -1] = alpha

        if mask is not None:

            result[mask] = 0

        if np.any((result < 0) | (result > 1)):

            raise ValueError("RGBA values should be within 0-1 range")

        return result

                           

                                                                               

                                                                               

                                                       

    if cbook._str_lower_equal(c, "none"):

        return np.zeros((0, 4), float)

    try:

        if np.iterable(alpha):

            return np.array([to_rgba(c, a) for a in alpha], float)

        else:

            return np.array([to_rgba(c, alpha)], float)

    except TypeError:

        pass

    except ValueError as e:

        if e.args == ("'alpha' must be between 0 and 1, inclusive", ):

                                                          

            raise e

    if isinstance(c, str):

        raise ValueError(f"{c!r} is not a valid color value.")



    if len(c) == 0:

        return np.zeros((0, 4), float)



                                                                           

                        

    if isinstance(c, Sequence):

        lens = {len(cc) if isinstance(cc, (list, tuple)) else -1 for cc in c}

        if lens == {3}:

            rgba = np.column_stack([c, np.ones(len(c))])

        elif lens == {4}:

            rgba = np.array(c)

        else:

            rgba = np.array([to_rgba(cc) for cc in c])

    else:

        rgba = np.array([to_rgba(cc) for cc in c])



    if alpha is not None:

        rgba[:, 3] = alpha

        if isinstance(c, Sequence):

                                                                                

                        

            none_mask = [cbook._str_equal(cc, "none") for cc in c]

            rgba[:, 3][none_mask] = 0

    return rgba





def to_rgb(c):

    

    return to_rgba(c)[:3]





def to_hex(c, keep_alpha=False):

    

    c = to_rgba(c)

    if not keep_alpha:

        c = c[:3]

    return "#" + "".join(format(round(val * 255), "02x") for val in c)





                                             





cnames = CSS4_COLORS

hexColorPattern = re.compile(r"\A#[a-fA-F0-9]{6}\Z")

rgb2hex = to_hex

hex2color = to_rgb





class ColorConverter:

    

    colors = _colors_full_map

    cache = _colors_full_map.cache

    to_rgb = staticmethod(to_rgb)

    to_rgba = staticmethod(to_rgba)

    to_rgba_array = staticmethod(to_rgba_array)





colorConverter = ColorConverter()





                                                    





def _create_lookup_table(N, data, gamma=1.0):

    



    if callable(data):

        xind = np.linspace(0, 1, N) ** gamma

        lut = np.clip(np.array(data(xind), dtype=float), 0, 1)

        return lut



    try:

        adata = np.array(data)

    except Exception as err:

        raise TypeError("data must be convertible to an array") from err

    _api.check_shape((None, 3), data=adata)



    x = adata[:, 0]

    y0 = adata[:, 1]

    y1 = adata[:, 2]



    if x[0] != 0. or x[-1] != 1.0:

        raise ValueError(

            "data mapping points must start with x=0 and end with x=1")

    if (np.diff(x) < 0).any():

        raise ValueError("data mapping points must have x in increasing order")

                                      

    if N == 1:

                                                                           

        lut = np.array(y0[-1])

    else:

        x = x * (N - 1)

        xind = (N - 1) * np.linspace(0, 1, N) ** gamma

        ind = np.searchsorted(x, xind)[1:-1]



        distance = (xind[1:-1] - x[ind - 1]) / (x[ind] - x[ind - 1])

        lut = np.concatenate([

            [y1[0]],

            distance * (y0[ind] - y1[ind - 1]) + y1[ind - 1],

            [y0[-1]],

        ])

                                                                              

    return np.clip(lut, 0.0, 1.0)





class Colormap:

    



    def __init__(self, name, N=256, *, bad=None, under=None, over=None):

        

        self.name = name

        self.N = int(N)                               

        self._rgba_bad = (0.0, 0.0, 0.0, 0.0) if bad is None else to_rgba(bad)

        self._rgba_under = None if under is None else to_rgba(under)

        self._rgba_over = None if over is None else to_rgba(over)

        self._i_under = self.N

        self._i_over = self.N + 1

        self._i_bad = self.N + 2

        self._isinit = False

        self.n_variates = 1

                                                                             

                                                                              

                                                              

                                                      

        self.colorbar_extend = False



    def __call__(self, X, alpha=None, bytes=False):

        

        rgba, mask = self._get_rgba_and_mask(X, alpha=alpha, bytes=bytes)

        if not np.iterable(X):

            rgba = tuple(rgba)

        return rgba



    def _get_rgba_and_mask(self, X, alpha=None, bytes=False):

        

        if not self._isinit:

            self._init()



        xa = np.array(X, copy=True)

        if not xa.dtype.isnative:

                                         

            xa = xa.byteswap().view(xa.dtype.newbyteorder())

        if xa.dtype.kind == "f":

            xa *= self.N

                                                                      

            xa[xa == self.N] = self.N - 1

                                                                         

                                                                         

        mask_under = xa < 0

        mask_over = xa >= self.N

                                                                            

        mask_bad = X.mask if np.ma.is_masked(X) else np.isnan(xa)

        with np.errstate(invalid="ignore"):

                                                                   

            xa = xa.astype(int)

        xa[mask_under] = self._i_under

        xa[mask_over] = self._i_over

        xa[mask_bad] = self._i_bad



        lut = self._lut

        if bytes:

            lut = (lut * 255).astype(np.uint8)



        rgba = lut.take(xa, axis=0, mode='clip')



        if alpha is not None:

            alpha = np.clip(alpha, 0, 1)

            if bytes:

                alpha *= 255                                          

            if alpha.shape not in [(), xa.shape]:

                raise ValueError(

                    f"alpha is array-like but its shape {alpha.shape} does "

                    f"not match that of X {xa.shape}")

            rgba[..., -1] = alpha

                                                                       

            if (lut[-1] == 0).all():

                rgba[mask_bad] = (0, 0, 0, 0)



        return rgba, mask_bad



    def __copy__(self):

        cls = self.__class__

        cmapobject = cls.__new__(cls)

        cmapobject.__dict__.update(self.__dict__)

        if self._isinit:

            cmapobject._lut = np.copy(self._lut)

        return cmapobject



    def __eq__(self, other):

        if (not isinstance(other, Colormap) or

                self.colorbar_extend != other.colorbar_extend):

            return False

                                                                       

        if not self._isinit:

            self._init()

        if not other._isinit:

            other._init()

        return np.array_equal(self._lut, other._lut)



    def get_bad(self):

        

        if not self._isinit:

            self._init()

        return np.array(self._lut[self._i_bad])



    def set_bad(self, color='k', alpha=None):

        

        self._rgba_bad = to_rgba(color, alpha)

        if self._isinit:

            self._set_extremes()



    def get_under(self):

        

        if not self._isinit:

            self._init()

        return np.array(self._lut[self._i_under])



    def set_under(self, color='k', alpha=None):

        

        self._rgba_under = to_rgba(color, alpha)

        if self._isinit:

            self._set_extremes()



    def get_over(self):

        

        if not self._isinit:

            self._init()

        return np.array(self._lut[self._i_over])



    def set_over(self, color='k', alpha=None):

        

        self._rgba_over = to_rgba(color, alpha)

        if self._isinit:

            self._set_extremes()



    def set_extremes(self, *, bad=None, under=None, over=None):

        

        if bad is not None:

            self.set_bad(bad)

        if under is not None:

            self.set_under(under)

        if over is not None:

            self.set_over(over)



    def with_extremes(self, *, bad=None, under=None, over=None):

        

        new_cm = self.copy()

        new_cm.set_extremes(bad=bad, under=under, over=over)

        return new_cm



    def _set_extremes(self):

        if self._rgba_under:

            self._lut[self._i_under] = self._rgba_under

        else:

            self._lut[self._i_under] = self._lut[0]

        if self._rgba_over:

            self._lut[self._i_over] = self._rgba_over

        else:

            self._lut[self._i_over] = self._lut[self.N - 1]

        self._lut[self._i_bad] = self._rgba_bad



    def with_alpha(self, alpha):

        

        if not isinstance(alpha, Real):

            raise TypeError(f"'alpha' must be numeric or None, not {type(alpha)}")

        if not 0 <= alpha <= 1:

            raise ValueError("'alpha' must be between 0 and 1, inclusive")

        new_cm = self.copy()

        if not new_cm._isinit:

            new_cm._init()

        new_cm._lut[:, 3] = alpha

        return new_cm



    def _init(self):

        

        raise NotImplementedError("Abstract class only")



    def is_gray(self):

        

        if not self._isinit:

            self._init()

        return (np.all(self._lut[:, 0] == self._lut[:, 1]) and

                np.all(self._lut[:, 0] == self._lut[:, 2]))



    def resampled(self, lutsize):

        

        if hasattr(self, '_resample'):

            _api.warn_external(

                "The ability to resample a color map is now public API "

                f"However the class {type(self)} still only implements "

                "the previous private _resample method.  Please update "

                "your class."

            )

            return self._resample(lutsize)



        raise NotImplementedError()



    def reversed(self, name=None):

        

        raise NotImplementedError()



    def _repr_png_(self):

        

        X = np.tile(np.linspace(0, 1, _REPR_PNG_SIZE[0]),

                    (_REPR_PNG_SIZE[1], 1))

        pixels = self(X, bytes=True)

        png_bytes = io.BytesIO()

        title = self.name + ' colormap'

        author = f'Matplotlib v{mpl.__version__}, https://matplotlib.org'

        pnginfo = PngInfo()

        pnginfo.add_text('Title', title)

        pnginfo.add_text('Description', title)

        pnginfo.add_text('Author', author)

        pnginfo.add_text('Software', author)

        Image.fromarray(pixels).save(png_bytes, format='png', pnginfo=pnginfo)

        return png_bytes.getvalue()



    def _repr_html_(self):

        

        png_bytes = self._repr_png_()

        png_base64 = base64.b64encode(png_bytes).decode('ascii')

        def color_block(color):

            hex_color = to_hex(color, keep_alpha=True)

            return (f'<div title="{hex_color}" '

                    'style="display: inline-block; '

                    'width: 1em; height: 1em; '

                    'margin: 0; '

                    'vertical-align: middle; '

                    'border: 1px solid #555; '

                    f'background-color: {hex_color};"></div>')



        return ('<div style="vertical-align: middle;">'

                f'<strong>{self.name}</strong> '

                '</div>'

                '<div class="cmap"><img '

                f'alt="{self.name} colormap" '

                f'title="{self.name}" '

                'style="border: 1px solid #555;" '

                f'src="data:image/png;base64,{png_base64}"></div>'

                '<div style="vertical-align: middle; '

                f'max-width: {_REPR_PNG_SIZE[0]+2}px; '

                'display: flex; justify-content: space-between;">'

                '<div style="float: left;">'

                f'{color_block(self.get_under())} under'

                '</div>'

                '<div style="margin: 0 auto; display: inline-block;">'

                f'bad {color_block(self.get_bad())}'

                '</div>'

                '<div style="float: right;">'

                f'over {color_block(self.get_over())}'

                '</div>'

                '</div>')



    def copy(self):

        

        return self.__copy__()





class LinearSegmentedColormap(Colormap):

    



    def __init__(self, name, segmentdata, N=256, gamma=1.0, *,

                 bad=None, under=None, over=None):

        

                                                                              

        self.monochrome = False

        super().__init__(name, N, bad=bad, under=under, over=over)

        self._segmentdata = segmentdata

        self._gamma = gamma



    def _init(self):

        self._lut = np.ones((self.N + 3, 4), float)

        self._lut[:-3, 0] = _create_lookup_table(

            self.N, self._segmentdata['red'], self._gamma)

        self._lut[:-3, 1] = _create_lookup_table(

            self.N, self._segmentdata['green'], self._gamma)

        self._lut[:-3, 2] = _create_lookup_table(

            self.N, self._segmentdata['blue'], self._gamma)

        if 'alpha' in self._segmentdata:

            self._lut[:-3, 3] = _create_lookup_table(

                self.N, self._segmentdata['alpha'], 1)

        self._isinit = True

        self._set_extremes()



    def set_gamma(self, gamma):

        

        self._gamma = gamma

        self._init()



    @staticmethod

    def from_list(name, colors, N=256, gamma=1.0, *, bad=None, under=None, over=None):

        

        if not np.iterable(colors):

            raise ValueError('colors must be iterable')



        try:

                                                           

                                             

            r, g, b, a = to_rgba_array(colors).T

            vals = np.linspace(0, 1, len(colors))

        except Exception as e:

                                                    

                                    

            try:

                _vals, _colors = itertools.zip_longest(*colors)

            except Exception as e2:

                raise e2 from e

            vals = np.asarray(_vals)

            if np.min(vals) < 0 or np.max(vals) > 1 or np.any(np.diff(vals) <= 0):

                raise ValueError(

                    "the values passed in the (value, color) pairs "

                    "must increase monotonically from 0 to 1."

                )

            r, g, b, a = to_rgba_array(_colors).T



        cdict = {

            "red": np.column_stack([vals, r, r]),

            "green": np.column_stack([vals, g, g]),

            "blue": np.column_stack([vals, b, b]),

            "alpha": np.column_stack([vals, a, a]),

        }



        return LinearSegmentedColormap(name, cdict, N, gamma,

                                       bad=bad, under=under, over=over)



    def resampled(self, lutsize):

        

        new_cmap = LinearSegmentedColormap(self.name, self._segmentdata,

                                           lutsize)

        new_cmap._rgba_over = self._rgba_over

        new_cmap._rgba_under = self._rgba_under

        new_cmap._rgba_bad = self._rgba_bad

        return new_cmap



                                                        

    @staticmethod

    def _reverser(func, x):

        return func(1 - x)



    def reversed(self, name=None):

        

        if name is None:

            name = self.name + "_r"



                                                          

        data_r = {key: (functools.partial(self._reverser, data)

                        if callable(data) else

                        [(1.0 - x, y1, y0) for x, y0, y1 in reversed(data)])

                  for key, data in self._segmentdata.items()}



        new_cmap = LinearSegmentedColormap(name, data_r, self.N, self._gamma)

                                           

        new_cmap._rgba_over = self._rgba_under

        new_cmap._rgba_under = self._rgba_over

        new_cmap._rgba_bad = self._rgba_bad

        return new_cmap





class ListedColormap(Colormap):

    



    @_api.delete_parameter(

        "3.11", "N",

        message="Passing 'N' to ListedColormap is deprecated since %(since)s "

                "and will be removed in %(removal)s. Please ensure the list "

                "of passed colors is the required length instead."

    )

    def __init__(self, colors, name='from_list', N=None, *,

                 bad=None, under=None, over=None):

        if N is None:

            self.colors = colors

            N = len(colors)

        else:

            if isinstance(colors, str):

                self.colors = [colors] * N

            elif np.iterable(colors):

                self.colors = list(

                    itertools.islice(itertools.cycle(colors), N))

            else:

                try:

                    gray = float(colors)

                except TypeError:

                    pass

                else:

                    self.colors = [gray] * N

        super().__init__(name, N, bad=bad, under=under, over=over)



    def _init(self):

        self._lut = np.zeros((self.N + 3, 4), float)

        self._lut[:-3] = to_rgba_array(self.colors)

        self._isinit = True

        self._set_extremes()



    @property

    def monochrome(self):

        

                                                                               

                                                                               

                                                          

         

                                                                           

                                                                                   

                                                                

        if not self._isinit:

            self._init()



        return self.N <= 1 or np.all(self._lut[0] == self._lut[1:self.N])



    def resampled(self, lutsize):

        

        colors = self(np.linspace(0, 1, lutsize))

        new_cmap = ListedColormap(colors, name=self.name)

                                        

        new_cmap._rgba_over = self._rgba_over

        new_cmap._rgba_under = self._rgba_under

        new_cmap._rgba_bad = self._rgba_bad

        return new_cmap



    def reversed(self, name=None):

        

        if name is None:

            name = self.name + "_r"



        colors_r = list(reversed(self.colors))

        new_cmap = ListedColormap(colors_r, name=name)

                                           

        new_cmap._rgba_over = self._rgba_under

        new_cmap._rgba_under = self._rgba_over

        new_cmap._rgba_bad = self._rgba_bad

        return new_cmap





class MultivarColormap:

    

    def __init__(self, colormaps, combination_mode, name='multivariate colormap'):

        

        self.name = name



        if not np.iterable(colormaps)
           or len(colormaps) == 1
           or isinstance(colormaps, str):

            raise ValueError("A MultivarColormap must have more than one colormap.")

        colormaps = list(colormaps)                                            

        for i, cmap in enumerate(colormaps):

            if isinstance(cmap, str):

                colormaps[i] = mpl.colormaps[cmap]

            elif not isinstance(cmap, Colormap):

                raise ValueError("colormaps must be a list of objects that subclass"

                                 " Colormap or a name found in the colormap registry.")



        self._colormaps = colormaps

        _api.check_in_list(['sRGB_add', 'sRGB_sub'], combination_mode=combination_mode)

        self._combination_mode = combination_mode

        self.n_variates = len(colormaps)

        self._rgba_bad = (0.0, 0.0, 0.0, 0.0)                                 



    def __call__(self, X, alpha=None, bytes=False, clip=True):

        



        if len(X) != len(self):

            raise ValueError(

                f'For the selected colormap the data must have a first dimension '

                f'{len(self)}, not {len(X)}')

        rgba, mask_bad = self[0]._get_rgba_and_mask(X[0], bytes=False)

        for c, xx in zip(self[1:], X[1:]):

            sub_rgba, sub_mask_bad = c._get_rgba_and_mask(xx, bytes=False)

            rgba[..., :3] += sub_rgba[..., :3]              

            rgba[..., 3] *= sub_rgba[..., 3]                  

            mask_bad |= sub_mask_bad



        if self.combination_mode == 'sRGB_sub':

            rgba[..., :3] -= len(self) - 1



        rgba[mask_bad] = self.get_bad()



        if clip:

            rgba = np.clip(rgba, 0, 1)



        if alpha is not None:

            if clip:

                alpha = np.clip(alpha, 0, 1)

            if np.shape(alpha) not in [(), np.shape(X[0])]:

                raise ValueError(

                    f"alpha is array-like but its shape {np.shape(alpha)} does "

                    f"not match that of X[0] {np.shape(X[0])}")

            rgba[..., -1] *= alpha



        if bytes:

            if not clip:

                raise ValueError(

                    "clip cannot be false while bytes is true"

                    " as uint8 does not support values below 0"

                    " or above 255.")

            rgba = (rgba * 255).astype('uint8')



        if not np.iterable(X[0]):

            rgba = tuple(rgba)



        return rgba



    def copy(self):

        

        return self.__copy__()



    def __copy__(self):

        cls = self.__class__

        cmapobject = cls.__new__(cls)

        cmapobject.__dict__.update(self.__dict__)

        cmapobject._colormaps = [cm.copy() for cm in self._colormaps]

        cmapobject._rgba_bad = np.copy(self._rgba_bad)

        return cmapobject



    def __eq__(self, other):

        if not isinstance(other, MultivarColormap):

            return False

        if len(self) != len(other):

            return False

        for c0, c1 in zip(self, other):

            if c0 != c1:

                return False

        if not all(self._rgba_bad == other._rgba_bad):

            return False

        if self.combination_mode != other.combination_mode:

            return False

        return True



    def __getitem__(self, item):

        return self._colormaps[item]



    def __iter__(self):

        for c in self._colormaps:

            yield c



    def __len__(self):

        return len(self._colormaps)



    def __str__(self):

        return self.name



    def get_bad(self):

        

        return np.array(self._rgba_bad)



    def resampled(self, lutshape):

        



        if not np.iterable(lutshape) or len(lutshape) != len(self):

            raise ValueError(f"lutshape must be of length {len(self)}")

        new_cmap = self.copy()

        for i, s in enumerate(lutshape):

            if s is not None:

                new_cmap._colormaps[i] = self[i].resampled(s)

        return new_cmap



    def with_extremes(self, *, bad=None, under=None, over=None):

        

        new_cm = self.copy()

        if bad is not None:

            new_cm._rgba_bad = to_rgba(bad)

        if under is not None:

            if not np.iterable(under) or len(under) != len(new_cm):

                raise ValueError("*under* must contain a color for each scalar colormap"

                                 f" i.e. be of length {len(new_cm)}.")

            else:

                for c, b in zip(new_cm, under):

                    c.set_under(b)

        if over is not None:

            if not np.iterable(over) or len(over) != len(new_cm):

                raise ValueError("*over* must contain a color for each scalar colormap"

                                 f" i.e. be of length {len(new_cm)}.")

            else:

                for c, b in zip(new_cm, over):

                    c.set_over(b)

        return new_cm



    @property

    def combination_mode(self):

        return self._combination_mode



    def _repr_png_(self):

        

        X = np.tile(np.linspace(0, 1, _REPR_PNG_SIZE[0]),

                                (_REPR_PNG_SIZE[1], 1))

        pixels = np.zeros((_REPR_PNG_SIZE[1]*len(self), _REPR_PNG_SIZE[0], 4),

                          dtype=np.uint8)

        for i, c in enumerate(self):

            pixels[i*_REPR_PNG_SIZE[1]:(i+1)*_REPR_PNG_SIZE[1], :] = c(X, bytes=True)

        png_bytes = io.BytesIO()

        title = self.name + ' multivariate colormap'

        author = f'Matplotlib v{mpl.__version__}, https://matplotlib.org'

        pnginfo = PngInfo()

        pnginfo.add_text('Title', title)

        pnginfo.add_text('Description', title)

        pnginfo.add_text('Author', author)

        pnginfo.add_text('Software', author)

        Image.fromarray(pixels).save(png_bytes, format='png', pnginfo=pnginfo)

        return png_bytes.getvalue()



    def _repr_html_(self):

        

        return ''.join([c._repr_html_() for c in self._colormaps])





class BivarColormap:

    



    def __init__(self, N=256, M=256, shape='square', origin=(0, 0),

                 name='bivariate colormap'):

        



        self.name = name

        self.N = int(N)                               

        self.M = int(M)

        _api.check_in_list(['square', 'circle', 'ignore', 'circleignore'], shape=shape)

        self._shape = shape

        self._rgba_bad = (0.0, 0.0, 0.0, 0.0)                                 

        self._rgba_outside = (1.0, 0.0, 1.0, 1.0)

        self._isinit = False

        self.n_variates = 2

        self._origin = (float(origin[0]), float(origin[1]))

        '''#: When this colormap exists on a scalar mappable and colorbar_extend
        #: is not False, colorbar creation will pick up ``colorbar_extend`` as
        #: the default value for the ``extend`` keyword in the
        #: `matplotlib.colorbar.Colorbar` constructor.
        self.colorbar_extend = False'''



    def __call__(self, X, alpha=None, bytes=False):

        



        if len(X) != 2:

            raise ValueError(

                f'For a `BivarColormap` the data must have a first dimension '

                f'2, not {len(X)}')



        if not self._isinit:

            self._init()



        X0 = np.ma.array(X[0], copy=True)

        X1 = np.ma.array(X[1], copy=True)

                                                        

        self._clip((X0, X1))



                                     

        if not X0.dtype.isnative:

            X0 = X0.byteswap().view(X0.dtype.newbyteorder())

        if not X1.dtype.isnative:

            X1 = X1.byteswap().view(X1.dtype.newbyteorder())



        if X0.dtype.kind == "f":

            X0 *= self.N

                                                                      

            X0[X0 == self.N] = self.N - 1



        if X1.dtype.kind == "f":

            X1 *= self.M

                                                                      

            X1[X1 == self.M] = self.M - 1



                                                                          

        mask_outside = (X0 < 0) | (X1 < 0) | (X0 >= self.N) | (X1 >= self.M)

                                                                            

        mask_bad_0 = X0.mask if np.ma.is_masked(X0) else np.isnan(X0)

        mask_bad_1 = X1.mask if np.ma.is_masked(X1) else np.isnan(X1)

        mask_bad = mask_bad_0 | mask_bad_1



        with np.errstate(invalid="ignore"):

                                                                   

            X0 = X0.astype(int)

            X1 = X1.astype(int)



                                   

                                                             

        for X_part in [X0, X1]:

            X_part[mask_outside] = 0

            X_part[mask_bad] = 0



        rgba = self._lut[X0, X1]

        if np.isscalar(X[0]):

            rgba = np.copy(rgba)

        rgba[mask_outside] = self._rgba_outside

        rgba[mask_bad] = self._rgba_bad

        if bytes:

            rgba = (rgba * 255).astype(np.uint8)

        if alpha is not None:

            alpha = np.clip(alpha, 0, 1)

            if bytes:

                alpha *= 255                                          

            if np.shape(alpha) not in [(), np.shape(X0)]:

                raise ValueError(

                    f"alpha is array-like but its shape {np.shape(alpha)} does "

                    f"not match that of X[0] {np.shape(X0)}")

            rgba[..., -1] = alpha

                                                                       

            if (np.array(self._rgba_bad) == 0).all():

                rgba[mask_bad] = (0, 0, 0, 0)



        if not np.iterable(X[0]):

            rgba = tuple(rgba)

        return rgba



    @property

    def lut(self):

        

        if not self._isinit:

            self._init()

        lut = np.copy(self._lut)

        if self.shape == 'circle' or self.shape == 'circleignore':

            n = np.linspace(-1, 1, self.N)

            m = np.linspace(-1, 1, self.M)

            radii_sqr = (n**2)[:, np.newaxis] + (m**2)[np.newaxis, :]

            mask_outside = radii_sqr > 1

            lut[mask_outside, 3] = 0

        return lut



    def __copy__(self):

        cls = self.__class__

        cmapobject = cls.__new__(cls)

        cmapobject.__dict__.update(self.__dict__)



        cmapobject._rgba_outside = np.copy(self._rgba_outside)

        cmapobject._rgba_bad = np.copy(self._rgba_bad)

        cmapobject._shape = self.shape

        if self._isinit:

            cmapobject._lut = np.copy(self._lut)

        return cmapobject



    def __eq__(self, other):

        if not isinstance(other, BivarColormap):

            return False

                                                                       

        if not self._isinit:

            self._init()

        if not other._isinit:

            other._init()

        if not np.array_equal(self._lut, other._lut):

            return False

        if not np.array_equal(self._rgba_bad, other._rgba_bad):

            return False

        if not np.array_equal(self._rgba_outside, other._rgba_outside):

            return False

        if self.shape != other.shape:

            return False

        return True



    def get_bad(self):

        

        return self._rgba_bad



    def get_outside(self):

        

        return self._rgba_outside



    def resampled(self, lutshape, transposed=False):

        



        if not np.iterable(lutshape) or len(lutshape) != 2:

            raise ValueError("lutshape must be of length 2")

        lutshape = [lutshape[0], lutshape[1]]

        if lutshape[0] is None or lutshape[0] == 1:

            lutshape[0] = self.N

        if lutshape[1] is None or lutshape[1] == 1:

            lutshape[1] = self.M



        inverted = [False, False]

        if lutshape[0] < 0:

            inverted[0] = True

            lutshape[0] = -lutshape[0]

            if lutshape[0] == 1:

                lutshape[0] = self.N

        if lutshape[1] < 0:

            inverted[1] = True

            lutshape[1] = -lutshape[1]

            if lutshape[1] == 1:

                lutshape[1] = self.M

        x_0, x_1 = np.mgrid[0:1:(lutshape[0] * 1j), 0:1:(lutshape[1] * 1j)]

        if inverted[0]:

            x_0 = x_0[::-1, :]

        if inverted[1]:

            x_1 = x_1[:, ::-1]



                                                                        

                                                                                      

                            

        shape_memory = self._shape

        self._shape = 'square'

        if transposed:

            new_lut = self((x_1, x_0))

            new_cmap = BivarColormapFromImage(new_lut, name=self.name,

                                              shape=shape_memory,

                                              origin=self.origin[::-1])

        else:

            new_lut = self((x_0, x_1))

            new_cmap = BivarColormapFromImage(new_lut, name=self.name,

                                              shape=shape_memory,

                                              origin=self.origin)

        self._shape = shape_memory



        new_cmap._rgba_bad = self._rgba_bad

        new_cmap._rgba_outside = self._rgba_outside

        return new_cmap



    def reversed(self, axis_0=True, axis_1=True):

        

        r_0 = -1 if axis_0 else 1

        r_1 = -1 if axis_1 else 1

        return self.resampled((r_0, r_1))



    def transposed(self):

        

        return self.resampled((None, None), transposed=True)



    def with_extremes(self, *, bad=None, outside=None, shape=None, origin=None):

        

        new_cm = self.copy()

        if bad is not None:

            new_cm._rgba_bad = to_rgba(bad)

        if outside is not None:

            new_cm._rgba_outside = to_rgba(outside)

        if shape is not None:

            _api.check_in_list(['square', 'circle', 'ignore', 'circleignore'],

                               shape=shape)

            new_cm._shape = shape

        if origin is not None:

            new_cm._origin = (float(origin[0]), float(origin[1]))



        return new_cm



    def _init(self):

        

        raise NotImplementedError("Abstract class only")



    @property

    def shape(self):

        return self._shape



    @property

    def origin(self):

        return self._origin



    def _clip(self, X):

        

        if self.shape == 'square':

            for X_part, mx in zip(X, (self.N, self.M)):

                X_part[X_part < 0] = 0

                if X_part.dtype.kind == "f":

                    X_part[X_part > 1] = 1

                else:

                    X_part[X_part >= mx] = mx - 1



        elif self.shape == 'ignore':

            for X_part, mx in zip(X, (self.N, self.M)):

                X_part[X_part < 0] = -1

                if X_part.dtype.kind == "f":

                    X_part[X_part > 1] = -1

                else:

                    X_part[X_part >= mx] = -1



        elif self.shape == 'circle' or self.shape == 'circleignore':

            for X_part in X:

                if X_part.dtype.kind != "f":

                    raise NotImplementedError(

                        "Circular bivariate colormaps are only"

                        " implemented for use with with floats")

            radii_sqr = (X[0] - 0.5)**2 + (X[1] - 0.5)**2

            mask_outside = radii_sqr > 0.25

            if self.shape == 'circle':

                overextend = 2 * np.sqrt(radii_sqr[mask_outside])

                X[0][mask_outside] = (X[0][mask_outside] - 0.5) / overextend + 0.5

                X[1][mask_outside] = (X[1][mask_outside] - 0.5) / overextend + 0.5

            else:

                X[0][mask_outside] = -1

                X[1][mask_outside] = -1



    def __getitem__(self, item):

        

        if not self._isinit:

            self._init()

        if item == 0:

            origin_1_as_int = int(self._origin[1]*self.M)

            if origin_1_as_int > self.M-1:

                origin_1_as_int = self.M-1

            one_d_lut = self._lut[:, origin_1_as_int]

            new_cmap = ListedColormap(one_d_lut, name=f'{self.name}_0')



        elif item == 1:

            origin_0_as_int = int(self._origin[0]*self.N)

            if origin_0_as_int > self.N-1:

                origin_0_as_int = self.N-1

            one_d_lut = self._lut[origin_0_as_int, :]

            new_cmap = ListedColormap(one_d_lut, name=f'{self.name}_1')

        else:

            raise KeyError(f"only 0 or 1 are"

                           f" valid keys for BivarColormap, not {item!r}")

        new_cmap._rgba_bad = self._rgba_bad

        if self.shape in ['ignore', 'circleignore']:

            new_cmap.set_over(self._rgba_outside)

            new_cmap.set_under(self._rgba_outside)

        return new_cmap



    def _repr_png_(self):

        

        if not self._isinit:

            self._init()

        pixels = self.lut

        if pixels.shape[0] < _BIVAR_REPR_PNG_SIZE:

            pixels = np.repeat(pixels,

                               repeats=_BIVAR_REPR_PNG_SIZE//pixels.shape[0],

                               axis=0)[:256, :]

        if pixels.shape[1] < _BIVAR_REPR_PNG_SIZE:

            pixels = np.repeat(pixels,

                               repeats=_BIVAR_REPR_PNG_SIZE//pixels.shape[1],

                               axis=1)[:, :256]

        pixels = (pixels[::-1, :, :] * 255).astype(np.uint8)

        png_bytes = io.BytesIO()

        title = self.name + ' BivarColormap'

        author = f'Matplotlib v{mpl.__version__}, https://matplotlib.org'

        pnginfo = PngInfo()

        pnginfo.add_text('Title', title)

        pnginfo.add_text('Description', title)

        pnginfo.add_text('Author', author)

        pnginfo.add_text('Software', author)

        Image.fromarray(pixels).save(png_bytes, format='png', pnginfo=pnginfo)

        return png_bytes.getvalue()



    def _repr_html_(self):

        

        png_bytes = self._repr_png_()

        png_base64 = base64.b64encode(png_bytes).decode('ascii')

        def color_block(color):

            hex_color = to_hex(color, keep_alpha=True)

            return (f'<div title="{hex_color}" '

                    'style="display: inline-block; '

                    'width: 1em; height: 1em; '

                    'margin: 0; '

                    'vertical-align: middle; '

                    'border: 1px solid #555; '

                    f'background-color: {hex_color};"></div>')



        return ('<div style="vertical-align: middle;">'

                f'<strong>{self.name}</strong> '

                '</div>'

                '<div class="cmap"><img '

                f'alt="{self.name} BivarColormap" '

                f'title="{self.name}" '

                'style="border: 1px solid #555;" '

                f'src="data:image/png;base64,{png_base64}"></div>'

                '<div style="vertical-align: middle; '

                f'max-width: {_BIVAR_REPR_PNG_SIZE+2}px; '

                'display: flex; justify-content: space-between;">'

                '<div style="float: left;">'

                f'{color_block(self.get_outside())} outside'

                '</div>'

                '<div style="float: right;">'

                f'bad {color_block(self.get_bad())}'

                '</div></div>')



    def copy(self):

        

        return self.__copy__()





class SegmentedBivarColormap(BivarColormap):

    



    def __init__(self, patch, N=256, shape='square', origin=(0, 0),

                 name='segmented bivariate colormap'):

        _api.check_shape((None, None, 3), patch=patch)

        self.patch = patch

        super().__init__(N, N, shape, origin, name=name)



    def _init(self):

        s = self.patch.shape

        _patch = np.empty((s[0], s[1], 4))

        _patch[:, :, :3] = self.patch

        _patch[:, :, 3] = 1

        transform = mpl.transforms.Affine2D().translate(-0.5, -0.5)
                                .scale(self.N / (s[1] - 1), self.N / (s[0] - 1))

        self._lut = np.empty((self.N, self.N, 4))



        _image.resample(_patch, self._lut, transform, _image.BILINEAR,

                        resample=False, alpha=1)

        self._isinit = True





class BivarColormapFromImage(BivarColormap):

    



    def __init__(self, lut, shape='square', origin=(0, 0), name='from image'):

                                                                                   

                                                                      

                                                           

               

                                    

                                          

        lut = np.array(lut, copy=True)

        if lut.ndim != 3 or lut.shape[2] not in (3, 4):

            raise ValueError("The lut must be an array of shape (n, m, 3) or (n, m, 4)",

                             " or a PIL.image encoded as RGB or RGBA")



        if lut.dtype == np.uint8:

            lut = lut.astype(np.float32)/255

        if lut.shape[2] == 3:

            new_lut = np.empty((lut.shape[0], lut.shape[1], 4), dtype=lut.dtype)

            new_lut[:, :, :3] = lut

            new_lut[:, :, 3] = 1.

            lut = new_lut

        self._lut = lut

        super().__init__(lut.shape[0], lut.shape[1], shape, origin, name=name)



    def _init(self):

        self._isinit = True





class Norm(ABC):

    



    def __init__(self):

        self.callbacks = cbook.CallbackRegistry(signals=["changed"])



    @property

    @abstractmethod

    def vmin(self):

        

        pass



    @property

    @abstractmethod

    def vmax(self):

        

        pass



    @property

    @abstractmethod

    def clip(self):

        

        pass



    @abstractmethod

    def __call__(self, value, clip=None):

        

        pass



    @abstractmethod

    def autoscale(self, A):

        

        pass



    @abstractmethod

    def autoscale_None(self, A):

        

        pass



    @abstractmethod

    def scaled(self):

        

        pass



    def _changed(self):

        

        self.callbacks.process('changed')



    @property

    @abstractmethod

    def n_components(self):

        

        pass





class Normalize(Norm):

    



    def __init__(self, vmin=None, vmax=None, clip=False):

        

        super().__init__()

        self._vmin = _sanitize_extrema(vmin)

        self._vmax = _sanitize_extrema(vmax)

        self._clip = clip

        self._scale = None



    @property

    def vmin(self):

                             

        return self._vmin



    @vmin.setter

    def vmin(self, value):

        value = _sanitize_extrema(value)

        if value != self._vmin:

            self._vmin = value

            self._changed()



    @property

    def vmax(self):

                             

        return self._vmax



    @vmax.setter

    def vmax(self, value):

        value = _sanitize_extrema(value)

        if value != self._vmax:

            self._vmax = value

            self._changed()



    @property

    def clip(self):

                             

        return self._clip



    @clip.setter

    def clip(self, value):

        if value != self._clip:

            self._clip = value

            self._changed()



    @staticmethod

    def process_value(value):

        

        is_scalar = not np.iterable(value)

        if is_scalar:

            value = [value]

        dtype = np.min_scalar_type(value)

        if np.issubdtype(dtype, np.integer) or dtype.type is np.bool_:

                                                                 

            dtype = np.promote_types(dtype, np.float32)

                                                                         

                                      

        mask = np.ma.getmask(value)

        data = np.asarray(value)

        result = np.ma.array(data, mask=mask, dtype=dtype, copy=True)

        return result, is_scalar



    def __call__(self, value, clip=None):

                             

        if clip is None:

            clip = self.clip



        result, is_scalar = self.process_value(value)



        if self.vmin is None or self.vmax is None:

            self.autoscale_None(result)

                                                              

        (vmin,), _ = self.process_value(self.vmin)

        (vmax,), _ = self.process_value(self.vmax)

        if vmin == vmax:

            result.fill(0)                                        

        elif vmin > vmax:

            raise ValueError("minvalue must be less than or equal to maxvalue")

        else:

            if clip:

                mask = np.ma.getmask(result)

                result = np.ma.array(np.clip(result.filled(vmax), vmin, vmax),

                                     mask=mask)

                                                              

            resdat = result.data

            resdat -= vmin

            resdat /= (vmax - vmin)

            result = np.ma.array(resdat, mask=result.mask, copy=False)

        if is_scalar:

            result = result[0]

        return result



    def inverse(self, value):

        

        if not self.scaled():

            raise ValueError("Not invertible until both vmin and vmax are set")

        (vmin,), _ = self.process_value(self.vmin)

        (vmax,), _ = self.process_value(self.vmax)



        if np.iterable(value):

            val = np.ma.asarray(value)

            return vmin + val * (vmax - vmin)

        else:

            return vmin + value * (vmax - vmin)



    def autoscale(self, A):

                             

        with self.callbacks.blocked():

                                                                  

                                               

            self.vmin = self.vmax = None

            self.autoscale_None(A)

        self._changed()



    def autoscale_None(self, A):

                             

        A = np.asanyarray(A)



        if isinstance(A, np.ma.MaskedArray):

                                                                                      

            if A.mask is False or not A.mask.shape:

                A = A.data



        if self.vmin is None and A.size:

            self.vmin = A.min()

        if self.vmax is None and A.size:

            self.vmax = A.max()



    def scaled(self):

                             

        return self.vmin is not None and self.vmax is not None



    @property

    def n_components(self):

        

        return 1





class TwoSlopeNorm(Normalize):

    def __init__(self, vcenter, vmin=None, vmax=None):

        



        super().__init__(vmin=vmin, vmax=vmax)

        self._vcenter = vcenter

        if vcenter is not None and vmax is not None and vcenter >= vmax:

            raise ValueError('vmin, vcenter, and vmax must be in '

                             'ascending order')

        if vcenter is not None and vmin is not None and vcenter <= vmin:

            raise ValueError('vmin, vcenter, and vmax must be in '

                             'ascending order')



    @property

    def vcenter(self):

        return self._vcenter



    @vcenter.setter

    def vcenter(self, value):

        if value != self._vcenter:

            self._vcenter = value

            self._changed()



    def autoscale_None(self, A):

        

        super().autoscale_None(A)

        if self.vmin >= self.vcenter:

            self.vmin = self.vcenter - (self.vmax - self.vcenter)

        if self.vmax <= self.vcenter:

            self.vmax = self.vcenter + (self.vcenter - self.vmin)



    def __call__(self, value, clip=None):

        

        result, is_scalar = self.process_value(value)

        self.autoscale_None(result)                                     



        if not self.vmin <= self.vcenter <= self.vmax:

            raise ValueError("vmin, vcenter, vmax must increase monotonically")

                                                          

        result = np.ma.masked_array(

            np.interp(result, [self.vmin, self.vcenter, self.vmax],

                      [0, 0.5, 1], left=-np.inf, right=np.inf),

            mask=np.ma.getmask(result))

        if is_scalar:

            result = np.atleast_1d(result)[0]

        return result



    def inverse(self, value):

        if not self.scaled():

            raise ValueError("Not invertible until both vmin and vmax are set")

        (vmin,), _ = self.process_value(self.vmin)

        (vmax,), _ = self.process_value(self.vmax)

        (vcenter,), _ = self.process_value(self.vcenter)

        result = np.interp(value, [0, 0.5, 1], [vmin, vcenter, vmax],

                           left=-np.inf, right=np.inf)

        return result





class CenteredNorm(Normalize):

    def __init__(self, vcenter=0, halfrange=None, clip=False):

        

        super().__init__(vmin=None, vmax=None, clip=clip)

        self._vcenter = vcenter

                                                           

        self.halfrange = halfrange



    def autoscale(self, A):

        

        A = np.asanyarray(A)

        self.halfrange = max(self._vcenter-A.min(),

                             A.max()-self._vcenter)



    def autoscale_None(self, A):

        

        A = np.asanyarray(A)

        if self.halfrange is None and A.size:

            self.autoscale(A)



    @property

    def vmin(self):

        return self._vmin



    @vmin.setter

    def vmin(self, value):

        value = _sanitize_extrema(value)

        if value != self._vmin:

            self._vmin = value

            self._vmax = 2*self.vcenter - value

            self._changed()



    @property

    def vmax(self):

        return self._vmax



    @vmax.setter

    def vmax(self, value):

        value = _sanitize_extrema(value)

        if value != self._vmax:

            self._vmax = value

            self._vmin = 2*self.vcenter - value

            self._changed()



    @property

    def vcenter(self):

        return self._vcenter



    @vcenter.setter

    def vcenter(self, vcenter):

        if vcenter != self._vcenter:

            self._vcenter = vcenter

                                                                          

            self.halfrange = self.halfrange

            self._changed()



    @property

    def halfrange(self):

        if self.vmin is None or self.vmax is None:

            return None

        return (self.vmax - self.vmin) / 2



    @halfrange.setter

    def halfrange(self, halfrange):

        if halfrange is None:

            self.vmin = None

            self.vmax = None

        else:

            self.vmin = self.vcenter - abs(halfrange)

            self.vmax = self.vcenter + abs(halfrange)





def make_norm_from_scale(scale_cls, base_norm_cls=None, *, init=None):

    



    if base_norm_cls is None:

        return functools.partial(make_norm_from_scale, scale_cls, init=init)



    if isinstance(scale_cls, functools.partial):

        scale_args = scale_cls.args

        scale_kwargs_items = tuple(scale_cls.keywords.items())

        scale_cls = scale_cls.func

    else:

        scale_args = scale_kwargs_items = ()



    if init is None:

        def init(vmin=None, vmax=None, clip=False): pass



    return _make_norm_from_scale(

        scale_cls, scale_args, scale_kwargs_items,

        base_norm_cls, inspect.signature(init))





@functools.cache

def _make_norm_from_scale(

    scale_cls, scale_args, scale_kwargs_items,

    base_norm_cls, bound_init_signature,

):

    



    class ScaleNorm(base_norm_cls):

        def __reduce__(self):

            cls = type(self)

                                                                             

                                                                            

                                                                           

                                                                              

                                                                               

                               

            try:

                if cls is getattr(importlib.import_module(cls.__module__),

                                  cls.__qualname__):

                    return (_create_empty_object_of_class, (cls,), vars(self))

            except (ImportError, AttributeError):

                pass

            return (_picklable_norm_constructor,

                    (scale_cls, scale_args, scale_kwargs_items,

                     base_norm_cls, bound_init_signature),

                    vars(self))



        def __init__(self, *args, **kwargs):

            ba = bound_init_signature.bind(*args, **kwargs)

            ba.apply_defaults()

            super().__init__(

                **{k: ba.arguments.pop(k) for k in ["vmin", "vmax", "clip"]})

            self._scale = functools.partial(

                scale_cls, *scale_args, **dict(scale_kwargs_items))(

                    axis=None, **ba.arguments)

            self._trf = self._scale.get_transform()



        __init__.__signature__ = bound_init_signature.replace(parameters=[

            inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD),

            *bound_init_signature.parameters.values()])



        def __call__(self, value, clip=None):

            value, is_scalar = self.process_value(value)

            if self.vmin is None or self.vmax is None:

                self.autoscale_None(value)

            if self.vmin > self.vmax:

                raise ValueError("vmin must be less or equal to vmax")

            if self.vmin == self.vmax:

                return np.full_like(value, 0)

            if clip is None:

                clip = self.clip

            if clip:

                value = np.clip(value, self.vmin, self.vmax)

            t_value = self._trf.transform(value).reshape(np.shape(value))

            t_vmin, t_vmax = self._trf.transform([self.vmin, self.vmax])

            if not np.isfinite([t_vmin, t_vmax]).all():

                raise ValueError("Invalid vmin or vmax")

            t_value -= t_vmin

            t_value /= (t_vmax - t_vmin)

            t_value = np.ma.masked_invalid(t_value, copy=False)

            return t_value[0] if is_scalar else t_value



        def inverse(self, value):

            if not self.scaled():

                raise ValueError("Not invertible until scaled")

            if self.vmin > self.vmax:

                raise ValueError("vmin must be less or equal to vmax")

            t_vmin, t_vmax = self._trf.transform([self.vmin, self.vmax])

            if not np.isfinite([t_vmin, t_vmax]).all():

                raise ValueError("Invalid vmin or vmax")

            value, is_scalar = self.process_value(value)

            rescaled = value * (t_vmax - t_vmin)

            rescaled += t_vmin

            value = (self._trf

                     .inverted()

                     .transform(rescaled)

                     .reshape(np.shape(value)))

            return value[0] if is_scalar else value



        def autoscale_None(self, A):

                                                                  

            in_trf_domain = np.extract(np.isfinite(self._trf.transform(A)), A)

            if in_trf_domain.size == 0:

                in_trf_domain = np.ma.masked

            return super().autoscale_None(in_trf_domain)



    if base_norm_cls is Normalize:

        ScaleNorm.__name__ = f"{scale_cls.__name__}Norm"

        ScaleNorm.__qualname__ = f"{scale_cls.__qualname__}Norm"

    else:

        ScaleNorm.__name__ = base_norm_cls.__name__

        ScaleNorm.__qualname__ = base_norm_cls.__qualname__

    ScaleNorm.__module__ = base_norm_cls.__module__

    ScaleNorm.__doc__ = base_norm_cls.__doc__



    return ScaleNorm





def _create_empty_object_of_class(cls):

    return cls.__new__(cls)





def _picklable_norm_constructor(*args):

    return _create_empty_object_of_class(_make_norm_from_scale(*args))





@make_norm_from_scale(

    scale.FuncScale,

    init=lambda functions, vmin=None, vmax=None, clip=False: None)

class FuncNorm(Normalize):

    





LogNorm = make_norm_from_scale(

    functools.partial(scale.LogScale, nonpositive="mask"))(Normalize)

LogNorm.__name__ = LogNorm.__qualname__ = "LogNorm"

LogNorm.__doc__ = "Normalize a given value to the 0-1 range on a log scale."





@make_norm_from_scale(

    scale.SymmetricalLogScale,

    init=lambda linthresh, linscale=1., vmin=None, vmax=None, clip=False, *,

                base=10: None)

class SymLogNorm(Normalize):

    



    @property

    def linthresh(self):

        return self._scale.linthresh



    @linthresh.setter

    def linthresh(self, value):

        self._scale.linthresh = value





@make_norm_from_scale(

    scale.AsinhScale,

    init=lambda linear_width=1, vmin=None, vmax=None, clip=False: None)

class AsinhNorm(Normalize):

    



    @property

    def linear_width(self):

        return self._scale.linear_width



    @linear_width.setter

    def linear_width(self, value):

        self._scale.linear_width = value





class PowerNorm(Normalize):

    

    def __init__(self, gamma, vmin=None, vmax=None, clip=False):

        super().__init__(vmin, vmax, clip)

        self.gamma = gamma



    def __call__(self, value, clip=None):

        if clip is None:

            clip = self.clip



        result, is_scalar = self.process_value(value)



        self.autoscale_None(result)

        gamma = self.gamma

        vmin, vmax = self.vmin, self.vmax

        if vmin > vmax:

            raise ValueError("minvalue must be less than or equal to maxvalue")

        elif vmin == vmax:

            result.fill(0)

        else:

            if clip:

                mask = np.ma.getmask(result)

                result = np.ma.array(np.clip(result.filled(vmax), vmin, vmax),

                                     mask=mask)

            resdat = result.data

            resdat -= vmin

            resdat /= (vmax - vmin)

            resdat[resdat > 0] = np.power(resdat[resdat > 0], gamma)



            result = np.ma.array(resdat, mask=result.mask, copy=False)

        if is_scalar:

            result = result[0]

        return result



    def inverse(self, value):

        if not self.scaled():

            raise ValueError("Not invertible until scaled")



        result, is_scalar = self.process_value(value)



        gamma = self.gamma

        vmin, vmax = self.vmin, self.vmax



        resdat = result.data

        resdat[resdat > 0] = np.power(resdat[resdat > 0], 1 / gamma)

        resdat *= (vmax - vmin)

        resdat += vmin



        result = np.ma.array(resdat, mask=result.mask, copy=False)

        if is_scalar:

            result = result[0]

        return result





class BoundaryNorm(Normalize):

    



                                                                            

                                                                             

                                                          



    def __init__(self, boundaries, ncolors, clip=False, *, extend='neither'):

        

        if clip and extend != 'neither':

            raise ValueError("'clip=True' is not compatible with 'extend'")

        super().__init__(vmin=boundaries[0], vmax=boundaries[-1], clip=clip)

        self.boundaries = np.asarray(boundaries)

        self.N = len(self.boundaries)

        if self.N < 2:

            raise ValueError("You must provide at least 2 boundaries "

                             f"(1 region) but you passed in {boundaries!r}")

        self.Ncmap = ncolors

        self.extend = extend



        self._scale = None                                



        self._n_regions = self.N - 1                           

        self._offset = 0

        if extend in ('min', 'both'):

            self._n_regions += 1

            self._offset = 1

        if extend in ('max', 'both'):

            self._n_regions += 1

        if self._n_regions > self.Ncmap:

            raise ValueError(f"There are {self._n_regions} color bins "

                             "including extensions, but ncolors = "

                             f"{ncolors}; ncolors must equal or exceed the "

                             "number of bins")



    def __call__(self, value, clip=None):

        

        if clip is None:

            clip = self.clip



        xx, is_scalar = self.process_value(value)

        mask = np.ma.getmaskarray(xx)

                                                             

        xx = np.atleast_1d(xx.filled(self.vmax + 1))

        if clip:

            np.clip(xx, self.vmin, self.vmax, out=xx)

            max_col = self.Ncmap - 1

        else:

            max_col = self.Ncmap

                                                                 

                                                              

        iret = np.digitize(xx, self.boundaries) - 1 + self._offset

                                                                 

                                                                     

                                                                      

                                                                    

                                                                      

        if self.Ncmap > self._n_regions:

            if self._n_regions == 1:

                                                                       

                iret[iret == 0] = (self.Ncmap - 1) // 2

            else:

                                                                           

                                           

                iret = (self.Ncmap - 1) / (self._n_regions - 1) * iret

                                             

        iret = iret.astype(np.int16)

        iret[xx < self.vmin] = -1

        iret[xx >= self.vmax] = max_col

        ret = np.ma.array(iret, mask=mask)

        if is_scalar:

            ret = int(ret[0])                        

        return ret



    def inverse(self, value):

        

        raise ValueError("BoundaryNorm is not invertible")





class NoNorm(Normalize):

    

    def __call__(self, value, clip=None):

        if np.iterable(value):

            return np.ma.array(value)

        return value



    def inverse(self, value):

        if np.iterable(value):

            return np.ma.array(value)

        return value





class MultiNorm(Norm):

    



    def __init__(self, norms, vmin=None, vmax=None, clip=None):

        

        if cbook.is_scalar_or_string(norms):

            raise ValueError(

                    "MultiNorm must be assigned an iterable of norms, where each "

                    f"norm is of type `str`, or `Normalize`, not {type(norms)}")



        if len(norms) < 1:

            raise ValueError("MultiNorm must be assigned at least one norm")



        def resolve(norm):

            if isinstance(norm, str):

                scale_cls = _api.check_getitem(scale._scale_mapping, norm=norm)

                return mpl.colorizer._auto_norm_from_scale(scale_cls)()

            elif isinstance(norm, Normalize):

                return norm

            else:

                raise ValueError(

                    "Each norm assigned to MultiNorm must be "

                    f"of type `str`, or `Normalize`, not {type(norm)}")



        self._norms = tuple(resolve(norm) for norm in norms)



        self.callbacks = cbook.CallbackRegistry(signals=["changed"])



        self.vmin = vmin

        self.vmax = vmax

        self.clip = clip



        for n in self._norms:

            n.callbacks.connect('changed', self._changed)



    @property

    def n_components(self):

        

        return len(self._norms)



    @property

    def norms(self):

        

        return self._norms



    @property

    def vmin(self):

        

        return tuple(n.vmin for n in self._norms)



    @vmin.setter

    def vmin(self, values):

        if values is None:

            return

        if not np.iterable(values) or len(values) != self.n_components:

            raise ValueError("*vmin* must have one component for each norm. "

                             f"Expected an iterable of length {self.n_components}, "

                             f"but got {values!r}")

        with self.callbacks.blocked():

            for norm, v in zip(self.norms, values):

                norm.vmin = v

        self._changed()



    @property

    def vmax(self):

        

        return tuple(n.vmax for n in self._norms)



    @vmax.setter

    def vmax(self, values):

        if values is None:

            return

        if not np.iterable(values) or len(values) != self.n_components:

            raise ValueError("*vmax* must have one component for each norm. "

                             f"Expected an iterable of length {self.n_components}, "

                             f"but got {values!r}")

        with self.callbacks.blocked():

            for norm, v in zip(self.norms, values):

                norm.vmax = v

        self._changed()



    @property

    def clip(self):

        

        return tuple(n.clip for n in self._norms)



    @clip.setter

    def clip(self, values):

        if values is None:

            return

        if not np.iterable(values) or len(values) != self.n_components:

            raise ValueError("*clip* must have one component for each norm. "

                             f"Expected an iterable of length {self.n_components}, "

                             f"but got {values!r}")

        with self.callbacks.blocked():

            for norm, v in zip(self.norms, values):

                norm.clip = v

        self._changed()



    def _changed(self):

        

        self.callbacks.process('changed')



    def __call__(self, values, clip=None):

        

        if clip is None:

            clip = self.clip

        if not np.iterable(clip) or len(clip) != self.n_components:

            raise ValueError("*clip* must have one component for each norm. "

                             f"Expected an iterable of length {self.n_components}, "

                             f"but got {clip!r}")



        values = self._iterable_components_in_data(values, self.n_components)

        result = tuple(n(v, clip=c) for n, v, c in zip(self.norms, values, clip))

        return result



    def inverse(self, values):

        

        values = self._iterable_components_in_data(values, self.n_components)

        result = tuple(n.inverse(v) for n, v in zip(self.norms, values))

        return result



    def autoscale(self, A):

        

        with self.callbacks.blocked():

            A = self._iterable_components_in_data(A, self.n_components)

            for n, a in zip(self.norms, A):

                n.autoscale(a)

        self._changed()



    def autoscale_None(self, A):

        

        with self.callbacks.blocked():

            A = self._iterable_components_in_data(A, self.n_components)

            for n, a in zip(self.norms, A):

                n.autoscale_None(a)

        self._changed()



    def scaled(self):

        

        return all(n.scaled() for n in self.norms)



    @staticmethod

    def _iterable_components_in_data(data, n_components):

        

        if isinstance(data, np.ndarray) and data.dtype.fields is not None:

                              

            if len(data.dtype.fields) != n_components:

                raise ValueError(

                    "Structured array inputs to MultiNorm must have the same "

                    "number of fields as components in the MultiNorm. Expected "

                    f"{n_components}, but got {len(data.dtype.fields)} fields"

                    )

            else:

                return tuple(data[field] for field in data.dtype.names)

        try:

            n_elements = len(data)

        except TypeError:

            raise ValueError("MultiNorm expects a sequence with one element per "

                             f"component as input, but got {data!r} instead")

        if n_elements != n_components:

            if isinstance(data, np.ndarray) and data.shape[-1] == n_components:

                if len(data.shape) == 2:

                    raise ValueError(

                        f"MultiNorm expects a sequence with one element per component. "

                        "You can use `data_transposed = data.T` "

                        "to convert the input data of shape "

                        f"{data.shape} to a compatible shape {data.shape[::-1]}")

                else:

                    raise ValueError(

                        f"MultiNorm expects a sequence with one element per component. "

                        "You can use `data_as_list = [data[..., i] for i in "

                        "range(data.shape[-1])]` to convert the input data of shape "

                        f" {data.shape} to a compatible list")



            raise ValueError(

                "MultiNorm expects a sequence with one element per component. "

                f"This MultiNorm has {n_components} components, but got a sequence "

                f"with {n_elements} elements"

                )



        return tuple(data[i] for i in range(n_elements))





def rgb_to_hsv(arr):

    

    arr = np.asarray(arr)



                                                                      

    if arr.shape[-1] != 3:

        raise ValueError("Last dimension of input array must be 3; "

                         f"shape {arr.shape} was found.")



    in_shape = arr.shape

    arr = np.array(

        arr, copy=False,

        dtype=np.promote_types(arr.dtype, np.float32),                       

        ndmin=2,                         

    )



    out = np.zeros_like(arr)

    arr_max = arr.max(-1)

                                             

    if np.any(arr_max > 1):

        raise ValueError(

            "Input array must be in the range [0, 1]. "

            f"Found a maximum value of {arr_max.max()}"

        )



    if arr.min() < 0:

        raise ValueError(

            "Input array must be in the range [0, 1]. "

            f"Found a minimum value of {arr.min()}"

        )



    ipos = arr_max > 0

    delta = np.ptp(arr, -1)

    s = np.zeros_like(delta)

    s[ipos] = delta[ipos] / arr_max[ipos]

    ipos = delta > 0

                

    idx = (arr[..., 0] == arr_max) & ipos

    out[idx, 0] = (arr[idx, 1] - arr[idx, 2]) / delta[idx]

                  

    idx = (arr[..., 1] == arr_max) & ipos

    out[idx, 0] = 2. + (arr[idx, 2] - arr[idx, 0]) / delta[idx]

                 

    idx = (arr[..., 2] == arr_max) & ipos

    out[idx, 0] = 4. + (arr[idx, 0] - arr[idx, 1]) / delta[idx]



    out[..., 0] = (out[..., 0] / 6.0) % 1.0

    out[..., 1] = s

    out[..., 2] = arr_max



    return out.reshape(in_shape)





def hsv_to_rgb(hsv):

    

    hsv = np.asarray(hsv)



                                                                      

    if hsv.shape[-1] != 3:

        raise ValueError("Last dimension of input array must be 3; "

                         f"shape {hsv.shape} was found.")



    in_shape = hsv.shape

    hsv = np.array(

        hsv, copy=False,

        dtype=np.promote_types(hsv.dtype, np.float32),                       

        ndmin=2,                         

    )



    h = hsv[..., 0]

    s = hsv[..., 1]

    v = hsv[..., 2]



    r = np.empty_like(h)

    g = np.empty_like(h)

    b = np.empty_like(h)



    i = (h * 6.0).astype(int)

    f = (h * 6.0) - i

    p = v * (1.0 - s)

    q = v * (1.0 - s * f)

    t = v * (1.0 - s * (1.0 - f))



    idx = i % 6 == 0

    r[idx] = v[idx]

    g[idx] = t[idx]

    b[idx] = p[idx]



    idx = i == 1

    r[idx] = q[idx]

    g[idx] = v[idx]

    b[idx] = p[idx]



    idx = i == 2

    r[idx] = p[idx]

    g[idx] = v[idx]

    b[idx] = t[idx]



    idx = i == 3

    r[idx] = p[idx]

    g[idx] = q[idx]

    b[idx] = v[idx]



    idx = i == 4

    r[idx] = t[idx]

    g[idx] = p[idx]

    b[idx] = v[idx]



    idx = i == 5

    r[idx] = v[idx]

    g[idx] = p[idx]

    b[idx] = q[idx]



    idx = s == 0

    r[idx] = v[idx]

    g[idx] = v[idx]

    b[idx] = v[idx]



    rgb = np.stack([r, g, b], axis=-1)



    return rgb.reshape(in_shape)





def _vector_magnitude(arr):

                                  

                                                 

                                                                        

    sum_sq = 0

    for i in range(arr.shape[-1]):

        sum_sq += arr[..., i, np.newaxis] ** 2

    return np.sqrt(sum_sq)





class LightSource:

    



    def __init__(self, azdeg=315, altdeg=45, hsv_min_val=0, hsv_max_val=1,

                 hsv_min_sat=1, hsv_max_sat=0):

        

        self.azdeg = azdeg

        self.altdeg = altdeg

        self.hsv_min_val = hsv_min_val

        self.hsv_max_val = hsv_max_val

        self.hsv_min_sat = hsv_min_sat

        self.hsv_max_sat = hsv_max_sat



    @property

    def direction(self):

        

                                                                        

                                                             

        az = np.radians(90 - self.azdeg)

        alt = np.radians(self.altdeg)

        return np.array([

            np.cos(az) * np.cos(alt),

            np.sin(az) * np.cos(alt),

            np.sin(alt)

        ])



    def hillshade(self, elevation, vert_exag=1, dx=1, dy=1, fraction=1.):

        



                                                                               

                                                                        

                                                       

        dy = -dy



                                                                 

        e_dy, e_dx = np.gradient(vert_exag * elevation, dy, dx)



                                     

        normal = np.empty(elevation.shape + (3,)).view(type(elevation))

        normal[..., 0] = -e_dx

        normal[..., 1] = -e_dy

        normal[..., 2] = 1

        normal /= _vector_magnitude(normal)



        return self.shade_normals(normal, fraction)



    def shade_normals(self, normals, fraction=1.):

        



        intensity = normals.dot(self.direction)



                                

        imin, imax = intensity.min(), intensity.max()

        intensity *= fraction



                                                               

                                                                            

                                 

        if (imax - imin) > 1e-6:

                                                                             

                                                                             

                                                                               

                                                         

            intensity -= imin

            intensity /= (imax - imin)

        intensity = np.clip(intensity, 0, 1)



        return intensity



    def shade(self, data, cmap, norm=None, blend_mode='overlay', vmin=None,

              vmax=None, vert_exag=1, dx=1, dy=1, fraction=1, **kwargs):

        

        if vmin is None:

            vmin = data.min()

        if vmax is None:

            vmax = data.max()

        if norm is None:

            norm = Normalize(vmin=vmin, vmax=vmax)



        rgb0 = cmap(norm(data))

        rgb1 = self.shade_rgb(rgb0, elevation=data, blend_mode=blend_mode,

                              vert_exag=vert_exag, dx=dx, dy=dy,

                              fraction=fraction, **kwargs)

                                                        

        rgb0[..., :3] = rgb1[..., :3]

        return rgb0



    def shade_rgb(self, rgb, elevation, fraction=1., blend_mode='hsv',

                  vert_exag=1, dx=1, dy=1, **kwargs):

        

                                              

        intensity = self.hillshade(elevation, vert_exag, dx, dy, fraction)

        intensity = intensity[..., np.newaxis]



                                                                   

        lookup = {

                'hsv': self.blend_hsv,

                'soft': self.blend_soft_light,

                'overlay': self.blend_overlay,

                }

        if blend_mode in lookup:

            blend = lookup[blend_mode](rgb, intensity, **kwargs)

        else:

            try:

                blend = blend_mode(rgb, intensity, **kwargs)

            except TypeError as err:

                raise ValueError('"blend_mode" must be callable or one of '

                                 f'{lookup.keys}') from err



                                                                  

        if np.ma.is_masked(intensity):

            mask = intensity.mask[..., 0]

            for i in range(3):

                blend[..., i][mask] = rgb[..., i][mask]



        return blend



    def blend_hsv(self, rgb, intensity, hsv_max_sat=None, hsv_max_val=None,

                  hsv_min_val=None, hsv_min_sat=None):

        

                                   

        if hsv_max_sat is None:

            hsv_max_sat = self.hsv_max_sat

        if hsv_max_val is None:

            hsv_max_val = self.hsv_max_val

        if hsv_min_sat is None:

            hsv_min_sat = self.hsv_min_sat

        if hsv_min_val is None:

            hsv_min_val = self.hsv_min_val



                                                                

        intensity = intensity[..., 0]

        intensity = 2 * intensity - 1



                                         

        hsv = rgb_to_hsv(rgb[:, :, 0:3])

        hue, sat, val = np.moveaxis(hsv, -1, 0)



                                                                

                                                   

        np.putmask(sat, (np.abs(sat) > 1.e-10) & (intensity > 0),

                   (1 - intensity) * sat + intensity * hsv_max_sat)

        np.putmask(sat, (np.abs(sat) > 1.e-10) & (intensity < 0),

                   (1 + intensity) * sat - intensity * hsv_min_sat)

        np.putmask(val, intensity > 0,

                   (1 - intensity) * val + intensity * hsv_max_val)

        np.putmask(val, intensity < 0,

                   (1 + intensity) * val - intensity * hsv_min_val)

        np.clip(hsv[:, :, 1:], 0, 1, out=hsv[:, :, 1:])



                                           

        return hsv_to_rgb(hsv)



    def blend_soft_light(self, rgb, intensity):

        

        return 2 * intensity * rgb + (1 - 2 * intensity) * rgb**2



    def blend_overlay(self, rgb, intensity):

        

        low = 2 * intensity * rgb

        high = 1 - 2 * (1 - intensity) * (1 - rgb)

        return np.where(rgb <= 0.5, low, high)





def from_levels_and_colors(levels, colors, extend='neither'):

    

    slice_map = {

        'both': slice(1, -1),

        'min': slice(1, None),

        'max': slice(0, -1),

        'neither': slice(0, None),

    }

    _api.check_in_list(slice_map, extend=extend)

    color_slice = slice_map[extend]



    n_data_colors = len(levels) - 1

    n_extend_colors = color_slice.start - (color_slice.stop or 0)             

    n_expected = n_data_colors + n_extend_colors

    if len(colors) != n_expected:

        raise ValueError(

            f'Expected {n_expected} colors ({n_data_colors} colors for {len(levels)} '

            f'levels, and {n_extend_colors} colors for extend == {extend!r}), '

            f'but got {len(colors)}')



    data_colors = colors[color_slice]

    under_color = colors[0] if extend in ['min', 'both'] else 'none'

    over_color = colors[-1] if extend in ['max', 'both'] else 'none'

    cmap = ListedColormap(data_colors, under=under_color, over=over_color)



    cmap.colorbar_extend = extend



    norm = BoundaryNorm(levels, ncolors=n_data_colors)

    return cmap, norm

