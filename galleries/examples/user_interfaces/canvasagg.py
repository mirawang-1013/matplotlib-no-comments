



from PIL import Image



import numpy as np



from matplotlib.backends.backend_agg import FigureCanvasAgg

from matplotlib.figure import Figure



fig = Figure(figsize=(5, 4), dpi=100)

                                                                              

                                                                      

           

canvas = FigureCanvasAgg(fig)



                   

ax = fig.add_subplot()

ax.plot([1, 2, 3])



                                                                               

        

fig.savefig("test.png")



                                                                             

              

canvas.draw()

rgba = np.asarray(canvas.buffer_rgba())

                         

im = Image.fromarray(rgba)

                                                                       

im.save("test.bmp")



                                                                              

           



    

 

                            

 

                                                                              

                     

 

                                                        

                                 

                                             

                                                                       

                                                             

