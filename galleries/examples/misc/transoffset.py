



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.transforms as mtransforms



xs = np.arange(7)

ys = xs**2



fig = plt.figure(figsize=(5, 10))

ax = plt.subplot(2, 1, 1)



                                                    

                                                 

                                                             

                                                          

trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,

                                       x=0.05, y=0.10, units='inches')



for x, y in zip(xs, ys):

    plt.plot(x, y, 'ro')

    plt.text(x, y, '%d, %d' % (int(x), int(y)), transform=trans_offset)





                                         

ax = plt.subplot(2, 1, 2, projection='polar')



trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,

                                       y=6, units='dots')



for x, y in zip(xs, ys):

    plt.polar(x, y, 'ro')

    plt.text(x, y, '%d, %d' % (int(x), int(y)),

             transform=trans_offset,

             horizontalalignment='center',

             verticalalignment='bottom')



plt.show()

