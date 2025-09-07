



import matplotlib.pyplot as plt

import numpy as np



from matplotlib import colors

from matplotlib.ticker import PercentFormatter



                                                                        

rng = np.random.default_rng(19680801)



    

                                           

                                           

 

                                                                              

                                                                           

                                



N_points = 100000

n_bins = 20



                                   

dist1 = rng.standard_normal(N_points)

dist2 = 0.4 * rng.standard_normal(N_points) + 5



fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)



                                                                 

axs[0].hist(dist1, bins=n_bins)

axs[1].hist(dist2, bins=n_bins)



plt.show()





    

                           

                           

 

                                                                              

                                                                            

                                                                      

                       



fig, axs = plt.subplots(1, 2, tight_layout=True)



                                                                

N, bins, patches = axs[0].hist(dist1, bins=n_bins)



                                                          

fracs = N / N.max()



                                                                          

norm = colors.Normalize(fracs.min(), fracs.max())



                                                                           

for thisfrac, thispatch in zip(fracs, patches):

    color = plt.colormaps["viridis"](norm(thisfrac))

    thispatch.set_facecolor(color)



                                                                

axs[1].hist(dist1, bins=n_bins, density=True)



                                                

axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))





    

                     

                     

 

                                                                        

                                              



fig, ax = plt.subplots(tight_layout=True)

hist = ax.hist2d(dist1, dist2)





    

                            

                            

 

                                                                       

                                                                



fig, axs = plt.subplots(3, 1, figsize=(5, 15), sharex=True, sharey=True,

                        tight_layout=True)



                                                 

axs[0].hist2d(dist1, dist2, bins=40)



                                               

axs[1].hist2d(dist1, dist2, bins=40, norm=colors.LogNorm())



                                                         

axs[2].hist2d(dist1, dist2, bins=(80, 10), norm=colors.LogNorm())



    

 

           

 

                          

                           

                       

                    

                             

                     

 

                            

 

                                                                              

                     

 

                                                             

                                 

                                           

