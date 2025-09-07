



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.ticker import AutoMinorLocator, MultipleLocator



t = np.arange(0.0, 100.0, 0.1)

s = np.sin(0.1 * np.pi * t) * np.exp(-t * 0.01)



fig, ax = plt.subplots()

ax.plot(t, s)



                                                                            

                                                                              

                                                                        

                        

ax.xaxis.set_major_locator(MultipleLocator(20))

ax.xaxis.set_major_formatter('{x:.0f}')



                                                            

ax.xaxis.set_minor_locator(MultipleLocator(5))



plt.show()



    

                                                     

 

                                                                               

                                                                            

                 

 

                                                                             

                                                                           

                                                  



t = np.arange(0.0, 100.0, 0.01)

s = np.sin(2 * np.pi * t) * np.exp(-t * 0.01)



fig, ax = plt.subplots()

ax.plot(t, s)



ax.xaxis.set_minor_locator(AutoMinorLocator())



ax.tick_params(which='both', width=2)

ax.tick_params(which='major', length=7)

ax.tick_params(which='minor', length=4, color='r')



plt.show()





    

 

                            

 

                                                                              

                     

 

                                   

                                                 

                                               

                                               

                                           

                                          

                                             

