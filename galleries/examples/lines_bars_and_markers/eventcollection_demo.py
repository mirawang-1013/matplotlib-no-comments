



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.collections import EventCollection



                                         

np.random.seed(19680801)



                    

xdata = np.random.random([2, 10])



                               

xdata1 = xdata[0, :]

xdata2 = xdata[1, :]



                                        

xdata1.sort()

xdata2.sort()



                           

ydata1 = xdata1 ** 2

ydata2 = 1 - xdata2 ** 3



               

fig = plt.figure()

ax = fig.add_subplot(1, 1, 1)

ax.plot(xdata1, ydata1, color='tab:blue')

ax.plot(xdata2, ydata2, color='tab:orange')



                                             

xevents1 = EventCollection(xdata1, color='tab:blue', linelength=0.05)

xevents2 = EventCollection(xdata2, color='tab:orange', linelength=0.05)



                                             

yevents1 = EventCollection(ydata1, color='tab:blue', linelength=0.05,

                           orientation='vertical')

yevents2 = EventCollection(ydata2, color='tab:orange', linelength=0.05,

                           orientation='vertical')



                            

ax.add_collection(xevents1)

ax.add_collection(xevents2)

ax.add_collection(yevents1)

ax.add_collection(yevents2)



                

ax.set_xlim(0, 1)

ax.set_ylim(0, 1)



ax.set_title('line plot with data points')



                  

plt.show()



    

           

 

                         

                        

