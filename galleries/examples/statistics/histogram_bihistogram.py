



import matplotlib.pyplot as plt

import numpy as np



                                                                        

rng = np.random.default_rng(19680801)



    

                                      

                                      

 

                                                                                  

                                                                                 

                                                                         



N_points = 10_000



                                   

dataset1 = np.random.normal(0, 1, size=N_points)

dataset2 = np.random.normal(1, 2, size=N_points)



                                                                                

bin_width = 0.25

bins = np.arange(np.min([dataset1, dataset2]),

                    np.max([dataset1, dataset2]) + bin_width, bin_width)



fig, ax = plt.subplots()



                          

ax.hist(dataset1, bins=bins, label="Dataset 1")



                           

                                                                     

ax.hist(dataset2, weights=-np.ones_like(dataset2), bins=bins, label="Dataset 2")

ax.axhline(0, color="k")

ax.legend()



plt.show()



    

 

                                                                       

