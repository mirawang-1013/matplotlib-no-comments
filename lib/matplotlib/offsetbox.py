



import functools



import numpy as np



import matplotlib as mpl

from matplotlib import _api, _docstring

import matplotlib.artist as martist

import matplotlib.path as mpath

import matplotlib.text as mtext

import matplotlib.transforms as mtransforms

from matplotlib.font_manager import FontProperties

from matplotlib.image import BboxImage

from matplotlib.patches import (

    FancyBboxPatch, FancyArrowPatch, bbox_artist as mbbox_artist)

from matplotlib.transforms import Bbox, BboxBase, TransformedBbox





DEBUG = False





def _compat_get_offset(meth):

    

    sigs = [lambda self, width, height, xdescent, ydescent, renderer: locals(),

            lambda self, bbox, renderer: locals()]



    @functools.wraps(meth)

    def get_offset(self, *args, **kwargs):

        params = _api.select_matching_signature(sigs, self, *args, **kwargs)

        bbox = (params["bbox"] if "bbox" in params else

                Bbox.from_bounds(-params["xdescent"], -params["ydescent"],

                                 params["width"], params["height"]))

        return meth(params["self"], bbox, params["renderer"])

    return get_offset





                   

def _bbox_artist(*args, **kwargs):

    if DEBUG:

        mbbox_artist(*args, **kwargs)





def _get_packed_offsets(widths, total, sep, mode="fixed"):

    

    _api.check_in_list(["fixed", "expand", "equal"], mode=mode)



    if mode == "fixed":

        offsets_ = np.cumsum([0] + [w + sep for w in widths])

        offsets = offsets_[:-1]

        if total is None:

            total = offsets_[-1] - sep

        return total, offsets



    elif mode == "expand":

                                                                   

                                                            

        if total is None:

            total = 1

        if len(widths) > 1:

            sep = (total - sum(widths)) / (len(widths) - 1)

        else:

            sep = 0

        offsets_ = np.cumsum([0] + [w + sep for w in widths])

        offsets = offsets_[:-1]

        return total, offsets



    elif mode == "equal":

        maxh = max(widths)

        if total is None:

            if sep is None:

                raise ValueError("total and sep cannot both be None when "

                                 "using layout mode 'equal'")

            total = (maxh + sep) * len(widths)

        else:

            sep = total / len(widths) - maxh

        offsets = (maxh + sep) * np.arange(len(widths))

        return total, offsets





def _get_aligned_offsets(yspans, height, align="baseline"):

    



    _api.check_in_list(

        ["baseline", "left", "top", "right", "bottom", "center"], align=align)

    if height is None:

        height = max(y1 - y0 for y0, y1 in yspans)



    if align == "baseline":

        yspan = (min(y0 for y0, y1 in yspans), max(y1 for y0, y1 in yspans))

        offsets = [0] * len(yspans)

    elif align in ["left", "bottom"]:

        yspan = (0, height)

        offsets = [-y0 for y0, y1 in yspans]

    elif align in ["right", "top"]:

        yspan = (0, height)

        offsets = [height - y1 for y0, y1 in yspans]

    elif align == "center":

        yspan = (0, height)

        offsets = [(height - (y1 - y0)) * .5 - y0 for y0, y1 in yspans]



    return yspan, offsets





class OffsetBox(martist.Artist):

    

    def __init__(self, **kwargs):

        super().__init__()

        self._internal_update(kwargs)

                                                                       

                                                                             

                            

        self.set_clip_on(False)

        self._children = []

        self._offset = (0, 0)



    def set_figure(self, fig):

        

        super().set_figure(fig)

        for c in self.get_children():

            c.set_figure(fig)



    @martist.Artist.axes.setter

    def axes(self, ax):

                                    

        martist.Artist.axes.fset(self, ax)

        for c in self.get_children():

            if c is not None:

                c.axes = ax



    def contains(self, mouseevent):

        

        if self._different_canvas(mouseevent):

            return False, {}

        for c in self.get_children():

            a, b = c.contains(mouseevent)

            if a:

                return a, b

        return False, {}



    def set_offset(self, xy):

        

        self._offset = xy

        self.stale = True



    @_compat_get_offset

    def get_offset(self, bbox, renderer):

        

        return (

            self._offset(bbox.width, bbox.height, -bbox.x0, -bbox.y0, renderer)

            if callable(self._offset)

            else self._offset)



    def set_width(self, width):

        

        self.width = width

        self.stale = True



    def set_height(self, height):

        

        self.height = height

        self.stale = True



    def get_visible_children(self):

        

        return [c for c in self._children if c.get_visible()]



    def get_children(self):

        

        return self._children



    def _get_bbox_and_child_offsets(self, renderer):

        

        raise NotImplementedError(

            "get_bbox_and_offsets must be overridden in derived classes")



    def get_bbox(self, renderer):

        

        bbox, offsets = self._get_bbox_and_child_offsets(renderer)

        return bbox



    def get_window_extent(self, renderer=None):

                             

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        bbox = self.get_bbox(renderer)

        try:                                                        

            px, py = self.get_offset(bbox, renderer)

        except TypeError:

            px, py = self.get_offset()

        return bbox.translated(px, py)



    def draw(self, renderer):

        

        bbox, offsets = self._get_bbox_and_child_offsets(renderer)

        px, py = self.get_offset(bbox, renderer)

        for c, (ox, oy) in zip(self.get_visible_children(), offsets):

            c.set_offset((px + ox, py + oy))

            c.draw(renderer)

        _bbox_artist(self, renderer, fill=False, props=dict(pad=0.))

        self.stale = False





class PackerBase(OffsetBox):

    def __init__(self, pad=0., sep=0., width=None, height=None,

                 align="baseline", mode="fixed", children=None):

        

        super().__init__()

        self.height = height

        self.width = width

        self.sep = sep

        self.pad = pad

        self.mode = mode

        self.align = align

        self._children = children





class VPacker(PackerBase):

    



    def _get_bbox_and_child_offsets(self, renderer):

                             

        dpicor = renderer.points_to_pixels(1.)

        pad = self.pad * dpicor

        sep = self.sep * dpicor



        if self.width is not None:

            for c in self.get_visible_children():

                if isinstance(c, PackerBase) and c.mode == "expand":

                    c.set_width(self.width)



        bboxes = [c.get_bbox(renderer) for c in self.get_visible_children()]

        (x0, x1), xoffsets = _get_aligned_offsets(

            [bbox.intervalx for bbox in bboxes], self.width, self.align)

        height, yoffsets = _get_packed_offsets(

            [bbox.height for bbox in bboxes], self.height, sep, self.mode)



        yoffsets = height - (yoffsets + [bbox.y1 for bbox in bboxes])

        ydescent = yoffsets[0]

        yoffsets = yoffsets - ydescent



        return (

            Bbox.from_bounds(x0, -ydescent, x1 - x0, height).padded(pad),

            [*zip(xoffsets, yoffsets)])





class HPacker(PackerBase):

    



    def _get_bbox_and_child_offsets(self, renderer):

                             

        dpicor = renderer.points_to_pixels(1.)

        pad = self.pad * dpicor

        sep = self.sep * dpicor



        bboxes = [c.get_bbox(renderer) for c in self.get_visible_children()]

        if not bboxes:

            return Bbox.from_bounds(0, 0, 0, 0).padded(pad), []



        (y0, y1), yoffsets = _get_aligned_offsets(

            [bbox.intervaly for bbox in bboxes], self.height, self.align)

        width, xoffsets = _get_packed_offsets(

            [bbox.width for bbox in bboxes], self.width, sep, self.mode)



        x0 = bboxes[0].x0

        xoffsets -= ([bbox.x0 for bbox in bboxes] - x0)



        return (Bbox.from_bounds(x0, y0, width, y1 - y0).padded(pad),

                [*zip(xoffsets, yoffsets)])





class PaddedBox(OffsetBox):

    



    def __init__(self, child, pad=0., *, draw_frame=False, patch_attrs=None):

        

        super().__init__()

        self.pad = pad

        self._children = [child]

        self.patch = FancyBboxPatch(

            xy=(0.0, 0.0), width=1., height=1.,

            facecolor='w', edgecolor='k',

            mutation_scale=1,                                   

            snap=True,

            visible=draw_frame,

            boxstyle="square,pad=0",

        )

        if patch_attrs is not None:

            self.patch.update(patch_attrs)



    def _get_bbox_and_child_offsets(self, renderer):

                              

        pad = self.pad * renderer.points_to_pixels(1.)

        return (self._children[0].get_bbox(renderer).padded(pad), [(0, 0)])



    def draw(self, renderer):

                             

        bbox, offsets = self._get_bbox_and_child_offsets(renderer)

        px, py = self.get_offset(bbox, renderer)

        for c, (ox, oy) in zip(self.get_visible_children(), offsets):

            c.set_offset((px + ox, py + oy))



        self.draw_frame(renderer)



        for c in self.get_visible_children():

            c.draw(renderer)



        self.stale = False



    def update_frame(self, bbox, fontsize=None):

        self.patch.set_bounds(bbox.bounds)

        if fontsize:

            self.patch.set_mutation_scale(fontsize)

        self.stale = True



    def draw_frame(self, renderer):

                                                    

        self.update_frame(self.get_window_extent(renderer))

        self.patch.draw(renderer)





class DrawingArea(OffsetBox):

    



    def __init__(self, width, height, xdescent=0., ydescent=0., clip=False):

        

        super().__init__()

        self.width = width

        self.height = height

        self.xdescent = xdescent

        self.ydescent = ydescent

        self._clip_children = clip

        self.offset_transform = mtransforms.Affine2D()

        self.dpi_transform = mtransforms.Affine2D()



    @property

    def clip_children(self):

        

        return self._clip_children



    @clip_children.setter

    def clip_children(self, val):

        self._clip_children = bool(val)

        self.stale = True



    def get_transform(self):

        

        return self.dpi_transform + self.offset_transform



    def set_transform(self, t):

        



    def set_offset(self, xy):

        

        self._offset = xy

        self.offset_transform.clear()

        self.offset_transform.translate(xy[0], xy[1])

        self.stale = True



    def get_offset(self):

        

        return self._offset



    def get_bbox(self, renderer):

                             

        dpi_cor = renderer.points_to_pixels(1.)

        return Bbox.from_bounds(

            -self.xdescent * dpi_cor, -self.ydescent * dpi_cor,

            self.width * dpi_cor, self.height * dpi_cor)



    def add_artist(self, a):

        

        self._children.append(a)

        if not a.is_transform_set():

            a.set_transform(self.get_transform())

        if self.axes is not None:

            a.axes = self.axes

        fig = self.get_figure(root=False)

        if fig is not None:

            a.set_figure(fig)



    def draw(self, renderer):

                             



        dpi_cor = renderer.points_to_pixels(1.)

        self.dpi_transform.clear()

        self.dpi_transform.scale(dpi_cor)



                                                       

                                                     

                                    

        tpath = mtransforms.TransformedPath(

            mpath.Path([[0, 0], [0, self.height],

                        [self.width, self.height],

                        [self.width, 0]]),

            self.get_transform())

        for c in self._children:

            if self._clip_children and not (c.clipbox or c._clippath):

                c.set_clip_path(tpath)

            c.draw(renderer)



        _bbox_artist(self, renderer, fill=False, props=dict(pad=0.))

        self.stale = False





class TextArea(OffsetBox):

    



    def __init__(self, s,

                 *,

                 textprops=None,

                 multilinebaseline=False,

                 ):

        

        if textprops is None:

            textprops = {}

        self._text = mtext.Text(0, 0, s, **textprops)

        super().__init__()

        self._children = [self._text]

        self.offset_transform = mtransforms.Affine2D()

        self._baseline_transform = mtransforms.Affine2D()

        self._text.set_transform(self.offset_transform +

                                 self._baseline_transform)

        self._multilinebaseline = multilinebaseline



    def set_text(self, s):

        

        self._text.set_text(s)

        self.stale = True



    def get_text(self):

        

        return self._text.get_text()



    def set_multilinebaseline(self, t):

        

        self._multilinebaseline = t

        self.stale = True



    def get_multilinebaseline(self):

        

        return self._multilinebaseline



    def set_transform(self, t):

        



    def set_offset(self, xy):

        

        self._offset = xy

        self.offset_transform.clear()

        self.offset_transform.translate(xy[0], xy[1])

        self.stale = True



    def get_offset(self):

        

        return self._offset



    def get_bbox(self, renderer):

        _, h_, d_ = mtext._get_text_metrics_with_cache(

            renderer, "lp", self._text._fontproperties,

            ismath="TeX" if self._text.get_usetex() else False,

            dpi=self.get_figure(root=True).dpi)



        bbox, info, yd = self._text._get_layout(renderer)

        w, h = bbox.size



        self._baseline_transform.clear()



        if len(info) > 1 and self._multilinebaseline:

            yd_new = 0.5 * h - 0.5 * (h_ - d_)

            self._baseline_transform.translate(0, yd - yd_new)

            yd = yd_new

        else:               

            h_d = max(h_ - d_, h - yd)

            h = h_d + yd



        ha = self._text.get_horizontalalignment()

        x0 = {"left": 0, "center": -w / 2, "right": -w}[ha]



        return Bbox.from_bounds(x0, -yd, w, h)



    def draw(self, renderer):

                             

        self._text.draw(renderer)

        _bbox_artist(self, renderer, fill=False, props=dict(pad=0.))

        self.stale = False





class AuxTransformBox(OffsetBox):

    

    def __init__(self, aux_transform):

        self.aux_transform = aux_transform

        super().__init__()

        self.offset_transform = mtransforms.Affine2D()

                                                                            

                                                        

        self.ref_offset_transform = mtransforms.Affine2D()



    def add_artist(self, a):

        

        self._children.append(a)

        a.set_transform(self.get_transform())

        self.stale = True



    def get_transform(self):

        

        return (self.aux_transform

                + self.ref_offset_transform

                + self.offset_transform)



    def set_transform(self, t):

        



    def set_offset(self, xy):

        

        self._offset = xy

        self.offset_transform.clear()

        self.offset_transform.translate(xy[0], xy[1])

        self.stale = True



    def get_offset(self):

        

        return self._offset



    def get_bbox(self, renderer):

                                     

        _off = self.offset_transform.get_matrix()                        

        self.ref_offset_transform.clear()

        self.offset_transform.clear()

                              

        bboxes = [c.get_window_extent(renderer) for c in self._children]

        ub = Bbox.union(bboxes)

                                     

        self.ref_offset_transform.translate(-ub.x0, -ub.y0)

                                  

        self.offset_transform.set_matrix(_off)

        return Bbox.from_bounds(0, 0, ub.width, ub.height)



    def draw(self, renderer):

                             

        for c in self._children:

            c.draw(renderer)

        _bbox_artist(self, renderer, fill=False, props=dict(pad=0.))

        self.stale = False





class AnchoredOffsetbox(OffsetBox):

    

    zorder = 5                        



                    

    codes = {'upper right': 1,

             'upper left': 2,

             'lower left': 3,

             'lower right': 4,

             'right': 5,

             'center left': 6,

             'center right': 7,

             'lower center': 8,

             'upper center': 9,

             'center': 10,

             }



    def __init__(self, loc, *,

                 pad=0.4, borderpad=0.5,

                 child=None, prop=None, frameon=True,

                 bbox_to_anchor=None,

                 bbox_transform=None,

                 **kwargs):

        

        super().__init__(**kwargs)



        self.set_bbox_to_anchor(bbox_to_anchor, bbox_transform)

        self.set_child(child)



        if isinstance(loc, str):

            loc = _api.check_getitem(self.codes, loc=loc)



        self.loc = loc

        self.borderpad = borderpad

        self.pad = pad



        if prop is None:

            self.prop = FontProperties(size=mpl.rcParams["legend.fontsize"])

        else:

            self.prop = FontProperties._from_any(prop)

            if isinstance(prop, dict) and "size" not in prop:

                self.prop.set_size(mpl.rcParams["legend.fontsize"])



        self.patch = FancyBboxPatch(

            xy=(0.0, 0.0), width=1., height=1.,

            facecolor='w', edgecolor='k',

            mutation_scale=self.prop.get_size_in_points(),

            snap=True,

            visible=frameon,

            boxstyle="square,pad=0",

        )



    def set_child(self, child):

        

        self._child = child

        if child is not None:

            child.axes = self.axes

        self.stale = True



    def get_child(self):

        

        return self._child



    def get_children(self):

        

        return [self._child]



    def get_bbox(self, renderer):

                             

        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())

        pad = self.pad * fontsize

        return self.get_child().get_bbox(renderer).padded(pad)



    def get_bbox_to_anchor(self):

        

        if self._bbox_to_anchor is None:

            return self.axes.bbox

        else:

            transform = self._bbox_to_anchor_transform

            if transform is None:

                return self._bbox_to_anchor

            else:

                return TransformedBbox(self._bbox_to_anchor, transform)



    def set_bbox_to_anchor(self, bbox, transform=None):

        

        if bbox is None or isinstance(bbox, BboxBase):

            self._bbox_to_anchor = bbox

        else:

            try:

                l = len(bbox)

            except TypeError as err:

                raise ValueError(f"Invalid bbox: {bbox}") from err



            if l == 2:

                bbox = [bbox[0], bbox[1], 0, 0]



            self._bbox_to_anchor = Bbox.from_bounds(*bbox)



        self._bbox_to_anchor_transform = transform

        self.stale = True



    @_compat_get_offset

    def get_offset(self, bbox, renderer):

                             

        fontsize_in_pixels = renderer.points_to_pixels(self.prop.get_size_in_points())

        try:

            borderpad_x, borderpad_y = self.borderpad

        except TypeError:

            borderpad_x = self.borderpad

            borderpad_y = self.borderpad

        pad_x_pixels = borderpad_x * fontsize_in_pixels

        pad_y_pixels = borderpad_y * fontsize_in_pixels

        bbox_to_anchor = self.get_bbox_to_anchor()

        x0, y0 = _get_anchored_bbox(

            self.loc,

            Bbox.from_bounds(0, 0, bbox.width, bbox.height),

            bbox_to_anchor,

            pad_x_pixels,

            pad_y_pixels

        )

        return x0 - bbox.x0, y0 - bbox.y0



    def update_frame(self, bbox, fontsize=None):

        self.patch.set_bounds(bbox.bounds)

        if fontsize:

            self.patch.set_mutation_scale(fontsize)



    def draw(self, renderer):

                             

        if not self.get_visible():

            return



                                                    

        bbox = self.get_window_extent(renderer)

        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())

        self.update_frame(bbox, fontsize)

        self.patch.draw(renderer)



        px, py = self.get_offset(self.get_bbox(renderer), renderer)

        self.get_child().set_offset((px, py))

        self.get_child().draw(renderer)

        self.stale = False





def _get_anchored_bbox(loc, bbox, parentbbox, pad_x, pad_y):

    

                                                                       

                                                                   

    c = [None, "NE", "NW", "SW", "SE", "E", "W", "E", "S", "N", "C"][loc]

    container = parentbbox.padded(-pad_x, -pad_y)

    return bbox.anchored(c, container=container).p0





class AnchoredText(AnchoredOffsetbox):

    



    def __init__(self, s, loc, *, pad=0.4, borderpad=0.5, prop=None, **kwargs):

        



        if prop is None:

            prop = {}

        badkwargs = {'va', 'verticalalignment'}

        if badkwargs & set(prop):

            raise ValueError(

                'Mixing verticalalignment with AnchoredText is not supported.')



        self.txt = TextArea(s, textprops=prop)

        fp = self.txt._text.get_fontproperties()

        super().__init__(

            loc, pad=pad, borderpad=borderpad, child=self.txt, prop=fp,

            **kwargs)





class OffsetImage(OffsetBox):



    def __init__(self, arr, *,

                 zoom=1,

                 cmap=None,

                 norm=None,

                 interpolation=None,

                 origin=None,

                 filternorm=True,

                 filterrad=4.0,

                 resample=False,

                 dpi_cor=True,

                 **kwargs

                 ):



        super().__init__()

        self._dpi_cor = dpi_cor



        self.image = BboxImage(bbox=self.get_window_extent,

                               cmap=cmap,

                               norm=norm,

                               interpolation=interpolation,

                               origin=origin,

                               filternorm=filternorm,

                               filterrad=filterrad,

                               resample=resample,

                               **kwargs

                               )



        self._children = [self.image]



        self.set_zoom(zoom)

        self.set_data(arr)



    def set_data(self, arr):

        self._data = np.asarray(arr)

        self.image.set_data(self._data)

        self.stale = True



    def get_data(self):

        return self._data



    def set_zoom(self, zoom):

        self._zoom = zoom

        self.stale = True



    def get_zoom(self):

        return self._zoom



    def get_offset(self):

        

        return self._offset



    def get_children(self):

        return [self.image]



    def get_bbox(self, renderer):

        dpi_cor = renderer.points_to_pixels(1.) if self._dpi_cor else 1.

        zoom = self.get_zoom()

        data = self.get_data()

        ny, nx = data.shape[:2]

        w, h = dpi_cor * nx * zoom, dpi_cor * ny * zoom

        return Bbox.from_bounds(0, 0, w, h)



    def draw(self, renderer):

                             

        self.image.draw(renderer)

                                                                     

        self.stale = False





class AnnotationBbox(martist.Artist, mtext._AnnotationBase):

    



    zorder = 3



    def __str__(self):

        return f"AnnotationBbox({self.xy[0]:g},{self.xy[1]:g})"



    @_docstring.interpd

    def __init__(self, offsetbox, xy, xybox=None, xycoords='data', boxcoords=None, *,

                 frameon=True, pad=0.4,                            

                 annotation_clip=None,

                 box_alignment=(0.5, 0.5),

                 bboxprops=None,

                 arrowprops=None,

                 fontsize=None,

                 **kwargs):

        



        martist.Artist.__init__(self)

        mtext._AnnotationBase.__init__(

            self, xy, xycoords=xycoords, annotation_clip=annotation_clip)



        self.offsetbox = offsetbox

        self.arrowprops = arrowprops.copy() if arrowprops is not None else None

        self.set_fontsize(fontsize)

        self.xybox = xybox if xybox is not None else xy

        self.boxcoords = boxcoords if boxcoords is not None else xycoords

        self._box_alignment = box_alignment



        if arrowprops is not None:

            self._arrow_relpos = self.arrowprops.pop("relpos", (0.5, 0.5))

            self.arrow_patch = FancyArrowPatch((0, 0), (1, 1),

                                               **self.arrowprops)

        else:

            self._arrow_relpos = None

            self.arrow_patch = None



        self.patch = FancyBboxPatch(         

            xy=(0.0, 0.0), width=1., height=1.,

            facecolor='w', edgecolor='k',

            mutation_scale=self.prop.get_size_in_points(),

            snap=True,

            visible=frameon,

        )

        self.patch.set_boxstyle("square", pad=pad)

        if bboxprops:

            self.patch.set(**bboxprops)



        self._internal_update(kwargs)



    @property

    def xyann(self):

        return self.xybox



    @xyann.setter

    def xyann(self, xyann):

        self.xybox = xyann

        self.stale = True



    @property

    def anncoords(self):

        return self.boxcoords



    @anncoords.setter

    def anncoords(self, coords):

        self.boxcoords = coords

        self.stale = True



    def contains(self, mouseevent):

        if self._different_canvas(mouseevent):

            return False, {}

        if not self._check_xy(None):

            return False, {}

        return self.offsetbox.contains(mouseevent)

                                                                              



    def get_children(self):

        children = [self.offsetbox, self.patch]

        if self.arrow_patch:

            children.append(self.arrow_patch)

        return children



    def set_figure(self, fig):

        if self.arrow_patch is not None:

            self.arrow_patch.set_figure(fig)

        self.offsetbox.set_figure(fig)

        martist.Artist.set_figure(self, fig)



    def set_fontsize(self, s=None):

        

        s = mpl._val_or_rc(s, "legend.fontsize")

        self.prop = FontProperties(size=s)

        self.stale = True



    def get_fontsize(self):

        

        return self.prop.get_size_in_points()



    def get_window_extent(self, renderer=None):

                             

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        self.update_positions(renderer)

        return Bbox.union([child.get_window_extent(renderer)

                           for child in self.get_children()])



    def get_tightbbox(self, renderer=None):

                             

        if renderer is None:

            renderer = self.get_figure(root=True)._get_renderer()

        self.update_positions(renderer)

        return Bbox.union([child.get_tightbbox(renderer)

                           for child in self.get_children()])



    def update_positions(self, renderer):

        



        ox0, oy0 = self._get_xy(renderer, self.xybox, self.boxcoords)

        bbox = self.offsetbox.get_bbox(renderer)

        fw, fh = self._box_alignment

        self.offsetbox.set_offset(

            (ox0 - fw*bbox.width - bbox.x0, oy0 - fh*bbox.height - bbox.y0))



        bbox = self.offsetbox.get_window_extent(renderer)

        self.patch.set_bounds(bbox.bounds)



        mutation_scale = renderer.points_to_pixels(self.get_fontsize())

        self.patch.set_mutation_scale(mutation_scale)



        if self.arrowprops:

                                                                          



                                                                             

                                                   

            arrow_begin = bbox.p0 + bbox.size * self._arrow_relpos

            arrow_end = self._get_position_xy(renderer)

                                                                             

                                                                          

                                                                       

            self.arrow_patch.set_positions(arrow_begin, arrow_end)



            if "mutation_scale" in self.arrowprops:

                mutation_scale = renderer.points_to_pixels(

                    self.arrowprops["mutation_scale"])

                                                                        

            self.arrow_patch.set_mutation_scale(mutation_scale)



            patchA = self.arrowprops.get("patchA", self.patch)

            self.arrow_patch.set_patchA(patchA)



    def draw(self, renderer):

                             

        if not self.get_visible() or not self._check_xy(renderer):

            return

        renderer.open_group(self.__class__.__name__, gid=self.get_gid())

        self.update_positions(renderer)

        if self.arrow_patch is not None:

            if (self.arrow_patch.get_figure(root=False) is None and

                    (fig := self.get_figure(root=False)) is not None):

                self.arrow_patch.set_figure(fig)

            self.arrow_patch.draw(renderer)

        self.patch.draw(renderer)

        self.offsetbox.draw(renderer)

        renderer.close_group(self.__class__.__name__)

        self.stale = False





class DraggableBase:

    



    def __init__(self, ref_artist, use_blit=False):

        self.ref_artist = ref_artist

        if not ref_artist.pickable():

            ref_artist.set_picker(self._picker)

        self.got_artist = False

        self._use_blit = use_blit and self.canvas.supports_blit

        callbacks = self.canvas.callbacks

        self._disconnectors = [

            functools.partial(

                callbacks.disconnect, callbacks._connect_picklable(name, func))

            for name, func in [

                ("pick_event", self.on_pick),

                ("button_release_event", self.on_release),

                ("motion_notify_event", self.on_motion),

            ]

        ]



    @staticmethod

    def _picker(artist, mouseevent):

                                                                    

        if mouseevent.name == "scroll_event":

            return False, {}

        return artist.contains(mouseevent)



                                                             

    canvas = property(lambda self: self.ref_artist.get_figure(root=True).canvas)

    cids = property(lambda self: [

        disconnect.args[0] for disconnect in self._disconnectors[:2]])



    def on_motion(self, evt):

        if self._check_still_parented() and self.got_artist:

            dx = evt.x - self.mouse_x

            dy = evt.y - self.mouse_y

            self.update_offset(dx, dy)

            if self._use_blit:

                self.canvas.restore_region(self.background)

                self.ref_artist.draw(

                    self.ref_artist.get_figure(root=True)._get_renderer())

                self.canvas.blit()

            else:

                self.canvas.draw()



    def on_pick(self, evt):

        if self._check_still_parented():

            if evt.artist == self.ref_artist:

                self.mouse_x = evt.mouseevent.x

                self.mouse_y = evt.mouseevent.y

                self.save_offset()

                self.got_artist = True

            if self.got_artist and self._use_blit:

                self.ref_artist.set_animated(True)

                self.canvas.draw()

                fig = self.ref_artist.get_figure(root=False)

                self.background = self.canvas.copy_from_bbox(fig.bbox)

                self.ref_artist.draw(fig._get_renderer())

                self.canvas.blit()



    def on_release(self, event):

        if self._check_still_parented() and self.got_artist:

            self.finalize_offset()

            self.got_artist = False

            if self._use_blit:

                self.canvas.restore_region(self.background)

                self.ref_artist.draw(self.ref_artist.figure._get_renderer())

                self.canvas.blit()

                self.ref_artist.set_animated(False)



    def _check_still_parented(self):

        if self.ref_artist.get_figure(root=False) is None:

            self.disconnect()

            return False

        else:

            return True



    def disconnect(self):

        

        for disconnector in self._disconnectors:

            disconnector()



    def save_offset(self):

        pass



    def update_offset(self, dx, dy):

        pass



    def finalize_offset(self):

        pass





class DraggableOffsetBox(DraggableBase):

    def __init__(self, ref_artist, offsetbox, use_blit=False):

        super().__init__(ref_artist, use_blit=use_blit)

        self.offsetbox = offsetbox



    def save_offset(self):

        offsetbox = self.offsetbox

        renderer = offsetbox.get_figure(root=True)._get_renderer()

        offset = offsetbox.get_offset(offsetbox.get_bbox(renderer), renderer)

        self.offsetbox_x, self.offsetbox_y = offset

        self.offsetbox.set_offset(offset)



    def update_offset(self, dx, dy):

        loc_in_canvas = self.offsetbox_x + dx, self.offsetbox_y + dy

        self.offsetbox.set_offset(loc_in_canvas)



    def get_loc_in_canvas(self):

        offsetbox = self.offsetbox

        renderer = offsetbox.get_figure(root=True)._get_renderer()

        bbox = offsetbox.get_bbox(renderer)

        ox, oy = offsetbox._offset

        loc_in_canvas = (ox + bbox.x0, oy + bbox.y0)

        return loc_in_canvas





class DraggableAnnotation(DraggableBase):

    def __init__(self, annotation, use_blit=False):

        super().__init__(annotation, use_blit=use_blit)

        self.annotation = annotation



    def save_offset(self):

        ann = self.annotation

        self.ox, self.oy = ann.get_transform().transform(ann.xyann)



    def update_offset(self, dx, dy):

        ann = self.annotation

        ann.xyann = ann.get_transform().inverted().transform(

            (self.ox + dx, self.oy + dy))

