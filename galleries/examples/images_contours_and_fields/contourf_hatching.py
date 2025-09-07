

import matplotlib.pyplot as plt

import numpy as np



                                                             

                                                       

x = np.linspace(-3, 5, 150).reshape(1, -1)

y = np.linspace(-3, 5, 120).reshape(-1, 1)

z = np.cos(x) + np.sin(y)



                                                                 

x, y = x.flatten(), y.flatten()



    

                                                   



fig1, ax1 = plt.subplots()

cs = ax1.contourf(x, y, z, hatches=['-', '/', '\\', '//'],

                  cmap='gray', extend='both', alpha=0.5)

fig1.colorbar(cs)



    

                                                       



fig2, ax2 = plt.subplots()

n_levels = 6

ax2.contour(x, y, z, n_levels, colors='black', linestyles='-')

cs = ax2.contourf(x, y, z, n_levels, colors='none',

                  hatches=['.', '/', '\\', None, '\\\\', '*'],

                  extend='lower')



                                     

artists, labels = cs.legend_elements(str_format='{:2.1f}'.format)

ax2.legend(artists, labels, handleheight=2, framealpha=1)

plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                   

                                                                     

                                                                         

                                                                 

                                      

                                                      

