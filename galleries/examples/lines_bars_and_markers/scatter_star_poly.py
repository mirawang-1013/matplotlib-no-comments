

import matplotlib.pyplot as plt

import numpy as np



                                         

np.random.seed(19680801)



x = np.random.rand(10)

y = np.random.rand(10)

z = np.sqrt(x**2 + y**2)



fig, axs = plt.subplots(2, 3, sharex=True, sharey=True, layout="constrained")



                          

axs[0, 0].scatter(x, y, s=80, c=z, marker=">")

axs[0, 0].set_title("marker='>'")



                                                                

axs[0, 1].scatter(x, y, s=80, c=z, marker=r"$\clubsuit$")

axs[0, 1].set_title(r"marker=r'\$\clubsuit\$'")



                                                                              

verts = [[-1, -1], [1, -1], [1, 1], [-1, -1]]

axs[0, 2].scatter(x, y, s=80, c=z, marker=verts)

axs[0, 2].set_title("marker=verts")



                         

axs[1, 0].scatter(x, y, s=80, c=z, marker=(5, 0))

axs[1, 0].set_title("marker=(5, 0)")



                               

axs[1, 1].scatter(x, y, s=80, c=z, marker=(5, 1))

axs[1, 1].set_title("marker=(5, 1)")



                                   

axs[1, 2].scatter(x, y, s=80, c=z, marker=(5, 2))

axs[1, 2].set_title("marker=(5, 2)")



plt.show()



    

           

 

                      

                    

