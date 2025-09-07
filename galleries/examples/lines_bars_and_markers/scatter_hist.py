



import matplotlib.pyplot as plt

import numpy as np



                                         

np.random.seed(19680801)



                  

x = np.random.randn(1000)

y = np.random.randn(1000)





def scatter_hist(x, y, ax, ax_histx, ax_histy):

               

    ax_histx.tick_params(axis="x", labelbottom=False)

    ax_histy.tick_params(axis="y", labelleft=False)



                       

    ax.scatter(x, y)



                                        

    binwidth = 0.25

    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))

    lim = (int(xymax/binwidth) + 1) * binwidth



    bins = np.arange(-lim, lim + binwidth, binwidth)

    ax_histx.hist(x, bins=bins)

    ax_histy.hist(y, bins=bins, orientation='horizontal')





    

                                                  

                                                  

 

                                                                           

                                                                               

                                                                      

                                                                      

                                                                              

                           



fig, axs = plt.subplot_mosaic([['histx', '.'],

                               ['scatter', 'histy']],

                              figsize=(6, 6),

                              width_ratios=(4, 1), height_ratios=(1, 4),

                              layout='constrained')

scatter_hist(x, y, axs['scatter'], axs['histx'], axs['histy'])





    

 

                                              

                                              

 

                                                                          

                                                                            

                                                                               

              



                                                   

fig = plt.figure(layout='constrained')

                       

ax = fig.add_subplot()

                                     

ax.set_aspect('equal')

                                                                               

                                                                           

                                                                             

                                                                            

                

ax_histx = ax.inset_axes([0, 1.05, 1, 0.25], sharex=ax)

ax_histy = ax.inset_axes([1.05, 0, 0.25, 1], sharey=ax)

                                      

scatter_hist(x, y, ax, ax_histx, ax_histy)



plt.show()





    

 

                                                                            

                                                   

 

                                                                     

                                         

                                               

                                                                                

                                                   

                                                                            

                                                    

                                                       

                                                           

 

                            

 

                                                                              

                     

 

                                                

                                         

                                             

                                        

                                     

                                  

 

           

 

                    

                       

                         

                        

