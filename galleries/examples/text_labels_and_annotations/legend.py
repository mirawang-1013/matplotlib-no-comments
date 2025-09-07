





import matplotlib.pyplot as plt

import numpy as np



                      

a = b = np.arange(0, 3, .02)

c = np.exp(a)

d = c[::-1]



                                       

fig, ax = plt.subplots()

ax.plot(a, c, 'k--', label='Model length')

ax.plot(a, d, 'k:', label='Data length')

ax.plot(a, c + d, 'k', label='Total message length')



legend = ax.legend(loc='upper center', shadow=True, fontsize='x-large')



                                             

legend.get_frame().set_facecolor('C0')



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                             

                                                                 

 

              

 

                                                                                 

                         

