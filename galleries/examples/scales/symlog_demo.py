

import matplotlib.pyplot as plt

import numpy as np



dt = 0.01

x = np.arange(-50.0, 50.0, dt)

y = np.arange(0, 100.0, dt)



fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)



ax0.plot(x, y)

ax0.set_xscale('symlog')

ax0.set_ylabel('symlogx')

ax0.grid()

ax0.xaxis.grid(which='minor')                     



ax1.plot(y, x)

ax1.set_yscale('symlog')

ax1.set_ylabel('symlogy')



ax2.plot(x, np.sin(x / 3.0))

ax2.set_xscale('symlog')

ax2.set_yscale('symlog', linthresh=0.015)

ax2.grid()

ax2.set_ylabel('symlog both')



fig.tight_layout()

plt.show()



    

                  

                  

                                                                                 

                                                                                   

                                                              

                                                                                  





def format_axes(ax, title=None):

    

    ax.xaxis.get_minor_locator().set_params(subs=[2, 3, 4, 5, 6, 7, 8, 9])

    ax.grid()

    ax.xaxis.grid(which='minor')                     

    linthresh = ax.xaxis.get_transform().linthresh

    linscale = ax.xaxis.get_transform().linscale

    ax.axvspan(-linthresh, linthresh, color='0.9')

    if title:

        ax.set_title(title.format(linthresh=linthresh, linscale=linscale))





x = np.linspace(-60, 60, 201)

y = np.linspace(0, 100.0, 201)



fig, (ax1, ax2) = plt.subplots(nrows=2, layout="constrained")



ax1.plot(x, y)

ax1.set_xscale('symlog', linthresh=1)

format_axes(ax1, title='Linear region: linthresh={linthresh}')



ax2.plot(x, y)

ax2.set_xscale('symlog', linthresh=5)

format_axes(ax2, title='Linear region: linthresh={linthresh}')



    

                                                                  

                                                           

                                             

 

 

              

              

                                                                                   

                                                                                 

                                                      



fig, (ax1, ax2) = plt.subplots(nrows=2, layout="constrained")



ax1.plot(x, y)

ax1.set_xscale('symlog', linthresh=1)

format_axes(ax1, title='Linear region: linthresh={linthresh}, linscale={linscale}')



ax2.plot(x, y)

ax2.set_xscale('symlog', linthresh=1, linscale=0.1)

format_axes(ax2, title='Linear region: linthresh={linthresh}, linscale={linscale}')



    

                                                                                    

                                                                                  

                                      

 

                              

                              

                                                                                 

                                                                              

                                                         



fig, ax = plt.subplots()

ax.plot(x, y)

ax.set_xscale('symlog', linscale=0.05)

format_axes(ax, title="Discontinuous gradient at linear/log transition")



    

                                                                                

                                                                                

                                        

 

 

                            

 

                                             

                                                

                                    

