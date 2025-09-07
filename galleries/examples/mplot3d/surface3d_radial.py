



import matplotlib.pyplot as plt

import numpy as np



fig = plt.figure()

ax = fig.add_subplot(projection='3d')



                                                                   

r = np.linspace(0, 1.25, 50)

p = np.linspace(0, 2*np.pi, 50)

R, P = np.meshgrid(r, p)

Z = ((R**2 - 1)**2)



                                           

X, Y = R*np.cos(P), R*np.sin(P)



                   

ax.plot_surface(X, Y, Z, cmap="YlGnBu_r")



                                             

ax.set_zlim(0, 1)

ax.set_xlabel(r'$\phi_\mathrm{real}$')

ax.set_ylabel(r'$\phi_\mathrm{im}$')

ax.set_zlabel(r'$V(\phi)$')



plt.show()



    

           

                                     

                    

