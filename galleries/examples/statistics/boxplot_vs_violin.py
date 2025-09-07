



import matplotlib.pyplot as plt

import numpy as np



fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))



                                         

np.random.seed(19680801)





                                

all_data = [np.random.normal(0, std, 100) for std in range(6, 10)]



                  

axs[0].violinplot(all_data,

                  showmeans=False,

                  showmedians=True)

axs[0].set_title('Violin plot')



               

axs[1].boxplot(all_data)

axs[1].set_title('Box plot')



                              

for ax in axs:

    ax.yaxis.grid(True)

    ax.set_xticks([y + 1 for y in range(len(all_data))],

                  labels=['x1', 'x2', 'x3', 'x4'])

    ax.set_xlabel('Four separate samples')

    ax.set_ylabel('Observed values')



plt.show()



    

 

                                                                     

 

                            

 

                                                                              

                     

 

                                                                   

                                                                         

