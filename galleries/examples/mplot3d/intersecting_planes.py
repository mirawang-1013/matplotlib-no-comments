

import matplotlib.pyplot as plt

import numpy as np





def plot_quadrants(ax, array, fixed_coord, cmap):

    

    nx, ny, nz = array.shape

    index = {

        'x': (nx // 2, slice(None), slice(None)),

        'y': (slice(None), ny // 2, slice(None)),

        'z': (slice(None), slice(None), nz // 2),

    }[fixed_coord]

    plane_data = array[index]



    n0, n1 = plane_data.shape

    quadrants = [

        plane_data[:n0 // 2, :n1 // 2],

        plane_data[:n0 // 2, n1 // 2:],

        plane_data[n0 // 2:, :n1 // 2],

        plane_data[n0 // 2:, n1 // 2:]

    ]



    min_val = array.min()

    max_val = array.max()



    cmap = plt.get_cmap(cmap)



    for i, quadrant in enumerate(quadrants):

        facecolors = cmap((quadrant - min_val) / (max_val - min_val))

        if fixed_coord == 'x':

            Y, Z = np.mgrid[0:ny // 2, 0:nz // 2]

            X = nx // 2 * np.ones_like(Y)

            Y_offset = (i // 2) * ny // 2

            Z_offset = (i % 2) * nz // 2

            ax.plot_surface(X, Y + Y_offset, Z + Z_offset, rstride=1, cstride=1,

                            facecolors=facecolors, shade=False)

        elif fixed_coord == 'y':

            X, Z = np.mgrid[0:nx // 2, 0:nz // 2]

            Y = ny // 2 * np.ones_like(X)

            X_offset = (i // 2) * nx // 2

            Z_offset = (i % 2) * nz // 2

            ax.plot_surface(X + X_offset, Y, Z + Z_offset, rstride=1, cstride=1,

                            facecolors=facecolors, shade=False)

        elif fixed_coord == 'z':

            X, Y = np.mgrid[0:nx // 2, 0:ny // 2]

            Z = nz // 2 * np.ones_like(X)

            X_offset = (i // 2) * nx // 2

            Y_offset = (i % 2) * ny // 2

            ax.plot_surface(X + X_offset, Y + Y_offset, Z, rstride=1, cstride=1,

                            facecolors=facecolors, shade=False)





def figure_3D_array_slices(array, cmap=None):

    

    fig = plt.figure()

    ax = fig.add_subplot(projection='3d')

    ax.set_box_aspect(array.shape)

    plot_quadrants(ax, array, 'x', cmap=cmap)

    plot_quadrants(ax, array, 'y', cmap=cmap)

    plot_quadrants(ax, array, 'z', cmap=cmap)

    return fig, ax





nx, ny, nz = 70, 100, 50

r_square = (np.mgrid[-1:1:1j * nx, -1:1:1j * ny, -1:1:1j * nz] ** 2).sum(0)



figure_3D_array_slices(r_square, cmap='viridis_r')

plt.show()





    

           

                   

                    

