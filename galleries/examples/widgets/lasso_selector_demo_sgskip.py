





import numpy as np



from matplotlib.path import Path

from matplotlib.widgets import LassoSelector





class SelectFromCollection:

    



    def __init__(self, ax, collection, alpha_other=0.3):

        self.canvas = ax.figure.canvas

        self.collection = collection

        self.alpha_other = alpha_other



        self.xys = collection.get_offsets()

        self.Npts = len(self.xys)



                                                             

        self.fc = collection.get_facecolors()

        if len(self.fc) == 0:

            raise ValueError('Collection must have a facecolor')

        elif len(self.fc) == 1:

            self.fc = np.tile(self.fc, (self.Npts, 1))



        self.lasso = LassoSelector(ax, onselect=self.onselect)

        self.ind = []



    def onselect(self, verts):

        path = Path(verts)

        self.ind = np.nonzero(path.contains_points(self.xys))[0]

        self.fc[:, -1] = self.alpha_other

        self.fc[self.ind, -1] = 1

        self.collection.set_facecolors(self.fc)

        self.canvas.draw_idle()



    def disconnect(self):

        self.lasso.disconnect_events()

        self.fc[:, -1] = 1

        self.collection.set_facecolors(self.fc)

        self.canvas.draw_idle()





if __name__ == '__main__':

    import matplotlib.pyplot as plt



                                             

    np.random.seed(19680801)



    data = np.random.rand(100, 2)



    subplot_kw = dict(xlim=(0, 1), ylim=(0, 1), autoscale_on=False)

    fig, ax = plt.subplots(subplot_kw=subplot_kw)



    pts = ax.scatter(data[:, 0], data[:, 1], s=80)

    selector = SelectFromCollection(ax, pts)



    def accept(event):

        if event.key == "enter":

            print("Selected points:")

            print(selector.xys[selector.ind])

            selector.disconnect()

            ax.set_title("")

            fig.canvas.draw()



    fig.canvas.mpl_connect("key_press_event", accept)

    ax.set_title("Press enter to accept selected points.")



    plt.show()



    

 

                            

 

                                                                              

                     

 

                                         

                             

