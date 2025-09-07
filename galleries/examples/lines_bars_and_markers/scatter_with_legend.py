



import matplotlib.pyplot as plt

import numpy as np



np.random.seed(19680801)





fig, ax = plt.subplots()

for color in ['tab:blue', 'tab:orange', 'tab:green']:

    n = 750

    x, y = np.random.rand(2, n)

    scale = 200.0 * np.random.rand(n)

    ax.scatter(x, y, c=color, s=scale, label=color,

               alpha=0.3, edgecolors='none')



ax.legend()

ax.grid(True)



plt.show()





    

                              

 

                           

                           

 

                                                                  

                                                                         

                                                                               

                                                                              





N = 45

x, y = np.random.rand(2, N)

c = np.random.randint(1, 5, size=N)

s = np.random.randint(10, 220, size=N)



fig, ax = plt.subplots()



scatter = ax.scatter(x, y, c=c, s=s)



                                                          

legend1 = ax.legend(*scatter.legend_elements(),

                    loc="lower left", title="Classes")

ax.add_artist(legend1)



                                                                 

handles, labels = scatter.legend_elements(prop="sizes", alpha=0.6)

legend2 = ax.legend(handles, labels, loc="upper right", title="Sizes")



plt.show()





    

                                                                   

                                                                             

                                                                 



volume = np.random.rayleigh(27, size=40)

amount = np.random.poisson(10, size=40)

ranking = np.random.normal(size=40)

price = np.random.uniform(1, 10, size=40)



fig, ax = plt.subplots()



                                                                            

                                                                

scatter = ax.scatter(volume, amount, c=ranking, s=0.3*(price*3)**2,

                     vmin=-3, vmax=3, cmap="Spectral")



                                                                               

                                                         

legend1 = ax.legend(*scatter.legend_elements(num=5),

                    loc="upper left", title="Ranking")

ax.add_artist(legend1)



                                                                            

                                                                              

                                                                             

                                                                             

                                                                          

kw = dict(prop="sizes", num=5, color=scatter.cmap(0.7), fmt="$ {x:.2f}",

          func=lambda s: np.sqrt(s/.3)/3)

legend2 = ax.legend(*scatter.legend_elements(**kw),

                    loc="lower right", title="Price")



plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                   

                                                                 

                                                              

 

           

 

                      

                       

                        

