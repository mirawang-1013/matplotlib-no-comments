



import matplotlib.pyplot as plt

import numpy as np



np.random.seed(19680801)



fig, ax = plt.subplots()

dots = np.linspace(0.3, 1.2, 10)

X, Y = np.meshgrid(dots, dots)

x, y = X.ravel(), Y.ravel()

ax.scatter(x, y, c=x+y)

plt.show()



    

                                                                              

                                                                               

                                       



plt.rcParams['axes.autolimit_mode'] = 'round_numbers'



                                                                     

                                                                      

                                               



fig, ax = plt.subplots()

ax.scatter(x, y, c=x+y)

plt.show()



    

                                                                              

                                                                         



fig, ax = plt.subplots()

ax.scatter(x, y, c=x+y)

ax.set_xmargin(0.8)

plt.show()

