



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.widgets import TextBox



fig, ax = plt.subplots()

fig.subplots_adjust(bottom=0.2)



t = np.arange(-2.0, 2.0, 0.001)

l, = ax.plot(t, np.zeros_like(t), lw=2)





def submit(expression):

    

    ydata = eval(expression, {'np': np}, {'t': t})

    l.set_ydata(ydata)

    ax.relim()

    ax.autoscale_view()

    plt.draw()





axbox = fig.add_axes((0.1, 0.05, 0.8, 0.075))

text_box = TextBox(axbox, "Evaluate", textalignment="center")

text_box.on_submit(submit)

text_box.set_val("t ** 2")                                             



plt.show()



    

 

                            

 

                                                                              

                     

 

                                   

