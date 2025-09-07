

import matplotlib.pyplot as plt

import numpy as np



x = np.linspace(0, 2 * np.pi, 100)

y = 2 * np.sin(x)



                                                                  

fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, layout='constrained')



ax0.plot(x, y)

ax0.set_title('normal spines')



ax1.plot(x, y)

ax1.set_title('bottom-left spines')



                               

ax1.spines.right.set_visible(False)

ax1.spines.top.set_visible(False)



ax2.plot(x, y)

ax2.set_title('spines with bounds limited to data range')



                                                         

ax2.spines.bottom.set_bounds(x.min(), x.max())

ax2.spines.left.set_bounds(y.min(), y.max())

                               

ax2.spines.right.set_visible(False)

ax2.spines.top.set_visible(False)



plt.show()



    

 

                            

 

                                                                              

                     

 

                                             

                                           

