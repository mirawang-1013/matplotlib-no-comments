



import matplotlib.pyplot as plt

import numpy as np



from matplotlib.colors import Normalize





def imshow3d(ax, array, value_direction='z', pos=0, norm=None, cmap=None):

    

    if norm is None:

        norm = Normalize()

    colors = plt.get_cmap(cmap)(norm(array))



    if value_direction == 'x':

        nz, ny = array.shape

        zi, yi = np.mgrid[0:nz + 1, 0:ny + 1]

        xi = np.full_like(yi, pos)

    elif value_direction == 'y':

        nx, nz = array.shape

        xi, zi = np.mgrid[0:nx + 1, 0:nz + 1]

        yi = np.full_like(zi, pos)

    elif value_direction == 'z':

        ny, nx = array.shape

        yi, xi = np.mgrid[0:ny + 1, 0:nx + 1]

        zi = np.full_like(xi, pos)

    else:

        raise ValueError(f"Invalid value_direction: {value_direction!r}")

    ax.plot_surface(xi, yi, zi, rstride=1, cstride=1, facecolors=colors, shade=False)





fig = plt.figure()

ax = fig.add_subplot(projection='3d')

ax.set(xlabel="x", ylabel="y", zlabel="z")



nx, ny, nz = 8, 10, 5

data_xy = np.arange(ny * nx).reshape(ny, nx) + 15 * np.random.random((ny, nx))

data_yz = np.arange(nz * ny).reshape(nz, ny) + 10 * np.random.random((nz, ny))

data_zx = np.arange(nx * nz).reshape(nx, nz) + 8 * np.random.random((nx, nz))



imshow3d(ax, data_xy)

imshow3d(ax, data_yz, value_direction='x', cmap='magma')

imshow3d(ax, data_zx, value_direction='y', pos=ny, cmap='plasma')



plt.show()



    

           

                   

                       

                    

