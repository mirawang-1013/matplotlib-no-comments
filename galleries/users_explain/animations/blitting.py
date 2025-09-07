



import matplotlib.pyplot as plt

import numpy as np



x = np.linspace(0, 2 * np.pi, 100)



fig, ax = plt.subplots()



                                                                

                       

(ln,) = ax.plot(x, np.sin(x), animated=True)



                                                            

plt.show(block=False)



                                                                   

             

 

                                                                  

                                 

                                                              

                                                                

                                                                             

plt.pause(0.1)



                                                                             

bg = fig.canvas.copy_from_bbox(fig.bbox)

                                                       

ax.draw_artist(ln)

                                                                             

                                                 

fig.canvas.blit(fig.bbox)



for j in range(100):

                                                                     

    fig.canvas.restore_region(bg)

                                                                             

    ln.set_ydata(np.sin(x + (j / 100) * np.pi))

                                                                         

    ax.draw_artist(ln)

                                                                          

    fig.canvas.blit(fig.bbox)

                                                                    

    fig.canvas.flush_events()

                                                            

                   



    

                                                                     

                                                                     

                                                             

                                                                    

                                                               

                                                                    

                       

 

                     

                     

 

                                                                      

                                                                      

                                                                      

                                                              

                                      





class BlitManager:

    def __init__(self, canvas, animated_artists=()):

        

        self.canvas = canvas

        self._bg = None

        self._artists = []



        for a in animated_artists:

            self.add_artist(a)

                                           

        self.cid = canvas.mpl_connect("draw_event", self.on_draw)



    def on_draw(self, event):

        

        cv = self.canvas

        if event is not None:

            if event.canvas != cv:

                raise RuntimeError

        self._bg = cv.copy_from_bbox(cv.figure.bbox)

        self._draw_animated()



    def add_artist(self, art):

        

        if art.figure != self.canvas.figure:

            raise RuntimeError

        art.set_animated(True)

        self._artists.append(art)



    def _draw_animated(self):

        

        fig = self.canvas.figure

        for a in self._artists:

            fig.draw_artist(a)



    def update(self):

        

        cv = self.canvas

        fig = cv.figure

                                                    

        if self._bg is None:

            self.on_draw(None)

        else:

                                    

            cv.restore_region(self._bg)

                                              

            self._draw_animated()

                                  

            cv.blit(fig.bbox)

                                                              

        cv.flush_events()





    

                                                                          

                                                                     



                   

fig, ax = plt.subplots()

            

(ln,) = ax.plot(x, np.sin(x), animated=True)

                    

fr_number = ax.annotate(

    "0",

    (0, 1),

    xycoords="axes fraction",

    xytext=(10, -10),

    textcoords="offset points",

    ha="left",

    va="top",

    animated=True,

)

bm = BlitManager(fig.canvas, [ln, fr_number])

                                                 

plt.show(block=False)

plt.pause(.1)



for j in range(100):

                        

    ln.set_ydata(np.sin(x + (j / 100) * np.pi))

    fr_number.set_text(f"frame: {j}")

                                               

    bm.update()



    

                                                                  

                              

