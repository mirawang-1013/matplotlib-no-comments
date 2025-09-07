



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.collections import PatchCollection

from matplotlib.patches import Rectangle



                       

n = 5



            

np.random.seed(19680801)

x = np.arange(0, n, 1)

y = np.random.rand(n) * 5.



                                

xerr = np.random.rand(2, n) + 0.1

yerr = np.random.rand(2, n) + 0.2





def make_error_boxes(ax, xdata, ydata, xerror, yerror, facecolor='r',

                     edgecolor='none', alpha=0.5):



                                                                 

    errorboxes = [Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum())

                  for x, y, xe, ye in zip(xdata, ydata, xerror.T, yerror.T)]



                                                         

    pc = PatchCollection(errorboxes, facecolor=facecolor, alpha=alpha,

                         edgecolor=edgecolor)



                            

    ax.add_collection(pc)



                    

    artists = ax.errorbar(xdata, ydata, xerr=xerror, yerr=yerror,

                          fmt='none', ecolor='k')



    return artists





                        

fig, ax = plt.subplots(1)



                                     

_ = make_error_boxes(ax, x, y, xerr, yerr)



plt.show()



    

 

 

           

 

                        

                         

                               

                       

 

                            

 

                                                                              

                     

 

                                                                     

                                            

                                               

