



import matplotlib.pyplot as plt

import numpy as np



from matplotlib import colors as mcolors

from matplotlib import path

from matplotlib.collections import RegularPolyCollection

from matplotlib.widgets import Lasso





class LassoManager:

    def __init__(self, ax, data):

                                                                                      

                                                                                   

                             

        self.collection = RegularPolyCollection(

            6, sizes=(100,), offset_transform=ax.transData,

            offsets=data, array=np.zeros(len(data)),

            clim=(0, 1), cmap=mcolors.ListedColormap(["tab:blue", "tab:red"]))

        ax.add_collection(self.collection)

        canvas = ax.figure.canvas

        canvas.mpl_connect('button_press_event', self.on_press)

        canvas.mpl_connect('button_release_event', self.on_release)



    def callback(self, verts):

        data = self.collection.get_offsets()

        self.collection.set_array(path.Path(verts).contains_points(data))

        canvas = self.collection.figure.canvas

        canvas.draw_idle()

        del self.lasso



    def on_press(self, event):

        canvas = self.collection.figure.canvas

        if event.inaxes is not self.collection.axes or canvas.widgetlock.locked():

            return

        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)

        canvas.widgetlock(self.lasso)                                        



    def on_release(self, event):

        canvas = self.collection.figure.canvas

        if hasattr(self, 'lasso') and canvas.widgetlock.isowner(self.lasso):

            canvas.widgetlock.release(self.lasso)





if __name__ == '__main__':

    np.random.seed(19680801)

    ax = plt.figure().add_subplot(

        xlim=(0, 1), ylim=(0, 1), title='Lasso points using left mouse button')

    manager = LassoManager(ax, np.random.rand(100, 2))

    plt.show()

