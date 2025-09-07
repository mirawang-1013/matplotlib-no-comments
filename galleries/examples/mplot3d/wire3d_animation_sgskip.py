



import time



import matplotlib.pyplot as plt

import numpy as np



fig = plt.figure()

ax = fig.add_subplot(projection='3d')



                         

xs = np.linspace(-1, 1, 50)

ys = np.linspace(-1, 1, 50)

X, Y = np.meshgrid(xs, ys)



                                                                

ax.set_zlim(-1, 1)



                 

wframe = None

tstart = time.time()

for phi in np.linspace(0, 180. / np.pi, 100):

                                                               

    if wframe:

        wframe.remove()

                    

    Z = np.cos(2 * np.pi * X + phi) * (1 - np.hypot(X, Y))

                                                                 

    wframe = ax.plot_wireframe(X, Y, Z, rstride=2, cstride=2)

    plt.pause(.001)



print('Average FPS: %f' % (100 / (time.time() - tstart)))



    

           

                   

                          

                    

