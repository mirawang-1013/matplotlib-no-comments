

import matplotlib.pyplot as plt

import numpy as np



r = np.arange(0, 2, 0.01)

theta = 2 * np.pi * r



fig, axs = plt.subplots(2, 1, figsize=(5, 8), subplot_kw={'projection': 'polar'},

                        layout='constrained')

ax = axs[0]

ax.plot(theta, r)

ax.set_rmax(2)

ax.set_rticks([0.5, 1, 1.5, 2])                      

ax.set_rlabel_position(-22.5)                                             

ax.grid(True)



ax.set_title("A line plot on a polar axis", va='bottom')



ax = axs[1]

ax.plot(theta, r)

ax.set_rmax(2)

ax.set_rmin(1)                                                 

ax.set_rorigin(0)                                          

ax.set_thetamin(0)

ax.set_thetamax(225)

ax.set_rticks([1, 1.5, 2])                      

ax.set_rlabel_position(-22.5)                                             



ax.grid(True)

ax.set_title("Same plot, but with reduced axis limits", va='bottom')

plt.show()



    

 

                            

 

                                                                              

                     

 

                                                             

                                     

                                               

                                                          

                                                        

                                                           

                                                        

                                                                   

 

           

 

                     

                    

