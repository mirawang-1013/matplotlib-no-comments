

import matplotlib.pyplot as plt

import numpy as np



plt.style.use('_mpl-gallery')



           

n = 4

x = np.linspace(-1, 1, n)

y = np.linspace(-1, 1, n)

z = np.linspace(-1, 1, n)

X, Y, Z = np.meshgrid(x, y, z)

U = (X + Y)/5

V = (Y - X)/5

W = Z*0





      

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

ax.quiver(X, Y, Z, U, V, W)



ax.set(xticklabels=[],

       yticklabels=[],

       zticklabels=[])



plt.show()

