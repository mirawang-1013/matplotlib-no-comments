



from io import BytesIO

import functools

import logging



from fontTools import subset



import matplotlib as mpl

from .. import font_manager, ft2font

from .._afm import AFM

from ..backend_bases import RendererBase





@functools.lru_cache(50)

def _cached_get_afm_from_fname(fname):

    with open(fname, "rb") as fh:

        return AFM(fh)





def get_glyphs_subset(fontfile, characters):

    



    options = subset.Options(glyph_names=True, recommended_glyphs=True)



                                      

    options.drop_tables += [

        'FFTM',                        

        'PfEd',                             

        'BDF',                   

        'meta',                                                                         

        'MERG',                

        'TSIV',                                        

        'Zapf',                                                        

        'bdat',                          

        'bloc',                              

        'cidg',                                                      

        'fdsc',                               

        'feat',                                                   

        'fmtx',                           

        'fond',                                                           

        'just',                                                        

        'kerx',                                                          

        'ltag',                 

        'morx',                                       

        'trak',                   

        'xref',                                                                    

    ]

                                               

    if fontfile.endswith(".ttc"):

        options.font_number = 0



    font = subset.load_font(fontfile, options)

    subsetter = subset.Subsetter(options=options)

    subsetter.populate(text=characters)

    subsetter.subset(font)

    return font





def font_as_file(font):

    

    fh = BytesIO()

    font.save(fh, reorderTables=False)

    return fh





class CharacterTracker:

    



    def __init__(self):

        self.used = {}



    def track(self, font, s):

        

        char_to_font = font._get_fontmap(s)

        for _c, _f in char_to_font.items():

            self.used.setdefault(_f.fname, set()).add(ord(_c))



    def track_glyph(self, font, glyph):

        

        self.used.setdefault(font.fname, set()).add(glyph)





class RendererPDFPSBase(RendererBase):

                                                                 

                     

                        



    def __init__(self, width, height):

        super().__init__()

        self.width = width

        self.height = height



    def flipy(self):

                             

        return False                                   



    def option_scale_image(self):

                             

        return True                                               



    def option_image_nocomposite(self):

                             

                                                                   

        return not mpl.rcParams["image.composite_image"]



    def get_canvas_width_height(self):

                             

        return self.width * 72.0, self.height * 72.0



    def get_text_width_height_descent(self, s, prop, ismath):

                             

        if ismath == "TeX":

            return super().get_text_width_height_descent(s, prop, ismath)

        elif ismath:

            parse = self._text2path.mathtext_parser.parse(s, 72, prop)

            return parse.width, parse.height, parse.depth

        elif mpl.rcParams[self._use_afm_rc_name]:

            font = self._get_font_afm(prop)

            l, b, w, h, d = font.get_str_bbox_and_descent(s)

            scale = prop.get_size_in_points() / 1000

            w *= scale

            h *= scale

            d *= scale

            return w, h, d

        else:

            font = self._get_font_ttf(prop)

            font.set_text(s, 0.0, flags=ft2font.LoadFlags.NO_HINTING)

            w, h = font.get_width_height()

            d = font.get_descent()

            scale = 1 / 64

            w *= scale

            h *= scale

            d *= scale

            return w, h, d



    def _get_font_afm(self, prop):

        fname = font_manager.findfont(

            prop, fontext="afm", directory=self._afm_font_dir)

        return _cached_get_afm_from_fname(fname)



    def _get_font_ttf(self, prop):

        fnames = font_manager.fontManager._find_fonts_by_props(prop)

        try:

            font = font_manager.get_font(fnames)

            font.clear()

            font.set_size(prop.get_size_in_points(), 72)

            return font

        except RuntimeError:

            logging.getLogger(__name__).warning(

                "The PostScript/PDF backend does not currently "

                "support the selected font (%s).", fnames)

            raise

