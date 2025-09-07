



import matplotlib.pyplot as plt

import numpy as np



ax = plt.figure().add_subplot(projection='3d')



                                          

x = np.linspace(0, 1, 100)

y = np.sin(x * 2 * np.pi) / 2 + 0.5

ax.plot(x, y, zs=0, zdir='z', label='curve in (x, y)')



                                                                      

colors = ('r', 'g', 'b', 'k')



                                         

np.random.seed(19680801)



x = np.random.sample(20 * len(colors))

y = np.random.sample(20 * len(colors))

c_list = []

for c in colors:

    c_list.extend([c] * 20)

                                                                           

                                                        

ax.scatter(x, y, zs=0, zdir='y', c=c_list, label='points in (x, z)')



                                         

ax.legend()

ax.set_xlim(0, 1)

ax.set_ylim(0, 1)

ax.set_zlim(0, 1)

ax.set_xlabel('X')

ax.set_ylabel('Y')

ax.set_zlabel('Z')



                                                                            

                  

ax.view_init(elev=20., azim=-35, roll=0)



plt.show()



    

           

                                                        

                     

                        

