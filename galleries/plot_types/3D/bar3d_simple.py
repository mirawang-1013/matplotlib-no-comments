

import matplotlib.pyplot as plt

import numpy as np



plt.style.use('_mpl-gallery')



           

x = [1, 1, 2, 2]

y = [1, 2, 1, 2]

z = [0, 0, 0, 0]

dx = np.ones_like(x)*0.5

dy = np.ones_like(x)*0.5

dz = [2, 3, 1, 4]



      

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

ax.bar3d(x, y, z, dx, dy, dz)



ax.set(xticklabels=[],

       yticklabels=[],

       zticklabels=[])



plt.show()

