



import numpy as np

from numpy import ma



from matplotlib import scale as mscale

from matplotlib import transforms as mtransforms

from matplotlib.ticker import FixedLocator, FuncFormatter





class MercatorLatitudeScale(mscale.ScaleBase):

    



                                                                              

                                                                               

                                

    name = 'mercator'



    def __init__(self, axis, *, thresh=np.deg2rad(85), **kwargs):

        

        super().__init__(axis)

        if thresh >= np.pi / 2:

            raise ValueError("thresh must be less than pi/2")

        self.thresh = thresh



    def get_transform(self):

        

        return self.MercatorLatitudeTransform(self.thresh)



    def set_default_locators_and_formatters(self, axis):

        

        fmt = FuncFormatter(

            lambda x, pos=None: f"{np.degrees(x):.0f}\N{DEGREE SIGN}")

        axis.set(major_locator=FixedLocator(np.radians(range(-90, 90, 10))),

                 major_formatter=fmt, minor_formatter=fmt)



    def limit_range_for_scale(self, vmin, vmax, minpos):

        

        return max(vmin, -self.thresh), min(vmax, self.thresh)



    class MercatorLatitudeTransform(mtransforms.Transform):

                                                           

                                                                    

                                                                 

                                                                   

                                                                      

                                                                   

                                                                      

                                                             

        input_dims = output_dims = 1



        def __init__(self, thresh):

            mtransforms.Transform.__init__(self)

            self.thresh = thresh



        def transform_non_affine(self, a):

            

            masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)

            if masked.mask.any():

                return ma.log(np.abs(ma.tan(masked) + 1 / ma.cos(masked)))

            else:

                return np.log(np.abs(np.tan(a) + 1 / np.cos(a)))



        def inverted(self):

            

            return MercatorLatitudeScale.InvertedMercatorLatitudeTransform(

                self.thresh)



    class InvertedMercatorLatitudeTransform(mtransforms.Transform):

        input_dims = output_dims = 1



        def __init__(self, thresh):

            mtransforms.Transform.__init__(self)

            self.thresh = thresh



        def transform_non_affine(self, a):

            return np.arctan(np.sinh(a))



        def inverted(self):

            return MercatorLatitudeScale.MercatorLatitudeTransform(self.thresh)





                                                                     

                              

mscale.register_scale(MercatorLatitudeScale)





if __name__ == '__main__':

    import matplotlib.pyplot as plt



    t = np.arange(-180.0, 180.0, 0.1)

    s = np.radians(t)/2.



    plt.plot(t, s, '-', lw=2)

    plt.yscale('mercator')



    plt.xlabel('Longitude')

    plt.ylabel('Latitude')

    plt.title('Mercator projection')

    plt.grid(True)



    plt.show()

