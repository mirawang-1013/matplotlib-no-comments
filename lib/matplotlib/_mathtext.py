



from __future__ import annotations



import abc

import copy

import enum

import functools

import itertools

import logging

import math

import os

import re

import types

import unicodedata

import string

import textwrap

import typing as T

from typing import NamedTuple



import numpy as np

from numpy.typing import NDArray

from pyparsing import (

    Empty, Forward, Literal, Group, NotAny, OneOrMore, Optional,

    ParseBaseException, ParseException, ParseExpression, ParseFatalException,

    ParserElement, ParseResults, QuotedString, Regex, StringEnd, ZeroOrMore,

    pyparsing_common, nested_expr, one_of)



import matplotlib as mpl

from . import cbook

from ._mathtext_data import (

    latex_to_bakoma, stix_glyph_fixes, stix_virtual_fonts, tex2uni)

from .font_manager import FontProperties, findfont, get_font

from .ft2font import FT2Font, Kerning, LoadFlags





if T.TYPE_CHECKING:

    from collections.abc import Iterable

    from .ft2font import Glyph



ParserElement.enable_packrat()

_log = logging.getLogger("matplotlib.mathtext")





                                                                              

       





def get_unicode_index(symbol: str) -> int:                      

    

    try:                                                        

        return ord(symbol)

    except TypeError:

        pass

    try:                                        

        return tex2uni[symbol.strip("\\")]

    except KeyError as err:

        raise ValueError(

            f"{symbol!r} is not a valid Unicode character or TeX/Type1 symbol"

            ) from err





class VectorParse(NamedTuple):

    

    width: float

    height: float

    depth: float

    glyphs: list[tuple[FT2Font, float, int, float, float]]

    rects: list[tuple[float, float, float, float]]



VectorParse.__module__ = "matplotlib.mathtext"





class RasterParse(NamedTuple):

    

    ox: float

    oy: float

    width: float

    height: float

    depth: float

    image: NDArray[np.uint8]



RasterParse.__module__ = "matplotlib.mathtext"





class Output:

    



    def __init__(self, box: Box):

        self.box = box

        self.glyphs: list[tuple[float, float, FontInfo]] = []                  

        self.rects: list[tuple[float, float, float, float]] = []                    



    def to_vector(self) -> VectorParse:

        w, h, d = map(

            np.ceil, [self.box.width, self.box.height, self.box.depth])

        gs = [(info.font, info.fontsize, info.num, ox, h - oy + info.offset)

              for ox, oy, info in self.glyphs]

        rs = [(x1, h - y2, x2 - x1, y2 - y1)

              for x1, y1, x2, y2 in self.rects]

        return VectorParse(w, h + d, d, gs, rs)



    def to_raster(self, *, antialiased: bool) -> RasterParse:

                                                                           

                                                 

        xmin = min([*[ox + info.metrics.xmin for ox, oy, info in self.glyphs],

                    *[x1 for x1, y1, x2, y2 in self.rects], 0]) - 1

        ymin = min([*[oy - info.metrics.ymax for ox, oy, info in self.glyphs],

                    *[y1 for x1, y1, x2, y2 in self.rects], 0]) - 1

        xmax = max([*[ox + info.metrics.xmax for ox, oy, info in self.glyphs],

                    *[x2 for x1, y1, x2, y2 in self.rects], 0]) + 1

        ymax = max([*[oy - info.metrics.ymin for ox, oy, info in self.glyphs],

                    *[y2 for x1, y1, x2, y2 in self.rects], 0]) + 1

        w = xmax - xmin

        h = ymax - ymin - self.box.depth

        d = ymax - ymin - self.box.height

        image = np.zeros((math.ceil(h + max(d, 0)), math.ceil(w)), np.uint8)



                                                                              

                                                                       

                                                                             

                                                            

        shifted = ship(self.box, (-xmin, -ymin))



        for ox, oy, info in shifted.glyphs:

            info.font.draw_glyph_to_bitmap(

                image, int(ox), int(oy - info.metrics.iceberg), info.glyph,

                antialiased=antialiased)

        for x1, y1, x2, y2 in shifted.rects:

            height = max(int(y2 - y1) - 1, 0)

            if height == 0:

                center = (y2 + y1) / 2

                y = int(center - (height + 1) / 2)

            else:

                y = int(y1)

            x1 = math.floor(x1)

            x2 = math.ceil(x2)

            image[y:y+height+1, x1:x2+1] = 0xff

        return RasterParse(0, 0, w, h + d, d, image)





class FontMetrics(NamedTuple):

    

    advance: float

    height: float

    width: float

    xmin: float

    xmax: float

    ymin: float

    ymax: float

    iceberg: float

    slanted: bool





class FontInfo(NamedTuple):

    font: FT2Font

    fontsize: float

    postscript_name: str

    metrics: FontMetrics

    num: int

    glyph: Glyph

    offset: float





class Fonts(abc.ABC):

    



    def __init__(self, default_font_prop: FontProperties, load_glyph_flags: LoadFlags):

        

        self.default_font_prop = default_font_prop

        self.load_glyph_flags = load_glyph_flags



    def get_kern(self, font1: str, fontclass1: str, sym1: str, fontsize1: float,

                 font2: str, fontclass2: str, sym2: str, fontsize2: float,

                 dpi: float) -> float:

        

        return 0.



    def _get_font(self, font: str) -> FT2Font:

        raise NotImplementedError



    def _get_info(self, font: str, font_class: str, sym: str, fontsize: float,

                  dpi: float) -> FontInfo:

        raise NotImplementedError



    def get_metrics(self, font: str, font_class: str, sym: str, fontsize: float,

                    dpi: float) -> FontMetrics:

        

        info = self._get_info(font, font_class, sym, fontsize, dpi)

        return info.metrics



    def render_glyph(self, output: Output, ox: float, oy: float, font: str,

                     font_class: str, sym: str, fontsize: float, dpi: float) -> None:

        

        info = self._get_info(font, font_class, sym, fontsize, dpi)

        output.glyphs.append((ox, oy, info))



    def render_rect_filled(self, output: Output,

                           x1: float, y1: float, x2: float, y2: float) -> None:

        

        output.rects.append((x1, y1, x2, y2))



    def get_xheight(self, font: str, fontsize: float, dpi: float) -> float:

        

        raise NotImplementedError()



    def get_underline_thickness(self, font: str, fontsize: float, dpi: float) -> float:

        

        raise NotImplementedError()



    def get_sized_alternatives_for_symbol(self, fontname: str,

                                          sym: str) -> list[tuple[str, str]]:

        

        return [(fontname, sym)]





class TruetypeFonts(Fonts, metaclass=abc.ABCMeta):

    



    def __init__(self, default_font_prop: FontProperties, load_glyph_flags: LoadFlags):

        super().__init__(default_font_prop, load_glyph_flags)

                             

        self._get_info = functools.cache(self._get_info)                               

        self._fonts = {}

        self.fontmap: dict[str | int, str] = {}



        filename = findfont(self.default_font_prop)

        default_font = get_font(filename)

        self._fonts['default'] = default_font

        self._fonts['regular'] = default_font



    def _get_font(self, font: str | int) -> FT2Font:

        if font in self.fontmap:

            basename = self.fontmap[font]

        else:

                                                                                       

                                                                           

            basename = T.cast(str, font)

        cached_font = self._fonts.get(basename)

        if cached_font is None and os.path.exists(basename):

            cached_font = get_font(basename)

            self._fonts[basename] = cached_font

            self._fonts[cached_font.postscript_name] = cached_font

            self._fonts[cached_font.postscript_name.lower()] = cached_font

        return T.cast(FT2Font, cached_font)                                       



    def _get_offset(self, font: FT2Font, glyph: Glyph, fontsize: float,

                    dpi: float) -> float:

        if font.postscript_name == 'Cmex10':

            return (glyph.height / 64 / 2) + (fontsize/3 * dpi/72)

        return 0.



    def _get_glyph(self, fontname: str, font_class: str,

                   sym: str) -> tuple[FT2Font, int, bool]:

        raise NotImplementedError



                                                           

    def _get_info(self, fontname: str, font_class: str, sym: str, fontsize: float,

                  dpi: float) -> FontInfo:

        font, num, slanted = self._get_glyph(fontname, font_class, sym)

        font.set_size(fontsize, dpi)

        glyph = font.load_char(num, flags=self.load_glyph_flags)



        xmin, ymin, xmax, ymax = (val / 64 for val in glyph.bbox)

        offset = self._get_offset(font, glyph, fontsize, dpi)

        metrics = FontMetrics(

            advance=glyph.linearHoriAdvance / 65536,

            height=glyph.height / 64,

            width=glyph.width / 64,

            xmin=xmin,

            xmax=xmax,

            ymin=ymin + offset,

            ymax=ymax + offset,

                                                         

            iceberg=glyph.horiBearingY / 64 + offset,

            slanted=slanted

        )



        return FontInfo(

            font=font,

            fontsize=fontsize,

            postscript_name=font.postscript_name,

            metrics=metrics,

            num=num,

            glyph=glyph,

            offset=offset

        )



    def get_xheight(self, fontname: str, fontsize: float, dpi: float) -> float:

        font = self._get_font(fontname)

        font.set_size(fontsize, dpi)

        pclt = font.get_sfnt_table('pclt')

        if pclt is None:

                                                                               

            metrics = self.get_metrics(

                fontname, mpl.rcParams['mathtext.default'], 'x', fontsize, dpi)

            return metrics.iceberg

        x_height = (pclt['xHeight'] / 64) * (fontsize / 12) * (dpi / 100)

        return x_height



    def get_underline_thickness(self, font: str, fontsize: float, dpi: float) -> float:

                                                                      

                                                                      

                           

        return ((0.75 / 12) * fontsize * dpi) / 72



    def get_kern(self, font1: str, fontclass1: str, sym1: str, fontsize1: float,

                 font2: str, fontclass2: str, sym2: str, fontsize2: float,

                 dpi: float) -> float:

        if font1 == font2 and fontsize1 == fontsize2:

            info1 = self._get_info(font1, fontclass1, sym1, fontsize1, dpi)

            info2 = self._get_info(font2, fontclass2, sym2, fontsize2, dpi)

            font = info1.font

            return font.get_kerning(info1.num, info2.num, Kerning.DEFAULT) / 64

        return super().get_kern(font1, fontclass1, sym1, fontsize1,

                                font2, fontclass2, sym2, fontsize2, dpi)





class BakomaFonts(TruetypeFonts):

    

    _fontmap = {

        'cal': 'cmsy10',

        'rm':  'cmr10',

        'tt':  'cmtt10',

        'it':  'cmmi10',

        'bf':  'cmb10',

        'sf':  'cmss10',

        'ex':  'cmex10',

    }



    def __init__(self, default_font_prop: FontProperties, load_glyph_flags: LoadFlags):

        self._stix_fallback = StixFonts(default_font_prop, load_glyph_flags)



        super().__init__(default_font_prop, load_glyph_flags)

        for key, val in self._fontmap.items():

            fullpath = findfont(val)

            self.fontmap[key] = fullpath

            self.fontmap[val] = fullpath



    _slanted_symbols = set(r"\int \oint".split())



    def _get_glyph(self, fontname: str, font_class: str,

                   sym: str) -> tuple[FT2Font, int, bool]:

        font = None

        if fontname in self.fontmap and sym in latex_to_bakoma:

            basename, num = latex_to_bakoma[sym]

            slanted = (basename == "cmmi10") or sym in self._slanted_symbols

            font = self._get_font(basename)

        elif len(sym) == 1:

            slanted = (fontname == "it")

            font = self._get_font(fontname)

            if font is not None:

                num = ord(sym)

        if font is not None and font.get_char_index(num) != 0:

            return font, num, slanted

        else:

            return self._stix_fallback._get_glyph(fontname, font_class, sym)



                                                                  

                                                                      

                                                

    _size_alternatives = {

        '(':           [('rm', '('), ('ex', '\xa1'), ('ex', '\xb3'),

                        ('ex', '\xb5'), ('ex', '\xc3')],

        ')':           [('rm', ')'), ('ex', '\xa2'), ('ex', '\xb4'),

                        ('ex', '\xb6'), ('ex', '\x21')],

        '{':           [('cal', '{'), ('ex', '\xa9'), ('ex', '\x6e'),

                        ('ex', '\xbd'), ('ex', '\x28')],

        '}':           [('cal', '}'), ('ex', '\xaa'), ('ex', '\x6f'),

                        ('ex', '\xbe'), ('ex', '\x29')],

                                                                        

                                                       

        '[':           [('rm', '['), ('ex', '\xa3'), ('ex', '\x68'),

                        ('ex', '\x22')],

        ']':           [('rm', ']'), ('ex', '\xa4'), ('ex', '\x69'),

                        ('ex', '\x23')],

        r'\lfloor':    [('ex', '\xa5'), ('ex', '\x6a'),

                        ('ex', '\xb9'), ('ex', '\x24')],

        r'\rfloor':    [('ex', '\xa6'), ('ex', '\x6b'),

                        ('ex', '\xba'), ('ex', '\x25')],

        r'\lceil':     [('ex', '\xa7'), ('ex', '\x6c'),

                        ('ex', '\xbb'), ('ex', '\x26')],

        r'\rceil':     [('ex', '\xa8'), ('ex', '\x6d'),

                        ('ex', '\xbc'), ('ex', '\x27')],

        r'\langle':    [('ex', '\xad'), ('ex', '\x44'),

                        ('ex', '\xbf'), ('ex', '\x2a')],

        r'\rangle':    [('ex', '\xae'), ('ex', '\x45'),

                        ('ex', '\xc0'), ('ex', '\x2b')],

        r'\__sqrt__':  [('ex', '\x70'), ('ex', '\x71'),

                        ('ex', '\x72'), ('ex', '\x73')],

        r'\backslash': [('ex', '\xb2'), ('ex', '\x2f'),

                        ('ex', '\xc2'), ('ex', '\x2d')],

        r'/':          [('rm', '/'), ('ex', '\xb1'), ('ex', '\x2e'),

                        ('ex', '\xcb'), ('ex', '\x2c')],

        r'\widehat':   [('rm', '\x5e'), ('ex', '\x62'), ('ex', '\x63'),

                        ('ex', '\x64')],

        r'\widetilde': [('rm', '\x7e'), ('ex', '\x65'), ('ex', '\x66'),

                        ('ex', '\x67')],

        r'<':          [('cal', 'h'), ('ex', 'D')],

        r'>':          [('cal', 'i'), ('ex', 'E')]

        }



    for alias, target in [(r'\leftparen', '('),

                          (r'\rightparen', ')'),

                          (r'\leftbrace', '{'),

                          (r'\rightbrace', '}'),

                          (r'\leftbracket', '['),

                          (r'\rightbracket', ']'),

                          (r'\{', '{'),

                          (r'\}', '}'),

                          (r'\[', '['),

                          (r'\]', ']')]:

        _size_alternatives[alias] = _size_alternatives[target]



    def get_sized_alternatives_for_symbol(self, fontname: str,

                                          sym: str) -> list[tuple[str, str]]:

        return self._size_alternatives.get(sym, [(fontname, sym)])





class UnicodeFonts(TruetypeFonts):

    



                                                                             

                                                                              

                                       

    _cmr10_substitutions = {

        0x00D7: 0x00A3,                        

        0x2212: 0x00A1,               

    }



    def __init__(self, default_font_prop: FontProperties, load_glyph_flags: LoadFlags):

                                                                      

        fallback_rc = mpl.rcParams['mathtext.fallback']

        font_cls: type[TruetypeFonts] | None = {

            'stix': StixFonts,

            'stixsans': StixSansFonts,

            'cm': BakomaFonts

        }.get(fallback_rc)

        self._fallback_font = (font_cls(default_font_prop, load_glyph_flags)

                               if font_cls else None)



        super().__init__(default_font_prop, load_glyph_flags)

        for texfont in "cal rm tt it bf sf bfit".split():

            prop = mpl.rcParams['mathtext.' + texfont]

            font = findfont(prop)

            self.fontmap[texfont] = font

        prop = FontProperties('cmex10')

        font = findfont(prop)

        self.fontmap['ex'] = font



                                                                        

        if isinstance(self._fallback_font, StixFonts):

            stixsizedaltfonts = {

                 0: 'STIXGeneral',

                 1: 'STIXSizeOneSym',

                 2: 'STIXSizeTwoSym',

                 3: 'STIXSizeThreeSym',

                 4: 'STIXSizeFourSym',

                 5: 'STIXSizeFiveSym'}



            for size, name in stixsizedaltfonts.items():

                fullpath = findfont(name)

                self.fontmap[size] = fullpath

                self.fontmap[name] = fullpath



    _slanted_symbols = set(r"\int \oint".split())



    def _map_virtual_font(self, fontname: str, font_class: str,

                          uniindex: int) -> tuple[str, int]:

        return fontname, uniindex



    def _get_glyph(self, fontname: str, font_class: str,

                   sym: str) -> tuple[FT2Font, int, bool]:

        try:

            uniindex = get_unicode_index(sym)

            found_symbol = True

        except ValueError:

            uniindex = ord('?')

            found_symbol = False

            _log.warning("No TeX to Unicode mapping for %a.", sym)



        fontname, uniindex = self._map_virtual_font(

            fontname, font_class, uniindex)



        new_fontname = fontname



                                                                            

                                                       

        if found_symbol:

            if fontname == 'it' and uniindex < 0x10000:

                char = chr(uniindex)

                if (unicodedata.category(char)[0] != "L"

                        or unicodedata.name(char).startswith("GREEK CAPITAL")):

                    new_fontname = 'rm'



            slanted = (new_fontname == 'it') or sym in self._slanted_symbols

            found_symbol = False

            font = self._get_font(new_fontname)

            if font is not None:

                if (uniindex in self._cmr10_substitutions

                        and font.family_name == "cmr10"):

                    font = get_font(

                        cbook._get_data_path("fonts/ttf/cmsy10.ttf"))

                    uniindex = self._cmr10_substitutions[uniindex]

                glyphindex = font.get_char_index(uniindex)

                if glyphindex != 0:

                    found_symbol = True



        if not found_symbol:

            if self._fallback_font:

                if (fontname in ('it', 'regular')

                        and isinstance(self._fallback_font, StixFonts)):

                    fontname = 'rm'



                g = self._fallback_font._get_glyph(fontname, font_class, sym)

                family = g[0].family_name

                if family in list(BakomaFonts._fontmap.values()):

                    family = "Computer Modern"

                _log.info("Substituting symbol %s from %s", sym, family)

                return g



            else:

                if (fontname in ('it', 'regular')

                        and isinstance(self, StixFonts)):

                    return self._get_glyph('rm', font_class, sym)

                _log.warning("Font %r does not have a glyph for %a [U+%x], "

                             "substituting with a dummy symbol.",

                             new_fontname, sym, uniindex)

                font = self._get_font('rm')

                uniindex = 0xA4                                              

                slanted = False



        return font, uniindex, slanted



    def get_sized_alternatives_for_symbol(self, fontname: str,

                                          sym: str) -> list[tuple[str, str]]:

        if self._fallback_font:

            return self._fallback_font.get_sized_alternatives_for_symbol(

                fontname, sym)

        return [(fontname, sym)]





class DejaVuFonts(UnicodeFonts, metaclass=abc.ABCMeta):

    _fontmap: dict[str | int, str] = {}



    def __init__(self, default_font_prop: FontProperties, load_glyph_flags: LoadFlags):

                                                                      

        if isinstance(self, DejaVuSerifFonts):

            self._fallback_font = StixFonts(default_font_prop, load_glyph_flags)

        else:

            self._fallback_font = StixSansFonts(default_font_prop, load_glyph_flags)

        self.bakoma = BakomaFonts(default_font_prop, load_glyph_flags)

        TruetypeFonts.__init__(self, default_font_prop, load_glyph_flags)

                                                    

        self._fontmap.update({

            1: 'STIXSizeOneSym',

            2: 'STIXSizeTwoSym',

            3: 'STIXSizeThreeSym',

            4: 'STIXSizeFourSym',

            5: 'STIXSizeFiveSym',

        })

        for key, name in self._fontmap.items():

            fullpath = findfont(name)

            self.fontmap[key] = fullpath

            self.fontmap[name] = fullpath



    def _get_glyph(self, fontname: str, font_class: str,

                   sym: str) -> tuple[FT2Font, int, bool]:

                                              

        if sym == r'\prime':

            return self.bakoma._get_glyph(fontname, font_class, sym)

        else:

                                                                      

            uniindex = get_unicode_index(sym)

            font = self._get_font('ex')

            if font is not None:

                glyphindex = font.get_char_index(uniindex)

                if glyphindex != 0:

                    return super()._get_glyph('ex', font_class, sym)

                                            

            return super()._get_glyph(fontname, font_class, sym)





class DejaVuSerifFonts(DejaVuFonts):

    

    _fontmap = {

        'rm': 'DejaVu Serif',

        'it': 'DejaVu Serif:italic',

        'bf': 'DejaVu Serif:weight=bold',

        'bfit': 'DejaVu Serif:italic:bold',

        'sf': 'DejaVu Sans',

        'tt': 'DejaVu Sans Mono',

        'ex': 'DejaVu Serif Display',

        0:    'DejaVu Serif',

    }





class DejaVuSansFonts(DejaVuFonts):

    

    _fontmap = {

        'rm': 'DejaVu Sans',

        'it': 'DejaVu Sans:italic',

        'bf': 'DejaVu Sans:weight=bold',

        'bfit': 'DejaVu Sans:italic:bold',

        'sf': 'DejaVu Sans',

        'tt': 'DejaVu Sans Mono',

        'ex': 'DejaVu Sans Display',

        0:    'DejaVu Sans',

    }





class StixFonts(UnicodeFonts):

    

    _fontmap: dict[str | int, str] = {

        'rm': 'STIXGeneral',

        'it': 'STIXGeneral:italic',

        'bf': 'STIXGeneral:weight=bold',

        'bfit': 'STIXGeneral:italic:bold',

        'nonunirm': 'STIXNonUnicode',

        'nonuniit': 'STIXNonUnicode:italic',

        'nonunibf': 'STIXNonUnicode:weight=bold',

        0: 'STIXGeneral',

        1: 'STIXSizeOneSym',

        2: 'STIXSizeTwoSym',

        3: 'STIXSizeThreeSym',

        4: 'STIXSizeFourSym',

        5: 'STIXSizeFiveSym',

    }

    _fallback_font = None

    _sans = False



    def __init__(self, default_font_prop: FontProperties, load_glyph_flags: LoadFlags):

        TruetypeFonts.__init__(self, default_font_prop, load_glyph_flags)

        for key, name in self._fontmap.items():

            fullpath = findfont(name)

            self.fontmap[key] = fullpath

            self.fontmap[name] = fullpath



    def _map_virtual_font(self, fontname: str, font_class: str,

                          uniindex: int) -> tuple[str, int]:

                                                            

                      

        font_mapping = stix_virtual_fonts.get(fontname)

        if (self._sans and font_mapping is None

                and fontname not in ('regular', 'default')):

            font_mapping = stix_virtual_fonts['sf']

            doing_sans_conversion = True

        else:

            doing_sans_conversion = False



        if isinstance(font_mapping, dict):

            try:

                mapping = font_mapping[font_class]

            except KeyError:

                mapping = font_mapping['rm']

        elif isinstance(font_mapping, list):

            mapping = font_mapping

        else:

            mapping = None



        if mapping is not None:

                                                

            lo = 0

            hi = len(mapping)

            while lo < hi:

                mid = (lo+hi)//2

                range = mapping[mid]

                if uniindex < range[0]:

                    hi = mid

                elif uniindex <= range[1]:

                    break

                else:

                    lo = mid + 1



            if range[0] <= uniindex <= range[1]:

                uniindex = uniindex - range[0] + range[3]

                fontname = range[2]

            elif not doing_sans_conversion:

                                                      

                uniindex = 0x1

                fontname = mpl.rcParams['mathtext.default']



                                    

        if fontname in ('rm', 'it'):

            uniindex = stix_glyph_fixes.get(uniindex, uniindex)



                                        

        if fontname in ('it', 'rm', 'bf', 'bfit') and 0xe000 <= uniindex <= 0xf8ff:

            fontname = 'nonuni' + fontname



        return fontname, uniindex



    @functools.cache

    def get_sized_alternatives_for_symbol(                          

            self,

            fontname: str,

            sym: str) -> list[tuple[str, str]] | list[tuple[int, str]]:

        fixes = {

            '\\{': '{', '\\}': '}', '\\[': '[', '\\]': ']',

            '<': '\N{MATHEMATICAL LEFT ANGLE BRACKET}',

            '>': '\N{MATHEMATICAL RIGHT ANGLE BRACKET}',

        }

        sym = fixes.get(sym, sym)

        try:

            uniindex = get_unicode_index(sym)

        except ValueError:

            return [(fontname, sym)]

        alternatives = [(i, chr(uniindex)) for i in range(6)

                        if self._get_font(i).get_char_index(uniindex) != 0]

                                                                      

                                                                 

        if sym == r'\__sqrt__':

            alternatives = alternatives[:-1]

        return alternatives





class StixSansFonts(StixFonts):

    

    _sans = True





                                                                              

                    



                                                                  

                                                                   

       

 

                                                                  

                                                    

 

                                   

                                                

                                

                                    

                                  

                              

                              

 

                                                                 

                     

 

                                                                     

             



                                                              

SHRINK_FACTOR   = 0.7

                                                                           

                 

NUM_SIZE_LEVELS = 6





class FontConstantsBase:

    

                                                                              

    script_space: T.ClassVar[float] = 0.05



                                                                          

    subdrop: T.ClassVar[float] = 0.4



                                                                           

    sup1: T.ClassVar[float] = 0.7



                                                                    

    sub1: T.ClassVar[float] = 0.3



                                                                           

                            

    sub2: T.ClassVar[float] = 0.5



                                                                             

                                         

    delta: T.ClassVar[float] = 0.025



                                                                     

                                                                     

                        

    delta_slanted: T.ClassVar[float] = 0.2



                                                                            

               

    delta_integral: T.ClassVar[float] = 0.1





class ComputerModernFontConstants(FontConstantsBase):

    script_space = 0.075

    subdrop = 0.2

    sup1 = 0.45

    sub1 = 0.2

    sub2 = 0.3

    delta = 0.075

    delta_slanted = 0.3

    delta_integral = 0.3





class STIXFontConstants(FontConstantsBase):

    script_space = 0.1

    sup1 = 0.8

    sub2 = 0.6

    delta = 0.05

    delta_slanted = 0.3

    delta_integral = 0.3





class STIXSansFontConstants(FontConstantsBase):

    script_space = 0.05

    sup1 = 0.8

    delta_slanted = 0.6

    delta_integral = 0.3





class DejaVuSerifFontConstants(FontConstantsBase):

    pass





class DejaVuSansFontConstants(FontConstantsBase):

    pass





                                                                

_font_constant_mapping = {

    'DejaVu Sans': DejaVuSansFontConstants,

    'DejaVu Sans Mono': DejaVuSansFontConstants,

    'DejaVu Serif': DejaVuSerifFontConstants,

    'cmb10': ComputerModernFontConstants,

    'cmex10': ComputerModernFontConstants,

    'cmmi10': ComputerModernFontConstants,

    'cmr10': ComputerModernFontConstants,

    'cmss10': ComputerModernFontConstants,

    'cmsy10': ComputerModernFontConstants,

    'cmtt10': ComputerModernFontConstants,

    'STIXGeneral': STIXFontConstants,

    'STIXNonUnicode': STIXFontConstants,

    'STIXSizeFiveSym': STIXFontConstants,

    'STIXSizeFourSym': STIXFontConstants,

    'STIXSizeThreeSym': STIXFontConstants,

    'STIXSizeTwoSym': STIXFontConstants,

    'STIXSizeOneSym': STIXFontConstants,

                                                          

    'Bitstream Vera Sans': DejaVuSansFontConstants,

    'Bitstream Vera': DejaVuSansFontConstants,

    }





def _get_font_constant_set(state: ParserState) -> type[FontConstantsBase]:

    constants = _font_constant_mapping.get(

        state.fontset._get_font(state.font).family_name, FontConstantsBase)

                                                                      

                                                                  

    if (constants is STIXFontConstants and

            isinstance(state.fontset, StixSansFonts)):

        return STIXSansFontConstants

    return constants





class Node:

    



    def __init__(self) -> None:

        self.size = 0



    def __repr__(self) -> str:

        return type(self).__name__



    def get_kerning(self, next: Node | None) -> float:

        return 0.0



    def shrink(self) -> None:

        

        self.size += 1



    def render(self, output: Output, x: float, y: float) -> None:

        





class Box(Node):

    



    def __init__(self, width: float, height: float, depth: float) -> None:

        super().__init__()

        self.width  = width

        self.height = height

        self.depth  = depth



    def shrink(self) -> None:

        super().shrink()

        if self.size < NUM_SIZE_LEVELS:

            self.width  *= SHRINK_FACTOR

            self.height *= SHRINK_FACTOR

            self.depth  *= SHRINK_FACTOR



    def render(self, output: Output,                          

               x1: float, y1: float, x2: float, y2: float) -> None:

        pass





class Vbox(Box):

    



    def __init__(self, height: float, depth: float):

        super().__init__(0., height, depth)





class Hbox(Box):

    



    def __init__(self, width: float):

        super().__init__(width, 0., 0.)





class Char(Node):

    



    def __init__(self, c: str, state: ParserState):

        super().__init__()

        self.c = c

        self.fontset = state.fontset

        self.font = state.font

        self.font_class = state.font_class

        self.fontsize = state.fontsize

        self.dpi = state.dpi

                                                                 

                                                     

        self._update_metrics()



    def __repr__(self) -> str:

        return '`%s`' % self.c



    def _update_metrics(self) -> None:

        metrics = self._metrics = self.fontset.get_metrics(

            self.font, self.font_class, self.c, self.fontsize, self.dpi)

        if self.c == ' ':

            self.width = metrics.advance

        else:

            self.width = metrics.width

        self.height = metrics.iceberg

        self.depth = -(metrics.iceberg - metrics.height)



    def is_slanted(self) -> bool:

        return self._metrics.slanted



    def get_kerning(self, next: Node | None) -> float:

        

        advance = self._metrics.advance - self.width

        kern = 0.

        if isinstance(next, Char):

            kern = self.fontset.get_kern(

                self.font, self.font_class, self.c, self.fontsize,

                next.font, next.font_class, next.c, next.fontsize,

                self.dpi)

        return advance + kern



    def render(self, output: Output, x: float, y: float) -> None:

        self.fontset.render_glyph(

            output, x, y,

            self.font, self.font_class, self.c, self.fontsize, self.dpi)



    def shrink(self) -> None:

        super().shrink()

        if self.size < NUM_SIZE_LEVELS:

            self.fontsize *= SHRINK_FACTOR

            self.width    *= SHRINK_FACTOR

            self.height   *= SHRINK_FACTOR

            self.depth    *= SHRINK_FACTOR





class Accent(Char):

    

    def _update_metrics(self) -> None:

        metrics = self._metrics = self.fontset.get_metrics(

            self.font, self.font_class, self.c, self.fontsize, self.dpi)

        self.width = metrics.xmax - metrics.xmin

        self.height = metrics.ymax - metrics.ymin

        self.depth = 0



    def shrink(self) -> None:

        super().shrink()

        self._update_metrics()



    def render(self, output: Output, x: float, y: float) -> None:

        self.fontset.render_glyph(

            output, x - self._metrics.xmin, y + self._metrics.ymin,

            self.font, self.font_class, self.c, self.fontsize, self.dpi)





class List(Box):

    



    def __init__(self, elements: T.Sequence[Node]):

        super().__init__(0., 0., 0.)

        self.shift_amount = 0.                        

        self.children = [*elements]                                

                                                                           

        self.glue_set     = 0.                                  

        self.glue_sign    = 0                                             

        self.glue_order   = 0                                                



    def __repr__(self):

        return "{}<w={:.02f} h={:.02f} d={:.02f} s={:.02f}>[{}]".format(

            super().__repr__(),

            self.width, self.height,

            self.depth, self.shift_amount,

            "\n" + textwrap.indent(

                "\n".join(map("{!r},".format, self.children)),

                "  ") + "\n"

            if self.children else ""

        )



    def _set_glue(self, x: float, sign: int, totals: list[float],

                  error_type: str) -> None:

        self.glue_order = o = next(

                                                                     

            (i for i in range(len(totals))[::-1] if totals[i] != 0), 0)

        self.glue_sign = sign

        if totals[o] != 0.:

            self.glue_set = x / totals[o]

        else:

            self.glue_sign = 0

            self.glue_ratio = 0.

        if o == 0:

            if len(self.children):

                _log.warning("%s %s: %r",

                             error_type, type(self).__name__, self)



    def shrink(self) -> None:

        for child in self.children:

            child.shrink()

        super().shrink()

        if self.size < NUM_SIZE_LEVELS:

            self.shift_amount *= SHRINK_FACTOR

            self.glue_set     *= SHRINK_FACTOR





class Hlist(List):

    



    def __init__(self, elements: T.Sequence[Node], w: float = 0.0,

                 m: T.Literal['additional', 'exactly'] = 'additional',

                 do_kern: bool = True):

        super().__init__(elements)

        if do_kern:

            self.kern()

        self.hpack(w=w, m=m)



    def kern(self) -> None:

        

        new_children = []

        for elem0, elem1 in itertools.zip_longest(self.children, self.children[1:]):

            new_children.append(elem0)

            kerning_distance = elem0.get_kerning(elem1)

            if kerning_distance != 0.:

                kern = Kern(kerning_distance)

                new_children.append(kern)

        self.children = new_children



    def hpack(self, w: float = 0.0,

              m: T.Literal['additional', 'exactly'] = 'additional') -> None:

        

                                                                          

                                

                                

        h = 0.

        d = 0.

        x = 0.

        total_stretch = [0.] * 4

        total_shrink = [0.] * 4

        for p in self.children:

            if isinstance(p, Char):

                x += p.width

                h = max(h, p.height)

                d = max(d, p.depth)

            elif isinstance(p, Box):

                x += p.width

                if not np.isinf(p.height) and not np.isinf(p.depth):

                    s = getattr(p, 'shift_amount', 0.)

                    h = max(h, p.height - s)

                    d = max(d, p.depth + s)

            elif isinstance(p, Glue):

                glue_spec = p.glue_spec

                x += glue_spec.width

                total_stretch[glue_spec.stretch_order] += glue_spec.stretch

                total_shrink[glue_spec.shrink_order] += glue_spec.shrink

            elif isinstance(p, Kern):

                x += p.width

        self.height = h

        self.depth = d



        if m == 'additional':

            w += x

        self.width = w

        x = w - x



        if x == 0.:

            self.glue_sign = 0

            self.glue_order = 0

            self.glue_ratio = 0.

            return

        if x > 0.:

            self._set_glue(x, 1, total_stretch, "Overful")

        else:

            self._set_glue(x, -1, total_shrink, "Underful")





class Vlist(List):

    



    def __init__(self, elements: T.Sequence[Node], h: float = 0.0,

                 m: T.Literal['additional', 'exactly'] = 'additional'):

        super().__init__(elements)

        self.vpack(h=h, m=m)



    def vpack(self, h: float = 0.0,

              m: T.Literal['additional', 'exactly'] = 'additional',

              l: float = np.inf) -> None:

        

                                                                          

                                

                                

        w = 0.

        d = 0.

        x = 0.

        total_stretch = [0.] * 4

        total_shrink = [0.] * 4

        for p in self.children:

            if isinstance(p, Box):

                x += d + p.height

                d = p.depth

                if not np.isinf(p.width):

                    s = getattr(p, 'shift_amount', 0.)

                    w = max(w, p.width + s)

            elif isinstance(p, Glue):

                x += d

                d = 0.

                glue_spec = p.glue_spec

                x += glue_spec.width

                total_stretch[glue_spec.stretch_order] += glue_spec.stretch

                total_shrink[glue_spec.shrink_order] += glue_spec.shrink

            elif isinstance(p, Kern):

                x += d + p.width

                d = 0.

            elif isinstance(p, Char):

                raise RuntimeError(

                    "Internal mathtext error: Char node found in Vlist")



        self.width = w

        if d > l:

            x += d - l

            self.depth = l

        else:

            self.depth = d



        if m == 'additional':

            h += x

        self.height = h

        x = h - x



        if x == 0:

            self.glue_sign = 0

            self.glue_order = 0

            self.glue_ratio = 0.

            return



        if x > 0.:

            self._set_glue(x, 1, total_stretch, "Overful")

        else:

            self._set_glue(x, -1, total_shrink, "Underful")





class Rule(Box):

    



    def __init__(self, width: float, height: float, depth: float, state: ParserState):

        super().__init__(width, height, depth)

        self.fontset = state.fontset



    def render(self, output: Output,                          

               x: float, y: float, w: float, h: float) -> None:

        self.fontset.render_rect_filled(output, x, y, x + w, y + h)





class Hrule(Rule):

    



    def __init__(self, state: ParserState, thickness: float | None = None):

        if thickness is None:

            thickness = state.get_current_underline_thickness()

        height = depth = thickness * 0.5

        super().__init__(np.inf, height, depth, state)





class Vrule(Rule):

    



    def __init__(self, state: ParserState):

        thickness = state.get_current_underline_thickness()

        super().__init__(thickness, np.inf, np.inf, state)





class _GlueSpec(NamedTuple):

    width: float

    stretch: float

    stretch_order: int

    shrink: float

    shrink_order: int





_GlueSpec._named = {                              

    'fil':         _GlueSpec(0., 1., 1, 0., 0),

    'fill':        _GlueSpec(0., 1., 2, 0., 0),

    'filll':       _GlueSpec(0., 1., 3, 0., 0),

    'neg_fil':     _GlueSpec(0., 0., 0, 1., 1),

    'neg_fill':    _GlueSpec(0., 0., 0, 1., 2),

    'neg_filll':   _GlueSpec(0., 0., 0, 1., 3),

    'empty':       _GlueSpec(0., 0., 0, 0., 0),

    'ss':          _GlueSpec(0., 1., 1, -1., 1),

}





class Glue(Node):

    



    def __init__(self,

                 glue_type: _GlueSpec | T.Literal["fil", "fill", "filll",

                                                  "neg_fil", "neg_fill", "neg_filll",

                                                  "empty", "ss"]):

        super().__init__()

        if isinstance(glue_type, str):

            glue_spec = _GlueSpec._named[glue_type]                              

        elif isinstance(glue_type, _GlueSpec):

            glue_spec = glue_type

        else:

            raise ValueError("glue_type must be a glue spec name or instance")

        self.glue_spec = glue_spec



    def shrink(self) -> None:

        super().shrink()

        if self.size < NUM_SIZE_LEVELS:

            g = self.glue_spec

            self.glue_spec = g._replace(width=g.width * SHRINK_FACTOR)





class HCentered(Hlist):

    



    def __init__(self, elements: list[Node]):

        super().__init__([Glue('ss'), *elements, Glue('ss')], do_kern=False)





class VCentered(Vlist):

    



    def __init__(self, elements: list[Node]):

        super().__init__([Glue('ss'), *elements, Glue('ss')])





class Kern(Node):

    



    height = 0

    depth = 0



    def __init__(self, width: float):

        super().__init__()

        self.width = width



    def __repr__(self) -> str:

        return "k%.02f" % self.width



    def shrink(self) -> None:

        super().shrink()

        if self.size < NUM_SIZE_LEVELS:

            self.width *= SHRINK_FACTOR





class AutoHeightChar(Hlist):

    



    def __init__(self, c: str, height: float, depth: float, state: ParserState,

                 always: bool = False, factor: float | None = None):

        alternatives = state.fontset.get_sized_alternatives_for_symbol(state.font, c)



        x_height = state.fontset.get_xheight(state.font, state.fontsize, state.dpi)



        state = state.copy()

        target_total = height + depth

        for fontname, sym in alternatives:

            state.font = fontname

            char = Char(sym, state)

                                                                             

                                                                 

            if char.height + char.depth >= target_total - 0.2 * x_height:

                break



        shift = 0.0

        if state.font != 0 or len(alternatives) == 1:

            if factor is None:

                factor = target_total / (char.height + char.depth)

            state.fontsize *= factor

            char = Char(sym, state)



            shift = (depth - char.depth)



        super().__init__([char])

        self.shift_amount = shift





class AutoWidthChar(Hlist):

    



    def __init__(self, c: str, width: float, state: ParserState, always: bool = False,

                 char_class: type[Char] = Char):

        alternatives = state.fontset.get_sized_alternatives_for_symbol(state.font, c)



        state = state.copy()

        for fontname, sym in alternatives:

            state.font = fontname

            char = char_class(sym, state)

            if char.width >= width:

                break



        factor = width / char.width

        state.fontsize *= factor

        char = char_class(sym, state)



        super().__init__([char])

        self.width = char.width





def ship(box: Box, xy: tuple[float, float] = (0, 0)) -> Output:

    

    ox, oy = xy

    cur_v = 0.

    cur_h = 0.

    off_h = ox

    off_v = oy + box.height

    output = Output(box)



    def clamp(value: float) -> float:

        return -1e9 if value < -1e9 else +1e9 if value > +1e9 else value



    def hlist_out(box: Hlist) -> None:

        nonlocal cur_v, cur_h



        cur_g = 0

        cur_glue = 0.

        glue_order = box.glue_order

        glue_sign = box.glue_sign

        base_line = cur_v

        left_edge = cur_h



        for p in box.children:

            if isinstance(p, Char):

                p.render(output, cur_h + off_h, cur_v + off_v)

                cur_h += p.width

            elif isinstance(p, Kern):

                cur_h += p.width

            elif isinstance(p, List):

                         

                if len(p.children) == 0:

                    cur_h += p.width

                else:

                    edge = cur_h

                    cur_v = base_line + p.shift_amount

                    if isinstance(p, Hlist):

                        hlist_out(p)

                    elif isinstance(p, Vlist):

                                                                    

                        vlist_out(p)

                    else:

                        assert False, "unreachable code"

                    cur_h = edge + p.width

                    cur_v = base_line

            elif isinstance(p, Box):

                         

                rule_height = p.height

                rule_depth = p.depth

                rule_width = p.width

                if np.isinf(rule_height):

                    rule_height = box.height

                if np.isinf(rule_depth):

                    rule_depth = box.depth

                if rule_height > 0 and rule_width > 0:

                    cur_v = base_line + rule_depth

                    p.render(output,

                             cur_h + off_h, cur_v + off_v,

                             rule_width, rule_height)

                    cur_v = base_line

                cur_h += rule_width

            elif isinstance(p, Glue):

                         

                glue_spec = p.glue_spec

                rule_width = glue_spec.width - cur_g

                if glue_sign != 0:          

                    if glue_sign == 1:              

                        if glue_spec.stretch_order == glue_order:

                            cur_glue += glue_spec.stretch

                            cur_g = round(clamp(box.glue_set * cur_glue))

                    elif glue_spec.shrink_order == glue_order:

                        cur_glue += glue_spec.shrink

                        cur_g = round(clamp(box.glue_set * cur_glue))

                rule_width += cur_g

                cur_h += rule_width



    def vlist_out(box: Vlist) -> None:

        nonlocal cur_v, cur_h



        cur_g = 0

        cur_glue = 0.

        glue_order = box.glue_order

        glue_sign = box.glue_sign

        left_edge = cur_h

        cur_v -= box.height

        top_edge = cur_v



        for p in box.children:

            if isinstance(p, Kern):

                cur_v += p.width

            elif isinstance(p, List):

                if len(p.children) == 0:

                    cur_v += p.height + p.depth

                else:

                    cur_v += p.height

                    cur_h = left_edge + p.shift_amount

                    save_v = cur_v

                    p.width = box.width

                    if isinstance(p, Hlist):

                        hlist_out(p)

                    elif isinstance(p, Vlist):

                        vlist_out(p)

                    else:

                        assert False, "unreachable code"

                    cur_v = save_v + p.depth

                    cur_h = left_edge

            elif isinstance(p, Box):

                rule_height = p.height

                rule_depth = p.depth

                rule_width = p.width

                if np.isinf(rule_width):

                    rule_width = box.width

                rule_height += rule_depth

                if rule_height > 0 and rule_depth > 0:

                    cur_v += rule_height

                    p.render(output,

                             cur_h + off_h, cur_v + off_v,

                             rule_width, rule_height)

            elif isinstance(p, Glue):

                glue_spec = p.glue_spec

                rule_height = glue_spec.width - cur_g

                if glue_sign != 0:          

                    if glue_sign == 1:              

                        if glue_spec.stretch_order == glue_order:

                            cur_glue += glue_spec.stretch

                            cur_g = round(clamp(box.glue_set * cur_glue))

                    elif glue_spec.shrink_order == glue_order:             

                        cur_glue += glue_spec.shrink

                        cur_g = round(clamp(box.glue_set * cur_glue))

                rule_height += cur_g

                cur_v += rule_height

            elif isinstance(p, Char):

                raise RuntimeError(

                    "Internal mathtext error: Char node found in vlist")



    assert isinstance(box, Hlist)

    hlist_out(box)

    return output





                                                                              

        





def Error(msg: str) -> ParserElement:

    

    def raise_error(s: str, loc: int, toks: ParseResults) -> T.Any:

        raise ParseFatalException(s, loc, msg)



    return Empty().set_parse_action(raise_error)





class ParserState:

    



    def __init__(self, fontset: Fonts, font: str, font_class: str, fontsize: float,

                 dpi: float):

        self.fontset = fontset

        self._font = font

        self.font_class = font_class

        self.fontsize = fontsize

        self.dpi = dpi



    def copy(self) -> ParserState:

        return copy.copy(self)



    @property

    def font(self) -> str:

        return self._font



    @font.setter

    def font(self, name: str) -> None:

        if name in ('rm', 'it', 'bf', 'bfit'):

            self.font_class = name

        self._font = name



    def get_current_underline_thickness(self) -> float:

        

        return self.fontset.get_underline_thickness(

            self.font, self.fontsize, self.dpi)





def cmd(expr: str, args: ParserElement) -> ParserElement:

    



    def names(elt: ParserElement) -> T.Generator[str, None, None]:

        if isinstance(elt, ParseExpression):

            for expr in elt.exprs:

                yield from names(expr)

        elif elt.resultsName:

            yield elt.resultsName



    csname = expr.split("{", 1)[0]

    err = (csname + "".join("{%s}" % name for name in names(args))

           if expr == csname else expr)

    return csname - (args | Error(f"Expected {err}"))





class Parser:

    



    class _MathStyle(enum.Enum):

        DISPLAYSTYLE = 0

        TEXTSTYLE = 1

        SCRIPTSTYLE = 2

        SCRIPTSCRIPTSTYLE = 3



    _binary_operators = set(

      '+ * - \N{MINUS SIGN}'

      r'''
      \pm             \sqcap                   \rhd
      \mp             \sqcup                   \unlhd
      \times          \vee                     \unrhd
      \div            \wedge                   \oplus
      \ast            \setminus                \ominus
      \star           \wr                      \otimes
      \circ           \diamond                 \oslash
      \bullet         \bigtriangleup           \odot
      \cdot           \bigtriangledown         \bigcirc
      \cap            \triangleleft            \dagger
      \cup            \triangleright           \ddagger
      \uplus          \lhd                     \amalg
      \dotplus        \dotminus                \Cap
      \Cup            \barwedge                \boxdot
      \boxminus       \boxplus                 \boxtimes
      \curlyvee       \curlywedge              \divideontimes
      \doublebarwedge \leftthreetimes          \rightthreetimes
      \slash          \veebar                  \barvee
      \cupdot         \intercal                \amalg
      \circledcirc    \circleddash             \circledast
      \boxbar         \obar                    \merge
      \minuscolon     \dotsminusdots
      '''.split())



    _relation_symbols = set(r'''
      = < > :
      \leq          \geq          \equiv       \models
      \prec         \succ         \sim         \perp
      \preceq       \succeq       \simeq       \mid
      \ll           \gg           \asymp       \parallel
      \subset       \supset       \approx      \bowtie
      \subseteq     \supseteq     \cong        \Join
      \sqsubset     \sqsupset     \neq         \smile
      \sqsubseteq   \sqsupseteq   \doteq       \frown
      \in           \ni           \propto      \vdash
      \dashv        \dots         \doteqdot    \leqq
      \geqq         \lneqq        \gneqq       \lessgtr
      \leqslant     \geqslant     \eqgtr       \eqless
      \eqslantless  \eqslantgtr   \lesseqgtr   \backsim
      \backsimeq    \lesssim      \gtrsim      \precsim
      \precnsim     \gnsim        \lnsim       \succsim
      \succnsim     \nsim         \lesseqqgtr  \gtreqqless
      \gtreqless    \subseteqq    \supseteqq   \subsetneqq
      \supsetneqq   \lessapprox   \approxeq    \gtrapprox
      \precapprox   \succapprox   \precnapprox \succnapprox
      \npreccurlyeq \nsucccurlyeq \nsqsubseteq \nsqsupseteq
      \sqsubsetneq  \sqsupsetneq  \nlesssim    \ngtrsim
      \nlessgtr     \ngtrless     \lnapprox    \gnapprox
      \napprox      \approxeq     \approxident \lll
      \ggg          \nparallel    \Vdash       \Vvdash
      \nVdash       \nvdash       \vDash       \nvDash
      \nVDash       \oequal       \simneqq     \triangle
      \triangleq         \triangleeq         \triangleleft
      \triangleright     \ntriangleleft      \ntriangleright
      \trianglelefteq    \ntrianglelefteq    \trianglerighteq
      \ntrianglerighteq  \blacktriangleleft  \blacktriangleright
      \equalparallel     \measuredrightangle \varlrtriangle
      \Doteq        \Bumpeq       \Subset      \Supset
      \backepsilon  \because      \therefore   \bot
      \top          \bumpeq       \circeq      \coloneq
      \curlyeqprec  \curlyeqsucc  \eqcirc      \eqcolon
      \eqsim        \fallingdotseq \gtrdot     \gtrless
      \ltimes       \rtimes       \lessdot     \ne
      \ncong        \nequiv       \ngeq        \ngtr
      \nleq         \nless        \nmid        \notin
      \nprec        \nsubset      \nsubseteq   \nsucc
      \nsupset      \nsupseteq    \pitchfork   \preccurlyeq
      \risingdotseq \subsetneq    \succcurlyeq \supsetneq
      \varpropto    \vartriangleleft \scurel
      \vartriangleright \rightangle \equal     \backcong
      \eqdef        \wedgeq       \questeq     \between
      \veeeq        \disin        \varisins    \isins
      \isindot      \varisinobar  \isinobar    \isinvb
      \isinE        \nisd         \varnis      \nis
      \varniobar    \niobar       \bagmember   \ratio
      \Equiv        \stareq       \measeq      \arceq
      \rightassert  \rightModels  \smallin     \smallowns
      \notsmallowns \nsimeq'''.split())



    _arrow_symbols = set(r"""
     \leftarrow \longleftarrow \uparrow \Leftarrow \Longleftarrow
     \Uparrow \rightarrow \longrightarrow \downarrow \Rightarrow
     \Longrightarrow \Downarrow \leftrightarrow \updownarrow
     \longleftrightarrow \updownarrow \Leftrightarrow
     \Longleftrightarrow \Updownarrow \mapsto \longmapsto \nearrow
     \hookleftarrow \hookrightarrow \searrow \leftharpoonup
     \rightharpoonup \swarrow \leftharpoondown \rightharpoondown
     \nwarrow \rightleftharpoons \leadsto \dashrightarrow
     \dashleftarrow \leftleftarrows \leftrightarrows \Lleftarrow
     \Rrightarrow \twoheadleftarrow \leftarrowtail \looparrowleft
     \leftrightharpoons \curvearrowleft \circlearrowleft \Lsh
     \upuparrows \upharpoonleft \downharpoonleft \multimap
     \leftrightsquigarrow \rightrightarrows \rightleftarrows
     \rightrightarrows \rightleftarrows \twoheadrightarrow
     \rightarrowtail \looparrowright \rightleftharpoons
     \curvearrowright \circlearrowright \Rsh \downdownarrows
     \upharpoonright \downharpoonright \rightsquigarrow \nleftarrow
     \nrightarrow \nLeftarrow \nRightarrow \nleftrightarrow
     \nLeftrightarrow \to \Swarrow \Searrow \Nwarrow \Nearrow
     \leftsquigarrow \overleftarrow \overleftrightarrow \cwopencirclearrow
     \downzigzagarrow \cupleftarrow \rightzigzagarrow \twoheaddownarrow
     \updownarrowbar \twoheaduparrow \rightarrowbar \updownarrows
     \barleftarrow \mapsfrom \mapsdown \mapsup \Ldsh \Rdsh
     """.split())



    _spaced_symbols = _binary_operators | _relation_symbols | _arrow_symbols



    _punctuation_symbols = set(r', ; . ! \ldotp \cdotp'.split())



    _overunder_symbols = set(r'''
       \sum \prod \coprod \bigcap \bigcup \bigsqcup \bigvee
       \bigwedge \bigodot \bigotimes \bigoplus \biguplus
       '''.split())



    _overunder_functions = set("lim liminf limsup sup max min".split())



    _dropsub_symbols = set(r'\int \oint \iint \oiint \iiint \oiiint \iiiint'.split())



    _fontnames = set("rm cal it tt sf bf bfit "

                     "default bb frak scr regular".split())



    _function_names = set("""
      arccos csc ker min arcsin deg lg Pr arctan det lim sec arg dim
      liminf sin cos exp limsup sinh cosh gcd ln sup cot hom log tan
      coth inf max tanh""".split())



    _ambi_delims = set(r"""
      | \| / \backslash \uparrow \downarrow \updownarrow \Uparrow
      \Downarrow \Updownarrow . \vert \Vert""".split())

    _left_delims = set(r"""
      ( [ \{ < \lfloor \langle \lceil \lbrace \leftbrace \lbrack \leftparen \lgroup
      """.split())

    _right_delims = set(r"""
      ) ] \} > \rfloor \rangle \rceil \rbrace \rightbrace \rbrack \rightparen \rgroup
      """.split())

    _delims = _left_delims | _right_delims | _ambi_delims



    _small_greek = set([unicodedata.name(chr(i)).split()[-1].lower() for i in

                       range(ord('\N{GREEK SMALL LETTER ALPHA}'),

                             ord('\N{GREEK SMALL LETTER OMEGA}') + 1)])

    _latin_alphabets = set(string.ascii_letters)



    def __init__(self) -> None:

        p = types.SimpleNamespace()



        def set_names_and_parse_actions() -> None:

            for key, val in vars(p).items():

                if not key.startswith('_'):

                                                                                   

                                                                                   

                                                                            

                    if key not in ("token", "placeable", "auto_delim"):

                        val.set_name(key)

                                 

                    if hasattr(self, key):

                        val.set_parse_action(getattr(self, key))



                           



                                                                          

        def csnames(group: str, names: Iterable[str]) -> Regex:

            ends_with_alpha = []

            ends_with_nonalpha = []

            for name in names:

                if name[-1].isalpha():

                    ends_with_alpha.append(name)

                else:

                    ends_with_nonalpha.append(name)

            return Regex(

                r"\\(?P<{group}>(?:{alpha})(?![A-Za-z]){additional}{nonalpha})".format(

                    group=group,

                    alpha="|".join(map(re.escape, ends_with_alpha)),

                    additional="|" if ends_with_nonalpha else "",

                    nonalpha="|".join(map(re.escape, ends_with_nonalpha)),

                )

            )



        p.float_literal  = Regex(r"[-+]?([0-9]+\.?[0-9]*|\.[0-9]+)")

        p.space          = one_of(self._space_widths)("space")



        p.style_literal  = one_of(

            [str(e.value) for e in self._MathStyle])("style_literal")



        p.symbol         = Regex(

            r"[a-zA-Z0-9 +\-*/<>=:,.;!\?&'@()\[\]|\U00000080-\U0001ffff]"

            r"|\\[%${}\[\]_|]"

            + r"|\\(?:{})(?![A-Za-z])".format(

                "|".join(map(re.escape, tex2uni)))

        )("sym").leave_whitespace()

        p.unknown_symbol = Regex(r"\\[A-Za-z]+")("name")



        p.font           = csnames("font", self._fontnames)

        p.start_group    = Optional(r"\math" + one_of(self._fontnames)("font")) + "{"

        p.end_group      = Literal("}")



        p.delim          = one_of(self._delims)



                                                                            

                                           

        p.auto_delim       = Forward()

        p.placeable        = Forward()

        p.named_placeable  = Forward()

        p.required_group   = Forward()

        p.optional_group   = Forward()

        p.token            = Forward()



                                                                      

                                                                            

                                                       

                                                                   

                                                               

        p.named_placeable <<= p.placeable



        set_names_and_parse_actions()                                       



        p.optional_group <<= "{" + ZeroOrMore(p.token)("group") + "}"

        p.required_group <<= "{" + OneOrMore(p.token)("group") + "}"



        p.customspace = cmd(r"\hspace", "{" + p.float_literal("space") + "}")



        p.accent = (

            csnames("accent", [*self._accent_map, *self._wide_accents])

            - p.named_placeable("sym"))



        p.function = csnames("name", self._function_names)



        p.group = p.start_group + ZeroOrMore(p.token)("group") + p.end_group

        p.unclosed_group = (p.start_group + ZeroOrMore(p.token)("group") + StringEnd())



        p.frac  = cmd(r"\frac", p.required_group("num") + p.required_group("den"))

        p.dfrac = cmd(r"\dfrac", p.required_group("num") + p.required_group("den"))

        p.binom = cmd(r"\binom", p.required_group("num") + p.required_group("den"))



        p.genfrac = cmd(

            r"\genfrac",

            "{" + Optional(p.delim)("ldelim") + "}"

            + "{" + Optional(p.delim)("rdelim") + "}"

            + "{" + p.float_literal("rulesize") + "}"

            + "{" + Optional(p.style_literal)("style") + "}"

            + p.required_group("num")

            + p.required_group("den"))



        p.sqrt = cmd(

            r"\sqrt{value}",

            Optional("[" + OneOrMore(NotAny("]") + p.token)("root") + "]")

            + p.required_group("value"))



        p.overline = cmd(r"\overline", p.required_group("body"))



        p.overset  = cmd(

            r"\overset",

            p.optional_group("annotation") + p.optional_group("body"))

        p.underset = cmd(

            r"\underset",

            p.optional_group("annotation") + p.optional_group("body"))



        p.text = cmd(r"\text", QuotedString('{', '\\', end_quote_char="}"))



        p.substack = cmd(r"\substack",

                           nested_expr(opener="{", closer="}",

                                       content=Group(OneOrMore(p.token)) +

                                       ZeroOrMore(Literal("\\\\").suppress()))("parts"))



        p.subsuper = (

            (Optional(p.placeable)("nucleus")

             + OneOrMore(one_of(["_", "^"]) - p.placeable)("subsuper")

             + Regex("'*")("apostrophes"))

            | Regex("'+")("apostrophes")

            | (p.named_placeable("nucleus") + Regex("'*")("apostrophes"))

        )



        p.simple = p.space | p.customspace | p.font | p.subsuper



        p.token <<= (

            p.simple

            | p.auto_delim

            | p.unclosed_group

            | p.unknown_symbol                

        )



        p.operatorname = cmd(r"\operatorname", "{" + ZeroOrMore(p.simple)("name") + "}")



        p.boldsymbol = cmd(

            r"\boldsymbol", "{" + ZeroOrMore(p.simple)("value") + "}")



        p.placeable     <<= (

            p.accent                                                       

            | p.symbol                                                         

                                               

            | p.function

            | p.operatorname

            | p.group

            | p.frac

            | p.dfrac

            | p.binom

            | p.genfrac

            | p.overset

            | p.underset

            | p.sqrt

            | p.overline

            | p.text

            | p.boldsymbol

            | p.substack

        )



        mdelim = r"\middle" - (p.delim("mdelim") | Error("Expected a delimiter"))

        p.auto_delim    <<= (

            r"\left" - (p.delim("left") | Error("Expected a delimiter"))

            + ZeroOrMore(p.simple | p.auto_delim | mdelim)("mid")

            + r"\right" - (p.delim("right") | Error("Expected a delimiter"))

        )



                           

        p.math          = OneOrMore(p.token)

        p.math_string   = QuotedString('$', '\\', unquote_results=False)

        p.non_math      = Regex(r"(?:(?:\\[$])|[^$])*").leave_whitespace()

        p.main          = (

            p.non_math + ZeroOrMore(p.math_string + p.non_math) + StringEnd()

        )

        set_names_and_parse_actions()                         



        self._expression = p.main

        self._math_expression = p.math



                                                                  

        self._in_subscript_or_superscript = False



    def parse(self, s: str, fonts_object: Fonts, fontsize: float, dpi: float) -> Hlist:

        

        self._state_stack = [

            ParserState(fonts_object, 'default', 'rm', fontsize, dpi)]

        self._em_width_cache: dict[tuple[str, float, float], float] = {}

        try:

            result = self._expression.parse_string(s)

        except ParseBaseException as err:

                                                                             

            raise ValueError("\n" + ParseException.explain(err, 0)) from None

        self._state_stack = []

        self._in_subscript_or_superscript = False

                                                                     

        self._em_width_cache = {}

        ParserElement.reset_cache()

        return T.cast(Hlist, result[0])                                



    def get_state(self) -> ParserState:

        

        return self._state_stack[-1]



    def pop_state(self) -> None:

        

        self._state_stack.pop()



    def push_state(self) -> None:

        

        self._state_stack.append(self.get_state().copy())



    def main(self, toks: ParseResults) -> list[Hlist]:

        return [Hlist(toks.as_list())]



    def math_string(self, toks: ParseResults) -> ParseResults:

        return self._math_expression.parse_string(toks[0][1:-1], parse_all=True)



    def math(self, toks: ParseResults) -> T.Any:

        hlist = Hlist(toks.as_list())

        self.pop_state()

        return [hlist]



    def non_math(self, toks: ParseResults) -> T.Any:

        s = toks[0].replace(r'\$', '$')

        symbols = [Char(c, self.get_state()) for c in s]

        hlist = Hlist(symbols)

                                                        

        self.push_state()

        self.get_state().font = mpl.rcParams['mathtext.default']

        return [hlist]



    float_literal = staticmethod(pyparsing_common.convert_to_float)



    def text(self, toks: ParseResults) -> T.Any:

        self.push_state()

        state = self.get_state()

        state.font = 'rm'

        hlist = Hlist([Char(c, state) for c in toks[1]])

        self.pop_state()

        return [hlist]



    def _make_space(self, percentage: float) -> Kern:

                                                                             

                                                                            

                                                                            

                                                                        

                             

        state = self.get_state()

        key = (state.font, state.fontsize, state.dpi)

        width = self._em_width_cache.get(key)

        if width is None:

            metrics = state.fontset.get_metrics(

                'it', mpl.rcParams['mathtext.default'], 'm',

                state.fontsize, state.dpi)

            width = metrics.advance

            self._em_width_cache[key] = width

        return Kern(width * percentage)



    _space_widths = {

        r'\,':         0.16667,                   

        r'\thinspace': 0.16667,                   

        r'\/':         0.16667,                   

        r'\>':         0.22222,                   

        r'\:':         0.22222,                   

        r'\;':         0.27778,                   

        r'\ ':         0.33333,                   

        r'~':          0.33333,                                 

        r'\enspace':   0.5,                       

        r'\quad':      1,                       

        r'\qquad':     2,                       

        r'\!':         -0.16667,                    

    }



    def space(self, toks: ParseResults) -> T.Any:

        num = self._space_widths[toks["space"]]

        box = self._make_space(num)

        return [box]



    def customspace(self, toks: ParseResults) -> T.Any:

        return [self._make_space(toks["space"])]



    def symbol(self, s: str, loc: int,

               toks: ParseResults | dict[str, str]) -> T.Any:

        c = toks["sym"]

        if c == "-":

                                                                             

                                                                        

                                                                            

                                                                             

                                                              

            c = "\N{MINUS SIGN}"

        try:

            char = Char(c, self.get_state())

        except ValueError as err:

            raise ParseFatalException(s, loc,

                                      "Unknown symbol: %s" % c) from err



        if c in self._spaced_symbols:

                                                                        

                                                        

            prev_char = next((c for c in s[:loc][::-1] if c != ' '), '')

                                                                      

                                                                          

            if (self._in_subscript_or_superscript or (

                    c in self._binary_operators and (

                    len(s[:loc].split()) == 0 or prev_char in {

                        '{', *self._left_delims, *self._relation_symbols}))):

                return [char]

            else:

                return [Hlist([self._make_space(0.2),

                               char,

                               self._make_space(0.2)],

                              do_kern=True)]

        elif c in self._punctuation_symbols:

            prev_char = next((c for c in s[:loc][::-1] if c != ' '), '')

            next_char = next((c for c in s[loc + 1:] if c != ' '), '')



                                                  

            if c == ',':

                if prev_char == '{' and next_char == '}':

                    return [char]



                                                     

            if c == '.' and prev_char.isdigit() and next_char.isdigit():

                return [char]

            else:

                return [Hlist([char, self._make_space(0.2)], do_kern=True)]

        return [char]



    def unknown_symbol(self, s: str, loc: int, toks: ParseResults) -> T.Any:

        raise ParseFatalException(s, loc, f"Unknown symbol: {toks['name']}")



    _accent_map = {

        r'hat':            r'\circumflexaccent',

        r'breve':          r'\combiningbreve',

        r'bar':            r'\combiningoverline',

        r'grave':          r'\combininggraveaccent',

        r'acute':          r'\combiningacuteaccent',

        r'tilde':          r'\combiningtilde',

        r'dot':            r'\combiningdotabove',

        r'ddot':           r'\combiningdiaeresis',

        r'dddot':          r'\combiningthreedotsabove',

        r'ddddot':         r'\combiningfourdotsabove',

        r'vec':            r'\combiningrightarrowabove',

        r'"':              r'\combiningdiaeresis',

        r"`":              r'\combininggraveaccent',

        r"'":              r'\combiningacuteaccent',

        r'~':              r'\combiningtilde',

        r'.':              r'\combiningdotabove',

        r'^':              r'\circumflexaccent',

        r'overrightarrow': r'\rightarrow',

        r'overleftarrow':  r'\leftarrow',

        r'mathring':       r'\circ',

    }



    _wide_accents = set(r"widehat widetilde widebar".split())



    def accent(self, toks: ParseResults) -> T.Any:

        state = self.get_state()

        thickness = state.get_current_underline_thickness()

        accent = toks["accent"]

        sym = toks["sym"]

        accent_box: Node

        if accent in self._wide_accents:

            accent_box = AutoWidthChar(

                '\\' + accent, sym.width, state, char_class=Accent)

        else:

            accent_box = Accent(self._accent_map[accent], state)

        if accent == 'mathring':

            accent_box.shrink()

            accent_box.shrink()

        centered = HCentered([Hbox(sym.width / 4.0), accent_box])

        centered.hpack(sym.width, 'exactly')

        return Vlist([

                centered,

                Vbox(0., thickness * 2.0),

                Hlist([sym])

                ])



    def function(self, s: str, loc: int, toks: ParseResults) -> T.Any:

        hlist = self.operatorname(s, loc, toks)

        hlist.function_name = toks["name"]

        return hlist



    def operatorname(self, s: str, loc: int, toks: ParseResults) -> T.Any:

        self.push_state()

        state = self.get_state()

        state.font = 'rm'

        hlist_list: list[Node] = []

                                                         

        name = toks["name"]

        for c in name:

            if isinstance(c, Char):

                c.font = 'rm'

                c._update_metrics()

                hlist_list.append(c)

            elif isinstance(c, str):

                hlist_list.append(Char(c, state))

            else:

                hlist_list.append(c)

        next_char_loc = loc + len(name) + 1

        if isinstance(name, ParseResults):

            next_char_loc += len('operatorname{}')

        next_char = next((c for c in s[next_char_loc:] if c != ' '), '')

        delimiters = self._delims | {'^', '_'}

        if (next_char not in delimiters and

                name not in self._overunder_functions):

                                                                               

            hlist_list += [self._make_space(self._space_widths[r'\,'])]

        self.pop_state()

                                                            

                                                                   

        if next_char in {'^', '_'}:

            self._in_subscript_or_superscript = True

        else:

            self._in_subscript_or_superscript = False



        return Hlist(hlist_list)



    def start_group(self, toks: ParseResults) -> T.Any:

        self.push_state()

                                           

        if toks.get("font"):

            self.get_state().font = toks.get("font")

        return []



    def group(self, toks: ParseResults) -> T.Any:

        grp = Hlist(toks.get("group", []))

        return [grp]



    def required_group(self, toks: ParseResults) -> T.Any:

        return Hlist(toks.get("group", []))



    optional_group = required_group



    def end_group(self) -> T.Any:

        self.pop_state()

        return []



    def unclosed_group(self, s: str, loc: int, toks: ParseResults) -> T.Any:

        raise ParseFatalException(s, len(s), "Expected '}'")



    def font(self, toks: ParseResults) -> T.Any:

        self.get_state().font = toks["font"]

        return []



    def is_overunder(self, nucleus: Node) -> bool:

        if isinstance(nucleus, Char):

            return nucleus.c in self._overunder_symbols

        elif isinstance(nucleus, Hlist) and hasattr(nucleus, 'function_name'):

            return nucleus.function_name in self._overunder_functions

        return False



    def is_dropsub(self, nucleus: Node) -> bool:

        if isinstance(nucleus, Char):

            return nucleus.c in self._dropsub_symbols

        return False



    def is_slanted(self, nucleus: Node) -> bool:

        if isinstance(nucleus, Char):

            return nucleus.is_slanted()

        return False



    def subsuper(self, s: str, loc: int, toks: ParseResults) -> T.Any:

        nucleus = toks.get("nucleus", Hbox(0))

        subsuper = toks.get("subsuper", [])

        napostrophes = len(toks.get("apostrophes", []))



        if not subsuper and not napostrophes:

            return nucleus



        sub = super = None

        while subsuper:

            op, arg, *subsuper = subsuper

            if op == '_':

                if sub is not None:

                    raise ParseFatalException("Double subscript")

                sub = arg

            else:

                if super is not None:

                    raise ParseFatalException("Double superscript")

                super = arg



        state = self.get_state()

        rule_thickness = state.fontset.get_underline_thickness(

            state.font, state.fontsize, state.dpi)

        x_height = state.fontset.get_xheight(

            state.font, state.fontsize, state.dpi)



        if napostrophes:

            if super is None:

                super = Hlist([])

            for i in range(napostrophes):

                super.children.extend(self.symbol(s, loc, {"sym": "\\prime"}))

                                                                      

                       

            super.kern()

            super.hpack()



                                                        

        if self.is_overunder(nucleus):

            vlist = []

            shift = 0.

            width = nucleus.width

            if super is not None:

                super.shrink()

                width = max(width, super.width)

            if sub is not None:

                sub.shrink()

                width = max(width, sub.width)



            vgap = rule_thickness * 3.0

            if super is not None:

                hlist = HCentered([super])

                hlist.hpack(width, 'exactly')

                vlist.extend([hlist, Vbox(0, vgap)])

            hlist = HCentered([nucleus])

            hlist.hpack(width, 'exactly')

            vlist.append(hlist)

            if sub is not None:

                hlist = HCentered([sub])

                hlist.hpack(width, 'exactly')

                vlist.extend([Vbox(0, vgap), hlist])

                shift = hlist.height + vgap + nucleus.depth

            vlt = Vlist(vlist)

            vlt.shift_amount = shift

            result = Hlist([vlt])

            return [result]



                                                                            

                                                                            

                                                     

                                                                           

                                                                              

                                                                               

                                        

        last_char = nucleus

        if isinstance(nucleus, Hlist):

            new_children = nucleus.children

            if len(new_children):

                                  

                if (isinstance(new_children[-1], Kern) and

                        isinstance(new_children[-2], Char)):

                    new_children = new_children[:-1]

                last_char = new_children[-1]

                if isinstance(last_char, Char):

                    last_char.width = last_char._metrics.advance

                                              

            nucleus = Hlist(new_children, do_kern=False)

        else:

            if isinstance(nucleus, Char):

                last_char.width = last_char._metrics.advance

            nucleus = Hlist([nucleus])



                                         

        consts = _get_font_constant_set(state)

        lc_height   = last_char.height

        lc_baseline = 0

        if self.is_dropsub(last_char):

            lc_baseline = last_char.depth



                                           

        superkern = consts.delta * x_height

        subkern = consts.delta * x_height

        if self.is_slanted(last_char):

            superkern += consts.delta * x_height

            superkern += consts.delta_slanted * (lc_height - x_height * 2 / 3)

            if self.is_dropsub(last_char):

                subkern = (3 * consts.delta - consts.delta_integral) * lc_height

                superkern = (3 * consts.delta + consts.delta_integral) * lc_height

            else:

                subkern = 0



        x: List

        if super is None:

                     

                                                                                     

                                                                                   

                             

            x = Hlist([Kern(subkern), T.cast(Node, sub)])

            x.shrink()

            if self.is_dropsub(last_char):

                shift_down = lc_baseline + consts.subdrop * x_height

            else:

                shift_down = consts.sub1 * x_height

            x.shift_amount = shift_down

        else:

            x = Hlist([Kern(superkern), super])

            x.shrink()

            if self.is_dropsub(last_char):

                shift_up = lc_height - consts.subdrop * x_height

            else:

                shift_up = consts.sup1 * x_height

            if sub is None:

                x.shift_amount = -shift_up

            else:                            

                y = Hlist([Kern(subkern), sub])

                y.shrink()

                if self.is_dropsub(last_char):

                    shift_down = lc_baseline + consts.subdrop * x_height

                else:

                    shift_down = consts.sub2 * x_height

                                                               

                clr = (2 * rule_thickness -

                       ((shift_up - x.depth) - (y.height - shift_down)))

                if clr > 0.:

                    shift_up += clr

                x = Vlist([

                    x,

                    Kern((shift_up - x.depth) - (y.height - shift_down)),

                    y])

                x.shift_amount = shift_down



        if not self.is_dropsub(last_char):

            x.width += consts.script_space * x_height



                                                      

                                                         

        spaced_nucleus: list[Node] = [nucleus, x]

        if self._in_subscript_or_superscript:

            spaced_nucleus += [self._make_space(self._space_widths[r'\,'])]

            self._in_subscript_or_superscript = False



        result = Hlist(spaced_nucleus)

        return [result]



    def _genfrac(self, ldelim: str, rdelim: str, rule: float | None, style: _MathStyle,

                 num: Hlist, den: Hlist) -> T.Any:

        state = self.get_state()

        thickness = state.get_current_underline_thickness()



        for _ in range(style.value):

            num.shrink()

            den.shrink()

        cnum = HCentered([num])

        cden = HCentered([den])

        width = max(num.width, den.width)

        cnum.hpack(width, 'exactly')

        cden.hpack(width, 'exactly')

        vlist = Vlist([

            cnum,                               

            Vbox(0, 2 * thickness),         

            Hrule(state, rule),            

            Vbox(0, 2 * thickness),         

            cden,                                 

        ])



                                                              

                     

        metrics = state.fontset.get_metrics(

            state.font, mpl.rcParams['mathtext.default'],

            '=', state.fontsize, state.dpi)

        shift = (cden.height -

                 ((metrics.ymax + metrics.ymin) / 2 - 3 * thickness))

        vlist.shift_amount = shift



        result: list[Box | Char | str] = [Hlist([vlist, Hbox(2 * thickness)])]

        if ldelim or rdelim:

            return self._auto_sized_delimiter(ldelim or ".", result, rdelim or ".")

        return result



    def style_literal(self, toks: ParseResults) -> T.Any:

        return self._MathStyle(int(toks["style_literal"]))



    def genfrac(self, toks: ParseResults) -> T.Any:

        return self._genfrac(

            toks.get("ldelim", ""), toks.get("rdelim", ""),

            toks["rulesize"], toks.get("style", self._MathStyle.TEXTSTYLE),

            toks["num"], toks["den"])



    def frac(self, toks: ParseResults) -> T.Any:

        return self._genfrac(

            "", "", self.get_state().get_current_underline_thickness(),

            self._MathStyle.TEXTSTYLE, toks["num"], toks["den"])



    def dfrac(self, toks: ParseResults) -> T.Any:

        return self._genfrac(

            "", "", self.get_state().get_current_underline_thickness(),

            self._MathStyle.DISPLAYSTYLE, toks["num"], toks["den"])



    def binom(self, toks: ParseResults) -> T.Any:

        return self._genfrac(

            "(", ")", 0,

            self._MathStyle.TEXTSTYLE, toks["num"], toks["den"])



    def _genset(self, s: str, loc: int, toks: ParseResults) -> T.Any:

        annotation = toks["annotation"]

        body = toks["body"]

        thickness = self.get_state().get_current_underline_thickness()



        annotation.shrink()

        centered_annotation = HCentered([annotation])

        centered_body = HCentered([body])

        width = max(centered_annotation.width, centered_body.width)

        centered_annotation.hpack(width, 'exactly')

        centered_body.hpack(width, 'exactly')



        vgap = thickness * 3

        if s[loc + 1] == "u":             

            vlist = Vlist([

                centered_body,                     

                Vbox(0, vgap),                      

                centered_annotation                      

            ])

                                                                  

            vlist.shift_amount = centered_body.depth + centered_annotation.height + vgap

        else:            

            vlist = Vlist([

                centered_annotation,                     

                Vbox(0, vgap),                      

                centered_body                      

            ])



                                                                    

                                                                

        return vlist



    overset = underset = _genset



    def sqrt(self, toks: ParseResults) -> T.Any:

        root = toks.get("root")

        body = toks["value"]

        state = self.get_state()

        thickness = state.get_current_underline_thickness()



                                                                     

                                               

        height = body.height - body.shift_amount + 5 * thickness

        depth = body.depth + body.shift_amount

        check = AutoHeightChar(r'\__sqrt__', height, depth, state, always=True)

        height = check.height - check.shift_amount

        depth = check.depth + check.shift_amount



                                                                    

        padded_body = Hlist([Hbox(2 * thickness), body, Hbox(2 * thickness)])

        rightside = Vlist([Hrule(state), Glue('fill'), padded_body])

                                                         

        rightside.vpack(height + (state.fontsize * state.dpi) / (100 * 12),

                        'exactly', depth)



                                                                   

                                                  

        if not root:

            root = Box(0.5 * check.width, 0., 0.)

        else:

            root = Hlist(root)

            root.shrink()

            root.shrink()



        root_vlist = Vlist([Hlist([root])])

        root_vlist.shift_amount = -height * 0.6



        hlist = Hlist([

            root_vlist,                      

            Kern(-0.5 * check.width),                                          

            check,                            

            rightside,                       

        ])

        return [hlist]



    def overline(self, toks: ParseResults) -> T.Any:

        body = toks["body"]



        state = self.get_state()

        thickness = state.get_current_underline_thickness()



        height = body.height - body.shift_amount + 3 * thickness

        depth = body.depth + body.shift_amount



                                   

        rightside = Vlist([Hrule(state), Glue('fill'), Hlist([body])])



                                                         

        rightside.vpack(height + (state.fontsize * state.dpi) / (100 * 12),

                        'exactly', depth)



        hlist = Hlist([rightside])

        return [hlist]



    def _auto_sized_delimiter(self, front: str,

                              middle: list[Box | Char | str],

                              back: str) -> T.Any:

        state = self.get_state()

        if len(middle):

            height = max([x.height for x in middle if not isinstance(x, str)])

            depth = max([x.depth for x in middle if not isinstance(x, str)])

            factor = None

            for idx, el in enumerate(middle):

                if el == r'\middle':

                    c = T.cast(str, middle[idx + 1])                              

                    if c != '.':

                        middle[idx + 1] = AutoHeightChar(

                                c, height, depth, state, factor=factor)

                    else:

                        middle.remove(c)

                    del middle[idx]

                                                                               

                                

            middle_part = T.cast(list[Box | Char], middle)

        else:

            height = 0

            depth = 0

            factor = 1.0

            middle_part = []



        parts: list[Node] = []

                                                                   

        if front != '.':

            parts.append(

                AutoHeightChar(front, height, depth, state, factor=factor))

        parts.extend(middle_part)

        if back != '.':

            parts.append(

                AutoHeightChar(back, height, depth, state, factor=factor))

        hlist = Hlist(parts)

        return hlist



    def auto_delim(self, toks: ParseResults) -> T.Any:

        return self._auto_sized_delimiter(

            toks["left"], toks["mid"].as_list(), toks["right"])



    def boldsymbol(self, toks: ParseResults) -> T.Any:

        self.push_state()

        state = self.get_state()

        hlist: list[Node] = []

        name = toks["value"]

        for c in name:

            if isinstance(c, Hlist):

                k = c.children[1]

                if isinstance(k, Char):

                    k.font = "bf"

                    k._update_metrics()

                hlist.append(c)

            elif isinstance(c, Char):

                c.font = "bf"

                if (c.c in self._latin_alphabets or

                   c.c[1:] in self._small_greek):

                    c.font = "bfit"

                    c._update_metrics()

                c._update_metrics()

                hlist.append(c)

            else:

                hlist.append(c)

        self.pop_state()



        return Hlist(hlist)



    def substack(self, toks: ParseResults) -> T.Any:

        parts = toks["parts"]

        state = self.get_state()

        thickness = state.get_current_underline_thickness()



        hlist = [Hlist(k) for k in parts[0]]

        max_width = max(map(lambda c: c.width, hlist))



        vlist = []

        for sub in hlist:

            cp = HCentered([sub])

            cp.hpack(max_width, 'exactly')

            vlist.append(cp)



        stack = [val

                 for pair in zip(vlist, [Vbox(0, thickness * 2)] * len(vlist))

                 for val in pair]

        del stack[-1]

        vlt = Vlist(stack)

        result = [Hlist([vlt])]

        return result

