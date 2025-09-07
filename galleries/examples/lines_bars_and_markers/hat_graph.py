

import matplotlib.pyplot as plt

import numpy as np





def hat_graph(ax, xlabels, values, group_labels):

    



    values = np.asarray(values)

    color_cycle_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']



                   

    bars = ax.grouped_bar(

        (values - values[0]).T, bottom=values[0], tick_labels=xlabels,

        labels=group_labels, edgecolor='black', group_spacing=0.8,

        colors=['none'] + color_cycle_colors)



                                            

    for bc, heights in zip(bars.bar_containers, values):

        ax.bar_label(bc, heights, padding=4)





                                                        

                                             

xlabels = ['I', 'II', 'III', 'IV', 'V']

playerA = np.array([5, 15, 22, 20, 25])

playerB = np.array([25, 32, 34, 30, 27])



fig, ax = plt.subplots(layout='constrained')



hat_graph(ax, xlabels, [playerA, playerB], ['Player A', 'Player B'])



                                                                     

ax.set_xlabel('Games')

ax.set_ylabel('Score')

ax.set_ylim(0, 60)

ax.set_title('Scores by number of game and players')

ax.legend()



plt.show()

    

 

                            

 

                                                                              

                     

 

                                                                           

                                                                       

 

           

 

                          

                   

                    

