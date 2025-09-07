



import matplotlib.pyplot as plt

import numpy as np



                         

N = 37

x, y = np.mgrid[:N, :N]

Z = (np.cos(x*0.2) + np.sin(y*0.3))



                                                         

Zpos = np.ma.masked_less(Z, 0)

Zneg = np.ma.masked_greater(Z, 0)



fig, (ax1, ax2, ax3) = plt.subplots(figsize=(13, 3), ncols=3)



                                          

                                                

pos = ax1.imshow(Zpos, cmap='Blues', interpolation='none')



                                             

                                                

                                     

fig.colorbar(pos, ax=ax1)



                                               

                                                          

neg = ax2.imshow(Zneg, cmap='Reds_r', interpolation='none')

fig.colorbar(neg, ax=ax2, location='right', anchor=(0, 0.3), shrink=0.7)



                                                        

pos_neg_clipped = ax3.imshow(Z, cmap='RdBu', vmin=-1.2, vmax=1.2,

                             interpolation='none')

                                                            

                          

cbar = fig.colorbar(pos_neg_clipped, ax=ax3, extend='both')

cbar.minorticks_on()

plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                 

                                                                         

                                                   

                                                    

 

           

 

                        

                   

                      

                    

