



import matplotlib.pyplot as plt



from mpl_toolkits.axes_grid1 import inset_locator



fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[6, 3])



im1 = ax1.imshow([[1, 2], [2, 3]])

axins1 = inset_locator.inset_axes(

    ax1,

    width="50%",                                   

    height="5%",              

    loc="upper right",

)

axins1.xaxis.set_ticks_position("bottom")

fig.colorbar(im1, cax=axins1, orientation="horizontal", ticks=[1, 2, 3])



im = ax2.imshow([[1, 2], [2, 3]])

axins = inset_locator.inset_axes(

    ax2,

    width="5%",                                  

    height="50%",               

    loc="lower left",

    bbox_to_anchor=(1.05, 0., 1, 1),

    bbox_transform=ax2.transAxes,

    borderpad=0,

)

fig.colorbar(im, cax=axins, ticks=[1, 2, 3])



plt.show()

