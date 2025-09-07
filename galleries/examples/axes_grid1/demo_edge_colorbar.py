



import matplotlib.pyplot as plt



from matplotlib import cbook

from mpl_toolkits.axes_grid1 import AxesGrid





def get_demo_image():

    z = cbook.get_sample_data("axes_grid/bivariate_normal.npy")               

    return z, (-3, 4, -4, 3)





def demo_bottom_cbar(fig):

    

    grid = AxesGrid(fig, 121,                           

                    nrows_ncols=(2, 2),

                    axes_pad=0.10,

                    share_all=True,

                    label_mode="1",

                    cbar_location="bottom",

                    cbar_mode="edge",

                    cbar_pad=0.25,

                    cbar_size="15%",

                    direction="column"

                    )



    Z, extent = get_demo_image()

    cmaps = ["autumn", "summer"]

    for i in range(4):

        im = grid[i].imshow(Z, extent=extent, cmap=cmaps[i//2])

        if i % 2:

            grid.cbar_axes[i//2].colorbar(im)



    for cax in grid.cbar_axes:

        cax.axis[cax.orientation].set_label("Bar")



                                                

    grid.axes_llc.set_xticks([-2, 0, 2])

    grid.axes_llc.set_yticks([-2, 0, 2])





def demo_right_cbar(fig):

    

    grid = AxesGrid(fig, 122,                           

                    nrows_ncols=(2, 2),

                    axes_pad=0.10,

                    label_mode="1",

                    share_all=True,

                    cbar_location="right",

                    cbar_mode="edge",

                    cbar_size="7%",

                    cbar_pad="2%",

                    )

    Z, extent = get_demo_image()

    cmaps = ["spring", "winter"]

    for i in range(4):

        im = grid[i].imshow(Z, extent=extent, cmap=cmaps[i//2])

        if i % 2:

            grid.cbar_axes[i//2].colorbar(im)



    for cax in grid.cbar_axes:

        cax.axis[cax.orientation].set_label('Foo')



                                                            

    grid.axes_llc.set_xticks([-2, 0, 2])

    grid.axes_llc.set_yticks([-2, 0, 2])





fig = plt.figure()



demo_bottom_cbar(fig)

demo_right_cbar(fig)



plt.show()

