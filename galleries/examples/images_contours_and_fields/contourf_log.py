



import matplotlib.pyplot as plt

import numpy as np

from numpy import ma



from matplotlib import ticker



N = 100

x = np.linspace(-3.0, 3.0, N)

y = np.linspace(-2.0, 2.0, N)



X, Y = np.meshgrid(x, y)



                                     

                                                                            

                                      

Z1 = np.exp(-X**2 - Y**2)

Z2 = np.exp(-(X * 10)**2 - (Y * 10)**2)

z = Z1 + 50 * Z2



                                                                             

z[:5, :5] = -1



                                                                

                                                

z = ma.masked_where(z <= 0, z)





                                                  

                                                

fig, ax = plt.subplots()

cs = ax.contourf(X, Y, z, locator=ticker.LogLocator(), cmap="PuBu_r")



                                                

               

                                                    

                                                  

                              

                                                        



cbar = fig.colorbar(cs)



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                     

                                                                         

                                                                 

                                     

