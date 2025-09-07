from numbers import Number

import functools

from types import MethodType



import numpy as np



from matplotlib import _api, cbook

from matplotlib.gridspec import SubplotSpec



from .axes_divider import Size, SubplotDivider, Divider

from .mpl_axes import Axes, SimpleAxisArtist





class CbarAxesBase:

    def __init__(self, *args, orientation, **kwargs):

        self.orientation = orientation

        super().__init__(*args, **kwargs)



    def colorbar(self, mappable, **kwargs):

        return self.get_figure(root=False).colorbar(

            mappable, cax=self, location=self.orientation, **kwargs)





_cbaraxes_class_factory = cbook._make_class_factory(CbarAxesBase, "Cbar{}")





class Grid:

    



    _defaultAxesClass = Axes



    @_api.rename_parameter("3.11", "ngrids", "n_axes")

    def __init__(self, fig,

                 rect,

                 nrows_ncols,

                 n_axes=None,

                 direction="row",

                 axes_pad=0.02,

                 *,

                 share_all=False,

                 share_x=True,

                 share_y=True,

                 label_mode="L",

                 axes_class=None,

                 aspect=False,

                 ):

        

        self._nrows, self._ncols = nrows_ncols



        if n_axes is None:

            n_axes = self._nrows * self._ncols

        else:

            if not 0 < n_axes <= self._nrows * self._ncols:

                raise ValueError(

                    "n_axes must be positive and not larger than nrows*ncols")



        self._horiz_pad_size, self._vert_pad_size = map(

            Size.Fixed, np.broadcast_to(axes_pad, 2))



        _api.check_in_list(["column", "row"], direction=direction)

        self._direction = direction



        if axes_class is None:

            axes_class = self._defaultAxesClass

        elif isinstance(axes_class, (list, tuple)):

            cls, kwargs = axes_class

            axes_class = functools.partial(cls, **kwargs)



        kw = dict(horizontal=[], vertical=[], aspect=aspect)

        if isinstance(rect, (Number, SubplotSpec)):

            self._divider = SubplotDivider(fig, rect, **kw)

        elif len(rect) == 3:

            self._divider = SubplotDivider(fig, *rect, **kw)

        elif len(rect) == 4:

            self._divider = Divider(fig, rect, **kw)

        else:

            raise TypeError("Incorrect rect format")



        rect = self._divider.get_position()



        axes_array = np.full((self._nrows, self._ncols), None, dtype=object)

        for i in range(n_axes):

            col, row = self._get_col_row(i)

            if share_all:

                sharex = sharey = axes_array[0, 0]

            else:

                sharex = axes_array[0, col] if share_x else None

                sharey = axes_array[row, 0] if share_y else None

            axes_array[row, col] = axes_class(

                fig, rect, sharex=sharex, sharey=sharey)

        self.axes_all = axes_array.ravel(

            order="C" if self._direction == "row" else "F").tolist()[:n_axes]

        self.axes_row = [[ax for ax in row if ax] for row in axes_array]

        self.axes_column = [[ax for ax in col if ax] for col in axes_array.T]

        self.axes_llc = self.axes_column[0][-1]



        self._init_locators()



        for ax in self.axes_all:

            fig.add_axes(ax)



        self.set_label_mode(label_mode)



    def _init_locators(self):

        self._divider.set_horizontal(

            [Size.Scaled(1), self._horiz_pad_size] * (self._ncols-1) + [Size.Scaled(1)])

        self._divider.set_vertical(

            [Size.Scaled(1), self._vert_pad_size] * (self._nrows-1) + [Size.Scaled(1)])

        for i in range(self.n_axes):

            col, row = self._get_col_row(i)

            self.axes_all[i].set_axes_locator(

                self._divider.new_locator(nx=2 * col, ny=2 * (self._nrows - 1 - row)))



    def _get_col_row(self, n):

        if self._direction == "column":

            col, row = divmod(n, self._nrows)

        else:

            row, col = divmod(n, self._ncols)



        return col, row



    n_axes = property(lambda self: len(self.axes_all))

    ngrids = _api.deprecated(property(lambda self: len(self.axes_all)))



                                                      

    def __len__(self):

        return len(self.axes_all)



    def __getitem__(self, i):

        return self.axes_all[i]



    def get_geometry(self):

        

        return self._nrows, self._ncols



    def set_axes_pad(self, axes_pad):

        

        self._horiz_pad_size.fixed_size = axes_pad[0]

        self._vert_pad_size.fixed_size = axes_pad[1]



    def get_axes_pad(self):

        

        return (self._horiz_pad_size.fixed_size,

                self._vert_pad_size.fixed_size)



    def set_aspect(self, aspect):

        

        self._divider.set_aspect(aspect)



    def get_aspect(self):

        

        return self._divider.get_aspect()



    def set_label_mode(self, mode):

        

        _api.check_in_list(["all", "L", "1", "keep"], mode=mode)

        if mode == "keep":

            return

        for i, j in np.ndindex(self._nrows, self._ncols):

            try:

                ax = self.axes_row[i][j]

            except IndexError:

                continue

            if isinstance(ax.axis, MethodType):

                bottom_axis = SimpleAxisArtist(ax.xaxis, 1, ax.spines["bottom"])

                left_axis = SimpleAxisArtist(ax.yaxis, 1, ax.spines["left"])

            else:

                bottom_axis = ax.axis["bottom"]

                left_axis = ax.axis["left"]

            display_at_bottom = (i == self._nrows - 1 if mode == "L" else

                                 i == self._nrows - 1 and j == 0 if mode == "1" else

                                 True)                    

            display_at_left = (j == 0 if mode == "L" else

                               i == self._nrows - 1 and j == 0 if mode == "1" else

                               True)                    

            bottom_axis.toggle(ticklabels=display_at_bottom, label=display_at_bottom)

            left_axis.toggle(ticklabels=display_at_left, label=display_at_left)



    def get_divider(self):

        return self._divider



    def set_axes_locator(self, locator):

        self._divider.set_locator(locator)



    def get_axes_locator(self):

        return self._divider.get_locator()





class ImageGrid(Grid):

    



    def __init__(self, fig,

                 rect,

                 nrows_ncols,

                 n_axes=None,

                 direction="row",

                 axes_pad=0.02,

                 *,

                 share_all=False,

                 aspect=True,

                 label_mode="L",

                 cbar_mode=None,

                 cbar_location="right",

                 cbar_pad=None,

                 cbar_size="5%",

                 cbar_set_cax=True,

                 axes_class=None,

                 ):

        

        _api.check_in_list(["each", "single", "edge", None],

                           cbar_mode=cbar_mode)

        _api.check_in_list(["left", "right", "bottom", "top"],

                           cbar_location=cbar_location)

        self._colorbar_mode = cbar_mode

        self._colorbar_location = cbar_location

        self._colorbar_pad = cbar_pad

        self._colorbar_size = cbar_size

                                                            



        super().__init__(

            fig, rect, nrows_ncols, n_axes,

            direction=direction, axes_pad=axes_pad,

            share_all=share_all, share_x=True, share_y=True, aspect=aspect,

            label_mode=label_mode, axes_class=axes_class)



        for ax in self.cbar_axes:

            fig.add_axes(ax)



        if cbar_set_cax:

            if self._colorbar_mode == "single":

                for ax in self.axes_all:

                    ax.cax = self.cbar_axes[0]

            elif self._colorbar_mode == "edge":

                for index, ax in enumerate(self.axes_all):

                    col, row = self._get_col_row(index)

                    if self._colorbar_location in ("left", "right"):

                        ax.cax = self.cbar_axes[row]

                    else:

                        ax.cax = self.cbar_axes[col]

            else:

                for ax, cax in zip(self.axes_all, self.cbar_axes):

                    ax.cax = cax



    def _init_locators(self):

                                                                             



        if self._colorbar_pad is None:

                                                 

            if self._colorbar_location in ("left", "right"):

                self._colorbar_pad = self._horiz_pad_size.fixed_size

            else:

                self._colorbar_pad = self._vert_pad_size.fixed_size

        self.cbar_axes = [

            _cbaraxes_class_factory(self._defaultAxesClass)(

                self.axes_all[0].get_figure(root=False), self._divider.get_position(),

                orientation=self._colorbar_location)

            for _ in range(self.n_axes)]



        cb_mode = self._colorbar_mode

        cb_location = self._colorbar_location



        h = []

        v = []



        h_ax_pos = []

        h_cb_pos = []

        if cb_mode == "single" and cb_location in ("left", "bottom"):

            if cb_location == "left":

                sz = self._nrows * Size.AxesX(self.axes_llc)

                h.append(Size.from_any(self._colorbar_size, sz))

                h.append(Size.from_any(self._colorbar_pad, sz))

                locator = self._divider.new_locator(nx=0, ny=0, ny1=-1)

            elif cb_location == "bottom":

                sz = self._ncols * Size.AxesY(self.axes_llc)

                v.append(Size.from_any(self._colorbar_size, sz))

                v.append(Size.from_any(self._colorbar_pad, sz))

                locator = self._divider.new_locator(nx=0, nx1=-1, ny=0)

            for i in range(self.n_axes):

                self.cbar_axes[i].set_visible(False)

            self.cbar_axes[0].set_axes_locator(locator)

            self.cbar_axes[0].set_visible(True)



        for col, ax in enumerate(self.axes_row[0]):

            if col != 0:

                h.append(self._horiz_pad_size)



            if ax:

                sz = Size.AxesX(ax, aspect="axes", ref_ax=self.axes_all[0])

            else:

                sz = Size.AxesX(self.axes_all[0],

                                aspect="axes", ref_ax=self.axes_all[0])



            if (cb_location == "left"

                    and (cb_mode == "each"

                         or (cb_mode == "edge" and col == 0))):

                h_cb_pos.append(len(h))

                h.append(Size.from_any(self._colorbar_size, sz))

                h.append(Size.from_any(self._colorbar_pad, sz))



            h_ax_pos.append(len(h))

            h.append(sz)



            if (cb_location == "right"

                    and (cb_mode == "each"

                         or (cb_mode == "edge" and col == self._ncols - 1))):

                h.append(Size.from_any(self._colorbar_pad, sz))

                h_cb_pos.append(len(h))

                h.append(Size.from_any(self._colorbar_size, sz))



        v_ax_pos = []

        v_cb_pos = []

        for row, ax in enumerate(self.axes_column[0][::-1]):

            if row != 0:

                v.append(self._vert_pad_size)



            if ax:

                sz = Size.AxesY(ax, aspect="axes", ref_ax=self.axes_all[0])

            else:

                sz = Size.AxesY(self.axes_all[0],

                                aspect="axes", ref_ax=self.axes_all[0])



            if (cb_location == "bottom"

                    and (cb_mode == "each"

                         or (cb_mode == "edge" and row == 0))):

                v_cb_pos.append(len(v))

                v.append(Size.from_any(self._colorbar_size, sz))

                v.append(Size.from_any(self._colorbar_pad, sz))



            v_ax_pos.append(len(v))

            v.append(sz)



            if (cb_location == "top"

                    and (cb_mode == "each"

                         or (cb_mode == "edge" and row == self._nrows - 1))):

                v.append(Size.from_any(self._colorbar_pad, sz))

                v_cb_pos.append(len(v))

                v.append(Size.from_any(self._colorbar_size, sz))



        for i in range(self.n_axes):

            col, row = self._get_col_row(i)

            locator = self._divider.new_locator(nx=h_ax_pos[col],

                                                ny=v_ax_pos[self._nrows-1-row])

            self.axes_all[i].set_axes_locator(locator)



            if cb_mode == "each":

                if cb_location in ("right", "left"):

                    locator = self._divider.new_locator(

                        nx=h_cb_pos[col], ny=v_ax_pos[self._nrows - 1 - row])



                elif cb_location in ("top", "bottom"):

                    locator = self._divider.new_locator(

                        nx=h_ax_pos[col], ny=v_cb_pos[self._nrows - 1 - row])



                self.cbar_axes[i].set_axes_locator(locator)

            elif cb_mode == "edge":

                if (cb_location == "left" and col == 0

                        or cb_location == "right" and col == self._ncols - 1):

                    locator = self._divider.new_locator(

                        nx=h_cb_pos[0], ny=v_ax_pos[self._nrows - 1 - row])

                    self.cbar_axes[row].set_axes_locator(locator)

                elif (cb_location == "bottom" and row == self._nrows - 1

                      or cb_location == "top" and row == 0):

                    locator = self._divider.new_locator(nx=h_ax_pos[col],

                                                        ny=v_cb_pos[0])

                    self.cbar_axes[col].set_axes_locator(locator)



        if cb_mode == "single":

            if cb_location == "right":

                sz = self._nrows * Size.AxesX(self.axes_llc)

                h.append(Size.from_any(self._colorbar_pad, sz))

                h.append(Size.from_any(self._colorbar_size, sz))

                locator = self._divider.new_locator(nx=-2, ny=0, ny1=-1)

            elif cb_location == "top":

                sz = self._ncols * Size.AxesY(self.axes_llc)

                v.append(Size.from_any(self._colorbar_pad, sz))

                v.append(Size.from_any(self._colorbar_size, sz))

                locator = self._divider.new_locator(nx=0, nx1=-1, ny=-2)

            if cb_location in ("right", "top"):

                for i in range(self.n_axes):

                    self.cbar_axes[i].set_visible(False)

                self.cbar_axes[0].set_axes_locator(locator)

                self.cbar_axes[0].set_visible(True)

        elif cb_mode == "each":

            for i in range(self.n_axes):

                self.cbar_axes[i].set_visible(True)

        elif cb_mode == "edge":

            if cb_location in ("right", "left"):

                count = self._nrows

            else:

                count = self._ncols

            for i in range(count):

                self.cbar_axes[i].set_visible(True)

            for j in range(i + 1, self.n_axes):

                self.cbar_axes[j].set_visible(False)

        else:

            for i in range(self.n_axes):

                self.cbar_axes[i].set_visible(False)

                self.cbar_axes[i].set_position([1., 1., 0.001, 0.001],

                                               which="active")



        self._divider.set_horizontal(h)

        self._divider.set_vertical(v)





AxesGrid = ImageGrid

