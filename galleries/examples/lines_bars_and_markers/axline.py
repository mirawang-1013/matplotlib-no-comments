



import matplotlib.pyplot as plt

import numpy as np



t = np.linspace(-10, 10, 100)

sig = 1 / (1 + np.exp(-t))



fig, ax = plt.subplots()

ax.axhline(y=0, color="black", linestyle="--")

ax.axhline(y=0.5, color="black", linestyle=":")

ax.axhline(y=1.0, color="black", linestyle="--")

ax.axvline(color="grey")

ax.axline((0, 0.5), slope=0.25, color="black", linestyle=(0, (5, 5)))

ax.plot(t, sig, linewidth=2, label=r"$\sigma(t) = \frac{1}{1 + e^{-t}}$")

ax.set(xlim=(-10, 10), xlabel="t")

ax.legend(fontsize=14)

plt.show()



    

                                                                           

                                                                            

                                                                      

                        



fig, ax = plt.subplots()

for pos in np.linspace(-2, 1, 10):

    ax.axline((pos, 0), slope=0.5, color='k', transform=ax.transAxes)



ax.set(xlim=(0, 1), ylim=(0, 1))

plt.show()



    

 

                            

 

                                                                              

                     

 

                                                                   

                                                                   

                                                                 

 

 

              

 

                                                                                 

                                                      

 

                                 

