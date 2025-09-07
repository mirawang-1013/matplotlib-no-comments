



import matplotlib.pyplot as plt



import matplotlib



fig = plt.figure()

ax = fig.add_subplot()

fig.subplots_adjust(top=0.85)



                                                        

fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')

ax.set_title('axes title')



ax.set_xlabel('xlabel')

ax.set_ylabel('ylabel')



                                                                    

ax.axis([0, 10, 0, 10])



ax.text(3, 8, 'boxed italics text in data coords', style='italic',

        bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})



ax.text(2, 6, r'an equation: $E=mc^2$', fontsize=15)



ax.text(3, 2, 'Unicode: Institut für Festkörperphysik')



ax.text(0.95, 0.01, 'colored text in axes coords',

        verticalalignment='bottom', horizontalalignment='right',

        transform=ax.transAxes,

        color='green', fontsize=15)



ax.plot([2], [1], 'o')

ax.annotate('annotate', xy=(2, 1), xytext=(3, 4),

            arrowprops=dict(facecolor='black', shrink=0.05))



plt.show()



    

                          

                          

 

                                                                         

                                                                           

          



import matplotlib.pyplot as plt

import numpy as np



x1 = np.linspace(0.0, 5.0, 100)

y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)



fig, ax = plt.subplots(figsize=(5, 3))

fig.subplots_adjust(bottom=0.15, left=0.2)

ax.plot(x1, y1)

ax.set_xlabel('Time (s)')

ax.set_ylabel('Damped oscillation (V)')



plt.show()



    

                                                                            

                                                                             

                                  



fig, ax = plt.subplots(figsize=(5, 3))

fig.subplots_adjust(bottom=0.15, left=0.2)

ax.plot(x1, y1*10000)

ax.set_xlabel('Time (s)')

ax.set_ylabel('Damped oscillation (V)')



plt.show()



    

                                                                        

                                                                           

              



fig, ax = plt.subplots(figsize=(5, 3))

fig.subplots_adjust(bottom=0.15, left=0.2)

ax.plot(x1, y1*10000)

ax.set_xlabel('Time (s)')

ax.set_ylabel('Damped oscillation (V)', labelpad=18)



plt.show()



    

                                                                               

                                                                             

                                                                             

                                                                           

                              



fig, ax = plt.subplots(figsize=(5, 3))

fig.subplots_adjust(bottom=0.15, left=0.2)

ax.plot(x1, y1)

ax.set_xlabel('Time (s)', position=(0., 1e6), horizontalalignment='left')

ax.set_ylabel('Damped oscillation (V)')



plt.show()



    

                                                                       

                                                                      

                                                  



from matplotlib.font_manager import FontProperties



font = FontProperties(family='Times New Roman', style='italic')



fig, ax = plt.subplots(figsize=(5, 3))

fig.subplots_adjust(bottom=0.15, left=0.2)

ax.plot(x1, y1)

ax.set_xlabel('Time (s)', fontsize='large', fontweight='bold')

ax.set_ylabel('Damped oscillation (V)', fontproperties=font)



plt.show()



    

                                                                       

                 



fig, ax = plt.subplots(figsize=(5, 3))

fig.subplots_adjust(bottom=0.2, left=0.2)

ax.plot(x1, np.cumsum(y1**2))

ax.set_xlabel('Time (s) \n This was a long experiment')

ax.set_ylabel(r'$\int\ Y^2\ dt\ \ (V^2 s)$')

plt.show()





    

        

        

 

                                                                     

                                                                           

                                  



fig, axs = plt.subplots(3, 1, figsize=(5, 6), tight_layout=True)

locs = ['center', 'left', 'right']

for ax, loc in zip(axs, locs):

    ax.plot(x1, y1)

    ax.set_title('Title with loc at ' + loc, loc=loc)

plt.show()



    

                                                                    

                                               



fig, ax = plt.subplots(figsize=(5, 3))

fig.subplots_adjust(top=0.8)

ax.plot(x1, y1)

ax.set_title('Vertically offset title', pad=30)

plt.show()





    

                      

                      

 

                                                                          

                                                                            

                                                                       

                                       

 

             

             

 

                                                                      

                                                                            

               

 

                                                             

                     

 

                                                         

                                                                              

                                                                               

                                                                              

                              

 

              

              

 

                                             

                                                                    

                                                                         

                                                                             

                                                                          

                                         



fig, axs = plt.subplots(2, 1, figsize=(5, 3), tight_layout=True)

axs[0].plot(x1, y1)

axs[1].plot(x1, y1)

axs[1].xaxis.set_ticks(np.arange(0., 8.1, 2.))

plt.show()



    

                                                                   

                                                                          

               



fig, axs = plt.subplots(2, 1, figsize=(5, 3), tight_layout=True)

axs[0].plot(x1, y1)

axs[1].plot(x1, y1)

ticks = np.arange(0., 8.1, 2.)

                                              

tickla = [f'{tick:1.2f}' for tick in ticks]

axs[1].xaxis.set_ticks(ticks)

axs[1].xaxis.set_ticklabels(tickla)

axs[1].set_xlim(axs[0].get_xlim())

plt.show()



    

                              

                              

 

                                                               

                                                                         

                                                                         

                                                      

                                                                         

                                                            



fig, axs = plt.subplots(2, 1, figsize=(5, 3), tight_layout=True)

axs[0].plot(x1, y1)

axs[1].plot(x1, y1)

ticks = np.arange(0., 8.1, 2.)

axs[1].xaxis.set_ticks(ticks)

axs[1].xaxis.set_major_formatter('{x:1.1f}')

axs[1].set_xlim(axs[0].get_xlim())

plt.show()



    

                                                                   

                                                                 

                                         



fig, axs = plt.subplots(2, 1, figsize=(5, 3), tight_layout=True)

axs[0].plot(x1, y1)

axs[1].plot(x1, y1)

locator = matplotlib.ticker.FixedLocator(ticks)

axs[1].xaxis.set_major_locator(locator)

axs[1].xaxis.set_major_formatter('±{x}°')

plt.show()



    

                                                                        

                                                                       

                                                                          

                                                               

                                                                     

                                                           

 

                                                                           

                                                             

                                                                    

                                                              

                                                               

                                    



fig, axs = plt.subplots(2, 2, figsize=(8, 5), tight_layout=True)

for n, ax in enumerate(axs.flat):

    ax.plot(x1*10., y1)



formatter = matplotlib.ticker.FormatStrFormatter('%1.1f')

locator = matplotlib.ticker.MaxNLocator(nbins='auto', steps=[1, 4, 10])

axs[0, 1].xaxis.set_major_locator(locator)

axs[0, 1].xaxis.set_major_formatter(formatter)



formatter = matplotlib.ticker.FormatStrFormatter('%1.5f')

locator = matplotlib.ticker.AutoLocator()

axs[1, 0].xaxis.set_major_formatter(formatter)

axs[1, 0].xaxis.set_major_locator(locator)



formatter = matplotlib.ticker.FormatStrFormatter('%1.5f')

locator = matplotlib.ticker.MaxNLocator(nbins=4)

axs[1, 1].xaxis.set_major_formatter(formatter)

axs[1, 1].xaxis.set_major_locator(locator)



plt.show()



    

                                                            

                                                   

                                                                 

                                                           





def formatoddticks(x, pos):

    

    if x % 2:

        return f'{x:1.2f}'

    else:

        return ''





fig, ax = plt.subplots(figsize=(5, 3), tight_layout=True)

ax.plot(x1, y1)

locator = matplotlib.ticker.MaxNLocator(nbins=6)

ax.xaxis.set_major_formatter(formatoddticks)

ax.xaxis.set_major_locator(locator)



plt.show()





    

           

           

 

                                                                  

                                                                 

                                                                  

                                                            

                                           

 

                                                                    

                                                    



import datetime



fig, ax = plt.subplots(figsize=(5, 3), tight_layout=True)

base = datetime.datetime(2017, 1, 1, 0, 0, 1)

time = [base + datetime.timedelta(days=x) for x in range(len(x1))]



ax.plot(time, y1)

ax.tick_params(axis='x', rotation=70)

plt.show()



    

                                                                              

                                                                          

                                                                             

                                              



import matplotlib.dates as mdates



locator = mdates.DayLocator(bymonthday=[1, 15])

formatter = mdates.DateFormatter('%b %d')



fig, ax = plt.subplots(figsize=(5, 3), tight_layout=True)

ax.xaxis.set_major_locator(locator)

ax.xaxis.set_major_formatter(formatter)

ax.plot(time, y1)

ax.tick_params(axis='x', rotation=70)

plt.show()



    

                         

                         

 

                       

                      

 

