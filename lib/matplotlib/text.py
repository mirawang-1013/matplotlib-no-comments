



import functools

import logging

import math

from numbers import Real

import weakref



import numpy as np



import matplotlib as mpl

from . import _api, artist, cbook, _docstring

from .artist import Artist

from .font_manager import FontProperties

from .patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from .textpath import TextPath, TextToPath                                 

from .transforms import (

    Affine2D, Bbox, BboxBase, BboxTransformTo, IdentityTransform, Transform)





_log = logging.getLogger(__name__)





def _get_textbox(text, renderer):

    

                                                                         

                                                                    

                                                                      

                                                                      

                                                                       



    projected_xs = []

    projected_ys = []



    theta = np.deg2rad(text.get_rotation())

    tr = Affine2D().rotate(-theta)



    _, parts, d = text._get_layout(renderer)



    for t, wh, x, y in parts:

        w, h = wh



        xt1, yt1 = tr.transform((x, y))

        yt1 -= d

        xt2, yt2 = xt1 + w, yt1 + h



        projected_xs.extend([xt1, xt2])

        projected_ys.extend([yt1, yt2])



    xt_box, yt_box = min(projected_xs), min(projected_ys)

    w_box, h_box = max(projected_xs) - xt_box, max(projected_ys) - yt_box



    x_box, y_box = Affine2D().rotate(theta).transform((xt_box, yt_box))



    return x_box, y_box, w_box, h_box





def _get_text_metrics_with_cache(renderer, text, fontprop, ismath, dpi):

    

                                                                            

                                                      

    return _get_text_metrics_with_cache_impl(

        weakref.ref(renderer), text, fontprop.copy(), ismath, dpi)





@functools.lru_cache(4096)

def _get_text_metrics_with_cache_impl(

        renderer_ref, text, fontprop, ismath, dpi):

                                                                               

    return renderer_ref().get_text_width_height_descent(text, fontprop, ismath)





@_docstring.interpd

@_api.define_aliases({

    "color": ["c"],

    "fontproperties": ["font", "font_properties"],

    "fontfamily": ["family"],

    "fontname": ["name"],

    "fontsize": ["size"],

    "fontstretch": ["stretch"],

    "fontstyle": ["style"],

    "fontvariant": ["variant"],

    "fontweight": ["weight"],

    "horizontalalignment": ["ha"],

    "verticalalignment": ["va"],

    "multialignment": ["ma"],

})

class Text(Artist):

    



    zorder = 3

    _charsize_cache = dict()



    def __repr__(self):

        return f"Text({self._x}, {self._y}, {self._text!r})"



    def __init__(self,

                 x=0, y=0, text='', *,

                 color=None,                                  

                 verticalalignment='baseline',

                 horizontalalignment='left',

                 multialignment=None,

                 fontproperties=None,                                

                 rotation=None,

                 linespacing=None,

                 rotation_mode=None,

                 usetex=None,                                               

                 wrap=False,

                 transform_rotates_text=False,

                 parse_math=None,                                             

                 antialiased=None,                                            

                 **kwargs

                 ):

        

        super().__init__()

        self._x, self._y = x, y

        self._text = ''

        self._reset_visual_defaults(

            text=text,

            color=color,

            fontproperties=fontproperties,

            usetex=usetex,

            parse_math=parse_math,

            wrap=wrap,

            verticalalignment=verticalalignment,

            horizontalalignment=horizontalalignment,

            multialignment=multialignment,

            rotation=rotation,

            transform_rotates_text=transform_rotates_text,

            linespacing=linespacing,

            rotation_mode=rotation_mode,

            antialiased=antialiased

        )

        self.update(kwargs)



    def _reset_visual_defaults(

        self,

        text='',

        color=None,

        fontproperties=None,

        usetex=None,

        parse_math=None,

        wrap=False,

        verticalalignment='baseline',

        horizontalalignment='left',

        multialignment=None,

        rotation=None,

        transform_rotates_text=False,

        linespacing=None,

        rotation_mode=None,

        antialiased=None

    ):

        self.set_text(text)

        self.set_color(mpl._val_or_rc(color, "text.color"))

        self.set_fontproperties(fontproperties)

        self.set_usetex(usetex)

        self.set_parse_math(mpl._val_or_rc(parse_math, 'text.parse_math'))

        self.set_wrap(wrap)

        self.set_verticalalignment(verticalalignment)

        self.set_horizontalalignment(horizontalalignment)

        self._multialignment = multialignment

        self.set_rotation(rotation)

        self._transform_rotates_text = transform_rotates_text

        self._bbox_patch = None                             

        self._renderer = None

        if linespacing is None:

            linespacing = 1.2                            

        self.set_linespacing(linespacing)

        self.set_rotation_mode(rotation_mode)

        self.set_antialiased(mpl._val_or_rc(antialiased, 'text.antialiased'))



    def update(self, kwargs):

                             

        ret = []

        kwargs = cbook.normalize_kwargs(kwargs, Text)

        sentinel = object()                                              

                                                                 

        fontproperties = kwargs.pop("fontproperties", sentinel)

        if fontproperties is not sentinel:

            ret.append(self.set_fontproperties(fontproperties))

                                                             

        bbox = kwargs.pop("bbox", sentinel)

        ret.extend(super().update(kwargs))

        if bbox is not sentinel:

            ret.append(self.set_bbox(bbox))

        return ret



    def __getstate__(self):

        d = super().__getstate__()

                                                    

        d['_renderer'] = None

        return d



    def contains(self, mouseevent):

        

        if (self._different_canvas(mouseevent) or not self.get_visible()

                or self._renderer is None):

            return False, {}

                                                             

                                                                       

                                                                

        bbox = Text.get_window_extent(self)

        inside = (bbox.x0 <= mouseevent.x <= bbox.x1

                  and bbox.y0 <= mouseevent.y <= bbox.y1)

        cattr = {}

                                                                             

                                                              

        if self._bbox_patch:

            patch_inside, patch_cattr = self._bbox_patch.contains(mouseevent)

            inside = inside or patch_inside

            cattr["bbox_patch"] = patch_cattr

        return inside, cattr



    def _get_xy_display(self):

        

        x, y = self.get_unitless_position()

        return self.get_transform().transform((x, y))



    def _get_multialignment(self):

        if self._multialignment is not None:

            return self._multialignment

        else:

            return self._horizontalalignment



    def _char_index_at(self, x):

        

        if not self._text:

            return 0



        text = self._text



        fontproperties = str(self._fontproperties)

        if fontproperties not in Text._charsize_cache:

            Text._charsize_cache[fontproperties] = dict()



        charsize_cache = Text._charsize_cache[fontproperties]

        for char in set(text):

            if char not in charsize_cache:

                self.set_text(char)

                bb = self.get_window_extent()

                charsize_cache[char] = bb.x1 - bb.x0



        self.set_text(text)

        bb = self.get_window_extent()



        size_accum = np.cumsum([0] + [charsize_cache[x] for x in text])

        std_x = x - bb.x0

        return (np.abs(size_accum - std_x)).argmin()



    def get_rotation(self):

        

        if self.get_transform_rotates_text():

            return self.get_transform().transform_angles(

                [self._rotation], [self.get_unitless_position()]).item(0)

        else:

            return self._rotation



    def get_transform_rotates_text(self):

        

        return self._transform_rotates_text



    def set_rotation_mode(self, m):

        

        if m is None:

            m = "default"

        else:

            _api.check_in_list(("anchor", "default", "xtick", "ytick"), rotation_mode=m)

        self._rotation_mode = m

        self.stale = True



    def get_rotation_mode(self):

        

        return self._rotation_mode



    def set_antialiased(self, antialiased):

        

        self._antialiased = antialiased

        self.stale = True



    def get_antialiased(self):

        

        return self._antialiased



    def update_from(self, other):

                             

        super().update_from(other)

        self._color = other._color

        self._multialignment = other._multialignment

        self._verticalalignment = other._verticalalignment

        self._horizontalalignment = other._horizontalalignment

        self._fontproperties = other._fontproperties.copy()

        self._usetex = other._usetex

        self._rotation = other._rotation

        self._transform_rotates_text = other._transform_rotates_text

        self._picker = other._picker

        self._linespacing = other._linespacing

        self._antialiased = other._antialiased

        self.stale = True



    def _get_layout(self, renderer):

        

        thisx, thisy = 0.0, 0.0

        lines = self._get_wrapped_text().split("\n")                               



        ws = []

        hs = []

        xs = []

        ys = []



                                                                           

        _, lp_h, lp_d = _get_text_metrics_with_cache(

            renderer, "lp", self._fontproperties,

            ismath="TeX" if self.get_usetex() else False,

            dpi=self.get_figure(root=True).dpi)

        min_dy = (lp_h - lp_d) * self._linespacing



        for i, line in enumerate(lines):

            clean_line, ismath = self._preprocess_math(line)

            if clean_line:

                w, h, d = _get_text_metrics_with_cache(

                    renderer, clean_line, self._fontproperties,

                    ismath=ismath, dpi=self.get_figure(root=True).dpi)

            else:

                w = h = d = 0



                                                                         

                                                                          

                                                                     

            h = max(h, lp_h)

            d = max(d, lp_d)



            ws.append(w)

            hs.append(h)



                                                             

            baseline = (h - d) - thisy



            if i == 0:

                                      

                thisy = -(h - d)

            else:

                                                                           

                thisy -= max(min_dy, (h - d) * self._linespacing)



            xs.append(thisx)         

            ys.append(thisy)



            thisy -= d



                                                         

        descent = d



                                  

        width = max(ws)

        xmin = 0

        xmax = width

        ymax = 0

        ymin = ys[-1] - descent                                           



                                 

        M = Affine2D().rotate_deg(self.get_rotation())



                                                             

        malign = self._get_multialignment()

        if malign == 'left':

            offset_layout = [(x, y) for x, y in zip(xs, ys)]

        elif malign == 'center':

            offset_layout = [(x + width / 2 - w / 2, y)

                             for x, y, w in zip(xs, ys, ws)]

        elif malign == 'right':

            offset_layout = [(x + width - w, y)

                             for x, y, w in zip(xs, ys, ws)]



                                                   

        corners_horiz = np.array(

            [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])



                             

        corners_rotated = M.transform(corners_horiz)

                                               

        xmin = corners_rotated[:, 0].min()

        xmax = corners_rotated[:, 0].max()

        ymin = corners_rotated[:, 1].min()

        ymax = corners_rotated[:, 1].max()

        width = xmax - xmin

        height = ymax - ymin



                                                                    

                           

        halign = self._horizontalalignment

        valign = self._verticalalignment



        rotation_mode = self.get_rotation_mode()

        if rotation_mode != "anchor":

            angle = self.get_rotation()

            if rotation_mode == 'xtick':

                halign = self._ha_for_angle(angle)

            elif rotation_mode == 'ytick':

                valign = self._va_for_angle(angle)

                                                                         

                                                            

            if halign == 'center':

                offsetx = (xmin + xmax) / 2

            elif halign == 'right':

                offsetx = xmax

            else:

                offsetx = xmin



            if valign == 'center':

                offsety = (ymin + ymax) / 2

            elif valign == 'top':

                offsety = ymax

            elif valign == 'baseline':

                offsety = ymin + descent

            elif valign == 'center_baseline':

                offsety = ymin + height - baseline / 2.0

            else:

                offsety = ymin

        else:

            xmin1, ymin1 = corners_horiz[0]

            xmax1, ymax1 = corners_horiz[2]



            if halign == 'center':

                offsetx = (xmin1 + xmax1) / 2.0

            elif halign == 'right':

                offsetx = xmax1

            else:

                offsetx = xmin1



            if valign == 'center':

                offsety = (ymin1 + ymax1) / 2.0

            elif valign == 'top':

                offsety = ymax1

            elif valign == 'baseline':

                offsety = ymax1 - baseline

            elif valign == 'center_baseline':

                offsety = ymax1 - baseline / 2.0

            else:

                offsety = ymin1



            offsetx, offsety = M.transform((offsetx, offsety))



        xmin -= offsetx

        ymin -= offsety



        bbox = Bbox.from_bounds(xmin, ymin, width, height)



                                                                   

        xys = M.transform(offset_layout) - (offsetx, offsety)



        return bbox, list(zip(lines, zip(ws, hs), *xys.T)), descent



    def set_bbox(self, rectprops):

        



        if rectprops is not None:

            props = rectprops.copy()

            boxstyle = props.pop("boxstyle", None)

            pad = props.pop("pad", None)

            if boxstyle is None:

                boxstyle = "square"

                if pad is None:

                    pad = 4          

                pad /= self.get_size()                            

            else:

                if pad is None:

                    pad = 0.3

                                                      

            if isinstance(boxstyle, str) and "pad" not in boxstyle:

                boxstyle += ",pad=%0.2f" % pad

            self._bbox_patch = FancyBboxPatch(

                (0, 0), 1, 1,

                boxstyle=boxstyle, transform=IdentityTransform(), **props)

        else:

            self._bbox_patch = None



        self._update_clip_properties()



    def get_bbox_patch(self):

        

        return self._bbox_patch



    def update_bbox_position_size(self, renderer):

        

        if self._bbox_patch:

                                                                             

                               

            posx = float(self.convert_xunits(self._x))

            posy = float(self.convert_yunits(self._y))

            posx, posy = self.get_transform().transform((posx, posy))



            x_box, y_box, w_box, h_box = _get_textbox(self, renderer)

            self._bbox_patch.set_bounds(0., 0., w_box, h_box)

            self._bbox_patch.set_transform(

                Affine2D()

                .rotate_deg(self.get_rotation())

                .translate(posx + x_box, posy + y_box))

            fontsize_in_pixel = renderer.points_to_pixels(self.get_size())

            self._bbox_patch.set_mutation_scale(fontsize_in_pixel)



    def _update_clip_properties(self):

        if self._bbox_patch:

            clipprops = dict(clip_box=self.clipbox,

                             clip_path=self._clippath,

                             clip_on=self._clipon)

            self._bbox_patch.update(clipprops)



    def set_clip_box(self, clipbox):

                              

        super().set_clip_box(clipbox)

        self._update_clip_properties()



    def set_clip_path(self, path, transform=None):

                              

        super().set_clip_path(path, transform)

        self._update_clip_properties()



    def set_clip_on(self, b):

                              

        super().set_clip_on(b)

        self._update_clip_properties()



    def get_wrap(self):

        

        return self._wrap



    def set_wrap(self, wrap):

        

        self._wrap = wrap



    def _get_wrap_line_width(self):

        

        x0, y0 = self.get_transform().transform(self.get_position())

        figure_box = self.get_figure().get_window_extent()



                                                           

        alignment = self.get_horizontalalignment()

        self.set_rotation_mode('anchor')

        rotation = self.get_rotation()



        left = self._get_dist_to_box(rotation, x0, y0, figure_box)

        right = self._get_dist_to_box(

            (180 + rotation) % 360, x0, y0, figure_box)



        if alignment == 'left':

            line_width = left

        elif alignment == 'right':

            line_width = right

        else:

            line_width = 2 * min(left, right)



        return line_width



    def _get_dist_to_box(self, rotation, x0, y0, figure_box):

        

        if rotation > 270:

            quad = rotation - 270

            h1 = (y0 - figure_box.y0) / math.cos(math.radians(quad))

            h2 = (figure_box.x1 - x0) / math.cos(math.radians(90 - quad))

        elif rotation > 180:

            quad = rotation - 180

            h1 = (x0 - figure_box.x0) / math.cos(math.radians(quad))

            h2 = (y0 - figure_box.y0) / math.cos(math.radians(90 - quad))

        elif rotation > 90:

            quad = rotation - 90

            h1 = (figure_box.y1 - y0) / math.cos(math.radians(quad))

            h2 = (x0 - figure_box.x0) / math.cos(math.radians(90 - quad))

        else:

            h1 = (figure_box.x1 - x0) / math.cos(math.radians(rotation))

            h2 = (figure_box.y1 - y0) / math.cos(math.radians(90 - rotation))



        return min(h1, h2)



    def _get_rendered_text_width(self, text):

        



        w, h, d = _get_text_metrics_with_cache(

            self._renderer, text, self.get_fontproperties(),

            cbook.is_math_text(text),

            self.get_figure(root=True).dpi)

        return math.ceil(w)



    def _get_wrapped_text(self):

        

        if not self.get_wrap():

            return self.get_text()



                                                                  

                               

        if self.get_usetex():

            return self.get_text()



                                                                             

        line_width = self._get_wrap_line_width()

        wrapped_lines = []



                                                    

        unwrapped_lines = self.get_text().split('\n')



                                                 

        for unwrapped_line in unwrapped_lines:



            sub_words = unwrapped_line.split(' ')

                                                                      

            while len(sub_words) > 0:

                if len(sub_words) == 1:

                                                              

                    wrapped_lines.append(sub_words.pop(0))

                    continue



                for i in range(2, len(sub_words) + 1):

                                                                     

                    line = ' '.join(sub_words[:i])

                    current_width = self._get_rendered_text_width(line)



                                                                               

                               

                    if current_width > line_width:

                        wrapped_lines.append(' '.join(sub_words[:i - 1]))

                        sub_words = sub_words[i - 1:]

                        break



                                                                              

                    elif i == len(sub_words):

                        wrapped_lines.append(' '.join(sub_words[:i]))

                        sub_words = []

                        break



        return '\n'.join(wrapped_lines)



    @artist.allow_rasterization

    def draw(self, renderer):

                             



        if renderer is not None:

            self._renderer = renderer

        if not self.get_visible():

            return

        if self.get_text() == '':

            return



        renderer.open_group('text', self.get_gid())



        with self._cm_set(text=self._get_wrapped_text()):

            bbox, info, descent = self._get_layout(renderer)

            trans = self.get_transform()



                                                                    

                               

            x, y = self._x, self._y

            if np.ma.is_masked(x):

                x = np.nan

            if np.ma.is_masked(y):

                y = np.nan

            posx = float(self.convert_xunits(x))

            posy = float(self.convert_yunits(y))

            posx, posy = trans.transform((posx, posy))

            if np.isnan(posx) or np.isnan(posy):

                return                              

            if not np.isfinite(posx) or not np.isfinite(posy):

                _log.warning("posx and posy should be finite values")

                return

            canvasw, canvash = renderer.get_canvas_width_height()



                                                      

                                                       

            if self._bbox_patch:

                self.update_bbox_position_size(renderer)

                self._bbox_patch.draw(renderer)



            gc = renderer.new_gc()

            gc.set_foreground(self.get_color())

            gc.set_alpha(self.get_alpha())

            gc.set_url(self._url)

            gc.set_antialiased(self._antialiased)

            self._set_gc_clip(gc)



            angle = self.get_rotation()



            for line, wh, x, y in info:



                mtext = self if len(info) == 1 else None

                x = x + posx

                y = y + posy

                if renderer.flipy():

                    y = canvash - y

                clean_line, ismath = self._preprocess_math(line)



                if self.get_path_effects():

                    from matplotlib.patheffects import PathEffectRenderer

                    textrenderer = PathEffectRenderer(

                        self.get_path_effects(), renderer)

                else:

                    textrenderer = renderer



                if self.get_usetex():

                    textrenderer.draw_tex(gc, x, y, clean_line,

                                          self._fontproperties, angle,

                                          mtext=mtext)

                else:

                    textrenderer.draw_text(gc, x, y, clean_line,

                                           self._fontproperties, angle,

                                           ismath=ismath, mtext=mtext)



        gc.restore()

        renderer.close_group('text')

        self.stale = False



    def get_color(self):

        

        return self._color



    def get_fontproperties(self):

        

        return self._fontproperties



    def get_fontfamily(self):

        

        return self._fontproperties.get_family()



    def get_fontname(self):

        

        return self._fontproperties.get_name()



    def get_fontstyle(self):

        

        return self._fontproperties.get_style()



    def get_fontsize(self):

        

        return self._fontproperties.get_size_in_points()



    def get_fontvariant(self):

        

        return self._fontproperties.get_variant()



    def get_fontweight(self):

        

        return self._fontproperties.get_weight()



    def get_stretch(self):

        

        return self._fontproperties.get_stretch()



    def get_horizontalalignment(self):

        

        return self._horizontalalignment



    def get_unitless_position(self):

        

                                                                             

                                                                             

        x = float(self.convert_xunits(self._x))

        y = float(self.convert_yunits(self._y))

        return x, y



    def get_position(self):

        

                                                                     

                                             

        return self._x, self._y



    def get_text(self):

        

        return self._text



    def get_verticalalignment(self):

        

        return self._verticalalignment



    def get_window_extent(self, renderer=None, dpi=None):

        

        if not self.get_visible():

            return Bbox.unit()



        fig = self.get_figure(root=True)

        if dpi is None:

            dpi = fig.dpi

        if self.get_text() == '':

            with cbook._setattr_cm(fig, dpi=dpi):

                tx, ty = self._get_xy_display()

                return Bbox.from_bounds(tx, ty, 0, 0)



        if renderer is not None:

            self._renderer = renderer

        if self._renderer is None:

            self._renderer = fig._get_renderer()

        if self._renderer is None:

            raise RuntimeError(

                "Cannot get window extent of text w/o renderer. You likely "

                "want to call 'figure.draw_without_rendering()' first.")



        with cbook._setattr_cm(fig, dpi=dpi):

            bbox, info, descent = self._get_layout(self._renderer)

            x, y = self.get_unitless_position()

            x, y = self.get_transform().transform((x, y))

            bbox = bbox.translated(x, y)

            return bbox



    def set_backgroundcolor(self, color):

        

        if self._bbox_patch is None:

            self.set_bbox(dict(facecolor=color, edgecolor=color))

        else:

            self._bbox_patch.update(dict(facecolor=color))



        self._update_clip_properties()

        self.stale = True



    def set_color(self, color):

        

                                                                              

                                          

        if not cbook._str_equal(color, "auto"):

            mpl.colors._check_color_like(color=color)

        self._color = color

        self.stale = True



    def set_horizontalalignment(self, align):

        

        _api.check_in_list(['center', 'right', 'left'], align=align)

        self._horizontalalignment = align

        self.stale = True



    def set_multialignment(self, align):

        

        _api.check_in_list(['center', 'right', 'left'], align=align)

        self._multialignment = align

        self.stale = True



    def set_linespacing(self, spacing):

        

        _api.check_isinstance(Real, spacing=spacing)

        self._linespacing = spacing

        self.stale = True



    def set_fontfamily(self, fontname):

        

        self._fontproperties.set_family(fontname)

        self.stale = True



    def set_fontvariant(self, variant):

        

        self._fontproperties.set_variant(variant)

        self.stale = True



    def set_fontstyle(self, fontstyle):

        

        self._fontproperties.set_style(fontstyle)

        self.stale = True



    def set_fontsize(self, fontsize):

        

        self._fontproperties.set_size(fontsize)

        self.stale = True



    def get_math_fontfamily(self):

        

        return self._fontproperties.get_math_fontfamily()



    def set_math_fontfamily(self, fontfamily):

        

        self._fontproperties.set_math_fontfamily(fontfamily)



    def set_fontweight(self, weight):

        

        self._fontproperties.set_weight(weight)

        self.stale = True



    def set_fontstretch(self, stretch):

        

        self._fontproperties.set_stretch(stretch)

        self.stale = True



    def set_position(self, xy):

        

        self.set_x(xy[0])

        self.set_y(xy[1])



    def set_x(self, x):

        

        self._x = x

        self.stale = True



    def set_y(self, y):

        

        self._y = y

        self.stale = True



    def set_rotation(self, s):

        

        if isinstance(s, Real):

            self._rotation = float(s) % 360

        elif cbook._str_equal(s, 'horizontal') or s is None:

            self._rotation = 0.

        elif cbook._str_equal(s, 'vertical'):

            self._rotation = 90.

        else:

            raise ValueError("rotation must be 'vertical', 'horizontal' or "

                             f"a number, not {s}")

        self.stale = True



    def set_transform_rotates_text(self, t):

        

        self._transform_rotates_text = t

        self.stale = True



    def set_verticalalignment(self, align):

        

        _api.check_in_list(

            ['top', 'bottom', 'center', 'baseline', 'center_baseline'],

            align=align)

        self._verticalalignment = align

        self.stale = True



    def set_text(self, s):

        

        s = '' if s is None else str(s)

        if s != self._text:

            self._text = s

            self.stale = True



    def _preprocess_math(self, s):

        

        if self.get_usetex():

            if s == " ":

                s = r"\ "

            return s, "TeX"

        elif not self.get_parse_math():

            return s, False

        elif cbook.is_math_text(s):

            return s, True

        else:

            return s.replace(r"\$", "$"), False



    def set_fontproperties(self, fp):

        

        self._fontproperties = FontProperties._from_any(fp).copy()

        self.stale = True



    @_docstring.kwarg_doc("bool, default: :rc:`text.usetex`")

    def set_usetex(self, usetex):

        

        self._usetex = bool(mpl._val_or_rc(usetex, 'text.usetex'))

        self.stale = True



    def get_usetex(self):

        

        return self._usetex



    def set_parse_math(self, parse_math):

        

        self._parse_math = bool(parse_math)



    def get_parse_math(self):

        

        return self._parse_math



    def set_fontname(self, fontname):

        

        self.set_fontfamily(fontname)



    def _ha_for_angle(self, angle):

        

        anchor_at_bottom = self.get_verticalalignment() == 'bottom'

        if (angle <= 10 or 85 <= angle <= 95 or 350 <= angle or

                170 <= angle <= 190 or 265 <= angle <= 275):

            return 'center'

        elif 10 < angle < 85 or 190 < angle < 265:

            return 'left' if anchor_at_bottom else 'right'

        return 'right' if anchor_at_bottom else 'left'



    def _va_for_angle(self, angle):

        

        anchor_at_left = self.get_horizontalalignment() == 'left'

        if (angle <= 10 or 350 <= angle or 170 <= angle <= 190

                or 80 <= angle <= 100 or 260 <= angle <= 280):

            return 'center'

        elif 190 < angle < 260 or 10 < angle < 80:

            return 'baseline' if anchor_at_left else 'top'

        return 'top' if anchor_at_left else 'baseline'





class OffsetFrom:

    



    def __init__(self, artist, ref_coord, unit="points"):

        

        self._artist = artist

        x, y = ref_coord                                                               

        self._ref_coord = x, y

        self.set_unit(unit)



    def set_unit(self, unit):

        

        _api.check_in_list(["points", "pixels"], unit=unit)

        self._unit = unit



    def get_unit(self):

        

        return self._unit



    def __call__(self, renderer):

        

        if isinstance(self._artist, Artist):

            bbox = self._artist.get_window_extent(renderer)

            xf, yf = self._ref_coord

            x = bbox.x0 + bbox.width * xf

            y = bbox.y0 + bbox.height * yf

        elif isinstance(self._artist, BboxBase):

            bbox = self._artist

            xf, yf = self._ref_coord

            x = bbox.x0 + bbox.width * xf

            y = bbox.y0 + bbox.height * yf

        elif isinstance(self._artist, Transform):

            x, y = self._artist.transform(self._ref_coord)

        else:

            _api.check_isinstance((Artist, BboxBase, Transform), artist=self._artist)

        scale = 1 if self._unit == "pixels" else renderer.points_to_pixels(1)

        return Affine2D().scale(scale).translate(x, y)





class _AnnotationBase:

    def __init__(self,

                 xy,

                 xycoords='data',

                 annotation_clip=None):



        x, y = xy                                                        

        self.xy = x, y

        self.xycoords = xycoords

        self.set_annotation_clip(annotation_clip)



        self._draggable = None



    def _get_xy(self, renderer, xy, coords):

        x, y = xy

        xcoord, ycoord = coords if isinstance(coords, tuple) else (coords, coords)

        if xcoord == 'data':

            x = float(self.convert_xunits(x))

        if ycoord == 'data':

            y = float(self.convert_yunits(y))

        return self._get_xy_transform(renderer, coords).transform((x, y))



    def _get_xy_transform(self, renderer, coords):



        if isinstance(coords, tuple):

            xcoord, ycoord = coords

            from matplotlib.transforms import blended_transform_factory

            tr1 = self._get_xy_transform(renderer, xcoord)

            tr2 = self._get_xy_transform(renderer, ycoord)

            return blended_transform_factory(tr1, tr2)

        elif callable(coords):

            tr = coords(renderer)

            if isinstance(tr, BboxBase):

                return BboxTransformTo(tr)

            elif isinstance(tr, Transform):

                return tr

            else:

                raise TypeError(

                    f"xycoords callable must return a BboxBase or Transform, not a "

                    f"{type(tr).__name__}")

        elif isinstance(coords, Artist):

            bbox = coords.get_window_extent(renderer)

            return BboxTransformTo(bbox)

        elif isinstance(coords, BboxBase):

            return BboxTransformTo(coords)

        elif isinstance(coords, Transform):

            return coords

        elif not isinstance(coords, str):

            raise TypeError(

                f"'xycoords' must be an instance of str, tuple[str, str], Artist, "

                f"Transform, or Callable, not a {type(coords).__name__}")



        if coords == 'data':

            return self.axes.transData

        elif coords == 'polar':

            from matplotlib.projections import PolarAxes

            return PolarAxes.PolarTransform() + self.axes.transData



        try:

            bbox_name, unit = coords.split()

        except ValueError:                                  

            raise ValueError(f"{coords!r} is not a valid coordinate") from None



        bbox0, xy0 = None, None



                                

        if bbox_name == "figure":

            bbox0 = self.get_figure(root=False).figbbox

        elif bbox_name == "subfigure":

            bbox0 = self.get_figure(root=False).bbox

        elif bbox_name == "axes":

            bbox0 = self.axes.bbox



                                              

        if bbox0 is not None:

            xy0 = bbox0.p0

        elif bbox_name == "offset":

            xy0 = self._get_position_xy(renderer)

        else:

            raise ValueError(f"{coords!r} is not a valid coordinate")



        if unit == "points":

            tr = Affine2D().scale(

                self.get_figure(root=True).dpi / 72)                         

        elif unit == "pixels":

            tr = Affine2D()

        elif unit == "fontsize":

            tr = Affine2D().scale(

                self.get_size() * self.get_figure(root=True).dpi / 72)

        elif unit == "fraction":

            tr = Affine2D().scale(*bbox0.size)

        else:

            raise ValueError(f"{unit!r} is not a recognized unit")



        return tr.translate(*xy0)



    def set_annotation_clip(self, b):

        

        self._annotation_clip = b



    def get_annotation_clip(self):

        

        return self._annotation_clip



    def _get_position_xy(self, renderer):

        

        return self._get_xy(renderer, self.xy, self.xycoords)



    def _check_xy(self, renderer=None):

        

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        b = self.get_annotation_clip()

        if b or (b is None and self.xycoords == "data"):

                                                  

            xy_pixel = self._get_position_xy(renderer)

            return self.axes.contains_point(xy_pixel)

        return True



    def draggable(self, state=None, use_blit=False):

        

        from matplotlib.offsetbox import DraggableAnnotation

        is_draggable = self._draggable is not None



                                       

        if state is None:

            state = not is_draggable



        if state:

            if self._draggable is None:

                self._draggable = DraggableAnnotation(self, use_blit)

        else:

            if self._draggable is not None:

                self._draggable.disconnect()

            self._draggable = None



        return self._draggable





class Annotation(Text, _AnnotationBase):

    



    def __str__(self):

        return f"Annotation({self.xy[0]:g}, {self.xy[1]:g}, {self._text!r})"



    def __init__(self, text, xy,

                 xytext=None,

                 xycoords='data',

                 textcoords=None,

                 arrowprops=None,

                 annotation_clip=None,

                 **kwargs):

        

        _AnnotationBase.__init__(self,

                                 xy,

                                 xycoords=xycoords,

                                 annotation_clip=annotation_clip)

                                     

        if (xytext is None and

                textcoords is not None and

                textcoords != xycoords):

            _api.warn_external("You have used the `textcoords` kwarg, but "

                               "not the `xytext` kwarg.  This can lead to "

                               "surprising results.")



                                                

        if textcoords is None:

            textcoords = self.xycoords

        self._textcoords = textcoords



                                 

        if xytext is None:

            xytext = self.xy

        x, y = xytext



        self.arrowprops = arrowprops

        if arrowprops is not None:

            arrowprops = arrowprops.copy()

            if "arrowstyle" in arrowprops:

                self._arrow_relpos = arrowprops.pop("relpos", (0.5, 0.5))

            else:

                                                                      

                for key in ['width', 'headwidth', 'headlength', 'shrink']:

                    arrowprops.pop(key, None)

            self.arrow_patch = FancyArrowPatch((0, 0), (1, 1), **arrowprops)

        else:

            self.arrow_patch = None



                                                                          

        Text.__init__(self, x, y, text, **kwargs)



    def contains(self, mouseevent):

        if self._different_canvas(mouseevent):

            return False, {}

        contains, tinfo = Text.contains(self, mouseevent)

        if self.arrow_patch is not None:

            in_patch, _ = self.arrow_patch.contains(mouseevent)

            contains = contains or in_patch

        return contains, tinfo



    @property

    def xycoords(self):

        return self._xycoords



    @xycoords.setter

    def xycoords(self, xycoords):

        def is_offset(s):

            return isinstance(s, str) and s.startswith("offset")



        if (isinstance(xycoords, tuple) and any(map(is_offset, xycoords))

                or is_offset(xycoords)):

            raise ValueError("xycoords cannot be an offset coordinate")

        self._xycoords = xycoords



    @property

    def xyann(self):

        

        return self.get_position()



    @xyann.setter

    def xyann(self, xytext):

        self.set_position(xytext)



    def get_anncoords(self):

        

        return self._textcoords



    def set_anncoords(self, coords):

        

        self._textcoords = coords



    anncoords = property(get_anncoords, set_anncoords, doc="""
        The coordinate system to use for `.Annotation.xyann`.""")



    def set_figure(self, fig):

                             

        if self.arrow_patch is not None:

            self.arrow_patch.set_figure(fig)

        Artist.set_figure(self, fig)



    def update_positions(self, renderer):

        

                                 

        self.set_transform(self._get_xy_transform(renderer, self.anncoords))



        arrowprops = self.arrowprops

        if arrowprops is None:

            return



        bbox = Text.get_window_extent(self, renderer)



        arrow_end = x1, y1 = self._get_position_xy(renderer)                  



        ms = arrowprops.get("mutation_scale", self.get_size())

        self.arrow_patch.set_mutation_scale(ms)



        if "arrowstyle" not in arrowprops:

                                                 

            shrink = arrowprops.get('shrink', 0.0)

            width = arrowprops.get('width', 4)

            headwidth = arrowprops.get('headwidth', 12)

            headlength = arrowprops.get('headlength', 12)



                              

            stylekw = dict(head_length=headlength / ms,

                           head_width=headwidth / ms,

                           tail_width=width / ms)



            self.arrow_patch.set_arrowstyle('simple', **stylekw)



                                  

                                                                          

            xpos = [(bbox.x0, 0), ((bbox.x0 + bbox.x1) / 2, 0.5), (bbox.x1, 1)]

            ypos = [(bbox.y0, 0), ((bbox.y0 + bbox.y1) / 2, 0.5), (bbox.y1, 1)]

            x, relposx = min(xpos, key=lambda v: abs(v[0] - x1))

            y, relposy = min(ypos, key=lambda v: abs(v[0] - y1))

            self._arrow_relpos = (relposx, relposy)

            r = np.hypot(y - y1, x - x1)

            shrink_pts = shrink * r / renderer.points_to_pixels(1)

            self.arrow_patch.shrinkA = self.arrow_patch.shrinkB = shrink_pts



                                                                         

                                                

        arrow_begin = bbox.p0 + bbox.size * self._arrow_relpos

                                                                             

                                                                              

                                                                              

        self.arrow_patch.set_positions(arrow_begin, arrow_end)



        if "patchA" in arrowprops:

            patchA = arrowprops["patchA"]

        elif self._bbox_patch:

            patchA = self._bbox_patch

        elif self.get_text() == "":

            patchA = None

        else:

            pad = renderer.points_to_pixels(4)

            patchA = Rectangle(

                xy=(bbox.x0 - pad / 2, bbox.y0 - pad / 2),

                width=bbox.width + pad, height=bbox.height + pad,

                transform=IdentityTransform(), clip_on=False)

        self.arrow_patch.set_patchA(patchA)



    @artist.allow_rasterization

    def draw(self, renderer):

                             

        if renderer is not None:

            self._renderer = renderer

        if not self.get_visible() or not self._check_xy(renderer):

            return

                                                                     

                                                  

        self.update_positions(renderer)

        self.update_bbox_position_size(renderer)

        if self.arrow_patch is not None:                   

            if (self.arrow_patch.get_figure(root=False) is None and

                    (fig := self.get_figure(root=False)) is not None):

                self.arrow_patch.set_figure(fig)

            self.arrow_patch.draw(renderer)

                                                                     

                                                                           

        Text.draw(self, renderer)



    def get_window_extent(self, renderer=None):

                             

                                                                             

                                                             

        if not self.get_visible() or not self._check_xy(renderer):

            return Bbox.unit()

        if renderer is not None:

            self._renderer = renderer

        if self._renderer is None:

            self._renderer = self.get_figure(root=True)._get_renderer()

        if self._renderer is None:

            raise RuntimeError('Cannot get window extent without renderer')



        self.update_positions(self._renderer)



        text_bbox = Text.get_window_extent(self)

        bboxes = [text_bbox]



        if self.arrow_patch is not None:

            bboxes.append(self.arrow_patch.get_window_extent())



        return Bbox.union(bboxes)



    def get_tightbbox(self, renderer=None):

                             

        if not self._check_xy(renderer):

            return Bbox.null()

        return super().get_tightbbox(renderer)





_docstring.interpd.register(Annotation=Annotation.__init__.__doc__)

