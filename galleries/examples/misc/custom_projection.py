



import numpy as np



import matplotlib

from matplotlib.axes import Axes

import matplotlib.axis as maxis

from matplotlib.patches import Circle

from matplotlib.path import Path

from matplotlib.projections import register_projection

import matplotlib.spines as mspines

from matplotlib.ticker import FixedLocator, Formatter, NullLocator

from matplotlib.transforms import Affine2D, BboxTransformTo, Transform



rcParams = matplotlib.rcParams



                                                                     

                                                                     

                                                                    

                                                                   

               





class GeoAxes(Axes):

    

    class ThetaFormatter(Formatter):

        

        def __init__(self, round_to=1.0):

            self._round_to = round_to



        def __call__(self, x, pos=None):

            degrees = round(np.rad2deg(x) / self._round_to) * self._round_to

            return f"{degrees:0.0f}\N{DEGREE SIGN}"



    RESOLUTION = 75



    def _init_axis(self):

        self.xaxis = maxis.XAxis(self)

        self.yaxis = maxis.YAxis(self)

                                                                  

                                                                 

                                                      



    def clear(self):

                             

        super().clear()



        self.set_longitude_grid(30)

        self.set_latitude_grid(15)

        self.set_longitude_grid_ends(75)

        self.xaxis.set_minor_locator(NullLocator())

        self.yaxis.set_minor_locator(NullLocator())

        self.xaxis.set_ticks_position('none')

        self.yaxis.set_ticks_position('none')

        self.yaxis.set_tick_params(label1On=True)

                                                          

                                           



        self.grid(rcParams['axes.grid'])



        Axes.set_xlim(self, -np.pi, np.pi)

        Axes.set_ylim(self, -np.pi / 2.0, np.pi / 2.0)



    def _set_lim_and_transforms(self):

                                                                         



                                                                    

         

                                                     

         

                                                            

                                           

         

                                                                   

                                         



                                                                   

                                                                     

                                         



                                                                      

                                                                  

                                                                      

                                                                      

                                                                     

                                                   



                                                         

                                                                 

        self.transProjection = self._get_core_transform(self.RESOLUTION)



                                                                  

                                                                   

                                                                   

                                                                      

                                    

        self.transAffine = self._get_affine_transform()



                                                                  

                

        self.transAxes = BboxTransformTo(self.bbox)



                                                                      

                                                                

                                                                    

                                                                  

                                   

        self.transData =
            self.transProjection +
            self.transAffine +
            self.transAxes



                                                                

                                    



                                                                 

                                                                   

                                                                  

                                                                     

                                                                   

                                  

        self._xaxis_pretransform =
            Affine2D()
            .scale(1.0, self._longitude_cap * 2.0)
            .translate(0.0, -self._longitude_cap)

        self._xaxis_transform =
            self._xaxis_pretransform +
            self.transData

        self._xaxis_text1_transform =
            Affine2D().scale(1.0, 0.0) +
            self.transData +
            Affine2D().translate(0.0, 4.0)

        self._xaxis_text2_transform =
            Affine2D().scale(1.0, 0.0) +
            self.transData +
            Affine2D().translate(0.0, -4.0)



                                                                         

                                                                      

                                                                      

                                                                     

                                                                   

                                                   

        yaxis_stretch = Affine2D().scale(np.pi*2, 1).translate(-np.pi, 0)

        yaxis_space = Affine2D().scale(1.0, 1.1)

        self._yaxis_transform =
            yaxis_stretch +
            self.transData

        yaxis_text_base =
            yaxis_stretch +
            self.transProjection +
            (yaxis_space +

             self.transAffine +

             self.transAxes)

        self._yaxis_text1_transform =
            yaxis_text_base +
            Affine2D().translate(-8.0, 0.0)

        self._yaxis_text2_transform =
            yaxis_text_base +
            Affine2D().translate(8.0, 0.0)



    def _get_affine_transform(self):

        transform = self._get_core_transform(1)

        xscale, _ = transform.transform((np.pi, 0))

        _, yscale = transform.transform((0, np.pi/2))

        return Affine2D()
            .scale(0.5 / xscale, 0.5 / yscale)
            .translate(0.5, 0.5)



    def get_xaxis_transform(self, which='grid'):

        

        if which not in ['tick1', 'tick2', 'grid']:

            raise ValueError(

                "'which' must be one of 'tick1', 'tick2', or 'grid'")

        return self._xaxis_transform



    def get_xaxis_text1_transform(self, pad):

        return self._xaxis_text1_transform, 'bottom', 'center'



    def get_xaxis_text2_transform(self, pad):

        

        return self._xaxis_text2_transform, 'top', 'center'



    def get_yaxis_transform(self, which='grid'):

        

        if which not in ['tick1', 'tick2', 'grid']:

            raise ValueError(

                "'which' must be one of 'tick1', 'tick2', or 'grid'")

        return self._yaxis_transform



    def get_yaxis_text1_transform(self, pad):

        

        return self._yaxis_text1_transform, 'center', 'right'



    def get_yaxis_text2_transform(self, pad):

        

        return self._yaxis_text2_transform, 'center', 'left'



    def _gen_axes_patch(self):

        

        return Circle((0.5, 0.5), 0.5)



    def _gen_axes_spines(self):

        return {'geo': mspines.Spine.circular_spine(self, (0.5, 0.5), 0.5)}



    def set_yscale(self, *args, **kwargs):

        if args[0] != 'linear':

            raise NotImplementedError



                                                                 

                                                                    

                                  

    set_xscale = set_yscale



                                                                      

                                                                   

                                                                      

                                                            

    def set_xlim(self, *args, **kwargs):

        raise TypeError("Changing axes limits of a geographic projection is "

                        "not supported.  Please consider using Cartopy.")



    set_ylim = set_xlim



    def format_coord(self, lon, lat):

        

        lon, lat = np.rad2deg([lon, lat])

        ns = 'N' if lat >= 0.0 else 'S'

        ew = 'E' if lon >= 0.0 else 'W'

        return ('%f\N{DEGREE SIGN}%s, %f\N{DEGREE SIGN}%s'

                % (abs(lat), ns, abs(lon), ew))



    def set_longitude_grid(self, degrees):

        

                                                        

        grid = np.arange(-180 + degrees, 180, degrees)

        self.xaxis.set_major_locator(FixedLocator(np.deg2rad(grid)))

        self.xaxis.set_major_formatter(self.ThetaFormatter(degrees))



    def set_latitude_grid(self, degrees):

        

                                                      

        grid = np.arange(-90 + degrees, 90, degrees)

        self.yaxis.set_major_locator(FixedLocator(np.deg2rad(grid)))

        self.yaxis.set_major_formatter(self.ThetaFormatter(degrees))



    def set_longitude_grid_ends(self, degrees):

        

        self._longitude_cap = np.deg2rad(degrees)

        self._xaxis_pretransform
            .clear()
            .scale(1.0, self._longitude_cap * 2.0)
            .translate(0.0, -self._longitude_cap)



    def get_data_ratio(self):

        

        return 1.0



                                                                            

                                                                

    def can_zoom(self):

        

        return False



    def can_pan(self):

        

        return False



    def start_pan(self, x, y, button):

        pass



    def end_pan(self):

        pass



    def drag_pan(self, button, key, x, y):

        pass





class HammerAxes(GeoAxes):

    



                                                                  

                                    

                                                   

    name = 'custom_hammer'



    class HammerTransform(Transform):

        

        input_dims = output_dims = 2



        def __init__(self, resolution):

            

            Transform.__init__(self)

            self._resolution = resolution



        def transform_non_affine(self, ll):

            longitude, latitude = ll.T



                                     

            half_long = longitude / 2

            cos_latitude = np.cos(latitude)

            sqrt2 = np.sqrt(2)



            alpha = np.sqrt(1 + cos_latitude * np.cos(half_long))

            x = (2 * sqrt2) * (cos_latitude * np.sin(half_long)) / alpha

            y = (sqrt2 * np.sin(latitude)) / alpha

            return np.column_stack([x, y])



        def transform_path_non_affine(self, path):

                                      

            ipath = path.interpolated(self._resolution)

            return Path(self.transform(ipath.vertices), ipath.codes)



        def inverted(self):

            return HammerAxes.InvertedHammerTransform(self._resolution)



    class InvertedHammerTransform(Transform):

        input_dims = output_dims = 2



        def __init__(self, resolution):

            Transform.__init__(self)

            self._resolution = resolution



        def transform_non_affine(self, xy):

            x, y = xy.T

            z = np.sqrt(1 - (x / 4) ** 2 - (y / 2) ** 2)

            longitude = 2 * np.arctan((z * x) / (2 * (2 * z ** 2 - 1)))

            latitude = np.arcsin(y*z)

            return np.column_stack([longitude, latitude])



        def inverted(self):

            return HammerAxes.HammerTransform(self._resolution)



    def __init__(self, *args, **kwargs):

        self._longitude_cap = np.pi / 2.0

        super().__init__(*args, **kwargs)

        self.set_aspect(0.5, adjustable='box', anchor='C')

        self.clear()



    def _get_core_transform(self, resolution):

        return self.HammerTransform(resolution)





                                                                        

register_projection(HammerAxes)





if __name__ == '__main__':

    import matplotlib.pyplot as plt



                                                            

    fig, ax = plt.subplots(subplot_kw={'projection': 'custom_hammer'})

    ax.plot([-1, 1, 1], [-1, -1, 1], "o-")

    ax.grid()



    plt.show()

