



import matplotlib.pyplot as plt

import numpy as np



fig, axs = plt.subplots(2, 3, figsize=(8.9, 5.5),

                        layout='constrained', gridspec_kw={'wspace': 0.1})



                            

for ax in axs.flat:

    scale = 2000 if ax.get_subplotspec().is_first_row() else 1

    ax.plot(scale * (1 - np.exp(-np.linspace(0, 5, 100))))

    if ax.get_subplotspec().is_last_row():

        ax.set_xlabel('xlabel', bbox=dict(facecolor='yellow', pad=5, alpha=0.2))

    ax.set_ylabel('ylabel', bbox=dict(facecolor='yellow', pad=5, alpha=0.2))

    ax.set_ylim(0, scale)



                                                     

axs[0, 0].xaxis.tick_top()

axs[1, 2].tick_params(axis='x', rotation=55)

axs[0, 0].set_title('ylabels not aligned')



              

fig.align_titles()                          

fig.align_xlabels()                                    

fig.align_ylabels(axs[:, 1])                                           

axs[0, 1].set_title('fig.align_ylabels()')



                                               

for ax in axs[:, 2]:

    ax.yaxis.set_label_coords(-0.3, 0.5)

axs[0, 2].set_title('ylabels manually aligned')



plt.show()





    

 

                            

 

                                                                              

                     

 

                                               

                                               

                                              

                                              

                                              

                                                             

                                       

                                        

                                      



    

           

 

                     

                     

                      

                    

