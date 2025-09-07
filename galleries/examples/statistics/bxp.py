

                                     



import matplotlib.pyplot as plt

import numpy as np



from matplotlib import cbook



np.random.seed(19680801)

data = np.random.randn(20, 3)



fig, (ax1, ax2) = plt.subplots(1, 2)



                     

ax1.boxplot(data, tick_labels=['A', 'B', 'C'],

            patch_artist=True, boxprops={'facecolor': 'bisque'})



                                                 

stats = cbook.boxplot_stats(data, labels=['A', 'B', 'C'])

ax2.bxp(stats, patch_artist=True, boxprops={'facecolor': 'bisque'})



    

                                                                                   

                                                                                    

 

                                                                                      

                                  



fig, ax = plt.subplots()



stats = [

    dict(med=0, q1=-1, q3=1, whislo=-2, whishi=2, fliers=[-4, -3, 3, 4], label='A'),

    dict(med=0, q1=-2, q3=2, whislo=-3, whishi=3, fliers=[], label='B'),

    dict(med=0, q1=-3, q3=3, whislo=-4, whishi=4, fliers=[], label='C'),

]



ax.bxp(stats, patch_artist=True, boxprops={'facecolor': 'bisque'})



plt.show()



    

 

                                                    

 

                            

 

                                                                              

                     

 

                                 

                                     

                                       

