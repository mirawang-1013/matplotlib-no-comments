



import matplotlib.pyplot as plt

import numpy as np



import matplotlib.colorizer as mcolorizer

import matplotlib.colors as mcolors



np.random.seed(19680801)



datasets = [

    (i+1)/10 * np.random.rand(10, 20)

    for i in range(4)

]



fig, axs = plt.subplots(2, 2)

fig.suptitle('Multiple images')



                                                                          

norm = mcolors.Normalize(vmin=np.min(datasets), vmax=np.max(datasets))

colorizer = mcolorizer.Colorizer(norm=norm)



images = []

for ax, data in zip(axs.flat, datasets):

    images.append(ax.imshow(data, colorizer=colorizer))



fig.colorbar(images[0], ax=axs, orientation='horizontal', fraction=.1)



plt.show()



    

                                                                        

                                                                      

                                                                    

                                                                      

                                                                        

                                                 

 

                            

 

                                                                              

                     

 

                                                                 

                                                                         

                                       

                                    

