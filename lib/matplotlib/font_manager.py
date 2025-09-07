



              

 

                   

                              

                                

                             

                                                          

                                           

                                                    



from __future__ import annotations



from base64 import b64encode

import copy

import dataclasses

from functools import cache, lru_cache

import functools

from io import BytesIO

import json

import logging

from numbers import Integral

import os

from pathlib import Path

import plistlib

import re

import subprocess

import sys

import threading



import matplotlib as mpl

from matplotlib import _api, _afm, cbook, ft2font

from matplotlib._fontconfig_pattern import (

    parse_fontconfig_pattern, generate_fontconfig_pattern)

from matplotlib.rcsetup import _validators



_log = logging.getLogger(__name__)



font_scalings = {

    'xx-small': 0.579,

    'x-small':  0.694,

    'small':    0.833,

    'medium':   1.0,

    'large':    1.200,

    'x-large':  1.440,

    'xx-large': 1.728,

    'larger':   1.2,

    'smaller':  0.833,

    None:       1.0,

}

stretch_dict = {

    'ultra-condensed': 100,

    'extra-condensed': 200,

    'condensed':       300,

    'semi-condensed':  400,

    'normal':          500,

    'semi-expanded':   600,

    'semi-extended':   600,

    'expanded':        700,

    'extended':        700,

    'extra-expanded':  800,

    'extra-extended':  800,

    'ultra-expanded':  900,

    'ultra-extended':  900,

}

weight_dict = {

    'ultralight': 100,

    'light':      200,

    'normal':     400,

    'regular':    400,

    'book':       400,

    'medium':     500,

    'roman':      500,

    'semibold':   600,

    'demibold':   600,

    'demi':       600,

    'bold':       700,

    'heavy':      800,

    'extra bold': 800,

    'black':      900,

}

_weight_regexes = [

                                                                    

                  

    ("thin", 100),

    ("extralight", 200),

    ("ultralight", 200),

    ("demilight", 350),

    ("semilight", 350),

    ("light", 300),                                         

    ("book", 380),

    ("regular", 400),

    ("normal", 400),

    ("medium", 500),

    ("demibold", 600),

    ("demi", 600),

    ("semibold", 600),

    ("extrabold", 800),

    ("superbold", 800),

    ("ultrabold", 800),

    ("bold", 700),                                                

    ("ultrablack", 1000),

    ("superblack", 1000),

    ("extrablack", 1000),

    (r"\bultra", 1000),

    ("black", 900),                                                 

    ("heavy", 900),

]

font_family_aliases = {

    'serif',

    'sans-serif',

    'sans serif',

    'cursive',

    'fantasy',

    'monospace',

    'sans',

}



               

try:

    _HOME = Path.home()

except Exception:                                                    

    _HOME = Path(os.devnull)                                            

MSFolders =
    r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'

MSFontDirectories = [

    r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts',

    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Fonts']

MSUserFontDirectories = [

    str(_HOME / 'AppData/Local/Microsoft/Windows/Fonts'),

    str(_HOME / 'AppData/Roaming/Microsoft/Windows/Fonts'),

]

X11FontDirectories = [

                                        

    "/usr/X11R6/lib/X11/fonts/TTF/",

    "/usr/X11/lib/X11/fonts",

                                                 

    "/usr/share/fonts/",

                                                     

    "/usr/local/share/fonts/",

                                           

    "/usr/lib/openoffice/share/fonts/truetype/",

                

    str((Path(os.environ.get('XDG_DATA_HOME') or _HOME / ".local/share"))

        / "fonts"),

    str(_HOME / ".fonts"),

]

OSXFontDirectories = [

    "/Library/Fonts/",

    "/Network/Library/Fonts/",

    "/System/Library/Fonts/",

                                  

    "/opt/local/share/fonts",

                

    str(_HOME / "Library/Fonts"),

]





def _normalize_weight(weight):

    return weight if isinstance(weight, Integral) else weight_dict[weight]





def get_fontext_synonyms(fontext):

    

    return {

        'afm': ['afm'],

        'otf': ['otf', 'ttc', 'ttf'],

        'ttc': ['otf', 'ttc', 'ttf'],

        'ttf': ['otf', 'ttc', 'ttf'],

    }[fontext]





def list_fonts(directory, extensions):

    

    extensions = ["." + ext for ext in extensions]

    return [os.path.join(dirpath, filename)

                                                              

            for dirpath, _, filenames in os.walk(directory)

            for filename in filenames

            if Path(filename).suffix.lower() in extensions]





def win32FontDirectory():

                  

    import winreg

    try:

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, MSFolders) as user:

            return winreg.QueryValueEx(user, 'Fonts')[0]

    except OSError:

        return os.path.join(os.environ['WINDIR'], 'Fonts')





def _get_win32_installed_fonts():

    

    import winreg

    items = set()

                                                      

    for domain, base_dirs in [

            (winreg.HKEY_LOCAL_MACHINE, [win32FontDirectory()]),           

            (winreg.HKEY_CURRENT_USER, MSUserFontDirectories),         

    ]:

        for base_dir in base_dirs:

            for reg_path in MSFontDirectories:

                try:

                    with winreg.OpenKey(domain, reg_path) as local:

                        for j in range(winreg.QueryInfoKey(local)[1]):

                                                                               

                                            

                            key, value, tp = winreg.EnumValue(local, j)

                            if not isinstance(value, str):

                                continue

                            try:

                                                                             

                                                                 

                                path = Path(base_dir, value).resolve()

                            except RuntimeError:

                                                                  

                                continue

                            items.add(path)

                except (OSError, MemoryError):

                    continue

    return items





@cache

def _get_fontconfig_fonts():

    

    try:

        if b'--format' not in subprocess.check_output(['fc-list', '--help']):

            _log.warning(                                        

                'Matplotlib needs fontconfig>=2.7 to query system fonts.')

            return []

        out = subprocess.check_output(['fc-list', '--format=%{file}\\n'])

    except (OSError, subprocess.CalledProcessError):

        return []

    return [Path(os.fsdecode(fname)) for fname in out.split(b'\n')]





@cache

def _get_macos_fonts():

    

    try:

        d, = plistlib.loads(

            subprocess.check_output(["system_profiler", "-xml", "SPFontsDataType"]))

    except (OSError, subprocess.CalledProcessError, plistlib.InvalidFileException):

        return []

    return [Path(entry["path"]) for entry in d["_items"]]





def findSystemFonts(fontpaths=None, fontext='ttf'):

    

    fontfiles = set()

    fontexts = get_fontext_synonyms(fontext)



    if fontpaths is None:

        if sys.platform == 'win32':

            installed_fonts = _get_win32_installed_fonts()

            fontpaths = []

        else:

            installed_fonts = _get_fontconfig_fonts()

            if sys.platform == 'darwin':

                installed_fonts += _get_macos_fonts()

                fontpaths = [*X11FontDirectories, *OSXFontDirectories]

            else:

                fontpaths = X11FontDirectories

        fontfiles.update(str(path) for path in installed_fonts

                         if path.suffix.lower()[1:] in fontexts)



    elif isinstance(fontpaths, str):

        fontpaths = [fontpaths]



    for path in fontpaths:

        fontfiles.update(map(os.path.abspath, list_fonts(path, fontexts)))



    return [fname for fname in fontfiles if os.path.exists(fname)]





@dataclasses.dataclass(frozen=True)

class FontEntry:

    



    fname: str = ''

    name: str = ''

    style: str = 'normal'

    variant: str = 'normal'

    weight: str | int = 'normal'

    stretch: str = 'normal'

    size: str = 'medium'



    def _repr_html_(self) -> str:

        png_stream = self._repr_png_()

        png_b64 = b64encode(png_stream).decode()

        return f"<img src=\"data:image/png;base64, {png_b64}\" />"



    def _repr_png_(self) -> bytes:

        from matplotlib.figure import Figure                    

        fig = Figure()

        font_path = Path(self.fname) if self.fname != '' else None

        fig.text(0, 0, self.name, font=font_path)

        with BytesIO() as buf:

            fig.savefig(buf, bbox_inches='tight', transparent=True)

            return buf.getvalue()





def ttfFontProperty(font):

    

    name = font.family_name



                                                        



    sfnt = font.get_sfnt()

    mac_key = (1,                       

               0,             

               0)                   

    ms_key = (3,                       

              1,                  

              0x0409)                                 



                                                                               

                                                                              

                                                                             

                                                                       

    sfnt2 = (sfnt.get((*mac_key, 2), b'').decode('latin-1').lower() or

             sfnt.get((*ms_key, 2), b'').decode('utf_16_be').lower())

    sfnt4 = (sfnt.get((*mac_key, 4), b'').decode('latin-1').lower() or

             sfnt.get((*ms_key, 4), b'').decode('utf_16_be').lower())



    if sfnt4.find('oblique') >= 0:

        style = 'oblique'

    elif sfnt4.find('italic') >= 0:

        style = 'italic'

    elif sfnt2.find('regular') >= 0:

        style = 'normal'

    elif ft2font.StyleFlags.ITALIC in font.style_flags:

        style = 'italic'

    else:

        style = 'normal'



                                                    



                     

    if name.lower() in ['capitals', 'small-caps']:

        variant = 'small-caps'

    else:

        variant = 'normal'



                                                                          

                                                          

    wws_subfamily = 22

    typographic_subfamily = 16

    font_subfamily = 2

    styles = [

        sfnt.get((*mac_key, wws_subfamily), b'').decode('latin-1'),

        sfnt.get((*mac_key, typographic_subfamily), b'').decode('latin-1'),

        sfnt.get((*mac_key, font_subfamily), b'').decode('latin-1'),

        sfnt.get((*ms_key, wws_subfamily), b'').decode('utf-16-be'),

        sfnt.get((*ms_key, typographic_subfamily), b'').decode('utf-16-be'),

        sfnt.get((*ms_key, font_subfamily), b'').decode('utf-16-be'),

    ]

    styles = [*filter(None, styles)] or [font.style_name]



    def get_weight():                                                  

                            

        os2 = font.get_sfnt_table("OS/2")

        if os2 and os2["version"] != 0xffff:

            return os2["usWeightClass"]

                                      

        try:

            ps_font_info_weight = (

                font.get_ps_font_info()["weight"].replace(" ", "") or "")

        except ValueError:

            pass

        else:

            for regex, weight in _weight_regexes:

                if re.fullmatch(regex, ps_font_info_weight, re.I):

                    return weight

                            

        for style in styles:

            style = style.replace(" ", "")

            for regex, weight in _weight_regexes:

                if re.search(regex, style, re.I):

                    return weight

        if ft2font.StyleFlags.BOLD in font.style_flags:

            return 700          

        return 500                            



    weight = int(get_weight())



                                           

                                                                           

                                                                         

                            

                                              

                              



    if any(word in sfnt4 for word in ['narrow', 'condensed', 'cond']):

        stretch = 'condensed'

    elif 'demi cond' in sfnt4:

        stretch = 'semi-condensed'

    elif any(word in sfnt4 for word in ['wide', 'expanded', 'extended']):

        stretch = 'expanded'

    else:

        stretch = 'normal'



                                          

                                                                            

                      

                                          

                                                        

                                                                  



    if not font.scalable:

        raise NotImplementedError("Non-scalable fonts are not supported")

    size = 'scalable'



    return FontEntry(font.fname, name, style, variant, weight, stretch, size)





def afmFontProperty(fontpath, font):

    



    name = font.get_familyname()

    fontname = font.get_fontname().lower()



                                                        



    if font.get_angle() != 0 or 'italic' in name.lower():

        style = 'italic'

    elif 'oblique' in name.lower():

        style = 'oblique'

    else:

        style = 'normal'



                                                    



                    

    if name.lower() in ['capitals', 'small-caps']:

        variant = 'small-caps'

    else:

        variant = 'normal'



    weight = font.get_weight().lower()

    if weight not in weight_dict:

        weight = 'normal'



                                           

                                                                           

                                                                         

                            

                                              

                              

    if 'demi cond' in fontname:

        stretch = 'semi-condensed'

    elif any(word in fontname for word in ['narrow', 'cond']):

        stretch = 'condensed'

    elif any(word in fontname for word in ['wide', 'expanded', 'extended']):

        stretch = 'expanded'

    else:

        stretch = 'normal'



                                          

                                                                            

                      

                                          

                                                        

                                                                  



                                             



    size = 'scalable'



    return FontEntry(fontpath, name, style, variant, weight, stretch, size)





def _cleanup_fontproperties_init(init_method):

    

    @functools.wraps(init_method)

    def wrapper(self, *args, **kwargs):

                                                          

        if len(args) > 1 or len(args) == 1 and kwargs:

                                                                                

                                                                            

            _api.warn_deprecated(

                "3.10",

                message="Passing individual properties to FontProperties() "

                        "positionally was deprecated in Matplotlib %(since)s and "

                        "will be removed in %(removal)s. Please pass all properties "

                        "via keyword arguments."

            )

                                                                 

        if len(args) == 1 and not kwargs and not cbook.is_scalar_or_string(args[0]):

                                                             

            _api.warn_deprecated(

                "3.10",

                message="Passing family as positional argument to FontProperties() "

                        "was deprecated in Matplotlib %(since)s and will be removed "

                        "in %(removal)s. Please pass family names as keyword"

                        "argument."

            )

                                    

                                                                                  

                                                                                   

                                

        return init_method(self, *args, **kwargs)



    return wrapper





class FontProperties:

    



    @_cleanup_fontproperties_init

    def __init__(self, family=None, style=None, variant=None, weight=None,

                 stretch=None, size=None,

                 fname=None,                                            

                 math_fontfamily=None):

        self.set_family(family)

        self.set_style(style)

        self.set_variant(variant)

        self.set_weight(weight)

        self.set_stretch(stretch)

        self.set_file(fname)

        self.set_size(size)

        self.set_math_fontfamily(math_fontfamily)

                                                                          

                                                                           

                                                                           

        if (isinstance(family, str)

                and style is None and variant is None and weight is None

                and stretch is None and size is None and fname is None):

            self.set_fontconfig_pattern(family)



    @classmethod

    def _from_any(cls, arg):

        

        if arg is None:

            return cls()

        elif isinstance(arg, cls):

            return arg

        elif isinstance(arg, os.PathLike):

            return cls(fname=arg)

        elif isinstance(arg, str):

            return cls(arg)

        else:

            return cls(**arg)



    def __hash__(self):

        l = (tuple(self.get_family()),

             self.get_slant(),

             self.get_variant(),

             self.get_weight(),

             self.get_stretch(),

             self.get_size(),

             self.get_file(),

             self.get_math_fontfamily())

        return hash(l)



    def __eq__(self, other):

        return hash(self) == hash(other)



    def __str__(self):

        return self.get_fontconfig_pattern()



    def get_family(self):

        

        return self._family



    def get_name(self):

        

        return get_font(findfont(self)).family_name



    def get_style(self):

        

        return self._slant



    def get_variant(self):

        

        return self._variant



    def get_weight(self):

        

        return self._weight



    def get_stretch(self):

        

        return self._stretch



    def get_size(self):

        

        return self._size



    def get_file(self):

        

        return self._file



    def get_fontconfig_pattern(self):

        

        return generate_fontconfig_pattern(self)



    def set_family(self, family):

        

        family = mpl._val_or_rc(family, 'font.family')

        if isinstance(family, str):

            family = [family]

        self._family = family



    def set_style(self, style):

        

        style = mpl._val_or_rc(style, 'font.style')

        _api.check_in_list(['normal', 'italic', 'oblique'], style=style)

        self._slant = style



    def set_variant(self, variant):

        

        variant = mpl._val_or_rc(variant, 'font.variant')

        _api.check_in_list(['normal', 'small-caps'], variant=variant)

        self._variant = variant



    def set_weight(self, weight):

        

        weight = mpl._val_or_rc(weight, 'font.weight')

        if weight in weight_dict:

            self._weight = weight

            return

        try:

            weight = int(weight)

        except ValueError:

            pass

        else:

            if 0 <= weight <= 1000:

                self._weight = weight

                return

        raise ValueError(f"{weight=} is invalid")



    def set_stretch(self, stretch):

        

        stretch = mpl._val_or_rc(stretch, 'font.stretch')

        if stretch in stretch_dict:

            self._stretch = stretch

            return

        try:

            stretch = int(stretch)

        except ValueError:

            pass

        else:

            if 0 <= stretch <= 1000:

                self._stretch = stretch

                return

        raise ValueError(f"{stretch=} is invalid")



    def set_size(self, size):

        

        size = mpl._val_or_rc(size, 'font.size')

        try:

            size = float(size)

        except ValueError:

            try:

                scale = font_scalings[size]

            except KeyError as err:

                raise ValueError(

                    "Size is invalid. Valid font size are "

                    + ", ".join(map(str, font_scalings))) from err

            else:

                size = scale * FontManager.get_default_size()

        if size < 1.0:

            _log.info('Fontsize %1.2f < 1.0 pt not allowed by FreeType. '

                      'Setting fontsize = 1 pt', size)

            size = 1.0

        self._size = size



    def set_file(self, file):

        

        self._file = os.fspath(file) if file is not None else None



    def set_fontconfig_pattern(self, pattern):

        

        for key, val in parse_fontconfig_pattern(pattern).items():

            if type(val) is list:

                getattr(self, "set_" + key)(val[0])

            else:

                getattr(self, "set_" + key)(val)



    def get_math_fontfamily(self):

        

        return self._math_fontfamily



    def set_math_fontfamily(self, fontfamily):

        

        if fontfamily is None:

            fontfamily = mpl.rcParams['mathtext.fontset']

        else:

            valid_fonts = _validators['mathtext.fontset'].valid.values()

                                                                         

                                                               

            _api.check_in_list(valid_fonts, math_fontfamily=fontfamily)

        self._math_fontfamily = fontfamily



    def copy(self):

        

        return copy.copy(self)



             

    set_name = set_family

    get_slant = get_style

    set_slant = set_style

    get_size_in_points = get_size





class _JSONEncoder(json.JSONEncoder):

    def default(self, o):

        if isinstance(o, FontManager):

            return dict(o.__dict__, __class__='FontManager')

        elif isinstance(o, FontEntry):

            d = dict(o.__dict__, __class__='FontEntry')

            try:

                                                                              

                                                                             

                d["fname"] = str(Path(d["fname"]).relative_to(mpl.get_data_path()))

            except ValueError:

                pass

            return d

        else:

            return super().default(o)





def _json_decode(o):

    cls = o.pop('__class__', None)

    if cls is None:

        return o

    elif cls == 'FontManager':

        r = FontManager.__new__(FontManager)

        r.__dict__.update(o)

        return r

    elif cls == 'FontEntry':

        if not os.path.isabs(o['fname']):

            o['fname'] = os.path.join(mpl.get_data_path(), o['fname'])

        r = FontEntry(**o)

        return r

    else:

        raise ValueError("Don't know how to deserialize __class__=%s" % cls)





def json_dump(data, filename):

    

    try:

        with cbook._lock_path(filename), open(filename, 'w') as fh:

            json.dump(data, fh, cls=_JSONEncoder, indent=2)

    except OSError as e:

        _log.warning('Could not save font_manager cache %s', e)





def json_load(filename):

    

    with open(filename) as fh:

        return json.load(fh, object_hook=_json_decode)





class FontManager:

    

                                                                

                                                                  

                                

    __version__ = '3.11.0a1'



    def __init__(self, size=None, weight='normal'):

        self._version = self.__version__



        self.__default_weight = weight

        self.default_size = size



                                    

        paths = [cbook._get_data_path('fonts', subdir)

                 for subdir in ['ttf', 'afm', 'pdfcorefonts']]

        _log.debug('font search path %s', paths)



        self.defaultFamily = {

            'ttf': 'DejaVu Sans',

            'afm': 'Helvetica'}



        self.afmlist = []

        self.ttflist = []



                                  

        timer = threading.Timer(5, lambda: _log.warning(

            'Matplotlib is building the font cache; this may take a moment.'))

        timer.start()

        try:

            for fontext in ["afm", "ttf"]:

                for path in [*findSystemFonts(paths, fontext=fontext),

                             *findSystemFonts(fontext=fontext)]:

                    try:

                        self.addfont(path)

                    except OSError as exc:

                        _log.info("Failed to open font file %s: %s", path, exc)

                    except Exception as exc:

                        _log.info("Failed to extract font properties from %s: "

                                  "%s", path, exc)

        finally:

            timer.cancel()



    def addfont(self, path):

        

                                                

                                                 

        path = os.fsdecode(path)

        if Path(path).suffix.lower() == ".afm":

            with open(path, "rb") as fh:

                font = _afm.AFM(fh)

            prop = afmFontProperty(path, font)

            self.afmlist.append(prop)

        else:

            font = ft2font.FT2Font(path)

            prop = ttfFontProperty(font)

            self.ttflist.append(prop)

        self._findfont_cached.cache_clear()



    @property

    def defaultFont(self):

                                                                               

                                                  

        return {ext: self.findfont(family, fontext=ext)

                for ext, family in self.defaultFamily.items()}



    def get_default_weight(self):

        

        return self.__default_weight



    @staticmethod

    def get_default_size():

        

        return mpl.rcParams['font.size']



    def set_default_weight(self, weight):

        

        self.__default_weight = weight



    @staticmethod

    def _expand_aliases(family):

        if family in ('sans', 'sans serif'):

            family = 'sans-serif'

        return mpl.rcParams['font.' + family]



                                                                       

                                                  

    def score_family(self, families, family2):

        

        if not isinstance(families, (list, tuple)):

            families = [families]

        elif len(families) == 0:

            return 1.0

        family2 = family2.lower()

        step = 1 / len(families)

        for i, family1 in enumerate(families):

            family1 = family1.lower()

            if family1 in font_family_aliases:

                options = [*map(str.lower, self._expand_aliases(family1))]

                if family2 in options:

                    idx = options.index(family2)

                    return (i + (idx / len(options))) * step

            elif family1 == family2:

                                                              

                                          

                return i * step

        return 1.0



    def score_style(self, style1, style2):

        

        if style1 == style2:

            return 0.0

        elif (style1 in ('italic', 'oblique')

              and style2 in ('italic', 'oblique')):

            return 0.1

        return 1.0



    def score_variant(self, variant1, variant2):

        

        if variant1 == variant2:

            return 0.0

        else:

            return 1.0



    def score_stretch(self, stretch1, stretch2):

        

        try:

            stretchval1 = int(stretch1)

        except ValueError:

            stretchval1 = stretch_dict.get(stretch1, 500)

        try:

            stretchval2 = int(stretch2)

        except ValueError:

            stretchval2 = stretch_dict.get(stretch2, 500)

        return abs(stretchval1 - stretchval2) / 1000.0



    def score_weight(self, weight1, weight2):

        

                                                                               

        if cbook._str_equal(weight1, weight2):

            return 0.0

        w1 = _normalize_weight(weight1)

        w2 = _normalize_weight(weight2)

        return 0.95 * (abs(w1 - w2) / 1000) + 0.05



    def score_size(self, size1, size2):

        

        if size2 == 'scalable':

            return 0.0

                                             

        try:

            sizeval1 = float(size1)

        except ValueError:

            sizeval1 = self.default_size * font_scalings[size1]

        try:

            sizeval2 = float(size2)

        except ValueError:

            return 1.0

        return abs(sizeval1 - sizeval2) / 72



    def findfont(self, prop, fontext='ttf', directory=None,

                 fallback_to_default=True, rebuild_if_missing=True):

        

                                                                         

                                                                           

                              

        rc_params = tuple(tuple(mpl.rcParams[key]) for key in [

            "font.serif", "font.sans-serif", "font.cursive", "font.fantasy",

            "font.monospace"])

        ret = self._findfont_cached(

            prop, fontext, directory, fallback_to_default, rebuild_if_missing,

            rc_params)

        if isinstance(ret, cbook._ExceptionInfo):

            raise ret.to_exception()

        return ret



    def get_font_names(self):

        

        return list({font.name for font in self.ttflist})



    def _find_fonts_by_props(self, prop, fontext='ttf', directory=None,

                             fallback_to_default=True, rebuild_if_missing=True):

        



        prop = FontProperties._from_any(prop)



        fpaths = []

        for family in prop.get_family():

            cprop = prop.copy()

            cprop.set_family(family)                             



            try:

                fpaths.append(

                    self.findfont(

                        cprop, fontext, directory,

                        fallback_to_default=False,                             

                        rebuild_if_missing=rebuild_if_missing,

                    )

                )

            except ValueError:

                if family in font_family_aliases:

                    _log.warning(

                        "findfont: Generic family %r not found because "

                        "none of the following families were found: %s",

                        family, ", ".join(self._expand_aliases(family))

                    )

                else:

                    _log.warning("findfont: Font family %r not found.", family)



                                                                

                                        

        if not fpaths:

            if fallback_to_default:

                dfamily = self.defaultFamily[fontext]

                cprop = prop.copy()

                cprop.set_family(dfamily)

                fpaths.append(

                    self.findfont(

                        cprop, fontext, directory,

                        fallback_to_default=True,

                        rebuild_if_missing=rebuild_if_missing,

                    )

                )

            else:

                raise ValueError("Failed to find any font, and fallback "

                                 "to the default font was disabled")



        return fpaths



    @lru_cache(1024)

    def _findfont_cached(self, prop, fontext, directory, fallback_to_default,

                         rebuild_if_missing, rc_params):



        prop = FontProperties._from_any(prop)



        fname = prop.get_file()

        if fname is not None:

            return fname



        if fontext == 'afm':

            fontlist = self.afmlist

        else:

            fontlist = self.ttflist



        best_score = 1e64

        best_font = None



        _log.debug('findfont: Matching %s.', prop)

        for font in fontlist:

            if (directory is not None and

                    Path(directory) not in Path(font.fname).parents):

                continue

                                                                             

            score = (self.score_family(prop.get_family(), font.name) * 10

                     + self.score_style(prop.get_style(), font.style)

                     + self.score_variant(prop.get_variant(), font.variant)

                     + self.score_weight(prop.get_weight(), font.weight)

                     + self.score_stretch(prop.get_stretch(), font.stretch)

                     + self.score_size(prop.get_size(), font.size))

            _log.debug('findfont: score(%s) = %s', font, score)

            if score < best_score:

                best_score = score

                best_font = font

            if score == 0:

                break

        if best_font is not None and (_normalize_weight(prop.get_weight()) !=

                                      _normalize_weight(best_font.weight)):

            _log.warning('findfont: Failed to find font weight %s, now using %s.',

                         prop.get_weight(), best_font.weight)



        if best_font is None or best_score >= 10.0:

            if fallback_to_default:

                _log.warning(

                    'findfont: Font family %s not found. Falling back to %s.',

                    prop.get_family(), self.defaultFamily[fontext])

                for family in map(str.lower, prop.get_family()):

                    if family in font_family_aliases:

                        _log.warning(

                            "findfont: Generic family %r not found because "

                            "none of the following families were found: %s",

                            family, ", ".join(self._expand_aliases(family)))

                default_prop = prop.copy()

                default_prop.set_family(self.defaultFamily[fontext])

                return self.findfont(default_prop, fontext, directory,

                                     fallback_to_default=False)

            else:

                                                                            

                                                                             

                                  

                return cbook._ExceptionInfo(

                    ValueError,

                    f"Failed to find font {prop}, and fallback to the default font was "

                    f"disabled"

                )

        else:

            _log.debug('findfont: Matching %s to %s (%r) with score of %f.',

                       prop, best_font.name, best_font.fname, best_score)

            result = best_font.fname



        if not os.path.isfile(result):

            if rebuild_if_missing:

                _log.info(

                    'findfont: Found a missing font file.  Rebuilding cache.')

                new_fm = _load_fontmanager(try_read_cache=False)

                                                                             

                                                        

                                                                             

                                                  

                vars(self).update(vars(new_fm))

                return self.findfont(

                    prop, fontext, directory, rebuild_if_missing=False)

            else:

                                                                            

                                                                             

                                  

                return cbook._ExceptionInfo(ValueError, "No valid font could be found")



        return _cached_realpath(result)





@lru_cache

def is_opentype_cff_font(filename):

    

    if os.path.splitext(filename)[1].lower() == '.otf':

        with open(filename, 'rb') as fd:

            return fd.read(4) == b"OTTO"

    else:

        return False





@lru_cache(64)

def _get_font(font_filepaths, hinting_factor, *, _kerning_factor, thread_id,

              enable_last_resort):

    first_fontpath, *rest = font_filepaths

    fallback_list = [

        ft2font.FT2Font(fpath, hinting_factor, _kerning_factor=_kerning_factor)

        for fpath in rest

    ]

    last_resort_path = _cached_realpath(

        cbook._get_data_path('fonts', 'ttf', 'LastResortHE-Regular.ttf'))

    try:

        last_resort_index = font_filepaths.index(last_resort_path)

    except ValueError:

        last_resort_index = -1

                                                                                        

                              

        if enable_last_resort:

            fallback_list.append(

                ft2font.FT2Font(last_resort_path, hinting_factor,

                                _kerning_factor=_kerning_factor,

                                _warn_if_used=True))

            last_resort_index = len(fallback_list)

    font = ft2font.FT2Font(

        first_fontpath, hinting_factor,

        _fallback_list=fallback_list,

        _kerning_factor=_kerning_factor

    )

                                                                                        

                                                                             

    if last_resort_index == 0:

        font.set_charmap(0)

    elif last_resort_index > 0:

        fallback_list[last_resort_index - 1].set_charmap(0)

    return font





                                                                               

                                                                             

                                                                              

                                                                              

                                             

if hasattr(os, "register_at_fork"):

    os.register_at_fork(after_in_child=_get_font.cache_clear)





@lru_cache(64)

def _cached_realpath(path):

                                                                              

                                                                 

    return os.path.realpath(path)





def get_font(font_filepaths, hinting_factor=None):

    

    if isinstance(font_filepaths, (str, Path, bytes)):

        paths = (_cached_realpath(font_filepaths),)

    else:

        paths = tuple(_cached_realpath(fname) for fname in font_filepaths)



    hinting_factor = mpl._val_or_rc(hinting_factor, 'text.hinting_factor')



    return _get_font(

                                      

        paths,

        hinting_factor,

        _kerning_factor=mpl.rcParams['text.kerning_factor'],

                                                                             

        thread_id=threading.get_ident(),

        enable_last_resort=mpl.rcParams['font.enable_last_resort'],

    )





def _load_fontmanager(*, try_read_cache=True):

    fm_path = Path(

        mpl.get_cachedir(), f"fontlist-v{FontManager.__version__}.json")

    if try_read_cache:

        try:

            fm = json_load(fm_path)

        except Exception:

            pass

        else:

            if getattr(fm, "_version", object()) == FontManager.__version__:

                _log.debug("Using fontManager instance from %s", fm_path)

                return fm

    fm = FontManager()

    json_dump(fm, fm_path)

    _log.info("generated new fontManager")

    return fm





fontManager = _load_fontmanager()

findfont = fontManager.findfont

get_font_names = fontManager.get_font_names

