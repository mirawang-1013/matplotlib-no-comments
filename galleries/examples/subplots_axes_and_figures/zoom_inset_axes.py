



import numpy as np



from matplotlib import cbook

from matplotlib import pyplot as plt



fig, ax = plt.subplots()



           

Z = cbook.get_sample_data("axes_grid/bivariate_normal.npy")               

Z2 = np.zeros((150, 150))

ny, nx = Z.shape

Z2[30:30+ny, 30:30+nx] = Z

extent = (-3, 4, -4, 3)



ax.imshow(Z2, extent=extent, origin="lower")



                

x1, x2, y1, y2 = -1.5, -0.9, -2.5, -1.9                                   

axins = ax.inset_axes(

    [0.5, 0.5, 0.47, 0.47],

    xlim=(x1, x2), ylim=(y1, y2), xticklabels=[], yticklabels=[])

axins.imshow(Z2, extent=extent, origin="lower")



ax.indicate_inset_zoom(axins, edgecolor="black")



plt.show()



    

 

                            

 

                                                                              

                     

 

                                        

                                                 

                                    

 

           

 

                    

                      

                        

