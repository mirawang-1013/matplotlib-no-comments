



import matplotlib.pyplot as plt



from matplotlib import cbook

from mpl_toolkits.axes_grid1 import ImageGrid



fig = plt.figure(figsize=(10.5, 2.5))

Z = cbook.get_sample_data("axes_grid/bivariate_normal.npy")               

extent = (-3, 4, -4, 3)





                                                                     

                             

grid = ImageGrid(

    fig, 141,                                    

     nrows_ncols=(2, 2), axes_pad=0.05, label_mode="1")

for ax in grid:

    ax.imshow(Z, extent=extent)

                                                                           

grid.axes_llc.set(xticks=[-2, 0, 2], yticks=[-2, 0, 2])





                                              

grid = ImageGrid(

    fig, 142,                                    

    nrows_ncols=(2, 2), axes_pad=0.0, label_mode="L", share_all=True,

    cbar_location="top", cbar_mode="single")

for ax in grid:

    im = ax.imshow(Z, extent=extent)

grid.cbar_axes[0].colorbar(im)

for cax in grid.cbar_axes:

    cax.tick_params(labeltop=False)

                                            

grid.axes_llc.set(xticks=[-2, 0, 2], yticks=[-2, 0, 2])





                                                        

grid = ImageGrid(

    fig, 143,                                    

    nrows_ncols=(2, 2), axes_pad=0.1, label_mode="1", share_all=True,

    cbar_location="top", cbar_mode="each", cbar_size="7%", cbar_pad="2%")

for ax, cax in zip(grid, grid.cbar_axes):

    im = ax.imshow(Z, extent=extent)

    cax.colorbar(im)

    cax.tick_params(labeltop=False)

                                            

grid.axes_llc.set(xticks=[-2, 0, 2], yticks=[-2, 0, 2])





                                                        

grid = ImageGrid(

    fig, 144,                                    

    nrows_ncols=(2, 2), axes_pad=(0.45, 0.15), label_mode="1", share_all=True,

    cbar_location="right", cbar_mode="each", cbar_size="7%", cbar_pad="2%")

                                           

limits = ((0, 1), (-2, 2), (-1.7, 1.4), (-1.5, 1))

for ax, cax, vlim in zip(grid, grid.cbar_axes, limits):

    im = ax.imshow(Z, extent=extent, vmin=vlim[0], vmax=vlim[1])

    cb = cax.colorbar(im)

    cb.set_ticks((vlim[0], vlim[1]))

                                            

grid.axes_llc.set(xticks=[-2, 0, 2], yticks=[-2, 0, 2])





plt.show()

