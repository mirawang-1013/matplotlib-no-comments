



import matplotlib.pyplot as plt





def draw_text(ax):

    

    from matplotlib.offsetbox import AnchoredText

    at = AnchoredText("Figure 1a",

                      loc='upper left', prop=dict(size=8), frameon=True,

                      )

    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")

    ax.add_artist(at)



    at2 = AnchoredText("Figure 1(b)",

                       loc='lower left', prop=dict(size=8), frameon=True,

                       bbox_to_anchor=(0., 1.),

                       bbox_transform=ax.transAxes

                       )

    at2.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")

    ax.add_artist(at2)





def draw_circle(ax):

    

    from matplotlib.patches import Circle

    from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea

    ada = AnchoredDrawingArea(20, 20, 0, 0,

                              loc='upper right', pad=0., frameon=False)

    p = Circle((10, 10), 10)

    ada.da.add_artist(p)

    ax.add_artist(ada)





def draw_sizebar(ax):

    

    from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

    asb = AnchoredSizeBar(ax.transData,

                          0.1,

                          r"1$^{\prime}$",

                          loc='lower center',

                          pad=0.1, borderpad=0.5, sep=5,

                          frameon=False)

    ax.add_artist(asb)





fig, ax = plt.subplots()

ax.set_aspect(1.)



draw_text(ax)

draw_circle(ax)

draw_sizebar(ax)



plt.show()

