

import matplotlib.pyplot as plt

import numpy as np



from matplotlib.backend_bases import MouseEvent

from matplotlib.widgets import Cursor





class AnnotatedCursor(Cursor):

    



    def __init__(self, line, numberformat="{0:.4g};{1:.4g}", offset=(5, 5),

                 dataaxis='x', textprops=None, **cursorargs):

        if textprops is None:

            textprops = {}

                                                                  

        self.line = line

                                                                               

        self.numberformat = numberformat

                              

        self.offset = np.array(offset)

                                                            

        self.dataaxis = dataaxis



                                           

                                                             

                                      

        super().__init__(**cursorargs)



                                             

        self.set_position(self.line.get_xdata()[0], self.line.get_ydata()[0])

                                        

        self.text = self.ax.text(

            self.ax.get_xbound()[0],

            self.ax.get_ybound()[0],

            "0, 0",

            animated=bool(self.useblit),

            visible=False, **textprops)

                                                         

        self.lastdrawnplotpoint = None



    def onmove(self, event):

        



                                                                        

        if self.ignore(event):

            self.lastdrawnplotpoint = None

            return

        if not self.canvas.widgetlock.available(self):

            self.lastdrawnplotpoint = None

            return



                                                                          

                                                                            

                               

        if event.inaxes != self.ax:

            self.lastdrawnplotpoint = None

            self.text.set_visible(False)

            super().onmove(event)

            return



                                                                 

                                             

        plotpoint = None

        if event.xdata is not None and event.ydata is not None:

                                                           

                                                      

            plotpoint = self.set_position(event.xdata, event.ydata)

                                                                    

                                                     

                                                 

            if plotpoint is not None:

                event.xdata = plotpoint[0]

                event.ydata = plotpoint[1]



                                                                        

                                      

                                                                              

                                                                         

                           

        if plotpoint is not None and plotpoint == self.lastdrawnplotpoint:

            return



                                                               

                                                             

                                

        super().onmove(event)



                                                          

                              

                                                            

        if not self.get_active() or not self.visible:

            return



                                                          

        if plotpoint is not None:

                                                 

                                                 

                                                               

                                                           

                                                                    

            temp = [event.xdata, event.ydata]

            temp = self.ax.transData.transform(temp)

            temp = temp + self.offset

            temp = self.ax.transData.inverted().transform(temp)

            self.text.set_position(temp)

            self.text.set_text(self.numberformat.format(*plotpoint))

            self.text.set_visible(self.visible)



                                                            

                                                                       

                                                                  

            self.needclear = True



                                                                            

                                                                          

                            

            self.lastdrawnplotpoint = plotpoint

                                        

        else:

            self.text.set_visible(False)



                                                               

                                                              

                                               

        if self.useblit:

            self.ax.draw_artist(self.text)

            self.canvas.blit(self.ax.bbox)

        else:

                                                                          

                                                     

                                                

            self.canvas.draw_idle()



    def set_position(self, xpos, ypos):

        



                            

        xdata = self.line.get_xdata()

        ydata = self.line.get_ydata()



                                                                               

                     

        if self.dataaxis == 'x':

            pos = xpos

            data = xdata

            lim = self.ax.get_xlim()

        elif self.dataaxis == 'y':

            pos = ypos

            data = ydata

            lim = self.ax.get_ylim()

        else:

            raise ValueError(f"The data axis specifier {self.dataaxis} should "

                             f"be 'x' or 'y'")



                                                            

        if pos is not None and lim[0] <= pos <= lim[-1]:

                                                      

                                                          

            index = np.searchsorted(data, pos)

                                                         

            if index < 0 or index >= len(data):

                return None

                                         

            return (xdata[index], ydata[index])



                                                                            

        return None



    def clear(self, event):

        



                                                                 

                                        

                                                  

        super().clear(event)

        if self.ignore(event):

            return

        self.text.set_visible(False)



    def _update(self):

        



        if self.useblit:

            super()._update()





fig, ax = plt.subplots(figsize=(8, 6))

ax.set_title("Cursor Tracking x Position")



x = np.linspace(-5, 5, 1000)

y = x**2



line, = ax.plot(x, y)

ax.set_xlim(-5, 5)

ax.set_ylim(0, 25)



                

                                                            

                                                     

                                                            



                                                                 

                                                                        

                                                  

                                              

cursor = AnnotatedCursor(

    line=line,

    numberformat="{0:.2f}\n{1:.2f}",

    dataaxis='x', offset=[10, 10],

    textprops={'color': 'blue', 'fontweight': 'bold'},

    ax=ax,

    useblit=True,

    color='red',

    linewidth=2)



                                                           

t = ax.transData

MouseEvent(

    "motion_notify_event", ax.figure.canvas, *t.transform((-2, 10))

)._process()



plt.show()



    

                                     

                                     

                                                                

                                                                              

                                                                         

                                                                

                                                        



fig, ax = plt.subplots(figsize=(8, 6))

ax.set_title("Cursor Tracking y Position")



line, = ax.plot(x, y)

ax.set_xlim(-5, 5)

ax.set_ylim(0, 25)



cursor = AnnotatedCursor(

    line=line,

    numberformat="{0:.2f}\n{1:.2f}",

    dataaxis='y', offset=[10, 10],

    textprops={'color': 'blue', 'fontweight': 'bold'},

    ax=ax,

    useblit=True,

    color='red', linewidth=2)



                                                           

t = ax.transData

MouseEvent(

    "motion_notify_event", ax.figure.canvas, *t.transform((-2, 10))

)._process()



plt.show()

