



import matplotlib.pyplot as plt

import numpy as np





                                                                  

class DataDisplayDownsampler:

    def __init__(self, xdata, y1data, y2data):

        self.origY1Data = y1data

        self.origY2Data = y2data

        self.origXData = xdata

        self.max_points = 50

        self.delta = xdata[-1] - xdata[0]



    def plot(self, ax):

        x, y1, y2 = self._downsample(self.origXData.min(), self.origXData.max())

        (self.line,) = ax.plot(x, y1, 'o-')

        self.poly_collection = ax.fill_between(x, y1, y2, step="pre", color="r")



    def _downsample(self, xstart, xend):

                                          

        mask = (self.origXData > xstart) & (self.origXData < xend)

                                                                 

                                                    

        mask = np.convolve([1, 1, 1], mask, mode='same').astype(bool)

                                          

        ratio = max(np.sum(mask) // self.max_points, 1)



                   

        xdata = self.origXData[mask]

        y1data = self.origY1Data[mask]

        y2data = self.origY2Data[mask]



                         

        xdata = xdata[::ratio]

        y1data = y1data[::ratio]

        y2data = y2data[::ratio]



        print(f"using {len(y1data)} of {np.sum(mask)} visible points")



        return xdata, y1data, y2data



    def update(self, ax):

                            

        lims = ax.viewLim

        if abs(lims.width - self.delta) > 1e-8:

            self.delta = lims.width

            xstart, xend = lims.intervalx

            x, y1, y2 = self._downsample(xstart, xend)

            self.line.set_data(x, y1)

            self.poly_collection.set_data(x, y1, y2, step="pre")

            ax.figure.canvas.draw_idle()





                 

xdata = np.linspace(16, 365, (365-16)*4)

y1data = np.sin(2*np.pi*xdata/153) + np.cos(2*np.pi*xdata/127)

y2data = y1data + .2



d = DataDisplayDownsampler(xdata, y1data, y2data)



fig, ax = plt.subplots()



                  

d.plot(ax)

ax.set_autoscale_on(False)                            



                                      

ax.callbacks.connect('xlim_changed', d.update)

ax.set_xlim(16, 365)

plt.show()



    

                                                              

