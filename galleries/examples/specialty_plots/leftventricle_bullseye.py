



import matplotlib.pyplot as plt

import numpy as np



import matplotlib as mpl





def bullseye_plot(ax, data, seg_bold=None, cmap="viridis", norm=None):

    



    data = np.ravel(data)

    if seg_bold is None:

        seg_bold = []

    if norm is None:

        norm = mpl.colors.Normalize(vmin=data.min(), vmax=data.max())



    r = np.linspace(0.2, 1, 4)



    ax.set(ylim=(0, 1), xticklabels=[], yticklabels=[])

    ax.grid(False)               



                                     

    for start, stop, r_in, r_out in [

            (0, 6, r[2], r[3]),

            (6, 12, r[1], r[2]),

            (12, 16, r[0], r[1]),

            (16, 17, 0, r[0]),

    ]:

        n = stop - start

        dtheta = 2*np.pi / n

        ax.bar(np.arange(n) * dtheta + np.pi/2, r_out - r_in, dtheta, r_in,

               color=cmap(norm(data[start:stop])))



                                                                             

                                                                           

                                                                               

                                                         

                                              

    for start, stop, r_in, r_out in [

            (0, 6, r[2], r[3]),

            (6, 12, r[1], r[2]),

            (12, 16, r[0], r[1]),

    ]:

        n = stop - start

        dtheta = 2*np.pi / n

        ax.bar(np.arange(n) * dtheta + np.pi/2, r_out - r_in, dtheta, r_in,

               clip_on=False, color="none", edgecolor="k", linewidth=[

                   4 if i + 1 in seg_bold else 2 for i in range(start, stop)])

                                                                              

                   

    ax.plot(np.linspace(0, 2*np.pi), np.linspace(r[0], r[0]), "k",

            linewidth=(4 if 17 in seg_bold else 2))





                      

data = np.arange(17) + 1





                                                    

fig = plt.figure(figsize=(10, 5), layout="constrained")

fig.get_layout_engine().set(wspace=.1, w_pad=.2)

axs = fig.subplots(1, 3, subplot_kw=dict(projection='polar'))

fig.canvas.manager.set_window_title('Left Ventricle Bulls Eyes (AHA)')





                                                               

                            

cmap = mpl.colormaps["viridis"]

norm = mpl.colors.Normalize(vmin=1, vmax=17)

                                                                         

                                                                        

fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm),

             cax=axs[0].inset_axes([0, -.15, 1, .1]),

             orientation='horizontal', label='Some units')





                                    

cmap2 = mpl.colormaps["cool"]

norm2 = mpl.colors.Normalize(vmin=1, vmax=17)

fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap2, norm=norm2),

             cax=axs[1].inset_axes([0, -.15, 1, .1]),

             orientation='horizontal', label='Some other units')





                                                               

                                                                

               

cmap3 = mpl.colors.ListedColormap(['r', 'g', 'b', 'c'], over='0.35', under='0.75')

                                                                     

                                                                    

                           

bounds = [2, 3, 7, 9, 15]

norm3 = mpl.colors.BoundaryNorm(bounds, cmap3.N)

fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap3, norm=norm3),

             cax=axs[2].inset_axes([0, -.15, 1, .1]),

             extend='both',

             ticks=bounds,            

             spacing='proportional',

             orientation='horizontal',

             label='Discrete intervals, some other units')





                             

bullseye_plot(axs[0], data, cmap=cmap, norm=norm)

axs[0].set_title('Bulls Eye (AHA)')



bullseye_plot(axs[1], data, cmap=cmap2, norm=norm2)

axs[1].set_title('Bulls Eye (AHA)')



bullseye_plot(axs[2], data, seg_bold=[3, 5, 6, 11, 12, 16],

              cmap=cmap3, norm=norm3)

axs[2].set_title('Segments [3, 5, 6, 11, 12, 16] in bold')



plt.show()

