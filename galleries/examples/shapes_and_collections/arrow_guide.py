



import matplotlib.pyplot as plt



import matplotlib.patches as mpatches



x_tail = 0.1

y_tail = 0.5

x_head = 0.9

y_head = 0.8

dx = x_head - x_tail

dy = y_head - y_tail





    

                                                                         

                                                                         

 

                                                                       

                                                           

 

                                                 

 

                                                                             

                             



fig, axs = plt.subplots(nrows=2)

arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),

                                 mutation_scale=100)

axs[0].add_patch(arrow)



arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),

                                 mutation_scale=100)

axs[1].add_patch(arrow)

axs[1].set(xlim=(0, 2), ylim=(0, 2))



    

                                                     

                                                     

 

                                                                          

                                                        

 

                                                                               

                                                                             

     

 

                                                                          

                



fig, axs = plt.subplots(nrows=2)

arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),

                                 mutation_scale=100,

                                 transform=axs[0].transAxes)

axs[0].add_patch(arrow)



arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),

                                 mutation_scale=100,

                                 transform=axs[1].transAxes)

axs[1].add_patch(arrow)

axs[1].set(xlim=(0, 2), ylim=(0, 2))





    

                                                  

                                                  

 

                                                                               

             

 

                                                                          

         

 

                                                                               

                                                                            

                                                                            

                                                       



fig, axs = plt.subplots(nrows=2)



arrow = mpatches.Arrow(x_tail, y_tail, dx, dy)

axs[0].add_patch(arrow)

arrow = mpatches.FancyArrow(x_tail, y_tail - .4, dx, dy,

                            width=.1, length_includes_head=True, color="C1")

axs[0].add_patch(arrow)

axs[0].arrow(x_tail + 1, y_tail - .4, dx, dy,

             width=.1, length_includes_head=True, color="C2")



arrow = mpatches.Arrow(x_tail, y_tail, dx, dy)

axs[1].add_patch(arrow)

arrow = mpatches.FancyArrow(x_tail, y_tail - .4, dx, dy,

                            width=.1, length_includes_head=True, color="C1")

axs[1].add_patch(arrow)

axs[1].arrow(x_tail + 1, y_tail - .4, dx, dy,

             width=.1, length_includes_head=True, color="C2")

axs[1].set(xlim=(0, 2), ylim=(0, 2))



    



plt.show()

