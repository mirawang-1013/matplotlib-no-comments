



import functools

import logging



import matplotlib as mpl

from matplotlib import _api, _mathtext

from matplotlib.ft2font import LoadFlags

from matplotlib.font_manager import FontProperties

from ._mathtext import (                              

    RasterParse, VectorParse, get_unicode_index)



_log = logging.getLogger(__name__)





get_unicode_index.__module__ = __name__



                                                                              

      





class MathTextParser:

    _parser = None

    _font_type_mapping = {

        'cm':          _mathtext.BakomaFonts,

        'dejavuserif': _mathtext.DejaVuSerifFonts,

        'dejavusans':  _mathtext.DejaVuSansFonts,

        'stix':        _mathtext.StixFonts,

        'stixsans':    _mathtext.StixSansFonts,

        'custom':      _mathtext.UnicodeFonts,

    }



    def __init__(self, output):

        

        self._output_type = _api.check_getitem(

            {"path": "vector", "agg": "raster", "macosx": "raster"},

            output=output.lower())



    def parse(self, s, dpi=72, prop=None, *, antialiased=None):

        

                                                                   

                                                                  

                                                                          

                                                                        

                                

        prop = prop.copy() if prop is not None else None

        antialiased = mpl._val_or_rc(antialiased, 'text.antialiased')

        from matplotlib.backends import backend_agg

        load_glyph_flags = {

            "vector": LoadFlags.NO_HINTING,

            "raster": backend_agg.get_hinting_flag(),

        }[self._output_type]

        return self._parse_cached(s, dpi, prop, antialiased, load_glyph_flags)



    @functools.lru_cache(50)

    def _parse_cached(self, s, dpi, prop, antialiased, load_glyph_flags):

        if prop is None:

            prop = FontProperties()

        fontset_class = _api.check_getitem(

            self._font_type_mapping, fontset=prop.get_math_fontfamily())

        fontset = fontset_class(prop, load_glyph_flags)

        fontsize = prop.get_size_in_points()



        if self._parser is None:                              

            self.__class__._parser = _mathtext.Parser()



        box = self._parser.parse(s, fontset, fontsize, dpi)

        output = _mathtext.ship(box)

        if self._output_type == "vector":

            return output.to_vector()

        elif self._output_type == "raster":

            return output.to_raster(antialiased=antialiased)





def math_to_image(s, filename_or_obj, prop=None, dpi=None, format=None,

                  *, color=None):

    

    from matplotlib import figure



    parser = MathTextParser('path')

    width, height, depth, _, _ = parser.parse(s, dpi=72, prop=prop)



    fig = figure.Figure(figsize=(width / 72.0, height / 72.0))

    fig.text(0, depth/height, s, fontproperties=prop, color=color)

    fig.savefig(filename_or_obj, dpi=dpi, format=format)



    return depth

