from matplotlib import transforms

from matplotlib.offsetbox import (AnchoredOffsetbox, AuxTransformBox,

                                  DrawingArea, TextArea, VPacker)

from matplotlib.patches import (Rectangle, ArrowStyle,

                                FancyArrowPatch, PathPatch)

from matplotlib.text import TextPath



__all__ = ['AnchoredDrawingArea', 'AnchoredAuxTransformBox',

           'AnchoredSizeBar', 'AnchoredDirectionArrows']





class AnchoredDrawingArea(AnchoredOffsetbox):

    def __init__(self, width, height, xdescent, ydescent,

                 loc, pad=0.4, borderpad=0.5, prop=None, frameon=True,

                 **kwargs):

        

        self.da = DrawingArea(width, height, xdescent, ydescent)

        self.drawing_area = self.da



        super().__init__(

            loc, pad=pad, borderpad=borderpad, child=self.da, prop=None,

            frameon=frameon, **kwargs

        )





class AnchoredAuxTransformBox(AnchoredOffsetbox):

    def __init__(self, transform, loc,

                 pad=0.4, borderpad=0.5, prop=None, frameon=True, **kwargs):

        

        self.drawing_area = AuxTransformBox(transform)



        super().__init__(loc, pad=pad, borderpad=borderpad,

                         child=self.drawing_area, prop=prop, frameon=frameon,

                         **kwargs)





class AnchoredSizeBar(AnchoredOffsetbox):

    def __init__(self, transform, size, label, loc,

                 pad=0.1, borderpad=0.1, sep=2,

                 frameon=True, size_vertical=0, color='black',

                 label_top=False, fontproperties=None, fill_bar=None,

                 **kwargs):

        

        if fill_bar is None:

            fill_bar = size_vertical > 0



        self.size_bar = AuxTransformBox(transform)

        self.size_bar.add_artist(Rectangle((0, 0), size, size_vertical,

                                           fill=fill_bar, facecolor=color,

                                           edgecolor=color))



        if fontproperties is None and 'prop' in kwargs:

            fontproperties = kwargs.pop('prop')



        if fontproperties is None:

            textprops = {'color': color}

        else:

            textprops = {'color': color, 'fontproperties': fontproperties}



        self.txt_label = TextArea(label, textprops=textprops)



        if label_top:

            _box_children = [self.txt_label, self.size_bar]

        else:

            _box_children = [self.size_bar, self.txt_label]



        self._box = VPacker(children=_box_children,

                            align="center",

                            pad=0, sep=sep)



        super().__init__(loc, pad=pad, borderpad=borderpad, child=self._box,

                         prop=fontproperties, frameon=frameon, **kwargs)





class AnchoredDirectionArrows(AnchoredOffsetbox):

    def __init__(self, transform, label_x, label_y, length=0.15,

                 fontsize=0.08, loc='upper left', angle=0, aspect_ratio=1,

                 pad=0.4, borderpad=0.4, frameon=False, color='w', alpha=1,

                 sep_x=0.01, sep_y=0, fontproperties=None, back_length=0.15,

                 head_width=10, head_length=15, tail_width=2,

                 text_props=None, arrow_props=None,

                 **kwargs):

        

        if arrow_props is None:

            arrow_props = {}



        if text_props is None:

            text_props = {}



        arrowstyle = ArrowStyle("Simple",

                                head_width=head_width,

                                head_length=head_length,

                                tail_width=tail_width)



        if fontproperties is None and 'prop' in kwargs:

            fontproperties = kwargs.pop('prop')



        if 'color' not in arrow_props:

            arrow_props['color'] = color



        if 'alpha' not in arrow_props:

            arrow_props['alpha'] = alpha



        if 'color' not in text_props:

            text_props['color'] = color



        if 'alpha' not in text_props:

            text_props['alpha'] = alpha



        t_start = transform

        t_end = t_start + transforms.Affine2D().rotate_deg(angle)



        self.box = AuxTransformBox(t_end)



        length_x = length

        length_y = length*aspect_ratio



        self.arrow_x = FancyArrowPatch(

                (0, back_length*length_y),

                (length_x, back_length*length_y),

                arrowstyle=arrowstyle,

                shrinkA=0.0,

                shrinkB=0.0,

                **arrow_props)



        self.arrow_y = FancyArrowPatch(

                (back_length*length_x, 0),

                (back_length*length_x, length_y),

                arrowstyle=arrowstyle,

                shrinkA=0.0,

                shrinkB=0.0,

                **arrow_props)



        self.box.add_artist(self.arrow_x)

        self.box.add_artist(self.arrow_y)



        text_path_x = TextPath((

            length_x+sep_x, back_length*length_y+sep_y), label_x,

            size=fontsize, prop=fontproperties)

        self.p_x = PathPatch(text_path_x, transform=t_start, **text_props)

        self.box.add_artist(self.p_x)



        text_path_y = TextPath((

            length_x*back_length+sep_x, length_y*(1-back_length)+sep_y),

            label_y, size=fontsize, prop=fontproperties)

        self.p_y = PathPatch(text_path_y, **text_props)

        self.box.add_artist(self.p_y)



        super().__init__(loc, pad=pad, borderpad=borderpad, child=self.box,

                         frameon=frameon, **kwargs)

