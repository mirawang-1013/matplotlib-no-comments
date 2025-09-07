



                                      



import matplotlib.pyplot as plt

import numpy as np



                              

x = np.linspace(0, 2 * np.pi, 400)

y = np.sin(x ** 2)



    

                                

                                

 

                                                                   

                

 

                                                                        

                  



fig, ax = plt.subplots()

ax.plot(x, y)

ax.set_title('A single plot')



    

                                    

                                    

 

                                                                             

                                       

 

                                                                               

                                      



fig, axs = plt.subplots(2)

fig.suptitle('Vertically stacked subplots')

axs[0].plot(x, y)

axs[1].plot(x, -y)



    

                                                                               

                                                                            

                              



fig, (ax1, ax2) = plt.subplots(2)

fig.suptitle('Vertically stacked subplots')

ax1.plot(x, y)

ax2.plot(x, -y)



    

                                                                               

          



fig, (ax1, ax2) = plt.subplots(1, 2)

fig.suptitle('Horizontally stacked subplots')

ax1.plot(x, y)

ax2.plot(x, -y)



    

                                     

                                     

 

                                                                            

 

                                                                           

                                                          



fig, axs = plt.subplots(2, 2)

axs[0, 0].plot(x, y)

axs[0, 0].set_title('Axis [0, 0]')

axs[0, 1].plot(x, y, 'tab:orange')

axs[0, 1].set_title('Axis [0, 1]')

axs[1, 0].plot(x, -y, 'tab:green')

axs[1, 0].set_title('Axis [1, 0]')

axs[1, 1].plot(x, -y, 'tab:red')

axs[1, 1].set_title('Axis [1, 1]')



for ax in axs.flat:

    ax.set(xlabel='x-label', ylabel='y-label')



                                                                          

for ax in axs.flat:

    ax.label_outer()



    

                                                                            

            



fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

fig.suptitle('Sharing x per column, y per row')

ax1.plot(x, y)

ax2.plot(x, y**2, 'tab:orange')

ax3.plot(x, -y, 'tab:green')

ax4.plot(x, -y**2, 'tab:red')



for ax in fig.get_axes():

    ax.label_outer()



    

              

              

 

                                                                       

                                                         



fig, (ax1, ax2) = plt.subplots(2)

fig.suptitle('Axes values are scaled individually by default')

ax1.plot(x, y)

ax2.plot(x + 1, -y)



    

                                                                            



fig, (ax1, ax2) = plt.subplots(2, sharex=True)

fig.suptitle('Aligning x-axis using sharex')

ax1.plot(x, y)

ax2.plot(x + 1, -y)



    

                                                                            

                                                                          

                                        



fig, axs = plt.subplots(3, sharex=True, sharey=True)

fig.suptitle('Sharing both axes')

axs[0].plot(x, y ** 2)

axs[1].plot(x, 0.3 * y, 'o')

axs[2].plot(x, y, '+')



    

                                                                           

                                                                          

                                                                 

 

                                                                          

                                                                     

                                                                          

                                                             

 

                                                                           

                                       



fig = plt.figure()

gs = fig.add_gridspec(3, hspace=0)

axs = gs.subplots(sharex=True, sharey=True)

fig.suptitle('Sharing both axes')

axs[0].plot(x, y ** 2)

axs[1].plot(x, 0.3 * y, 'o')

axs[2].plot(x, y, '+')



                                                        

for ax in axs:

    ax.label_outer()



    

                                                                          

                                                                    



fig = plt.figure()

gs = fig.add_gridspec(2, 2, hspace=0, wspace=0)

(ax1, ax2), (ax3, ax4) = gs.subplots(sharex='col', sharey='row')

fig.suptitle('Sharing x per column, y per row')

ax1.plot(x, y)

ax2.plot(x, y**2, 'tab:orange')

ax3.plot(x + 1, -y, 'tab:green')

ax4.plot(x + 2, -y**2, 'tab:red')



for ax in fig.get_axes():

    ax.label_outer()



    

                                                                        

                                                                    

                                                       



fig, axs = plt.subplots(2, 2)

axs[0, 0].plot(x, y)

axs[0, 0].set_title("main")

axs[1, 0].plot(x, y**2)

axs[1, 0].set_title("shares x with main")

axs[1, 0].sharex(axs[0, 0])

axs[0, 1].plot(x + 1, y + 1)

axs[0, 1].set_title("unrelated")

axs[1, 1].plot(x + 2, y + 2)

axs[1, 1].set_title("also unrelated")

fig.tight_layout()



    

            

            

 

                                                                       

                                                                              

                                 



fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw=dict(projection='polar'))

ax1.plot(x, y)

ax2.plot(x, y ** 2)



plt.show()



    

           

 

                        

                     

                    

                     

                     

                    

                      

