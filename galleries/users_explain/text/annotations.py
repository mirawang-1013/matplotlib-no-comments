

    

                           

 

                  

                  

 

                                                                              

                                                                              

                                           



import matplotlib.pyplot as plt

import numpy as np



fig, ax = plt.subplots(figsize=(3, 3))



t = np.arange(0.0, 5.0, 0.01)

s = np.cos(2*np.pi*t)

line, = ax.plot(t, s, lw=2)



ax.annotate('local max', xy=(2, 1), xytext=(3, 1.5),

            arrowprops=dict(facecolor='black', shrink=0.05))

ax.set_ylim(-2, 2)



    

                                                                   

                                                                        

                                                                     

                                                                   

                                                 

 

                                                                              

                                       

                                                                              

                                                                     

                                                                     

                                                                              

                                                               

                                                               

                                                                            

                                                         

                                                                              

 

                                                                 

 

                                                                              

                                       

                                                                              

                                                          

                                                          

                                                                              

 

                                                                      

                                               

                                                                          

                                                                             

                                                                            

 

                      

 

                 

                 

 

                                                                          



fig, ax = plt.subplots(figsize=(3, 3))



t = np.arange(0.0, 5.0, 0.01)

s = np.cos(2*np.pi*t)

line, = ax.plot(t, s, lw=2)



ax.annotate('local max', xy=(2, 1), xycoords='data',

            xytext=(0.01, .99), textcoords='axes fraction',

            va='top', ha='left',

            arrowprops=dict(facecolor='black', shrink=0.05))

ax.set_ylim(-2, 2)



    

 

                      

                      

 

                                                                            

                                                                             

                        



import matplotlib.patches as mpatches



fig, ax = plt.subplots(figsize=(3, 3))

arr = mpatches.FancyArrowPatch((1.25, 1.5), (1.75, 1.5),

                               arrowstyle='->,head_width=.15', mutation_scale=20)

ax.add_patch(arr)

ax.annotate("label", (.5, .5), xycoords=arr, ha='center', va='bottom')

ax.set(xlim=(1, 2), ylim=(1, 2))



    

                                                                           

                                                                        

                                                                         

                                                                           

                                                    

                                       

 

 

                            

 

                        

                        

 

                                                                         

                                                                    

                        

 

                                                                            

                                  

                                                                            

                                                       

                                                                            

                                                                        

                                                                   

                                                   

 

                                                                       

                                          

                                                                            

 

                                                                       

                                                                   

                                                                  

                                                                    

                                                                       

                                                                    

                    



fig = plt.figure()

ax = fig.add_subplot(projection='polar')

r = np.arange(0, 1, 0.001)

theta = 2 * 2*np.pi * r

line, = ax.plot(theta, r, color='#ee8d18', lw=3)



ind = 800

thisr, thistheta = r[ind], theta[ind]

ax.plot([thistheta], [thisr], 'o')

ax.annotate('a polar annotation',

            xy=(thistheta, thisr),                 

            xytext=(0.05, 0.05),                        

            textcoords='figure fraction',

            arrowprops=dict(facecolor='black', shrink=0.05),

            horizontalalignment='left',

            verticalalignment='bottom')



    

                                                                           

 

                              

 

                                           

                                           

 

                                                                         

                                                                                

                         



fig, ax = plt.subplots(figsize=(3, 3))

x = [1, 3, 5, 7, 9]

y = [2, 4, 6, 8, 10]

annotations = ["A", "B", "C", "D", "E"]

ax.scatter(x, y, s=20)



for xi, yi, text in zip(x, y, annotations):

    ax.annotate(text,

                xy=(xi, yi), xycoords='data',

                xytext=(1.5, 1.5), textcoords='offset points')



    

                                                                               

 

                                

 

                     

                     

 

                                                                                   

                                                                      

 

                            

                            

 

                                                                             

       



fig, ax = plt.subplots(figsize=(5, 5))

t = ax.text(0.5, 0.5, "Direction",

            ha="center", va="center", rotation=45, size=15,

            bbox=dict(boxstyle="rarrow,pad=0.3",

                      fc="lightblue", ec="steelblue", lw=2))



    

                                                                    

                                                                     

 

                                                          

                                     

                                                          

                                       

                                       

                                       

                                       

                                       

                                                          

                                                          

                                                       

                                                       

                                       

                                                          

 

                                                                                   

                                                                

                   

 

                                                                         

 

                             

 

                                                           

                                                                     

                                                     

 

                                       

 

                                                                

                              

 

                                       

 

 

                            

                            

 

                                                                                    

                                                                                      

                                                                  

 

                                                                                

 

                                                  

                                                                



from matplotlib.path import Path





def custom_box_style(x0, y0, width, height, mutation_size):

    

             

    mypad = 0.3

    pad = mutation_size * mypad

                                          

    width = width + 2 * pad

    height = height + 2 * pad

                                

    x0, y0 = x0 - pad, y0 - pad

    x1, y1 = x0 + width, y0 + height

                         

    return Path([(x0, y0), (x1, y0), (x1, y1), (x0, y1),

                 (x0-pad, (y0+y1)/2), (x0, y0), (x0, y0)],

                closed=True)



fig, ax = plt.subplots(figsize=(3, 3))

ax.text(0.5, 0.5, "Test", size=30, va="center", ha="center", rotation=30,

        bbox=dict(boxstyle=custom_box_style, alpha=0.2))



    

                                                                          

               

 

                                                                            

                                                    

                                                                 

                                                                          

                       



from matplotlib.patches import BoxStyle





class MyStyle:

    



    def __init__(self, pad=0.3):

        

        self.pad = pad

        super().__init__()



    def __call__(self, x0, y0, width, height, mutation_size):

        

                 

        pad = mutation_size * self.pad

                                             

        width = width + 2 * pad

        height = height + 2 * pad

                                    

        x0, y0 = x0 - pad, y0 - pad

        x1, y1 = x0 + width, y0 + height

                             

        return Path([(x0, y0), (x1, y0), (x1, y1), (x0, y1),

                     (x0-pad, (y0+y1)/2), (x0, y0), (x0, y0)],

                    closed=True)





BoxStyle._style_list["angled"] = MyStyle                              



fig, ax = plt.subplots(figsize=(3, 3))

ax.text(0.5, 0.5, "Test", size=30, va="center", ha="center", rotation=30,

        bbox=dict(boxstyle="angled,pad=0.5", alpha=0.2))



del BoxStyle._style_list["angled"]                  



    

                                                                                        

                                                                   

 

                                   

 

                               

                               

 

                                                                 

                                                                  

                                     



fig, ax = plt.subplots(figsize=(3, 3))

ax.annotate("",

            xy=(0.2, 0.2), xycoords='data',

            xytext=(0.8, 0.8), textcoords='data',

            arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))



    

                                

 

                                                                     

                                 

                                                                             

         

                                                                       

                                                                               

               

 

           

                              

 

                                           

 

                       

                       

                    

                                            

                                                            

                                                                                 

                                                                               

                                                                                        

       

 

                                                                        

                                                                 

                                          

 

                                                                        

                           

 

                                                           

 

                      

                 

                                           

                                                 

                                                                                      

                                                                              

 

                                                                          

 

                                                                       

 

                                                                         

                                                                 

 

                                                            

                    

                                                            

                                         

                                 

                                                            

                      

                                                        

                                                            

 

                                                                        

                                                             

                                                                        

                                                         

 

                                                                          

                                                                             

                                                 

 

           

                                                 

 

                                              

                           

                           

 

                                          

                         

                                                   

                                                         

                                                                   

                                                           

                                                               

                                                                      

                                        

                       

 

                                                                

                                                              

 

                                                                                

 

                                                                          

                                                            

                                                            

                                              

                                               

                                                

                                                                    

                                                                    

                                                                   

                                                                                

                                                                                

                                                                               

                                                   

                                                    

                                                              

 

                        

                                                                       

 

                                                                       

                                                        

 

                                                            

                    

                                                            

                   

                                             

                                                 

                                    

                                             

                                             

                                             

                                             

                                             

                                                            

                                                            

                                               

                                                            

 

                                                                                          

                                                                       

                   

 

                                                                   

                                                                          

                                                                        

        

 

                                                                       

                         



fig, ax = plt.subplots(figsize=(3, 3))



ax.annotate("Test",

            xy=(0.2, 0.2), xycoords='data',

            xytext=(0.8, 0.8), textcoords='data',

            size=20, va="center", ha="center",

            arrowprops=dict(arrowstyle="simple",

                            connectionstyle="arc3,rad=-0.2"))



    

                                                                            

           



fig, ax = plt.subplots(figsize=(3, 3))



ann = ax.annotate("Test",

                  xy=(0.2, 0.2), xycoords='data',

                  xytext=(0.8, 0.8), textcoords='data',

                  size=20, va="center", ha="center",

                  bbox=dict(boxstyle="round4", fc="w"),

                  arrowprops=dict(arrowstyle="-|>",

                                  connectionstyle="arc3,rad=-0.2",

                                  fc="w"))



    

                                                                 

                                                                     

                                                                     

                                               



fig, ax = plt.subplots(figsize=(3, 3))



ann = ax.annotate("Test",

                  xy=(0.2, 0.2), xycoords='data',

                  xytext=(0.8, 0.8), textcoords='data',

                  size=20, va="center", ha="center",

                  bbox=dict(boxstyle="round4", fc="w"),

                  arrowprops=dict(arrowstyle="-|>",

                                  connectionstyle="arc3,rad=0.2",

                                  relpos=(0., 0.),

                                  fc="w"))



ann = ax.annotate("Test",

                  xy=(0.2, 0.2), xycoords='data',

                  xytext=(0.8, 0.8), textcoords='data',

                  size=20, va="center", ha="center",

                  bbox=dict(boxstyle="round4", fc="w"),

                  arrowprops=dict(arrowstyle="-|>",

                                  connectionstyle="arc3,rad=-0.2",

                                  relpos=(1., 0.),

                                  fc="w"))



    

                                           

                                           

 

                                                                

                                                                   

                                                                 

                                                                        

                                                  



from matplotlib.offsetbox import AnchoredText



fig, ax = plt.subplots(figsize=(3, 3))

at = AnchoredText("Figure 1a",

                  prop=dict(size=15), frameon=True, loc='upper left')

at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")

ax.add_artist(at)



    

                                                              

 

                                                                       

                                                                  

                                                                        

                                            

                                                                               

                                                                               

                                                                                 

                                                                           

                                             

 

                                                                  

                                                                   

                                                                        

                                                                    



from matplotlib.patches import Circle

from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea



fig, ax = plt.subplots(figsize=(3, 3))

ada = AnchoredDrawingArea(40, 20, 0, 0,

                          loc='upper right', pad=0., frameon=False)

p1 = Circle((10, 10), 10)

ada.drawing_area.add_artist(p1)

p2 = Circle((30, 10), 5, fc="r")

ada.drawing_area.add_artist(p2)

ax.add_artist(ada)



    

                                                                        

                                                    

                                                                            

                    

                                                                             

                                                                               

                      

 

                                                             

                                                              

                                                               



from matplotlib.patches import Ellipse

from mpl_toolkits.axes_grid1.anchored_artists import AnchoredAuxTransformBox



fig, ax = plt.subplots(figsize=(3, 3))

box = AnchoredAuxTransformBox(ax.transData, loc='upper left')

el = Ellipse((0, 0), width=0.1, height=0.4, angle=30)                        

box.drawing_area.add_artist(el)

ax.add_artist(box)



    

                                                                           

                                                                          

                                                                              

                            



from matplotlib.offsetbox import (AnchoredOffsetbox, DrawingArea, HPacker,

                                  TextArea)



fig, ax = plt.subplots(figsize=(3, 3))



box1 = TextArea(" Test: ", textprops=dict(color="k"))

box2 = DrawingArea(60, 20, 0, 0)



el1 = Ellipse((10, 10), width=16, height=5, angle=30, fc="r")

el2 = Ellipse((30, 10), width=16, height=5, angle=170, fc="g")

el3 = Ellipse((50, 10), width=16, height=5, angle=230, fc="b")

box2.add_artist(el1)

box2.add_artist(el2)

box2.add_artist(el3)



box = HPacker(children=[box1, box2],

              align="center",

              pad=0, sep=5)



anchored_box = AnchoredOffsetbox(loc='lower left',

                                 child=box, pad=0.,

                                 frameon=True,

                                 bbox_to_anchor=(0., 1.02),

                                 bbox_transform=ax.transAxes,

                                 borderpad=0.,)



ax.add_artist(anchored_box)

fig.subplots_adjust(top=0.8)



    

                                                                  

                                 

 

                                    

 

                                    

                                    

 

                                                                         

                                                                              

                                        

 

                       

                       

 

                                                                           

                                                                          

                                                                         

                                                                         

                                                                                

                                                                            



fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(6, 3))

ax1.annotate("Test", xy=(0.2, 0.2), xycoords=ax1.transAxes)

ax2.annotate("Test", xy=(0.2, 0.2), xycoords="axes fraction")



    

                                                                         

                                                                              

                                                                         

                                                                         

                       



x = np.linspace(-1, 1)



fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(6, 3))

ax1.plot(x, -x**3)

ax2.plot(x, -3*x**2)

ax2.annotate("",

             xy=(0, 0), xycoords=ax1.transData,

             xytext=(0, 0), textcoords=ax2.transData,

             arrowprops=dict(arrowstyle="<->"))



    

                              

 

                    

                    

 

                                                                               

                                    



fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(3, 3))

an1 = ax.annotate("Test 1",

                  xy=(0.5, 0.5), xycoords="data",

                  va="center", ha="center",

                  bbox=dict(boxstyle="round", fc="w"))



an2 = ax.annotate("Test 2",

                  xy=(1, 0.5), xycoords=an1,                          

                  xytext=(30, 0), textcoords="offset points",

                  va="center", ha="left",

                  bbox=dict(boxstyle="round", fc="w"),

                  arrowprops=dict(arrowstyle="->"))



    

                                                                              

                                                                          

                                                                           

                      

 

                                                   

                                                   

 

                                                                            

                                                                         

                                                                             

                               



fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(3, 3))

an1 = ax.annotate("Test 1",

                  xy=(0.5, 0.5), xycoords="data",

                  va="center", ha="center",

                  bbox=dict(boxstyle="round", fc="w"))



an2 = ax.annotate("Test 2",

                  xy=(1, 0.5), xycoords=an1.get_window_extent,

                  xytext=(30, 0), textcoords="offset points",

                  va="center", ha="left",

                  bbox=dict(boxstyle="round", fc="w"),

                  arrowprops=dict(arrowstyle="->"))



    

                                                                           

                                                                        



fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(6, 3))



an1 = ax1.annotate("Test1", xy=(0.5, 0.5), xycoords="axes fraction")

an2 = ax2.annotate("Test 2", xy=(0.5, 0.5), xycoords=ax2.get_window_extent)



    

                                  

                                  

 

                                                                  

                                                                             

                                                                 



fig, ax = plt.subplots(figsize=(3, 3))

ax.annotate("Test", xy=(0.5, 1), xycoords=("data", "axes fraction"))

ax.axvline(x=.5, color='lightgray')

ax.set(xlim=(0, 2), ylim=(1, 2))



    

                                                                  

                                                                        

                                      



fig, ax = plt.subplots(figsize=(3, 3))



t1 = ax.text(0.05, .05, "Text 1", va='bottom', ha='left')

t2 = ax.text(0.90, .90, "Text 2", ha='right')

t3 = ax.annotate("Anchored to 1 & 2", xy=(0, 0), xycoords=(t1, t2),

                 va='bottom', color='tab:orange',)



    

                    

                    

 

                                                                             

                                                                            

                          



from matplotlib.text import OffsetFrom



fig, ax = plt.subplots(figsize=(3, 3))

an1 = ax.annotate("Test 1", xy=(0.5, 0.5), xycoords="data",

                  va="center", ha="center",

                  bbox=dict(boxstyle="round", fc="w"))



offset_from = OffsetFrom(an1, (0.5, 0))

an2 = ax.annotate("Test 2", xy=(0.1, 0.1), xycoords="data",

                  xytext=(0, -10), textcoords=offset_from,

                                                                            

                  va="top", ha="center",

                  bbox=dict(boxstyle="round", fc="w"),

                  arrowprops=dict(arrowstyle="->"))



    

                      

                      

 

                            

 

                       

                       

 

                                                                                

                                                                              

                                                                             

                                                                               

             



from matplotlib.patches import ConnectionPatch



fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(6, 3))

xy = (0.3, 0.2)

con = ConnectionPatch(xyA=xy, coordsA=ax1.transData,

                      xyB=xy, coordsB=ax2.transData)



fig.add_artist(con)



    

                                                       

                                                                            

                                                                                

                                                                

                           

 

                          

                          

 

                                                                               

                           

 

                                                                                         

                                                                      

                   

 

                                

                                                                

                                             

                 

