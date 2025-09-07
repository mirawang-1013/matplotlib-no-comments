



import matplotlib.pyplot as plt

import numpy as np



fig, ax = plt.subplots()

                                                                   

ax.spines[["left", "bottom"]].set_position(("data", 0))

                                

ax.spines[["top", "right"]].set_visible(False)



                                                                              

                                                                              

                                                                              

                                                                               

                                  

ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)

ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)



                   

x = np.linspace(-0.5, 1., 100)

ax.plot(x, np.sin(x*np.pi))



plt.show()

