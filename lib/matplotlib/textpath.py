from collections import OrderedDict

import logging

import urllib.parse



import numpy as np



from matplotlib import _text_helpers, dviread

from matplotlib.font_manager import (

    FontProperties, get_font, fontManager as _fontManager

)

from matplotlib.ft2font import LoadFlags

from matplotlib.mathtext import MathTextParser

from matplotlib.path import Path

from matplotlib.texmanager import TexManager

from matplotlib.transforms import Affine2D



_log = logging.getLogger(__name__)





class TextToPath:

    



    FONT_SCALE = 100.

    DPI = 72



    def __init__(self):

        self.mathtext_parser = MathTextParser('path')

        self._texmanager = None



    def _get_font(self, prop):

        

        filenames = _fontManager._find_fonts_by_props(prop)

        font = get_font(filenames)

        font.set_size(self.FONT_SCALE, self.DPI)

        return font



    def _get_hinting_flag(self):

        return LoadFlags.NO_HINTING



    def _get_char_id(self, font, ccode):

        

        return urllib.parse.quote(f"{font.postscript_name}-{ccode:x}")



    def get_text_width_height_descent(self, s, prop, ismath):

        fontsize = prop.get_size_in_points()



        if ismath == "TeX":

            return TexManager().get_text_width_height_descent(s, fontsize)



        scale = fontsize / self.FONT_SCALE



        if ismath:

            prop = prop.copy()

            prop.set_size(self.FONT_SCALE)

            width, height, descent, *_ =
                self.mathtext_parser.parse(s, 72, prop)

            return width * scale, height * scale, descent * scale



        font = self._get_font(prop)

        font.set_text(s, 0.0, flags=LoadFlags.NO_HINTING)

        w, h = font.get_width_height()

        w /= 64.0                          

        h /= 64.0

        d = font.get_descent()

        d /= 64.0

        return w * scale, h * scale, d * scale



    def get_text_path(self, prop, s, ismath=False):

        

        if ismath == "TeX":

            glyph_info, glyph_map, rects = self.get_glyphs_tex(prop, s)

        elif not ismath:

            font = self._get_font(prop)

            glyph_info, glyph_map, rects = self.get_glyphs_with_font(font, s)

        else:

            glyph_info, glyph_map, rects = self.get_glyphs_mathtext(prop, s)



        verts, codes = [], []

        for glyph_id, xposition, yposition, scale in glyph_info:

            verts1, codes1 = glyph_map[glyph_id]

            verts.extend(verts1 * scale + [xposition, yposition])

            codes.extend(codes1)

        for verts1, codes1 in rects:

            verts.extend(verts1)

            codes.extend(codes1)



                                                                

                                                                

        if not verts:

            verts = np.empty((0, 2))



        return verts, codes



    def get_glyphs_with_font(self, font, s, glyph_map=None,

                             return_new_glyphs_only=False):

        



        if glyph_map is None:

            glyph_map = OrderedDict()



        if return_new_glyphs_only:

            glyph_map_new = OrderedDict()

        else:

            glyph_map_new = glyph_map



        xpositions = []

        glyph_ids = []

        for item in _text_helpers.layout(s, font):

            char_id = self._get_char_id(item.ft_object, ord(item.char))

            glyph_ids.append(char_id)

            xpositions.append(item.x)

            if char_id not in glyph_map:

                glyph_map_new[char_id] = item.ft_object.get_path()



        ypositions = [0] * len(xpositions)

        sizes = [1.] * len(xpositions)



        rects = []



        return (list(zip(glyph_ids, xpositions, ypositions, sizes)),

                glyph_map_new, rects)



    def get_glyphs_mathtext(self, prop, s, glyph_map=None,

                            return_new_glyphs_only=False):

        



        prop = prop.copy()

        prop.set_size(self.FONT_SCALE)



        width, height, descent, glyphs, rects = self.mathtext_parser.parse(

            s, self.DPI, prop)



        if not glyph_map:

            glyph_map = OrderedDict()



        if return_new_glyphs_only:

            glyph_map_new = OrderedDict()

        else:

            glyph_map_new = glyph_map



        xpositions = []

        ypositions = []

        glyph_ids = []

        sizes = []



        for font, fontsize, ccode, ox, oy in glyphs:

            char_id = self._get_char_id(font, ccode)

            if char_id not in glyph_map:

                font.clear()

                font.set_size(self.FONT_SCALE, self.DPI)

                font.load_char(ccode, flags=LoadFlags.NO_HINTING)

                glyph_map_new[char_id] = font.get_path()



            xpositions.append(ox)

            ypositions.append(oy)

            glyph_ids.append(char_id)

            size = fontsize / self.FONT_SCALE

            sizes.append(size)



        myrects = []

        for ox, oy, w, h in rects:

            vert1 = [(ox, oy), (ox, oy + h), (ox + w, oy + h),

                     (ox + w, oy), (ox, oy), (0, 0)]

            code1 = [Path.MOVETO,

                     Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,

                     Path.CLOSEPOLY]

            myrects.append((vert1, code1))



        return (list(zip(glyph_ids, xpositions, ypositions, sizes)),

                glyph_map_new, myrects)



    def get_glyphs_tex(self, prop, s, glyph_map=None,

                       return_new_glyphs_only=False):

        

                                           



        dvifile = TexManager().make_dvi(s, self.FONT_SCALE)

        with dviread.Dvi(dvifile, self.DPI) as dvi:

            page, = dvi



        if glyph_map is None:

            glyph_map = OrderedDict()



        if return_new_glyphs_only:

            glyph_map_new = OrderedDict()

        else:

            glyph_map_new = glyph_map



        glyph_ids, xpositions, ypositions, sizes = [], [], [], []



                                                                 

                                  

        t1_encodings = {}

        for text in page.text:

            font = get_font(text.font_path)

            char_id = self._get_char_id(font, text.glyph)

            if char_id not in glyph_map:

                font.clear()

                font.set_size(self.FONT_SCALE, self.DPI)

                font.load_glyph(text.index, flags=LoadFlags.TARGET_LIGHT)

                glyph_map_new[char_id] = font.get_path()



            glyph_ids.append(char_id)

            xpositions.append(text.x)

            ypositions.append(text.y)

            sizes.append(text.font_size / self.FONT_SCALE)



        myrects = []



        for ox, oy, h, w in page.boxes:

            vert1 = [(ox, oy), (ox + w, oy), (ox + w, oy + h),

                     (ox, oy + h), (ox, oy), (0, 0)]

            code1 = [Path.MOVETO,

                     Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO,

                     Path.CLOSEPOLY]

            myrects.append((vert1, code1))



        return (list(zip(glyph_ids, xpositions, ypositions, sizes)),

                glyph_map_new, myrects)





text_to_path = TextToPath()





class TextPath(Path):

    



    def __init__(self, xy, s, size=None, prop=None,

                 _interpolation_steps=1, usetex=False):

        

                          

        from matplotlib.text import Text



        prop = FontProperties._from_any(prop)

        if size is None:

            size = prop.get_size_in_points()



        self._xy = xy

        self.set_size(size)



        self._cached_vertices = None

        s, ismath = Text(usetex=usetex)._preprocess_math(s)

        super().__init__(

            *text_to_path.get_text_path(prop, s, ismath=ismath),

            _interpolation_steps=_interpolation_steps,

            readonly=True)

        self._should_simplify = False



    def set_size(self, size):

        

        self._size = size

        self._invalid = True



    def get_size(self):

        

        return self._size



    @property

    def vertices(self):

        

        self._revalidate_path()

        return self._cached_vertices



    @property

    def codes(self):

        

        return self._codes



    def _revalidate_path(self):

        

        if self._invalid or self._cached_vertices is None:

            tr = (Affine2D()

                  .scale(self._size / text_to_path.FONT_SCALE)

                  .translate(*self._xy))

            self._cached_vertices = tr.transform(self._vertices)

            self._cached_vertices.flags.writeable = False

            self._invalid = False

