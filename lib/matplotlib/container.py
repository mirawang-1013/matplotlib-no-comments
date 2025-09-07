from matplotlib import cbook

from matplotlib.artist import Artist





class Container(tuple):

    



    def __repr__(self):

        return f"<{type(self).__name__} object of {len(self)} artists>"



    def __new__(cls, *args, **kwargs):

        return tuple.__new__(cls, args[0])



    def __init__(self, kl, label=None):

        self._callbacks = cbook.CallbackRegistry(signals=["pchanged"])

        self._remove_method = None

        self._label = str(label) if label is not None else None



    def remove(self):

        for c in cbook.flatten(

                self, scalarp=lambda x: isinstance(x, Artist)):

            if c is not None:

                c.remove()

        if self._remove_method:

            self._remove_method(self)



    def get_children(self):

        return [child for child in cbook.flatten(self) if child is not None]



    get_label = Artist.get_label

    set_label = Artist.set_label

    add_callback = Artist.add_callback

    remove_callback = Artist.remove_callback

    pchanged = Artist.pchanged





class BarContainer(Container):

    



    def __init__(self, patches, errorbar=None, *, datavalues=None,

                 orientation=None, **kwargs):

        self.patches = patches

        self.errorbar = errorbar

        self.datavalues = datavalues

        self.orientation = orientation

        super().__init__(patches, **kwargs)



    @property

    def bottoms(self):

        

        if self.orientation == 'vertical':

            return [p.get_y() for p in self.patches]

        elif self.orientation == 'horizontal':

            return [p.get_x() for p in self.patches]

        else:

            raise ValueError("orientation must be 'vertical' or 'horizontal'.")



    @property

    def tops(self):

        

        if self.orientation == 'vertical':

            return [p.get_y() + p.get_height() for p in self.patches]

        elif self.orientation == 'horizontal':

            return [p.get_x() + p.get_width() for p in self.patches]

        else:

            raise ValueError("orientation must be 'vertical' or 'horizontal'.")



    @property

    def position_centers(self):

        

        if self.orientation == 'vertical':

            return [p.get_x() + p.get_width() / 2 for p in self.patches]

        elif self.orientation == 'horizontal':

            return [p.get_y() + p.get_height() / 2 for p in self.patches]

        else:

            raise ValueError("orientation must be 'vertical' or 'horizontal'.")





class ErrorbarContainer(Container):

    



    def __init__(self, lines, has_xerr=False, has_yerr=False, **kwargs):

        self.lines = lines

        self.has_xerr = has_xerr

        self.has_yerr = has_yerr

        super().__init__(lines, **kwargs)





class StemContainer(Container):

    

    def __init__(self, markerline_stemlines_baseline, **kwargs):

        

        markerline, stemlines, baseline = markerline_stemlines_baseline

        self.markerline = markerline

        self.stemlines = stemlines

        self.baseline = baseline

        super().__init__(markerline_stemlines_baseline, **kwargs)

