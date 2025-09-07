



from itertools import cycle



import numpy as np



from matplotlib import cbook

from matplotlib.lines import Line2D

from matplotlib.patches import Rectangle

import matplotlib.collections as mcoll





def update_from_first_child(tgt, src):

    first_child = next(iter(src.get_children()), None)

    if first_child is not None:

        tgt.update_from(first_child)





class HandlerBase:

    

    def __init__(self, xpad=0., ypad=0., update_func=None):

        

        self._xpad, self._ypad = xpad, ypad

        self._update_prop_func = update_func



    def _update_prop(self, legend_handle, orig_handle):

        if self._update_prop_func is None:

            self._default_update_prop(legend_handle, orig_handle)

        else:

            self._update_prop_func(legend_handle, orig_handle)



    def _default_update_prop(self, legend_handle, orig_handle):

        legend_handle.update_from(orig_handle)



    def update_prop(self, legend_handle, orig_handle, legend):



        self._update_prop(legend_handle, orig_handle)



        legend._set_artist_props(legend_handle)

        legend_handle.set_clip_box(None)

        legend_handle.set_clip_path(None)



    def adjust_drawing_area(self, legend, orig_handle,

                            xdescent, ydescent, width, height, fontsize,

                            ):

        xdescent = xdescent - self._xpad * fontsize

        ydescent = ydescent - self._ypad * fontsize

        width = width - self._xpad * fontsize

        height = height - self._ypad * fontsize

        return xdescent, ydescent, width, height



    def legend_artist(self, legend, orig_handle,

                      fontsize, handlebox):

        

        xdescent, ydescent, width, height = self.adjust_drawing_area(

                 legend, orig_handle,

                 handlebox.xdescent, handlebox.ydescent,

                 handlebox.width, handlebox.height,

                 fontsize)

        artists = self.create_artists(legend, orig_handle,

                                      xdescent, ydescent, width, height,

                                      fontsize, handlebox.get_transform())



                                                       

        for a in artists:

            handlebox.add_artist(a)



                                         

        return artists[0]



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize,

                       trans):

        

        raise NotImplementedError('Derived must override')





class HandlerNpoints(HandlerBase):

    



    def __init__(self, marker_pad=0.3, numpoints=None, **kwargs):

        

        super().__init__(**kwargs)



        self._numpoints = numpoints

        self._marker_pad = marker_pad



    def get_numpoints(self, legend):

        if self._numpoints is None:

            return legend.numpoints

        else:

            return self._numpoints



    def get_xdata(self, legend, xdescent, ydescent, width, height, fontsize):

        numpoints = self.get_numpoints(legend)

        if numpoints > 1:

                                                                       

            pad = self._marker_pad * fontsize

            xdata = np.linspace(-xdescent + pad,

                                -xdescent + width - pad,

                                numpoints)

            xdata_marker = xdata

        else:

            xdata = [-xdescent, -xdescent + width]

            xdata_marker = [-xdescent + 0.5 * width]

        return xdata, xdata_marker





class HandlerNpointsYoffsets(HandlerNpoints):

    



    def __init__(self, numpoints=None, yoffsets=None, **kwargs):

        

        super().__init__(numpoints=numpoints, **kwargs)

        self._yoffsets = yoffsets



    def get_ydata(self, legend, xdescent, ydescent, width, height, fontsize):

        if self._yoffsets is None:

            ydata = height * legend._scatteryoffsets

        else:

            ydata = height * np.asarray(self._yoffsets)



        return ydata





class HandlerLine2DCompound(HandlerNpoints):

    



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize,

                       trans):

                             

        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,

                                             width, height, fontsize)



        ydata = np.full_like(xdata, ((height - ydescent) / 2))

        legline = Line2D(xdata, ydata)



        self.update_prop(legline, orig_handle, legend)

        legline.set_drawstyle('default')

        legline.set_marker("")



        legline_marker = Line2D(xdata_marker, ydata[:len(xdata_marker)])

        self.update_prop(legline_marker, orig_handle, legend)

        legline_marker.set_linestyle('None')

        if legend.markerscale != 1:

            newsz = legline_marker.get_markersize() * legend.markerscale

            legline_marker.set_markersize(newsz)

                                                              

                                                               

                         

        legline._legmarker = legline_marker



        legline.set_transform(trans)

        legline_marker.set_transform(trans)



        return [legline, legline_marker]





class HandlerLine2D(HandlerNpoints):

    



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize,

                       trans):

                             

        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,

                                             width, height, fontsize)



        markevery = None

        if self.get_numpoints(legend) == 1:

                                                                   

                                                                   

                                                                      

            xdata = np.linspace(xdata[0], xdata[-1], 3)

            markevery = [1]



        ydata = np.full_like(xdata, (height - ydescent) / 2)

        legline = Line2D(xdata, ydata, markevery=markevery)



        self.update_prop(legline, orig_handle, legend)



        if legend.markerscale != 1:

            newsz = legline.get_markersize() * legend.markerscale

            legline.set_markersize(newsz)



        legline.set_transform(trans)



        return [legline]





class HandlerPatch(HandlerBase):

    



    def __init__(self, patch_func=None, **kwargs):

        

        super().__init__(**kwargs)

        self._patch_func = patch_func



    def _create_patch(self, legend, orig_handle,

                      xdescent, ydescent, width, height, fontsize):

        if self._patch_func is None:

            p = Rectangle(xy=(-xdescent, -ydescent),

                          width=width, height=height)

        else:

            p = self._patch_func(legend=legend, orig_handle=orig_handle,

                                 xdescent=xdescent, ydescent=ydescent,

                                 width=width, height=height, fontsize=fontsize)

        return p



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize, trans):

                             

        p = self._create_patch(legend, orig_handle,

                               xdescent, ydescent, width, height, fontsize)

        self.update_prop(p, orig_handle, legend)

        p.set_transform(trans)

        return [p]





class HandlerStepPatch(HandlerBase):

    



    @staticmethod

    def _create_patch(orig_handle, xdescent, ydescent, width, height):

        return Rectangle(xy=(-xdescent, -ydescent), width=width,

                         height=height, color=orig_handle.get_facecolor())



    @staticmethod

    def _create_line(orig_handle, width, height):

                                                  

        legline = Line2D([0, width], [height/2, height/2],

                         color=orig_handle.get_edgecolor(),

                         linestyle=orig_handle.get_linestyle(),

                         linewidth=orig_handle.get_linewidth(),

                         )



                                                                        

        legline.set_drawstyle('default')

        legline.set_marker("")

        return legline



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize, trans):

                             

        if orig_handle.get_fill() or (orig_handle.get_hatch() is not None):

            p = self._create_patch(orig_handle, xdescent, ydescent, width,

                                   height)

            self.update_prop(p, orig_handle, legend)

        else:

            p = self._create_line(orig_handle, width, height)

        p.set_transform(trans)

        return [p]





class HandlerLineCollection(HandlerLine2D):

    

    def get_numpoints(self, legend):

        if self._numpoints is None:

            return legend.scatterpoints

        else:

            return self._numpoints



    def _default_update_prop(self, legend_handle, orig_handle):

        lw = orig_handle.get_linewidths()[0]

        dashes = orig_handle._us_linestyles[0]

        color = orig_handle.get_colors()[0]

        legend_handle.set_color(color)

        legend_handle.set_linestyle(dashes)

        legend_handle.set_linewidth(lw)



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize, trans):

                             

        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,

                                             width, height, fontsize)

        ydata = np.full_like(xdata, (height - ydescent) / 2)

        legline = Line2D(xdata, ydata)



        self.update_prop(legline, orig_handle, legend)

        legline.set_transform(trans)



        return [legline]





class HandlerRegularPolyCollection(HandlerNpointsYoffsets):

    



    def __init__(self, yoffsets=None, sizes=None, **kwargs):

        super().__init__(yoffsets=yoffsets, **kwargs)



        self._sizes = sizes



    def get_numpoints(self, legend):

        if self._numpoints is None:

            return legend.scatterpoints

        else:

            return self._numpoints



    def get_sizes(self, legend, orig_handle,

                  xdescent, ydescent, width, height, fontsize):

        if self._sizes is None:

            handle_sizes = orig_handle.get_sizes()

            if not len(handle_sizes):

                handle_sizes = [1]

            size_max = max(handle_sizes) * legend.markerscale ** 2

            size_min = min(handle_sizes) * legend.markerscale ** 2



            numpoints = self.get_numpoints(legend)

            if numpoints < 4:

                sizes = [.5 * (size_max + size_min), size_max,

                         size_min][:numpoints]

            else:

                rng = (size_max - size_min)

                sizes = rng * np.linspace(0, 1, numpoints) + size_min

        else:

            sizes = self._sizes



        return sizes



    def update_prop(self, legend_handle, orig_handle, legend):



        self._update_prop(legend_handle, orig_handle)



        legend_handle.set_figure(legend.get_figure(root=False))

                                                 

        legend_handle.set_clip_box(None)

        legend_handle.set_clip_path(None)



    def create_collection(self, orig_handle, sizes, offsets, offset_transform):

        return type(orig_handle)(

            orig_handle.get_numsides(),

            rotation=orig_handle.get_rotation(), sizes=sizes,

            offsets=offsets, offset_transform=offset_transform,

        )



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize,

                       trans):

                             

        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,

                                             width, height, fontsize)



        ydata = self.get_ydata(legend, xdescent, ydescent,

                               width, height, fontsize)



        sizes = self.get_sizes(legend, orig_handle, xdescent, ydescent,

                               width, height, fontsize)



        p = self.create_collection(

            orig_handle, sizes,

            offsets=list(zip(xdata_marker, ydata)), offset_transform=trans)



        self.update_prop(p, orig_handle, legend)

        p.set_offset_transform(trans)

        return [p]





class HandlerPathCollection(HandlerRegularPolyCollection):

    



    def create_collection(self, orig_handle, sizes, offsets, offset_transform):

        return type(orig_handle)(

            [orig_handle.get_paths()[0]], sizes=sizes,

            offsets=offsets, offset_transform=offset_transform,

        )





class HandlerCircleCollection(HandlerRegularPolyCollection):

    



    def create_collection(self, orig_handle, sizes, offsets, offset_transform):

        return type(orig_handle)(

            sizes, offsets=offsets, offset_transform=offset_transform)





class HandlerErrorbar(HandlerLine2D):

    



    def __init__(self, xerr_size=0.5, yerr_size=None,

                 marker_pad=0.3, numpoints=None, **kwargs):



        self._xerr_size = xerr_size

        self._yerr_size = yerr_size



        super().__init__(marker_pad=marker_pad, numpoints=numpoints, **kwargs)



    def get_err_size(self, legend, xdescent, ydescent,

                     width, height, fontsize):

        xerr_size = self._xerr_size * fontsize



        if self._yerr_size is None:

            yerr_size = xerr_size

        else:

            yerr_size = self._yerr_size * fontsize



        return xerr_size, yerr_size



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize,

                       trans):

                             

        plotlines, caplines, barlinecols = orig_handle



        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,

                                             width, height, fontsize)



        ydata = np.full_like(xdata, (height - ydescent) / 2)

        legline = Line2D(xdata, ydata)



        xdata_marker = np.asarray(xdata_marker)

        ydata_marker = np.asarray(ydata[:len(xdata_marker)])



        xerr_size, yerr_size = self.get_err_size(legend, xdescent, ydescent,

                                                 width, height, fontsize)



        legline_marker = Line2D(xdata_marker, ydata_marker)



                                                                     

                                 

        if plotlines is None:

            legline.set_visible(False)

            legline_marker.set_visible(False)

        else:

            self.update_prop(legline, plotlines, legend)



            legline.set_drawstyle('default')

            legline.set_marker('none')



            self.update_prop(legline_marker, plotlines, legend)

            legline_marker.set_linestyle('None')



            if legend.markerscale != 1:

                newsz = legline_marker.get_markersize() * legend.markerscale

                legline_marker.set_markersize(newsz)



        handle_barlinecols = []

        handle_caplines = []



        if orig_handle.has_xerr:

            verts = [((x - xerr_size, y), (x + xerr_size, y))

                     for x, y in zip(xdata_marker, ydata_marker)]

            coll = mcoll.LineCollection(verts)

            self.update_prop(coll, barlinecols[0], legend)

            handle_barlinecols.append(coll)



            if caplines:

                capline_left = Line2D(xdata_marker - xerr_size, ydata_marker)

                capline_right = Line2D(xdata_marker + xerr_size, ydata_marker)

                self.update_prop(capline_left, caplines[0], legend)

                self.update_prop(capline_right, caplines[0], legend)

                capline_left.set_marker("|")

                capline_right.set_marker("|")



                handle_caplines.append(capline_left)

                handle_caplines.append(capline_right)



        if orig_handle.has_yerr:

            verts = [((x, y - yerr_size), (x, y + yerr_size))

                     for x, y in zip(xdata_marker, ydata_marker)]

            coll = mcoll.LineCollection(verts)

            self.update_prop(coll, barlinecols[0], legend)

            handle_barlinecols.append(coll)



            if caplines:

                capline_left = Line2D(xdata_marker, ydata_marker - yerr_size)

                capline_right = Line2D(xdata_marker, ydata_marker + yerr_size)

                self.update_prop(capline_left, caplines[0], legend)

                self.update_prop(capline_right, caplines[0], legend)

                capline_left.set_marker("_")

                capline_right.set_marker("_")



                handle_caplines.append(capline_left)

                handle_caplines.append(capline_right)



        artists = [

            *handle_barlinecols, *handle_caplines, legline, legline_marker,

        ]

        for artist in artists:

            artist.set_transform(trans)

        return artists





class HandlerStem(HandlerNpointsYoffsets):

    



    def __init__(self, marker_pad=0.3, numpoints=None,

                 bottom=None, yoffsets=None, **kwargs):

        

        super().__init__(marker_pad=marker_pad, numpoints=numpoints,

                         yoffsets=yoffsets, **kwargs)

        self._bottom = bottom



    def get_ydata(self, legend, xdescent, ydescent, width, height, fontsize):

        if self._yoffsets is None:

            ydata = height * (0.5 * legend._scatteryoffsets + 0.5)

        else:

            ydata = height * np.asarray(self._yoffsets)



        return ydata



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize,

                       trans):

                             

        markerline, stemlines, baseline = orig_handle

                                                                           

                                                                           

                                    

        using_linecoll = isinstance(stemlines, mcoll.LineCollection)



        xdata, xdata_marker = self.get_xdata(legend, xdescent, ydescent,

                                             width, height, fontsize)



        ydata = self.get_ydata(legend, xdescent, ydescent,

                               width, height, fontsize)



        if self._bottom is None:

            bottom = 0.

        else:

            bottom = self._bottom



        leg_markerline = Line2D(xdata_marker, ydata[:len(xdata_marker)])

        self.update_prop(leg_markerline, markerline, legend)



        leg_stemlines = [Line2D([x, x], [bottom, y])

                         for x, y in zip(xdata_marker, ydata)]



        if using_linecoll:

                                                                        

                                                

            with cbook._setattr_cm(

                    self, _update_prop_func=self._copy_collection_props):

                for line in leg_stemlines:

                    self.update_prop(line, stemlines, legend)



        else:

            for lm, m in zip(leg_stemlines, stemlines):

                self.update_prop(lm, m, legend)



        leg_baseline = Line2D([np.min(xdata), np.max(xdata)],

                              [bottom, bottom])

        self.update_prop(leg_baseline, baseline, legend)



        artists = [*leg_stemlines, leg_baseline, leg_markerline]

        for artist in artists:

            artist.set_transform(trans)

        return artists



    def _copy_collection_props(self, legend_handle, orig_handle):

        

        legend_handle.set_color(orig_handle.get_color()[0])

        legend_handle.set_linestyle(orig_handle.get_linestyle()[0])





class HandlerTuple(HandlerBase):

    



    def __init__(self, ndivide=1, pad=None, **kwargs):

        

        self._ndivide = ndivide

        self._pad = pad

        super().__init__(**kwargs)



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize,

                       trans):

                             

        handler_map = legend.get_legend_handler_map()



        if self._ndivide is None:

            ndivide = len(orig_handle)

        else:

            ndivide = self._ndivide



        if self._pad is None:

            pad = legend.borderpad * fontsize

        else:

            pad = self._pad * fontsize



        if ndivide > 1:

            width = (width - pad * (ndivide - 1)) / ndivide



        xds_cycle = cycle(xdescent - (width + pad) * np.arange(ndivide))



        a_list = []

        for handle1 in orig_handle:

            handler = legend.get_legend_handler(handler_map, handle1)

            _a_list = handler.create_artists(

                legend, handle1,

                next(xds_cycle), ydescent, width, height, fontsize, trans)

            a_list.extend(_a_list)



        return a_list





class HandlerPolyCollection(HandlerBase):

    

    def _update_prop(self, legend_handle, orig_handle):

        def first_color(colors):

            if colors.size == 0:

                return (0, 0, 0, 0)

            return tuple(colors[0])



        def get_first(prop_array):

            if len(prop_array):

                return prop_array[0]

            else:

                return None



                                                                       

                                                                    

        legend_handle._facecolor = first_color(orig_handle.get_facecolor())

        legend_handle._edgecolor = first_color(orig_handle.get_edgecolor())

        legend_handle._hatch_color = first_color(orig_handle.get_hatchcolor())

        legend_handle._original_facecolor = orig_handle._original_facecolor

        legend_handle._original_edgecolor = orig_handle._original_edgecolor

        legend_handle._fill = orig_handle.get_fill()

        legend_handle._hatch = orig_handle.get_hatch()

                                                        

        legend_handle.set_linewidth(get_first(orig_handle.get_linewidths()))

        legend_handle.set_linestyle(get_first(orig_handle.get_linestyles()))

        legend_handle.set_transform(get_first(orig_handle.get_transforms()))

                                                                      



    def create_artists(self, legend, orig_handle,

                       xdescent, ydescent, width, height, fontsize, trans):

                             

        p = Rectangle(xy=(-xdescent, -ydescent),

                      width=width, height=height)

        self.update_prop(p, orig_handle, legend)

        p.set_transform(trans)

        return [p]

