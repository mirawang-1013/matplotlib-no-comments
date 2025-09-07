



import matplotlib.pyplot as plt

import numpy as np



np.random.seed(19680801)

fruit_weights = [

    np.random.normal(130, 10, size=100),

    np.random.normal(125, 20, size=100),

    np.random.normal(120, 30, size=100),

]

labels = ['peaches', 'oranges', 'tomatoes']

colors = ['peachpuff', 'orange', 'tomato']



fig, ax = plt.subplots()

ax.set_ylabel('fruit weight (g)')



bplot = ax.boxplot(fruit_weights,

                   patch_artist=True,                   

                   tick_labels=labels)                                 



                  

for patch, color in zip(bplot['boxes'], colors):

    patch.set_facecolor(color)



plt.show()



    

 

                                                                  

 

                            

 

                                                                              

                     

 

                                                                   

