



from contextlib import nullcontext



import matplotlib as mpl



from matplotlib._constrained_layout import do_constrained_layout

from matplotlib._tight_layout import (get_subplotspec_list,

                                      get_tight_layout_figure)





class LayoutEngine:

    

                                

    _adjust_compatible = None

    _colorbar_gridspec = None



    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._params = {}



    def set(self, **kwargs):

        

        raise NotImplementedError



    @property

    def colorbar_gridspec(self):

        

        if self._colorbar_gridspec is None:

            raise NotImplementedError

        return self._colorbar_gridspec



    @property

    def adjust_compatible(self):

        

        if self._adjust_compatible is None:

            raise NotImplementedError

        return self._adjust_compatible



    def get(self):

        

        return dict(self._params)



    def execute(self, fig):

        

                                         

        raise NotImplementedError





class PlaceHolderLayoutEngine(LayoutEngine):

    

    def __init__(self, adjust_compatible, colorbar_gridspec, **kwargs):

        self._adjust_compatible = adjust_compatible

        self._colorbar_gridspec = colorbar_gridspec

        super().__init__(**kwargs)



    def execute(self, fig):

        

        return





class TightLayoutEngine(LayoutEngine):

    

    _adjust_compatible = True

    _colorbar_gridspec = True



    def __init__(self, *, pad=1.08, h_pad=None, w_pad=None,

                 rect=(0, 0, 1, 1), **kwargs):

        

        super().__init__(**kwargs)

        for td in ['pad', 'h_pad', 'w_pad', 'rect']:

                                                               

            self._params[td] = None

        self.set(pad=pad, h_pad=h_pad, w_pad=w_pad, rect=rect)



    def execute(self, fig):

        

        info = self._params

        renderer = fig._get_renderer()

        with getattr(renderer, "_draw_disabled", nullcontext)():

            kwargs = get_tight_layout_figure(

                fig, fig.axes, get_subplotspec_list(fig.axes), renderer,

                pad=info['pad'], h_pad=info['h_pad'], w_pad=info['w_pad'],

                rect=info['rect'])

        if kwargs:

            fig.subplots_adjust(**kwargs)



    def set(self, *, pad=None, w_pad=None, h_pad=None, rect=None):

        

        for td in self.set.__kwdefaults__:

            if locals()[td] is not None:

                self._params[td] = locals()[td]





class ConstrainedLayoutEngine(LayoutEngine):

    



    _adjust_compatible = False

    _colorbar_gridspec = False



    def __init__(self, *, h_pad=None, w_pad=None,

                 hspace=None, wspace=None, rect=(0, 0, 1, 1),

                 compress=False, **kwargs):

        

        super().__init__(**kwargs)

                           

        self.set(w_pad=mpl.rcParams['figure.constrained_layout.w_pad'],

                 h_pad=mpl.rcParams['figure.constrained_layout.h_pad'],

                 wspace=mpl.rcParams['figure.constrained_layout.wspace'],

                 hspace=mpl.rcParams['figure.constrained_layout.hspace'],

                 rect=(0, 0, 1, 1))

                                                                 

        self.set(w_pad=w_pad, h_pad=h_pad, wspace=wspace, hspace=hspace,

                 rect=rect)

        self._compress = compress



    def execute(self, fig):

        

        width, height = fig.get_size_inches()

                                                                 

        w_pad = self._params['w_pad'] / width

        h_pad = self._params['h_pad'] / height



        return do_constrained_layout(fig, w_pad=w_pad, h_pad=h_pad,

                                     wspace=self._params['wspace'],

                                     hspace=self._params['hspace'],

                                     rect=self._params['rect'],

                                     compress=self._compress)



    def set(self, *, h_pad=None, w_pad=None,

            hspace=None, wspace=None, rect=None):

        

        for td in self.set.__kwdefaults__:

            if locals()[td] is not None:

                self._params[td] = locals()[td]

