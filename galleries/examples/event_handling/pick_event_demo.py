



import matplotlib.pyplot as plt

import numpy as np

from numpy.random import rand



from matplotlib.image import AxesImage

from matplotlib.lines import Line2D

from matplotlib.patches import Rectangle

from matplotlib.text import Text



                                         

np.random.seed(19680801)





    

                                            

                                            



fig, (ax1, ax2) = plt.subplots(2, 1)

ax1.set_title('click on points, rectangles or text', picker=True)

ax1.set_ylabel('ylabel', picker=True, bbox=dict(facecolor='red'))

line, = ax1.plot(rand(100), 'o', picker=True, pickradius=5)



                     

ax2.bar(range(10), rand(10), picker=True)

for label in ax2.get_xticklabels():                                   

    label.set_picker(True)





def onpick1(event):

    if isinstance(event.artist, Line2D):

        thisline = event.artist

        xdata = thisline.get_xdata()

        ydata = thisline.get_ydata()

        ind = event.ind

        print('onpick1 line:', np.column_stack([xdata[ind], ydata[ind]]))

    elif isinstance(event.artist, Rectangle):

        patch = event.artist

        print('onpick1 patch:', patch.get_path())

    elif isinstance(event.artist, Text):

        text = event.artist

        print('onpick1 text:', text.get_text())





fig.canvas.mpl_connect('pick_event', onpick1)





    

                                         

                                         

                                                                             

                              

 

                                        

 

                                                                          

                                                                            

                              



def line_picker(line, mouseevent):

    

    if mouseevent.xdata is None:

        return False, dict()

    xdata = line.get_xdata()

    ydata = line.get_ydata()

    maxd = 0.05

    d = np.sqrt(

        (xdata - mouseevent.xdata)**2 + (ydata - mouseevent.ydata)**2)



    ind, = np.nonzero(d <= maxd)

    if len(ind):

        pickx = xdata[ind]

        picky = ydata[ind]

        props = dict(ind=ind, pickx=pickx, picky=picky)

        return True, props

    else:

        return False, dict()





def onpick2(event):

    print('onpick2 line:', event.pickx, event.picky)





fig, ax = plt.subplots()

ax.set_title('custom picker for line data')

line, = ax.plot(rand(100), rand(100), 'o', picker=line_picker)

fig.canvas.mpl_connect('pick_event', onpick2)





    

                           

                           

                                                                         



x, y, c, s = rand(4, 100)





def onpick3(event):

    ind = event.ind

    print('onpick3 scatter:', ind, x[ind], y[ind])





fig, ax = plt.subplots()

ax.scatter(x, y, 100*s, c, picker=True)

fig.canvas.mpl_connect('pick_event', onpick3)





    

                

                

                                                                       

          



fig, ax = plt.subplots()

ax.imshow(rand(10, 5), extent=(1, 2, 1, 2), picker=True)

ax.imshow(rand(5, 10), extent=(3, 4, 1, 2), picker=True)

ax.imshow(rand(20, 25), extent=(1, 2, 3, 4), picker=True)

ax.imshow(rand(30, 12), extent=(3, 4, 3, 4), picker=True)

ax.set(xlim=(0, 5), ylim=(0, 5))





def onpick4(event):

    artist = event.artist

    if isinstance(artist, AxesImage):

        im = artist

        A = im.get_array()

        print('onpick4 image', A.shape)





fig.canvas.mpl_connect('pick_event', onpick4)



plt.show()

