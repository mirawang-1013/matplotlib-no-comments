



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.ticker import EngFormatter



                                         

prng = np.random.RandomState(19680801)



                                 

                                                                          

xs = np.logspace(1, 9, 100)

ys = (0.8 + 0.4 * prng.uniform(size=100)) * np.log10(xs)**2



                                                                            

fig, (ax0, ax1) = plt.subplots(nrows=2, figsize=(7, 9.6))

for ax in (ax0, ax1):

    ax.set_xscale('log')



                                                               

ax0.set_title('Full unit ticklabels, w/ default precision & space separator')

formatter0 = EngFormatter(unit='Hz')

ax0.xaxis.set_major_formatter(formatter0)

ax0.plot(xs, ys)

ax0.set_xlabel('Frequency')



                                                                        

                                                           

ax1.set_title('SI-prefix only ticklabels, 1-digit precision & '

              'thin space separator')

formatter1 = EngFormatter(places=1, sep="\N{THIN SPACE}")          

ax1.xaxis.set_major_formatter(formatter1)

ax1.plot(xs, ys)

ax1.set_xlabel('Frequency [Hz]')



plt.tight_layout()

plt.show()

