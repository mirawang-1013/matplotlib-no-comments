



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.cm as cm

from matplotlib.patches import Rectangle



fig, (ax1, ax2) = plt.subplots(1, 2)



                                                     

ax1.add_patch(Rectangle((0.1, 0.5), 0.8, 0.3, hatch=".", hatchcolor='red',

                        edgecolor='black', lw=2))

                                                                  

ax1.add_patch(Rectangle((0.1, 0.1), 0.8, 0.3, hatch='x', edgecolor='orange', lw=2))



x = np.arange(1, 5)

y = np.arange(1, 5)



ax2.bar(x, y, facecolor='none', edgecolor='red', hatch='//', hatchcolor='blue')

ax2.set_xlim(0, 5)

ax2.set_ylim(0, 5)



    

                       

                       

 

                                                                                       

                                                                               

                                                                                

                        



fig, ax = plt.subplots()



num_points_x = 10

num_points_y = 9

x = np.linspace(0, 1, num_points_x)

y = np.linspace(0, 1, num_points_y)



X, Y = np.meshgrid(x, y)

X[1::2, :] += (x[1] - x[0]) / 2                               



                                                                                

                                                                              

colors = [cm.rainbow(val) for val in x]



ax.scatter(

    X.ravel(),

    Y.ravel(),

    s=1700,

    facecolor="none",

    edgecolor="gray",

    linewidth=2,

    marker="h",                         

    hatch="xxx",

    hatchcolor=colors,

)

ax.set_xlim(0, 1)

ax.set_ylim(0, 1)



plt.show()



    

 

                            

 

                                                                              

                     

 

                           

                                   

                                       

                                                           

                               

                                                                   

