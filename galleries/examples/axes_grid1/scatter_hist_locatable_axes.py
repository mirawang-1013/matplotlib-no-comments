



import matplotlib.pyplot as plt

import numpy as np



from mpl_toolkits.axes_grid1 import make_axes_locatable



                                         

np.random.seed(19680801)



                 

x = np.random.randn(1000)

y = np.random.randn(1000)





fig, ax = plt.subplots(figsize=(5.5, 5.5))



                   

ax.scatter(x, y)



                              

ax.set_aspect(1.)



                                                                 

divider = make_axes_locatable(ax)

                                    

ax_histx = divider.append_axes("top", 1.2, pad=0.1, sharex=ax)

ax_histy = divider.append_axes("right", 1.2, pad=0.1, sharey=ax)



                            

ax_histx.xaxis.set_tick_params(labelbottom=False)

ax_histy.yaxis.set_tick_params(labelleft=False)



                                    

binwidth = 0.25

xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))

lim = (int(xymax/binwidth) + 1)*binwidth



bins = np.arange(-lim, lim + binwidth, binwidth)

ax_histx.hist(x, bins=bins)

ax_histy.hist(y, bins=bins, orientation='horizontal')



                                                                 

                                                                     

       



ax_histx.set_yticks([0, 50, 100])

ax_histy.set_xticks([0, 50, 100])



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                 

                                        

                                     

                                  

