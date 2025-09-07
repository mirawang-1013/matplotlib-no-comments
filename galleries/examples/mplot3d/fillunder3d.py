



import math



import matplotlib.pyplot as plt

import numpy as np



gamma = np.vectorize(math.gamma)

N = 31

x = np.linspace(0., 10., N)

lambdas = range(1, 9)



ax = plt.figure().add_subplot(projection='3d')



facecolors = plt.colormaps['viridis_r'](np.linspace(0, 1, len(lambdas)))



for i, l in enumerate(lambdas):

                                                                            

    ax.fill_between(x, l, l**x * np.exp(-l) / gamma(x + 1),

                    x, l, 0,

                    facecolors=facecolors[i], alpha=.7)



ax.set(xlim=(0, 10), ylim=(1, 9), zlim=(0, 0.35),

       xlabel='x', ylabel=r'$\lambda$', zlabel='probability')



plt.show()



    

           

                   

                             

                    

