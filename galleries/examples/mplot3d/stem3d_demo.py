



import matplotlib.pyplot as plt

import numpy as np



theta = np.linspace(0, 2*np.pi)

x = np.cos(theta - np.pi/2)

y = np.sin(theta - np.pi/2)

z = theta



fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

ax.stem(x, y, z)



plt.show()



    

 

                                                                            

                                                                              

                                                                             

                                                                              

                                                                 



fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

markerline, stemlines, baseline = ax.stem(

    x, y, z, linefmt='grey', markerfmt='D', bottom=np.pi)

markerline.set_markerfacecolor('none')



plt.show()



    

 

                                                                               

                                                                          

                                        

 

                                                                             

                                                           



fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

markerline, stemlines, baseline = ax.stem(x, y, z, bottom=-1, orientation='x')

ax.set(xlabel='x', ylabel='y', zlabel='z')



plt.show()



    

           

                                         

                    

