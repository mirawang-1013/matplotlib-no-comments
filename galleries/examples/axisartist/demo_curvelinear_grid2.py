



import matplotlib.pyplot as plt

import numpy as np



from mpl_toolkits.axisartist.axislines import Axes

from mpl_toolkits.axisartist.grid_finder import ExtremeFinderSimple, MaxNLocator

from mpl_toolkits.axisartist.grid_helper_curvelinear import GridHelperCurveLinear





def curvelinear_test1(fig):

    



    def tr(x, y):

        return np.sign(x)*abs(x)**.5, y



    def inv_tr(x, y):

        return np.sign(x)*x**2, y



    grid_helper = GridHelperCurveLinear(

        (tr, inv_tr),

        extreme_finder=ExtremeFinderSimple(20, 20),

                             

        grid_locator1=MaxNLocator(nbins=6), grid_locator2=MaxNLocator(nbins=6))



    ax1 = fig.add_subplot(axes_class=Axes, grid_helper=grid_helper)

                                                              

                                                                              

                                                                      



    ax1.imshow(np.arange(25).reshape(5, 5),

               vmax=50, cmap="gray_r", origin="lower")





if __name__ == "__main__":

    fig = plt.figure(figsize=(7, 4))

    curvelinear_test1(fig)

    plt.show()

