import numpy as np



from matplotlib import cbook

from .backend_agg import RendererAgg

from matplotlib._tight_bbox import process_figure_for_rasterizing





class MixedModeRenderer:

    

    def __init__(self, figure, width, height, dpi, vector_renderer,

                 raster_renderer_class=None,

                 bbox_inches_restore=None):

        

        if raster_renderer_class is None:

            raster_renderer_class = RendererAgg



        self._raster_renderer_class = raster_renderer_class

        self._width = width

        self._height = height

        self.dpi = dpi



        self._vector_renderer = vector_renderer



        self._raster_renderer = None



                                                                  

                                                                     

                                                                  

        self.figure = figure

        self._figdpi = figure.dpi



        self._bbox_inches_restore = bbox_inches_restore



        self._renderer = vector_renderer



    def __getattr__(self, attr):

                                                                  

                                                                 

                                                              

                                                               

                                                               

                                              

        return getattr(self._renderer, attr)



    def start_rasterizing(self):

        

                                                   

        self.figure.dpi = self.dpi



        self._raster_renderer = self._raster_renderer_class(

            self._width*self.dpi, self._height*self.dpi, self.dpi)

        self._renderer = self._raster_renderer



        if self._bbox_inches_restore:                           

            r = process_figure_for_rasterizing(self.figure,

                                               self._bbox_inches_restore,

                                               self._raster_renderer)

            self._bbox_inches_restore = r



    def stop_rasterizing(self):

        



        self._renderer = self._vector_renderer



        height = self._height * self.dpi

        img = np.asarray(self._raster_renderer.buffer_rgba())

        slice_y, slice_x = cbook._get_nonzero_slices(img[..., 3])

        cropped_img = img[slice_y, slice_x]

        if cropped_img.size:

            gc = self._renderer.new_gc()

                                                                         

                                                                         

                                          

            self._renderer.draw_image(

                gc,

                slice_x.start * self._figdpi / self.dpi,

                (height - slice_y.stop) * self._figdpi / self.dpi,

                cropped_img[::-1])

        self._raster_renderer = None



                                 

        self.figure.dpi = self._figdpi



        if self._bbox_inches_restore:                           

            r = process_figure_for_rasterizing(self.figure,

                                               self._bbox_inches_restore,

                                               self._vector_renderer,

                                               self._figdpi)

            self._bbox_inches_restore = r

