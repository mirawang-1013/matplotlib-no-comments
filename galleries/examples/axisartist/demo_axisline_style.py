



import matplotlib.pyplot as plt

import numpy as np



from mpl_toolkits.axisartist.axislines import AxesZero



fig = plt.figure()

ax = fig.add_subplot(axes_class=AxesZero)



for direction in ["xzero", "yzero"]:

                                          

    ax.axis[direction].set_axisline_style("-|>")



                                       

    ax.axis[direction].set_visible(True)



for direction in ["left", "right", "bottom", "top"]:

                   

    ax.axis[direction].set_visible(False)



x = np.linspace(-0.5, 1., 100)

ax.plot(x, np.sin(x*np.pi))



plt.show()

