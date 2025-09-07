



import matplotlib.pyplot as plt

import numpy as np



np.random.seed(19680801)



fig, ax = plt.subplots()

x = 30*np.random.randn(10000)

mu = x.mean()

median = np.median(x)

sigma = x.std()

textstr = '\n'.join((

    r'$\mu=%.2f$' % (mu, ),

    r'$\mathrm{median}=%.2f$' % (median, ),

    r'$\sigma=%.2f$' % (sigma, )))



ax.hist(x, 50)

                                             

props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)



                                               

ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,

        verticalalignment='top', bbox=props)



plt.show()

