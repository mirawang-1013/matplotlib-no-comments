



    

                                                                

                                                              



import matplotlib.pyplot as plt

import numpy as np





x = np.linspace(-2 * np.pi, 2 * np.pi, 100)

y = np.sinc(x)



fig, ax = plt.subplots()

ax.plot(x, y)



    

         

         

                                                                        

                                                                          

                         



print(ax.margins())



    

                                                                        

                                  



fig, ax = plt.subplots()

ax.plot(x, y)

ax.margins(0.2, 0.2)



    

                                                                               

                                                                       

                                                                             

                                                                               

                               



fig, ax = plt.subplots()

ax.plot(x, y)

ax.margins(y=-0.2)



    

              

              

                                                                              

                                                                           

                                        

 



xx, yy = np.meshgrid(x, x)

zz = np.sinc(np.sqrt((xx - 1)**2 + (yy - 1)**2))



fig, ax = plt.subplots(ncols=2, figsize=(12, 8))

ax[0].imshow(zz)

ax[0].set_title("default margins")

ax[1].imshow(zz)

ax[1].margins(0.2)

ax[1].set_title("margins(0.2)")



    

                                                             

                                                                      

                                                                           

                                           

                                                                   

                                                                        

                            

 

                                                                         



fig, ax = plt.subplots(ncols=3, figsize=(16, 10))

ax[0].imshow(zz)

ax[0].margins(0.2)

ax[0].set_title("default use_sticky_edges\nmargins(0.2)")

ax[1].imshow(zz)

ax[1].margins(0.2)

ax[1].use_sticky_edges = False

ax[1].set_title("use_sticky_edges=False\nmargins(0.2)")

ax[2].imshow(zz)

ax[2].margins(-0.2)

ax[2].set_title("default use_sticky_edges\nmargins(-0.2)")



    

                                                                           

                         

 

                                                                          

                                                                    

                                        

 

                       

                       

 

                            

                                                          



fig, ax = plt.subplots(ncols=2, figsize=(12, 8))

ax[0].plot(x, y)

ax[0].set_title("Single curve")

ax[1].plot(x, y)

ax[1].plot(x * 2.0, y)

ax[1].set_title("Two curves")



    

                                                                          

                       

 

                                                       

                                                                      

                                                                             

                                                                         

                                    



fig, ax = plt.subplots(ncols=2, figsize=(12, 8))

ax[0].plot(x, y)

ax[0].set_xlim(left=-1, right=1)

ax[0].plot(x + np.pi * 0.5, y)

ax[0].set_title("set_xlim(left=-1, right=1)\n")

ax[1].plot(x, y)

ax[1].set_xlim(left=-1, right=1)

ax[1].plot(x + np.pi * 0.5, y)

ax[1].autoscale()

ax[1].set_title("set_xlim(left=-1, right=1)\nautoscale()")



    

                                                                             

                                                                



print(ax[0].get_autoscale_on())                        

print(ax[1].get_autoscale_on())                                      



    

                                                                              

                                                                              

                                                                             

                                                                              

                                                                          

                                                                            

                                                                  



fig, ax = plt.subplots()

ax.plot(x, y)

ax.margins(0.2, 0.2)

ax.autoscale(enable=None, axis="x", tight=True)



print(ax.margins())

