



import matplotlib.pyplot as plt

import numpy as np



import matplotlib as mpl



n_lines = 21

cmap = mpl.colormaps['plasma']



                                                         

colors = cmap(np.linspace(0, 1, n_lines))



fig, ax = plt.subplots(layout='constrained')



for i, color in enumerate(colors):

    ax.plot([0, i], color=color)



plt.show()



    

 

                                            

                                            

                                                                              

                                                                               

                                                                              

                                                                          



colors = mpl.colormaps['Dark2'].colors



fig, ax = plt.subplots(layout='constrained')



for i, color in enumerate(colors):

    ax.plot([0, i], color=color)



plt.show()



    

          

          

 

                                                                                      

                                                         

 

                            

 

                                                                              

                     

 

                                   

                                             

 

           

 

                      

                   

                    

                        

