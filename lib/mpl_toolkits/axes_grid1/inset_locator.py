



from matplotlib import _api, _docstring

from matplotlib.offsetbox import AnchoredOffsetbox

from matplotlib.patches import Patch, Rectangle

from matplotlib.path import Path

from matplotlib.transforms import Bbox

from matplotlib.transforms import IdentityTransform, TransformedBbox



from . import axes_size as Size

from .parasite_axes import HostAxes





class AnchoredLocatorBase(AnchoredOffsetbox):

    def __init__(self, bbox_to_anchor, offsetbox, loc,

                 borderpad=0.5, bbox_transform=None):

        super().__init__(

            loc, pad=0., child=None, borderpad=borderpad,

            bbox_to_anchor=bbox_to_anchor, bbox_transform=bbox_transform

        )



    def draw(self, renderer):

        raise RuntimeError("No draw method should be called")



    def __call__(self, ax, renderer):

        fig = ax.get_figure(root=False)

        if renderer is None:

            renderer = fig._get_renderer()

        self.axes = ax

        bbox = self.get_window_extent(renderer)

        px, py = self.get_offset(bbox.width, bbox.height, 0, 0, renderer)

        bbox_canvas = Bbox.from_bounds(px, py, bbox.width, bbox.height)

        tr = fig.transSubfigure.inverted()

        return TransformedBbox(bbox_canvas, tr)





class AnchoredSizeLocator(AnchoredLocatorBase):

    def __init__(self, bbox_to_anchor, x_size, y_size, loc,

                 borderpad=0.5, bbox_transform=None):

        super().__init__(

            bbox_to_anchor, None, loc,

            borderpad=borderpad, bbox_transform=bbox_transform

        )



        self.x_size = Size.from_any(x_size)

        self.y_size = Size.from_any(y_size)



    def get_bbox(self, renderer):

        bbox = self.get_bbox_to_anchor()

        dpi = renderer.points_to_pixels(72.)



        r, a = self.x_size.get_size(renderer)

        width = bbox.width * r + a * dpi

        r, a = self.y_size.get_size(renderer)

        height = bbox.height * r + a * dpi



        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())

        pad = self.pad * fontsize



        return Bbox.from_bounds(0, 0, width, height).padded(pad)





class AnchoredZoomLocator(AnchoredLocatorBase):

    def __init__(self, parent_axes, zoom, loc,

                 borderpad=0.5,

                 bbox_to_anchor=None,

                 bbox_transform=None):

        self.parent_axes = parent_axes

        self.zoom = zoom

        if bbox_to_anchor is None:

            bbox_to_anchor = parent_axes.bbox

        super().__init__(

            bbox_to_anchor, None, loc, borderpad=borderpad,

            bbox_transform=bbox_transform)



    def get_bbox(self, renderer):

        bb = self.parent_axes.transData.transform_bbox(self.axes.viewLim)

        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())

        pad = self.pad * fontsize

        return (

            Bbox.from_bounds(

                0, 0, abs(bb.width * self.zoom), abs(bb.height * self.zoom))

            .padded(pad))





class BboxPatch(Patch):

    @_docstring.interpd

    def __init__(self, bbox, **kwargs):

        

        if "transform" in kwargs:

            raise ValueError("transform should not be set")



        kwargs["transform"] = IdentityTransform()

        super().__init__(**kwargs)

        self.bbox = bbox



    def get_path(self):

                             

        x0, y0, x1, y1 = self.bbox.extents

        return Path._create_closed([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])





class BboxConnector(Patch):

    @staticmethod

    def get_bbox_edge_pos(bbox, loc):

        

        x0, y0, x1, y1 = bbox.extents

        if loc == 1:

            return x1, y1

        elif loc == 2:

            return x0, y1

        elif loc == 3:

            return x0, y0

        elif loc == 4:

            return x1, y0



    @staticmethod

    def connect_bbox(bbox1, bbox2, loc1, loc2=None):

        

        if isinstance(bbox1, Rectangle):

            bbox1 = TransformedBbox(Bbox.unit(), bbox1.get_transform())

        if isinstance(bbox2, Rectangle):

            bbox2 = TransformedBbox(Bbox.unit(), bbox2.get_transform())

        if loc2 is None:

            loc2 = loc1

        x1, y1 = BboxConnector.get_bbox_edge_pos(bbox1, loc1)

        x2, y2 = BboxConnector.get_bbox_edge_pos(bbox2, loc2)

        return Path([[x1, y1], [x2, y2]])



    @_docstring.interpd

    def __init__(self, bbox1, bbox2, loc1, loc2=None, **kwargs):

        

        if "transform" in kwargs:

            raise ValueError("transform should not be set")



        kwargs["transform"] = IdentityTransform()

        kwargs.setdefault(

            "fill", bool({'fc', 'facecolor', 'color'}.intersection(kwargs)))

        super().__init__(**kwargs)

        self.bbox1 = bbox1

        self.bbox2 = bbox2

        self.loc1 = loc1

        self.loc2 = loc2



    def get_path(self):

                             

        return self.connect_bbox(self.bbox1, self.bbox2,

                                 self.loc1, self.loc2)





class BboxConnectorPatch(BboxConnector):

    @_docstring.interpd

    def __init__(self, bbox1, bbox2, loc1a, loc2a, loc1b, loc2b, **kwargs):

        

        if "transform" in kwargs:

            raise ValueError("transform should not be set")

        super().__init__(bbox1, bbox2, loc1a, loc2a, **kwargs)

        self.loc1b = loc1b

        self.loc2b = loc2b



    def get_path(self):

                             

        path1 = self.connect_bbox(self.bbox1, self.bbox2, self.loc1, self.loc2)

        path2 = self.connect_bbox(self.bbox2, self.bbox1,

                                  self.loc2b, self.loc1b)

        path_merged = [*path1.vertices, *path2.vertices, path1.vertices[0]]

        return Path(path_merged)





def _add_inset_axes(parent_axes, axes_class, axes_kwargs, axes_locator):

    

    if axes_class is None:

        axes_class = HostAxes

    if axes_kwargs is None:

        axes_kwargs = {}

    fig = parent_axes.get_figure(root=False)

    inset_axes = axes_class(

        fig, parent_axes.get_position(),

        **{"navigate": False, **axes_kwargs, "axes_locator": axes_locator})

    return fig.add_axes(inset_axes)





@_docstring.interpd

def inset_axes(parent_axes, width, height, loc='upper right',

               bbox_to_anchor=None, bbox_transform=None,

               axes_class=None, axes_kwargs=None,

               borderpad=0.5):

    



    if (bbox_transform in [parent_axes.transAxes,

                           parent_axes.get_figure(root=False).transFigure]

            and bbox_to_anchor is None):

        _api.warn_external("Using the axes or figure transform requires a "

                           "bounding box in the respective coordinates. "

                           "Using bbox_to_anchor=(0, 0, 1, 1) now.")

        bbox_to_anchor = (0, 0, 1, 1)

    if bbox_to_anchor is None:

        bbox_to_anchor = parent_axes.bbox

    if (isinstance(bbox_to_anchor, tuple) and

            (isinstance(width, str) or isinstance(height, str))):

        if len(bbox_to_anchor) != 4:

            raise ValueError("Using relative units for width or height "

                             "requires to provide a 4-tuple or a "

                             "`Bbox` instance to `bbox_to_anchor.")

    return _add_inset_axes(

        parent_axes, axes_class, axes_kwargs,

        AnchoredSizeLocator(

            bbox_to_anchor, width, height, loc=loc,

            bbox_transform=bbox_transform, borderpad=borderpad))





@_docstring.interpd

def zoomed_inset_axes(parent_axes, zoom, loc='upper right',

                      bbox_to_anchor=None, bbox_transform=None,

                      axes_class=None, axes_kwargs=None,

                      borderpad=0.5):

    



    return _add_inset_axes(

        parent_axes, axes_class, axes_kwargs,

        AnchoredZoomLocator(

            parent_axes, zoom=zoom, loc=loc,

            bbox_to_anchor=bbox_to_anchor, bbox_transform=bbox_transform,

            borderpad=borderpad))





class _TransformedBboxWithCallback(TransformedBbox):

    



    def __init__(self, *args, callback, **kwargs):

        super().__init__(*args, **kwargs)

        self._callback = callback



    def get_points(self):

        self._callback()

        return super().get_points()





@_docstring.interpd

def mark_inset(parent_axes, inset_axes, loc1, loc2, **kwargs):

    

    rect = _TransformedBboxWithCallback(

        inset_axes.viewLim, parent_axes.transData,

        callback=parent_axes._unstale_viewLim)



    kwargs.setdefault("fill", bool({'fc', 'facecolor', 'color'}.intersection(kwargs)))

    pp = BboxPatch(rect, **kwargs)

    parent_axes.add_patch(pp)



    p1 = BboxConnector(inset_axes.bbox, rect, loc1=loc1, **kwargs)

    inset_axes.add_patch(p1)

    p1.set_clip_on(False)

    p2 = BboxConnector(inset_axes.bbox, rect, loc1=loc2, **kwargs)

    inset_axes.add_patch(p2)

    p2.set_clip_on(False)



    return pp, p1, p2

