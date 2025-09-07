from matplotlib import _api, cbook

import matplotlib.artist as martist

import matplotlib.transforms as mtransforms

from matplotlib.transforms import Bbox

from .mpl_axes import Axes





class ParasiteAxesBase:



    def __init__(self, parent_axes, aux_transform=None,

                 *, viewlim_mode=None, **kwargs):

        self._parent_axes = parent_axes

        self.transAux = aux_transform

        self.set_viewlim_mode(viewlim_mode)

        kwargs["frameon"] = False

        super().__init__(parent_axes.get_figure(root=False),

                         parent_axes._position, **kwargs)



    def clear(self):

        super().clear()

        martist.setp(self.get_children(), visible=False)

        self._get_lines = self._parent_axes._get_lines

        self._parent_axes.callbacks._connect_picklable(

            "xlim_changed", self._sync_lims)

        self._parent_axes.callbacks._connect_picklable(

            "ylim_changed", self._sync_lims)



    def get_axes_locator(self):

        return self._parent_axes.get_axes_locator()



    def pick(self, mouseevent):

                                                                             

                                                                           

                                          

        super().pick(mouseevent)

                                                                              

                                                             

        for a in self.get_children():

            if (hasattr(mouseevent.inaxes, "parasites")

                    and self in mouseevent.inaxes.parasites):

                a.pick(mouseevent)



                           



    def _set_lim_and_transforms(self):

        if self.transAux is not None:

            self.transAxes = self._parent_axes.transAxes

            self.transData = self.transAux + self._parent_axes.transData

            self._xaxis_transform = mtransforms.blended_transform_factory(

                self.transData, self.transAxes)

            self._yaxis_transform = mtransforms.blended_transform_factory(

                self.transAxes, self.transData)

        else:

            super()._set_lim_and_transforms()



    def set_viewlim_mode(self, mode):

        _api.check_in_list([None, "equal", "transform"], mode=mode)

        self._viewlim_mode = mode



    def get_viewlim_mode(self):

        return self._viewlim_mode



    def _sync_lims(self, parent):

        viewlim = parent.viewLim.frozen()

        mode = self.get_viewlim_mode()

        if mode is None:

            pass

        elif mode == "equal":

            self.viewLim.set(viewlim)

        elif mode == "transform":

            self.viewLim.set(viewlim.transformed(self.transAux.inverted()))

        else:

            _api.check_in_list([None, "equal", "transform"], mode=mode)



                                  





parasite_axes_class_factory = cbook._make_class_factory(

    ParasiteAxesBase, "{}Parasite")

ParasiteAxes = parasite_axes_class_factory(Axes)





class HostAxesBase:

    def __init__(self, *args, **kwargs):

        self.parasites = []

        super().__init__(*args, **kwargs)



    def get_aux_axes(

            self, tr=None, viewlim_mode="equal", axes_class=None, **kwargs):

        

        if axes_class is None:

            axes_class = self._base_axes_class

        parasite_axes_class = parasite_axes_class_factory(axes_class)

        ax2 = parasite_axes_class(

            self, tr, viewlim_mode=viewlim_mode, **kwargs)

                                                       

                                                                         

        self.parasites.append(ax2)

        ax2._remove_method = self.parasites.remove

        return ax2



    def draw(self, renderer):

        orig_children_len = len(self._children)



        locator = self.get_axes_locator()

        if locator:

            pos = locator(self, renderer)

            self.set_position(pos, which="active")

            self.apply_aspect(pos)

        else:

            self.apply_aspect()



        rect = self.get_position()

        for ax in self.parasites:

            ax.apply_aspect(rect)

            self._children.extend(ax.get_children())



        super().draw(renderer)

        del self._children[orig_children_len:]



    def clear(self):

        super().clear()

        for ax in self.parasites:

            ax.clear()



    def pick(self, mouseevent):

        super().pick(mouseevent)

                                                                       

                                              

        for a in self.parasites:

            a.pick(mouseevent)



    def twinx(self, axes_class=None):

        

        ax = self._add_twin_axes(axes_class, sharex=self)

        self.axis["right"].set_visible(False)

        ax.axis["right"].set_visible(True)

        ax.axis["left", "top", "bottom"].set_visible(False)

        return ax



    def twiny(self, axes_class=None):

        

        ax = self._add_twin_axes(axes_class, sharey=self)

        self.axis["top"].set_visible(False)

        ax.axis["top"].set_visible(True)

        ax.axis["left", "right", "bottom"].set_visible(False)

        return ax



    def twin(self, aux_trans=None, axes_class=None):

        

        if aux_trans is None:

            aux_trans = mtransforms.IdentityTransform()

        ax = self._add_twin_axes(

            axes_class, aux_transform=aux_trans, viewlim_mode="transform")

        self.axis["top", "right"].set_visible(False)

        ax.axis["top", "right"].set_visible(True)

        ax.axis["left", "bottom"].set_visible(False)

        return ax



    def _add_twin_axes(self, axes_class, **kwargs):

        

        if axes_class is None:

            axes_class = self._base_axes_class

        ax = parasite_axes_class_factory(axes_class)(self, **kwargs)

        self.parasites.append(ax)

        ax._remove_method = self._remove_any_twin

        return ax



    def _remove_any_twin(self, ax):

        self.parasites.remove(ax)

        restore = ["top", "right"]

        if ax._sharex:

            restore.remove("top")

        if ax._sharey:

            restore.remove("right")

        self.axis[tuple(restore)].set_visible(True)

        self.axis[tuple(restore)].toggle(ticklabels=False, label=False)



    def get_tightbbox(self, renderer=None, *, call_axes_locator=True,

                      bbox_extra_artists=None):

        bbs = [

            *[ax.get_tightbbox(renderer, call_axes_locator=call_axes_locator)

              for ax in self.parasites],

            super().get_tightbbox(renderer,

                                  call_axes_locator=call_axes_locator,

                                  bbox_extra_artists=bbox_extra_artists)]

        return Bbox.union([b for b in bbs if b.width != 0 or b.height != 0])





host_axes_class_factory = host_subplot_class_factory =
    cbook._make_class_factory(HostAxesBase, "{}HostAxes", "_base_axes_class")

HostAxes = SubplotHost = host_axes_class_factory(Axes)





def host_axes(*args, axes_class=Axes, figure=None, **kwargs):

    

    import matplotlib.pyplot as plt

    host_axes_class = host_axes_class_factory(axes_class)

    if figure is None:

        figure = plt.gcf()

    ax = host_axes_class(figure, *args, **kwargs)

    figure.add_axes(ax)

    return ax





host_subplot = host_axes

