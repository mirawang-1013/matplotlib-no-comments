

from datetime import datetime



import matplotlib.pyplot as plt

import numpy as np





def update_title(axes):

    axes.set_title(datetime.now())

    axes.figure.canvas.draw()



fig, ax = plt.subplots()



x = np.linspace(-3, 3)

ax.plot(x, x ** 2)



                                                                 

                                                                      

timer = fig.canvas.new_timer(interval=100)

timer.add_callback(update_title, ax)

timer.start()



                                                

                         

                   

                                       

                                                            



plt.show()

