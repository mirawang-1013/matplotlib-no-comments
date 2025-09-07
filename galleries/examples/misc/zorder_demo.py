



import matplotlib.pyplot as plt

import numpy as np



r = np.linspace(0.3, 1, 30)

theta = np.linspace(0, 4*np.pi, 30)

x = r * np.sin(theta)

y = r * np.cos(theta)



    

                                                                            

                                                                         

                                                                

                                                                          

                     



fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3.2))



ax1.plot(x, y, 'C3', lw=3)

ax1.scatter(x, y, s=120)

ax1.set_title('Lines on top of dots')



ax2.plot(x, y, 'C3', lw=3)

ax2.scatter(x, y, s=120, zorder=2.5)                            

ax2.set_title('Dots on top of lines')



plt.tight_layout()



    

                                                                             

                                                                           



x = np.linspace(0, 7.5, 100)

plt.rcParams['lines.linewidth'] = 5

plt.figure()

plt.plot(x, np.sin(x), label='zorder=2', zorder=2)          

plt.plot(x, np.sin(x+0.5), label='zorder=3',  zorder=3)

plt.axhline(0, label='zorder=2.5', color='lightgrey', zorder=2.5)

plt.title('Custom order of elements')

l = plt.legend(loc='upper right')

l.set_zorder(2.5)                                       

plt.show()

