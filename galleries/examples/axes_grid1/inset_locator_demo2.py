



import matplotlib.pyplot as plt

import numpy as np



from matplotlib import cbook

from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

from mpl_toolkits.axes_grid1.inset_locator import mark_inset, zoomed_inset_axes



fig, (ax, ax2) = plt.subplots(ncols=2, figsize=[6, 3])





                                                  

ax.set_aspect(1)



axins = zoomed_inset_axes(ax, zoom=0.5, loc='upper right')

                                           

axins.yaxis.get_major_locator().set_params(nbins=7)

axins.xaxis.get_major_locator().set_params(nbins=7)

axins.tick_params(labelleft=False, labelbottom=False)





def add_sizebar(ax, size):

    asb = AnchoredSizeBar(ax.transData,

                          size,

                          str(size),

                          loc="lower center",

                          pad=0.1, borderpad=0.5, sep=5,

                          frameon=False)

    ax.add_artist(asb)



add_sizebar(ax, 0.5)

add_sizebar(axins, 0.5)





                                                                        

Z = cbook.get_sample_data("axes_grid/bivariate_normal.npy")               

extent = (-3, 4, -4, 3)

Z2 = np.zeros((150, 150))

ny, nx = Z.shape

Z2[30:30+ny, 30:30+nx] = Z



ax2.imshow(Z2, extent=extent, origin="lower")



axins2 = zoomed_inset_axes(ax2, zoom=6, loc="upper right")

axins2.imshow(Z2, extent=extent, origin="lower")



                                 

x1, x2, y1, y2 = -1.5, -0.9, -2.5, -1.9

axins2.set_xlim(x1, x2)

axins2.set_ylim(y1, y2)

                                           

axins2.yaxis.get_major_locator().set_params(nbins=7)

axins2.xaxis.get_major_locator().set_params(nbins=7)

axins2.tick_params(labelleft=False, labelbottom=False)



                                                                    

                                                           

mark_inset(ax2, axins2, loc1=2, loc2=4, fc="none", ec="0.5")



plt.show()

