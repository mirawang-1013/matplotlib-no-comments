

import matplotlib.pyplot as plt

import numpy as np



import matplotlib.ticker as mticker



                                         

rng = np.random.default_rng(seed=19680801)



    

                                            



fig, ax = plt.subplots()



data = rng.standard_normal((250, 250))



cax = ax.imshow(data, vmin=-1, vmax=1, cmap='coolwarm')

ax.set_title('Gaussian noise with vertical colorbar')



                                                                               

cbar = fig.colorbar(cax,

                    ticks=[-1, 0, 1],

                    format=mticker.FixedFormatter(['< -1', '0', '> 1']),

                    extend='both'

                    )

labels = cbar.ax.get_yticklabels()

labels[0].set_verticalalignment('top')

labels[-1].set_verticalalignment('bottom')



    

                                    



fig, ax = plt.subplots()



data = np.clip(data, -1, 1)



cax = ax.imshow(data, cmap='afmhot')

ax.set_title('Gaussian noise with horizontal colorbar')



                                          

cbar = fig.colorbar(cax, orientation='horizontal')

cbar.set_ticks(ticks=[-1, 0, 1], labels=['Low', 'Medium', 'High'])



plt.show()



    

 

                            

 

                                                                              

                     

 

                                               

                                                                         

