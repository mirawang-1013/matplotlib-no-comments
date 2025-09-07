



import matplotlib.pyplot as plt

import numpy as np



                                         

np.random.seed(19680801)



fig, ax = plt.subplots()

ax.plot(100*np.random.rand(20))



                                  

ax.yaxis.set_major_formatter('${x:1.2f}')



ax.yaxis.set_tick_params(which='major', labelcolor='green',

                         labelleft=False, labelright=True)



plt.show()





    

 

                            

 

                                                                              

                     

 

                                   

                                                 

                                             

                             

                                             

