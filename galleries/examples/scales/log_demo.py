



import matplotlib.pyplot as plt

import numpy as np



fig, (ax1, ax2, ax3) = plt.subplots(1, 3, layout='constrained', figsize=(7, 7/3))

            

t = np.arange(0.01, 10.0, 0.01)

ax1.semilogx(t, np.sin(2 * np.pi * t))

ax1.set(title='semilogx')

ax1.grid()

ax1.grid(which="minor", color="0.9")



            

x = np.arange(4)

ax2.semilogy(4*x, 10**x, 'o--')

ax2.set(title='semilogy')

ax2.grid()

ax2.grid(which="minor", color="0.9")



                  

x = np.array([1, 10, 100, 1000])

ax3.loglog(x, 5 * x, 'o--')

ax3.set(title='loglog')

ax3.grid()

ax3.grid(which="minor", color="0.9")



    

                             

                             

                                                                                 

            

fig, ax = plt.subplots()

ax.bar(["L1 cache", "L2 cache", "L3 cache", "RAM", "SSD"],

       [32, 1_000, 32_000, 16_000_000, 512_000_000])

ax.set_yscale('log', base=2)

ax.set_yticks([1, 2**10, 2**20, 2**30], labels=['kB', 'MB', 'GB', 'TB'])

ax.set_title("Typical memory sizes")

ax.yaxis.grid()



    

                              

                              

                                                                                   

                                                                                

                                                                                

                             

 

                                                                                   

                                                                                 

                                                                               

                          

x = np.linspace(0.0, 2.0, 10)

y = 10**x

yerr = 1.75 + 0.75*y



fig, (ax1, ax2) = plt.subplots(1, 2, layout="constrained", figsize=(6, 3))

fig.suptitle("errorbars going negative")

ax1.set_yscale("log", nonpositive='mask')

ax1.set_title('nonpositive="mask"')

ax1.errorbar(x, y, yerr=yerr, fmt='o', capsize=5)



ax2.set_yscale("log", nonpositive='clip')

ax2.set_title('nonpositive="clip"')

ax2.errorbar(x, y, yerr=yerr, fmt='o', capsize=5)



plt.show()

