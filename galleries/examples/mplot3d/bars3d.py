



import matplotlib.pyplot as plt

import numpy as np



                                         

np.random.seed(19680801)





fig = plt.figure()

ax = fig.add_subplot(projection='3d')



colors = ['r', 'g', 'b', 'y']

yticks = [3, 2, 1, 0]

for c, k in zip(colors, yticks):

                                                   

    xs = np.arange(20)

    ys = np.random.rand(20)



                                                                               

                                                                              

    cs = [c] * len(xs)

    cs[0] = 'c'



                                                                              

    ax.bar(xs, ys, zs=k, zdir='y', color=cs, alpha=0.8)



ax.set_xlabel('X')

ax.set_ylabel('Y')

ax.set_zlabel('Z')



                                                                           

ax.set_yticks(yticks)



plt.show()



    

           

                                   

                    

                    

